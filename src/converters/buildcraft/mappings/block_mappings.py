"""
Mapowania bloków BuildCraft 1.7.10 -> 1.18.2.

BuildCraft 1.7.10 używa pełnych ścieżek klas jako TileEntity ID:
  net.minecraft.src.buildcraft.transport.GenericPipe
  net.minecraft.src.buildcraft.energy.TileEngineWood
  ...

W 1.18.2 target mody:
  - Pipez (rury)
  - Thermal Expansion (silniki, refinery)
  - Mekanism (tank, pump)
  - REMOVE (assembly table, laser, integration table, zone plan)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BlockMapping:
    """Mapowanie pojedynczego bloku/TE BuildCraft."""
    te_id_1710: str
    block_id_1182: str
    te_id_1182: str | None = None
    action: str = "CONVERT"  # CONVERT, REMOVE
    nbt_converter: str = "identity"
    blockstate_props: dict[str, str] = field(default_factory=dict)
    notes: str = ""


# ──────────────────────────────────────────────────────────────────────────────
# Główne mapowania BuildCraft TE -> 1.18.2
# ──────────────────────────────────────────────────────────────────────────────

TE_ID_TO_MAPPING: dict[str, BlockMapping] = {
    # Silniki
    "net.minecraft.src.buildcraft.energy.TileEngineWood": BlockMapping(
        te_id_1710="net.minecraft.src.buildcraft.energy.TileEngineWood",
        block_id_1182="minecraft:air",
        action="REMOVE",
        notes="Redstone Engine -> zbyt slaby, brak odpowiednika",
    ),
    "net.minecraft.src.buildcraft.energy.TileEngineStone": BlockMapping(
        te_id_1710="net.minecraft.src.buildcraft.energy.TileEngineStone",
        block_id_1182="thermal:dynamo_stirling",
        te_id_1182="thermal:tile_dynamo_stirling",
        nbt_converter="engine_stone",
        notes="Stirling Engine -> Thermal Steam Dynamo",
    ),
    "net.minecraft.src.buildcraft.energy.TileEngineIron": BlockMapping(
        te_id_1710="net.minecraft.src.buildcraft.energy.TileEngineIron",
        block_id_1182="thermal:dynamo_compression",
        te_id_1182="thermal:tile_dynamo_compression",
        nbt_converter="engine_iron",
        notes="Combustion Engine -> Thermal Compression Dynamo",
    ),

    # Rury
    "net.minecraft.src.buildcraft.transport.GenericPipe": BlockMapping(
        te_id_1710="net.minecraft.src.buildcraft.transport.GenericPipe",
        block_id_1182="pipez:universal_pipe",
        action="CONVERT",
        nbt_converter="pipe",
        notes="GenericPipe -> Pipez Universal Pipe (domyslnie); fluid/energy w zaleznosci od kontekstu",
    ),

    # Maszyny fabryczne
    "net.minecraft.src.buildcraft.factory.TileTank": BlockMapping(
        te_id_1710="net.minecraft.src.buildcraft.factory.TileTank",
        block_id_1182="mekanism:basic_fluid_tank",
        te_id_1182="mekanism:tile_basic_fluid_tank",
        nbt_converter="tank",
        notes="Tank -> Mekanism Basic Fluid Tank",
    ),
    "net.minecraft.src.buildcraft.factory.TilePump": BlockMapping(
        te_id_1710="net.minecraft.src.buildcraft.factory.TilePump",
        block_id_1182="mekanism:electric_pump",
        te_id_1182="mekanism:tile_electric_pump",
        nbt_converter="pump",
        notes="Pump -> Mekanism Electric Pump",
    ),
    "net.minecraft.src.buildcraft.factory.Refinery": BlockMapping(
        te_id_1710="net.minecraft.src.buildcraft.factory.Refinery",
        block_id_1182="thermal:machine_refinery",
        te_id_1182="thermal:tile_machine_refinery",
        nbt_converter="refinery",
        notes="Refinery -> Thermal Refinery (custom receptura oil->fuel wymagana)",
    ),

    # Specjalne maszyny (REMOVE)
    "net.minecraft.src.buildcraft.factory.TileAssemblyTable": BlockMapping(
        te_id_1710="net.minecraft.src.buildcraft.factory.TileAssemblyTable",
        block_id_1182="minecraft:air",
        action="REMOVE",
        notes="Assembly Table -> brak odpowiednika; inventory do wydropienia",
    ),
    "net.minecraft.src.buildcraft.factory.TileIntegrationTable": BlockMapping(
        te_id_1710="net.minecraft.src.buildcraft.factory.TileIntegrationTable",
        block_id_1182="minecraft:air",
        action="REMOVE",
        notes="Integration Table -> brak odpowiednika",
    ),
    "net.minecraft.src.buildcraft.factory.TileLaser": BlockMapping(
        te_id_1710="net.minecraft.src.buildcraft.factory.TileLaser",
        block_id_1182="minecraft:air",
        action="REMOVE",
        notes="Laser -> brak odpowiednika",
    ),
    "net.minecraft.src.buildcraft.commander.TileZonePlan": BlockMapping(
        te_id_1710="net.minecraft.src.buildcraft.commander.TileZonePlan",
        block_id_1182="minecraft:air",
        action="REMOVE",
        notes="Zone Plan -> brak odpowiednika",
    ),
    "net.minecraft.src.buildcraft.factory.TileAutoWorkbench": BlockMapping(
        te_id_1710="net.minecraft.src.buildcraft.factory.TileAutoWorkbench",
        block_id_1182="minecraft:air",
        action="REMOVE",
        notes="Auto Workbench -> brak odpowiednika",
    ),
}


def get_mapping_for_te_id(te_id: str) -> BlockMapping | None:
    """Zwraca mapowanie dla danego TileEntity ID BuildCraft."""
    return TE_ID_TO_MAPPING.get(te_id)


def is_buildcraft_te_id(te_id: str) -> bool:
    """Sprawdza czy TE ID należy do BuildCraft."""
    return te_id in TE_ID_TO_MAPPING or "buildcraft" in te_id.lower()
