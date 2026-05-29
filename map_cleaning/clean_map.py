"""
Skrypt do czyszczenia mapy Minecraft 1.7.10 z:
- Entities (mobów, przedmiotów, etc.)
- Block Entities/Tile Entities (skrzynie, maszyny modów)
- Bloków z modów (zamiana na air)

Używa map-cleaner JVM workera (map_cleaning/jvm/) do modyfikacji bloków/TE/entities.
"""
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field

# Dodaj src do path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from minecraft_map_parser.anvil_parser import AnvilParser, ChunkData
from minecraft_map_parser.nbt_parser import NBTTag


# Vanilla block IDs w Minecraft 1.7.10
VANILLA_BLOCK_IDS = set(range(0, 176))
VANILLA_BLOCK_IDS.update(range(176, 198))  # 1.7.x additions
VANILLA_BLOCK_IDS.update([159, 160, 161, 162, 163, 164, 165, 166, 167,
                           168, 169, 170, 171, 172, 173, 174, 175])


@dataclass
class BlockEdit:
    """Pojedyncza edycja bloku."""
    x: int
    y: int
    z: int
    block_id: int
    meta: int = 0


@dataclass
class ChunkAnalysis:
    """Wynik analizy chunka."""
    chunk_x: int
    chunk_z: int
    region_file: Path
    local_chunk_x: int
    local_chunk_z: int
    
    # Bloki do zamiany na bedrock (lista pozycji)
    mod_blocks: List[Tuple[int, int, int]] = field(default_factory=list)
    
    # Tile entities do usunięcia (lista pozycji)
    tile_entities: List[Tuple[int, int, int, str]] = field(default_factory=list)
    
    # Entities do usunięcia (liczba)
    entity_count: int = 0
    
    @property
    def has_changes(self) -> bool:
        return bool(self.mod_blocks or self.tile_entities or self.entity_count > 0)


def get_block_id_from_section(section: Dict, local_x: int, local_y: int, local_z: int) -> int:
    """Pobiera pełne 12-bitowe ID bloku z sekcji (Blocks + Add array)."""
    blocks = section.get('Blocks')
    if blocks is None:
        return 0
    if isinstance(blocks, NBTTag):
        blocks = blocks.value
    if not isinstance(blocks, (list, tuple, bytes, bytearray)):
        return 0

    index = local_y * 256 + local_z * 16 + local_x
    if index >= len(blocks):
        return 0

    raw = blocks[index]
    low = raw if isinstance(raw, int) else ord(raw)
    low &= 0xFF

    # Górne 4 bity z tablicy Add (bloki z modów mają ID >= 256)
    add = section.get('Add') or section.get('AddBlocks')
    if isinstance(add, NBTTag):
        add = add.value
    high = 0
    if add and isinstance(add, (bytes, bytearray, list)) and index // 2 < len(add):
        nibble_byte = add[index // 2]
        nibble_byte = nibble_byte if isinstance(nibble_byte, int) else ord(nibble_byte)
        if index % 2 == 0:
            high = nibble_byte & 0x0F
        else:
            high = (nibble_byte >> 4) & 0x0F

    return (high << 8) | low


def analyze_chunk(chunk: ChunkData, region_file: Path, local_x: int, local_z: int) -> ChunkAnalysis:
    """Analizuje chunk pod kątem bloków z modów, TE i entities."""
    result = ChunkAnalysis(
        chunk_x=chunk.x,
        chunk_z=chunk.z,
        region_file=region_file,
        local_chunk_x=local_x,
        local_chunk_z=local_z
    )
    
    # Analizuj sekcje
    sections = chunk.get_sections()
    for section in sections:
        if not isinstance(section, dict):
            continue
            
        y_section = section.get('Y')
        if isinstance(y_section, NBTTag):
            y_section = y_section.value
        if y_section is None:
            continue
        
        # Przeskanuj wszystkie bloki w sekcji
        for y in range(16):
            world_y = y_section * 16 + y
            for z in range(16):
                for x in range(16):
                    block_id = get_block_id_from_section(section, x, y, z)
                    
                    # Jeśli blok nie jest vanilla, dodaj do listy
                    if block_id not in VANILLA_BLOCK_IDS and block_id != 0:  # 0 = air
                        world_x = chunk.x * 16 + x
                        world_z = chunk.z * 16 + z
                        result.mod_blocks.append((world_x, world_y, world_z))
    
    # Analizuj Tile Entities
    tile_entities = chunk.get_tile_entities()
    for te in tile_entities:
        if not isinstance(te, dict):
            continue
        
        te_id = te.get('id')
        if isinstance(te_id, NBTTag):
            te_id = te_id.value
        
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
            result.tile_entities.append((int(x), int(y), int(z), str(te_id) if te_id else "unknown"))
    
    # Zlicz entities
    entities = chunk.get_entities()
    result.entity_count = len(entities)
    
    return result


def run_map_cleaner(world_path: Path) -> bool:
    """Uruchamia map-cleaner JAR na podanym świecie.

    JAR czyta pełne 12-bitowe ID bloków (Blocks + Add), zastępuje bloki modów
    (ID >= 256) na air (replacementBlock=0), czyści TileEntities i Entities.
    """
    cleaner_jar = Path(__file__).parent / "jvm" / "build" / "libs" / "map-cleaner-1.0-SNAPSHOT.jar"

    if not cleaner_jar.exists():
        print(f"Błąd: Nie znaleziono map-cleaner JAR: {cleaner_jar}")
        print("Zbuduj: cd map_cleaning/jvm && .\\gradlew.bat build")
        return False

    cmd = ["java", "-jar", str(cleaner_jar), str(world_path), "--full"]

    print(f"Uruchamiam map-cleaner JAR...")
    print(f"  Świat: {world_path}")
    print(f"  Tryb: --full (bloki -> air, TE, entities)")

    try:
        result = subprocess.run(cmd, capture_output=False, text=True, timeout=3600)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("Błąd: Timeout podczas czyszczenia (>1h)")
        return False
    except Exception as e:
        print(f"Błąd podczas uruchamiania map-cleaner: {e}")
        return False


def clean_entities_via_python(world_path: Path, analysis_results: List[ChunkAnalysis]) -> None:
    """Czyści entities bezpośrednio przez Python (nie wymaga JVM)."""
    import struct
    import zlib
    import nbtlib
    
    SECTOR_SIZE = 4096
    
    def read_chunk_nbt(region_data: bytearray, local_x: int, local_z: int) -> Optional[nbtlib.Compound]:
        index = local_x + local_z * 32
        offset = index * 4
        
        if offset + 4 > len(region_data):
            return None
        
        data = region_data[offset:offset + 4]
        sector_offset = ((data[0] << 16) | (data[1] << 8) | data[2])
        
        if sector_offset == 0:
            return None
        
        byte_offset = sector_offset * SECTOR_SIZE
        
        if byte_offset + 5 > len(region_data):
            return None
        
        length = struct.unpack('>I', region_data[byte_offset:byte_offset + 4])[0]
        compression_type = region_data[byte_offset + 4]
        
        compressed_data = region_data[byte_offset + 5:byte_offset + 5 + length - 1]
        
        try:
            if compression_type == 2:
                data = zlib.decompress(compressed_data)
            elif compression_type == 1:
                import gzip
                data = gzip.decompress(compressed_data)
            else:
                data = compressed_data
            
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(data)
                tmp_path = tmp.name
            
            try:
                return nbtlib.load(tmp_path, byteorder='big')
            finally:
                os.unlink(tmp_path)
        except:
            return None
    
    def write_chunk_nbt(region_data: bytearray, local_x: int, local_z: int, nbt: nbtlib.Compound) -> bool:
        from io import BytesIO
        
        buffer = BytesIO()
        nbt.write(buffer, byteorder='big')
        nbt_bytes = buffer.getvalue()
        
        compressed = zlib.compress(nbt_bytes)
        chunk_data = struct.pack('>I', len(compressed) + 1) + b'\x02' + compressed
        
        padding = (SECTOR_SIZE - (len(chunk_data) % SECTOR_SIZE)) % SECTOR_SIZE
        chunk_data_padded = chunk_data + b'\x00' * padding
        new_sector_count = len(chunk_data_padded) // SECTOR_SIZE
        
        index = local_x + local_z * 32
        offset = index * 4
        
        data = region_data[offset:offset + 4]
        sector_offset = ((data[0] << 16) | (data[1] << 8) | data[2])
        
        if sector_offset == 0:
            sector_offset = len(region_data) // SECTOR_SIZE
            if len(region_data) % SECTOR_SIZE != 0:
                sector_offset += 1
        
        byte_offset = sector_offset * SECTOR_SIZE
        end_offset = byte_offset + len(chunk_data_padded)
        
        if end_offset > len(region_data):
            region_data.extend(b'\x00' * (end_offset - len(region_data)))
        
        region_data[byte_offset:end_offset] = chunk_data_padded
        
        region_data[offset] = (sector_offset >> 16) & 0xFF
        region_data[offset + 1] = (sector_offset >> 8) & 0xFF
        region_data[offset + 2] = sector_offset & 0xFF
        region_data[offset + 3] = new_sector_count
        
        return True
    
    # Grupuj chunki po regionach
    regions_to_clean: Dict[Path, Set[Tuple[int, int]]] = {}
    
    for chunk_analysis in analysis_results:
        if chunk_analysis.entity_count > 0:
            region_file = chunk_analysis.region_file
            local_pos = (chunk_analysis.local_chunk_x, chunk_analysis.local_chunk_z)
            
            if region_file not in regions_to_clean:
                regions_to_clean[region_file] = set()
            regions_to_clean[region_file].add(local_pos)
    
    if not regions_to_clean:
        print("  Brak entities do wyczyszczenia")
        return
    
    print(f"  Czyszczenie entities z {len(regions_to_clean)} regionów...")
    
    total_modified = 0
    total_entities = 0
    
    for region_file, chunks in regions_to_clean.items():
        try:
            with open(region_file, 'rb') as f:
                region_data = bytearray(f.read())
            
            modified = 0
            for local_x, local_z in chunks:
                nbt = read_chunk_nbt(region_data, local_x, local_z)
                if nbt is None:
                    continue
                
                level = nbt.get('Level')
                if level is None:
                    continue
                
                entities = level.get('Entities')
                if entities is None or len(entities) == 0:
                    continue
                
                entity_count = len(entities)
                level['Entities'] = nbtlib.List[nbtlib.Compound]([])
                
                write_chunk_nbt(region_data, local_x, local_z, nbt)
                
                modified += 1
                total_entities += entity_count
            
            if modified > 0:
                with open(region_file, 'wb') as f:
                    f.write(region_data)
                total_modified += modified
        
        except Exception as e:
            print(f"    Błąd w {region_file.name}: {e}")
    
    print(f"  Wyczyszczono {total_entities} entities z {total_modified} chunków")


def copy_world_for_singleplayer(source_world: Path, output_world: Path) -> None:
    """
    Kopiuje wszystkie pliki potrzebne do otwarcia mapy w singleplayerze.
    Obejmuje: level.dat, session.lock, playerdata, stats, data, region, DIM-1, DIM1
    """
    output_world.mkdir(parents=True, exist_ok=True)
    
    # Lista plików i folderów potrzebnych do singleplayer
    singleplayer_files = [
        "level.dat",
        "level.dat_old",
        "session.lock",
        "uid.dat",
        "forcedchunks.dat",
        "idcounts.dat",
        "playerdata",      # Dane graczy
        "stats",           # Statystyki
        "data",            # Dane map i inne
        "region",          # Główny świat
        "DIM-1",           # Nether
        "DIM1",            # End
    ]
    
    for item_name in singleplayer_files:
        source_path = source_world / item_name
        output_path = output_world / item_name
        
        if not source_path.exists():
            continue
            
        try:
            if source_path.is_dir():
                if output_path.exists():
                    shutil.rmtree(output_path)
                shutil.copytree(source_path, output_path)
                print(f"  [DIR] {item_name}")
            else:
                shutil.copy2(source_path, output_path)
                print(f"  [FILE] {item_name}")
        except Exception as e:
            print(f"  [SKIP] {item_name}: {e}")


def clean_map(source_world: Path, output_world: Path, regions_filter: Optional[List[Tuple[int, int]]] = None, use_move: bool = False) -> bool:
    """
    Główna funkcja czyszcząca mapę.
    
    Args:
        source_world: Ścieżka do źródłowego świata
        output_world: Ścieżka do wyjściowego (wyczyszczonego) świata
        regions_filter: Opcjonalna lista regionów do przetworzenia (x, z)
        use_move: Jeśli True, użyj shutil.move zamiast copy (szybsze, oszczędza miejsce, ale usuwa źródło jeśli to inny folder)
    """
    print("=" * 60)
    print("CZYSZCZENIE MAPY MINECRAFT 1.7.10")
    print("=" * 60)
    print(f"Źródło: {source_world}")
    print(f"Cel: {output_world}")
    
    # Przygotuj świat
    print("\n[1/3] Przygotowywanie świata...")
    if output_world.exists():
        print(f"  Usuwanie starego katalogu: {output_world}")
        shutil.rmtree(output_world)
    
    if use_move:
        # Użyj move - szybsze, nie zabiera dodatkowego miejsca na dysku
        # UWAGA: To usunie źródło jeśli jest na tym samym dysku!
        print(f"  Przenoszenie świata (move)...")
        shutil.move(str(source_world), str(output_world))
    else:
        # Standardowe kopiowanie z zachowaniem wszystkich plików singleplayer
        print(f"  Kopiowanie wszystkich plików singleplayer...")
        copy_world_for_singleplayer(source_world, output_world)
    
    print(f"  Gotowe")
    
    # Analizuj regiony
    print("\n[2/3] Analiza regionów...")
    output_region = output_world / "region"
    region_files = list(output_region.glob("r.*.mca"))
    
    if regions_filter:
        filtered_files = []
        for rx, rz in regions_filter:
            rfile = output_region / f"r.{rx}.{rz}.mca"
            if rfile.exists():
                filtered_files.append(rfile)
        region_files = filtered_files
    
    print(f"  Znaleziono {len(region_files)} plików regionów")
    
    all_analysis: List[ChunkAnalysis] = []
    
    for i, region_file in enumerate(region_files, 1):
        print(f"  [{i}/{len(region_files)}] Analiza {region_file.name}...")
        
        try:
            parser = AnvilParser(str(region_file))
            
            for chunk_z in range(32):
                for chunk_x in range(32):
                    chunk = parser.get_chunk(chunk_x, chunk_z)
                    if chunk is None:
                        continue
                    
                    analysis = analyze_chunk(chunk, region_file, chunk_x, chunk_z)
                    if analysis.has_changes:
                        all_analysis.append(analysis)
        
        except Exception as e:
            print(f"    Błąd: {e}")
    
    print(f"\n  Podsumowanie analizy:")
    print(f"    Chunki do modyfikacji: {len(all_analysis)}")
    print(f"    Bloki z modów: {sum(len(a.mod_blocks) for a in all_analysis)}")
    print(f"    Tile Entities: {sum(len(a.tile_entities) for a in all_analysis)}")
    print(f"    Entities: {sum(a.entity_count for a in all_analysis)}")
    
    if not all_analysis:
        print("\n  Brak zmian do wykonania!")
        return True

    # Uruchom map-cleaner JAR — zastępuje bloki modów na air, czyści TE i entities
    print("\n[3/3] Czyszczenie bloków, TileEntities i Entities (map-cleaner JAR)...")
    success = run_map_cleaner(output_world)

    if not success:
        print("  Błąd podczas czyszczenia!")
        return False
    
    print("\n" + "=" * 60)
    print("CZYSZCZENIE ZAKONCZONE")
    print("=" * 60)
    print(f"Wyczyszczona mapa: {output_world}")
    
    return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Czyści mapę Minecraft 1.7.10 z modów, TE i entities"
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(__file__).parent.parent / "mapa_1710",
        help="Ścieżka do źródłowego świata (domyślnie: ../mapa_1710)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent / "map_1710_no_mods",
        help="Ścieżka do wyjściowego świata (domyślnie: ./map_1710_no_mods)"
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="Użyj przeniesienia (move) zamiast kopiowania - szybsze i oszczędza miejsce, ALE usuwa źródło!"
    )
    parser.add_argument(
        "--region",
        type=str,
        help="Przetwórz tylko konkretny region (format: x,z, np. 0,0)"
    )
    
    args = parser.parse_args()
    
    # Parsuj filtr regionów
    regions_filter = None
    if args.region:
        parts = args.region.split(',')
        if len(parts) == 2:
            regions_filter = [(int(parts[0]), int(parts[1]))]
    
    success = clean_map(args.source, args.output, regions_filter, use_move=args.move)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
