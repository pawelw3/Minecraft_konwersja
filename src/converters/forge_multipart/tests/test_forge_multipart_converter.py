"""
Testy konwertera ForgeMultipart -> CB Multipart.

Testujemy:
1. Mapowanie block ID
2. Konwersję NBT TileMultipart (z parts)
3. Mapowanie part IDs
4. Round-trip symulacji (NBT -> konwerter -> NBT -> deserializacja 1.18.2)
"""

from __future__ import annotations

import pytest
import sys
from pathlib import Path

# Dodaj parent do path żeby importy działały
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from converters.forge_multipart.forge_multipart_converter import ForgeMultipartConverter
from converters.forge_multipart.nbt_converter import TileMultipartNBTConverter
from converters.forge_multipart.mappings import (
    SAFE_MICROBLOCK_MATERIALS_1182,
    map_block_id,
    map_microblock_material,
    map_part_id,
    map_te_id,
)


# ---------------------------------------------------------------------------
# Testy mapowań
# ---------------------------------------------------------------------------
def test_map_block_id():
    assert map_block_id("ForgeMultipart:block") == "cb_multipart:multipart"
    assert map_block_id("unknown:block") is None


def test_map_te_id():
    assert map_te_id("savedMultipart") == "cb_multipart:saved_multipart"
    assert map_te_id("TileMultipart") == "cb_multipart:saved_multipart"
    assert map_te_id("ForgeMultipart:TileMultipart") == "cb_multipart:saved_multipart"


def test_map_part_id_microblocks():
    assert map_part_id("mcr_face") == "cb_microblock:face"
    assert map_part_id("mcr_hollow") == "cb_microblock:hollow"
    assert map_part_id("mcr_corner") == "cb_microblock:corner"
    assert map_part_id("mcr_edge") == "cb_microblock:edge"
    assert map_part_id("mcr_post") == "cb_microblock:post"


def test_map_part_id_vanilla():
    assert map_part_id("mc_torch") == "minecraft:torch"
    assert map_part_id("mc_redtorch") == "minecraft:redstone_torch"
    assert map_part_id("mc_button") == "minecraft:stone_button"
    assert map_part_id("mc_lever") == "minecraft:lever"


def test_map_part_id_unknown_fallback():
    # Nieznane ID powinny zostać zwrócone bez zmian (z ostrzeżeniem w runtime)
    assert map_part_id("custom:unknown_part") == "custom:unknown_part"


def test_map_microblock_material_extrautils_colored_blocks():
    assert map_microblock_material("tile.extrautils:color_quartzBlock_2") == "minecraft:quartz_block"
    assert map_microblock_material("tile.extrautils:color_blockLapis_15") == "minecraft:lapis_block"


def test_map_microblock_material_falls_back_to_valid_resource_location():
    assert map_microblock_material("bad material with spaces") == "minecraft:stone"


def test_map_microblock_material_rejects_unknown_but_syntactically_valid_ids():
    assert map_microblock_material("unknownmod:looks_valid") == "minecraft:stone"
    assert map_microblock_material("chisel:glowstone_4") == "minecraft:glowstone"
    assert map_microblock_material("chisel:gold2_2") == "minecraft:gold_block"
    assert map_microblock_material("chisel:marble") == "minecraft:calcite"


def test_map_microblock_material_converts_legacy_vanilla_names():
    assert map_microblock_material("minecraft:stonebrick") == "minecraft:stone_bricks"
    assert map_microblock_material("minecraft:brick_block") == "minecraft:bricks"
    assert map_microblock_material("minecraft:stained_hardened_clay_13") == "minecraft:green_terracotta"
    assert map_microblock_material("minecraft:wool_14") == "minecraft:red_wool"


def test_map_microblock_material_converts_old_mod_materials_to_safe_vanilla():
    assert map_microblock_material("tile.extrautils:colorstonebrick_7") == "minecraft:stone_bricks"
    assert map_microblock_material("thermalfoundation:storage_2") == "minecraft:iron_block"
    assert map_microblock_material("mekanism:basicblock_5") == "minecraft:iron_block"


def test_regression_crash_materials_resolve_to_known_safe_materials():
    crash_materials = [
        "chisel:glowstone_4",
        "chisel:gold2_2",
        "chisel:marble",
        "chisel:concrete_4",
        "minecraft:stained_hardened_clay_13",
        "tile.extrautils:colorstonebrick_7",
        "thermalfoundation:storage_2",
        "mekanism:basicblock_5",
        "unknownmod:looks_valid",
    ]

    for material in crash_materials:
        mapped = map_microblock_material(material)
        assert mapped in SAFE_MICROBLOCK_MATERIALS_1182


# ---------------------------------------------------------------------------
# Testy konwersji NBT TileMultipart
# ---------------------------------------------------------------------------
def test_convert_empty_tilemultipart():
    nbt_1710 = {
        "id": "TileMultipart",
        "x": 10, "y": 64, "z": -5,
        "parts": []
    }
    nbt_1182 = TileMultipartNBTConverter.convert(nbt_1710)
    assert nbt_1182 is not None
    assert nbt_1182["id"] == "cb_multipart:saved_multipart"
    assert nbt_1182["parts"] == []


def test_convert_face_microblock():
    nbt_1710 = {
        "id": "TileMultipart",
        "x": 20, "y": 70, "z": 30,
        "parts": [
            {"id": "mcr_face", "shape": 16, "material": "minecraft:stone"}
        ]
    }
    nbt_1182 = TileMultipartNBTConverter.convert(nbt_1710)
    assert nbt_1182 is not None
    part = nbt_1182["parts"][0]
    assert part["id"] == "cb_microblock:face"
    assert part["shape"] == 16
    assert part["material"] == "minecraft:stone"


def test_convert_extrautils_colored_microblock_material_is_resource_location_safe():
    nbt_1710 = {
        "id": "savedMultipart",
        "x": -100, "y": 70, "z": -65,
        "parts": [
            {"id": "mcr_face", "shape": 16, "material": "tile.extrautils:color_quartzBlock_2"}
        ]
    }
    nbt_1182 = TileMultipartNBTConverter.convert(nbt_1710)
    assert nbt_1182 is not None
    part = nbt_1182["parts"][0]
    assert part["id"] == "cb_microblock:face"
    assert part["material"] == "minecraft:quartz_block"
    assert "color_quartzBlock" not in part["material"]


def test_convert_multiple_parts():
    nbt_1710 = {
        "id": "ForgeMultipart:TileMultipart",
        "x": 100, "y": 65, "z": 200,
        "parts": [
            {"id": "mcr_hollow", "shape": 64, "material": "minecraft:stonebrick"},
            {"id": "mc_torch", "meta": 4},
            {"id": "mc_lever", "meta": 5},
        ]
    }
    nbt_1182 = TileMultipartNBTConverter.convert(nbt_1710)
    assert nbt_1182 is not None
    assert nbt_1182["id"] == "cb_multipart:saved_multipart"
    assert len(nbt_1182["parts"]) == 3

    assert nbt_1182["parts"][0]["id"] == "cb_microblock:hollow"
    assert nbt_1182["parts"][1]["id"] == "minecraft:torch"
    assert nbt_1182["parts"][1]["state"] == {
        "Name": "minecraft:wall_torch",
        "Properties": {"facing": "north"},
    }
    assert "meta" not in nbt_1182["parts"][1]
    assert nbt_1182["parts"][2]["id"] == "minecraft:lever"
    assert nbt_1182["parts"][2]["state"]["Name"] == "minecraft:lever"


def test_convert_preserves_coordinates():
    nbt_1710 = {
        "id": "TileMultipart",
        "x": -1000, "y": 255, "z": 1000,
        "parts": []
    }
    nbt_1182 = TileMultipartNBTConverter.convert(nbt_1710)
    assert nbt_1182["x"] == -1000
    assert nbt_1182["y"] == 255
    assert nbt_1182["z"] == 1000


def test_convert_does_not_mutate_original():
    nbt_1710 = {
        "id": "TileMultipart",
        "x": 0, "y": 0, "z": 0,
        "parts": [{"id": "mcr_face", "shape": 1, "material": "minecraft:dirt"}]
    }
    original_id = nbt_1710["id"]
    original_part_id = nbt_1710["parts"][0]["id"]

    TileMultipartNBTConverter.convert(nbt_1710)

    assert nbt_1710["id"] == original_id
    assert nbt_1710["parts"][0]["id"] == original_part_id


# ---------------------------------------------------------------------------
# Testy głównego konwertera
# ---------------------------------------------------------------------------
def test_converter_block_multipart():
    conv = ForgeMultipartConverter()
    result = conv.convert_block(
        block_id_1710="ForgeMultipart:block",
        metadata=0,
        nbt_1710={
            "id": "savedMultipart",
            "x": 10, "y": 64, "z": -5,
            "parts": [{"id": "mcr_face", "shape": 16, "material": "minecraft:stone"}]
        },
        position=(10, 64, -5),
    )

    assert result.converted.success
    assert result.converted.block_id_1182 == "cb_multipart:multipart"
    assert result.converted.nbt_1182 is not None
    assert result.converted.nbt_1182["id"] == "cb_multipart:saved_multipart"


def test_converter_unknown_block():
    conv = ForgeMultipartConverter()
    result = conv.convert_block(
        block_id_1710="ForgeMultipart:unknown",
        metadata=0,
        position=(0, 0, 0),
    )
    assert not result.converted.success
    assert result.converted.errors
    assert "FMP-E-BLOCK-NOT-MAPPED" in result.converted.errors[0]


def test_converter_event_format():
    conv = ForgeMultipartConverter()
    conv.convert_block(
        block_id_1710="ForgeMultipart:block",
        metadata=0,
        nbt_1710={
            "id": "TileMultipart",
            "x": 5, "y": 70, "z": 5,
            "parts": []
        },
        position=(5, 70, 5),
    )

    assert len(conv.events) == 1
    event = conv.events[0]
    assert event["op"] == "set_block_entity"
    assert event["pos"] == [5, 70, 5]
    assert event["block"] == "cb_multipart:multipart"
    assert event["source"]["mod"] == "ForgeMultipart"
    assert event["source"]["block_id"] == "ForgeMultipart:block"
    assert "nbt" in event


def test_converter_stats():
    conv = ForgeMultipartConverter()
    conv.convert_block("ForgeMultipart:block", 0, None, (0, 0, 0))
    conv.convert_block("ForgeMultipart:block", 0, None, (1, 1, 1))
    conv.convert_block("unknown:block", 0, None, (2, 2, 2))

    stats = conv.get_stats()
    assert stats["processed"] == 3
    assert stats["converted"] == 2
    assert stats["failed"] == 1


# ---------------------------------------------------------------------------
# Testy edge cases
# ---------------------------------------------------------------------------
def test_convert_none_nbt():
    assert TileMultipartNBTConverter.convert(None) is None


def test_convert_missing_parts_key():
    nbt_1710 = {"id": "TileMultipart", "x": 0, "y": 0, "z": 0}
    nbt_1182 = TileMultipartNBTConverter.convert(nbt_1710)
    assert nbt_1182 is not None
    # Brak klucza "parts" w źródle powinien skutkować pustą listą w wyniku
    assert nbt_1182.get("parts") == []


def test_router_sends_microblock_savedmultipart_to_forge_multipart():
    from converters.router import convert_te_to_events

    events = convert_te_to_events(
        te_nbt={
            "id": "savedMultipart",
            "x": 1, "y": 2, "z": 3,
            "parts": [{"id": "mcr_face", "shape": 16, "material": "minecraft:stone"}],
        },
        block_numeric_id=0,
        metadata=0,
        global_pos=(1, 2, 3),
    )

    assert len(events) == 1
    assert events[0]["block"] == "cb_multipart:multipart"
    assert events[0]["nbt"]["id"] == "cb_multipart:saved_multipart"
    assert events[0]["nbt"]["parts"][0]["id"] == "cb_microblock:face"


def test_router_sanitizes_extrautils_microblock_material():
    from converters.router import convert_te_to_events

    events = convert_te_to_events(
        te_nbt={
            "id": "savedMultipart",
            "x": -100, "y": 70, "z": -65,
            "parts": [{"id": "mcr_face", "shape": 16, "material": "tile.extrautils:color_quartzBlock_2"}],
        },
        block_numeric_id=0,
        metadata=0,
        global_pos=(-100, 70, -65),
    )

    assert len(events) == 1
    assert events[0]["block"] == "cb_multipart:multipart"
    assert events[0]["nbt"]["parts"][0]["material"] == "minecraft:quartz_block"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
