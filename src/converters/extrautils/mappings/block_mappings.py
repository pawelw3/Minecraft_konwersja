"""
Mapowania bloków Extra Utilities 1.7.10 → 1.18.2.

Strategia: hybrydowa — różne funkcje ExU mapowane na dedykowane mody 1.18.2.
Zob. docs/MAPAOWANIE_USUNIETYCH_MODOW.md, sekcja Extra Utilities.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BlockMapping:
    source_block_id: str
    source_metadata: int
    target_block_id: str
    nbt_converter: str | None
    notes: str = ""


# ──────────────────────────────────────────────────────────────────────────────
# Generatory Extra Utilities
# Blok: extrautils:generator / extrautils:generator.8 / extrautils:generator.64
# Meta określa typ generatora (0-11).
# W 1.18.2 mapujemy na odpowiedniki Thermal Series / Mekanism.
# ──────────────────────────────────────────────────────────────────────────────
_GENERATOR_TYPES: dict[int, tuple[str, str, str]] = {
    # meta: (suffix, target_block, notes)
    0: ("stone",     "thermal:dynamo_stirling",   "Survivalist Generator → Stirling Dynamo"),
    1: ("base",      "thermal:dynamo_stirling",   "Furnace Generator → Stirling Dynamo"),
    2: ("lava",      "thermal:dynamo_magmatic",   "Lava Generator → Magmatic Dynamo"),
    3: ("ender",     "thermal:dynamo_numismatic", "Ender Generator → Numismatic Dynamo"),
    4: ("redflux",   "thermal:dynamo_lapidary",   "Heated Redstone Generator → Lapidary Dynamo"),
    5: ("food",      "thermal:dynamo_gourmand",   "Culinary Generator → Gourmand Dynamo"),
    6: ("potion",    "thermal:dynamo_compression", "Potion Generator → Compression Dynamo (fluid fuel)"),
    7: ("solar",     "mekanismgenerators:solar_generator", "Solar Generator → Solar Generator (Mek)"),
    8: ("tnt",       "thermal:dynamo_disenchantment", "TNT Generator → Disenchantment Dynamo"),
    9: ("pink",      "thermal:dynamo_gourmand",   "Pink Generator → Gourmand Dynamo (fallback)"),
    10: ("overclocked", "thermal:dynamo_stirling", "High-temp Furnace Generator → Stirling Dynamo"),
    11: ("nether",    "thermal:dynamo_numismatic", "Nether Star Generator → Numismatic Dynamo"),
}

# Trzy bloki generatorów w ExU (x1, x8, x64)
_GENERATOR_BLOCKS = [
    "extrautils:generator",
    "extrautils:generator.8",
    "extrautils:generator.64",
]


# ──────────────────────────────────────────────────────────────────────────────
# Bloki bezpośrednie (dekoracyjne / utility)
# ─────────────────────────────────────────────────────────────────────────────-
_STATIC_MAPPINGS: dict[tuple[str, int], BlockMapping] = {
    # Magnum Torch (AntiMobTorch) → Torchmaster Mega Torch
    ("extrautils:magnumTorch", 0): BlockMapping(
        "extrautils:magnumTorch", 0,
        "torchmaster:megatorch", None,
        "Magnum Torch → Mega Torch (spawn protection preserved)"
    ),

    # Cursed Earth → Cursed Earth mod
    ("extrautils:cursedEarth", 0): BlockMapping(
        "extrautils:cursedEarth", 0,
        "cursedearth:cursed_earth", None,
        "Cursed Earth → Cursed Earth"
    ),
    ("extrautils:cursedearthside", 0): BlockMapping(
        "extrautils:cursedearthside", 0,
        "cursedearth:cursed_earth", None,
        "Cursed Earth (side variant) → Cursed Earth"
    ),

    # Angel Block → Angel Block Renewed
    ("extrautils:angelBlock", 0): BlockMapping(
        "extrautils:angelBlock", 0,
        "angelblockrenewed:angel_block", None,
        "Angel Block → Angel Block Renewed"
    ),

    # Trash Can → Trash Cans mod
    ("extrautils:trashCan", 0): BlockMapping(
        "extrautils:trashCan", 0,
        "trashcans:item_trash_can", None,
        "Trash Can → Item Trash Can"
    ),
    ("extrautils:trashCan", 1): BlockMapping(
        "extrautils:trashCan", 1,
        "trashcans:liquid_trash_can", None,
        "Fluid Trash Can → Liquid Trash Can"
    ),
    ("extrautils:trashCan", 2): BlockMapping(
        "extrautils:trashCan", 2,
        "trashcans:energy_trash_can", None,
        "Energy Trash Can → Energy Trash Can"
    ),
    ("extrautils:trashcan", 0): BlockMapping(
        "extrautils:trashcan", 0,
        "trashcans:item_trash_can", None,
        "Trash Can → Item Trash Can"
    ),
    ("extrautils:trashcan", 1): BlockMapping(
        "extrautils:trashcan", 1,
        "trashcans:liquid_trash_can", None,
        "Fluid Trash Can → Liquid Trash Can"
    ),
    ("extrautils:trashcan", 2): BlockMapping(
        "extrautils:trashcan", 2,
        "trashcans:energy_trash_can", None,
        "Energy Trash Can → Energy Trash Can"
    ),

    # Sound Muffler → Extreme Sound Muffler
    ("extrautils:soundMuffler", 0): BlockMapping(
        "extrautils:soundMuffler", 0,
        "extremesoundmuffler:sound_muffler", None,
        "Sound Muffler → Sound Muffler"
    ),
    ("extrautils:sound_muffler", 0): BlockMapping(
        "extrautils:sound_muffler", 0,
        "extremesoundmuffler:sound_muffler", None,
        "Sound Muffler → Sound Muffler"
    ),

    # Filing Cabinet — brak bezpośredniego odpowiednika, używamy placeholder z inventory
    ("extrautils:filing", 0): BlockMapping(
        "extrautils:filing", 0,
        "conversion_placeholders:inventory_placeholder", "filing_cabinet",
        "Filing Cabinet → inventory placeholder (no direct equivalent in 1.18.2)"
    ),
    ("extrautils:filing", 1): BlockMapping(
        "extrautils:filing", 1,
        "conversion_placeholders:inventory_placeholder", "filing_cabinet",
        "Filing Cabinet → inventory placeholder (no direct equivalent in 1.18.2)"
    ),
    ("extrautils:filing", 2): BlockMapping(
        "extrautils:filing", 2,
        "conversion_placeholders:inventory_placeholder", "filing_cabinet",
        "Filing Cabinet → inventory placeholder (no direct equivalent in 1.18.2)"
    ),
    ("extrautils:filing", 3): BlockMapping(
        "extrautils:filing", 3,
        "conversion_placeholders:inventory_placeholder", "filing_cabinet",
        "Filing Cabinet → inventory placeholder (no direct equivalent in 1.18.2)"
    ),
    ("extrautils:filing", 4): BlockMapping(
        "extrautils:filing", 4,
        "conversion_placeholders:inventory_placeholder", "filing_cabinet",
        "Filing Cabinet → inventory placeholder (no direct equivalent in 1.18.2)"
    ),
    ("extrautils:filing", 5): BlockMapping(
        "extrautils:filing", 5,
        "conversion_placeholders:inventory_placeholder", "filing_cabinet",
        "Filing Cabinet → inventory placeholder (no direct equivalent in 1.18.2)"
    ),
    # Diamond variant (meta + 6)
    ("extrautils:filing", 6): BlockMapping(
        "extrautils:filing", 6,
        "conversion_placeholders:inventory_placeholder", "filing_cabinet",
        "Diamond Filing Cabinet → inventory placeholder"
    ),
    ("extrautils:filing", 7): BlockMapping(
        "extrautils:filing", 7,
        "conversion_placeholders:inventory_placeholder", "filing_cabinet",
        "Diamond Filing Cabinet → inventory placeholder"
    ),
    ("extrautils:filing", 8): BlockMapping(
        "extrautils:filing", 8,
        "conversion_placeholders:inventory_placeholder", "filing_cabinet",
        "Diamond Filing Cabinet → inventory placeholder"
    ),
    ("extrautils:filing", 9): BlockMapping(
        "extrautils:filing", 9,
        "conversion_placeholders:inventory_placeholder", "filing_cabinet",
        "Diamond Filing Cabinet → inventory placeholder"
    ),
    ("extrautils:filing", 10): BlockMapping(
        "extrautils:filing", 10,
        "conversion_placeholders:inventory_placeholder", "filing_cabinet",
        "Diamond Filing Cabinet → inventory placeholder"
    ),
    ("extrautils:filing", 11): BlockMapping(
        "extrautils:filing", 11,
        "conversion_placeholders:inventory_placeholder", "filing_cabinet",
        "Diamond Filing Cabinet → inventory placeholder"
    ),

    # Drum — storage płynów (brak dobrego portu, placeholder)
    ("extrautils:drum", 0): BlockMapping(
        "extrautils:drum", 0,
        "conversion_placeholders:block_entity_placeholder", "drum",
        "Drum → placeholder (fluid storage cannot be directly converted)"
    ),

    # Ender Quarry — brak bezpośredniego odpowiednika w jednym bloku
    ("extrautils:enderQuarry", 0): BlockMapping(
        "extrautils:enderQuarry", 0,
        "conversion_placeholders:block_entity_placeholder", "ender_quarry",
        "Ender Quarry → placeholder (use RFTools Builder + Quarry Card manually)"
    ),

    # Ender-Thermic Pump
    ("extrautils:enderThermicPump", 0): BlockMapping(
        "extrautils:enderThermicPump", 0,
        "mekanism:electric_pump", "ender_thermic_pump",
        "Ender-Thermic Pump → Mekanism Electric Pump"
    ),
}


def _build_generator_mappings() -> dict[tuple[str, int], BlockMapping]:
    """Rozwijaj mapowania generatorów dla x1, x8, x64."""
    mappings: dict[tuple[str, int], BlockMapping] = {}
    for block in _GENERATOR_BLOCKS:
        for meta, (suffix, target, notes) in _GENERATOR_TYPES.items():
            mappings[(block, meta)] = BlockMapping(
                block, meta, target, "generator", notes
            )
    return mappings


STATIC_MAPPINGS: dict[tuple[str, int], BlockMapping] = {
    **_STATIC_MAPPINGS,
    **_build_generator_mappings(),
}


def _normalize_block_id(block_id: str) -> str:
    """Normalizuj nazwę bloku ExU — mapa 1.7.10 używa 'ExtraUtilities:'
    podczas gdy mapowania w projekcie używają 'extrautils:'."""
    bid = block_id.lower()
    if bid.startswith("extrautilities:"):
        return "extrautils:" + block_id[len("ExtraUtilities:"):]
    return block_id


def get_mapping(block_id: str, metadata: int = 0) -> BlockMapping | None:
    """Pobierz mapowanie dla bloku 1.7.10."""
    normalized = _normalize_block_id(block_id)
    return STATIC_MAPPINGS.get((normalized, metadata))


def is_extrautils_block(block_id: str) -> bool:
    """Sprawdź czy block_id należy do Extra Utilities."""
    if not block_id:
        return False
    bid = block_id.lower()
    return bid.startswith("extrautils:") or bid.startswith("extrautilities:")


# Mapowanie TileEntity ID → (block_id, metadata) dla przypadków gdy
# TE id jest znane, ale block_id trzeba wywnioskować.
TE_ID_TO_BLOCK: dict[str, tuple[str, int]] = {
    # Generatory — TE id to "extrautils:generator<suffix>"
    "extrautils:generatorstone":        ("extrautils:generator", 0),
    "extrautils:generatorbase":         ("extrautils:generator", 1),
    "extrautils:generatorlava":         ("extrautils:generator", 2),
    "extrautils:generatorender":        ("extrautils:generator", 3),
    "extrautils:generatorredflux":      ("extrautils:generator", 4),
    "extrautils:generatorfood":         ("extrautils:generator", 5),
    "extrautils:generatorpotion":       ("extrautils:generator", 6),
    "extrautils:generatorsolar":        ("extrautils:generator", 7),
    "extrautils:generatortnt":          ("extrautils:generator", 8),
    "extrautils:generatorpink":         ("extrautils:generator", 9),
    "extrautils:generatoroverclocked":  ("extrautils:generator", 10),
    "extrautils:generatornether":       ("extrautils:generator", 11),
    # Magnum Torch
    "TileEntityAntiMobTorch":           ("extrautils:magnumTorch", 0),
    # Filing Cabinet
    "TileEntityFilingCabinet":          ("extrautils:filing", 0),
    # Drum
    "extrautils:drum":                  ("extrautils:drum", 0),
    # Ender Quarry
    "extrautils:enderquarry":           ("extrautils:enderQuarry", 0),
    # Ender-Thermic Pump
    "extrautils:enderpump":             ("extrautils:enderThermicPump", 0),
}
