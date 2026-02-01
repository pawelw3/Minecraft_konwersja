"""
Konwersja testowej mapy AE2 z 1.7.10 do 1.18.2.

Używa istniejącego konwertera AE2 do przetworzenia wszystkich bloków i TE.
"""

import sys
import json
import shutil
from pathlib import Path

sys.path.insert(0, 'src')

from minecraft_map_parser.anvil_parser import AnvilParser
from minecraft_map_parser.nbt_parser import NBTTag
from converters.ae2.ae2_converter import AE2Converter


def convert_ae2_test_map():
    """Konwertuje testową mapę AE2 do 1.18.2."""
    
    source_world = Path("lightweigh_map_templates/1710_modded/ae2_test")
    target_world = Path("lightweigh_map_templates/118_modded/ae2_test_converted")
    
    print("=" * 60)
    print("AE2 Test Map Converter - 1.7.10 -> 1.18.2")
    print("=" * 60)
    
    # Skopiuj bazową strukturę mapy 1.18.2
    if target_world.exists():
        shutil.rmtree(target_world)
    
    # Użyj istniejącej mapy 1.18.2 jako bazy lub utwórz nową
    base_118 = Path("lightweigh_map_templates/118_modded/ae2_1")
    if base_118.exists():
        shutil.copytree(base_118, target_world)
        print(f"\nSkopiowano bazę z: {base_118}")
    else:
        target_world.mkdir(parents=True, exist_ok=True)
        print(f"\nUtworzono nowy katalog: {target_world}")
    
    # Inicjalizuj konwerter
    converter = AE2Converter()
    
    # Zbierz wszystkie AE2 bloki do konwersji
    blocks_to_convert = []
    
    region_dir = source_world / "region"
    for region_file in region_dir.glob("*.mca"):
        print(f"\nAnaliza regionu: {region_file.name}")
        parser = AnvilParser(str(region_file))
        
        # Sprawdź wszystkie chunki w regionie
        for cx in range(32):
            for cz in range(32):
                try:
                    chunk = parser.get_chunk(cx, cz)
                    if not chunk:
                        continue
                    
                    # Pobierz Tile Entities
                    level = chunk.nbt.get('Level', {})
                    if isinstance(level, NBTTag):
                        level = level.value
                    
                    te_list = level.get('TileEntities', [])
                    if isinstance(te_list, NBTTag):
                        te_list = te_list.value
                    
                    for te in te_list:
                        if isinstance(te, NBTTag):
                            te = te.value
                        
                        te_id = te.get('id', '')
                        if isinstance(te_id, NBTTag):
                            te_id = te_id.value
                        
                        # Sprawdź czy to AE2 TE
                        if te_id.startswith('Block') and any(x in te_id for x in [
                            'Controller', 'Drive', 'Chest', 'Interface', 'Molecular',
                            'Crafting', 'Cable', 'Energy', 'IOPort', 'Inscriber',
                            'Charger', 'Security', 'Quantum', 'Spatial', 'Condenser',
                            'Vibration', 'SkyChest', 'Wireless', 'Growth'
                        ]):
                            x = te.get('x', 0)
                            y = te.get('y', 0)
                            z = te.get('z', 0)
                            if isinstance(x, NBTTag): x = x.value
                            if isinstance(y, NBTTag): y = y.value
                            if isinstance(z, NBTTag): z = z.value
                            
                            blocks_to_convert.append({
                                'te_id': te_id,
                                'x': x,
                                'y': y,
                                'z': z,
                                'nbt': te
                            })
                            
                except Exception as e:
                    pass
    
    print(f"\nZnaleziono {len(blocks_to_convert)} bloków AE2 do konwersji")
    
    # Konwertuj bloki
    conversion_results = []
    errors = []
    
    for block in blocks_to_convert:
        try:
            # Przygotuj ID bloku w formacie 1.7.10
            block_id_1710 = f"appliedenergistics2:tile.{block['te_id']}"
            
            # Konwertuj
            result = converter.convert_block(
                block_id_1710=block_id_1710,
                nbt_1710=block['nbt'],
                position=(block['x'], block['y'], block['z'])
            )
            
            conversion_results.append({
                'original': block,
                'converted': result
            })
            
            if result.converted.errors:
                errors.extend(result.converted.errors)
                
        except Exception as e:
            errors.append(f"Błąd konwersji {block['te_id']} at ({block['x']},{block['y']},{block['z']}): {e}")
    
    # Podsumowanie
    print("\n" + "=" * 60)
    print("PODSUMOWANIE KONWERSJI")
    print("=" * 60)
    
    successful = sum(1 for r in conversion_results if r['converted'].converted.success)
    failed = len(conversion_results) - successful
    
    print(f"Łącznie bloków: {len(conversion_results)}")
    print(f"  Udane: {successful}")
    print(f"  Nieudane: {failed}")
    print(f"  Błędy: {len(errors)}")
    
    if errors:
        print("\nPierwsze 10 błędów:")
        for error in errors[:10]:
            print(f"  - {error}")
    
    # Zapisz raport
    report = {
        'source_world': str(source_world),
        'target_world': str(target_world),
        'total_blocks': len(conversion_results),
        'successful': successful,
        'failed': failed,
        'errors': errors[:20],
        'conversions': [
            {
                'original_id': r['original']['te_id'],
                'position': [r['original']['x'], r['original']['y'], r['original']['z']],
                'new_id': r['converted'].converted.block_id_1182,
                'success': r['converted'].converted.success,
                'errors': r['converted'].converted.errors,
                'warnings': r['converted'].converted.warnings
            }
            for r in conversion_results
        ]
    }
    
    report_file = target_world / "conversion_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nRaport zapisany: {report_file}")
    
    return report


if __name__ == "__main__":
    convert_ae2_test_map()
