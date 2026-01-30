# ae2_handlers.py
from typing import List, Dict, Any
from amulet_nbt import TAG_Compound, TAG_String, TAG_Int, TAG_Byte
from core import raw_root_for_chunk, ensure_chunk, set_block_index, put_chunk

def make_block_entity(local_x: int, y: int, local_z: int, nbt_root):
    from amulet.api.block_entity import BlockEntity
    from amulet_nbt import NamedTag
    named = NamedTag(nbt_root)

    # spróbuj znanych sygnatur
    tries = [
        ((named,), {}),                                   # BlockEntity(NamedTag)
        ((), {"nbt": named},),                           # BlockEntity(nbt=NamedTag)
        ((local_x, y, local_z, named), {}),              # BlockEntity(x, y, z, NamedTag)
        ((named, (local_x, y, local_z)), {}),            # BlockEntity(NamedTag, (x,y,z))
        (((local_x, y, local_z), named), {}),            # BlockEntity((x,y,z), NamedTag)
        (("ae2:dummy", local_x, y, local_z, named), {}), # BlockEntity(id, x,y,z, NamedTag)
        ((), {"nbt": named, "x": local_x, "y": y, "z": local_z}),  # keywordy
    ]
    last_err = None
    for pargs, kwargs in tries:
        try:
            return BlockEntity(*pargs, **kwargs)
        except Exception as e:
            last_err = e

    # Fallback: ręcznie ustaw pola, których oczekuje property .location
    be_obj = BlockEntity.__new__(BlockEntity)
    # NBT – najpierw _nbt, jeśli nie ma to nbt
    try:
        setattr(be_obj, "_nbt", named)
    except Exception:
        setattr(be_obj, "nbt", named)
    # Współrzędne: ustaw prywatne, bo .location czyta _x/_y/_z
    setattr(be_obj, "_x", local_x)
    setattr(be_obj, "_y", y)
    setattr(be_obj, "_z", local_z)
    # Dla pewności dodaj też publiczne read-only „cienie”, jeśli istnieją
    if not hasattr(be_obj, "location"):
        setattr(be_obj, "location", (local_x, y, local_z))
    return be_obj



# mapowanie kierunków
DIR_MAP = {
    "DOWN":"DOWN","UP":"UP","NORTH":"NORTH","SOUTH":"SOUTH","WEST":"WEST","EAST":"EAST",
    "down":"DOWN","up":"UP","north":"NORTH","south":"SOUTH","west":"WEST","east":"EAST",
    0:"DOWN",1:"UP",2:"NORTH",3:"SOUTH",4:"WEST",5:"EAST",
}
def _s(tag, d=""): 
    try: return tag.value if hasattr(tag,"value") else str(tag)
    except: return d
def _i(tag, d=0): 
    try: return int(tag.value if hasattr(tag,"value") else int(tag))
    except: return d

# ---------- CREATIVE ENERGY CELL ----------
AE2_CREATIVE_TE_IDS_1710 = {
    "BlockCreativeEnergyCell",
    "appliedenergistics2:tile.BlockEnergyCellCreative",
    "appliedenergistics2:BlockCreativeEnergyCell",
    "tile.BlockEnergyCellCreative",
    "BlockEnergyCellCreative",
}

def scan_cells_in_chunk(old_world, dim_key: str, cx: int, cz: int) -> List[Dict[str,Any]]:
    root = raw_root_for_chunk(old_world, dim_key, cx, cz)
    if root is None: return []
    lvl = root["Level"] if "Level" in root else root
    out: List[Dict[str,Any]] = []
    if "TileEntities" not in lvl: return out
    for te in lvl["TileEntities"]:
        if not isinstance(te, TAG_Compound): continue
        te_id = _s(te.get("id", TAG_String("")), "")
        if te_id in AE2_CREATIVE_TE_IDS_1710 or ("creative" in te_id.lower() and "energy" in te_id.lower() and "cell" in te_id.lower()):
            x = _i(te.get("x", TAG_Int(cx*16)), cx*16)
            y = _i(te.get("y", TAG_Int(64)), 64)
            z = _i(te.get("z", TAG_Int(cz*16)), cz*16)
            fwd = DIR_MAP.get(_s(te.get("orientation_forward", te.get("forward", TAG_String("UP"))), "UP"), "UP")
            up  = DIR_MAP.get(_s(te.get("orientation_up",      te.get("up",      TAG_String("UP"))), "UP"), "UP")
            out.append({"kind":"ae2_cell", "pos":(x,y,z), "forward":fwd, "up":up})
    return out

def place_cell(new_world, dim_key: str, task: Dict[str,Any]):
    x,y,z = task["pos"]; fwd=task["forward"]; up=task["up"]
    chunk = ensure_chunk(new_world, x>>4, z>>4, dim_key)
    set_block_index(chunk, x, y, z, "ae2", "creative_energy_cell")
    # zbuduj TE
    be_root = TAG_Compound({
        "id": TAG_String("ae2:creative_energy_cell"),
        "x": TAG_Int(x), "y": TAG_Int(y), "z": TAG_Int(z),
        "forward": TAG_String(fwd), "up": TAG_String(up),
        "keepPacked": TAG_Byte(0), "ForgeCaps": TAG_Compound({}), "proxy": TAG_Compound({}),
    })
    be_obj = make_block_entity(x & 15, y, z & 15, be_root)
    chunk.block_entities[(x & 15, y, z & 15)] = be_obj
    put_chunk(new_world, chunk, x>>4, z>>4, dim_key)


# ---------- FLUIX GLASS CABLE ----------
# 1.7.10: TE BlockCableBus, part.g=109 (często) → fluix glass
CABLE_TE_IDS_1710 = {
    "tile.BlockCableBus", "appliedenergistics2:tile.BlockCableBus",
    "BlockCableBus", "appeng.tile.networking.TileCableBus", "TileCableBus",
}
G_FLUIX_1710 = {109}   # znane wartości; damy też heurystykę po stringu „fluix”

def scan_fluix_cables_in_chunk(old_world, dim_key: str, cx: int, cz: int) -> List[Dict[str,Any]]:
    root = raw_root_for_chunk(old_world, dim_key, cx, cz)
    if root is None: return []
    lvl = root["Level"] if "Level" in root else root
    out: List[Dict[str,Any]] = []
    if "TileEntities" not in lvl: return out

    for te in lvl["TileEntities"]:
        if not isinstance(te, TAG_Compound): continue
        te_id = _s(te.get("id", TAG_String("")), "")
        if te_id not in CABLE_TE_IDS_1710: continue

        # preferuj odczyt extra.part.g
        part = None
        if "extra" in te and isinstance(te["extra"], TAG_Compound) and "part" in te["extra"]:
            part = te["extra"]["part"]
        elif "part" in te:
            part = te["part"]

        is_fluix = False
        if isinstance(part, TAG_Compound) and "g" in part:
            try:
                gval = _i(part["g"])
                is_fluix = gval in G_FLUIX_1710
            except Exception:
                pass
        if not is_fluix:
            # heurystyka: gdziekolwiek w TE pojawia się słowo "fluix"
            if "fluix" in str(te).lower():
                is_fluix = True

        if is_fluix:
            x = _i(te.get("x", TAG_Int(cx*16)), cx*16)
            y = _i(te.get("y", TAG_Int(64)), 64)
            z = _i(te.get("z", TAG_Int(cz*16)), cz*16)
            out.append({"kind":"ae2_fluix_glass", "pos":(x,y,z)})

    return out

def place_fluix_cable(new_world, dim_key: str, task: Dict[str,Any]):
    """
    1.18 zapis:
      blok:  ae2:fluix_glass_cable
      TE:    ae2:cable_bus z polem 'cable' => { id:"ae2:fluix_glass_cable", gn:{g:59,k:-1,p:0} }
    """
    x,y,z = task["pos"]
    chunk = ensure_chunk(new_world, x>>4, z>>4, dim_key)

    # postaw blok
    set_block_index(chunk, x, y, z, "ae2", "fluix_glass_cable")

    # zbuduj TE
    be_root = TAG_Compound({
        "id": TAG_String("ae2:cable_bus"),
        "x": TAG_Int(x), "y": TAG_Int(y), "z": TAG_Int(z),
        "keepPacked": TAG_Byte(0),
        "ForgeCaps": TAG_Compound({}),
        "hasRedstone": TAG_Int(2),
        "cable": TAG_Compound({
            "id": TAG_String("ae2:fluix_glass_cable"),
            "gn": TAG_Compound({"g": TAG_Int(59), "k": TAG_Int(-1), "p": TAG_Int(0)})
        })
    })
    be_obj = make_block_entity(x & 15, y, z & 15, be_root)
    chunk.block_entities[(x & 15, y, z & 15)] = be_obj
    put_chunk(new_world, chunk, x>>4, z>>4, dim_key)

