"""Konwerter NBT dla maszyn Thermal Expansion.

Maszyny 1.7.10: Furnace, Pulverizer, Sawmill, Smelter, Crucible, Transposer,
                Precipitator, Extruder, Accumulator, Assembler, Charger, Insolator

Target 1.18.2: thermal:machine_* (z wyjatkiem fallbackow na Mekanism)
"""

from __future__ import annotations

from typing import Any, Dict

from .base_converter import (
    build_base_nbt_1182,
    convert_energy,
    convert_facing,
    convert_inventory,
    convert_augments,
    convert_tier,
    convert_redstone_control,
    convert_side_config,
)


def convert_machine_nbt(nbt_1710: dict, target_id: str) -> dict:
    """Konwertuje NBT maszyny z 1.7.10 na 1.18.2.

    Specyficzne pola maszyn:
    - Process (int) - aktualny postep
    - ProcessMax (int) - maksymalny postep
    - SlotIn / SlotOut - sloty input/output (rozne nazwy w zaleznosci od maszyny)
    """
    result = build_base_nbt_1182(nbt_1710, target_id)

    # Maszyny maja rozne pojemnosci energii w zaleznosci od tieru
    tier = convert_tier(nbt_1710)
    capacity_map = {
        "basic": 20000,
        "hardened": 80000,
        "reinforced": 180000,
        "resonant": 320000,
        "creative": 2000000,
    }
    default_cap = capacity_map.get(tier, 40000)
    result["energy"] = convert_energy(nbt_1710, default_capacity=default_cap)

    # Proces przetwarzania
    progress = nbt_1710.get("Process", 0)
    progress_max = nbt_1710.get("ProcessMax", 200)
    result["process"] = int(progress)
    result["process_max"] = int(progress_max)

    # Inventory maszyny: zazwyczaj sloty 0-5 (input, output, secondary)
    # W 1.18.2 sloty maja te same numery
    result["Items"] = convert_inventory(nbt_1710)

    # Tier maszyny (w 1.18.2 w blockstate, ale czasem w NBT)
    result["tier"] = tier

    # Augmenty (wplywaja na speed/efficiency)
    result["augments"] = convert_augments(nbt_1710)

    # Konfiguracja stron (input/output)
    result["side_config"] = convert_side_config(nbt_1710)

    # Redstone control
    result["redstone_control"] = convert_redstone_control(nbt_1710)

    # Usun potencjalnie duplikujace sie pola z base
    result.pop("ForgeData", None)

    return result


def convert_charger_nbt(nbt_1710: dict, target_id: str) -> dict:
    """Konwerter dla Energetic Infuser / Charge Bench."""
    result = convert_machine_nbt(nbt_1710, target_id)
    # Charger ma slot na ladowany item (zazwyczaj slot 0)
    # W 1.18.2 charge_bench ma podobna mechanike
    result["charge_slot"] = 0
    return result


def convert_insolator_nbt(nbt_1710: dict, target_id: str) -> dict:
    """Konwerter dla Phytogenic Insolator."""
    result = convert_machine_nbt(nbt_1710, target_id)
    # Insolator ma dodatkowe pole na soil/fertilizer
    result["soil_type"] = nbt_1710.get("Soil", "")
    result["fertilizer"] = nbt_1710.get("Fertilizer", 0)
    return result
