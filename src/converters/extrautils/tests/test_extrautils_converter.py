"""
Testy jednostkowe konwertera Extra Utilities.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from converters.extrautils.extrautils_converter import ExtraUtilsConverter, ConversionResult
from converters.extrautils.mappings.block_mappings import get_mapping, TE_ID_TO_BLOCK
from converters.extrautils.nbt_converters.generator_converter import convert_generator_nbt
from converters.extrautils.nbt_converters.filing_cabinet_converter import convert_filing_cabinet_nbt
from converters.extrautils.nbt_converters.base_converter import (
    convert_rotation_to_facing,
    convert_energy,
    convert_fluid_tank,
)


class TestExtraUtilsConverter:
    def setup_method(self):
        self.conv = ExtraUtilsConverter()

    # ── Generator mappings ──

    def test_generator_lava_mapping(self):
        """Lava Generator (meta 2) → Magmatic Dynamo."""
        mapping = get_mapping("extrautils:generator", 2)
        assert mapping is not None
        assert mapping.target_block_id == "thermal:dynamo_magmatic"

    def test_generator_stone_mapping(self):
        """Survivalist Generator (meta 0) → Stirling Dynamo."""
        mapping = get_mapping("extrautils:generator", 0)
        assert mapping.target_block_id == "thermal:dynamo_stirling"

    def test_generator_x8_lava_mapping(self):
        """Lava Generator x8 (block .8, meta 2) → Magmatic Dynamo."""
        mapping = get_mapping("extrautils:generator.8", 2)
        assert mapping is not None
        assert mapping.target_block_id == "thermal:dynamo_magmatic"

    def test_generator_x64_solar_mapping(self):
        """Solar Generator x64 (block .64, meta 7) → Solar Generator (Mek)."""
        mapping = get_mapping("extrautils:generator.64", 7)
        assert mapping.target_block_id == "mekanismgenerators:solar_generator"

    # ── Utility block mappings ──

    def test_magnum_torch_mapping(self):
        mapping = get_mapping("extrautils:magnumTorch", 0)
        assert mapping.target_block_id == "torchmaster:megatorch"

    def test_cursed_earth_mapping(self):
        mapping = get_mapping("extrautils:cursedEarth", 0)
        assert mapping.target_block_id == "cursedearth:cursed_earth"

    def test_angel_block_mapping(self):
        mapping = get_mapping("extrautils:angelBlock", 0)
        assert mapping.target_block_id == "angelblockrenewed:angel_block"

    def test_trash_can_item_mapping(self):
        mapping = get_mapping("extrautils:trashCan", 0)
        assert mapping.target_block_id == "trashcans:item_trash_can"

    def test_trash_can_fluid_mapping(self):
        mapping = get_mapping("extrautils:trashCan", 1)
        assert mapping.target_block_id == "trashcans:liquid_trash_can"

    def test_trash_can_energy_mapping(self):
        mapping = get_mapping("extrautils:trashCan", 2)
        assert mapping.target_block_id == "trashcans:energy_trash_can"

    # ── Extended mappings (Zadanie 3) ──

    def test_filing_cabinet_mapping(self):
        mapping = get_mapping("extrautils:filing", 0)
        assert mapping is not None
        assert mapping.target_block_id == "conversion_placeholders:inventory_placeholder"

    def test_filing_cabinet_diamond_mapping(self):
        mapping = get_mapping("extrautils:filing", 6)
        assert mapping is not None
        assert mapping.target_block_id == "conversion_placeholders:inventory_placeholder"

    def test_drum_mapping(self):
        mapping = get_mapping("extrautils:drum", 0)
        assert mapping is not None
        assert mapping.target_block_id == "conversion_placeholders:block_entity_placeholder"

    def test_ender_quarry_mapping(self):
        mapping = get_mapping("extrautils:enderQuarry", 0)
        assert mapping is not None
        assert mapping.target_block_id == "conversion_placeholders:block_entity_placeholder"

    def test_ender_thermic_pump_mapping(self):
        mapping = get_mapping("extrautils:enderThermicPump", 0)
        assert mapping is not None
        assert mapping.target_block_id == "mekanism:electric_pump"

    # ── Converter block conversion ──

    def test_convert_generator_lava_block_no_nbt(self):
        result = self.conv.convert_block("extrautils:generator", metadata=2)
        assert result.success
        assert result.block_id_1182 == "thermal:dynamo_magmatic"

    def test_convert_generator_lava_block_with_nbt(self):
        """Konwersja generatora z prawdziwym NBT z mapy."""
        nbt = {
            "id": "extrautils:generatorlava",
            "x": -88, "y": 50, "z": 903,
            "Energy": 0,
            "rotation": 3,
            "Tank_0": {"Empty": ""},
            "coolDown": 0.0,
        }
        result = self.conv.convert_block("extrautils:generator", metadata=2, nbt_1710=nbt)
        assert result.success
        assert result.block_id_1182 == "thermal:dynamo_magmatic"
        assert result.blockstate_props is not None
        assert result.blockstate_props.get("facing") == "east"
        assert result.nbt_1182 is not None
        assert result.nbt_1182.get("id") == "thermal:dynamo_magmatic"
        assert result.nbt_1182.get("energy") == {"Stored": 0, "Capacity": 100000}

    def test_convert_generator_lava_block_with_energy(self):
        """Generator z energią — powinien wygenerować ostrzeżenie."""
        nbt = {
            "x": 0, "y": 64, "z": 0,
            "Energy": 50000,
            "rotation": 1,
            "Tank_0": {"Empty": ""},
            "coolDown": 0.0,
        }
        result = self.conv.convert_block("extrautils:generator", metadata=2, nbt_1710=nbt)
        assert result.success
        assert result.nbt_1182["energy"] == {"Stored": 50000, "Capacity": 100000}
        assert any("ENERGY-TRANSFERRED" in w for w in result.warnings)
        assert result.blockstate_props.get("facing") == "west"

    def test_convert_generator_lava_block_with_fluid(self):
        """Generator z lawą w tanku — powinien przenieść płyn."""
        nbt = {
            "x": 0, "y": 64, "z": 0,
            "Energy": 0,
            "rotation": 0,
            "Tank_0": {"FluidName": "lava", "Amount": 4000},
            "coolDown": 0.0,
        }
        result = self.conv.convert_block("extrautils:generator", metadata=2, nbt_1710=nbt)
        assert result.success
        assert result.nbt_1182.get("fuel") == {"FluidName": "lava", "Amount": 4000}
        assert any("FLUID-TRANSFERRED" in w for w in result.warnings)

    def test_convert_magnum_torch_block(self):
        result = self.conv.convert_block("extrautils:magnumTorch", metadata=0)
        assert result.success
        assert result.block_id_1182 == "torchmaster:megatorch"

    def test_convert_filing_cabinet_empty(self):
        """Pusty Filing Cabinet → placeholder."""
        nbt = {"id": "TileEntityFilingCabinet", "x": 10, "y": 64, "z": 10}
        result = self.conv.convert_block("extrautils:filing", metadata=4, nbt_1710=nbt)
        assert result.success
        assert result.block_id_1182 == "conversion_placeholders:inventory_placeholder"
        assert result.nbt_1182 is not None
        assert result.nbt_1182.get("id") == "conversion_placeholders:inventory_placeholder"
        assert result.nbt_1182.get("source_mod") == "extrautils"

    def test_convert_filing_cabinet_with_items(self):
        """Filing Cabinet z itemami — powinien przenieść inventory."""
        nbt = {
            "id": "TileEntityFilingCabinet",
            "x": 10, "y": 64, "z": 10,
            "item_no": 2,
            "item_0": {"id": "minecraft:stone", "Count": 1, "Damage": 0, "Size": 64},
            "item_1": {"id": "minecraft:dirt", "Count": 1, "Damage": 0, "Size": 32},
        }
        result = self.conv.convert_block("extrautils:filing", metadata=4, nbt_1710=nbt)
        assert result.success
        assert result.block_id_1182 == "conversion_placeholders:inventory_placeholder"
        items = result.nbt_1182.get("Items", [])
        assert len(items) == 2
        assert items[0]["id"] == "minecraft:stone"
        assert items[0]["Count"] == 64
        assert items[1]["id"] == "minecraft:dirt"
        assert items[1]["Count"] == 32

    def test_convert_filing_cabinet_overflow(self):
        """Filing Cabinet z >54 itemami — ostrzeżenie o przepełnieniu."""
        nbt = {
            "id": "TileEntityFilingCabinet",
            "x": 10, "y": 64, "z": 10,
            "item_no": 60,
        }
        for i in range(60):
            nbt[f"item_{i}"] = {"id": "minecraft:stone", "Count": 1, "Damage": 0, "Size": 64}
        result = self.conv.convert_block("extrautils:filing", metadata=4, nbt_1710=nbt)
        assert result.success
        assert any("OVERFLOW" in w for w in result.warnings)
        assert len(result.nbt_1182.get("Items", [])) == 54

    def test_convert_unknown_block(self):
        result = self.conv.convert_block("extrautils:unknownBlock", metadata=0)
        assert not result.success
        assert any("NOT-MAPPED" in e for e in result.errors)

    def test_convert_non_extrautils_block(self):
        result = self.conv.convert_block("minecraft:stone", metadata=0)
        assert not result.success
        assert any("NOT-EXTRAUTILS" in e for e in result.errors)

    # ── Converter TE conversion ──

    def test_convert_te_generator_lava(self):
        """TE id 'extrautils:generatorlava' → Magmatic Dynamo."""
        nbt = {"id": "extrautils:generatorlava", "x": 10, "y": 64, "z": 10}
        result = self.conv.convert_tile_entity("extrautils:generatorlava", nbt, metadata=2)
        assert result.success
        assert result.block_id_1182 == "thermal:dynamo_magmatic"

    def test_convert_te_antimobtorch(self):
        """TE id 'TileEntityAntiMobTorch' → Mega Torch."""
        nbt = {"id": "TileEntityAntiMobTorch", "x": 5, "y": 70, "z": 5}
        result = self.conv.convert_tile_entity("TileEntityAntiMobTorch", nbt, metadata=0)
        assert result.success
        assert result.block_id_1182 == "torchmaster:megatorch"

    def test_convert_te_filing_cabinet(self):
        """TE id 'TileEntityFilingCabinet' → placeholder."""
        nbt = {"id": "TileEntityFilingCabinet", "x": 10, "y": 64, "z": 10}
        result = self.conv.convert_tile_entity("TileEntityFilingCabinet", nbt, metadata=4)
        assert result.success
        assert result.block_id_1182 == "conversion_placeholders:inventory_placeholder"

    def test_convert_te_unknown(self):
        nbt = {"id": "extrautils:someUnknownTE"}
        result = self.conv.convert_tile_entity("extrautils:someUnknownTE", nbt)
        assert not result.success
        assert any("TE-NOT-MAPPED" in e for e in result.errors)

    # ── NBT converter tests ──

    def test_rotation_to_facing(self):
        assert convert_rotation_to_facing({"rotation": 0}) == "south"
        assert convert_rotation_to_facing({"rotation": 1}) == "west"
        assert convert_rotation_to_facing({"rotation": 2}) == "north"
        assert convert_rotation_to_facing({"rotation": 3}) == "east"
        assert convert_rotation_to_facing({"rotation": 4}) == "south"  # modulo 4
        assert convert_rotation_to_facing({}) == "south"

    def test_convert_energy_rf_to_fe(self):
        assert convert_energy({"Energy": 5000}) == {"Stored": 5000, "Capacity": 100000}
        assert convert_energy({"Energy": 0}) == {"Stored": 0, "Capacity": 100000}
        assert convert_energy({}) == {"Stored": 0, "Capacity": 100000}
        assert convert_energy({"Energy": {"Storage": 25000, "Capacity": 50000}}) == {"Stored": 25000, "Capacity": 50000}

    def test_convert_fluid_tank_empty(self):
        assert convert_fluid_tank({"Empty": ""}) == {"FluidName": "", "Amount": 0}

    def test_convert_fluid_tank_with_lava(self):
        assert convert_fluid_tank({"FluidName": "lava", "Amount": 1000}) == {"FluidName": "lava", "Amount": 1000}

    def test_convert_generator_nbt_full(self):
        nbt = {
            "x": 10, "y": 64, "z": 10,
            "Energy": 25000,
            "rotation": 2,
            "Tank_0": {"FluidName": "lava", "Amount": 2000},
            "coolDown": 5.0,
            "backup": {"x": 10, "y": 64, "z": 10},
        }
        result = convert_generator_nbt(nbt, "thermal:dynamo_magmatic")
        assert result["nbt"]["id"] == "thermal:dynamo_magmatic"
        assert result["nbt"]["x"] == 10
        assert result["nbt"]["energy"] == {"Stored": 25000, "Capacity": 100000}
        assert result["blockstate_props"]["facing"] == "north"
        assert result["nbt"]["fuel"] == {"FluidName": "lava", "Amount": 2000}
        assert any("ENERGY-TRANSFERRED" in w for w in result["warnings"])
        assert any("COOLDOWN-LOST" in w for w in result["warnings"])
        assert any("BACKUP-IGNORED" in w for w in result["warnings"])

    def test_convert_filing_cabinet_nbt_empty(self):
        nbt = {"id": "TileEntityFilingCabinet", "x": 10, "y": 64, "z": 10}
        result = convert_filing_cabinet_nbt(nbt, "conversion_placeholders:inventory_placeholder")
        assert result["nbt"]["id"] == "conversion_placeholders:inventory_placeholder"
        assert "Items" not in result["nbt"]
        assert result["nbt"]["original_nbt"] == nbt

    def test_convert_filing_cabinet_nbt_with_items(self):
        nbt = {
            "id": "TileEntityFilingCabinet",
            "x": 10, "y": 64, "z": 10,
            "item_no": 2,
            "item_0": {"id": "minecraft:stone", "Count": 1, "Damage": 0, "Size": 64},
            "item_1": {"id": "minecraft:diamond", "Count": 1, "Damage": 0, "Size": 7},
        }
        result = convert_filing_cabinet_nbt(nbt, "conversion_placeholders:inventory_placeholder")
        items = result["nbt"]["Items"]
        assert len(items) == 2
        assert items[0] == {"Slot": 0, "id": "minecraft:stone", "Count": 64}
        assert items[1] == {"Slot": 1, "id": "minecraft:diamond", "Count": 7}

    # ── TE_ID_TO_BLOCK completeness ──

    def test_all_generator_te_ids_mapped(self):
        """Wszystkie znane TE id generatorów muszą być w TE_ID_TO_BLOCK."""
        expected = [
            "extrautils:generatorstone",
            "extrautils:generatorbase",
            "extrautils:generatorlava",
            "extrautils:generatorender",
            "extrautils:generatorredflux",
            "extrautils:generatorfood",
            "extrautils:generatorpotion",
            "extrautils:generatorsolar",
            "extrautils:generatortnt",
            "extrautils:generatorpink",
            "extrautils:generatoroverclocked",
            "extrautils:generatornether",
        ]
        for te_id in expected:
            assert te_id in TE_ID_TO_BLOCK, f"Missing TE mapping for {te_id}"

    def test_te_id_to_block_has_antimobtorch(self):
        assert "TileEntityAntiMobTorch" in TE_ID_TO_BLOCK
        assert TE_ID_TO_BLOCK["TileEntityAntiMobTorch"] == ("extrautils:magnumTorch", 0)

    def test_te_id_to_block_has_filing_cabinet(self):
        assert "TileEntityFilingCabinet" in TE_ID_TO_BLOCK
        assert TE_ID_TO_BLOCK["TileEntityFilingCabinet"] == ("extrautils:filing", 0)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
