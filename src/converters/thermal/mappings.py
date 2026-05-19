"""Mapowania blokow Thermal Series 1.7.10 -> 1.18.2.

Zakres: Thermal Expansion 4.1.5, Thermal Foundation 1.2.6, Thermal Dynamics 1.2.1.
Dla elementow bez odpowiednika w Thermal 1.18.2 uzywane sa funkcjonalne
odpowiedniki z Mekanism (zgodnie z decyzja projektowa).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class BlockMapping:
    source_block_id: str
    metadata: int | None
    target_block_id: str
    has_block_entity: bool = False
    nbt_converter: str = "identity"
    notes: str = ""


# Tier mapping dla storage blocks (Cell, Tank, Strongbox, Cache, Workbench)
# 0=Basic, 1=Hardened, 2=Reinforced, 3=Resonant, 4=Creative
THERMAL_TIER_BY_META = {
    0: "basic",
    1: "hardened",
    2: "reinforced",
    3: "resonant",
    4: "creative",
}

# Rockwool colors (meta -> dye color)
THERMAL_ROCKWOOL_BY_META = {
    0: "white",
    1: "orange",
    2: "magenta",
    3: "light_blue",
    4: "yellow",
    5: "lime",
    6: "pink",
    7: "gray",
    8: "light_gray",
    9: "cyan",
    10: "purple",
    11: "blue",
    12: "brown",
    13: "green",
    14: "red",
    15: "black",
}

# Thermal Foundation ores (meta -> ore type)
THERMAL_ORE_BY_META = {
    0: "copper",
    1: "tin",
    2: "silver",
    3: "lead",
    4: "nickel",
    5: "platinum",
    6: "mithril",
}

# Thermal Foundation storage blocks (meta -> material)
THERMAL_STORAGE_BY_META = {
    0: "copper",
    1: "tin",
    2: "silver",
    3: "lead",
    4: "nickel",
    5: "platinum",
    6: "mithril",
    7: "electrum",
    8: "invar",
    9: "bronze",
    10: "signalum",
    11: "lumium",
    12: "enderium",
}


# ============================================================
# STATIC MAPPINGS
# ============================================================

STATIC_MAPPINGS: dict[tuple[str, int], BlockMapping] = {
    # --------------------------------------------------------
    # Thermal Expansion: Machines
    # --------------------------------------------------------
    ("ThermalExpansion:Machine", 0): BlockMapping(
        "ThermalExpansion:Machine", 0,
        "thermal:machine_furnace", True, "machine",
        "Redstone Furnace"
    ),
    ("ThermalExpansion:Machine", 1): BlockMapping(
        "ThermalExpansion:Machine", 1,
        "thermal:machine_pulverizer", True, "machine",
        "Pulverizer"
    ),
    ("ThermalExpansion:Machine", 2): BlockMapping(
        "ThermalExpansion:Machine", 2,
        "thermal:machine_sawmill", True, "machine",
        "Sawmill"
    ),
    ("ThermalExpansion:Machine", 3): BlockMapping(
        "ThermalExpansion:Machine", 3,
        "thermal:machine_smelter", True, "machine",
        "Induction Smelter"
    ),
    ("ThermalExpansion:Machine", 4): BlockMapping(
        "ThermalExpansion:Machine", 4,
        "thermal:machine_crucible", True, "machine",
        "Magma Crucible"
    ),
    ("ThermalExpansion:Machine", 5): BlockMapping(
        "ThermalExpansion:Machine", 5,
        "thermal:machine_bottler", True, "machine",
        "Fluid Transposer -> Fluid Encapsulator"
    ),
    ("ThermalExpansion:Machine", 6): BlockMapping(
        "ThermalExpansion:Machine", 6,
        "thermal:machine_chiller", True, "machine",
        "Glacial Precipitator"
    ),
    ("ThermalExpansion:Machine", 7): BlockMapping(
        "ThermalExpansion:Machine", 7,
        "thermal:machine_extruder", True, "machine",
        "Igneous Extruder"
    ),
    ("ThermalExpansion:Machine", 8): BlockMapping(
        "ThermalExpansion:Machine", 8,
        "thermal:device_water_gen", True, "device",
        "Aqueous Accumulator -> Device Water Gen"
    ),
    ("ThermalExpansion:Machine", 9): BlockMapping(
        "ThermalExpansion:Machine", 9,
        "thermal:machine_crafter", True, "machine",
        "Sequential Fabricator"
    ),
    ("ThermalExpansion:Machine", 10): BlockMapping(
        "ThermalExpansion:Machine", 10,
        "thermal:charge_bench", True, "device",
        "Energetic Infuser -> Charge Bench"
    ),
    ("ThermalExpansion:Machine", 11): BlockMapping(
        "ThermalExpansion:Machine", 11,
        "thermal:machine_insolator", True, "machine",
        "Phytogenic Insolator"
    ),

    # --------------------------------------------------------
    # Thermal Expansion: Devices
    # --------------------------------------------------------
    ("ThermalExpansion:Device", 0): BlockMapping(
        "ThermalExpansion:Device", 0,
        "thermal:tinker_bench", True, "device",
        "Tinker's Workbench"
    ),
    ("ThermalExpansion:Device", 1): BlockMapping(
        "ThermalExpansion:Device", 1,
        "mekanism:electric_pump", True, "machine",
        "Fluid Pump -> Mekanism Electric Pump (fallback)"
    ),
    ("ThermalExpansion:Device", 2): BlockMapping(
        "ThermalExpansion:Device", 2,
        "minecraft:dispenser", True, "identity",
        "Autonomous Activator -> vanilla Dispenser (lossy fallback)"
    ),
    ("ThermalExpansion:Device", 3): BlockMapping(
        "ThermalExpansion:Device", 3,
        "thermal:device_nullifier", True, "device",
        "Terrain Smasher -> Nullifier (placeholder; no direct Mekanism equivalent for block breaker)"
    ),
    ("ThermalExpansion:Device", 4): BlockMapping(
        "ThermalExpansion:Device", 4,
        "thermal:device_collector", True, "device",
        "Vacuumulator"
    ),
    ("ThermalExpansion:Device", 5): BlockMapping(
        "ThermalExpansion:Device", 5,
        "thermal:device_nullifier", True, "device",
        "Item Nullifier"
    ),
    ("ThermalExpansion:Device", 6): BlockMapping(
        "ThermalExpansion:Device", 6,
        "thermal:item_buffer", True, "buffer",
        "Item Buffer"
    ),
    ("ThermalExpansion:Device", 7): BlockMapping(
        "ThermalExpansion:Device", 7,
        "thermal:energy_cell", True, "energy_cell",
        "Energy Cell Extender -> Energy Cell (fallback)"
    ),

    # --------------------------------------------------------
    # Thermal Expansion: Dynamos
    # --------------------------------------------------------
    ("ThermalExpansion:Dynamo", 0): BlockMapping(
        "ThermalExpansion:Dynamo", 0,
        "thermal:dynamo_stirling", True, "dynamo",
        "Steam Dynamo"
    ),
    ("ThermalExpansion:Dynamo", 1): BlockMapping(
        "ThermalExpansion:Dynamo", 1,
        "thermal:dynamo_magmatic", True, "dynamo",
        "Magmatic Dynamo"
    ),
    ("ThermalExpansion:Dynamo", 2): BlockMapping(
        "ThermalExpansion:Dynamo", 2,
        "thermal:dynamo_compression", True, "dynamo",
        "Compression Dynamo"
    ),
    ("ThermalExpansion:Dynamo", 3): BlockMapping(
        "ThermalExpansion:Dynamo", 3,
        "thermal:dynamo_compression", True, "dynamo",
        "Reactant Dynamo -> Compression Dynamo (fallback; no direct Thermal equivalent)"
    ),
    ("ThermalExpansion:Dynamo", 4): BlockMapping(
        "ThermalExpansion:Dynamo", 4,
        "thermal:dynamo_lapidary", True, "dynamo",
        "Enervation Dynamo -> Lapidary Dynamo (fallback; consumes gems instead of energy items)"
    ),

    # --------------------------------------------------------
    # Thermal Expansion: Storage (tiered)
    # --------------------------------------------------------
    ("ThermalExpansion:Cell", 0): BlockMapping(
        "ThermalExpansion:Cell", 0,
        "thermal:energy_cell", True, "energy_cell",
        "Energy Cell (tier in blockstate/NBT)"
    ),
    ("ThermalExpansion:Tank", 0): BlockMapping(
        "ThermalExpansion:Tank", 0,
        "thermal:fluid_cell", True, "fluid_cell",
        "Portable Tank -> Fluid Cell (tier in blockstate/NBT)"
    ),
    ("ThermalExpansion:Strongbox", 0): BlockMapping(
        "ThermalExpansion:Strongbox", 0,
        "thermal:item_cell", True, "item_cell",
        "Strongbox -> Item Cell (lossy; Item Cell stores 1 type, Strongbox was general chest)"
    ),
    ("ThermalExpansion:Cache", 0): BlockMapping(
        "ThermalExpansion:Cache", 0,
        "thermal:item_cell", True, "item_cell",
        "Cache -> Item Cell (functional; both store single item type in large quantity)"
    ),
    ("ThermalExpansion:Workbench", 0): BlockMapping(
        "ThermalExpansion:Workbench", 0,
        "thermal:tinker_bench", True, "tinker_bench",
        "Tinker's Workbench"
    ),

    # --------------------------------------------------------
    # Thermal Expansion: Special
    # --------------------------------------------------------
    ("ThermalExpansion:Tesseract", 0): BlockMapping(
        "ThermalExpansion:Tesseract", 0,
        "mekanism:quantum_entangloporter", True, "frequency",
        "Tesseract -> Quantum Entangloporter (Mekanism fallback; transports energy/fluid/item/gas across dimensions)"
    ),

    # --------------------------------------------------------
    # Thermal Expansion: Plates (most lack direct equivalents)
    # --------------------------------------------------------
    ("ThermalExpansion:Plate", 0): BlockMapping(
        "ThermalExpansion:Plate", 0,
        "thermal:machine_frame", False, "identity",
        "Plate Frame -> Machine Frame (decorative fallback)"
    ),
    ("ThermalExpansion:Plate", 1): BlockMapping(
        "ThermalExpansion:Plate", 1,
        "thermal:charge_bench", True, "device",
        "Flux Charger -> Charge Bench"
    ),
    ("ThermalExpansion:Plate", 2): BlockMapping(
        "ThermalExpansion:Plate", 2,
        "minecraft:piston", False, "identity",
        "Excursion Plate -> Piston (lossy fallback)"
    ),
    ("ThermalExpansion:Plate", 3): BlockMapping(
        "ThermalExpansion:Plate", 3,
        "minecraft:slime_block", False, "identity",
        "Impulse Plate -> Slime Block (lossy fallback)"
    ),
    ("ThermalExpansion:Plate", 4): BlockMapping(
        "ThermalExpansion:Plate", 4,
        "minecraft:observer", False, "identity",
        "Signal Plate -> Observer (lossy fallback)"
    ),
    ("ThermalExpansion:Plate", 5): BlockMapping(
        "ThermalExpansion:Plate", 5,
        "mekanism:teleporter", True, "frequency",
        "Teleport Plate -> Mekanism Teleporter (fallback)"
    ),
    ("ThermalExpansion:Plate", 6): BlockMapping(
        "ThermalExpansion:Plate", 6,
        "minecraft:sticky_piston", False, "identity",
        "Translocation Plate -> Sticky Piston (lossy fallback)"
    ),

    # --------------------------------------------------------
    # Thermal Expansion: Simple blocks
    # --------------------------------------------------------
    ("ThermalExpansion:Frame", 0): BlockMapping(
        "ThermalExpansion:Frame", 0,
        "thermal:machine_frame", False, "identity",
        "Machine Frame"
    ),
    ("ThermalExpansion:Glass", 0): BlockMapping(
        "ThermalExpansion:Glass", 0,
        "thermal:obsidian_glass", False, "identity",
        "Hardened Glass -> Obsidian Glass"
    ),
    ("ThermalExpansion:Rockwool", 0): BlockMapping(
        "ThermalExpansion:Rockwool", 0,
        "thermal:white_rockwool", False, "rockwool",
        "Rockwool (color in blockstate)"
    ),
    ("ThermalExpansion:Sponge", 0): BlockMapping(
        "ThermalExpansion:Sponge", 0,
        "minecraft:sponge", False, "identity",
        "Sponge -> vanilla Sponge"
    ),
    ("ThermalExpansion:Sponge", 1): BlockMapping(
        "ThermalExpansion:Sponge", 1,
        "minecraft:wet_sponge", False, "identity",
        "Magmatic Sponge -> wet Sponge (lossy fallback)"
    ),
    ("ThermalExpansion:Sponge", 2): BlockMapping(
        "ThermalExpansion:Sponge", 2,
        "minecraft:sponge", False, "identity",
        "Creative Sponge -> vanilla Sponge"
    ),
    ("ThermalExpansion:Light", 0): BlockMapping(
        "ThermalExpansion:Light", 0,
        "minecraft:glowstone", False, "identity",
        "Glowstone Illuminator -> Glowstone"
    ),
    ("ThermalExpansion:Light", 1): BlockMapping(
        "ThermalExpansion:Light", 1,
        "minecraft:air", False, "identity",
        "LightFalse -> Air (technical block, remove)"
    ),

    # Air blocks (technical)
    ("ThermalExpansion:AirSignal", 0): BlockMapping(
        "ThermalExpansion:AirSignal", 0, "minecraft:air", False, "identity", "Technical"
    ),
    ("ThermalExpansion:AirLight", 0): BlockMapping(
        "ThermalExpansion:AirLight", 0, "minecraft:air", False, "identity", "Technical"
    ),
    ("ThermalExpansion:AirForce", 0): BlockMapping(
        "ThermalExpansion:AirForce", 0, "minecraft:air", False, "identity", "Technical"
    ),
    ("ThermalExpansion:AirBarrier", 0): BlockMapping(
        "ThermalExpansion:AirBarrier", 0, "minecraft:air", False, "identity", "Technical"
    ),

    # --------------------------------------------------------
    # Thermal Foundation: Ores
    # --------------------------------------------------------
    ("ThermalFoundation:Ore", 0): BlockMapping(
        "ThermalFoundation:Ore", 0, "thermal:copper_ore", False, "identity"
    ),
    ("ThermalFoundation:Ore", 1): BlockMapping(
        "ThermalFoundation:Ore", 1, "thermal:tin_ore", False, "identity"
    ),
    ("ThermalFoundation:Ore", 2): BlockMapping(
        "ThermalFoundation:Ore", 2, "thermal:silver_ore", False, "identity"
    ),
    ("ThermalFoundation:Ore", 3): BlockMapping(
        "ThermalFoundation:Ore", 3, "thermal:lead_ore", False, "identity"
    ),
    ("ThermalFoundation:Ore", 4): BlockMapping(
        "ThermalFoundation:Ore", 4, "thermal:nickel_ore", False, "identity"
    ),
    ("ThermalFoundation:Ore", 5): BlockMapping(
        "ThermalFoundation:Ore", 5, "thermal:cinnabar_ore", False, "identity",
        "Platinum -> Cinnabar (ore redistribution in Thermal 1.18.2)"
    ),
    ("ThermalFoundation:Ore", 6): BlockMapping(
        "ThermalFoundation:Ore", 6, "thermal:sapphire_ore", False, "identity",
        "Mithril -> Sapphire (ore redistribution)"
    ),

    # --------------------------------------------------------
    # Thermal Foundation: Storage blocks
    # --------------------------------------------------------
    ("ThermalFoundation:Storage", 0): BlockMapping(
        "ThermalFoundation:Storage", 0, "thermal:copper_block", False, "identity"
    ),
    ("ThermalFoundation:Storage", 1): BlockMapping(
        "ThermalFoundation:Storage", 1, "thermal:tin_block", False, "identity"
    ),
    ("ThermalFoundation:Storage", 2): BlockMapping(
        "ThermalFoundation:Storage", 2, "thermal:silver_block", False, "identity"
    ),
    ("ThermalFoundation:Storage", 3): BlockMapping(
        "ThermalFoundation:Storage", 3, "thermal:lead_block", False, "identity"
    ),
    ("ThermalFoundation:Storage", 4): BlockMapping(
        "ThermalFoundation:Storage", 4, "thermal:nickel_block", False, "identity"
    ),
    ("ThermalFoundation:Storage", 5): BlockMapping(
        "ThermalFoundation:Storage", 5, "thermal:electrum_block", False, "identity",
        "Platinum -> Electrum (redistribution)"
    ),
    ("ThermalFoundation:Storage", 6): BlockMapping(
        "ThermalFoundation:Storage", 6, "thermal:invar_block", False, "identity",
        "Mithril -> Invar (redistribution)"
    ),
    ("ThermalFoundation:Storage", 7): BlockMapping(
        "ThermalFoundation:Storage", 7, "thermal:electrum_block", False, "identity"
    ),
    ("ThermalFoundation:Storage", 8): BlockMapping(
        "ThermalFoundation:Storage", 8, "thermal:invar_block", False, "identity"
    ),
    ("ThermalFoundation:Storage", 9): BlockMapping(
        "ThermalFoundation:Storage", 9, "thermal:bronze_block", False, "identity"
    ),
    ("ThermalFoundation:Storage", 10): BlockMapping(
        "ThermalFoundation:Storage", 10, "thermal:signalum_block", False, "identity"
    ),
    ("ThermalFoundation:Storage", 11): BlockMapping(
        "ThermalFoundation:Storage", 11, "thermal:lumium_block", False, "identity"
    ),
    ("ThermalFoundation:Storage", 12): BlockMapping(
        "ThermalFoundation:Storage", 12, "thermal:enderium_block", False, "identity"
    ),
}


# ============================================================
# TILE ENTITY ID -> (BLOCK_ID, META) dla lookup z NBT
# ============================================================

TE_ID_TO_BLOCK_META: dict[str, tuple[str, int]] = {
    # Machines
    "thermalexpansion.Furnace": ("ThermalExpansion:Machine", 0),
    "thermalexpansion.Pulverizer": ("ThermalExpansion:Machine", 1),
    "thermalexpansion.Sawmill": ("ThermalExpansion:Machine", 2),
    "thermalexpansion.Smelter": ("ThermalExpansion:Machine", 3),
    "thermalexpansion.Crucible": ("ThermalExpansion:Machine", 4),
    "thermalexpansion.Transposer": ("ThermalExpansion:Machine", 5),
    "thermalexpansion.Precipitator": ("ThermalExpansion:Machine", 6),
    "thermalexpansion.Extruder": ("ThermalExpansion:Machine", 7),
    "thermalexpansion.Accumulator": ("ThermalExpansion:Machine", 8),
    "thermalexpansion.Assembler": ("ThermalExpansion:Machine", 9),
    "thermalexpansion.Charger": ("ThermalExpansion:Machine", 10),
    "thermalexpansion.Insolator": ("ThermalExpansion:Machine", 11),
    # Devices
    "thermalexpansion.Workbench": ("ThermalExpansion:Device", 0),
    "thermalexpansion.Pump": ("ThermalExpansion:Device", 1),
    "thermalexpansion.Activator": ("ThermalExpansion:Device", 2),
    "thermalexpansion.Breaker": ("ThermalExpansion:Device", 3),
    "thermalexpansion.Collector": ("ThermalExpansion:Device", 4),
    "thermalexpansion.Nullifier": ("ThermalExpansion:Device", 5),
    "thermalexpansion.Buffer": ("ThermalExpansion:Device", 6),
    "thermalexpansion.Extender": ("ThermalExpansion:Device", 7),
    # Dynamos
    "thermalexpansion.DynamoSteam": ("ThermalExpansion:Dynamo", 0),
    "thermalexpansion.DynamoMagmatic": ("ThermalExpansion:Dynamo", 1),
    "thermalexpansion.DynamoCompression": ("ThermalExpansion:Dynamo", 2),
    "thermalexpansion.DynamoReactant": ("ThermalExpansion:Dynamo", 3),
    "thermalexpansion.DynamoEnervation": ("ThermalExpansion:Dynamo", 4),
    # Storage
    "thermalexpansion.Cell": ("ThermalExpansion:Cell", 0),
    "thermalexpansion.CellCreative": ("ThermalExpansion:Cell", 4),
    "thermalexpansion.Tank": ("ThermalExpansion:Tank", 0),
    "thermalexpansion.TankCreative": ("ThermalExpansion:Tank", 4),
    "thermalexpansion.Strongbox": ("ThermalExpansion:Strongbox", 0),
    "thermalexpansion.StrongboxCreative": ("ThermalExpansion:Strongbox", 4),
    "thermalexpansion.Cache": ("ThermalExpansion:Cache", 0),
    "thermalexpansion.NewWorkbench": ("ThermalExpansion:Workbench", 0),
    "thermalexpansion.WorkbenchCreative": ("ThermalExpansion:Workbench", 4),
    # Special
    "thermalexpansion.Tesseract": ("ThermalExpansion:Tesseract", 0),
    "thermalexpansion.Light": ("ThermalExpansion:Light", 0),
    "thermalexpansion.LightFalse": ("ThermalExpansion:Light", 1),
    "thermalexpansion.Sponge": ("ThermalExpansion:Sponge", 0),
    "thermalexpansion.SpongeMagmatic": ("ThermalExpansion:Sponge", 1),
    "thermalexpansion.SpongeCreative": ("ThermalExpansion:Sponge", 2),
    # Plates
    "cofh.thermalexpansion.PlateFrame": ("ThermalExpansion:Plate", 0),
    "cofh.thermalexpansion.PlateCharger": ("ThermalExpansion:Plate", 1),
    "cofh.thermalexpansion.PlateExcursion": ("ThermalExpansion:Plate", 2),
    "cofh.thermalexpansion.PlateImpulse": ("ThermalExpansion:Plate", 3),
    "cofh.thermalexpansion.PlateSignal": ("ThermalExpansion:Plate", 4),
    "cofh.thermalexpansion.PlateTeleporter": ("ThermalExpansion:Plate", 5),
    "cofh.thermalexpansion.PlateTranslocate": ("ThermalExpansion:Plate", 6),
    # Thermal Dynamics
    "thermaldynamics.FluxDuct": ("ThermalDynamics:FluxDuct", 0),
    "thermaldynamics.FluxDuctSuperConductor": ("ThermalDynamics:FluxDuct", 1),
    "thermaldynamics.FluidDuct": ("ThermalDynamics:FluidDuct", 0),
    "thermaldynamics.FluidDuctFragile": ("ThermalDynamics:FluidDuct", 1),
    "thermaldynamics.FluidDuctFlux": ("ThermalDynamics:FluidDuct", 2),
    "thermaldynamics.FluidDuctSuper": ("ThermalDynamics:FluidDuct", 3),
    "thermaldynamics.ItemDuct": ("ThermalDynamics:ItemDuct", 0),
    "thermaldynamics.ItemDuctEnder": ("ThermalDynamics:ItemDuct", 1),
    "thermaldynamics.ItemDuctFlux": ("ThermalDynamics:ItemDuct", 2),
    "thermaldynamics.StructuralDuct": ("ThermalDynamics:StructuralDuct", 0),
    "thermaldynamics.TransportDuct": ("ThermalDynamics:TransportDuct", 0),
    "thermaldynamics.TransportDuctLongRange": ("ThermalDynamics:TransportDuct", 1),
    "thermaldynamics.TransportDuctCrossover": ("ThermalDynamics:TransportDuct", 2),
}


# ============================================================
# DUCT MAPPINGS (Thermal Dynamics 1.7.10 -> 1.18.2 / Mekanism)
# ============================================================

DUCT_MAPPINGS: dict[tuple[str, int], BlockMapping] = {
    ("ThermalDynamics:FluxDuct", 0): BlockMapping(
        "ThermalDynamics:FluxDuct", 0,
        "thermal:energy_duct", True, "duct_energy",
        "Leadstone Fluxduct -> Energy Duct"
    ),
    ("ThermalDynamics:FluxDuct", 1): BlockMapping(
        "ThermalDynamics:FluxDuct", 1,
        "thermal:energy_duct", True, "duct_energy",
        "Super-Lamina Fluxduct -> Energy Duct (tier lost)"
    ),
    ("ThermalDynamics:FluidDuct", 0): BlockMapping(
        "ThermalDynamics:FluidDuct", 0,
        "thermal:fluid_duct", True, "duct_fluid",
        "Temperate Fluiduct"
    ),
    ("ThermalDynamics:FluidDuct", 1): BlockMapping(
        "ThermalDynamics:FluidDuct", 1,
        "thermal:fluid_duct", True, "duct_fluid",
        "Fluiduct Fragile -> Fluid Duct"
    ),
    ("ThermalDynamics:FluidDuct", 2): BlockMapping(
        "ThermalDynamics:FluidDuct", 2,
        "thermal:fluid_duct", True, "duct_fluid",
        "Flux-Plated Fluiduct -> Fluid Duct"
    ),
    ("ThermalDynamics:FluidDuct", 3): BlockMapping(
        "ThermalDynamics:FluidDuct", 3,
        "thermal:fluid_duct_windowed", True, "duct_fluid",
        "Super-Laminar Fluiduct -> Windowed Fluid Duct"
    ),
    ("ThermalDynamics:ItemDuct", 0): BlockMapping(
        "ThermalDynamics:ItemDuct", 0,
        "thermal:item_buffer", True, "item_buffer",
        "Itemduct -> Item Buffer (lossy; no item duct in 1.18.2 Thermal)"
    ),
    ("ThermalDynamics:ItemDuct", 1): BlockMapping(
        "ThermalDynamics:ItemDuct", 1,
        "mekanism:basic_logistical_transporter", True, "transporter",
        "Ender Itemduct -> Mekanism Logistical Transporter (fallback)"
    ),
    ("ThermalDynamics:ItemDuct", 2): BlockMapping(
        "ThermalDynamics:ItemDuct", 2,
        "thermal:item_buffer", True, "item_buffer",
        "Flux-Plated Itemduct -> Item Buffer"
    ),
    ("ThermalDynamics:StructuralDuct", 0): BlockMapping(
        "ThermalDynamics:StructuralDuct", 0,
        "thermal:machine_frame", False, "identity",
        "Structuralduct -> Machine Frame (decorative)"
    ),
    ("ThermalDynamics:TransportDuct", 0): BlockMapping(
        "ThermalDynamics:TransportDuct", 0,
        "minecraft:rail", False, "identity",
        "Viaduct -> Rail (lossy fallback)"
    ),
    ("ThermalDynamics:TransportDuct", 1): BlockMapping(
        "ThermalDynamics:TransportDuct", 1,
        "minecraft:rail", False, "identity",
        "Long-Range Viaduct -> Rail"
    ),
    ("ThermalDynamics:TransportDuct", 2): BlockMapping(
        "ThermalDynamics:TransportDuct", 2,
        "minecraft:rail", False, "identity",
        "Viaduct Crossover -> Rail"
    ),
}


# ============================================================
# FLUID MAPPINGS (Thermal Foundation 1.7.10 -> 1.18.2)
# ============================================================

FLUID_MAPPINGS: dict[str, str] = {
    "fluidRedstone": "thermal:redstone",
    "fluidGlowstone": "thermal:glowstone",
    "fluidEnder": "thermal:ender",
    "fluidPyrotheum": "thermal:pyrotheum",
    "fluidCryotheum": "thermal:cryotheum",
    "fluidAerotheum": "thermal:aerotheum",
    "fluidPetrotheum": "thermal:petrotheum",
    "fluidMana": "thermal:mana",
    "fluidSteam": "thermal:steam",
    "fluidCoal": "thermal:creosote",
}


def get_mapping(block_id: str, metadata: int = 0) -> BlockMapping | None:
    """Pobiera mapping dla danego bloku i metadata."""
    key = (block_id, metadata)
    # Najpierw sprawdz static mappings
    if key in STATIC_MAPPINGS:
        return STATIC_MAPPINGS[key]
    # Dla storage blocks z tierem (meta 0-4) uzywamy meta 0 mapping
    if metadata in range(5) and (block_id, 0) in STATIC_MAPPINGS:
        mapping = STATIC_MAPPINGS[(block_id, 0)]
        # Zwroc z zachowaniem oryginalnego metadata w notes
        return BlockMapping(
            source_block_id=block_id,
            metadata=metadata,
            target_block_id=mapping.target_block_id,
            has_block_entity=mapping.has_block_entity,
            nbt_converter=mapping.nbt_converter,
            notes=f"{mapping.notes} (tier={THERMAL_TIER_BY_META.get(metadata, metadata)})"
        )
    # Dla ductow (direct names)
    if key in DUCT_MAPPINGS:
        return DUCT_MAPPINGS[key]

    # Dla ThermalDynamics sub-blokow (1.7.10 map format: ThermalDynamics_0, _16, _32, _48, _64)
    if block_id.startswith("ThermalDynamics:ThermalDynamics_"):
        try:
            offset = int(block_id.split("_")[-1])
        except ValueError:
            offset = 0
        global_meta = offset + metadata
        # Map global meta to logical block+meta
        # Energy (0-7)
        if 0 <= global_meta <= 7:
            # 0,1 = mapped; 2,4,6 = higher tiers -> energy_duct; 3,5,7 = empty/crafting -> ignore
            if global_meta in (0, 1, 2, 4, 6):
                return BlockMapping(
                    block_id, metadata,
                    "thermal:energy_duct", True, "duct_energy",
                    f"Energy duct global_meta={global_meta} -> energy_duct"
                )
            else:
                return BlockMapping(
                    block_id, metadata,
                    "thermal:energy_duct", True, "duct_energy",
                    f"Empty energy duct global_meta={global_meta} -> energy_duct (fallback)"
                )
        # Fluid (16-23)
        elif 16 <= global_meta <= 23:
            target = "thermal:fluid_duct_windowed" if global_meta in (22, 23) else "thermal:fluid_duct"
            return BlockMapping(
                block_id, metadata,
                target, True, "duct_fluid",
                f"Fluid duct global_meta={global_meta} -> {target}"
            )
        # Item (32-39)
        elif 32 <= global_meta <= 39:
            if global_meta in (36, 37):  # Ender itemduct
                return BlockMapping(
                    block_id, metadata,
                    "mekanism:basic_logistical_transporter", True, "transporter",
                    f"Ender itemduct global_meta={global_meta} -> Mekanism transporter"
                )
            else:
                return BlockMapping(
                    block_id, metadata,
                    "thermal:item_buffer", True, "item_buffer",
                    f"Item duct global_meta={global_meta} -> item_buffer"
                )
        # Structure (48-49)
        elif 48 <= global_meta <= 49:
            return BlockMapping(
                block_id, metadata,
                "thermal:machine_frame", False, "identity",
                f"Structural duct global_meta={global_meta} -> machine_frame"
            )
        # Transport (64-67)
        elif 64 <= global_meta <= 67:
            return BlockMapping(
                block_id, metadata,
                "minecraft:rail", False, "identity",
                f"Transport duct global_meta={global_meta} -> rail"
            )
    # Dla Rockwool
    if block_id == "ThermalExpansion:Rockwool" and metadata in THERMAL_ROCKWOOL_BY_META:
        color = THERMAL_ROCKWOOL_BY_META[metadata]
        return BlockMapping(
            block_id, metadata,
            f"thermal:{color}_rockwool", False, "rockwool"
        )
    # Dla TF ores
    if block_id == "ThermalFoundation:Ore" and metadata in THERMAL_ORE_BY_META:
        ore = THERMAL_ORE_BY_META[metadata]
        return BlockMapping(
            block_id, metadata,
            f"thermal:{ore}_ore", False, "identity"
        )
    # Dla TF storage
    if block_id == "ThermalFoundation:Storage" and metadata in THERMAL_STORAGE_BY_META:
        mat = THERMAL_STORAGE_BY_META[metadata]
        return BlockMapping(
            block_id, metadata,
            f"thermal:{mat}_block", False, "identity"
        )
    return None


def get_mapping_by_te_id(te_id: str) -> BlockMapping | None:
    """Pobiera mapping na podstawie Tile Entity ID z NBT."""
    block_meta = TE_ID_TO_BLOCK_META.get(te_id)
    if block_meta is None:
        return None
    return get_mapping(block_meta[0], block_meta[1])
