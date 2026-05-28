"""Reliquary mod converter: 1.7.10 → 1.18.2.

Handles three TileEntities:
  - reliquaryAltar   → reliquary:alkahestry_altar   (NBT identical, key-change only)
  - reliquaryCauldron → reliquary:apothecary_cauldron (hasGlowstone→int, liquidLevel, potionEssence)
  - apothecaryMortar → reliquary:apothecary_mortar  (inventory format remap)
"""
from __future__ import annotations

from typing import Any

from converters.reliquary.mappings import TE_ID_TO_BLOCK
from converters.reliquary.simulations.cauldron_sim import CauldronConverter
from converters.reliquary.simulations.mortar_sim import MortarConverter


class ConversionResult:
    def __init__(
        self,
        success: bool,
        block_id_1182: str | None = None,
        nbt_1182: dict[str, Any] | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
    ):
        self.success = success
        self.block_id_1182 = block_id_1182
        self.nbt_1182 = nbt_1182
        self.warnings = warnings or []
        self.errors = errors or []


class ReliquaryConverter:
    """Converts Reliquary TileEntities from 1.7.10 to 1.18.2."""

    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"
    MOD = "reliquary"

    def __init__(self):
        self._cauldron = CauldronConverter()
        self._mortar = MortarConverter()

    def convert_tile_entity(
        self,
        te_id: str,
        nbt_1710: dict[str, Any],
        metadata: int = 0,
        position: tuple[int, int, int] = (0, 0, 0),
    ) -> ConversionResult:
        """Convert a Reliquary TileEntity.

        Args:
            te_id: 1.7.10 TE registry name (e.g. "reliquaryAltar")
            nbt_1710: raw NBT dict from 1.7.10 chunk
            metadata: block metadata (used for cauldron liquidLevel)
            position: world position (unused, kept for interface consistency)

        Returns:
            ConversionResult with block_id_1182 and nbt_1182
        """
        block_id = TE_ID_TO_BLOCK.get(te_id)
        if block_id is None:
            return ConversionResult(
                success=False,
                errors=[f"Unknown Reliquary TE id: {te_id}"],
            )

        if te_id == "reliquaryAltar":
            return self._convert_altar(nbt_1710, block_id)

        if te_id == "reliquaryCauldron":
            return self._convert_cauldron(nbt_1710, metadata, block_id)

        if te_id == "apothecaryMortar":
            return self._convert_mortar(nbt_1710, block_id)

        return ConversionResult(success=False, errors=[f"Unhandled TE: {te_id}"])

    # ------------------------------------------------------------------
    # Internal converters
    # ------------------------------------------------------------------

    def _convert_altar(
        self, nbt_1710: dict[str, Any], block_id: str
    ) -> ConversionResult:
        """Alkahestry Altar: NBT is identical between versions."""
        nbt_1182: dict[str, Any] = {}
        for key in ("cycleTime", "redstoneCount", "isActive"):
            if key in nbt_1710:
                nbt_1182[key] = nbt_1710[key]
        return ConversionResult(
            success=True,
            block_id_1182=block_id,
            nbt_1182=nbt_1182 if nbt_1182 else None,
        )

    def _convert_cauldron(
        self,
        nbt_1710: dict[str, Any],
        block_meta: int,
        block_id: str,
    ) -> ConversionResult:
        """Apothecary Cauldron: hasGlowstone→int, liquidLevel from meta, potionEssence→effects."""
        nbt_1182, warnings = self._cauldron.convert_to_nbt(nbt_1710, block_meta)
        return ConversionResult(
            success=True,
            block_id_1182=block_id,
            nbt_1182=nbt_1182,
            warnings=warnings,
        )

    def _convert_mortar(
        self, nbt_1710: dict[str, Any], block_id: str
    ) -> ConversionResult:
        """Apothecary Mortar: Items (vanilla list) → items (ItemStackHandler)."""
        nbt_1182, warnings = self._mortar.convert(nbt_1710)
        return ConversionResult(
            success=True,
            block_id_1182=block_id,
            nbt_1182=nbt_1182,
            warnings=warnings,
        )
