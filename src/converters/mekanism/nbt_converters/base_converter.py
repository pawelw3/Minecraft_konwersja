"""Bazowe narzedzia konwersji NBT Mekanism."""

from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


@dataclass
class NBTConversionResult:
    success: bool
    converted_nbt: dict[str, Any] | None = None
    blockstate_props: dict[str, str] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class BaseMekanismNBTConverter(ABC):
    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"

    POSITION_KEYS = {"x", "y", "z"}
    ORIENTATION_KEYS = {"facing", "facingSet", "side", "forward", "up"}
    CACHE_KEYS = {
        "clientActive",
        "clientToMine",
        "currentRedstoneLevel",
        "delayTicks",
        "initCalc",
        "inventoryID",
        "isActive",
        "numPowering",
        "oresToMine",
        "prevEnergy",
        "replaceMap",
        "searcher",
        "structure",
        "structureFound",
        "toMine",
        "updateDelay",
    }

    @property
    @abstractmethod
    def converter_name(self) -> str:
        pass

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_te_id: str,
        block_id: str | None = None,
        metadata: int = 0,
    ) -> NBTConversionResult:
        try:
            converted, warnings = self._convert(nbt_1710, target_te_id, block_id, metadata)
        except Exception as exc:  # pragma: no cover - defensive boundary
            return NBTConversionResult(False, errors=[f"MEK-E-NBT-{self.converter_name}: {exc}"])
        blockstate_props = self._extract_blockstate(nbt_1710)
        return NBTConversionResult(True, converted, blockstate_props, warnings=warnings)

    def _convert(
        self,
        nbt_1710: dict[str, Any],
        target_te_id: str,
        block_id: str | None,
        metadata: int,
    ) -> tuple[dict[str, Any], list[str]]:
        warnings: list[str] = []
        converted = self._base_copy(nbt_1710, target_te_id, warnings)
        return converted, warnings

    def _base_copy(self, nbt_1710: dict[str, Any], target_te_id: str, warnings: list[str]) -> dict[str, Any]:
        converted: dict[str, Any] = {"id": target_te_id}
        for key, value in nbt_1710.items():
            if key == "id" or key in self.POSITION_KEYS or key in self.ORIENTATION_KEYS:
                continue
            if key in self.CACHE_KEYS:
                warnings.append(f"MEK-W-DROP-CACHE: pomijam cache NBT `{key}`")
                continue
            converted[key] = deepcopy(value)
        return converted

    def _extract_blockstate(self, nbt: dict[str, Any]) -> dict[str, str]:
        if "facing" in nbt:
            return {"facing": self._direction_to_facing(nbt.get("facing"))}
        if "side" in nbt:
            return {"facing": self._direction_to_facing(nbt.get("side"))}
        if "forward" in nbt:
            return {"facing": self._direction_to_facing(nbt.get("forward"))}
        return {}

    def _convert_inventory_list(self, nbt_1710: dict[str, Any]) -> list[dict[str, Any]]:
        raw_items = nbt_1710.get("Items") or nbt_1710.get("items") or []
        if not isinstance(raw_items, list):
            return []
        return [self._convert_item_stack(item) for item in raw_items if isinstance(item, dict)]

    def _convert_item_stack(self, item: dict[str, Any]) -> dict[str, Any]:
        converted = deepcopy(item)
        if "id" in converted:
            converted["id"] = self._convert_item_id(str(converted["id"]), int(converted.get("Damage", 0) or 0))
        return converted

    def _convert_item_id(self, item_id: str, damage: int = 0) -> str:
        if item_id.startswith("Mekanism:"):
            name = item_id.split(":", 1)[1]
            mapping = {
                "OsmiumDust": "mekanism:dust_osmium",
                "DirtyOsmiumDust": "mekanism:dirty_dust_osmium",
                "OsmiumClump": "mekanism:clump_osmium",
                "OsmiumShard": "mekanism:shard_osmium",
                "OsmiumCrystal": "mekanism:crystal_osmium",
            }
            if name == "Ingot" and damage == 1:
                return "mekanism:ingot_osmium"
            return mapping.get(name, f"mekanism:{_camel_to_snake(name)}")
        return item_id

    def _extract_energy(self, nbt_1710: dict[str, Any]) -> float | None:
        for key in ("electricityStored", "energy", "Energy"):
            if key in nbt_1710:
                try:
                    return float(nbt_1710[key])
                except (TypeError, ValueError):
                    return None
        return None

    def _energy_container(self, amount: float | None, warning_context: str, warnings: list[str]) -> list[dict[str, str]]:
        if amount is None:
            return []
        warnings.append(f"MEK-W-ENERGY-RATIO: {warning_context}; zapisuje wartosc jako ratio/preserve candidate")
        return [{"stored": str(amount), "conversionPolicy": "preserve_legacy_joules_or_fill_ratio"}]

    def _direction_to_facing(self, direction: Any) -> str:
        if isinstance(direction, str):
            return direction.lower()
        return {
            0: "down",
            1: "up",
            2: "north",
            3: "south",
            4: "west",
            5: "east",
        }.get(_int_value(direction, 2), "north")


class IdentityMekanismConverter(BaseMekanismNBTConverter):
    @property
    def converter_name(self) -> str:
        return "identity"


def _camel_to_snake(value: str) -> str:
    out = []
    for index, char in enumerate(value):
        if char.isupper() and index > 0 and value[index - 1].islower():
            out.append("_")
        out.append(char.lower())
    return "".join(out)


def _int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
