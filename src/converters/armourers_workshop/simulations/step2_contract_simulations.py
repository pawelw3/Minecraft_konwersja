"""Armourer's Workshop task 2 contract simulations.

These simulations do not emulate Minecraft. They encode the conversion
contracts that matter for Armourer's Workshop 1.7.10 -> 1.18.2:

* legacy `.armour` serializer dispatch,
* library folder/path migration,
* skin pointer / descriptor migration,
* legacy part-name aliases kept by the 1.18.2 v13 reader.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
MOD_DIR = ROOT / "src" / "converters" / "armourers_workshop"
OUT_JSON = MOD_DIR / "ARMOURERS_WORKSHOP_ZADANIE2_SIMULATION_RESULTS.json"
OUT_MD = MOD_DIR / "ARMOURERS_WORKSHOP_ZADANIE2_SYMULACJE.md"
STEP1_INVENTORY = ROOT / "output" / "armourers_workshop_step1" / "armourers_workshop_step1_inventory.json"


SOURCE_EVIDENCE = {
    "1710_skin_serializer": (
        "Skin.FILE_VERSION = 13 and SkinSerializer.writeToStream writes an int "
        "version followed by AW-SKIN-START/PROPS/TYPE/PAINT/PART markers."
    ),
    "1182_skin_serializer_dispatch": (
        "SkinSerializer registers v20, v13, v12; readFromStream picks by file "
        "version and handles the SKIN header for >=20."
    ),
    "1182_v13_part_aliases": (
        "SkinPartSerializerV13 remaps skirt.base -> legs.skirt, bow.base -> "
        "bow.frame1 and arrow.base -> bow.arrow."
    ),
    "1710_library_dir": (
        "SkinIOUtils.getSkinLibraryDirectory returns user.dir / LibModInfo.ID; "
        "this pack has pliki_globalne_serwer_1710/armourersWorkshop."
    ),
    "1182_library_dir": (
        "EnvironmentManager.getSkinLibraryDirectory returns root / skin-library; "
        "SkinLibraryLoader keeps recursive .armour paths and exposes ws:<path>."
    ),
    "1710_skin_pointer": (
        "SkinPointer stores compound tag armourersWorkshop with identifier, lock "
        "and SkinDye; SkinIdentifier may contain localId, libraryFile, globalId "
        "and skinType."
    ),
    "1182_data_domain": (
        "DataDomain uses namespaces fs, rs, ws, db, ln, ks, kv, sp; server "
        "library skins use ws:<path>."
    ),
}


PART_ALIASES_V13 = {
    "armourers:skirt.base": "armourers:legs.skirt",
    "armourers:bow.base": "armourers:bow.frame1",
    "armourers:arrow.base": "armourers:bow.arrow",
}


@dataclass(frozen=True)
class ArmourSkinFile:
    relative_path: str
    file_version: int
    skin_type: str
    part_types: tuple[str, ...] = ()
    cube_count: int = 0
    valid_header: bool = True

    @property
    def target_path(self) -> str:
        return normalize_library_path(self.relative_path, require_extension=True)

    @property
    def basename(self) -> str:
        return Path(self.target_path).stem


@dataclass(frozen=True)
class SerializerDecision:
    read_serializer: str
    write_serializer: str
    output_file_version: int
    requires_header: bool
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "read_serializer": self.read_serializer,
            "write_serializer": self.write_serializer,
            "output_file_version": self.output_file_version,
            "requires_header": self.requires_header,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class LibraryEntry1182:
    name: str
    path: str
    skin_identifier: str
    skin_type: str | None
    source_file_version: int
    target_file_version: int
    is_directory: bool = False
    migrated_parts: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "skin_identifier": self.skin_identifier,
            "skin_type": self.skin_type,
            "source_file_version": self.source_file_version,
            "target_file_version": self.target_file_version,
            "is_directory": self.is_directory,
            "migrated_parts": list(self.migrated_parts),
        }


@dataclass(frozen=True)
class SkinIdentifier1710:
    local_id: int = 0
    library_file: str | None = None
    global_id: int = 0
    skin_type: str | None = None


@dataclass(frozen=True)
class SkinPointer1710:
    identifier: SkinIdentifier1710
    lock_skin: bool = False
    dye: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SkinDescriptor1182:
    identifier: str
    skin_type: str | None
    dye: dict[str, Any]
    lock_skin: bool
    warnings: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "identifier": self.identifier,
            "skin_type": self.skin_type,
            "dye": self.dye,
            "lock_skin": self.lock_skin,
            "warnings": list(self.warnings),
        }


def normalize_library_path(path: str, require_extension: bool = False) -> str:
    cleaned = path.replace("\\", "/").lstrip("/")
    while "//" in cleaned:
        cleaned = cleaned.replace("//", "/")
    parts = []
    for part in cleaned.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            parts.append("_")
        else:
            parts.append(part.replace(":", "_"))
    normalized = "/".join(parts)
    if require_extension and not normalized.lower().endswith(".armour"):
        normalized += ".armour"
    return normalized


def choose_read_serializer(file_version: int, has_modern_header: bool = False) -> str:
    if has_modern_header and file_version >= 20:
        return "SkinSerializerV20"
    if file_version >= 20:
        return "SkinSerializerV20"
    if file_version == 13:
        return "SkinSerializerV13"
    if file_version <= 12:
        return "SkinSerializerV12"
    raise ValueError(f"Unsupported Armourer's Workshop file version: {file_version}")


def choose_write_serializer(source_version: int, force_latest: bool) -> SerializerDecision:
    read_serializer = choose_read_serializer(source_version)
    if force_latest:
        return SerializerDecision(
            read_serializer=read_serializer,
            write_serializer="SkinSerializerV20",
            output_file_version=25,
            requires_header=True,
            notes=("force SkinFileOptions.FileVersion to Versions.LATEST",),
        )
    if source_version == 13:
        return SerializerDecision(
            read_serializer=read_serializer,
            write_serializer="SkinSerializerV13",
            output_file_version=13,
            requires_header=False,
            notes=("legacy-preserving write; not suitable as final migration output",),
        )
    if source_version <= 12:
        return SerializerDecision(
            read_serializer=read_serializer,
            write_serializer="SkinSerializerV12",
            output_file_version=12,
            requires_header=False,
            notes=("legacy-preserving write; should be followed by latest rewrite",),
        )
    return SerializerDecision(
        read_serializer=read_serializer,
        write_serializer="SkinSerializerV20",
        output_file_version=max(source_version, 25),
        requires_header=True,
    )


def migrate_part_type(part_type: str) -> str:
    return PART_ALIASES_V13.get(part_type, part_type)


def migrate_skin_file_to_1182(skin_file: ArmourSkinFile, force_latest: bool = True) -> LibraryEntry1182:
    decision = choose_write_serializer(skin_file.file_version, force_latest=force_latest)
    migrated_parts = tuple(migrate_part_type(part) for part in skin_file.part_types)
    target_path = skin_file.target_path
    return LibraryEntry1182(
        name=Path(target_path).stem,
        path=target_path,
        skin_identifier=f"ws:{target_path}",
        skin_type=skin_file.skin_type,
        source_file_version=skin_file.file_version,
        target_file_version=decision.output_file_version,
        migrated_parts=migrated_parts,
    )


def migrate_library(files: list[ArmourSkinFile], force_latest: bool = True) -> list[LibraryEntry1182]:
    entries = []
    for skin_file in files:
        if not skin_file.valid_header:
            continue
        if not skin_file.relative_path.lower().endswith(".armour"):
            continue
        entries.append(migrate_skin_file_to_1182(skin_file, force_latest=force_latest))
    return sorted(entries, key=lambda entry: entry.path.lower())


def migrate_skin_pointer(pointer: SkinPointer1710) -> SkinDescriptor1182:
    identifier = pointer.identifier
    warnings: list[str] = []
    if identifier.library_file:
        path = normalize_library_path(identifier.library_file, require_extension=True)
        target_identifier = f"ws:{path}"
    elif identifier.global_id:
        target_identifier = f"ks:{identifier.global_id}"
        warnings.append("global skin id requires online/global-library validation")
    elif identifier.local_id:
        target_identifier = f"db:{identifier.local_id}"
        warnings.append("local database id has no file path; rescue mapping required")
    else:
        target_identifier = "missing:"
        warnings.append("empty skin identifier")
    return SkinDescriptor1182(
        identifier=target_identifier,
        skin_type=identifier.skin_type,
        dye=dict(pointer.dye),
        lock_skin=pointer.lock_skin,
        warnings=tuple(warnings),
    )


def load_step1_sample(limit: int = 10) -> list[ArmourSkinFile]:
    if not STEP1_INVENTORY.exists():
        return []
    data = json.loads(STEP1_INVENTORY.read_text(encoding="utf-8"))
    raw_models = data.get("global_skins_1710", data.get("global_models_1710", []))
    files: list[ArmourSkinFile] = []
    for item in raw_models[:limit]:
        raw_path = item.get("relative_path", item.get("file", item.get("path", "")))
        relative_path = normalize_source_library_path(raw_path)
        files.append(
            ArmourSkinFile(
                relative_path=relative_path,
                file_version=int(item.get("file_version", 13)),
                skin_type=item.get("skin_type") or "unknown",
                part_types=tuple(item.get("part_types", [])),
                cube_count=int(item.get("cube_count", 0)),
                valid_header=item.get("parse_status", "ok") == "ok",
            )
        )
    return files


def normalize_source_library_path(path: str) -> str:
    normalized = normalize_library_path(path, require_extension=False)
    marker = "pliki_globalne_serwer_1710/armourersWorkshop/"
    if normalized.startswith(marker):
        return normalized[len(marker) :]
    marker = "armourersWorkshop/"
    if normalized.startswith(marker):
        return normalized[len(marker) :]
    return normalized


def run_simulations() -> dict[str, Any]:
    sample_files = load_step1_sample(limit=12)
    if not sample_files:
        sample_files = [
            ArmourSkinFile(
                relative_path="official/demo_block.armour",
                file_version=13,
                skin_type="armourers:block",
                part_types=("armourers:skirt.base", "armourers:bow.base"),
                cube_count=42,
            )
        ]

    migrated_library = migrate_library(sample_files, force_latest=True)
    pointer_cases = {
        "library_file": migrate_skin_pointer(
            SkinPointer1710(
                SkinIdentifier1710(library_file="official/demo_block", skin_type="armourers:block"),
                lock_skin=True,
                dye={"primary": 0x336699},
            )
        ),
        "global_id": migrate_skin_pointer(
            SkinPointer1710(SkinIdentifier1710(global_id=12345, skin_type="armourers:head"))
        ),
        "local_id": migrate_skin_pointer(
            SkinPointer1710(SkinIdentifier1710(local_id=67890, skin_type="armourers:chest"))
        ),
    }

    serializer_cases = {
        "legacy_v13_forced_latest": choose_write_serializer(13, force_latest=True).as_dict(),
        "legacy_v13_without_force": choose_write_serializer(13, force_latest=False).as_dict(),
        "modern_v25": choose_write_serializer(25, force_latest=True).as_dict(),
    }

    part_alias_cases = {
        old: migrate_part_type(old)
        for old in ("armourers:skirt.base", "armourers:bow.base", "armourers:arrow.base", "armourers:head.base")
    }

    results = {
        "source_evidence": SOURCE_EVIDENCE,
        "sample_file_count": len(sample_files),
        "migrated_library_count": len(migrated_library),
        "migrated_library": [entry.as_dict() for entry in migrated_library],
        "serializer_cases": serializer_cases,
        "part_alias_cases": part_alias_cases,
        "pointer_cases": {name: descriptor.as_dict() for name, descriptor in pointer_cases.items()},
        "contracts": {
            "v13_reads_with_1182": choose_read_serializer(13) == "SkinSerializerV13",
            "forced_latest_writes_v25": serializer_cases["legacy_v13_forced_latest"]["output_file_version"] == 25,
            "server_library_uses_ws_namespace": all(entry.skin_identifier.startswith("ws:") for entry in migrated_library),
            "library_paths_keep_armour_extension": all(entry.path.endswith(".armour") for entry in migrated_library),
        },
    }
    return results


def write_report(results: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    contracts = results["contracts"]
    lines = [
        "# Armourer's Workshop - Zadanie 2: symulacje kontraktowe",
        "",
        "## Podsumowanie",
        "",
        "Przygotowano czyste symulacje Python dla nietrywialnych funkcji AW 1.7.10 -> 1.18.2:",
        "",
        "- dispatch serializerow `.armour` v12/v13/v20..v25,",
        "- migracja globalnej biblioteki z `armourersWorkshop` do `skin-library`,",
        "- migracja referencji `SkinPointer`/`SkinIdentifier` do domen 1.18.2,",
        "- aliasy partow zachowane przez `SkinPartSerializerV13`.",
        "",
        "## Wyniki kontraktow",
        "",
    ]
    for key, value in contracts.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Pliki",
            "",
            "- `src/converters/armourers_workshop/simulations/step2_contract_simulations.py`",
            "- `src/converters/armourers_workshop/tests/test_step2_contract_simulations.py`",
            "- `src/converters/armourers_workshop/ARMOURERS_WORKSHOP_ZADANIE2_SIMULATION_RESULTS.json`",
            "",
            "## Zrodla z kodu",
            "",
        ]
    )
    for key, value in SOURCE_EVIDENCE.items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(
        [
            "",
            "## Znaczenie dla Zadania 3",
            "",
            "Konwerter nie powinien tylko kopiowac plikow `.armour`. Dla finalnego wyniku",
            "trzeba wczytac v13 przez serializer 1.18.2 i zapisac do latest v25, zachowujac",
            "relatywna sciezke biblioteki oraz aktualizujac referencje do `ws:<path>.armour`.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    results = run_simulations()
    write_report(results)
    print(json.dumps(results["contracts"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
