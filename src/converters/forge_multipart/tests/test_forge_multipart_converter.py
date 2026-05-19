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
from converters.forge_multipart.mappings import map_block_id, map_part_id, map_te_id


# ---------------------------------------------------------------------------
# Testy mapowań
# ---------------------------------------------------------------------------
def test_map_block_id():
    assert map_block_id("ForgeMultipart:block") == "cb_multipart:block"
    assert map_block_id("unknown:block") is None


def test_map_te_id():
    assert map_te_id("savedMultipart") == "cb_multipart:tile_multipart"
    assert map_te_id("TileMultipart") == "cb_multipart:tile_multipart"
    assert map_te_id("ForgeMultipart:TileMultipart") == "cb_multipart:tile_multipart"


def test_map_part_id_microblocks():
    assert map_part_id("mcr_face") == "microblockcbe:face"
    assert map_part_id("mcr_hollow") == "microblockcbe:hollow"
    assert map_part_id("mcr_corner") == "microblockcbe:corner"
    assert map_part_id("mcr_edge") == "microblockcbe:edge"
    assert map_part_id("mcr_post") == "microblockcbe:post"


def test_map_part_id_vanilla():
    assert map_part_id("mc_torch") == "cb_multipart:torch"
    assert map_part_id("mc_redtorch") == "cb_multipart:redstone_torch"
    assert map_part_id("mc_button") == "cb_multipart:button"
    assert map_part_id("mc_lever") == "cb_multipart:lever"


def test_map_part_id_unknown_fallback():
    # Nieznane ID powinny zostać zwrócone bez zmian (z ostrzeżeniem w runtime)
    assert map_part_id("custom:unknown_part") == "custom:unknown_part"


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
    assert nbt_1182["id"] == "cb_multipart:tile_multipart"
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
    assert part["id"] == "microblockcbe:face"
    assert part["shape"] == 16
    assert part["material"] == "minecraft:stone"


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
    assert nbt_1182["id"] == "cb_multipart:tile_multipart"
    assert len(nbt_1182["parts"]) == 3

    assert nbt_1182["parts"][0]["id"] == "microblockcbe:hollow"
    assert nbt_1182["parts"][1]["id"] == "cb_multipart:torch"
    assert nbt_1182["parts"][1]["meta"] == 4
    assert nbt_1182["parts"][2]["id"] == "cb_multipart:lever"


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
    assert result.converted.block_id_1182 == "cb_multipart:block"
    assert result.converted.nbt_1182 is not None
    assert result.converted.nbt_1182["id"] == "cb_multipart:tile_multipart"


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
    assert event["block"] == "cb_multipart:block"
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
