package mc.editkit.worker

import org.json.JSONObject
import java.io.File

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
    
    // Zapisz zmiany
    editor.commit()
    
    println("Edycja zakończona sukcesem.")
}

fun printHelp() {
    println("""
        MC EditKit Worker (Hephaistos) v1.0
        
        Użycie:
          java -jar worker.jar --world <path> --patch <path>
          java -jar worker.jar --world <path> --list-regions
          java -jar worker.jar --world <path> --test-roundtrip
        
        Opcje:
          --world <path>      Ścieżka do katalogu świata Minecraft
          --patch <path>      Ścieżka do pliku JSON z opisem zmian
          --list-regions      Wyświetla listę regionów (Test 1)
          --test-roundtrip    Testuje read/write roundtrip (Test 2)
          --help              Wyświetla tę pomoc
        
        Format pliku patch:
        {
          "edits": [
            {"op": "set_block", "x": 0, "y": 64, "z": 0, "id": 1, "meta": 0},
            {"op": "set_te", "x": 0, "y": 64, "z": 0, "nbt": {"id": "Control", "Command": "/say Hello"}}
          ]
        }
    """.trimIndent())
}
