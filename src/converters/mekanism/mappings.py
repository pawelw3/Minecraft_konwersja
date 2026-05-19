"""Mapowania blokow Mekanism 1.7.10 -> 1.18.2.

Zakres: Mekanism core. MekanismGenerators i MekanismTools sa celowo poza tym
modulem.
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


TIER_BY_META = {
    0: "basic",
    1: "advanced",
    2: "elite",
    3: "ultimate",
    4: "creative",
}

FACTORY_TIER_BY_META = {
    5: "basic",
    6: "advanced",
    7: "elite",
}

FACTORY_RECIPE_BY_ORDINAL = {
    0: "smelting",
    1: "enriching",
    2: "crushing",
    3: "compressing",
    4: "combining",
    5: "purifying",
    6: "injecting",
    7: "infusing",
}

MACHINE_BLOCK = "Mekanism:MachineBlock"
MACHINE_BLOCK2 = "Mekanism:MachineBlock2"
MACHINE_BLOCK3 = "Mekanism:MachineBlock3"
BASIC_BLOCK = "Mekanism:BasicBlock"
BASIC_BLOCK2 = "Mekanism:BasicBlock2"
ORE_BLOCK = "Mekanism:OreBlock"
ENERGY_CUBE = "Mekanism:EnergyCube"
GAS_TANK = "Mekanism:GasTank"
BOUNDING_BLOCK = "Mekanism:BoundingBlock"
OBSIDIAN_TNT = "Mekanism:ObsidianTNT"
PLASTIC_BLOCK = "Mekanism:PlasticBlock"
SLICK_PLASTIC_BLOCK = "Mekanism:SlickPlasticBlock"
ROAD_PLASTIC_BLOCK = "Mekanism:RoadPlasticBlock"
GLOW_PLASTIC_BLOCK = "Mekanism:GlowPlasticBlock"
REINFORCED_PLASTIC_BLOCK = "Mekanism:ReinforcedPlasticBlock"
PLASTIC_FENCE = "Mekanism:PlasticFence"
CARDBOARD_BOX = "Mekanism:CardboardBox"
SALT_BLOCK = "Mekanism:SaltBlock"


CONCRETE_BY_LEGACY_DYE_META = {
    0: "minecraft:black_concrete",
    1: "minecraft:red_concrete",
    2: "minecraft:green_concrete",
    3: "minecraft:brown_concrete",
    4: "minecraft:blue_concrete",
    5: "minecraft:purple_concrete",
    6: "minecraft:cyan_concrete",
    7: "minecraft:light_gray_concrete",
    8: "minecraft:gray_concrete",
    9: "minecraft:pink_concrete",
    10: "minecraft:lime_concrete",
    11: "minecraft:yellow_concrete",
    12: "minecraft:light_blue_concrete",
    13: "minecraft:magenta_concrete",
    14: "minecraft:orange_concrete",
    15: "minecraft:white_concrete",
}


STATIC_MAPPINGS: dict[tuple[str, int], BlockMapping] = {
    (MACHINE_BLOCK, 0): BlockMapping(MACHINE_BLOCK, 0, "mekanism:enrichment_chamber", True, "machine"),
    (MACHINE_BLOCK, 1): BlockMapping(MACHINE_BLOCK, 1, "mekanism:osmium_compressor", True, "machine"),
    (MACHINE_BLOCK, 2): BlockMapping(MACHINE_BLOCK, 2, "mekanism:combiner", True, "machine"),
    (MACHINE_BLOCK, 3): BlockMapping(MACHINE_BLOCK, 3, "mekanism:crusher", True, "machine"),
    (MACHINE_BLOCK, 4): BlockMapping(MACHINE_BLOCK, 4, "mekanism:digital_miner", True, "digital_miner"),
    (MACHINE_BLOCK, 8): BlockMapping(MACHINE_BLOCK, 8, "mekanism:metallurgic_infuser", True, "machine"),
    (MACHINE_BLOCK, 9): BlockMapping(MACHINE_BLOCK, 9, "mekanism:purification_chamber", True, "machine"),
    (MACHINE_BLOCK, 10): BlockMapping(MACHINE_BLOCK, 10, "mekanism:energized_smelter", True, "machine"),
    (MACHINE_BLOCK, 11): BlockMapping(MACHINE_BLOCK, 11, "mekanism:teleporter", True, "frequency"),
    (MACHINE_BLOCK, 12): BlockMapping(MACHINE_BLOCK, 12, "mekanism:electric_pump", True, "machine"),
    (MACHINE_BLOCK, 13): BlockMapping(MACHINE_BLOCK, 13, "mekanism:personal_chest", True, "frequency"),
    (MACHINE_BLOCK, 14): BlockMapping(MACHINE_BLOCK, 14, "mekanism:chargepad", True, "machine"),
    (MACHINE_BLOCK, 15): BlockMapping(MACHINE_BLOCK, 15, "mekanism:logistical_sorter", True, "machine"),
    (MACHINE_BLOCK2, 0): BlockMapping(MACHINE_BLOCK2, 0, "mekanism:rotary_condensentrator", True, "chemical_machine"),
    (MACHINE_BLOCK2, 1): BlockMapping(MACHINE_BLOCK2, 1, "mekanism:chemical_oxidizer", True, "chemical_machine"),
    (MACHINE_BLOCK2, 2): BlockMapping(MACHINE_BLOCK2, 2, "mekanism:chemical_infuser", True, "chemical_machine"),
    (MACHINE_BLOCK2, 3): BlockMapping(MACHINE_BLOCK2, 3, "mekanism:chemical_injection_chamber", True, "chemical_machine"),
    (MACHINE_BLOCK2, 4): BlockMapping(MACHINE_BLOCK2, 4, "mekanism:electrolytic_separator", True, "chemical_machine"),
    (MACHINE_BLOCK2, 5): BlockMapping(MACHINE_BLOCK2, 5, "mekanism:precision_sawmill", True, "machine"),
    (MACHINE_BLOCK2, 6): BlockMapping(MACHINE_BLOCK2, 6, "mekanism:chemical_dissolution_chamber", True, "chemical_machine"),
    (MACHINE_BLOCK2, 7): BlockMapping(MACHINE_BLOCK2, 7, "mekanism:chemical_washer", True, "chemical_machine"),
    (MACHINE_BLOCK2, 8): BlockMapping(MACHINE_BLOCK2, 8, "mekanism:chemical_crystallizer", True, "chemical_machine"),
    (MACHINE_BLOCK2, 9): BlockMapping(MACHINE_BLOCK2, 9, "mekanism:seismic_vibrator", True, "machine"),
    (MACHINE_BLOCK2, 10): BlockMapping(MACHINE_BLOCK2, 10, "mekanism:pressurized_reaction_chamber", True, "chemical_machine"),
    (MACHINE_BLOCK2, 12): BlockMapping(MACHINE_BLOCK2, 12, "mekanism:fluidic_plenisher", True, "machine"),
    (MACHINE_BLOCK2, 13): BlockMapping(MACHINE_BLOCK2, 13, "mekanism:laser", True, "machine"),
    (MACHINE_BLOCK2, 14): BlockMapping(MACHINE_BLOCK2, 14, "mekanism:laser_amplifier", True, "machine"),
    (MACHINE_BLOCK2, 15): BlockMapping(MACHINE_BLOCK2, 15, "mekanism:laser_tractor_beam", True, "machine"),
    (MACHINE_BLOCK3, 0): BlockMapping(MACHINE_BLOCK3, 0, "mekanism:quantum_entangloporter", True, "frequency"),
    (MACHINE_BLOCK3, 1): BlockMapping(MACHINE_BLOCK3, 1, "mekanism:solar_neutron_activator", True, "chemical_machine"),
    (MACHINE_BLOCK3, 2): BlockMapping(
        MACHINE_BLOCK3,
        2,
        "mekanism:chemical_oxidizer",
        True,
        "chemical_machine",
        "Mekanism 10.2.0/1.18.2 nie ma Ambient Accumulator; zachowuje jako istniejaca maszyna chemical z warningiem.",
    ),
    (MACHINE_BLOCK3, 3): BlockMapping(MACHINE_BLOCK3, 3, "mekanism:oredictionificator", True, "machine"),
    (MACHINE_BLOCK3, 4): BlockMapping(MACHINE_BLOCK3, 4, "mekanism:resistive_heater", True, "machine"),
    (MACHINE_BLOCK3, 5): BlockMapping(MACHINE_BLOCK3, 5, "mekanism:formulaic_assemblicator", True, "machine"),
    (MACHINE_BLOCK3, 6): BlockMapping(MACHINE_BLOCK3, 6, "mekanism:fuelwood_heater", True, "machine"),
    (BASIC_BLOCK, 0): BlockMapping(BASIC_BLOCK, 0, "mekanism:block_osmium"),
    (BASIC_BLOCK, 1): BlockMapping(BASIC_BLOCK, 1, "mekanism:block_bronze"),
    (BASIC_BLOCK, 2): BlockMapping(BASIC_BLOCK, 2, "mekanism:block_refined_obsidian"),
    (BASIC_BLOCK, 3): BlockMapping(BASIC_BLOCK, 3, "mekanism:block_charcoal"),
    (BASIC_BLOCK, 4): BlockMapping(BASIC_BLOCK, 4, "mekanism:block_refined_glowstone"),
    (BASIC_BLOCK, 5): BlockMapping(BASIC_BLOCK, 5, "mekanism:block_steel"),
    (BASIC_BLOCK, 7): BlockMapping(BASIC_BLOCK, 7, "mekanism:teleporter_frame"),
    (BASIC_BLOCK, 8): BlockMapping(BASIC_BLOCK, 8, "mekanism:steel_casing"),
    (BASIC_BLOCK, 9): BlockMapping(BASIC_BLOCK, 9, "mekanism:dynamic_tank", True, "multiblock"),
    (BASIC_BLOCK, 10): BlockMapping(BASIC_BLOCK, 10, "mekanism:structural_glass", True, "multiblock"),
    (BASIC_BLOCK, 11): BlockMapping(BASIC_BLOCK, 11, "mekanism:dynamic_valve", True, "multiblock"),
    (BASIC_BLOCK, 12): BlockMapping(BASIC_BLOCK, 12, "minecraft:copper_block", False, "identity", "Mekanism 10.2.5 nie ma copper block w core JAR; target vanilla."),
    (BASIC_BLOCK, 13): BlockMapping(BASIC_BLOCK, 13, "mekanism:block_tin"),
    (BASIC_BLOCK, 14): BlockMapping(BASIC_BLOCK, 14, "mekanism:thermal_evaporation_controller", True, "multiblock"),
    (BASIC_BLOCK, 15): BlockMapping(BASIC_BLOCK, 15, "mekanism:thermal_evaporation_valve", True, "multiblock"),
    (BASIC_BLOCK2, 0): BlockMapping(BASIC_BLOCK2, 0, "mekanism:thermal_evaporation_block", True, "multiblock"),
    (BASIC_BLOCK2, 1): BlockMapping(BASIC_BLOCK2, 1, "mekanism:induction_casing", True, "multiblock"),
    (BASIC_BLOCK2, 2): BlockMapping(BASIC_BLOCK2, 2, "mekanism:induction_port", True, "multiblock"),
    (BASIC_BLOCK2, 5): BlockMapping(BASIC_BLOCK2, 5, "mekanism:superheating_element", True, "multiblock"),
    (BASIC_BLOCK2, 6): BlockMapping(BASIC_BLOCK2, 6, "mekanism:pressure_disperser", True, "multiblock"),
    (BASIC_BLOCK2, 7): BlockMapping(BASIC_BLOCK2, 7, "mekanism:boiler_casing", True, "multiblock"),
    (BASIC_BLOCK2, 8): BlockMapping(BASIC_BLOCK2, 8, "mekanism:boiler_valve", True, "multiblock"),
    (BASIC_BLOCK2, 9): BlockMapping(BASIC_BLOCK2, 9, "mekanism:security_desk", True, "frequency"),
    (ORE_BLOCK, 0): BlockMapping(ORE_BLOCK, 0, "mekanism:osmium_ore"),
    (ORE_BLOCK, 1): BlockMapping(ORE_BLOCK, 1, "minecraft:copper_ore", False, "identity", "Mekanism 10.2.5 nie ma copper ore w core JAR; target vanilla."),
    (ORE_BLOCK, 2): BlockMapping(ORE_BLOCK, 2, "mekanism:tin_ore"),
    (SALT_BLOCK, 0): BlockMapping(SALT_BLOCK, 0, "mekanism:block_salt"),
    (BOUNDING_BLOCK, 0): BlockMapping(
        BOUNDING_BLOCK,
        0,
        "mekanism:bounding_block",
        False,
        "identity",
        "Blok pomocniczy multibloku/modelu; target jest niewidocznym bounding blockiem Mekanism 10.",
    ),
    (BOUNDING_BLOCK, 1): BlockMapping(
        BOUNDING_BLOCK,
        1,
        "mekanism:bounding_block",
        False,
        "identity",
        "Blok pomocniczy multibloku/modelu; serwer 1.18.2 nie rejestruje advanced_bounding_block, wiec zachowuje jako bounding_block.",
    ),
    (OBSIDIAN_TNT, 0): BlockMapping(
        OBSIDIAN_TNT,
        0,
        "minecraft:tnt",
        False,
        "identity",
        "Mekanism 10.2.5 nie ma Obsidian TNT; target vanilla TNT traci zwiekszona odpornosc/sile.",
    ),
}


TE_ID_TO_MAPPING_KEY: dict[str, tuple[str, int]] = {
    "EnrichmentChamber": (MACHINE_BLOCK, 0),
    "OsmiumCompressor": (MACHINE_BLOCK, 1),
    "Combiner": (MACHINE_BLOCK, 2),
    "Crusher": (MACHINE_BLOCK, 3),
    "DigitalMiner": (MACHINE_BLOCK, 4),
    "SmeltingFactory": (MACHINE_BLOCK, 5),
    "AdvancedSmeltingFactory": (MACHINE_BLOCK, 6),
    "UltimateSmeltingFactory": (MACHINE_BLOCK, 7),
    "MetallurgicInfuser": (MACHINE_BLOCK, 8),
    "PurificationChamber": (MACHINE_BLOCK, 9),
    "EnergizedSmelter": (MACHINE_BLOCK, 10),
    "MekanismTeleporter": (MACHINE_BLOCK, 11),
    "ElectricPump": (MACHINE_BLOCK, 12),
    "ElectricChest": (MACHINE_BLOCK, 13),
    "Chargepad": (MACHINE_BLOCK, 14),
    "LogisticalSorter": (MACHINE_BLOCK, 15),
    "RotaryCondensentrator": (MACHINE_BLOCK2, 0),
    "ChemicalOxidizer": (MACHINE_BLOCK2, 1),
    "ChemicalInfuser": (MACHINE_BLOCK2, 2),
    "ChemicalInjectionChamber": (MACHINE_BLOCK2, 3),
    "ElectrolyticSeparator": (MACHINE_BLOCK2, 4),
    "PrecisionSawmill": (MACHINE_BLOCK2, 5),
    "ChemicalDissolutionChamber": (MACHINE_BLOCK2, 6),
    "ChemicalWasher": (MACHINE_BLOCK2, 7),
    "ChemicalCrystallizer": (MACHINE_BLOCK2, 8),
    "SeismicVibrator": (MACHINE_BLOCK2, 9),
    "PressurizedReactionChamber": (MACHINE_BLOCK2, 10),
    "PortableTank": (MACHINE_BLOCK2, 11),
    "FluidicPlenisher": (MACHINE_BLOCK2, 12),
    "Laser": (MACHINE_BLOCK2, 13),
    "LaserAmplifier": (MACHINE_BLOCK2, 14),
    "LaserTractorBeam": (MACHINE_BLOCK2, 15),
    "EnergyCube": (ENERGY_CUBE, 0),
    "GasTank": (GAS_TANK, 0),
    "Bin": (BASIC_BLOCK, 6),
    "DynamicTank": (BASIC_BLOCK, 9),
    "DynamicValve": (BASIC_BLOCK, 11),
    "SalinationController": (BASIC_BLOCK, 14),
    "InductionPort": (BASIC_BLOCK2, 2),
    "SecurityDesk": (BASIC_BLOCK2, 9),
    "QuantumEntangloporter": (MACHINE_BLOCK3, 0),
    "SolarNeutronActivator": (MACHINE_BLOCK3, 1),
    "AmbientAccumulator": (MACHINE_BLOCK3, 2),
    "Oredictionificator": (MACHINE_BLOCK3, 3),
    "ResistiveHeater": (MACHINE_BLOCK3, 4),
    "FormulaicAssemblicator": (MACHINE_BLOCK3, 5),
    "FuelwoodHeater": (MACHINE_BLOCK3, 6),
}


def get_block_mapping(block_id: str, metadata: int = 0, nbt: dict | None = None) -> BlockMapping | None:
    if block_id in (PLASTIC_BLOCK, SLICK_PLASTIC_BLOCK, ROAD_PLASTIC_BLOCK, GLOW_PLASTIC_BLOCK, REINFORCED_PLASTIC_BLOCK):
        target = CONCRETE_BY_LEGACY_DYE_META.get(metadata)
        if target:
            variant_notes = {
                PLASTIC_BLOCK: "Mekanism 10.2.5 nie ma plastic blocks; zachowuje kolor jako concrete.",
                SLICK_PLASTIC_BLOCK: "Mekanism 10.2.5 nie ma slick plastic; zachowuje kolor jako concrete, bez sliskosci.",
                ROAD_PLASTIC_BLOCK: "Mekanism 10.2.5 nie ma road plastic; zachowuje kolor jako concrete, bez speed boost.",
                GLOW_PLASTIC_BLOCK: "Mekanism 10.2.5 nie ma glow plastic; zachowuje kolor jako concrete, bez swiecenia.",
                REINFORCED_PLASTIC_BLOCK: "Mekanism 10.2.5 nie ma reinforced plastic; zachowuje kolor jako concrete, bez zwiekszonej odpornosci.",
            }
            return BlockMapping(block_id, metadata, target, False, "identity", variant_notes[block_id])
    if block_id == PLASTIC_FENCE and 0 <= metadata <= 15:
        return BlockMapping(
            block_id,
            metadata,
            "minecraft:oak_fence",
            False,
            "identity",
            "Mekanism 10.2.5 nie ma plastic fence; zachowuje funkcje ogrodzenia, ale traci kolor/material.",
        )
    if block_id == CARDBOARD_BOX and metadata == 0:
        return BlockMapping(
            block_id,
            metadata,
            "mekanism:cardboard_box",
            True,
            "identity",
            "Cardboard Box zachowuje legacy NBT jako kandydat do rekonstrukcji packed block.",
        )
    if block_id == ENERGY_CUBE:
        tier = TIER_BY_META.get(metadata)
        if tier:
            return BlockMapping(block_id, metadata, f"mekanism:{tier}_energy_cube", True, "energy_cube")
    if block_id == GAS_TANK:
        tier = TIER_BY_META.get(metadata)
        if tier and tier != "creative":
            return BlockMapping(block_id, metadata, f"mekanism:{tier}_chemical_tank", True, "gas_tank")
    if block_id == BASIC_BLOCK and metadata == 6:
        tier = _tier_from_nbt_or_meta(nbt, metadata, default="basic")
        return BlockMapping(block_id, metadata, f"mekanism:{tier}_bin", True, "bin")
    if block_id == BASIC_BLOCK2 and metadata in (3, 4):
        tier = _tier_from_nbt_or_meta(nbt, 0, default="basic")
        suffix = "induction_cell" if metadata == 3 else "induction_provider"
        return BlockMapping(block_id, metadata, f"mekanism:{tier}_{suffix}", True, "multiblock")
    if block_id == MACHINE_BLOCK2 and metadata == 11:
        tier = _tier_from_nbt_or_meta(nbt, metadata, default="basic")
        return BlockMapping(block_id, metadata, f"mekanism:{tier}_fluid_tank", True, "fluid_tank")
    if block_id == MACHINE_BLOCK and metadata in FACTORY_TIER_BY_META:
        tier = FACTORY_TIER_BY_META[metadata]
        recipe = FACTORY_RECIPE_BY_ORDINAL.get(_int_value((nbt or {}).get("recipeType"), 0), "smelting")
        return BlockMapping(block_id, metadata, f"mekanism:{tier}_{recipe}_factory", True, "factory")
    return STATIC_MAPPINGS.get((block_id, metadata))


def get_mapping_for_te_id(te_id: str, metadata: int = 0, nbt: dict | None = None) -> BlockMapping | None:
    key = TE_ID_TO_MAPPING_KEY.get(te_id)
    if not key:
        return None
    block_id, default_meta = key
    effective_meta = metadata if block_id not in (ENERGY_CUBE, GAS_TANK) else _int_value((nbt or {}).get("tier"), metadata)
    if block_id == MACHINE_BLOCK and default_meta in FACTORY_TIER_BY_META:
        effective_meta = default_meta
    return get_block_mapping(block_id, effective_meta or default_meta, nbt)


def is_mekanism_block(block_id: str) -> bool:
    return block_id.startswith("Mekanism:") or block_id in TE_ID_TO_MAPPING_KEY


def _tier_from_nbt_or_meta(nbt: dict | None, metadata: int, default: str = "basic") -> str:
    nbt = nbt or {}
    raw = nbt.get("tier", metadata)
    if isinstance(raw, str):
        value = raw.lower()
        return value if value in ("basic", "advanced", "elite", "ultimate", "creative") else default
    return TIER_BY_META.get(_int_value(raw, 0), default)


def _int_value(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
