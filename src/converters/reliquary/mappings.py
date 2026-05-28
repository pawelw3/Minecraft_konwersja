"""Block/item ID mappings for Reliquary 1.7.10 → 1.18.2.

1.7.10 uses modid `xreliquary`, 1.18.2 uses `reliquary`.
Block string-keys used in 1.7.10 (as registered by Sandstone helper) match
the 1.18.2 registry path suffix, so the mapping is straightforward.
"""

# Reliquary TE IDs in 1.7.10 NBT → 1.18.2 block registry ID
# These are the values stored in the `id` field of TileEntity NBT.
TE_ID_TO_BLOCK: dict[str, str] = {
    "reliquaryAltar":   "reliquary:alkahestry_altar",
    "reliquaryCauldron": "reliquary:apothecary_cauldron",
    "apothecaryMortar": "reliquary:apothecary_mortar",
}

# Reliquary block string-keys in 1.7.10 → 1.18.2 registry IDs
# Used for blocks without TE (converted via block-id-only events).
BLOCK_ID_MAP: dict[str, str] = {
    "xreliquary:alkahestry_altar":    "reliquary:alkahestry_altar",
    "xreliquary:apothecary_cauldron": "reliquary:apothecary_cauldron",
    "xreliquary:apothecary_mortar":   "reliquary:apothecary_mortar",
    "xreliquary:fertile_lily_pad":    "reliquary:fertile_lily_pad",
    "xreliquary:interdiction_torch":  "reliquary:interdiction_torch",
    "xreliquary:wraith_node":         "reliquary:wraith_node",
    # Bare string-key variants (as used internally by Sandstone registry)
    "alkahestry_altar":    "reliquary:alkahestry_altar",
    "apothecary_cauldron": "reliquary:apothecary_cauldron",
    "apothecary_mortar":   "reliquary:apothecary_mortar",
    "fertile_lily_pad":    "reliquary:fertile_lily_pad",
    "interdiction_torch":  "reliquary:interdiction_torch",
    "wraith_node":         "reliquary:wraith_node",
}

# All 1.7.10 TE IDs that belong to Reliquary
RELIQUARY_TE_IDS: frozenset[str] = frozenset(TE_ID_TO_BLOCK.keys())
