"""Rebuild AE2 step 1 inventory from local sources and map analysis."""

from __future__ import annotations

import csv
import importlib.util
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AE2_DIR = ROOT / "src" / "converters" / "ae2"
MAP_ANALYSIS = ROOT / "output" / "ae2_analysis" / "ae2_analysis_fixed.json"
MAP_CSV = ROOT / "output" / "ae2_analysis" / "ae2_block_entities_all.csv"
SRC_1710 = ROOT / "mod_src" / "1710" / "actual_src" / "1.7.10" / "AppliedEnergistics2" / "repo"
SRC_1182 = ROOT / "mod_src" / "118" / "actual_src" / "1.18.2" / "AppliedEnergistics2" / "repo"
JAR_1710 = ROOT / "modpack_1710" / "appliedenergistics2-rv3-beta-6.jar"
JAR_1182 = ROOT / "headless_server" / "1.18.2" / "mods" / "appliedenergistics2-forge-11.7.6.jar"
MAPPINGS_FILE = AE2_DIR / "mappings" / "block_mappings.py"
CONVERTER_FILE = AE2_DIR / "ae2_converter.py"
CABLE_CONVERTER_FILE = AE2_DIR / "nbt_converters" / "cable_converter.py"

OUT_JSON = AE2_DIR / "AE2_STEP1_REANALYSIS.json"
OUT_MD = AE2_DIR / "AE2_STEP1_REANALYSIS.md"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def load_block_mappings() -> dict[str, Any]:
    spec = importlib.util.spec_from_file_location("ae2_block_mappings_for_step1", MAPPINGS_FILE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {MAPPINGS_FILE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return dict(module.BLOCK_MAPPINGS_1710_TO_1182)


def load_normalize_block_id():
    spec = importlib.util.spec_from_file_location("ae2_block_mappings_for_step1_normalizer", MAPPINGS_FILE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {MAPPINGS_FILE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.normalize_block_id


def load_converter_keys() -> set[str]:
    text = read_text(CONVERTER_FILE)
    match = re.search(r"self\.nbt_converters:\s*Dict\[.*?\]\s*=\s*\{(?P<body>.*?)\n\s*\}", text, re.S)
    if not match:
        return set()
    return set(re.findall(r"'([^']+)'\s*:", match.group("body")))


def load_map_analysis() -> tuple[dict[str, Any], list[dict[str, str]]]:
    analysis = json.loads(read_text(MAP_ANALYSIS))
    rows: list[dict[str, str]] = []
    if MAP_CSV.exists():
        with MAP_CSV.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
    return analysis, rows


def source_1710_blocks() -> list[dict[str, str]]:
    blocks: list[dict[str, str]] = []
    block_root = SRC_1710 / "src" / "main" / "java" / "appeng" / "block"
    for path in sorted(block_root.rglob("Block*.java")):
        text = read_text(path)
        block_class = path.stem
        tile_match = re.search(r"setTileEntity\(\s*(\w+)\.class\s*\)", text)
        blocks.append(
            {
                "block_class": block_class,
                "tile_class": tile_match.group(1) if tile_match else "",
                "source_path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "registry_id_guess": f"appliedenergistics2:tile.{block_class}",
                "nbt_id_guess": block_class,
            }
        )
    return blocks


def source_1710_tile_classes() -> list[str]:
    tile_root = SRC_1710 / "src" / "main" / "java" / "appeng" / "tile"
    return sorted(path.stem for path in tile_root.rglob("Tile*.java"))


def target_1182_source_blocks() -> list[str]:
    blockstates = SRC_1182 / "src" / "generated" / "resources" / "assets" / "ae2" / "blockstates"
    return sorted(f"ae2:{path.stem}" for path in blockstates.glob("*.json"))


def target_1182_jar_blocks() -> list[str]:
    return sorted(
        "ae2:" + Path(name).stem
        for name in jar_entries(JAR_1182, "assets/ae2/blockstates/", ".json")
    )


def target_1182_block_entities() -> list[dict[str, str]]:
    text = read_text(SRC_1182 / "src" / "main" / "java" / "appeng" / "core" / "definitions" / "AEBlockEntities.java")
    entries = []
    pattern = re.compile(
        r"DeferredBlockEntityType<(?P<class>\w+)>\s+(?P<const>\w+)\s*=\s*create\(\s*\"(?P<id>[^\"]+)\"(?P<body>.*?);",
        re.S,
    )
    for match in pattern.finditer(text):
        block_refs = sorted(set(re.findall(r"AEBlocks\.(\w+)", match.group("body"))))
        entries.append(
            {
                "id": f"ae2:{match.group('id')}",
                "constant": match.group("const"),
                "class": match.group("class"),
                "blocks": ", ".join(block_refs),
            }
        )
    return entries


def block_constant_to_id(constant: str) -> str:
    special = {
        "ME_CHEST": "chest",
        "WIRELESS_ACCESS_POINT": "wireless_access_point",
    }
    return "ae2:" + special.get(constant, constant.lower())


def block_entity_block_links(entries: list[dict[str, str]]) -> dict[str, str]:
    links = {}
    for entry in entries:
        for constant in entry["blocks"].split(", "):
            if constant:
                links[block_constant_to_id(constant)] = entry["id"]
    return links


def jar_entries(path: Path, prefix: str, suffix: str) -> list[str]:
    if not path.exists():
        return []
    with zipfile.ZipFile(path) as jar:
        return sorted(name for name in jar.namelist() if name.startswith(prefix) and name.endswith(suffix))


def cable_part_mappings() -> dict[str, str]:
    text = read_text(CABLE_CONVERTER_FILE)
    match = re.search(r"PART_TYPE_MAPPING\s*=\s*\{(?P<body>.*?)\n\}", text, re.S)
    if not match:
        return {}
    result = {}
    for source, target in re.findall(r"'([^']+)'\s*:\s*'([^']+)'", match.group("body")):
        result[source] = target
    return result


def summarize_positions(rows: list[dict[str, str]]) -> dict[str, Any]:
    regions = Counter()
    chunks = Counter()
    for row in rows:
        chunks[row["id"]] += 1
        rx = int(row["chunk_x"]) // 32
        rz = int(row["chunk_z"]) // 32
        regions[(row["id"], f"r.{rx}.{rz}.mca")] += 1

    top_regions: dict[str, list[dict[str, Any]]] = {}
    for (te_id, region), count in regions.most_common():
        top_regions.setdefault(te_id, [])
        if len(top_regions[te_id]) < 5:
            top_regions[te_id].append({"region": region, "count": count})
    return {"rows": len(rows), "by_id": dict(chunks), "top_regions": top_regions}


def build_report() -> dict[str, Any]:
    mappings = load_block_mappings()
    normalize_block_id = load_normalize_block_id()
    converter_keys = load_converter_keys()
    analysis, rows = load_map_analysis()
    target_source_blocks = set(target_1182_source_blocks())
    target_jar_blocks = set(target_1182_jar_blocks())
    target_blocks = target_source_blocks | target_jar_blocks
    target_block_entities = target_1182_block_entities()
    target_be_ids = {entry["id"] for entry in target_block_entities}
    target_be_links = block_entity_block_links(target_block_entities)

    map_rows = []
    for te_id, count in sorted(analysis["te_by_type"].items(), key=lambda item: (-item[1], item[0])):
        prefixed = f"appliedenergistics2:tile.{te_id}"
        normalized = normalize_block_id(te_id)
        mapping = mappings.get(normalized)
        target_id = mapping.id_1182 if mapping else ""
        converter = mapping.nbt_converter if mapping else ""
        map_rows.append(
            {
                "nbt_id": te_id,
                "count": count,
                "prefixed_mapping_key": prefixed,
                "normalized_mapping_key": normalized,
                "mapped_by_current_table": bool(mapping),
                "unprefixed_alias_supported": normalized in mappings and normalized != te_id,
                "target_block": target_id,
                "target_block_exists_in_1182_assets": target_id in target_blocks if target_id else False,
                "target_block_entity_exists": (
                    target_id in target_be_ids or target_id in target_be_links
                ) if target_id else False,
                "target_block_entity_id": target_be_links.get(target_id, target_id if target_id in target_be_ids else ""),
                "converter": converter or "",
                "converter_registered": converter in converter_keys if converter else False,
                "notes": "Nie-AE2 albo addon" if te_id == "TileChestHungry" else "",
            }
        )

    mapped_counts = sum(row["count"] for row in map_rows if row["mapped_by_current_table"])
    alias_missing_counts = sum(
        row["count"]
        for row in map_rows
        if row["mapped_by_current_table"]
        and not row["unprefixed_alias_supported"]
        and row["nbt_id"].startswith("Block")
    )
    unmapped_rows = [row for row in map_rows if not row["mapped_by_current_table"]]
    target_missing_rows = [row for row in map_rows if row["mapped_by_current_table"] and not row["target_block_exists_in_1182_assets"]]
    converter_missing_rows = [row for row in map_rows if row["converter"] and not row["converter_registered"]]

    return {
        "inputs": {
            "map_analysis": str(MAP_ANALYSIS.relative_to(ROOT)).replace("\\", "/"),
            "map_csv": str(MAP_CSV.relative_to(ROOT)).replace("\\", "/"),
            "source_1710": str(SRC_1710.relative_to(ROOT)).replace("\\", "/"),
            "source_1182": str(SRC_1182.relative_to(ROOT)).replace("\\", "/"),
            "jar_1710": str(JAR_1710.relative_to(ROOT)).replace("\\", "/"),
            "jar_1182": str(JAR_1182.relative_to(ROOT)).replace("\\", "/"),
        },
        "map_totals": {
            "regions_with_ae2_like_te": analysis["regions_with_ae2"],
            "total_ae2_like_te": analysis["total_ae2_te"],
            "mapped_te_count_by_prefixed_table": mapped_counts,
            "unmapped_te_count": analysis["total_ae2_te"] - mapped_counts,
            "mapped_but_unprefixed_alias_missing_count": alias_missing_counts,
        },
        "map_tile_entities": map_rows,
        "source_1710_blocks": source_1710_blocks(),
        "source_1710_tile_classes": source_1710_tile_classes(),
        "target_1182_source_blocks": sorted(target_source_blocks),
        "target_1182_jar_blocks": sorted(target_jar_blocks),
        "target_1182_blocks": sorted(target_blocks),
        "target_1182_block_entities": target_block_entities,
        "target_1182_block_entity_links": target_be_links,
        "source_1710_jar_tile_classes": jar_entries(JAR_1710, "appeng/tile/", ".class"),
        "cable_part_mappings": cable_part_mappings(),
        "position_summary": summarize_positions(rows),
        "gaps": {
            "unmapped_map_rows": unmapped_rows,
            "mapped_but_unprefixed_alias_missing_rows": [
                row for row in map_rows if row["mapped_by_current_table"] and not row["unprefixed_alias_supported"]
            ],
            "target_block_missing_rows": target_missing_rows,
            "converter_missing_rows": converter_missing_rows,
        },
    }


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def render_markdown(report: dict[str, Any]) -> str:
    totals = report["map_totals"]
    map_rows = report["map_tile_entities"]
    gaps = report["gaps"]
    source_te_blocks = [row for row in report["source_1710_blocks"] if row["tile_class"]]

    lines = [
        "# AE2 - Krok 1 wykonany ponownie",
        "",
        "Ten dokument zastępuje stary opis `AE2_BLOCKS_AND_TE.md` jako audyt kroku 1.",
        "Powstał z lokalnych źródeł AE2 1.7.10 i 1.18.2, z JAR-ów używanych w projekcie oraz z aktualnej analizy `mapa_1710`.",
        "",
        "## Werdykt",
        "",
        "Poprzedni krok 1 był wykonany za słabo. Mieszał rejestrowe ID bloków 1.7.10 z faktycznym `id` TileEntity w NBT mapy, a liczniki użycia były nieaktualne.",
        "Po kroku 3 tabela mapowań obsługuje już aliasy surowych NBT ID (`BlockDrive`, `BlockCableBus` itd.), więc ten raport pełni teraz rolę regresyjnego audytu pokrycia.",
        "",
        "## Dane wejściowe",
        "",
    ]
    for key, value in report["inputs"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(
        [
            "",
            "## Skala na mapie",
            "",
            f"- Regiony z AE2-like TileEntity: {totals['regions_with_ae2_like_te']}",
            f"- Łącznie AE2-like TileEntity: {totals['total_ae2_like_te']}",
            f"- Pokryte przez obecną tabelę po pełnym prefiksie: {totals['mapped_te_count_by_prefixed_table']}",
            f"- Niepokryte przez obecną tabelę: {totals['unmapped_te_count']}",
            f"- Pokryte logicznie, ale bez aliasu surowego NBT ID: {totals['mapped_but_unprefixed_alias_missing_count']}",
            "",
            "## TileEntity znalezione na mapie",
            "",
            md_table(
                ["NBT id", "Ilość", "Mapowanie", "Alias NBT", "Cel 1.18.2", "Blok celu", "BE celu", "Konwerter", "Konwerter OK", "Uwagi"],
                [
                    [
                        row["nbt_id"],
                        row["count"],
                        "tak" if row["mapped_by_current_table"] else "nie",
                        "tak" if row["unprefixed_alias_supported"] else "nie",
                        row["target_block"] or "-",
                        "tak" if row["target_block_exists_in_1182_assets"] else "nie",
                        "tak" if row["target_block_entity_exists"] else "nie",
                        row["converter"] or "-",
                        "tak" if row["converter_registered"] else ("-" if not row["converter"] else "nie"),
                        row["notes"] or "",
                    ]
                    for row in map_rows
                ],
            ),
            "",
            "## Źródło 1.7.10 - bloki z TileEntity",
            "",
            md_table(
                ["Blok", "Tile class", "Registry guess", "NBT id guess", "Plik"],
                [
                    [
                        row["block_class"],
                        row["tile_class"],
                        row["registry_id_guess"],
                        row["nbt_id_guess"],
                        row["source_path"],
                    ]
                    for row in source_te_blocks
                ],
            ),
            "",
            "## Cel 1.18.2 - BlockEntity z kodu AE2",
            "",
            md_table(
                ["BE id", "Stała", "Klasa", "Bloki"],
                [
                    [row["id"], row["constant"], row["class"], row["blocks"]]
                    for row in report["target_1182_block_entities"]
                ],
            ),
            "",
            "## CableBus - rozpoznawane części",
            "",
            md_table(
                ["Klasa części 1.7.10", "Typ pośredni"],
                [[source, target] for source, target in sorted(report["cable_part_mappings"].items())],
            ),
            "",
            "## Luki wykryte w kroku 1",
            "",
        ]
    )

    if gaps["unmapped_map_rows"]:
        lines.append("### Brak mapowania dla NBT z mapy")
        lines.append("")
        lines.append(
            md_table(
                ["NBT id", "Ilość", "Uwagi"],
                [[row["nbt_id"], row["count"], row["notes"] or ""] for row in gaps["unmapped_map_rows"]],
            )
        )
        lines.append("")

    if gaps["mapped_but_unprefixed_alias_missing_rows"]:
        lines.append("### Brak aliasów dla surowych NBT id")
        lines.append("")
        lines.append(
            md_table(
                ["NBT id", "Ilość", "Istniejący klucz mapowania", "Cel"],
                [
                [row["nbt_id"], row["count"], row["normalized_mapping_key"], row["target_block"]]
                    for row in gaps["mapped_but_unprefixed_alias_missing_rows"]
                ],
            )
        )
        lines.append("")

    if gaps["target_block_missing_rows"]:
        lines.append("### Cel niepotwierdzony w assets 1.18.2")
        lines.append("")
        lines.append(
            md_table(
                ["NBT id", "Cel", "Ilość"],
                [[row["nbt_id"], row["target_block"], row["count"]] for row in gaps["target_block_missing_rows"]],
            )
        )
        lines.append("")

    if gaps["converter_missing_rows"]:
        lines.append("### Konwerter wpisany w mapowaniu, ale niezarejestrowany")
        lines.append("")
        lines.append(
            md_table(
                ["NBT id", "Konwerter", "Ilość"],
                [[row["nbt_id"], row["converter"], row["count"]] for row in gaps["converter_missing_rows"]],
            )
        )
        lines.append("")

    lines.extend(
        [
            "## Wniosek dla kolejnych kroków",
            "",
            "Krok 1 jest teraz wystarczająco twardy jako inwentarz regresyjny. Po kroku 3 aliasy surowych `id` TileEntity są obsługiwane; otwarte pozostają tylko świadome fallbacki `BlockCrank`/`BlockGrinder` i nie-core `TileChestHungry`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(json.dumps(report["map_totals"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
