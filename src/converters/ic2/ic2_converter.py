"""Główny konwerter IndustrialCraft 2 (1.7.10) → Industrial Reborn / FTBIC (1.18.2).

Source mapping (1.7.10):
- Bloki: ic2/core/block/Block*.java
- TileEntities: ic2/core/block/machine/tileentity/TileEntity*.java (writeToNBT/readFromNBT)

Source mapping (1.18.2 targets):
- Industrial Reborn: com/maciej916/indreb/common/blockentity/*.java
- FTBIC: dev/ftb/mods/ftbic/block/entity/*.java

Kontrakty:
- Wejście: block_id_1710 (string) + metadata + te_nbt_1710 (dict)
- Wyjście: IC2BlockConversion z ConversionResult (block_id_1182, nbt_1182, blockstate_props)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from converters.common.conversion_event import ConversionEvent

from .mappings.block_inventory import IC2_ALL_BLOCKS
from .mappings.block_mappings import (
    BlockMapping,
    get_block_mapping,
    get_block_meta_for_te_id,
    get_mapping_for_te_id,
    is_ic2_block,
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
class IC2BlockConversion:
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


class IC2Converter:
    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"
    MOD = "ic2"

    def __init__(self) -> None:
        self.events: list[ConversionEvent] = []
        self.stats = {"processed": 0, "converted": 0, "failed": 0, "warnings": 0}

    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────

    def convert_block(
        self,
        block_id_1710: str,
        metadata: int = 0,
        nbt_1710: dict[str, Any] | None = None,
        position: tuple[int, int, int] = (0, 0, 0),
    ) -> IC2BlockConversion:
        """Convert an IC2 block + optional TileEntity NBT to 1.18.2."""
        self.stats["processed"] += 1

        mapping = self._resolve_mapping(block_id_1710, metadata, nbt_1710)
        if not mapping:
            message = f"IC2-E-BLOCK-NOT-MAPPED: brak mapowania dla {block_id_1710} meta={metadata}"
            self.stats["failed"] += 1
            result = ConversionResult(False, errors=[message])
            return IC2BlockConversion(block_id_1710, position, metadata, result)

        nbt_result = (
            self._convert_nbt(mapping, nbt_1710, block_id_1710, metadata)
            if nbt_1710 and mapping.has_block_entity
            else None
        )

        warnings: list[str] = []
        if mapping.notes:
            warnings.append(f"IC2-W-MAPPING-NOTE: {mapping.notes}")
        errors: list[str] = []
        if nbt_result:
            warnings.extend(nbt_result.warnings)
            errors.extend(nbt_result.errors)

        success = not errors
        self.stats["converted" if success else "failed"] += 1
        self.stats["warnings"] += len(warnings)

        event = self._make_event(
            mapping=mapping,
            source_block_id=block_id_1710,
            metadata=metadata,
            position=position,
            nbt_1710=nbt_1710,
            nbt_result=nbt_result,
            warnings=warnings,
            errors=errors,
        )
        self.events.append(event)

        return IC2BlockConversion(
            original_id=block_id_1710,
            original_pos=position,
            metadata=metadata,
            converted=ConversionResult(
                success=success,
                block_id_1182=mapping.target_block_id,
                blockstate_props=nbt_result.blockstate_props if nbt_result else {},
                nbt_1182=nbt_result.converted_nbt if nbt_result else None,
                errors=errors,
                warnings=warnings,
                event=event,
            ),
        )

    def convert_tile_entity(
        self,
        te_id: str,
        nbt_1710: dict[str, Any],
        metadata: int = 0,
        position: tuple[int, int, int] = (0, 0, 0),
    ) -> IC2BlockConversion:
        """Convert by TileEntity class name.

        Tries to resolve the source block_id from the TE inventory,
        then delegates to convert_block().
        """
        block_id = self._resolve_block_id_from_te(te_id, metadata)
        if block_id:
            return self.convert_block(block_id, metadata, nbt_1710, position)
        # Fallback: pass TE id directly — _resolve_mapping handles TE ids too
        return self.convert_block(te_id, metadata, nbt_1710, position)

    def get_events(self) -> list[ConversionEvent]:
        return list(self.events)

    def reset(self) -> None:
        self.events.clear()
        self.stats = {"processed": 0, "converted": 0, "failed": 0, "warnings": 0}

    # ──────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _resolve_mapping(
        self,
        block_id_1710: str,
        metadata: int,
        nbt_1710: dict[str, Any] | None,
    ) -> BlockMapping | None:
        # Prefer explicit block+metadata when the caller has section data.
        # Registry TE ids such as "Cable" are generic and must not override
        # metadata-specific mappings like IC2:blockCable:9.
        if is_ic2_block(block_id_1710):
            by_block = get_block_mapping(block_id_1710, metadata)
            if by_block:
                return by_block

        # Try by TE id when block id is unavailable or unknown.
        if nbt_1710 and nbt_1710.get("id"):
            by_te = get_mapping_for_te_id(str(nbt_1710["id"]))
            if by_te:
                return by_te
        # If block_id_1710 is itself a known TE class name
        by_te = get_mapping_for_te_id(block_id_1710)
        if by_te:
            return by_te
        # Standard block+metadata lookup
        return get_block_mapping(block_id_1710, metadata)

    def _convert_nbt(
        self,
        mapping: BlockMapping,
        nbt_1710: dict[str, Any],
        block_id_1710: str,
        metadata: int,
    ) -> NBTConversionResult:
        converter = get_nbt_converter(mapping.nbt_converter)
        return converter.convert(
            nbt_1710,
            mapping.target_block_id,
            block_id_1710,
            metadata,
        )

    def _make_event(
        self,
        mapping: BlockMapping,
        source_block_id: str,
        metadata: int,
        position: tuple[int, int, int],
        nbt_1710: dict[str, Any] | None,
        nbt_result: NBTConversionResult | None,
        warnings: list[str],
        errors: list[str],
    ) -> ConversionEvent:
        return ConversionEvent(
            mod=self.MOD,
            source_version=self.SOURCE_VERSION,
            target_version=self.TARGET_VERSION,
            event_type="block_entity" if mapping.has_block_entity else "block",
            source_block_id=source_block_id,
            source_metadata=metadata,
            target_block_id=mapping.target_block_id,
            position=position,
            source_te_id=str(nbt_1710.get("id")) if nbt_1710 and nbt_1710.get("id") else None,
            target_te_id=mapping.target_block_id if mapping.has_block_entity else None,
            nbt_1182=nbt_result.converted_nbt if nbt_result else None,
            blockstate_props=nbt_result.blockstate_props if nbt_result else {},
            warnings=warnings,
            errors=errors,
            source_nbt=nbt_1710,
        )

    def _resolve_block_id_from_te(self, te_id: str, metadata: int) -> str | None:
        """Look up block_id from TE class name using block_inventory data."""
        resolved = get_block_meta_for_te_id(te_id)
        if resolved:
            return resolved[0]
        for block_id, variants in IC2_ALL_BLOCKS.items():
            meta_info = variants.get(metadata, variants.get(0))
            if meta_info and meta_info.get("te_class") == te_id:
                return block_id
        return None
