package mc.editkit.worker

import org.jglrxavpok.hephaistos.mca.RegionFile
import org.jglrxavpok.hephaistos.nbt.NBTCompound
import org.jglrxavpok.hephaistos.nbt.NBTList
import java.io.RandomAccessFile
import java.nio.file.Paths

/**
 * Test 4: Weryfikacja command block i Tile Entity
 */
fun testCommandBlock(worldPath: String, expectedX: Int, expectedY: Int, expectedZ: Int) {
    println("\nTest 4: Weryfikacja Command Block + TE")
    println("=" * 50)
    
    val chunkX = chunkCoordFromBlock(expectedX)
    val chunkZ = chunkCoordFromBlock(expectedZ)
    val regionX = regionCoordFromChunk(chunkX)
    val regionZ = regionCoordFromChunk(chunkZ)
    
    println("Szukam command blocka na pozycji ($expectedX, $expectedY, $expectedZ)")
    println("Chunk: ($chunkX, $chunkZ), Region: ($regionX, $regionZ)")
    
    val regionFile = Paths.get(worldPath, "region", "r.$regionX.$regionZ.mca")
    if (!regionFile.toFile().exists()) {
        println("❌ FAIL: Brak pliku regionu: $regionFile")
        return
    }
    
    var raf: RandomAccessFile? = null
    try {
        raf = RandomAccessFile(regionFile.toFile(), "r")
        val region = RegionFile(raf, regionX, regionZ, 0, 255)
        
        if (!region.hasChunk(chunkX, chunkZ)) {
            println("❌ FAIL: Chunk ($chunkX, $chunkZ) nie istnieje")
            return
        }
        
        val chunkData = region.getChunkData(chunkX, chunkZ)
        if (chunkData == null) {
            println("❌ FAIL: Nie udało się odczytać danych chunka")
            return
        }
        
        val level = chunkData.getCompound("Level")
        if (level == null) {
            println("❌ FAIL: Brak Level w chunku")
            return
        }
        
        // Sprawdź Tile Entities
        val tileEntities = level.getList<NBTCompound>("TileEntities")
        if (tileEntities == null || tileEntities.size == 0) {
            println("❌ FAIL: Brak Tile Entities w chunku")
            return
        }
        
        println("Znaleziono ${tileEntities.size} Tile Entities:")
        
        var foundCommandBlock = false
        for (i in 0 until tileEntities.size) {
            val te = tileEntities[i]
            val x = te.getInt("x") ?: 0
            val y = te.getInt("y") ?: 0
            val z = te.getInt("z") ?: 0
            val id = te.getString("id") ?: "unknown"
            
            println("  TE[$i]: ($x, $y, $z) id='$id'")
            
            if (x == expectedX && y == expectedY && z == expectedZ) {
                foundCommandBlock = true
                val command = te.getString("Command")
                println("  -> Command Block znaleziony!")
                println("  -> Command: '$command'")
                
                if (command != null && "[ROUNDTRIP]" in command) {
                    println("✅ Test 4 PASS: Command Block z TE ustawiony poprawnie")
                } else {
                    println("❌ Test 4 FAIL: Command nie zawiera '[ROUNDTRIP]'")
                }
            }
        }
        
        if (!foundCommandBlock) {
            println("❌ Test 4 FAIL: Nie znaleziono command blocka na oczekiwanej pozycji")
        }
        
        raf.close()
        
    } catch (e: Exception) {
        println("❌ Test 4 FAIL: Błąd - ${e.message}")
        e.printStackTrace()
    } finally {
        try { raf?.close() } catch (_: Exception) {}
    }
}
