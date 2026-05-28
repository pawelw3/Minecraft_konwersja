"""
Konwerter Extra Utilities 1.7.10 → 1.18.2.

Strategia hybrydowa — poszczególne funkcje ExU mapowane na dedykowane mody:
- Generatory      → Thermal Series / Mekanism Generators
- Magnum Torch    → Torchmaster Mega Torch
- Cursed Earth    → Cursed Earth mod
- Angel Block     → Angel Block Renewed
- Trash Can       → Trash Cans
- Sound Muffler   → Extreme Sound Muffler
"""
from __future__ import annotations

from typing import Any

from converters.extrautils.mappings.block_mappings import (
    BlockMapping,
    get_mapping,
    is_extrautils_block,
    TE_ID_TO_BLOCK,
)
from converters.extrautils.simulations.extrautils_simulation import (
    simulate_extrautils_conversion,
)


class ConversionResult:
    def __init__(
        self,
        success: bool,
        block_id_1182: str | None = None,
        blockstate_props: dict[str, Any] | None = None,
        nbt_1182: dict[str, Any] | None = None,
        errors: list[str] | None = None,
        warnings: list[str] | None = None,
        event: Any = None,
    ):
        self.success = success
        self.block_id_1182 = block_id_1182
        self.blockstate_props = blockstate_props or {}
        self.nbt_1182 = nbt_1182
        self.errors = errors or []
        self.warnings = warnings or []
        self.event = event


class ExtraUtilsConverter:
    """Konwerter bloków i tile entities Extra Utilities."""

    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"
    MOD = "extrautils"

    # ──────────────────────────────────────────────────────────────────────────
    # Bloki
    # ──────────────────────────────────────────────────────────────────────────

    def convert_block(
        self,
        block_id_1710: str,
        metadata: int = 0,
        nbt_1710: dict[str, Any] | None = None,
        position: tuple[int, int, int] = (0, 0, 0),
    ) -> ConversionResult:
        """Konwertuj blok (z opcjonalnym TE NBT) z 1.7.10 na 1.18.2."""
        if not is_extrautils_block(block_id_1710):
            return ConversionResult(
                success=False,
                errors=[f"EXU-E-NOT-EXTRAUTILS: {block_id_1710}"],
            )

        mapping = get_mapping(block_id_1710, metadata)
        if mapping is None:
            return ConversionResult(
                success=False,
                errors=[f"EXU-E-BLOCK-NOT-MAPPED: {block_id_1710} meta={metadata}"],
            )

        sim_result = simulate_extrautils_conversion(
            block_id_1710, metadata, nbt_1710, mapping
        )

        warnings = list(sim_result.get("warnings", []))
        errors = list(sim_result.get("errors", []))

        return ConversionResult(
            success=not errors,
            block_id_1182=sim_result["block_id_1182"],
            blockstate_props=sim_result.get("blockstate_props"),
            nbt_1182=sim_result.get("nbt_1182"),
            errors=errors,
            warnings=warnings,
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Tile Entities
    # ──────────────────────────────────────────────────────────────────────────

    def convert_tile_entity(
        self,
        te_id: str,
        nbt_1710: dict[str, Any],
        metadata: int = 0,
        position: tuple[int, int, int] = (0, 0, 0),
    ) -> ConversionResult:
        """Konwertuj Tile Entity Extra Utilities.

        Dla wielu bloków ExU TE id jest inne niż block registry name.
        Używamy TE_ID_TO_BLOCK aby wywnioskować block_id i metadata.
        """
        # Normalizacja TE id — usuwamy wiodący namespace jeśli jest "extrautils:"
        bare_te = te_id.split(":")[-1] if ":" in te_id else te_id

        # Najpierw spróbuj bezpośrednie mapowanie TE → (block_id, meta)
        if te_id in TE_ID_TO_BLOCK:
            block_id, meta = TE_ID_TO_BLOCK[te_id]
            return self.convert_block(block_id, meta, nbt_1710, position)

        # Fallback: jeśli TE id zaczyna się od "extrautils:generator"
        if te_id.startswith("extrautils:generator"):
            suffix = te_id[len("extrautils:generator"):]
            # Znajdź meta dla danego suffixu
            for (bid, meta), mapping in get_all_generator_mappings().items():
                if bid == "extrautils:generator" and mapping.notes and suffix in mapping.notes.lower():
                    return self.convert_block(bid, meta, nbt_1710, position)
            # Jeśli nie znaleziono, spróbuj domyślnego bloku generator
            return self.convert_block("extrautils:generator", metadata, nbt_1710, position)

        # Jeśli nie ma mapowania — zwróć błąd
        return ConversionResult(
            success=False,
            errors=[f"EXU-E-TE-NOT-MAPPED: {te_id}"],
        )


def get_all_generator_mappings() -> dict[tuple[str, int], BlockMapping]:
    """Pomocnicza funkcja zwracająca wszystkie mapowania generatorów."""
    from converters.extrautils.mappings.block_mappings import STATIC_MAPPINGS
    return {
        k: v for k, v in STATIC_MAPPINGS.items()
        if k[0].startswith("extrautils:generator")
    }
