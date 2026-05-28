"""Testy konwertera Open Modular Turrets.

Uruchamiać z katalogu projektu:
  python -m pytest src/converters/openmodularturrets/tests/test_omt_converter.py -v
"""
import pytest

from converters.openmodularturrets.mappings import OMT_TE_IDS, TE_ID_TO_BLOCK_REGISTRY
from converters.openmodularturrets.omt_converter import OpenModularTurretsConverter
from converters.common.placeholders import (
    PLACEHOLDER_BLOCK_ID,
    INVENTORY_PLACEHOLDER_BLOCK_ID,
    is_placeholder_event,
)
from converters.router import detect_mod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def conv():
    return OpenModularTurretsConverter()


# ---------------------------------------------------------------------------
# Mappings
# ---------------------------------------------------------------------------

class TestMappings:

    def test_all_bases_in_te_ids(self):
        for te_id in ("turretWoodBase", "turretBaseOne", "turretBaseTwo",
                      "turretBaseThree", "turretBaseFour"):
            assert te_id in OMT_TE_IDS

    def test_all_heads_in_te_ids(self):
        for te_id in ("machineGunTurret", "railGunTurret", "laserTurret",
                      "rocketTurret", "grenadeTurret", "incendiaryTurret",
                      "relativisticTurret", "teleporterTurret",
                      "potatoCannonTurret", "disposableItemTurret"):
            assert te_id in OMT_TE_IDS

    def test_all_expanders_in_te_ids(self):
        for suffix in ("TierOne", "TierTwo", "TierThree", "TierFour", "TierFive"):
            assert f"expanderPowerTier{suffix[4:]}" in OMT_TE_IDS or \
                   f"expanderPower{suffix}" in OMT_TE_IDS
        for te_id in ("expanderInvTierOne", "expanderInvTierFive",
                      "expanderPowerTierOne", "expanderPowerTierFive"):
            assert te_id in OMT_TE_IDS

    def test_lever_in_te_ids(self):
        assert "leverTileEntity" in OMT_TE_IDS

    def test_lowercase_variant_in_te_ids(self):
        assert "turretbase" in OMT_TE_IDS

    def test_block_registry_covers_all_te_ids(self):
        missing = OMT_TE_IDS - {"turretbase"} - set(TE_ID_TO_BLOCK_REGISTRY)
        assert not missing, f"Missing block registry entries: {missing}"

    def test_block_registry_values_have_namespace(self):
        for block_id in TE_ID_TO_BLOCK_REGISTRY.values():
            assert block_id.startswith("openmodularturrets:"), (
                f"{block_id} should start with openmodularturrets:"
            )


# ---------------------------------------------------------------------------
# Router detection
# ---------------------------------------------------------------------------

class TestDetectMod:

    @pytest.mark.parametrize("te_id", [
        "turretWoodBase", "turretBaseOne", "turretBaseTwo",
        "turretBaseThree", "turretBaseFour", "turretbase",
        "machineGunTurret", "railGunTurret", "laserTurret",
        "rocketTurret", "grenadeTurret", "incendiaryTurret",
        "relativisticTurret", "teleporterTurret",
        "potatoCannonTurret", "disposableItemTurret",
        "expanderPowerTierOne", "expanderPowerTierFive",
        "expanderInvTierOne", "expanderInvTierFive",
        "leverTileEntity",
    ])
    def test_all_omt_te_ids_detected(self, te_id):
        assert detect_mod(te_id) == "openmodularturrets", (
            f"detect_mod({te_id!r}) should return 'openmodularturrets'"
        )


# ---------------------------------------------------------------------------
# Converter – placeholder output format
# ---------------------------------------------------------------------------

class TestPlaceholderOutput:

    def test_returns_list_with_one_event(self, conv):
        events = conv.convert_tile_entity("turretWoodBase", {})
        assert isinstance(events, list)
        assert len(events) == 1

    def test_event_is_placeholder(self, conv):
        events = conv.convert_tile_entity("turretBaseOne", {})
        assert is_placeholder_event(events[0])

    def test_op_is_set_block_entity(self, conv):
        events = conv.convert_tile_entity("machineGunTurret", {})
        assert events[0]["op"] == "set_block_entity"

    def test_position_set_correctly(self, conv):
        events = conv.convert_tile_entity("laserTurret", {}, position=(10, 64, -5))
        assert events[0]["pos"] == [10, 64, -5]

    def test_source_mod_in_nbt(self, conv):
        events = conv.convert_tile_entity("railGunTurret", {})
        assert events[0]["nbt"]["source_mod"] == "openmodularturrets"

    def test_source_te_id_in_nbt(self, conv):
        events = conv.convert_tile_entity("grenadeTurret", {})
        assert events[0]["nbt"]["source_te_id"] == "grenadeTurret"

    def test_conversion_reason(self, conv):
        events = conv.convert_tile_entity("rocketTurret", {})
        assert events[0]["nbt"]["conversion_reason"] == "no_118_equivalent"

    def test_source_block_id_from_registry(self, conv):
        events = conv.convert_tile_entity("turretBaseTwo", {})
        assert events[0]["nbt"]["source_block_id"] == "openmodularturrets:baseTierTwoBlock"


# ---------------------------------------------------------------------------
# Converter – NBT preservation
# ---------------------------------------------------------------------------

class TestNBTPreservation:

    def test_turretbase_nbt_preserved(self, conv):
        nbt = {
            "owner": "550e8400-e29b-41d4-a716-446655440000",
            "ownerName": "Player1",
            "energyStored": 50000,
            "maxStorage": 100000,
            "attacksMobs": True,
            "attacksPlayers": False,
            "active": True,
            "trustedPlayers": [
                {"name": "Player2", "UUID": "abc123", "admin": False,
                 "canOpenGUI": True, "canChangeTargeting": False}
            ],
            "Inventory": [
                {"Slot": 0, "id": "openmodularturrets:turretUpgrade", "Count": 1, "Damage": 0}
            ],
        }
        events = conv.convert_tile_entity("turretBaseOne", nbt, position=(0, 64, 0))
        original = events[0]["nbt"]["original_nbt"]
        assert original["owner"] == nbt["owner"]
        assert original["ownerName"] == nbt["ownerName"]
        assert original["energyStored"] == 50000
        assert original["attacksMobs"] is True
        assert original["active"] is True
        assert len(original["trustedPlayers"]) == 1
        assert len(original["Inventory"]) == 1

    def test_expander_inv_nbt_preserved(self, conv):
        nbt = {
            "Inventory": [
                {"Slot": i, "id": f"openmodularturrets:ammo{i}", "Count": 64, "Damage": 0}
                for i in range(9)
            ]
        }
        events = conv.convert_tile_entity("expanderInvTierThree", nbt)
        original = events[0]["nbt"]["original_nbt"]
        assert len(original["Inventory"]) == 9

    def test_expander_power_empty_nbt(self, conv):
        events = conv.convert_tile_entity("expanderPowerTierFive", {})
        assert events[0]["nbt"]["original_nbt"] == {}

    def test_turrethead_nbt_preserved(self, conv):
        nbt = {"rotationXY": 45.0, "rotationXZ": 90.0, "shouldConceal": False}
        events = conv.convert_tile_entity("machineGunTurret", nbt)
        original = events[0]["nbt"]["original_nbt"]
        assert original["rotationXY"] == 45.0
        assert original["shouldConceal"] is False

    def test_inventory_triggers_inventory_placeholder(self, conv):
        nbt = {
            "Inventory": [
                {"Slot": 0, "id": "minecraft:iron_ingot", "Count": 32, "Damage": 0}
            ]
        }
        events = conv.convert_tile_entity("expanderInvTierOne", nbt)
        assert events[0]["block"] == INVENTORY_PLACEHOLDER_BLOCK_ID

    def test_no_inventory_uses_plain_placeholder(self, conv):
        events = conv.convert_tile_entity("expanderPowerTierOne", {})
        assert events[0]["block"] == PLACEHOLDER_BLOCK_ID


# ---------------------------------------------------------------------------
# is_known_te
# ---------------------------------------------------------------------------

class TestIsKnownTe:

    def test_known_base(self, conv):
        assert conv.is_known_te("turretBaseOne")

    def test_known_head(self, conv):
        assert conv.is_known_te("railGunTurret")

    def test_known_expander(self, conv):
        assert conv.is_known_te("expanderInvTierTwo")

    def test_unknown_returns_false(self, conv):
        assert not conv.is_known_te("someOtherMod:thing")
        assert not conv.is_known_te("")
