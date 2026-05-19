"""Konwerter NBT dla dynam (generatorow) Thermal Expansion.

Dynama 1.7.10: Steam, Magmatic, Compression, Reactant, Enervation
Target 1.18.2: thermal:dynamo_*
"""

from __future__ import annotations

from .base_converter import (
    build_base_nbt_1182,
    convert_energy,
    convert_facing,
    convert_tier,
    convert_redstone_control,
)


def convert_dynamo_nbt(nbt_1710: dict, target_id: str) -> dict:
    """Konwertuje NBT dynama z 1.7.10 na 1.18.2.

    Specyficzne pola dynama:
    - Fuel (int) - aktualne paliwo
    - FuelMax (int) - maksymalne paliwo
    - FuelItem (item) - item paliwowy (dla Reactant/Enervation)
    - FuelFluid (fluid) - plyn paliwowy (dla Steam/Magmatic/Compression)
    """
    result = build_base_nbt_1182(nbt_1710, target_id)

    # Pojemnosci energii dynama
    tier = convert_tier(nbt_1710)
    capacity_map = {
        "basic": 40000,
        "hardened": 160000,
        "reinforced": 360000,
        "resonant": 640000,
        "creative": 4000000,
    }
    cap = capacity_map.get(tier, 40000)
    result["energy"] = convert_energy(nbt_1710, default_capacity=cap)

    # Paliwo
    fuel = nbt_1710.get("Fuel", 0)
    fuel_max = nbt_1710.get("FuelMax", 1000)
    result["fuel"] = int(fuel)
    result["fuel_max"] = int(fuel_max)

    # Fluid paliwowy (dla Steam/Magmatic/Compression)
    fuel_fluid = nbt_1710.get("FuelFluid", {})
    if isinstance(fuel_fluid, dict):
        result["fuel_fluid"] = {
            "FluidName": fuel_fluid.get("FluidName", ""),
            "Amount": fuel_fluid.get("Amount", 0),
        }
    else:
        result["fuel_fluid"] = {"FluidName": "", "Amount": 0}

    # Item paliwowy (dla Reactant/Enervation)
    fuel_item = nbt_1710.get("FuelItem", {})
    if isinstance(fuel_item, dict):
        result["fuel_item"] = {
            "id": fuel_item.get("id", ""),
            "Count": fuel_item.get("Count", 1),
        }
    else:
        result["fuel_item"] = {"id": "", "Count": 0}

    # Tier
    result["tier"] = tier

    # Augmenty (dynamy moga miec augments wplywajace na output)
    # Zostawiamy z base_converter

    # Redstone control
    result["redstone_control"] = convert_redstone_control(nbt_1710)

    # Usun Items (dynama nie maja inventory)
    result.pop("Items", None)

    return result
