package mc.editkit.worker

import org.jglrxavpok.hephaistos.nbt.NBTCompound
import org.jglrxavpok.hephaistos.nbt.NBTReader
import org.jglrxavpok.hephaistos.nbt.CompressedProcesser
import java.io.RandomAccessFile
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.zip.Inflater

/**
 * Niskopoziomowy czytnik chunków bezpośrednio z plików .mca
 * Obejście błędu Hephaistos w obsłudze chunków ujemnych
 */
class LowLevelChunkReader(private val regionFile: java.io.File) {
    
    /**
     * Czyta chunk bezpośrednio z pliku regionu
     * @param localChunkX lokalny X w regionie (0-31)
     * @param localChunkZ lokalny Z w regionie (0-31)
     * @return NBTCompound lub null jeśli chunk nie istnieje
     */
    fun readChunk(localChunkX: Int, localChunkZ: Int): NBTCompound? {
        val raf = RandomAccessFile(regionFile, "r")
        
        try {
            // Indeks chunka w tablicy lokalizacji
            val index = localChunkX + localChunkZ * 32
            
            // Odczytaj offset z nagłówka (4 bajty na chunk)
            raf.seek((index * 4).toLong())
            val offsetBytes = ByteArray(4)
            if (raf.read(offsetBytes) != 4) return null
            
            // Big-endian: 3 bajty offset + 1 bajt sektor count
            val sectorOffset = ((offsetBytes[0].toInt() and 0xFF) shl 16) or
                              ((offsetBytes[1].toInt() and 0xFF) shl 8) or
                              (offsetBytes[2].toInt() and 0xFF)
            val sectorCount = offsetBytes[3].toInt() and 0xFF
            
            // Jeśli offset = 0, chunk nie istnieje
            if (sectorOffset == 0 || sectorCount == 0) {
                return null
            }
            
            // Przejdź do danych chunka
            raf.seek((sectorOffset * 4096).toLong())
            
            // Odczytaj długość (4 bajty, big-endian)
            val lengthBytes = ByteArray(4)
            raf.readFully(lengthBytes)
            val length = ByteBuffer.wrap(lengthBytes).order(ByteOrder.BIG_ENDIAN).int
            
            // Typ kompresji (1 bajt)
            val compressionType = raf.readByte().toInt()
            
            if (length < 1 || length > 1024 * 1024) {
                return null // Nieprawidłowa długość
            }
            
            // Odczytaj skompresowane dane
            val compressedData = ByteArray(length - 1)
            raf.readFully(compressedData)
            
            // Dekompresja
            val uncompressedData = when (compressionType) {
                1 -> decompressGzip(compressedData)
                2 -> decompressZlib(compressedData)
                else -> compressedData
            }
            
            // Parsuj NBT
            return NBTReader(uncompressedData, CompressedProcesser.NONE).read() as? NBTCompound
            
        } catch (e: Exception) {
            System.err.println("Błąd odczytu chunk ($localChunkX, $localChunkZ): ${e.message}")
            return null
        } finally {
            raf.close()
        }
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
}
