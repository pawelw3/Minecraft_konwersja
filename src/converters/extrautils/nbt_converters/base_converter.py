"""
Bazowe narzędzia konwersji NBT dla Extra Utilities 1.7.10 → 1.18.2.

ExU 1.7.10 używa pól takich jak:
- Energy (int) - energia RF
- rotation (byte) - orientacja 0-3
- Tank_0 (CompoundTag) - tank na płyny
- coolDown (double)

Docelowe mody 1.18.2 (Thermal, Mekanism, Torchmaster) używają własnych formatów NBT.
"""
from __future__ import annotations

from typing import Any


# Mapowanie rotation ExU (0-3) → blockstate facing string
# W ExU rotation obliczany jest jako MathHelper.floor_double((rotationYaw+180)*4/360+0.5)&3
# co daje: 0=south, 1=west, 2=north, 3=east
ROTATION_TO_FACING = {
    0: "south",
    1: "west",
    2: "north",
    3: "east",
}


def convert_rotation_to_facing(nbt_1710: dict) -> str:
    """Konwertuje ExU rotation (byte 0-3) na facing string."""
    rotation = nbt_1710.get("rotation", 0)
    if isinstance(rotation, (int, float)):
        return ROTATION_TO_FACING.get(int(rotation) & 3, "south")
    return "south"


def convert_energy(nbt_1710: dict, default_capacity: int = 100000) -> dict:
    """Konwertuje energię RF z ExU na format CoFH 1.18.2 (FE).

    ExU 1.7.10: Energy (int) - RF
    1.18.2: { Stored: int, Capacity: int } - FE (1 RF = 1 FE)
    """
    energy = nbt_1710.get("Energy", 0)
    if isinstance(energy, dict):
        stored = int(energy.get("Storage", 0))
        capacity = int(energy.get("Capacity", default_capacity))
    else:
        stored = int(energy) if isinstance(energy, (int, float)) else 0
        capacity = default_capacity

    return {
        "Stored": stored,
        "Capacity": capacity,
    }


def convert_fluid_tank(tank_nbt: dict) -> dict:
    """Konwertuje tank płynów ExU na format CoFH/Neoforge 1.18.2.

    ExU 1.7.10 używa FluidTank z NBT zawierającym FluidName i Amount.
    1.18.2 używa zbliżonego formatu: { FluidName: str, Amount: int }.
    """
    if not isinstance(tank_nbt, dict):
        return {"FluidName": "", "Amount": 0}

    if tank_nbt.get("Empty") == "":
        return {"FluidName": "", "Amount": 0}

    fluid_name = tank_nbt.get("FluidName", "")
    amount = tank_nbt.get("Amount", 0)

    return {
        "FluidName": fluid_name,
        "Amount": int(amount),
    }


def build_base_nbt_1182(nbt_1710: dict, target_id: str) -> dict:
    """Buduje bazowy NBT Block Entity dla 1.18.2."""
    return {
        "id": target_id,
        "x": nbt_1710.get("x", 0),
        "y": nbt_1710.get("y", 0),
        "z": nbt_1710.get("z", 0),
    }
