package mc.editkit.worker

import org.jglrxavpok.hephaistos.mca.RegionFile
import org.jglrxavpok.hephaistos.nbt.*
import org.json.JSONObject
import java.io.File
import java.io.RandomAccessFile
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.file.Path
import java.nio.file.Paths
import java.util.zip.Deflater
import java.util.zip.GZIPInputStream
import java.util.zip.Inflater

/**
 * Edytor świata Minecraft 1.7.10 używający Hephaistos
 * Dla formatu 1.7.10 pracujemy bezpośrednio na NBT, nie używając ChunkColumn (który jest dla nowszych wersji)
 */
class WorldEditor(private val worldPath: String) {
    private val regionPath = Paths.get(worldPath, "region")
    private val modifiedRegions = mutableMapOf<Path, RegionData>()
    
    data class RegionData(
        val regionFile: RegionFile,
        val raf: RandomAccessFile,
        val chunks: MutableMap<Pair<Int, Int>, ChunkData> = mutableMapOf()
    )
    
    data class ChunkData(
        var nbt: NBTCompound? = null,
        var modified: Boolean = false
    )
    
    init {
        if (!regionPath.toFile().exists()) {
            regionPath.toFile().mkdirs()
        }
    }
    
    /**
     * Ustawia blok na danej pozycji (format 1.7.10)
     */
    fun setBlock(x: Int, y: Int, z: Int, blockId: Int, meta: Int = 0) {
        val (chunkX, chunkZ) = blockToChunk(x, z)
        val (regionX, regionZ) = chunkToRegion(chunkX, chunkZ)
        val localChunkX = chunkX and 31
        val localChunkZ = chunkZ and 31
        
        val regionFilePath = regionPath.resolve("r.$regionX.$regionZ.mca")
        
        val chunk = getOrCreateChunk(regionFilePath, regionX, regionZ, localChunkX, localChunkZ, chunkX, chunkZ)
        
        val sectionY = y shr 4
        val localY = y and 15
        val localX = x and 15
        val localZ = z and 15
        
        // Pobierz Level compound
        val level = chunk.nbt?.getCompound("Level") 
            ?: throw IllegalStateException("Chunk nie ma tagu Level")
        
        // Pobierz sekcje jako listę
        val sectionsList = level.getList<NBTCompound>("Sections")
        val sections = if (sectionsList != null) {
            mutableListOf<NBTCompound>().apply { 
                for (i in 0 until sectionsList.size) {
                    add(sectionsList[i])
                }
            }
        } else mutableListOf()
        
        // Znajdź lub utwórz sekcję
        var sectionIndex = -1
        var section: NBTCompound? = null
        for (i in sections.indices) {
            val s = sections[i]
            val yVal = s.getByte("Y")?.toInt()
            if (yVal == sectionY) {
                section = s
                sectionIndex = i
                break
            }
        }
        
        if (section == null) {
            section = createSectionNBT(sectionY)
            sections.add(section)
            sectionIndex = sections.size - 1
        }
        
        // Modyfikuj bloki
        val blocksArray = section.getByteArray("Blocks")
        val blocks = if (blocksArray != null) blocksArray.copyArray() else ByteArray(4096)
        
        val dataArray = section.getByteArray("Data")
        val data = if (dataArray != null) dataArray.copyArray() else ByteArray(2048)
        
        val index = (localY * 16 + localZ) * 16 + localX
        blocks[index] = (blockId and 0xFF).toByte()
        
        // Nibble array dla metadata
        val dataIndex = index shr 1
        val oldData = data[dataIndex].toInt() and 0xFF
        val newNibble = if (index and 1 == 0) {
            (oldData and 0xF0) or (meta and 0x0F)
        } else {
            (oldData and 0x0F) or ((meta and 0x0F) shl 4)
        }
        data[dataIndex] = newNibble.toByte()
        
        // Zaktualizuj sekcję - stwórz nowy NBT (immutable)
        val newSection = NBT.Compound { sec ->
            sec.setByte("Y", sectionY.toByte())
            sec.setByteArray("Blocks", blocks)
            sec.setByteArray("Data", data)
            
            // Zachowaj istniejące światło jeśli istnieje
            val skyLight = section.getByteArray("SkyLight")
            if (skyLight != null) {
                sec.setByteArray("SkyLight", skyLight.copyArray())
            } else {
                sec.setByteArray("SkyLight", ByteArray(2048) { 0xFF.toByte() })
            }
            
            val blockLight = section.getByteArray("BlockLight")
            if (blockLight != null) {
                sec.setByteArray("BlockLight", blockLight.copyArray())
            } else {
                sec.setByteArray("BlockLight", ByteArray(2048))
            }
        }
        
        // Zaktualizuj listę sekcji
        sections[sectionIndex] = newSection
        
        val newSections = NBT.List(NBTType.TAG_Compound, sections)
        
        // Zaktualizuj Level
        val newLevel = NBT.Compound { lvl ->
            // Kopiuj wszystkie istniejące pola poza Sections
            for (key in level.keys) {
                if (key != "Sections") {
                    lvl[key] = level[key]!!
                }
            }
            lvl["Sections"] = newSections
        }
        
        // Zaktualizuj chunk
        val newChunk = NBT.Compound { root ->
            for (key in (chunk.nbt?.keys ?: emptySet())) {
                if (key != "Level") {
                    root[key] = chunk.nbt!![key]!!
                }
            }
            root["Level"] = newLevel
        }
        
        chunk.nbt = newChunk
        chunk.modified = true
        
        println("setBlock($x, $y, $z): id=$blockId meta=$meta")
    }
    
    fun setTileEntity(x: Int, y: Int, z: Int, nbtData: JSONObject) {
        val (chunkX, chunkZ) = blockToChunk(x, z)
        val (regionX, regionZ) = chunkToRegion(chunkX, chunkZ)
        val localChunkX = chunkX and 31
        val localChunkZ = chunkZ and 31
        
        val regionFilePath = regionPath.resolve("r.$regionX.$regionZ.mca")
        val chunk = getOrCreateChunk(regionFilePath, regionX, regionZ, localChunkX, localChunkZ, chunkX, chunkZ)
        
        val level = chunk.nbt?.getCompound("Level")
            ?: throw IllegalStateException("Chunk nie ma tagu Level")
        
        // Pobierz istniejące TileEntities
        val teList = level.getList<NBTCompound>("TileEntities")
        val tileEntities = if (teList != null) {
            mutableListOf<NBTCompound>().apply {
                for (i in 0 until teList.size) {
                    add(teList[i])
                }
            }
        } else mutableListOf()
        
        // Usuń istniejące TE na tej samej pozycji
        val filtered = tileEntities.filter { te ->
            val tex = te.getInt("x") ?: 0
            val tey = te.getInt("y") ?: 0
            val tez = te.getInt("z") ?: 0
            !(tex == x && tey == y && tez == z)
        }.toMutableList()
        
        // Utwórz nowe TE
        val newTe = NBT.Compound { te ->
            te.setInt("x", x)
            te.setInt("y", y)
            te.setInt("z", z)
            
            for (key in nbtData.keys()) {
                val value = nbtData.get(key)
                when (value) {
                    is String -> te.setString(key, value)
                    is Int -> te.setInt(key, value)
                    is Long -> te.setLong(key, value)
                    is Byte -> te.setByte(key, value)
                    is Double -> te.setDouble(key, value)
                    is Float -> te.setFloat(key, value)
                }
            }
        }
        
        filtered.add(newTe)
        
        // Zaktualizuj Level
        val newLevel = NBT.Compound { lvl ->
            for (key in level.keys) {
                if (key != "TileEntities") {
                    lvl[key] = level[key]!!
                }
            }
            lvl["TileEntities"] = NBT.List(NBTType.TAG_Compound, filtered)
        }
        
        // Zaktualizuj chunk
        val newChunk = NBT.Compound { root ->
            for (key in (chunk.nbt?.keys ?: emptySet())) {
                if (key != "Level") {
                    root[key] = chunk.nbt!![key]!!
                }
            }
            root["Level"] = newLevel
        }
        
        chunk.nbt = newChunk
        chunk.modified = true
        
        println("setTileEntity($x, $y, $z): id=${nbtData.optString("id", "unknown")}")
    }
    
    fun commit() {
        println("Zapisywanie zmian...")
        
        for ((path, regionData) in modifiedRegions) {
            var savedChunks = 0
            
            for ((localPos, chunkData) in regionData.chunks) {
                if (chunkData.modified && chunkData.nbt != null) {
                    try {
                        writeChunkDirect(regionData.raf, localPos.first, localPos.second, chunkData.nbt!!)
                        savedChunks++
                    } catch (e: Exception) {
                        println("Błąd zapisu chunk ${localPos.first},${localPos.second}: ${e.message}")
                        e.printStackTrace()
                    }
                }
            }
            
            regionData.raf.close()
            println("Zapisano region: ${path.fileName} ($savedChunks chunków)")
        }
        
        modifiedRegions.clear()
        println("Zapis zakończony.")
    }
    
    private fun getOrCreateChunk(
        regionFilePath: Path,
        regionX: Int,
        regionZ: Int,
        localChunkX: Int,
        localChunkZ: Int,
        globalChunkX: Int,
        globalChunkZ: Int
    ): ChunkData {
        val regionData = modifiedRegions.getOrPut(regionFilePath) {
            if (!regionFilePath.parent.toFile().exists()) {
                regionFilePath.parent.toFile().mkdirs()
            }
            
            val raf = RandomAccessFile(regionFilePath.toFile().apply {
                if (!exists()) createNewFile()
            }, "rw")
            
            val regionFile = RegionFile(raf, regionX, regionZ, 0, 255)
            RegionData(regionFile, raf)
        }
        
        val key = Pair(localChunkX, localChunkZ)
        
        return regionData.chunks.getOrPut(key) {
            val existingNbt = try {
                readChunkNBT(regionData.raf, localChunkX, localChunkZ)
            } catch (e: Exception) {
                null
            }
            
            if (existingNbt != null) {
                ChunkData(existingNbt)
            } else {
                ChunkData(createEmptyChunkNBT(globalChunkX, globalChunkZ))
            }
        }
    }
    
    private fun readChunkNBT(raf: RandomAccessFile, localChunkX: Int, localChunkZ: Int): NBTCompound? {
        val index = localChunkX + localChunkZ * 32
        raf.seek((index * 4).toLong())
        
        val offsetBytes = ByteArray(4)
        if (raf.read(offsetBytes) != 4) return null
        
        val sectorOffset = ((offsetBytes[0].toInt() and 0xFF) shl 16) or
                          ((offsetBytes[1].toInt() and 0xFF) shl 8) or
                          (offsetBytes[2].toInt() and 0xFF)
        val sectorCount = offsetBytes[3].toInt() and 0xFF
        
        if (sectorOffset == 0 || sectorCount == 0) {
            return null
        }
        
        raf.seek((sectorOffset * 4096).toLong())
        
        val lengthBytes = ByteArray(4)
        raf.readFully(lengthBytes)
        val length = ByteBuffer.wrap(lengthBytes).order(ByteOrder.BIG_ENDIAN).int
        
        val compressionType = raf.readByte().toInt()
        
        if (length < 1 || length > 1024 * 1024) return null
        
        val compressedData = ByteArray(length - 1)
        raf.readFully(compressedData)
        
        val uncompressedData = when (compressionType) {
            1 -> decompressGzip(compressedData)
            2 -> decompressZlib(compressedData)
            else -> compressedData
        }
        
        return NBTReader(uncompressedData, CompressedProcesser.NONE).read() as? NBTCompound
    }
    
    private fun writeChunkDirect(raf: RandomAccessFile, localChunkX: Int, localChunkZ: Int, nbt: NBTCompound) {
        val baos = java.io.ByteArrayOutputStream()
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
    
    private fun createEmptyChunkNBT(chunkX: Int, chunkZ: Int): NBTCompound {
        return NBT.Compound { root ->
            root.setInt("DataVersion", 0)
            root["Level"] = NBT.Compound { level ->
                level.setInt("xPos", chunkX)
                level.setInt("zPos", chunkZ)
                level.setLong("LastUpdate", 0)
                level.setByte("TerrainPopulated", 1)
                level["Sections"] = NBT.List(NBTType.TAG_Compound, emptyList())
                level["TileEntities"] = NBT.List(NBTType.TAG_Compound, emptyList())
                level["Entities"] = NBT.List(NBTType.TAG_Compound, emptyList())
                level.setByteArray("Biomes", ByteArray(256))
                level.setIntArray("HeightMap", IntArray(256))
            }
        }
    }
    
    private fun createSectionNBT(y: Int): NBTCompound {
        return NBT.Compound { section ->
            section.setByte("Y", y.toByte())
            section.setByteArray("Blocks", ByteArray(4096))
            section.setByteArray("Data", ByteArray(2048))
            section.setByteArray("SkyLight", ByteArray(2048) { 0xFF.toByte() })
            section.setByteArray("BlockLight", ByteArray(2048))
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
            GZIPInputStream(bis).use { gis ->
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
    
    private fun blockToChunk(x: Int, z: Int): Pair<Int, Int> {
        return Pair(x shr 4, z shr 4)
    }
    
    private fun chunkToRegion(chunkX: Int, chunkZ: Int): Pair<Int, Int> {
        return Pair(
            if (chunkX >= 0) chunkX shr 5 else (chunkX + 1) shr 5 - 1,
            if (chunkZ >= 0) chunkZ shr 5 else (chunkZ + 1) shr 5 - 1
        )
    }
}
