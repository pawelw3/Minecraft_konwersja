# core.py
from typing import Optional
try:
    from amulet.api.level import load_level
except Exception:
    import amulet as _amulet; load_level = _amulet.load_level

from amulet_nbt import NamedTag, TAG_Compound

def open_world(path: str):
    return load_level(path)

def pick_dim(wrapper, preferred="minecraft:overworld"):
    keys = list(wrapper.dimensions)
    if preferred in keys: return preferred
    for k in keys:
        if "overworld" in k: return k
    return keys[0] if keys else preferred

def raw_root_for_chunk(world, dim_key: str, cx: int, cz: int) -> Optional[TAG_Compound]:
    raw = world.level_wrapper._get_raw_chunk_data(cx, cz, dim_key)
    if not isinstance(raw, dict) or not raw: return None
    for named in raw.values():
        if isinstance(named, tuple): named = named[1]
        root = named.tag if isinstance(named, NamedTag) else named
        if isinstance(root, TAG_Compound) and "Level" in root:
            return root
    named = list(raw.values())[0]
    if isinstance(named, tuple): named = named[1]
    return named.tag if isinstance(named, NamedTag) else named

def ensure_chunk(world, cx, cz, dim_key):
    try:
        return world.get_chunk(cx, cz, dim_key)
    except Exception:
        try:
            world.create_chunk(cx, cz, dimension=dim_key)
        except TypeError:
            world.create_chunk(cx, cz, dim_key)
        return world.get_chunk(cx, cz, dim_key)

def set_block_index(chunk, x, y, z, ns: str, name: str):
    from amulet.api.block import Block
    pid = chunk.block_palette.get_add_block(Block(namespace=ns, base_name=name))
    chunk.blocks[x & 15, y, z & 15] = pid
    return pid

def put_chunk(world, chunk, cx, cz, dim_key):
    try:
        chunk.changed = True
    except Exception:
        pass
    for call in (
        lambda: world.put_chunk(chunk, dim_key),
        lambda: world.put_chunk(chunk, cx, cz, dim_key),
        lambda: world.put_chunk(chunk, cx, cz),
        lambda: world.put_chunk((dim_key, cx, cz), chunk),
    ):
        try:
            return call()
        except TypeError:
            continue
    raise RuntimeError("put_chunk nieobsługiwany w tej wersji amulet-core")
