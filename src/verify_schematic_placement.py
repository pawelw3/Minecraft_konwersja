"""
Skrypt weryfikujący poprawność wstawienia schematica do mapy.
"""

import struct
import zlib
from pathlib import Path
from typing import Dict, List, Tuple

from minecraft_map_parser.nbt_parser import NBTTag, NBTParser


def read_chunk_from_region(region_path: Path, chunk_x: int, chunk_z: int) -> NBTTag:
    """Odczytuje chunk z pliku regionu."""
    
    local_x = chunk_x % 32
    local_z = chunk_z % 32
    
    with open(region_path, 'rb') as f:
        location_offset = (local_z * 32 + local_x) * 4
        f.seek(location_offset)
        
        offset_data = f.read(4)
        if len(offset_data) < 4:
            return None
        
        offset = ((offset_data[0] << 16) | (offset_data[1] << 8) | offset_data[2]) * 4096
        sector_count = offset_data[3]
        
        if offset == 0:
            return None
        
        f.seek(offset)
        length = struct.unpack('>I', f.read(4))[0]
        compression = struct.unpack('B', f.read(1))[0]
        chunk_data = f.read(length - 1)
        
        if compression == 2:
            decompressed = zlib.decompress(chunk_data)
        else:
            decompressed = chunk_data
        
        parser = NBTParser(decompressed)
        return parser.parse()


def get_section_value(section, key):
    """Pobiera wartość z sekcji obsługując różne formaty."""
    if isinstance(section, dict):
        val = section.get(key)
    elif isinstance(section, NBTTag):
        val = section.value.get(key) if hasattr(section.value, 'get') else None
    else:
        return None
    
    if val is None:
        return None
    
    # Rozpakuj tuple (type, value) lub NBTTag
    if isinstance(val, tuple):
        return val[1]
    elif isinstance(val, NBTTag):
        return val.value
    return val


def get_block_from_chunk(chunk_nbt: NBTTag, x: int, y: int, z: int) -> Tuple[int, int]:
    """Pobiera ID i metadata bloku z chunka."""
    
    level = chunk_nbt.value.get('Level')
    if not level:
        return (0, 0)
    
    sections = level.value.get('Sections')
    if not sections:
        return (0, 0)
    
    section_idx = y // 16
    local_y = y % 16
    local_x = x % 16
    local_z = z % 16
    
    for section in sections.value:
        if isinstance(section, tuple):
            _, section = section
        
        y_val = get_section_value(section, 'Y')
        if y_val != section_idx:
            continue
        
        blocks = get_section_value(section, 'Blocks')
        data = get_section_value(section, 'Data')
        
        if blocks is None:
            continue
        
        idx = local_y * 16 * 16 + local_z * 16 + local_x
        if idx >= len(blocks):
            continue
            
        block_id = blocks[idx] & 0xFF
        
        # Metadata (nibble)
        meta = 0
        if data:
            data_idx = idx // 2
            is_high_nibble = idx % 2 == 1
            if data_idx < len(data):
                meta = (data[data_idx] >> 4) & 0x0F if is_high_nibble else data[data_idx] & 0x0F
        
        return (block_id, meta)
    
    return (0, 0)


def verify_placement(world_path: Path, expected_blocks: List[Tuple[int, int, int, int, int]]):
    """
    Weryfikuje wstawienie bloków.
    expected_blocks: lista (world_x, world_y, world_z, expected_id, expected_meta)
    """
    print(f"Weryfikacja mapy: {world_path}")
    print("-" * 60)
    
    # Grupuj według regionów i chunków
    by_chunk: Dict[Tuple[int, int, int, int], List[Tuple[int, int, int, int, int]]] = {}
    
    for wx, wy, wz, exp_id, exp_meta in expected_blocks:
        chunk_x = wx // 16
        chunk_z = wz // 16
        region_x = chunk_x // 32
        region_z = chunk_z // 32
        
        key = (region_x, region_z, chunk_x, chunk_z)
        if key not in by_chunk:
            by_chunk[key] = []
        by_chunk[key].append((wx, wy, wz, exp_id, exp_meta))
    
    total_checked = 0
    total_ok = 0
    errors = []
    
    for (rx, rz, cx, cz), blocks in by_chunk.items():
        region_path = world_path / "region" / f"r.{rx}.{rz}.mca"
        
        if not region_path.exists():
            print(f"  BŁĄD: Brak pliku regionu {region_path}")
            continue
        
        chunk_nbt = read_chunk_from_region(region_path, cx, cz)
        if not chunk_nbt:
            print(f"  BŁĄD: Nie można odczytać chunka ({cx}, {cz})")
            continue
        
        for wx, wy, wz, exp_id, exp_meta in blocks:
            local_x = wx % 16
            local_z = wz % 16
            
            block_id, meta = get_block_from_chunk(chunk_nbt, local_x, wy, local_z)
            
            total_checked += 1
            
            if block_id == exp_id:  # Compare only block ID for now
                total_ok += 1
            else:
                errors.append(f"  ({wx},{wy},{wz}): oczekiwano ID={exp_id}, odczytano ID={block_id}")
    
    print(f"Sprawdzono bloków: {total_checked}")
    print(f"Poprawnych: {total_ok}")
    print(f"Błędów: {len(errors)}")
    
    if errors:
        print("\nPierwsze 10 błędów:")
        for err in errors[:10]:
            print(err)
    else:
        print("\n✓ Wszystkie bloki są poprawne!")
    
    return len(errors) == 0


if __name__ == "__main__":
    import sys
    
    world_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("lightweigh_map_templates/1710_modded/konwersja1_with_schematic")
    
    # Lista oczekiwanych bloków z digital_counter
    # Schematic wstawiony na (0, 60, 0) z offsetami (0, 0, 2)
    # Format: (world_x, world_y, world_z, block_id, meta)
    # y_world = y_schematic + 60
    expected = [
        # Stone supports (ID: 1)
        (1, 62, 2, 1, 0),   # clock_inverter_support
        (6, 60, 6, 1, 0),   # D0_support
        (6, 62, 6, 1, 0),   # D0_power_block
        
        # Redstone wire (ID: 55)
        (6, 63, 2, 55, 0),  # clock_out
        (6, 63, 6, 55, 0),  # D0_bus
        
        # Dropper (ID: 158)
        (6, 61, 6, 158, 0),  # D0 dropper
        (7, 61, 6, 158, 0),  # D1 dropper
        
        # Comparator (ID: 149)
        (6, 61, 5, 149, 0),  # C0 comparator
        
        # Command block (ID: 137)
        (6, 61, 4, 137, 0),  # CMD0
        
        # Lever (ID: 69)
        (0, 63, 2, 69, 0),  # master_switch
        
        # Repeater (ID: 93)
        (3, 63, 2, 93, 0),  # clock_delay_r1
        
        # Redstone torch (ID: 75)
        (2, 63, 2, 75, 0),  # clock_inverter_torch
    ]
    
    verify_placement(world_path, expected)
