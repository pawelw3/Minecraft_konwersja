package mc.editkit.worker

import org.jglrxavpok.hephaistos.mca.RegionFile
import org.jglrxavpok.hephaistos.nbt.*
import org.json.JSONObject
import java.io.RandomAccessFile
import java.nio.file.Path
import java.nio.file.Paths

/**
 * Generator testowej mapy z blokami Enchanting Plus dla wersji 1.7.10
 * 
 * Tworzy:
 * - enchanting_table (podstawowy stół)
 * - advanced_table (zaawansowany stół)
 * - arcane_inscriber (konwerter książek -> zwoje)
 * 
 * Z różnymi stanami Tile Entities (z inventory i bez)
 */
class EnchantingPlusTestWorldGenerator(private val worldPath: String) {
    private val regionPath = Paths.get(worldPath, "region")
    private val editor = WorldEditor(worldPath)
    
    // ID bloków Enchanting Plus (numeryczne ID zależą od modpacka, używamy typowych)
    // W 1.7.10 ID są przydzielane dynamicznie, ale dla testów używamy wysokich ID (>200)
    companion object {
        // Typowe ID dla Enchanting Plus w modpackach (mogą się różnić)
        const val EP_ENCHANTING_TABLE_ID = 210  // Przykładowe ID
        const val EP_ADVANCED_TABLE_ID = 211
        const val EP_ARCANE_INSCRIBER_ID = 212
        
        // Metadata (zazwyczaj 0 dla bloków EP)
        const val META_DEFAULT = 0
    }
    
    init {
        if (!regionPath.toFile().exists()) {
            regionPath.toFile().mkdirs()
        }
    }
    
    /**
     * Generuje kompletną testową mapę z blokami Enchanting Plus
     */
    fun generateTestWorld() {
        println("=" * 60)
        println("GENERATOR TESTOWEJ MAPY ENCHANTING PLUS")
        println("=" * 60)
        println("Ścieżka: $worldPath")
        println()
        
        // Stwórz podłogę (kamień) dla testów
        createPlatform(0, 63, 0, 20, 20)
        
        // Rząd 1: Podstawowe stoły enchantujące
        println("\n--- Rząd 1: Podstawowe stoły enchantujące ---")
        createEnchantingTable(2, 64, 2, "basic", emptyMap())
        createEnchantingTable(4, 64, 2, "with_player", mapOf("lastPlayer" to "TestPlayer"))
        createEnchantingTable(6, 64, 2, "with_inventory", mapOf(
            "Items" to listOf(
                mapOf("id" to 403, "Count" to 1, "Damage" to 0, "Slot" to 0),  // Enchanted Book
                mapOf("id" to 267, "Count" to 1, "Damage" to 0, "Slot" to 1)   // Iron Sword
            )
        ))
        
        // Rząd 2: Zaawansowane stoły
        println("\n--- Rząd 2: Zaawansowane stoły enchantujące ---")
        createAdvancedTable(2, 64, 5, "basic", emptyMap())
        createAdvancedTable(4, 64, 5, "with_repair_data", mapOf(
            "repairCost" to 15,
            "playerKnowledge" to listOf("sharpness", "efficiency", "unbreaking")
        ))
        createAdvancedTable(6, 64, 5, "full_inventory", mapOf(
            "Items" to listOf(
                mapOf("id" to 276, "Count" to 1, "Damage" to 10, "Slot" to 0,  // Diamond Sword damaged
                      "tag" to mapOf("ench" to listOf(mapOf("id" to 16, "lvl" to 3)))),  // Sharpness III
                mapOf("id" to 278, "Count" to 1, "Damage" to 0, "Slot" to 1,   // Diamond Pickaxe
                      "tag" to mapOf("ench" to listOf(
                          mapOf("id" to 32, "lvl" to 4),  // Efficiency IV
                          mapOf("id" to 34, "lvl" to 3)   // Unbreaking III
                      )))
            )
        ))
        
        // Rząd 3: Arcane Inscriber (do usunięcia w konwersji)
        println("\n--- Rząd 3: Arcane Inscriber (do usunięcia) ---")
        createArcaneInscriber(2, 64, 8, "empty", emptyMap())
        createArcaneInscriber(4, 64, 8, "with_scrolls", mapOf(
            "storedScrolls" to listOf(
                mapOf("enchantId" to 16, "enchantLevel" to 5, "scrollType" to "weapon"),
                mapOf("enchantId" to 32, "enchantLevel" to 4, "scrollType" to "tool")
            ),
            "Items" to listOf(
                mapOf("id" to 403, "Count" to 5, "Damage" to 0, "Slot" to 0)  // Stack of enchanted books
            )
        ))
        createArcaneInscriber(6, 64, 8, "complex_state", mapOf(
            "currentRecipe" to mapOf("input" to "book", "output" to "scroll", "cost" to 10),
            "progress" to 50,
            "playerOwner" to "TestPlayer123"
        ))
        
        // Rząd 4: Kombinacje bloków (różne typy obok siebie)
        println("\n--- Rząd 4: Kombinacje bloków ---")
        createEnchantingTable(10, 64, 2, "combo_1", emptyMap())
        createAdvancedTable(11, 64, 2, "combo_2", emptyMap())
        createArcaneInscriber(12, 64, 2, "combo_3", emptyMap())
        
        // Zapisz wszystkie zmiany
        println("\n--- Zapisywanie zmian ---")
        editor.commit("EnchantingPlusTestWorldGenerator", "Testowa mapa z blokami Enchanting Plus 1.7.10")
        
        // Generuj metadane
        generateMetadata()
        
        println("\n" + "=" * 60)
        println("GENEROWANIE ZAKOŃCZONE")
        println("=" * 60)
        println("Lokalizacja: $worldPath")
        println("Region files: ${regionPath.toFile().list()?.joinToString()}")
    }
    
    /**
     * Tworzy podstawowy stół enchantujący z Tile Entity
     */
    private fun createEnchantingTable(x: Int, y: Int, z: Int, variant: String, extraData: Map<String, Any>) {
        // Ustaw blok (w 1.7.10 używamy stone jako placeholder - mod zamieni na właściwy blok)
        // W prawdziwej mapie ID są dynamiczne, tu używamy stone (1) jako placeholder
        editor.setBlock(x, y, z, 1, 0)  // Stone jako placeholder
        
        // Stwórz Tile Entity dla enchanting table
        val teNBT = createTileEntityNBT(x, y, z, "EnchantingPlus:enchanting_table", extraData)
        editor.setTileEntity(x, y, z, teNBT)
        
        println("  Created enchanting_table at ($x, $y, $z) variant=$variant")
    }
    
    /**
     * Tworzy zaawansowany stół enchantujący z Tile Entity
     */
    private fun createAdvancedTable(x: Int, y: Int, z: Int, variant: String, extraData: Map<String, Any>) {
        editor.setBlock(x, y, z, 1, 0)  // Stone jako placeholder
        
        val teNBT = createTileEntityNBT(x, y, z, "EnchantingPlus:advanced_table", extraData)
        editor.setTileEntity(x, y, z, teNBT)
        
        println("  Created advanced_table at ($x, $y, $z) variant=$variant")
    }
    
    /**
     * Tworzy Arcane Inscriber z Tile Entity
     */
    private fun createArcaneInscriber(x: Int, y: Int, z: Int, variant: String, extraData: Map<String, Any>) {
        editor.setBlock(x, y, z, 1, 0)  // Stone jako placeholder
        
        val teNBT = createTileEntityNBT(x, y, z, "EnchantingPlus:arcane_inscriber", extraData)
        editor.setTileEntity(x, y, z, teNBT)
        
        println("  Created arcane_inscriber at ($x, $y, $z) variant=$variant")
    }
    
    /**
     * Tworzy NBT dla Tile Entity Enchanting Plus
     */
    private fun createTileEntityNBT(x: Int, y: Int, z: Int, id: String, extraData: Map<String, Any>): JSONObject {
        val nbt = JSONObject()
        nbt.put("id", id)
        nbt.put("x", x)
        nbt.put("y", y)
        nbt.put("z", z)
        
        // Dodaj extra dane
        for ((key, value) in extraData) {
            when (value) {
                is String -> nbt.put(key, value)
                is Int -> nbt.put(key, value)
                is Double -> nbt.put(key, value)
                is Boolean -> nbt.put(key, value)
                is List<*> -> nbt.put(key, value)
                is Map<*, *> -> nbt.put(key, JSONObject(value))
            }
        }
        
        return nbt
    }
    
    /**
     * Tworzy platformę z kamienia
     */
    private fun createPlatform(startX: Int, startY: Int, startZ: Int, width: Int, depth: Int) {
        println("Tworzenie platformy ${width}x$depth...")
        for (x in 0 until width) {
            for (z in 0 until depth) {
                editor.setBlock(startX + x, startY, startZ + z, 1, 0)  // Stone
            }
        }
    }
    
    /**
     * Generuje metadane dla testowej mapy
     */
    private fun generateMetadata() {
        val metadata = JSONObject()
        metadata.put("generator", "EnchantingPlusTestWorldGenerator")
        metadata.put("version", "1.7.10")
        metadata.put("created", System.currentTimeMillis())
        metadata.put("blocks", JSONObject().apply {
            put("enchanting_table", 3)
            put("advanced_table", 3)
            put("arcane_inscriber", 3)
        })
        metadata.put("variants", listOf(
            "basic", "with_player", "with_inventory",
            "with_repair_data", "full_inventory",
            "empty", "with_scrolls", "complex_state",
            "combo_1", "combo_2", "combo_3"
        ))
        metadata.put("conversion_target", "Enchanting Infuser 1.18.2")
        
        val metadataPath = Paths.get(worldPath, "ep_test_metadata.json")
        metadataPath.toFile().writeText(metadata.toString(2))
        println("Metadane zapisane do: $metadataPath")
    }
    
    private operator fun String.times(n: Int): String = this.repeat(n)
}

/**
 * Główna funkcja do uruchomienia generatora
 */
fun main(args: Array<String>) {
    val worldPath = args.getOrElse(0) { "lightweigh_map_templates/1710_modded/ep_test_world" }
    
    val generator = EnchantingPlusTestWorldGenerator(worldPath)
    generator.generateTestWorld()
}
