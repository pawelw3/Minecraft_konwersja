"""Big Reactors block-only mappings for 1.7.10 -> 1.18.2.

Maps numeric ID + metadata (BRMetalBlock) to BiggerReactors block IDs.
"""

from __future__ import annotations

# BRMetalBlock metadata -> BiggerReactors target
BR_METAL_MAP: dict[int, str] = {
    0: "biggerreactors:uranium_block",   # Yellorium -> Uranium
    1: "biggerreactors:cyanite_block",
    2: "biggerreactors:graphite_block",
    3: "biggerreactors:blutonium_block",
    4: "biggerreactors:ludicrite_block",
}

# Registry name -> converter handler key
REGISTRY_HANDLERS: dict[str, str] = {
    "bigreactors:yelloriteore": "ore",
    "bigreactors:brmetalblock": "metal",
}

# Fallback block for unknown BRMetal metadata
FALLBACK_METAL = "biggerreactors:graphite_block"

# Ore mapping
ORE_TARGET = "biggerreactors:uranium_ore"
ORE_TARGET_DEEPSLATE = "biggerreactors:deepslate_uranium_ore"
