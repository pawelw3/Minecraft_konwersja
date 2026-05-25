"""
Testy jednostkowe konwertera BuildCraft.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from converters.buildcraft.buildcraft_converter import BuildCraftConverter


class TestBuildCraftConverter:
    def test_engine_wood_remove(self):
        conv = BuildCraftConverter()
        result = conv.convert_tile_entity(
            te_id="net.minecraft.src.buildcraft.energy.TileEngineWood",
            nbt_1710={
                "id": "net.minecraft.src.buildcraft.energy.TileEngineWood",
                "x": 10, "y": 64, "z": 10,
                "orientation": 0, "heat": 20.0, "energy": 0,
            },
            metadata=0,
            position=(10, 64, 10),
        )
        assert result.converted.success is True
        assert result.converted.block_id_1182 == "minecraft:air"
        assert conv.stats["removed"] == 1

    def test_engine_stone_convert(self):
        conv = BuildCraftConverter()
        result = conv.convert_tile_entity(
            te_id="net.minecraft.src.buildcraft.energy.TileEngineStone",
            nbt_1710={
                "id": "net.minecraft.src.buildcraft.energy.TileEngineStone",
                "x": 11, "y": 64, "z": 10,
                "orientation": 2,
                "heat": 25.0,
                "energy": 100,
                "burnTime": 800,
                "totalBurnTime": 1600,
                "Items": [{"Slot": 0, "id": 263, "Count": 16, "Damage": 0}],
            },
            metadata=0,
            position=(11, 64, 10),
        )
        assert result.converted.success is True
        assert result.converted.block_id_1182 == "thermal:dynamo_steam"
        assert result.converted.blockstate_props.get("facing") == "north"
        assert result.converted.nbt_1182 is not None
        assert "Items" in result.converted.nbt_1182
        assert conv.stats["converted"] == 1

    def test_engine_iron_convert(self):
        conv = BuildCraftConverter()
        result = conv.convert_tile_entity(
            te_id="net.minecraft.src.buildcraft.energy.TileEngineIron",
            nbt_1710={
                "id": "net.minecraft.src.buildcraft.energy.TileEngineIron",
                "x": 12, "y": 64, "z": 10,
                "orientation": 5,
                "heat": 40.0,
                "energy": 500,
                "tankFuel": {"FluidName": "fuel", "Amount": 2000},
                "tankCoolant": {"FluidName": "water", "Amount": 1000},
            },
            metadata=0,
            position=(12, 64, 10),
        )
        assert result.converted.success is True
        assert result.converted.block_id_1182 == "thermal:dynamo_compression"
        assert result.converted.blockstate_props.get("facing") == "east"
        assert result.converted.nbt_1182 is not None
        assert "Tanks" in result.converted.nbt_1182

    def test_pipe_convert(self):
        conv = BuildCraftConverter()
        result = conv.convert_tile_entity(
            te_id="net.minecraft.src.buildcraft.transport.GenericPipe",
            nbt_1710={
                "id": "net.minecraft.src.buildcraft.transport.GenericPipe",
                "x": 13, "y": 64, "z": 10,
                "pipeId": 4163,
                "inputOpen": 63,
                "outputOpen": 63,
                "wireSet[0]": 0,
                "travelingEntities": [],
            },
            metadata=0,
            position=(13, 64, 10),
        )
        assert result.converted.success is True
        assert result.converted.block_id_1182 == "pipez:universal_pipe"

    def test_tank_convert(self):
        conv = BuildCraftConverter()
        result = conv.convert_tile_entity(
            te_id="net.minecraft.src.buildcraft.factory.TileTank",
            nbt_1710={
                "id": "net.minecraft.src.buildcraft.factory.TileTank",
                "x": 14, "y": 64, "z": 10,
                "tank": {"FluidName": "water", "Amount": 4000},
            },
            metadata=0,
            position=(14, 64, 10),
        )
        assert result.converted.success is True
        assert result.converted.block_id_1182 == "mekanism:basic_fluid_tank"
        assert result.converted.nbt_1182 is not None
        assert "Tanks" in result.converted.nbt_1182

    def test_pump_convert(self):
        conv = BuildCraftConverter()
        result = conv.convert_tile_entity(
            te_id="net.minecraft.src.buildcraft.factory.TilePump",
            nbt_1710={
                "id": "net.minecraft.src.buildcraft.factory.TilePump",
                "x": 15, "y": 64, "z": 10,
                "battery": {"energy": 300, "maxEnergy": 1000},
                "tank": {"FluidName": "water", "Amount": 500},
            },
            metadata=0,
            position=(15, 64, 10),
        )
        assert result.converted.success is True
        assert result.converted.block_id_1182 == "mekanism:electric_pump"

    def test_refinery_convert(self):
        conv = BuildCraftConverter()
        result = conv.convert_tile_entity(
            te_id="net.minecraft.src.buildcraft.factory.Refinery",
            nbt_1710={
                "id": "net.minecraft.src.buildcraft.factory.Refinery",
                "x": 16, "y": 64, "z": 10,
                "tank1": {"acceptedFluid": "oil", "Empty": ""},
                "tank2": {"acceptedFluid": "oil", "FluidName": "oil", "Amount": 200},
                "result": {"acceptedFluid": "fuel", "Empty": ""},
                "battery": {"energy": 0, "maxEnergy": 10000},
            },
            metadata=0,
            position=(16, 64, 10),
        )
        assert result.converted.success is True
        assert result.converted.block_id_1182 == "thermal:machine_refinery"

    def test_assembly_table_remove(self):
        conv = BuildCraftConverter()
        result = conv.convert_tile_entity(
            te_id="net.minecraft.src.buildcraft.factory.TileAssemblyTable",
            nbt_1710={
                "id": "net.minecraft.src.buildcraft.factory.TileAssemblyTable",
                "x": 17, "y": 64, "z": 10,
                "inv": [], "energy": 0,
            },
            metadata=0,
            position=(17, 64, 10),
        )
        assert result.converted.success is True
        assert result.converted.block_id_1182 == "minecraft:air"

    def test_unknown_te_fails(self):
        conv = BuildCraftConverter()
        result = conv.convert_tile_entity(
            te_id="net.minecraft.src.buildcraft.unknown.TileUnknown",
            nbt_1710={"id": "net.minecraft.src.buildcraft.unknown.TileUnknown", "x": 18, "y": 64, "z": 10},
            metadata=0,
            position=(18, 64, 10),
        )
        assert result.converted.success is False
        assert conv.stats["failed"] == 1

    def test_to_dict(self):
        conv = BuildCraftConverter()
        result = conv.convert_tile_entity(
            te_id="net.minecraft.src.buildcraft.factory.TileTank",
            nbt_1710={
                "id": "net.minecraft.src.buildcraft.factory.TileTank",
                "x": 19, "y": 64, "z": 10,
                "tank": {"Empty": ""},
            },
            metadata=0,
            position=(19, 64, 10),
        )
        d = result.to_dict()
        assert d["original_id"] == "net.minecraft.src.buildcraft.factory.TileTank"
        assert d["new_id"] == "mekanism:basic_fluid_tank"
        assert d["original_pos"] == (19, 64, 10)
