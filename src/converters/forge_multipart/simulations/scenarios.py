"""
Scenariusze testowe dla ForgeMultipart 1.7.10 -> CB Multipart 1.18.2
Zadanie 2 — symulacje działania funkcjonalności.

Każdy scenariusz tworzy te same struktury w obu wersjach API,
serializuje je do NBT i porównuje różnice.
"""

import json
from typing import Dict

# Importy symulacji 1.7.10
from .fmp_1710 import (
    TileMultipart as TileMultipart1710,
    FaceMicroblock as FaceMicroblock1710,
    HollowMicroblock as HollowMicroblock1710,
    TorchPart as TorchPart1710,
    LeverPart as LeverPart1710,
    ItemMicroPart as ItemMicroPart1710,
    MicroMaterialRegistry as MatReg1710,
    MultiPartRegistry as Reg1710,
)

# Importy symulacji 1.18.2
from .cbm_1182 import (
    TileMultipart as TileMultipart1182,
    FaceMicroblock as FaceMicroblock1182,
    HollowMicroblock as HollowMicroblock1182,
    TorchPart as TorchPart1182,
    LeverPart as LeverPart1182,
    ItemMicroPart as ItemMicroPart1182,
    MicroMaterialRegistry as MatReg1182,
    PartRegistry as Reg1182,
)


def _pretty(obj: dict) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


# ==========================================================================
# SCENARIUSZ 1: Pojedynczy mikroblok (płytka z kamienia)
# ==========================================================================
def scenario_1_single_face_microblock():
    """
    Tworzy pojedynczy FaceMicroblock (płytka 1/4 bloku) z materiału minecraft:stone
    w TileMultipart na pozycji (10, 64, -5).
    Symuluje zapis/odczyt NBT w obu wersjach.
    """
    print("=" * 70)
    print("SCENARIUSZ 1: Pojedynczy FaceMicroblock (stone)")
    print("=" * 70)

    # --- 1.7.10 ---
    MatReg1710.reset()
    Reg1710.reset()
    from . import fmp_1710 as fmp
    fmp.register_defaults()
    fmp.MicroMaterialRegistry.register("minecraft:stone")

    tile_1710 = TileMultipart1710(10, 64, -5)
    mb_1710 = ItemMicroPart1710.create(1, "minecraft:stone")  # size=1, mat=stone
    mb_1710.set_shape(1, 0)  # size=1 (1/4), slot=0
    tile_1710.add_part(mb_1710)

    nbt_1710 = tile_1710.write_to_nbt()
    print("\n--- 1.7.10 NBT ---")
    print(_pretty(nbt_1710))

    # Round-trip
    tile_1710_rt = TileMultipart1710.read_from_nbt(nbt_1710)
    print(f"\nRound-trip 1.7.10 OK: {tile_1710_rt is not None}, parts={len(tile_1710_rt.parts)}")

    # --- 1.18.2 ---
    MatReg1182.reset()
    Reg1182.reset()
    from . import cbm_1182 as cbm
    cbm.register_defaults()
    cbm.MicroMaterialRegistry.register("minecraft:stone")

    tile_1182 = TileMultipart1182(10, 64, -5)
    mb_1182 = ItemMicroPart1182.create(1, "minecraft:stone")
    mb_1182.set_shape(1, 0)
    tile_1182.add_part(mb_1182)

    nbt_1182 = tile_1182.save_additional()
    # W 1.18.2 chunk dodaje id, x, y, z — symulujemy pełny tag:
    full_nbt_1182 = {
        "id": "cb_multipart:saved_multipart",
        "x": 10, "y": 64, "z": -5,
        **nbt_1182
    }
    print("\n--- 1.18.2 NBT ---")
    print(_pretty(full_nbt_1182))

    tile_1182_rt = TileMultipart1182.load(full_nbt_1182, (10, 64, -5))
    print(f"\nRound-trip 1.18.2 OK: parts={len(tile_1182_rt.parts)}")

    # --- Porównanie ---
    print("\n--- ANALIZA RÓŻNIC ---")
    print(f"ID TE 1.7.10 : {nbt_1710['id']}")
    print(f"ID TE 1.18.2 : {full_nbt_1182['id']}")
    print(f"Part ID 1.7.10: {nbt_1710['parts'][0]['id']}")
    print(f"Part ID 1.18.2: {full_nbt_1182['parts'][0]['id']}")
    print(f"Shape/Material identyczne: "
          f"{nbt_1710['parts'][0]['shape']} == {full_nbt_1182['parts'][0]['shape']}  &&  "
          f"{nbt_1710['parts'][0]['material']} == {full_nbt_1182['parts'][0]['material']}")


# ==========================================================================
# SCENARIUSZ 2: Multiple parts w jednym block-space (kabel + mikroblok + torch)
# ==========================================================================
def scenario_2_multiple_parts():
    """
    Symuluje typowy przypadek z mapy: w jednym block-space znajdują się:
    - HollowMicroblock (rura dekoracyjna)
    - TorchPart (pochodnia na ścianie)
    To pokazuje jak TileMultipart zarządza wieloma partami.
    """
    print("\n" + "=" * 70)
    print("SCENARIUSZ 2: Wiele partów w jednym block-space")
    print("=" * 70)

    # --- 1.7.10 ---
    MatReg1710.reset()
    Reg1710.reset()
    from . import fmp_1710 as fmp
    fmp.register_defaults()
    fmp.MicroMaterialRegistry.register("minecraft:stonebrick")

    tile_1710 = TileMultipart1710(20, 70, 30)
    hollow = ItemMicroPart1710.create(4 | (1 << 8), "minecraft:stonebrick")  # size=4, class=1 (hollow)
    hollow.set_shape(4, 0)
    torch = TorchPart1710(4)  # meta=4 (np. na ścianie)

    tile_1710.add_part(hollow)
    tile_1710.add_part(torch)

    nbt_1710 = tile_1710.write_to_nbt()
    print("\n--- 1.7.10 NBT ---")
    print(_pretty(nbt_1710))
    print(f"Liczba partów: {len(nbt_1710['parts'])}")

    # --- 1.18.2 ---
    MatReg1182.reset()
    Reg1182.reset()
    from . import cbm_1182 as cbm
    cbm.register_defaults()
    cbm.MicroMaterialRegistry.register("minecraft:stonebrick")

    tile_1182 = TileMultipart1182(20, 70, 30)
    hollow2 = ItemMicroPart1182.create(4 | (1 << 8), "minecraft:stonebrick")
    hollow2.set_shape(4, 0)
    torch2 = TorchPart1182(4)

    tile_1182.add_part(hollow2)
    tile_1182.add_part(torch2)

    nbt_1182 = tile_1182.save_additional()
    full_nbt_1182 = {
        "id": "cb_multipart:saved_multipart",
        "x": 20, "y": 70, "z": 30,
        **nbt_1182
    }
    print("\n--- 1.18.2 NBT ---")
    print(_pretty(full_nbt_1182))
    print(f"Liczba partów: {len(full_nbt_1182['parts'])}")

    # --- Porównanie ---
    print("\n--- ANALIZA RÓŻNIC ---")
    for i, (p1710, p1182) in enumerate(zip(nbt_1710['parts'], full_nbt_1182['parts'])):
        print(f"Part {i}: 1.7.10 id='{p1710['id']}'  ->  1.18.2 id='{p1182['id']}'")
        if 'meta' in p1710:
            print(f"        meta={p1710['meta']} (zachowane)")


# ==========================================================================
# SCENARIUSZ 3: Konwersja NBT mikrobloku (shape + material)
# ==========================================================================
def scenario_3_microblock_nbt_conversion():
    """
    Pokazuje jak przekonwertować NBT mikrobloku z 1.7.10 na 1.18.2.
    Kluczowe: zmiana namespace part ID, pozostałe dane (shape, material) bez zmian.
    """
    print("\n" + "=" * 70)
    print("SCENARIUSZ 3: Konwersja NBT mikrobloku 1.7.10 -> 1.18.2")
    print("=" * 70)

    # Symulujemy surowy NBT z mapy 1.7.10
    source_nbt = {
        "id": "TileMultipart",
        "x": 100, "y": 65, "z": 200,
        "parts": [
            {"id": "mcr_corner", "shape": 34, "material": "minecraft:glass"},
            {"id": "mcr_edge",   "shape": 18, "material": "minecraft:iron_block"},
        ]
    }
    print("\n--- NBT źródłowy 1.7.10 ---")
    print(_pretty(source_nbt))

    # Mapowanie ID partów 1.7.10 -> 1.18.2
    id_mapping = {
        "mcr_face":   "cb_microblock:face",
        "mcr_hollow": "cb_microblock:hollow",
        "mcr_corner": "cb_microblock:corner",
        "mcr_edge":   "cb_microblock:edge",
        "mcr_post":   "cb_microblock:post",
        "mc_torch":   "minecraft:torch",
        "mc_redtorch": "minecraft:redstone_torch",
        "mc_button":  "minecraft:stone_button",
        "mc_lever":   "minecraft:lever",
    }

    converted_parts = []
    for part in source_nbt["parts"]:
        old_id = part["id"]
        new_id = id_mapping.get(old_id, old_id)
        converted_parts.append({
            "id": new_id,
            "shape": part["shape"],
            "material": part["material"],
        })

    target_nbt = {
        "id": "cb_multipart:saved_multipart",
        "x": source_nbt["x"],
        "y": source_nbt["y"],
        "z": source_nbt["z"],
        "parts": converted_parts,
    }
    print("\n--- NBT docelowy 1.18.2 ---")
    print(_pretty(target_nbt))

    # Weryfikacja: deserializacja w 1.18.2
    MatReg1182.reset()
    Reg1182.reset()
    from . import cbm_1182 as cbm
    cbm.register_defaults()
    cbm.MicroMaterialRegistry.register("minecraft:glass")
    cbm.MicroMaterialRegistry.register("minecraft:iron_block")

    tile = TileMultipart1182.load(target_nbt, (100, 65, 200))
    print(f"\nDeserializacja 1.18.2 OK: parts={len(tile.parts)}")
    for p in tile.parts:
        print(f"  {p}")


# ==========================================================================
# SCENARIUSZ 4: Dropy i harvest (symulacja kolizji)
# ==========================================================================
def scenario_4_drops_and_harvest():
    """
    Symuluje zachowanie przy niszczeniu multipart blocka.
    W 1.7.10 BlockMultipart.dropAndDestroy iteruje po partList i zleca dropy.
    W 1.18.2 mechanika jest analogiczna.
    """
    print("\n" + "=" * 70)
    print("SCENARIUSZ 4: Dropy przy niszczeniu blocka")
    print("=" * 70)

    MatReg1710.reset()
    Reg1710.reset()
    from . import fmp_1710 as fmp
    fmp.register_defaults()
    fmp.MicroMaterialRegistry.register("minecraft:planks")

    tile = TileMultipart1710(5, 64, 5)
    tile.add_part(ItemMicroPart1710.create(2 | (3 << 8), "minecraft:planks"))  # edge, size=2
    tile.add_part(TorchPart1710(1))

    print("\n--- Dropy z TileMultipart 1.7.10 ---")
    for part in tile.parts:
        drops = part.get_drops()
        print(f"  {part.get_type()} -> drops={drops}")


# ==========================================================================
# Uruchomienie wszystkich scenariuszy
# ==========================================================================
def run_all():
    scenario_1_single_face_microblock()
    scenario_2_multiple_parts()
    scenario_3_microblock_nbt_conversion()
    scenario_4_drops_and_harvest()
    print("\n" + "=" * 70)
    print("WSZYSTKIE SCENARIUSZE ZAKOŃCZONE")
    print("=" * 70)


if __name__ == "__main__":
    run_all()
