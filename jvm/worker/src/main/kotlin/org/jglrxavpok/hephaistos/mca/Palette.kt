package org.jglrxavpok.hephaistos.mca

import org.jglrxavpok.hephaistos.collections.ImmutableLongArray
import org.jglrxavpok.hephaistos.nbt.NBT
import org.jglrxavpok.hephaistos.nbt.NBTCompound
import org.jglrxavpok.hephaistos.nbt.NBTList
import org.jglrxavpok.hephaistos.nbt.NBTType
import kotlin.math.ceil
import kotlin.math.log2

/**
 * Block palette for a chunk section.
 *
 * Identical to Hephaistos 2.2.0 except that the secondary constructor and
 * loadReferences() have been widened from `internal` to `public` so that the
 * overriding ChunkSection (in this worker module) can call them despite living
 * in a different Gradle module.
 */
class Palette() {

    val blocks = mutableListOf<BlockState>()
    private val referenceCounts = HashMap<BlockState, Int>()

    // Widened from internal to public so ChunkSection in this module can use it.
    constructor(blocks: NBTList<NBTCompound>) : this() {
        for (b in blocks) this.blocks += BlockState(b)
    }

    // Widened from internal to public.
    fun loadReferences(states: Iterable<BlockState>) {
        for (state in states) {
            if (state !in blocks) throw IllegalArgumentException("Tried to add a reference counter to $state which is not in this palette")
            referenceCounts[state] = (referenceCounts.computeIfAbsent(state) { 0 }) + 1
        }
    }

    fun increaseReference(block: BlockState) {
        if (referenceCounts.containsKey(block)) {
            referenceCounts[block] = referenceCounts[block]!! + 1
        } else {
            referenceCounts[block] = 1
            blocks.add(block)
        }
    }

    fun decreaseReference(block: BlockState) {
        if (referenceCounts.containsKey(block)) {
            referenceCounts[block] = referenceCounts[block]!! - 1
            if (referenceCounts[block]!! <= 0) {
                blocks.remove(block)
                referenceCounts.remove(block)
            }
        } else {
            throw IllegalArgumentException("Block state $block was not in the palette when trying to decrease its reference count")
        }
    }

    fun toNBT(): NBTList<NBTCompound> =
        NBT.List(NBTType.TAG_Compound, blocks.map { it.toNBT() })

    @JvmOverloads
    fun compactIDs(states: Array<BlockState>, version: SupportedVersion = SupportedVersion.Latest): ImmutableLongArray {
        val indices = states.map(blocks::indexOf).toIntArray()
        // 1.18.2+ requires a minimum of 4 bits per block-state entry.
        // Using fewer bits produces a long-array shorter than the server expects,
        // causing "invalid length given for storage" on chunk load.
        val minBits = if (version >= SupportedVersion.MC_1_18_2) 4 else 1
        val bitLength = ceil(log2(blocks.size.toFloat())).toInt().coerceAtLeast(minBits)
        return when {
            version == SupportedVersion.MC_1_15 -> compress(indices, bitLength)
            version >= SupportedVersion.MC_1_16 -> pack(indices, bitLength)
            else -> throw AnvilException("Unsupported version for compacting palette: $version")
        }
    }

    fun isEmpty(): Boolean = blocks.size == 1 && blocks[0] == BlockState.AIR
}
