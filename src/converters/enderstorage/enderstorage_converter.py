"""
Konwerter EnderStorage 1.7.10 → 1.18.2.
"""

from __future__ import annotations

from typing import Any

from converters.enderstorage.mappings.block_mappings import get_mapping, is_enderstorage_block
from converters.enderstorage.simulations.enderstorage_simulation import simulate_enderstorage_conversion


class ConversionResult:
    def __init__(self, success, block_id_1182=None, blockstate_props=None, nbt_1182=None, errors=None, warnings=None, event=None):
        self.success = success
        self.block_id_1182 = block_id_1182
        self.blockstate_props = blockstate_props or {}
        self.nbt_1182 = nbt_1182
        self.errors = errors or []
        self.warnings = warnings or []
        self.event = event


class EnderStorageConverter:
    MOD = "enderstorage"

    def convert_block(
        self,
        block_id_1710: str,
        metadata: int = 0,
        nbt_1710: dict[str, Any] | None = None,
        position: tuple[int, int, int] = (0, 0, 0),
    ) -> ConversionResult:
        if not is_enderstorage_block(block_id_1710):
            return ConversionResult(
                success=False,
                errors=[f"ES-E-NOT-ENDERSTORAGE: {block_id_1710}"],
            )

        mapping = get_mapping(block_id_1710, metadata)
        if mapping is None:
            return ConversionResult(
                success=False,
                errors=[f"ES-E-BLOCK-NOT-MAPPED: {block_id_1710} meta={metadata}"],
            )

        sim_result = simulate_enderstorage_conversion(block_id_1710, metadata, nbt_1710)

        warnings = list(sim_result.get("warnings", []))
        errors = list(sim_result.get("errors", []))

        if mapping.notes:
            warnings.append(f"ES-W-MAPPING: {mapping.notes}")

        return ConversionResult(
            success=not errors,
            block_id_1182=sim_result["block_id_1182"],
            blockstate_props=sim_result.get("blockstate_props"),
            nbt_1182=sim_result.get("nbt_1182"),
            errors=errors,
            warnings=warnings,
        )

    def convert_tile_entity(
        self,
        te_id: str,
        nbt_1710: dict[str, Any],
        metadata: int = 0,
        position: tuple[int, int, int] = (0, 0, 0),
    ) -> ConversionResult:
        # EnderStorage 1.7.10: jeden blok "EnderStorage:enderChest" z meta 0/1
        # TE IDs: "Ender Chest", "Ender Tank"
        block_id = "EnderStorage:enderChest"
        return self.convert_block(
            block_id_1710=block_id,
            metadata=metadata,
            nbt_1710=nbt_1710,
            position=position,
        )
