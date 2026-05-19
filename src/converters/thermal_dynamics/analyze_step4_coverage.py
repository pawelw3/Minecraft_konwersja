"""
Krok 4: Analiza pokrycia konwersji Thermal Dynamics na mapie 1.7.10.

Sprawdza:
1. Ile bloków/TE TD jest na mapie
2. Czy każdy znaleziony blok ma mapowanie w konwerterze
3. Czy załączniki są poprawnie wykrywane w rzeczywistych NBT
4. Jakie braki (Structuralduct) występują i w jakiej ilości
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from minecraft_map_parser.anvil_parser import AnvilParser
from minecraft_map_parser.nbt_parser import NBTTag

from converters.thermal_dynamics.mappings import (
    get_mapping_for_te_id,
    is_thermal_dynamics_te,
    TE_ID_TO_BLOCK,
)


def get_nbt_value(value):
    """Wyciąga wartość z NBTTag lub zwraca bezpośrednio."""
    if isinstance(value, NBTTag):
        return value.value
    return value


def analyze_td_coverage(sample_regions: int | None = None):
    project_root = ROOT
    map_path = project_root / "mapa_1710"
    region_path = map_path / "region"

    if not region_path.exists():
        print(f"BŁĄD: Nie znaleziono folderu regionów w {region_path}")
        return

    region_files = sorted(region_path.glob("r.*.*.mca"))
    total_regions = len(region_files)
    print(f"Znaleziono {total_regions} plików regionów.")

    if sample_regions and sample_regions < total_regions:
        print(f"Analizowanie próbki {sample_regions} regionów...")
        region_files = region_files[:sample_regions]
    else:
        print(f"Analizowanie WSZYSTKICH {total_regions} regionów...")
        sample_regions = total_regions

    stats = {
        "regions_with_td": 0,
        "total_chunks_checked": 0,
        "total_td_te_found": 0,
        "td_te_by_id": Counter(),
        "td_te_mapped": Counter(),
        "td_te_unmapped": Counter(),
        "attachments_found": Counter(),
        "facades_found": Counter(),
        "regions_with_td_list": [],
        "errors": [],
    }

    for i, region_file in enumerate(region_files):
        if i % 50 == 0 and i > 0:
            print(f"  Przetworzono {i}/{len(region_files)} regionów...")

        try:
            parser = AnvilParser(str(region_file))
            chunks = parser.get_all_chunks()
            region_has_td = False
            region_coords = parser.get_region_coordinates()

            for chunk in chunks:
                stats["total_chunks_checked"] += 1

                for te in chunk.get_tile_entities():
                    te_id = str(get_nbt_value(te.get('id', '')))

                    if not is_thermal_dynamics_te(te_id):
                        continue

                    stats["total_td_te_found"] += 1
                    stats["td_te_by_id"][te_id] += 1
                    region_has_td = True

                    # Sprawdź mapowanie
                    mapping = get_mapping_for_te_id(te_id)
                    if mapping:
                        stats["td_te_mapped"][te_id] += 1
                    else:
                        stats["td_te_unmapped"][te_id] += 1

                    # Sprawdź załączniki
                    te_dict = te.to_dict() if hasattr(te, 'to_dict') else dict(te)
                    for side in range(6):
                        att_key = f"attachment{side}"
                        if att_key in te_dict:
                            att = te_dict[att_key]
                            if isinstance(att, dict) and att:
                                stats["attachments_found"][te_id] += 1

                        facade_key = f"facade{side}"
                        if facade_key in te_dict:
                            facade = te_dict[facade_key]
                            if isinstance(facade, dict) and facade:
                                stats["facades_found"][te_id] += 1

            if region_has_td:
                stats["regions_with_td"] += 1
                stats["regions_with_td_list"].append(str(region_coords))

        except Exception as e:
            stats["errors"].append(f"{region_file.name}: {type(e).__name__}: {e}")

    save_coverage_report(stats, sample_regions, total_regions)
    return stats


def save_coverage_report(stats: dict, sample_regions: int, total_regions: int):
    output_dir = Path("src/converters/thermal_dynamics")
    output_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "sample_regions": sample_regions,
        "total_regions": total_regions,
        "regions_with_td": stats["regions_with_td"],
        "total_chunks_checked": stats["total_chunks_checked"],
        "total_td_te_found": stats["total_td_te_found"],
        "td_te_by_id": dict(stats["td_te_by_id"]),
        "td_te_mapped": dict(stats["td_te_mapped"]),
        "td_te_unmapped": dict(stats["td_te_unmapped"]),
        "attachments_found": dict(stats["attachments_found"]),
        "facades_found": dict(stats["facades_found"]),
        "regions_with_td_list": stats["regions_with_td_list"],
        "errors_count": len(stats["errors"]),
        "errors": stats["errors"][:10],
    }

    json_file = output_dir / "THERMAL_DYNAMICS_STEP4_COVERAGE.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    md_file = output_dir / "THERMAL_DYNAMICS_STEP4_COVERAGE.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# Thermal Dynamics — Krok 4 (Pokrycie na mapie)\n\n")
        f.write("> Analiza rzeczywistych bloków Thermal Dynamics na mapie 1.7.10\n\n")
        f.write("## Wyniki\n\n")
        f.write(f"- **Próbkowane regiony:** {sample_regions}/{total_regions}\n")
        f.write(f"- **Regiony z TD:** {stats['regions_with_td']}\n")
        f.write(f"- **Sprawdzone chunki:** {stats['total_chunks_checked']:,}\n")
        f.write(f"- **Znalezione TE TD:** {stats['total_td_te_found']}\n\n")

        # Tabela pokrycia
        f.write("## Pokrycie konwersji\n\n")
        f.write("| Tile Entity ID | Liczba | Mapowanie | Uwagi |\n")
        f.write("|----------------|--------|-----------|-------|\n")

        for te_id, count in stats["td_te_by_id"].most_common():
            mapped_count = stats["td_te_mapped"].get(te_id, 0)
            unmapped_count = stats["td_te_unmapped"].get(te_id, 0)
            status = "[OK]" if unmapped_count == 0 else "[MISSING]"
            notes = []
            if stats["attachments_found"].get(te_id, 0) > 0:
                notes.append("ma załączniki")
            if stats["facades_found"].get(te_id, 0) > 0:
                notes.append("ma facady")
            note_str = ", ".join(notes) if notes else "-"
            f.write(f"| {te_id} | {count} | {status} | {note_str} |\n")

        # Podsumowanie
        f.write("\n## Podsumowanie\n\n")
        total_mapped = sum(stats["td_te_mapped"].values())
        total_unmapped = sum(stats["td_te_unmapped"].values())
        f.write(f"- **Zmapowane TE:** {total_mapped}/{stats['total_td_te_found']} "
                f"({100*total_mapped//max(stats['total_td_te_found'],1)}%)\n")
        f.write(f"- **Niezmapowane TE:** {total_unmapped}\n")
        f.write(f"- **TE z załącznikami:** {sum(stats['attachments_found'].values())}\n")
        f.write(f"- **TE z facadami:** {sum(stats['facades_found'].values())}\n")

        if stats["errors"]:
            f.write(f"\n## Błędy ({len(stats['errors'])})\n\n")
            for err in stats["errors"][:10]:
                f.write(f"- {err}\n")

    print(f"\n{'='*60}")
    print("RAPORT POKRYCIA (KROK 4):")
    print(f"{'='*60}")
    print(f"Próbka: {sample_regions}/{total_regions} regionów")
    print(f"Regiony z TD: {stats['regions_with_td']}")
    print(f"Sprawdzone chunki: {stats['total_chunks_checked']:,}")
    print(f"Znalezione TE TD: {stats['total_td_te_found']}")
    print(f"Zmapowane: {total_mapped} | Niezmapowane: {total_unmapped}")

    if stats["td_te_by_id"]:
        print(f"\nRozkład TE:")
        for te_id, count in stats["td_te_by_id"].most_common():
            mapped = "[OK]" if stats["td_te_unmapped"].get(te_id, 0) == 0 else "[MISSING]"
            print(f"  {mapped} {te_id}: {count}")

    print(f"\nRaport zapisano do:")
    print(f"  - {json_file}")
    print(f"  - {md_file}")


if __name__ == "__main__":
    print("="*60)
    print("THERMAL DYNAMICS — KROK 4: POKRYCIE NA MAPIE")
    print("="*60)

    # Przeanalizuj wszystkie regiony (można ograniczyć podając liczbę jako argument)
    sample = None
    if len(sys.argv) > 1:
        try:
            sample = int(sys.argv[1])
        except ValueError:
            pass

    analyze_td_coverage(sample_regions=sample)
