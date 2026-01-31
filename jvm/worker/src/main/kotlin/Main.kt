package mc.editkit.worker

import org.json.JSONObject
import org.json.JSONArray
import java.io.File
import java.nio.file.Paths

/**
 * Worker JVM do edycji światów Minecraft 1.7.10 używający Hephaistos
 * Argumenty:
 *   --world <path> - ścieżka do świata
 *   --patch <path> - ścieżka do pliku patch JSON
 */
fun main(args: Array<String>) {
    println("MC EditKit Worker (Hephaistos) v1.0")
    
    // Parsuj argumenty
    var worldPath: String? = null
    var patchPath: String? = null
    
    var i = 0
    while (i < args.size) {
        when (args[i]) {
            "--world" -> worldPath = args.getOrNull(++i)
            "--patch" -> patchPath = args.getOrNull(++i)
        }
        i++
    }
    
    if (worldPath == null || patchPath == null) {
        println("Użycie: java -jar worker.jar --world <path> --patch <path>")
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
