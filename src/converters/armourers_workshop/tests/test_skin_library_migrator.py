from __future__ import annotations

import struct
from pathlib import Path

from src.converters.armourers_workshop.skin_library_migrator import (
    SKIN_HEADER,
    TARGET_FILE_VERSION,
    migrate_skin_library,
    read_skin_file_header,
    scan_skin_library,
)


def _write_legacy(path: Path, version: int = 13) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(struct.pack(">i", version) + b"legacy-body")


def _write_modern(path: Path, version: int = TARGET_FILE_VERSION) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(struct.pack(">ii", SKIN_HEADER, version) + b"modern-body")


def test_read_skin_file_header_detects_legacy_and_modern(tmp_path: Path) -> None:
    root = tmp_path / "aw_migrator_header_test"
    legacy = root / "legacy.armour"
    modern = root / "modern.armour"
    _write_legacy(legacy, 13)
    _write_modern(modern, 25)

    assert read_skin_file_header(legacy) == {"has_modern_header": False, "file_version": 13}
    assert read_skin_file_header(modern) == {"has_modern_header": True, "file_version": 25}


def test_scan_skin_library_preserves_relative_paths_and_ws_ids(tmp_path: Path) -> None:
    source = tmp_path / "armourersWorkshop"
    target = tmp_path / "skin-library"
    _write_legacy(source / "official" / "Barrel.armour", 13)

    entries = scan_skin_library(source, target)

    assert len(entries) == 1
    assert entries[0].relative_path == "official/Barrel.armour"
    assert entries[0].target_path == target / "official" / "Barrel.armour"
    assert entries[0].target_identifier == "ws:official/Barrel.armour"
    assert entries[0].source_file_version == 13


def test_dry_run_writes_no_targets(tmp_path: Path) -> None:
    source = tmp_path / "armourersWorkshop"
    target = tmp_path / "skin-library"
    _write_legacy(source / "a.armour", 13)

    result = migrate_skin_library(source, target, dry_run=True)

    assert result.dry_run is True
    assert result.converted == []
    assert len(result.skipped) == 1
    assert not (target / "a.armour").exists()


def test_missing_runner_is_error_not_legacy_copy(tmp_path: Path) -> None:
    source = tmp_path / "armourersWorkshop"
    target = tmp_path / "skin-library"
    _write_legacy(source / "a.armour", 13)

    result = migrate_skin_library(source, target)

    assert result.converted == []
    assert result.errors[0]["status"] == "missing_runner"


def test_runner_output_must_be_modern_v25(tmp_path: Path) -> None:
    source = tmp_path / "armourersWorkshop"
    target = tmp_path / "skin-library"
    _write_legacy(source / "a.armour", 13)

    def bad_runner(_source_path: Path, target_path: Path) -> None:
        _write_legacy(target_path, 13)

    result = migrate_skin_library(source, target, runner=bad_runner)

    assert result.converted == []
    assert "not v25" in result.errors[0]["message"]


def test_runner_can_convert_to_modern_v25(tmp_path: Path) -> None:
    source = tmp_path / "armourersWorkshop"
    target = tmp_path / "skin-library"
    _write_legacy(source / "official" / "Barrel.armour", 13)

    def good_runner(_source_path: Path, target_path: Path) -> None:
        _write_modern(target_path, 25)

    result = migrate_skin_library(source, target, runner=good_runner)

    assert len(result.converted) == 1
    assert result.errors == []
    assert read_skin_file_header(target / "official" / "Barrel.armour") == {
        "has_modern_header": True,
        "file_version": 25,
    }
