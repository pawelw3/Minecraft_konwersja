package mapcleaner

import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import java.io.File

/**
 * Reguły czyszczenia mapy - definiuje które bloki, TileEntities i Entities są uznawane za modowe
 */
data class CleaningRules(
    /** Lista ID bloków do usunięcia (pusta lista = użyj heurystyki >= 256) */
    val removeBlockIds: Set<Int> = emptySet(),
    /** Lista ID bloków do zachowania (whitelist) */
    val keepBlockIds: Set<Int> = emptySet(),
    /** Prefiksy ID TileEntities do usunięcia */
    val removeTileEntityIds: Set<String> = emptySet(),
    /** Prefiksy ID Entities do usunięcia */
    val removeEntityIds: Set<String> = emptySet(),
    /** ID bloku zastępczego (domyślnie 0 = air) */
    val replacementBlock: Int = 0,
    /** Czy używać heurystyki (bloki >= 256 są modowe) */
    val useHeuristics: Boolean = true,
    /** Czy czyścić TileEntities */
    val cleanTileEntities: Boolean = true,
    /** Czy czyścić Entities */
    val cleanEntities: Boolean = true,
    /** Vanilla block IDs (0-175 dla 1.7.10) */
    val vanillaBlockIds: Set<Int> = (0..175).toSet()
) {
    /**
     * Sprawdza czy blok o danym ID jest modowy
     */
    fun isModBlock(fullId: Int): Boolean {
        // Jeśli w whitelist - nie jest modowy
        if (fullId in keepBlockIds) return false
        
        // Jeśli w liście do usunięcia - jest modowy
        if (fullId in removeBlockIds) return true
        
        // Heurystyka: bloki >= 256 są modowe (dla 1.7.10)
        if (useHeuristics && fullId >= 256) return true
        
        return false
    }
    
    /**
     * Sprawdza czy TileEntity jest modowe
     */
    fun isModTileEntity(id: String?): Boolean {
        if (id == null) return false
        
        // Jeśli nie jest w vanilla - jest modowe
        if (!isVanillaTileEntity(id)) {
            // Sprawdź czy pasuje do prefiksów do usunięcia
            if (removeTileEntityIds.isEmpty()) return true
            return removeTileEntityIds.any { prefix -> id.startsWith(prefix) || id.contains(prefix) }
        }
        
        return false
    }
    
    /**
     * Sprawdza czy Entity jest modowe
     */
    fun isModEntity(id: String?): Boolean {
        if (id == null) return false
        
        // Jeśli nie jest w vanilla - jest modowe
        if (!isVanillaEntity(id)) {
            // Sprawdź czy pasuje do prefiksów do usunięcia
            if (removeEntityIds.isEmpty()) return true
            return removeEntityIds.any { prefix -> id.startsWith(prefix) || id.contains(prefix) }
        }
        
        return false
    }
    
    /**
     * Sprawdza czy TileEntity jest vanilla
     */
    private fun isVanillaTileEntity(id: String): Boolean {
        return id in VANILLA_TILE_ENTITIES || id.startsWith("minecraft:") && id.substring(10) in VANILLA_TILE_ENTITIES
    }
    
    /**
     * Sprawdza czy Entity jest vanilla
     */
    private fun isVanillaEntity(id: String): Boolean {
        return id in VANILLA_ENTITIES || id.startsWith("minecraft:") && id.substring(10) in VANILLA_ENTITIES
    }
    
    companion object {
        /** Vanilla TileEntities w 1.7.10 */
        val VANILLA_TILE_ENTITIES = setOf(
            "Sign", "MobSpawner", "Chest", "EnderChest", "Dropper", "Hopper", "Dispenser",
            "Furnace", "BrewingStand", "NoteBlock", "Jukebox", "RecordPlayer",
            "Trap", "EnchantTable", "CommandBlock", "Beacon", "Skull",
            "Comparator", "FlowerPot", "Banner", "EndGateway", "Structure",
            "Control", // Command block
            "AirPortal", // End portal
            "DaylightDetector", "RedstoneLight",
            "Cauldron", "Music", "Piston", // Piston extension
            "AirPortal", // Portal
            "FlowerPot"
        )
        
        /** Vanilla Entities w 1.7.10 */
        val VANILLA_ENTITIES = setOf(
            "Item", "XPOrb", "LeashKnot", "Painting", "Arrow", "Snowball",
            "Fireball", "SmallFireball", "ThrownEnderpearl", "EyeOfEnderSignal",
            "ThrownPotion", "ThrownExpBottle", "ItemFrame", "WitherSkull",
            "PrimedTnt", "FallingSand", "FireworksRocketEntity",
            "Boat", "MinecartRideable", "MinecartChest", "MinecartFurnace",
            "MinecartTNT", "MinecartHopper", "MinecartSpawner", "MinecartCommandBlock",
            "Creeper", "Skeleton", "Spider", "Giant", "Zombie", "Slime",
            "Ghast", "PigZombie", "Enderman", "CaveSpider", "Silverfish",
            "Blaze", "LavaSlime", "EnderDragon", "WitherBoss", "Bat",
            "Witch", "Pig", "Sheep", "Cow", "Chicken", "Squid", "Wolf",
            "MushroomCow", "SnowMan", "Ozelot", "VillagerGolem", "EntityHorse",
            "Villager", "EnderCrystal"
        )
        
        /**
         * Wczytuje reguły z pliku JSON
         */
        fun fromFile(file: File): CleaningRules {
            if (!file.exists()) {
                println("Plik reguł nie istnieje: ${file.absolutePath}, używam domyślnych")
                return CleaningRules()
            }
            
            return try {
                val gson = Gson()
                val json = file.readText()
                gson.fromJson(json, CleaningRules::class.java)
            } catch (e: Exception) {
                println("Błąd wczytywania reguł: ${e.message}, używam domyślnych")
                CleaningRules()
            }
        }
        
        /**
         * Tworzy domyślny plik reguł
         */
        fun createDefaultRules(file: File) {
            val rules = CleaningRules(
                removeTileEntityIds = setOf(
                    "appliedenergistics2", "AE2", "mekanism", "Mekanism",
                    "thermalexpansion", "ThermalExpansion", "tconstruct",
                    "TConstruct", "enderio", "EnderIO", "buildcraft", "BuildCraft",
                    "ic2", "IC2", "forestry", "Forestry", "railcraft", "Railcraft",
                    "bibliocraft", "BiblioCraft", "chisel", "Chisel",
                    "ironchest", "IronChest", "jabb", "JABBA", "logisticspipes", "LogisticsPipes"
                ),
                removeEntityIds = setOf(
                    "appliedenergistics2", "mekanism", "thermalexpansion", 
                    "tconstruct", "enderio", "buildcraft", "ic2", "forestry",
                    "railcraft", "bibliocraft", "chisel", "ironchest", "jabb"
                )
            )
            
            val gson = Gson()
            file.writeText(gson.toJson(rules))
        }
    }
}
