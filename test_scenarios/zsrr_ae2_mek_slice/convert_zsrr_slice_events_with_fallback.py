#!/usr/bin/env python3
"""Generate target 1.18.2 Event JSON for the ZSRR AE2/Mekanism slice.

Supported conversions are delegated to the current AE2 and Mekanism
converters. Every unsupported BlockEntity is converted into
conversion_placeholders:block_entity_placeholder so its original NBT remains
recoverable from the target world.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
DEFAULT_WORLD = PROJECT_ROOT / "lightweigh_map_templates" / "1710_modded" / "zsrr_ae2_mek_300"
DEFAULT_EVENTS = SCENARIO_DIR / "zsrr_ae2_mek_slice_events_1182.json"
DEFAULT_REPORT = SCENARIO_DIR / "zsrr_ae2_mek_slice_events_report.json"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from minecraft_map_parser.anvil_parser import AnvilParser  # noqa: E402
from src.converters.ae2.ae2_converter import AE2Converter  # noqa: E402
from src.converters.ae2.analyze_ae2_fixed import is_ae2_tile_entity  # noqa: E402
from src.converters.common.placeholders import (  # noqa: E402
    make_block_entity_placeholder_event,
    summarize_placeholder_events,
)
from src.converters.mekanism import MekanismConverter  # noqa: E402
from src.converters.mekanism.analyze_map_coverage import (  # noqa: E402
    get_block_at,
    load_block_registry,
    nbt_to_python,
)
from src.converters.mekanism.mappings import TE_ID_TO_MAPPING_KEY  # noqa: E402


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sanitize_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): sanitize_json(inner) for key, inner in value.items()}
    if isinstance(value, (list, tuple)):
        return [sanitize_json(item) for item in value]
    if isinstance(value, bytes):
        return [int(item) for item in value]
    if isinstance(value, bytearray):
        return [int(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def source_mod_for(te_id: str, block_id: str | None) -> str:
    block_prefix = (block_id or "").split(":", 1)[0].lower()
    if block_prefix == "appliedenergistics2" or is_ae2_tile_entity(te_id):
        return "AE2"
    if block_prefix == "mekanism" or te_id in TE_ID_TO_MAPPING_KEY:
        return "Mekanism"
    if block_prefix:
        return block_prefix
    return "unknown"


def is_mekanism_tile_entity(te_id: str, block_id: str | None) -> bool:
    return te_id in TE_ID_TO_MAPPING_KEY or (block_id or "").lower().startswith("mekanism:")


def event_from_conversion(conversion: Any, source: dict[str, Any]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    converted = conversion.converted
    if not converted.success or not converted.block_id_1182:
        return events

    x, y, z = conversion.original_pos
    base = {
        "op": "set_block_entity" if converted.nbt_1182 is not None else "set_block",
        "pos": [int(x), int(y), int(z)],
        "block": converted.block_id_1182,
        "blockstate": sanitize_json(converted.blockstate_props or {}),
        "source": source,
    }
    if converted.nbt_1182 is not None:
        nbt = sanitize_json(converted.nbt_1182)
        nbt.setdefault("id", converted.block_id_1182)
        base["nbt"] = nbt
    events.append(base)

    for extra in getattr(converted, "additional_blocks", []) or []:
        events.extend(event_from_conversion(extra, source | {"additional": True}))
    return events


def placeholder_event(
    *,
    pos: tuple[int, int, int],
    te_nbt: dict[str, Any],
    block_id: str | None,
    metadata: int,
    reason: str,
    stage: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    te_id = str(te_nbt.get("id") or "")
    return make_block_entity_placeholder_event(
        position=pos,
        source_mod=source_mod_for(te_id, block_id),
        source_block_id=block_id or "",
        source_te_id=te_id,
        source_metadata=metadata,
        conversion_reason=reason,
        conversion_stage=stage,
        original_nbt=sanitize_json(te_nbt),
        extra=sanitize_json(extra or {}),
    )


def iter_tile_entities(world: Path):
    registry = load_block_registry(world)
    for region_file in sorted((world / "region").glob("r.*.*.mca")):
        parser = AnvilParser(str(region_file))
        for chunk in parser.get_all_chunks():
            for raw_te in chunk.get_tile_entities():
                te_nbt = sanitize_json(nbt_to_python(raw_te))
                try:
                    x, y, z = int(te_nbt["x"]), int(te_nbt["y"]), int(te_nbt["z"])
                except (KeyError, TypeError, ValueError):
                    continue
                numeric_id, metadata = get_block_at(chunk, x, y, z)
                block_id = registry.get(numeric_id) if numeric_id is not None else None
                yield {
                    "pos": (x, y, z),
                    "te_nbt": te_nbt,
                    "te_id": str(te_nbt.get("id") or ""),
                    "numeric_id": numeric_id,
                    "metadata": int(metadata or 0),
                    "block_id": block_id,
                    "region": region_file.name,
                    "chunk": [chunk.x, chunk.z],
                }


def convert(world: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    ae2 = AE2Converter()
    mekanism = MekanismConverter()
    events: list[dict[str, Any]] = []
    stats = Counter()
    by_te = Counter()
    failures: list[dict[str, Any]] = []

    for item in iter_tile_entities(world):
        pos = item["pos"]
        te_nbt = item["te_nbt"]
        te_id = item["te_id"]
        block_id = item["block_id"] or te_id
        metadata = item["metadata"]
        by_te[te_id or "[missing]"] += 1

        source = {
            "mod": source_mod_for(te_id, item["block_id"]),
            "block_id": item["block_id"] or "",
            "te_id": te_id,
            "metadata": metadata,
            "region": item["region"],
        }

        converted_events: list[dict[str, Any]] = []
        if is_ae2_tile_entity(te_id):
            stats["ae2_seen"] += 1
            try:
                conversion = ae2.convert_block(block_id, te_nbt, metadata, pos)
                converted_events = event_from_conversion(conversion, source | {"converter": "AE2Converter"})
                errors = conversion.converted.errors
                warnings = conversion.converted.warnings
            except Exception as exc:
                conversion = None
                converted_events = []
                errors = [f"{type(exc).__name__}: {exc}"]
                warnings = []
            if converted_events:
                stats["ae2_converted"] += 1
            else:
                failures.append({"pos": list(pos), "te_id": te_id, "errors": errors})
                stats["ae2_placeholder"] += 1
                converted_events = [
                    placeholder_event(
                        pos=pos,
                        te_nbt=te_nbt,
                        block_id=item["block_id"],
                        metadata=metadata,
                        reason="ae2_converter_failed",
                        stage="zsrr_ae2_mek_slice",
                        extra={"errors": errors, "warnings": warnings},
                    )
                ]
        elif is_mekanism_tile_entity(te_id, item["block_id"]):
            stats["mekanism_seen"] += 1
            try:
                conversion = mekanism.convert_block(block_id, metadata, te_nbt, pos)
                converted_events = event_from_conversion(conversion, source | {"converter": "MekanismConverter"})
                errors = conversion.converted.errors
                warnings = conversion.converted.warnings
            except Exception as exc:
                conversion = None
                converted_events = []
                errors = [f"{type(exc).__name__}: {exc}"]
                warnings = []
            if converted_events:
                stats["mekanism_converted"] += 1
            else:
                failures.append({"pos": list(pos), "te_id": te_id, "errors": errors})
                stats["mekanism_placeholder"] += 1
                converted_events = [
                    placeholder_event(
                        pos=pos,
                        te_nbt=te_nbt,
                        block_id=item["block_id"],
                        metadata=metadata,
                        reason="mekanism_converter_failed",
                        stage="zsrr_ae2_mek_slice",
                        extra={"errors": errors, "warnings": warnings},
                    )
                ]
        else:
            stats["fallback_placeholder"] += 1
            converted_events = [
                placeholder_event(
                    pos=pos,
                    te_nbt=te_nbt,
                    block_id=item["block_id"],
                    metadata=metadata,
                    reason="unsupported_mod_or_be",
                    stage="zsrr_ae2_mek_slice",
                )
            ]

        events.extend(converted_events)

    placeholder_summary = summarize_placeholder_events(events).to_dict()
    event_file = {
        "version": "2.0",
        "metadata": {
            "converter": "zsrr_ae2_mek_slice_with_fallback",
            "source_world": str(world),
            "target_version": "1.18.2",
            "stats": {
                "total_events": len(events),
                "block_entities_seen": sum(by_te.values()),
                **dict(stats),
            },
        },
        "events": events,
    }
    report = {
        "source_world": str(world),
        "event_count": len(events),
        "stats": dict(stats),
        "tile_entities_by_id": dict(by_te.most_common()),
        "placeholder_summary": placeholder_summary,
        "conversion_failures": failures[:200],
        "conversion_failure_count": len(failures),
    }
    return event_file, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--world", type=Path, default=DEFAULT_WORLD)
    parser.add_argument("--out-events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    events, report = convert(args.world)
    write_json(args.out_events, events)
    write_json(args.report, report)
    print(f"Events: {report['event_count']}")
    print(f"AE2 converted: {report['stats'].get('ae2_converted', 0)} / {report['stats'].get('ae2_seen', 0)}")
    print(f"Mekanism converted: {report['stats'].get('mekanism_converted', 0)} / {report['stats'].get('mekanism_seen', 0)}")
    print(f"Placeholders: {report['placeholder_summary']['total']}")
    print(f"Events file: {args.out_events}")
    print(f"Report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
