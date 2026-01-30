# -*- coding: utf-8 -*-
"""
Konwersja AE2 Creative Energy Cell z 1.7.10 -> 1.18 (po DFU) poprzez surowe NBT.
Czytamy wyłącznie Level.TileEntities (raw), omijając ch.block_entities.

Użycie:
  - Podmień ścieżki OLD_WORLD_DIR i NEW_WORLD_DIR (ustawione pod Twoje lokalizacje).
  - Zostaw SCAN_MODE="chunk" i CHUNK_LIST=[(-5,-5)] żeby skanować tylko ten chunk,
    albo ustaw SCAN_MODE="all" żeby przelecieć cały świat (wolniej).
  - Uruchom:  python ae2_convert_creative_cells_raw.py
"""

import os
from typing import Iterable, List, Tuple, Dict

# --- ŚCIEŻKI (ustawione wg Twojego opisu) ---
OLD_WORLD_DIR = r"C:\Users\pawel\AppData\Roaming\.minecraft\saves\konwersja1_all"               # 1.7.10 PRZED DFU
NEW_WORLD_DIR = r"C:\Users\pawel\AppData\Roaming\.minecraft118\saves\konwersja1_all"       # 1.18 PO DFU

# --- TRYB SKANU ---
SCAN_MODE  = "all"               # "chunk" albo "all"
CHUNK_LIST = [(-5, -5)]            # globalne (cx, cz) do skanowania, gdy SCAN_MODE="chunk"

# --- IMPORTY AMULET (zgodne z różnymi wersjami) ---
try:
    from amulet.api.level import load_level
except Exception:
    import amulet as _amulet_pkg
    load_level = _amulet_pkg.load_level

from amulet.api.block import Block
from amulet.api.errors import ChunkDoesNotExist
from amulet_nbt import NamedTag, TAG_Compound, TAG_String, TAG_Int, TAG_Byte

# --- ID TE (różne warianty spotykane w 1.7.10) ---
AE2_CREATIVE_TE_IDS = {
    "BlockCreativeEnergyCell",
    "appliedenergistics2:tile.BlockEnergyCellCreative",
    "appliedenergistics2:BlockCreativeEnergyCell",
    "tile.BlockEnergyCellCreative",
    "BlockEnergyCellCreative",
}

DIR_MAP = {
    "DOWN": "DOWN", "UP": "UP", "NORTH": "NORTH", "SOUTH": "SOUTH", "WEST": "WEST", "EAST": "EAST",
    "down": "DOWN", "up": "UP", "north": "NORTH", "south": "SOUTH", "west": "WEST", "east": "EAST",
    0: "DOWN", 1: "UP", 2: "NORTH", 3: "SOUTH", 4: "WEST", 5: "EAST",
}

def pick_dimension_key(level_wrapper, preferred="minecraft:overworld") -> str:
    keys = list(level_wrapper.dimensions)
    return preferred if preferred in keys else (keys[0] if keys else preferred)

def _get_raw_root_for_chunk(level, dim_key: str, cx: int, cz: int) -> TAG_Compound | None:
    """Zwróć root TAG_Compound (NamedTag.tag) dla pierwszej warstwy chunka."""
    raw_layers = level.level_wrapper._get_raw_chunk_data(cx, cz, dim_key)
    if not isinstance(raw_layers, dict) or not raw_layers:
        return None
    # wybierz warstwę, gdzie istnieje 'Level' w root, w przeciwnym razie pierwszą
    for _layer_name, named in raw_layers.items():
        if isinstance(named, tuple):
            named = named[1]
        root = named.tag if isinstance(named, NamedTag) else named
        if isinstance(root, TAG_Compound) and "Level" in root:
            return root
    # fallback: pierwsza warstwa
    _layer_name, named = next(iter(raw_layers.items()))
    if isinstance(named, tuple):
        named = named[1]
    return named.tag if isinstance(named, NamedTag) else named

def _get_str(nbt_val, default: str) -> str:
    try:
        return nbt_val.value if hasattr(nbt_val, "value") else str(nbt_val)
    except Exception:
        return default

def _get_int(nbt_val, default: int) -> int:
    try:
        return int(nbt_val.value if hasattr(nbt_val, "value") else int(nbt_val))
    except Exception:
        return default

def iter_all_chunk_coords(level, dim_key: str) -> Iterable[Tuple[int, int]]:
    """Iteruj po wszystkich chunkach dostępnych w wymiarze."""
    for cx, cz in level.all_chunk_coords(dim_key):
        yield cx, cz

def collect_cells_from_chunk_raw(level, dim_key: str, cx: int, cz: int) -> List[Dict]:
    """Przeczytaj surowe Level.TileEntities w danym chunku i wyciągnij Creative Energy Cell."""
    out: List[Dict] = []
    root = _get_raw_root_for_chunk(level, dim_key, cx, cz)
    if root is None:
        return out
    level_tag = root["Level"] if "Level" in root else root
    if "TileEntities" not in level_tag:
        return out

    te_list = level_tag["TileEntities"]
    # to jest TAG_List → iterujemy po elementach (TAG_Compound)
    for te in te_list:
        if not isinstance(te, TAG_Compound):
            continue
        te_id = _get_str(te.get("id", TAG_String("")), "")
        strict = te_id in AE2_CREATIVE_TE_IDS
        heur  = ("energy" in te_id.lower() and "cell" in te_id.lower() and "creative" in te_id.lower())
        if not (strict or heur):
            continue

        x = _get_int(te.get("x", TAG_Int(cx*16)), cx*16)
        y = _get_int(te.get("y", TAG_Int(64)), 64)
        z = _get_int(te.get("z", TAG_Int(cz*16)), cz*16)

        fwd = _get_str(te.get("orientation_forward", te.get("forward", TAG_String("UP"))), "UP")
        up  = _get_str(te.get("orientation_up",      te.get("up",      TAG_String("UP"))), "UP")
        fwd = DIR_MAP.get(fwd, fwd)
        up  = DIR_MAP.get(up,  up)

        out.append({"x": x, "y": y, "z": z, "forward": fwd, "up": up, "chunk": (cx, cz), "id": te_id})
    return out

def collect_cells(old_world_path: str, scan_mode: str, chunk_list: List[Tuple[int,int]]) -> List[Dict]:
    old = load_level(old_world_path)
    cells: List[Dict] = []
    try:
        dim_key = pick_dimension_key(old.level_wrapper, "minecraft:overworld")
        if scan_mode == "chunk":
            coords = chunk_list
            print(f"[INFO] Skanuję wskazane chunki: {coords} (dim='{dim_key}')")
        else:
            coords = list(iter_all_chunk_coords(old, dim_key))
            print(f"[INFO] Skanuję cały świat: {len(coords)} chunków (dim='{dim_key}')")

        hits = 0
        for cx, cz in coords:
            found = collect_cells_from_chunk_raw(old, dim_key, cx, cz)
            if found:
                for f in found:
                    print(f"[HIT] {f['id']} @({f['x']},{f['y']},{f['z']}) fwd={f['forward']} up={f['up']} chunk=({cx},{cz})")
                hits += len(found)
                cells.extend(found)
        print(f"[INFO] Razem znaleziono: {hits}")
    finally:
        try:
            old.close()
        except Exception:
            pass
    return cells

def make_be_nbt(x: int, y: int, z: int, forward: str, up: str):
    """Block-entity NBT dla 1.18 AE2 creative_energy_cell."""
    from amulet_nbt import TAG_Compound, TAG_String, TAG_Int, TAG_Byte, NamedTag
    be = TAG_Compound({
        "id": TAG_String("ae2:creative_energy_cell"),
        "x": TAG_Int(int(x)),
        "y": TAG_Int(int(y)),
        "z": TAG_Int(int(z)),
        "forward": TAG_String(forward),
        "up": TAG_String(up),
        "keepPacked": TAG_Byte(0),
        "ForgeCaps": TAG_Compound({}),
        "proxy": TAG_Compound({}),  # AE2 odbuduje sobie wnętrzności
    })
    return NamedTag(be)

def place_in_new_world(cells, new_world_path: str) -> int:
    """
    Wstawia Creative Energy Celle do świata 1.18 (po DFU) i TRWALE zapisuje zmiany (.mca).
    """
    new = load_level(new_world_path)
    placed = 0
    try:
        # wybór wymiaru (Overworld)
        def pick_dim(wrapper, preferred="minecraft:overworld"):
            keys = list(wrapper.dimensions)
            if preferred in keys:
                return preferred
            for k in keys:
                if "overworld" in k:
                    return k
            return keys[0] if keys else preferred

        dim_key = pick_dim(new.level_wrapper, "minecraft:overworld")
        print(f"[INFO] Wymiar celu: {dim_key}")

        from amulet.api.block import Block
        from amulet.api.block_entity import BlockEntity
        from amulet_nbt import TAG_Compound, TAG_String, TAG_Int, TAG_Byte, NamedTag

        block = Block(namespace="ae2", base_name="creative_energy_cell")

        def build_block_entity(bx, y, bz, gx, gy, gz, forward: str, up: str):
            be_nbt = TAG_Compound({
                "id": TAG_String("ae2:creative_energy_cell"),
                "x": TAG_Int(gx), "y": TAG_Int(gy), "z": TAG_Int(gz),
                "forward": TAG_String(forward),
                "up":      TAG_String(up),
                "keepPacked": TAG_Byte(0),
                "ForgeCaps": TAG_Compound({}),
                "proxy": TAG_Compound({}),
            })
            named = NamedTag(be_nbt)
            # spróbuj paru sygnatur
            for pargs, kwargs in (
                ((bx, y, bz, named), {}),
                ((named, (bx, y, bz)), {}),
                (((bx, y, bz), named), {}),
                (("ae2:creative_energy_cell", bx, y, bz, named), {}),
                ((named,), {}),
                ((), {"nbt": named, "x": bx, "y": y, "z": bz}),
                ((), {"nbt": named, "namespace": "ae2", "base_name": "creative_energy_cell", "x": bx, "y": y, "z": bz}),
            ):
                try:
                    return BlockEntity(*pargs, **kwargs)
                except Exception:
                    pass
            # brutalny fallback
            be_obj = BlockEntity.__new__(BlockEntity)
            setattr(be_obj, "nbt", named)
            setattr(be_obj, "x", bx); setattr(be_obj, "y", y); setattr(be_obj, "z", bz)
            if not hasattr(be_obj, "location"):
                setattr(be_obj, "location", (bx, y, bz))
            if not hasattr(be_obj, "namespaced_name"):
                setattr(be_obj, "namespaced_name", "ae2:creative_energy_cell")
            return be_obj

        for c in cells:
            gx, gy, gz = int(c["x"]), int(c["y"]), int(c["z"])
            cx, cz = gx >> 4, gz >> 4
            bx, bz = gx & 15, gz & 15

            # pobierz/utwórz chunk
            try:
                chunk = new.get_chunk(cx, cz, dim_key)
            except Exception:
                try:
                    new.create_chunk(cx, cz, dimension=dim_key)
                except TypeError:
                    new.create_chunk(cx, cz, dim_key)
                chunk = new.get_chunk(cx, cz, dim_key)

            # blok -> paleta -> index
            pid = chunk.block_palette.get_add_block(block)
            chunk.blocks[bx, gy, bz] = pid

            # block entity
            be_obj = build_block_entity(bx, gy, bz, gx, gy, gz, c["forward"], c["up"])
            chunk.block_entities[(bx, gy, bz)] = be_obj

            # oznacz zmieniony i WŁÓŻ z powrotem (ważne!)
            try:
                chunk.changed = True
            except Exception:
                pass

            # >>> poprawne put_chunk dla Twojej wersji <<<
            # po modyfikacjach chunku:
            try:
                # ✅ Twoja wersja: (chunk, dimension)
                new.put_chunk(chunk, dim_key)
            except TypeError:
                try:
                    # inne wydanie: (chunk, cx, cz, dimension)
                    new.put_chunk(chunk, cx, cz, dim_key)
                except TypeError:
                    try:
                        # inne: (chunk, cx, cz)
                        new.put_chunk(chunk, cx, cz)
                    except TypeError:
                        # rzadkie: (key, chunk)
                        new.put_chunk((dim_key, cx, cz), chunk)


            placed += 1
            print(f"[SET] ae2:creative_energy_cell @({gx},{gy},{gz}) fwd={c['forward']} up={c['up']}")

        print(f"[INFO] Zapisuję świat: {new_world_path}")
        new.save()
    finally:
        try:
            new.close()
        except Exception:
            pass

    print(f"[INFO] Wstawiono: {placed}")
    return placed





def main():
    if not os.path.isdir(OLD_WORLD_DIR):
        raise SystemExit(f"Brak folderu starego świata: {OLD_WORLD_DIR}")
    if not os.path.isdir(NEW_WORLD_DIR):
        raise SystemExit(f"Brak folderu nowego świata: {NEW_WORLD_DIR}")

    cells = collect_cells(OLD_WORLD_DIR, SCAN_MODE, CHUNK_LIST)
    if not cells:
        print("[WARN] Nie znaleziono żadnych Creative Energy Cell w danych wejściowych.")
        return
    place_in_new_world(cells, NEW_WORLD_DIR)

if __name__ == "__main__":
    main()
