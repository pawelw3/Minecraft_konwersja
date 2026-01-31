package mc.editkit.worker

import org.jglrxavpok.hephaistos.mca.RegionFile
import org.jglrxavpok.hephaistos.nbt.NBTCompound
import java.io.RandomAccessFile
import java.nio.file.Paths

/**
 * Weryfikacja testu 2 (długi kabel z 12 repeaterami)
 */
fun verifyTest2(worldPath: String) {
    println("\n" + "=".repeat(60))
    println("WERYFIKACJA TESTU 2 (DŁUGI KABEL)")
    println("=".repeat(60))
    
    val targetX = 752
    val targetY = 70
    val targetZ = -164
    
    val chunkX = chunkCoordFromBlock(targetX)
    val chunkZ = chunkCoordFromBlock(targetZ)
    val regionX = regionCoordFromChunk(chunkX)
    val regionZ = regionCoordFromChunk(chunkZ)
    
    println("Szukam Command Blocka na pozycji ($targetX, $targetY, $targetZ)")
    println("Chunk: ($chunkX, $chunkZ), Region: ($regionX, $regionZ)")
    
    val regionFile = Paths.get(worldPath, "region", "r.$regionX.$regionZ.mca")
    if (!regionFile.toFile().exists()) {
        println("[FAIL] Brak pliku regionu: $regionFile")
        return
    }
    
    var raf: RandomAccessFile? = null
    try {
        raf = RandomAccessFile(regionFile.toFile(), "r")
        val region = RegionFile(raf, regionX, regionZ, 0, 255)
        
        if (!region.hasChunk(chunkX, chunkZ)) {
            println("[FAIL] Chunk ($chunkX, $chunkZ) nie istnieje")
            return
        }
        
        val chunkData = region.getChunkData(chunkX, chunkZ)
        if (chunkData == null) {
            println("[FAIL] Nie udało się odczytać danych chunka")
            return
        }
        
        val level = chunkData.getCompound("Level")
        if (level == null) {
            println("[FAIL] Brak Level w chunku")
            return
        }
        
        // Sprawdź Tile Entities
        val tileEntities = level.getList<NBTCompound>("TileEntities")
        if (tileEntities == null || tileEntities.size == 0) {
            println("[FAIL] Brak Tile Entities w chunku")
            return
        }
        
        println("\nZnaleziono ${tileEntities.size} Tile Entities w chunku:")
        
        var foundCommandBlock = false
        for (i in 0 until tileEntities.size) {
            val te = tileEntities[i]
            val x = te.getInt("x") ?: 0
            val y = te.getInt("y") ?: 0
            val z = te.getInt("z") ?: 0
            val id = te.getString("id") ?: "unknown"
            
            if (id == "Control" || (x == targetX && y == targetY && z == targetZ)) {
                println("  TE[$i]: ($x, $y, $z) id='$id'")
                
                if (x == targetX && y == targetY && z == targetZ) {
                    foundCommandBlock = true
                    val command = te.getString("Command")
                    val customName = te.getString("CustomName")
                    
                    println("  -> Command Block ZNALEZIONY!")
                    println("  -> Command: '$command'")
                    println("  -> CustomName: '$customName'")
                    
                    println("\n" + "=".repeat(60))
                    if (command != null && "[TEST2]" in command) {
                        println("[PASS] Command Block z TE ustawiony poprawnie!")
                        println("       Komenda TEST2 znaleziona.")
                    } else {
                        println("[WARN] Command Block znaleziony, ale inna komenda")
                    }
                    println("=".repeat(60))
                }
            }
        }
        
        if (!foundCommandBlock) {
            println("\n[FAIL] Nie znaleziono Command Blocka")
        }
        
        // Dodatkowo sprawdź czy dźwignia jest włączona
        println("\n--- Sprawdzanie dźwigni ---")
        val leverChunkX = chunkCoordFromBlock(700)
        val leverChunkZ = chunkCoordFromBlock(-164)
        if (region.hasChunk(leverChunkX, leverChunkZ)) {
            val leverChunk = region.getChunkData(leverChunkX, leverChunkZ)
            val leverLevel = leverChunk?.getCompound("Level")
            val sections = leverLevel?.getList<NBTCompound>("Sections")
            
            if (sections != null) {
                val sectionY = 70 / 16  // 4
                for (s in 0 until sections.size) {
                    val section = sections[s]
                    if (section.getByte("Y")?.toInt() == sectionY) {
                        val blocks = section.getByteArray("Blocks")
                        if (blocks != null) {
                            // Pozycja 700, 70, -164 w chunku
                            val localX = 700 % 16  // 12
                            val localY = 70 % 16   // 6
                            val localZ = (-164) % 16  // -4 -> 12 (z ujemnych)
                            val actualLocalZ = if (localZ < 0) localZ + 16 else localZ
                            
                            val index = (localY * 16 + actualLocalZ) * 16 + localX
                            if (index < blocks.size) {
                                val blockId = blocks[index].toInt() and 0xFF
                                println("Dźwignia (700, 70, -164): ID=$blockId (oczekiwano 69)")
                                if (blockId == 69) {
                                    println("[PASS] Dźwignia jest na miejscu!")
                                }
                            }
                        }
                        break
                    }
                }
            }
        }
        
        raf.close()
        
    } catch (e: Exception) {
        println("[FAIL] Błąd - ${e.message}")
        e.printStackTrace()
    } finally {
        try { raf?.close() } catch (_: Exception) {}
    }
}
