package mc.editkit.worker

import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import java.nio.file.Path
import kotlin.io.path.*

/**
 * Metadane o edycji świata - zapisywane razem ze światem
 * Pozwala na późniejszą weryfikację czy edycja została wykonana poprawnie
 */
@Serializable
data class EditMetadata(
    /** Wersja formatu metadanych */
    val version: Int = 1,
    
    /** Timestamp edycji */
    val editTimestamp: Long = System.currentTimeMillis(),
    
    /** Nazwa operacji/toola który wykonał edycję */
    val toolName: String,
    
    /** Opis co było zmieniane */
    val description: String,
    
    /** Lista zmodyfikowanych chunków (regionX, regionZ, chunkX, chunkZ) */
    val modifiedChunks: List<ChunkCoord> = emptyList(),
    
    /** Oczekiwane zmiany - co powinno być w świecie */
    val expectedChanges: List<ExpectedChange> = emptyList()
) {
    @Serializable
    data class ChunkCoord(
        val regionX: Int,
        val regionZ: Int,
        val chunkX: Int,  // 0-31 w regionie
        val chunkZ: Int   // 0-31 w regionie
    ) {
        fun toGlobalChunkX(): Int = regionX * 32 + chunkX
        fun toGlobalChunkZ(): Int = regionZ * 32 + chunkZ
        
        fun toBlockX(): Int = toGlobalChunkX() * 16
        fun toBlockZ(): Int = toGlobalChunkZ() * 16
        
        override fun toString(): String = "r.$regionX.$regionZ/${chunkX},${chunkZ}"
    }
    
    @Serializable
    sealed class ExpectedChange {
        abstract val x: Int
        abstract val y: Int
        abstract val z: Int
        
        /** Oczekiwany blok na danej pozycji */
        @Serializable
        data class Block(
            override val x: Int,
            override val y: Int,
            override val z: Int,
            val blockId: Int,
            val metadata: Int = 0,
            val description: String = ""
        ) : ExpectedChange()
        
        /** Oczekiwane Tile Entity na danej pozycji */
        @Serializable
        data class TileEntity(
            override val x: Int,
            override val y: Int,
            override val z: Int,
            val id: String,  // np. "Control" dla command block
            val requiredNbtKeys: List<String> = emptyList(),  // Klucze które muszą istnieć
            val description: String = ""
        ) : ExpectedChange()
    }
    
    /**
     * Zapisz metadane do pliku JSON w folderze świata
     */
    fun save(worldPath: Path): Path {
        val metadataPath = worldPath.resolve("editkit_metadata.json")
        val json = Json { 
            prettyPrint = true 
            ignoreUnknownKeys = true
        }
        metadataPath.writeText(json.encodeToString(this))
        return metadataPath
    }
    
    companion object {
        /**
         * Wczytaj metadane z folderu świata
         */
        fun load(worldPath: Path): EditMetadata? {
            val metadataPath = worldPath.resolve("editkit_metadata.json")
            if (!metadataPath.exists()) return null
            
            return try {
                val json = Json { ignoreUnknownKeys = true }
                json.decodeFromString<EditMetadata>(metadataPath.readText())
            } catch (e: Exception) {
                System.err.println("Błąd wczytywania metadanych: ${e.message}")
                null
            }
        }
        
        /**
         * Utwórz metadane z listy edycji (BlockEdit, TEEdit)
         */
        fun fromEdits(
            toolName: String,
            description: String,
            edits: List<EditOperation>
        ): EditMetadata {
            val chunks = mutableSetOf<ChunkCoord>()
            val expected = mutableListOf<ExpectedChange>()
            
            for (edit in edits) {
                // Oblicz chunk z pozycji
                val chunkX = edit.x shr 4
                val chunkZ = edit.z shr 4
                val regionX = chunkX shr 5
                val regionZ = chunkZ shr 5
                val localChunkX = chunkX and 31
                val localChunkZ = chunkZ and 31
                
                chunks.add(ChunkCoord(regionX, regionZ, localChunkX, localChunkZ))
                
                // Dodaj oczekiwaną zmianę
                expected.add(when (edit) {
                    is BlockEdit -> ExpectedChange.Block(
                        x = edit.x,
                        y = edit.y,
                        z = edit.z,
                        blockId = edit.blockId,
                        metadata = edit.metadata,
                        description = edit.description
                    )
                    is TEEdit -> ExpectedChange.TileEntity(
                        x = edit.x,
                        y = edit.y,
                        z = edit.z,
                        id = edit.id,
                        requiredNbtKeys = edit.requiredNbtKeys,
                        description = edit.description
                    )
                    else -> continue
                })
            }
            
            return EditMetadata(
                toolName = toolName,
                description = description,
                modifiedChunks = chunks.toList(),
                expectedChanges = expected
            )
        }
    }
}

/**
 * Abstrakcyjna operacja edycji
 */
sealed class EditOperation {
    abstract val x: Int
    abstract val y: Int
    abstract val z: Int
    abstract val description: String
}

data class BlockEdit(
    override val x: Int,
    override val y: Int,
    override val z: Int,
    val blockId: Int,
    val metadata: Int = 0,
    override val description: String = ""
) : EditOperation()

data class TEEdit(
    override val x: Int,
    override val y: Int,
    override val z: Int,
    val id: String,
    val requiredNbtKeys: List<String> = emptyList(),
    override val description: String = ""
) : EditOperation()
