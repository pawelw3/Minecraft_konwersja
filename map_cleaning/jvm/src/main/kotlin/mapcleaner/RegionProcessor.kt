package mapcleaner

import org.jglrxavpok.hephaistos.nbt.*
import java.io.RandomAccessFile
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.zip.Deflater
import java.util.zip.Inflater

/**
 * Przetwarza pojedynczy plik regionu (.mca)
 */
class RegionProcessor(private val rules: CleaningRules) {
    
    /**
     * Wynik przetwarzania regionu
     */
    data class RegionResult(
        val chunksProcessed: Int,
        val chunksModified: Int,
        val stats: ChunkCleaner.CleanStats
    )
    
    private val chunkCleaner = ChunkCleaner(rules)
    
    /**
     * Przetwarza plik regionu
     * @param regionFile Ścieżka do pliku .mca
     * @param dryRun Jeśli true - tylko analiza bez zapisu
     * @return RegionResult ze statystykami
     */
    fun processRegion(regionFile: java.io.File, dryRun: Boolean): RegionResult {
        if (!regionFile.exists()) {
            return RegionResult(0, 0, ChunkCleaner.CleanStats())
        }
        
        val mode = if (dryRun) "r" else "rw"
        val raf = RandomAccessFile(regionFile, mode)
        
        try {
            val fileSize = raf.length()
            if (fileSize < 8192) {
                return RegionResult(0, 0, ChunkCleaner.CleanStats())
            }
            
            var chunksProcessed = 0
            var chunksModified = 0
            val totalStats = ChunkCleaner.CleanStats()
            val modifiedChunks = mutableListOf<Pair<Int, ByteArray>>() // (index, compressed_data)
            
            // Przetwórz wszystkie 1024 chunki (32x32)
            for (localZ in 0 until 32) {
                for (localX in 0 until 32) {
                    val index = localX + localZ * 32
                    val result = processChunk(raf, index, dryRun)
                    
                    if (result != null) {
                        chunksProcessed++
                        if (result.modified) {
                            chunksModified++
                            totalStats.blocksRemoved += result.stats.blocksRemoved
                            totalStats.tileEntitiesRemoved += result.stats.tileEntitiesRemoved
                            totalStats.entitiesRemoved += result.stats.entitiesRemoved
                            totalStats.sectionsModified += result.stats.sectionsModified
                            
                            if (!dryRun && result.compressedData != null) {
                                modifiedChunks.add(index to result.compressedData)
                            }
                        }
                    }
                }
            }
            
            // Zapisz zmodyfikowane chunki
            if (!dryRun && modifiedChunks.isNotEmpty()) {
                writeModifiedChunks(raf, modifiedChunks)
            }
            
            return RegionResult(chunksProcessed, chunksModified, totalStats)
            
        } finally {
            raf.close()
        }
    }
    
    /**
     * Wynik przetwarzania pojedynczego chunka
     */
    private data class ChunkProcessResult(
        val modified: Boolean,
        val stats: ChunkCleaner.CleanStats,
        val compressedData: ByteArray?
    )
    
    /**
     * Przetwarza pojedynczy chunk
     */
    private fun processChunk(raf: RandomAccessFile, index: Int, dryRun: Boolean): ChunkProcessResult? {
        // Odczytaj nagłówek chunka
        raf.seek((index * 4).toLong())
        val offsetBytes = ByteArray(4)
        if (raf.read(offsetBytes) != 4) return null
        
        val sectorOffset = ((offsetBytes[0].toInt() and 0xFF) shl 16) or
                          ((offsetBytes[1].toInt() and 0xFF) shl 8) or
                          (offsetBytes[2].toInt() and 0xFF)
        val sectorCount = offsetBytes[3].toInt() and 0xFF
        
        // Jeśli offset = 0, chunk nie istnieje
        if (sectorOffset == 0 || sectorCount == 0) {
            return null
        }
        
        // Odczytaj dane chunka
        val chunkData = readChunkData(raf, sectorOffset) ?: return null
        
        // Parsuj NBT
        val nbt = try {
            NBTReader(chunkData, CompressedProcesser.NONE).read() as? NBTCompound
        } catch (e: Exception) {
            null
        } ?: return null
        
        // Wyczyść chunk
        val cleanResult = chunkCleaner.cleanChunk(nbt)
        
        if (!cleanResult.modified) {
            return ChunkProcessResult(false, cleanResult.stats, null)
        }
        
        // Skompresuj zmodyfikowany chunk
        val compressedData = if (!dryRun) {
            compressChunk(cleanResult.cleanedNbt)
        } else null
        
        return ChunkProcessResult(true, cleanResult.stats, compressedData)
    }
    
    /**
     * Odczytuje dane chunka z pliku
     */
    private fun readChunkData(raf: RandomAccessFile, sectorOffset: Int): ByteArray? {
        return try {
            raf.seek((sectorOffset * 4096).toLong())
            
            val lengthBytes = ByteArray(4)
            raf.readFully(lengthBytes)
            val length = ByteBuffer.wrap(lengthBytes).order(ByteOrder.BIG_ENDIAN).int
            
            val compressionType = raf.readByte().toInt()
            
            if (length < 1 || length > 10 * 1024 * 1024) {
                return null // Za duży lub uszkodzony
            }
            
            val compressedData = ByteArray(length - 1)
            raf.readFully(compressedData)
            
            when (compressionType) {
                1 -> decompressGzip(compressedData)
                2 -> decompressZlib(compressedData)
                else -> compressedData
            }
        } catch (e: Exception) {
            null
        }
    }
    
    /**
     * Kompresuje chunk do zapisu
     */
    private fun compressChunk(nbt: NBTCompound): ByteArray {
        val baos = java.io.ByteArrayOutputStream()
        NBTWriter(baos, CompressedProcesser.NONE).use { it.writeNamed("", nbt) }
        val nbtData = baos.toByteArray()
        
        val compressed = compressZlib(nbtData)
        
        // Format: [length: 4 bytes][compression: 1 byte][data...]
        val result = ByteArray(4 + 1 + compressed.size)
        ByteBuffer.wrap(result).order(ByteOrder.BIG_ENDIAN).putInt(compressed.size + 1)
        result[4] = 2 // zlib compression
        System.arraycopy(compressed, 0, result, 5, compressed.size)
        
        return result
    }
    
    /**
     * Zapisuje zmodyfikowane chunki do pliku
     */
    private fun writeModifiedChunks(
        raf: RandomAccessFile,
        modifiedChunks: List<Pair<Int, ByteArray>>
    ) {
        if (modifiedChunks.isEmpty()) return
        
        println("  Zapisywanie ${modifiedChunks.size} zmodyfikowanych chunków...")
        
        val header = ByteArray(8192) // 4096 offsets + 4096 timestamps
        raf.seek(0)
        raf.readFully(header)
        
        var currentOffset = ((raf.length() + 4095) / 4096).toInt()
        if (currentOffset < 2) currentOffset = 2
        
        var inPlaceCount = 0
        var appendCount = 0
        
        for ((i, pair) in modifiedChunks.withIndex()) {
            val (index, chunkData) = pair
            val newSectorCount = (chunkData.size + 4095) / 4096
            
            // Odczytaj stary offset i rozmiar z nagłówka
            val oldOffset = ((header[index * 4].toInt() and 0xFF) shl 16) or
                           ((header[index * 4 + 1].toInt() and 0xFF) shl 8) or
                           (header[index * 4 + 2].toInt() and 0xFF)
            val oldSectorCount = header[index * 4 + 3].toInt() and 0xFF
            
            // Decyzja: nadpisz w starym miejscu czy dopisz na końcu?
            val (writeOffset, usedInPlace) = if (oldOffset != 0 && newSectorCount <= oldSectorCount) {
                // Mieści się w starych sektorach - nadpisz
                inPlaceCount++
                Pair(oldOffset, true)
            } else {
                // Za duży lub brak starego - dopisz na końcu
                appendCount++
                val offset = currentOffset
                currentOffset += newSectorCount
                Pair(offset, false)
            }
            
            // Aktualizuj nagłówek
            header[index * 4] = ((writeOffset shr 16) and 0xFF).toByte()
            header[index * 4 + 1] = ((writeOffset shr 8) and 0xFF).toByte()
            header[index * 4 + 2] = (writeOffset and 0xFF).toByte()
            header[index * 4 + 3] = newSectorCount.toByte()
            
            // Aktualizuj timestamp
            val timestamp = (System.currentTimeMillis() / 1000).toInt()
            header[4096 + index * 4] = (timestamp shr 24).toByte()
            header[4096 + index * 4 + 1] = (timestamp shr 16).toByte()
            header[4096 + index * 4 + 2] = (timestamp shr 8).toByte()
            header[4096 + index * 4 + 3] = timestamp.toByte()
            
            // Zapisz dane chunka
            raf.seek((writeOffset * 4096).toLong())
            val paddedData = chunkData.copyOf(newSectorCount * 4096)
            raf.write(paddedData)
            
            // Logowanie postępu co 100 chunków
            if (i % 100 == 0 && i > 0) {
                println("    Zapisano $i/${modifiedChunks.size} chunków...")
            }
        }
        
        // Zapisz zaktualizowany nagłówek
        raf.seek(0)
        raf.write(header)
        
        // Przytnij plik do aktualnego rozmiaru
        raf.setLength(currentOffset * 4096L)
        
        println("  Zapis zakończony: ${modifiedChunks.size} chunków (in-place: $inPlaceCount, append: $appendCount)")
    }
    
    private fun decompressZlib(data: ByteArray): ByteArray {
        val inflater = Inflater()
        inflater.setInput(data)
        
        val output = java.io.ByteArrayOutputStream()
        val buffer = ByteArray(8192)
        
        while (!inflater.finished()) {
            val count = inflater.inflate(buffer)
            output.write(buffer, 0, count)
        }
        
        inflater.end()
        return output.toByteArray()
    }
    
    private fun decompressGzip(data: ByteArray): ByteArray {
        return java.io.ByteArrayInputStream(data).use { bis ->
            java.util.zip.GZIPInputStream(bis).use { gis ->
                gis.readBytes()
            }
        }
    }
    
    private fun compressZlib(data: ByteArray): ByteArray {
        val deflater = Deflater()
        deflater.setInput(data)
        deflater.finish()
        
        val output = java.io.ByteArrayOutputStream()
        val buffer = ByteArray(8192)
        
        while (!deflater.finished()) {
            val count = deflater.deflate(buffer)
            output.write(buffer, 0, count)
        }
        
        deflater.end()
        return output.toByteArray()
    }
}
