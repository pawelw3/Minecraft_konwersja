package mc.editkit.worker

import org.jglrxavpok.hephaistos.mca.RegionFile
import org.jglrxavpok.hephaistos.nbt.NBTCompound
import java.io.RandomAccessFile
import java.nio.file.Paths

/**
 * Szczegółowa analiza wszystkich chunków w zakresie -2 do 2
 */
fun inspectAllNearbyChunks(worldPath: String) {
    val path = Paths.get(worldPath)
    
    println("=".repeat(70))
    println("ANALIZA WSZYSTKICH CHUNKÓW W ZAKRESIE -2 do 2")
    println("=".repeat(70))
    
    val results = mutableMapOf<Pair<Int, Int>, Int>()
    
    for (cx in -2..2) {
        for (cz in -2..2) {
            val count = countRedstoneInChunk(path, cx, cz)
            results[Pair(cx, cz)] = count
        }
    }
    
    // Wyświetl mapę
    println("\nMapa chunków (X→, Z↓) - liczba elementów redstone:")
    println("     " + (-2..2).joinToString(" ") { String.format("%2d", it) })
    
    for (cz in -2..2) {
        val row = StringBuilder()
        row.append(String.format("Z%2d: ", cz))
        for (cx in -2..2) {
            val count = results[Pair(cx, cz)] ?: 0
            if (count > 0) {
                row.append(String.format("%2d ", count))
            } else {
                row.append(" . ")
            }
        }
        println(row)
    }
    
    // Szczegóły dla chunków z redstone
    println("\n--- Chunki z redstone ---")
    results.filter { it.value > 0 }.forEach { (chunk, count) ->
        println("Chunk (${chunk.first}, ${chunk.second}): $count elementów")
    }
    
    val total = results.values.sum()
    println("\nRAZEM: $total elementów redstone w ${results.count { it.value > 0 }} chunkach")
}

private fun countRedstoneInChunk(path: java.nio.file.Path, chunkX: Int, chunkZ: Int): Int {
    val regionX = regionCoordFromChunk(chunkX)
    val regionZ = regionCoordFromChunk(chunkZ)
    val localChunkX = localChunkFromChunk(chunkX)
    val localChunkZ = localChunkFromChunk(chunkZ)
    
    val regionFile = path.resolve("region/r.${regionX}.${regionZ}.mca")
    if (!regionFile.toFile().exists()) return -1
    
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
        return -2
    }
}
