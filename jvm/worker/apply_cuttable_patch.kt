/**
 * Skrypt wstawiający bloki ukośne (CuttableBlocks) do mapy Minecraft 1.7.10
 * 
 * Użycie: kotlin apply_cuttable_patch.kt <world_path> <patch_json_path>
 */

import org.jglrxavpok.hephaistos.mca.*
import org.jglrxavpok.hephaistos.nbt.*
import java.io.RandomAccessFile
import java.nio.file.Paths
import java.io.File

// Block ID dla CuttableBlock (tymczasowe - mod przypisze właściwe)
val CUTTABLE_BLOCK_ID = 200  // Tymczasowy ID poza zakresem vanilla

/**
 * Wstawia blok ukośny do sekcji chunka
 */
fun insertCuttableBlock(
    chunk: NBTCompound,
    blockX: Int, 
    blockY: Int, 
    blockZ: Int,
    originalBlockId: Int,
    originalMeta: Int,
    normalX: Float,
    normalY: Float,
    normalZ: Float,
    keepPositive: Boolean
) {
    val level = chunk.getCompound("Level") ?: return
    
    // Pobierz lub utwórz sekcje
    val sections = level.getList<NBTCompound>("Sections") 
        ?: mutableListOf<NBTCompound>().also {
            level.set("Sections", NBTList<NBTCompound>(NBTTypes.TAG_Compound, it))
        }
    
    // Znajdź lub utwórz sekcję dla danego Y
    val sectionY = blockY shr 4
    var section = sections.find { it.getByte("Y")?.toInt() == sectionY }
    
    if (section == null) {
        // Utwórz nową sekcję
        section = NBTCompound()
            .setByte("Y", sectionY.toByte())
            .setByteArray("Blocks", ByteArray(4096) { 0 })
            .setByteArray("Data", ByteArray(2048) { 0 })
            .setByteArray("SkyLight", ByteArray(2048) { 0xFF.toByte() })
            .setByteArray("BlockLight", ByteArray(2048) { 0 })
        sections.add(section)
    }
    
    // Oblicz pozycję w sekcji
    val localX = blockX and 15
    val localY = blockY and 15
    val localZ = blockZ and 15
    val blockIndex = localY * 256 + localZ * 16 + localX
    val dataIndex = blockIndex shr 1
    val dataShift = (blockIndex and 1) * 4
    
    // Wstaw blok
    val blocks = section.getByteArray("Blocks")?.copyArray() ?: ByteArray(4096)
    val data = section.getByteArray("Data")?.copyArray() ?: ByteArray(2048)
    
    blocks[blockIndex] = CUTTABLE_BLOCK_ID.toByte()
    data[dataIndex] = ((data[dataIndex].toInt() and (0xF0 shr dataShift)) or 
                      (originalMeta shl dataShift)).toByte()
    
    section.setByteArray("Blocks", blocks)
    section.setByteArray("Data", data)
    
    // Dodaj TileEntity dla bloku ukośnego
    val tileEntities = level.getList<NBTCompound>("TileEntities") 
        ?: mutableListOf<NBTCompound>().also {
            level.set("TileEntities", NBTList<NBTCompound>(NBTTypes.TAG_Compound, it))
        }
    
    // Usuń istniejące TE na tej pozycji
    tileEntities.removeIf { te ->
        te.getInt("x") == blockX && 
        te.getInt("y") == blockY && 
        te.getInt("z") == blockZ
    }
    
    // Utwórz nowe TileEntity
    val tileEntity = NBTCompound()
        .setString("id", "CuttableTE")
        .setInt("x", blockX)
        .setInt("y", blockY)
        .setInt("z", blockZ)
        .setInt("OriginalBlockID", originalBlockId)
        .setInt("OriginalMeta", originalMeta)
        .setFloat("NormalX", normalX)
        .setFloat("NormalY", normalY)
        .setFloat("NormalZ", normalZ)
        .setByte("KeepPositive", if (keepPositive) 1 else 0)
    
    tileEntities.add(tileEntity)
    
    println("    Wstawiono blok ukośny at ($blockX, $blockY, $blockZ)")
}

/**
 * Mapuje nazwę bloku na ID (podstawowa mapa dla vanilla)
 */
fun getBlockId(blockName: String): Int {
    return when (blockName) {
        "minecraft:stone" -> 1
        "minecraft:grass" -> 2
        "minecraft:dirt" -> 3
        "minecraft:cobblestone" -> 4
        "minecraft:planks" -> 5
        "minecraft:bedrock" -> 7
        "minecraft:sand" -> 12
        "minecraft:gravel" -> 14
        "minecraft:gold_ore" -> 14
        "minecraft:iron_ore" -> 15
        "minecraft:coal_ore" -> 16
        "minecraft:log" -> 17
        "minecraft:leaves" -> 18
        "minecraft:glass" -> 20
        "minecraft:lapis_ore" -> 21
        "minecraft:lapis_block" -> 22
        "minecraft:sandstone" -> 24
        "minecraft:wool" -> 35
        "minecraft:gold_block" -> 41
        "minecraft:iron_block" -> 42
        "minecraft:brick_block" -> 45
        "minecraft:bookshelf" -> 47
        "minecraft:mossy_cobblestone" -> 48
        "minecraft:obsidian" -> 49
        "minecraft:diamond_ore" -> 56
        "minecraft:diamond_block" -> 57
        "minecraft:crafting_table" -> 58
        "minecraft:redstone_ore" -> 73
        "minecraft:emerald_ore" -> 129
        "minecraft:emerald_block" -> 133
        "minecraft:stonebrick" -> 98
        else -> 1  // Default to stone
    }
}

/**
 * Przetwarza pojedynczy chunk
 */
fun processChunk(worldPath: String, chunkX: Int, chunkZ: Int, blocks: List<Map<String, Any>>) {
    val regionX = chunkX shr 5
    val regionZ = chunkZ shr 5
    val localChunkX = chunkX and 31
    val localChunkZ = chunkZ and 31
    
    println("Processing chunk ($chunkX, $chunkZ) -> Region ($regionX, $regionZ), local ($localChunkX, $localChunkZ)")
    
    val regionFile = Paths.get(worldPath, "region", "r.$regionX.$regionZ.mca")
    if (!regionFile.toFile().exists()) {
        println("  Region nie istnieje: $regionFile")
        return
    }
    
    val raf = RandomAccessFile(regionFile.toFile(), "rw")
    RegionFile(raf, regionX, regionZ, 0, 255).use { region ->
        val chunkData = region.getChunkData(localChunkX, localChunkZ)
        if (chunkData == null) {
            println("  Chunk nie istnieje w regionie")
            return
        }
        
        // Wstaw bloki
        for (block in blocks) {
            val x = (block["x"] as Number).toInt()
            val y = (block["y"] as Number).toInt()
            val z = (block["z"] as Number).toInt()
            val originalBlock = block["original_block"] as String
            val originalMeta = (block["original_meta"] as Number).toInt()
            val normal = block["normal"] as List<*>
            val keepPositive = block["keep_positive"] as Boolean
            
            val blockId = getBlockId(originalBlock)
            
            insertCuttableBlock(
                chunkData,
                x, y, z,
                blockId, originalMeta,
                (normal[0] as Number).toFloat(),
                (normal[1] as Number).toFloat(),
                (normal[2] as Number).toFloat(),
                keepPositive
            )
        }
        
        // Zapisz zmieniony chunk
        region.writeChunkData(localChunkX, localChunkZ, chunkData)
        println("  Zapisano chunk ($chunkX, $chunkZ)")
    }
}

/**
 * Główna funkcja
 */
fun main(args: Array<String>) {
    if (args.size < 2) {
        println("Użycie: kotlin apply_cuttable_patch.kt <world_path> <patch_json_path>")
        println("Przykład: kotlin apply_cuttable_patch.kt \"../../headless_server/1.7.10/world_cuttable_test\" \"../../new_mod_trial/cuttable_test_patch_jvm.json\"")
        return
    }
    
    val worldPath = args[0]
    val patchPath = args[1]
    
    println("=== APLIKOWANIE PATCHA CUTTABLE BLOCKS ===")
    println("Świat: $worldPath")
    println("Patch: $patchPath")
    
    // Wczytaj patch JSON
    val patchFile = File(patchPath)
    if (!patchFile.exists()) {
        println("BŁĄD: Plik patcha nie istnieje: $patchPath")
        return
    }
    
    val patchContent = patchFile.readText()
    val patch = parseJson(patchContent) as Map<String, Any>
    
    println("\nMetadane:")
    val metadata = patch["metadata"] as Map<String, String>
    metadata.forEach { (k, v) -> println("  $k: $v") }
    
    // Przetwórz chunki
    val chunks = patch["chunks"] as Map<String, Map<String, Any>>
    println("\nPrzetwarzanie ${chunks.size} chunków...")
    
    for ((chunkKey, chunkData) in chunks) {
        val cx = (chunkData["x"] as Number).toInt()
        val cz = (chunkData["z"] as Number).toInt()
        val blocks = chunkData["blocks"] as List<Map<String, Any>>
        
        processChunk(worldPath, cx, cz, blocks)
    }
    
    println("\n=== ZAKOŃCZONO ===")
    println("Bloki ukośne zostały wstawione do mapy.")
    println("Uruchom serwer z modem CuttableBlocks aby zobaczyć efekt.")
}

/**
 * Prosty parser JSON (bo nie mamy dostępne biblioteki JSON w Kotlin)
 */
fun parseJson(json: String): Any {
    // Używamy prostej implementacji - w rzeczywistości Hephaistos ma NBT reader
    // Tutaj zakładamy że struktura jest prosta
    
    // Dla uproszczenia, parsujemy ręcznie
    val trimmed = json.trim()
    
    return when {
        trimmed.startsWith("{") -> parseObject(trimmed)
        trimmed.startsWith("[") -> parseArray(trimmed)
        trimmed.startsWith("\"") -> trimmed.trim('"')
        trimmed == "true" -> true
        trimmed == "false" -> false
        trimmed.contains(".") -> trimmed.toDouble()
        else -> trimmed.toInt()
    }
}

fun parseObject(json: String): Map<String, Any> {
    val result = mutableMapOf<String, Any>()
    val content = json.substring(1, json.length - 1).trim()
    
    var i = 0
    while (i < content.length) {
        // Znajdź klucz
        val keyStart = content.indexOf('"', i)
        if (keyStart == -1) break
        val keyEnd = content.indexOf('"', keyStart + 1)
        val key = content.substring(keyStart + 1, keyEnd)
        
        // Znajdź wartość
        val colonIndex = content.indexOf(':', keyEnd)
        val valueStart = colonIndex + 1
        
        // Znajdź koniec wartości
        val (value, nextIndex) = parseValue(content, valueStart)
        result[key] = value
        
        i = nextIndex
    }
    
    return result
}

fun parseArray(json: String): List<Any> {
    val result = mutableListOf<Any>()
    val content = json.substring(1, json.length - 1).trim()
    
    if (content.isEmpty()) return result
    
    var i = 0
    while (i < content.length) {
        val (value, nextIndex) = parseValue(content, i)
        result.add(value)
        
        // Pomiń przecinek
        i = nextIndex
        while (i < content.length && (content[i] == ',' || content[i].isWhitespace())) {
            i++
        }
    }
    
    return result
}

fun parseValue(content: String, start: Int): Pair<Any, Int> {
    var i = start
    while (i < content.length && content[i].isWhitespace()) i++
    
    return when {
        content[i] == '"' -> {
            val end = content.indexOf('"', i + 1)
            Pair(content.substring(i + 1, end), end + 1)
        }
        content[i] == '{' -> {
            val end = findMatchingBrace(content, i, '{', '}')
            Pair(parseObject(content.substring(i, end + 1)), end + 1)
        }
        content[i] == '[' -> {
            val end = findMatchingBrace(content, i, '[', ']')
            Pair(parseArray(content.substring(i, end + 1)), end + 1)
        }
        else -> {
            // Liczba lub boolean
            val end = findValueEnd(content, i)
            val value = content.substring(i, end).trim()
            val parsed = when {
                value == "true" -> true
                value == "false" -> false
                value.contains(".") -> value.toDouble()
                else -> value.toInt()
            }
            Pair(parsed, end)
        }
    }
}

fun findMatchingBrace(content: String, start: Int, open: Char, close: Char): Int {
    var count = 1
    var i = start + 1
    while (i < content.length && count > 0) {
        when (content[i]) {
            open -> count++
            close -> count--
            '"' -> i = content.indexOf('"', i + 1)  // Pomiń string
        }
        i++
    }
    return i - 1
}

fun findValueEnd(content: String, start: Int): Int {
    var i = start
    while (i < content.length && content[i] != ',' && content[i] != '}' && content[i] != ']') {
        i++
    }
    return i
}

main(args)
