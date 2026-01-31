package mc.editkit.worker

import org.jglrxavpok.hephaistos.mca.RegionFile
import org.jglrxavpok.hephaistos.nbt.*
import java.io.ByteArrayOutputStream
import java.io.RandomAccessFile
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.file.Paths
import java.util.zip.Deflater

/**
 * Komendy testowe dla Hephaistos
 */

fun listRegions(worldPath: String) {
    println("Test 1: Open world + list regions")
    println("=" * 50)
    
    val regionPath = Paths.get(worldPath, "region")
    if (!regionPath.toFile().exists()) {
        println("❌ FAIL: Katalog region nie istnieje: $regionPath")
        return
    }
    
    val regionFiles = regionPath.toFile().listFiles { f -> f.name.endsWith(".mca") }
    if (regionFiles.isNullOrEmpty()) {
        println("❌ FAIL: Brak plików .mca w katalogu region")
        return
    }
    
    println("Znaleziono ${regionFiles.size} plików regionów:")
    
    var successCount = 0
    for (regionFile in regionFiles.sortedBy { it.name }) {
        var raf: RandomAccessFile? = null
        try {
            raf = RandomAccessFile(regionFile, "r")
            val name = regionFile.name
            
            // Parsuj nazwę r.X.Z.mca
            val parts = name.removePrefix("r.").removeSuffix(".mca").split(".")
            val regionX = parts[0].toInt()
            val regionZ = parts[1].toInt()
            
            // Spróbuj otworzyć przez Hephaistos
            val region = RegionFile(raf, regionX, regionZ, 0, 255)
            
            // Policz chunki - używamy globalnych koordynatów chunków
            var chunkCount = 0
            val chunkStartX = regionX * 32
            val chunkStartZ = regionZ * 32
            
            for (lz in 0..31) {
                for (lx in 0..31) {
                    val globalCx = chunkStartX + lx
                    val globalCz = chunkStartZ + lz
                    if (region.hasChunk(globalCx, globalCz)) {
                        chunkCount++
                    }
                }
            }
            
            // Spróbuj odczytać pierwszy chunk
            var firstChunkRead = false
            for (lz in 0..31) {
                for (lx in 0..31) {
                    val globalCx = chunkStartX + lx
                    val globalCz = chunkStartZ + lz
                    if (region.hasChunk(globalCx, globalCz)) {
                        val chunkData = region.getChunkData(globalCx, globalCz)
                        if (chunkData != null) {
                            firstChunkRead = true
                            // Sprawdź czy ma Level
                            if (chunkData.containsKey("Level")) {
                                println("  ✅ $name: $chunkCount chunków, pierwszy chunk OK")
                            } else {
                                println("  ⚠️  $name: $chunkCount chunków, brak Level w chunku")
                            }
                            break
                        }
                    }
                }
                if (firstChunkRead) break
            }
            
            if (!firstChunkRead) {
                println("  ⚠️  $name: $chunkCount chunków, nie udało się odczytać pierwszego chunka")
            }
            
            raf.close()
            successCount++
            
        } catch (e: Exception) {
            println("  ❌ ${regionFile.name}: Błąd - ${e.message}")
            e.printStackTrace()
        } finally {
            try { raf?.close() } catch (_: Exception) {}
        }
    }
    
    println("=" * 50)
    if (successCount == regionFiles.size) {
        println("✅ Test 1 PASS: Wszystkie regiony odczytane poprawnie")
    } else {
        println("❌ Test 1 FAIL: $successCount/${regionFiles.size} regionów odczytanych")
    }
}

fun testReadWriteRoundtrip(worldPath: String) {
    println("\nTest 2: Read → Write unchanged → Read again")
    println("=" * 50)
    
    val testRegionFile = Paths.get(worldPath, "region", "r.0.0.mca")
    if (!testRegionFile.toFile().exists()) {
        println("❌ SKIP: Brak regionu r.0.0.mca do testu")
        return
    }
    
    // Skopiuj plik do tymczasowego
    val tempFile = Paths.get(worldPath, "region", "r.0.0.test.mca")
    testRegionFile.toFile().copyTo(tempFile.toFile(), overwrite = true)
    
    var raf: RandomAccessFile? = null
    try {
        raf = RandomAccessFile(tempFile.toFile(), "rw")
        val region = RegionFile(raf, 0, 0, 0, 255)
        
        // Znajdź pierwszy chunk
        var foundChunk = false
        var testChunkX = 0
        var testChunkZ = 0
        var originalNbt: NBTCompound? = null
        
        for (cz in 0..31) {
            for (cx in 0..31) {
                val globalCx = cx
                val globalCz = cz
                if (region.hasChunk(globalCx, globalCz)) {
                    val chunkData = region.getChunkData(globalCx, globalCz)
                    if (chunkData != null) {
                        foundChunk = true
                        testChunkX = globalCx
                        testChunkZ = globalCz
                        originalNbt = chunkData
                        println("Znaleziono chunk ($globalCx, $globalCz) w regionie 0,0")
                        println("  - NBT keys: ${chunkData.keys}")
                        break
                    }
                }
            }
            if (foundChunk) break
        }
        
        if (!foundChunk || originalNbt == null) {
            println("❌ SKIP: Nie znaleziono chunku do testu")
            return
        }
        
        // Zapisz chunk bezpośrednio przez NBT (nie używając ChunkColumn który wymaga DataVersion)
        // Używamy własnej funkcji zapisu z WorldEditor
        writeChunkDirect(raf, testChunkX and 31, testChunkZ and 31, originalNbt)
        println("Zapisano chunk z powrotem (bezpośrednio przez NBT)")
        
        // Odczytaj ponownie przez RegionFile
        val chunkData2 = region.getChunkData(testChunkX, testChunkZ)
        if (chunkData2 != null) {
            // Sprawdź czy kluczowe dane są zachowane
            val level1 = originalNbt.getCompound("Level")
            val level2 = chunkData2.getCompound("Level")
            
            if (level1 != null && level2 != null) {
                val x1 = level1.getInt("xPos")
                val x2 = level2.getInt("xPos")
                val z1 = level1.getInt("zPos")
                val z2 = level2.getInt("zPos")
                
                if (x1 == x2 && z1 == z2) {
                    println("✅ Test 2 PASS: Round-trip zadziałał, koordynaty zachowane ($x1, $z1)")
                } else {
                    println("❌ Test 2 FAIL: Koordynaty się nie zgadzają: ($x1, $z1) vs ($x2, $z2)")
                }
            } else {
                println("❌ Test 2 FAIL: Brak Level w jednym z odczytów")
            }
        } else {
            println("❌ Test 2 FAIL: Nie udało się odczytać po zapisie")
        }
        
        raf.close()
        
    } catch (e: Exception) {
        println("❌ Test 2 FAIL: Błąd - ${e.message}")
        e.printStackTrace()
    } finally {
        try { raf?.close() } catch (_: Exception) {}
        try { tempFile.toFile().delete() } catch (_: Exception) {}
    }
}

/**
 * Zapisuje chunk bezpośrednio do pliku regionu (low-level, kompatybilny z 1.7.10)
 */
private fun writeChunkDirect(raf: RandomAccessFile, localChunkX: Int, localChunkZ: Int, nbt: NBTCompound) {
    val baos = ByteArrayOutputStream()
    NBTWriter(baos, CompressedProcesser.NONE).use { it.writeNamed("", nbt) }
    val nbtData = baos.toByteArray()
    
    val compressed = compressZlib(nbtData)
    
    val chunkData = ByteArray(4 + 1 + compressed.size)
    val length = compressed.size + 1
    
    ByteBuffer.wrap(chunkData).order(ByteOrder.BIG_ENDIAN).putInt(length)
    chunkData[4] = 2.toByte()
    System.arraycopy(compressed, 0, chunkData, 5, compressed.size)
    
    val sectorCount = (chunkData.size + 4096 - 1) / 4096
    val paddedChunkData = chunkData.copyOf(sectorCount * 4096)
    
    val index = localChunkX + localChunkZ * 32
    raf.seek((index * 4).toLong())
    
    val offsetBytes = ByteArray(4)
    val hasExisting = raf.read(offsetBytes) == 4
    
    var sectorOffset = if (hasExisting) {
        ((offsetBytes[0].toInt() and 0xFF) shl 16) or
        ((offsetBytes[1].toInt() and 0xFF) shl 8) or
        (offsetBytes[2].toInt() and 0xFF)
    } else 0
    val oldSectorCount = if (hasExisting) offsetBytes[3].toInt() and 0xFF else 0
    
    if (sectorOffset == 0 || sectorCount > oldSectorCount) {
        sectorOffset = (raf.length() / 4096).toInt()
        if (raf.length() % 4096 != 0L) {
            sectorOffset++
        }
    }
    
    raf.seek((sectorOffset * 4096).toLong())
    raf.write(paddedChunkData)
    
    raf.seek((index * 4).toLong())
    val newOffsetBytes = ByteArray(4)
    newOffsetBytes[0] = ((sectorOffset shr 16) and 0xFF).toByte()
    newOffsetBytes[1] = ((sectorOffset shr 8) and 0xFF).toByte()
    newOffsetBytes[2] = (sectorOffset and 0xFF).toByte()
    newOffsetBytes[3] = sectorCount.toByte()
    raf.write(newOffsetBytes)
    
    raf.seek((4096 + index * 4).toLong())
    val timestamp = (System.currentTimeMillis() / 1000).toInt()
    raf.writeInt(timestamp)
}

private fun compressZlib(data: ByteArray): ByteArray {
    val deflater = Deflater()
    deflater.setInput(data)
    deflater.finish()
    
    val output = ByteArrayOutputStream()
    val buffer = ByteArray(8192)
    
    while (!deflater.finished()) {
        val count = deflater.deflate(buffer)
        output.write(buffer, 0, count)
    }
    
    deflater.end()
    return output.toByteArray()
}


