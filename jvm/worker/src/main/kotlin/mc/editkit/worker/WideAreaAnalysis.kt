package mc.editkit.worker

import org.jglrxavpok.hephaistos.mca.RegionFile
import org.jglrxavpok.hephaistos.nbt.NBTCompound
import java.io.RandomAccessFile
import java.nio.file.Paths

/**
 * Analiza szerokiego obszaru - szukanie redstone we wszystkich chunkach
 */
fun wideAreaAnalysis(worldPath: String) {
    val path = Paths.get(worldPath)
    
    println("=".repeat(70))
    println("SZEROKA ANALIZA - WSZYSTKIE REGIONY")
    println("=".repeat(70))
    
    val results = mutableMapOf<Triple<Int, Int, Int>, Int>() // regionX, regionZ, count
    val chunkDetails = mutableListOf<String>()
    
    // Sprawdź wszystkie regiony
    val regionFiles = path.resolve("region").toFile().listFiles { _, name -> name.endsWith(".mca") }
        ?.sortedBy { it.name } ?: emptyList()
    
    regionFiles.forEach { regionFile ->
        val name = regionFile.name
        val regex = Regex("r\\.(-?\\d+)\\.(-?\\d+)\\.mca")
        val match = regex.find(name) ?: return@forEach
        
        val regionX = match.groupValues[1].toInt()
        val regionZ = match.groupValues[2].toInt()
        
        var regionTotal = 0
        
        try {
            val raf = RandomAccessFile(regionFile, "r")
            RegionFile(raf, regionX, regionZ, 0, 255).use { region ->
                // Sprawdź wszystkie 32x32 chunków w regionie
                for (localX in 0..31) {
                    for (localZ in 0..31) {
                        val chunkData = region.getChunkData(localX, localZ)
                        if (chunkData != null) {
                            val level = chunkData.getCompound("Level")
                            val sections = level?.getList<NBTCompound>("Sections")
                            
                            var chunkRedstone = 0
                            sections?.forEach { section ->
                                val blocks = section.getByteArray("Blocks")?.copyArray()
                                blocks?.forEach { b ->
                                    val id = b.toInt() and 0xFF
                                    if (id in RedstoneAnalyzer.REDSTONE_COMPONENTS) {
                                        chunkRedstone++
                                    }
                                }
                            }
                            
                            if (chunkRedstone > 0) {
                                val globalChunkX = regionX * 32 + localX
                                val globalChunkZ = regionZ * 32 + localZ
                                regionTotal += chunkRedstone
                                chunkDetails.add("Chunk ($globalChunkX, $globalChunkZ): $chunkRedstone elementów")
                            }
                        }
                    }
                }
            }
        } catch (e: Exception) {
            println("Błąd regionu $name: ${e.message}")
        }
        
        if (regionTotal > 0) {
            results[Triple(regionX, regionZ, regionTotal)] = regionTotal
            println("Region $name: $regionTotal elementów redstone")
        }
    }
    
    println()
    println("=".repeat(70))
    println("SZCZEGÓŁY CHUNKÓW Z REDSTONE:")
    println("=".repeat(70))
    chunkDetails.sorted().forEach { println(it) }
    
    val total = results.values.sum()
    println()
    println("=".repeat(70))
    println("RAZEM: $total elementów redstone")
    println("=".repeat(70))
}
