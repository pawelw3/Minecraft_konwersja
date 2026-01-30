# -*- coding: utf-8 -*-
"""
Zapisuje sekcję 'Level' wybranego chunka do JSON, odporne na numpy.int32 itp.

Użycie:
  - Ustaw ścieżki i współrzędne w sekcji KONFIG
  - python dump_chunk_level_to_json.py
"""

import os
import json

# ======== KONFIG ========
WORLD_DIR      = r"C:\Users\pawel\AppData\Roaming\.minecraft\saves\konwersja1"   # <--- PODMIEŃ: folder świata
CHUNK_X        = -5                        # globalny chunk X
CHUNK_Z        = -5                        # globalny chunk Z
OUT_JSON_PATH  = r".\chunk_-5_-5_Level.json"
PREFERRED_DIM  = "minecraft:overworld"     # zmień na the_nether / the_end, jeśli trzeba
# ========================

# --- importy kompatybilne z różnymi wersjami amulet-core
try:
    from amulet.api.level import load_level
except Exception:
    import amulet as _amulet_pkg
    load_level = _amulet_pkg.load_level

from amulet_nbt import (
    NamedTag, TAG_Compound, TAG_List,
    TAG_String, TAG_Int, TAG_Short, TAG_Long, TAG_Float, TAG_Double, TAG_Byte,
    TAG_Byte_Array, TAG_Int_Array, TAG_Long_Array
)

# Spróbuj załadować numpy – jeśli jest, obsłużymy wszystkie typy numpy w encoderze.
try:
    import numpy as np
    HAVE_NUMPY = True
except Exception:
    HAVE_NUMPY = False

def pick_dimension_key(level_wrapper, preferred="minecraft:overworld"):
    """Zwróć istniejący klucz wymiaru (string)."""
    keys = list(level_wrapper.dimensions)
    if preferred in keys:
        return preferred
    return keys[0] if keys else preferred

def nbt_to_python(value):
    """
    Ostrożna, rekursywna konwersja amulet_nbt -> prymitywy Pythona.
    Nie musi złapać WSZYSTKIEGO (bo default encoder i tak zamknie temat),
    ale spłaszczy NamedTag i typy NBT.
    """
    # numpy prymitywy
    if HAVE_NUMPY and isinstance(value, (np.integer, np.floating, np.bool_)):
        return value.item()
    # numpy tablice
    if HAVE_NUMPY and isinstance(value, np.ndarray):
        return [nbt_to_python(v) for v in value.tolist()]

    if isinstance(value, NamedTag):
        return nbt_to_python(value.tag)
    if isinstance(value, TAG_Compound):
        return {k: nbt_to_python(v) for k, v in value.items()}
    if isinstance(value, TAG_List):
        return [nbt_to_python(v) for v in value]
    if isinstance(value, (TAG_String, TAG_Int, TAG_Short, TAG_Long, TAG_Float, TAG_Double, TAG_Byte)):
        return value.value
    if isinstance(value, (TAG_Byte_Array, TAG_Int_Array, TAG_Long_Array)):
        # arrays -> zwykłe listy
        return list(value)

    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [nbt_to_python(v) for v in value]
    if isinstance(value, dict):
        return {k: nbt_to_python(v) for k, v in value.items()}

    # Ostatnia próba...
    try:
        return int(value)
    except Exception:
        try:
            return float(value)
        except Exception:
            return str(value)

class NumpyJSONEncoder(json.JSONEncoder):
    """
    Encoder JSON, który potrafi zamienić KAŻDY obiekt numpy.* i resztki NBT
    na typy akceptowalne przez json.
    """
    def default(self, obj):
        # numpy skalarne typy
        if HAVE_NUMPY:
            if isinstance(obj, (np.integer, np.floating, np.bool_)):
                return obj.item()
            if isinstance(obj, np.ndarray):
                return obj.tolist()

        # amulet_nbt typy (gdyby coś przeszło)
        if isinstance(obj, NamedTag):
            return nbt_to_python(obj)
        if isinstance(obj, (TAG_Compound, TAG_List,
                            TAG_String, TAG_Int, TAG_Short, TAG_Long, TAG_Float, TAG_Double, TAG_Byte,
                            TAG_Byte_Array, TAG_Int_Array, TAG_Long_Array)):
            return nbt_to_python(obj)

        # a jak nie – ostatni fallback
        return super().default(obj)

def dump_level_section_to_json(world_dir: str, cx: int, cz: int, out_path: str, preferred_dim: str = PREFERRED_DIM):
    level = load_level(world_dir)
    try:
        dim_key = pick_dimension_key(level.level_wrapper, preferred_dim)
        print(f"[INFO] Wymiar: {dim_key}")

        # surowe warstwy z wrappera (Anvil)
        raw_layers = level.level_wrapper._get_raw_chunk_data(cx, cz, dim_key)
        if not isinstance(raw_layers, dict) or not raw_layers:
            data = {"error": "Brak surowych warstw chunka (raw_layers)."}
            chosen_layer = None
        else:
            # spróbuj znaleźć warstwę z 'Level'
            chosen_layer = None
            chosen_root = None
            for layer_name, named in raw_layers.items():
                # named może być NamedTag albo (ver, NamedTag)
                if isinstance(named, tuple):
                    named = named[1]
                root = named.tag if isinstance(named, NamedTag) else named
                if isinstance(root, TAG_Compound) and "Level" in root:
                    chosen_layer = layer_name
                    chosen_root = root["Level"]
                    break
            # jeśli nie znaleźć 'Level' – weź pierwszą i zserializuj całość
            if chosen_root is None:
                layer_name, named = next(iter(raw_layers.items()))
                if isinstance(named, tuple):
                    named = named[1]
                root = named.tag if isinstance(named, NamedTag) else named
                chosen_layer = layer_name
                chosen_root = root.get("Level", root)

            data = nbt_to_python(chosen_root)

        # zapisz JSON z custom encoderem (łapie numpy na 100%)
        os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "_meta": {
                        "dimension": dim_key,
                        "chunk": [cx, cz],
                        "chosen_layer": chosen_layer,
                        "available_layers": list(raw_layers.keys()) if isinstance(raw_layers, dict) else None
                    },
                    "Level": data
                },
                f,
                ensure_ascii=False,
                indent=2,
                cls=NumpyJSONEncoder
            )

        print(f"[OK] Zapisano Level JSON do: {os.path.abspath(out_path)}")
    finally:
        try:
            level.close()
        except Exception:
            pass

if __name__ == "__main__":
    if not os.path.isdir(WORLD_DIR):
        raise SystemExit(f"Nie znaleziono folderu świata: {WORLD_DIR}")
    dump_level_section_to_json(WORLD_DIR, CHUNK_X, CHUNK_Z, OUT_JSON_PATH)
