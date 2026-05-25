"""Konwerter NBT dla Cyanite Reprocessor."""

from __future__ import annotations

from typing import Any

from .base_converter import IdentityBiggerReactorsConverter, NBTConversionResult


class CyaniteReprocessorConverter(IdentityBiggerReactorsConverter):
    """Konwerter dla Cyanite Reprocessor — zachowuje inventory, energie i progress."""

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

        # Inventory
        if "Items" in nbt_1710:
            nbt["Items"] = self._convert_items(nbt_1710["Items"])
            warnings.append("BIG-W-INVENTORY: przekonwertowano inventory Cyanite Reprocessor")

        # Energy (RF -> FE 1:1)
        if "energyStored" in nbt_1710:
            nbt["energy"] = nbt_1710["energyStored"]

        # Progress
        if "cookTime" in nbt_1710:
            nbt["progress"] = nbt_1710["cookTime"]
        if "processTime" in nbt_1710:
            nbt["progress"] = nbt_1710["processTime"]

        return NBTConversionResult(
            converted_nbt=nbt,
            warnings=warnings,
        )

    @staticmethod
    def _convert_items(items: list[dict]) -> list[dict]:
        converted = []
        for item in items:
            if not isinstance(item, dict):
                continue
            new_item = dict(item)
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
