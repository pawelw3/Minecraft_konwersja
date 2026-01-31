"""
Weryfikacja czy schematic został poprawnie wygenerowany z JSON.
Porównuje strukturę JSON z tym co jest w mapie Minecraft.
"""

import json
import struct
import zlib
from pathlib import Path
from collections import Counter
import sys

sys.path.insert(0, str(Path(__file__).parent))
from minecraft_map_parser.nbt_parser import NBTParser


def analyze_json(json_path: Path):
    """Analizuje plik JSON z voxel grid."""
    with open(json_path) as f:
        data = json.load(f)
    
    voxels = []
    for section_name, section_data in data['sections'].items():
        for v in section_data.get('voxels', []):
            voxels.append({
                'x': v['x'], 'y': v['y'], 'z': v['z'],
                'block': v['block'].split(':')[-1],
                'properties': v.get('properties', {}),
                'purpose': v.get('purpose', '')
            })
    
    return voxels


def analyze_region(region_path: Path, chunk_x: int = 0, chunk_z: int = 0):
    """Analizuje chunk z pliku regionu."""
    with open(region_path, 'rb') as f:
        # Location table
        location_table = f.read(4096)
        
        # Chunk 0,0
        idx = chunk_z * 32 + chunk_x
        offset_data = location_table[idx * 4:(idx + 1) * 4]
        offset = ((offset_data[0] << 16) | (offset_data[1] << 8) | offset_data[2]) * 4096
        
        if offset == 0:
            return None
        
        f.seek(offset)
        length = struct.unpack('>I', f.read(4))[0]
        compression = struct.unpack('B', f.read(1))[0]
        chunk_data = f.read(length - 1)
        
        # Dekompresuj
        decompressed = zlib.decompress(chunk_data)
        
        # Parsuj NBT
        parser = NBTParser(decompressed)
        chunk = parser.parse()
        
        # Pobierz sekcje
        level = chunk.value['Level']
        sections = level.value['Sections']
        
        blocks_in_world = []
        
        for sec in sections.value:
            if isinstance(sec, tuple):
                _, sec = sec
            
            y_val = sec.get('Y')
            if isinstance(y_val, tuple):
                y_val = y_val[1]
            elif hasattr(y_val, 'value'):
                y_val = y_val.value
            
            blocks_tag = sec.get('Blocks')
            if isinstance(blocks_tag, tuple):
                blocks = blocks_tag[1]
            elif hasattr(blocks_tag, 'value'):
                blocks = blocks_tag.value
            else:
                continue
            
            # Znajdź nie-air bloki
            for i, block_id in enumerate(blocks):
                if block_id != 0:
                    local_y = i // 256
                    local_z = (i % 256) // 16
                    local_x = i % 16
                    
                    world_y = y_val * 16 + local_y
                    world_x = local_x  # chunk 0,0
                    world_z = local_z
                    
                    blocks_in_world.append({
                        'x': world_x, 'y': world_y, 'z': world_z,
                        'block_id': block_id
                    })
        
        return blocks_in_world


def compare_structures(json_voxels, world_blocks):
    """Porównuje strukturę JSON z tym co jest w świecie."""
    
    # Mapowanie nazw bloków na ID (1.7.10)
    BLOCK_MAP = {
        'stone': 1,
        'redstone_wire': 55,
        'redstone_torch': 76,
        'unlit_redstone_torch': 75,
        'repeater': 93,
        'dropper': 158,
        'comparator': 149,
        'command_block': 137,
        'lever': 69,
    }
    
    print("\n" + "="*60)
    print("PORÓWNANIE JSON vs ŚWIAT MINECRAFT")
    print("="*60)
    
    # JSON stats
    json_blocks = Counter(v['block'] for v in json_voxels)
    print("\n[JSON] Liczba blokow:")
    for block, count in sorted(json_blocks.items()):
        print(f"  {block}: {count}")
    
    # World stats  
    world_block_names = {}
    for b in world_blocks:
        name = None
        for n, bid in BLOCK_MAP.items():
            if bid == b['block_id']:
                name = n
                break
        if not name:
            name = f"ID:{b['block_id']}"
        world_block_names[name] = world_block_names.get(name, 0) + 1
    
    print("\n[SWIAT] Liczba blokow:")
    for name, count in sorted(world_block_names.items()):
        print(f"  {name}: {count}")
    
    # Sprawdź kluczowe bloki
    print("\n[WERYFIKACJA] KLUCZOWE BLOKI:")
    
    checks = [
        ('stone', json_blocks.get('stone', 0), world_block_names.get('stone', 0)),
        ('dropper', json_blocks.get('dropper', 0), world_block_names.get('dropper', 0)),
        ('comparator', json_blocks.get('comparator', 0), world_block_names.get('comparator', 0)),
        ('command_block', json_blocks.get('command_block', 0), world_block_names.get('command_block', 0)),
        ('redstone_wire', json_blocks.get('redstone_wire', 0), world_block_names.get('redstone_wire', 0)),
        ('repeater', json_blocks.get('repeater', 0), world_block_names.get('repeater', 0)),
        ('lever', json_blocks.get('lever', 0), world_block_names.get('lever', 0)),
    ]
    
    all_ok = True
    for name, json_count, world_count in checks:
        status = "[OK]" if json_count == world_count else "[BLAD]"
        if json_count != world_count:
            all_ok = False
        print(f"  {status} {name}: JSON={json_count}, ŚWIAT={world_count}")
    
    # Sprawdź współrzędne
    print("\n[ZAKRESY] WSPOLRZEDNE:")
    json_min_x = min(v['x'] for v in json_voxels)
    json_max_x = max(v['x'] for v in json_voxels)
    json_min_y = min(v['y'] for v in json_voxels)
    json_max_y = max(v['y'] for v in json_voxels)
    json_min_z = min(v['z'] for v in json_voxels)
    json_max_z = max(v['z'] for v in json_voxels)
    
    print(f"  JSON: X({json_min_x}-{json_max_x}), Y({json_min_y}-{json_max_y}), Z({json_min_z}-{json_max_z})")
    
    if world_blocks:
        world_min_x = min(b['x'] for b in world_blocks)
        world_max_x = max(b['x'] for b in world_blocks)
        world_min_y = min(b['y'] for b in world_blocks)
        world_max_y = max(b['y'] for b in world_blocks)
        world_min_z = min(b['z'] for b in world_blocks)
        world_max_z = max(b['z'] for b in world_blocks)
        
        print(f"  ŚWIAT: X({world_min_x}-{world_max_x}), Y({world_min_y}-{world_max_y}), Z({world_min_z}-{world_max_z})")
    
    print("\n" + "="*60)
    if all_ok:
        print("[SUKCES] WERYFIKACJA ZAKONCZONA POMYSLNIE")
        print("Schematic został poprawnie wygenerowany z JSON!")
    else:
        print("[BLAD] WYKRYTO ROZNICE")
        print("Schematic może wymagać korekty.")
    print("="*60)
    
    return all_ok


if __name__ == "__main__":
    # Analizuj JSON
    json_voxels = analyze_json(Path("test_scenarios/digital_counter_vanilla/schematics/voxel_grid.json"))
    
    # Analizuj świat
    world_blocks = analyze_region(Path("headless_server/1.7.10/world/region/r.0.0.mca"), 0, 0)
    
    if world_blocks is None:
        print("❌ Nie znaleziono chunka (0,0) w regionie!")
        sys.exit(1)
    
    # Porównaj
    compare_structures(json_voxels, world_blocks)
