"""
Test integracyjny: konwersja Thermal Series TE z mapy testowej thermal_test_v2.
"""
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from minecraft_map_parser.anvil_parser import AnvilParser
from converters.thermal.thermal_converter import ThermalConverter
from converters.thermal.mappings import get_mapping_by_te_id


def test_map(world_name: str):
    world_path = ROOT / "lightweigh_map_templates" / "1710_modded" / world_name
    region_file = world_path / "region" / "r.0.0.mca"

    if not region_file.exists():
        print(f"BRAK: {region_file}")
        return False

    parser = AnvilParser(str(region_file))
    chunks = parser.get_all_chunks()

    converter = ThermalConverter()
    stats = {
        "total_te": 0,
        "converted": 0,
        "failed": 0,
        "by_id": Counter(),
        "events": [],
    }

    for chunk in chunks:
        for te in chunk.get_tile_entities():
            te_id = str(te.get('id', ''))
            if not (te_id.startswith('thermalexpansion.') or te_id.startswith('thermalfoundation.')):
                continue

            stats["total_te"] += 1
            stats["by_id"][te_id] += 1
            te_x = int(te.get('x', 0))
            te_y = int(te.get('y', 0))
            te_z = int(te.get('z', 0))

            try:
                result = converter.convert_te_by_id(te_id, te.to_dict() if hasattr(te, 'to_dict') else dict(te), (te_x, te_y, te_z))
            except Exception as e:
                print(f"  BŁĄD KONWERSJI: {te_id} at ({te_x},{te_y},{te_z}): {e}")
                stats["failed"] += 1
                continue

            if result and result.get("target_block_id"):
                stats["converted"] += 1
                stats["events"].append({
                    "pos": [te_x, te_y, te_z],
                    "from": te_id,
                    "to": result["target_block_id"],
                    "nbt": result.get("target_nbt") is not None,
                })
            else:
                print(f"  KONWERSJA NIEUDANA: {te_id} at ({te_x},{te_y},{te_z})")
                stats["failed"] += 1

    print(f"\nWynik testu integracyjnego ({world_name}):")
    print(f"  TE Thermal znaleziono: {stats['total_te']}")
    print(f"  Skonwertowane: {stats['converted']}")
    print(f"  Nieudane: {stats['failed']}")
    print(f"\n  Rozkład TE:")
    for te_id, count in stats["by_id"].most_common():
        print(f"    {te_id}: {count}")

    targets = Counter(e["to"] for e in stats["events"])
    print(f"\n  Cele konwersji:")
    for target, count in targets.most_common():
        print(f"    {target}: {count}")

    return stats["failed"] == 0


if __name__ == "__main__":
    ok1 = test_map("thermal_test_v2")
    print("\n" + "="*50 + "\n")
    ok2 = test_map("thermal_test")
    sys.exit(0 if (ok1 and ok2) else 1)
