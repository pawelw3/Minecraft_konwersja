"""Specyficzne konwertery NBT Mekanism."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ..mappings import FACTORY_RECIPE_BY_ORDINAL, FACTORY_TIER_BY_META, TIER_BY_META
from .base_converter import BaseMekanismNBTConverter, _int_value


class MachineConverter(BaseMekanismNBTConverter):
    @property
    def converter_name(self) -> str:
        return "machine"

    def _convert(self, nbt_1710: dict[str, Any], target_te_id: str, block_id: str | None, metadata: int):
        warnings: list[str] = []
        converted = self._base_copy(nbt_1710, target_te_id, warnings)
        energy = self._extract_energy(nbt_1710)
        if energy is not None:
            converted["energyContainers"] = self._energy_container(energy, target_te_id, warnings)
            converted.pop("electricityStored", None)
        items = self._convert_inventory_list(nbt_1710)
        if items:
            converted["Items"] = items
        if "operatingTicks" in nbt_1710:
            converted["operatingTicks"] = _int_value(nbt_1710["operatingTicks"])
        return converted, warnings


class FactoryConverter(MachineConverter):
    @property
    def converter_name(self) -> str:
        return "factory"

    def _convert(self, nbt_1710: dict[str, Any], target_te_id: str, block_id: str | None, metadata: int):
        converted, warnings = super()._convert(nbt_1710, target_te_id, block_id, metadata)
        recipe_ordinal = _int_value(nbt_1710.get("recipeType"), 0)
        recipe = FACTORY_RECIPE_BY_ORDINAL.get(recipe_ordinal, "smelting")
        tier = FACTORY_TIER_BY_META.get(metadata, "basic")
        converted["recipeType"] = recipe_ordinal
        converted["factoryRecipe"] = recipe
        converted["factoryTier"] = tier
        converted["recipeTicks"] = _int_value(nbt_1710.get("recipeTicks"), 0)
        progress = {}
        for key, value in nbt_1710.items():
            if key.startswith("progress") and key[len("progress") :].isdigit():
                progress[key] = _int_value(value)
        converted["progress"] = progress
        expected_target = f"mekanism:{tier}_{recipe}_factory"
        if target_te_id != expected_target:
            warnings.append(f"MEK-W-FACTORY-TARGET: oczekiwany target z recipeType to {expected_target}")
        return converted, warnings


class EnergyCubeConverter(BaseMekanismNBTConverter):
    @property
    def converter_name(self) -> str:
        return "energy_cube"

    def _convert(self, nbt_1710: dict[str, Any], target_te_id: str, block_id: str | None, metadata: int):
        warnings: list[str] = []
        converted = self._base_copy(nbt_1710, target_te_id, warnings)
        tier = _tier_name(nbt_1710.get("tier", metadata), metadata)
        converted["tier"] = tier
        energy = self._extract_energy(nbt_1710)
        converted["energyContainers"] = self._energy_container(energy, "EnergyCube", warnings)
        converted.pop("electricityStored", None)
        return converted, warnings


class GasTankConverter(BaseMekanismNBTConverter):
    @property
    def converter_name(self) -> str:
        return "gas_tank"

    def _convert(self, nbt_1710: dict[str, Any], target_te_id: str, block_id: str | None, metadata: int):
        warnings: list[str] = []
        converted = self._base_copy(nbt_1710, target_te_id, warnings)
        converted["tier"] = _tier_name(nbt_1710.get("tier", metadata), metadata)
        converted["dumping"] = _int_value(nbt_1710.get("dumping"), 0)
        gas_tank = nbt_1710.get("gasTank", {})
        converted["chemicalTank"] = _convert_gas_tank(gas_tank)
        converted.pop("gasTank", None)
        return converted, warnings


class BinConverter(BaseMekanismNBTConverter):
    @property
    def converter_name(self) -> str:
        return "bin"

    def _convert(self, nbt_1710: dict[str, Any], target_te_id: str, block_id: str | None, metadata: int):
        warnings: list[str] = []
        converted = self._base_copy(nbt_1710, target_te_id, warnings)
        converted["tier"] = _tier_name(nbt_1710.get("tier", metadata), metadata)
        for stack_key in ("itemType", "bottomStack", "topStack"):
            if isinstance(nbt_1710.get(stack_key), dict):
                converted[stack_key] = self._convert_item_stack(nbt_1710[stack_key])
        converted["itemCount"] = _int_value(nbt_1710.get("itemCount"), 0)
        return converted, warnings


class DigitalMinerConverter(MachineConverter):
    @property
    def converter_name(self) -> str:
        return "digital_miner"

    def _convert(self, nbt_1710: dict[str, Any], target_te_id: str, block_id: str | None, metadata: int):
        converted, warnings = super()._convert(nbt_1710, target_te_id, block_id, metadata)
        for key in ("radius", "minY", "maxY"):
            if key in nbt_1710:
                converted[key] = _int_value(nbt_1710[key])
        for key in ("doEject", "doPull", "silkTouch", "inverse"):
            converted[key] = bool(nbt_1710.get(key, False))
        converted["running"] = False
        if nbt_1710.get("running"):
            warnings.append("MEK-W-DIGITAL-MINER-RUNNING: resetuje running=false; target musi przeliczyc oresToMine")
        converted["filters"] = deepcopy(nbt_1710.get("filters", []))
        converted["inverseReplace"] = False
        converted["replaceStack"] = None
        for key in ("oresToMine", "replaceMap", "searcher", "clientToMine"):
            converted.pop(key, None)
        return converted, warnings


class FrequencyConverter(MachineConverter):
    @property
    def converter_name(self) -> str:
        return "frequency"

    def _convert(self, nbt_1710: dict[str, Any], target_te_id: str, block_id: str | None, metadata: int):
        converted, warnings = super()._convert(nbt_1710, target_te_id, block_id, metadata)
        frequency = _extract_frequency(nbt_1710)
        if frequency:
            converted["frequency"] = frequency
        owner_name = nbt_1710.get("owner") or nbt_1710.get("ownerName") or nbt_1710.get("Owner")
        owner_uuid = nbt_1710.get("ownerUUID") or nbt_1710.get("ownerUUIDMost")
        if owner_name:
            converted["ownerNameLegacy"] = owner_name
        if owner_uuid:
            converted["ownerUUID"] = owner_uuid
        elif owner_name:
            warnings.append("MEK-W-OWNER-UUID-MISSING: zachowano ownerNameLegacy, ale brak UUID wlasciciela")
        if "public" in nbt_1710:
            converted["public"] = bool(nbt_1710.get("public"))
        return converted, warnings


class MultiblockConverter(MachineConverter):
    @property
    def converter_name(self) -> str:
        return "multiblock"

    def _convert(self, nbt_1710: dict[str, Any], target_te_id: str, block_id: str | None, metadata: int):
        converted, warnings = super()._convert(nbt_1710, target_te_id, block_id, metadata)
        for key in ("structure", "structureFound", "multiblock", "clientHasStructure"):
            if key in converted:
                converted.pop(key, None)
                warnings.append(f"MEK-W-MULTIBLOCK-CACHE: pomijam `{key}`, target musi przeliczyc strukture")
        return converted, warnings


class ChemicalMachineConverter(MachineConverter):
    @property
    def converter_name(self) -> str:
        return "chemical_machine"


def _tier_name(value: Any, metadata: int) -> str:
    if isinstance(value, str):
        lowered = value.lower()
        if lowered in ("basic", "advanced", "elite", "ultimate", "creative"):
            return lowered
    return TIER_BY_META.get(_int_value(value, metadata), TIER_BY_META.get(metadata, "basic"))


def _convert_gas_tank(gas_tank: Any) -> dict[str, Any]:
    if not isinstance(gas_tank, dict):
        return {}
    stored = gas_tank.get("stored", {})
    if not isinstance(stored, dict):
        stored = {}
    gas_id = stored.get("gasName") or stored.get("gas") or stored.get("Gas") or stored.get("id")
    amount = stored.get("amount", gas_tank.get("amount", 0))
    return {
        "stored": {
            "chemical": gas_to_chemical_id(gas_id),
            "amount": _int_value(amount, 0),
        },
        "legacyGasTank": deepcopy(gas_tank),
    }


def gas_to_chemical_id(gas_id: str | None) -> str | None:
    if gas_id is None:
        return None
    stripped = str(gas_id).replace("gas:", "").replace("Mekanism:", "").lower()
    aliases = {
        "hydrogenchloride": "hydrogen_chloride",
        "sulfuricacid": "sulfuric_acid",
        "sulfurdioxide": "sulfur_dioxide",
        "sulfurtrioxide": "sulfur_trioxide",
    }
    return f"mekanism:{aliases.get(stripped, stripped)}"


def _extract_frequency(nbt: dict[str, Any]) -> dict[str, Any] | None:
    for key in ("frequency", "Frequency", "freq", "frequencyName"):
        if key in nbt:
            value = nbt[key]
            if isinstance(value, dict):
                return deepcopy(value)
            return {"name": str(value)}
    return None
