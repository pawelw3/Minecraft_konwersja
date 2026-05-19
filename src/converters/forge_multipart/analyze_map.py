"""
Analiza mapy 1.7.10 pod kątem ForgeMultipart/CB Multipart.
Zadanie 4 — weryfikacja pokrycia i exact TE ID.

NIGDY nie modyfikuje mapa_1710/ — tylko odczyt.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from collections import Counter
from typing import Dict, List, Set, Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from minecraft_map_parser.anvil_parser import AnvilParser


# Ścieżki
# Ustal root projektu (3 poziomy wyżej od tego pliku)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
WORLD_PATH = PROJECT_ROOT / "mapa_1710"
OUTPUT_PATH = PROJECT_ROOT / "output/forge_multipart"
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# Wzorce do szukania TE ID ForgeMultipart
TE_PATTERNS = [
    r"TileMultipart",
    r"ForgeMultipart",
    r"multipart",
]


def scan_region_for_te_ids(region_file: Path) -> Dict[str, List[Dict[str, Any]]]:
    """
    Skanuje pojedynczy plik regionu i zwraca dict:
    {te_id: [lista TE data dict]}
    """
    results: Dict[str, List[Dict[str, Any]]] = {}
    try:
        parser = AnvilParser(str(region_file))
    except Exception as e:
        print(f"  Błąd odczytu {region_file.name}: {e}")
        return results

    for cz in range(32):
        for cx in range(32):
            try:
                chunk = parser.get_chunk(cx, cz)
                if not chunk:
                    continue
            except Exception:
                continue

            try:
                tes = chunk.get_tile_entities()
            except Exception:
                continue

            for te in tes:
                if isinstance(te, dict):
                    te_id = te.get("id", "")
                else:
                    # NBTTag
                    te_id = str(te.get("id", ""))
                if not te_id:
                    continue

                # Sprawdź czy pasuje do wzorców ForgeMultipart
                matched = any(p.lower() in te_id.lower() for p in TE_PATTERNS)
                if matched:
                    if te_id not in results:
                        results[te_id] = []
                    # Konwertuj na zwykły dict jeśli to NBTTag
                    if hasattr(te, 'to_dict'):
                        te_data = te.to_dict()
                    elif hasattr(te, 'value'):
                        te_data = _nbt_to_python(te)
                    else:
                        te_data = dict(te)
                    results[te_id].append(te_data)

    return results


def _nbt_to_python(value: Any) -> Any:
    """Rekurencyjnie konwertuje NBT na typy Python."""
    from minecraft_map_parser.nbt_parser import NBTTag
    if isinstance(value, NBTTag):
        if value.type == NBTTag.TAG_COMPOUND:
            return {k: _nbt_to_python(v) for k, v in value.value.items()}
        elif value.type == NBTTag.TAG_LIST:
            return [_nbt_to_python(v) for v in value.value]
        else:
            return value.value
    elif isinstance(value, dict):
        return {k: _nbt_to_python(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_nbt_to_python(v) for v in value]
    else:
        return value


# Regiony odpowiadające strefom (+ dodatkowe losowe)
ZONE_REGIONS = [
    # billund
    "r.0.-1.mca", "r.1.-1.mca",
    # choroszcz
    "r.1.-2.mca",
    # iii_rzesza
    "r.0.5.mca", "r.0.6.mca", "r.1.5.mca", "r.1.6.mca",
    # rzym
    "r.0.0.mca", "r.0.1.mca", "r.1.0.mca", "r.1.1.mca",
    # zsrr
    "r.-6.-6.mca", "r.-6.-5.mca", "r.-6.-4.mca",
    "r.-5.-6.mca", "r.-5.-5.mca", "r.-5.-4.mca",
    # dodatkowe losowe
    "r.-1.-1.mca", "r.10.10.mca", "r.-10.-10.mca",
]


def discover_te_ids(max_regions: int = 0, region_list: List[str] | None = None) -> tuple[Dict[str, int], Dict[str, List[Dict]]]:
    """
    Odkrywa wszystkie TE ID pasujące do ForgeMultipart.
    
    Args:
        max_regions: jeśli > 0, ogranicza liczbę skanowanych regionów (dla trybu sample)
        region_list: jeśli podana, skanuje TYLKO te regiony (np. strefy)
    """
    if region_list:
        region_files = [WORLD_PATH.joinpath("region", name) for name in region_list]
        region_files = [rf for rf in region_files if rf.exists()]
    else:
        region_files = sorted(WORLD_PATH.joinpath("region").glob("r.*.*.mca"))
        if max_regions > 0:
            region_files = region_files[:max_regions]

    all_ids: Counter[str] = Counter()
    all_samples: Dict[str, List[Dict]] = {}

    print(f"Skanowanie {len(region_files)} regionów...")
    for i, rf in enumerate(region_files):
        if i % 5 == 0:
            print(f"  {i}/{len(region_files)}: {rf.name}")
        region_results = scan_region_for_te_ids(rf)
        for te_id, samples in region_results.items():
            all_ids[te_id] += len(samples)
            if te_id not in all_samples:
                all_samples[te_id] = []
            all_samples[te_id].extend(samples[:5])  # max 5 samples per region

    return dict(all_ids), all_samples


def analyze_parts(samples: List[Dict]) -> Counter[str]:
    """Analizuje jakie part-y występują w próbkach TileMultipart."""
    part_ids: Counter[str] = Counter()
    for sample in samples:
        parts = sample.get("parts", [])
        if isinstance(parts, list):
            for part in parts:
                if isinstance(part, dict):
                    pid = part.get("id", "UNKNOWN")
                    part_ids[pid] += 1
    return part_ids


def generate_report(te_counts: Dict[str, int], samples: Dict[str, List[Dict]]) -> str:
    """Generuje raport markdown."""
    lines = [
        "# Raport analizy ForgeMultipart na mapie 1.7.10",
        "",
        f"Przeskanowane regiony: `{len(list(WORLD_PATH.joinpath('region').glob('r.*.*.mca')))}`",
        f"Znalezione unikalne TE ID: `{len(te_counts)}`",
        "",
        "## Znalezione TileEntity ID",
        "",
        "| TileEntity ID | Liczba | Przykładowe part-y |",
        "|---------------|--------|-------------------|",
    ]

    try:
        from .mappings import PART_ID_1710_TO_1182
    except ImportError:
        from mappings import PART_ID_1710_TO_1182

    for te_id, count in sorted(te_counts.items(), key=lambda x: -x[1]):
        te_samples = samples.get(te_id, [])
        part_counter = analyze_parts(te_samples)
        sample_parts = ", ".join(f"{k}({v})" for k, v in part_counter.most_common(3))
        lines.append(f"| `{te_id}` | {count} | {sample_parts} |")

    lines.extend([
        "",
        "## Analiza partów (wszystkie próbki)",
        "",
    ])

    all_parts: Counter[str] = Counter()
    for te_samples in samples.values():
        all_parts.update(analyze_parts(te_samples))

    lines.extend([
        "| Part ID 1.7.10 | Liczba | Obsługiwany | Mapowanie 1.18.2 |",
        "|----------------|--------|-------------|------------------|",
    ])

    unmapped: Set[str] = set()
    for part_id, count in sorted(all_parts.items(), key=lambda x: -x[1]):
        mapped = PART_ID_1710_TO_1182.get(part_id)
        if mapped:
            status = "✅"
            mapping = f"`{mapped}`"
        else:
            status = "❌"
            mapping = "BRAK"
            unmapped.add(part_id)
        lines.append(f"| `{part_id}` | {count} | {status} | {mapping} |")

    if unmapped:
        lines.extend([
            "",
            "## ⚠️ Nieobsługiwane part-y",
            "",
            "Następujące part-y zostały znalezione na mapie ale NIE są obecnie mapowane:",
            "",
        ])
        for pid in sorted(unmapped):
            lines.append(f"- `{pid}`")
        lines.extend([
            "",
            "**Rekomendacja:** Rozszerzyć `PART_ID_1710_TO_1182` w `mappings.py` o powyższe ID.",
        ])
    else:
        lines.extend([
            "",
            "## ✅ Wszystkie znalezione part-y są obsługiwane",
        ])

    lines.append("")
    return "\n".join(lines)


def run_analysis(sample_only: bool = False, all_regions: bool = False):
    """
    Uruchamia analizę.
    Domyślnie skanuje regiony ze stref + losowe.
    Jeśli all_regions=True, skanuje CAŁĄ mapę.
    Jeśli sample_only=True, skanuje tylko pierwsze 20 regionów (szybki test).
    """
    if all_regions:
        te_counts, samples = discover_te_ids(max_regions=0, region_list=None)
    elif sample_only:
        te_counts, samples = discover_te_ids(max_regions=20, region_list=None)
    else:
        te_counts, samples = discover_te_ids(region_list=ZONE_REGIONS)

    # Zapisz surowe dane
    with open(OUTPUT_PATH / "forge_multipart_analysis.json", "w", encoding="utf-8") as f:
        json.dump({
            "te_counts": te_counts,
            "samples": {k: v[:50] for k, v in samples.items()},  # limit samples
        }, f, indent=2, ensure_ascii=False)

    # Zapisz raport
    report = generate_report(te_counts, samples)
    with open(OUTPUT_PATH / "forge_multipart_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print("\n" + "=" * 60)
    print("ANALIZA ZAKOŃCZONA")
    print("=" * 60)
    print(f"Wyniki zapisano w: {OUTPUT_PATH}")
    print(f"Znalezione TE ID: {list(te_counts.keys())}")
    print(f"Liczba TileMultipart: {te_counts.get('TileMultipart', 0)}")


if __name__ == "__main__":
    # Domyślnie skan stref; --sample = pierwsze 20 regionów; --all = cała mapa
    sample = "--sample" in sys.argv
    all_reg = "--all" in sys.argv
    run_analysis(sample_only=sample, all_regions=all_reg)
