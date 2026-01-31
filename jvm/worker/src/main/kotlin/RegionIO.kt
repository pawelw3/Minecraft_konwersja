package mc.editkit.worker

import com.flowpowered.nbt.*
import com.flowpowered.nbt.stream.NBTInputStream
import com.flowpowered.nbt.stream.NBTOutputStream
import java.io.*
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.file.Path
import java.util.zip.Deflater
import java.util.zip.GZIPInputStream
import java.util.zip.Inflater

/**
 * I/O dla plików regionów Anvil (.mca) używając flow-nbt
 */

private const val SECTOR_SIZE = 4096
private const val CHUNK_HEADER_SIZE = 5

/**
 * Wczytuje chunk z pliku regionu
 */
fun readChunk(regionFile: Path, localChunkX: Int, localChunkZ: Int): CompoundMap? {
    if (!regionFile.toFile().exists()) return null
    
    RandomAccessFile(regionFile.toFile(), "r").use { raf ->
        // Pobierz lokalizację chunka z nagłówka
        val index = localChunkX + localChunkZ * 32
        raf.seek((index * 4).toLong())
        
        val offsetBytes = ByteArray(4)
        raf.readFully(offsetBytes)
        
        val sectorOffset = ((offsetBytes[0].toInt() and 0xFF) shl 16) or
                          ((offsetBytes[1].toInt() and 0xFF) shl 8) or
                          (offsetBytes[2].toInt() and 0xFF)
        val sectorCount = offsetBytes[3].toInt() and 0xFF
        
        if (sectorOffset == 0 || sectorCount == 0) {
            return null // Chunk nie istnieje
        }
        
        // Wczytaj dane chunka
        raf.seek((sectorOffset * SECTOR_SIZE).toLong())
        
        val lengthBytes = ByteArray(4)
        raf.readFully(lengthBytes)
        val length = ByteBuffer.wrap(lengthBytes).order(ByteOrder.BIG_ENDIAN).int
        
        val compressionType = raf.readByte().toInt()
        
        if (length < 1) return null
        
        val compressedData = ByteArray(length - 1)
        raf.readFully(compressedData)
        
        // Dekompresja
        val nbtData = when (compressionType) {
            1 -> decompressGzip(compressedData)
            2 -> decompressZlib(compressedData)
            else -> compressedData
        }
        
        // Parsuj NBT
        return parseNBT(nbtData)
    }
}

/**
 * Zapisuje chunk do pliku regionu
 */
fun writeChunk(raf: RandomAccessFile, localChunkX: Int, localChunkZ: Int, nbt: CompoundMap) {
    // Serializuj NBT
    val nbtData = serializeNBT(nbt)
    
    // Kompresja zlib
    val compressed = compressZlib(nbtData)
    
    // Przygotuj dane chunka
    val chunkData = ByteArray(4 + 1 + compressed.size)
    val length = compressed.size + 1
    
    ByteBuffer.wrap(chunkData).order(ByteOrder.BIG_ENDIAN).putInt(length)
    chunkData[4] = 2.toByte() // compression type: zlib
    System.arraycopy(compressed, 0, chunkData, 5, compressed.size)
    
    // Zaokrąglij do wielokrotności sektora
    val sectorCount = (chunkData.size + SECTOR_SIZE - 1) / SECTOR_SIZE
    val paddedChunkData = chunkData.copyOf(sectorCount * SECTOR_SIZE)
    
    // Pobierz aktualną lokalizację chunka
    val index = localChunkX + localChunkZ * 32
    raf.seek((index * 4).toLong())
    
    val offsetBytes = ByteArray(4)
    raf.readFully(offsetBytes)
    
    var sectorOffset = ((offsetBytes[0].toInt() and 0xFF) shl 16) or
                      ((offsetBytes[1].toInt() and 0xFF) shl 8) or
                      (offsetBytes[2].toInt() and 0xFF)
    val oldSectorCount = offsetBytes[3].toInt() and 0xFF
    
    // Sprawdź czy mieści się w starym miejscu
    if (sectorOffset == 0 || sectorCount > oldSectorCount) {
        // Potrzebne nowe miejsce - dopisz na końcu
        sectorOffset = (raf.length() / SECTOR_SIZE).toInt()
        if (raf.length() % SECTOR_SIZE != 0L) {
            sectorOffset++
        }
    }
    
    // Zapisz dane
    raf.seek((sectorOffset * SECTOR_SIZE).toLong())
    raf.write(paddedChunkData)
    
    // Aktualizuj nagłówek
    raf.seek((index * 4).toLong())
    val newOffsetBytes = ByteArray(4)
    newOffsetBytes[0] = ((sectorOffset shr 16) and 0xFF).toByte()
    newOffsetBytes[1] = ((sectorOffset shr 8) and 0xFF).toByte()
    newOffsetBytes[2] = (sectorOffset and 0xFF).toByte()
    newOffsetBytes[3] = sectorCount.toByte()
    raf.write(newOffsetBytes)
    
    // Aktualizuj timestamp (opcjonalnie)
    raf.seek((SECTOR_SIZE + index * 4).toLong())
    val timestamp = (System.currentTimeMillis() / 1000).toInt()
    raf.writeInt(timestamp)
}

/**
 * Tworzy pusty plik regionu
 */
fun createEmptyRegion(regionFile: Path) {
    regionFile.parent.toFile().mkdirs()
    RandomAccessFile(regionFile.toFile(), "rw").use { raf ->
        // Nagłówek z lokalizacjami (8KB)
        raf.setLength((SECTOR_SIZE * 2).toLong())
        raf.write(ByteArray(SECTOR_SIZE * 2))
    }
}

private fun decompressZlib(data: ByteArray): ByteArray {
    val inflater = Inflater()
    inflater.setInput(data)
    
    val output = ByteArrayOutputStream()
    val buffer = ByteArray(8192)
    
    while (!inflater.finished()) {
        val count = inflater.inflate(buffer)
        output.write(buffer, 0, count)
    }
    
    inflater.end()
    return output.toByteArray()
}

private fun decompressGzip(data: ByteArray): ByteArray {
    return ByteArrayInputStream(data).use { bis ->
        GZIPInputStream(bis).use { gis ->
            gis.readBytes()
        }
    }
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

private fun parseNBT(data: ByteArray): CompoundMap? {
    return ByteArrayInputStream(data).use { bis ->
        NBTInputStream(bis, false).use { nbtIn ->
            val tag = nbtIn.readTag()
            if (tag is CompoundTag) {
                tag.value
            } else {
                null
            }
        }
    }
}

private fun serializeNBT(nbt: CompoundMap): ByteArray {
    val baos = ByteArrayOutputStream()
    NBTOutputStream(baos, false).use { nbtOut ->
        nbtOut.writeTag(CompoundTag("", nbt))
    }
    return baos.toByteArray()
}
