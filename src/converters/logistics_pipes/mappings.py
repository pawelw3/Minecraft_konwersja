"""Mappings for Logistics Pipes 1.7.10 conversion."""

from __future__ import annotations

from dataclasses import dataclass, field


GENERIC_PIPE_TE_ID = "logisticspipes.pipes.basic.LogisticsTileGenericPipe"

SOLID_TE_TO_KIND = {
    "logisticspipes.blocks.LogisticsSolderingTileEntity": "soldering",
    "logisticspipes.blocks.powertile.LogisticsPowerJuntionTileEntity": "power_junction",
    "logisticspipes.blocks.powertile.LogisticsPowerJunctionTileEntity": "power_junction",
    "logisticspipes.blocks.LogisticsSecurityTileEntity": "security",
    "logisticspipes.blocks.crafting.LogisticsCraftingTableTileEntity": "crafting_table",
    "logisticspipes.blocks.stats.LogisticsStatisticsTileEntity": "statistics",
    "logisticspipes.blocks.powertile.LogisticsRFPowerProviderTileEntity": "rf_power_provider",
    "logisticspipes.blocks.powertile.LogisticsIC2PowerProviderTileEntity": "ic2_power_provider",
}

CHASSIS_SLOTS_1710 = {
    "PipeLogisticsChassiMk1": 1,
    "PipeLogisticsChassiMk2": 2,
    "PipeLogisticsChassiMk3": 3,
    "PipeLogisticsChassiMk4": 4,
    "PipeLogisticsChassiMk5": 8,
}

PRETTY_PIPE_MODULE_SLOTS = 3

# Dynamic item IDs read from mapa_1710/level.dat FML ItemData for this world.
# LogisticsTileGenericPipe stores only this numeric item ID in NBT (`pipeId`).
PIPE_ID_TO_PIPE_CLASS = {
    8749: "PipeItemsBasicLogistics",
    8750: "PipeItemsRequestLogistics",
    8751: "PipeItemsProviderLogistics",
    8752: "PipeItemsCraftingLogistics",
    8753: "PipeItemsSatelliteLogistics",
    8754: "PipeItemsSupplierLogistics",
    8755: "PipeLogisticsChassiMk1",
    8756: "PipeLogisticsChassiMk2",
    8757: "PipeLogisticsChassiMk3",
    8758: "PipeLogisticsChassiMk4",
    8759: "PipeLogisticsChassiMk5",
    8760: "PipeItemsCraftingLogisticsMk2",
    8761: "PipeItemsRequestLogisticsMk2",
    8762: "PipeItemsRemoteOrdererLogistics",
    8763: "PipeItemsProviderLogisticsMk2",
    8764: "PipeItemsApiaristAnalyser",
    8765: "PipeItemsApiaristSink",
    8766: "PipeItemsInvSysConnector",
    8767: "PipeItemsSystemEntranceLogistics",
    8769: "PipeItemsCraftingLogisticsMk3",
    8770: "PipeItemsFirewall",
    8771: "PipeItemsFluidSupplier",
    8772: "PipeFluidBasic",
    8773: "PipeFluidInsertion",
    8774: "PipeFluidProvider",
    8775: "PipeFluidRequestLogistics",
    8776: "PipeFluidExtractor",
    8777: "PipeFluidSatellite",
    8778: "PipeFluidSupplierMk2",
    8779: "PipeBlockRequestTable",
    8780: "PipeItemsBasicTransport",
}

LP_MODULE_TO_PRETTY_MODULE = {
    "ModuleProvider": "prettypipes:high_extraction_module",
    "ModuleProviderMk2": "prettypipes:high_extraction_module",
    "ModuleActiveSupplier": "prettypipes:high_retrieval_module",
    "ModulePassiveSupplier": "prettypipes:low_priority_module",
    "ModuleCrafter": "prettypipes:high_crafting_module",
    "ModuleCrafterMK2": "prettypipes:high_crafting_module",
    "ModuleCrafterMK3": "prettypipes:high_crafting_module",
}


@dataclass(frozen=True)
class PipeRoleMapping:
    role: str
    target_block_id: str
    target_te_id: str | None = None
    pretty_modules: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    note: str = ""


PIPE_CLASS_MAPPINGS = {
    "PipeItemsBasicLogistics": PipeRoleMapping(
        role="basic_routed_pipe",
        target_block_id="prettypipes:pipe",
        target_te_id="prettypipes:pipe",
        note="simple routed LP pipe becomes Pretty Pipes pipe",
    ),
    "PipeItemsBasicTransport": PipeRoleMapping(
        role="basic_transport_pipe",
        target_block_id="prettypipes:pipe",
        target_te_id="prettypipes:pipe",
        note="transport-only LP pipe becomes Pretty Pipes pipe",
    ),
    "PipeItemsProviderLogistics": PipeRoleMapping(
        role="provider_pipe",
        target_block_id="prettypipes:pipe",
        target_te_id="prettypipes:pipe",
        pretty_modules=("prettypipes:high_extraction_module",),
    ),
    "PipeItemsProviderLogisticsMk2": PipeRoleMapping(
        role="provider_pipe_mk2",
        target_block_id="prettypipes:pipe",
        target_te_id="prettypipes:pipe",
        pretty_modules=("prettypipes:high_extraction_module",),
    ),
    "PipeItemsSupplierLogistics": PipeRoleMapping(
        role="supplier_pipe",
        target_block_id="prettypipes:pipe",
        target_te_id="prettypipes:pipe",
        pretty_modules=("prettypipes:high_retrieval_module",),
        warnings=("LP-W-SUPPLIER-STOCK-TARGET: supplier target stock NBT is not 1:1 in Pretty Pipes.",),
    ),
    "PipeItemsRemoteOrdererLogistics": PipeRoleMapping(
        role="remote_orderer_pipe",
        target_block_id="prettypipes:item_terminal",
        target_te_id="prettypipes:item_terminal",
        warnings=("LP-W-REMOTE-ORDERER: remote orderer pipe becomes local Pretty Pipes item terminal role.",),
    ),
    "PipeItemsRequestLogistics": PipeRoleMapping(
        role="request_pipe",
        target_block_id="prettypipes:item_terminal",
        target_te_id="prettypipes:item_terminal",
        warnings=("LP-W-REQUEST-TERMINAL: request pipe becomes a Pretty Pipes item terminal role.",),
    ),
    "PipeItemsRequestLogisticsMk2": PipeRoleMapping(
        role="request_pipe_mk2",
        target_block_id="prettypipes:item_terminal",
        target_te_id="prettypipes:item_terminal",
        warnings=("LP-W-REQUEST-TERMINAL: request pipe mk2 becomes a Pretty Pipes item terminal role.",),
    ),
    "PipeBlockRequestTable": PipeRoleMapping(
        role="request_table_pipe",
        target_block_id="prettypipes:item_terminal",
        target_te_id="prettypipes:item_terminal",
        warnings=("LP-W-REQUEST-TABLE: request table pipe becomes Pretty Pipes item terminal.",),
    ),
    "PipeItemsCraftingLogistics": PipeRoleMapping(
        role="crafting_pipe",
        target_block_id="prettypipes:pipe",
        target_te_id="prettypipes:pipe",
        pretty_modules=("prettypipes:high_crafting_module",),
        warnings=("LP-W-CRAFTING-PATTERN: crafting pattern must be verified or rebuilt.",),
    ),
    "PipeItemsCraftingLogisticsMk2": PipeRoleMapping(
        role="crafting_pipe_mk2",
        target_block_id="prettypipes:pipe",
        target_te_id="prettypipes:pipe",
        pretty_modules=("prettypipes:high_crafting_module",),
        warnings=("LP-W-CRAFTING-PATTERN: crafting pattern mk2 must be verified or rebuilt.",),
    ),
    "PipeItemsCraftingLogisticsMk3": PipeRoleMapping(
        role="crafting_pipe_mk3",
        target_block_id="prettypipes:pipe",
        target_te_id="prettypipes:pipe",
        pretty_modules=("prettypipes:high_crafting_module",),
        warnings=("LP-W-CRAFTING-MK3: mk3 buffer/advanced crafting needs manual verification.",),
    ),
    "PipeItemsSatelliteLogistics": PipeRoleMapping(
        role="satellite_pipe",
        target_block_id="prettypipes:pipe",
        target_te_id="prettypipes:pipe",
        warnings=("LP-W-SATELLITE: satellite IDs/targets must be rebuilt manually.",),
    ),
    "PipeItemsInvSysConnector": PipeRoleMapping(
        role="inventory_system_connector",
        target_block_id="prettypipes:pipe",
        target_te_id="prettypipes:pipe",
        warnings=("LP-W-INVSYS: inventory system connector has no 1:1 Pretty Pipes equivalent.",),
    ),
    "PipeItemsSystemEntranceLogistics": PipeRoleMapping(
        role="system_entrance",
        target_block_id="prettypipes:pipe",
        target_te_id="prettypipes:pipe",
        warnings=("LP-W-SYSTEM-ROUTING: entrance/destination routing must be rebuilt manually.",),
    ),
    "PipeItemsSystemDestinationLogistics": PipeRoleMapping(
        role="system_destination",
        target_block_id="prettypipes:pipe",
        target_te_id="prettypipes:pipe",
        warnings=("LP-W-SYSTEM-ROUTING: entrance/destination routing must be rebuilt manually.",),
    ),
    "PipeItemsFirewall": PipeRoleMapping(
        role="firewall_pipe",
        target_block_id="prettypipes:pipe",
        target_te_id="prettypipes:pipe",
        warnings=("LP-W-FIREWALL: LP firewall filtering/security must be rebuilt manually.",),
    ),
    "PipeItemsApiaristAnalyser": PipeRoleMapping(
        role="apiarist_analyser",
        target_block_id="prettypipes:pipe",
        target_te_id="prettypipes:pipe",
        warnings=("LP-W-APIARIST: Forestry bee-specific routing is not preserved.",),
    ),
    "PipeItemsApiaristSink": PipeRoleMapping(
        role="apiarist_sink",
        target_block_id="prettypipes:pipe",
        target_te_id="prettypipes:pipe",
        warnings=("LP-W-APIARIST: Forestry bee-specific routing is not preserved.",),
    ),
    "PipeFluidBasic": PipeRoleMapping(
        role="fluid_basic",
        target_block_id="pipez:fluid_pipe",
        warnings=("LP-W-FLUID-PIPE: Pretty Pipes core is item-only; fluid pipe routed to Pipez.",),
    ),
    "PipeFluidRequestLogistics": PipeRoleMapping(
        role="fluid_request",
        target_block_id="pipez:fluid_pipe",
        warnings=("LP-W-FLUID-REQUEST: fluid request logic is not preserved; routed to Pipez fluid pipe.",),
    ),
    "PipeFluidProvider": PipeRoleMapping(
        role="fluid_provider",
        target_block_id="pipez:fluid_pipe",
        warnings=("LP-W-FLUID-PROVIDER: fluid provider logic is not preserved; routed to Pipez fluid pipe.",),
    ),
    "PipeFluidSatellite": PipeRoleMapping(
        role="fluid_satellite",
        target_block_id="pipez:fluid_pipe",
        warnings=("LP-W-FLUID-SATELLITE: satellite target must be rebuilt manually.",),
    ),
    "PipeItemsFluidSupplier": PipeRoleMapping(
        role="fluid_supplier",
        target_block_id="pipez:fluid_pipe",
        warnings=("LP-W-FLUID-SUPPLIER: fluid supplier stockkeeping must be rebuilt manually.",),
    ),
    "PipeFluidSupplierMk2": PipeRoleMapping(
        role="fluid_supplier_mk2",
        target_block_id="pipez:fluid_pipe",
        warnings=("LP-W-FLUID-SUPPLIER: fluid supplier mk2 stockkeeping must be rebuilt manually.",),
    ),
    "PipeFluidInsertion": PipeRoleMapping(
        role="fluid_insertion",
        target_block_id="pipez:fluid_pipe",
        warnings=("LP-W-FLUID-INSERTION: insertion rules are not preserved.",),
    ),
    "PipeFluidExtractor": PipeRoleMapping(
        role="fluid_extractor",
        target_block_id="pipez:fluid_pipe",
        warnings=("LP-W-FLUID-EXTRACTOR: extraction rules are not preserved.",),
    ),
}

for chassis_class in CHASSIS_SLOTS_1710:
    PIPE_CLASS_MAPPINGS[chassis_class] = PipeRoleMapping(
        role="chassis_pipe",
        target_block_id="prettypipes:pipe",
        target_te_id="prettypipes:pipe",
        note=f"{chassis_class} module inventory is mapped with Pretty Pipes 3-slot limit",
    )


def is_logistics_pipes_te_id(te_id: str) -> bool:
    return te_id == GENERIC_PIPE_TE_ID or te_id in SOLID_TE_TO_KIND or te_id.startswith("logisticspipes.")


def get_pipe_mapping(pipe_class: str | None) -> PipeRoleMapping:
    if pipe_class and pipe_class in PIPE_CLASS_MAPPINGS:
        return PIPE_CLASS_MAPPINGS[pipe_class]
    return PipeRoleMapping(
        role="unknown_pipe",
        target_block_id="prettypipes:pipe",
        target_te_id="prettypipes:pipe",
        warnings=("LP-W-PIPE-TYPE-UNKNOWN: pipe class could not be resolved from NBT; converted as plain Pretty Pipes pipe.",),
    )


def resolve_pipe_class_from_id(pipe_id: object) -> str | None:
    try:
        return PIPE_ID_TO_PIPE_CLASS.get(int(pipe_id))
    except (TypeError, ValueError):
        return None
