package mc.editkit.worker

import org.jglrxavpok.hephaistos.mca.BlockState
import org.jglrxavpok.hephaistos.mca.RegionFile
import org.jglrxavpok.hephaistos.nbt.CompressedProcesser
import org.jglrxavpok.hephaistos.nbt.NBT
import org.jglrxavpok.hephaistos.nbt.NBTCompound
import org.jglrxavpok.hephaistos.nbt.NBTList
import org.jglrxavpok.hephaistos.nbt.NBTType
import org.jglrxavpok.hephaistos.nbt.NBTWriter
import org.json.JSONArray
import org.json.JSONObject
import java.io.RandomAccessFile
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.file.Path
import java.util.zip.Deflater

/**
 * Minimalny edytor docelowego świata 1.18.2 dla Event JSON.
 *
 * Ten edytor używa palet BlockState przez Hephaistos i zapisuje bezpośrednio
 * do plików region MCA. Obsługiwany zakres jest celowo mały: set_block,
 * set_block_entity oraz remove_block. To wystarcza dla aktualnego fallbacku
 * AE2/Mekanism/placeholder.
 */
class WorldEditor1182(private val worldPath: Path) {
    private val regionPath = worldPath.resolve("region")
    private val openRegions = mutableMapOf<Pair<Int, Int>, OpenRegion>()
    private val modifiedChunks = mutableSetOf<Pair<Int, Int>>()

    private data class OpenRegion(
        val raf: RandomAccessFile,
        val region: RegionFile,
    )

    init {
        regionPath.toFile().mkdirs()
    }

    fun setBlock(x: Int, y: Int, z: Int, blockId: String, properties: Map<String, String> = emptyMap()) {
        val region = regionForBlock(x, z)
        region.region.setBlockState(x, y, z, BlockState(blockId, properties))
        modifiedChunks.add(chunkCoordFromBlock(x) to chunkCoordFromBlock(z))
    }

    fun setBlockEntity(
        x: Int,
        y: Int,
        z: Int,
        blockId: String,
        properties: Map<String, String> = emptyMap(),
        nbtData: JSONObject,
    ) {
        setBlock(x, y, z, blockId, properties)

        val region = regionForBlock(x, z)
        val chunkX = chunkCoordFromBlock(x)
        val chunkZ = chunkCoordFromBlock(z)
        val chunk = region.region.getOrCreateChunk(chunkX, chunkZ)

        val existing = mutableListOf<NBTCompound>()
        for (tag in chunk.tileEntities) {
            val tex = tag.getInt("x") ?: Int.MIN_VALUE
            val tey = tag.getInt("y") ?: Int.MIN_VALUE
            val tez = tag.getInt("z") ?: Int.MIN_VALUE
            if (tex != x || tey != y || tez != z) {
                existing.add(tag)
            }
        }

        val newTag = jsonObjectToNbt(nbtData, x, y, z)
        existing.add(newTag)
        chunk.tileEntities = NBT.List(NBTType.TAG_Compound, existing)
        modifiedChunks.add(chunkX to chunkZ)
    }

    fun removeBlock(x: Int, y: Int, z: Int) {
        setBlock(x, y, z, "minecraft:air")
        val region = regionForBlock(x, z)
        val chunk = region.region.getOrCreateChunk(chunkCoordFromBlock(x), chunkCoordFromBlock(z))
        val filtered = mutableListOf<NBTCompound>()
        for (i in 0 until chunk.tileEntities.size) {
            val tag = chunk.tileEntities[i]
            if (tag.getInt("x") != x || tag.getInt("y") != y || tag.getInt("z") != z) {
                filtered.add(tag)
            }
        }
        chunk.tileEntities = NBT.List(NBTType.TAG_Compound, filtered)
    }

    fun commit() {
        val chunksByRegion = modifiedChunks.groupBy { (chunkX, chunkZ) ->
            regionCoordFromChunk(chunkX) to regionCoordFromChunk(chunkZ)
        }

        for ((regionKey, chunks) in chunksByRegion) {
            val open = openRegions[regionKey] ?: continue
            for ((chunkX, chunkZ) in chunks) {
                val chunk = open.region.getChunk(chunkX, chunkZ) ?: continue
                writeChunkDirect(open.raf, localChunkFromChunk(chunkX), localChunkFromChunk(chunkZ), chunk.toNBT())
            }
            println("Zapisano region 1.18.2 r.${regionKey.first}.${regionKey.second} (${chunks.size} chunkow)")
        }

        for (open in openRegions.values) {
            open.region.close()
            open.raf.close()
        }
        openRegions.clear()
        modifiedChunks.clear()
    }

    private fun regionForBlock(x: Int, z: Int): OpenRegion {
        val chunkX = chunkCoordFromBlock(x)
        val chunkZ = chunkCoordFromBlock(z)
        val regionX = regionCoordFromChunk(chunkX)
        val regionZ = regionCoordFromChunk(chunkZ)
        val key = regionX to regionZ
        return openRegions.getOrPut(key) {
            val regionFile = regionPath.resolve("r.$regionX.$regionZ.mca")
            regionFile.parent.toFile().mkdirs()
            val raf = RandomAccessFile(regionFile.toFile().apply {
                if (!exists()) {
                    createNewFile()
                }
            }, "rw")
            OpenRegion(raf, RegionFile(raf, regionX, regionZ, -64, 319))
        }
    }

    private fun jsonObjectToNbt(obj: JSONObject, x: Int, y: Int, z: Int): NBTCompound {
        return NBT.Compound { compound ->
            for (key in obj.keys()) {
                val tag = jsonToNbt(obj.get(key))
                if (tag != null) {
                    compound[key] = tag
                }
            }
            compound["x"] = NBT.Int(x)
            compound["y"] = NBT.Int(y)
            compound["z"] = NBT.Int(z)
            compound["keepPacked"] = NBT.Byte(0)
        }
    }

    @Suppress("UNCHECKED_CAST")
    private fun jsonToNbt(value: Any?): NBT? {
        if (value == null || value == JSONObject.NULL) {
            return null
        }
        return when (value) {
            is JSONObject -> {
                NBT.Compound { compound ->
                    for (key in value.keys()) {
                        val tag = jsonToNbt(value.get(key))
                        if (tag != null) {
                            compound[key] = tag
                        }
                    }
                }
            }
            is JSONArray -> jsonArrayToNbt(value)
            is Boolean -> NBT.Byte(if (value) 1 else 0)
            is String -> NBT.String(value)
            is Byte -> NBT.Byte(value)
            is Short -> NBT.Short(value)
            is Int -> NBT.Int(value)
            is Long -> NBT.Long(value)
            is Float -> NBT.Float(value)
            is Double -> NBT.Double(value)
            is Number -> {
                val asLong = value.toLong()
                if (asLong in Int.MIN_VALUE..Int.MAX_VALUE) NBT.Int(asLong.toInt()) else NBT.Long(asLong)
            }
            else -> NBT.String(value.toString())
        }
    }

    private fun jsonArrayToNbt(array: JSONArray): NBT {
        if (array.length() == 0) {
            return NBT.List(NBTType.TAG_Compound)
        }

        val tags = mutableListOf<NBT>()
        for (i in 0 until array.length()) {
            jsonToNbt(array.get(i))?.let { tags.add(it) }
        }
        if (tags.isEmpty()) {
            return NBT.List(NBTType.TAG_Compound)
        }

        val firstType = tags.first().ID
        return if (tags.all { it.ID == firstType }) {
            NBTList(firstType as NBTType<NBT>, tags)
        } else {
            NBT.List(NBTType.TAG_String, tags.map { NBT.String(it.toSNBT()) })
        }
    }

    private fun writeChunkDirect(raf: RandomAccessFile, localChunkX: Int, localChunkZ: Int, nbt: NBTCompound) {
        val baos = java.io.ByteArrayOutputStream()
        NBTWriter(baos, CompressedProcesser.NONE).use { it.writeNamed("", nbt) }
        val compressed = compressZlib(baos.toByteArray())

        val length = compressed.size + 1
        val chunkData = ByteArray(4 + length)
        ByteBuffer.wrap(chunkData).order(ByteOrder.BIG_ENDIAN).putInt(length)
        chunkData[4] = 2.toByte()
        System.arraycopy(compressed, 0, chunkData, 5, compressed.size)

        val sectorCount = (chunkData.size + 4095) / 4096
        val paddedChunkData = chunkData.copyOf(sectorCount * 4096)
        val index = localChunkX + localChunkZ * 32

        raf.seek((index * 4).toLong())
        val offsetBytes = ByteArray(4)
        val hasExisting = raf.read(offsetBytes) == 4
        var sectorOffset = if (hasExisting) {
            ((offsetBytes[0].toInt() and 0xFF) shl 16) or
                ((offsetBytes[1].toInt() and 0xFF) shl 8) or
                (offsetBytes[2].toInt() and 0xFF)
        } else {
            0
        }
        val oldSectorCount = if (hasExisting) offsetBytes[3].toInt() and 0xFF else 0

        if (sectorOffset == 0 || sectorCount > oldSectorCount) {
            sectorOffset = (raf.length() / 4096).toInt()
            if (raf.length() % 4096 != 0L) {
                sectorOffset++
            }
        }

        raf.seek((sectorOffset * 4096).toLong())
        raf.write(paddedChunkData)

        raf.seek((index * 4).toLong())
        raf.write(byteArrayOf(
            ((sectorOffset shr 16) and 0xFF).toByte(),
            ((sectorOffset shr 8) and 0xFF).toByte(),
            (sectorOffset and 0xFF).toByte(),
            sectorCount.toByte(),
        ))

        raf.seek((4096 + index * 4).toLong())
        raf.writeInt((System.currentTimeMillis() / 1000).toInt())
    }

    private fun compressZlib(data: ByteArray): ByteArray {
        val deflater = Deflater()
        deflater.setInput(data)
        deflater.finish()

        val output = java.io.ByteArrayOutputStream()
        val buffer = ByteArray(8192)
        while (!deflater.finished()) {
            val count = deflater.deflate(buffer)
            output.write(buffer, 0, count)
        }
        deflater.end()
        return output.toByteArray()
    }
}

fun applyEvents1182(eventFile: Path, targetWorld: Path, dryRun: Boolean = false): JSONObject {
    val root = JSONObject(eventFile.toFile().readText())
    val events = when {
        root.has("events") -> root.getJSONArray("events")
        root.has("edits") -> root.getJSONArray("edits")
        else -> JSONArray()
    }
    val editor = WorldEditor1182(targetWorld)
    var applied = 0
    var skipped = 0
    val failures = JSONArray()

    for (i in 0 until events.length()) {
        val event = events.getJSONObject(i)
        try {
            val op = event.getString("op")
            val pos = event.getJSONArray("pos")
            val x = pos.getInt(0)
            val y = pos.getInt(1)
            val z = pos.getInt(2)
            when (op) {
                "set_block" -> {
                    if (!dryRun) {
                        editor.setBlock(x, y, z, event.getString("block"), jsonProperties(event.optJSONObject("blockstate")))
                    }
                    applied++
                }
                "set_block_entity" -> {
                    if (!dryRun) {
                        editor.setBlockEntity(
                            x,
                            y,
                            z,
                            event.getString("block"),
                            jsonProperties(event.optJSONObject("blockstate")),
                            event.getJSONObject("nbt"),
                        )
                    }
                    applied++
                }
                "remove_block" -> {
                    if (!dryRun) {
                        editor.removeBlock(x, y, z)
                    }
                    applied++
                }
                else -> {
                    skipped++
                }
            }
        } catch (e: Exception) {
            failures.put(JSONObject().put("index", i).put("error", e.message ?: e.toString()).put("event", event))
        }
    }

    if (!dryRun) {
        editor.commit()
    }

    return JSONObject()
        .put("event_file", eventFile.toString())
        .put("target_world", targetWorld.toString())
        .put("dry_run", dryRun)
        .put("total_events", events.length())
        .put("applied", applied)
        .put("skipped", skipped)
        .put("failed", failures.length())
        .put("failures", failures)
}

fun applyEvents1182Jsonl(eventFile: Path, targetWorld: Path, dryRun: Boolean = false): JSONObject {
    val editor = WorldEditor1182(targetWorld)
    var total = 0
    var applied = 0
    var skipped = 0
    val failures = JSONArray()

    eventFile.toFile().forEachLine { rawLine ->
        val line = rawLine.trim()
        if (line.isEmpty()) {
            return@forEachLine
        }
        val index = total
        total++
        val event = try {
            JSONObject(line)
        } catch (e: Exception) {
            failures.put(JSONObject().put("index", index).put("error", e.message ?: e.toString()).put("line", line.take(500)))
            return@forEachLine
        }

        try {
            val op = event.getString("op")
            val pos = event.getJSONArray("pos")
            val x = pos.getInt(0)
            val y = pos.getInt(1)
            val z = pos.getInt(2)
            when (op) {
                "set_block" -> {
                    if (!dryRun) {
                        editor.setBlock(x, y, z, event.getString("block"), jsonProperties(event.optJSONObject("blockstate")))
                    }
                    applied++
                }
                "set_block_entity" -> {
                    if (!dryRun) {
                        editor.setBlockEntity(
                            x,
                            y,
                            z,
                            event.getString("block"),
                            jsonProperties(event.optJSONObject("blockstate")),
                            event.getJSONObject("nbt"),
                        )
                    }
                    applied++
                }
                "remove_block" -> {
                    if (!dryRun) {
                        editor.removeBlock(x, y, z)
                    }
                    applied++
                }
                else -> {
                    skipped++
                }
            }
        } catch (e: Exception) {
            failures.put(JSONObject().put("index", index).put("error", e.message ?: e.toString()).put("event", event))
        }
    }

    if (!dryRun) {
        editor.commit()
    }

    return JSONObject()
        .put("event_file", eventFile.toString())
        .put("target_world", targetWorld.toString())
        .put("dry_run", dryRun)
        .put("format", "jsonl")
        .put("total_events", total)
        .put("applied", applied)
        .put("skipped", skipped)
        .put("failed", failures.length())
        .put("failures", failures)
}

private fun jsonProperties(obj: JSONObject?): Map<String, String> {
    if (obj == null) {
        return emptyMap()
    }
    val result = linkedMapOf<String, String>()
    for (key in obj.keys()) {
        result[key] = obj.get(key).toString()
    }
    return result
}
