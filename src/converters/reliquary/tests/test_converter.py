"""
Testy konwertera Reliquary – Zadanie 3

Uruchamiać z katalogu projektu:
  python -m pytest src/converters/reliquary/tests/test_converter.py -v
"""

import pytest
from converters.reliquary.converter import ReliquaryConverter
from converters.reliquary.mappings import TE_ID_TO_BLOCK, RELIQUARY_TE_IDS


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def conv():
    return ReliquaryConverter()


# =============================================================================
# Mappings
# =============================================================================

class TestMappings:

    def test_all_te_ids_present(self):
        assert "reliquaryAltar" in TE_ID_TO_BLOCK
        assert "reliquaryCauldron" in TE_ID_TO_BLOCK
        assert "apothecaryMortar" in TE_ID_TO_BLOCK

    def test_block_ids_have_reliquary_namespace(self):
        for block_id in TE_ID_TO_BLOCK.values():
            assert block_id.startswith("reliquary:"), f"{block_id} should have reliquary: prefix"

    def test_reliquary_te_ids_frozenset(self):
        for te_id in ("reliquaryAltar", "reliquaryCauldron", "apothecaryMortar"):
            assert te_id in RELIQUARY_TE_IDS


# =============================================================================
# Alkahestry Altar
# =============================================================================

class TestAltarConverter:

    def test_altar_block_id(self, conv):
        result = conv.convert_tile_entity("reliquaryAltar", {})
        assert result.success
        assert result.block_id_1182 == "reliquary:alkahestry_altar"

    def test_altar_empty_nbt(self, conv):
        result = conv.convert_tile_entity("reliquaryAltar", {})
        assert result.success
        assert result.nbt_1182 is None or result.nbt_1182 == {}

    def test_altar_cycle_time_preserved(self, conv):
        nbt = {"cycleTime": 500, "redstoneCount": 3, "isActive": True}
        result = conv.convert_tile_entity("reliquaryAltar", nbt)
        assert result.success
        assert result.nbt_1182["cycleTime"] == 500
        assert result.nbt_1182["redstoneCount"] == 3
        assert result.nbt_1182["isActive"] is True

    def test_altar_active_state(self, conv):
        nbt = {"cycleTime": 2400, "redstoneCount": 5, "isActive": False}
        result = conv.convert_tile_entity("reliquaryAltar", nbt)
        assert result.nbt_1182["isActive"] is False
        assert result.nbt_1182["cycleTime"] == 2400

    def test_altar_no_extra_keys(self, conv):
        nbt = {"cycleTime": 100, "redstoneCount": 1, "isActive": True, "someExtraKey": "ignored"}
        result = conv.convert_tile_entity("reliquaryAltar", nbt)
        assert "someExtraKey" not in result.nbt_1182

    def test_altar_no_warnings(self, conv):
        nbt = {"cycleTime": 100, "redstoneCount": 1, "isActive": True}
        result = conv.convert_tile_entity("reliquaryAltar", nbt)
        assert result.warnings == []


# =============================================================================
# Apothecary Cauldron
# =============================================================================

class TestCauldronConverter:

    def test_cauldron_block_id(self, conv):
        result = conv.convert_tile_entity(
            "reliquaryCauldron",
            {"hasGlowstone": False, "hasNetherwart": False, "hasGunpowder": False,
             "redstoneCount": 0, "cookTime": 0, "potionEssence": {}},
            metadata=3,
        )
        assert result.success
        assert result.block_id_1182 == "reliquary:apothecary_cauldron"

    def test_cauldron_liquid_level_from_meta(self, conv):
        result = conv.convert_tile_entity(
            "reliquaryCauldron",
            {"hasGlowstone": False, "hasNetherwart": False, "hasGunpowder": False,
             "redstoneCount": 0, "cookTime": 0, "potionEssence": {}},
            metadata=2,
        )
        assert result.nbt_1182["liquidLevel"] == 2

    def test_cauldron_glowstone_bool_to_int(self, conv):
        nbt = {"hasGlowstone": True, "hasNetherwart": True, "hasGunpowder": False,
               "redstoneCount": 0, "cookTime": 0, "potionEssence": {}}
        result = conv.convert_tile_entity("reliquaryCauldron", nbt, metadata=3)
        assert result.nbt_1182["glowstoneCount"] == 1

    def test_cauldron_glowstone_false_gives_zero(self, conv):
        nbt = {"hasGlowstone": False, "hasNetherwart": False, "hasGunpowder": False,
               "redstoneCount": 0, "cookTime": 0, "potionEssence": {}}
        result = conv.convert_tile_entity("reliquaryCauldron", nbt, metadata=3)
        assert result.nbt_1182["glowstoneCount"] == 0

    def test_cauldron_dragon_breath_always_false(self, conv):
        nbt = {"hasGlowstone": True, "hasNetherwart": True, "hasGunpowder": False,
               "redstoneCount": 0, "cookTime": 0, "potionEssence": {}}
        result = conv.convert_tile_entity("reliquaryCauldron", nbt, metadata=3)
        assert result.nbt_1182["hasDragonBreath"] is False

    def test_cauldron_with_potion_essence(self, conv):
        nbt = {
            "hasGlowstone": True, "hasNetherwart": True, "hasGunpowder": False,
            "redstoneCount": 2, "cookTime": 80,
            "potionEssence": {
                "effects": [
                    {"id": 1, "duration": 900, "potency": 0},
                    {"id": 10, "duration": 300, "potency": 0},
                ]
            },
        }
        result = conv.convert_tile_entity("reliquaryCauldron", nbt, metadata=3)
        assert result.success
        assert "effects" in result.nbt_1182
        assert "custom_effects" in result.nbt_1182["effects"]
        assert len(result.nbt_1182["effects"]["custom_effects"]) == 2

    def test_cauldron_no_essence_no_effects_key(self, conv):
        nbt = {"hasGlowstone": False, "hasNetherwart": False, "hasGunpowder": False,
               "redstoneCount": 0, "cookTime": 0, "potionEssence": {}}
        result = conv.convert_tile_entity("reliquaryCauldron", nbt, metadata=3)
        assert "effects" not in result.nbt_1182

    def test_cauldron_cook_time_preserved(self, conv):
        nbt = {"hasGlowstone": False, "hasNetherwart": True, "hasGunpowder": False,
               "redstoneCount": 3, "cookTime": 120, "potionEssence": {}}
        result = conv.convert_tile_entity("reliquaryCauldron", nbt, metadata=1)
        assert result.nbt_1182["cookTime"] == 120
        assert result.nbt_1182["redstoneCount"] == 3


# =============================================================================
# Apothecary Mortar
# =============================================================================

class TestMortarConverter:

    def test_mortar_block_id(self, conv):
        result = conv.convert_tile_entity("apothecaryMortar", {"pestleUsed": 0, "Items": []})
        assert result.success
        assert result.block_id_1182 == "reliquary:apothecary_mortar"

    def test_mortar_empty(self, conv):
        result = conv.convert_tile_entity("apothecaryMortar", {"pestleUsed": 0, "Items": []})
        assert result.nbt_1182["pestleUsed"] == 0
        assert result.nbt_1182["items"]["Size"] == 3
        assert result.nbt_1182["items"]["Items"] == []

    def test_mortar_pestle_used_preserved(self, conv):
        nbt = {
            "pestleUsed": 3,
            "Items": [
                {"Slot": 0, "id": "minecraft:sugar", "Count": 1, "Damage": 0},
            ],
        }
        result = conv.convert_tile_entity("apothecaryMortar", nbt)
        assert result.nbt_1182["pestleUsed"] == 3

    def test_mortar_xreliquary_prefix_remapped(self, conv):
        nbt = {
            "pestleUsed": 2,
            "Items": [
                {"Slot": 0, "id": "xreliquary:mob_ingredient", "Count": 1, "Damage": 3},
            ],
        }
        result = conv.convert_tile_entity("apothecaryMortar", nbt)
        ids = [i["id"] for i in result.nbt_1182["items"]["Items"]]
        assert "reliquary:mob_ingredient" in ids
        assert "xreliquary:mob_ingredient" not in ids

    def test_mortar_item_stack_handler_format(self, conv):
        nbt = {
            "pestleUsed": 1,
            "Items": [
                {"Slot": 0, "id": "minecraft:ghast_tear", "Count": 1, "Damage": 0},
            ],
        }
        result = conv.convert_tile_entity("apothecaryMortar", nbt)
        handler = result.nbt_1182["items"]
        assert "Size" in handler
        assert handler["Size"] == 3
        for item in handler["Items"]:
            assert "Count" in item
            assert "count" not in item

    def test_mortar_vanilla_item_id_unchanged(self, conv):
        nbt = {
            "pestleUsed": 0,
            "Items": [
                {"Slot": 0, "id": "minecraft:blaze_powder", "Count": 1, "Damage": 0},
            ],
        }
        result = conv.convert_tile_entity("apothecaryMortar", nbt)
        ids = [i["id"] for i in result.nbt_1182["items"]["Items"]]
        assert "minecraft:blaze_powder" in ids


# =============================================================================
# Unknown TE id
# =============================================================================

class TestUnknownTE:

    def test_unknown_te_id_fails(self, conv):
        result = conv.convert_tile_entity("unknownReliquaryTE", {})
        assert not result.success
        assert result.errors


# =============================================================================
# Router integration
# =============================================================================

class TestRouterDetection:

    def test_detect_altar(self):
        from converters.router import detect_mod
        assert detect_mod("reliquaryAltar") == "reliquary"

    def test_detect_cauldron(self):
        from converters.router import detect_mod
        assert detect_mod("reliquaryCauldron") == "reliquary"

    def test_detect_mortar(self):
        from converters.router import detect_mod
        assert detect_mod("apothecaryMortar") == "reliquary"

    def test_altar_produces_event(self):
        from converters.router import convert_te_to_events
        te = {"id": "reliquaryAltar", "cycleTime": 100, "redstoneCount": 2, "isActive": True}
        events = convert_te_to_events(te, block_numeric_id=0, metadata=0, global_pos=(10, 64, 20))
        assert len(events) == 1
        ev = events[0]
        assert ev["op"] == "set_block_entity"
        assert ev["block"] == "reliquary:alkahestry_altar"
        assert ev["nbt"]["cycleTime"] == 100

    def test_cauldron_produces_event(self):
        from converters.router import convert_te_to_events
        te = {
            "id": "reliquaryCauldron",
            "hasGlowstone": True, "hasNetherwart": True, "hasGunpowder": False,
            "redstoneCount": 2, "cookTime": 80,
            "potionEssence": {
                "effects": [{"id": 1, "duration": 900, "potency": 0}]
            },
        }
        events = convert_te_to_events(te, block_numeric_id=0, metadata=3, global_pos=(5, 64, 5))
        assert len(events) == 1
        ev = events[0]
        assert ev["block"] == "reliquary:apothecary_cauldron"
        assert ev["nbt"]["liquidLevel"] == 3
        assert ev["nbt"]["glowstoneCount"] == 1

    def test_mortar_produces_event(self):
        from converters.router import convert_te_to_events
        te = {
            "id": "apothecaryMortar",
            "pestleUsed": 2,
            "Items": [{"Slot": 0, "id": "minecraft:sugar", "Count": 1, "Damage": 0}],
        }
        events = convert_te_to_events(te, block_numeric_id=0, metadata=0, global_pos=(0, 64, 0))
        assert len(events) == 1
        ev = events[0]
        assert ev["block"] == "reliquary:apothecary_mortar"
        assert ev["nbt"]["pestleUsed"] == 2
