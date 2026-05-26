"""Logistics Pipes 1.7.10 -> Pretty Pipes / AE2 / XNet converter."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from converters.common.conversion_event import ConversionEvent
from converters.common.placeholders import PLACEHOLDER_BLOCK_ENTITY_ID, PLACEHOLDER_BLOCK_ID

from .mappings import (
    CHASSIS_SLOTS_1710,
    GENERIC_PIPE_TE_ID,
    LP_MODULE_TO_PRETTY_MODULE,
    PRETTY_PIPE_MODULE_SLOTS,
    SOLID_TE_TO_KIND,
    get_pipe_mapping,
    resolve_pipe_class_from_id,
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


@dataclass
class LogisticsPipesBlockConversion:
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


class LogisticsPipesConverter:
    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"
    MOD = "logisticspipes"

    def __init__(self) -> None:
        self.events: list[ConversionEvent] = []
        self.stats = {"processed": 0, "converted": 0, "placeholder": 0, "failed": 0, "warnings": 0}

    def convert_tile_entity(
        self,
        te_id: str,
        nbt_1710: dict[str, Any],
        metadata: int = 0,
        position: tuple[int, int, int] = (0, 0, 0),
    ) -> LogisticsPipesBlockConversion:
        self.stats["processed"] += 1

        if te_id == GENERIC_PIPE_TE_ID:
            result = self._convert_generic_pipe(te_id, nbt_1710, metadata, position)
        elif te_id in SOLID_TE_TO_KIND:
            result = self._convert_solid_tile(te_id, nbt_1710, metadata, position)
        else:
            message = f"LP-E-TE-NOT-MAPPED: brak mapowania dla {te_id}"
            self.stats["failed"] += 1
            result = ConversionResult(False, errors=[message])

        if result.success:
            if result.block_id_1182 == PLACEHOLDER_BLOCK_ID:
                self.stats["placeholder"] += 1
            else:
                self.stats["converted"] += 1
        self.stats["warnings"] += len(result.warnings)
        return LogisticsPipesBlockConversion(te_id, position, metadata, result)

    def _convert_generic_pipe(
        self,
        te_id: str,
        nbt_1710: dict[str, Any],
        metadata: int,
        position: tuple[int, int, int],
    ) -> ConversionResult:
        pipe_class = find_pipe_class(nbt_1710)
        resolved_from_pipe_id = False
        if pipe_class is None:
            pipe_class = resolve_pipe_class_from_id(nbt_1710.get("pipeId"))
            resolved_from_pipe_id = pipe_class is not None
        mapping = get_pipe_mapping(pipe_class)
        warnings = list(mapping.warnings)
        conversion_note: dict[str, Any] = {
            "source_pipe_class": pipe_class or "",
            "source_pipe_id": nbt_1710.get("pipeId"),
            "role": mapping.role,
            "pipe_class_resolved_from_pipe_id": resolved_from_pipe_id,
        }

        modules: list[str] = list(mapping.pretty_modules)
        overflow_modules: list[str] = []
        source_modules: list[str] = []
        if pipe_class in CHASSIS_SLOTS_1710:
            chassis = convert_chassis_modules(pipe_class, extract_module_classes(nbt_1710))
            modules = chassis["pretty_modules"]
            overflow_modules = chassis["overflow"]
            source_modules = chassis["source_modules"]
            conversion_note["chassis"] = chassis
            if overflow_modules:
                warnings.append(
                    "LP-W-CHASSIS-OVERFLOW: LP chassis has more active modules than Pretty Pipes can store."
                )
            if not source_modules:
                warnings.append("LP-W-CHASSIS-MODULES-UNKNOWN: no module inventory could be extracted from NBT.")

        if pipe_class is None and nbt_1710.get("pipeId") is not None:
            warnings.append(
                "LP-W-DYNAMIC-PIPE-ID: NBT stores numeric pipeId; item-id lookup is required for exact role."
            )

        nbt_1182 = None
        if mapping.target_te_id:
            nbt_1182 = make_pretty_pipe_nbt(mapping.target_te_id, position, modules, conversion_note)
        elif mapping.target_block_id.startswith("pipez:"):
            warnings.append("LP-W-PIPEZ-NBT: Pipez target is emitted as block-only; old routing rules kept in warning metadata.")

        result = ConversionResult(
            success=True,
            block_id_1182=mapping.target_block_id,
            nbt_1182=nbt_1182,
            warnings=warnings,
        )
        result.event = self._make_event(te_id, metadata, position, nbt_1710, result, mapping.target_te_id)
        self.events.append(result.event)
        return result

    def _convert_solid_tile(
        self,
        te_id: str,
        nbt_1710: dict[str, Any],
        metadata: int,
        position: tuple[int, int, int],
    ) -> ConversionResult:
        kind = SOLID_TE_TO_KIND[te_id]
        if kind == "crafting_table":
            warnings = ["LP-W-CRAFTING-TABLE: converted to AE2 pattern provider shell; recipe/pattern needs verification."]
            if metadata == 4 or nbt_1710.get("fuzzy") or nbt_1710.get("Fuzzy"):
                warnings.append("LP-W-FUZZY-CRAFTING: fuzzy crafting has no automatic 1:1 conversion.")
            nbt_1182 = {
                "id": "ae2:pattern_provider",
                "x": position[0],
                "y": position[1],
                "z": position[2],
                "conversion_source": {
                    "mod": self.MOD,
                    "kind": kind,
                    "source_te_id": te_id,
                    "source_metadata": metadata,
                    "source_nbt": deepcopy(nbt_1710),
                },
            }
            result = ConversionResult(True, "ae2:pattern_provider", nbt_1182=nbt_1182, warnings=warnings)
            result.event = self._make_event(te_id, metadata, position, nbt_1710, result, "ae2:pattern_provider")
            self.events.append(result.event)
            return result

        if kind in {"power_junction", "rf_power_provider", "ic2_power_provider"}:
            warnings = [
                "LP-W-POWER-NOT-LOSSLESS: LP internal power is not a lossless Pretty Pipes FE value.",
                "LP-W-PRESSURIZER-RECOMMENDED: generated pressurizer shell; verify placement against adjacent pipe network.",
            ]
            if kind == "ic2_power_provider":
                warnings.append("LP-W-IC2-EU: IC2 EU provider requires IC2 energy migration review.")
            nbt_1182 = {
                "id": "prettypipes:pressurizer",
                "x": position[0],
                "y": position[1],
                "z": position[2],
                "energy": safe_int(nbt_1710.get("energy", nbt_1710.get("Energy", 0))),
                "conversion_source": {
                    "mod": self.MOD,
                    "kind": kind,
                    "source_te_id": te_id,
                    "source_metadata": metadata,
                    "source_nbt": deepcopy(nbt_1710),
                },
            }
            result = ConversionResult(True, "prettypipes:pressurizer", nbt_1182=nbt_1182, warnings=warnings)
            result.event = self._make_event(te_id, metadata, position, nbt_1710, result, "prettypipes:pressurizer")
            self.events.append(result.event)
            return result

        reason = {
            "soldering": "LP-W-SOLDERING-NO-TARGET: soldering station has no runtime target in 1.18.2 stack.",
            "security": "LP-W-SECURITY-NO-TARGET: LP security station permissions are not portable.",
            "statistics": "LP-W-STATISTICS-NO-TARGET: LP statistics table has no direct replacement.",
        }.get(kind, "LP-W-SOLID-NO-TARGET: unsupported Logistics Pipes solid block.")
        nbt_1182 = make_placeholder_nbt(te_id, nbt_1710, metadata, position, kind)
        result = ConversionResult(True, PLACEHOLDER_BLOCK_ID, nbt_1182=nbt_1182, warnings=[reason])
        result.event = self._make_event(te_id, metadata, position, nbt_1710, result, PLACEHOLDER_BLOCK_ENTITY_ID)
        self.events.append(result.event)
        return result

    def _make_event(
        self,
        te_id: str,
        metadata: int,
        position: tuple[int, int, int],
        source_nbt: dict[str, Any],
        result: ConversionResult,
        target_te_id: str | None,
    ) -> ConversionEvent:
        return ConversionEvent(
            mod=self.MOD,
            source_version=self.SOURCE_VERSION,
            target_version=self.TARGET_VERSION,
            event_type="placeholder" if result.block_id_1182 == PLACEHOLDER_BLOCK_ID else "remap",
            source_block_id=source_nbt.get("block_id", "LogisticsPipes:unknown"),
            source_metadata=metadata,
            target_block_id=result.block_id_1182,
            position=position,
            source_te_id=te_id,
            target_te_id=target_te_id,
            nbt_1182=result.nbt_1182,
            blockstate_props=result.blockstate_props,
            warnings=list(result.warnings),
            errors=list(result.errors),
            source_nbt=deepcopy(source_nbt),
        )


def find_pipe_class(nbt: dict[str, Any]) -> str | None:
    direct_keys = ("pipeClass", "pipe_class", "pipeType", "pipe_type", "pipeItemClass", "pipeName", "PipeClass")
    for key in direct_keys:
        value = nbt.get(key)
        if isinstance(value, str) and value:
            return value.split(".")[-1]

    for text in iter_strings(nbt):
        if text.startswith("Pipe") or ".Pipe" in text:
            tail = text.split(".")[-1]
            if tail.startswith("Pipe"):
                return tail
    return None


def extract_module_classes(nbt: dict[str, Any]) -> list[str]:
    for key in ("modules", "Modules", "chassi", "chassis", "moduleInventory", "ModuleInventory"):
        if key not in nbt:
            continue
        modules = module_classes_from_value(nbt[key])
        if modules:
            return modules
    return []


def module_classes_from_value(value: Any) -> list[str]:
    modules: list[str] = []
    if isinstance(value, list):
        for entry in value:
            modules.extend(module_classes_from_value(entry))
    elif isinstance(value, dict):
        for key in ("moduleClass", "ModuleClass", "module", "Module", "id", "item", "name"):
            raw = value.get(key)
            if isinstance(raw, str):
                tail = raw.split(".")[-1]
                if tail.startswith("Module"):
                    modules.append(tail)
        for inner in value.values():
            if isinstance(inner, (dict, list)):
                modules.extend(module_classes_from_value(inner))
    elif isinstance(value, str):
        tail = value.split(".")[-1]
        if tail.startswith("Module"):
            modules.append(tail)
    return modules


def convert_chassis_modules(pipe_class: str, source_modules: list[str]) -> dict[str, Any]:
    lp_slots = CHASSIS_SLOTS_1710[pipe_class]
    installed = source_modules[:lp_slots]
    mapped = [LP_MODULE_TO_PRETTY_MODULE.get(module, "manual-review") for module in installed]
    return {
        "lp_slots": lp_slots,
        "source_modules": installed,
        "pretty_modules": mapped[:PRETTY_PIPE_MODULE_SLOTS],
        "overflow": mapped[PRETTY_PIPE_MODULE_SLOTS:],
    }


def make_pretty_pipe_nbt(
    target_te_id: str,
    position: tuple[int, int, int],
    modules: list[str],
    conversion_note: dict[str, Any],
) -> dict[str, Any]:
    nbt: dict[str, Any] = {
        "id": target_te_id,
        "x": position[0],
        "y": position[1],
        "z": position[2],
        "conversion_source": conversion_note,
    }
    if target_te_id == "prettypipes:pipe":
        nbt["modules"] = {
            "Size": PRETTY_PIPE_MODULE_SLOTS,
            "Items": [
                {"Slot": slot, "id": module_id, "Count": 1}
                for slot, module_id in enumerate(modules[:PRETTY_PIPE_MODULE_SLOTS])
            ],
        }
    return nbt


def make_placeholder_nbt(
    te_id: str,
    source_nbt: dict[str, Any],
    metadata: int,
    position: tuple[int, int, int],
    kind: str,
) -> dict[str, Any]:
    return {
        "id": PLACEHOLDER_BLOCK_ENTITY_ID,
        "x": position[0],
        "y": position[1],
        "z": position[2],
        "source_mod": "logisticspipes",
        "source_block_id": "LogisticsPipes:logisticsSolidBlock",
        "source_te_id": te_id,
        "source_metadata": metadata,
        "conversion_reason": kind,
        "conversion_stage": "logistics_pipes_zadanie3",
        "original_nbt": deepcopy(source_nbt),
        "extra": {"kind": kind},
    }


def iter_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for inner in value.values():
            yield from iter_strings(inner)
    elif isinstance(value, list):
        for inner in value:
            yield from iter_strings(inner)


def safe_int(value: Any) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0
