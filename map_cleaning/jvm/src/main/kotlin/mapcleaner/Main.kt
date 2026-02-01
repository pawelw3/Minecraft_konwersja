package mapcleaner

import java.io.File
import java.nio.file.Path
import java.nio.file.Paths
import kotlin.system.exitProcess
import kotlin.system.measureTimeMillis

/**
 * Map Cleaner - Czyści mapę Minecraft 1.7.10 z modowej zawartości
 * 
 * Użycie: java -jar map-cleaner.jar <ścieżka_świata> [opcje]
 */
fun main(args: Array<String>) {
    if (args.isEmpty() || args.contains("--help") || args.contains("-h")) {
        printHelp()
        return
    }
    
    val worldPath = Paths.get(args[0])
    
    // Parsowanie argumentów
    val outputPath = parseArg(args, "--output")?.let { Paths.get(it) }
    val threads = parseArg(args, "--threads")?.toIntOrNull() ?: Runtime.getRuntime().availableProcessors()
    val dryRun = args.contains("--dry-run")
    val backup = args.contains("--backup")
    val rulesPath = parseArg(args, "--rules")?.let { Paths.get(it) }
    val dimension = parseArg(args, "--dim")
    
    // Poziomy agresywności
    val blocksOnly = args.contains("--blocks-only")
    val blocksAndTe = args.contains("--blocks-and-te")
    val fullClean = args.contains("--full")
    
    // Walidacja ścieżki
    if (!worldPath.toFile().exists()) {
        println("BŁĄD: Świat nie istnieje: $worldPath")
        exitProcess(1)
    }
    
    println("=" * 70)
    println("MAP CLEANER - Czyszczenie mapy Minecraft 1.7.10")
    println("=" * 70)
    println("Świat: $worldPath")
    
    if (outputPath != null && outputPath != worldPath) {
        println("Wyjście: $outputPath")
    } else {
        println("Wyjście: ${if (dryRun) "tylko analiza" else "nadpisanie oryginału"}")
    }
    
    println("Wątki: $threads")
    println("Tryb: ${if (dryRun) "ANALIZA (dry-run)" else "CZYSZCZENIE"}")
    
    // Wczytaj lub utwórz reguły
    val rulesFile = rulesPath?.toFile() ?: File("rules.json")
    val rules = if (rulesFile.exists()) {
        println("Reguły: ${rulesFile.absolutePath}")
        CleaningRules.fromFile(rulesFile)
    } else {
        println("Reguły: domyślne (brak pliku ${rulesFile.absolutePath})")
        // Utwórz przykładowy plik reguł
        CleaningRules.createDefaultRules(File("rules.json.example"))
        println("  (Utworzono przykładowy plik rules.json.example)")
        CleaningRules()
    }
    
    // Dostosuj reguły do poziomu agresywności
    val finalRules = when {
        blocksOnly -> rules.copy(cleanTileEntities = false, cleanEntities = false)
        blocksAndTe -> rules.copy(cleanTileEntities = true, cleanEntities = false)
        fullClean -> rules.copy(cleanTileEntities = true, cleanEntities = true)
        else -> rules
    }
    
    println("Czyszczenie: bloki=${finalRules.useHeuristics}, TE=${finalRules.cleanTileEntities}, Entities=${finalRules.cleanEntities}")
    println("=" * 70)
    println()
    
    // Jeśli output to inna lokalizacja - skopiuj strukturę
    val targetPath = outputPath ?: worldPath
    if (!dryRun && outputPath != null && outputPath != worldPath) {
        println("Kopiowanie struktury świata...")
        val scanner = WorldScanner(worldPath, finalRules, threads)
        scanner.createBackup(outputPath)
        println()
    }
    
    // Jeśli output != source i nie jest dry-run, kopiuj regiony
    if (!dryRun && outputPath != null && outputPath != worldPath) {
        println("Kopiowanie regionów...")
        copyRegions(worldPath, outputPath)
        println()
    }
    
    // Określ który wymiar przetwarzać
    val dimensionType = when (dimension?.lowercase()) {
        "overworld", "0" -> WorldScanner.DimensionType.OVERWORLD
        "nether", "-1" -> WorldScanner.DimensionType.NETHER
        "end", "1" -> WorldScanner.DimensionType.END
        "all" -> WorldScanner.DimensionType.ALL_MODDED
        null -> WorldScanner.DimensionType.ALL_MODDED
        else -> WorldScanner.DimensionType.SPECIFIC
    }
    
    // Przetwórz świat
    val scanner = WorldScanner(
        if (!dryRun && outputPath != null && outputPath != worldPath) outputPath else worldPath,
        finalRules,
        threads
    )
    
    var result: WorldScanner.WorldResult? = null
    val time = measureTimeMillis {
        result = scanner.processAll(dryRun, dimensionType)
    }
    
    result?.let { r ->
        println()
        println("=" * 70)
        println("PODSUMOWANIE")
        println("=" * 70)
        println("Przetworzone regiony: ${r.regionsProcessed}")
        println("Przeskanowane chunki: ${r.chunksProcessed}")
        println("Zmodyfikowane chunki: ${r.chunksModified}")
        println()
        println("Szczegóły:")
        println("  Bloki usunięte:     ${r.stats.blocksRemoved}")
        println("  TileEntities usunięte: ${r.stats.tileEntitiesRemoved}")
        println("  Entities usunięte:  ${r.stats.entitiesRemoved}")
        println("  Sekcje zmodyfikowane: ${r.stats.sectionsModified}")
        println()
        println("Wymiary: ${r.processedDimensions.joinToString(", ")}")
        println("Czas wykonania: ${time / 1000}s")
        println("=" * 70)
        
        if (dryRun) {
            println()
            println("UWAGA: To był tryb analizy (dry-run). Żadne zmiany nie zostały zapisane.")
            println("Aby wykonać czyszczenie, uruchom bez flagi --dry-run")
        }
    }
    
    println()
    println("Zakończono w ${time / 1000}s")
}

/**
 * Parsuje wartość argumentu
 */
private fun parseArg(args: Array<String>, name: String): String? {
    val index = args.indexOf(name)
    return if (index >= 0 && index < args.size - 1) args[index + 1] else null
}

/**
 * Kopiuje wszystkie regiony ze źródła do celu
 */
private fun copyRegions(source: Path, target: Path) {
    val sourceWorld = source.toFile()
    val targetWorld = target.toFile()
    
    // Funkkcja pomocnicza do kopiowania regionów
    fun copyRegionDir(sourceDir: File, targetDir: File) {
        if (!sourceDir.exists()) return
        
        targetDir.mkdirs()
        
        sourceDir.listFiles { f -> f.name.endsWith(".mca") }?.forEach { region ->
            val targetRegion = File(targetDir, region.name)
            if (!targetRegion.exists()) {
                region.copyTo(targetRegion)
            }
        }
    }
    
    // Overworld
    copyRegionDir(
        source.resolve("region").toFile(),
        target.resolve("region").toFile()
    )
    
    // Nether
    copyRegionDir(
        source.resolve("DIM-1/region").toFile(),
        target.resolve("DIM-1/region").toFile()
    )
    
    // End
    copyRegionDir(
        source.resolve("DIM1/region").toFile(),
        target.resolve("DIM1/region").toFile()
    )
    
    // Inne wymiary
    sourceWorld.listFiles { f -> f.isDirectory && f.name.startsWith("DIM") }?.forEach { dimDir ->
        copyRegionDir(
            File(dimDir, "region"),
            File(targetWorld.resolve(dimDir.name), "region")
        )
    }
}

/**
 * Wyświetla pomoc
 */
private fun printHelp() {
    println("""
        |Map Cleaner - Czyści mapę Minecraft 1.7.10 z modowej zawartości
        |
        |UŻYCIE:
        |  java -jar map-cleaner.jar <ścieżka_świata> [opcje]
        |
        |OPCJE:
        |  --output PATH       Ścieżka docelowa (domyślnie: nadpisuje źródło)
        |  --threads N         Liczba wątków (domyślnie: liczba rdzeni)
        |  --dry-run           Tylko analiza, bez modyfikacji
        |  --backup            Utwórz backup przed czyszczeniem
        |  --rules PATH        Ścieżka do pliku reguł JSON
        |  --dim TYPE          Wymiar do przetworzenia:
        |                       overworld, nether, end, all (domyślnie: all)
        |
        |POZIOMY AKTYWNOŚCI:
        |  --blocks-only       Tylko bloki (bez TileEntities i Entities)
        |  --blocks-and-te     Bloki + TileEntities (bez Entities)
        |  --full              Pełne czyszczenie (wszystko)
        |
        |PRZYKŁADY:
        |  # Analiza (tylko statystyki)
        |  java -jar map-cleaner.jar ../mapa_1710 --dry-run
        |
        |  # Czyszczenie z zapisem do nowej lokalizacji
        |  java -jar map-cleaner.jar ../mapa_1710 --output ../mapa_wyczyszczona
        |
        |  # Czyszczenie w miejscu z backup
        |  java -jar map-cleaner.jar ../mapa_1710 --backup
        |
        |  # Tylko overworld
        |  java -jar map-cleaner.jar ../mapa_1710 --dim overworld --dry-run
        |
        |FORMAT PLIKU REGUŁ (rules.json):
        |  {
        |    "removeBlockIds": [256, 257, ...],
        |    "keepBlockIds": [255, ...],
        |    "removeTileEntityIds": ["appliedenergistics2", "mekanism", ...],
        |    "removeEntityIds": ["customnpcs", ...],
        |    "replacementBlock": 0,
        |    "useHeuristics": true,
        |    "cleanTileEntities": true,
        |    "cleanEntities": true
        |  }
    """.trimMargin())
}

/**
 * Operator mnożenia stringa
 */
private operator fun String.times(n: Int): String = repeat(n)
