package mc.editkit.worker

import org.jglrxavpok.hephaistos.mca.RegionFile
import org.jglrxavpok.hephaistos.nbt.NBTCompound
import java.io.RandomAccessFile
import java.nio.file.Paths

/**
 * Weryfikacja testowego układu redstone z command blockiem
 */
fun verifyRedstoneTest(worldPath: String) {
    println("\n" + "=".repeat(60))
    println("WERYFIKACJA TESTOWEGO UKŁADU REDSTONE")
    println("=".repeat(60))
    
    val targetX = 60
    val targetY = 64
    val targetZ = 50
    
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
            
            // Pokaż tylko Command Blocki lub TE na naszej pozycji
            if (id == "Control" || (x == targetX && y == targetY && z == targetZ)) {
                println("  TE[$i]: ($x, $y, $z) id='$id'")
                
                if (x == targetX && y == targetY && z == targetZ) {
                    foundCommandBlock = true
                    val command = te.getString("Command")
                    val customName = te.getString("CustomName")
                    val trackOutput = te.getByte("TrackOutput")
                    
                    println("  -> Command Block ZNALEZIONY!")
                    println("  -> Command: '$command'")
                    println("  -> CustomName: '$customName'")
                    println("  -> TrackOutput: $trackOutput")
                    
                    println("\n" + "=".repeat(60))
                    if (command != null && "[TEST_REDSTONE]" in command) {
                        println("[PASS] Command Block z TE ustawiony poprawnie!")
                        println("       Testowa komenda znaleziona w polu Command.")
                    } else {
                        println("[WARN] Command Block znaleziony, ale komenda nie zawiera '[TEST_REDSTONE]'")
                    }
                    println("=".repeat(60))
                }
            }
        }
        
        if (!foundCommandBlock) {
            println("\n[FAIL] Nie znaleziono Command Blocka na pozycji ($targetX, $targetY, $targetZ)")
        }
        
        raf.close()
        
    } catch (e: Exception) {
        println("[FAIL] Błąd - ${e.message}")
        e.printStackTrace()
    } finally {
        try { raf?.close() } catch (_: Exception) {}
    }
}
