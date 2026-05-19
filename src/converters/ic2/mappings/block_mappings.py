"""Mapowania bloków IC2 1.7.10 → Industrial Reborn / FTBIC / Placeholder 1.18.2.

Strategia (Tier-1 first):
1. Industrial Reborn (indreb) – główny target, FE, najbliższy 1:1
2. FTB Industrial Contraptions (ftbic) – uzupełnienie braków indreb
3. Mekanism / Thermal – tylko jeśli brak w Tier-1
4. Placeholder – ostateczność

Źródła:
- docs/ANALIZA_MODOW_SZCZEGOLOWA.md (sekcja 3.6)
- Kod źródłowy IC2 2.2.827 (dekompilacja)
- Zweryfikowane blockstates z pobranych JARów (mod_src/118/mod_jars/candidates/)

Kluczowa reguła: 1 EU → 4 FE (stosowana tylko do wartości NBT)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    from ..block_inventory import IC2_ALL_BLOCKS
except ImportError:
    IC2_ALL_BLOCKS = {}


@dataclass(frozen=True)
class BlockMapping:
    source_block_id: str
    metadata: int | None
    target_block_id: str
    has_block_entity: bool = False
    nbt_converter: str = "identity"
    notes: str = ""
    # Dodatkowe właściwości konwersji
    blockstate_props: dict[str, str] | None = None
    energy_multiplier: float = 4.0  # EU → FE


# Block IDs w IC2 (prefiks "IC2:" dodawany przez Forge)
MACHINE = "IC2:blockMachine"
MACHINE2 = "IC2:blockMachine2"
MACHINE3 = "IC2:blockMachine3"
GENERATOR = "IC2:blockGenerator"
HEAT_GENERATOR = "IC2:blockHeatGenerator"
KINETIC_GENERATOR = "IC2:blockKineticGenerator"
CABLE = "IC2:blockCable"
ELECTRIC = "IC2:blockElectric"
CHARGEPAD = "IC2:blockChargepad"
REACTOR_CHAMBER = "IC2:blockReactorChamber"
REACTOR_FLUID_PORT = "IC2:blockReactorFluidPort"
REACTOR_ACCESS_HATCH = "IC2:blockReactorAccessHatch"
REACTOR_REDSTONE_PORT = "IC2:blockReactorRedstonePort"
REACTOR_VESSEL = "IC2:blockreactorvessel"
PERSONAL = "IC2:blockPersonal"
LUMINATOR = "IC2:blockLuminator"
LUMINATOR_DARK = "IC2:blockLuminatorDark"

# Placeholder block (z common/placeholders.py)
PLACEHOLDER_BLOCK = "conversion_placeholders:block_entity_placeholder"


# ============================================================
# MAPOWANIA STATYCZNE – Tier-1 first (indreb → ftbic → Mek/Thermal)
# ============================================================

STATIC_MAPPINGS: dict[tuple[str, int], BlockMapping] = {
    # --- BlockMachine ---
    (MACHINE, 0): BlockMapping(MACHINE, 0, "indreb:basic_machine_casing", False, "identity", "Machine Block"),
    (MACHINE, 1): BlockMapping(MACHINE, 1, "indreb:iron_furnace", True, "generic_machine", "Iron Furnace"),
    (MACHINE, 2): BlockMapping(MACHINE, 2, "indreb:electric_furnace", True, "standard_machine", "Electric Furnace"),
    (MACHINE, 3): BlockMapping(MACHINE, 3, "indreb:crusher", True, "standard_machine", "Macerator → Crusher"),
    (MACHINE, 4): BlockMapping(MACHINE, 4, "indreb:extractor", True, "standard_machine", "Extractor"),
    (MACHINE, 5): BlockMapping(MACHINE, 5, "indreb:compressor", True, "standard_machine", "Compressor"),
    (MACHINE, 6): BlockMapping(MACHINE, 6, "indreb:canning_machine", True, "standard_machine", "Canning Machine"),
    (MACHINE, 7): BlockMapping(MACHINE, 7, PLACEHOLDER_BLOCK, True, "placeholder", "Miner - brak odpowiednika w Tier-1"),
    (MACHINE, 8): BlockMapping(MACHINE, 8, "ftbic:pump", True, "generic_machine", "Pump (ftbic)"),
    (MACHINE, 9): BlockMapping(MACHINE, 9, PLACEHOLDER_BLOCK, True, "placeholder", "Magnetizer - unikalny IC2, brak odpowiednika"),
    (MACHINE, 10): BlockMapping(MACHINE, 10, PLACEHOLDER_BLOCK, True, "placeholder", "Electrolyzer - brak w Tier-1"),
    (MACHINE, 11): BlockMapping(MACHINE, 11, "indreb:recycler", True, "standard_machine", "Recycler"),
    (MACHINE, 12): BlockMapping(MACHINE, 12, "indreb:advanced_machine_casing", False, "identity", "Advanced Machine Block"),
    (MACHINE, 13): BlockMapping(MACHINE, 13, "indreb:electric_furnace", True, "standard_machine", "Induction Furnace → Electric Furnace (lossy)"),
    (MACHINE, 14): BlockMapping(MACHINE, 14, "ftbic:antimatter_constructor", True, "generic_machine", "Mass Fabricator → Antimatter Constructor (ftbic)"),
    (MACHINE, 15): BlockMapping(MACHINE, 15, PLACEHOLDER_BLOCK, True, "placeholder", "Terraformer - brak odpowiednika"),

    # --- BlockMachine2 ---
    (MACHINE2, 0): BlockMapping(MACHINE2, 0, "ftbic:teleporter", True, "teleporter", "Teleporter (ftbic)"),
    (MACHINE2, 1): BlockMapping(MACHINE2, 1, PLACEHOLDER_BLOCK, True, "placeholder", "Tesla Coil - brak odpowiednika"),
    (MACHINE2, 2): BlockMapping(MACHINE2, 2, PLACEHOLDER_BLOCK, True, "placeholder", "Crop-Matron - brak odpowiednika w Tier-1"),
    (MACHINE2, 3): BlockMapping(MACHINE2, 3, PLACEHOLDER_BLOCK, True, "placeholder", "Thermal Centrifuge - brak w Tier-1"),
    (MACHINE2, 4): BlockMapping(MACHINE2, 4, "indreb:extruder", True, "standard_machine", "Metal Former → Extruder (lossy)"),
    (MACHINE2, 5): BlockMapping(MACHINE2, 5, PLACEHOLDER_BLOCK, True, "placeholder", "Ore Washing Plant - brak w Tier-1"),
    (MACHINE2, 6): BlockMapping(MACHINE2, 6, PLACEHOLDER_BLOCK, True, "placeholder", "Pattern Storage - brak odpowiednika"),
    (MACHINE2, 7): BlockMapping(MACHINE2, 7, PLACEHOLDER_BLOCK, True, "placeholder", "Scanner - brak odpowiednika"),
    (MACHINE2, 8): BlockMapping(MACHINE2, 8, PLACEHOLDER_BLOCK, True, "placeholder", "Replicator - brak odpowiednika"),
    (MACHINE2, 9): BlockMapping(MACHINE2, 9, "indreb:canning_machine", True, "standard_machine", "Solid Canner → Canning Machine"),
    (MACHINE2, 10): BlockMapping(MACHINE2, 10, "indreb:canning_machine", True, "standard_machine", "Fluid Bottler → Canning Machine"),
    (MACHINE2, 11): BlockMapping(MACHINE2, 11, "ftbic:quarry", True, "generic_machine", "Advanced Miner → Quarry (ftbic, lossy)"),
    (MACHINE2, 12): BlockMapping(MACHINE2, 12, PLACEHOLDER_BLOCK, True, "placeholder", "Liquid Heat Exchanger - brak odpowiednika"),
    (MACHINE2, 13): BlockMapping(MACHINE2, 13, "indreb:fermenter", True, "standard_machine", "Fermenter"),
    (MACHINE2, 14): BlockMapping(MACHINE2, 14, PLACEHOLDER_BLOCK, True, "placeholder", "Fluid Regulator - brak odpowiednika"),
    (MACHINE2, 15): BlockMapping(MACHINE2, 15, PLACEHOLDER_BLOCK, True, "placeholder", "Condenser - brak odpowiednika"),

    # --- BlockMachine3 ---
    (MACHINE3, 0): BlockMapping(MACHINE3, 0, PLACEHOLDER_BLOCK, True, "placeholder", "Steam Generator - brak w Tier-1"),
    (MACHINE3, 1): BlockMapping(MACHINE3, 1, "indreb:iron_furnace", True, "generic_machine", "Blast Furnace → Iron Furnace (lossy)"),
    (MACHINE3, 2): BlockMapping(MACHINE3, 2, "indreb:sawmill", True, "standard_machine", "Block Cutter → Sawmill"),
    (MACHINE3, 3): BlockMapping(MACHINE3, 3, PLACEHOLDER_BLOCK, True, "placeholder", "Solar Distiller - brak odpowiednika"),
    (MACHINE3, 4): BlockMapping(MACHINE3, 4, PLACEHOLDER_BLOCK, True, "placeholder", "Fluid Distributor - brak odpowiednika"),
    (MACHINE3, 5): BlockMapping(MACHINE3, 5, PLACEHOLDER_BLOCK, True, "placeholder", "Sorting Machine - brak odpowiednika"),
    (MACHINE3, 6): BlockMapping(MACHINE3, 6, PLACEHOLDER_BLOCK, True, "placeholder", "Item Buffer - brak odpowiednika (rozważ Modular Routers)"),
    (MACHINE3, 7): BlockMapping(MACHINE3, 7, PLACEHOLDER_BLOCK, True, "placeholder", "Crop Harvester - brak odpowiednika (rozważ Industrial Foregoing)"),
    (MACHINE3, 8): BlockMapping(MACHINE3, 8, PLACEHOLDER_BLOCK, True, "placeholder", "Lathe - brak w Tier-1"),

    # --- BlockGenerator ---
    (GENERATOR, 0): BlockMapping(GENERATOR, 0, "indreb:generator", True, "generator", "Generator"),
    (GENERATOR, 1): BlockMapping(GENERATOR, 1, "indreb:geo_generator", True, "generator", "Geothermal Generator"),
    (GENERATOR, 2): BlockMapping(GENERATOR, 2, PLACEHOLDER_BLOCK, True, "placeholder", "Water Mill - brak w Tier-1 (rozważ Create/IE)"),
    (GENERATOR, 3): BlockMapping(GENERATOR, 3, "indreb:solar_generator", True, "generator", "Solar Panel"),
    (GENERATOR, 4): BlockMapping(GENERATOR, 4, "ftbic:wind_mill", True, "generator", "Wind Mill (ftbic)"),
    (GENERATOR, 5): BlockMapping(GENERATOR, 5, "ftbic:nuclear_reactor", True, "placeholder", "Nuclear Reactor (ftbic) - wymaga ręcznej konfiguracji"),
    (GENERATOR, 6): BlockMapping(GENERATOR, 6, PLACEHOLDER_BLOCK, True, "placeholder", "RT Generator - brak odpowiednika"),
    (GENERATOR, 7): BlockMapping(GENERATOR, 7, "indreb:semifluid_generator", True, "generator", "Semifluid Generator"),
    (GENERATOR, 8): BlockMapping(GENERATOR, 8, PLACEHOLDER_BLOCK, True, "placeholder", "Stirling Generator - brak w Tier-1"),
    (GENERATOR, 9): BlockMapping(GENERATOR, 9, PLACEHOLDER_BLOCK, True, "placeholder", "Kinetic Generator - brak odpowiednika"),

    # --- BlockHeatGenerator ---
    (HEAT_GENERATOR, 0): BlockMapping(HEAT_GENERATOR, 0, PLACEHOLDER_BLOCK, True, "placeholder", "Electric Heat Generator - brak odpowiednika"),
    (HEAT_GENERATOR, 1): BlockMapping(HEAT_GENERATOR, 1, PLACEHOLDER_BLOCK, True, "placeholder", "Fluid Heat Generator - brak w Tier-1"),
    (HEAT_GENERATOR, 2): BlockMapping(HEAT_GENERATOR, 2, PLACEHOLDER_BLOCK, True, "placeholder", "RT Heat Generator - brak odpowiednika"),
    (HEAT_GENERATOR, 3): BlockMapping(HEAT_GENERATOR, 3, PLACEHOLDER_BLOCK, True, "placeholder", "Solid Heat Generator - brak w Tier-1"),

    # --- BlockKineticGenerator --- (wszystkie placeholder)
    (KINETIC_GENERATOR, 0): BlockMapping(KINETIC_GENERATOR, 0, PLACEHOLDER_BLOCK, True, "placeholder", "Electric Kinetic Generator"),
    (KINETIC_GENERATOR, 1): BlockMapping(KINETIC_GENERATOR, 1, PLACEHOLDER_BLOCK, True, "placeholder", "Manual Kinetic Generator"),
    (KINETIC_GENERATOR, 2): BlockMapping(KINETIC_GENERATOR, 2, PLACEHOLDER_BLOCK, True, "placeholder", "Steam Kinetic Generator"),
    (KINETIC_GENERATOR, 3): BlockMapping(KINETIC_GENERATOR, 3, PLACEHOLDER_BLOCK, True, "placeholder", "Stirling Kinetic Generator"),
    (KINETIC_GENERATOR, 4): BlockMapping(KINETIC_GENERATOR, 4, PLACEHOLDER_BLOCK, True, "placeholder", "Water Kinetic Generator"),
    (KINETIC_GENERATOR, 5): BlockMapping(KINETIC_GENERATOR, 5, PLACEHOLDER_BLOCK, True, "placeholder", "Wind Kinetic Generator"),

    # --- BlockCable --- (Industrial Reborn ma praktycznie wszystkie kable IC2)
    (CABLE, 0): BlockMapping(CABLE, 0, "indreb:copper_cable_insulated", True, "cable", "Insulated Copper Cable"),
    (CABLE, 1): BlockMapping(CABLE, 1, "indreb:copper_cable", True, "cable", "Copper Cable"),
    (CABLE, 2): BlockMapping(CABLE, 2, "indreb:gold_cable", True, "cable", "Gold Cable"),
    (CABLE, 3): BlockMapping(CABLE, 3, "indreb:gold_cable_insulated", True, "cable", "Insulated Gold Cable"),
    (CABLE, 4): BlockMapping(CABLE, 4, "indreb:gold_cable_insulated", True, "cable", "Double Insulated Gold Cable"),
    (CABLE, 5): BlockMapping(CABLE, 5, "indreb:hv_cable", True, "cable", "Iron Cable (HV)"),
    (CABLE, 6): BlockMapping(CABLE, 6, "indreb:hv_cable_insulated", True, "cable", "Insulated Iron Cable"),
    (CABLE, 7): BlockMapping(CABLE, 7, "indreb:hv_cable_insulated", True, "cable", "Double Insulated Iron Cable"),
    (CABLE, 8): BlockMapping(CABLE, 8, "indreb:hv_cable_insulated", True, "cable", "Triple Insulated Iron Cable"),
    (CABLE, 9): BlockMapping(CABLE, 9, "indreb:glass_fibre_cable", True, "cable", "Glass Fibre Cable"),
    (CABLE, 10): BlockMapping(CABLE, 10, "indreb:copper_cable", True, "cable", "Tin Cable → Copper Cable"),
    (CABLE, 11): BlockMapping(CABLE, 11, "indreb:glass_fibre_cable", True, "lossy_cable", "Detector Cable → Glass Fibre (funkcja detekcji tracona)"),
    (CABLE, 12): BlockMapping(CABLE, 12, "indreb:glass_fibre_cable", True, "lossy_cable", "Splitter Cable → Glass Fibre (funkcja przełączania tracona)"),
    (CABLE, 13): BlockMapping(CABLE, 13, "indreb:copper_cable_insulated", True, "cable", "Insulated Tin Cable → Insulated Copper"),

    # --- BlockElectric (storage + transformatory) ---
    (ELECTRIC, 0): BlockMapping(ELECTRIC, 0, "indreb:battery_box", True, "energy_storage", "BatBox"),
    (ELECTRIC, 1): BlockMapping(ELECTRIC, 1, "indreb:mfe", True, "energy_storage", "MFE"),
    (ELECTRIC, 2): BlockMapping(ELECTRIC, 2, "indreb:mfsu", True, "energy_storage", "MFSU"),
    (ELECTRIC, 3): BlockMapping(ELECTRIC, 3, "indreb:lv_transformer", True, "transformer", "LV Transformer"),
    (ELECTRIC, 4): BlockMapping(ELECTRIC, 4, "indreb:mv_transformer", True, "transformer", "MV Transformer"),
    (ELECTRIC, 5): BlockMapping(ELECTRIC, 5, "indreb:hv_transformer", True, "transformer", "HV Transformer"),
    (ELECTRIC, 6): BlockMapping(ELECTRIC, 6, "indreb:ev_transformer", True, "transformer", "EV Transformer"),
    (ELECTRIC, 7): BlockMapping(ELECTRIC, 7, "indreb:cesu", True, "energy_storage", "CESU"),

    # --- BlockChargepad ---
    (CHARGEPAD, 0): BlockMapping(CHARGEPAD, 0, "indreb:charge_pad_battery_box", True, "energy_storage", "BatBox Chargepad"),
    (CHARGEPAD, 1): BlockMapping(CHARGEPAD, 1, "indreb:charge_pad_cesu", True, "energy_storage", "CESU Chargepad"),
    (CHARGEPAD, 2): BlockMapping(CHARGEPAD, 2, "indreb:charge_pad_mfe", True, "energy_storage", "MFE Chargepad"),
    (CHARGEPAD, 3): BlockMapping(CHARGEPAD, 3, "indreb:charge_pad_mfsu", True, "energy_storage", "MFSU Chargepad"),

    # --- Reactor ---
    (REACTOR_CHAMBER, 0): BlockMapping(REACTOR_CHAMBER, 0, PLACEHOLDER_BLOCK, True, "placeholder", "Reactor Chamber - zachowaj strukturę ręcznie (ftbic ma nuclear_reactor_chamber, ale struktura może się różnić)"),
    (REACTOR_FLUID_PORT, 0): BlockMapping(REACTOR_FLUID_PORT, 0, PLACEHOLDER_BLOCK, True, "placeholder", "Reactor Fluid Port - zachowaj strukturę ręcznie"),
    (REACTOR_ACCESS_HATCH, 0): BlockMapping(REACTOR_ACCESS_HATCH, 0, PLACEHOLDER_BLOCK, True, "placeholder", "Reactor Access Hatch - zachowaj strukturę ręcznie"),
    (REACTOR_REDSTONE_PORT, 0): BlockMapping(REACTOR_REDSTONE_PORT, 0, PLACEHOLDER_BLOCK, True, "placeholder", "Reactor Redstone Port - brak odpowiednika"),
    (REACTOR_VESSEL, 0): BlockMapping(REACTOR_VESSEL, 0, PLACEHOLDER_BLOCK, False, "identity", "Reactor Pressure Vessel - zachowaj strukturę ręcznie"),

    # --- BlockPersonal ---
    (PERSONAL, 0): BlockMapping(PERSONAL, 0, PLACEHOLDER_BLOCK, True, "placeholder", "Personal Safe - brak odpowiednika w Tier-1"),
    (PERSONAL, 1): BlockMapping(PERSONAL, 1, PLACEHOLDER_BLOCK, True, "placeholder", "Trade-O-Mat - brak odpowiednika"),
    (PERSONAL, 2): BlockMapping(PERSONAL, 2, PLACEHOLDER_BLOCK, True, "placeholder", "Energy-O-Mat - brak odpowiednika"),

    # --- Luminatory ---
    (LUMINATOR, 0): BlockMapping(LUMINATOR, 0, "indreb:luminator", True, "identity", "Luminator (active)"),
    (LUMINATOR_DARK, 0): BlockMapping(LUMINATOR_DARK, 0, "indreb:luminator", True, "identity", "Luminator (dark) → Luminator"),
}


# ============================================================
# MAPOWANIA RUD I DEKORACJI – Tier-1 first
# ============================================================

RESOURCE_MAPPINGS: dict[tuple[str, int], BlockMapping] = {
    ("IC2:blockOreCopper", 0): BlockMapping("IC2:blockOreCopper", 0, "minecraft:copper_ore", False, "identity", "Ruda miedzi (vanilla 1.18.2)"),
    ("IC2:blockOreTin", 0): BlockMapping("IC2:blockOreTin", 0, "indreb:deepslate_tin_ore", False, "identity", "Ruda cyny (indreb)"),
    ("IC2:blockOreUran", 0): BlockMapping("IC2:blockOreUran", 0, "indreb:deepslate_uranium_ore", False, "identity", "Ruda uranu (indreb)"),
    ("IC2:blockOreLead", 0): BlockMapping("IC2:blockOreLead", 0, "indreb:deepslate_lead_ore", False, "identity", "Ruda ołowiu (indreb)"),
    ("IC2:blockRubWood", 0): BlockMapping("IC2:blockRubWood", 0, "indreb:rubber_log", False, "identity", "Rubber Wood (indreb)"),
    ("IC2:blockRubLeaves", 0): BlockMapping("IC2:blockRubLeaves", 0, "indreb:rubber_leaves", False, "identity", "Rubber Leaves (indreb)"),
    ("IC2:blockRubSapling", 0): BlockMapping("IC2:blockRubSapling", 0, "indreb:rubber_sapling", False, "identity", "Rubber Sapling (indreb)"),
    ("IC2:blockAlloy", 0): BlockMapping("IC2:blockAlloy", 0, "indreb:reinforced_stone", False, "identity", "Reinforced Stone (indreb)"),
    ("IC2:blockAlloyGlass", 0): BlockMapping("IC2:blockAlloyGlass", 0, "indreb:reinforced_glass", False, "identity", "Reinforced Glass (indreb)"),
    ("IC2:blockBasalt", 0): BlockMapping("IC2:blockBasalt", 0, "minecraft:basalt", False, "identity", "Basalt (vanilla)"),
    ("IC2:blockMetal", 0): BlockMapping("IC2:blockMetal", 0, "indreb:bronze_block", False, "identity", "Bronze Block (indreb)"),
    ("IC2:blockMetal", 1): BlockMapping("IC2:blockMetal", 1, "minecraft:copper_block", False, "identity", "Copper Block (vanilla 1.18.2)"),
    ("IC2:blockMetal", 2): BlockMapping("IC2:blockMetal", 2, "indreb:tin_block", False, "identity", "Tin Block (indreb)"),
    ("IC2:blockMetal", 3): BlockMapping("IC2:blockMetal", 3, "ftbic:uranium_block", False, "identity", "Uranium Block (ftbic)"),
    ("IC2:blockMetal", 4): BlockMapping("IC2:blockMetal", 4, "ftbic:lead_block", False, "identity", "Lead Block (ftbic)"),
    ("IC2:blockMetal", 5): BlockMapping("IC2:blockMetal", 5, "thermal:steel_block", False, "identity", "Steel Block (Thermal, brak w Tier-1)"),
}


# Połączone mapowania
ALL_MAPPINGS = {**STATIC_MAPPINGS, **RESOURCE_MAPPINGS}


def get_block_mapping(block_id: str, metadata: int) -> BlockMapping | None:
    """Zwraca mapowanie dla bloku IC2 lub None."""
    key = (block_id, metadata)
    mapping = ALL_MAPPINGS.get(key)
    if mapping:
        return mapping
    # Spróbuj wildcard (dowolne metadata)
    key_wildcard = (block_id, None)
    return ALL_MAPPINGS.get(key_wildcard)


def get_mapping_for_te_id(te_id: str) -> BlockMapping | None:
    """Próbuje znaleźć mapowanie na podstawie TileEntity ID (class name).
    
    Uwaga: W IC2 1.7.10 TE ID to nazwa klasy lub string rejestracyjny.
    """
    # Mapowanie odwrotne TE → block
    for (block_id, meta), mapping in ALL_MAPPINGS.items():
        info = IC2_ALL_BLOCKS.get(block_id, {}).get(meta if meta is not None else 0, {})
        if info.get("te_class") == te_id:
            return mapping
    return None


def is_ic2_block(block_id: str) -> bool:
    return block_id.startswith("IC2:")


def list_placeholder_mappings() -> list[BlockMapping]:
    """Zwraca listę wszystkich mapowań prowadzących do placeholdera."""
    return [m for m in ALL_MAPPINGS.values() if m.target_block_id == PLACEHOLDER_BLOCK]


def list_tier1_real_mappings() -> list[BlockMapping]:
    """Zwraca listę mapowań na realne bloki Tier-1 (indreb/ftbic)."""
    tier1_prefixes = ("indreb:", "ftbic:")
    return [m for m in ALL_MAPPINGS.values() if m.target_block_id.startswith(tier1_prefixes)]


if __name__ == "__main__":
    total = len(ALL_MAPPINGS)
    placeholders = len(list_placeholder_mappings())
    tier1 = len(list_tier1_real_mappings())
    print(f"Liczba mapowań: {total}")
    print(f"Liczba placeholderów: {placeholders}")
    print(f"Tier-1 real blocks (indreb/ftbic): {tier1}")
    print(f"Stopień konwersji real-block: {((total - placeholders) / total * 100):.1f}%")
    print(f"Stopień konwersji Tier-1: {(tier1 / total * 100):.1f}%")
    print("\nPlaceholdery:")
    for m in list_placeholder_mappings():
        print(f"  {m.source_block_id}:{m.metadata} — {m.notes}")
