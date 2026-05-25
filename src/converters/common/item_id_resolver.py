"""
Resolver numerycznych ID przedmiotow (1.7.10) -> string ID (1.18.2).

Wczytuje mapowanie z level.dat mapy 1.7.10 (FML/ItemData).
Mozna uzyc jako singleton lub wczytac raz na sesje.
"""

from __future__ import annotations

import gzip
import json
import os
from pathlib import Path
from typing import Dict, Optional

# Singleton cache
_item_id_cache: Optional[Dict[str, str]] = None


def load_item_id_mapping(level_dat_path: str | Path) -> Dict[str, str]:
    """Wczytuje mapowanie numerycznych ID -> string ID z level.dat."""
    global _item_id_cache
    if _item_id_cache is not None:
        return _item_id_cache

    level_dat_path = Path(level_dat_path)
    if not level_dat_path.exists():
        raise FileNotFoundError(f"level.dat not found: {level_dat_path}")

    # Dynamiczny import aby uniknac cyklicznych zaleznosci
    import sys
    from pathlib import Path as P
    src_dir = P(__file__).parent.parent.parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    from minecraft_map_parser.nbt_parser import parse_nbt

    with open(level_dat_path, "rb") as f:
        data = f.read()
    uncompressed = gzip.decompress(data)
    nbt = parse_nbt(uncompressed)

    fml = nbt.get("FML", {})
    if hasattr(fml, "value"):
        fml = fml.value

    item_data = fml.get("ItemData", [])
    if hasattr(item_data, "value"):
        item_data = item_data.value

    mapping: Dict[str, str] = {}
    for item in item_data:
        if hasattr(item, "value"):
            item = item.value
        if isinstance(item, dict):
            name = None
            id_val = None
            for k, v in item.items():
                key = k.value if hasattr(k, "value") else k
                val = v.value if hasattr(v, "value") else v
                if key == "K":
                    name = str(val)
                    if name:
                        name = name[1:]  # Usun typ (pierwszy bajt)
                elif key == "V":
                    id_val = val
            if name and id_val is not None:
                mapping[str(id_val)] = name

    _item_id_cache = mapping
    return mapping


def resolve_item_id(numeric_id: str | int, level_dat_path: str | Path | None = None) -> str:
    """
    Konwertuje numeryczne ID przedmiotu na string ID.

    Jesli nie zna mapowania, zwraca oryginalna wartosc.
    """
    key = str(numeric_id)

    # Jesli juz jest stringiem (np. "minecraft:diamond"), zwroc bez zmian
    if ":" in key:
        return key

    global _item_id_cache
    if _item_id_cache is None and level_dat_path is not None:
        load_item_id_mapping(level_dat_path)

    if _item_id_cache is not None:
        return _item_id_cache.get(key, key)

    return key


def resolve_item_ids_in_inventory(
    items: list[dict],
    level_dat_path: str | Path | None = None,
) -> list[dict]:
    """Przechodzi przez liste itemow i zamienia numeryczne ID na string ID."""
    result = []
    for item in items:
        new_item = dict(item)
        if "id" in new_item:
            new_item["id"] = resolve_item_id(new_item["id"], level_dat_path)
        result.append(new_item)
    return result
