package org.jglrxavpok.hephaistos.mca

import org.jglrxavpok.hephaistos.mca.AnvilException.Companion.missing
import org.jglrxavpok.hephaistos.nbt.NBT
import org.jglrxavpok.hephaistos.nbt.NBTCompound
import org.jglrxavpok.hephaistos.nbt.NBTType
import kotlin.experimental.and
import kotlin.experimental.or
import kotlin.math.ceil

/**
 * 16x16x16 subchunk.
 *
 * Extended from Hephaistos 2.2.0 to support the 1.18.2 section format where
 * block states are stored in a "block_states" compound (with "palette" and
 * optional "data") rather than top-level "Palette"+"BlockStates" fields.
 * Pre-1.18 format is fully preserved.
 */
class ChunkSection(val y: Byte) {

    private var palette: Palette? = null
    val empty get() = palette == null
    private val blockStates: Array<BlockState> = Array(16 * 16 * 16) { BlockState.AIR }
    var blockLights = ByteArray(0)
    var skyLights = ByteArray(0)

    @Throws(AnvilException::class)
    @JvmOverloads
    constructor(nbt: NBTCompound, version: SupportedVersion = SupportedVersion.Latest) :
            this(nbt.getByte("Y") ?: missing("Y")) {

        if (version < SupportedVersion.MC_1_17_0) {
            if (y !in 0..15)
                throw AnvilException("Invalid section Y: $y. Must be in 0..15 for pre-1.17 sections")
        }

        if (version >= SupportedVersion.MC_1_18_2) {
            // ── 1.18+ format ──────────────────────────────────────────────
            // Block states are inside a "block_states" compound.
            val bs = nbt.getCompound("block_states")
            if (bs != null) {
                val paletteList = bs.getList<NBTCompound>("palette")
                palette = paletteList?.let { Palette(it) }

                if (palette != null) {
                    val data = bs.getLongArray("data")
                    if (data != null && data.size > 0) {
                        val sizeInBits = data.size * 64 / 4096
                        val intPerLong = 64 / sizeInBits
                        val expected = ceil(4096.0 / intPerLong).toInt()
                        if (data.size != expected) {
                            throw AnvilException(
                                "Invalid block_states.data length (${data.size}). " +
                                "At $sizeInBits bits/value, expected $expected longs."
                            )
                        }
                        val ids = unpack(data, sizeInBits).sliceArray(0 until 4096)
                        for ((i, id) in ids.withIndex()) {
                            blockStates[i] = palette!!.blocks.getOrElse(id) { BlockState.AIR }
                        }
                    } else {
                        // Single-entry palette — all blocks are the same type.
                        val single = palette!!.blocks.firstOrNull() ?: BlockState.AIR
                        blockStates.fill(single)
                    }
                    palette!!.loadReferences(blockStates.asIterable())
                }
            }
            // Light arrays are still present in 1.18.2 sections.
            nbt.getByteArray("SkyLight")?.let { a ->
                skyLights = ByteArray(a.size); a.copyInto(skyLights)
            }
            nbt.getByteArray("BlockLight")?.let { a ->
                blockLights = ByteArray(a.size); a.copyInto(blockLights)
            }
        } else {
            // ── Pre-1.18 format ───────────────────────────────────────────
            val paletteNBT = nbt.getList<NBTCompound>("Palette")
            palette = paletteNBT?.let { Palette(it) }

            if (palette == null && nbt.containsKey("BlockStates")) {
                System.err.println(
                    "[Hephaistos] Attempted to load a ChunkSection with no palette but block states. " +
                    "Because Hephaistos cannot interpret global IDs, block states will be skipped"
                )
            } else if (palette != null) {
                val compactedBlockStates = nbt.getLongArray("BlockStates") ?: missing("BlockStates")
                val sizeInBits = compactedBlockStates.size * 64 / 4096
                val ids: IntArray = when {
                    version == SupportedVersion.MC_1_15 -> {
                        val d = decompress(compactedBlockStates, sizeInBits)
                        if (d.size != 4096) throw AnvilException("Invalid decompressed BlockStates length (${d.size}). Must be 4096")
                        d
                    }
                    version >= SupportedVersion.MC_1_16 -> {
                        val intPerLong = 64 / sizeInBits
                        val expected = ceil(4096.0 / intPerLong).toInt()
                        if (compactedBlockStates.size != expected)
                            throw AnvilException("Invalid compressed BlockStates length (${compactedBlockStates.size}). At $sizeInBits bit per value, expected $expected bytes")
                        unpack(compactedBlockStates, sizeInBits).sliceArray(0 until 4096)
                    }
                    else -> throw AnvilException("Unsupported version for compressed block states: $version")
                }
                for ((index, id) in ids.withIndex()) {
                    blockStates[index] = palette!!.blocks[id]
                }
                palette!!.loadReferences(blockStates.asIterable())

                nbt.getByteArray("BlockLight")?.let { a -> blockLights = ByteArray(a.size); a.copyInto(blockLights) }
                nbt.getByteArray("SkyLight")?.let { a -> skyLights = ByteArray(a.size); a.copyInto(skyLights) }
            }
        }
    }

    operator fun set(x: Int, y: Int, z: Int, block: BlockState) {
        checkBounds(x, y, z)
        if (palette == null) {
            palette = Palette()
            palette!!.blocks += BlockState.AIR
            palette!!.loadReferences(blockStates.asIterable())
            palette!!.increaseReference(block)
            palette!!.decreaseReference(BlockState.AIR)
            blockStates[index(x, y, z)] = block
        } else {
            val previous = this[x, y, z]
            palette!!.increaseReference(block)
            palette!!.decreaseReference(previous)
            blockStates[index(x, y, z)] = block
        }
    }

    @Throws(AnvilException::class)
    operator fun get(x: Int, y: Int, z: Int): BlockState {
        checkBounds(x, y, z)
        if (empty) throw AnvilException("Trying to access empty section!")
        return blockStates[index(x, y, z)]
    }

    @Throws(AnvilException::class)
    fun getBlockLight(x: Int, y: Int, z: Int): Byte {
        if (empty) throw AnvilException("Trying to access empty section!")
        checkBounds(x, y, z)
        val i = index(x, y, z)
        return if (i % 2 == 0) blockLights[i / 2] and 0x0F else ((blockLights[i / 2].toInt() shr 4) and 0x0F).toByte()
    }

    @Throws(AnvilException::class)
    fun getSkyLight(x: Int, y: Int, z: Int): Byte {
        if (empty) throw AnvilException("Trying to access empty section!")
        checkBounds(x, y, z)
        val i = index(x, y, z)
        return if (i % 2 == 0) skyLights[i / 2] and 0x0F else ((skyLights[i / 2].toInt() shr 4) and 0x0F).toByte()
    }

    fun setSkyLight(x: Int, y: Int, z: Int, light: Byte) {
        checkBounds(x, y, z); fillInIfEmpty()
        if (skyLights.isEmpty()) skyLights = ByteArray(2048)
        val i = index(x, y, z)
        skyLights[i / 2] = if (i % 2 == 0)
            (skyLights[i / 2] and 0xF0.toByte()) or (light and 0x0F)
        else
            (skyLights[i / 2] and 0x0F.toByte()) or ((light.toInt() shl 4) and 0x0F).toByte()
    }

    fun setBlockLight(x: Int, y: Int, z: Int, light: Byte) {
        checkBounds(x, y, z); fillInIfEmpty()
        if (blockLights.isEmpty()) blockLights = ByteArray(2048)
        val i = index(x, y, z)
        blockLights[i / 2] = if (i % 2 == 0)
            (blockLights[i / 2] and 0xF0.toByte()) or (light and 0x0F)
        else
            (blockLights[i / 2] and 0x0F.toByte()) or ((light.toInt() shl 4) and 0x0F).toByte()
    }

    private fun fillInIfEmpty() {
        if (empty) {
            palette = Palette()
            palette!!.blocks += BlockState.AIR
            palette!!.loadReferences(blockStates.asIterable())
        }
    }

    private fun checkBounds(x: Int, y: Int, z: Int) {
        if (x !in 0..15) throw IllegalArgumentException("x ($x) is not in 0..15")
        if (y !in 0..15) throw IllegalArgumentException("y ($y) is not in 0..15")
        if (z !in 0..15) throw IllegalArgumentException("z ($z) is not in 0..15")
    }

    private fun index(x: Int, y: Int, z: Int) = y * 256 + z * 16 + x

    @JvmOverloads
    fun toNBT(version: SupportedVersion = SupportedVersion.Latest): NBTCompound = NBT.Kompound {
        this["Y"] = NBT.Byte(y)

        if (version >= SupportedVersion.MC_1_18_2) {
            // ── 1.18+ format ──────────────────────────────────────────────
            if (!empty) {
                this["block_states"] = NBT.Kompound {
                    this["palette"] = palette!!.toNBT()
                    // Omit "data" when there is only one block type (MC optimisation).
                    if (palette!!.blocks.size > 1) {
                        this["data"] = NBT.LongArray(palette!!.compactIDs(blockStates, version))
                    }
                }
            }
            // Always write a biome entry so the server can load the chunk.
            this["biomes"] = NBT.Kompound {
                this["palette"] = NBT.List(NBTType.TAG_String, listOf(NBT.String("minecraft:plains")))
            }
            if (blockLights.isNotEmpty()) this["BlockLight"] = NBT.ByteArray(*blockLights)
            if (skyLights.isNotEmpty()) this["SkyLight"] = NBT.ByteArray(*skyLights)
        } else {
            // ── Pre-1.18 format ───────────────────────────────────────────
            this["BlockLight"] = NBT.ByteArray(*blockLights)
            this["SkyLight"] = NBT.ByteArray(*skyLights)
            if (!empty) {
                this["Palette"] = palette!!.toNBT()
                this["BlockStates"] = NBT.LongArray(palette!!.compactIDs(blockStates, version))
            }
        }
    }
}
