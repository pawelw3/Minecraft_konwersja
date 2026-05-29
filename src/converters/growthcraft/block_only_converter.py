"""Block-only converter for GrowthCraft 1.7.10 simple blocks.

The current client pack does not include GrowthCraft 1.18.2, so this converter
uses vanilla-safe fallbacks for simple crops/plants/decorative blocks.
"""

from __future__ import annotations

from converters.common.block_only import BlockOnlyResult, Position, explicit_fallback, normalize_metadata


REQUIRES_TE_FAMILIES = {
    "grc.fruitPress",
    "grc.fruitPresser",
    "grc.brewKettle",
    "grc.fermentBarrel",
    "grc.fermentJar",
    "grc.beeBox",
    "grc.fishTrap",
    "grcmilk.ButterChurn",
    "grcmilk.CheesePress",
    "grcmilk.CheeseVat",
    "grcmilk.Pancheon",
}

FAMILY_TARGETS = {
    "grc.fenceRope": "minecraft:oak_fence",
    "grc.ropeBlock": "minecraft:chain",
    "grccore.salt_block": "minecraft:white_concrete",
    "grc.netherBrickFenceRope": "minecraft:nether_brick_fence",
    "grc.appleSapling": "minecraft:oak_sapling",
    "grc.appleLeaves": "minecraft:oak_leaves",
    "grc.appleBlock": "minecraft:red_wool",
    "grc.bambooBlock": "minecraft:oak_planks",
    "grc.bambooShoot": "minecraft:bamboo",
    "grc.bambooStalk": "minecraft:bamboo",
    "grc.bambooLeaves": "minecraft:jungle_leaves",
    "grc.bambooFence": "minecraft:oak_fence",
    "grc.bambooFenceRope": "minecraft:oak_fence",
    "grc.bambooStairs": "minecraft:oak_stairs",
    "grc.bambooSingleSlab": "minecraft:oak_slab",
    "grc.bambooDoubleSlab": "minecraft:oak_planks",
    "grc.bambooDoor": "minecraft:oak_door",
    "grc.bambooFenceGate": "minecraft:oak_fence_gate",
    "grc.bambooScaffold": "minecraft:scaffolding",
    "grc.bambooWall": "minecraft:oak_fence",
    "grc.beeHive": "minecraft:bee_nest",
    "grc.grapeVine0": "minecraft:vine",
    "grc.grapeVine1": "minecraft:vine",
    "grc.grapeLeaves": "minecraft:oak_leaves",
    "grc.grapeBlock": "minecraft:purple_wool",
    "grc.hopVine": "minecraft:vine",
    "grcmilk.Thistle": "minecraft:fern",
    "grc.riceBlock": "minecraft:wheat",
    "grc.paddyField": "minecraft:farmland",
}


def convert_block_only(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: Position = (0, 0, 0),
) -> BlockOnlyResult:
    del numeric_id, position
    meta = normalize_metadata(metadata)
    if not registry_name.startswith("Growthcraft"):
        return BlockOnlyResult.fail(f"GRC-BO-E-NOT-GROWTHCRAFT: {registry_name}")

    family = _family(registry_name)
    if family in REQUIRES_TE_FAMILIES:
        return BlockOnlyResult.fail(
            f"GRC-BO-E-REQUIRES-BLOCK-ENTITY: {registry_name}:{meta}",
            warnings=["block must be handled by GrowthCraft TE/NBT converter"],
        )

    target = FAMILY_TARGETS.get(family)
    if target:
        return explicit_fallback(
            target,
            f"GRC-BO-W-VANILLA-FALLBACK: {family}:{meta}",
            confidence="low",
        )

    if "Fluid" in family or "Fluid." in family:
        return BlockOnlyResult.fail(
            f"GRC-BO-E-FLUID-OUT-OF-SCOPE: {registry_name}:{meta}",
            warnings=["fluid blocks require a separate fluid conversion policy"],
        )

    return explicit_fallback(
        "minecraft:oak_planks",
        f"GRC-BO-W-FALLBACK-UNKNOWN: {registry_name}:{meta}",
    )


def _family(registry_name: str) -> str:
    return registry_name.split(":", 1)[1] if ":" in registry_name else registry_name
