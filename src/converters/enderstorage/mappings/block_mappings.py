"""
Mapowania EnderStorage 1.7.10 → 1.18.2.
"""

from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class BlockMapping:
    source_block_id: str
    source_metadata: int
    target_block_id: str
    nbt_converter: str
    notes: str = ""

STATIC_MAPPINGS: dict[tuple[str, int], BlockMapping] = {
    ("EnderStorage:enderChest", 0): BlockMapping(
        "EnderStorage:enderChest", 0,
        "enderstorage:ender_chest", "ender_chest",
        "Ender Chest → Ender Chest (frequency preserved)"
    ),
    ("EnderStorage:enderChest", 1): BlockMapping(
        "EnderStorage:enderChest", 1,
        "enderstorage:ender_tank", "ender_tank",
        "Ender Tank → Ender Tank (frequency preserved)"
    ),
}

def get_mapping(block_id: str, metadata: int) -> BlockMapping | None:
    return STATIC_MAPPINGS.get((block_id, metadata))

def is_enderstorage_block(block_id: str) -> bool:
    return block_id.startswith("EnderStorage:")
