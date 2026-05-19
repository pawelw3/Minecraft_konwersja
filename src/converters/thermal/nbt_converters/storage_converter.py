"""Konwerter NBT dla storage blocks: Cell, Tank, Strongbox, Cache, Workbench.

W 1.7.10 storage ma tier (Type byte: 0-4).
W 1.18.2 tier jest w blockstate (type=basic/hardened/reinforced/resonant/creative).
"""

from __future__ import annotations

from .base_converter import (
    build_base_nbt_1182,
    convert_energy,
    convert_inventory,
    convert_tier,
)


def convert_cell_nbt(nbt_1710: dict, target_id: str) -> dict:
    """Konwertuje Energy Cell (1.7.10) -> energy_cell (1.18.2).

    Specyficzne pola:
    - Type (byte) - tier
    - Tracker (byte) - output tracker
    - Send (int) - max energy send per tick
    """
    result = build_base_nbt_1182(nbt_1710, target_id)
    tier = convert_tier(nbt_1710)

    # Pojemnosci energii per tier w 1.7.10
    capacity_map = {
        "basic": 2000000,
        "hardened": 8000000,
        "reinforced": 18000000,
        "resonant": 32000000,
        "creative": 200000000,
    }
    cap = capacity_map.get(tier, 2000000)
    result["energy"] = convert_energy(nbt_1710, default_capacity=cap)

    # Output rate (Send)
    send = nbt_1710.get("Send", 0)
    result["output_rate"] = int(send)

    # Tier w NBT (blockstate tez bedzie mial type)
    result["tier"] = tier

    # Usun Items (Cell nie ma inventory)
    result.pop("Items", None)
    result.pop("augments", None)

    return result


def convert_tank_nbt(nbt_1710: dict, target_id: str) -> dict:
    """Konwertuje Portable Tank (1.7.10) -> fluid_cell (1.18.2).

    Specyficzne pola:
    - Type (byte) - tier
    - Mode (byte) - input/output mode
    - Tank (NBTTagCompound) - fluid data
    """
    result = build_base_nbt_1182(nbt_1710, target_id)
    tier = convert_tier(nbt_1710)

    # Pojemnosci plynu per tier
    capacity_map = {
        "basic": 8000,
        "hardened": 32000,
        "reinforced": 72000,
        "resonant": 128000,
        "creative": 800000,
    }
    cap = capacity_map.get(tier, 8000)

    # Fluid data
    tank = nbt_1710.get("Tank", {})
    if isinstance(tank, dict):
        fluid_name = tank.get("FluidName", "")
        fluid_amount = tank.get("Amount", 0)
    else:
        fluid_name = ""
        fluid_amount = 0

    result["tank"] = {
        "FluidName": fluid_name,
        "Amount": int(fluid_amount),
        "Capacity": cap,
    }
    result["tier"] = tier
    result["mode"] = int(nbt_1710.get("Mode", 0))  # 0=input, 1=output, 2=both

    # Usun Items (Tank nie ma inventory)
    result.pop("Items", None)
    result.pop("augments", None)

    return result


def convert_strongbox_nbt(nbt_1710: dict, target_id: str) -> dict:
    """Konwertuje Strongbox (1.7.10) -> item_cell (1.18.2).

    Strongbox to skrzynia z 9/18/27/36/45 slotami w zaleznosci od tieru.
    Item Cell w 1.18.2 przechowuje 1 typ itemu w duzej ilosci.
    To jest lossy conversion!
    """
    result = build_base_nbt_1182(nbt_1710, target_id)
    tier = convert_tier(nbt_1710)

    # Liczba slotow w Strongbox (1.7.10)
    slots_map = {
        "basic": 9,
        "hardened": 18,
        "reinforced": 27,
        "resonant": 36,
        "creative": 45,
    }
    result["legacy_strongbox_slots"] = slots_map.get(tier, 9)
    result["tier"] = tier

    # Inventory Strongbox -> Items
    result["Items"] = convert_inventory(nbt_1710)

    # Item Cell nie ma augmentow
    result.pop("augments", None)
    result.pop("energy", None)

    return result


def convert_cache_nbt(nbt_1710: dict, target_id: str) -> dict:
    """Konwertuje Cache (1.7.10) -> item_cell (1.18.2).

    Cache przechowywal 1 typ itemu w stacku xN (N zalezne od tieru).
    Item Cell w 1.18.2 robi to samo — to jest funkcjonalny odpowiednik.
    """
    result = build_base_nbt_1182(nbt_1710, target_id)
    tier = convert_tier(nbt_1710)

    # Cache capacity per tier (stack multiplier)
    capacity_map = {
        "basic": 2000,
        "hardened": 8000,
        "reinforced": 18000,
        "resonant": 32000,
        "creative": 200000,
    }
    result["item_capacity"] = capacity_map.get(tier, 2000)
    result["tier"] = tier

    # Cache zazwyczaj mial 1 slot z itemem
    result["Items"] = convert_inventory(nbt_1710)

    result.pop("augments", None)
    result.pop("energy", None)

    return result


def convert_workbench_nbt(nbt_1710: dict, target_id: str) -> dict:
    """Konwertuje Tinker's Workbench (1.7.10) -> tinker_bench (1.18.2)."""
    result = build_base_nbt_1182(nbt_1710, target_id)
    tier = convert_tier(nbt_1710)
    result["tier"] = tier
    result["Items"] = convert_inventory(nbt_1710)
    result.pop("augments", None)
    result.pop("energy", None)
    return result
