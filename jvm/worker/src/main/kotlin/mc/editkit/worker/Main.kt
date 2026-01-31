package mc.editkit.worker

import org.json.JSONObject
import java.io.File
import java.nio.file.Paths

/**
 * Worker JVM do edycji światów Minecraft 1.7.10 używający Hephaistos
 * Argumenty:
 *   --world <path> - ścieżka do świata
 *   --patch <path> - ścieżka do pliku patch JSON
 *   --list-regions - wyświetla listę regionów (Test 1)
 *   --test-roundtrip - testuje read/write roundtrip (Test 2)
 *   --help - wyświetla pomoc
 */
fun main(args: Array<String>) {
    println("MC EditKit Worker (Hephaistos) v1.0")
    
    // Parsuj argumenty
    var worldPath: String? = null
    var patchPath: String? = null
    var listRegions = false
    var testRoundtrip = false
    var verifyBlock = false
    var verifyX = 0
    var verifyY = 0
    var verifyZ = 0
    var verifyId = 0
    var verifyMeta = 0
    var showHelp = false
    
    var i = 0
    while (i < args.size) {
        when (args[i]) {
            "--world" -> worldPath = args.getOrNull(++i)
            "--patch" -> patchPath = args.getOrNull(++i)
            "--list-regions" -> listRegions = true
            "--test-roundtrip" -> testRoundtrip = true
            "--verify-block" -> {
                verifyBlock = true
                verifyX = args.getOrNull(++i)?.toIntOrNull() ?: 0
                verifyY = args.getOrNull(++i)?.toIntOrNull() ?: 0
                verifyZ = args.getOrNull(++i)?.toIntOrNull() ?: 0
                verifyId = args.getOrNull(++i)?.toIntOrNull() ?: 0
                verifyMeta = args.getOrNull(++i)?.toIntOrNull() ?: 0
            }
            "--help" -> showHelp = true
        }
        i++
    }
    
    if (showHelp || args.isEmpty()) {
        printHelp()
        System.exit(0)
        return
    }
    
    // Test 1: List regions
    if (listRegions) {
        if (worldPath == null) {
            println("Błąd: --world jest wymagane dla --list-regions")
            System.exit(1)
            return
        }
        listRegions(worldPath)
        return
    }
    
    // Test 2: Roundtrip test
    if (testRoundtrip) {
        if (worldPath == null) {
            println("Błąd: --world jest wymagane dla --test-roundtrip")
            System.exit(1)
            return
        }
        testReadWriteRoundtrip(worldPath)
        return
    }
    
    // Test 3: Verify block
    if (verifyBlock) {
        if (worldPath == null) {
            println("Błąd: --world jest wymagane dla --verify-block")
            System.exit(1)
            return
        }
        testBlockSet(worldPath, verifyX, verifyY, verifyZ, verifyId, verifyMeta)
        return
    }
    
    // Test 4: Verify command block
    if (args.contains("--verify-command-block")) {
        if (worldPath == null) {
            println("Błąd: --world jest wymagane dla --verify-command-block")
            System.exit(1)
            return
        }
        testCommandBlock(worldPath, 0, 64, 1)
        return
    }
    
    // Weryfikacja testowego układu redstone
    if (args.contains("--verify-redstone-test")) {
        if (worldPath == null) {
            println("Błąd: --world jest wymagane dla --verify-redstone-test")
            System.exit(1)
            return
        }
        verifyRedstoneTest(worldPath)
        return
    }
    
    // Weryfikacja testu 2
    if (args.contains("--verify-test2")) {
        if (worldPath == null) {
            println("Błąd: --world jest wymagane dla --verify-test2")
            System.exit(1)
            return
        }
        verifyTest2(worldPath)
        return
    }
    
    // Test 6: Multi-chunk
    if (args.contains("--generate-multichunk")) {
        val patch = generateMultiChunkTest(0, 64, 0)
        val outputFile = args.getOrNull(args.indexOf("--generate-multichunk") + 1) ?: "multichunk_patch.json"
        java.io.File(outputFile).writeText(patch.toString(2))
        println("Wygenerowano multi-chunk patch: $outputFile")
        return
    }
    
    // Test 7: Spiral R=1
    if (args.contains("--generate-spiral-r1")) {
        val spiral = generateSpiral(0, 64, 0, radius = 1)
        val patch = spiralToPatch(spiral)
        val outputFile = args.getOrNull(args.indexOf("--generate-spiral-r1") + 1) ?: "spiral_r1_patch.json"
        java.io.File(outputFile).writeText(patch.toString(2))
        println("Wygenerowano spiralę R=1: ${spiral.size} punktów, ${spiral.count { it.isCheckpoint }} checkpointów -> $outputFile")
        return
    }
    
    // Test 8: Spiral R=3
    if (args.contains("--generate-spiral-r3")) {
        val spiral = generateSpiral(0, 64, 0, radius = 3)
        val patch = spiralToPatch(spiral)
        val outputFile = args.getOrNull(args.indexOf("--generate-spiral-r3") + 1) ?: "spiral_r3_patch.json"
        java.io.File(outputFile).writeText(patch.toString(2))
        println("Wygenerowano spiralę R=3: ${spiral.size} punktów, ${spiral.count { it.isCheckpoint }} checkpointów -> $outputFile")
        return
    }
    
    // Weryfikacja spirali
    if (args.contains("--verify-spiral")) {
        if (worldPath == null) {
            println("Błąd: --world jest wymagane")
            System.exit(1)
            return
        }
        val expected = args.getOrNull(args.indexOf("--verify-spiral") + 1)?.toIntOrNull() ?: 0
        verifySpiral(worldPath, expected)
        return
    }
    
    // Walidacja świata (pre-flight check)
    if (args.contains("--validate-world")) {
        if (worldPath == null) {
            println("Błąd: --world jest wymagane dla --validate-world")
            System.exit(1)
            return
        }
        validateWorldCommand(worldPath)
        return
    }
    
    // Analiza redstone
    if (args.contains("--analyze-redstone")) {
        if (worldPath == null) {
            println("Błąd: --world jest wymagane dla --analyze-redstone")
            System.exit(1)
            return
        }
        val radius = args.getOrNull(args.indexOf("--analyze-redstone") + 1)?.toIntOrNull() ?: 2
        analyzeRedstoneCommand(worldPath, radius)
        return
    }
    
    // Wykrywanie wzorca spirali
    if (args.contains("--detect-spiral")) {
        if (worldPath == null) {
            println("Błąd: --world jest wymagane dla --detect-spiral")
            System.exit(1)
            return
        }
        detectSpiralPattern(worldPath)
        return
    }
    
    // Inspekcja konkretnych chunków
    if (args.contains("--inspect-chunks")) {
        if (worldPath == null) {
            println("Błąd: --world jest wymagane dla --inspect-chunks")
            System.exit(1)
            return
        }
        // Sprawdź chunki: (0,0), (-1,-1), (0,-1), (-1,0)
        inspectChunks(worldPath, listOf(
            Pair(0, 0),
            Pair(-1, -1),
            Pair(0, -1),
            Pair(-1, 0)
        ))
        return
    }
    
    // Analiza wszystkich pobliskich chunków
    if (args.contains("--inspect-all-nearby")) {
        if (worldPath == null) {
            println("Błąd: --world jest wymagane")
            System.exit(1)
            return
        }
        inspectAllNearbyChunks(worldPath)
        return
    }
    
    // Pełne skanowanie obszaru -5 do 4
    if (args.contains("--scan-full-area")) {
        if (worldPath == null) {
            println("Błąd: --world jest wymagane")
            System.exit(1)
            return
        }
        scanFullArea(worldPath)
        return
    }
    
    // Poprawiona analiza - wszystkie poziomy Y
    if (args.contains("--correct-analysis")) {
        if (worldPath == null) {
            println("Błąd: --world jest wymagane")
            System.exit(1)
            return
        }
        correctAnalysis(worldPath)
        return
    }
    
    // Szeroka analiza wszystkich regionów
    if (args.contains("--wide-analysis")) {
        if (worldPath == null) {
            println("Błąd: --world jest wymagane")
            System.exit(1)
            return
        }
        wideAreaAnalysis(worldPath)
        return
    }
    
    // Wizualizacja mapy SVG
    if (args.contains("--visualize-svg")) {
        if (worldPath == null) {
            println("Błąd: --world jest wymagane")
            System.exit(1)
            return
        }
        val outputFile = args.getOrNull(args.indexOf("--visualize-svg") + 1) ?: "map_visualization.svg"
        visualizeMapArea(worldPath, -70, -70, 70, 70, outputFile)
        return
    }
    
    // Wizualizacja 4 chunków spirali
    if (args.contains("--visualize-spiral")) {
        if (worldPath == null) {
            println("Błąd: --world jest wymagane")
            System.exit(1)
            return
        }
        val outputDir = args.getOrNull(args.indexOf("--visualize-spiral") + 1) ?: "spiral_visualization"
        visualizeSpiralChunks(worldPath, outputDir)
        return
    }
    
    // Uruchomienie serwera z walidacją
    if (args.contains("--launch-server")) {
        val serverDir = args.getOrNull(args.indexOf("--launch-server") + 1)
        val worldName = args.getOrNull(args.indexOf("--launch-server") + 2)
        val port = args.getOrNull(args.indexOf("--launch-server") + 3)?.toIntOrNull() ?: 25565
        
        if (serverDir == null || worldName == null) {
            println("Błąd: --launch-server <server-dir> <world-name> [port]")
            System.exit(1)
            return
        }
        launchServerCommand(serverDir, worldName, port)
        return
    }
    
    // Normalna operacja edycji
    if (worldPath == null || patchPath == null) {
        println("Użycie: java -jar worker.jar --world <path> --patch <path>")
        println("Lub: java -jar worker.jar --world <path> --list-regions")
        println("Lub: java -jar worker.jar --world <path> --test-roundtrip")
        System.exit(1)
        return
    }
    
    println("Świat: $worldPath")
    println("Patch: $patchPath")
    
    // Wczytaj patch
    val patchFile = File(patchPath)
    if (!patchFile.exists()) {
        println("Błąd: Plik patch nie istnieje: $patchPath")
        System.exit(1)
        return
    }
    
    val patchJson = JSONObject(patchFile.readText())
    val edits = patchJson.getJSONArray("edits")
    
    println("Edits do wykonania: ${edits.length()}")
    
    // Wykonaj edycje
    val editor = WorldEditor(worldPath)
    
    for (j in 0 until edits.length()) {
        val edit = edits.getJSONObject(j)
        val op = edit.getString("op")
        
        when (op) {
            "set_block" -> {
                val x = edit.getInt("x")
                val y = edit.getInt("y")
                val z = edit.getInt("z")
                val id = edit.getInt("id")
                val meta = edit.optInt("meta", 0)
                editor.setBlock(x, y, z, id, meta)
            }
            "set_te" -> {
                val x = edit.getInt("x")
                val y = edit.getInt("y")
                val z = edit.getInt("z")
                val nbt = edit.getJSONObject("nbt")
                editor.setTileEntity(x, y, z, nbt)
            }
            else -> println("Nieznana operacja: $op")
        }
    }
    
    // Zapisz zmiany z metadanymi
    val metadataPath = editor.commit(
        toolName = "MC-EditKit Worker",
        description = "Applied patch: ${File(patchPath).name} (${edits.length()} edits)"
    )
    
    println("Edycja zakończona sukcesem.")
    if (metadataPath != null) {
        println("Metadane zapisane: ${metadataPath.fileName}")
    }
}

fun printHelp() {
    println("""
        MC EditKit Worker (Hephaistos) v1.0
        
        UŻYCIE:
          java -jar worker.jar --world <path> --patch <path>
          java -jar worker.jar --world <path> --list-regions
          java -jar worker.jar --world <path> --test-roundtrip
          java -jar worker.jar --world <path> --validate-world
          java -jar worker.jar --launch-server <server-dir> <world-name> [port]
        
        OPCJE:
          --world <path>           Ścieżka do katalogu świata Minecraft
          --patch <path>           Ścieżka do pliku JSON z opisem zmian
          --list-regions           Wyświetla listę regionów (Test 1)
          --test-roundtrip         Testuje read/write roundtrip (Test 2)
          --validate-world         Sprawdza świat przed uruchomieniem serwera
          --launch-server <d> <w>  Uruchamia serwer z pre-flight validation
          --help                   Wyświetla tę pomoc
        
        PRZYKŁADY:
          # Walidacja świata
          java -jar worker.jar --world headless_server/1.7.10/spiral_y100 --validate-world
          
          # Analiza redstone w chunkach wokół 0,0
          java -jar worker.jar --world map_read_write_tests/kimi1 --analyze-redstone 2
          
          # Uruchomienie serwera z walidacją (domyślny port 25565)
          java -jar worker.jar --launch-server headless_server/1.7.10 spiral_y100
        
        Format pliku patch:
        {
          "edits": [
            {"op": "set_block", "x": 0, "y": 64, "z": 0, "id": 1, "meta": 0},
            {"op": "set_te", "x": 0, "y": 64, "z": 0, "nbt": {"id": "Control", "Command": "/say Hello"}}
          ]
        }
    """.trimIndent())
}

/**
 * Komenda walidacji świata
 */
fun validateWorldCommand(worldPath: String) {
    println("=".repeat(60))
    println("WERYFIKACJA ŚWIATA: $worldPath")
    println("=".repeat(60))
    
    val result = WorldValidator.validateWorld(java.nio.file.Paths.get(worldPath))
    
    if (result == null) {
        println("❌ BRAK METADANYCH")
        println("Świat nie ma pliku editkit_metadata.json")
        println("Nie można przeprowadzić weryfikacji.")
        System.exit(1)
        return
    }
    
    println(result.formatReport())
    
    if (result.isValid) {
        println("✅ Świat zweryfikowany pomyślnie!")
        System.exit(0)
    } else {
        println("❌ WERYFIKACJA NIE POWIODŁA SIĘ!")
        println("Napraw błędy przed uruchomieniem serwera.")
        System.exit(1)
    }
}

/**
 * Komenda uruchomienia serwera z walidacją
 */
fun launchServerCommand(serverDir: String, worldName: String, port: Int) {
    println("=".repeat(60))
    println("URUCHAMIANIE SERWERA Z WALIDACJĄ")
    println("=".repeat(60))
    println("Server dir: $serverDir")
    println("World: $worldName")
    println("Port: $port")
    println()
    
    val launcher = ServerLauncher(
        serverDir = java.nio.file.Paths.get(serverDir),
        javaPath = "C:\\Program Files (x86)\\Common Files\\Oracle\\Java\\java8path\\java.exe"
    )
    
    val config = ServerLauncher.LaunchConfig(
        worldName = worldName,
        port = port
    )
    
    val result = launcher.launchAndWait(config, skipValidation = false, timeoutSeconds = 120)
    
    println()
    println("=".repeat(60))
    if (result.success) {
        println("✅ ${result.message}")
        println("=".repeat(60))
        System.exit(0)
    } else {
        println("❌ ${result.message}")
        println("=".repeat(60))
        System.exit(1)
    }
}
