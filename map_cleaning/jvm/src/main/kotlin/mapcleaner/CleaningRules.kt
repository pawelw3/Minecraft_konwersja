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
        // Vanilla bloki: 0-175 (w 1.7.10 jest ich dokładnie 176)
        // Dodatkowe vanilla: 256+ to już mody
        if (useHeuristics && fullId >= 256) return true
        
        return false
    }
    
    /**
     * Sprawdza czy TileEntity jest modowe
     */
    fun isModTileEntity(id: String?): Boolean {
        if (id == null) return false
        
        // Normalizuj ID (usuń prefiks "minecraft:" jeśli jest)
        val normalizedId = if (id.startsWith("minecraft:")) id.substring(10) else id
        
        // Jeśli to vanilla - nie usuwaj
        if (isVanillaTileEntity(normalizedId)) {
            return false
        }
        
        // Jeśli lista removeTileEntityIds jest pusta - wszystko co nie vanilla jest modowe
        if (removeTileEntityIds.isEmpty()) return true
        
        // Sprawdź czy pasuje do prefiksów do usunięcia (case-insensitive)
        val lowerId = id.lowercase()
        return removeTileEntityIds.any { prefix -> 
            lowerId.startsWith(prefix.lowercase()) || 
            lowerId.contains(":" + prefix.lowercase())
        }
    }
    
    /**
     * Sprawdza czy Entity jest modowe
     */
    fun isModEntity(id: String?): Boolean {
        if (id == null) return false
        
        // Normalizuj ID
        val normalizedId = if (id.startsWith("minecraft:")) id.substring(10) else id
        
        // Jeśli to vanilla - nie usuwaj
        if (isVanillaEntity(normalizedId)) {
            return false
        }
        
        // Jeśli lista removeEntityIds jest pusta - wszystko co nie vanilla jest modowe
        if (removeEntityIds.isEmpty()) return true
        
        // Sprawdź czy pasuje do prefiksów do usunięcia (case-insensitive)
        val lowerId = id.lowercase()
        return removeEntityIds.any { prefix -> 
            lowerId.startsWith(prefix.lowercase()) || 
            lowerId.contains(":" + prefix.lowercase())
        }
    }
    
    /**
     * Sprawdza czy TileEntity jest vanilla
     */
    private fun isVanillaTileEntity(id: String): Boolean {
        return id in VANILLA_TILE_ENTITIES
    }
    
    /**
     * Sprawdza czy Entity jest vanilla
     */
    private fun isVanillaEntity(id: String): Boolean {
        return id in VANILLA_ENTITIES
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
         * Prefiksy TileEntities dla wszystkich modów z modpacku 1.7.10
         */
        val MOD_TILE_ENTITY_PREFIXES = setOf(
            // Applied Energistics 2
            "appliedenergistics2", "AE2", "appeng",
            
            // Mekanism
            "mekanism", "Mekanism",
            
            // Thermal Series
            "thermalexpansion", "ThermalExpansion", "thermalfoundation", "ThermalFoundation",
            "thermaldynamics", "ThermalDynamics",
            
            // Tinkers' Construct
            "tconstruct", "TConstruct",
            
            // BuildCraft
            "buildcraft", "BuildCraft",
            
            // IndustrialCraft 2
            "ic2", "IC2",
            
            // Forestry
            "forestry", "Forestry",
            
            // Railcraft
            "railcraft", "Railcraft",
            
            // BiblioCraft
            "bibliocraft", "BiblioCraft",
            
            // Chisel
            "chisel", "Chisel",
            
            // Iron Chests / JABBA
            "ironchest", "IronChest", "jabb", "JABBA",
            
            // Logistics Pipes
            "logisticspipes", "LogisticsPipes",
            
            // Thaumcraft
            "thaumcraft", "Thaumcraft",
            
            // Witchery
            "witchery", "Witchery",
            
            // Blood Magic
            "bloodmagic", "BloodMagic", "AWWayofTime",
            
            // ProjectRed
            "projectred", "ProjectRed",
            
            // ComputerCraft
            "computercraft", "ComputerCraft",
            
            // OpenComputers
            "opencomputers", "OpenComputers",
            
            // Big Reactors
            "bigreactors", "BigReactors",
            
            // EnderStorage / Ender IO
            "enderstorage", "EnderStorage", "enderio", "EnderIO",
            
            // Carpenter's Blocks
            "carpentersblocks", "CarpentersBlocks",
            
            // Extra Utilities
            "extrautilities", "ExtraUtilities",
            
            // Growthcraft
            "growthcraft", "Growthcraft",
            
            // Pam's HarvestCraft
            "harvestcraft", "HarvestCraft",
            
            // Traincraft
            "traincraft", "Traincraft",
            
            // Flan's Mod
            "flansmod", "FlansMod",
            
            // CustomNPCs
            "customnpcs", "CustomNPCs",
            
            // MrCrayfish Furniture
            "cfm", "CFM", "furniture", "Furniture",
            
            // Open Modular Turrets
            "openmodularturrets", "OpenModularTurrets",
            
            // Statues
            "statues", "Statues",
            
            // Armourer's Workshop
            "armourers", "Armourers", " ArmourersWorkshop",
            
            // Backpacks
            "backpack", "Backpack",
            
            // Better Storage
            "betterstorage", "BetterStorage",
            
            // Nuclear Control
            "ic2nuclearcontrol", "IC2NuclearControl",
            
            // Enchanting Plus
            "enchantingplus", "EnchantingPlus",
            
            // Reliquary
            "xreliquary", "XReliquary", "reliquary", "Reliquary",
            
            // Thaumic addons
            "thaumicenergistics", "ThaumicEnergistics",
            "thaumicexploration", "ThaumicExploration",
            "thaumichorizons", "ThaumicHorizons",
            "thaumictinkerer", "ThaumicTinkerer",
            
            // AsieLib
            "asielib", "AsieLib",
            
            // Placeable Items
            "placeableitems", "PlaceableItems",
            
            // Jammy Furniture
            "jammyfurniture", "JammyFurniture",
            
            // Power Converters
            "powerconverters", "PowerConverters",
            
            // BuildCraft Compat
            "buildcraftcompat", "BuildCraftCompat"
        )
        
        /**
         * Prefiksy Entities dla wszystkich modów z modpacku 1.7.10
         */
        val MOD_ENTITY_PREFIXES = setOf(
            // Applied Energistics 2
            "appliedenergistics2", "AE2", "appeng",
            
            // Mekanism
            "mekanism", "Mekanism",
            
            // Thermal Series
            "thermalexpansion", "ThermalExpansion", "thermalfoundation", "ThermalFoundation",
            "thermaldynamics", "ThermalDynamics",
            
            // Tinkers' Construct
            "tconstruct", "TConstruct",
            
            // BuildCraft
            "buildcraft", "BuildCraft",
            
            // IndustrialCraft 2
            "ic2", "IC2",
            
            // Forestry
            "forestry", "Forestry",
            
            // Railcraft
            "railcraft", "Railcraft",
            
            // BiblioCraft
            "bibliocraft", "BiblioCraft",
            
            // Chisel
            "chisel", "Chisel",
            
            // Iron Chests / JABBA
            "ironchest", "IronChest", "jabb", "JABBA",
            
            // Logistics Pipes
            "logisticspipes", "LogisticsPipes",
            
            // Thaumcraft
            "thaumcraft", "Thaumcraft",
            
            // Witchery
            "witchery", "Witchery",
            
            // Blood Magic
            "bloodmagic", "BloodMagic", "AWWayofTime",
            
            // ProjectRed
            "projectred", "ProjectRed",
            
            // ComputerCraft
            "computercraft", "ComputerCraft",
            
            // OpenComputers
            "opencomputers", "OpenComputers",
            
            // Big Reactors
            "bigreactors", "BigReactors",
            
            // EnderStorage / Ender IO
            "enderstorage", "EnderStorage", "enderio", "EnderIO",
            
            // Carpenter's Blocks
            "carpentersblocks", "CarpentersBlocks",
            
            // Extra Utilities
            "extrautilities", "ExtraUtilities",
            
            // Growthcraft
            "growthcraft", "Growthcraft",
            
            // Pam's HarvestCraft
            "harvestcraft", "HarvestCraft",
            
            // Traincraft
            "traincraft", "Traincraft",
            
            // Flan's Mod
            "flansmod", "FlansMod",
            
            // CustomNPCs
            "customnpcs", "CustomNPCs",
            
            // MrCrayfish Furniture
            "cfm", "CFM", "furniture", "Furniture",
            
            // Open Modular Turrets
            "openmodularturrets", "OpenModularTurrets",
            
            // Statues
            "statues", "Statues",
            
            // Armourer's Workshop
            "armourers", "Armourers",
            
            // Backpacks
            "backpack", "Backpack",
            
            // Better Storage
            "betterstorage", "BetterStorage",
            
            // Nuclear Control
            "ic2nuclearcontrol", "IC2NuclearControl",
            
            // Reliquary
            "xreliquary", "XReliquary", "reliquary", "Reliquary",
            
            // Thaumic addons
            "thaumicenergistics", "ThaumicEnergistics",
            "thaumicexploration", "ThaumicExploration",
            "thaumichorizons", "ThaumicHorizons",
            "thaumictinkerer", "ThaumicTinkerer",
            
            // AsieLib
            "asielib", "AsieLib",
            
            // Placeable Items
            "placeableitems", "PlaceableItems",
            
            // Jammy Furniture
            "jammyfurniture", "JammyFurniture",
            
            // Power Converters
            "powerconverters", "PowerConverters",
            
            // BuildCraft Compat
            "buildcraftcompat", "BuildCraftCompat"
        )
        
        /**
         * Wczytuje reguły z pliku JSON
         */
        fun fromFile(file: File): CleaningRules {
            if (!file.exists()) {
                println("Plik reguł nie istnieje: ${file.absolutePath}, używam domyślnych")
                return createDefaultRules()
            }
            
            return try {
                val gson = Gson()
                val json = file.readText()
                gson.fromJson(json, CleaningRules::class.java)
            } catch (e: Exception) {
                println("Błąd wczytywania reguł: ${e.message}, używam domyślnych")
                createDefaultRules()
            }
        }
        
        /**
         * Tworzy domyślne reguły dla modpacku 1.7.10
         */
        fun createDefaultRules(): CleaningRules {
            return CleaningRules(
                removeTileEntityIds = MOD_TILE_ENTITY_PREFIXES,
                removeEntityIds = MOD_ENTITY_PREFIXES,
                replacementBlock = 0, // air
                useHeuristics = true,
                cleanTileEntities = true,
                cleanEntities = true
            )
        }
        
        /**
         * Tworzy przykładowy plik reguł
         */
        fun createDefaultRules(file: File) {
            val rules = createDefaultRules()
            
            val gson = Gson()
            file.writeText(gson.toJson(rules))
        }
    }
}
