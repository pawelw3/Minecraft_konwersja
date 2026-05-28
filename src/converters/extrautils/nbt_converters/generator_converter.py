"""
Konwerter NBT dla generatorów Extra Utilities 1.7.10 → 1.18.2.

Generatory ExU mapowane są na:
- Thermal Expansion Dynamo (dla większości typów)
- Mekanism Generators (dla solar)

NBT ExU generatora zawiera:
- Energy (int) - zgromadzona energia RF
- rotation (byte) - orientacja 0-3
- Tank_0 (CompoundTag) - tank na płyny (np. lava dla Magmatic)
- coolDown (double) - cooldown generatora
- backup (CompoundTag) - kopia zapasowa samego TE
"""
from __future__ import annotations

from typing import Any

from .base_converter import (
    build_base_nbt_1182,
    convert_energy,
    convert_fluid_tank,
    convert_rotation_to_facing,
)


def convert_generator_nbt(
    nbt_1710: dict,
    target_id: str,
) -> dict[str, Any]:
    """Konwertuje NBT generatora ExU na NBT dla 1.18.2 (Thermal/Mekanism).

    Returns dict z polami NBT oraz blockstate_props.
    """
    result = build_base_nbt_1182(nbt_1710, target_id)
    blockstate_props: dict[str, str] = {}
    warnings: list[str] = []

    # Energia: RF → FE (1:1)
    energy = convert_energy(nbt_1710)
    if energy["Stored"] > 0:
        warnings.append(
            f"EXU-W-ENERGY-TRANSFERRED: Transferred {energy['Stored']} RF → FE. "
            "Verify compatibility with target mod."
        )
    result["energy"] = energy

    # Orientacja: rotation → facing w blockstate
    facing = convert_rotation_to_facing(nbt_1710)
    blockstate_props["facing"] = facing

    # Tank płynów (dla generatorów które używają płynów, np. lava)
    tank = nbt_1710.get("Tank_0")
    if isinstance(tank, dict) and tank.get("Empty") != "":
        fluid = convert_fluid_tank(tank)
        if fluid["Amount"] > 0:
            warnings.append(
                f"EXU-W-FLUID-TRANSFERRED: Transferred {fluid['Amount']} mB of "
                f"{fluid['FluidName']}. Verify tank compatibility."
            )
        # W Thermal 1.18.2 tank paliwa w dynamo to zazwyczaj 'fuel' lub 'tank'
        # Używamy 'fuel' jako najbardziej prawdopodobnej nazwy dla Magmatic Dynamo
        result["fuel"] = fluid

    # coolDown nie ma bezpośredniego odpowiednika w Thermal 1.18.2
    cool_down = nbt_1710.get("coolDown", 0.0)
    if cool_down and cool_down > 0:
        warnings.append(
            f"EXU-W-COOLDOWN-LOST: coolDown value {cool_down} discarded — "
            "no equivalent in 1.18.2 dynamo."
        )

    # backup to kopia zapasowa samego TE — nie przenosimy
    if "backup" in nbt_1710:
        warnings.append("EXU-W-BACKUP-IGNORED: backup NBT ignored.")

    # Inventory (sloty paliwa) — jeśli istnieje
    items = nbt_1710.get("Items")
    if isinstance(items, list) and items:
        # Thermal 1.18.2 używa 'Items' jako ListTag
        # Ale większość dynamo nie ma inventory itemów (paliwo jest w tanku)
        warnings.append(
            "EXU-W-ITEMS-LOST: Generator inventory items cannot be directly "
            "converted to 1.18.2 dynamo format."
        )

    return {
        "nbt": result,
        "blockstate_props": blockstate_props,
        "warnings": warnings,
    }
