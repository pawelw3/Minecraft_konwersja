"""Helpers for emitting conversion placeholder BlockEntities.

The placeholder mod stores unsupported legacy TileEntities in the target
1.18.2 world without pretending that their original behavior was converted.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable


PLACEHOLDER_MOD_ID = "conversion_placeholders"
PLACEHOLDER_BLOCK_ID = f"{PLACEHOLDER_MOD_ID}:block_entity_placeholder"
PLACEHOLDER_BLOCK_ENTITY_ID = f"{PLACEHOLDER_MOD_ID}:block_entity_placeholder"

Position = tuple[int, int, int]
ZoneResolver = Callable[[Position, dict[str, Any]], str | None]


def make_block_entity_placeholder_event(
    *,
    position: Position,
    source_mod: str,
    original_nbt: dict[str, Any] | None = None,
    source_block_id: str | None = None,
    source_te_id: str | None = None,
    source_metadata: int | None = None,
    conversion_reason: str = "unsupported_be",
    conversion_stage: str | None = None,
    extra: dict[str, Any] | None = None,
    blockstate: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build a standard Event JSON ``set_block_entity`` placeholder event.

    ``original_nbt`` is deep-copied and kept intact, including nested
    compounds/lists and legacy ``x/y/z`` fields. The target BE receives its
    own current ``x/y/z`` fields separately, so world writers can place it at
    ``position`` without losing the original coordinates.
    """

    pos = _normalize_position(position)
    source_pos = _source_pos_from(original_nbt, pos)
    te_id = source_te_id or _string_or_none((original_nbt or {}).get("id"))

    nbt = {
        "id": PLACEHOLDER_BLOCK_ENTITY_ID,
        "x": pos[0],
        "y": pos[1],
        "z": pos[2],
        "source_mod": source_mod or "unknown",
        "source_block_id": source_block_id or "",
        "source_te_id": te_id or "",
        "source_metadata": int(source_metadata or 0),
        "source_pos": list(source_pos),
        "conversion_reason": conversion_reason or "unsupported_be",
        "conversion_stage": conversion_stage or "",
        "original_nbt": deepcopy(original_nbt) if original_nbt is not None else {},
        "extra": deepcopy(extra) if extra is not None else {},
    }

    event = {
        "op": "set_block_entity",
        "pos": list(pos),
        "block": PLACEHOLDER_BLOCK_ID,
        "nbt": nbt,
        "source": {
            "mod": source_mod or "unknown",
            "reason": conversion_reason or "unsupported_be",
        },
    }
    if blockstate:
        event["blockstate"] = dict(blockstate)
    if source_block_id:
        event["source"]["block_id"] = source_block_id
    if te_id:
        event["source"]["te_id"] = te_id
    if source_metadata is not None:
        event["source"]["metadata"] = int(source_metadata)
    if conversion_stage:
        event["source"]["stage"] = conversion_stage
    return event


@dataclass
class PlaceholderReport:
    total: int = 0
    by_mod: Counter[str] = field(default_factory=Counter)
    by_te_id: Counter[str] = field(default_factory=Counter)
    by_zone: Counter[str] = field(default_factory=Counter)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "by_mod": dict(sorted(self.by_mod.items())),
            "by_te_id": dict(sorted(self.by_te_id.items())),
            "by_zone": dict(sorted(self.by_zone.items())),
        }


def summarize_placeholder_events(
    events: Iterable[dict[str, Any]],
    zone_resolver: ZoneResolver | None = None,
) -> PlaceholderReport:
    """Count placeholder events by source mod, TE id and optional zone."""

    report = PlaceholderReport()
    for event in events:
        if not is_placeholder_event(event):
            continue

        nbt = event.get("nbt") or {}
        source = event.get("source") or {}
        pos = _normalize_position(tuple(event.get("pos") or (0, 0, 0)))

        report.total += 1
        report.by_mod[str(nbt.get("source_mod") or source.get("mod") or "unknown")] += 1
        report.by_te_id[str(nbt.get("source_te_id") or source.get("te_id") or "[missing]")] += 1

        if zone_resolver:
            zone = zone_resolver(pos, event)
            if zone:
                report.by_zone[zone] += 1

    return report


def is_placeholder_event(event: dict[str, Any]) -> bool:
    return (
        event.get("op") == "set_block_entity"
        and event.get("block") == PLACEHOLDER_BLOCK_ID
        and (event.get("nbt") or {}).get("id") == PLACEHOLDER_BLOCK_ENTITY_ID
    )


def _source_pos_from(original_nbt: dict[str, Any] | None, fallback: Position) -> Position:
    if not original_nbt:
        return fallback
    try:
        return (
            int(original_nbt.get("x", fallback[0])),
            int(original_nbt.get("y", fallback[1])),
            int(original_nbt.get("z", fallback[2])),
        )
    except (TypeError, ValueError):
        return fallback


def _normalize_position(position: tuple[Any, Any, Any]) -> Position:
    if len(position) != 3:
        raise ValueError(f"position must have 3 elements, got {position!r}")
    return (int(position[0]), int(position[1]), int(position[2]))


def _string_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None
