"""Block-only converter for Jammy Furniture blocks without inventory TE."""

from __future__ import annotations

from converters.common.block_only import BlockOnlyResult, Position, explicit_fallback, normalize_metadata
from converters.jammyfurniture.jammyfurniture_mapping import get_mapping


INSTALLED_TARGET_MODS = {"minecraft", "supplementaries", "conversion_placeholders"}
FALLBACK_BY_SOURCE = {
    "LightsOn": "minecraft:lantern",
    "LightsOff": "minecraft:lantern",
    "RoofingBlocksOne": "minecraft:brick_stairs",
    "MobHeadsOne": "minecraft:skeleton_skull",
    "MobHeadsTwo": "minecraft:skeleton_skull",
    "MobHeadsThree": "minecraft:skeleton_skull",
    "MobHeadsFour": "minecraft:skeleton_skull",
    "ArmChair": "conversion_placeholders:block_entity_placeholder",
    "SofaLeft": "conversion_placeholders:block_entity_placeholder",
    "SofaRight": "conversion_placeholders:block_entity_placeholder",
    "SofaCenter": "conversion_placeholders:block_entity_placeholder",
    "SofaCorner": "conversion_placeholders:block_entity_placeholder",
    "Bath": "minecraft:cauldron",
}


def convert_block_only(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: Position = (0, 0, 0),
) -> BlockOnlyResult:
    del numeric_id, position
    meta = normalize_metadata(metadata)
    if not registry_name.startswith("JammyFurniture:"):
        return BlockOnlyResult.fail(f"JAMMY-BO-E-NOT-JAMMY: {registry_name}")

    source_block = _source_block(registry_name)
    mapping = get_mapping(source_block, meta)
    if mapping is None:
        return _fallback(registry_name, meta, "JAMMY-BO-W-FALLBACK-UNKNOWN")

    if mapping.preserve_inventory:
        return BlockOnlyResult.fail(
            f"JAMMY-BO-E-REQUIRES-INVENTORY: {registry_name}:{meta}",
            warnings=["mapping preserves inventory and is outside block-only"],
        )

    if mapping.target_mod in INSTALLED_TARGET_MODS:
        return BlockOnlyResult.ok(
            f"{mapping.target_mod}:{mapping.target_block}",
            blockstate_props={str(k): str(v) for k, v in mapping.target_state.items()},
            confidence="medium",
            warnings=[f"JAMMY-BO-W-MAPPED: {mapping.notes}"] if mapping.notes else [],
        )

    return _fallback(
        registry_name,
        meta,
        f"JAMMY-BO-W-TARGET-MOD-NOT-IN-PACK: {mapping.target_mod}",
    )


def _source_block(registry_name: str) -> str:
    return "jammyfurniture:" + registry_name.split(":", 1)[1]


def _fallback(registry_name: str, metadata: int, warning: str) -> BlockOnlyResult:
    family = registry_name.split(":", 1)[1] if ":" in registry_name else registry_name
    target = FALLBACK_BY_SOURCE.get(family, "conversion_placeholders:block_entity_placeholder")
    return explicit_fallback(target, f"{warning}: {registry_name}:{metadata}")
