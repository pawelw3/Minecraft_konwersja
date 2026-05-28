"""Chisel 1.7.10 -> Rechiseled/Chipped event converter."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from converters.common.conversion_event import ConversionEvent
from converters.common.placeholders import make_block_entity_placeholder_event

from .mappings import (
    DynamicChiselIdEntry,
    is_chisel_block_id,
    is_chisel_te_id,
    load_dynamic_id_map,
    resolve_from_block_id,
)


@dataclass
class ConversionResult:
    success: bool
    block_id_1182: str | None = None
    blockstate_props: dict[str, str] = field(default_factory=dict)
    nbt_1182: dict[str, Any] | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    event: ConversionEvent | None = None
    event_json: dict[str, Any] | None = None


@dataclass
class ChiselBlockConversion:
    original_id: str
    original_pos: tuple[int, int, int]
    metadata: int
    converted: ConversionResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "original_id": self.original_id,
            "original_pos": list(self.original_pos),
            "metadata": self.metadata,
            "new_id": self.converted.block_id_1182,
            "blockstate_props": self.converted.blockstate_props,
            "nbt": self.converted.nbt_1182,
            "errors": self.converted.errors,
            "warnings": self.converted.warnings,
            "event": self.converted.event.to_dict() if self.converted.event else self.converted.event_json,
        }


class ChiselConverter:
    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"
    MOD = "chisel"

    def __init__(
        self,
        dynamic_id_map: dict[int, DynamicChiselIdEntry] | None = None,
        dynamic_id_map_path: str | None = None,
    ) -> None:
        self.dynamic_id_map = dynamic_id_map if dynamic_id_map is not None else load_dynamic_id_map(dynamic_id_map_path)
        self.stats = {"processed": 0, "converted": 0, "placeholder": 0, "failed": 0, "warnings": 0}

    def convert_block(
        self,
        block_id_1710: str | int,
        metadata: int = 0,
        nbt_1710: dict[str, Any] | None = None,
        position: tuple[int, int, int] = (0, 0, 0),
    ) -> ChiselBlockConversion:
        self.stats["processed"] += 1
        original_id = str(block_id_1710)

        if nbt_1710 and is_chisel_te_id(str(nbt_1710.get("id", ""))):
            return self.convert_tile_entity(str(nbt_1710.get("id", "")), nbt_1710, metadata, position)

        if not is_chisel_block_id(block_id_1710, self.dynamic_id_map):
            result = ConversionResult(
                success=False,
                errors=[f"CHISEL-E-NOT-CHISEL-BLOCK: {block_id_1710} meta={metadata}"],
            )
            self.stats["failed"] += 1
            return ChiselBlockConversion(original_id, position, metadata, result)

        target = resolve_from_block_id(block_id_1710, metadata, self.dynamic_id_map)
        warnings = [
            f"CHISEL-W-VISUAL-MAPPING: {target.reason}; confidence={target.confidence}",
            "CHISEL-W-META-VERIFY: exact 1.7.10 metadata variant must be verified against map/test-world dynamic ID scan.",
        ]
        if target.confidence == "low":
            warnings.append("CHISEL-W-LOW-CONFIDENCE: fallback may be visually rough; prefer texture histogram matching in Zadanie 4.")

        event = ConversionEvent(
            mod=self.MOD,
            source_version=self.SOURCE_VERSION,
            target_version=self.TARGET_VERSION,
            event_type="remap",
            source_block_id=original_id,
            source_metadata=int(metadata),
            target_block_id=target.block_id,
            position=position,
            blockstate_props=dict(target.blockstate_props),
            warnings=warnings,
            source_nbt=deepcopy(nbt_1710) if nbt_1710 else None,
        )
        result = ConversionResult(
            success=True,
            block_id_1182=target.block_id,
            blockstate_props=dict(target.blockstate_props),
            warnings=warnings,
            event=event,
        )
        self.stats["converted"] += 1
        self.stats["warnings"] += len(warnings)
        return ChiselBlockConversion(original_id, position, metadata, result)

    def convert_tile_entity(
        self,
        te_id: str,
        nbt_1710: dict[str, Any],
        metadata: int = 0,
        position: tuple[int, int, int] = (0, 0, 0),
    ) -> ChiselBlockConversion:
        self.stats["processed"] += 1
        if not is_chisel_te_id(te_id):
            result = ConversionResult(
                success=False,
                errors=[f"CHISEL-E-TE-NOT-MAPPED: {te_id}"],
            )
            self.stats["failed"] += 1
            return ChiselBlockConversion(te_id, position, metadata, result)

        warnings = [
            "CHISEL-W-TE-PLACEHOLDER: Rechiseled 1.18.2 has no Auto Chisel/Present/Beacon block entity equivalent.",
            "CHISEL-W-DATA-RESCUE: original NBT is preserved in conversion placeholder.",
        ]
        event_json = make_block_entity_placeholder_event(
            position=position,
            source_mod=self.MOD,
            original_nbt=nbt_1710,
            source_block_id="chisel:tile_entity",
            source_te_id=te_id,
            source_metadata=metadata,
            conversion_reason="chisel_te_no_1182_equivalent",
            conversion_stage="chisel_zadanie3",
            extra={
                "recommended_manual_action": _manual_action_for_te(te_id),
                "visual_policy": "Decorative Chisel blocks should be remapped separately by block ID/meta.",
            },
        )
        result = ConversionResult(
            success=True,
            block_id_1182=event_json["block"],
            nbt_1182=event_json.get("nbt"),
            warnings=warnings,
            event_json=event_json,
        )
        self.stats["placeholder"] += 1
        self.stats["warnings"] += len(warnings)
        return ChiselBlockConversion(te_id, position, metadata, result)

    def to_events(self, conversion: ChiselBlockConversion) -> list[dict[str, Any]]:
        result = conversion.converted
        if not result.success:
            return []
        if result.event_json:
            return [result.event_json]
        if result.event:
            event = result.event.to_set_block_event()
            return [event] if event else []
        return []

    def get_stats(self) -> dict[str, int]:
        return dict(self.stats)


def _manual_action_for_te(te_id: str) -> str:
    lowered = te_id.lower()
    if "autochisel" in lowered or "auto_chisel" in lowered:
        return "Recover input/output/target items from placeholder; rebuild with Rechiseled chisel item workflow if needed."
    if "present" in lowered:
        return "Inspect preserved NBT and replace with a decorative/storage placeholder or vanilla barrel/chest if it carried items."
    if "beacon" in lowered:
        return "Replace with vanilla beacon or decorative Rechiseled block after visual review."
    return "Inspect placeholder NBT manually."

