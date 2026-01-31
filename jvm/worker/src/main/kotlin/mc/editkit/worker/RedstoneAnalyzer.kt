package mc.editkit.worker

import org.jglrxavpok.hephaistos.mca.RegionFile
import org.jglrxavpok.hephaistos.nbt.NBTCompound
import java.io.RandomAccessFile
import java.nio.file.Path
import java.nio.file.Paths

/**
 * Analizator elementów redstone w świecie Minecraft 1.7.10
 */
class RedstoneAnalyzer(private val worldPath: Path) {
    
    // ID bloków redstone w 1.7.10
    companion object {
        val REDSTONE_BLOCKS = mapOf(
            55 to "Redstone Wire",
            75 to "Redstone Torch (off)",
            76 to "Redstone Torch (on)",
            152 to "Block of Redstone",
            137 to "Command Block",
            138 to "Beacon",
            69 to "Lever",
            70 to "Stone Pressure Plate",
            72 to "Wooden Pressure Plate",
            77 to "Stone Button",
            93 to "Redstone Repeater (off)",
            94 to "Redstone Repeater (on)",
            149 to "Redstone Comparator (off)",
            150 to "Redstone Comparator (on)",
            147 to "Weighted Pressure Plate (light)",
            148 to "Weighted Pressure Plate (heavy)",
            143 to "Wooden Button",
            154 to "Hopper",
            158 to "Dropper",
            23 to "Dispenser",
            29 to "Sticky Piston",
            33 to "Piston",
            25 to "Note Block",
            46 to "TNT",
            27 to "Powered Rail",
            28 to "Detector Rail",
            157 to "Activator Rail",
            84 to "Jukebox",
            131 to "Tripwire Hook",
            132 to "Tripwire"
        )
        
        val REDSTONE_COMPONENTS = setOf(
            55, 75, 76, 152, 137, 138, 69, 70, 72, 77, 93, 94,
            149, 150, 147, 148, 143, 154, 158, 23, 29, 33, 25,
            46, 27, 28, 157, 84, 131, 132
        )
    }
    
    data class RedstoneElement(
        val x: Int,
        val y: Int,
        val z: Int,
        val blockId: Int,
        val metadata: Int,
        val name: String
    ) {
        fun getChunkX(): Int = chunkCoordFromBlock(x)
        fun getChunkZ(): Int = chunkCoordFromBlock(z)
        fun getRegionX(): Int = regionCoordFromChunk(getChunkX())
        fun getRegionZ(): Int = regionCoordFromChunk(getChunkZ())
        fun getLocalChunkX(): Int = localChunkFromChunk(getChunkX())
        fun getLocalChunkZ(): Int = localChunkFromChunk(getChunkZ())
    }
    
    data class AnalysisResult(
        val elements: List<RedstoneElement>,
        val elementsByChunk: Map<Pair<Int, Int>, List<RedstoneElement>>,
        val elementsByType: Map<Int, List<RedstoneElement>>,
        val chunkCount: Int
    ) {
        fun summary(): String {
            val sb = StringBuilder()
            sb.appendLine("=".repeat(70))
            sb.appendLine("ANALIZA ELEMENTÓW REDSTONE")
            sb.appendLine("=".repeat(70))
            sb.appendLine("Całkowita liczba elementów: ${elements.size}")
            sb.appendLine("Liczba chunków z redstone: $chunkCount")
            sb.appendLine()
            
            sb.appendLine("ELEMENTY WG TYPU:")
            sb.appendLine("-".repeat(70))
            elementsByType.entries
                .sortedByDescending { it.value.size }
                .forEach { entry ->
                    val id = entry.key
                    val list = entry.value
                    val name = REDSTONE_BLOCKS[id] ?: "Unknown($id)"
                    sb.appendLine("  ${name.padEnd(30)} : ${list.size} szt.")
                }
            
            sb.appendLine()
            sb.appendLine("ELEMENTY WG CHUNKA (chunkX, chunkZ):")
            sb.appendLine("-".repeat(70))
            elementsByChunk.entries
                .sortedWith(compareBy({ it.key.first }, { it.key.second }))
                .forEach { entry ->
                    val chunk = entry.key
                    val list = entry.value
                    sb.appendLine("  Chunk (${chunk.first}, ${chunk.second}): ${list.size} elementów")
                    list.take(5).forEach { el ->
                        sb.appendLine("    - ${el.name} at (${el.x}, ${el.y}, ${el.z})")
                    }
                    if (list.size > 5) {
                        sb.appendLine("    ... i ${list.size - 5} więcej")
                    }
                }
            
            return sb.toString()
        }
    }
    
    /**
     * Analizuj chunki wokół chunka 0,0
     */
    fun analyzeAroundChunkZeroZero(radiusChunks: Int = 2): AnalysisResult {
        val elements = mutableListOf<RedstoneElement>()
        
        // Analizuj chunki od -radius do +radius wokół 0,0
        for (chunkX in -radiusChunks..radiusChunks) {
            for (chunkZ in -radiusChunks..radiusChunks) {
                val chunkElements = analyzeChunk(chunkX, chunkZ)
                elements.addAll(chunkElements)
            }
        }
        
        return groupResults(elements)
    }
    
    /**
     * Analizuj konkretny chunk
     * Uwaga: Hephaistos RegionFile.getChunkData() wymaga GLOBALNYCH koordynatów chunka!
     */
    fun analyzeChunk(chunkX: Int, chunkZ: Int): List<RedstoneElement> {
        val globalCoord = GlobalChunkCoord(chunkX, chunkZ)
        val regionCoord = globalCoord.toRegionCoord()
        val localCoord = globalCoord.toLocalCoord()
        
        // WAŻNE: Hephaistos API używa GLOBALNYCH koordynatów, nie lokalnych!
        // getChunkData(globalChunkX, globalChunkZ) - nie getChunkData(localX, localZ)
        
        val regionFile = worldPath.resolve("region/${regionCoord.fileName()}").toFile()
        if (!regionFile.exists()) {
            return emptyList()
        }
        
        val elements = mutableListOf<RedstoneElement>()
        
        try {
            val raf = RandomAccessFile(regionFile, "r")
            RegionFile(raf, regionCoord.x, regionCoord.z, 0, 255).use { region ->
                // Przekazujemy GLOBALNE koordynaty do Hephaistos!
                val chunkData = region.getChunkData(globalCoord.x, globalCoord.z)
                if (chunkData == null) {
                    println("DEBUG: Chunk $globalCoord nie istnieje w regionie")
                    return@use
                }
                
                // chunkData to NBTCompound, nie obiekt z polem compound
                val level = chunkData.getCompound("Level") ?: return@use
                elements.addAll(scanChunkForRedstone(level, chunkX, chunkZ))
            }
        } catch (e: Exception) {
            System.err.println("Błąd analizy chunk $globalCoord: ${e.message}")
            e.printStackTrace()
        }
        
        return elements
    }
    
    /**
     * Skanuj chunk w poszukiwaniu elementów redstone
     */
    private fun scanChunkForRedstone(level: NBTCompound, chunkX: Int, chunkZ: Int): List<RedstoneElement> {
        val elements = mutableListOf<RedstoneElement>()
        val sections = level.getList<NBTCompound>("Sections") ?: return emptyList()
        
        val baseX = chunkX * 16
        val baseZ = chunkZ * 16
        
        for (section in sections) {
            val sectionY = section.getByte("Y")?.toInt() ?: continue
            val blocks = section.getByteArray("Blocks")?.copyArray() ?: continue
            val data = section.getByteArray("Data")?.copyArray() ?: continue
            
            for (y in 0..15) {
                for (z in 0..15) {
                    for (x in 0..15) {
                        val index = (y * 16 + z) * 16 + x
                        val blockId = blocks[index].toInt() and 0xFF
                        
                        if (blockId in REDSTONE_COMPONENTS) {
                            val dataIndex = index shr 1
                            val nibble = data[dataIndex].toInt() and 0xFF
                            val metadata = if (index and 1 == 0) {
                                nibble and 0x0F
                            } else {
                                (nibble shr 4) and 0x0F
                            }
                            
                            val worldX = baseX + x
                            val worldY = (sectionY * 16) + y
                            val worldZ = baseZ + z
                            
                            elements.add(RedstoneElement(
                                x = worldX,
                                y = worldY,
                                z = worldZ,
                                blockId = blockId,
                                metadata = metadata,
                                name = REDSTONE_BLOCKS[blockId] ?: "Unknown($blockId)"
                            ))
                        }
                    }
                }
            }
        }
        
        return elements
    }
    
    /**
     * Znajdź struktury połączeń redstone (redstone wire połączone ze sobą)
     */
    fun findRedstoneCircuits(elements: List<RedstoneElement>): List<List<RedstoneElement>> {
        val wireElements = elements.filter { it.blockId == 55 }.toMutableSet()
        val circuits = mutableListOf<List<RedstoneElement>>()
        
        while (wireElements.isNotEmpty()) {
            val circuit = mutableListOf<RedstoneElement>()
            val toVisit = mutableListOf(wireElements.first())
            wireElements.remove(wireElements.first())
            
            while (toVisit.isNotEmpty()) {
                val current = toVisit.removeAt(0)
                circuit.add(current)
                
                // Znajdź sąsiadów (w odległości 1 bloku na tej samej wysokości)
                val neighbors = wireElements.filter { 
                    kotlin.math.abs(it.x - current.x) <= 1 && 
                    kotlin.math.abs(it.z - current.z) <= 1 &&
                    it.y == current.y &&
                    !(it.x == current.x && it.z == current.z)
                }
                
                toVisit.addAll(neighbors)
                wireElements.removeAll(neighbors)
            }
            
            circuits.add(circuit)
        }
        
        return circuits
    }
    
    private fun groupResults(elements: List<RedstoneElement>): AnalysisResult {
        val byChunk = elements.groupBy { Pair(it.getChunkX(), it.getChunkZ()) }
        val byType = elements.groupBy { it.blockId }
        
        return AnalysisResult(
            elements = elements,
            elementsByChunk = byChunk,
            elementsByType = byType,
            chunkCount = byChunk.size
        )
    }
}

/**
 * Komenda CLI do analizy redstone
 */
fun analyzeRedstoneCommand(worldPath: String, chunkRadius: Int = 2) {
    val path = Paths.get(worldPath)
    if (!path.toFile().exists()) {
        println("❌ Świat nie istnieje: $worldPath")
        return
    }
    
    val analyzer = RedstoneAnalyzer(path)
    val result = analyzer.analyzeAroundChunkZeroZero(chunkRadius)
    
    println(result.summary())
    
    // Szczegółowa analiza obwodów redstone
    if (result.elements.any { it.blockId == 55 }) {
        println()
        println("ANALIZA OBWODÓW REDSTONE:")
        println("-".repeat(70))
        
        val circuits = analyzer.findRedstoneCircuits(result.elements)
        println("Znaleziono ${circuits.size} obwodów:")
        
        circuits.forEachIndexed { index, circuit ->
            val minX = circuit.minOf { it.x }
            val maxX = circuit.maxOf { it.x }
            val minZ = circuit.minOf { it.z }
            val maxZ = circuit.maxOf { it.z }
            val yLevels = circuit.map { it.y }.distinct().sorted()
            
            println()
            println("  Obwód #${index + 1}: ${circuit.size} bloków redstone")
            println("    Zakres X: $minX do $maxX")
            println("    Zakres Z: $minZ do $maxZ")
            println("    Poziomy Y: ${yLevels.joinToString(", ")}")
            
            // Sprawdź czy ma zasilanie
            val hasPowerSource = result.elements.any { powerSource ->
                powerSource.blockId in setOf(152, 76, 137) && // Redstone block, torch, command block
                circuit.any { wire ->
                    kotlin.math.abs(powerSource.x - wire.x) <= 1 &&
                    kotlin.math.abs(powerSource.z - wire.z) <= 1 &&
                    kotlin.math.abs(powerSource.y - wire.y) <= 1
                }
            }
            println("    Źródło zasilania w pobliżu: ${if (hasPowerSource) "TAK" else "NIE"}")
        }
    }
}
