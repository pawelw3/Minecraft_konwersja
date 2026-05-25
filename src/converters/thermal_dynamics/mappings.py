"""Mapowania bloków Thermal Dynamics 1.7.10 -> 1.18.2 (TD + Mekanism).

Zakres: wszystkie ducty z Thermal Dynamics 1.7.10.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BlockMapping:
    source_block_id: str
    metadata: int | None
    target_block_id: str
    has_block_entity: bool = False
    nbt_converter: str = "identity"
    notes: str = ""


# Bloki docelowe dostępne w 1.18.2
TARGET_BLOCKS_1182 = {
    # Thermal Dynamics
    "thermal:energy_duct",
    "thermal:fluid_duct",
    "thermal:fluid_duct_windowed",
    "thermal:item_buffer",
    # Mekanism
    "mekanism:basic_logistical_transporter",
    "mekanism:advanced_logistical_transporter",
    "mekanism:elite_logistical_transporter",
    "mekanism:ultimate_logistical_transporter",
    "mekanism:teleporter",
    "mekanism:teleporter_frame",
}


# Mapowanie (block_id, metadata) -> BlockMapping
# Źródło: dekompilacja TDDucts.java z ThermalDynamics-[1.7.10]1.2.1-172.jar
STATIC_MAPPINGS: dict[tuple[str, int], BlockMapping] = {
    # --- Energy Ducts (offset 0) ---
    ("ThermalDynamics:thermaldynamics.Duct0", 0): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct0", 0, "thermal:energy_duct", True, "energy_duct"
    ),
    ("ThermalDynamics:thermaldynamics.Duct0", 1): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct0", 1, "thermal:energy_duct", True, "energy_duct"
    ),
    ("ThermalDynamics:thermaldynamics.Duct0", 2): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct0", 2, "thermal:energy_duct", True, "energy_duct"
    ),
    ("ThermalDynamics:thermaldynamics.Duct0", 4): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct0", 4, "thermal:energy_duct", True, "energy_duct"
    ),
    ("ThermalDynamics:thermaldynamics.Duct0", 6): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct0", 6, "thermal:energy_duct", True, "energy_duct"
    ),
    # --- Fluid Ducts (offset 16) ---
    ("ThermalDynamics:thermaldynamics.Duct16", 0): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct16", 0, "thermal:fluid_duct", True, "fluid_duct"
    ),
    ("ThermalDynamics:thermaldynamics.Duct16", 1): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct16", 1, "thermal:fluid_duct", True, "fluid_duct"
    ),
    ("ThermalDynamics:thermaldynamics.Duct16", 2): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct16", 2, "thermal:fluid_duct", True, "fluid_duct"
    ),
    ("ThermalDynamics:thermaldynamics.Duct16", 3): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct16", 3, "thermal:fluid_duct", True, "fluid_duct"
    ),
    ("ThermalDynamics:thermaldynamics.Duct16", 4): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct16", 4, "thermal:fluid_duct", True, "fluid_duct"
    ),
    ("ThermalDynamics:thermaldynamics.Duct16", 5): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct16", 5, "thermal:fluid_duct", True, "fluid_duct"
    ),
    ("ThermalDynamics:thermaldynamics.Duct16", 6): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct16", 6, "thermal:fluid_duct_windowed", True, "fluid_duct"
    ),
    ("ThermalDynamics:thermaldynamics.Duct16", 7): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct16", 7, "thermal:fluid_duct_windowed", True, "fluid_duct"
    ),
    # --- Item Ducts (offset 32) -> Mekanism ---
    ("ThermalDynamics:thermaldynamics.Duct32", 0): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct32", 0, "mekanism:basic_logistical_transporter", True, "mekanism_transporter"
    ),
    ("ThermalDynamics:thermaldynamics.Duct32", 1): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct32", 1, "mekanism:basic_logistical_transporter", True, "mekanism_transporter"
    ),
    ("ThermalDynamics:thermaldynamics.Duct32", 2): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct32", 2, "mekanism:advanced_logistical_transporter", True, "mekanism_transporter"
    ),
    ("ThermalDynamics:thermaldynamics.Duct32", 3): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct32", 3, "mekanism:advanced_logistical_transporter", True, "mekanism_transporter"
    ),
    ("ThermalDynamics:thermaldynamics.Duct32", 4): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct32", 4, "mekanism:elite_logistical_transporter", True, "mekanism_transporter"
    ),
    ("ThermalDynamics:thermaldynamics.Duct32", 5): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct32", 5, "mekanism:elite_logistical_transporter", True, "mekanism_transporter"
    ),
    ("ThermalDynamics:thermaldynamics.Duct32", 6): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct32", 6, "mekanism:ultimate_logistical_transporter", True, "mekanism_transporter"
    ),
    ("ThermalDynamics:thermaldynamics.Duct32", 7): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct32", 7, "mekanism:ultimate_logistical_transporter", True, "mekanism_transporter"
    ),
    # --- Transport Ducts (offset 64) -> Mekanism ---
    ("ThermalDynamics:thermaldynamics.Duct64", 0): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct64", 0, "mekanism:teleporter", True, "mekanism_teleporter"
    ),
    ("ThermalDynamics:thermaldynamics.Duct64", 1): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct64", 1, "mekanism:teleporter", True, "mekanism_teleporter"
    ),
    ("ThermalDynamics:thermaldynamics.Duct64", 2): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct64", 2, "mekanism:teleporter", True, "mekanism_teleporter"
    ),
    ("ThermalDynamics:thermaldynamics.Duct64", 3): BlockMapping(
        "ThermalDynamics:thermaldynamics.Duct64", 3, "mekanism:teleporter_frame", False, "identity"
    ),
}


# Mapowanie TileEntity ID -> (block_id, default_metadata)
# Używane gdy konwerter jest wywoływany przez router na podstawie TE ID z NBT
TE_ID_TO_BLOCK: dict[str, tuple[str, int]] = {
    "thermaldynamics.FluxDuct": ("ThermalDynamics:thermaldynamics.Duct0", 0),
    "thermaldynamics.FluxDuctSuperConductor": ("ThermalDynamics:thermaldynamics.Duct0", 6),
    "thermaldynamics.FluidDuct": ("ThermalDynamics:thermaldynamics.Duct16", 2),
    "thermaldynamics.FluidDuctFragile": ("ThermalDynamics:thermaldynamics.Duct16", 0),
    "thermaldynamics.FluidDuctFlux": ("ThermalDynamics:thermaldynamics.Duct16", 4),
    "thermaldynamics.FluidDuctSuper": ("ThermalDynamics:thermaldynamics.Duct16", 6),
    "thermaldynamics.ItemDuct": ("ThermalDynamics:thermaldynamics.Duct32", 0),
    "thermaldynamics.ItemDuctEnder": ("ThermalDynamics:thermaldynamics.Duct32", 4),
    "thermaldynamics.ItemDuctFlux": ("ThermalDynamics:thermaldynamics.Duct32", 6),
    "thermaldynamics.StructuralDuct": ("ThermalDynamics:thermaldynamics.Duct48", 0),
    "thermaldynamics.TransportDuct": ("ThermalDynamics:thermaldynamics.Duct64", 0),
    "thermaldynamics.TransportDuctLongRange": ("ThermalDynamics:thermaldynamics.Duct64", 1),
    "thermaldynamics.TransportDuctCrossover": ("ThermalDynamics:thermaldynamics.Duct64", 2),
}


def get_block_mapping(block_id: str, metadata: int = 0) -> BlockMapping | None:
    """Zwróć mapowanie dla danego block_id + metadata."""
    return STATIC_MAPPINGS.get((block_id, metadata))


def get_mapping_for_te_id(te_id: str, metadata: int | None = None) -> BlockMapping | None:
    """Zwróć mapowanie na podstawie TileEntity ID z NBT."""
    key = TE_ID_TO_BLOCK.get(te_id)
    if not key:
        return None
    block_id, default_meta = key
    effective_meta = default_meta if metadata in (None, 0) else metadata
    return STATIC_MAPPINGS.get((block_id, effective_meta))


def is_thermal_dynamics_block(block_id: str) -> bool:
    return block_id.startswith("ThermalDynamics:")


def is_thermal_dynamics_te(te_id: str) -> bool:
    return te_id.startswith("thermaldynamics.")
