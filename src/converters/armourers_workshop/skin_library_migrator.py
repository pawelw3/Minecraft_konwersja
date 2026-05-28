"""Armourer's Workshop `.armour` library migration orchestration.

Source mapping:
- 1.7.10 `SkinIOUtils.getSkinLibraryDirectory()` stores server skins under
  `<server-root>/armourersWorkshop`.
- 1.18.2 `EnvironmentManager.getSkinLibraryDirectory()` stores them under
  `<server-root>/skin-library`.
- 1.18.2 `SkinSerializer` reads v12/v13/v20 and `SkinSerializerV20` writes
  latest v25 with the leading `SKIN` header.

This module does not reimplement the binary skin serializer in Python.  It
prepares and validates the file migration, while the actual v12/v13 -> v25
rewrite is delegated to a runner backed by the 1.18.2 Armourer's Workshop
serializer.
"""

from __future__ import annotations

import json
import shutil
import struct
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

from .simulations.step2_contract_simulations import normalize_library_path


SKIN_HEADER = 0x534B494E
TARGET_FILE_VERSION = 25
DEFAULT_SOURCE_ROOT = Path("pliki_globalne_serwer_1710") / "armourersWorkshop"
DEFAULT_TARGET_ROOT = Path("mapa_118") / "skin-library"

Runner = Callable[[Path, Path], None]


@dataclass(frozen=True)
class SkinLibraryFile:
    source_path: Path
    relative_path: str
    target_path: Path
    source_file_version: int
    source_has_modern_header: bool = False

    @property
    def target_identifier(self) -> str:
        return f"ws:{self.relative_path}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": str(self.source_path),
            "relative_path": self.relative_path,
            "target_path": str(self.target_path),
            "source_file_version": self.source_file_version,
            "source_has_modern_header": self.source_has_modern_header,
            "target_identifier": self.target_identifier,
        }


@dataclass
class SkinLibraryMigrationResult:
    source_root: Path
    target_root: Path
    entries: list[SkinLibraryFile] = field(default_factory=list)
    converted: list[dict[str, Any]] = field(default_factory=list)
    skipped: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    dry_run: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_root": str(self.source_root),
            "target_root": str(self.target_root),
            "entry_count": len(self.entries),
            "converted_count": len(self.converted),
            "skipped_count": len(self.skipped),
            "error_count": len(self.errors),
            "dry_run": self.dry_run,
            "entries": [entry.to_dict() for entry in self.entries],
            "converted": self.converted,
            "skipped": self.skipped,
            "errors": self.errors,
        }

    def write_manifest(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True), encoding="utf-8")


def scan_skin_library(source_root: Path, target_root: Path) -> list[SkinLibraryFile]:
    source_root = Path(source_root)
    target_root = Path(target_root)
    if not source_root.exists():
        raise FileNotFoundError(f"Armourer's Workshop source library not found: {source_root}")
    entries: list[SkinLibraryFile] = []
    for source_path in sorted(source_root.rglob("*.armour"), key=lambda path: str(path).lower()):
        relative_path = normalize_library_path(str(source_path.relative_to(source_root)), require_extension=True)
        header = read_skin_file_header(source_path)
        entries.append(
            SkinLibraryFile(
                source_path=source_path,
                relative_path=relative_path,
                target_path=target_root / Path(relative_path),
                source_file_version=header["file_version"],
                source_has_modern_header=header["has_modern_header"],
            )
        )
    return entries


def migrate_skin_library(
    source_root: Path = DEFAULT_SOURCE_ROOT,
    target_root: Path = DEFAULT_TARGET_ROOT,
    *,
    runner: Runner | None = None,
    runner_command: Sequence[str] | None = None,
    dry_run: bool = False,
    allow_legacy_copy_for_tests: bool = False,
) -> SkinLibraryMigrationResult:
    """Run or plan `.armour` library migration.

    `runner` or `runner_command` must perform the actual binary rewrite using
    AW 1.18.2 `SkinSerializer.readFromStream` and `writeToStream(...v25...)`.
    The output is accepted only when it validates as modern v25.
    """

    source_root = Path(source_root)
    target_root = Path(target_root)
    entries = scan_skin_library(source_root, target_root)
    result = SkinLibraryMigrationResult(source_root, target_root, entries=entries, dry_run=dry_run)
    selected_runner = runner or _subprocess_runner(runner_command)

    for entry in entries:
        if dry_run:
            result.skipped.append(_entry_status(entry, "dry_run"))
            continue
        if selected_runner is None and not allow_legacy_copy_for_tests:
            result.errors.append(_entry_status(entry, "missing_runner", "No AW serializer runner was provided."))
            continue

        entry.target_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            if allow_legacy_copy_for_tests:
                shutil.copyfile(entry.source_path, entry.target_path)
            else:
                assert selected_runner is not None
                selected_runner(entry.source_path, entry.target_path)
            target_header = read_skin_file_header(entry.target_path)
            if target_header != {"has_modern_header": True, "file_version": TARGET_FILE_VERSION}:
                raise ValueError(f"target is not v{TARGET_FILE_VERSION} with SKIN header: {target_header}")
            result.converted.append(_entry_status(entry, "converted", target_header=target_header))
        except Exception as exc:  # noqa: BLE001 - preserve per-file diagnostics
            result.errors.append(_entry_status(entry, "failed", str(exc)))
    return result


def read_skin_file_header(path: Path) -> dict[str, Any]:
    data = Path(path).read_bytes()[:8]
    if len(data) < 4:
        raise ValueError(f"file too short: {path}")
    first = struct.unpack(">i", data[:4])[0]
    if first == SKIN_HEADER:
        if len(data) < 8:
            raise ValueError(f"modern header without version: {path}")
        return {"has_modern_header": True, "file_version": struct.unpack(">i", data[4:8])[0]}
    return {"has_modern_header": False, "file_version": first}


def write_cli_manifest(
    source_root: Path = DEFAULT_SOURCE_ROOT,
    target_root: Path = DEFAULT_TARGET_ROOT,
    manifest_path: Path = Path("output") / "armourers_workshop_step4" / "skin_library_migration_manifest.json",
) -> SkinLibraryMigrationResult:
    result = migrate_skin_library(source_root, target_root, dry_run=True)
    result.write_manifest(manifest_path)
    return result


def _subprocess_runner(command: Sequence[str] | None) -> Runner | None:
    if not command:
        return None

    def run(source_path: Path, target_path: Path) -> None:
        args = [
            part.format(source=str(source_path), target=str(target_path), version=str(TARGET_FILE_VERSION))
            for part in command
        ]
        completed = subprocess.run(args, check=False, capture_output=True, text=True)
        if completed.returncode != 0:
            raise RuntimeError(
                f"runner failed with {completed.returncode}: "
                f"stdout={completed.stdout.strip()} stderr={completed.stderr.strip()}"
            )

    return run


def _entry_status(
    entry: SkinLibraryFile,
    status: str,
    message: str | None = None,
    *,
    target_header: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data = entry.to_dict()
    data["status"] = status
    if message:
        data["message"] = message
    if target_header:
        data["target_header"] = target_header
    return data


def _main(argv: Iterable[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Plan or run Armourer's Workshop skin library migration.")
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET_ROOT)
    parser.add_argument("--manifest", type=Path, default=Path("output/armourers_workshop_step4/skin_library_migration_manifest.json"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--runner", nargs="+", help="Command template; use {source}, {target}, {version}.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    result = migrate_skin_library(
        args.source_root,
        args.target_root,
        runner_command=args.runner,
        dry_run=args.dry_run or not args.runner,
    )
    result.write_manifest(args.manifest)
    print(json.dumps({k: result.to_dict()[k] for k in ("entry_count", "converted_count", "skipped_count", "error_count", "dry_run")}, indent=2))
    return 1 if result.errors else 0


if __name__ == "__main__":
    raise SystemExit(_main())

