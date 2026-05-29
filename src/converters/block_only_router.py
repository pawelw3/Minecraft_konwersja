"""Central router for direct block-only conversions."""

from __future__ import annotations

from converters.common.block_only import BlockOnlyResult, Position, explicit_fallback


def convert_block_only(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: Position = (0, 0, 0),
) -> BlockOnlyResult:
    module = _module_for(registry_name)
    if module is None:
        return explicit_fallback(
            "minecraft:stone",
            f"BO-W-UNKNOWN-MOD-BLOCK: {registry_name}:{metadata}",
        )
    return module.convert_block_only(numeric_id, registry_name, metadata, position)


def convert_block_only_to_event(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: Position = (0, 0, 0),
) -> dict | None:
    """Convert a single block to an Event JSON dict suitable for the 1.18.2 writer.

    Returns None for blocks that should be left as-is (eg. vanilla blocks handled
    by another layer) or when the router explicitly returns an empty result.
    """
    result = convert_block_only(numeric_id, registry_name, metadata, position)
    if not result.success or not result.target_block:
        return None

    event: dict = {
        "op": "set_block",
        "pos": list(position),
        "block": result.target_block,
    }
    if result.blockstate_props:
        event["blockstate"] = dict(result.blockstate_props)
    if result.warnings:
        event["warnings"] = list(result.warnings)
    if result.confidence != "medium":
        event["confidence"] = result.confidence
    return event


def _module_for(registry_name: str):
    reg = registry_name.lower()
    if reg.startswith("appliedenergistics2:"):
        from converters.ae2 import block_only_converter
        return block_only_converter
    if reg.startswith("bibliocraft:"):
        from converters.bibliocraft import block_only_converter
        return block_only_converter
    if reg.startswith("bigreactors:"):
        from converters.bigreactors import block_only_converter
        return block_only_converter
    if reg.startswith("awwayoftime:"):
        from converters.bloodmagic import block_only_converter
        return block_only_converter
    if reg.startswith("buildcraft|"):
        from converters.buildcraft import block_only_converter
        return block_only_converter
    if reg.startswith("chisel:"):
        from converters.chisel import block_only_converter
        return block_only_converter
    if reg.startswith("mekanism:"):
        from converters.mekanism import block_only_converter
        return block_only_converter
    if reg.startswith("extrautils:") or reg.startswith("extrautilities:"):
        from converters.extrautils import block_only_converter
        return block_only_converter
    if reg.startswith("ic2:"):
        from converters.ic2 import block_only_converter
        return block_only_converter
    if reg.startswith("growthcraft"):
        from converters.growthcraft import block_only_converter
        return block_only_converter
    if reg.startswith("jammyfurniture:"):
        from converters.jammyfurniture import block_only_converter
        return block_only_converter
    if reg.startswith("cfm:"):
        from converters.mrcrayfish_furniture import block_only_converter
        return block_only_converter
    if reg.startswith("openmodularturrets:"):
        from converters.openmodularturrets import block_only_converter
        return block_only_converter
    if reg.startswith("projred|"):
        from converters.projectred import block_only_converter
        return block_only_converter
    if reg.startswith("railcraft:"):
        from converters.railcraft import block_only_converter
        return block_only_converter
    if reg.startswith("xreliquary:"):
        from converters.reliquary import block_only_converter
        return block_only_converter
    if reg.startswith("thermalfoundation:") or reg.startswith("thermalexpansion:"):
        from converters.thermal import block_only_converter
        return block_only_converter
    if reg.startswith("thermaldynamics:"):
        from converters.thermal_dynamics import block_only_converter
        return block_only_converter
    if reg.startswith("tc:"):
        from converters.traincraft import block_only_converter
        return block_only_converter
    if reg.startswith("witchery:"):
        from converters.witchery import block_only_converter
        return block_only_converter
    return None
