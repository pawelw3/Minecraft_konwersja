"""Symulacja konwersji magazynów energii IC2 → Mekanism/indreb/ftbic 1.18.2.

Obsługuje:
- BatBox, CESU, MFE, MFSU
- Chargepady (BatBox/CESU/MFE/MFSU)
- Konwersja energy (double EU) → FE (zależnie od targetu)

Źródła:
- IC2 1.7.10: TileEntityElectricBatBox/MFE/MFSU (writeToNBT)
- indreb 1.18.2: BlockEntityBatteryBox/MFE/MFSU/CESU (IndRebBlockEntity.save)
- ftbic 1.18.2: BatteryBoxBlockEntity (ElectricBlockEntity.writeData)
"""

from __future__ import annotations

import math
from typing import Any

from .machine_simulation import EU_TO_FE, convert_facing

# Pojemności docelowe Energy Cube w Mekanism (FE)
# Uwaga: W 1.18.2 Energy Cube ma różne tier'y z różnymi pojemnościami
MEKANISM_CUBE_CAPACITY = {
    "mekanism:basic_energy_cube": 1_600_000,
    "mekanism:advanced_energy_cube": 6_400_000,
    "mekanism:elite_energy_cube": 25_600_000,
    "mekanism:ultimate_energy_cube": 102_400_000,
}

# Mapowanie chargepadów → tier dla Mekanism
# W Mekanism chargepad ma jeden block_id, tier określany przez NBT
CHARGEPAD_TIER_BY_SOURCE = {
    ("IC2:blockChargepad", 0): "basic",
    ("IC2:blockChargepad", 1): "advanced",
    ("IC2:blockChargepad", 2): "elite",
    ("IC2:blockChargepad", 3): "ultimate",
}


def simulate_energy_storage_conversion(
    nbt_1710: dict[str, Any],
    target_block_id: str,
    source_block_id: str = "",
    source_metadata: int = 0,
) -> dict[str, Any]:
    """Konwertuje BatBox/MFE/MFSU/CESU na Energy Cube 1.18.2."""
    result = {
        "nbt_1182": {},
        "blockstate_props": {},
        "warnings": [],
        "errors": [],
    }
    
    # --- Facing ---
    ic2_facing = int(nbt_1710.get("facing", 2))
    result["blockstate_props"]["facing"] = convert_facing(ic2_facing)
    
    # --- Energy (EU → FE) ---
    energy_eu = float(nbt_1710.get("energy", 0.0))
    energy_fe = max(0, int(math.floor(energy_eu * EU_TO_FE)))
    
    if target_block_id.startswith("mekanism:"):
        result["nbt_1182"]["energyContainer"] = {"stored": energy_fe}
    elif target_block_id.startswith("indreb:"):
        # indreb: flat int "energy" (IndRebBlockEntity.save)
        result["nbt_1182"]["energy"] = energy_fe
    elif target_block_id.startswith("ftbic:"):
        # ftbic: double "Energy" (ElectricBlockEntity.writeData)
        result["nbt_1182"]["Energy"] = float(energy_fe)
    else:
        result["nbt_1182"]["energy"] = energy_fe
    
    # --- Redstone mode ---
    redstone_mode = nbt_1710.get("redstoneMode")
    if redstone_mode is not None and target_block_id.startswith("mekanism:"):
        result["nbt_1182"]["redstoneControl"] = int(redstone_mode)
    
    # --- Tier / Type (dla chargepadów) ---
    if source_block_id == "IC2:blockChargepad":
        if target_block_id.startswith("mekanism:"):
            tier = CHARGEPAD_TIER_BY_SOURCE.get((source_block_id, source_metadata), "basic")
            result["nbt_1182"]["tier"] = tier
        elif target_block_id.startswith("indreb:"):
            # indreb chargepady mają osobne block_id (charge_pad_battery_box, itp.)
            # tier jest zakodowany w block_id, nie w NBT
            pass
        elif target_block_id.startswith("ftbic:"):
            # ftbic chargepady - sprawdź czy mają tier w NBT
            pass
    
    # --- Capacity check ---
    capacity = MEKANISM_CUBE_CAPACITY.get(target_block_id)
    if capacity and energy_fe > capacity:
        result["warnings"].append(
            f"IC2-W-ENERGY-OVERFLOW: Energy {energy_fe} FE exceeds target capacity "
            f"{capacity}. Clamped to capacity."
        )
        if target_block_id.startswith("mekanism:"):
            result["nbt_1182"]["energyContainer"]["stored"] = capacity
        elif target_block_id.startswith("indreb:"):
            result["nbt_1182"]["energy"] = capacity
        elif target_block_id.startswith("ftbic:"):
            result["nbt_1182"]["Energy"] = float(capacity)
    
    return result
