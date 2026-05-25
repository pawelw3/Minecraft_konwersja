"""
Test integracyjny: konwersja TD TE z mapy testowej thermal_test_v2.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from minecraft_map_parser.anvil_parser import AnvilParser
from converters.thermal_dynamics.thermal_dynamics_converter import ThermalDynamicsConverter
from converters.thermal_dynamics.mappings import get_mapping_for_te_id


def test_thermal_test_v2():
    world_path = ROOT / "lightweigh_map_templates" / "1710_modded" / "thermal_test_v2"
    region_file = world_path / "region" / "r.0.0.mca"

    if not region_file.exists():
        print(f"BRAK: {region_file}")
        return False

    parser = AnvilParser(str(region_file))
    chunks = parser.get_all_chunks()

    converter = ThermalDynamicsConverter()
    stats = {
        "total_te": 0,
        "converted": 0,
        "failed": 0,
        "events": [],
    }

    for chunk in chunks:
        for te in chunk.get_tile_entities():
            te_id = str(te.get('id', ''))
            if not te_id.startswith('thermaldynamics'):
                continue

            stats["total_te"] += 1
            te_x = int(te.get('x', 0))
            te_y = int(te.get('y', 0))
            te_z = int(te.get('z', 0))

            mapping = get_mapping_for_te_id(te_id)
            if not mapping:
                print(f"  BRAK MAPPINGU: {te_id} at ({te_x},{te_y},{te_z})")
                stats["failed"] += 1
                continue

            result = converter.convert_block(
                block_id_1710=mapping.source_block_id,
                metadata=mapping.metadata,
                nbt_1710=te.to_dict() if hasattr(te, 'to_dict') else dict(te),
                position=(te_x, te_y, te_z),
            )

            if result.converted.success and result.converted.block_id_1182:
                stats["converted"] += 1
                stats["events"].append({
                    "pos": [te_x, te_y, te_z],
                    "from": te_id,
                    "to": result.converted.block_id_1182,
                    "nbt": result.converted.nbt_1182 is not None,
                    "extra_events": len(getattr(result.converted, 'extra_events', [])),
                })
            else:
                print(f"  KONWERSJA NIEUDANA: {te_id} at ({te_x},{te_y},{te_z})")
                stats["failed"] += 1

    print(f"\nWynik testu integracyjnego (thermal_test_v2):")
    print(f"  TD TE znaleziono: {stats['total_te']}")
    print(f"  Skonwertowane: {stats['converted']}")
    print(f"  Nieudane: {stats['failed']}")

    for ev in stats["events"]:
        print(f"  {ev['from']} -> {ev['to']} at {ev['pos']} (NBT:{ev['nbt']}, extras:{ev['extra_events']})")

    return stats["failed"] == 0


if __name__ == "__main__":
    ok = test_thermal_test_v2()
    sys.exit(0 if ok else 1)
