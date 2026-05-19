"""Testy jednostkowe konwertera IC2 (IC2Converter + router integration).

Zakres:
- Mapowanie bloku + metadata → target_block_id
- Konwersja NBT przez registry converterów
- Produkcja ConversionEvent
- Integracja z router.py (detect_mod, convert_te_to_events)
- Placeholder handling
"""

from __future__ import annotations

import pytest

from converters.ic2.ic2_converter import IC2Converter
from converters.ic2.mappings.block_mappings import PLACEHOLDER_BLOCK
from converters.router import convert_te_to_events, detect_mod


class TestIC2ConverterBasic:
    """Podstawowe testy konwertera IC2."""

    @pytest.fixture
    def converter(self):
        c = IC2Converter()
        c.reset()
        return c

    def test_macerator_to_indreb_crusher(self, converter):
        nbt = {
            "id": "TileEntityMacerator",
            "facing": 3,
            "energy": 512.0,
            "progress": 200,
            "InvSlots": {
                "input": {"0": {"id": "minecraft:iron_ore", "Count": 1}},
                "output": {"0": {"id": "IC2:itemDustIron", "Count": 2}},
            },
        }
        result = converter.convert_block(
            block_id_1710="IC2:blockMachine",
            metadata=3,
            nbt_1710=nbt,
            position=(10, 64, -5),
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "indreb:crusher"
        assert result.converted.blockstate_props.get("facing") == "south"
        assert result.converted.nbt_1182 is not None
        assert result.converted.event is not None
        assert result.converted.event.mod == "ic2"

    def test_generator_to_indreb_generator(self, converter):
        nbt = {"id": "TileEntityGenerator", "facing": 2, "energy": 100.0}
        result = converter.convert_block(
            "IC2:blockGenerator", 0, nbt, (0, 70, 0)
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "indreb:generator"

    def test_batbox_to_indreb_battery_box(self, converter):
        nbt = {"id": "TileEntityElectricBatBox", "facing": 4, "energy": 1000.0}
        result = converter.convert_block(
            "IC2:blockElectric", 0, nbt, (5, 60, 5)
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "indreb:battery_box"
        assert result.converted.nbt_1182 is not None

    def test_copper_cable_to_indreb(self, converter):
        nbt = {"id": "TileEntityCable", "cableType": 0, "color": 0, "foamed": 0}
        result = converter.convert_block(
            "IC2:blockCable", 0, nbt, (1, 2, 3)
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "indreb:copper_cable_insulated"

    def test_transformer_identity_no_nbt(self, converter):
        # Transformers are mapped with "identity" converter (no block entity NBT)
        nbt = {"id": "TileEntityElectricTransformer", "facing": 2}
        result = converter.convert_block(
            "IC2:blockElectric", 3, nbt, (1, 2, 3)
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "indreb:lv_transformer"

    def test_placeholder_miner(self, converter):
        nbt = {"id": "TileEntityMiner", "facing": 2}
        result = converter.convert_block(
            "IC2:blockMachine", 7, nbt, (1, 2, 3)
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == PLACEHOLDER_BLOCK
        assert any("PLACEHOLDER" in w for w in result.converted.warnings)

    def test_unmapped_block_returns_error(self, converter):
        result = converter.convert_block(
            "IC2:blockSomeUnknown", 99, {}, (0, 0, 0)
        )
        assert not result.converted.success
        assert any("NOT-MAPPED" in e for e in result.converted.errors)

    def test_convert_by_te_id(self, converter):
        """Converter should resolve block_id from TE class name."""
        nbt = {"id": "TileEntityMacerator", "facing": 2, "energy": 0.0}
        result = converter.convert_tile_entity(
            te_id="TileEntityMacerator",
            nbt_1710=nbt,
            metadata=3,
            position=(1, 2, 3),
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "indreb:crusher"

    def test_stats_tracking(self, converter):
        converter.convert_block("IC2:blockMachine", 3, {}, (0, 0, 0))
        converter.convert_block("IC2:blockMachine", 7, {}, (0, 0, 0))
        converter.convert_block("IC2:blockUnknown", 99, {}, (0, 0, 0))
        assert converter.stats["processed"] == 3
        assert converter.stats["converted"] == 2
        assert converter.stats["failed"] == 1


class TestIC2RouterIntegration:
    """Testy integracji z router.py."""

    def test_detect_mod_ic2_macerator(self):
        assert detect_mod("TileEntityMacerator") == "ic2"

    def test_detect_mod_ic2_generator(self):
        assert detect_mod("TileEntityGenerator") == "ic2"

    def test_detect_mod_ic2_batbox(self):
        assert detect_mod("TileEntityElectricBatBox") == "ic2"

    def test_detect_mod_not_ic2(self):
        # Vanilla TEs should not match IC2
        assert detect_mod("Chest") == "vanilla"
        assert detect_mod("Furnace") == "vanilla"
        # Other mods
        assert detect_mod("TileEntityCarpentersBlock") == "carpentersblocks"
        assert detect_mod("TileEntityBookcase") == "bibliocraft"

    def test_convert_te_to_events_ic2_macerator(self):
        te_nbt = {
            "id": "TileEntityMacerator",
            "facing": 3,
            "energy": 512.0,
            "progress": 200,
        }
        events = convert_te_to_events(
            te_nbt=te_nbt,
            block_numeric_id=123,
            metadata=3,
            global_pos=(10, 64, -5),
        )
        assert len(events) == 1
        ev = events[0]
        assert ev["block"] == "indreb:crusher"
        assert ev["op"] == "set_block_entity"
        assert ev["pos"] == [10, 64, -5]
        assert ev["blockstate"]["facing"] == "south"
        # For indreb targets, progress is not mapped (unknown NBT shape)
        assert ev["nbt"]["energy"] == 2048  # 512 EU * 4 = 2048 FE

    def test_convert_te_to_events_ic2_placeholder(self):
        te_nbt = {"id": "TileEntityMiner", "facing": 2}
        events = convert_te_to_events(
            te_nbt=te_nbt,
            block_numeric_id=123,
            metadata=7,
            global_pos=(0, 0, 0),
        )
        assert len(events) == 1
        ev = events[0]
        assert ev["block"] == PLACEHOLDER_BLOCK
        assert ev["op"] == "set_block_entity"
        assert "legacy_ic2_nbt" in ev["nbt"]

    def test_convert_te_to_events_ic2_cable(self):
        te_nbt = {"id": "TileEntityCable", "cableType": 9, "color": 0, "foamed": 0}
        events = convert_te_to_events(
            te_nbt=te_nbt,
            block_numeric_id=123,
            metadata=9,
            global_pos=(1, 2, 3),
        )
        assert len(events) == 1
        ev = events[0]
        assert ev["block"] == "indreb:glass_fibre_cable"
        # indreb cables have no NBT (BlockEntityCable doesn't override save/load)
        assert ev.get("op") == "set_block"

    def test_transformer_has_energy_and_mode(self):
        te_nbt = {"id": "TileEntityElectricTransformer", "facing": 2, "energy": 100.0}
        events = convert_te_to_events(
            te_nbt=te_nbt,
            block_numeric_id=123,
            metadata=3,
            global_pos=(0, 0, 0),
        )
        assert len(events) == 1
        ev = events[0]
        assert ev["block"] == "indreb:lv_transformer"
        assert ev["nbt"]["energy"] == 400
        assert ev["nbt"]["transformerMode"] == 0

    def test_macerator_indreb_nbt_shape(self):
        """Verify indreb NBT shape matches decompiled sources."""
        te_nbt = {
            "id": "TileEntityMacerator",
            "facing": 3,
            "energy": 512.0,
            "progress": 200,
            "InvSlots": {
                "input": {"0": {"id": "minecraft:iron_ore", "Count": 1}},
                "output": {"0": {"id": "IC2:itemDustIron", "Count": 2}},
            },
        }
        events = convert_te_to_events(
            te_nbt=te_nbt,
            block_numeric_id=123,
            metadata=3,
            global_pos=(1, 2, 3),
        )
        ev = events[0]
        nbt = ev["nbt"]
        # IndRebBlockEntity.save shape
        assert "energy" in nbt  # flat int
        assert "active" in nbt  # boolean
        assert "progress" in nbt  # CompoundTag {progress, progressMax}
        assert "progress" in nbt["progress"]  # float
        assert "progressMax" in nbt["progress"]  # float
        assert "inventory" in nbt  # CompoundTag {Size, Items}
        assert "Size" in nbt["inventory"]
        assert "Items" in nbt["inventory"]
        # Slots should be unique (no duplicates)
        slots = [it["Slot"] for it in nbt["inventory"]["Items"]]
        assert len(slots) == len(set(slots)), f"Duplicate slots: {slots}"
