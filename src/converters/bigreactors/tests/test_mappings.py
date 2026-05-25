"""Testy mapowan blokow Big Reactors -> Bigger Reactors."""

from __future__ import annotations

import pytest

from converters.bigreactors.mappings import (
    REACTOR_PART_BY_META,
    TURBINE_PART_BY_META,
    METAL_BLOCK_BY_META,
    STATIC_MAPPINGS,
    TE_ID_TO_BLOCK_META,
    get_block_mapping,
    get_mapping_for_te_id,
    is_bigreactors_block,
    is_bigreactors_te_id,
)


class TestBlockMappings:
    def test_yellorite_ore(self):
        m = get_block_mapping("BigReactors:YelloriteOre", 0)
        assert m is not None
        assert m.target_block_id == "biggerreactors:uranium_ore"

    def test_metal_block_yellorium(self):
        m = get_block_mapping("BigReactors:BRMetalBlock", 0)
        assert m.target_block_id == "biggerreactors:uranium_block"

    def test_metal_block_cyanite(self):
        m = get_block_mapping("BigReactors:BRMetalBlock", 1)
        assert m.target_block_id == "biggerreactors:cyanite_block"

    def test_metal_block_graphite(self):
        m = get_block_mapping("BigReactors:BRMetalBlock", 2)
        assert m.target_block_id == "biggerreactors:graphite_block"

    def test_metal_block_blutonium(self):
        m = get_block_mapping("BigReactors:BRMetalBlock", 3)
        assert m.target_block_id == "biggerreactors:blutonium_block"

    def test_metal_block_ludicrite(self):
        m = get_block_mapping("BigReactors:BRMetalBlock", 4)
        assert m.target_block_id == "biggerreactors:ludicrite_block"

    def test_reactor_part_casing(self):
        m = get_block_mapping("BigReactors:BRReactorPart", 0)
        assert m.target_block_id == "biggerreactors:reactor_casing"
        assert m.has_block_entity is True

    def test_reactor_part_controller(self):
        m = get_block_mapping("BigReactors:BRReactorPart", 1)
        assert m.target_block_id == "biggerreactors:reactor_terminal"

    def test_reactor_part_control_rod(self):
        m = get_block_mapping("BigReactors:BRReactorPart", 2)
        assert m.target_block_id == "biggerreactors:reactor_control_rod"

    def test_reactor_part_power_tap(self):
        m = get_block_mapping("BigReactors:BRReactorPart", 3)
        assert m.target_block_id == "biggerreactors:reactor_power_tap"

    def test_reactor_part_access_port(self):
        m = get_block_mapping("BigReactors:BRReactorPart", 4)
        assert m.target_block_id == "biggerreactors:reactor_access_port"
        assert m.nbt_converter == "multiblock_reactor_accessport"

    def test_reactor_part_coolant_port(self):
        m = get_block_mapping("BigReactors:BRReactorPart", 5)
        assert m.target_block_id == "biggerreactors:reactor_coolant_port"

    def test_reactor_part_rednet_port_fallback(self):
        m = get_block_mapping("BigReactors:BRReactorPart", 6)
        assert m.target_block_id == "biggerreactors:reactor_redstone_port"
        assert "RedNet" in m.notes

    def test_reactor_part_computer_port(self):
        m = get_block_mapping("BigReactors:BRReactorPart", 7)
        assert m.target_block_id == "biggerreactors:reactor_computer_port"

    def test_reactor_redstone_port(self):
        m = get_block_mapping("BigReactors:BRReactorRedstonePort", 0)
        assert m.target_block_id == "biggerreactors:reactor_redstone_port"

    def test_reactor_glass(self):
        m = get_block_mapping("BigReactors:BRMultiblockGlass", 0)
        assert m.target_block_id == "biggerreactors:reactor_glass"

    def test_turbine_glass(self):
        m = get_block_mapping("BigReactors:BRMultiblockGlass", 1)
        assert m.target_block_id == "biggerreactors:turbine_glass"

    def test_fuel_rod(self):
        m = get_block_mapping("BigReactors:YelloriumFuelRod", 0)
        assert m.target_block_id == "biggerreactors:reactor_fuel_rod"

    def test_turbine_part_housing(self):
        m = get_block_mapping("BigReactors:BRTurbinePart", 0)
        assert m.target_block_id == "biggerreactors:turbine_casing"

    def test_turbine_part_controller(self):
        m = get_block_mapping("BigReactors:BRTurbinePart", 1)
        assert m.target_block_id == "biggerreactors:turbine_terminal"

    def test_turbine_part_power_tap(self):
        m = get_block_mapping("BigReactors:BRTurbinePart", 2)
        assert m.target_block_id == "biggerreactors:turbine_power_tap"

    def test_turbine_part_fluid_port(self):
        m = get_block_mapping("BigReactors:BRTurbinePart", 3)
        assert m.target_block_id == "biggerreactors:turbine_fluid_port"

    def test_turbine_part_bearing(self):
        m = get_block_mapping("BigReactors:BRTurbinePart", 4)
        assert m.target_block_id == "biggerreactors:turbine_rotor_bearing"

    def test_turbine_part_computer_port(self):
        m = get_block_mapping("BigReactors:BRTurbinePart", 5)
        assert m.target_block_id == "biggerreactors:turbine_computer_port"

    def test_turbine_rotor_shaft(self):
        m = get_block_mapping("BigReactors:BRTurbineRotorPart", 0)
        assert m.target_block_id == "biggerreactors:turbine_rotor_shaft"

    def test_turbine_rotor_blade(self):
        m = get_block_mapping("BigReactors:BRTurbineRotorPart", 1)
        assert m.target_block_id == "biggerreactors:turbine_rotor_blade"

    def test_cyanite_reprocessor(self):
        m = get_block_mapping("BigReactors:BRDevice", 0)
        assert m.target_block_id == "biggerreactors:cyanite_reprocessor"
        assert m.nbt_converter == "cyanite_reprocessor"

    def test_creative_parts_removed(self):
        m0 = get_block_mapping("BigReactors:BRMultiblockCreativePart", 0)
        m1 = get_block_mapping("BigReactors:BRMultiblockCreativePart", 1)
        assert m0.target_block_id == "minecraft:air"
        assert m1.target_block_id == "minecraft:air"

    def test_fluid_yellorium(self):
        m = get_block_mapping("BigReactors:tile.bigreactors.yellorium.still", 0)
        assert m.target_block_id == "biggerreactors:liquid_uranium"


class TestTEMappings:
    def test_te_id_to_block_meta_all_known(self):
        for te_id, (block_id, meta) in TE_ID_TO_BLOCK_META.items():
            m = get_mapping_for_te_id(te_id, meta)
            assert m is not None, f"Brak mapowania dla TE {te_id}"

    def test_te_power_tap(self):
        m = get_mapping_for_te_id("BRReactorPowerTap", 0)
        assert m.target_block_id == "biggerreactors:reactor_power_tap"

    def test_te_fuel_rod(self):
        m = get_mapping_for_te_id("BRFuelRod", 0)
        assert m.target_block_id == "biggerreactors:reactor_fuel_rod"

    def test_te_turbine_rotor_part(self):
        m = get_mapping_for_te_id("BRTurbineRotorPart", 0)
        assert m.target_block_id == "biggerreactors:turbine_rotor_shaft"

    def test_te_cyanite_reprocessor(self):
        m = get_mapping_for_te_id("BRCyaniteReprocessor", 0)
        assert m.target_block_id == "biggerreactors:cyanite_reprocessor"


class TestHelpers:
    def test_is_bigreactors_block_positive(self):
        assert is_bigreactors_block("BigReactors:BRReactorPart") is True
        assert is_bigreactors_block("BRReactorPart") is True

    def test_is_bigreactors_block_negative(self):
        assert is_bigreactors_block("minecraft:stone") is False

    def test_is_bigreactors_te_id_positive(self):
        assert is_bigreactors_te_id("BRReactorPart") is True
        assert is_bigreactors_te_id("BRCyaniteReprocessor") is True

    def test_is_bigreactors_te_id_negative(self):
        assert is_bigreactors_te_id("Chest") is False

    def test_unknown_block_returns_none(self):
        assert get_block_mapping("BigReactors:UnknownBlock", 0) is None

    def test_normalize_block_id(self):
        from converters.bigreactors.mappings import _normalize_block_id
        assert _normalize_block_id("BRReactorPart") == "BigReactors:BRReactorPart"
        assert _normalize_block_id("BigReactors:BRReactorPart") == "BigReactors:BRReactorPart"
