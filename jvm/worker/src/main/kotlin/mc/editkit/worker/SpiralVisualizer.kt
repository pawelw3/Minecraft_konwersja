package mc.editkit.worker

import org.jglrxavpok.hephaistos.mca.RegionFile
import org.jglrxavpok.hephaistos.nbt.NBTCompound
import java.io.RandomAccessFile
import java.nio.file.Paths

/**
 * Wizualizator spirali - pokazuje 4 chunki (-1,-1) do (0,0) z podziałem na Y
 */
fun visualizeSpiralChunks(worldPath: String, outputDir: String) {
    val path = Paths.get(worldPath)
    val output = Paths.get(outputDir)
    output.toFile().mkdirs()
    
    println("=".repeat(70))
    println("WIZUALIZACJA SPIRALI - 4 CHUNKI")
    println("Chunks: (-1,-1), (-1,0), (0,-1), (0,0)")
    println("=".repeat(70))
    
    val chunks = listOf(
        Pair(-1, -1), Pair(-1, 0),
        Pair(0, -1), Pair(0, 0)
    )
    
    // Zbierz wszystkie dane
    val allBlocks = mutableListOf<BlockInfo>()
    
    for ((chunkX, chunkZ) in chunks) {
        val globalCoord = GlobalChunkCoord(chunkX, chunkZ)
        val regionCoord = globalCoord.toRegionCoord()
        
        val regionFile = path.resolve("region/${regionCoord.fileName()}")
        if (!regionFile.toFile().exists()) {
            println("Region nie istnieje: ${regionCoord.fileName()}")
            continue
        }
        
        try {
            val raf = RandomAccessFile(regionFile.toFile(), "r")
            RegionFile(raf, regionCoord.x, regionCoord.z, 0, 255).use { region ->
                val chunkData = region.getChunkData(globalCoord.x, globalCoord.z) ?: return@use
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
                                
                                if (blockId in RedstoneAnalyzer.REDSTONE_COMPONENTS) {
                                    val worldX = (chunkX * 16) + x
                                    val worldY = (secY * 16) + y
                                    val worldZ = (chunkZ * 16) + z
                                    
                                    allBlocks.add(BlockInfo(
                                        x = worldX, y = worldY, z = worldZ,
                                        chunkX = chunkX, chunkZ = chunkZ,
                                        blockId = blockId
                                    ))
                                }
                            }
                        }
                    }
                }
            }
        } catch (e: Exception) {
            println("Błąd chunk ($chunkX, $chunkZ): ${e.message}")
        }
    }
    
    println("Znaleziono ${allBlocks.size} elementów redstone")
    
    // Grupuj po Y
    val byY = allBlocks.groupBy { it.y }
    val minY = byY.keys.minOrNull() ?: 0
    val maxY = byY.keys.maxOrNull() ?: 0
    
    println("Zakres Y: $minY..$maxY")
    
    // Granice obszaru (4 chunki = 64x64 bloki)
    val minX = -16
    val maxX = 15
    val minZ = -16
    val maxZ = 15
    
    // Generuj SVG dla każdego poziomu Y
    for (y in minY..maxY) {
        val blocksAtY = byY[y] ?: emptyList()
        if (blocksAtY.isEmpty()) continue
        
        val svgFile = output.resolve("spiral_y${y}.svg").toString()
        generateSpiralSvg(blocksAtY, minX, maxX, minZ, maxZ, y, svgFile)
    }
    
    // Generuj podsumowanie SVG z wszystkimi poziomami
    val summaryFile = output.resolve("spiral_all_layers.svg").toString()
    generateAllLayersSvg(byY, minX, maxX, minZ, maxZ, minY, maxY, summaryFile)
    
    // Generuj widok 3D (izometryczny)
    val isoFile = output.resolve("spiral_3d.svg").toString()
    generateIsometricSvg(allBlocks, minX, maxX, minZ, maxZ, minY, maxY, isoFile)
    
    println()
    println("Wygenerowano pliki:")
    println("  - $summaryFile (wszystkie poziomy)")
    println("  - $isoFile (widok 3D)")
    println("  - ${outputDir}/spiral_y*.svg (pojedyncze poziomy)")
}

data class BlockInfo(
    val x: Int, val y: Int, val z: Int,
    val chunkX: Int, val chunkZ: Int,
    val blockId: Int
)

private fun generateSpiralSvg(
    blocks: List<BlockInfo>,
    minX: Int, maxX: Int, minZ: Int, maxZ: Int,
    y: Int, outputFile: String
) {
    val width = maxX - minX + 1
    val height = maxZ - minZ + 1
    val scale = 8
    val svgWidth = width * scale
    val svgHeight = height * scale
    
    val sb = StringBuilder()
    sb.appendLine("""<?xml version="1.0" encoding="UTF-8"?>""")
    sb.appendLine("""<svg xmlns="http://www.w3.org/2000/svg" width="$svgWidth" height="$svgHeight" viewBox="0 0 $svgWidth $svgHeight">""")
    sb.appendLine("""  <rect width="100%" height="100%" fill="#1a1a2e"/>""")
    
    // Grid chunków
    sb.appendLine("  <!-- Granice chunków -->")
    // Linia X=0 (granica między chunkami -1 i 0 na X)
    val x0 = (0 - minX) * scale
    sb.appendLine("""  <line x1="$x0" y1="0" x2="$x0" y2="$svgHeight" stroke="#333" stroke-width="2"/>""")
    // Linia Z=0 (granica między chunkami -1 i 0 na Z)
    val z0 = (0 - minZ) * scale
    sb.appendLine("""  <line x1="0" y1="$z0" x2="$svgWidth" y2="$z0" stroke="#333" stroke-width="2"/>""")
    
    // Etykiety chunków
    sb.appendLine("  <!-- Etykiety chunków -->")
    sb.appendLine("""  <text x="${x0/2}" y="${z0/2}" fill="#666" font-size="20" text-anchor="middle" dominant-baseline="middle">(-1,-1)</text>""")
    sb.appendLine("""  <text x="${x0 + (svgWidth-x0)/2}" y="${z0/2}" fill="#666" font-size="20" text-anchor="middle" dominant-baseline="middle">(0,-1)</text>""")
    sb.appendLine("""  <text x="${x0/2}" y="${z0 + (svgHeight-z0)/2}" fill="#666" font-size="20" text-anchor="middle" dominant-baseline="middle">(-1,0)</text>""")
    sb.appendLine("""  <text x="${x0 + (svgWidth-x0)/2}" y="${z0 + (svgHeight-z0)/2}" fill="#666" font-size="20" text-anchor="middle" dominant-baseline="middle">(0,0)</text>""")
    
    // Bloki
    sb.appendLine("  <!-- Bloki redstone (Y=$y) -->")
    for (block in blocks) {
        val svgX = (block.x - minX) * scale + scale/2
        val svgY = (block.z - minZ) * scale + scale/2
        val color = getBlockColor(block.blockId)
        sb.appendLine("""  <rect x="${svgX - scale / 2 + 1}" y="${svgY - scale / 2 + 1}" width="${scale - 2}" height="${scale - 2}" fill="$color" stroke="white" stroke-width="0.5"/>""")
    }
    
    // Tytuł
    sb.appendLine("""  <text x="10" y="20" fill="white" font-size="14">Y = $y | ${blocks.size} bloków</text>""")
    
    sb.appendLine("</svg>")
    
    java.io.File(outputFile).writeText(sb.toString())
}

private fun generateAllLayersSvg(
    byY: Map<Int, List<BlockInfo>>,
    minX: Int, maxX: Int, minZ: Int, maxZ: Int,
    minY: Int, maxY: Int, outputFile: String
) {
    val width = maxX - minX + 1
    val height = maxZ - minZ + 1
    val scale = 8
    val svgWidth = width * scale
    val layersHeight = (maxY - minY + 1) * 20 + 100
    
    val sb = StringBuilder()
    sb.appendLine("""<?xml version="1.0" encoding="UTF-8"?>""")
    sb.appendLine("""<svg xmlns="http://www.w3.org/2000/svg" width="$svgWidth" height="$layersHeight" viewBox="0 0 $svgWidth $layersHeight">""")
    sb.appendLine("""  <rect width="100%" height="100%" fill="#0f0f23"/>""")
    
    var currentY = 30
    
    sb.appendLine("""  <text x="10" y="$currentY" fill="white" font-size="16" font-weight="bold">Wszystkie poziomy Y - 4 chunki</text>""")
    currentY += 30
    
    for (y in maxY downTo minY) {
        val blocks = byY[y] ?: emptyList()
        
        // Tytuł poziomu
        sb.appendLine("""  <text x="10" y="$currentY" fill="#aaa" font-size="12">Y=$y: ${blocks.size} bloków</text>""")
        currentY += 15
        
        // Miniatura poziomu
        val miniScale = 2
        val miniWidth = width * miniScale
        
        sb.appendLine("  <!-- Y=$y -->")
        
        // Granice chunków na miniaturze
        val x0 = (0 - minX) * miniScale
        val z0 = (0 - minZ) * miniScale
        
        for (block in blocks) {
            val svgX = 10 + (block.x - minX) * miniScale
            val svgY = currentY + (block.z - minZ) * miniScale
            val color = getBlockColor(block.blockId)
            sb.appendLine("""  <rect x="$svgX" y="$svgY" width="$miniScale" height="$miniScale" fill="$color"/>""")
        }
        
        // Linie chunków
        sb.appendLine("""  <line x1="${10+x0}" y1="$currentY" x2="${10+x0}" y2="${currentY + height*miniScale}" stroke="#444" stroke-width="1"/>""")
        sb.appendLine("""  <line x1="10" y1="${currentY+z0}" x2="${10 + miniWidth}" y2="${currentY+z0}" stroke="#444" stroke-width="1"/>""")
        
        currentY += height * miniScale + 10
    }
    
    sb.appendLine("</svg>")
    
    java.io.File(outputFile).writeText(sb.toString())
}

private fun generateIsometricSvg(
    blocks: List<BlockInfo>,
    minX: Int, maxX: Int, minZ: Int, maxZ: Int,
    minY: Int, maxY: Int, outputFile: String
) {
    val isoScale = 4
    val offsetX = 200
    val offsetY = 100
    
    val sb = StringBuilder()
    sb.appendLine("""<?xml version="1.0" encoding="UTF-8"?>""")
    sb.appendLine("""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">""")
    sb.appendLine("""  <rect width="100%" height="100%" fill="#0a0a14"/>""")
    
    // Sortuj bloki po Y (od najniższego do najwyższego - rysuj od dołu)
    val sortedBlocks = blocks.sortedBy { it.y }
    
    // Rysuj siatkę podłogi (Y=minY-1)
    sb.appendLine("  <!-- Siatka podłogi -->")
    for (x in minX..maxX) {
        val (x1, y1) = isoProject(x, minZ, minY - 1, offsetX, offsetY, isoScale)
        val (x2, y2) = isoProject(x, maxZ, minY - 1, offsetX, offsetY, isoScale)
        sb.appendLine("""  <line x1="$x1" y1="$y1" x2="$x2" y2="$y2" stroke="#222" stroke-width="1"/>""")
    }
    for (z in minZ..maxZ) {
        val (x1, y1) = isoProject(minX, z, minY - 1, offsetX, offsetY, isoScale)
        val (x2, y2) = isoProject(maxX, z, minY - 1, offsetX, offsetY, isoScale)
        sb.appendLine("""  <line x1="$x1" y1="$y1" x2="$x2" y2="$y2" stroke="#222" stroke-width="1"/>""")
    }
    
    // Rysuj bloki
    sb.appendLine("  <!-- Bloki redstone (widok izometryczny) -->")
    for (block in sortedBlocks) {
        val (ix, iy) = isoProject(block.x, block.z, block.y, offsetX, offsetY, isoScale)
        val color = getBlockColor(block.blockId)
        
        // Rysuj sześcian jako romb
        val size = isoScale * 0.8
        sb.appendLine("""  <polygon points="$ix,${iy-size} ${ix+size},${iy-size/2} $ix,${iy+size} ${ix-size},${iy-size/2}" fill="$color" stroke="white" stroke-width="0.5" opacity="0.9"/>""")
    }
    
    // Legenda
    sb.appendLine("  <!-- Legenda -->")
    sb.appendLine("""  <text x="10" y="30" fill="white" font-size="16" font-weight="bold">Widok 3D - 4 chunki redstone</text>""")
    sb.appendLine("""  <text x="10" y="50" fill="#aaa" font-size="12">Bloki: ${blocks.size}</text>""")
    sb.appendLine("""  <text x="10" y="65" fill="#aaa" font-size="12">Zakres Y: $minY..$maxY</text>""")
    sb.appendLine("""  <text x="10" y="80" fill="#ff0000" font-size="12">■ Redstone Wire (55)</text>""")
    sb.appendLine("""  <text x="10" y="95" fill="#808080" font-size="12">■ Repeater (93/94)</text>""")
    sb.appendLine("""  <text x="10" y="110" fill="#ff6600" font-size="12">■ Torch (75/76)</text>""")
    sb.appendLine("""  <text x="10" y="125" fill="#ff00ff" font-size="12">■ Comparator (152)</text>""")
    
    sb.appendLine("</svg>")
    
    java.io.File(outputFile).writeText(sb.toString())
}

// Izometryczna projekcja: X prawo-góra, Z prawo-dół, Y góra
private fun isoProject(x: Int, z: Int, y: Int, offsetX: Int, offsetY: Int, scale: Int): Pair<Double, Double> {
    val ix = offsetX + (x - z) * scale * 0.866
    val iy = offsetY + (x + z) * scale * 0.5 - y * scale * 0.8
    return Pair(ix, iy)
}

private fun getBlockColor(blockId: Int): String {
    return when (blockId) {
        55 -> "#ff0000"      // Redstone wire
        93, 94 -> "#808080"  // Repeater
        75, 76 -> "#ff6600"  // Torch
        152 -> "#ff00ff"     // Comparator
        else -> "#ff00ff"
    }
}
