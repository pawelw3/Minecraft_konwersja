# dump_te.py
from typing import Optional, List, Tuple
from amulet_nbt import TAG_Compound, NamedTag
from core import raw_root_for_chunk

def _to_python(obj):
    """Rekurencyjna konwersja amulet_nbt -> czyste typy Pythona (JSON-owalne)."""
    # amulet-nbt tag
    try:
        from amulet_nbt import BaseTag
        if isinstance(obj, BaseTag):
            try:
                return obj.py()  # nowsze API
            except Exception:
                return _to_python(getattr(obj, "value", None))
    except Exception:
        pass

    if isinstance(obj, dict):
        return {str(k): _to_python(v) for k, v in obj.items()}

    if isinstance(obj, NamedTag):
        return _to_python(obj.tag)

    if isinstance(obj, (list, tuple)):
        return [_to_python(x) for x in obj]

    try:
        import numpy as np
        if isinstance(obj, np.generic):
            return obj.item()
    except Exception:
        pass

    if isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj

    return str(obj)

def _find_te_list_container(level_tag: TAG_Compound):
    """
    Zwraca (lista_TE, nazwa_klucza), obsługując:
      - 1.7.x: 'TileEntities'
      - 1.13+ / 1.18.x: 'block_entities'
    Dodatkowo działa „miękko” na warianty wielkości liter.
    """
    # typowe klucze
    if "TileEntities" in level_tag:
        return level_tag["TileEntities"], "TileEntities"
    if "block_entities" in level_tag:
        return level_tag["block_entities"], "block_entities"

    # miękkie dopasowanie (na wszelki wypadek różnych buildów)
    for k in level_tag.keys():
        ks = str(k)
        if ks.lower() == "tileentities":
            return level_tag[k], ks
        if ks.lower() == "block_entities":
            return level_tag[k], ks

    # brak listy TE/BE
    return None, None

def _get_id_str(te_compound: TAG_Compound) -> str:
    # w 1.7.x bywało 'id' bez namespace; w 1.18.x też 'id' ale namespaced
    try:
        id_tag = te_compound.get("id", None)
        if id_tag is None:
            return ""
        if hasattr(id_tag, "py"):
            return id_tag.py()
        if hasattr(id_tag, "value"):
            return str(id_tag.value)
        return str(id_tag)
    except Exception:
        return ""

def _collect_filtered_tes(level_tag: TAG_Compound):
    """
    Zwraca listę TE/BE po odfiltrowaniu niechcianych wpisów (RCHiddenTile).
    Działa dla 1.7.x i 1.18.x.
    """
    te_list, key_name = _find_te_list_container(level_tag)
    out = []
    if te_list is None:
        return out, key_name

    for te in te_list:
        if not isinstance(te, TAG_Compound):
            continue
        te_id = _get_id_str(te)
        if te_id == "RCHiddenTile":   # ignoruj Railcraftowe „niewidki”
            continue
        out.append(te)
    return out, key_name

def dump_tile_entities_json(old_world, dim_key: str, chunk: Tuple[int,int], out_path: str) -> int:
    """
    Zapisuje TE/BE z chunka do JSON:
      - 1.7.x -> 'TileEntities'
      - 1.18.x -> 'block_entities'
    Ignoruje id == 'RCHiddenTile'.
    """
    cx, cz = chunk
    root = raw_root_for_chunk(old_world, dim_key, cx, cz)
    if root is None:
        raise RuntimeError(f"Brak surowego NBT dla chunka ({cx},{cz})")

    level_tag = root["Level"] if "Level" in root else root
    te_list, key_used = _collect_filtered_tes(level_tag)

    data = {
        "chunk": {"xPos": cx, "zPos": cz},
        "container_key": key_used,          # np. 'TileEntities' lub 'block_entities'
        "tile_entities_count": len(te_list),
        "tile_entities": _to_python(te_list),
    }

    import json, os
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return len(te_list)

def dump_tile_entities_json_many(old_world, dim_key: str, chunks: List[Tuple[int,int]], out_path: str) -> int:
    """Zrzuca TE/BE dla wielu chunków do jednego pliku JSON (ignoruje RCHiddenTile)."""
    all_items = []
    total = 0
    for cx, cz in chunks:
        try:
            root = raw_root_for_chunk(old_world, dim_key, cx, cz)
            if root is None:
                all_items.append({"chunk": {"xPos": cx, "zPos": cz}, "tile_entities_count": 0, "tile_entities": []})
                continue
            level_tag = root["Level"] if "Level" in root else root
            te_list, key_used = _collect_filtered_tes(level_tag)
            total += len(te_list)
            all_items.append({
                "chunk": {"xPos": cx, "zPos": cz},
                "container_key": key_used,
                "tile_entities_count": len(te_list),
                "tile_entities": _to_python(te_list),
            })
        except Exception as e:
            all_items.append({
                "chunk": {"xPos": cx, "zPos": cz},
                "error": str(e)
            })

    data = {
        "range_total_chunks": len(chunks),
        "tile_entities_total": total,
        "items": all_items
    }
    import json, os
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return total
