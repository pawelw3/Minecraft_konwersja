package mapcleaner

import org.jglrxavpok.hephaistos.nbt.*

/**
 * Czyści pojedynczy chunk z modowych bloków, TileEntities i Entities
 */
class ChunkCleaner(private val rules: CleaningRules) {
    
    /**
     * Wynik czyszczenia chunka
     */
    data class CleanResult(
        val modified: Boolean,
        val cleanedNbt: NBTCompound,
        val stats: CleanStats
    )
    
    /**
     * Statystyki czyszczenia
     */
    data class CleanStats(
        var blocksRemoved: Int = 0,
        var tileEntitiesRemoved: Int = 0,
        var entitiesRemoved: Int = 0,
        var sectionsModified: Int = 0
    ) {
        fun total() = blocksRemoved + tileEntitiesRemoved + entitiesRemoved
    }
    
    /**
     * Pozycja bloku w świecie
     */
    data class BlockPos(val x: Int, val y: Int, val z: Int)
    
    /**
     * Czyści chunk z modowej zawartości
     * @param root NBTCompound chunka (root tag zawierający Level)
     * @return CleanResult zawierający zmodyfikowany NBT i statystyki
     */
    fun cleanChunk(root: NBTCompound): CleanResult {
        val stats = CleanStats()
        val modifiedPositions = mutableSetOf<BlockPos>()
        
        // Pobierz Level compound
        val level = root.getCompound("Level") 
            ?: return CleanResult(false, root, stats)
        
        // Wyczyść bloki w sekcjach
        val (newSections, sectionsModified) = cleanSections(level, stats, modifiedPositions)
        
        // Wyczyść TileEntities
        val newTileEntities = cleanTileEntities(level, stats, modifiedPositions)
        
        // Wyczyść Entities
        val newEntities = cleanEntities(level, stats)
        
        // Sprawdź czy były zmiany
        val modified = sectionsModified || 
                       stats.tileEntitiesRemoved > 0 || 
                       stats.entitiesRemoved > 0
        
        if (!modified) {
            return CleanResult(false, root, stats)
        }
        
        // Zbuduj nowy Level compound
        val newLevel = NBT.Compound { lvl ->
            // Kopiuj wszystkie istniejące pola
            for (key in level.keys) {
                when (key) {
                    "Sections" -> lvl["Sections"] = newSections
                    "TileEntities" -> if (newTileEntities != null) lvl["TileEntities"] = newTileEntities
                    "Entities" -> if (newEntities != null) lvl["Entities"] = newEntities
                    else -> lvl[key] = level[key]!!
                }
            }
        }
        
        // Zbuduj nowy root compound
        val newRoot = NBT.Compound { r ->
            for (key in root.keys) {
                if (key == "Level") {
                    r["Level"] = newLevel
                } else {
                    r[key] = root[key]!!
                }
            }
        }
        
        return CleanResult(true, newRoot, stats)
    }
    
    /**
     * Czyści sekcje chunka
     */
    private fun cleanSections(
        level: NBTCompound,
        stats: CleanStats,
        modifiedPositions: MutableSet<BlockPos>
    ): Pair<NBTList<NBTCompound>, Boolean> {
        val sectionsList = level.getList<NBTCompound>("Sections")
            ?: return Pair(NBT.List(NBTType.TAG_Compound, emptyList()), false)
        
        val chunkX = level.getInt("xPos") ?: 0
        val chunkZ = level.getInt("zPos") ?: 0
        
        val newSections = mutableListOf<NBTCompound>()
        var anyModified = false
        
        for (sectionNbt in sectionsList) {
            val y = sectionNbt.getByte("Y")?.toInt() ?: continue
            
            val blocks = sectionNbt.getByteArray("Blocks")?.copyArray()
            val addArray = sectionNbt.getByteArray("Add")?.copyArray()
            val data = sectionNbt.getByteArray("Data")?.copyArray()
            val skyLight = sectionNbt.getByteArray("SkyLight")?.copyArray()
            val blockLight = sectionNbt.getByteArray("BlockLight")?.copyArray()
            
            if (blocks == null) continue
            
            var sectionModified = false
            var newAdd = addArray?.copyOf()
            val newData = data?.copyOf() ?: ByteArray(2048)
            
            // Przeskanuj wszystkie bloki w sekcji
            for (idx in blocks.indices) {
                val fullId = BlockCodec.readFullId(blocks, addArray, idx)
                
                if (rules.isModBlock(fullId)) {
                    // Zastąp blok
                    val x = idx and 0x0F
                    val z = (idx shr 4) and 0x0F
                    val localY = (idx shr 8) and 0x0F
                    val worldY = y * 16 + localY
                    
                    newAdd = BlockCodec.writeFullId(
                        blocks, newAdd, newData, idx,
                        rules.replacementBlock, 0
                    )
                    
                    modifiedPositions.add(BlockPos(chunkX * 16 + x, worldY, chunkZ * 16 + z))
                    stats.blocksRemoved++
                    sectionModified = true
                }
            }
            
            // Usuń puste Add (jeśli wszystkie high nibble = 0)
            if (newAdd != null && newAdd.all { it == 0.toByte() }) {
                newAdd = null
            }
            
            if (sectionModified) {
                stats.sectionsModified++
                anyModified = true
                
                // Zbuduj nową sekcję
                val newSection = NBT.Compound { sec ->
                    sec.setByte("Y", y.toByte())
                    sec.setByteArray("Blocks", blocks)
                    if (newAdd != null) {
                        sec.setByteArray("Add", newAdd)
                    }
                    sec.setByteArray("Data", newData)
                    if (skyLight != null) sec.setByteArray("SkyLight", skyLight)
                    if (blockLight != null) sec.setByteArray("BlockLight", blockLight)
                }
                newSections.add(newSection)
            } else {
                newSections.add(sectionNbt)
            }
        }
        
        return Pair(NBT.List<NBTCompound>(NBTType.TAG_Compound, newSections), anyModified)
    }
    
    /**
     * Czyści TileEntities
     */
    private fun cleanTileEntities(
        level: NBTCompound,
        stats: CleanStats,
        modifiedPositions: Set<BlockPos>
    ): NBTList<NBTCompound>? {
        if (!rules.cleanTileEntities) return null
        
        val teList = level.getList<NBTCompound>("TileEntities")
            ?: return null
        
        val chunkX = level.getInt("xPos") ?: 0
        val chunkZ = level.getInt("zPos") ?: 0
        
        val newTileEntities = mutableListOf<NBTCompound>()
        
        for (te in teList) {
            val id = te.getString("id")
            val x = te.getInt("x") ?: 0
            val y = te.getInt("y") ?: 0
            val z = te.getInt("z") ?: 0
            val pos = BlockPos(x, y, z)
            
            // Usuń TE jeśli:
            // 1. Jest na pozycji gdzie usunęliśmy blok
            // 2. Ma modowe ID
            val shouldRemove = pos in modifiedPositions || rules.isModTileEntity(id)
            
            if (shouldRemove) {
                stats.tileEntitiesRemoved++
            } else {
                newTileEntities.add(te)
            }
        }
        
        return NBT.List<NBTCompound>(NBTType.TAG_Compound, newTileEntities)
    }
    
    /**
     * Czyści Entities
     */
    private fun cleanEntities(
        level: NBTCompound,
        stats: CleanStats
    ): NBTList<NBTCompound>? {
        if (!rules.cleanEntities) return null
        
        val entityList = level.getList<NBTCompound>("Entities")
            ?: return null
        
        val newEntities = mutableListOf<NBTCompound>()
        
        for (entity in entityList) {
            val id = entity.getString("id")
            
            if (rules.isModEntity(id)) {
                stats.entitiesRemoved++
            } else {
                newEntities.add(entity)
            }
        }
        
        return NBT.List<NBTCompound>(NBTType.TAG_Compound, newEntities)
    }
}
