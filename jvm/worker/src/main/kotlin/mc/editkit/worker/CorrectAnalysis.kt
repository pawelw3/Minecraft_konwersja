package mc.editkit.worker

import org.jglrxavpok.hephaistos.mca.RegionFile
import org.jglrxavpok.hephaistos.nbt.NBTCompound
import java.io.RandomAccessFile
import java.nio.file.Paths

/**
 * Poprawiona analiza - sprawdza wszystkie poziomy Y
 * Używa Hephaistos API z GLOBALNYMI koordynatami
 */
fun correctAnalysis(worldPath: String) {
    val path = Paths.get(worldPath)
    
    println("=".repeat(70))
    println("POPRAWIONA ANALIZA - WSZYSTKIE POZIOMY Y")
    println("=".repeat(70))
    
    val chunksToCheck = listOf(
        Pair(0, 0),
        Pair(0, -1),
        Pair(-1, 0),
        Pair(-1, -1),
        Pair(1, 0),
        Pair(0, 1),
        Pair(1, 1),
        Pair(-1, 1),
        Pair(1, -1)
    )
    
    var totalRedstone = 0
    
    chunksToCheck.forEach { (chunkX, chunkZ) ->
        val globalCoord = GlobalChunkCoord(chunkX, chunkZ)
        val regionCoord = globalCoord.toRegionCoord()
        val localCoord = globalCoord.toLocalCoord()
        
        // DEBUG: Logowanie mapowania
        println("DEBUG: $globalCoord -> $regionCoord + $localCoord")
        
        val regionFile = path.resolve("region/${regionCoord.fileName()}")
        if (!regionFile.toFile().exists()) {
            println("Chunk ($chunkX, $chunkZ): Region nie istnieje")
            return@forEach
        }
        
        try {
            // WAŻNE: Hephaistos API używa GLOBALNYCH koordynatów!
            val raf = RandomAccessFile(regionFile.toFile(), "r")
            RegionFile(raf, regionCoord.x, regionCoord.z, 0, 255).use { region ->
                // Używamy getChunkData zamiast getChunk - zwraca obiekt z compound
                val chunkData = region.getChunkData(globalCoord.x, globalCoord.z)
                if (chunkData == null) {
                    println("Chunk ($chunkX, $chunkZ): Niezapisany (null)")
                    return@use
                }
                
                // chunkData to NBTCompound, nie obiekt z polem compound
                val level = chunkData.getCompound("Level") ?: return@use
                val sections = level.getList<NBTCompound>("Sections") ?: return@use
                
                val byY = mutableMapOf<Int, MutableList<Triple<Int, Int, Int>>>()
                
                sections.forEach { section: NBTCompound ->
                    val secY = section.getByte("Y")?.toInt() ?: return@forEach
                    val blocks = section.getByteArray("Blocks")?.copyArray() ?: return@forEach
                    
                    for (y in 0..15) {
                        for (z in 0..15) {
                            for (x in 0..15) {
                                val idx = (y * 16 + z) * 16 + x
                                val blockId = blocks[idx].toInt() and 0xFF
                                
                                if (blockId in RedstoneAnalyzer.REDSTONE_COMPONENTS) {
                                    val worldX = (chunkX * 16) + x
                                    val worldY = (secY * 16) + y
                                    val worldZ = (chunkZ * 16) + z
                                    
                                    byY.getOrPut(worldY) { mutableListOf() }
                                        .add(Triple(worldX, worldY, worldZ))
                                }
                            }
                        }
                    }
                }
                
                if (byY.isEmpty()) {
                    println("Chunk ($chunkX, $chunkZ): Brak redstone")
                } else {
                    val chunkTotal = byY.values.sumOf { it.size }
                    totalRedstone += chunkTotal
                    println("Chunk ($chunkX, $chunkZ): $chunkTotal elementów redstone")
                    byY.toSortedMap().forEach { (y, positions) ->
                        println("  Y=$y: ${positions.size} elementów")
                        if (positions.size <= 10) {
                            positions.forEach { println("    (${it.first}, ${it.second}, ${it.third})") }
                        }
                    }
                }
            }
        } catch (e: Exception) {
            println("Chunk ($chunkX, $chunkZ): Błąd - ${e.message}")
        }
    }
    
    println()
    println("=".repeat(70))
    println("RAZEM: $totalRedstone elementów redstone")
    println("=".repeat(70))
}
