"""Główny konwerter BuildCraft (1.7.10) -> Pipez / Thermal / Mekanism (1.18.2).

Wejście: te_id (string) + nbt_1710 (dict) + metadata + position
Wyjście: BuildCraftBlockConversion z ConversionResult (block_id_1182, nbt_1182, blockstate_props)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from converters.common.conversion_event import ConversionEvent

from .mappings.block_mappings import (
    BlockMapping,
    get_mapping_for_te_id,
    is_buildcraft_te_id,
)
from .nbt_converters.base_converter import NBTConversionResult
from .nbt_converters.converter_registry import get_nbt_converter


@dataclass
class ConversionResult:
    success: bool
    block_id_1182: str | None = None
    blockstate_props: dict[str, str] = field(default_factory=dict)
    nbt_1182: dict[str, Any] | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    event: ConversionEvent | None = None


@dataclass
class BuildCraftBlockConversion:
    original_id: str
    original_pos: tuple[int, int, int]
    metadata: int
    converted: ConversionResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "original_id": self.original_id,
            "original_pos": self.original_pos,
            "metadata": self.metadata,
            "new_id": self.converted.block_id_1182,
            "blockstate_props": self.converted.blockstate_props,
            "nbt": self.converted.nbt_1182,
            "errors": self.converted.errors,
            "warnings": self.converted.warnings,
            "event": self.converted.event.to_dict() if self.converted.event else None,
        }


class BuildCraftConverter:
    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"
    MOD = "buildcraft"

    def __init__(self) -> None:
        self.events: list[ConversionEvent] = []
        self.stats = {"processed": 0, "converted": 0, "removed": 0, "failed": 0, "warnings": 0}

    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────

    def convert_tile_entity(
        self,
        te_id: str,
        nbt_1710: dict[str, Any],
        metadata: int = 0,
        position: tuple[int, int, int] = (0, 0, 0),
    ) -> BuildCraftBlockConversion:
        """Convert a BuildCraft TileEntity NBT to 1.18.2."""
        self.stats["processed"] += 1

        mapping = get_mapping_for_te_id(te_id)
        if not mapping:
            message = f"BC-E-TE-NOT-MAPPED: brak mapowania dla {te_id}"
            self.stats["failed"] += 1
            result = ConversionResult(False, errors=[message])
            return BuildCraftBlockConversion(te_id, position, metadata, result)

        if mapping.action == "REMOVE":
            self.stats["removed"] += 1
            result = ConversionResult(
                success=True,
                block_id_1182="minecraft:air",
                warnings=[mapping.notes],
            )
            return BuildCraftBlockConversion(te_id, position, metadata, result)

        # CONVERT
        nbt_result = self._convert_nbt(mapping, nbt_1710, te_id, metadata)
        block_id = mapping.block_id_1182

        # Special case: pipe converter may suggest different block_id (fluid/energy)
        suggested = nbt_result.blockstate_props.pop("_suggested_block_id", None)
        if suggested:
            block_id = suggested

        result = ConversionResult(
            success=nbt_result.success,
            block_id_1182=block_id,
            blockstate_props=nbt_result.blockstate_props,
            nbt_1182=nbt_result.converted_nbt,
            warnings=nbt_result.warnings,
            errors=nbt_result.errors,
        )
        self.stats["converted"] += 1
        return BuildCraftBlockConversion(te_id, position, metadata, result)

    # ──────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _convert_nbt(
        self,
        mapping: BlockMapping,
        nbt_1710: dict[str, Any],
        source_block_id: str,
        source_metadata: int,
    ) -> NBTConversionResult:
        converter = get_nbt_converter(mapping.nbt_converter)
        return converter.convert(
            nbt_1710=nbt_1710,
            target_block_id=mapping.block_id_1182,
            source_block_id=source_block_id,
            source_metadata=source_metadata,
        )
