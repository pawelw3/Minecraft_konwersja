#!/usr/bin/env python3
"""
Skrypt skanujący mapę 1.7.10 w poszukiwaniu bloków z wybranych modów.
Skanuje regiony w kolejności: 0,0 -> 1,1 -> -5,-5 -> pozostałe środkowe.
"""

import os
import sys
import struct
import zlib
import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

# Prefiksy modów do wyszukania (w danych binarnych chunka)
# Bazując na analizie kodu źródłowego i danych znalezionych na mapie
MOD_PREFIXES = {
    # Better Storage - nazwy tile entities z kodu: container.betterstorage.X
    # Na mapie znaleziono format: betterstorage.X (bez "container.")
    "Better Storage": [
        b"betterstorage.",  # format na mapie: betterstorage.reinforcedChest, etc.
        b"container.betterstorage.",  # format z kodu źródłowego
    ],

    # Blood Magic - bloki: AWWayofTime:X, tile entities: containerX (BEZ prefiksu moda!)
    # Tile entities z kodu: containerAltar, containerMasterStone, containerSocket, etc.
    "Blood Magic": [
        b"AWWayofTime:",  # bloki: AWWayofTime:AlchemicalWizardrybloodRune
        b"containerAltar", b"containerMasterStone", b"containerSocket",
        b"containerWritingTable", b"containerHomHeart", b"containerPedestal",
        b"containerPlinth", b"containerTeleposer", b"containerConduit",
        b"containerOrientable", b"containerSpellParadigmBlock", b"containerSpellEffectBlock",
        b"containerSpellModifierBlock", b"containerSpellEnhancementBlock",
        b"spectralContainerTileEntity", b"containerDemonPortal", b"containerSchematicSaver",
        b"containerSpectralBlock", b"containerReagentConduit", b"containerBellJar",
        b"containerAlchemicCalcinator", b"containerDemonChest", b"containerMimic",
        b"containerCrucible",
    ],

    # Enchanting Plus - format na mapie: eplus:X
    "Enchanting Plus": [
        b"eplus:",  # znalezione na mapie: eplus:advancedEnchantmentTable, eplus:enchantment_book
        b"EnchantingPlus:",  # alternatywny format z mapowania
    ],

    # Growthcraft - tile entities z kodu źródłowego:
    # grc.tileentity.X (cellar, bees, fishtrap), grcmilk.tileentity.X (milk)
    "Growthcraft": [
        b"grc.tileentity.",  # cellar: fruitPress, fruitPresser, brewKettle, fermentBarrel, fermentJar
        b"grcmilk.tileentity.",  # milk: ButterChurn, CheeseBlock, CheesePress, CheeseVat, HangingCurds, Pancheon
        b"grcmilk.",  # itemy: whey, cream, rennet, skimmilk, cheeseemmentaler
        b"grccellar:", b"grcbees:", b"grcfishtrap:", b"grcbamboo:",  # bloki
    ],
}

# Kolejność regionów do skanowania
PRIORITY_REGIONS = [
    (0, 0),
    (1, 1),
    (-5, -5),
    # Pozostałe środkowe regiony
    (-1, -1), (0, 1), (1, 0), (-1, 0), (0, -1),
    (-2, -2), (2, 2), (-3, -3), (3, 3),
    (-4, -4), (4, 4),
]


def read_region_file(filepath: Path) -> List[Tuple[int, int, bytes]]:
    """Czyta plik regionu .mca i zwraca chunki jako (local_x, local_z, data)."""
    chunks = []
    try:
        with open(filepath, 'rb') as f:
            header = f.read(8192)
            if len(header) < 8192:
                return chunks

            for chunk_x in range(32):
                for chunk_z in range(32):
                    idx = chunk_x + chunk_z * 32
                    offset_data = header[idx*4:(idx+1)*4]
                    offset = ((offset_data[0] << 16) | (offset_data[1] << 8) | offset_data[2]) * 4096

                    if offset == 0:
                        continue

                    f.seek(offset)
                    length_bytes = f.read(4)
                    if len(length_bytes) < 4:
                        continue
                    length = struct.unpack('>I', length_bytes)[0]
                    compression = struct.unpack('B', f.read(1))[0]

                    if length > 0 and length < 2*1024*1024:
                        compressed_data = f.read(length - 1)
                        try:
                            if compression == 2:
                                chunk_data = zlib.decompress(compressed_data)
                                chunks.append((chunk_x, chunk_z, chunk_data))
                            elif compression == 1:
                                import gzip
                                chunk_data = gzip.decompress(compressed_data)
                                chunks.append((chunk_x, chunk_z, chunk_data))
                        except Exception:
                            pass
    except Exception as e:
        print(f"  Błąd odczytu {filepath}: {e}")

    return chunks


def find_mod_occurrences(chunk_data: bytes, prefixes: List[bytes]) -> List[str]:
    """Znajduje wystąpienia prefiksów moda w danych chunka."""
    found = []
    for prefix in prefixes:
        pos = 0
        while True:
            pos = chunk_data.find(prefix, pos)
            if pos == -1:
                break
            # Wyciągnij pełny ID bloku (do następnego null byte lub specjalnego znaku)
            end = pos + len(prefix)
            while end < len(chunk_data) and end < pos + 100:
                c = chunk_data[end]
                if c < 32 or c > 126:  # Nie-ASCII lub kontrolny
                    break
                end += 1
            try:
                block_id = chunk_data[pos:end].decode('ascii', errors='ignore')
                if block_id and len(block_id) > len(prefix.decode()):
                    found.append(block_id)
            except:
                pass
            pos = end
    return found


def scan_region(region_path: Path, region_x: int, region_z: int) -> Dict[str, List[Tuple[str, int, int, int]]]:
    """
    Skanuje pojedynczy region w poszukiwaniu bloków z modów.
    Zwraca słownik: mod_name -> lista (block_id, world_x, world_y, world_z)
    """
    results = defaultdict(list)

    chunks = read_region_file(region_path)

    for local_x, local_z, chunk_data in chunks:
        # Oblicz globalne współrzędne chunka
        chunk_x = region_x * 32 + local_x
        chunk_z = region_z * 32 + local_z

        # Sprawdź każdy mod
        for mod_name, prefixes in MOD_PREFIXES.items():
            found_blocks = find_mod_occurrences(chunk_data, prefixes)
            for block_id in found_blocks:
                # Aproksymacja współrzędnych świata (środek chunka)
                world_x = chunk_x * 16 + 8
                world_z = chunk_z * 16 + 8
                world_y = 64  # Domyślnie Y=64
                results[mod_name].append((block_id, world_x, world_y, world_z))

    return results


def main():
    map_path = Path("mapa_1710")
    region_dir = map_path / "region"
    output_dir = Path("output/mod_scan_results")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("SKANOWANIE MAPY 1.7.10 - WYSZUKIWANIE BLOKÓW MODÓW")
    print("=" * 70)
    print(f"Mapa: {map_path}")
    print(f"Mody do wyszukania: {', '.join(MOD_PREFIXES.keys())}")
    print(f"Regiony priorytetowe: {PRIORITY_REGIONS[:3]}")
    print()

    if not region_dir.exists():
        print(f"BŁĄD: Nie znaleziono folderu regionów: {region_dir}")
        sys.exit(1)

    # Wyniki dla każdego moda
    mod_results: Dict[str, List[Tuple[str, int, int, int, str]]] = defaultdict(list)  # block_id, x, y, z, region
    mods_found_in_region: Dict[str, Set[str]] = defaultdict(set)  # mod -> set of regions where found

    # Skanuj regiony w kolejności priorytetowej
    scanned_regions = set()
    regions_to_scan = list(PRIORITY_REGIONS)

    # Dodaj pozostałe regiony (do 20 regionów max)
    all_mca_files = list(region_dir.glob("r.*.*.mca"))
    for mca_file in all_mca_files:
        parts = mca_file.stem.split('.')
        if len(parts) == 3:
            try:
                rx, rz = int(parts[1]), int(parts[2])
                if (rx, rz) not in regions_to_scan:
                    regions_to_scan.append((rx, rz))
            except ValueError:
                pass

    print(f"Dostępnych regionów: {len(all_mca_files)}")
    print()

    for rx, rz in regions_to_scan:
        region_file = region_dir / f"r.{rx}.{rz}.mca"
        if not region_file.exists():
            continue

        if (rx, rz) in scanned_regions:
            continue
        scanned_regions.add((rx, rz))

        print(f"Skanowanie regionu ({rx}, {rz})...", end=" ")

        results = scan_region(region_file, rx, rz)

        found_mods = []
        for mod_name, blocks in results.items():
            if blocks:
                found_mods.append(f"{mod_name}({len(blocks)})")
                mods_found_in_region[mod_name].add(f"{rx},{rz}")
                for block_info in blocks:
                    mod_results[mod_name].append((*block_info, f"r.{rx}.{rz}"))

        if found_mods:
            print(f"ZNALEZIONO: {', '.join(found_mods)}")
        else:
            print("brak bloków modów")

        # Sprawdz czy wszystkie mody zostaly juz znalezione
        all_mods_found = all(mod in mods_found_in_region for mod in MOD_PREFIXES.keys())
        if all_mods_found:
            print(f"\n[OK] Wszystkie mody znalezione po {len(scanned_regions)} regionach!")
            break

    # Podsumowanie i zapis CSV
    print()
    print("=" * 70)
    print("PODSUMOWANIE")
    print("=" * 70)

    for mod_name in MOD_PREFIXES.keys():
        blocks = mod_results.get(mod_name, [])
        regions = mods_found_in_region.get(mod_name, set())

        if blocks:
            print(f"\n[OK] {mod_name}:")
            print(f"   Znaleziono {len(blocks)} wystapien w {len(regions)} regionach")
            print(f"   Regiony: {', '.join(sorted(regions)[:5])}{'...' if len(regions) > 5 else ''}")

            # Zapisz do CSV
            csv_file = output_dir / f"{mod_name.lower().replace(' ', '_')}_locations.csv"
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['block_id', 'world_x', 'world_y', 'world_z', 'region'])

                # Unikalne bloki
                unique_blocks = defaultdict(int)
                for block_id, x, y, z, region in blocks:
                    writer.writerow([block_id, x, y, z, region])
                    unique_blocks[block_id] += 1

            print(f"   CSV zapisany: {csv_file}")
            print(f"   Unikalne typy bloków ({len(unique_blocks)}):")
            for bid, count in sorted(unique_blocks.items(), key=lambda x: -x[1])[:10]:
                print(f"      - {bid}: {count}")
        else:
            print(f"\n[--] {mod_name}: NIE ZNALEZIONO na mapie")

            # Zapisz pusty CSV
            csv_file = output_dir / f"{mod_name.lower().replace(' ', '_')}_locations.csv"
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['block_id', 'world_x', 'world_y', 'world_z', 'region'])
            print(f"   Pusty CSV zapisany: {csv_file}")

    print()
    print(f"Przeskanowano {len(scanned_regions)} regionów.")
    print(f"Wyniki zapisane w: {output_dir}/")


if __name__ == "__main__":
    main()
