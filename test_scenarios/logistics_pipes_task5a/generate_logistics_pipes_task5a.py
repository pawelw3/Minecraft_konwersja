#!/usr/bin/env python3
"""Generate Logistics Pipes Task 5A fixture and conversion report.

This is a lightweight Task 5A variant: it does not materialize an MCA world.
Instead, it builds representative 1.7.10 TileEntity NBT samples and runs them
through the real converter/router path used by map scans.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
SOURCE_FIXTURE = SCENARIO_DIR / "logistics_pipes_task5a_source_fixture_1710.json"
OUT_PATCH = SCENARIO_DIR / "logistics_pipes_task5a_converted_patch_1182.json"
OUT_EVENTS = SCENARIO_DIR / "logistics_pipes_task5a_events_1182.json"
OUT_VALIDATION = SCENARIO_DIR / "logistics_pipes_task5a_validation.json"
OUT_REPORT = SCENARIO_DIR / "LOGISTICS_PIPES_TASK5A_REPORT.md"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from converters.router import convert_te_to_events  # noqa: E402


GENERIC_PIPE_TE = "logisticspipes.pipes.basic.LogisticsTileGenericPipe"
CRAFTING_TABLE_TE = "logisticspipes.blocks.crafting.LogisticsCraftingTableTileEntity"
POWER_JUNCTION_TE = "logisticspipes.blocks.powertile.LogisticsPowerJuntionTileEntity"
SECURITY_TE = "logisticspipes.blocks.LogisticsSecurityTileEntity"


@dataclass(frozen=True)
class Sample:
    name: str
    metadata: int
    position: tuple[int, int, int]
    te_nbt: dict[str, Any]
    expected_block: str
    expected_warning_codes: tuple[str, ...] = ()
    purpose: str = ""

    @property
    def te_id(self) -> str:
        return str(self.te_nbt["id"])


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def warning_code(warning: str) -> str:
    return warning.split(":", 1)[0].strip()


def pipe_nbt(pipe_id: int, x: int, y: int, z: int, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    nbt: dict[str, Any] = {
        "id": GENERIC_PIPE_TE,
        "x": x,
        "y": y,
        "z": z,
        "pipeId": pipe_id,
        "block_id": "LogisticsPipes:logisticsPipeBlock",
    }
    if extra:
        nbt.update(extra)
    return nbt


def build_samples() -> list[Sample]:
    base_x, base_y, base_z = 48, 70, 48

    def pos(dx: int, dz: int) -> tuple[int, int, int]:
        return (base_x + dx, base_y, base_z + dz)

    samples: list[Sample] = []

    def add_pipe(
        name: str,
        pipe_id: int,
        dx: int,
        dz: int,
        expected_block: str,
        expected_warning_codes: tuple[str, ...] = (),
        extra: dict[str, Any] | None = None,
        purpose: str = "",
    ) -> None:
        x, y, z = pos(dx, dz)
        samples.append(
            Sample(
                name=name,
                metadata=0,
                position=(x, y, z),
                te_nbt=pipe_nbt(pipe_id, x, y, z, extra),
                expected_block=expected_block,
                expected_warning_codes=expected_warning_codes,
                purpose=purpose,
            )
        )

    add_pipe(
        "basic_transport_pipeid_8780",
        8780,
        0,
        0,
        "prettypipes:pipe",
        purpose="Real map majority case: transport-only pipe resolved from pipeId.",
    )
    add_pipe(
        "basic_logistics_pipeid_8749",
        8749,
        1,
        0,
        "prettypipes:pipe",
        purpose="Simple routed Logistics Pipe with no special modules.",
    )
    add_pipe(
        "supplier_pipeid_8754",
        8754,
        2,
        0,
        "prettypipes:pipe",
        ("LP-W-SUPPLIER-STOCK-TARGET",),
        purpose="Supplier pipe keeps stock-target warning.",
    )
    add_pipe(
        "provider_mk2_pipeid_8763",
        8763,
        3,
        0,
        "prettypipes:pipe",
        purpose="Provider Mk2 emits Pretty Pipes extraction module.",
    )
    add_pipe(
        "chassis_mk4_with_modules",
        8758,
        4,
        0,
        "prettypipes:pipe",
        ("LP-W-CHASSIS-OVERFLOW",),
        {
            "chassi": [
                {"moduleClass": "ModuleProvider"},
                {"moduleClass": "ModuleActiveSupplier"},
                {"moduleClass": "ModuleCrafter"},
                {"moduleClass": "ModulePassiveSupplier"},
            ]
        },
        "Mk4 has four LP slots, while Pretty Pipes stores three module items.",
    )
    add_pipe(
        "chassis_mk4_unknown_modules",
        8758,
        5,
        0,
        "prettypipes:pipe",
        ("LP-W-CHASSIS-MODULES-UNKNOWN",),
        purpose="Mirrors real map chassis cases where module inventory was not extracted.",
    )
    add_pipe(
        "request_pipeid_8750",
        8750,
        6,
        0,
        "prettypipes:item_terminal",
        ("LP-W-REQUEST-TERMINAL",),
        purpose="Request pipe becomes Pretty Pipes terminal role.",
    )
    add_pipe(
        "request_table_pipeid_8779",
        8779,
        7,
        0,
        "prettypipes:item_terminal",
        ("LP-W-REQUEST-TABLE",),
        purpose="Request table pipe from real map becomes terminal role.",
    )
    add_pipe(
        "remote_orderer_pipeid_8762",
        8762,
        8,
        0,
        "prettypipes:item_terminal",
        ("LP-W-REMOTE-ORDERER",),
        purpose="Remote orderer has only a local terminal fallback.",
    )

    x, y, z = pos(0, 2)
    samples.append(
        Sample(
            name="crafting_table_basic",
            metadata=3,
            position=(x, y, z),
            te_nbt={
                "id": CRAFTING_TABLE_TE,
                "x": x,
                "y": y,
                "z": z,
                "block_id": "LogisticsPipes:logisticsSolidBlock",
                "craftingGrid": [{"Slot": 0, "id": "minecraft:iron_ingot", "Count": 1}],
                "resultInv": [{"Slot": 0, "id": "minecraft:iron_block", "Count": 1}],
            },
            expected_block="ae2:pattern_provider",
            expected_warning_codes=("LP-W-CRAFTING-TABLE",),
            purpose="Crafting table becomes AE2 pattern provider shell.",
        )
    )

    x, y, z = pos(1, 2)
    samples.append(
        Sample(
            name="crafting_table_fuzzy",
            metadata=4,
            position=(x, y, z),
            te_nbt={
                "id": CRAFTING_TABLE_TE,
                "x": x,
                "y": y,
                "z": z,
                "block_id": "LogisticsPipes:logisticsSolidBlock",
                "fuzzy": True,
            },
            expected_block="ae2:pattern_provider",
            expected_warning_codes=("LP-W-CRAFTING-TABLE", "LP-W-FUZZY-CRAFTING"),
            purpose="Fuzzy crafting must remain visible for manual rebuild.",
        )
    )

    x, y, z = pos(2, 2)
    samples.append(
        Sample(
            name="power_junction",
            metadata=1,
            position=(x, y, z),
            te_nbt={
                "id": POWER_JUNCTION_TE,
                "x": x,
                "y": y,
                "z": z,
                "block_id": "LogisticsPipes:logisticsSolidBlock",
                "energy": 12500,
            },
            expected_block="prettypipes:pressurizer",
            expected_warning_codes=("LP-W-POWER-NOT-LOSSLESS", "LP-W-PRESSURIZER-RECOMMENDED"),
            purpose="Power junction becomes pressurizer shell with non-lossless energy warning.",
        )
    )

    x, y, z = pos(3, 2)
    samples.append(
        Sample(
            name="security_station_placeholder",
            metadata=2,
            position=(x, y, z),
            te_nbt={
                "id": SECURITY_TE,
                "x": x,
                "y": y,
                "z": z,
                "block_id": "LogisticsPipes:logisticsSolidBlock",
                "owner": "legacy-owner",
            },
            expected_block="conversion_placeholders:block_entity_placeholder",
            expected_warning_codes=("LP-W-SECURITY-NO-TARGET",),
            purpose="Unsupported LP security state is retained as placeholder.",
        )
    )

    return samples


def convert_samples(samples: list[Sample]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    event_records: list[dict[str, Any]] = []
    validations: list[dict[str, Any]] = []

    for sample in samples:
        events = convert_te_to_events(
            te_nbt=sample.te_nbt,
            block_numeric_id=0,
            metadata=sample.metadata,
            global_pos=sample.position,
        )
        first_event = events[0] if events else {}
        warnings = (first_event.get("nbt") or {}).get("conversion_source", {}).get("warnings", [])
        if not warnings:
            warnings = first_event.get("warnings", [])
        event_warnings = list(warnings)

        # Router events currently keep warnings in the converter's event dict only
        # when serialising through ConversionEvent, so also inspect target NBT.
        event_codes = {warning_code(w) for w in collect_warning_strings(first_event)}
        target_block = str(first_event.get("block", ""))
        missing_codes = sorted(code for code in sample.expected_warning_codes if code not in event_codes)
        status = "ok" if target_block == sample.expected_block and not missing_codes else "error"

        event_records.append(
            {
                "sample": sample.name,
                "purpose": sample.purpose,
                "source": {
                    "te_id": sample.te_id,
                    "metadata": sample.metadata,
                    "position": list(sample.position),
                    "nbt": sample.te_nbt,
                },
                "events": events,
            }
        )
        validations.append(
            {
                "name": sample.name,
                "status": status,
                "expected_block": sample.expected_block,
                "actual_block": target_block,
                "expected_warning_codes": list(sample.expected_warning_codes),
                "actual_warning_codes": sorted(event_codes),
                "missing_warning_codes": missing_codes,
                "event_count": len(events),
                "event_warnings_seen": event_warnings,
            }
        )

    return event_records, validations


def flatten_events(event_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    edits: list[dict[str, Any]] = []
    for record in event_records:
        sample = record["sample"]
        for event in record.get("events", []):
            edit = dict(event)
            edit["sample"] = sample
            edits.append(edit)
    return edits


def collect_warning_strings(event: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    for value in walk_values(event):
        if isinstance(value, str) and value.startswith("LP-W-"):
            warnings.append(value)
    return warnings


def walk_values(value: Any):
    if isinstance(value, dict):
        for inner in value.values():
            yield from walk_values(inner)
    elif isinstance(value, list):
        for inner in value:
            yield from walk_values(inner)
    else:
        yield value


def source_fixture(samples: list[Sample]) -> dict[str, Any]:
    return {
        "mod": "Logistics Pipes",
        "task": "5A",
        "type": "lightweight_nbt_fixture",
        "source_version": "1.7.10",
        "target_version": "1.18.2",
        "note": "Fixture uses representative TE NBT instead of materialized MCA world.",
        "samples": [
            {
                "name": sample.name,
                "purpose": sample.purpose,
                "metadata": sample.metadata,
                "position": list(sample.position),
                "te_id": sample.te_id,
                "expected_block": sample.expected_block,
                "expected_warning_codes": list(sample.expected_warning_codes),
                "nbt": sample.te_nbt,
            }
            for sample in samples
        ],
    }


def write_markdown_report(samples: list[Sample], validations: list[dict[str, Any]]) -> None:
    passed = sum(1 for row in validations if row["status"] == "ok")
    total = len(validations)
    by_target: dict[str, int] = {}
    for row in validations:
        by_target[row["actual_block"]] = by_target.get(row["actual_block"], 0) + 1

    lines = [
        "# Logistics Pipes Task 5A Report",
        "",
        "## Podsumowanie",
        f"Utworzono lekki fixture NBT dla Logistics Pipes zamiast materializowanej mapy MCA. Walidacja przeszla {passed}/{total} probek.",
        "",
        "## Zakres fixture",
        "- Realne `pipeId` z `mapa_1710/level.dat`: `8749`, `8750`, `8754`, `8758`, `8762`, `8763`, `8779`, `8780`.",
        "- Solid TileEntities: crafting table, fuzzy crafting table, power junction, security station placeholder.",
        "- Scenariusz nie modyfikuje `mapa_1710/`.",
        "",
        "## Targety",
    ]
    for target, count in sorted(by_target.items()):
        lines.append(f"- `{target}`: {count}")

    lines.extend(
        [
            "",
            "## Wyniki probek",
            "| Status | Probka | Target | Warningi |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in validations:
        warnings = ", ".join(f"`{code}`" for code in row["actual_warning_codes"]) or "-"
        lines.append(f"| `{row['status']}` | `{row['name']}` | `{row['actual_block']}` | {warnings} |")

    lines.extend(
        [
            "",
            "## Pliki",
            f"- `{SOURCE_FIXTURE.relative_to(PROJECT_ROOT)}`",
            f"- `{OUT_PATCH.relative_to(PROJECT_ROOT)}`",
            f"- `{OUT_EVENTS.relative_to(PROJECT_ROOT)}`",
            f"- `{OUT_VALIDATION.relative_to(PROJECT_ROOT)}`",
            "",
            "## Nastepny krok",
            "1. [ ] Zadanie 5B: zmaterializowac ten fixture na swiecie 1.18.2/headless albo przygotowac writer MCA, gdy dostepne bedzie narzedzie sekcji.",
        ]
    )
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    samples = build_samples()
    event_records, validations = convert_samples(samples)
    edits = flatten_events(event_records)
    write_json(SOURCE_FIXTURE, source_fixture(samples))
    write_json(OUT_PATCH, {"edits": edits})
    write_json(OUT_EVENTS, {"events": event_records})
    write_json(
        OUT_VALIDATION,
        {
            "mod": "Logistics Pipes",
            "task": "5A",
            "total_samples": len(samples),
            "passed": sum(1 for row in validations if row["status"] == "ok"),
            "failed": sum(1 for row in validations if row["status"] != "ok"),
            "results": validations,
        },
    )
    write_markdown_report(samples, validations)
    print(f"Generated {len(samples)} Logistics Pipes samples")
    print(f"Validation: {sum(1 for row in validations if row['status'] == 'ok')}/{len(validations)} passed")
    print(f"Report: {OUT_REPORT}")


if __name__ == "__main__":
    main()
