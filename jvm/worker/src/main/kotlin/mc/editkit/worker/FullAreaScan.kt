package mc.editkit.worker

import org.jglrxavpok.hephaistos.mca.RegionFile
import org.jglrxavpok.hephaistos.nbt.NBTCompound
import java.io.RandomAccessFile
import java.nio.file.Paths

/**
 * Pełne skanowanie obszaru -5 do 4 (chunki) = -80 do 64 bloki
 * Pokrywa zakres -70 do 70 z zapasem
 */
fun scanFullArea(worldPath: String) {
    val path = Paths.get(worldPath)
    
    println("=".repeat(70))
    println("PEŁNE SKANOWANIE OBSZARU")
    println("Chunki: -5 do 4 (zakres bloków: -80 do 80)")
    println("=".repeat(70))
    
    val chunkResults = mutableListOf<Triple<Int, Int, Int>>() // cx, cz, count
    
    for (cx in -5..4) {
        for (cz in -5..4) {
            val count = analyzeChunkForRedstone(path, cx, cz)
            if (count > 0) {
                chunkResults.add(Triple(cx, cz, count))
            }
        }
    }
    
    // Wyświetl wyniki
    println("\nZnaleziono ${chunkResults.size} chunków z redstone:")
    println()
    
    chunkResults.forEach { (cx, cz, count) ->
        val blockX1 = cx * 16
        val blockX2 = blockX1 + 15
        val blockZ1 = cz * 16
        val blockZ2 = blockZ1 + 15
        println("Chunk ($cx, $cz): $count elementów")
        println("  Zakres bloków: X=$blockX1..$blockX2, Z=$blockZ1..$blockZ2")
        
        // Szczegóły pozycji
        val positions = getRedstonePositions(path, cx, cz)
        val byY = positions.groupBy { it.second }.toSortedMap()
        byY.forEach { (y, posList) ->
            println("  Y=$y: ${posList.size} elementów")
            posList.take(5).forEach { p ->
                println("    (${p.first}, ${p.second}, ${p.third})")
            }
            if (posList.size > 5) println("    ... i ${posList.size - 5} więcej")
        }
        println()
    }
    
    val total = chunkResults.sumOf { it.third }
    println("=".repeat(70))
    println("RAZEM: $total elementów redstone w ${chunkResults.size} chunkach")
    println("=".repeat(70))
}

private fun analyzeChunkForRedstone(path: java.nio.file.Path, chunkX: Int, chunkZ: Int): Int {
    val regionX = regionCoordFromChunk(chunkX)
    val regionZ = regionCoordFromChunk(chunkZ)
    val localChunkX = localChunkFromChunk(chunkX)
    val localChunkZ = localChunkFromChunk(chunkZ)
    
    val regionFile = path.resolve("region/r.${regionX}.${regionZ}.mca")
    if (!regionFile.toFile().exists()) return 0
    
    try {
        val raf = RandomAccessFile(regionFile.toFile(), "r")
        RegionFile(raf, regionX, regionZ, 0, 255).use { region ->
            val chunkData = region.getChunkData(localChunkX, localChunkZ) ?: return 0
            val level = chunkData.getCompound("Level") ?: return 0
            val sections = level.getList<NBTCompound>("Sections") ?: return 0
            
            var count = 0
            for (section in sections) {
                val blocks = section.getByteArray("Blocks")?.copyArray() ?: continue
                for (b in blocks) {
                    val id = b.toInt() and 0xFF
                    if (id in RedstoneAnalyzer.REDSTONE_COMPONENTS) count++
                }
            }
            return count
        }
    } catch (e: Exception) {
        return 0
    }
}

private fun getRedstonePositions(
    path: java.nio.file.Path, 
    chunkX: Int, 
    chunkZ: Int
): List<Triple<Int, Int, Int>> {
    val regionX = regionCoordFromChunk(chunkX)
    val regionZ = regionCoordFromChunk(chunkZ)
    val localChunkX = localChunkFromChunk(chunkX)
    val localChunkZ = localChunkFromChunk(chunkZ)
    
    val positions = mutableListOf<Triple<Int, Int, Int>>()
    
    val regionFile = path.resolve("region/r.${regionX}.${regionZ}.mca")
    val raf = RandomAccessFile(regionFile.toFile(), "r")
    RegionFile(raf, regionX, regionZ, 0, 255).use { region ->
        val chunkData = region.getChunkData(localChunkX, localChunkZ) ?: return emptyList()
        val level = chunkData.getCompound("Level") ?: return emptyList()
        val sections = level.getList<NBTCompound>("Sections") ?: return emptyList()
        
        for (section in sections) {
            val secY = section.getByte("Y")?.toInt() ?: continue
            val blocks = section.getByteArray("Blocks")?.copyArray() ?: continue
            
            for (y in 0..15) {
                for (z in 0..15) {
                    for (x in 0..15) {
                        val idx = (y * 16 + z) * 16 + x
                        val blockId = blocks[idx].toInt() and 0xFF
                        
                        if (blockId in RedstoneAnalyzer.REDSTONE_COMPONENTS) {
                            val worldX = (chunkX * 16) + x
                            val worldY = (secY * 16) + y
                            val worldZ = (chunkZ * 16) + z
                            positions.add(Triple(worldX, worldY, worldZ))
                        }
                    }
                }
            }
        }
    }
    
    return positions
}
