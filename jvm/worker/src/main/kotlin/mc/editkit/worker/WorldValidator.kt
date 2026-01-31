package mc.editkit.worker

import org.jglrxavpok.hephaistos.mca.RegionFile
import org.jglrxavpok.hephaistos.nbt.NBTCompound
import java.io.RandomAccessFile
import java.nio.file.Path
import kotlin.io.path.exists
import kotlin.io.path.isRegularFile

/**
 * Walidator świata Minecraft - sprawdza czy edycje zostały wykonane poprawnie
 * Używa Hephaistos do czytania regionów MCA
 */
class WorldValidator(private val worldPath: Path) {
    
    data class ValidationResult(
        val isValid: Boolean,
        val checkedChunks: Int,
        val passedChecks: Int,
        val failedChecks: Int,
        val errors: List<ValidationError>
    ) {
        data class ValidationError(
            val type: ErrorType,
            val message: String,
            val position: Triple<Int, Int, Int>? = null,
            val expected: String? = null,
            val actual: String? = null
        )
        
        enum class ErrorType {
            CHUNK_MISSING,      // Chunk nie istnieje w regionie
            BLOCK_MISMATCH,     // Blok nie zgadza się z oczekiwanym
            TE_MISSING,         // Tile Entity nie istnieje
            TE_MISMATCH,        // Tile Entity ma zły ID lub brakuje kluczy NBT
            NBT_ERROR,          // Błąd odczytu NBT
            REGION_ERROR        // Błąd odczytu regionu
        }
        
        fun formatReport(): String {
            val sb = StringBuilder()
            sb.appendLine("=".repeat(60))
            sb.appendLine("WERYFIKACJA ŚWIATA: ${if (isValid) "✅ PASS" else "❌ FAIL"}")
            sb.appendLine("=".repeat(60))
            sb.appendLine("Sprawdzone chunki: $checkedChunks")
            sb.appendLine("Pomyślne: $passedChecks")
            sb.appendLine("Błędy: $failedChecks")
            
            if (errors.isNotEmpty()) {
                sb.appendLine()
                sb.appendLine("SZCZEGÓŁY BŁĘDÓW:")
                sb.appendLine("-".repeat(60))
                errors.forEachIndexed { index, error ->
                    sb.appendLine("${index + 1}. [${error.type}] ${error.message}")
                    if (error.position != null) {
                        sb.appendLine("   Pozycja: ${error.position.first}, ${error.position.second}, ${error.position.third}")
                    }
                    if (error.expected != null) {
                        sb.appendLine("   Oczekiwano: ${error.expected}")
                    }
                    if (error.actual != null) {
                        sb.appendLine("   Rzeczywiste: ${error.actual}")
                    }
                    sb.appendLine()
                }
            }
            
            return sb.toString()
        }
    }
    
    /**
     * Waliduj świat na podstawie metadanych edycji
     * Sprawdza TYLKO chunki które były modyfikowane
     */
    fun validate(metadata: EditMetadata): ValidationResult {
        val errors = mutableListOf<ValidationResult.ValidationError>()
        var checkedChunks = 0
        var passedChecks = 0
        var failedChecks = 0
        
        // Grupuj oczekiwane zmiany po chunkach dla efektywności
        val changesByChunk = metadata.expectedChanges.groupBy { change ->
            val chunkX = change.x shr 4
            val chunkZ = change.z shr 4
            Pair(chunkX, chunkZ)
        }
        
        // Sprawdź każdy zmodyfikowany chunk
        for (chunkCoord in metadata.modifiedChunks) {
            checkedChunks++
            
            val regionFile = worldPath.resolve("region/r.${chunkCoord.regionX}.${chunkCoord.regionZ}.mca")
            
            if (!regionFile.exists() || !regionFile.isRegularFile()) {
                errors.add(ValidationResult.ValidationError(
                    type = ValidationResult.ErrorType.REGION_ERROR,
                    message = "Region file nie istnieje: ${regionFile.fileName}",
                    position = null
                ))
                failedChecks++
                continue
            }
            
            try {
                val raf = RandomAccessFile(regionFile.toFile(), "r")
                RegionFile(raf, chunkCoord.regionX, chunkCoord.regionZ, 0, 255).use { region ->
                    val chunkData = region.getChunkData(chunkCoord.chunkX, chunkCoord.chunkZ)
                    
                    if (chunkData == null) {
                        errors.add(ValidationResult.ValidationError(
                            type = ValidationResult.ErrorType.CHUNK_MISSING,
                            message = "Chunk ${chunkCoord} nie istnieje w regionie",
                            position = Triple(
                                chunkCoord.toBlockX(),
                                0,
                                chunkCoord.toBlockZ()
                            )
                        ))
                        failedChecks++
                        return@use
                    }
                    
                    // Pobierz dane chunka
                    val level = chunkData.getCompound("Level") 
                        ?: throw IllegalStateException("Brak 'Level' w chunk ${chunkCoord}")
                    
                    // Sprawdź wszystkie oczekiwane zmiany w tym chunku
                    val globalChunkX = chunkCoord.toGlobalChunkX()
                    val globalChunkZ = chunkCoord.toGlobalChunkZ()
                    val chunkChanges = changesByChunk[Pair(globalChunkX, globalChunkZ)] ?: emptyList()
                    
                    for (expectedChange in chunkChanges) {
                        when (expectedChange) {
                            is EditMetadata.ExpectedChange.Block -> {
                                val result = validateBlock(level, expectedChange)
                                if (result) {
                                    passedChecks++
                                } else {
                                    failedChecks++
                                    errors.add(ValidationResult.ValidationError(
                                        type = ValidationResult.ErrorType.BLOCK_MISMATCH,
                                        message = "Nieprawidłowy blok",
                                        position = Triple(expectedChange.x, expectedChange.y, expectedChange.z),
                                        expected = "ID=${expectedChange.blockId}, meta=${expectedChange.metadata}",
                                        actual = getBlockInfo(level, expectedChange.x, expectedChange.y, expectedChange.z)
                                    ))
                                }
                            }
                            is EditMetadata.ExpectedChange.TileEntity -> {
                                val result = validateTileEntity(level, expectedChange)
                                if (result) {
                                    passedChecks++
                                } else {
                                    failedChecks++
                                    errors.add(ValidationResult.ValidationError(
                                        type = ValidationResult.ErrorType.TE_MISMATCH,
                                        message = "Nieprawidłowe Tile Entity",
                                        position = Triple(expectedChange.x, expectedChange.y, expectedChange.z),
                                        expected = "ID=${expectedChange.id}, keys=${expectedChange.requiredNbtKeys}",
                                        actual = getTileEntityInfo(level, expectedChange.x, expectedChange.y, expectedChange.z)
                                    ))
                                }
                            }
                        }
                    }
                }
            } catch (e: Exception) {
                errors.add(ValidationResult.ValidationError(
                    type = ValidationResult.ErrorType.NBT_ERROR,
                    message = "Błąd odczytu chunk ${chunkCoord}: ${e.message}",
                    position = Triple(chunkCoord.toBlockX(), 0, chunkCoord.toBlockZ())
                ))
                failedChecks++
            }
        }
        
        return ValidationResult(
            isValid = errors.isEmpty(),
            checkedChunks = checkedChunks,
            passedChecks = passedChecks,
            failedChecks = failedChecks,
            errors = errors
        )
    }
    
    /**
     * Waliduj pojedynczy blok w chunku
     */
    private fun validateBlock(level: NBTCompound, expected: EditMetadata.ExpectedChange.Block): Boolean {
        val (blockId, metadata) = readBlockAt(level, expected.x, expected.y, expected.z)
        return blockId == expected.blockId && metadata == expected.metadata
    }
    
    /**
     * Waliduj Tile Entity w chunku
     */
    private fun validateTileEntity(level: NBTCompound, expected: EditMetadata.ExpectedChange.TileEntity): Boolean {
        val tileEntities = level.getList<NBTCompound>("TileEntities") ?: return false
        
        for (te in tileEntities) {
            val x = te.getInt("x") ?: continue
            val y = te.getInt("y") ?: continue
            val z = te.getInt("z") ?: continue
            
            if (x == expected.x && y == expected.y && z == expected.z) {
                val id = te.getString("id") ?: return false
                if (id != expected.id) return false
                
                // Sprawdź czy wszystkie wymagane klucze NBT istnieją
                for (key in expected.requiredNbtKeys) {
                    if (!te.containsKey(key)) return false
                }
                return true
            }
        }
        return false
    }
    
    /**
     * Odczytaj blok z chunku (1.7.10 format)
     */
    private fun readBlockAt(level: NBTCompound, x: Int, y: Int, z: Int): Pair<Int, Int> {
        val sections = level.getList<NBTCompound>("Sections") 
            ?: return Pair(0, 0)
        
        val sectionY = (y shr 4)
        val localY = y and 0xF
        val localX = x and 0xF
        val localZ = z and 0xF
        
        for (section in sections) {
            val secY = section.getByte("Y")?.toInt() ?: continue
            if (secY != sectionY) continue
            
            val blocks = section.getByteArray("Blocks")?.copyArray() 
                ?: return Pair(0, 0)
            val data = section.getByteArray("Data")?.copyArray() 
                ?: ByteArray(2048)
            
            val idx = (localY * 16 + localZ) * 16 + localX
            val blockId = blocks[idx].toInt() and 0xFF
            
            val dataIdx = idx shr 1
            val nibble = data[dataIdx].toInt() and 0xFF
            val metadata = if (idx and 1 == 0) {
                nibble and 0x0F
            } else {
                (nibble shr 4) and 0x0F
            }
            
            return Pair(blockId, metadata)
        }
        
        return Pair(0, 0) // Air
    }
    
    /**
     * Pobierz informacje o bloku do raportu błędu
     */
    private fun getBlockInfo(level: NBTCompound, x: Int, y: Int, z: Int): String {
        val (id, meta) = readBlockAt(level, x, y, z)
        return "ID=$id, meta=$meta"
    }
    
    /**
     * Pobierz informacje o Tile Entity do raportu błędu
     */
    private fun getTileEntityInfo(level: NBTCompound, x: Int, y: Int, z: Int): String {
        val tileEntities = level.getList<NBTCompound>("TileEntities") ?: return "brak TE"
        
        for (te in tileEntities) {
            val tex = te.getInt("x") ?: continue
            val tey = te.getInt("y") ?: continue
            val tez = te.getInt("z") ?: continue
            
            if (tex == x && tey == y && tez == z) {
                val id = te.getString("id") ?: "unknown"
                return "ID=$id"
            }
        }
        return "brak TE"
    }
    
    companion object {
        /**
         * Sprawdź czy świat ma metadane i zweryfikuj go
         */
        fun validateWorld(worldPath: Path): ValidationResult? {
            val metadata = EditMetadata.load(worldPath) ?: return null
            return WorldValidator(worldPath).validate(metadata)
        }
    }
}
