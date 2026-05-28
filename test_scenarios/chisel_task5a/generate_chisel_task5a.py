#!/usr/bin/env python3
"""Generate Chisel Task 5A source and converted patches.

The scenario covers every Chisel block family discovered in the dynamic
1.7.10 registry and every block/meta variant observed during Task 4 coverage.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
COVERAGE_JSON = PROJECT_ROOT / "output" / "chisel_coverage" / "chisel_coverage_report.json"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.converters.chisel.chisel_converter import ChiselConverter  # noqa: E402
from src.converters.chisel.mappings import DynamicChiselIdEntry, normalize_family  # noqa: E402


SOURCE_PATCH = SCENARIO_DIR / "chisel_task5a_source_patch_1710.json"
CONVERTED_PATCH = SCENARIO_DIR / "chisel_task5a_converted_patch_1182.json"
EVENTS_JSON = SCENARIO_DIR / "chisel_task5a_events_1182.json"
CONVERSION_REPORT = SCENARIO_DIR / "chisel_task5a_conversion_report.json"
REPORT_MD = SCENARIO_DIR / "CHISEL_TASK5A_REPORT.md"
HANDOFF = SCENARIO_DIR / "HANDOFF.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def registry_from_coverage(coverage: dict[str, Any]) -> dict[int, str]:
    return {int(k): str(v) for k, v in coverage["numeric_block_registry"].items()}


def dynamic_map_from_registry(registry: dict[int, str]) -> dict[int, DynamicChiselIdEntry]:
    result: dict[int, DynamicChiselIdEntry] = {}
    for numeric_id, registry_name in registry.items():
        path = registry_name.split(":", 1)[1]
        family = path.rsplit(".", 1)[0] if "." in path else path
        result[numeric_id] = DynamicChiselIdEntry(numeric_id=numeric_id, family=normalize_family(family))
    return result


def split_block_meta(key: str) -> tuple[str, int]:
    block_name, metadata = key.rsplit(":", 1)
    return block_name, int(metadata)


def item_stack(item_id: str, count: int = 1, slot: int = 0, damage: int = 0) -> dict[str, Any]:
    stack: dict[str, Any] = {"id": item_id, "Count": count, "Slot": slot}
    if damage:
        stack["Damage"] = damage
    return stack


def position_for(index: int) -> tuple[int, int, int]:
    columns = 32
    spacing = 2
    return (100 + (index % columns) * spacing, 64, 100 + (index // columns) * spacing)


def make_samples(coverage: dict[str, Any]) -> list[dict[str, Any]]:
    registry = registry_from_coverage(coverage)
    name_to_id = {name.lower(): numeric_id for numeric_id, name in registry.items()}
    samples: list[dict[str, Any]] = []
    seen: set[tuple[int, int, str | None]] = set()

    def add(
        *,
        name: str,
        block_name: str,
        metadata: int,
        category: str,
        observed_count: int = 0,
        te_id: str | None = None,
        nbt_extra: dict[str, Any] | None = None,
    ) -> None:
        numeric_id = name_to_id.get(block_name.lower())
        if numeric_id is None:
            return
        key = (numeric_id, metadata, te_id)
        if key in seen:
            return
        seen.add(key)
        x, y, z = position_for(len(samples))
        nbt = None
        if te_id:
            nbt = {"id": te_id, "x": x, "y": y, "z": z}
            if nbt_extra:
                nbt.update(nbt_extra)
        samples.append(
            {
                "name": name,
                "category": category,
                "block_name": block_name,
                "block_id": numeric_id,
                "metadata": metadata,
                "x": x,
                "y": y,
                "z": z,
                "te_id": te_id,
                "nbt": nbt,
                "observed_count": observed_count,
            }
        )

    block_counts = coverage.get("block_counts", {})
    for key, count in sorted(block_counts.items(), key=lambda item: int(item[1]), reverse=True):
        block_name, metadata = split_block_meta(key)
        add(
            name=f"observed_{block_name.replace(':', '_')}_{metadata}",
            block_name=block_name,
            metadata=metadata,
            category="observed_block_meta",
            observed_count=int(count),
        )

    observed_names = {split_block_meta(key)[0].lower() for key in block_counts}
    for numeric_id, registry_name in sorted(registry.items()):
        if registry_name.lower() in observed_names:
            continue
        add(
            name=f"registry_{numeric_id}_{registry_name.replace(':', '_')}",
            block_name=registry_name,
            metadata=0,
            category="registry_meta0_unobserved",
        )

    add(
        name="te_auto_chisel_empty",
        block_name="chisel:autoChisel",
        metadata=0,
        category="tile_entity",
        te_id="autoChisel",
        nbt_extra={"Items": [], "progress": 0, "energy": 0},
    )
    add(
        name="te_auto_chisel_with_items_and_progress",
        block_name="chisel:autoChisel",
        metadata=0,
        category="tile_entity",
        te_id="TileEntityAutoChisel",
        nbt_extra={
            "Items": [
                item_stack("chisel:marble", 16, slot=0),
                item_stack("chisel:limestone", 8, slot=1),
                item_stack("minecraft:diamond", 1, slot=2),
            ],
            "progress": 768,
            "energy": 12000,
            "target": {"id": "chisel:marble", "Damage": 1, "Count": 1},
        },
    )
    add(
        name="te_present_legacy_alias_with_inventory",
        block_name="chisel:present",
        metadata=0,
        category="tile_entity",
        te_id="tile.chisel.present",
        nbt_extra={"Items": [item_stack("minecraft:emerald", 3, slot=0)], "owner": "task5a"},
    )
    add(
        name="te_carvable_beacon",
        block_name="chisel:beacon",
        metadata=0,
        category="tile_entity",
        te_id="TileEntityCarvableBeacon",
        nbt_extra={"Primary": 1, "Secondary": 0, "Levels": 4},
    )
    return samples


def build_source_patch(samples: list[dict[str, Any]]) -> dict[str, Any]:
    edits: list[dict[str, Any]] = []
    for sample in samples:
        edits.append(
            {
                "op": "set_block",
                "x": sample["x"],
                "y": sample["y"],
                "z": sample["z"],
                "id": sample["block_id"],
                "meta": sample["metadata"],
                "registry_name": sample["block_name"],
                "label": sample["name"],
                "category": sample["category"],
            }
        )
        if sample["nbt"]:
            edits.append(
                {
                    "op": "set_te",
                    "x": sample["x"],
                    "y": sample["y"],
                    "z": sample["z"],
                    "nbt": sample["nbt"],
                    "label": sample["name"],
                    "category": sample["category"],
                }
            )
    return {
        "format_version": "1.7.10",
        "metadata": {
            "name": "chisel_task5a_source",
            "generated_by": "generate_chisel_task5a.py",
            "coverage_source": str(COVERAGE_JSON.relative_to(PROJECT_ROOT)),
            "samples": len(samples),
        },
        "edits": edits,
    }


def convert_samples(samples: list[dict[str, Any]], registry: dict[int, str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    converter = ChiselConverter(dynamic_id_map=dynamic_map_from_registry(registry))
    events: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    warning_counts: Counter[str] = Counter()
    target_counts: Counter[str] = Counter()

    for sample in samples:
        pos = (sample["x"], sample["y"], sample["z"])
        result = converter.convert_block(
            sample["block_id"],
            metadata=sample["metadata"],
            nbt_1710=sample["nbt"],
            position=pos,
        )
        sample_events = converter.to_events(result)
        events.extend(sample_events)
        target = result.converted.block_id_1182
        if target:
            target_counts[target] += 1
        warning_counts.update(result.converted.warnings)
        results.append(
            {
                "sample": sample["name"],
                "category": sample["category"],
                "source_block": sample["block_name"],
                "source_numeric_id": sample["block_id"],
                "metadata": sample["metadata"],
                "position": list(pos),
                "source_te_id": sample["te_id"],
                "observed_count": sample["observed_count"],
                "success": result.converted.success,
                "target_block": target,
                "event_count": len(sample_events),
                "warnings": result.converted.warnings,
                "errors": result.converted.errors,
            }
        )

    report = {
        "name": "Chisel Task 5A conversion report",
        "samples": len(samples),
        "events": len(events),
        "successful_samples": sum(1 for item in results if item["success"]),
        "failed_samples": sum(1 for item in results if not item["success"]),
        "placeholder_events": sum(1 for event in events if event.get("op") == "set_block_entity"),
        "target_counts": dict(target_counts.most_common()),
        "warning_counts": dict(warning_counts.most_common()),
        "converter_stats": converter.get_stats(),
        "results": results,
    }
    return events, results, report


def write_report_md(samples: list[dict[str, Any]], report: dict[str, Any]) -> None:
    top_targets = list(report["target_counts"].items())[:12]
    lines = [
        "# Chisel Task 5A - raport",
        "",
        "## Podsumowanie",
        "",
        "Zadanie 5A wygenerowalo testowy patch 1.7.10 i przekonwertowalo go do eventow 1.18.2.",
        "Scenariusz obejmuje wszystkie dynamiczne rodziny Chisela z `level.dat` oraz wszystkie realnie zaobserwowane warianty `block/meta` z raportu Zadania 4.",
        "",
        f"- Probki: {report['samples']}",
        f"- Eventy 1.18.2: {report['events']}",
        f"- Sukcesy: {report['successful_samples']}",
        f"- Bledy: {report['failed_samples']}",
        f"- Placeholdery TE: {report['placeholder_events']}",
        "",
        "## Zakres probek",
        "",
        f"- `observed_block_meta`: {sum(1 for s in samples if s['category'] == 'observed_block_meta')}",
        f"- `registry_meta0_unobserved`: {sum(1 for s in samples if s['category'] == 'registry_meta0_unobserved')}",
        f"- `tile_entity`: {sum(1 for s in samples if s['category'] == 'tile_entity')}",
        "",
        "## Najczestsze targety w scenariuszu",
        "",
    ]
    for target, count in top_targets:
        lines.append(f"- `{target}`: {count}")
    lines.extend(
        [
            "",
            "## Pliki",
            "",
            "- `chisel_task5a_source_patch_1710.json` - patch zrodlowy 1.7.10.",
            "- `chisel_task5a_converted_patch_1182.json` - patch docelowy 1.18.2.",
            "- `chisel_task5a_events_1182.json` - surowe eventy konwertera.",
            "- `chisel_task5a_conversion_report.json` - pelny raport per probka.",
            "",
            "## Wnioski",
            "",
            "Konwersja technicznie pokrywa caly scenariusz 5A. Nadal zostaje znane ryzyko wizualne: czesc rodzin bez dokladnego odpowiednika trafia do fallbackow Rechiseled/Chipped albo vanilla.",
            "Nastepny etap powinien materializowac patch na 1.18.2 i zweryfikowac wizualnie najczestsze rodziny: marble, limestone, concrete, stonebricksmooth, factoryblock i technical2.",
            "",
        ]
    )
    write_text(REPORT_MD, "\n".join(lines))


def write_handoff(report: dict[str, Any]) -> None:
    text = f"""# Handoff: Chisel - Zadanie 5A

## Podsumowanie sesji

Wykonano Zadanie 5A dla Chisel: wygenerowano testowy patch 1.7.10 obejmujacy dynamiczne rodziny i realne warianty `block/meta`, a nastepnie przekonwertowano go przez `ChiselConverter` do eventow 1.18.2.

## Ukonczono

- [x] Dodano generator `test_scenarios/chisel_task5a/generate_chisel_task5a.py`.
- [x] Wygenerowano source patch 1.7.10.
- [x] Wygenerowano converted patch i eventy 1.18.2.
- [x] Dodano probki TE: Auto Chisel, legacy Present alias i Carvable Beacon.
- [x] Rozszerzono detekcje TE Chisel o legacy alias `tile.chisel.present`.
- [x] Uruchomiono testy Chisela.

## Wyniki

- Probki: {report['samples']}.
- Eventy 1.18.2: {report['events']}.
- Sukcesy: {report['successful_samples']}.
- Bledy: {report['failed_samples']}.
- Placeholdery TE: {report['placeholder_events']}.

## Nowe pliki

- `test_scenarios/chisel_task5a/generate_chisel_task5a.py`
- `test_scenarios/chisel_task5a/chisel_task5a_source_patch_1710.json`
- `test_scenarios/chisel_task5a/chisel_task5a_converted_patch_1182.json`
- `test_scenarios/chisel_task5a/chisel_task5a_events_1182.json`
- `test_scenarios/chisel_task5a/chisel_task5a_conversion_report.json`
- `test_scenarios/chisel_task5a/CHISEL_TASK5A_REPORT.md`

## Zmodyfikowane pliki

- `src/converters/chisel/mappings.py`
- `src/converters/chisel/tests/test_chisel_converter.py`
- `src/converters/router.py`

## Nastepne kroki

1. [ ] Zadanie 5B: zmaterializowac `chisel_task5a_converted_patch_1182.json` na headless 1.18.2 przez datapack albo worker.
2. [ ] Wykonac wizualna weryfikacje topowych rodzin dekoracyjnych.
3. [ ] Po weryfikacji poprawic fallbacki dla rodzin trafiajacych do `minecraft:stone` lub zbyt ogolnych blokow quartz.
"""
    write_text(HANDOFF, text)


def main() -> None:
    if not COVERAGE_JSON.exists():
        raise FileNotFoundError(f"Missing coverage report: {COVERAGE_JSON}")
    coverage = load_json(COVERAGE_JSON)
    registry = registry_from_coverage(coverage)
    samples = make_samples(coverage)
    source_patch = build_source_patch(samples)
    events, _results, report = convert_samples(samples, registry)
    converted_patch = {
        "format_version": "1.18.2",
        "metadata": {
            "name": "chisel_task5a_converted",
            "generated_by": "generate_chisel_task5a.py",
            "source_patch": SOURCE_PATCH.name,
        },
        "edits": events,
    }

    write_json(SOURCE_PATCH, source_patch)
    write_json(EVENTS_JSON, {"format_version": "1.18.2", "events": events})
    write_json(CONVERTED_PATCH, converted_patch)
    write_json(CONVERSION_REPORT, report)
    write_report_md(samples, report)
    write_handoff(report)

    print(f"Samples: {report['samples']}")
    print(f"Events: {report['events']}")
    print(f"Success: {report['successful_samples']} failed: {report['failed_samples']}")
    print(f"Placeholder events: {report['placeholder_events']}")
    print(f"Wrote: {CONVERTED_PATCH}")


if __name__ == "__main__":
    main()
