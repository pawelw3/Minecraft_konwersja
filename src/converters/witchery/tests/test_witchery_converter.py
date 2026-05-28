"""Testy konwertera Witchery (uproszczona konwersja – tylko placeholdery).

UWAGA: Witchery nie ma portu na 1.18.2.  Konwerter generuje wyłącznie
placeholder eventy.  Testy weryfikują poprawność tych placeholderów
i zachowanie oryginalnego NBT – NIE weryfikują faktycznej konwersji danych.

Uruchamiać z katalogu projektu:
  python -m pytest src/converters/witchery/tests/test_witchery_converter.py -v
"""
import pytest

from converters.witchery.mappings import (
    WITCHERY_TE_IDS,
    TE_ID_TO_BLOCK_REGISTRY,
    TE_ID_TO_GROUP,
    GROUP_FUNCTIONAL,
    GROUP_SPECIAL,
    GROUP_DECORATIVE,
    GROUP_REDSTONE,
    GROUP_FLUID,
)
from converters.witchery.witchery_converter import WitcheryConverter
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
    return WitcheryConverter()


# ---------------------------------------------------------------------------
# Mappings – kompletność i spójność
# ---------------------------------------------------------------------------

class TestMappings:

    def test_functional_te_ids_present(self):
        for te_id in (
            "witchery:altar", "witchery:kettle", "witchery:cauldron",
            "witchery:spinningwheel", "witchery:witchesovenidle",
            "witchery:distilleryidle", "witchery:poppetshelf",
            "witchery:leechchest", "witchery:refillingchest",
            "witchery:silvervat", "witchery:brazier", "witchery:bloodcrucible",
        ):
            assert te_id in WITCHERY_TE_IDS, f"Brak {te_id!r} w WITCHERY_TE_IDS"

    def test_special_te_ids_present(self):
        for te_id in (
            "witchery:mirrorblock", "witchery:mirrorblock2",
            "witchery:dreamcatcher", "witchery:crystalball",
            "witchery:coffinblock", "witchery:decurseteleport",
            "witchery:decursedirected", "witchery:placeditem",
            "witchery:spiritportal",
        ):
            assert te_id in WITCHERY_TE_IDS, f"Brak {te_id!r} w WITCHERY_TE_IDS"

    def test_decorative_te_ids_present(self):
        for te_id in (
            "witchery:fumefunnel", "witchery:scarecrow", "witchery:trent",
            "witchery:witchsladder", "witchery:beartrap", "witchery:wolftrap",
            "witchery:candelabra", "witchery:chalice", "witchery:circle",
        ):
            assert te_id in WITCHERY_TE_IDS, f"Brak {te_id!r} w WITCHERY_TE_IDS"

    def test_cursed_redstone_te_ids_present(self):
        for te_id in (
            "witchery:clever", "witchery:cwoodendoor",
            "witchery:cwoodpressureplate", "witchery:cstonepressureplate",
            "witchery:csnowpressureplate", "witchery:cbuttonwood",
            "witchery:cbuttonstone",
        ):
            assert te_id in WITCHERY_TE_IDS, f"Brak {te_id!r} w WITCHERY_TE_IDS"

    def test_brew_fluid_te_ids_present(self):
        for te_id in ("witchery:brewgas", "witchery:brewliquid", "witchery:slurp"):
            assert te_id in WITCHERY_TE_IDS, f"Brak {te_id!r} w WITCHERY_TE_IDS"

    def test_all_te_ids_have_witchery_prefix(self):
        for te_id in WITCHERY_TE_IDS:
            assert te_id.startswith("witchery:"), (
                f"{te_id!r} nie ma prefiksu 'witchery:'"
            )

    def test_all_te_ids_have_block_registry_entry(self):
        missing = WITCHERY_TE_IDS - set(TE_ID_TO_BLOCK_REGISTRY)
        assert not missing, f"Brak wpisów w TE_ID_TO_BLOCK_REGISTRY: {missing}"

    def test_all_block_registry_values_have_witchery_prefix(self):
        for block_id in TE_ID_TO_BLOCK_REGISTRY.values():
            assert block_id.startswith("witchery:"), (
                f"Wartość {block_id!r} nie zaczyna się od 'witchery:'"
            )

    def test_all_te_ids_have_group(self):
        missing = WITCHERY_TE_IDS - set(TE_ID_TO_GROUP)
        assert not missing, f"Brak grupy w TE_ID_TO_GROUP: {missing}"

    def test_group_values_are_valid(self):
        valid = {GROUP_FUNCTIONAL, GROUP_SPECIAL, GROUP_DECORATIVE,
                 GROUP_REDSTONE, GROUP_FLUID}
        for te_id, group in TE_ID_TO_GROUP.items():
            assert group in valid, f"{te_id!r} ma nieznaną grupę {group!r}"

    def test_altar_is_functional(self):
        assert TE_ID_TO_GROUP["witchery:altar"] == GROUP_FUNCTIONAL

    def test_mirror_is_special(self):
        assert TE_ID_TO_GROUP["witchery:mirrorblock"] == GROUP_SPECIAL

    def test_candelabra_is_decorative(self):
        assert TE_ID_TO_GROUP["witchery:candelabra"] == GROUP_DECORATIVE

    def test_clever_is_redstone(self):
        assert TE_ID_TO_GROUP["witchery:clever"] == GROUP_REDSTONE

    def test_brewgas_is_fluid(self):
        assert TE_ID_TO_GROUP["witchery:brewgas"] == GROUP_FLUID

    def test_total_te_count_reasonable(self):
        # Musi być co najmniej 40 TE IDs (sanity check na kompletność)
        assert len(WITCHERY_TE_IDS) >= 40, (
            f"Za mało TE IDs: {len(WITCHERY_TE_IDS)} (oczekiwano >=40)"
        )


# ---------------------------------------------------------------------------
# Router – detekcja moda
# ---------------------------------------------------------------------------

class TestDetectMod:

    @pytest.mark.parametrize("te_id", [
        # Funkcjonalne
        "witchery:altar", "witchery:kettle", "witchery:cauldron",
        "witchery:spinningwheel", "witchery:witchesovenidle",
        "witchery:distilleryidle", "witchery:poppetshelf",
        # Specjalne
        "witchery:mirrorblock", "witchery:mirrorblock2",
        "witchery:dreamcatcher", "witchery:coffinblock",
        "witchery:decurseteleport", "witchery:placeditem",
        # Dekoracyjne
        "witchery:scarecrow", "witchery:trent", "witchery:witchsladder",
        "witchery:candelabra", "witchery:beartrap", "witchery:wolftrap",
        # Redstone
        "witchery:clever", "witchery:cwoodendoor",
        # Fluidy
        "witchery:brewgas", "witchery:slurp",
    ])
    def test_known_witchery_te_ids_detected(self, te_id):
        assert detect_mod(te_id) == "witchery", (
            f"detect_mod({te_id!r}) powinno zwrócić 'witchery'"
        )

    def test_unknown_witchery_prefixed_id_detected(self):
        # Fallback: nieznane TE z prefiksem witchery: też powinny być wykryte
        assert detect_mod("witchery:someunknownblock") == "witchery"

    def test_non_witchery_not_detected(self):
        assert detect_mod("reliquaryAltar") != "witchery"
        assert detect_mod("witchery:altar"[:7]) != "witchery"  # "witche"


# ---------------------------------------------------------------------------
# Konwerter – format wyjściowy placeholder
# ---------------------------------------------------------------------------

class TestPlaceholderOutput:

    def test_returns_list_with_one_event(self, conv):
        events = conv.convert_tile_entity("witchery:altar", {})
        assert isinstance(events, list)
        assert len(events) == 1

    def test_event_is_placeholder(self, conv):
        events = conv.convert_tile_entity("witchery:kettle", {})
        assert is_placeholder_event(events[0])

    def test_op_is_set_block_entity(self, conv):
        events = conv.convert_tile_entity("witchery:cauldron", {})
        assert events[0]["op"] == "set_block_entity"

    def test_position_set_correctly(self, conv):
        events = conv.convert_tile_entity("witchery:spinningwheel", {}, position=(10, 64, -5))
        assert events[0]["pos"] == [10, 64, -5]

    def test_source_mod_in_nbt(self, conv):
        events = conv.convert_tile_entity("witchery:mirrorblock", {})
        assert events[0]["nbt"]["source_mod"] == "witchery"

    def test_source_te_id_in_nbt(self, conv):
        events = conv.convert_tile_entity("witchery:poppetshelf", {})
        assert events[0]["nbt"]["source_te_id"] == "witchery:poppetshelf"

    def test_conversion_reason_is_no_118_equivalent(self, conv):
        events = conv.convert_tile_entity("witchery:altar", {})
        assert events[0]["nbt"]["conversion_reason"] == "no_118_equivalent"

    def test_source_block_id_from_registry(self, conv):
        events = conv.convert_tile_entity("witchery:kettle", {})
        assert events[0]["nbt"]["source_block_id"] == "witchery:kettle"

    def test_conversion_stage_is_group(self, conv):
        events = conv.convert_tile_entity("witchery:altar", {})
        assert events[0]["nbt"]["conversion_stage"] == GROUP_FUNCTIONAL

    def test_conversion_stage_special_for_mirror(self, conv):
        events = conv.convert_tile_entity("witchery:mirrorblock", {})
        assert events[0]["nbt"]["conversion_stage"] == GROUP_SPECIAL

    def test_conversion_stage_decorative_for_candelabra(self, conv):
        events = conv.convert_tile_entity("witchery:candelabra", {})
        assert events[0]["nbt"]["conversion_stage"] == GROUP_DECORATIVE

    def test_conversion_stage_redstone_for_clever(self, conv):
        events = conv.convert_tile_entity("witchery:clever", {})
        assert events[0]["nbt"]["conversion_stage"] == GROUP_REDSTONE

    def test_conversion_stage_fluid_for_brewgas(self, conv):
        events = conv.convert_tile_entity("witchery:brewgas", {})
        assert events[0]["nbt"]["conversion_stage"] == GROUP_FLUID


# ---------------------------------------------------------------------------
# Konwerter – zachowanie NBT (najważniejszy wymóg)
# ---------------------------------------------------------------------------

class TestNBTPreservation:

    def test_altar_nbt_preserved(self, conv):
        nbt = {
            "Power": 1500.0,
            "MaxPower": 2000.0,
            "PowerScale": 2,
            "RechargeScale": 1,
            "RangeScale": 3,
        }
        events = conv.convert_tile_entity("witchery:altar", nbt, position=(0, 64, 0))
        original = events[0]["nbt"]["original_nbt"]
        assert original["Power"] == 1500.0
        assert original["MaxPower"] == 2000.0
        assert original["PowerScale"] == 2

    def test_kettle_inventory_preserved_and_inventory_placeholder(self, conv):
        nbt = {
            "Ruined": False,
            "LiquidColor": 0xFF0000,
            "Items": [
                {"Slot": 0, "id": "minecraft:sugar", "Count": 3, "Damage": 0},
                {"Slot": 1, "id": "witchery:ingredient", "Count": 1, "Damage": 5},
            ],
        }
        events = conv.convert_tile_entity("witchery:kettle", nbt)
        assert events[0]["block"] == INVENTORY_PLACEHOLDER_BLOCK_ID
        original = events[0]["nbt"]["original_nbt"]
        assert original["Ruined"] is False
        assert original["LiquidColor"] == 0xFF0000
        assert len(original["Items"]) == 2

    def test_spinning_wheel_with_items(self, conv):
        nbt = {
            "CookTime": 120,
            "PowerLevel": 3,
            "Items": [
                {"Slot": 0, "id": "witchery:wool", "Count": 1, "Damage": 0},
            ],
        }
        events = conv.convert_tile_entity("witchery:spinningwheel", nbt)
        assert events[0]["block"] == INVENTORY_PLACEHOLDER_BLOCK_ID
        assert events[0]["nbt"]["original_nbt"]["CookTime"] == 120

    def test_oven_nbt_preserved(self, conv):
        nbt = {
            "BurnTime": 200,
            "CookTime": 50,
            "CurrentItemBurnTime": 200,
            "Items": [
                {"Slot": 0, "id": "minecraft:coal", "Count": 1, "Damage": 0},
            ],
        }
        events = conv.convert_tile_entity("witchery:witchesovenidle", nbt)
        assert events[0]["block"] == INVENTORY_PLACEHOLDER_BLOCK_ID
        original = events[0]["nbt"]["original_nbt"]
        assert original["BurnTime"] == 200
        assert original["CookTime"] == 50

    def test_mirror_nbt_preserved(self, conv):
        nbt = {
            "owner": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Mirror of Pawel",
            "trapped": False,
        }
        events = conv.convert_tile_entity("witchery:mirrorblock", nbt)
        original = events[0]["nbt"]["original_nbt"]
        assert original["owner"] == "550e8400-e29b-41d4-a716-446655440000"
        assert original["name"] == "Mirror of Pawel"
        assert original["trapped"] is False

    def test_placed_item_nbt_preserved(self, conv):
        nbt = {
            "Item": {
                "id": "witchery:ingredient",
                "Count": 1,
                "Damage": 15,
            }
        }
        events = conv.convert_tile_entity("witchery:placeditem", nbt)
        original = events[0]["nbt"]["original_nbt"]
        assert original["Item"]["id"] == "witchery:ingredient"
        assert original["Item"]["Damage"] == 15

    def test_blood_crucible_nbt_preserved(self, conv):
        nbt = {"bloodLevel": 12}
        events = conv.convert_tile_entity("witchery:bloodcrucible", nbt)
        assert events[0]["nbt"]["original_nbt"]["bloodLevel"] == 12

    def test_empty_nbt_uses_plain_placeholder(self, conv):
        events = conv.convert_tile_entity("witchery:candelabra", {})
        assert events[0]["block"] == PLACEHOLDER_BLOCK_ID

    def test_empty_nbt_original_nbt_is_empty_dict(self, conv):
        events = conv.convert_tile_entity("witchery:circle", {})
        assert events[0]["nbt"]["original_nbt"] == {}

    def test_poppet_shelf_contents_preserved(self, conv):
        nbt = {
            "contents": [
                {"id": "witchery:poppet", "Count": 1, "Damage": 0},
                {"id": "witchery:poppet", "Count": 1, "Damage": 1},
            ]
        }
        events = conv.convert_tile_entity("witchery:poppetshelf", nbt)
        original = events[0]["nbt"]["original_nbt"]
        assert len(original["contents"]) == 2

    def test_cauldron_brew_data_preserved(self, conv):
        nbt = {
            "boiling": True,
            "power": 500,
            "brewData": {"effect": "fire_resistance", "duration": 3600},
        }
        events = conv.convert_tile_entity("witchery:cauldron", nbt)
        original = events[0]["nbt"]["original_nbt"]
        assert original["boiling"] is True
        assert original["power"] == 500
        assert original["brewData"]["effect"] == "fire_resistance"

    def test_unknown_witchery_te_id_handled(self, conv):
        events = conv.convert_tile_entity("witchery:futureblock", {"someData": 42})
        assert len(events) == 1
        assert is_placeholder_event(events[0])
        assert events[0]["nbt"]["original_nbt"]["someData"] == 42


# ---------------------------------------------------------------------------
# is_known_te
# ---------------------------------------------------------------------------

class TestIsKnownTe:

    def test_known_functional(self, conv):
        assert conv.is_known_te("witchery:altar")
        assert conv.is_known_te("witchery:kettle")

    def test_known_special(self, conv):
        assert conv.is_known_te("witchery:mirrorblock")
        assert conv.is_known_te("witchery:dreamcatcher")

    def test_known_decorative(self, conv):
        assert conv.is_known_te("witchery:candelabra")
        assert conv.is_known_te("witchery:beartrap")

    def test_unknown_witchery_prefix_returns_true(self, conv):
        # Fallback: nieznane TE z prefiksem witchery: też są "znane"
        assert conv.is_known_te("witchery:someunknownfutureblock")

    def test_other_mod_returns_false(self, conv):
        assert not conv.is_known_te("reliquaryAltar")
        assert not conv.is_known_te("")
        assert not conv.is_known_te("minecraft:chest")
