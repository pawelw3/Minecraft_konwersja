"""Block-only converter for Thermal Foundation/Expansion simple blocks."""

from __future__ import annotations

from converters.common.block_only import BlockOnlyResult, Position, explicit_fallback, normalize_metadata
from converters.thermal.mappings import get_mapping


FAKE_AIR = {
    "ThermalExpansion:FakeAirSignal",
    "ThermalExpansion:FakeAirLight",
    "ThermalExpansion:FakeAirForce",
    "ThermalExpansion:FakeAirBarrier",
}


def convert_block_only(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: Position = (0, 0, 0),
) -> BlockOnlyResult:
    del numeric_id, position
    meta = normalize_metadata(metadata)
    if not (registry_name.startswith("ThermalFoundation:") or registry_name.startswith("ThermalExpansion:")):
        return BlockOnlyResult.fail(f"TH-BO-E-NOT-THERMAL: {registry_name}")
    if registry_name in FAKE_AIR:
        return explicit_fallback("minecraft:air", f"TH-BO-W-FAKE-AIR-REMOVED: {registry_name}", confidence="high")

    mapping = get_mapping(registry_name, meta)
    if mapping is None:
        return explicit_fallback("minecraft:stone", f"TH-BO-W-FALLBACK-UNKNOWN: {registry_name}:{meta}")
    if mapping.has_block_entity:
        return BlockOnlyResult.fail(
            f"TH-BO-E-REQUIRES-BLOCK-ENTITY: {registry_name}:{meta}",
            warnings=["Thermal block has BE/NBT mapping and is outside block-only"],
        )
    warnings = [f"TH-BO-W-MAPPED: {mapping.notes}"] if mapping.notes else []
    confidence = "medium" if warnings else "high"
    if registry_name.startswith("ThermalFoundation:Fluid"):
        confidence = "low"
        warnings.append("TH-BO-W-FLUID-STATE-REVIEW")
    return BlockOnlyResult.ok(mapping.target_block_id, confidence=confidence, warnings=warnings)
