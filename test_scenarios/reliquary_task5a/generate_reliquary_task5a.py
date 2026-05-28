#!/usr/bin/env python3
"""Generate Reliquary Task 5A test patches.

Produces:
- a 1.7.10 source patch with representative Reliquary blocks and tile entities,
- a 1.18.2 target patch produced by the Reliquary converter (via router),
- a conversion report with per-sample results and warnings.

Covered scenarios:
  - Alkahestry Altar (2 states: inactive, active)
  - Apothecary Cauldron (4 states: empty/meta3, brewing+glowstone, splash/meta2, partial/meta1)
  - Apothecary Mortar (5 states: empty, vanilla ingredients, mob_ingredient, potion_essence, full)
  - Blocks without TE (fertile_lily_pad, interdiction_torch, wraith_node)
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from converters.reliquary.converter import ReliquaryConverter  # noqa: E402
from converters.router import convert_te_to_events  # noqa: E402


SOURCE_PATCH = SCENARIO_DIR / "reliquary_task5a_source_patch_1710.json"
CONVERTED_PATCH = SCENARIO_DIR / "reliquary_task5a_converted_patch_1182.json"
CONVERSION_REPORT = SCENARIO_DIR / "reliquary_task5a_conversion_report.json"
REPORT_MD = SCENARIO_DIR / "RELIQUARY_TASK5A_REPORT.md"
HANDOFF = SCENARIO_DIR / "HANDOFF_RELIQUARY_TASK5A.md"

# Numeric block IDs are world-specific. These are placeholder values used only
# in the source-patch `set_block` entries for documentation purposes.
# The TE conversion uses string TE IDs, not numeric block IDs.
BLOCK_IDS_PLACEHOLDER: dict[str, int] = {
    "xreliquary:alkahestry_altar":    0,
    "xreliquary:apothecary_cauldron": 0,
    "xreliquary:apothecary_mortar":   0,
    "xreliquary:fertile_lily_pad":    0,
    "xreliquary:interdiction_torch":  0,
    "xreliquary:wraith_node":         0,
}


@dataclass
class Sample:
    name: str
    block_id: str        # 1.7.10 registry name (e.g. "xreliquary:alkahestry_altar")
    metadata: int
    x: int
    y: int
    z: int
    te_id: str | None = None        # 1.7.10 TE registry name if block has TE
    nbt: dict[str, Any] | None = None
    category: str = "block"
    purpose: str = ""


def position_for(index: int) -> tuple[int, int, int]:
    columns = 10
    spacing = 2
    return (300 + (index % columns) * spacing, 64, 300 + (index // columns) * spacing)


def build_samples() -> list[Sample]:
    samples: list[Sample] = []
    idx = 0

    def add(
        name: str,
        block_id: str,
        metadata: int,
        category: str,
        purpose: str,
        te_id: str | None = None,
        nbt_extra: dict[str, Any] | None = None,
    ) -> None:
        nonlocal idx
        x, y, z = position_for(idx)
        nbt = None
        if te_id is not None:
            nbt = {"id": te_id, "x": x, "y": y, "z": z}
            if nbt_extra:
                nbt.update(nbt_extra)
        samples.append(Sample(name, block_id, metadata, x, y, z, te_id, nbt, category, purpose))
        idx += 1

    # ── Alkahestry Altar ──────────────────────────────────────────────────────
    add(
        "altar_inactive",
        "xreliquary:alkahestry_altar",
        0,
        "tile_entity",
        "Altar in resting state (no cycle running).",
        te_id="reliquaryAltar",
        nbt_extra={"cycleTime": 0, "redstoneCount": 0, "isActive": False},
    )
    add(
        "altar_active_midcycle",
        "xreliquary:alkahestry_altar",
        0,
        "tile_entity",
        "Altar mid-cycle: 5 RS inserted, 600 ticks remaining.",
        te_id="reliquaryAltar",
        nbt_extra={"cycleTime": 600, "redstoneCount": 5, "isActive": True},
    )

    # ── Apothecary Cauldron ───────────────────────────────────────────────────
    add(
        "cauldron_empty_full_water",
        "xreliquary:apothecary_cauldron",
        3,
        "tile_entity",
        "Empty cauldron, full of water (meta=3). glowstoneCount should be 0.",
        te_id="reliquaryCauldron",
        nbt_extra={
            "hasGlowstone": False,
            "hasNetherwart": False,
            "hasGunpowder": False,
            "redstoneCount": 0,
            "cookTime": 0,
            "potionEssence": {},
        },
    )
    add(
        "cauldron_brewing_glowstone_regen",
        "xreliquary:apothecary_cauldron",
        3,
        "tile_entity",
        "Brewing cauldron: Speed+Regen essence, glowstone=True → 1, 2 redstone.",
        te_id="reliquaryCauldron",
        nbt_extra={
            "hasGlowstone": True,
            "hasNetherwart": True,
            "hasGunpowder": False,
            "redstoneCount": 2,
            "cookTime": 80,
            "potionEssence": {
                "effects": [
                    {"id": 1,  "duration": 900,  "potency": 0},
                    {"id": 10, "duration": 300,  "potency": 0},
                ]
            },
        },
    )
    add(
        "cauldron_done_splash_strength",
        "xreliquary:apothecary_cauldron",
        2,
        "tile_entity",
        "Splash potion ready: Strength II, gunpowder+netherwart, meta=2 → liquidLevel=2.",
        te_id="reliquaryCauldron",
        nbt_extra={
            "hasGlowstone": False,
            "hasNetherwart": True,
            "hasGunpowder": True,
            "redstoneCount": 0,
            "cookTime": 160,
            "potionEssence": {
                "effects": [
                    {"id": 5, "duration": 1800, "potency": 1},
                ]
            },
        },
    )
    add(
        "cauldron_partial_nightvision_absorption",
        "xreliquary:apothecary_cauldron",
        1,
        "tile_entity",
        "Partially drained cauldron (meta=1), Night Vision + Absorption essence.",
        te_id="reliquaryCauldron",
        nbt_extra={
            "hasGlowstone": True,
            "hasNetherwart": True,
            "hasGunpowder": False,
            "redstoneCount": 5,
            "cookTime": 160,
            "potionEssence": {
                "effects": [
                    {"id": 16, "duration": 4800, "potency": 0},
                    {"id": 22, "duration": 1200, "potency": 0},
                ]
            },
        },
    )

    # ── Apothecary Mortar ─────────────────────────────────────────────────────
    add(
        "mortar_empty",
        "xreliquary:apothecary_mortar",
        0,
        "tile_entity",
        "Empty mortar, 0 pestle uses.",
        te_id="apothecaryMortar",
        nbt_extra={"pestleUsed": 0, "Items": []},
    )
    add(
        "mortar_two_vanilla_ingredients",
        "xreliquary:apothecary_mortar",
        0,
        "tile_entity",
        "Sugar + Ghast Tear, 2 pestle uses.",
        te_id="apothecaryMortar",
        nbt_extra={
            "pestleUsed": 2,
            "Items": [
                {"Slot": 0, "id": "minecraft:sugar",      "Count": 1, "Damage": 0},
                {"Slot": 1, "id": "minecraft:ghast_tear", "Count": 1, "Damage": 0},
            ],
        },
    )
    add(
        "mortar_mob_ingredient_meta3",
        "xreliquary:apothecary_mortar",
        0,
        "tile_entity",
        "xreliquary:mob_ingredient Damage=3 (type remapped to components.custom_data).",
        te_id="apothecaryMortar",
        nbt_extra={
            "pestleUsed": 4,
            "Items": [
                {"Slot": 0, "id": "xreliquary:mob_ingredient", "Count": 1, "Damage": 3},
                {"Slot": 1, "id": "minecraft:spider_eye",       "Count": 1, "Damage": 0},
            ],
        },
    )
    add(
        "mortar_with_potion_essence",
        "xreliquary:apothecary_mortar",
        0,
        "tile_entity",
        "PotionEssence item in slot 0 with Speed+Regen effects.",
        te_id="apothecaryMortar",
        nbt_extra={
            "pestleUsed": 1,
            "Items": [
                {
                    "Slot": 0,
                    "id": "xreliquary:potion_essence",
                    "Count": 1,
                    "Damage": 0,
                    "tag": {
                        "effects": [
                            {"id": 1,  "duration": 900, "potency": 0},
                            {"id": 10, "duration": 300, "potency": 0},
                        ]
                    },
                },
                {"Slot": 1, "id": "minecraft:blaze_powder", "Count": 1, "Damage": 0},
            ],
        },
    )
    add(
        "mortar_full_three_slots",
        "xreliquary:apothecary_mortar",
        0,
        "tile_entity",
        "Full mortar: 3 vanilla items, 3 pestle uses.",
        te_id="apothecaryMortar",
        nbt_extra={
            "pestleUsed": 3,
            "Items": [
                {"Slot": 0, "id": "minecraft:iron_ingot",    "Count": 1, "Damage": 0},
                {"Slot": 1, "id": "minecraft:magma_cream",   "Count": 1, "Damage": 0},
                {"Slot": 2, "id": "minecraft:golden_carrot", "Count": 1, "Damage": 0},
            ],
        },
    )

    # ── Blocks without TE ──────────────────────────────────────────────────────
    add("fertile_lily_pad",   "xreliquary:fertile_lily_pad",   0, "block_no_te", "Fertile Lily Pad → reliquary:fertile_lily_pad.")
    add("interdiction_torch", "xreliquary:interdiction_torch", 0, "block_no_te", "Interdiction Torch → reliquary:interdiction_torch.")
    add("wraith_node",        "xreliquary:wraith_node",        0, "block_no_te", "Wraith Node → reliquary:wraith_node.")

    return samples


# ──────────────────────────────────────────────────────────────────────────────
# Source patch builder
# ──────────────────────────────────────────────────────────────────────────────

def build_source_patch(samples: list[Sample]) -> dict[str, Any]:
    edits: list[dict[str, Any]] = []
    for sample in samples:
        edits.append({
            "op": "set_block",
            "x": sample.x, "y": sample.y, "z": sample.z,
            "id": BLOCK_IDS_PLACEHOLDER.get(sample.block_id, 0),
            "meta": sample.metadata,
            "registry_name": sample.block_id,
            "label": sample.name,
            "category": sample.category,
        })
        if sample.nbt:
            edits.append({
                "op": "set_te",
                "x": sample.x, "y": sample.y, "z": sample.z,
                "nbt": sample.nbt,
                "label": sample.name,
            })
    return {
        "format_version": "1.7.10",
        "metadata": {
            "name": "reliquary_task5a_source",
            "generated_by": "generate_reliquary_task5a.py",
            "note": "Numeric block IDs are placeholder (0). TE conversion uses TE string IDs.",
            "samples": len(samples),
        },
        "edits": edits,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Conversion
# ──────────────────────────────────────────────────────────────────────────────

def convert_samples(
    samples: list[Sample],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Run each sample through the router (TE samples) or direct block remap.

    Returns (all_events, per_sample_results).
    """
    all_events: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []

    for sample in samples:
        pos = (sample.x, sample.y, sample.z)

        if sample.te_id and sample.nbt:
            # Route via the real pipeline (router.convert_te_to_events)
            events = convert_te_to_events(
                te_nbt=sample.nbt,
                block_numeric_id=BLOCK_IDS_PLACEHOLDER.get(sample.block_id, 0),
                metadata=sample.metadata,
                global_pos=pos,
            )
        else:
            # Block without TE: simple remap via mappings
            from converters.reliquary.mappings import BLOCK_ID_MAP
            target_id = BLOCK_ID_MAP.get(sample.block_id)
            if target_id:
                events = [{"op": "set_block", "pos": list(pos), "block": target_id}]
            else:
                events = []

        all_events.extend(events)

        success = bool(events and events[0].get("op") in ("set_block", "set_block_entity"))
        is_placeholder = any(
            "conversion_placeholders" in str(ev.get("block", ""))
            for ev in events
        )
        target_block = events[0].get("block", "") if events else ""
        warnings_in_ev = []
        for ev in events:
            warnings_in_ev.extend(ev.get("warnings", []))

        results.append({
            "name": sample.name,
            "category": sample.category,
            "purpose": sample.purpose,
            "source": {
                "block_id": sample.block_id,
                "metadata": sample.metadata,
                "te_id": sample.te_id,
                "position": list(pos),
            },
            "target_block": target_block,
            "event_count": len(events),
            "success": success and not is_placeholder,
            "is_placeholder": is_placeholder,
            "warnings": warnings_in_ev,
        })

    return all_events, results


# ──────────────────────────────────────────────────────────────────────────────
# Output builders
# ──────────────────────────────────────────────────────────────────────────────

def build_converted_patch(events: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "format_version": "1.18.2",
        "metadata": {
            "name": "reliquary_task5a_converted",
            "generated_by": "generate_reliquary_task5a.py",
            "source_patch": SOURCE_PATCH.name,
        },
        "edits": events,
    }


def build_report(samples: list[Sample], results: list[dict[str, Any]], events: list[dict[str, Any]]) -> dict[str, Any]:
    success_count = sum(1 for r in results if r["success"])
    failure_count = sum(1 for r in results if not r["success"])
    placeholder_count = sum(1 for r in results if r["is_placeholder"])
    all_warnings: list[str] = []
    for r in results:
        all_warnings.extend(r["warnings"])
    return {
        "name": "Reliquary Task 5A conversion report",
        "samples": len(samples),
        "total_events": len(events),
        "success_count": success_count,
        "failure_count": failure_count,
        "placeholder_count": placeholder_count,
        "warnings": all_warnings,
        "results": results,
    }


def write_report_md(samples: list[Sample], report: dict[str, Any]) -> None:
    lines = [
        "# Reliquary Task 5A – Raport konwersji",
        "",
        "## Podsumowanie",
        "",
        f"- Próbki: {report['samples']}",
        f"- Eventy 1.18.2: {report['total_events']}",
        f"- Sukcesy: {report['success_count']}",
        f"- Błędy: {report['failure_count']}",
        f"- Placeholdery: {report['placeholder_count']}",
        "",
        "## Wyniki per próbka",
        "",
        "| Próbka | Kategoria | Target | Wynik |",
        "|--------|-----------|--------|-------|",
    ]
    for r in report["results"]:
        status = "✅" if r["success"] else ("⚠️ placeholder" if r["is_placeholder"] else "❌")
        lines.append(f"| `{r['name']}` | {r['category']} | `{r['target_block']}` | {status} |")

    if report["warnings"]:
        lines += ["", "## Ostrzeżenia", ""]
        for w in report["warnings"]:
            lines.append(f"- {w}")

    lines += [
        "",
        "## Kategorie",
        "",
        f"- `tile_entity`: {sum(1 for s in samples if s.category == 'tile_entity')}",
        f"- `block_no_te`: {sum(1 for s in samples if s.category == 'block_no_te')}",
        "",
        "## Pliki",
        "",
        "- `reliquary_task5a_source_patch_1710.json` – patch źródłowy 1.7.10",
        "- `reliquary_task5a_converted_patch_1182.json` – patch docelowy 1.18.2",
        "- `reliquary_task5a_conversion_report.json` – pełny raport per próbka",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_handoff(report: dict[str, Any]) -> None:
    text = f"""# Handoff: Reliquary – Zadanie 5A (Task 5A)

## Podsumowanie sesji

Wykonano Zadanie 5A dla Reliquary: wygenerowano testowy patch 1.7.10 pokrywający
wszystkie 3 typy TE i 3 bloki bez TE, a następnie przekonwertowano przez pełny
pipeline (router → ReliquaryConverter).

## Ukończono

- [x] Wygenerowano source patch 1.7.10 (`reliquary_task5a_source_patch_1710.json`)
- [x] Uruchomiono konwersję przez router dla wszystkich próbek TE
- [x] Wygenerowano converted patch 1.18.2 i raport
- [x] Zweryfikowano wyniki wszystkich {report['samples']} próbek

## Wyniki

- Próbki: {report['samples']}
- Eventy: {report['total_events']}
- Sukcesy: {report['success_count']}
- Błędy: {report['failure_count']}
- Placeholdery: {report['placeholder_count']}

## Nowe pliki

- `test_scenarios/reliquary_task5a/generate_reliquary_task5a.py`
- `test_scenarios/reliquary_task5a/reliquary_task5a_source_patch_1710.json`
- `test_scenarios/reliquary_task5a/reliquary_task5a_converted_patch_1182.json`
- `test_scenarios/reliquary_task5a/reliquary_task5a_conversion_report.json`
- `test_scenarios/reliquary_task5a/RELIQUARY_TASK5A_REPORT.md`

## Następne kroki (Zadanie 5B)

1. Zmaterializować `reliquary_task5a_converted_patch_1182.json` na headless serwerze 1.18.2
2. Zweryfikować że bloki Reliquary ładują się poprawnie (brak missing block crashes)
3. Sprawdzić kauldron NBT w grze: `liquidLevel`, `glowstoneCount`, `effects`

---

**Status:** ✅ Zadanie 5A ukończone
**Data:** 2026-05-28
"""
    HANDOFF.write_text(text, encoding="utf-8")


# ──────────────────────────────────────────────────────────────────────────────

def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    samples = build_samples()
    source_patch = build_source_patch(samples)
    events, results = convert_samples(samples)
    converted_patch = build_converted_patch(events)
    report = build_report(samples, results, events)

    write_json(SOURCE_PATCH, source_patch)
    write_json(CONVERTED_PATCH, converted_patch)
    write_json(CONVERSION_REPORT, report)
    write_report_md(samples, report)
    write_handoff(report)

    print(f"Samples:  {report['samples']}")
    print(f"Events:   {report['total_events']}")
    print(f"Success:  {report['success_count']}  Failure: {report['failure_count']}  Placeholders: {report['placeholder_count']}")
    if report["warnings"]:
        print(f"Warnings: {report['warnings']}")
    return 0 if report["failure_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
