"""
Testy symulacji Reliquary – Zadanie 2

Uruchamiać z katalogu projektu:
  python -m pytest src/converters/reliquary/simulations/test_simulations.py -v
"""

import pytest
from .potion_essence_sim import (
    PotionEssenceConverter,
    PotionEffect1710,
    INSTANT_EFFECT_IDS,
    POTION_ID_TO_RESOURCE,
    SAMPLE_ESSENCE_SPEED_REGEN,
    SAMPLE_ESSENCE_STRENGTH_FIRE,
    SAMPLE_ESSENCE_INSTANT_HARM,
    SAMPLE_ESSENCE_MULTI,
    SAMPLE_ESSENCE_UNKNOWN_ID,
)
from .cauldron_sim import (
    CauldronConverter,
    SAMPLE_CAULDRON_EMPTY,
    SAMPLE_CAULDRON_BREWING,
    SAMPLE_CAULDRON_DONE_SPLASH,
    SAMPLE_CAULDRON_PARTIAL,
)
from .mortar_sim import (
    MortarConverter,
    SAMPLE_MORTAR_EMPTY,
    SAMPLE_MORTAR_TWO_INGREDIENTS,
    SAMPLE_MORTAR_MOB_INGREDIENT,
    SAMPLE_MORTAR_WITH_ESSENCE,
    SAMPLE_MORTAR_FULL,
)


# =============================================================================
# PotionEssenceConverter
# =============================================================================

class TestPotionEssenceConverter:

    def setup_method(self):
        self.converter = PotionEssenceConverter()

    def test_speed_regen_conversion(self):
        result, warnings = self.converter.build_cauldron_effects_tag(SAMPLE_ESSENCE_SPEED_REGEN)
        assert len(warnings) == 0
        effects = result["custom_effects"]
        assert len(effects) == 2

        speed = next(e for e in effects if e["id"] == "minecraft:speed")
        assert speed["duration"] == 900
        assert speed["amplifier"] == 0
        assert speed["ambient"] is False
        assert speed["show_particles"] is True

        regen = next(e for e in effects if e["id"] == "minecraft:regeneration")
        assert regen["duration"] == 300
        assert regen["amplifier"] == 0

    def test_strength_ii_fire_resistance(self):
        result, warnings = self.converter.build_cauldron_effects_tag(SAMPLE_ESSENCE_STRENGTH_FIRE)
        assert len(warnings) == 0
        effects = result["custom_effects"]
        assert len(effects) == 2

        strength = next(e for e in effects if e["id"] == "minecraft:strength")
        assert strength["amplifier"] == 1  # potency=1 → amplifier=1

        fire = next(e for e in effects if e["id"] == "minecraft:fire_resistance")
        assert fire["duration"] == 3600

    def test_instant_damage_duration_forced_to_1(self):
        result, warnings = self.converter.build_cauldron_effects_tag(SAMPLE_ESSENCE_INSTANT_HARM)
        assert len(warnings) == 0
        effects = result["custom_effects"]

        harm = next(e for e in effects if e["id"] == "minecraft:instant_damage")
        # Efekt instant – duration zawsze 1, niezależnie od wartości wejściowej
        assert harm["duration"] == 1

        weakness = next(e for e in effects if e["id"] == "minecraft:weakness")
        assert weakness["duration"] == 300

    def test_multi_effect_count(self):
        result, warnings = self.converter.build_cauldron_effects_tag(SAMPLE_ESSENCE_MULTI)
        assert len(warnings) == 0
        assert len(result["custom_effects"]) == 4

    def test_unknown_potion_id_generates_warning(self):
        result, warnings = self.converter.build_cauldron_effects_tag(SAMPLE_ESSENCE_UNKNOWN_ID)
        assert len(warnings) == 1
        assert "99" in warnings[0]
        # Speed nadal jest skonwertowany
        assert len(result["custom_effects"]) == 1
        assert result["custom_effects"][0]["id"] == "minecraft:speed"

    def test_empty_essence_returns_empty_custom_effects(self):
        result, warnings = self.converter.build_cauldron_effects_tag({"effects": []})
        assert "custom_effects" not in result

    def test_all_vanilla_ids_have_mapping(self):
        for potion_id in range(1, 24):
            assert potion_id in POTION_ID_TO_RESOURCE, f"Brakuje mapowania dla ID {potion_id}"

    def test_instant_effect_ids_are_correct(self):
        assert 6 in INSTANT_EFFECT_IDS   # instant_health
        assert 7 in INSTANT_EFFECT_IDS   # instant_damage
        assert 1 not in INSTANT_EFFECT_IDS  # speed to nie instant


# =============================================================================
# CauldronConverter
# =============================================================================

class TestCauldronConverter:

    def setup_method(self):
        self.converter = CauldronConverter()

    def test_empty_cauldron_meta3(self):
        nbt, warnings = self.converter.convert_to_nbt(
            SAMPLE_CAULDRON_EMPTY["te_nbt"], SAMPLE_CAULDRON_EMPTY["block_meta"]
        )
        assert nbt["liquidLevel"] == 3
        assert nbt["glowstoneCount"] == 0
        assert nbt["hasGunpowder"] is False
        assert nbt["hasDragonBreath"] is False
        assert "effects" not in nbt

    def test_glowstone_bool_to_int_true(self):
        nbt, _ = self.converter.convert_to_nbt(
            SAMPLE_CAULDRON_BREWING["te_nbt"], SAMPLE_CAULDRON_BREWING["block_meta"]
        )
        # hasGlowstone=True → glowstoneCount=1
        assert nbt["glowstoneCount"] == 1

    def test_glowstone_bool_to_int_false(self):
        nbt, _ = self.converter.convert_to_nbt(
            SAMPLE_CAULDRON_DONE_SPLASH["te_nbt"], SAMPLE_CAULDRON_DONE_SPLASH["block_meta"]
        )
        # hasGlowstone=False → glowstoneCount=0
        assert nbt["glowstoneCount"] == 0

    def test_liquid_level_from_block_meta(self):
        # meta=2 → liquidLevel=2
        nbt, _ = self.converter.convert_to_nbt(
            SAMPLE_CAULDRON_DONE_SPLASH["te_nbt"], SAMPLE_CAULDRON_DONE_SPLASH["block_meta"]
        )
        assert nbt["liquidLevel"] == 2

    def test_dragon_breath_always_false(self):
        nbt, _ = self.converter.convert_to_nbt(
            SAMPLE_CAULDRON_BREWING["te_nbt"], SAMPLE_CAULDRON_BREWING["block_meta"]
        )
        assert nbt["hasDragonBreath"] is False

    def test_brewing_cauldron_has_effects(self):
        nbt, warnings = self.converter.convert_to_nbt(
            SAMPLE_CAULDRON_BREWING["te_nbt"], SAMPLE_CAULDRON_BREWING["block_meta"]
        )
        assert len(warnings) == 0
        assert "effects" in nbt
        assert "custom_effects" in nbt["effects"]
        assert len(nbt["effects"]["custom_effects"]) == 2

    def test_cook_time_and_redstone_preserved(self):
        nbt, _ = self.converter.convert_to_nbt(
            SAMPLE_CAULDRON_BREWING["te_nbt"], SAMPLE_CAULDRON_BREWING["block_meta"]
        )
        assert nbt["cookTime"] == 80
        assert nbt["redstoneCount"] == 2

    def test_netherwart_and_gunpowder_preserved(self):
        nbt, _ = self.converter.convert_to_nbt(
            SAMPLE_CAULDRON_DONE_SPLASH["te_nbt"], SAMPLE_CAULDRON_DONE_SPLASH["block_meta"]
        )
        assert nbt["hasNetherwart"] is True
        assert nbt["hasGunpowder"] is True

    def test_invalid_meta_generates_warning(self):
        _, warnings = self.converter.convert_to_nbt(
            SAMPLE_CAULDRON_EMPTY["te_nbt"], block_meta=99
        )
        assert any("metadata" in w for w in warnings)

    def test_partial_cauldron_meta1(self):
        nbt, _ = self.converter.convert_to_nbt(
            SAMPLE_CAULDRON_PARTIAL["te_nbt"], SAMPLE_CAULDRON_PARTIAL["block_meta"]
        )
        assert nbt["liquidLevel"] == 1
        assert nbt["glowstoneCount"] == 1
        assert nbt["redstoneCount"] == 5


# =============================================================================
# MortarConverter
# =============================================================================

class TestMortarConverter:

    def setup_method(self):
        self.converter = MortarConverter()

    def test_empty_mortar(self):
        nbt, warnings = self.converter.convert(SAMPLE_MORTAR_EMPTY)
        assert len(warnings) == 0
        assert nbt["pestleUsed"] == 0
        assert nbt["items"]["Size"] == 3
        assert nbt["items"]["Items"] == []

    def test_pestle_used_preserved(self):
        nbt, _ = self.converter.convert(SAMPLE_MORTAR_TWO_INGREDIENTS)
        assert nbt["pestleUsed"] == 2

    def test_vanilla_item_id_unchanged(self):
        nbt, _ = self.converter.convert(SAMPLE_MORTAR_TWO_INGREDIENTS)
        ids = [i["id"] for i in nbt["items"]["Items"]]
        assert "minecraft:sugar" in ids
        assert "minecraft:ghast_tear" in ids

    def test_xreliquary_prefix_remapped(self):
        nbt, _ = self.converter.convert(SAMPLE_MORTAR_MOB_INGREDIENT)
        ids = [i["id"] for i in nbt["items"]["Items"]]
        assert "reliquary:mob_ingredient" in ids
        assert "xreliquary:mob_ingredient" not in ids

    def test_mob_ingredient_damage_to_components(self):
        nbt, _ = self.converter.convert(SAMPLE_MORTAR_MOB_INGREDIENT)
        items = nbt["items"]["Items"]
        mob_item = next(i for i in items if "mob_ingredient" in i["id"])
        # Damage=3 powinien być zachowany w components
        assert mob_item.get("components") is not None
        assert mob_item["components"]["minecraft:custom_data"]["Damage"] == 3

    def test_potion_essence_converted(self):
        nbt, warnings = self.converter.convert(SAMPLE_MORTAR_WITH_ESSENCE)
        assert len(warnings) == 0
        items = nbt["items"]["Items"]
        essence_item = next(i for i in items if "potion_essence" in i["id"])
        assert essence_item["id"] == "reliquary:potion_essence"
        assert "minecraft:potion_contents" in essence_item.get("components", {})
        contents = essence_item["components"]["minecraft:potion_contents"]
        assert len(contents["custom_effects"]) == 2

    def test_full_mortar_three_slots(self):
        nbt, _ = self.converter.convert(SAMPLE_MORTAR_FULL)
        assert len(nbt["items"]["Items"]) == 3

    def test_item_stack_handler_format(self):
        nbt, _ = self.converter.convert(SAMPLE_MORTAR_TWO_INGREDIENTS)
        handler = nbt["items"]
        assert "Size" in handler
        assert "Items" in handler
        assert handler["Size"] == 3
        # Forge 1.18.2: ItemStack uses "Count" (uppercase, byte) not "count"
        for item in handler["Items"]:
            assert "Count" in item
            assert "count" not in item

    def test_slot_numbers_preserved(self):
        nbt, _ = self.converter.convert(SAMPLE_MORTAR_MOB_INGREDIENT)
        items = nbt["items"]["Items"]
        slots = [i["Slot"] for i in items]
        assert 0 in slots
        assert 1 in slots
