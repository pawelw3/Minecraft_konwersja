package mc.editkit.worker

import com.flowpowered.nbt.*
import org.json.JSONObject
import java.io.RandomAccessFile
import java.nio.file.Path
import java.nio.file.Paths

/**
 * Edytor świata Minecraft 1.7.10 używający flow-nbt
 */
class WorldEditor(private val worldPath: String) {
    private val regionPath = Paths.get(worldPath, "region")
    private val modifiedRegions = mutableMapOf<Path, RegionData>()
    
    data class RegionData(
        val chunks: MutableMap<Pair<Int, Int>, ChunkData> = mutableMapOf()
    )
    
    data class ChunkData(
        var nbt: CompoundMap? = null,
        var modified: Boolean = false
    )
    
    /**
     * Ustawia blok na danej pozycji
     */
    fun setBlock(x: Int, y: Int, z: Int, blockId: Int, meta: Int = 0) {
        val (chunkX, chunkZ) = blockToChunk(x, z)
        val (regionX, regionZ) = chunkToRegion(chunkX, chunkZ)
        val localChunkX = chunkX and 31
        val localChunkZ = chunkZ and 31
        
        val regionFile = regionPath.resolve("r.$regionX.$regionZ.mca")
        
        val chunk = getOrCreateChunk(regionFile, localChunkX, localChunkZ, chunkX, chunkZ)
        
        val sectionY = y shr 4
        val localY = y and 15
        val localX = x and 15
        val localZ = z and 15
        
        val level = chunk.nbt?.get("Level") as? CompoundMap ?: chunk.nbt!!
        val sectionsTag = level.get("Sections") as? ListTag<*>
        val sections = if (sectionsTag != null) {
            convertToCompoundList(sectionsTag)
        } else {
            mutableListOf<CompoundTag>()
        }
        
        var section = findSection(sections, sectionY)
        if (section == null) {
            section = createSection(sectionY)
            sections.add(section)
            level["Sections"] = ListTag("Sections", CompoundTag::class.java, sections)
        }
        
        val sectionMap = section.value
        val blocks = sectionMap.get("Blocks") as? ByteArrayTag ?: ByteArrayTag("Blocks", ByteArray(4096))
        val data = sectionMap.get("Data") as? ByteArrayTag ?: ByteArrayTag("Data", ByteArray(2048))
        
        val index = (localY * 16 + localZ) * 16 + localX
        blocks.value[index] = (blockId and 0xFF).toByte()
        
        val dataIndex = index shr 1
        val oldData = data.value[dataIndex].toInt() and 0xFF
        val newNibble = if (index and 1 == 0) {
            (oldData and 0xF0) or (meta and 0x0F)
        } else {
            (oldData and 0x0F) or ((meta and 0x0F) shl 4)
        }
        data.value[dataIndex] = newNibble.toByte()
        
        sectionMap["Blocks"] = blocks
        sectionMap["Data"] = data
        
        chunk.modified = true
        
        println("setBlock($x, $y, $z): id=$blockId meta=$meta")
    }
    
    fun setTileEntity(x: Int, y: Int, z: Int, nbtData: JSONObject) {
        val (chunkX, chunkZ) = blockToChunk(x, z)
        val (regionX, regionZ) = chunkToRegion(chunkX, chunkZ)
        val localChunkX = chunkX and 31
        val localChunkZ = chunkZ and 31
        
        val regionFile = regionPath.resolve("r.$regionX.$regionZ.mca")
        val chunk = getOrCreateChunk(regionFile, localChunkX, localChunkZ, chunkX, chunkZ)
        
        val level = chunk.nbt?.get("Level") as? CompoundMap ?: chunk.nbt!!
        val teTag = level.get("TileEntities") as? ListTag<*>
        val tileEntities = if (teTag != null) {
            convertToCompoundList(teTag)
        } else {
            mutableListOf<CompoundTag>()
        }
        
        val filtered = mutableListOf<CompoundTag>()
        for (te in tileEntities) {
            val teMap = te.value
            val tex = (teMap.get("x") as? IntTag)?.value ?: 0
            val tey = (teMap.get("y") as? IntTag)?.value ?: 0
            val tez = (teMap.get("z") as? IntTag)?.value ?: 0
            if (tex != x || tey != y || tez != z) {
                filtered.add(te)
            }
        }
        
        val newTeMap = CompoundMap()
        newTeMap["x"] = IntTag("x", x)
        newTeMap["y"] = IntTag("y", y)
        newTeMap["z"] = IntTag("z", z)
        
        for (key in nbtData.keys()) {
            val value = nbtData.get(key)
            when (value) {
                is String -> newTeMap[key] = StringTag(key, value)
                is Int -> newTeMap[key] = IntTag(key, value)
                is Long -> newTeMap[key] = LongTag(key, value)
                is Byte -> newTeMap[key] = ByteTag(key, value)
            }
        }
        
        filtered.add(CompoundTag("", newTeMap))
        level["TileEntities"] = ListTag("TileEntities", CompoundTag::class.java, filtered)
        
        chunk.modified = true
        
        println("setTileEntity($x, $y, $z): id=${nbtData.getString("id")}")
    }
    
    fun commit() {
        println("Zapisywanie zmian...")
        
        for ((regionFile, regionData) in modifiedRegions) {
            if (!regionFile.toFile().exists()) {
                createEmptyRegion(regionFile)
            }
            
            val raf = RandomAccessFile(regionFile.toFile(), "rw")
            
            for ((localPos, chunkData) in regionData.chunks) {
                if (chunkData.modified && chunkData.nbt != null) {
                    writeChunk(raf, localPos.first, localPos.second, chunkData.nbt!!)
                }
            }
            
            raf.close()
            println("Zapisano region: ${regionFile.fileName}")
        }
        
        println("Zapis zakończony.")
    }
    
    private fun getOrCreateChunk(
        regionFile: Path,
        localChunkX: Int,
        localChunkZ: Int,
        globalChunkX: Int,
        globalChunkZ: Int
    ): ChunkData {
        val regionData = modifiedRegions.getOrPut(regionFile) { RegionData() }
        val key = Pair(localChunkX, localChunkZ)
        
        return regionData.chunks.getOrPut(key) {
            if (regionFile.toFile().exists()) {
                val chunk = readChunk(regionFile, localChunkX, localChunkZ)
                if (chunk != null) {
                    return@getOrPut ChunkData(chunk)
                }
            }
            ChunkData(createNewChunk(globalChunkX, globalChunkZ))
        }
    }
    
    private fun createNewChunk(chunkX: Int, chunkZ: Int): CompoundMap {
        val level = CompoundMap()
        level["xPos"] = IntTag("xPos", chunkX)
        level["zPos"] = IntTag("zPos", chunkZ)
        level["LastUpdate"] = LongTag("LastUpdate", 0)
        level["TerrainPopulated"] = ByteTag("TerrainPopulated", 1)
        level["Sections"] = ListTag("Sections", CompoundTag::class.java, emptyList())
        level["TileEntities"] = ListTag("TileEntities", CompoundTag::class.java, emptyList())
        level["Biomes"] = ByteArrayTag("Biomes", ByteArray(256))
        
        val root = CompoundMap()
        root["Level"] = CompoundTag("Level", level)
        root["DataVersion"] = IntTag("DataVersion", 0)
        
        return root
    }
    
    private fun createSection(y: Int): CompoundTag {
        val section = CompoundMap()
        section["Y"] = ByteTag("Y", y.toByte())
        section["Blocks"] = ByteArrayTag("Blocks", ByteArray(4096))
        section["Data"] = ByteArrayTag("Data", ByteArray(2048))
        section["SkyLight"] = ByteArrayTag("SkyLight", ByteArray(2048) { 0xFF.toByte() })
        section["BlockLight"] = ByteArrayTag("BlockLight", ByteArray(2048))
        return CompoundTag("", section)
    }
    
    private fun findSection(sections: List<CompoundTag>, y: Int): CompoundTag? {
        for (section in sections) {
            val sectionY = (section.value.get("Y") as? ByteTag)?.value?.toInt() ?: continue
            if (sectionY == y) {
                return section
            }
        }
        return null
    }
    
    @Suppress("UNCHECKED_CAST")
    private fun convertToCompoundList(tag: ListTag<*>): MutableList<CompoundTag> {
        val result = mutableListOf<CompoundTag>()
        val size = (tag as ListTag<Tag<*>>).length()
        for (i in 0 until size) {
            val item = tag.get(i)
            if (item is CompoundTag) {
                result.add(item)
            }
        }
        return result
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
