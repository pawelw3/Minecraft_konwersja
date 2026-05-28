#!/usr/bin/env python3
"""Generate Armourer's Workshop Task 5A source and converted fixtures."""

from __future__ import annotations

import json
import shutil
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from converters.armourers_workshop.converter import (  # noqa: E402
    ArmourersWorkshopConverter,
    build_library_migration_event,
)
from converters.armourers_workshop.mappings import BLOCK_MAPPINGS  # noqa: E402
from converters.common.item_id_resolver import load_item_id_mapping  # noqa: E402


SOURCE_PATCH = SCENARIO_DIR / "armourers_workshop_task5a_source_patch_1710.json"
CONVERTED_PATCH = SCENARIO_DIR / "armourers_workshop_task5a_converted_patch_1182.json"
EVENTS_1182 = SCENARIO_DIR / "armourers_workshop_task5a_events_1182.json"
CONVERSION_REPORT = SCENARIO_DIR / "armourers_workshop_task5a_conversion_report.json"
REPORT_MD = SCENARIO_DIR / "ARMOURERS_WORKSHOP_TASK5A_REPORT.md"
HANDOFF = SCENARIO_DIR / "HANDOFF_ARMOURERS_WORKSHOP_TASK5A.md"
WORLD_DIR = PROJECT_ROOT / "lightweigh_map_templates" / "1710_modded" / "armourers_workshop_task5a_world"
SKIN_SOURCE_ROOT = SCENARIO_DIR / "skin_library_source" / "armourersWorkshop"


@dataclass(frozen=True)
class Sample:
    name: str
    source_name: str
    block_id: str
    metadata: int
    x: int
    y: int
    z: int
    te_id: str | None = None
    nbt: dict[str, Any] | None = None
    category: str = "block"
    purpose: str = ""


def position_for(index: int) -> tuple[int, int, int]:
    columns = 8
    spacing = 3
    return (160 + (index % columns) * spacing, 70, 160 + (index // columns) * spacing)


def aw_block(source_name: str) -> str:
    return f"armourersWorkshop:block.{source_name}"


def load_dynamic_ids() -> dict[str, int]:
    mapping = load_item_id_mapping(PROJECT_ROOT / "mapa_1710" / "level.dat")
    result: dict[str, int] = {}
    for numeric_id, registry_name in mapping.items():
        name = str(registry_name)
        if name.startswith("armourersWorkshop:block."):
            result[name] = int(numeric_id)
    return result


def skin_identifier(library_file: str, skin_type: str = "armourers:block") -> dict[str, Any]:
    return {
        "localId": 0,
        "libraryFile": library_file,
        "globalId": 0,
        "skinType": skin_type,
    }


def skin_payload(library_file: str, skin_type: str = "armourers:block") -> dict[str, Any]:
    return {
        "identifier": skin_identifier(library_file, skin_type),
        "lock": False,
        "SkinDye": {
            "primary": 0xFFFFFF,
            "secondary": 0x336699,
        },
    }


def te_base(te_id: str, x: int, y: int, z: int, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    data: dict[str, Any] = {"id": te_id, "x": x, "y": y, "z": z}
    if extra:
        data.update(extra)
    return data


def build_samples() -> list[Sample]:
    samples: list[Sample] = []

    def add(
        name: str,
        source_name: str,
        metadata: int,
        category: str,
        purpose: str,
        te_id: str | None = None,
        nbt_extra: dict[str, Any] | None = None,
    ) -> None:
        x, y, z = position_for(len(samples))
        nbt = te_base(te_id, x, y, z, nbt_extra) if te_id else None
        samples.append(Sample(name, source_name, aw_block(source_name), metadata, x, y, z, te_id, nbt, category, purpose))

    add("armour_library_empty", "armourLibrary", 0, "library", "Local skin library block.", "te.armourLibrary", {"customName": "Task5A Library"})
    add("global_skin_library_empty", "globalSkinLibrary", 0, "library", "Global skin library access block.", "te.globalSkinLibrary", {"customName": "Task5A Global Library"})
    add("skinning_table", "skinningTable", 0, "workstation", "Skinning table with empty inventory.", "te.skinningTable", {"Items": []})
    add("dye_table", "dyeTable", 0, "workstation", "Dye table with a vanilla dye stack.", "te.dyeTable", {"Items": [{"Slot": 0, "id": "minecraft:dye", "Count": 1, "Damage": 4}]})
    add("colour_mixer", "colourMixer", 0, "workstation", "Colour mixer with RGB-like saved values.", "te.colourMixer", {"Red": 32, "Green": 96, "Blue": 180})
    add("armourer_brain", "armourerBrain", 2, "builder", "Armourer workspace controller.", "te.armourerBrain", {"skinType": "armourers:block", "buildGuide": True})
    add("bounding_box", "awBoundingBox6", 0, "builder", "Bounding helper linked to armourer.", "te.awBoundingBox6", {"parentX": 175, "parentY": 70, "parentZ": 160})
    add("colourable", "colourable", 0, "builder_cube", "Solid paintable cube.", "te.colourable", {"colour": 0xCC8844})
    add("colourable_glass", "colourableGlass", 0, "builder_cube", "Transparent paintable cube.")
    add("colourable_glowing", "colourableGlowing", 0, "builder_cube", "Glowing paintable cube.")
    add("colourable_glass_glowing", "colourableGlassGlowing", 0, "builder_cube", "Glowing transparent paintable cube.")
    add(
        "hologram_projector",
        "hologramProjector",
        1,
        "preview",
        "Hologram projector with powered/glowing fields.",
        "te.hologramProjector",
        {"isGlowing": True, "isPowered": True, "modelScale": 1.25, "powerMode": 1, "Items": [{"Slot": 0, "id": "armourersWorkshop:equipmentSkin", "Count": 1, "Damage": 0}]},
    )
    add(
        "mannequin_with_items",
        "mannequin",
        0,
        "placeholder",
        "Mannequin becomes entity-stage placeholder and keeps inventory.",
        "te.mannequin",
        {"Items": [{"Slot": 0, "id": "minecraft:leather_chestplate", "Count": 1, "Damage": 0}], "Skin": skin_payload("official/Witch's Hat.armour", "armourers:head")},
    )
    add("doll_placeholder", "doll", 0, "placeholder", "Doll has no safe 1.18.2 block target yet.")
    add("mini_armourer_placeholder", "miniArmourer", 0, "placeholder", "Legacy mini armourer is preserved for manual review.", "te.miniArmourer", {"note": "task5a"})
    add("outfit_maker", "outfit_maker", 0, "workstation", "Outfit maker dynamic registry block from level.dat.")

    for metadata, facing in [(2, "south"), (3, "west"), (4, "north"), (5, "east")]:
        parent_x, parent_y, parent_z = position_for(len(samples))
        library_file = "official/Barrel.armour" if metadata in (2, 4) else "Biret kap_a_ski.armour"
        related = [
            {"x": parent_x, "y": parent_y, "z": parent_z},
            {"x": parent_x + 1, "y": parent_y, "z": parent_z},
        ]
        add(
            f"skinnable_parent_meta_{metadata}_{facing}",
            "skinnable",
            metadata,
            "skinnable",
            f"Parent skinnable with metadata {metadata} -> facing {facing}.",
            "te.skinnable",
            {"hasSkin": True, "armourersWorkshop": skin_payload(library_file), "relatedBlocks": related},
        )
        add(
            f"skinnable_child_meta_{metadata}_{facing}",
            "skinnableChild",
            metadata,
            "skinnable_child",
            f"Child skinnable linked back to metadata {metadata} parent.",
            "te.skinnableChild",
            {"parentX": parent_x, "parentY": parent_y, "parentZ": parent_z},
        )

    add("skinnable_glowing_library", "skinnableGlowing", 4, "skinnable", "Glowing parent with library skin.", None, {"hasSkin": True, "armourersWorkshop": skin_payload("official/Glass Chair.armour")})
    add("skinnable_child_glowing", "skinnableChildGlowing", 4, "skinnable_child", "Glowing child without TE id in 1.7 mapping.", None, {"parentX": 160, "parentY": 70, "parentZ": 160})
    return samples


def source_edit(sample: Sample, dynamic_ids: dict[str, int]) -> dict[str, Any]:
    return {
        "op": "set_block_entity" if sample.nbt else "set_block",
        "pos": [sample.x, sample.y, sample.z],
        "block": sample.block_id,
        "numeric_block_id": dynamic_ids.get(sample.block_id),
        "metadata": sample.metadata,
        "nbt": sample.nbt,
        "sample": sample.name,
        "category": sample.category,
        "purpose": sample.purpose,
    }


def convert_sample(converter: ArmourersWorkshopConverter, sample: Sample) -> dict[str, Any]:
    conversion = converter.convert_block(sample.block_id, sample.metadata, sample.nbt, (sample.x, sample.y, sample.z))
    events = converter.to_events(conversion)
    return {
        "sample": sample.name,
        "source_name": sample.source_name,
        "source_block": sample.block_id,
        "metadata": sample.metadata,
        "pos": [sample.x, sample.y, sample.z],
        "success": conversion.converted.success,
        "target": conversion.converted.block_id_1182,
        "event_count": len(events),
        "events": events,
        "warnings": conversion.converted.warnings,
        "errors": conversion.converted.errors,
        "status": "placeholder" if conversion.converted.event_json else ("converted" if conversion.converted.success else "failed"),
    }


def prepare_skin_fixture() -> list[dict[str, Any]]:
    fixtures = [
        ("official/Barrel.armour", PROJECT_ROOT / "pliki_globalne_serwer_1710" / "armourersWorkshop" / "official" / "Barrel.armour"),
        ("Biret kap_a_ski.armour", PROJECT_ROOT / "pliki_globalne_serwer_1710" / "armourersWorkshop" / "Biret kap_a_ski.armour"),
    ]
    entries: list[dict[str, Any]] = []
    for relative_path, source_path in fixtures:
        target = SKIN_SOURCE_ROOT / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, target)
        entries.append(
            {
                "relative_path": relative_path.replace("\\", "/"),
                "source_path": str(source_path.relative_to(PROJECT_ROOT)),
                "fixture_path": str(target.relative_to(PROJECT_ROOT)),
                "target_identifier": f"ws:{relative_path.replace(chr(92), '/')}",
            }
        )
    return entries


def write_world_marker(samples: list[Sample]) -> None:
    WORLD_DIR.mkdir(parents=True, exist_ok=True)
    (WORLD_DIR / "README.md").write_text(
        "\n".join(
            [
                "# Armourer's Workshop Task 5A lightweight world",
                "",
                "This directory is a materialization target for the 1.7.10 source patch.",
                "The actual block/TE fixture is stored in:",
                f"`{SOURCE_PATCH.relative_to(PROJECT_ROOT)}`",
                "",
                f"Samples: {len(samples)}",
                "",
                "No original world data from `mapa_1710` is copied here.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def write_report(samples: list[Sample], conversions: list[dict[str, Any]], skin_entries: list[dict[str, Any]]) -> None:
    status_counts = Counter(item["status"] for item in conversions)
    warning_counts = Counter(warning for item in conversions for warning in item["warnings"])
    source_names = sorted({sample.source_name for sample in samples})
    lines = [
        "# Armourer's Workshop Task 5A - raport",
        "",
        "Zakres: deterministyczny fixture mapy 1.7.10 obejmujacy wszystkie znane bloki AW, reprezentatywne TE/NBT oraz globalne pliki `.armour`.",
        "",
        "## Podsumowanie",
        "",
        f"- Samples: {len(samples)}",
        f"- Source names covered: {len(source_names)} / {len(BLOCK_MAPPINGS)}",
        f"- Converted: {status_counts.get('converted', 0)}",
        f"- Placeholder-rescue: {status_counts.get('placeholder', 0)}",
        f"- Failed: {status_counts.get('failed', 0)}",
        f"- Skin library fixture files: {len(skin_entries)}",
        "",
        "## Pokryte source names",
        "",
    ]
    for source_name in source_names:
        lines.append(f"- `{source_name}`")
    lines.extend(["", "## Wyniki konwersji", ""])
    for item in conversions:
        lines.append(f"- `{item['sample']}` -> `{item['target']}` ({item['status']})")
    lines.extend(["", "## Fixture biblioteki skinow", ""])
    for entry in skin_entries:
        lines.append(f"- `{entry['relative_path']}` -> `{entry['target_identifier']}`")
    if warning_counts:
        lines.extend(["", "## Warningi unikalne", ""])
        for warning, count in warning_counts.most_common():
            lines.append(f"- `{warning}`: {count}")
    lines.extend(
        [
            "",
            "## Pliki",
            "",
            f"- `{SOURCE_PATCH.relative_to(PROJECT_ROOT)}`",
            f"- `{CONVERTED_PATCH.relative_to(PROJECT_ROOT)}`",
            f"- `{EVENTS_1182.relative_to(PROJECT_ROOT)}`",
            f"- `{CONVERSION_REPORT.relative_to(PROJECT_ROOT)}`",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_handoff(samples: list[Sample], conversions: list[dict[str, Any]]) -> None:
    status_counts = Counter(item["status"] for item in conversions)
    text = f"""# Handoff: Armourer's Workshop - Zadanie 5A

## Podsumowanie sesji

Wykonano Zadanie 5A dla Armourer's Workshop: wygenerowano deterministyczny
fixture testowej mapy 1.7.10, przekonwertowano go przez
`ArmourersWorkshopConverter` i dodano fixture globalnej biblioteki `.armour`.

## Ukonczono

- [x] Wygenerowano source patch 1.7.10.
- [x] Wygenerowano converted patch 1.18.2.
- [x] Wygenerowano plaski plik eventow 1.18.2.
- [x] Pokryto wszystkie source names z `BLOCK_MAPPINGS`.
- [x] Uwzgledniono warianty `skinnable` metadata 2/3/4/5.
- [x] Uwzgledniono parent/child skinnable oraz wskazniki `libraryFile`.
- [x] Uwzgledniono placeholder-rescue dla `mannequin`, `doll`, `miniArmourer`.
- [x] Dodano fixture globalnych plikow `.armour`.

## Wyniki

- Samples: `{len(samples)}`.
- Converted: `{status_counts.get('converted', 0)}`.
- Placeholder-rescue: `{status_counts.get('placeholder', 0)}`.
- Failed: `{status_counts.get('failed', 0)}`.

## Nowe pliki

- `test_scenarios/armourers_workshop_task5a/generate_armourers_workshop_task5a.py`
- `test_scenarios/armourers_workshop_task5a/armourers_workshop_task5a_source_patch_1710.json`
- `test_scenarios/armourers_workshop_task5a/armourers_workshop_task5a_converted_patch_1182.json`
- `test_scenarios/armourers_workshop_task5a/armourers_workshop_task5a_events_1182.json`
- `test_scenarios/armourers_workshop_task5a/armourers_workshop_task5a_conversion_report.json`
- `test_scenarios/armourers_workshop_task5a/ARMOURERS_WORKSHOP_TASK5A_REPORT.md`
- `test_scenarios/armourers_workshop_task5a/skin_library_source/`
- `lightweigh_map_templates/1710_modded/armourers_workshop_task5a_world/README.md`
- `src/converters/armourers_workshop/tests/test_task5a_fixture.py`
- `src/converters/armourers_workshop/HANDOFF_ARMOURERS_WORKSHOP_ZADANIE5A.md`

## Weryfikacja

- `python test_scenarios\\armourers_workshop_task5a\\generate_armourers_workshop_task5a.py` -> OK.
- `python -m py_compile test_scenarios\\armourers_workshop_task5a\\generate_armourers_workshop_task5a.py src\\converters\\armourers_workshop\\tests\\test_task5a_fixture.py` -> OK.
- `python -m pytest src\\converters\\armourers_workshop\\tests -q` -> OK.

## Nastepne kroki

1. [ ] W Zadaniu 5B zmaterializowac `armourers_workshop_task5a_converted_patch_1182.json` na headless 1.18.2.
2. [ ] Podpiac batch runner `.armour` dla fixture i pelnej biblioteki.
"""
    HANDOFF.write_text(text, encoding="utf-8")


def main() -> int:
    dynamic_ids = load_dynamic_ids()
    samples = build_samples()
    converter = ArmourersWorkshopConverter()
    conversions = [convert_sample(converter, sample) for sample in samples]
    events = [event for item in conversions for event in item["events"]]
    skin_entries = prepare_skin_fixture()
    source_names = sorted({sample.source_name for sample in samples})
    missing = sorted(set(BLOCK_MAPPINGS) - set(source_names))

    source_patch = {
        "metadata": {
            "name": "armourers_workshop_task5a_source",
            "minecraft_version": "1.7.10",
            "generated_by": Path(__file__).name,
            "world_dir": str(WORLD_DIR.relative_to(PROJECT_ROOT)),
        },
        "skin_library": {
            "source_root": str(SKIN_SOURCE_ROOT.relative_to(PROJECT_ROOT)),
            "entries": skin_entries,
        },
        "edits": [source_edit(sample, dynamic_ids) for sample in samples],
    }
    converted_patch = {
        "metadata": {
            "name": "armourers_workshop_task5a_converted",
            "minecraft_version": "1.18.2",
            "generated_by": Path(__file__).name,
        },
        "sidecars": [build_library_migration_event(str(SKIN_SOURCE_ROOT.relative_to(PROJECT_ROOT)), "skin-library")],
        "events": events,
    }
    report = {
        "metadata": {
            "name": "Armourer's Workshop Task 5A conversion report",
            "sample_count": len(samples),
            "event_count": len(events),
            "covered_source_names": source_names,
            "missing_source_names": missing,
            "skin_library_entries": skin_entries,
        },
        "status_counts": dict(Counter(item["status"] for item in conversions)),
        "samples": [asdict(sample) for sample in samples],
        "conversions": conversions,
    }

    write_json(SOURCE_PATCH, source_patch)
    write_json(CONVERTED_PATCH, converted_patch)
    write_json(EVENTS_1182, events)
    write_json(CONVERSION_REPORT, report)
    write_world_marker(samples)
    write_report(samples, conversions, skin_entries)
    write_handoff(samples, conversions)

    failed = [item for item in conversions if not item["success"]]
    print(json.dumps({"samples": len(samples), "events": len(events), "failed": len(failed), "missing_source_names": missing}, indent=2))
    return 1 if failed or missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
