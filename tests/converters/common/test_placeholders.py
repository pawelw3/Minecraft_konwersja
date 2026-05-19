import unittest
from copy import deepcopy

from src.converters.common.placeholders import (
    PLACEHOLDER_BLOCK_ENTITY_ID,
    PLACEHOLDER_BLOCK_ID,
    is_placeholder_event,
    make_block_entity_placeholder_event,
    summarize_placeholder_events,
)


class TestPlaceholderEvent(unittest.TestCase):
    def test_builds_standard_set_block_entity_event(self):
        event = make_block_entity_placeholder_event(
            position=(10, 64, -5),
            source_mod="Thaumcraft",
            source_block_id="Thaumcraft:blockMetalDevice",
            source_te_id="TileAlchemyFurnace",
            source_metadata=2,
            original_nbt={"id": "TileAlchemyFurnace", "x": 1, "y": 2, "z": 3},
            conversion_stage="thaumcraft_zadanie3",
        )

        self.assertEqual(event["op"], "set_block_entity")
        self.assertEqual(event["pos"], [10, 64, -5])
        self.assertEqual(event["block"], PLACEHOLDER_BLOCK_ID)
        self.assertEqual(event["nbt"]["id"], PLACEHOLDER_BLOCK_ENTITY_ID)
        self.assertEqual(event["nbt"]["x"], 10)
        self.assertEqual(event["nbt"]["y"], 64)
        self.assertEqual(event["nbt"]["z"], -5)
        self.assertEqual(event["nbt"]["source_pos"], [1, 2, 3])
        self.assertEqual(event["source"]["mod"], "Thaumcraft")
        self.assertEqual(event["source"]["te_id"], "TileAlchemyFurnace")
        self.assertTrue(is_placeholder_event(event))

    def test_preserves_nested_original_nbt_and_deep_copies(self):
        original = {
            "id": "Machine",
            "Items": [
                {"Slot": 0, "id": "minecraft:diamond", "Count": 64},
                {"Slot": 1, "tag": {"display": {"Name": "Legacy"}}},
            ],
            "Config": {"side": {"north": "input"}},
        }
        snapshot = deepcopy(original)

        event = make_block_entity_placeholder_event(
            position=(0, 70, 0),
            source_mod="ExampleMod",
            original_nbt=original,
        )
        original["Items"][0]["Count"] = 1

        self.assertEqual(event["nbt"]["original_nbt"], snapshot)
        self.assertEqual(event["nbt"]["source_te_id"], "Machine")

    def test_handles_missing_original_nbt(self):
        event = make_block_entity_placeholder_event(
            position=(1, 2, 3),
            source_mod="UnknownMod",
        )

        self.assertEqual(event["nbt"]["original_nbt"], {})
        self.assertEqual(event["nbt"]["source_pos"], [1, 2, 3])
        self.assertEqual(event["nbt"]["source_te_id"], "")
        self.assertEqual(event["nbt"]["conversion_reason"], "unsupported_be")


class TestPlaceholderReport(unittest.TestCase):
    def test_summarizes_by_mod_te_and_zone(self):
        events = [
            make_block_entity_placeholder_event(
                position=(0, 64, 0),
                source_mod="Thaumcraft",
                source_te_id="A",
            ),
            make_block_entity_placeholder_event(
                position=(100, 64, 100),
                source_mod="Thaumcraft",
                source_te_id="B",
            ),
            make_block_entity_placeholder_event(
                position=(200, 64, 200),
                source_mod="Forestry",
                source_te_id="A",
            ),
            {"op": "set_block", "block": "minecraft:stone", "pos": [0, 0, 0]},
        ]

        report = summarize_placeholder_events(
            events,
            zone_resolver=lambda pos, _event: "spawn" if pos[0] < 150 else "outer",
        ).to_dict()

        self.assertEqual(report["total"], 3)
        self.assertEqual(report["by_mod"], {"Forestry": 1, "Thaumcraft": 2})
        self.assertEqual(report["by_te_id"], {"A": 2, "B": 1})
        self.assertEqual(report["by_zone"], {"outer": 1, "spawn": 2})


if __name__ == "__main__":
    unittest.main()
