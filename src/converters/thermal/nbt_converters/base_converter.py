"""Bazowe narzedzia konwersji NBT dla Thermal Series.

Thermal 1.7.10 uzywa NBTTagCompound z polami takimi jak:
- Facing (byte)
- Type (byte) - tier/subtyp
- Energy (int) lub struktura z cofh.api.energy.EnergyStorage
- Inventory (NBTTagList)
- Augments (NBTTagList)
- SideCache / SideConfig (byte array)
- RedstoneControl (byte)

Thermal 1.18.2 uzywa CompoundTag z polami:
- energy (CompoundTag) z Stored, Capacity
- Items (ListTag) z Slot, id, Count, tag
- augments (ListTag)
- facing (string: north/south/east/west/up/down)
- side_config (int array lub string)
- redstone_control (string)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


# Mapping kierunkow 1.7.10 (byte) -> 1.18.2 (string)
FACING_BYTE_TO_STRING = {
    0: "down",
    1: "up",
    2: "north",
    3: "south",
    4: "west",
    5: "east",
}

# Tier 1.7.10 (byte) -> 1.18.2 (string)
TIER_BYTE_TO_STRING = {
    0: "basic",
    1: "hardened",
    2: "reinforced",
    3: "resonant",
    4: "creative",
}

# Redstone control 1.7.10 -> 1.18.2
REDSTONE_CONTROL_MAP = {
    0: "ignored",
    1: "low",
    2: "high",
    3: "disabled",
}


def convert_facing(nbt_1710: dict) -> str:
    """Konwertuje Facing z byte na string."""
    facing_byte = nbt_1710.get("Facing", 3)  # default south
    return FACING_BYTE_TO_STRING.get(facing_byte, "south")


def convert_tier(nbt_1710: dict) -> str:
    """Konwertuje Type (tier) z byte na string."""
    tier_byte = nbt_1710.get("Type", 0)
    return TIER_BYTE_TO_STRING.get(tier_byte, "basic")


def convert_energy(nbt_1710: dict, default_capacity: int = 40000) -> dict:
    """Konwertuje energie z formatu CoFH 1.7.10 na 1.18.2.

    W 1.7.10 energia moze byc w polu 'Energy' (int) lub w EnergyStorage.
    W 1.18.2: { Stored: int, Capacity: int }.
    """
    energy = nbt_1710.get("Energy", 0)
    # Czasami Energy jest CompoundTag z polami Storage / Capacity
    if isinstance(energy, dict):
        stored = energy.get("Storage", 0)
        capacity = energy.get("Capacity", default_capacity)
    else:
        stored = int(energy) if isinstance(energy, (int, float)) else 0
        capacity = default_capacity

    # RF -> FE (1:1)
    return {
        "Stored": stored,
        "Capacity": capacity,
    }


def convert_inventory(nbt_1710: dict, slot_offset: int = 0) -> List[dict]:
    """Konwertuje inventory z 1.7.10 na 1.18.2.

    1.7.10: 'Items' jako NBTTagList z tagami 'Slot', 'id', 'Damage', 'Count'
    1.18.2: 'Items' jako ListTag z 'Slot', 'id', 'Count', 'tag'
    """
    items = nbt_1710.get("Items", [])
    result = []
    if not isinstance(items, list):
        return result

    for item in items:
        if not isinstance(item, dict):
            continue
        slot = item.get("Slot", 0)
        item_id = item.get("id", "")
        count = item.get("Count", 1)
        damage = item.get("Damage", 0)

        # Mapowanie ID itemow (uproszczone)
        new_id = _map_item_id(item_id, damage)

        entry = {
            "Slot": slot + slot_offset,
            "id": new_id,
            "Count": count,
        }
        # Jesli item ma NBT (tag), zachowaj
        if "tag" in item:
            entry["tag"] = item["tag"]
        result.append(entry)

    return result


def _map_item_id(old_id: str, damage: int = 0) -> str:
    """Podstawowe mapowanie ID itemow 1.7.10 -> 1.18.2."""
    # Usun numer ID jesli jest (vanilla uzywala numerycznych ID czasem)
    # Thermal itemy maja zazwyczaj string ID
    if old_id.startswith("thermalexpansion:"):
        return old_id.replace("thermalexpansion:", "thermal:")
    if old_id.startswith("thermalfoundation:"):
        return old_id.replace("thermalfoundation:", "thermal:")
    if old_id.startswith("thermaldynamics:"):
        return old_id.replace("thermaldynamics:", "thermal:")
    # Mekanism fallback
    if old_id.startswith("Mekanism:"):
        return old_id.replace("Mekanism:", "mekanism:")
    return old_id


def convert_side_config(nbt_1710: dict) -> List[int]:
    """Konwertuje konfiguracje stron.

    1.7.10: 'SideCache' lub 'SideConfig' jako byte array (6 elementow)
    1.18.2: 'side_config' jako int array (6 elementow)
    """
    side_cache = nbt_1710.get("SideCache", nbt_1710.get("SideConfig", []))
    if isinstance(side_cache, list):
        return [int(x) for x in side_cache]
    return [0, 0, 0, 0, 0, 0]


def convert_redstone_control(nbt_1710: dict) -> str:
    """Konwertuje redstone control z byte na string."""
    rs = nbt_1710.get("RedstoneControl", 0)
    return REDSTONE_CONTROL_MAP.get(rs, "ignored")


def convert_augments(nbt_1710: dict) -> List[dict]:
    """Konwertuje augments z 1.7.10 na 1.18.2.

    1.7.10: 'Augments' jako NBTTagList itemow.
    1.18.2: 'augments' jako ListTag. Augmenty sa itemami w slotach augment.
    """
    augments = nbt_1710.get("Augments", [])
    if not isinstance(augments, list):
        return []
    result = []
    for i, aug in enumerate(augments):
        if not isinstance(aug, dict):
            continue
        entry = {
            "Slot": i,
            "id": _map_item_id(aug.get("id", "")),
            "Count": aug.get("Count", 1),
        }
        if "tag" in aug:
            entry["tag"] = aug["tag"]
        result.append(entry)
    return result


def build_base_nbt_1182(nbt_1710: dict, target_id: str) -> dict:
    """Buduje bazowy NBT Block Entity dla 1.18.2.

    Zwraca dict z polami wspolnymi dla wiekszosci TE Thermal.
    """
    return {
        "id": target_id,
        "x": nbt_1710.get("x", 0),
        "y": nbt_1710.get("y", 0),
        "z": nbt_1710.get("z", 0),
        "facing": convert_facing(nbt_1710),
        "energy": convert_energy(nbt_1710),
        "Items": convert_inventory(nbt_1710),
        "augments": convert_augments(nbt_1710),
        "side_config": convert_side_config(nbt_1710),
        "redstone_control": convert_redstone_control(nbt_1710),
    }
