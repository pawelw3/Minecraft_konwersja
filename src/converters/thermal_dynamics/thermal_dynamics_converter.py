"""Główny konwerter Thermal Dynamics 1.7.10 -> 1.18.2 (TD + Mekanism)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .conversion_event import ConversionEvent
from .mappings import BlockMapping, get_block_mapping, get_mapping_for_te_id, is_thermal_dynamics_block, is_thermal_dynamics_te
from .nbt_converters import (
    DuctNBTConverter,
    IdentityTDConverter,
    MekanismTeleporterConverter,
    MekanismTransporterConverter,
    NBTConversionResult,
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
    extra_items: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class TDBlockConversion:
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
            "extra_items": self.converted.extra_items,
            "event": self.converted.event.to_dict() if self.converted.event else None,
        }


class ThermalDynamicsConverter:
    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"

    def __init__(self) -> None:
        self.nbt_converters = {
            "identity": IdentityTDConverter(),
            "energy_duct": DuctNBTConverter(),
            "fluid_duct": DuctNBTConverter(),
            "mekanism_transporter": MekanismTransporterConverter(),
            "mekanism_teleporter": MekanismTeleporterConverter(),
        }
        self.events: list[ConversionEvent] = []
        self.stats = {"processed": 0, "converted": 0, "failed": 0, "warnings": 0}

    def convert_block(
        self,
        block_id_1710: str,
        metadata: int = 0,
        nbt_1710: dict[str, Any] | None = None,
        position: tuple[int, int, int] = (0, 0, 0),
    ) -> TDBlockConversion:
        self.stats["processed"] += 1
        mapping = self._resolve_mapping(block_id_1710, metadata, nbt_1710)
        if not mapping:
            message = f"TD-E-BLOCK-NOT-MAPPED: brak mapowania dla {block_id_1710} meta={metadata}"
            self.stats["failed"] += 1
            result = ConversionResult(False, errors=[message])
            return TDBlockConversion(block_id_1710, position, metadata, result)

        nbt_result = (
            self._convert_nbt(mapping, nbt_1710, block_id_1710, metadata)
            if mapping.has_block_entity
            else NBTConversionResult(True, {})
        )

        warnings = list(mapping.notes and [f"TD-W-MAPPING-NOTE: {mapping.notes}"] or [])
        errors: list[str] = []
        extra_items: list[dict[str, Any]] = []

        if nbt_result:
            warnings.extend(nbt_result.warnings)
            errors.extend(nbt_result.errors)
            extra_items.extend(nbt_result.extra_items)

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

        return TDBlockConversion(
            block_id_1710,
            position,
            metadata,
            ConversionResult(
                success=success,
                block_id_1182=mapping.target_block_id,
                nbt_1182=nbt_result.nbt_1182 if nbt_result else None,
                warnings=warnings,
                errors=errors,
                event=event,
                extra_items=extra_items,
            ),
        )

    def convert_tile_entity(
        self,
        te_id: str,
        nbt_1710: dict[str, Any],
        metadata: int = 0,
        position: tuple[int, int, int] = (0, 0, 0),
    ) -> TDBlockConversion:
        mapping = get_mapping_for_te_id(te_id, metadata)
        if mapping:
            return self.convert_block(mapping.source_block_id, metadata, nbt_1710, position)
        # Fallback: spróbuj użyć te_id jako block_id (rzadki przypadek)
        return self.convert_block(te_id, metadata, nbt_1710, position)

    def _resolve_mapping(
        self, block_id: str, metadata: int, nbt: dict[str, Any] | None
    ) -> BlockMapping | None:
        if is_thermal_dynamics_block(block_id):
            return get_block_mapping(block_id, metadata)
        # Jeśli block_id to TE ID (z routera), spróbuj przez TE mapping
        if is_thermal_dynamics_te(block_id):
            return get_mapping_for_te_id(block_id, metadata)
        return None

    def _convert_nbt(
        self,
        mapping: BlockMapping,
        nbt_1710: dict[str, Any] | None,
        block_id: str,
        metadata: int,
    ) -> NBTConversionResult:
        converter = self.nbt_converters.get(mapping.nbt_converter)
        if not converter:
            return NBTConversionResult(
                False, errors=[f"TD-E-NBT-CONVERTER-MISSING: {mapping.nbt_converter}"]
            )
        try:
            return converter.convert(nbt_1710 or {}, mapping.target_block_id)
        except Exception as exc:
            return NBTConversionResult(
                False, errors=[f"TD-E-NBT-EXCEPTION: {type(exc).__name__}: {exc}"]
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
            mod="ThermalDynamics",
            source_version=self.SOURCE_VERSION,
            target_version=self.TARGET_VERSION,
            event_type="block_entity" if mapping.has_block_entity else "block",
            source_block_id=source_block_id,
            source_metadata=metadata,
            target_block_id=mapping.target_block_id,
            position=position,
            source_te_id=nbt_1710.get("id") if nbt_1710 else None,
            target_te_id=mapping.target_block_id if mapping.has_block_entity else None,
            nbt_1182=nbt_result.nbt_1182 if nbt_result else None,
            warnings=warnings,
            errors=errors,
        )
