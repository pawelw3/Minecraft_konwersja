"""
Testy jednostkowe głównego konwertera Railcraft.

Uruchomienie:
    python -m pytest src/converters/railcraft/tests/test_railcraft_converter.py -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from converters.railcraft.railcraft_converter import RailcraftConverter


class TestConverterTileEntityResolution:
    def setup_method(self):
        self.c = RailcraftConverter()

    def test_alpha_machine_te_resolution(self):
        r = self.c.convert_tile_entity("RCCokeOvenTile", {"id": "RCCokeOvenTile"}, 7, (0, 0, 0))
        assert r.converted.block_id_1182 == "immersiveengineering:coke_oven"

    def test_beta_machine_te_resolution(self):
        r = self.c.convert_tile_entity("RCIronTankWallTile", {"id": "RCIronTankWallTile"}, 0, (0, 0, 0))
        assert r.converted.block_id_1182 == "create:fluid_tank"

    def test_gamma_machine_te_resolution(self):
        r = self.c.convert_tile_entity("RCLoaderTile", {"id": "RCLoaderTile"}, 0, (0, 0, 0))
        assert r.converted.block_id_1182 == "create:chute"

    def test_delta_machine_te_resolution(self):
        r = self.c.convert_tile_entity("RCWireTile", {"id": "RCWireTile"}, 0, (0, 0, 0))
        assert r.converted.block_id_1182 == "minecraft:redstone_wire"

    def test_epsilon_machine_te_resolution(self):
        r = self.c.convert_tile_entity("RCFluxTransformerTile", {"id": "RCFluxTransformerTile"}, 4, (0, 0, 0))
        assert r.converted.block_id_1182 == "mekanism:basic_energy_cube"

    def test_track_te_resolution(self):
        r = self.c.convert_tile_entity("RailcraftTrackTile", {"id": "RailcraftTrackTile", "trackTag": "railcraft:track.switch"}, 7, (0, 0, 0))
        assert r.converted.block_id_1182 == "create:track"

    def test_signal_te_resolution(self):
        r = self.c.convert_tile_entity("RCTileStructureBlockSignal", {"id": "RCTileStructureBlockSignal"}, 3, (0, 0, 0))
        assert r.converted.block_id_1182 == "railways:semaphore"

    def test_detector_te_resolution(self):
        r = self.c.convert_tile_entity("RCDetectorTile", {"id": "RCDetectorTile"}, 0, (0, 0, 0))
        assert r.converted.block_id_1182 == "minecraft:observer"

    def test_hidden_tile_removed(self):
        r = self.c.convert_tile_entity("RCHiddenTile", {"id": "RCHiddenTile", "seed": 123}, 0, (0, 0, 0))
        assert r.converted.block_id_1182 == "minecraft:air"
        assert r.converted.success is True
        assert any("RC-W-IGNORED" in w for w in r.converted.warnings)

    def test_anchor_placeholder(self):
        r = self.c.convert_tile_entity("RCWorldAnchorTile", {"id": "RCWorldAnchorTile"}, 0, (0, 0, 0))
        assert r.converted.block_id_1182 == "conversion_placeholders:block_entity_placeholder"

    def test_unknown_te_fallback(self):
        r = self.c.convert_tile_entity("RCFakeTile", {"id": "RCFakeTile"}, 0, (0, 0, 0))
        assert r.converted.success is False
        assert any("RC-E-BLOCK-NOT-MAPPED" in e for e in r.converted.errors)

    def test_stats_accumulate(self):
        c = RailcraftConverter()
        c.convert_tile_entity("RCCokeOvenTile", {"id": "RCCokeOvenTile"}, 7, (0, 0, 0))
        c.convert_tile_entity("RCFakeTile", {"id": "RCFakeTile"}, 0, (0, 0, 0))
        assert c.stats["processed"] == 2
        assert c.stats["converted"] == 1
        assert c.stats["failed"] == 1


class TestConverterBlockDirect:
    def setup_method(self):
        self.c = RailcraftConverter()

    def test_direct_block_conversion(self):
        r = self.c.convert_block("railcraft.machine.alpha", 12, {"id": "RCBlastFurnaceTile"}, (10, 20, 30))
        assert r.converted.block_id_1182 == "immersiveengineering:blast_furnace"
        assert r.original_pos == (10, 20, 30)

    def test_non_railcraft_block_rejected(self):
        r = self.c.convert_block("minecraft:stone", 0, None, (0, 0, 0))
        assert r.converted.success is False
        assert any("RC-E-NOT-RAILCRAFT" in e for e in r.converted.errors)


class TestRouterIntegration:
    """Testy integracyjne z converters.router."""

    def test_router_coke_oven(self):
        from converters.router import convert_te_to_events
        events = convert_te_to_events(
            {"id": "RCCokeOvenTile", "master": True},
            block_numeric_id=0, metadata=7, global_pos=(10, 64, 10),
        )
        assert len(events) == 1
        ev = events[0]
        assert ev["block"] == "immersiveengineering:coke_oven"
        assert ev["op"] == "set_block_entity"
        assert ev["pos"] == [10, 64, 10]

    def test_router_hidden_tile_air(self):
        from converters.router import convert_te_to_events
        events = convert_te_to_events(
            {"id": "RCHiddenTile", "seed": 12345},
            block_numeric_id=0, metadata=0, global_pos=(5, 64, 5),
        )
        assert len(events) == 1
        ev = events[0]
        assert ev["block"] == "minecraft:air"
        assert ev["op"] == "set_block"

    def test_router_unknown_railcraft_placeholder(self):
        from converters.router import convert_te_to_events
        events = convert_te_to_events(
            {"id": "RCFakeTile"},
            block_numeric_id=0, metadata=0, global_pos=(0, 0, 0),
        )
        assert len(events) == 1
        ev = events[0]
        assert ev["block"] == "conversion_placeholders:block_entity_placeholder"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
