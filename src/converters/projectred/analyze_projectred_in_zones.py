"""
Analiza bloków i TileEntity ProjectRed w strefach głównej mapy (mapa_1710).
Tylko odczyt - bez żadnych modyfikacji mapy!

Zadanie 4: Sprawdzenie pokrycia kodu konwersji dla głównej mapy.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict

# Dodaj src do path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from minecraft_map_parser.anvil_parser import AnvilParser


# Strefy z coords.json
ZONES = {
    "billund": {"x_range": (280, 602), "z_range": (-364, -81)},
    "choroszcz": {"x_range": (763, 916), "z_range": (-787, -636)},
    "iii_rzesza": {"x_range": (455, 966), "z_range": (2955, 3477)},
    "rzym": {"x_range": (301, 1005), "z_range": (163, 929)},
    "zsrr": {"x_range": (-2948, -2086), "z_range": (-2857, -1759)},
}

# ID bloków ProjectRed do wykrycia
PROJECTRED_BLOCK_PATTERNS = [
    "ProjRed",
    "projectred",
]

# ID TileEntity ProjectRed
PROJECTRED_TE_PATTERNS = [
    # Expansion
    "TileInductiveFurnace",
    "TileElectrotineGenerator",
    "TileBlockBreaker",
    "TileItemImporter",
    "TileBlockPlacer",
    "TileFilteredImporter",
    "TileFireStarter",
    "TileBatteryBox",
    "TileChargingBench",
    "TileTeleposer",
    "TileFrameMotor",
    "TileFrameActuator",
    "TileProjectBench",
    "TileAutoCrafter",
    "TileDiamondBlockBreaker",
    # Fabrication
    "TileICWorkbench",
    "TileICPrinter",
    # Illumination
    "TileLamp",
    "TileAirousLight",
    # Exploration
    "TileBarrel",
    "TileLily",
]

# Typy multipart ProjectRed
PROJECTRED_MULTIPART_TYPES = {
    # Bramki (Integration)
    "pr_sgate",      # Simple gates: AND, OR, NOT, NOR, NAND, XOR, XNOR, Buffer, Multiplexer, Repeater, etc.
    "pr_igate",      # Sequential gates: Timer, Counter, Sequencer, Pulse, StateCell
    "pr_agate",      # Array gates: NullCell, InvertCell, BufferCell, ANDCell
    "pr_bgate",      # Bundled gates: BusTransceiver, BusRandomizer, BusConverter, BusInputPanel
    "pr_tgate",      # Additional sequential gates
    "pr_icgate",     # IC Gates (Fabrication)
    # Przewody (Transmission)
    "pr_redwire",    # Red Alloy Wire
    "pr_insulated",  # Insulated Wire (16 kolorów)
    "pr_bundled",    # Bundled Cable
    "pr_framed_redwire",     # Framed Red Alloy Wire
    "pr_framed_insulated",   # Framed Insulated Wire
    "pr_framed_bundled",     # Framed Bundled Cable
    "pr_framed",     # Generic framed wire
    # Transportation
    "pr_ptube",      # Pressure Tubes
    "pr_rptube",     # Routing Pipes
}


def get_region_coords(x: int, z: int) -> Tuple[int, int]:
    """Konwertuje współrzędne świata na współrzędne regionu"""
    return (x >> 9, z >> 9)  # region = 512 bloków = 32 chunki


def get_nbt_value(val):
    """Wyciąga wartość z NBTTag lub zwraca wartość bezpośrednio"""
    if val is None:
        return None
    if hasattr(val, 'value'):
        return val.value
    return val


def is_projectred_te(te_id) -> bool:
    """Sprawdza czy TileEntity należy do ProjectRed"""
    # Wyciągnij wartość jeśli to NBTTag
    te_id_str = get_nbt_value(te_id)
    if not te_id_str or not isinstance(te_id_str, str):
        return False
    # Sprawdź wzorce
    for pattern in PROJECTRED_TE_PATTERNS:
        if pattern.lower() in te_id_str.lower():
            return True
    # Sprawdź prefix
    for pattern in PROJECTRED_BLOCK_PATTERNS:
        if pattern.lower() in te_id_str.lower():
            return True
    return False


def extract_multipart_info(te: Dict) -> List[Dict]:
    """Wyciąga informacje o częściach multipart z TileEntity ForgeMultipart"""
    parts = []

    # Sprawdź czy to jest multipart container
    if 'savedParts' not in te and 'parts' not in te:
        return parts

    # FMP zapisuje parts w 'parts' lub 'savedParts'
    raw_parts = get_nbt_value(te.get('parts')) or get_nbt_value(te.get('savedParts', []))
    if raw_parts is None:
        return parts

    # raw_parts może być listą obiektów NBTTag
    if hasattr(raw_parts, '__iter__') and not isinstance(raw_parts, (str, bytes)):
        for part in raw_parts:
            part_dict = get_nbt_value(part)
            if isinstance(part_dict, dict):
                part_id = get_nbt_value(part_dict.get('id', ''))
                if not isinstance(part_id, str):
                    continue
                # Sprawdź czy to część ProjectRed
                if any(part_id.startswith(p) for p in PROJECTRED_MULTIPART_TYPES):
                    part_info = {
                        'type': part_id,
                        'nbt': part_dict,
                        'subID': get_nbt_value(part_dict.get('subID', -1)) or -1,
                        'orient': get_nbt_value(part_dict.get('orient', -1)) or -1,
                        'colour': get_nbt_value(part_dict.get('colour', -1)) or -1,
                    }
                    parts.append(part_info)

    return parts


def analyze_zone(zone_name: str, zone_data: dict, map_path: Path) -> Dict[str, Any]:
    """Analizuje strefę pod kątem bloków ProjectRed"""

    x_range = zone_data["x_range"]
    z_range = zone_data["z_range"]

    # Znajdź regiony do sprawdzenia
    regions_to_check = set()
    for x in range(x_range[0], x_range[1] + 1, 512):  # co region (512 bloków)
        for z in range(z_range[0], z_range[1] + 1, 512):
            rx, rz = get_region_coords(x, z)
            regions_to_check.add((rx, rz))

    # Dodaj regiony na granicach
    for x in [x_range[0], x_range[1]]:
        for z in [z_range[0], z_range[1]]:
            rx, rz = get_region_coords(x, z)
            regions_to_check.add((rx, rz))

    print(f"\n{'='*60}")
    print(f"Strefa: {zone_name}")
    print(f"Zakres X: {x_range}, Z: {z_range}")
    print(f"Regiony do sprawdzenia: {len(regions_to_check)}")
    print(f"{'='*60}")

    # Statystyki
    stats = {
        "zone": zone_name,
        "regions_checked": 0,
        "chunks_checked": 0,
        "pr_blocks_found": defaultdict(int),
        "pr_tile_entities": defaultdict(int),
        "pr_multipart_parts": defaultdict(int),
        "pr_gate_types": defaultdict(int),  # subID -> count
        "pr_wire_colors": defaultdict(int),  # colour -> count
        "sample_positions": [],  # przykładowe pozycje (do 10)
        "errors": []
    }

    for rx, rz in sorted(regions_to_check):
        region_file = map_path / f"region/r.{rx}.{rz}.mca"

        if not region_file.exists():
            continue

        stats["regions_checked"] += 1
        print(f"  Sprawdzam region {rx},{rz}...", end=" ")

        try:
            parser = AnvilParser(str(region_file))
            chunks = parser.get_all_chunks()
            chunks_in_zone = 0

            for chunk in chunks:
                # Sprawdź czy chunk jest w strefie
                chunk_x_world = chunk.x * 16
                chunk_z_world = chunk.z * 16

                # Chunk jest 16x16, więc sprawdzamy czy jakikolwiek blok jest w strefie
                if not (chunk_x_world + 16 >= x_range[0] and chunk_x_world <= x_range[1] and
                        chunk_z_world + 16 >= z_range[0] and chunk_z_world <= z_range[1]):
                    continue

                chunks_in_zone += 1
                stats["chunks_checked"] += 1

                # Sprawdź tile entities
                for te in chunk.get_tile_entities():
                    te_id_raw = te.get('id', '')
                    te_id = get_nbt_value(te_id_raw)
                    if not isinstance(te_id, str):
                        te_id = str(te_id) if te_id else ''

                    # Sprawdź czy to ProjectRed TE
                    if is_projectred_te(te_id):
                        stats["pr_tile_entities"][te_id] += 1

                        # Zapisz przykładową pozycję
                        if len(stats["sample_positions"]) < 10:
                            x = get_nbt_value(te.get('x', 0)) or 0
                            y = get_nbt_value(te.get('y', 0)) or 0
                            z = get_nbt_value(te.get('z', 0)) or 0
                            pos = (x, y, z)
                            stats["sample_positions"].append({
                                'pos': pos,
                                'type': te_id,
                                'nbt_keys': list(te.keys()) if hasattr(te, 'keys') else []
                            })

                    # Sprawdź multipart (ForgeMultipart / CB Multipart)
                    if 'savedParts' in te or 'parts' in te:
                        parts = extract_multipart_info(te)
                        for part in parts:
                            part_type = part['type']
                            stats["pr_multipart_parts"][part_type] += 1

                            # Zlicz typy bramek (subID)
                            sub_id = part['subID']
                            if 'gate' in part_type and sub_id is not None and sub_id >= 0:
                                stats["pr_gate_types"][sub_id] += 1

                            # Zlicz kolory przewodów
                            colour = part['colour']
                            if colour is not None and colour >= 0:
                                stats["pr_wire_colors"][colour] += 1

                            # Zapisz przykładową pozycję
                            if len(stats["sample_positions"]) < 20:
                                x = get_nbt_value(te.get('x', 0)) or 0
                                y = get_nbt_value(te.get('y', 0)) or 0
                                z = get_nbt_value(te.get('z', 0)) or 0
                                pos = (x, y, z)
                                stats["sample_positions"].append({
                                    'pos': pos,
                                    'type': f"multipart:{part_type}",
                                    'subID': sub_id,
                                    'nbt_keys': list(part['nbt'].keys()) if part['nbt'] else []
                                })

            print(f"{chunks_in_zone} chunków w strefie")

        except Exception as e:
            stats["errors"].append(f"Region {rx},{rz}: {str(e)}")
            print(f"BŁĄD: {e}")

    return stats


def analyze_all_zones():
    """Analizuje wszystkie strefy"""
    map_path = Path("mapa_1710")

    if not map_path.exists():
        # Spróbuj względnej ścieżki
        map_path = Path(__file__).parent.parent.parent.parent / "mapa_1710"

    if not map_path.exists():
        print(f"BŁĄD: Nie znaleziono mapy w {map_path}")
        print(f"Sprawdź ścieżkę: {map_path.absolute()}")
        return

    print(f"Mapa: {map_path.absolute()}")

    all_results = []

    for zone_name, zone_data in ZONES.items():
        result = analyze_zone(zone_name, zone_data, map_path)
        all_results.append(result)

        # Podsumowanie strefy
        print(f"\n--- Podsumowanie strefy {zone_name} ---")
        print(f"Sprawdzone regiony: {result['regions_checked']}")
        print(f"Sprawdzone chunki: {result['chunks_checked']}")

        if result['pr_tile_entities']:
            print(f"\nZnalezione Tile Entities ProjectRed:")
            for te_id, count in sorted(result['pr_tile_entities'].items()):
                print(f"  - {te_id}: {count}")

        if result['pr_multipart_parts']:
            print(f"\nZnalezione części Multipart ProjectRed:")
            for part_type, count in sorted(result['pr_multipart_parts'].items()):
                print(f"  - {part_type}: {count}")

        if not result['pr_tile_entities'] and not result['pr_multipart_parts']:
            print("\nBrak elementów ProjectRed w tej strefie")

        if result['errors']:
            print(f"\nBłędy ({len(result['errors'])}):")
            for err in result['errors'][:5]:
                print(f"  ! {err}")

    # Zapisz raport i sprawdź pokrycie
    save_report_and_check_coverage(all_results)


def save_report_and_check_coverage(results: List[Dict]):
    """Zapisuje raport i sprawdza pokrycie kodu konwersji"""
    output_dir = Path(__file__).parent / "zone_analysis"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Podsumowanie wszystkich stref
    summary = {
        "total_regions": sum(r['regions_checked'] for r in results),
        "total_chunks": sum(r['chunks_checked'] for r in results),
        "zones_with_projectred": [],
        "all_pr_te": defaultdict(int),
        "all_pr_multipart": defaultdict(int),
        "all_gate_types": defaultdict(int),
        "all_wire_colors": defaultdict(int),
        "sample_positions": [],
        "coverage_report": {}
    }

    for r in results:
        if r['pr_tile_entities'] or r['pr_multipart_parts']:
            summary["zones_with_projectred"].append(r['zone'])

        for te_id, count in r['pr_tile_entities'].items():
            summary["all_pr_te"][te_id] += count

        for part_type, count in r['pr_multipart_parts'].items():
            summary["all_pr_multipart"][part_type] += count

        for gate_type, count in r['pr_gate_types'].items():
            summary["all_gate_types"][gate_type] += count

        for color, count in r['pr_wire_colors'].items():
            summary["all_wire_colors"][color] += count

        summary["sample_positions"].extend(r.get("sample_positions", []))

    # Konwertuj defaultdict do dict dla JSON
    summary["all_pr_te"] = dict(summary["all_pr_te"])
    summary["all_pr_multipart"] = dict(summary["all_pr_multipart"])
    summary["all_gate_types"] = dict(summary["all_gate_types"])
    summary["all_wire_colors"] = dict(summary["all_wire_colors"])

    # ===== SPRAWDZENIE POKRYCIA KODU KONWERSJI =====
    print("\n" + "="*60)
    print("SPRAWDZENIE POKRYCIA KODU KONWERSJI")
    print("="*60)

    # Importuj mappingi z konwertera
    try:
        from mappings.block_mappings import (
            ALL_PROJECTRED_BLOCK_IDS_1710,
            MACHINE1_MAPPINGS,
            MACHINE2_MAPPINGS,
            ORE_MAPPINGS,
            STONE_MAPPINGS,
            IC_BLOCK_MAPPINGS,
        )
        from nbt_converters.multipart_converters import GATE_TYPE_NAMES
        mapping_available = True
    except ImportError as e:
        print(f"UWAGA: Nie udało się zaimportować mappingów: {e}")
        mapping_available = False

    # Kolory przewodów (standardowe kolory Minecraft)
    WIRE_COLOR_NAMES = {
        0: "white", 1: "orange", 2: "magenta", 3: "light_blue",
        4: "yellow", 5: "lime", 6: "pink", 7: "gray",
        8: "light_gray", 9: "cyan", 10: "purple", 11: "blue",
        12: "brown", 13: "green", 14: "red", 15: "black"
    }

    # Mapowanie TileEntity -> metadata dla machine2
    TE_TO_METADATA = {
        'TileBlockBreaker': 0,
        'TileItemImporter': 1,
        'TileBlockPlacer': 2,
        'TileFilteredImporter': 3,
        'TileFireStarter': 4,
        'TileBatteryBox': 5,
        'TileChargingBench': 6,
        'TileTeleposer': 7,
        'TileFrameMotor': 8,
        'TileFrameActuator': 9,
        'TileProjectBench': 10,
        'TileAutoCrafter': 11,
        'TileDiamondBlockBreaker': 12,
    }

    coverage = {
        "tile_entities": {
            "found": list(summary["all_pr_te"].keys()),
            "supported": [],
            "not_supported": [],
            "removed_in_1182": [],
        },
        "multipart_parts": {
            "found": list(summary["all_pr_multipart"].keys()),
            "supported": [],
            "not_supported": [],
        },
        "gate_types": {
            "found": list(summary["all_gate_types"].keys()),
            "supported": [],
            "not_supported": [],
        },
    }

    # Sprawdź pokrycie TileEntity
    # Format ID na mapie: tile.projectred.<module>.<block>|<meta>
    # np. tile.projectred.expansion.machine2|10
    if mapping_available:
        for te_id in summary["all_pr_te"].keys():
            # Parsuj format tile.projectred.<module>.<block>|<meta>
            meta = -1
            block_type = ""

            if "|" in te_id:
                parts = te_id.rsplit("|", 1)
                base_id = parts[0]
                try:
                    meta = int(parts[1])
                except ValueError:
                    meta = -1

                # Wyciągnij typ bloku (np. machine2, lamp, icblock)
                if "expansion.machine2" in base_id:
                    block_type = "machine2"
                elif "expansion.machine1" in base_id:
                    block_type = "machine1"
                elif "illumination.lamp" in base_id:
                    block_type = "lamp"
                elif "integration.icblock" in base_id or "fabrication.icblock" in base_id:
                    block_type = "icblock"
                elif "exploration.lily" in base_id:
                    block_type = "lily"
                elif "expansion.frame" in base_id:
                    block_type = "frame"
            else:
                # Stary format TileXxx
                te_name = te_id.split(":")[-1] if ":" in te_id else te_id
                meta = TE_TO_METADATA.get(te_name, -1)
                if meta >= 0:
                    block_type = "machine2"

            # Sprawdź pokrycie na podstawie typu bloku i meta
            if block_type == "machine2" and meta >= 0:
                mapping = MACHINE2_MAPPINGS.get(meta)
                if mapping:
                    if mapping.removed:
                        coverage["tile_entities"]["removed_in_1182"].append(te_id)
                    else:
                        coverage["tile_entities"]["supported"].append(te_id)
                else:
                    coverage["tile_entities"]["not_supported"].append(te_id)
            elif block_type == "machine1" and meta >= 0:
                mapping = MACHINE1_MAPPINGS.get(meta)
                if mapping:
                    if mapping.removed:
                        coverage["tile_entities"]["removed_in_1182"].append(te_id)
                    else:
                        coverage["tile_entities"]["supported"].append(te_id)
                else:
                    coverage["tile_entities"]["not_supported"].append(te_id)
            elif block_type == "icblock" and meta >= 0:
                mapping = IC_BLOCK_MAPPINGS.get(meta)
                if mapping:
                    if mapping.removed:
                        coverage["tile_entities"]["removed_in_1182"].append(te_id)
                    else:
                        coverage["tile_entities"]["supported"].append(te_id)
                else:
                    coverage["tile_entities"]["not_supported"].append(te_id)
            elif block_type == "lamp":
                # Lampy są wspierane (16 kolorów)
                coverage["tile_entities"]["supported"].append(te_id)
            elif block_type == "lily":
                # Lilie - USUNIĘTE w 1.18.2 (zamiana na vanilla flowers)
                coverage["tile_entities"]["removed_in_1182"].append(te_id)
            elif block_type == "frame":
                # Frame - wspierane
                coverage["tile_entities"]["supported"].append(te_id)
            else:
                coverage["tile_entities"]["not_supported"].append(te_id)

        # Sprawdź pokrycie multipart
        SUPPORTED_MULTIPART = {
            "pr_sgate", "pr_igate", "pr_agate", "pr_bgate",
            "pr_redwire", "pr_insulated", "pr_bundled", "pr_framed"
        }
        for part_type in summary["all_pr_multipart"].keys():
            if part_type in SUPPORTED_MULTIPART:
                coverage["multipart_parts"]["supported"].append(part_type)
            else:
                coverage["multipart_parts"]["not_supported"].append(part_type)

        # Sprawdź pokrycie typów bramek (0-33)
        for gate_id in summary["all_gate_types"].keys():
            if 0 <= int(gate_id) <= 33:
                coverage["gate_types"]["supported"].append(gate_id)
            else:
                coverage["gate_types"]["not_supported"].append(gate_id)

    summary["coverage_report"] = coverage

    # Zapisz JSON
    report_file = output_dir / "projectred_zone_analysis.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": summary,
            "zones": [{
                "zone": r["zone"],
                "regions_checked": r["regions_checked"],
                "chunks_checked": r["chunks_checked"],
                "pr_tile_entities": dict(r["pr_tile_entities"]),
                "pr_multipart_parts": dict(r["pr_multipart_parts"]),
                "errors": r["errors"]
            } for r in results]
        }, f, indent=2, ensure_ascii=False, default=str)

    # Zapisz raport tekstowy
    text_report = output_dir / "projectred_zone_analysis.txt"
    with open(text_report, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("RAPORT ANALIZY PROJECTRED W STREFACH MAPY 1.7.10\n")
        f.write("Zadanie 4: Sprawdzenie pokrycia kodu konwersji\n")
        f.write("="*60 + "\n\n")

        f.write(f"Całkowita liczba regionów: {summary['total_regions']}\n")
        f.write(f"Całkowita liczba chunków: {summary['total_chunks']}\n")
        f.write(f"Strefy z ProjectRed: {', '.join(summary['zones_with_projectred']) if summary['zones_with_projectred'] else 'Brak'}\n\n")

        f.write("-"*60 + "\n")
        f.write("ZNALEZIONE TILE ENTITIES PROJECTRED:\n")
        f.write("-"*60 + "\n")
        for te_id, count in sorted(summary['all_pr_te'].items()):
            if te_id in coverage["tile_entities"]["supported"]:
                status = "✅ WSPIERANE"
            elif te_id in coverage["tile_entities"]["removed_in_1182"]:
                status = "⚠️ USUNIĘTE W 1.18.2"
            else:
                status = "❌ NIE WSPIERANE"
            f.write(f"{status} | {te_id}: {count}\n")

        f.write("\n" + "-"*60 + "\n")
        f.write("ZNALEZIONE CZĘŚCI MULTIPART:\n")
        f.write("-"*60 + "\n")
        for part_type, count in sorted(summary['all_pr_multipart'].items()):
            if part_type in coverage["multipart_parts"]["supported"]:
                status = "✅"
            else:
                status = "❌"
            f.write(f"{status} {part_type}: {count}\n")

        if summary['all_gate_types']:
            f.write("\n" + "-"*60 + "\n")
            f.write("TYPY BRAMEK (subID):\n")
            f.write("-"*60 + "\n")
            for gate_id, count in sorted(summary['all_gate_types'].items(), key=lambda x: int(x[0])):
                f.write(f"  subID={gate_id}: {count}\n")

        if summary['all_wire_colors']:
            f.write("\n" + "-"*60 + "\n")
            f.write("KOLORY PRZEWODÓW:\n")
            f.write("-"*60 + "\n")
            for color, count in sorted(summary['all_wire_colors'].items(), key=lambda x: int(x[0])):
                f.write(f"  colour={color}: {count}\n")

        f.write("\n" + "="*60 + "\n")
        f.write("RAPORT POKRYCIA KODU KONWERSJI:\n")
        f.write("="*60 + "\n\n")

        # TileEntity
        total_te = len(coverage['tile_entities']['found'])
        supported_te = len(coverage['tile_entities']['supported'])
        removed_te = len(coverage['tile_entities']['removed_in_1182'])
        not_supported_te = len(coverage['tile_entities']['not_supported'])

        f.write(f"Tile Entities:\n")
        f.write(f"  - Znalezione na mapie: {total_te}\n")
        f.write(f"  - Wspierane przez konwerter: {supported_te}\n")
        f.write(f"  - Usunięte w 1.18.2 (z ostrzeżeniem): {removed_te}\n")
        f.write(f"  - NIE wspierane: {not_supported_te}\n")
        if total_te > 0:
            coverage_pct = (supported_te + removed_te) / total_te * 100
            f.write(f"  - POKRYCIE: {coverage_pct:.1f}%\n")

        # Multipart
        total_mp = len(coverage['multipart_parts']['found'])
        supported_mp = len(coverage['multipart_parts']['supported'])
        not_supported_mp = len(coverage['multipart_parts']['not_supported'])

        f.write(f"\nMultipart Parts:\n")
        f.write(f"  - Znalezione na mapie: {total_mp}\n")
        f.write(f"  - Wspierane przez konwerter: {supported_mp}\n")
        f.write(f"  - NIE wspierane: {not_supported_mp}\n")
        if total_mp > 0:
            coverage_pct = supported_mp / total_mp * 100
            f.write(f"  - POKRYCIE: {coverage_pct:.1f}%\n")

        # Gates
        if coverage['gate_types']['found']:
            total_gates = len(coverage['gate_types']['found'])
            supported_gates = len(coverage['gate_types']['supported'])
            f.write(f"\nTypy bramek:\n")
            f.write(f"  - Znalezione typy: {total_gates}\n")
            f.write(f"  - Wspierane przez konwerter: {supported_gates}\n")

        # Niewspierane
        if coverage['tile_entities']['not_supported']:
            f.write("\n" + "-"*60 + "\n")
            f.write("⚠️ NIEWSPIERANE TILE ENTITIES:\n")
            f.write("-"*60 + "\n")
            for te_id in coverage['tile_entities']['not_supported']:
                count = summary['all_pr_te'].get(te_id, 0)
                f.write(f"  - {te_id}: {count}\n")

        if coverage['multipart_parts']['not_supported']:
            f.write("\n" + "-"*60 + "\n")
            f.write("⚠️ NIEWSPIERANE CZĘŚCI MULTIPART:\n")
            f.write("-"*60 + "\n")
            for part_type in coverage['multipart_parts']['not_supported']:
                count = summary['all_pr_multipart'].get(part_type, 0)
                f.write(f"  - {part_type}: {count}\n")

        # Sample positions
        if summary['sample_positions']:
            f.write("\n" + "-"*60 + "\n")
            f.write("PRZYKŁADOWE POZYCJE (do weryfikacji):\n")
            f.write("-"*60 + "\n")
            for sample in summary['sample_positions'][:15]:
                f.write(f"  {sample['type']} @ {sample['pos']}\n")

    print(f"\n{'='*60}")
    print("Raport zapisano do:")
    print(f"  - {report_file}")
    print(f"  - {text_report}")
    print(f"{'='*60}")

    # Wyświetl podsumowanie
    print("\n" + "="*60)
    print("PODSUMOWANIE POKRYCIA KODU:")
    print("="*60)

    total_elements = (
        len(coverage['tile_entities']['found']) +
        len(coverage['multipart_parts']['found'])
    )
    supported_elements = (
        len(coverage['tile_entities']['supported']) +
        len(coverage['tile_entities']['removed_in_1182']) +
        len(coverage['multipart_parts']['supported'])
    )

    if total_elements > 0:
        coverage_pct = supported_elements / total_elements * 100
        print(f"Całkowite pokrycie: {coverage_pct:.1f}% ({supported_elements}/{total_elements})")

        if coverage['tile_entities']['not_supported'] or coverage['multipart_parts']['not_supported']:
            print("\n⚠️ UWAGA: Znaleziono elementy bez pokrycia!")
            for te_id in coverage['tile_entities']['not_supported']:
                print(f"  - TE: {te_id}")
            for part_type in coverage['multipart_parts']['not_supported']:
                print(f"  - MP: {part_type}")
        else:
            print("\n✅ Wszystkie znalezione elementy są wspierane przez konwerter!")
    else:
        print("Nie znaleziono żadnych elementów ProjectRed na mapie")


if __name__ == "__main__":
    print("="*60)
    print("ANALIZA PROJECTRED W STREFACH GŁÓWNEJ MAPY")
    print("TRYB: TYLKO ODCZYT (brak modyfikacji mapy)")
    print("="*60)

    analyze_all_zones()
