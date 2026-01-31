package mc.editkit.worker

import org.jglrxavpok.hephaistos.mca.RegionFile
import org.jglrxavpok.hephaistos.nbt.NBTCompound
import java.io.RandomAccessFile
import java.nio.file.Paths

/**
 * Test 3: Weryfikacja ustawienia bloku
 */
fun testBlockSet(worldPath: String, expectedX: Int, expectedY: Int, expectedZ: Int, expectedId: Int, expectedMeta: Int) {
    println("\nTest 3: Weryfikacja ustawionego bloku")
    println("=" * 50)
    
    val chunkX = chunkCoordFromBlock(expectedX)
    val chunkZ = chunkCoordFromBlock(expectedZ)
    val regionX = regionCoordFromChunk(chunkX)
    val regionZ = regionCoordFromChunk(chunkZ)
    val localChunkX = localChunkFromChunk(chunkX)
    val localChunkZ = localChunkFromChunk(chunkZ)
    val localX = localBlockFromWorld(expectedX)
    val localY = localBlockFromWorld(expectedY)
    val localZ = localBlockFromWorld(expectedZ)
    val sectionY = chunkCoordFromBlock(expectedY)
    
    println("Pozycja globalna: ($expectedX, $expectedY, $expectedZ)")
    println("Chunk: ($chunkX, $chunkZ), Region: ($regionX, $regionZ), Local chunk: ($localChunkX, $localChunkZ)")
    println("Lokalna pozycja w chunku: ($localX, $localY, $localZ), Sekcja Y: $sectionY")
    
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
        
        val sections = level.getList<NBTCompound>("Sections")
        if (sections == null) {
            println("❌ FAIL: Brak Sections w Level")
            return
        }
        
        // Znajdź sekcję
        var foundSection: NBTCompound? = null
        for (i in 0 until sections.size) {
            val sec = sections[i]
            val yVal = sec.getByte("Y")?.toInt()
            if (yVal == sectionY) {
                foundSection = sec
                break
            }
        }
        
        if (foundSection == null) {
            println("❌ FAIL: Nie znaleziono sekcji Y=$sectionY")
            return
        }
        
        val blocks = foundSection.getByteArray("Blocks")?.copyArray()
        val data = foundSection.getByteArray("Data")?.copyArray()
        
        if (blocks == null || data == null) {
            println("❌ FAIL: Brak Blocks lub Data w sekcji")
            return
        }
        
        val index = (localY * 16 + localZ) * 16 + localX
        val actualId = blocks[index].toInt() and 0xFF
        
        val dataIndex = index shr 1
        val dataValue = data[dataIndex].toInt() and 0xFF
        val actualMeta = if (index and 1 == 0) dataValue and 0x0F else (dataValue shr 4) and 0x0F
        
        println("Odczytano: ID=$actualId, Meta=$actualMeta (spodziewano: ID=$expectedId, Meta=$expectedMeta)")
        
        if (actualId == expectedId && actualMeta == expectedMeta) {
            println("✅ Test 3 PASS: Blok ustawiony poprawnie")
        } else {
            println("❌ Test 3 FAIL: Blok nie zgadza się z oczekiwaniami")
        }
        
        raf.close()
        
    } catch (e: Exception) {
        println("❌ Test 3 FAIL: Błąd - ${e.message}")
        e.printStackTrace()
    } finally {
        try { raf?.close() } catch (_: Exception) {}
    }
}


