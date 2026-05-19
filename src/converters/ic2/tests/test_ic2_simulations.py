"""Testy jednostkowe symulacji konwersji IC2.

Zakres:
- Konwersja maszyn standardowych (progress, energy, facing, inventory)
- Konwersja storage (BatBox/MFE/MFSU, energy, redstone)
- Konwersja kabli (cableType, foamed, color)
- Teleporter (współrzędne celu)
- Reaktor (legacy data)
- Reguła EU → FE (1 EU = 4 FE)
"""

from __future__ import annotations

import pytest

from ..simulations.machine_simulation import (
    EU_TO_FE,
    convert_energy_eu_to_fe,
    convert_facing,
    extract_inventory,
    simulate_reactor_conversion,
    simulate_standard_machine_conversion,
    simulate_teleporter_conversion,
)
from ..simulations.energy_storage_simulation import simulate_energy_storage_conversion
from ..simulations.cable_simulation import simulate_cable_conversion


class TestEnergyConversion:
    """Testy reguły EU → FE."""

    def test_basic_conversion(self):
        assert convert_energy_eu_to_fe(100.0) == 400
        assert convert_energy_eu_to_fe(0.0) == 0
        assert convert_energy_eu_to_fe(1.0) == 4

    def test_fractional_conversion_rounds_down(self):
        assert convert_energy_eu_to_fe(1.1) == 4  # 4.4 → 4
        assert convert_energy_eu_to_fe(1.9) == 7  # 7.6 → 7

    def test_negative_is_clamped(self):
        # W razie błędnych danych upewniamy się że nie ma ujemnej energii
        assert convert_energy_eu_to_fe(-10.0) == 0


class TestFacingConversion:
    """Testy mapowania facing IC2 → 1.18.2."""

    def test_all_facings(self):
        assert convert_facing(0) == "down"
        assert convert_facing(1) == "up"
        assert convert_facing(2) == "north"
        assert convert_facing(3) == "south"
        assert convert_facing(4) == "west"
        assert convert_facing(5) == "east"

    def test_unknown_facing_defaults_north(self):
        assert convert_facing(99) == "north"


class TestInventoryExtraction:
    """Testy wyciągania inventory z różnych formatów NBT."""

    def test_invslots_format(self):
        nbt = {
            "InvSlots": {
                "input": {
                    "0": {"id": "IC2:itemDustIron", "Count": 2, "tag": {}},
                    "1": {"id": "IC2:itemDustGold", "Count": 1, "tag": {}},
                }
            }
        }
        items = extract_inventory(nbt)
        assert len(items) == 2
        assert items[0]["id"] == "IC2:itemDustIron"
        assert items[0]["Count"] == 2

    def test_legacy_items_format(self):
        nbt = {
            "Items": [
                {"Slot": 0, "id": "minecraft:iron_ore", "Count": 5, "tag": {}},
                {"Slot": 1, "id": "minecraft:gold_ore", "Count": 3},
            ]
        }
        items = extract_inventory(nbt)
        assert len(items) == 2
        assert items[1]["id"] == "minecraft:gold_ore"

    def test_empty_inventory(self):
        assert extract_inventory({}) == []
        assert extract_inventory({"InvSlots": {}}) == []


class TestStandardMachineConversion:
    """Testy konwersji maszyn standardowych (Macerator, Furnace, etc.)."""

    def test_macerator_to_crusher(self):
        nbt_1710 = {
            "facing": 3,  # south
            "active": True,
            "energy": 512.0,  # EU
            "progress": 200,
            "InvSlots": {
                "input": {"0": {"id": "minecraft:iron_ore", "Count": 1}},
                "output": {"0": {"id": "IC2:itemDustIron", "Count": 2}},
            },
        }
        result = simulate_standard_machine_conversion(
            nbt_1710, target_block_id="mekanism:crusher"
        )
        
        # Facing
        assert result["blockstate_props"]["facing"] == "south"
        # Energy: 512 EU * 4 = 2048 FE
        assert result["nbt_1182"]["energyContainer"]["stored"] == 2048
        # Progress
        assert result["nbt_1182"]["operatingTicks"] == 200
        # Inventory
        assert len(result["nbt_1182"]["Items"]) == 2
        # Brak błędów
        assert len(result["errors"]) == 0

    def test_furnace_to_smelter_thermal(self):
        nbt_1710 = {
            "facing": 4,  # west
            "active": True,
            "energy": 1000.0,
            "progress": 100,
        }
        result = simulate_standard_machine_conversion(
            nbt_1710, target_block_id="thermal:machine_smelter"
        )
        
        assert result["blockstate_props"]["active"] == "true"
        assert result["blockstate_props"]["facing"] == "west"
        assert result["nbt_1182"]["Process"] == 50  # 100/400 * 200
        assert result["nbt_1182"]["ProcessMax"] == 200

    def test_blast_furnace_vanilla(self):
        nbt_1710 = {
            "facing": 2,
            "active": True,
            "energy": 0.0,
        }
        result = simulate_standard_machine_conversion(
            nbt_1710, target_block_id="minecraft:blast_furnace"
        )
        
        assert result["blockstate_props"]["lit"] == "true"
        assert result["blockstate_props"]["facing"] == "north"

    def test_progress_without_items_warning(self):
        nbt_1710 = {
            "facing": 2,
            "active": True,
            "energy": 100.0,
            "progress": 50,
        }
        result = simulate_standard_machine_conversion(
            nbt_1710, target_block_id="mekanism:crusher"
        )
        assert any("PROGRESS-NO-ITEMS" in w for w in result["warnings"])


class TestEnergyStorageConversion:
    """Testy konwersji BatBox/MFE/MFSU."""

    def test_batbox_to_basic_cube(self):
        nbt_1710 = {
            "facing": 5,  # east
            "energy": 10000.0,  # EU (1/4 pojemności BatBox)
            "redstoneMode": 1,
        }
        result = simulate_energy_storage_conversion(
            nbt_1710, target_block_id="mekanism:basic_energy_cube"
        )
        
        assert result["blockstate_props"]["facing"] == "east"
        assert result["nbt_1182"]["energyContainer"]["stored"] == 40000
        assert result["nbt_1182"]["redstoneControl"] == 1

    def test_mfsu_to_ultimate_cube_overflow(self):
        nbt_1710 = {
            "facing": 2,
            "energy": 40_000_000.0,  # pełny MFSU
        }
        result = simulate_energy_storage_conversion(
            nbt_1710, target_block_id="mekanism:ultimate_energy_cube"
        )
        
        # 40M EU * 4 = 160M FE — przekracza pojemność ultimate (102.4M)
        # Ale w IC2 MFSU ma 40M EU, więc po konwersji 160M FE
        # Ultimate ma 102.4M, więc powinien być clamped
        stored = result["nbt_1182"]["energyContainer"]["stored"]
        assert stored <= 102_400_000
        assert any("OVERFLOW" in w for w in result["warnings"])

    def test_chargepad_tier(self):
        nbt_1710 = {"facing": 2, "energy": 5000.0}
        result = simulate_energy_storage_conversion(
            nbt_1710,
            target_block_id="mekanism:chargepad",
            source_block_id="IC2:blockChargepad",
            source_metadata=2,  # MFE tier
        )
        assert result["nbt_1182"]["tier"] == "elite"


class TestCableConversion:
    """Testy konwersji kabli."""

    def test_glass_fiber_no_warnings(self):
        nbt_1710 = {"cableType": 9, "color": 0, "foamed": 0}
        result = simulate_cable_conversion(nbt_1710, "mekanism:ultimate_universal_cable")
        assert len(result["warnings"]) == 0

    def test_colored_cable_warning(self):
        nbt_1710 = {"cableType": 0, "color": 5, "foamed": 0}
        result = simulate_cable_conversion(nbt_1710, "mekanism:basic_universal_cable")
        assert any("CABLE-COLOR" in w for w in result["warnings"])

    def test_foamed_cable_warning(self):
        nbt_1710 = {"cableType": 0, "color": 0, "foamed": 2, "foamColor": 7}
        result = simulate_cable_conversion(nbt_1710, "mekanism:basic_universal_cable")
        assert any("CABLE-FOAMED" in w for w in result["warnings"])


class TestTeleporterConversion:
    """Testy teleportera."""

    def test_teleporter_with_target(self):
        nbt_1710 = {
            "facing": 2,
            "energy": 100000.0,
            "targetSet": True,
            "targetX": 100,
            "targetY": 64,
            "targetZ": -200,
        }
        result = simulate_teleporter_conversion(nbt_1710)
        assert result["nbt_1182"]["energyContainer"]["stored"] == 400_000
        assert result["nbt_1182"]["legacy_target"] == [100, 64, -200]
        assert any("TELEPORTER-TARGET" in w for w in result["warnings"])


class TestReactorConversion:
    """Testy reaktora jądrowego."""

    def test_reactor_legacy_data(self):
        nbt_1710 = {
            "heat": 2500,
            "energy": 500000.0,
            "Items": [
                {"Slot": 0, "id": "IC2:reactorUraniumSimple", "Count": 1},
                {"Slot": 1, "id": "IC2:reactorPlating", "Count": 1},
            ],
        }
        result = simulate_reactor_conversion(nbt_1710)
        assert result["nbt_1182"]["legacy_ic2_heat"] == 2500
        assert result["nbt_1182"]["legacy_ic2_energy"] == 2_000_000
        assert len(result["nbt_1182"]["legacy_ic2_items"]) == 2
        assert any("REACTOR-NO-1" in w for w in result["warnings"])


class TestIndrebNBTShape:
    """Testy weryfikujące zgodność NBT z dekompilacją indreb 1.18.2."""

    def test_indreb_machine_nbt(self):
        nbt_1710 = {
            "facing": 3,
            "active": True,
            "energy": 512.0,
            "progress": 200,
            "InvSlots": {
                "input": {"0": {"id": "minecraft:iron_ore", "Count": 1}},
                "output": {"0": {"id": "IC2:itemDustIron", "Count": 2}},
            },
        }
        result = simulate_standard_machine_conversion(nbt_1710, "indreb:crusher")
        nbt = result["nbt_1182"]
        assert nbt["energy"] == 2048
        assert nbt["active"] is True
        assert nbt["progress"]["progress"] == 200.0
        assert nbt["progress"]["progressMax"] == 400.0
        assert nbt["inventory"]["Size"] == 2
        assert len(nbt["inventory"]["Items"]) == 2
        # Sloty powinny być unikalne
        slots = [it["Slot"] for it in nbt["inventory"]["Items"]]
        assert slots == [0, 1]

    def test_indreb_generator_nbt(self):
        nbt_1710 = {"facing": 2, "energy": 100.0, "progress": 50}
        result = simulate_standard_machine_conversion(nbt_1710, "indreb:generator")
        nbt = result["nbt_1182"]
        assert "energy" in nbt
        assert "progress" in nbt
        assert "active" in nbt

    def test_indreb_battery_box_nbt(self):
        nbt_1710 = {"facing": 2, "energy": 1000.0}
        result = simulate_energy_storage_conversion(nbt_1710, "indreb:battery_box")
        assert result["nbt_1182"]["energy"] == 4000
        assert "energyContainer" not in result["nbt_1182"]

    def test_indreb_cable_no_nbt(self):
        nbt_1710 = {"cableType": 0, "color": 0, "foamed": 0}
        result = simulate_cable_conversion(nbt_1710, "indreb:copper_cable_insulated")
        assert result["nbt_1182"] == {} or result["nbt_1182"] is None


class TestFTBICNBTShape:
    """Testy weryfikujące zgodność NBT z dekompilacją ftbic 1.18.2."""

    def test_ftbic_machine_nbt(self):
        nbt_1710 = {
            "facing": 3,
            "active": True,
            "energy": 512.0,
            "progress": 200,
            "InvSlots": {
                "input": {"0": {"id": "minecraft:iron_ore", "Count": 1}},
                "output": {"0": {"id": "IC2:itemDustIron", "Count": 2}},
            },
        }
        result = simulate_standard_machine_conversion(nbt_1710, "ftbic:macerator")
        nbt = result["nbt_1182"]
        assert "Energy" in nbt  # double, capital E
        assert nbt["Energy"] == 2048.0
        assert "Progress" in nbt  # double
        assert "MaxProgress" in nbt  # double
        assert "Inventory" in nbt  # ListTag
        assert "active" not in nbt  # ftbic uses blockstate, not NBT

    def test_ftbic_pump_nbt(self):
        nbt_1710 = {"facing": 2, "energy": 100.0}
        result = simulate_standard_machine_conversion(nbt_1710, "ftbic:pump")
        assert result["nbt_1182"]["Energy"] == 400.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
