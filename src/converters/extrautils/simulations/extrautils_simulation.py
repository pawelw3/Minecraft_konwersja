"""
Symulacje konwersji Extra Utilities 1.7.10 → 1.18.2.

Dla prostych bloków (dekoracyjne / utility) konwersja jest bezstanowa —
wystarczy zamiana block_id. Dla generatorów przepisujemy podstawowe NBT
(energia zgromadzona, rotacja, tank płynów) przez dedykowane NBT converters.
"""
from __future__ import annotations

from typing import Any

from converters.extrautils.nbt_converters.generator_converter import convert_generator_nbt
from converters.extrautils.nbt_converters.filing_cabinet_converter import convert_filing_cabinet_nbt


def simulate_extrautils_conversion(
    block_id_1710: str,
    metadata: int,
    nbt_1710: dict[str, Any] | None,
    mapping,
) -> dict[str, Any]:
    """Zasymuluj konwersję bloku ExU.

    Returns dict z polami:
        block_id_1182: str
        blockstate_props: dict | None
        nbt_1182: dict | None
        warnings: list[str]
        errors: list[str]
    """
    nbt_1710 = nbt_1710 or {}
    warnings: list[str] = []
    errors: list[str] = []
    nbt_1182: dict[str, Any] | None = None
    blockstate_props: dict[str, Any] | None = None

    target_id = mapping.target_block_id
    converter_key = mapping.nbt_converter

    if converter_key == "generator":
        # Użyj dedykowanego konwertera NBT dla generatorów
        conv_result = convert_generator_nbt(nbt_1710, target_id)
        nbt_1182 = conv_result.get("nbt")
        blockstate_props = conv_result.get("blockstate_props")
        warnings.extend(conv_result.get("warnings", []))

    elif converter_key == "filing_cabinet":
        conv_result = convert_filing_cabinet_nbt(nbt_1710, target_id)
        nbt_1182 = conv_result.get("nbt")
        blockstate_props = conv_result.get("blockstate_props")
        warnings.extend(conv_result.get("warnings", []))

    elif target_id == "torchmaster:mega_torch":
        # Mega Torch w 1.18.2 (Torchmaster) nie wymaga NBT.
        pass

    elif target_id in ("cursedearth:cursed_earth", "angelblockrenewed:angel_block"):
        # Proste bloki bez NBT
        pass

    elif target_id.startswith("trashcans:"):
        # Trash Cans mogą mieć filtry w 1.18.2, ale ExU 1.7.10 nie miało filtrów.
        pass

    elif target_id.startswith("conversion_placeholders:"):
        # Placeholdery — zachowaj oryginalne NBT
        nbt_1182 = dict(nbt_1710) if nbt_1710 else None

    else:
        # Dla pozostałych — prosta zamiana block_id.
        pass

    if mapping.notes:
        warnings.append(f"EXU-W-MAPPING: {mapping.notes}")

    return {
        "block_id_1182": target_id,
        "blockstate_props": blockstate_props,
        "nbt_1182": nbt_1182,
        "warnings": warnings,
        "errors": errors,
    }
