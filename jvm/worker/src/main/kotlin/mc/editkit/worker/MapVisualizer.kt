package mc.editkit.worker

import org.jglrxavpok.hephaistos.mca.RegionFile
import org.jglrxavpok.hephaistos.nbt.NBTCompound
import java.io.RandomAccessFile
import java.nio.file.Path
import java.nio.file.Paths

/**
 * Wizualizator mapy - eksportuje dane bloków do SVG
 */
fun visualizeMapArea(worldPath: String, minX: Int, minZ: Int, maxX: Int, maxZ: Int, outputSvg: String) {
    val path = Paths.get(worldPath)
    
    println("=".repeat(70))
    println("WIZUALIZACJA MAPY")
    println("Obszar: X=$minX..$maxX, Z=$minZ..$maxZ")
    println("=".repeat(70))
    
    // Znajdź zakres chunków
    val minChunkX = chunkCoordFromBlock(minX)
    val maxChunkX = chunkCoordFromBlock(maxX)
    val minChunkZ = chunkCoordFromBlock(minZ)
    val maxChunkZ = chunkCoordFromBlock(maxZ)
    
    println("Chunki: X=$minChunkX..$maxChunkX, Z=$minChunkZ..$maxChunkZ")
    
    // Zbierz wszystkie bloki redstone
    val redstoneBlocks = mutableListOf<Triple<Int, Int, Int>>() // x, y, z
    val repeaterBlocks = mutableListOf<Triple<Int, Int, Int>>()
    val torchBlocks = mutableListOf<Triple<Int, Int, Int>>()
    val otherBlocks = mutableListOf<Triple<Int, Int, Int>>()
    
    for (chunkX in minChunkX..maxChunkX) {
        for (chunkZ in minChunkZ..maxChunkZ) {
            val regionX = regionCoordFromChunk(chunkX)
            val regionZ = regionCoordFromChunk(chunkZ)
            val localChunkX = localChunkFromChunk(chunkX)
            val localChunkZ = localChunkFromChunk(chunkZ)
            
            val regionFile = path.resolve("region/r.${regionX}.${regionZ}.mca")
            if (!regionFile.toFile().exists()) continue
            
            try {
                val raf = RandomAccessFile(regionFile.toFile(), "r")
                RegionFile(raf, regionX, regionZ, 0, 255).use { region ->
                    val chunkData = region.getChunkData(localChunkX, localChunkZ) ?: return@use
                    val level = chunkData.getCompound("Level") ?: return@use
                    val sections = level.getList<NBTCompound>("Sections") ?: return@use
                    
                    for (section in sections) {
                        val secY = section.getByte("Y")?.toInt() ?: continue
                        val blocks = section.getByteArray("Blocks")?.copyArray() ?: continue
                        
                        for (y in 0..15) {
                            for (z in 0..15) {
                                for (x in 0..15) {
                                    val idx = (y * 16 + z) * 16 + x
                                    val blockId = blocks[idx].toInt() and 0xFF
                                    
                                    if (blockId != 0) { // Nie air
                                        val worldX = (chunkX * 16) + x
                                        val worldY = (secY * 16) + y
                                        val worldZ = (chunkZ * 16) + z
                                        
                                        // Sprawdź czy w obszarze
                                        if (worldX in minX..maxX && worldZ in minZ..maxZ) {
                                            when (blockId) {
                                                55 -> redstoneBlocks.add(Triple(worldX, worldY, worldZ))
                                                93, 94 -> repeaterBlocks.add(Triple(worldX, worldY, worldZ))
                                                75, 76 -> torchBlocks.add(Triple(worldX, worldY, worldZ))
                                                in RedstoneAnalyzer.REDSTONE_COMPONENTS -> otherBlocks.add(Triple(worldX, worldY, worldZ))
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            } catch (e: Exception) {
                // Chunk nie istnieje
            }
        }
    }
    
    println("Znaleziono:")
    println("  Redstone Wire: ${redstoneBlocks.size}")
    println("  Repeaters: ${repeaterBlocks.size}")
    println("  Torches: ${torchBlocks.size}")
    println("  Other redstone: ${otherBlocks.size}")
    
    // Generuj SVG
    generateSvg(redstoneBlocks, repeaterBlocks, torchBlocks, otherBlocks, 
                minX, minZ, maxX, maxZ, outputSvg)
    
    println("Zapisano: $outputSvg")
}

private fun generateSvg(
    redstone: List<Triple<Int, Int, Int>>,
    repeaters: List<Triple<Int, Int, Int>>,
    torches: List<Triple<Int, Int, Int>>,
    other: List<Triple<Int, Int, Int>>,
    minX: Int, minZ: Int, maxX: Int, maxZ: Int,
    outputFile: String
) {
    val width = maxX - minX + 1
    val height = maxZ - minZ + 1
    
    // Skala: 1 blok = 4 piksele
    val scale = 4
    val svgWidth = width * scale
    val svgHeight = height * scale
    
    val sb = StringBuilder()
    sb.appendLine("""<?xml version="1.0" encoding="UTF-8"?>""")
    sb.appendLine("""<svg xmlns="http://www.w3.org/2000/svg" width="$svgWidth" height="$svgHeight" viewBox="0 0 $svgWidth $svgHeight">""")
    sb.appendLine("""  <rect width="100%" height="100%" fill="#2d5016"/>""") // Grass green background
    
    // Linie chunków (co 16 bloków)
    sb.appendLine("  <!-- Linie chunków -->")
    for (x in minX..maxX step 16) {
        val svgX = (x - minX) * scale
        sb.appendLine("""  <line x1="$svgX" y1="0" x2="$svgX" y2="$svgHeight" stroke="#1a3009" stroke-width="1"/>""")
    }
    for (z in minZ..maxZ step 16) {
        val svgY = (z - minZ) * scale
        sb.appendLine("""  <line x1="0" y1="$svgY" x2="$svgWidth" y2="$svgY" stroke="#1a3009" stroke-width="1"/>""")
    }
    
    // Redstone wire (czerwone kropki)
    sb.appendLine("  <!-- Redstone Wire -->")
    for ((x, y, z) in redstone) {
        val svgX = (x - minX) * scale + scale/2
        val svgY = (z - minZ) * scale + scale/2
        sb.appendLine("""  <circle cx="$svgX" cy="$svgY" r="${scale/2 - 0.5}" fill="#8b0000"/>""")
    }
    
    // Repeaters (szare kwadraty)
    sb.appendLine("  <!-- Repeaters -->")
    for ((x, y, z) in repeaters) {
        val svgX = (x - minX) * scale + 1
        val svgY = (z - minZ) * scale + 1
        sb.appendLine("""  <rect x="$svgX" y="$svgY" width="${scale-2}" height="${scale-2}" fill="#808080" stroke="#404040" stroke-width="0.5"/>""")
    }
    
    // Torches (pomarańczowe kropki)
    sb.appendLine("  <!-- Torches -->")
    for ((x, y, z) in torches) {
        val svgX = (x - minX) * scale + scale/2
        val svgY = (z - minZ) * scale + scale/2
        sb.appendLine("""  <circle cx="$svgX" cy="$svgY" r="${scale/2 - 0.5}" fill="#ff6600"/>""")
    }
    
    // Inne bloki redstone (różowe)
    sb.appendLine("  <!-- Other redstone -->")
    for ((x, y, z) in other) {
        val svgX = (x - minX) * scale + scale/2
        val svgY = (z - minZ) * scale + scale/2
        sb.appendLine("""  <circle cx="$svgX" cy="$svgY" r="${scale/2 - 0.5}" fill="#ff00ff"/>""")
    }
    
    // Oś X i Z na środku
    val centerX = (0 - minX) * scale
    val centerZ = (0 - minZ) * scale
    sb.appendLine("  <!-- Oś X=0, Z=0 -->")
    sb.appendLine("""  <line x1="$centerX" y1="0" x2="$centerX" y2="$svgHeight" stroke="#ffffff" stroke-width="2" opacity="0.5"/>""")
    sb.appendLine("""  <line x1="0" y1="$centerZ" x2="$svgWidth" y2="$centerZ" stroke="#ffffff" stroke-width="2" opacity="0.5"/>""")
    
    // Legenda
    sb.appendLine("  <!-- Legenda -->")
    sb.appendLine("""  <text x="10" y="20" fill="white" font-size="12">Redstone Wire: ${redstone.size}</text>""")
    sb.appendLine("""  <text x="10" y="35" fill="white" font-size="12">Repeaters: ${repeaters.size}</text>""")
    sb.appendLine("""  <text x="10" y="50" fill="white" font-size="12">Torches: ${torches.size}</text>""")
    sb.appendLine("""  <text x="10" y="65" fill="white" font-size="12">Obszar: X=$minX..$maxX, Z=$minZ..$maxZ</text>""")
    
    sb.appendLine("</svg>")
    
    java.io.File(outputFile).writeText(sb.toString())
}
