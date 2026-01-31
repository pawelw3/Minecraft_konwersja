package mc.editkit.worker

import org.jglrxavpok.hephaistos.mca.RegionFile
import org.jglrxavpok.hephaistos.nbt.NBTCompound
import java.io.RandomAccessFile
import java.nio.file.Path
import java.nio.file.Paths

/**
 * Szczegółowa inspekcja konkretnych chunków
 */
fun inspectChunks(worldPath: String, chunks: List<Pair<Int, Int>>) {
    val path = Paths.get(worldPath)
    
    println("=".repeat(70))
    println("INSPEKCJA KONKRETNYCH CHUNKÓW")
    println("=".repeat(70))
    
    var totalRedstone = 0
    
    for ((chunkX, chunkZ) in chunks) {
        println("\n--- Chunk ($chunkX, $chunkZ) ---")
        
        val regionX = regionCoordFromChunk(chunkX)
        val regionZ = regionCoordFromChunk(chunkZ)
        val localChunkX = localChunkFromChunk(chunkX)
        val localChunkZ = localChunkFromChunk(chunkZ)
        
        println("  Region: r.$regionX.$regionZ")
        println("  Local: ($localChunkX, $localChunkZ)")
        
        val regionFile = path.resolve("region/r.${regionX}.${regionZ}.mca")
        if (!regionFile.toFile().exists()) {
            println("  ❌ Region NIE ISTNIEJE")
            continue
        }
        
        try {
            val raf = RandomAccessFile(regionFile.toFile(), "r")
            RegionFile(raf, regionX, regionZ, 0, 255).use { region ->
                val chunkData = region.getChunkData(localChunkX, localChunkZ)
                
                if (chunkData == null) {
                    println("  ❌ Chunk nie istnieje w regionie (niezapisany)")
                    return@use
                }
                
                val level = chunkData.getCompound("Level")
                if (level == null) {
                    println("  ❌ Brak Level w chunku")
                    return@use
                }
                
                // Szczegółowa analiza sekcji
                val sections = level.getList<NBTCompound>("Sections")
                if (sections == null || sections.isEmpty()) {
                    println("  ❌ Brak sekcji (pusty chunk)")
                    return@use
                }
                
                println("  ✅ Chunk istnieje (${sections.size} sekcji)")
                
                val redstoneBlocks = mutableListOf<Triple<Int, Int, Int>>()
                
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
                                    redstoneBlocks.add(Triple(worldX, worldY, worldZ))
                                }
                            }
                        }
                    }
                }
                
                if (redstoneBlocks.isEmpty()) {
                    println("  Brak elementów redstone")
                } else {
                    println("  ✅ ZNALEZIONO ${redstoneBlocks.size} elementów redstone:")
                    totalRedstone += redstoneBlocks.size
                    
                    // Grupuj po Y
                    val byY = redstoneBlocks.groupBy { it.second }.toSortedMap()
                    byY.forEach { (y, positions) ->
                        println("    Y=$y: ${positions.size} elementów")
                        positions.take(10).forEach { pos ->
                            val name = getBlockName(blocksAt(path, pos.first, pos.second, pos.third))
                            println("      (${pos.first}, ${pos.second}, ${pos.third}) = $name")
                        }
                        if (positions.size > 10) {
                            println("      ... i ${positions.size - 10} więcej")
                        }
                    }
                }
            }
        } catch (e: Exception) {
            println("  ❌ Błąd: ${e.message}")
            e.printStackTrace()
        }
    }
    
    println()
    println("=".repeat(70))
    println("RAZEM: $totalRedstone elementów redstone")
    println("=".repeat(70))
}

private fun blocksAt(worldPath: Path, x: Int, y: Int, z: Int): Int {
    val analyzer = RedstoneAnalyzer(worldPath)
    val elements = analyzer.analyzeChunk(x shr 4, z shr 4)
    return elements.find { it.x == x && it.y == y && it.z == z }?.blockId ?: 0
}

private fun getBlockName(id: Int): String {
    return RedstoneAnalyzer.REDSTONE_BLOCKS[id] ?: "Block($id)"
}
