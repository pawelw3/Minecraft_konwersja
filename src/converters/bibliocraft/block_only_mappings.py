"""BiblioCraft block-only mappings for 1.7.10 -> 1.18.2.

Only decorative blocks without TileEntity are mapped here.
"""

from __future__ import annotations

# Seat metadata -> wood type -> vanilla stairs
# BiblioCraft seat metadata corresponds to wood types.
SEAT_WOOD_MAP: dict[int, str] = {
    0: "minecraft:oak_stairs",
    1: "minecraft:spruce_stairs",
    2: "minecraft:birch_stairs",
    3: "minecraft:jungle_stairs",
    4: "minecraft:acacia_stairs",
    5: "minecraft:dark_oak_stairs",
}

# Fallback for unknown wood type
SEAT_FALLBACK = "minecraft:oak_stairs"

# Registry name -> handler key
# FML ItemData uses CamelCase names like "BiblioCraft:BiblioBell".
# We match lower-case with both the short and long "Biblio" prefix forms.
REGISTRY_HANDLERS: dict[str, str] = {
    "bibliocraft:bell": "bell",
    "bibliocraft:bibliobell": "bell",
    "bibliocraft:seat": "seat",
    "bibliocraft:biblioseats": "seat",
    "bibliocraft:mapframe": "mapframe",
    "bibliocraft:bibliomapframe": "mapframe",
}
