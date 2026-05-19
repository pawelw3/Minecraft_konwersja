"""
Skanowanie stref mapy w poszukiwaniu bloków BiblioCraft
Zadanie 4: Sprawdzenie pokrycia kodu konwersji
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from converters.bibliocraft import BiblioCraftChunkParser, find_bc_blocks_in_world

# Definicje stref
STREFY = {
    "billund": {"x_range": (280, 602), "z_range": (-364, -81)},
    "choroszcz": {"x_range": (763, 916), "z_range": (-787, -636)},
    "iii_rzesza": {"x_range": (455, 966), "z_range": (2955, 3477)},
    "rzym": {"x_range": (301, 1005), "z_range": (163, 929)},
    "zsrr": {"x_range": (-2948, -2086), "z_range": (-2857, -1759)},
}

# Obsługiwane TE IDs (rzeczywiste klucze z MCA 1.7.10)
from converters.bibliocraft.bc_chunk_parser import BiblioCraftChunkParser
OBSŁUGIWANE_BLOKI = BiblioCraftChunkParser.KNOWN_BC_TE_IDS

def get_chunks_in_range(x_range: Tuple[int, int], z_range: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Zwraca listę chunków w zakresie"""
    chunks = []
    chunk_x_start = x_range[0] >> 4
    chunk_x_end = x_range[1] >> 4
    chunk_z_start = z_range[0] >> 4
    chunk_z_end = z_range[1] >> 4
    
    for cx in range(chunk_x_start, chunk_x_end + 1):
        for cz in range(chunk_z_start, chunk_z_end + 1):
            chunks.append((cx, cz))
    return chunks

def analyze_strefa(name: str, x_range: Tuple[int, int], z_range: Tuple[int, int], world_path: str):
    """Analizuje pojedynczą strefę"""
    print(f"\n{'='*60}")
    print(f"Analiza strefy: {name.upper()}")
    print(f"Zakres X: {x_range[0]} do {x_range[1]}")
    print(f"Zakres Z: {z_range[0]} do {z_range[1]}")
    print(f"{'='*60}")
    
    parser = BiblioCraftChunkParser(world_path)
    chunks = get_chunks_in_range(x_range, z_range)
    
    print(f"Liczba chunków do sprawdzenia: {len(chunks)}")
    
    found_blocks: Dict[str, int] = {}
    unknown_blocks: Set[str] = set()
    blocks_with_inventory = 0
    blocks_with_texture = 0
    
    for i, (cx, cz) in enumerate(chunks):
        if i % 50 == 0:
            print(f"  Przetwarzanie... {i}/{len(chunks)} chunków")
        
        result = parser.analyze_chunk(cx, cz)
        
        for block in result.bc_blocks:
            block_id = block.block_id
            
            # Zliczaj wszystkie bloki
            found_blocks[block_id] = found_blocks.get(block_id, 0) + 1
            
            # Sprawdź czy obsługiwany
            if block_id not in OBSŁUGIWANE_BLOKI:
                unknown_blocks.add(block_id)
            
            # Sprawdź czy ma inventory
            if block.tile_entity:
                if any(key in block.tile_entity for key in ["Items", "shelfItems", "armorItems"]):
                    blocks_with_inventory += 1
                if block.tile_entity.get("frameTexture") or block.tile_entity.get("resourceLocation"):
                    blocks_with_texture += 1
    
    total_blocks = sum(found_blocks.values())
    
    print(f"\nWYNIKI:")
    print(f"  Znaleziono bloków BC: {total_blocks}")
    print(f"  Unikalnych typów: {len(found_blocks)}")
    print(f"  Z inventory: {blocks_with_inventory}")
    print(f"  Z teksturami: {blocks_with_texture}")
    
    if found_blocks:
        print(f"\n  Szczegóły:")
        for block_id, count in sorted(found_blocks.items(), key=lambda x: -x[1]):
            status = "✅" if block_id in OBSŁUGIWANE_BLOKI else "❌ NIEZNANY"
            print(f"    {block_id}: {count} {status}")
    
    if unknown_blocks:
        print(f"\n  ❌ NIEZNANE BLOKI (wymagają dodania do kodu):")
        for bid in unknown_blocks:
            print(f"    - {bid}")
    
    return {
        "name": name,
        "total_blocks": total_blocks,
        "unique_types": len(found_blocks),
        "blocks": found_blocks,
        "unknown_blocks": list(unknown_blocks),
        "with_inventory": blocks_with_inventory,
        "with_texture": blocks_with_texture
    }

def main():
    world_path = "mapa_1710"
    
    print("="*60)
    print("SKANOWANIE STREF - BIBLIOCRAFT ANALIZA")
    print("="*60)
    print(f"Świat: {world_path}")
    print(f"Obsługiwane bloki w kodzie: {len(OBSŁUGIWANE_BLOKI)}")
    
    results = []
    
    for name, coords in STREFY.items():
        result = analyze_strefa(
            name,
            coords["x_range"],
            coords["z_range"],
            world_path
        )
        results.append(result)
    
    # Podsumowanie
    print(f"\n{'='*60}")
    print("PODSUMOWANIE CAŁOŚCIOWE")
    print(f"{'='*60}")
    
    total_all = sum(r["total_blocks"] for r in results)
    all_unknown = set()
    for r in results:
        all_unknown.update(r["unknown_blocks"])
    
    print(f"Całkowita liczba bloków BC: {total_all}")
    print(f"Nieznane bloki wymagające dodania: {len(all_unknown)}")
    
    if all_unknown:
        print(f"\nLista nieznanych bloków do dodania:")
        for bid in sorted(all_unknown):
            print(f"  - {bid}")
    else:
        print(f"\n✅ Wszystkie znalezione bloki są obsługiwane przez kod!")
    
    # Zapisz raport
    report_path = "output/bc_strefy_analysis.json"
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nRaport zapisano do: {report_path}")

if __name__ == "__main__":
    main()
