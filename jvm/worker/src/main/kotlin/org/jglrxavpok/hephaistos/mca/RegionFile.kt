package org.jglrxavpok.hephaistos.mca

import org.jglrxavpok.hephaistos.data.DataSource
import org.jglrxavpok.hephaistos.data.RandomAccessFileSource
import org.jglrxavpok.hephaistos.nbt.CompressedProcesser
import org.jglrxavpok.hephaistos.nbt.NBTCompound
import org.jglrxavpok.hephaistos.nbt.NBTReader
import org.jglrxavpok.hephaistos.nbt.NBTWriter
import java.io.ByteArrayOutputStream
import java.io.Closeable
import java.io.IOException
import java.io.RandomAccessFile
import java.util.concurrent.ConcurrentHashMap
import kotlin.math.ceil

/**
 * Region file (.mca) reader/writer.
 *
 * Identical to Hephaistos 2.2.0 except that the Y-coordinate bounds in
 * setBlockState / getBlockState / setBiome / getBiome now use minY..maxY
 * instead of the hardcoded 0..255. This allows passing -64 to 319 for 1.18.2.
 */
class RegionFile @Throws(AnvilException::class, IOException::class) @JvmOverloads constructor(
    val dataSource: DataSource,
    val regionX: Int,
    val regionZ: Int,
    val minY: Int = 0,
    val maxY: Int = 255,
) : Closeable {

    companion object {
        private const val GZipCompression: Byte = 1
        private const val ZlibCompression: Byte = 2
        private const val NoCompression: Byte = 3
        private const val MaxEntryCount = 1024
        private const val SectorSize = 4096
        private const val Sector1MB = 1024 * 1024 / SectorSize
        private const val HeaderLength = MaxEntryCount * 2 * 4

        fun createFileName(regionX: Int, regionZ: Int) = "r.$regionX.$regionZ.mca"
    }

    private val locations = IntArray(MaxEntryCount)
    private val timestamps = IntArray(MaxEntryCount)
    private val freeSectors: MutableList<Boolean>
    private val columnCache = ConcurrentHashMap<Int, ChunkColumn>()

    val logicalHeight = maxY - minY + 1

    @Throws(AnvilException::class, IOException::class)
    @JvmOverloads
    constructor(file: RandomAccessFile, regionX: Int, regionZ: Int, minY: Int = 0, maxY: Int = 255) :
            this(RandomAccessFileSource(file), regionX, regionZ, minY, maxY)

    init {
        if (minY > maxY) throw AnvilException("minY must be <= maxY")

        dataSource.seek(0L)
        if (dataSource.length() < HeaderLength) {
            repeat(HeaderLength) { dataSource.writeByte(0) }
        }

        addPadding()

        val availableSectors = dataSource.length() / SectorSize
        freeSectors = MutableList(availableSectors.toInt()) { true }.also {
            it[0] = false; it[1] = false
        }

        dataSource.seek(0)
        for (i in 0 until MaxEntryCount) {
            val location = dataSource.readInt()
            locations[i] = location
            if (location != 0 && sectorOffset(location) + sizeInSectors(location) <= freeSectors.size) {
                for (si in 0 until sizeInSectors(location)) freeSectors[si + sectorOffset(location)] = false
            }
        }
        for (i in 0 until MaxEntryCount) timestamps[i] = dataSource.readInt()
    }

    @Throws(AnvilException::class, IOException::class)
    fun getChunk(x: Int, z: Int): ChunkColumn? {
        if (out(x, z)) throw AnvilException("Out of RegionFile: $x,$z (chunk)")
        if (!hasLoadedChunk(x, z)) return null
        return columnCache.computeIfAbsent(index(x.chunkInsideRegion(), z.chunkInsideRegion())) {
            readColumn(x.chunkInsideRegion(), z.chunkInsideRegion())
        }
    }

    @Throws(AnvilException::class, IOException::class)
    fun getChunkData(x: Int, z: Int): NBTCompound? {
        if (out(x, z)) throw AnvilException("Out of RegionFile: $x,$z (chunk)")
        if (!hasLoadedChunk(x, z)) return null
        return readColumnData(x.chunkInsideRegion(), z.chunkInsideRegion())
    }

    @Throws(AnvilException::class, IOException::class)
    fun getOrCreateChunk(x: Int, z: Int): ChunkColumn {
        if (out(x, z)) throw AnvilException("Out of RegionFile: $x,$z (chunk)")
        if (hasChunk(x, z)) return getChunk(x, z)!!
        val idx = index(x.chunkInsideRegion(), z.chunkInsideRegion())
        columnCache[idx]?.let { return it }
        val column = ChunkColumn(x, z, minY, maxY)
        columnCache[idx] = column
        return column
    }

    @Throws(AnvilException::class, IOException::class)
    private fun readColumnData(x: Int, z: Int): NBTCompound {
        val offset = fileOffset(x, z)
        val length = readInt(offset.toLong())
        val compressionType = readByte(offset + 4L)
        val rawData = ByteArray(length - 1)
        readBytes(offset + 5L, rawData)
        val reader = NBTReader(
            rawData, when (compressionType) {
                GZipCompression -> CompressedProcesser.GZIP
                ZlibCompression -> CompressedProcesser.ZLIB
                NoCompression -> CompressedProcesser.NONE
                else -> throw AnvilException("Invalid compression type: $compressionType")
            }
        )
        val chunkData = reader.read()
        reader.close()
        if (chunkData !is NBTCompound) throw AnvilException("Chunk root tag must be TAG_Compound")
        return chunkData
    }

    @Throws(AnvilException::class, IOException::class)
    private fun readColumn(x: Int, z: Int): ChunkColumn =
        ChunkColumn(readColumnData(x, z), minY, maxY)

    @Throws(IOException::class)
    fun writeColumn(column: ChunkColumn) {
        if (column.minY < minY) throw AnvilException("ChunkColumn minY must be >= to RegionFile minY")
        if (column.maxY > maxY) throw AnvilException("ChunkColumn maxY must be <= to RegionFile maxY")
        val x = column.x
        val z = column.z
        if (out(x, z)) throw AnvilException("Out of RegionFile: $x,$z (chunk)")

        val nbt = column.toNBT()
        val dataOut = ByteArrayOutputStream()
        NBTWriter(dataOut, CompressedProcesser.ZLIB).use { it.writeNamed("", nbt) }
        val dataSize = dataOut.size()
        val sectorCount = ceil(dataSize.toDouble() / SectorSize).toInt()
        if (sectorCount >= Sector1MB) throw AnvilException("ChunkColumn over 1MB; cannot save in RegionFile.")

        val location = index(column.x, column.z)
        val previousSectorCount = sizeInSectors(locations[index(x, z)])
        val previousSectorStart = sectorOffset(locations[index(x, z)])
        var appendToEnd = false
        var position: Long
        var sectorStart: Int

        synchronized(dataSource) {
            sectorStart = findAvailableSectors(sectorCount)
            if (sectorStart == -1) {
                val eof = dataSource.length()
                position = eof
                sectorStart = (eof / SectorSize).toInt()
                for (i in 0 until sectorCount) writeBytes(eof + i * SectorSize, ByteArray(SectorSize) { 0 })
                appendToEnd = true
            } else {
                position = (sectorStart * SectorSize).toLong()
            }
            for (i in sectorStart until sectorStart + sectorCount) {
                if (i < freeSectors.size) freeSectors[i] = false else freeSectors += false
            }
            writeInt(position, dataSize)
            writeByte(position + 4, ZlibCompression)
            writeBytes(position + 5, dataOut.toByteArray())
            if (appendToEnd) addPadding()
            locations[location] = buildLocation(sectorStart, sectorCount)
            writeLocation(column.x, column.z)
            timestamps[location] = System.currentTimeMillis().toInt()
            writeTimestamp(column.x, column.z)
            for (i in previousSectorStart until previousSectorStart + previousSectorCount) freeSectors[i] = true
        }
    }

    // ── Block / biome accessors (Y bounds use minY..maxY) ────────────────────

    @Throws(AnvilException::class, IllegalArgumentException::class)
    fun setBlockState(x: Int, y: Int, z: Int, blockState: BlockState) {
        if (out(x.blockToChunk(), z.blockToChunk())) throw IllegalArgumentException("Out of region $x;$z (block)")
        if (y !in minY..maxY) throw IllegalArgumentException("y ($y) must be in $minY..$maxY")
        val chunk = getOrCreateChunk(x.blockToChunk(), z.blockToChunk())
        chunk.setBlockState(x.blockInsideChunk(), y, z.blockInsideChunk(), blockState)
    }

    @Throws(AnvilException::class, IllegalArgumentException::class)
    fun getBlockState(x: Int, y: Int, z: Int): BlockState {
        if (out(x.blockToChunk(), z.blockToChunk())) throw IllegalArgumentException("Out of region $x;$z (block)")
        if (y !in minY..maxY) throw IllegalArgumentException("y ($y) must be in $minY..$maxY")
        val chunk = getChunk(x.blockToChunk(), z.blockToChunk()) ?: throw AnvilException("No chunk at $x,$y,$z")
        return chunk.getBlockState(x.blockInsideChunk(), y, z.blockInsideChunk())
    }

    @Throws(AnvilException::class, IllegalArgumentException::class)
    fun setBiome(x: Int, y: Int, z: Int, biomeID: Int) {
        if (out(x.blockToChunk(), z.blockToChunk())) throw IllegalArgumentException("Out of region $x;$z (block)")
        if (y !in minY..maxY) throw IllegalArgumentException("y ($y) must be in $minY..$maxY")
        val chunk = getOrCreateChunk(x.blockToChunk(), z.blockToChunk())
        chunk.setBiome(x.blockInsideChunk(), y, z.blockInsideChunk(), biomeID)
    }

    @Throws(AnvilException::class, IllegalArgumentException::class)
    fun getBiome(x: Int, y: Int, z: Int): Int {
        if (out(x.blockToChunk(), z.blockToChunk())) throw IllegalArgumentException("Out of region $x;$z (block)")
        if (y !in minY..maxY) throw IllegalArgumentException("y ($y) must be in $minY..$maxY")
        val chunk = getChunk(x.blockToChunk(), z.blockToChunk()) ?: throw AnvilException("No chunk at $x,$y,$z")
        return chunk.getBiome(x.blockInsideChunk(), y, z.blockInsideChunk())
    }

    @Throws(AnvilException::class)
    fun hasChunk(x: Int, z: Int): Boolean {
        if (out(x, z)) throw AnvilException("Out of RegionFile: $x,$z (chunk)")
        return locations[index(x.chunkInsideRegion(), z.chunkInsideRegion())] != 0
    }

    @Throws(AnvilException::class)
    fun hasLoadedChunk(x: Int, z: Int): Boolean = hasChunk(x, z) ||
            columnCache.containsKey(index(x.chunkInsideRegion(), z.chunkInsideRegion()))

    @Throws(IOException::class)
    fun flushCachedChunks() {
        synchronized(columnCache) {
            columnCache.values.parallelStream().forEach { writeColumn(it) }
            columnCache.clear()
        }
    }

    @Throws(IOException::class)
    override fun close() {
        synchronized(columnCache) { columnCache.clear() }
        dataSource.close()
    }

    fun forget(column: ChunkColumn) {
        val idx = index(column.x, column.z)
        if (columnCache[idx] == column) columnCache.remove(idx)
        else throw IllegalArgumentException("Tried to remove column that is not inside the region")
    }

    // ── Internal helpers ─────────────────────────────────────────────────────

    private fun addPadding() {
        synchronized(dataSource) {
            val missing = dataSource.length() % SectorSize
            if (missing > 0) dataSource.setLength(dataSource.length() + (SectorSize - missing))
        }
    }

    private fun writeLocation(x: Int, z: Int) = writeInt(index(x, z) * 4L, locations[index(x, z)])
    private fun writeByte(pos: Long, b: Byte) = dataSource.writeByte(pos, b)
    private fun writeBytes(pos: Long, bytes: ByteArray) = dataSource.writeBytes(pos, bytes)
    private fun writeInt(pos: Long, int: Int) = dataSource.writeInt(pos, int)
    private fun readBytes(pos: Long, dest: ByteArray) = dataSource.readBytes(pos, dest)
    private fun readByte(pos: Long): Byte = dataSource.readByte(pos)
    private fun readInt(pos: Long): Int = dataSource.readInt(pos)
    private fun writeTimestamp(x: Int, z: Int) = writeInt(index(x, z) * 4L + 4096, timestamps[index(x, z)])

    private fun findAvailableSectors(count: Int): Int {
        for (start in 0 until freeSectors.size - count) {
            if ((0 until count).all { freeSectors[it + start] }) return start
        }
        return -1
    }

    @Suppress("NOTHING_TO_INLINE") private inline fun out(x: Int, z: Int) = x.chunkToRegion() != regionX || z.chunkToRegion() != regionZ
    @Suppress("NOTHING_TO_INLINE") private inline fun sizeInSectors(loc: Int) = loc and 0xFF
    @Suppress("NOTHING_TO_INLINE") private inline fun sectorOffset(loc: Int) = loc ushr 8
    @Suppress("NOTHING_TO_INLINE") private inline fun index(cx: Int, cz: Int) = (cx.chunkInsideRegion() and 31) + (cz.chunkInsideRegion() and 31) * 32
    @Suppress("NOTHING_TO_INLINE") private inline fun fileOffset(cx: Int, cz: Int) = sectorOffset(locations[index(cx, cz)]) * SectorSize
    @Suppress("NOTHING_TO_INLINE") private inline fun buildLocation(start: Int, length: Int) = ((start shl 8) or (length and 0xFF)) and 0xFFFFFFFF.toInt()
}
