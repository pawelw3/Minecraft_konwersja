package mapcleaner

import java.io.File
import java.nio.file.Path
import java.nio.file.Paths
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger

/**
 * Skanuje wszystkie wymiary świata i koordynuje czyszczenie
 */
class WorldScanner(
    private val worldPath: Path,
    private val rules: CleaningRules,
    private val threads: Int = Runtime.getRuntime().availableProcessors()
) {
    
    /**
     * Wynik skanowania świata
     */
    data class WorldResult(
        val regionsProcessed: Int,
        val chunksProcessed: Int,
        val chunksModified: Int,
        val stats: ChunkCleaner.CleanStats,
        val processedDimensions: List<String>
    )
    
    /**
     * Typ wymiaru do przetworzenia
     */
    enum class DimensionType {
        OVERWORLD, NETHER, END, ALL_MODDED, SPECIFIC
    }
    
    /**
     * Znajduje wszystkie pliki regionów we wszystkich wymiarach
     */
    fun findAllRegions(dimensionFilter: DimensionType = DimensionType.ALL_MODDED, specificDim: String? = null): List<Pair<Path, String>> {
        val regions = mutableListOf<Pair<Path, String>>()
        
        // Overworld (region/)
        if (dimensionFilter == DimensionType.OVERWORLD || dimensionFilter == DimensionType.ALL_MODDED) {
            val overworldRegion = worldPath.resolve("region")
            findRegionsInDir(overworldRegion, "overworld", regions)
        }
        
        // Nether (DIM-1/region)
        if (dimensionFilter == DimensionType.NETHER || dimensionFilter == DimensionType.ALL_MODDED) {
            val netherRegion = worldPath.resolve("DIM-1/region")
            findRegionsInDir(netherRegion, "nether", regions)
        }
        
        // End (DIM1/region)
        if (dimensionFilter == DimensionType.END || dimensionFilter == DimensionType.ALL_MODDED) {
            val endRegion = worldPath.resolve("DIM1/region")
            findRegionsInDir(endRegion, "end", regions)
        }
        
        // Inne wymiary modowe (DIM*/region)
        if (dimensionFilter == DimensionType.ALL_MODDED) {
            val worldDir = worldPath.toFile()
            if (worldDir.exists() && worldDir.isDirectory) {
                worldDir.listFiles { file -> 
                    file.isDirectory && file.name.startsWith("DIM-") && file.name.length > 4
                }?.forEach { dimDir ->
                    val dimName = dimDir.name
                    if (dimName != "DIM-1") { // Nether już obsłużony
                        val dimRegion = dimDir.toPath().resolve("region")
                        findRegionsInDir(dimRegion, dimName, regions)
                    }
                }
                
                // Wymiary z dodatnimi ID (DIM1, DIM2, ...)
                worldDir.listFiles { file ->
                    file.isDirectory && file.name.startsWith("DIM") && 
                    file.name.length > 3 && file.name[3].isDigit() &&
                    file.name != "DIM1" // End już obsłużony
                }?.forEach { dimDir ->
                    val dimName = dimDir.name
                    val dimRegion = dimDir.toPath().resolve("region")
                    findRegionsInDir(dimRegion, dimName, regions)
                }
            }
        }
        
        // Konkretny wymiar
        if (dimensionFilter == DimensionType.SPECIFIC && specificDim != null) {
            val specificRegion = worldPath.resolve("$specificDim/region")
            findRegionsInDir(specificRegion, specificDim, regions)
        }
        
        return regions
    }
    
    /**
     * Znajduje regiony w konkretnym katalogu
     */
    private fun findRegionsInDir(
        regionDir: Path, 
        dimensionName: String, 
        regions: MutableList<Pair<Path, String>>
    ) {
        val dir = regionDir.toFile()
        if (!dir.exists() || !dir.isDirectory) return
        
        dir.listFiles { file ->
            file.isFile && file.name.endsWith(".mca") && file.name.startsWith("r.")
        }?.forEach { regionFile ->
            regions.add(regionFile.toPath() to dimensionName)
        }
    }
    
    /**
     * Przetwarza wszystkie regiony
     */
    fun processAll(dryRun: Boolean = false, dimensionFilter: DimensionType = DimensionType.ALL_MODDED): WorldResult {
        val regions = findAllRegions(dimensionFilter)
        
        if (regions.isEmpty()) {
            println("Nie znaleziono regionów do przetworzenia")
            return WorldResult(0, 0, 0, ChunkCleaner.CleanStats(), emptyList())
        }
        
        println("Znaleziono ${regions.size} regionów w ${regions.map { it.second }.distinct().size} wymiarach")
        
        val processor = RegionProcessor(rules)
        val totalRegions = AtomicInteger(0)
        val totalChunks = AtomicInteger(0)
        val totalModifiedChunks = AtomicInteger(0)
        val totalStats = ChunkCleaner.CleanStats()
        
        val executor = Executors.newFixedThreadPool(threads)
        
        regions.forEach { (regionPath, dimension) ->
            executor.submit {
                try {
                    val result = processor.processRegion(regionPath.toFile(), dryRun)
                    
                    totalRegions.incrementAndGet()
                    totalChunks.addAndGet(result.chunksProcessed)
                    totalModifiedChunks.addAndGet(result.chunksModified)
                    
                    synchronized(totalStats) {
                        totalStats.blocksRemoved += result.stats.blocksRemoved
                        totalStats.tileEntitiesRemoved += result.stats.tileEntitiesRemoved
                        totalStats.entitiesRemoved += result.stats.entitiesRemoved
                        totalStats.sectionsModified += result.stats.sectionsModified
                    }
                    
                    val processed = totalRegions.get()
                    if (processed % 10 == 0 || processed == regions.size) {
                        println("[$processed/${regions.size}] Przetworzono ${regionPath.fileName} ($dimension)")
                    }
                } catch (e: Exception) {
                    println("BŁĄD w ${regionPath.fileName}: ${e.message}")
                    e.printStackTrace()
                }
            }
        }
        
        executor.shutdown()
        val timeoutMinutes = if (dryRun) 5L else 30L  // Dry-run = 5min, zapis = 30min
        val finished = executor.awaitTermination(timeoutMinutes, TimeUnit.MINUTES)
        
        if (!finished) {
            println("UWAGA: Timeout po ${timeoutMinutes} minutach. Niektóre regiony mogły nie zostać przetworzone.")
            println("Możliwe przyczyny:")
            println("  - Bardzo duże zmodyfikowane chunki (wolny zapis na dysk)")
            println("  - Problem z dostępem do pliku (blokada)")
            println("  - Zbyt wolny dysk dla liczby wątków (spróbuj --threads 1)")
            executor.shutdownNow()
        }
        
        val processedDimensions = regions.map { it.second }.distinct()
        
        return WorldResult(
            regionsProcessed = totalRegions.get(),
            chunksProcessed = totalChunks.get(),
            chunksModified = totalModifiedChunks.get(),
            stats = totalStats,
            processedDimensions = processedDimensions
        )
    }
    
    /**
     * Tworzy backup struktury świata
     */
    fun createBackup(outputPath: Path) {
        val worldDir = worldPath.toFile()
        val outputDir = outputPath.toFile()
        
        if (!outputDir.exists()) {
            outputDir.mkdirs()
        }
        
        // Lista folderów i plików do skopiowania (bez regionów)
        val items = listOf(
            "level.dat", "level.dat_old", "session.lock", "uid.dat",
            "playerdata", "stats", "data", "forcedchunks.dat"
        )
        
        for (item in items) {
            val src = worldPath.resolve(item)
            val dst = outputPath.resolve(item)
            
            if (src.toFile().exists()) {
                if (src.toFile().isDirectory) {
                    src.toFile().copyRecursively(dst.toFile(), overwrite = true)
                    println("  [DIR] $item")
                } else {
                    src.toFile().copyTo(dst.toFile(), overwrite = true)
                    println("  [FILE] $item")
                }
            }
        }
    }
}
