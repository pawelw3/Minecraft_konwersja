"""Registry of BuildCraft NBT converters wrapping simulation functions."""

from __future__ import annotations

from typing import Any

from ..simulations.engine_simulation import (
    EngineState1710,
    simulate_engine_conversion,
)
from ..simulations.factory_simulation import (
    PumpState1710,
    RefineryState1710,
    TankState1710,
    simulate_pump_conversion,
    simulate_refinery_conversion,
    simulate_tank_conversion,
)
from ..simulations.pipe_simulation import (
    PipeState1710,
    simulate_pipe_conversion,
)
from .base_converter import BaseBuildCraftNBTConverter, NBTConversionResult


class IdentityConverter(BaseBuildCraftNBTConverter):
    """No-op converter for blocks that don't need NBT transformation."""

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        source_metadata: int = 0,
    ) -> NBTConversionResult:
        return NBTConversionResult(success=True)


class RemoveConverter(BaseBuildCraftNBTConverter):
    """Converter for blocks that should be removed (no 1.18.2 equivalent)."""

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        source_metadata: int = 0,
    ) -> NBTConversionResult:
        return NBTConversionResult(
            success=True,
            warnings=["BuildCraft: block removed (no 1.18.2 equivalent)"],
        )


class EngineStoneConverter(BaseBuildCraftNBTConverter):
    """TileEngineStone (Stirling) -> thermal:dynamo_steam."""

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        source_metadata: int = 0,
    ) -> NBTConversionResult:
        state = EngineState1710.from_nbt(nbt_1710)
        result = simulate_engine_conversion(state)
        if result["action"] == "REMOVE":
            return NBTConversionResult(
                success=True,
                warnings=[result["reason"]],
            )
        target = result["target"]
        nbt_1182: dict[str, Any] = {}
        if target.inventory:
            nbt_1182["Items"] = target.inventory
        if target.energy_fe > 0:
            nbt_1182["energy"] = target.energy_fe
        return NBTConversionResult(
            success=True,
            converted_nbt=nbt_1182 if nbt_1182 else None,
            blockstate_props={"facing": target.facing} if target.facing else {},
            warnings=[result.get("note", "")] if result.get("note") else [],
        )


class EngineIronConverter(BaseBuildCraftNBTConverter):
    """TileEngineIron (Combustion) -> thermal:dynamo_compression."""

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        source_metadata: int = 0,
    ) -> NBTConversionResult:
        state = EngineState1710.from_nbt(nbt_1710)
        result = simulate_engine_conversion(state)
        if result["action"] == "REMOVE":
            return NBTConversionResult(
                success=True,
                warnings=[result["reason"]],
            )
        target = result["target"]
        nbt_1182: dict[str, Any] = {}
        if target.inventory:
            nbt_1182["Items"] = target.inventory
        if target.fluid_tanks:
            nbt_1182["Tanks"] = target.fluid_tanks
        if target.energy_fe > 0:
            nbt_1182["energy"] = target.energy_fe
        return NBTConversionResult(
            success=True,
            converted_nbt=nbt_1182 if nbt_1182 else None,
            blockstate_props={"facing": target.facing} if target.facing else {},
            warnings=[result.get("note", "")] if result.get("note") else [],
        )


class TankConverter(BaseBuildCraftNBTConverter):
    """TileTank -> mekanism:basic_fluid_tank."""

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        source_metadata: int = 0,
    ) -> NBTConversionResult:
        state = TankState1710.from_nbt(nbt_1710)
        result = simulate_tank_conversion(state)
        target = result["target"]
        nbt_1182: dict[str, Any] = {}
        if target.fluid_tanks:
            nbt_1182["Tanks"] = target.fluid_tanks
        return NBTConversionResult(
            success=True,
            converted_nbt=nbt_1182 if nbt_1182 else None,
            warnings=[result.get("note", "")] if result.get("note") else [],
        )


class PumpConverter(BaseBuildCraftNBTConverter):
    """TilePump -> mekanism:electric_pump."""

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        source_metadata: int = 0,
    ) -> NBTConversionResult:
        state = PumpState1710.from_nbt(nbt_1710)
        result = simulate_pump_conversion(state)
        target = result["target"]
        nbt_1182: dict[str, Any] = {}
        if target.fluid_tanks:
            nbt_1182["Tanks"] = target.fluid_tanks
        if target.energy_fe > 0:
            nbt_1182["energy"] = target.energy_fe
        return NBTConversionResult(
            success=True,
            converted_nbt=nbt_1182 if nbt_1182 else None,
            warnings=[result.get("note", "")] if result.get("note") else [],
        )


class RefineryConverter(BaseBuildCraftNBTConverter):
    """TileRefinery -> thermal:machine_refinery."""

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        source_metadata: int = 0,
    ) -> NBTConversionResult:
        state = RefineryState1710.from_nbt(nbt_1710)
        result = simulate_refinery_conversion(state)
        target = result["target"]
        nbt_1182: dict[str, Any] = {}
        if target.fluid_tanks:
            nbt_1182["Tanks"] = target.fluid_tanks
        if target.energy_fe > 0:
            nbt_1182["energy"] = target.energy_fe
        warnings = []
        if result.get("note"):
            warnings.append(result["note"])
        if result.get("warning"):
            warnings.append(result["warning"])
        return NBTConversionResult(
            success=True,
            converted_nbt=nbt_1182 if nbt_1182 else None,
            warnings=warnings,
        )


class PipeConverter(BaseBuildCraftNBTConverter):
    """GenericPipe -> pipez:universal_pipe (lub fluid/energy pipe)."""

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        source_metadata: int = 0,
    ) -> NBTConversionResult:
        state = PipeState1710.from_nbt(nbt_1710)
        result = simulate_pipe_conversion(state)
        replacement = result.get("replacement_block", "pipez:universal_pipe")
        warnings = [result["reason"]] if result.get("reason") else []
        # Uwaga: konwerter nie może zmienić block_id_1182 w event, ale może zwrócić
        # informację w blockstate lub dodatkowym polu. W praktyce router musi obsłużyć
        # zmianę block_id jeśli pipe ma być fluid/energy pipe.
        # Dla uproszczenia zwracamy sugerowany block_id jako dodatkowe info.
        return NBTConversionResult(
            success=True,
            blockstate_props={"_suggested_block_id": replacement},
            warnings=warnings,
        )


# ──────────────────────────────────────────────────────────────────────────────
# Public registry
# ──────────────────────────────────────────────────────────────────────────────

NBT_CONVERTERS: dict[str, BaseBuildCraftNBTConverter] = {
    "identity": IdentityConverter(),
    "remove": RemoveConverter(),
    "engine_stone": EngineStoneConverter(),
    "engine_iron": EngineIronConverter(),
    "tank": TankConverter(),
    "pump": PumpConverter(),
    "refinery": RefineryConverter(),
    "pipe": PipeConverter(),
}


def get_nbt_converter(name: str) -> BaseBuildCraftNBTConverter:
    return NBT_CONVERTERS.get(name, NBT_CONVERTERS["identity"])
