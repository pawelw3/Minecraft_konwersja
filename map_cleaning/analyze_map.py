"""
Skrypt do analizy mapy Minecraft 1.7.10 - pokazuje statystyki:
- Liczbę regionów, chunków
- Bloki z modów (nie-vanilla)
- Tile Entities (z podziałem na typy)
- Entities (z podziałem na typy)
"""
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from minecraft_map_parser.anvil_parser import AnvilParser, ChunkData
from minecraft_map_parser.nbt_parser import NBTTag


# Vanilla block IDs w Minecraft 1.7.10 (0-197)
VANILLA_BLOCK_IDS = set(range(0, 198))
VANILLA_BLOCK_IDS.add(159)  # stained_hardened_clay
VANILLA_BLOCK_IDS.add(160)  # stained_glass_pane
VANILLA_BLOCK_IDS.add(161)  # leaves2
VANILLA_BLOCK_IDS.add(162)  # log2
VANILLA_BLOCK_IDS.add(163)  # acacia_stairs
VANILLA_BLOCK_IDS.add(164)  # dark_oak_stairs
VANILLA_BLOCK_IDS.add(165)  # slime
VANILLA_BLOCK_IDS.add(166)  # barrier (ale to techniczne)
VANILLA_BLOCK_IDS.add(167)  # iron_trapdoor
VANILLA_BLOCK_IDS.add(168)  # prismarine
VANILLA_BLOCK_IDS.add(169)  # sea_lantern
VANILLA_BLOCK_IDS.add(170)  # hay_block
VANILLA_BLOCK_IDS.add(171)  # carpet
VANILLA_BLOCK_IDS.add(172)  # hardened_clay
VANILLA_BLOCK_IDS.add(173)  # coal_block
VANILLA_BLOCK_IDS.add(174)  # packed_ice
VANILLA_BLOCK_IDS.add(175)  # double_plant
# Dodaj pozostałe vanilla IDs jeśli występują


def get_block_id_from_section(section: Dict, local_x: int, local_y: int, local_z: int) -> int:
    """Pobiera ID bloku z sekcji."""
    blocks = section.get('Blocks')
    if blocks is None:
        return 0
    
    if isinstance(blocks, NBTTag):
        blocks = blocks.value
    if blocks is None:
        return 0
    
    index = local_y * 256 + local_z * 16 + local_x
    
    if isinstance(blocks, (list, tuple, bytes, bytearray)):
        if 0 <= index < len(blocks):
            val = blocks[index]
            if isinstance(val, int):
                return val
            elif isinstance(val, str):
                return ord(val)
            else:
                return int(val)
    return 0


def analyze_region(region_file: Path, verbose: bool = False) -> Dict:
    """Analizuje pojedynczy plik regionu."""
    result = {
        "chunks_analyzed": 0,
        "chunks_empty": 0,
        "mod_blocks": Counter(),  # id -> count
        "mod_block_positions": [],  # (x, y, z, id)
        "tile_entities": Counter(),  # id -> count
        "tile_entity_positions": [],  # (x, y, z, id)
        "entities": Counter(),  # id -> count
        "entity_positions": [],  # (x, y, z, id)
        "errors": []
    }
    
    try:
        parser = AnvilParser(str(region_file))
        
        for chunk_z in range(32):
            for chunk_x in range(32):
                try:
                    chunk = parser.get_chunk(chunk_x, chunk_z)
                    if chunk is None:
                        result["chunks_empty"] += 1
                        continue
                    
                    result["chunks_analyzed"] += 1
                    
                    # Analizuj sekcje (bloki)
                    sections = chunk.get_sections()
                    for section in sections:
                        if not isinstance(section, dict):
                            continue
                            
                        y_section = section.get('Y')
                        if isinstance(y_section, NBTTag):
                            y_section = y_section.value
                        if y_section is None:
                            continue
                        
                        for y in range(16):
                            world_y = y_section * 16 + y
                            for z in range(16):
                                for x in range(16):
                                    block_id = get_block_id_from_section(section, x, y, z)
                                    
                                    if block_id not in VANILLA_BLOCK_IDS and block_id != 0:
                                        world_x = chunk.x * 16 + x
                                        world_z = chunk.z * 16 + z
                                        result["mod_blocks"][block_id] += 1
                                        result["mod_block_positions"].append((world_x, world_y, world_z, block_id))
                    
                    # Analizuj Tile Entities
                    tile_entities = chunk.get_tile_entities()
                    for te in tile_entities:
                        if not isinstance(te, dict):
                            continue
                        
                        te_id = te.get('id')
                        if isinstance(te_id, NBTTag):
                            te_id = te_id.value
                        te_id = str(te_id) if te_id else "unknown"
                        
                        x = te.get('x')
                        y = te.get('y')
                        z = te.get('z')
                        if isinstance(x, NBTTag):
                            x = x.value
                        if isinstance(y, NBTTag):
                            y = y.value
                        if isinstance(z, NBTTag):
                            z = z.value
                        
                        if x is not None and y is not None and z is not None:
                            result["tile_entities"][te_id] += 1
                            result["tile_entity_positions"].append((int(x), int(y), int(z), te_id))
                    
                    # Analizuj Entities
                    entities = chunk.get_entities()
                    for entity in entities:
                        if not isinstance(entity, dict):
                            continue
                        
                        entity_id = entity.get('id')
                        if isinstance(entity_id, NBTTag):
                            entity_id = entity_id.value
                        entity_id = str(entity_id) if entity_id else "unknown"
                        
                        pos = entity.get('Pos')
                        if isinstance(pos, NBTTag):
                            pos = pos.value
                        
                        x = y = z = None
                        if isinstance(pos, (list, tuple)) and len(pos) >= 3:
                            x, y, z = pos[0], pos[1], pos[2]
                            if isinstance(x, NBTTag):
                                x = x.value
                            if isinstance(y, NBTTag):
                                y = y.value
                            if isinstance(z, NBTTag):
                                z = z.value
                        
                        result["entities"][entity_id] += 1
                        if x is not None and y is not None and z is not None:
                            result["entity_positions"].append((float(x), float(y), float(z), entity_id))
                
                except Exception as e:
                    if verbose:
                        result["errors"].append(f"Chunk ({chunk_x},{chunk_z}): {e}")
    
    except Exception as e:
        result["errors"].append(f"Region file: {e}")
    
    return result


def analyze_world(world_path: Path, regions_filter: Optional[List[Tuple[int, int]]] = None, verbose: bool = False) -> Dict:
    """Analizuje cały świat."""
    region_path = world_path / "region"
    
    if not region_path.exists():
        print(f"Błąd: Nie znaleziono katalogu region: {region_path}")
        return {}
    
    region_files = list(region_path.glob("r.*.mca"))
    
    if regions_filter:
        filtered_files = []
        for rx, rz in regions_filter:
            rfile = region_path / f"r.{rx}.{rz}.mca"
            if rfile.exists():
                filtered_files.append(rfile)
        region_files = filtered_files
    
    print(f"Znaleziono {len(region_files)} plików regionów")
    
    total = {
        "chunks_analyzed": 0,
        "chunks_empty": 0,
        "mod_blocks": Counter(),
        "mod_block_positions": [],
        "tile_entities": Counter(),
        "tile_entity_positions": [],
        "entities": Counter(),
        "entity_positions": [],
        "errors": []
    }
    
    for i, region_file in enumerate(sorted(region_files), 1):
        print(f"[{i}/{len(region_files)}] Analiza {region_file.name}...")
        
        region_result = analyze_region(region_file, verbose)
        
        total["chunks_analyzed"] += region_result["chunks_analyzed"]
        total["chunks_empty"] += region_result["chunks_empty"]
        total["mod_blocks"].update(region_result["mod_blocks"])
        total["mod_block_positions"].extend(region_result["mod_block_positions"])
        total["tile_entities"].update(region_result["tile_entities"])
        total["tile_entity_positions"].extend(region_result["tile_entity_positions"])
        total["entities"].update(region_result["entities"])
        total["entity_positions"].extend(region_result["entity_positions"])
        total["errors"].extend(region_result["errors"])
    
    return total


def print_report(results: Dict):
    """Drukuje raport z analizy."""
    print("\n" + "=" * 70)
    print("RAPORT ANALIZY MAPY")
    print("=" * 70)
    
    print(f"\n[OGOLNE STATYSTYKI]")
    print(f"  Przeanalizowane chunki: {results['chunks_analyzed']}")
    print(f"  Puste chunki: {results['chunks_empty']}")
    
    print(f"\n[BLOKI Z MODOW (nie-vanilla)]")
    if results["mod_blocks"]:
        print(f"  Całkowita liczba: {sum(results['mod_blocks'].values())}")
        print(f"  Unikalne ID: {len(results['mod_blocks'])}")
        print(f"  Top 20 bloków:")
        for block_id, count in results["mod_blocks"].most_common(20):
            print(f"    ID {block_id}: {count} bloków")
    else:
        print("  Brak bloków z modów")
    
    print(f"\n[TILE ENTITIES]")
    if results["tile_entities"]:
        print(f"  Całkowita liczba: {sum(results['tile_entities'].values())}")
        print(f"  Unikalne typy: {len(results['tile_entities'])}")
        print(f"  Top 20 typów:")
        for te_id, count in results["tile_entities"].most_common(20):
            print(f"    {te_id}: {count}")
    else:
        print("  Brak tile entities")
    
    print(f"\n[ENTITIES]")
    if results["entities"]:
        print(f"  Całkowita liczba: {sum(results['entities'].values())}")
        print(f"  Unikalne typy: {len(results['entities'])}")
        print(f"  Top 20 typów:")
        for entity_id, count in results["entities"].most_common(20):
            print(f"    {entity_id}: {count}")
    else:
        print("  Brak entities")
    
    if results["errors"]:
        print(f"\n[BLENDY ({len(results['errors'])})]:")
        for error in results["errors"][:10]:
            print(f"  - {error}")
        if len(results["errors"]) > 10:
            print(f"  ... i {len(results['errors']) - 10} więcej")
    
    print("\n" + "=" * 70)


def save_detailed_report(results: Dict, output_file: Path):
    """Zapisuje szczegółowy raport do pliku JSON."""
    # Konwertuj Counter na dict dla JSON
    data = {
        "chunks_analyzed": results["chunks_analyzed"],
        "chunks_empty": results["chunks_empty"],
        "mod_blocks": dict(results["mod_blocks"]),
        "tile_entities": dict(results["tile_entities"]),
        "entities": dict(results["entities"]),
        "errors": results["errors"]
    }
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n[Szczegolowy raport zapisano do: {output_file}]")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Analizuje mapę Minecraft 1.7.10"
    )
    parser.add_argument(
        "--world",
        type=Path,
        default=Path(__file__).parent.parent / "mapa_1710",
        help="Ścieżka do świata (domyślnie: ../mapa_1710)"
    )
    parser.add_argument(
        "--region",
        type=str,
        help="Przetwórz tylko konkretny region (format: x,z, np. 0,0)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Zapisz szczegółowy raport do pliku JSON"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Pokaż szczegółowe błędy"
    )
    
    args = parser.parse_args()
    
    regions_filter = None
    if args.region:
        parts = args.region.split(',')
        if len(parts) == 2:
            regions_filter = [(int(parts[0]), int(parts[1]))]
    
    print("=" * 70)
    print("ANALIZA MAPY MINECRAFT 1.7.10")
    print("=" * 70)
    print(f"Świat: {args.world}")
    
    results = analyze_world(args.world, regions_filter, args.verbose)
    
    if results:
        print_report(results)
        
        if args.output:
            save_detailed_report(results, args.output)


if __name__ == "__main__":
    main()
