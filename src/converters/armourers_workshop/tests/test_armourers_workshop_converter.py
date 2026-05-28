from __future__ import annotations

from src.converters.armourers_workshop.converter import (
    ArmourersWorkshopConverter,
    build_library_migration_event,
)


def test_skin_library_block_maps_to_1182_hyphenated_id() -> None:
    converter = ArmourersWorkshopConverter()
    conversion = converter.convert_block(
        "armourersworkshop:block.armourLibrary",
        metadata=0,
        nbt_1710={"id": "te.armourLibrary", "x": 1, "y": 64, "z": 2},
        position=(1, 64, 2),
    )

    assert conversion.converted.success is True
    assert conversion.converted.block_id_1182 == "armourers_workshop:skin-library"
    assert conversion.converted.nbt_1182 == {
        "id": "armourers_workshop:skin-library",
        "x": 1,
        "y": 64,
        "z": 2,
    }
    assert converter.to_events(conversion)[0]["op"] == "set_block_entity"


def test_skinnable_parent_migrates_skin_pointer_and_related_offsets() -> None:
    converter = ArmourersWorkshopConverter()
    conversion = converter.convert_block(
        "armourersworkshop:block.skinnable",
        metadata=4,
        nbt_1710={
            "id": "te.skinnable",
            "x": 10,
            "y": 70,
            "z": -5,
            "hasSkin": True,
            "armourersWorkshop": {
                "identifier": {
                    "localId": 123,
                    "libraryFile": "official/Barrel",
                    "globalId": 0,
                    "skinType": "armourers:block",
                },
                "lock": True,
            },
            "relatedBlocks": [
                {"x": 10, "y": 70, "z": -5},
                {"x": 11, "y": 70, "z": -5},
            ],
        },
        position=(10, 70, -5),
    )

    assert conversion.converted.block_id_1182 == "armourers_workshop:skinnable"
    assert conversion.converted.blockstate_props["facing"] == "north"
    assert conversion.converted.nbt_1182["Skin"] == {
        "Identifier": "ws:official/Barrel.armour",
        "SkinType": "armourers:block",
    }
    assert conversion.converted.nbt_1182["Refers"] == [[0, 0, 0], [1, 0, 0]]
    assert any("SHAPE" in warning for warning in conversion.converted.warnings)


def test_skinnable_child_uses_parent_reference_offset() -> None:
    converter = ArmourersWorkshopConverter()
    conversion = converter.convert_block(
        "armourersworkshop:block.skinnableChild",
        metadata=5,
        nbt_1710={
            "id": "te.skinnableChild",
            "x": 12,
            "y": 70,
            "z": -5,
            "parentX": 10,
            "parentY": 70,
            "parentZ": -5,
        },
        position=(12, 70, -5),
    )

    assert conversion.converted.nbt_1182["Refer"] == [2, 0, 0]
    assert conversion.converted.blockstate_props["facing"] == "east"


def test_mannequin_becomes_placeholder_with_entity_hint() -> None:
    converter = ArmourersWorkshopConverter()
    conversion = converter.convert_block(
        "armourersworkshop:block.mannequin",
        nbt_1710={"id": "te.mannequin", "x": 0, "y": 65, "z": 0},
        position=(0, 65, 0),
    )

    event = converter.to_events(conversion)[0]
    assert event["block"] == "conversion_placeholders:block_entity_placeholder"
    assert event["nbt"]["extra"]["target_hint"].startswith("armourers_workshop:mannequin entity")
    assert "original_nbt" in event["nbt"]


def test_unknown_block_fails_without_event() -> None:
    converter = ArmourersWorkshopConverter()
    conversion = converter.convert_block("minecraft:stone")

    assert conversion.converted.success is False
    assert converter.to_events(conversion) == []


def test_library_migration_event_declares_v25_ws_contract() -> None:
    event = build_library_migration_event()

    assert event["op"] == "armourers_workshop_convert_skin_library"
    assert event["target_root"] == "skin-library"
    assert event["target_file_version"] == 25
    assert event["target_identifier_prefix"] == "ws:"

