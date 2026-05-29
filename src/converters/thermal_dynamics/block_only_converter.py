"""Conservative block-only converter for Thermal Dynamics."""

from __future__ import annotations

from converters.common.block_only import BlockOnlyResult, Position, explicit_fallback, normalize_metadata


def convert_block_only(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: Position = (0, 0, 0),
) -> BlockOnlyResult:
    del numeric_id, position
    meta = normalize_metadata(metadata)
    if not registry_name.startswith("ThermalDynamics:"):
        return BlockOnlyResult.fail(f"TD-BO-E-NOT-THERMAL-DYNAMICS: {registry_name}")
    if registry_name == "ThermalDynamics:ThermalDynamics_48" and meta in (0, 1):
        return explicit_fallback(
            "thermal:machine_frame",
            f"TD-BO-W-STRUCTURAL-DUCT-FALLBACK: meta={meta}",
            confidence="medium",
        )
    if registry_name == "ThermalDynamics:ThermalDynamics_64" and meta in (0, 1, 2):
        return explicit_fallback(
            "minecraft:rail",
            f"TD-BO-W-TRANSPORT-DUCT-FALLBACK: meta={meta}",
            confidence="low",
        )
    if registry_name == "ThermalDynamics:ThermalDynamics_64" and meta == 3:
        return explicit_fallback(
            "mekanism:teleporter_frame",
            "TD-BO-W-LOW-CONFIDENCE-DUCT64-META3",
            confidence="low",
        )
    return BlockOnlyResult.fail(
        f"TD-BO-E-REQUIRES-BLOCK-ENTITY: {registry_name}:{meta}",
        warnings=["Thermal Dynamics energy/fluid/item ducts are network/BE-owned"],
    )
