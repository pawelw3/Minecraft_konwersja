package org.jglrxavpok.hephaistos.mca

/**
 * Supported Minecraft versions for chunk format reading/writing.
 *
 * Extends the original Hephaistos 2.2.0 enum with MC_1_18_2 support.
 * The 1.18 release (data version 2860+) removed the "Level" wrapper from chunk NBT
 * and changed section format from Palette/BlockStates to block_states compound.
 *
 * Pre-1.18 format (with Level): still fully supported — ordinal comparison ensures
 * MC_1_15/MC_1_16/MC_1_17_0 branches in ChunkSection/Palette remain unaffected.
 */
enum class SupportedVersion(val lowestDataVersion: Int) {

    MC_1_15(2225),
    MC_1_16(2504),
    MC_1_17_0(2724),
    MC_1_18_2(2860),  // flat format: no "Level" wrapper, lowercase "sections", "block_entities"
    ;

    companion object {

        val Latest: SupportedVersion = MC_1_18_2

        /**
         * Returns the closest known version for the given data version.
         * Defaults to MC_1_15 for very old data versions.
         */
        fun closest(dataVersion: Int): SupportedVersion {
            var closestFound = MC_1_15
            for (v in values()) {
                if (v.lowestDataVersion <= dataVersion) {
                    closestFound = v
                }
            }
            return closestFound
        }
    }
}
