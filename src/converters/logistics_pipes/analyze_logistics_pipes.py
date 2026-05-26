"""Step 1 inventory for Logistics Pipes conversion.

This script does not touch the source world. It records the block and Tile
Entity surface that later conversion steps must handle for Logistics Pipes
1.7.10 and its planned Pretty Pipes replacement layer.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class BlockEntry:
    version: str
    registry: str
    java_class: str
    metadata: str
    description: str
    target_hint: str


@dataclass(frozen=True)
class TileEntityEntry:
    version: str
    registry: str
    java_class: str
    has_mod_prefix: bool
    block_registry: str
    metadata: str
    description: str
    target_hint: str


LP_1710_BLOCKS = [
    BlockEntry(
        "1.7.10",
        "LogisticsPipes:logisticsPipeBlock",
        "logisticspipes.pipes.basic.LogisticsBlockGenericPipe",
        "pipe type is stored in the embedded CoreUnroutedPipe, not block metadata",
        "Common container block for all Logistics Pipes pipe variants, including item pipes, fluid pipes and the request table.",
        "prettypipes:pipe plus modules, or AE2/XNet reconstruction for complex networks",
    ),
    BlockEntry(
        "1.7.10",
        "LogisticsPipes:logisticsSolidBlock",
        "logisticspipes.blocks.LogisticsSolidBlock",
        "0=soldering, 1=power junction, 2=security, 3=autocrafting, 4=fuzzy crafting, 5=statistics, 11=RF provider, 12=IC2 provider",
        "Solid utility block family for power, security, crafting tables, statistics and soldering station.",
        "case-by-case: AE2/Pretty Pipes/manual report; power/security mostly non-portable",
    ),
]


LP_1710_TILE_ENTITIES = [
    TileEntityEntry(
        "1.7.10",
        "logisticspipes.pipes.basic.LogisticsTileGenericPipe",
        "logisticspipes.pipes.basic.LogisticsTileGenericPipe",
        True,
        "LogisticsPipes:logisticsPipeBlock",
        "all pipe item variants",
        "Stores and ticks the actual pipe object, BuildCraft/Thermal Dynamics connections, pluggables, render state and routed item/fluid behavior.",
        "prettypipes:pipe with module inventory where recoverable; otherwise network report",
    ),
    TileEntityEntry(
        "1.7.10",
        "logisticspipes.blocks.LogisticsSolderingTileEntity",
        "logisticspipes.blocks.LogisticsSolderingTileEntity",
        True,
        "LogisticsPipes:logisticsSolidBlock",
        "meta 0",
        "GUI crafting station used by Logistics Pipes recipes.",
        "no direct target; convert to placeholder/report unless needed for decorative preservation",
    ),
    TileEntityEntry(
        "1.7.10",
        "logisticspipes.blocks.powertile.LogisticsPowerJuntionTileEntity",
        "logisticspipes.blocks.powertile.LogisticsPowerJunctionTileEntity",
        True,
        "LogisticsPipes:logisticsSolidBlock",
        "meta 1",
        "Internal Logistics Pipes power buffer. Registry string contains the original typo 'Juntion'.",
        "no direct Pretty Pipes equivalent; likely drop/report or replace with energy infrastructure marker",
    ),
    TileEntityEntry(
        "1.7.10",
        "logisticspipes.blocks.LogisticsSecurityTileEntity",
        "logisticspipes.blocks.LogisticsSecurityTileEntity",
        True,
        "LogisticsPipes:logisticsSolidBlock",
        "meta 2",
        "Security station with ID card inventory, UUID authorization and ComputerCraft/OpenComputers permission settings.",
        "manual report; no direct Pretty Pipes equivalent",
    ),
    TileEntityEntry(
        "1.7.10",
        "logisticspipes.blocks.crafting.LogisticsCraftingTableTileEntity",
        "logisticspipes.blocks.crafting.LogisticsCraftingTableTileEntity",
        True,
        "LogisticsPipes:logisticsSolidBlock",
        "meta 3 or 4",
        "Autocrafting/fuzzy crafting table used by LP crafting recipes and pipe integration.",
        "AE2 pattern provider / Pretty Pipes crafting module reconstruction candidate",
    ),
    TileEntityEntry(
        "1.7.10",
        "logisticspipes.blocks.stats.LogisticsStatisticsTileEntity",
        "logisticspipes.blocks.stats.LogisticsStatisticsTileEntity",
        True,
        "LogisticsPipes:logisticsSolidBlock",
        "meta 5",
        "Statistics table for LP network/item information.",
        "manual report or remove; no direct target block",
    ),
    TileEntityEntry(
        "1.7.10",
        "logisticspipes.blocks.powertile.LogisticsRFPowerProviderTileEntity",
        "logisticspipes.blocks.powertile.LogisticsRFPowerProviderTileEntity",
        True,
        "LogisticsPipes:logisticsSolidBlock",
        "meta 11",
        "RF/CoFH power provider with local energy storage and conversion into LP power.",
        "no direct Pretty Pipes equivalent; Pretty Pipes pressurizer consumes FE directly",
    ),
    TileEntityEntry(
        "1.7.10",
        "logisticspipes.blocks.powertile.LogisticsIC2PowerProviderTileEntity",
        "logisticspipes.blocks.powertile.LogisticsIC2PowerProviderTileEntity",
        True,
        "LogisticsPipes:logisticsSolidBlock",
        "meta 12",
        "IC2 EU power provider for LP power networks.",
        "no direct target; report as IC2/energy migration issue",
    ),
]


LP_1710_PIPE_ITEMS = [
    "PipeItemsBasicLogistics",
    "PipeItemsRequestLogistics",
    "PipeItemsRequestLogisticsMk2",
    "PipeItemsProviderLogistics",
    "PipeItemsProviderLogisticsMk2",
    "PipeItemsCraftingLogistics",
    "PipeItemsCraftingLogisticsMk2",
    "PipeItemsCraftingLogisticsMk3",
    "PipeItemsSatelliteLogistics",
    "PipeItemsSupplierLogistics",
    "PipeLogisticsChassiMk1",
    "PipeLogisticsChassiMk2",
    "PipeLogisticsChassiMk3",
    "PipeLogisticsChassiMk4",
    "PipeLogisticsChassiMk5",
    "PipeItemsRemoteOrdererLogistics",
    "PipeItemsInvSysConnector",
    "PipeItemsSystemEntranceLogistics",
    "PipeItemsSystemDestinationLogistics",
    "PipeItemsFirewall",
    "PipeItemsApiaristAnalyser",
    "PipeItemsApiaristSink",
    "PipeFluidBasic",
    "PipeFluidRequestLogistics",
    "PipeFluidProvider",
    "PipeFluidSatellite",
    "PipeItemsFluidSupplier",
    "PipeFluidSupplierMk2",
    "PipeFluidInsertion",
    "PipeFluidExtractor",
    "PipeBlockRequestTable",
    "PipeItemsBasicTransport",
]


PRETTY_PIPES_BLOCKS = [
    BlockEntry("replacement-source", "prettypipes:pipe", "de.ellpeck.prettypipes.pipe.PipeBlock", "blockstate directions; modules in BE", "Base item pipe; behavior comes from installed modules.", "primary target for simple LP routed pipes"),
    BlockEntry("replacement-source", "prettypipes:item_terminal", "de.ellpeck.prettypipes.terminal.ItemTerminalBlock", "n/a", "Terminal for requesting/inserting items from the pipe network.", "target role for LP request pipe/request table networks"),
    BlockEntry("replacement-source", "prettypipes:crafting_terminal", "de.ellpeck.prettypipes.terminal.CraftingTerminalBlock", "n/a", "Item terminal with crafting grid behavior.", "target role for LP request table convenience, not full LP autocraft"),
    BlockEntry("replacement-source", "prettypipes:pressurizer", "de.ellpeck.prettypipes.pressurizer.PressurizerBlock", "n/a", "FE-powered pipe accelerator.", "functional replacement for LP power-speed support, not a power-junction conversion"),
]


PRETTY_PIPES_BLOCK_ENTITIES = [
    TileEntityEntry("replacement-source", "prettypipes:pipe", "de.ellpeck.prettypipes.pipe.PipeBlockEntity", True, "prettypipes:pipe", "n/a", "Stores up to three modules, optional cover, priority and moving items/active crafts via PipeNetwork.", "main target for provider/supplier/crafting/filter-like pipe roles"),
    TileEntityEntry("replacement-source", "prettypipes:item_terminal", "de.ellpeck.prettypipes.terminal.ItemTerminalBlockEntity", True, "prettypipes:item_terminal", "n/a", "Terminal-side network access for item requests and insertion.", "request table/request pipe target role"),
    TileEntityEntry("replacement-source", "prettypipes:crafting_terminal", "de.ellpeck.prettypipes.terminal.CraftingTerminalBlockEntity", True, "prettypipes:crafting_terminal", "n/a", "Crafting terminal block entity for terminal GUI and network operations.", "request table convenience target role"),
    TileEntityEntry("replacement-source", "prettypipes:pressurizer", "de.ellpeck.prettypipes.pressurizer.PressurizerBlockEntity", True, "prettypipes:pressurizer", "n/a", "FE storage/consumer that pressurizes nearby pipe network item movement.", "optional replacement for powered LP networks"),
]


def build_report() -> dict[str, object]:
    return {
        "source_mod": "Logistics Pipes 0.9.3.132 for Minecraft 1.7.10",
        "target_layer": "Pretty Pipes + AE2/XNet reconstruction layer",
        "source_status": (
            "PrettyPipes replacement source is decompiled from "
            "mod_src/118/mod_jars/PrettyPipes-1.12.8.jar, the 1.18.2 Forge "
            "target. The old upstream checkout with a 1.21.1 build setup is "
            "kept as mod_src/118/actual_src/1.18.2/PrettyPipes/"
            "repo_wrong_1.21_reference and must not be used for conversion."
        ),
        "blocks_1710": [asdict(entry) for entry in LP_1710_BLOCKS],
        "tile_entities_1710": [asdict(entry) for entry in LP_1710_TILE_ENTITIES],
        "pipe_item_classes_1710": LP_1710_PIPE_ITEMS,
        "replacement_blocks": [asdict(entry) for entry in PRETTY_PIPES_BLOCKS],
        "replacement_block_entities": [asdict(entry) for entry in PRETTY_PIPES_BLOCK_ENTITIES],
    }


def main() -> None:
    output_path = Path(__file__).with_name("logistics_pipes_step1_inventory.json")
    report = build_report()
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print("Logistics Pipes step 1 inventory")
    print(f"1.7.10 blocks: {len(LP_1710_BLOCKS)}")
    print(f"1.7.10 tile entities: {len(LP_1710_TILE_ENTITIES)}")
    print(f"1.7.10 pipe item classes: {len(LP_1710_PIPE_ITEMS)}")
    print(f"replacement blocks: {len(PRETTY_PIPES_BLOCKS)}")
    print(f"replacement block entities: {len(PRETTY_PIPES_BLOCK_ENTITIES)}")
    print(f"wrote: {output_path}")


if __name__ == "__main__":
    main()
