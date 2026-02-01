package mapcleaner

import java.io.ByteArrayOutputStream
import java.io.RandomAccessFile
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.channels.FileChannel
import java.nio.channels.FileChannel.MapMode
import java.nio.file.Path
import java.nio.file.Paths
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicInteger
import java.util.zip.Deflater
import java.util.zip.Inflater
import kotlin.system.measureTimeMillis

// Bedrock block ID
const val BEDROCK_ID: Byte = 7

// Vanilla block IDs (0-175 dla 1.7.10)
val VANILLA_BLOCK_IDS = (0..175).toSet()

fun main(args: Array<String>) {
    if (args.isEmpty() || args.contains("--help")) {
        println("""
            |Map Cleaner - Czyści mapę Minecraft 1.7.10 z modów
            |Użycie: java -jar map-cleaner.jar <ścieżka_źródłowa> [opcje]
            |
            |OPCJE:
            |  --output PATH  - ścieżka docelowa (domyślnie: nadpisuje źródło)
            |  --threads N    - liczba wątków (domyślnie: liczba rdzeni)
            |  --dry-run      - tylko analiza, bez modyfikacji
            |  --region x,z   - przetwórz tylko jeden region
            |  --all-regions  - przetwórz WSZYSTKIE regiony (bez domyślnego limitu -16..16)
            |
            |PRZYKŁADY:
            |  # Analiza (tylko pokazuje statystyki)
            |  java -jar map-cleaner.jar ../../mapa_1710 --dry-run
            |
            |  # Czyszczenie z zapisem do nowej lokalizacji
            |  java -jar map-cleaner.jar ../../mapa_1710 --output ../mapa_wyczyszczona
            |
            |  # Czyszczenie w miejscu (nadpisuje oryginał!)
            |  java -jar map-cleaner.jar ../../mapa_1710
            |
            |  # Tylko region 0,0
            |  java -jar map-cleaner.jar ../../mapa_1710 --region 0,0 --output ./region_00
        """.trimMargin())
        return
    }

    val sourcePath = Paths.get(args[0])
    val outputPath = args.find { it == "--output" }?.let {
        args.getOrNull(args.indexOf(it) + 1)?.let { Paths.get(it) }
    } ?: sourcePath  // Domyślnie nadpisujemy źródło
    
    val threads = args.find { it == "--threads" }?.let { 
        args.getOrNull(args.indexOf(it) + 1)?.toIntOrNull() 
    } ?: Runtime.getRuntime().availableProcessors()
    val dryRun = args.contains("--dry-run")
    val singleRegion = args.find { it == "--region" }?.let {
        args.getOrNull(args.indexOf(it) + 1)?.split(",")?.map { it.toInt() }
    }
    val allRegions = args.contains("--all-regions")
    
    // Domyślny zakres regionów: -16 do 16 (opcjonalnie można rozciągnąć --all-regions)
    val regionRange = if (allRegions) -1000..1000 else -16..16

    println("=" * 60)
    println("MAP CLEANER - Czyszczenie mapy Minecraft 1.7.10")
    println("=" * 60)
    println("Źródło: $sourcePath")
    println("Cel: $outputPath")
    if (sourcePath == outputPath) {
        println("UWAGA: Czyszczenie w miejscu (nadpisze oryginał!)")
    }
    println("Zakres regionów: ${if (allRegions) "WSZYSTKIE" else "-16..16 (użyj --all-regions dla pełnego zakresu)"}")
    println("Wątki: $threads")
    println("Tryb: ${if (dryRun) "ANALIZA" else "CZYSZCZENIE"}")
    println()

    val sourceRegionDir = sourcePath.resolve("region")
    if (!sourceRegionDir.toFile().exists()) {
        println("BŁĄD: Nie znaleziono folderu region: $sourceRegionDir")
        return
    }
    
    // Jeśli output to inna lokalizacja - kopiujemy strukturę
    if (sourcePath != outputPath && !dryRun) {
        println("Kopiowanie struktury mapy...")
        copyWorldStructure(sourcePath, outputPath)
    }
    
    val targetRegionDir = outputPath.resolve("region")
    
    // Jeśli output != source i nie jest dry-run, musimy zapewnić źródłowe regiony
    val sourceRegionDirToUse = if (dryRun || sourcePath == outputPath) {
        sourceRegionDir  // Pracujemy na źródle
    } else {
        // Kopiujemy potrzebne regiony ze źródła do target
        println("Kopiowanie regionów...")
        targetRegionDir.toFile().mkdirs()
        
        // Najpierw znajdźmy które regiony potrzebujemy
        val neededRegions = if (singleRegion != null && singleRegion.size == 2) {
            listOf(sourceRegionDir.resolve("r.${singleRegion[0]}.${singleRegion[1]}.mca"))
        } else {
            sourceRegionDir.toFile().listFiles()
                ?.filter { it.name.endsWith(".mca") && isRegionInRange(it.name, regionRange) }
                ?.map { it.toPath() } ?: emptyList()
        }
        
        // Kopiujemy tylko te które istnieją
        for (src in neededRegions) {
            if (src.toFile().exists()) {
                val dst = targetRegionDir.resolve(src.fileName)
                src.toFile().copyTo(dst.toFile(), overwrite = true)
            }
        }
        println("Skopiowano ${neededRegions.size} regionów")
        targetRegionDir  // Teraz pracujemy na target
    }

    val regionFiles = if (singleRegion != null && singleRegion.size == 2) {
        val (rx, rz) = singleRegion
        // Sprawdź czy w dozwolonym zakresie
        if (rx !in regionRange || rz !in regionRange) {
            println("UWAGA: Region $rx,$rz poza domyślnym zakresem. Użyj --all-regions aby przetworzyć.")
        }
        val specific = sourceRegionDirToUse.resolve("r.$rx.$rz.mca")
        if (specific.toFile().exists()) listOf(specific) else emptyList()
    } else {
        sourceRegionDirToUse.toFile().listFiles()?.filter { 
            it.name.endsWith(".mca") && isRegionInRange(it.name, regionRange)
        }?.map { it.toPath() } ?: emptyList()
    }

    if (regionFiles.isEmpty()) {
        println("BŁĄD: Nie znaleziono plików regionów")
        return
    }

    println("Znaleziono ${regionFiles.size} regionów do przetworzenia")
    println()

    val totalModBlocks = AtomicInteger(0)
    val totalChunks = AtomicInteger(0)
    val processedRegions = AtomicInteger(0)

    val executor = Executors.newFixedThreadPool(threads)
    val time = measureTimeMillis {
        val futures = regionFiles.map { regionFile ->
            executor.submit {
                try {
                    val result = processRegion(regionFile, dryRun)
                    totalModBlocks.addAndGet(result.modBlocks)
                    totalChunks.addAndGet(result.chunks)
                    val processed = processedRegions.incrementAndGet()
                    if (processed % 10 == 0 || processed == regionFiles.size) {
                        println("[$processed/${regionFiles.size}] Przetworzono ${regionFile.fileName}")
                    }
                } catch (e: Exception) {
                    println("BŁĄD w ${regionFile.fileName}: ${e.message}")
                    e.printStackTrace()
                }
            }
        }
        futures.forEach { it.get() }
    }

    executor.shutdown()

    println()
    println("=" * 60)
    println("PODSUMOWANIE")
    println("=" * 60)
    println("Przetworzone regiony: ${processedRegions.get()}")
    println("Przeskanowane chunki: ${totalChunks.get()}")
    println("Znalezione bloki z modów: ${totalModBlocks.get()}")
    println("Czas wykonania: ${time / 1000}s")
    if (!dryRun) {
        println("Status: WYCZYSZCZONO")
    }
    println("=" * 60)
}

private operator fun String.times(n: Int) = repeat(n)

fun isRegionInRange(filename: String, range: IntRange): Boolean {
    // Format: r.X.Z.mca
    val regex = Regex("r\\.(-?\\d+)\\.(-?\\d+)\\.mca")
    val match = regex.matchEntire(filename) ?: return false
    val x = match.groupValues[1].toInt()
    val z = match.groupValues[2].toInt()
    return x in range && z in range
}

fun copyWorldStructure(source: Path, target: Path) {
    // Lista folderów i plików do skopiowania dla singleplayer
    val items = listOf(
        "level.dat", "level.dat_old", "session.lock", "uid.dat",
        "playerdata", "stats", "data", "forcedchunks.dat", "idcounts.dat"
    )
    
    target.toFile().mkdirs()
    
    for (item in items) {
        val src = source.resolve(item)
        val dst = target.resolve(item)
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
    
    // Tworzymy folder region jeśli nie istnieje
    target.resolve("region").toFile().mkdirs()
}

data class ProcessResult(val modBlocks: Int, val chunks: Int)

fun processRegion(regionPath: Path, dryRun: Boolean): ProcessResult {
    val mode = if (dryRun) "r" else "rw"
    val mapMode = if (dryRun) MapMode.READ_ONLY else MapMode.READ_WRITE
    
    val raf = RandomAccessFile(regionPath.toFile(), mode)
    val channel = raf.channel
    val size = channel.size()
    
    if (size < 8192) return ProcessResult(0, 0) // Pusty lub uszkodzony region
    
    // Memory-map cały plik
    val mapped = channel.map(mapMode, 0, size)
    mapped.order(ByteOrder.BIG_ENDIAN)
    
    var totalModBlocks = 0
    var totalChunks = 0
    
    // Nagłówek: 4096 bajtów (1024 wpisy po 4 bajty)
    val header = ByteArray(4096)
    mapped.position(0)
    mapped.get(header)
    
    // Timestamps: kolejne 4096 bajtów
    val timestamps = ByteArray(4096)
    mapped.get(timestamps)
    
    val modifiedChunks = mutableListOf<Pair<Int, ByteArray>>() // (index, nowe_dane)
    
    for (chunkZ in 0 until 32) {
        for (chunkX in 0 until 32) {
            val index = chunkX + chunkZ * 32
            val offset = ((header[index * 4].toInt() and 0xFF) shl 16) or
                        ((header[index * 4 + 1].toInt() and 0xFF) shl 8) or
                        (header[index * 4 + 2].toInt() and 0xFF)
            val sectorCount = header[index * 4 + 3].toInt() and 0xFF
            
            if (offset == 0 || sectorCount == 0) continue // Pusty chunk
            
            val byteOffset = offset * 4096L
            if (byteOffset + 5 > size) continue
            
            mapped.position(byteOffset.toInt())
            val length = mapped.int
            val compressionType = mapped.get()
            
            if (length < 1 || length > 10 * 1024 * 1024) continue // Za duży lub uszkodzony
            
            val compressedData = ByteArray(length - 1)
            mapped.get(compressedData)
            
            // Dekompresja
            val uncompressed = try {
                when (compressionType.toInt()) {
                    2 -> decompressZlib(compressedData)
                    1 -> decompressGzip(compressedData)
                    else -> compressedData
                }
            } catch (e: Exception) {
                continue
            }
            
            // Parsuj i modyfikuj NBT
            val (modified, modBlocks) = processChunkNBT(uncompressed, !dryRun)
            
            if (modBlocks > 0) {
                totalModBlocks += modBlocks
                totalChunks++
                
                if (!dryRun && modified != null) {
                    val recompressed = compressZlib(modified)
                    modifiedChunks.add(index to recompressed)
                }
            }
        }
    }
    
    channel.close()
    raf.close()
    
    // Zapisz zmodyfikowane chunki (poza memory mapping - pozwala na rozszerzanie pliku)
    if (!dryRun && modifiedChunks.isNotEmpty()) {
        val writeRaf = RandomAccessFile(regionPath.toFile(), "rw")
        
        // Czytaj aktualny nagłówek
        val currentHeader = ByteArray(4096)
        writeRaf.seek(0)
        writeRaf.readFully(currentHeader)
        
        var currentOffset = ((size + 4095) / 4096).toInt()
        if (currentOffset < 2) currentOffset = 2
        
        // Zapisz nowe chunki
        for ((index, newData) in modifiedChunks) {
            val newSize = newData.size + 5
            val newSectorCount = (newSize + 4095) / 4096
            
            // Aktualizuj nagłówek
            currentHeader[index * 4] = ((currentOffset shr 16) and 0xFF).toByte()
            currentHeader[index * 4 + 1] = ((currentOffset shr 8) and 0xFF).toByte()
            currentHeader[index * 4 + 2] = (currentOffset and 0xFF).toByte()
            currentHeader[index * 4 + 3] = newSectorCount.toByte()
            
            // Zapisz dane
            writeRaf.seek(currentOffset * 4096L)
            writeRaf.writeInt(newData.size + 1)
            writeRaf.writeByte(2)
            writeRaf.write(newData)
            
            // Padding
            val paddingSize = newSectorCount * 4096 - newSize
            if (paddingSize > 0) {
                writeRaf.write(ByteArray(paddingSize))
            }
            
            currentOffset += newSectorCount
        }
        
        // Zapisz nagłówek
        writeRaf.seek(0)
        writeRaf.write(currentHeader)
        
        // Utnij plik
        writeRaf.setLength(currentOffset * 4096L)
        writeRaf.close()
    }
    
    return ProcessResult(totalModBlocks, totalChunks)
}

fun decompressZlib(data: ByteArray): ByteArray {
    val inflater = Inflater()
    inflater.setInput(data)
    val output = ByteArrayOutputStream()
    val buffer = ByteArray(8192)
    while (!inflater.finished()) {
        val count = inflater.inflate(buffer)
        output.write(buffer, 0, count)
    }
    inflater.end()
    return output.toByteArray()
}

fun decompressGzip(data: ByteArray): ByteArray {
    return java.io.ByteArrayInputStream(data).use { bis ->
        java.util.zip.GZIPInputStream(bis).use { gis ->
            gis.readBytes()
        }
    }
}

fun compressZlib(data: ByteArray): ByteArray {
    val deflater = Deflater()
    deflater.setInput(data)
    deflater.finish()
    val output = ByteArrayOutputStream()
    val buffer = ByteArray(8192)
    while (!deflater.finished()) {
        val count = deflater.deflate(buffer)
        output.write(buffer, 0, count)
    }
    deflater.end()
    return output.toByteArray()
}

fun processChunkNBT(data: ByteArray, modify: Boolean): Pair<ByteArray?, Int> {
    // Prosty parser NBT - szukamy sekcji z blokami
    val buffer = ByteBuffer.wrap(data)
    buffer.order(ByteOrder.BIG_ENDIAN)
    
    var modBlocksFound = 0
    var modified = false
    val output = ByteArrayOutputStream(data.size)
    
    // Parsujemy strukturę NBT szukając "Blocks" w sekcjach
    // To uproszczona wersja - zakładamy strukturę 1.7.10
    
    try {
        val root = parseNBTCompound(buffer)
        val level = root["Level"] as? NBTCompound ?: return Pair(null, 0)
        val sections = level["Sections"] as? NBTList ?: return Pair(null, 0)
        
        for (section in sections.elements) {
            val sec = section as? NBTCompound ?: continue
            val blocks = sec["Blocks"] as? NBTByteArray ?: continue
            
            val blockArray = blocks.data
            for (i in blockArray.indices) {
                val blockId = blockArray[i].toInt() and 0xFF
                if (blockId > 175 && blockId != 0) { // Nie vanilla i nie air
                    modBlocksFound++
                    if (modify) {
                        blockArray[i] = BEDROCK_ID
                        modified = true
                    }
                }
            }
        }
        
        if (modify && modified) {
            // Serializuj zmodyfikowane NBT z powrotem
            val newData = serializeNBT(root)
            return Pair(newData, modBlocksFound)
        }
    } catch (e: Exception) {
        // Nieprawidłowa struktura NBT - pomiń
    }
    
    return Pair(null, modBlocksFound)
}

// Prosta reprezentacja NBT
sealed class NBT
data class NBTCompound(val elements: MutableMap<String, NBT> = mutableMapOf()) : NBT() {
    operator fun get(key: String) = elements[key]
    operator fun set(key: String, value: NBT) { elements[key] = value }
}
data class NBTList(val elements: List<NBT>) : NBT()
data class NBTByteArray(val data: ByteArray) : NBT()

fun parseNBTCompound(buffer: ByteBuffer): NBTCompound {
    // Uproszczony parser - zakładamy że struktura jest poprawna
    val result = NBTCompound()
    
    // Root tag
    val rootType = buffer.get()
    if (rootType.toInt() != 10) throw IllegalStateException("Expected compound")
    
    // Root name (pomijamy)
    val nameLen = buffer.short
    val nameBytes = ByteArray(nameLen.toInt())
    buffer.get(nameBytes)
    
    parseCompoundContent(buffer, result)
    return result
}

fun parseCompoundContent(buffer: ByteBuffer, compound: NBTCompound) {
    while (true) {
        val type = buffer.get().toInt() and 0xFF
        if (type == 0) break // TAG_End
        
        val nameLen = buffer.short.toInt() and 0xFFFF
        val nameBytes = ByteArray(nameLen)
        buffer.get(nameBytes)
        val name = String(nameBytes, Charsets.UTF_8)
        
        val value = when (type) {
            1 -> NBTByteArray(byteArrayOf(buffer.get())) // Byte
            2 -> { buffer.short; NBTByteArray(byteArrayOf()) } // Short - pomijamy
            3 -> { buffer.int; NBTByteArray(byteArrayOf()) } // Int - pomijamy
            4 -> { buffer.long; NBTByteArray(byteArrayOf()) } // Long - pomijamy
            5 -> { buffer.float; NBTByteArray(byteArrayOf()) } // Float - pomijamy
            6 -> { buffer.double; NBTByteArray(byteArrayOf()) } // Double - pomijamy
            7 -> { // Byte Array - to nas interesuje dla Blocks
                val len = buffer.int
                val data = ByteArray(len)
                buffer.get(data)
                NBTByteArray(data)
            }
            8 -> { // String
                val strLen = buffer.short.toInt() and 0xFFFF
                val strBytes = ByteArray(strLen)
                buffer.get(strBytes)
                NBTByteArray(strBytes) // Używamy jako placeholder
            }
            9 -> parseNBTList(buffer) // List
            10 -> { // Compound
                val nested = NBTCompound()
                parseCompoundContent(buffer, nested)
                nested
            }
            11 -> { // Int Array
                val len = buffer.int
                repeat(len) { buffer.int }
                NBTByteArray(byteArrayOf())
            }
            else -> throw IllegalStateException("Unknown type: $type")
        }
        
        compound[name] = value
    }
}

fun parseNBTList(buffer: ByteBuffer): NBTList {
    val type = buffer.get().toInt() and 0xFF
    val len = buffer.int
    val elements = mutableListOf<NBT>()
    
    repeat(len) {
        val element = when (type) {
            10 -> {
                val compound = NBTCompound()
                parseCompoundContent(buffer, compound)
                compound
            }
            else -> {
                // Pomijamy inne typy w liście
                NBTByteArray(byteArrayOf())
            }
        }
        elements.add(element)
    }
    
    return NBTList(elements)
}

fun serializeNBT(compound: NBTCompound): ByteArray {
    val output = ByteArrayOutputStream()
    val dos = java.io.DataOutputStream(output)
    
    // Root tag
    dos.writeByte(10) // TAG_Compound
    dos.writeShort(0) // Empty name
    
    serializeCompound(dos, compound)
    dos.writeByte(0) // TAG_End
    
    return output.toByteArray()
}

fun serializeCompound(dos: java.io.DataOutputStream, compound: NBTCompound) {
    for ((key, value) in compound.elements) {
        when (value) {
            is NBTCompound -> {
                dos.writeByte(10)
                dos.writeShort(key.length)
                dos.writeBytes(key)
                serializeCompound(dos, value)
                dos.writeByte(0)
            }
            is NBTList -> {
                dos.writeByte(9)
                dos.writeShort(key.length)
                dos.writeBytes(key)
                dos.writeByte(10) // TAG_Compound
                dos.writeInt(value.elements.size)
                for (elem in value.elements) {
                    if (elem is NBTCompound) {
                        serializeCompound(dos, elem)
                        dos.writeByte(0)
                    }
                }
            }
            is NBTByteArray -> {
                if (key == "Blocks" || key == "Data" || key == "SkyLight" || key == "BlockLight") {
                    dos.writeByte(7)
                    dos.writeShort(key.length)
                    dos.writeBytes(key)
                    dos.writeInt(value.data.size)
                    dos.write(value.data)
                }
            }
        }
    }
}
