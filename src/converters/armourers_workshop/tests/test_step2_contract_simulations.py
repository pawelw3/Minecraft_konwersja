from __future__ import annotations

from src.converters.armourers_workshop.simulations.step2_contract_simulations import (
    ArmourSkinFile,
    SkinIdentifier1710,
    SkinPointer1710,
    choose_read_serializer,
    choose_write_serializer,
    migrate_library,
    migrate_part_type,
    migrate_skin_file_to_1182,
    migrate_skin_pointer,
    normalize_library_path,
    normalize_source_library_path,
    run_simulations,
)


def test_v13_skin_uses_1182_v13_reader_and_forced_latest_writer() -> None:
    assert choose_read_serializer(13) == "SkinSerializerV13"
    decision = choose_write_serializer(13, force_latest=True)
    assert decision.read_serializer == "SkinSerializerV13"
    assert decision.write_serializer == "SkinSerializerV20"
    assert decision.output_file_version == 25
    assert decision.requires_header is True


def test_without_latest_force_v13_would_remain_legacy() -> None:
    decision = choose_write_serializer(13, force_latest=False)
    assert decision.write_serializer == "SkinSerializerV13"
    assert decision.output_file_version == 13
    assert decision.requires_header is False


def test_part_aliases_match_1182_v13_serializer_contract() -> None:
    assert migrate_part_type("armourers:skirt.base") == "armourers:legs.skirt"
    assert migrate_part_type("armourers:bow.base") == "armourers:bow.frame1"
    assert migrate_part_type("armourers:arrow.base") == "armourers:bow.arrow"
    assert migrate_part_type("armourers:head.base") == "armourers:head.base"


def test_library_file_migrates_to_ws_identifier_and_keeps_extension() -> None:
    skin_file = ArmourSkinFile(
        relative_path="official/demo_block.armour",
        file_version=13,
        skin_type="armourers:block",
        part_types=("armourers:skirt.base",),
    )
    entry = migrate_skin_file_to_1182(skin_file)
    assert entry.path == "official/demo_block.armour"
    assert entry.skin_identifier == "ws:official/demo_block.armour"
    assert entry.target_file_version == 25
    assert entry.migrated_parts == ("armourers:legs.skirt",)


def test_library_migration_filters_non_armour_and_invalid_headers() -> None:
    files = [
        ArmourSkinFile("a/head.armour", 13, "armourers:head", valid_header=True),
        ArmourSkinFile("a/readme.txt", 13, "unknown", valid_header=True),
        ArmourSkinFile("a/broken.armour", 13, "unknown", valid_header=False),
    ]
    entries = migrate_library(files)
    assert [entry.path for entry in entries] == ["a/head.armour"]


def test_path_normalization_blocks_parent_escape_and_colons() -> None:
    assert normalize_library_path("../private/a:b", require_extension=True) == "_/private/a_b.armour"


def test_source_library_path_strips_1710_global_root() -> None:
    path = "pliki_globalne_serwer_1710/armourersWorkshop/folder/Test.armour"
    assert normalize_source_library_path(path) == "folder/Test.armour"


def test_skin_pointer_library_file_becomes_server_library_descriptor() -> None:
    pointer = SkinPointer1710(
        SkinIdentifier1710(library_file="town/hat", skin_type="armourers:head"),
        lock_skin=True,
        dye={"primary": 12},
    )
    descriptor = migrate_skin_pointer(pointer)
    assert descriptor.identifier == "ws:town/hat.armour"
    assert descriptor.skin_type == "armourers:head"
    assert descriptor.lock_skin is True
    assert descriptor.dye == {"primary": 12}
    assert descriptor.warnings == ()


def test_skin_pointer_global_and_local_ids_get_explicit_rescue_domains() -> None:
    global_descriptor = migrate_skin_pointer(
        SkinPointer1710(SkinIdentifier1710(global_id=44, skin_type="armourers:feet"))
    )
    local_descriptor = migrate_skin_pointer(
        SkinPointer1710(SkinIdentifier1710(local_id=55, skin_type="armourers:chest"))
    )
    assert global_descriptor.identifier == "ks:44"
    assert "global" in global_descriptor.warnings[0]
    assert local_descriptor.identifier == "db:55"
    assert "rescue" in local_descriptor.warnings[0]


def test_run_simulations_contracts_pass() -> None:
    results = run_simulations()
    assert all(results["contracts"].values())
