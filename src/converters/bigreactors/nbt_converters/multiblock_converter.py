"""Konwertery NBT dla multiblokow reaktora i turbiny Big Reactors."""

from __future__ import annotations

from typing import Any

from .base_converter import IdentityBiggerReactorsConverter, NBTConversionResult


class MultiblockReactorConverter(IdentityBiggerReactorsConverter):
    """Konwerter dla TE reaktora (casing, control rod, coolant port, itp.).

    Zachowuje podstawowe pola (x,y,z,id,facing). Dla control rod probuje
    zachowac poziom wciagniecia (insertion). Dla power tap / coolant port
    zachowuje bufor energii / cieczy jesli jest dostepny (ograniczony)."""

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        metadata: int = 0,
    ) -> NBTConversionResult:
        result = super().convert(nbt_1710, target_block_id, source_block_id, metadata)
        nbt = result.converted_nbt or {}
        warnings = list(result.warnings)

        # Control rod insertion (zazwyczaj int 0-100)
        if "controlRodInsertion" in nbt_1710:
            nbt["insertion"] = nbt_1710["controlRodInsertion"]

        # Aktywnosc reaktora (nie zawsze jest zapisywana w TE, ale jesli tak)
        if "reactorActive" in nbt_1710:
            nbt["active"] = bool(nbt_1710["reactorActive"])

        # Energy stored (power tap)
        if "energyStored" in nbt_1710 and nbt_1710["energyStored"]:
            # BiggerReactors uzywa FE; stara wartosc RF jest kompatybilna 1:1
            nbt["energy"] = nbt_1710["energyStored"]
            warnings.append("BIG-W-ENERGY: zachowano energie RF jako FE (1:1)")

        # Temperatura (jako ciekawostka / diagnostyka)
        if "heat" in nbt_1710:
            nbt["temperature"] = nbt_1710["heat"]

        return NBTConversionResult(
            converted_nbt=nbt,
            warnings=warnings,
        )


class ReactorAccessPortConverter(IdentityBiggerReactorsConverter):
    """Konwerter dla Reactor Access Port — zachowuje inventory."""

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        metadata: int = 0,
    ) -> NBTConversionResult:
        result = super().convert(nbt_1710, target_block_id, source_block_id, metadata)
        nbt = result.converted_nbt or {}
        warnings = list(result.warnings)

        if "Items" in nbt_1710:
            nbt["Items"] = self._convert_items(nbt_1710["Items"])
            warnings.append("BIG-W-INVENTORY: przekonwertowano inventory Access Port")

        # Input/output mode jesli istnieje
        if "inlet" in nbt_1710:
            nbt["inlet"] = nbt_1710["inlet"]

        return NBTConversionResult(
            converted_nbt=nbt,
            warnings=warnings,
        )

    @staticmethod
    def _convert_items(items: list[dict]) -> list[dict]:
        """Przeksztalc item stacki 1.7.10 -> 1.18.2 (podstawowa zamiana ID)."""
        converted = []
        for item in items:
            if not isinstance(item, dict):
                continue
            new_item = dict(item)
            # Zamiana nazw materialow
            item_id = str(new_item.get("id", ""))
            if item_id == "BigReactors:ingotYellorium":
                new_item["id"] = "biggerreactors:uranium_ingot"
            elif item_id == "BigReactors:ingotBlutonium":
                new_item["id"] = "biggerreactors:blutonium_ingot"
            elif item_id == "BigReactors:ingotCyanite":
                new_item["id"] = "biggerreactors:cyanite_ingot"
            elif item_id == "BigReactors:ingotGraphite":
                new_item["id"] = "biggerreactors:graphite_ingot"
            elif item_id == "BigReactors:ingotLudicrite":
                new_item["id"] = "biggerreactors:ludicrite_ingot"
            converted.append(new_item)
        return converted


class MultiblockTurbineConverter(IdentityBiggerReactorsConverter):
    """Konwerter dla TE turbiny."""

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        metadata: int = 0,
    ) -> NBTConversionResult:
        result = super().convert(nbt_1710, target_block_id, source_block_id, metadata)
        nbt = result.converted_nbt or {}
        warnings = list(result.warnings)

        # Energy stored
        if "energyStored" in nbt_1710 and nbt_1710["energyStored"]:
            nbt["energy"] = nbt_1710["energyStored"]
            warnings.append("BIG-W-ENERGY: zachowano energie RF jako FE (1:1)")

        # Fluid tanks (turbine fluid port)
        if "tanks" in nbt_1710:
            # BiggerReactors uzywa innego formatu tankow, wiec tylko
            # diagnostyka — pełna konwersja wymaga znajomosci formatu Phosphophyllite
            warnings.append("BIG-W-FLUID: zawartosc tankow turbiny wymaga recznej weryfikacji")

        return NBTConversionResult(
            converted_nbt=nbt,
            warnings=warnings,
        )
