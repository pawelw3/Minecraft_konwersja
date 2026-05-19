"""Registry of IC2 NBT converters wrapping simulation functions.

Each converter maps IC2 1.7.10 TileEntity NBT to 1.18.2 BlockEntity NBT
for a specific class of blocks (machines, generators, cables, etc.).
"""

from __future__ import annotations

from typing import Any

from ..simulations.cable_simulation import simulate_cable_conversion
from ..simulations.energy_storage_simulation import simulate_energy_storage_conversion
from ..simulations.machine_simulation import (
    simulate_reactor_conversion,
    simulate_standard_machine_conversion,
    simulate_teleporter_conversion,
)
from .base_converter import BaseIC2NBTConverter, NBTConversionResult


class IdentityConverter(BaseIC2NBTConverter):
    """No-op converter for blocks that don't need NBT transformation."""

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        source_metadata: int = 0,
    ) -> NBTConversionResult:
        return NBTConversionResult(success=True)


class StandardMachineConverter(BaseIC2NBTConverter):
    """Converter for standard IC2 machines (Macerator, Extractor, Compressor, etc.)."""

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        source_metadata: int = 0,
    ) -> NBTConversionResult:
        result = simulate_standard_machine_conversion(nbt_1710, target_block_id)
        return NBTConversionResult(
            success=len(result.get("errors", [])) == 0,
            converted_nbt=result.get("nbt_1182") or None,
            blockstate_props=result.get("blockstate_props", {}),
            warnings=result.get("warnings", []),
            errors=result.get("errors", []),
        )


class GenericMachineConverter(BaseIC2NBTConverter):
    """Converter for machines with simpler NBT (Iron Furnace, Pump, etc.).

    Uses standard_machine simulation but with relaxed expectations.
    """

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        source_metadata: int = 0,
    ) -> NBTConversionResult:
        result = simulate_standard_machine_conversion(nbt_1710, target_block_id)
        # Generic machines may not have all fields; downgrade errors to warnings
        errors = result.get("errors", [])
        warnings = list(result.get("warnings", []))
        for err in errors:
            warnings.append(f"IC2-W-GENERIC-MACHINE: {err}")
        return NBTConversionResult(
            success=True,
            converted_nbt=result.get("nbt_1182") or None,
            blockstate_props=result.get("blockstate_props", {}),
            warnings=warnings,
            errors=[],
        )


class GeneratorConverter(BaseIC2NBTConverter):
    """Converter for IC2 generators (Generator, Geothermal, Solar, etc.).

    Generators share the same NBT structure as standard machines
    (facing, energy, active).  Some may have additional fields
    (solar: sun intensity, geothermal: fluid tank).
    """

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        source_metadata: int = 0,
    ) -> NBTConversionResult:
        result = simulate_standard_machine_conversion(nbt_1710, target_block_id)
        warnings = list(result.get("warnings", []))
        # Generator-specific fields that may be lost
        if "output" in nbt_1710:
            warnings.append(
                "IC2-W-GENERATOR-OUTPUT: Generator had 'output' field (EU/t config). "
                "Not preserved in target mod."
            )
        return NBTConversionResult(
            success=len(result.get("errors", [])) == 0,
            converted_nbt=result.get("nbt_1182") or None,
            blockstate_props=result.get("blockstate_props", {}),
            warnings=warnings,
            errors=result.get("errors", []),
        )


class EnergyStorageConverter(BaseIC2NBTConverter):
    """Converter for BatBox, MFE, MFSU, CESU, and chargepads."""

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        source_metadata: int = 0,
    ) -> NBTConversionResult:
        result = simulate_energy_storage_conversion(
            nbt_1710, target_block_id, source_block_id, source_metadata
        )
        return NBTConversionResult(
            success=len(result.get("errors", [])) == 0,
            converted_nbt=result.get("nbt_1182") or None,
            blockstate_props=result.get("blockstate_props", {}),
            warnings=result.get("warnings", []),
            errors=result.get("errors", []),
        )


class CableConverter(BaseIC2NBTConverter):
    """Converter for IC2 cables."""

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        source_metadata: int = 0,
    ) -> NBTConversionResult:
        result = simulate_cable_conversion(nbt_1710, target_block_id)
        return NBTConversionResult(
            success=True,
            converted_nbt=result.get("nbt_1182") or None,
            blockstate_props=result.get("blockstate_props", {}),
            warnings=result.get("warnings", []),
            errors=result.get("errors", []),
        )


class LossyCableConverter(BaseIC2NBTConverter):
    """Converter for cables that lose functionality (Detector/Splitter → plain cable)."""

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        source_metadata: int = 0,
    ) -> NBTConversionResult:
        result = simulate_cable_conversion(nbt_1710, target_block_id)
        warnings = list(result.get("warnings", []))
        warnings.append(
            "IC2-W-LOSSY-CABLE: Special cable function (detector/splitter) lost. "
            "Converted to plain cable."
        )
        return NBTConversionResult(
            success=True,
            converted_nbt=result.get("nbt_1182") or None,
            blockstate_props=result.get("blockstate_props", {}),
            warnings=warnings,
            errors=result.get("errors", []),
        )


class TeleporterConverter(BaseIC2NBTConverter):
    """Converter for IC2 Teleporter."""

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        source_metadata: int = 0,
    ) -> NBTConversionResult:
        result = simulate_teleporter_conversion(nbt_1710)
        return NBTConversionResult(
            success=len(result.get("errors", [])) == 0,
            converted_nbt=result.get("nbt_1182") or None,
            blockstate_props=result.get("blockstate_props", {}),
            warnings=result.get("warnings", []),
            errors=result.get("errors", []),
        )


class ReactorConverter(BaseIC2NBTConverter):
    """Converter for IC2 Nuclear Reactor — preserves legacy data as placeholder."""

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        source_metadata: int = 0,
    ) -> NBTConversionResult:
        result = simulate_reactor_conversion(nbt_1710)
        return NBTConversionResult(
            success=True,
            converted_nbt=result.get("nbt_1182") or None,
            blockstate_props=result.get("blockstate_props", {}),
            warnings=result.get("warnings", []),
            errors=result.get("errors", []),
        )


class TransformerConverter(BaseIC2NBTConverter):
    """Converter for IC2 transformers → indreb transformers.

    indreb BlockEntityTransformer uses:
    - energy (int) from IndRebBlockEntity
    - transformerMode (int: 0=STEP_UP, 1=STEP_DOWN)
    """

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        source_metadata: int = 0,
    ) -> NBTConversionResult:
        from ..simulations.machine_simulation import convert_energy_eu_to_fe

        result = {
            "nbt_1182": {},
            "blockstate_props": {},
            "warnings": [],
            "errors": [],
        }

        # Facing → blockstate
        ic2_facing = int(nbt_1710.get("facing", 2))
        from ..simulations.machine_simulation import convert_facing
        result["blockstate_props"]["facing"] = convert_facing(ic2_facing)

        # Energy (EU → FE)
        energy_eu = float(nbt_1710.get("energy", 0.0))
        energy_fe = convert_energy_eu_to_fe(energy_eu)

        if target_block_id.startswith("indreb:"):
            result["nbt_1182"]["energy"] = energy_fe
            # Default to STEP_UP (0) — IC2 transformers don't have mode in NBT
            result["nbt_1182"]["transformerMode"] = 0
        else:
            result["nbt_1182"]["energy"] = energy_fe

        return NBTConversionResult(
            success=True,
            converted_nbt=result["nbt_1182"] if result["nbt_1182"] else None,
            blockstate_props=result["blockstate_props"],
            warnings=result["warnings"],
            errors=result["errors"],
        )


class PlaceholderConverter(BaseIC2NBTConverter):
    """Converter for blocks with no Tier-1 equivalent.

    Preserves full original NBT under legacy keys for potential manual recovery.
    """

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        source_metadata: int = 0,
    ) -> NBTConversionResult:
        warnings = [
            "IC2-W-PLACEHOLDER: No Tier-1 equivalent. Block converted to placeholder. "
            "Original NBT preserved under legacy_ic2_nbt."
        ]
        legacy_nbt = {k: v for k, v in nbt_1710.items() if k != "id"}
        return NBTConversionResult(
            success=True,
            converted_nbt={"legacy_ic2_nbt": legacy_nbt} if legacy_nbt else None,
            warnings=warnings,
        )


# ──────────────────────────────────────────────────────────────────────────────
# Public registry
# ──────────────────────────────────────────────────────────────────────────────

NBT_CONVERTERS: dict[str, BaseIC2NBTConverter] = {
    "identity": IdentityConverter(),
    "standard_machine": StandardMachineConverter(),
    "generic_machine": GenericMachineConverter(),
    "generator": GeneratorConverter(),
    "energy_storage": EnergyStorageConverter(),
    "cable": CableConverter(),
    "lossy_cable": LossyCableConverter(),
    "teleporter": TeleporterConverter(),
    "reactor_component": ReactorConverter(),
    "transformer": TransformerConverter(),
    "placeholder": PlaceholderConverter(),
}


def get_nbt_converter(name: str) -> BaseIC2NBTConverter:
    return NBT_CONVERTERS.get(name, NBT_CONVERTERS["identity"])
