package mapcleaner

import org.jglrxavpok.hephaistos.nbt.*
import java.io.RandomAccessFile
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.zip.Deflater
import java.util.zip.Inflater

/**
 * Przetwarza pojedynczy plik regionu (.mca) z defragmentacją
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
    
    companion object {
        const val SECTOR_SIZE = 4096
        const val HEADER_SIZE = 8192 // 4096 offsets + 4096 timestamps
    }
    
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
            if (fileSize < HEADER_SIZE) {
                return RegionResult(0, 0, ChunkCleaner.CleanStats())
            }
            
            var chunksProcessed = 0
            var chunksModified = 0
            val totalStats = ChunkCleaner.CleanStats()
            
            // Zbierz wszystkie chunki do przetworzenia
            val chunkResults = mutableListOf<ChunkData>()
            
            // Przetwórz wszystkie 1024 chunki (32x32)
            for (localZ in 0 until 32) {
                for (localX in 0 until 32) {
                    val index = localX + localZ * 32
                    val chunkData = readChunk(raf, index)
                    
                    if (chunkData != null) {
                        chunksProcessed++
                        val result = processChunkData(chunkData)
                        
                        if (result != null) {
                            chunksModified++
                            totalStats.blocksRemoved += result.stats.blocksRemoved
                            totalStats.tileEntitiesRemoved += result.stats.tileEntitiesRemoved
                            totalStats.entitiesRemoved += result.stats.entitiesRemoved
                            totalStats.sectionsModified += result.stats.sectionsModified
                            
                            if (!dryRun) {
                                chunkResults.add(ChunkData(index, result.compressedData, chunkData.oldOffset, chunkData.oldSectorCount))
                            }
                        }
                    }
                }
            }
            
            // Zapisz zmodyfikowane chunki z defragmentacją
            if (!dryRun && chunkResults.isNotEmpty()) {
                writeRegionDefragmented(raf, chunkResults)
            }
            
            return RegionResult(chunksProcessed, chunksModified, totalStats)
            
        } finally {
            raf.close()
        }
    }
    
    /**
     * Dane chunka do przetworzenia
     */
    private data class ChunkData(
        val index: Int,
        val compressedData: ByteArray,
        val oldOffset: Int,
        val oldSectorCount: Int
    )
    
    /**
     * Wynik przetwarzania chunka
     */
    private data class ChunkProcessResult(
        val stats: ChunkCleaner.CleanStats,
        val compressedData: ByteArray
    )
    
    /**
     * Odczytuje chunk z pliku
     */
    private fun readChunk(raf: RandomAccessFile, index: Int): ChunkData? {
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
        
        return ChunkData(index, chunkData, sectorOffset, sectorCount)
    }
    
    /**
     * Przetwarza dane chunka (czyści z modów)
     */
    private fun processChunkData(chunkData: ChunkData): ChunkProcessResult? {
        // Parsuj NBT - format: [length: 4][compression: 1][data...]
        val nbt = try {
            parseChunkNBT(chunkData.compressedData)
        } catch (e: Exception) {
            // Logowanie błędu w debugowaniu
            // println("Błąd parsowania chunka ${chunkData.index}: ${e.message}")
            return null
        } ?: return null
        
        // Wyczyść chunk
        val cleanResult = chunkCleaner.cleanChunk(nbt)
        
        if (!cleanResult.modified) {
            return null
        }
        
        // Skompresuj zmodyfikowany chunk (używamy zlib jak oryginał)
        val compressedData = compressChunk(cleanResult.cleanedNbt)
        
        return ChunkProcessResult(cleanResult.stats, compressedData)
    }
    
    /**
     * Parsuje NBT z danych chunka
     * Format: [length: 4 bytes][compression: 1 byte][compressed data...]
     */
    private fun parseChunkNBT(data: ByteArray): NBTCompound? {
        if (data.size < 5) return null
        
        val length = ByteBuffer.wrap(data, 0, 4).order(ByteOrder.BIG_ENDIAN).int
        val compressionType = data[4].toInt() and 0xFF
        val compressedData = data.copyOfRange(5, data.size)
        
        // Dekompresuj dane
        val decompressedData = when (compressionType) {
            1 -> decompressGzip(compressedData)
            2 -> decompressZlib(compressedData)
            else -> compressedData // Brak kompresji
        } ?: return null
        
        // Parsuj NBT
        return try {
            NBTReader(decompressedData.inputStream(), CompressedProcesser.NONE).read() as? NBTCompound
        } catch (e: Exception) {
            null
        }
    }
    
    /**
     * Zapisuje region z defragmentacją - wszystkie chunki są upakowane jeden po drugim
     */
    private fun writeRegionDefragmented(raf: RandomAccessFile, modifiedChunks: List<ChunkData>) {
        if (modifiedChunks.isEmpty()) return
        
        // Utwórz mapę index -> nowe dane
        val modifiedMap = modifiedChunks.associateBy { it.index }
        
        // Przygotuj nowy nagłówek i dane
        val newHeader = ByteArray(HEADER_SIZE)
        val newData = mutableListOf<ByteArray>()
        
        var currentSector = 2 // Nagłówek to sektory 0 i 1
        
        // Przetwórz wszystkie 1024 chunki
        for (index in 0 until 1024) {
            val chunk = modifiedMap[index]
            
            if (chunk != null) {
                // Ten chunk był modyfikowany
                val sectorCount = (chunk.compressedData.size + SECTOR_SIZE - 1) / SECTOR_SIZE
                
                // Zapisz offset w nagłówku
                newHeader[index * 4] = ((currentSector shr 16) and 0xFF).toByte()
                newHeader[index * 4 + 1] = ((currentSector shr 8) and 0xFF).toByte()
                newHeader[index * 4 + 2] = (currentSector and 0xFF).toByte()
                newHeader[index * 4 + 3] = sectorCount.toByte()
                
                // Zapisz timestamp
                val timestamp = (System.currentTimeMillis() / 1000).toInt()
                newHeader[4096 + index * 4] = (timestamp shr 24).toByte()
                newHeader[4096 + index * 4 + 1] = (timestamp shr 16).toByte()
                newHeader[4096 + index * 4 + 2] = (timestamp shr 8).toByte()
                newHeader[4096 + index * 4 + 3] = timestamp.toByte()
                
                // Dodaj dane do listy (z paddingiem do wielokrotności sektora)
                val paddedData = chunk.compressedData.copyOf(sectorCount * SECTOR_SIZE)
                newData.add(paddedData)
                
                currentSector += sectorCount
            } else {
                // Chunk nie był modyfikowany - odczytaj go z oryginalnego pliku
                val originalChunk = readOriginalChunk(raf, index)
                
                if (originalChunk != null) {
                    val sectorCount = (originalChunk.size + SECTOR_SIZE - 1) / SECTOR_SIZE
                    
                    // Zapisz offset w nagłówku
                    newHeader[index * 4] = ((currentSector shr 16) and 0xFF).toByte()
                    newHeader[index * 4 + 1] = ((currentSector shr 8) and 0xFF).toByte()
                    newHeader[index * 4 + 2] = (currentSector and 0xFF).toByte()
                    newHeader[index * 4 + 3] = sectorCount.toByte()
                    
                    // Zachowaj oryginalny timestamp
                    raf.seek((4096 + index * 4).toLong())
                    val tsBytes = ByteArray(4)
                    raf.readFully(tsBytes)
                    newHeader[4096 + index * 4] = tsBytes[0]
                    newHeader[4096 + index * 4 + 1] = tsBytes[1]
                    newHeader[4096 + index * 4 + 2] = tsBytes[2]
                    newHeader[4096 + index * 4 + 3] = tsBytes[3]
                    
                    // Dodaj dane z paddingiem
                    val paddedData = originalChunk.copyOf(sectorCount * SECTOR_SIZE)
                    newData.add(paddedData)
                    
                    currentSector += sectorCount
                } else {
                    // Pusty chunk - zapisz zera
                    newHeader[index * 4] = 0
                    newHeader[index * 4 + 1] = 0
                    newHeader[index * 4 + 2] = 0
                    newHeader[index * 4 + 3] = 0
                }
            }
        }
        
        // Zapisz nowy plik
        raf.seek(0)
        raf.write(newHeader)
        
        for (data in newData) {
            raf.write(data)
        }
        
        // Przytnij plik do nowego rozmiaru
        raf.setLength(currentSector * SECTOR_SIZE.toLong())
    }
    
    /**
     * Odczytuje oryginalny chunk z pliku
     */
    private fun readOriginalChunk(raf: RandomAccessFile, index: Int): ByteArray? {
        return try {
            raf.seek((index * 4).toLong())
            val offsetBytes = ByteArray(4)
            if (raf.read(offsetBytes) != 4) return null
            
            val sectorOffset = ((offsetBytes[0].toInt() and 0xFF) shl 16) or
                              ((offsetBytes[1].toInt() and 0xFF) shl 8) or
                              (offsetBytes[2].toInt() and 0xFF)
            val sectorCount = offsetBytes[3].toInt() and 0xFF
            
            if (sectorOffset == 0 || sectorCount == 0) return null
            
            // Odczytaj dane chunka (razem z nagłówkiem length+compression)
            raf.seek((sectorOffset * SECTOR_SIZE).toLong())
            val chunkData = ByteArray(sectorCount * SECTOR_SIZE)
            raf.readFully(chunkData)
            
            // Zwróć tylko faktyczne dane (bez paddingu na końcu sektora)
            val length = ByteBuffer.wrap(chunkData, 0, 4).order(ByteOrder.BIG_ENDIAN).int
            if (length < 1 || length > 10 * 1024 * 1024) return null
            
            chunkData.copyOf(4 + 1 + length - 1) // length + compression + data
        } catch (e: Exception) {
            null
        }
    }
    
    /**
     * Odczytuje dane chunka z pliku (razem z nagłówkiem)
     */
    private fun readChunkData(raf: RandomAccessFile, sectorOffset: Int): ByteArray? {
        return try {
            raf.seek((sectorOffset * SECTOR_SIZE).toLong())
            
            val lengthBytes = ByteArray(4)
            raf.readFully(lengthBytes)
            val length = ByteBuffer.wrap(lengthBytes).order(ByteOrder.BIG_ENDIAN).int
            
            if (length < 1 || length > 10 * 1024 * 1024) {
                return null
            }
            
            val compressionType = raf.readByte().toInt()
            val compressedData = ByteArray(length - 1)
            raf.readFully(compressedData)
            
            // Zwracamy dane z nagłówkiem: [length: 4][compression: 1][data...]
            val result = ByteArray(4 + 1 + compressedData.size)
            System.arraycopy(lengthBytes, 0, result, 0, 4)
            result[4] = compressionType.toByte()
            System.arraycopy(compressedData, 0, result, 5, compressedData.size)
            
            result
        } catch (e: Exception) {
            null
        }
    }
    
    /**
     * Kompresuje chunk do zapisu (używając zlib jak oryginalne chunki)
     */
    private fun compressChunk(nbt: NBTCompound): ByteArray {
        // Najpierw serializuj NBT do bajtów
        val baos = java.io.ByteArrayOutputStream()
        NBTWriter(baos, CompressedProcesser.NONE).use { it.writeNamed("", nbt) }
        val nbtData = baos.toByteArray()
        
        // Kompresuj zlib
        val compressed = compressZlib(nbtData)
        
        // Format: [length: 4 bytes][compression: 1 byte][data...]
        val result = ByteArray(4 + 1 + compressed.size)
        ByteBuffer.wrap(result).order(ByteOrder.BIG_ENDIAN).putInt(compressed.size + 1)
        result[4] = 2 // zlib compression
        System.arraycopy(compressed, 0, result, 5, compressed.size)
        
        return result
    }
    
    private fun decompressZlib(data: ByteArray): ByteArray? {
        return try {
            val inflater = Inflater()
            inflater.setInput(data)
            
            val output = java.io.ByteArrayOutputStream()
            val buffer = ByteArray(8192)
            
            while (!inflater.finished()) {
                val count = inflater.inflate(buffer)
                if (count == 0 && !inflater.finished()) {
                    // Problem z dekompresją
                    break
                }
                output.write(buffer, 0, count)
            }
            
            inflater.end()
            output.toByteArray()
        } catch (e: Exception) {
            null
        }
    }
    
    private fun decompressGzip(data: ByteArray): ByteArray? {
        return try {
            java.io.ByteArrayInputStream(data).use { bis ->
                java.util.zip.GZIPInputStream(bis).use { gis ->
                    gis.readBytes()
                }
            }
        } catch (e: Exception) {
            null
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
