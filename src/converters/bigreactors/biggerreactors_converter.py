"""Glowny konwerter Big Reactors 1.7.10 -> Bigger Reactors 1.18.2."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .mappings import BlockMapping, get_block_mapping, get_mapping_for_te_id, is_bigreactors_block
from .nbt_converters import (
    CyaniteReprocessorConverter,
    IdentityBiggerReactorsConverter,
    MultiblockReactorConverter,
    MultiblockTurbineConverter,
    NBTConversionResult,
    ReactorAccessPortConverter,
)


@dataclass
class ConversionResult:
    success: bool
    block_id_1182: str | None = None
    blockstate_props: dict[str, str] = field(default_factory=dict)
    nbt_1182: dict[str, Any] | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class BiggerReactorsBlockConversion:
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
        }


class BiggerReactorsConverter:
    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"

    def __init__(self) -> None:
        self.nbt_converters = {
            "identity": IdentityBiggerReactorsConverter(),
            "multiblock_reactor": MultiblockReactorConverter(),
            "multiblock_reactor_accessport": ReactorAccessPortConverter(),
            "multiblock_turbine": MultiblockTurbineConverter(),
            "cyanite_reprocessor": CyaniteReprocessorConverter(),
            "fluid": IdentityBiggerReactorsConverter(),
        }
        self.stats = {"processed": 0, "converted": 0, "failed": 0, "warnings": 0}

    def convert_block(
        self,
        block_id_1710: str,
        metadata: int = 0,
        nbt_1710: dict[str, Any] | None = None,
        position: tuple[int, int, int] = (0, 0, 0),
    ) -> BiggerReactorsBlockConversion:
        self.stats["processed"] += 1

        mapping = self._resolve_mapping(block_id_1710, metadata, nbt_1710)
        if not mapping:
            message = f"BIG-E-BLOCK-NOT-MAPPED: brak mapowania dla {block_id_1710} meta={metadata}"
            self.stats["failed"] += 1
            result = ConversionResult(False, errors=[message])
            return BiggerReactorsBlockConversion(block_id_1710, position, metadata, result)

        nbt_result = (
            self._convert_nbt(mapping, nbt_1710, block_id_1710, metadata)
            if nbt_1710 and mapping.has_block_entity
            else None
        )

        warnings: list[str] = []
        if mapping.notes:
            warnings.append(f"BIG-W-MAPPING-NOTE: {mapping.notes}")
        errors: list[str] = []
        if nbt_result:
            warnings.extend(nbt_result.warnings)
            errors.extend(nbt_result.errors)

        success = not errors
        self.stats["converted" if success else "failed"] += 1
        self.stats["warnings"] += len(warnings)

        return BiggerReactorsBlockConversion(
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
            ),
        )

    def convert_tile_entity(
        self,
        te_id: str,
        nbt_1710: dict[str, Any],
        metadata: int = 0,
        position: tuple[int, int, int] = (0, 0, 0),
    ) -> BiggerReactorsBlockConversion:
        return self.convert_block(te_id, metadata, nbt_1710, position)

    def convert_item(self, item_id_1710: str, damage: int = 0, nbt: dict[str, Any] | None = None) -> ConversionResult:
        """Prosta konwersja item ID (np. ingotYellorium -> uranium_ingot)."""
        item_map = {
            "BigReactors:ingotYellorium": "biggerreactors:uranium_ingot",
            "BigReactors:ingotBlutonium": "biggerreactors:blutonium_ingot",
            "BigReactors:ingotCyanite": "biggerreactors:cyanite_ingot",
            "BigReactors:ingotGraphite": "biggerreactors:graphite_ingot",
            "BigReactors:ingotLudicrite": "biggerreactors:ludicrite_ingot",
            "BigReactors:dustYellorium": "biggerreactors:uranium_dust",
            "BigReactors:dustBlutonium": "biggerreactors:blutonium_dust",
            "BigReactors:dustCyanite": "biggerreactors:cyanite_dust",
            "BigReactors:dustGraphite": "biggerreactors:graphite_dust",
            "BigReactors:dustLudicrite": "biggerreactors:ludicrite_dust",
        }
        target_id = item_map.get(item_id_1710, item_id_1710)
        return ConversionResult(True, block_id_1182=target_id, nbt_1182=nbt)

    def _resolve_mapping(self, block_id_1710: str, metadata: int, nbt_1710: dict[str, Any] | None) -> BlockMapping | None:
        # Sprobuj po TE id z NBT
        if nbt_1710 and nbt_1710.get("id"):
            by_te = get_mapping_for_te_id(str(nbt_1710["id"]), metadata, nbt_1710)
            if by_te:
                return by_te
        # Sprobuj po znanym TE ID (jesli block_id_1710 wyglada jak TE ID)
        if block_id_1710 in ("BRReactorPart", "BRTurbinePart", "BRFuelRod", "BRCyaniteReprocessor",
                             "BRReactorPowerTap", "BRReactorAccessPort", "BRReactorCoolantPort",
                             "BRReactorControlRod", "BRReactorRedstonePort", "BRReactorComputerPort",
                             "BRReactorRedNetPort", "BRReactorGlass", "BRTurbinePowerTap",
                             "BRTurbineFluidPort", "BRTurbineComputerPort", "BRTurbineGlass",
                             "BRTurbineRotorBearing", "BRTurbineRotorPart",
                             "BRReactorCreativeCoolantPort", "BRTurbineCreativeSteamGenerator"):
            by_te = get_mapping_for_te_id(block_id_1710, metadata, nbt_1710)
            if by_te:
                return by_te
        # Standardowe mapowanie po block_id + metadata
        return get_block_mapping(block_id_1710, metadata, nbt_1710)

    def _convert_nbt(
        self,
        mapping: BlockMapping,
        nbt_1710: dict[str, Any],
        block_id_1710: str,
        metadata: int,
    ) -> NBTConversionResult:
        converter = self.nbt_converters.get(mapping.nbt_converter, self.nbt_converters["identity"])
        return converter.convert(nbt_1710, mapping.target_block_id, block_id_1710, metadata)

    def is_bigreactors_block(self, block_id: str) -> bool:
        return is_bigreactors_block(block_id)
