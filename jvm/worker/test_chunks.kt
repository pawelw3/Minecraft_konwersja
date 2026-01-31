import org.jglrxavpok.hephaistos.mca.RegionFile
import java.io.RandomAccessFile
import java.nio.file.Paths

fun analyzeChunk(worldPath: String, chunkX: Int, chunkZ: Int) {
    val regionX = if (chunkX >= 0) chunkX shr 5 else (chunkX + 1) shr 5 - 1
    val regionZ = if (chunkZ >= 0) chunkZ shr 5 else (chunkZ + 1) shr 5 - 1
    val localChunkX = chunkX and 31
    val localChunkZ = chunkZ and 31
    
    println("Chunk (, ) -> Region (, ), local (, )")
    
    val regionFile = Paths.get(worldPath, "region", "r...mca")
    if (!regionFile.toFile().exists()) {
        println("  Region nie istnieje: ")
        return
    }
    
    val raf = RandomAccessFile(regionFile.toFile(), "r")
    RegionFile(raf, regionX, regionZ, 0, 255).use { region ->
        val chunkData = region.getChunkData(localChunkX, localChunkZ)
        if (chunkData == null) {
            println("  Chunk nie istnieje w regionie")
            return
        }
        
        val level = chunkData.getCompound("Level") ?: return
        val sections = level.getList<org.jglrxavpok.hephaistos.nbt.NBTCompound>("Sections") ?: return
        
        println("  Sekcje Y: ")
        var redstoneCount = 0
        
        for (section in sections) {
            val y = section.getByte("Y")?.toInt() ?: continue
            val blocks = section.getByteArray("Blocks")?.copyArray() ?: continue
            
            var hasBlocks = false
            for (i in blocks.indices) {
                val id = blocks[i].toInt() and 0xFF
                if (id == 55 || id == 75 || id == 76 || id == 93 || id == 94 || id == 137 || id == 152) {
                    hasBlocks = true
                    redstoneCount++
                }
            }
            if (hasBlocks) print("Y=(), ")
        }
        println()
        println("  Znaleziono  bloków redstone")
    }
}

fun main() {
    val world = "..\\..\\map_read_write_tests\\kimi1"
    println("=== ANALIZA POJEDYNCZYCH CHUNKÓW ===")
    analyzeChunk(world, 0, 0)
    analyzeChunk(world, -1, -1)
    analyzeChunk(world, 0, -1)
    analyzeChunk(world, -1, 0)
}

main()
