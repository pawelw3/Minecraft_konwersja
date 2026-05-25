"""
Testy jednostkowe symulacji konwersji Railcraft 1.7.10 → 1.18.2.

Uruchomienie:
    python -m pytest src/converters/railcraft/tests/test_railcraft_simulations.py -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from converters.railcraft.mappings.block_mappings import get_mapping, PLACEHOLDER_BLOCK_ID
from converters.railcraft.simulations.railcraft_simulation import (
    convert_track_nbt,
    convert_machine_inventory_nbt,
    convert_multiblock_nbt,
    convert_signal_nbt,
    convert_detector_nbt,
    convert_anchor_nbt,
    simulate_railcraft_conversion,
)


class TestTrackMappings:
    def test_switch_track_mapping(self):
        m = get_mapping("railcraft.track", 7)
        assert m is not None
        assert m.target_block_id == "create:track"
        assert m.track_tag == "railcraft:track.switch"

    def test_deprecated_boarding_track(self):
        m = get_mapping("railcraft.track", 0)
        assert m is not None
        assert m.target_block_id == PLACEHOLDER_BLOCK_ID
        assert "Deprecated" in m.notes

    def test_electric_track(self):
        m = get_mapping("railcraft.track", 43)
        assert m.target_block_id == "create:track"
        assert "no electrification" in m.notes

    def test_buffer_stop(self):
        m = get_mapping("railcraft.track", 28)
        assert m.target_block_id == PLACEHOLDER_BLOCK_ID

    def test_coupler_track(self):
        m = get_mapping("railcraft.track", 22)
        assert m.target_block_id == "railways:track_coupler"


class TestMachineAlphaMappings:
    def test_coke_oven(self):
        m = get_mapping("railcraft.machine.alpha", 7)
        assert m.target_block_id == "immersiveengineering:coke_oven"

    def test_blast_furnace(self):
        m = get_mapping("railcraft.machine.alpha", 12)
        assert m.target_block_id == "immersiveengineering:blast_furnace"

    def test_rock_crusher(self):
        m = get_mapping("railcraft.machine.alpha", 15)
        assert m.target_block_id == "create:crushing_wheel"

    def test_world_anchor_placeholder(self):
        m = get_mapping("railcraft.machine.alpha", 0)
        assert m.target_block_id == PLACEHOLDER_BLOCK_ID

    def test_rolling_machine(self):
        m = get_mapping("railcraft.machine.alpha", 8)
        assert m.target_block_id == "create:mechanical_press"


class TestMachineBetaMappings:
    def test_steam_engine(self):
        m = get_mapping("railcraft.machine.beta", 7)
        assert m.target_block_id == "create:steam_engine"

    def test_iron_tank(self):
        m = get_mapping("railcraft.machine.beta", 0)
        assert m.target_block_id == "create:fluid_tank"

    def test_void_chest(self):
        m = get_mapping("railcraft.machine.beta", 11)
        assert m.target_block_id == "thermal:device_nullifier"


class TestMachineGammaMappings:
    def test_item_loader(self):
        m = get_mapping("railcraft.machine.gamma", 0)
        assert m.target_block_id == "create:chute"

    def test_energy_loader(self):
        m = get_mapping("railcraft.machine.gamma", 6)
        assert m.target_block_id == "mekanism:basic_universal_cable"


class TestSignalMappings:
    def test_block_signal(self):
        m = get_mapping("railcraft.signal", 3)
        assert m.target_block_id == "railways:semaphore"

    def test_switch_lever(self):
        m = get_mapping("railcraft.signal", 4)
        assert m.target_block_id == "minecraft:lever"


class TestDetectorMappings:
    def test_all_detectors_to_observer(self):
        for meta in range(17):
            m = get_mapping("railcraft.detector", meta)
            assert m.target_block_id == "minecraft:observer"


class TestOtherMappings:
    def test_residual_heat_ignored(self):
        m = get_mapping("railcraft.residual.heat", 0)
        assert m.target_block_id == "minecraft:air"


class TestTrackNBTConversion:
    def test_switch_track_nbt(self):
        nbt, props, warnings = convert_track_nbt({"trackTag": "railcraft:track.switch"})
        assert props["shape"] == "north_south"
        assert nbt is None
        assert not any("LOST" in w for w in warnings)

    def test_booster_track_warns(self):
        nbt, props, warnings = convert_track_nbt({"trackTag": "railcraft:track.speed.boost"})
        assert any("RC-W-TRACK-SPECIAL-LOST" in w for w in warnings)

    def test_legacy_track_id_warns(self):
        nbt, props, warnings = convert_track_nbt({"trackId": 7})
        assert any("RC-W-TRACK-LEGACY-ID" in w for w in warnings)


class TestInventoryConversion:
    def test_items_preserved_with_warning(self):
        nbt, warnings = convert_machine_inventory_nbt({
            "Items": [{"Slot": 0, "id": "minecraft:iron_ingot", "Count": 2}]
        })
        assert nbt is not None
        assert "Items" in nbt
        assert any("RC-W-ITEM-IDS" in w for w in warnings)

    def test_empty_inventory(self):
        nbt, warnings = convert_machine_inventory_nbt({})
        assert nbt is None
        assert warnings == []


class TestMultiblockConversion:
    def test_master_flag_preserved(self):
        nbt, warnings = convert_multiblock_nbt({"master": True, "pattern": {"x": 1}})
        assert nbt is not None
        assert nbt.get("legacy_railcraft", {}).get("master") is True
        assert any("RC-W-MULTIBLOCK" in w for w in warnings)


class TestSignalNBTConversion:
    def test_signal_warning(self):
        nbt, props, warnings = convert_signal_nbt({"id": "RCTileStructureBlockSignal"})
        assert any("RC-W-SIGNAL-LOST" in w for w in warnings)

    def test_box_warning(self):
        nbt, props, warnings = convert_signal_nbt({"id": "RCTileStructureControllerBox"})
        assert any("RC-W-SIGNAL-BOX-LOST" in w for w in warnings)


class TestDetectorNBTConversion:
    def test_observer_with_warning(self):
        nbt, props, warnings = convert_detector_nbt({"id": "RCDetectorTile"})
        assert nbt is None
        assert props["facing"] == "north"
        assert any("RC-W-DETECTOR-LOST" in w for w in warnings)


class TestAnchorNBTConversion:
    def test_anchor_lost_warning(self):
        nbt, warnings = convert_anchor_nbt({"id": "RCWorldAnchorTile"})
        assert nbt is None
        assert any("RC-W-ANCHOR-LOST" in w for w in warnings)


class TestEndToEndSimulation:
    def test_coke_oven_e2e(self):
        result = simulate_railcraft_conversion(
            "railcraft.machine.alpha", 7,
            {"id": "RCCokeOvenTile", "master": True, "Items": [{"Slot": 0, "id": "minecraft:coal", "Count": 8}]}
        )
        assert result["block_id_1182"] == "immersiveengineering:coke_oven"
        assert result["nbt_1182"] is not None
        assert any("RC-W-MULTIBLOCK" in w for w in result["warnings"])

    def test_hidden_tile_e2e(self):
        result = simulate_railcraft_conversion(
            "railcraft.residual.heat", 0,
            {"id": "RCHiddenTile", "seed": 12345}
        )
        assert result["block_id_1182"] == "minecraft:air"
        assert any("RC-W-IGNORED" in w for w in result["warnings"])

    def test_unknown_block(self):
        result = simulate_railcraft_conversion("railcraft.unknown", 99, None)
        assert result["block_id_1182"] == PLACEHOLDER_BLOCK_ID
        assert any("RC-E-UNKNOWN-BLOCK" in e for e in result["errors"])


class TestSlabStairMappings:
    def test_slab_mapping_exists(self):
        m = get_mapping("railcraft.slab", 5)
        assert m is not None
        assert m.target_block_id == "framedblocks:framed_slab"

    def test_stair_mapping_exists(self):
        m = get_mapping("railcraft.stair", 3)
        assert m is not None
        assert m.target_block_id == "framedblocks:framed_stairs"

    def test_slab_bottom_half(self):
        result = simulate_railcraft_conversion("railcraft.slab", 2, {"id": "RCSlabTile", "slab": "IRON"})
        assert result["blockstate_props"]["type"] == "bottom"
        assert any("RC-W-SLAB-MATERIAL-LOST" in w for w in result["warnings"])

    def test_slab_top_half(self):
        result = simulate_railcraft_conversion("railcraft.slab", 10, {"id": "RCSlabTile", "slab": "STEEL"})
        assert result["blockstate_props"]["type"] == "top"

    def test_stair_facing_and_half(self):
        result = simulate_railcraft_conversion("railcraft.stair", 3, {"id": "RCStairTile", "stair": "IRON"})
        assert result["blockstate_props"]["facing"] == "north"
        assert result["blockstate_props"]["half"] == "bottom"
        assert result["blockstate_props"]["shape"] == "straight"
        assert any("RC-W-STAIR-MATERIAL-LOST" in w for w in result["warnings"])

    def test_stair_upside_down(self):
        result = simulate_railcraft_conversion("railcraft.stair", 6, {"id": "RCStairTile", "stair": "COPPER"})
        assert result["blockstate_props"]["facing"] == "south"
        assert result["blockstate_props"]["half"] == "top"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
