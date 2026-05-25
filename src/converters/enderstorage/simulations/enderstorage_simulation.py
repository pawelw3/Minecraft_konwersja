"""
Symulacje konwersji NBT EnderStorage 1.7.10 → 1.18.2.
"""

from __future__ import annotations

from typing import Any


def convert_frequency_nbt(te_nbt: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    """Konwertuje NBT częstotliwości EnderStorage.

    Wejście (1.7.10):
        te_nbt = {
            "id": "Ender Chest" | "Ender Tank",
            "freq": int,     # packed: top=(freq>>8)&0xF, middle=(freq>>4)&0xF, bottom=freq&0xF
            "owner": string, # "global" lub UUID
        }

    Wyjście (1.18.2):
        nbt_1182 = {
            "Frequency": {
                "left": int,
                "middle": int,
                "right": int,
                "owner": UUID,  # optional
            }
        }
    """
    warnings: list[str] = []
    freq = te_nbt.get("freq", 0)
    top = (freq >> 8) & 0xF
    middle = (freq >> 4) & 0xF
    bottom = freq & 0xF

    # Mapowanie kolorów: w 1.7.10 kolejność to top, left, right (z getColoursFromFreq)
    # ai[0] = (freq >> 8) & 0xF  -> top
    # ai[1] = (freq >> 4) & 0xF  -> left
    # ai[2] = freq & 0xF          -> right
    # W 1.18.2: left, middle, right
    # Zakładamy że top -> left, left -> middle, right -> right
    # (To może wymagać weryfikacji w grze)
    nbt_1182: dict[str, Any] = {
        "Frequency": {
            "left": top,
            "middle": middle,
            "right": bottom,
        }
    }

    owner = te_nbt.get("owner", "global")
    if owner and owner != "global":
        nbt_1182["Frequency"]["owner"] = owner

    return nbt_1182, warnings


def simulate_enderstorage_conversion(
    block_id_1710: str,
    metadata: int,
    te_nbt: dict[str, Any] | None,
) -> dict[str, Any]:
    """Symulacja end-to-end konwersji EnderStorage."""
    from ..mappings.block_mappings import get_mapping

    result: dict[str, Any] = {
        "block_id_1182": None,
        "blockstate_props": {},
        "nbt_1182": None,
        "warnings": [],
        "errors": [],
    }

    mapping = get_mapping(block_id_1710, metadata)
    if mapping is None:
        result["errors"].append(f"ES-E-UNKNOWN-BLOCK: {block_id_1710}:{metadata}")
        result["block_id_1182"] = "conversion_placeholders:block_entity_placeholder"
        return result

    result["block_id_1182"] = mapping.target_block_id

    if te_nbt is None:
        return result

    nbt_1182, warnings = convert_frequency_nbt(te_nbt)
    result["nbt_1182"] = nbt_1182
    result["warnings"].extend(warnings)

    return result
