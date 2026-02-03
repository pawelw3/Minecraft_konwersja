"""
Enchanting Plus Chunk Parser

Integracja z minecraft_map_parser do wykrywania bloków Enchanting Plus w chunkach.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
import json

from .mappings.block_mappings import is_enchantingplus_block, get_block_name


def get_project_root() -> Path:
    """Zwraca ścieżkę do root projektu."""
    current = Path(__file__).resolve()
    # Idź w górę aż znajdziesz folder z 'mapa_1710' lub 'src'
    for parent in current.parents:
        if (parent / 'mapa_1710').exists() or (parent / 'src').exists():
            return parent
    return current.parents[3]  # src/converters/enchantingplus -> src/converters -> src -> root


@dataclass
class EPBlockInChunk:
    """Reprezentuje blok Enchanting Plus znaleziony w chunku."""
    x: int
    y: int
    z: int
    block_id: str          # np. "EnchantingPlus:enchanting_table"
    block_name: str        # np. "enchanting_table"
    chunk_x: int
    chunk_z: int
    tile_entity: Optional[Dict[str, Any]] = None
    
    @property
    def absolute_pos(self) -> Tuple[int, int, int]:
        """Zwraca absolutną pozycję (x, y, z)."""
        return (self.x, self.y, self.z)
    
    @property
    def region_pos(self) -> Tuple[int, int]:
        """Zwraca pozycję regionu (rx, rz)."""
        return (self.chunk_x >> 5, self.chunk_z >> 5)
    
    def to_dict(self) -> Dict[str, Any]:
        """Eksportuje do słownika."""
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'block_id': self.block_id,
            'block_name': self.block_name,
            'chunk_x': self.chunk_x,
            'chunk_z': self.chunk_z,
            'region_x': self.region_pos[0],
            'region_z': self.region_pos[1],
            'has_tile_entity': self.tile_entity is not None,
            'tile_entity_keys': list(self.tile_entity.keys()) if self.tile_entity else []
        }


@dataclass
class ChunkAnalysisResult:
    """Wynik analizy chunka."""
    chunk_x: int
    chunk_z: int
    ep_blocks: List[EPBlockInChunk]
    total_tile_entities: int
    
    @property
    def has_ep_blocks(self) -> bool:
        """Czy chunk zawiera bloki EP."""
        return len(self.ep_blocks) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Eksportuje do słownika."""
        return {
            'chunk_x': self.chunk_x,
            'chunk_z': self.chunk_z,
            'has_ep_blocks': self.has_ep_blocks,
            'ep_blocks_count': len(self.ep_blocks),
            'total_tile_entities': self.total_tile_entities,
            'ep_blocks': [b.to_dict() for b in self.ep_blocks]
        }


class EPChunkParser:
    """
    Parser chunków do wykrywania bloków Enchanting Plus.
    
    Integruje się z AnvilParser z minecraft_map_parser.
    """
    
    def __init__(self, world_path: Optional[str] = None):
        """
        Inicjalizuje parser.
        
        Args:
            world_path: Ścieżka do świata 1.7.10 (opcjonalnie, domyślnie mapa_1710)
        """
        if world_path is None:
            world_path = str(get_project_root() / 'mapa_1710')
        
        self.world_path = Path(world_path)
        self.region_path = self.world_path / 'region'
        
        # Lazy import aby uniknąć circular dependencies
        self._anvil_parser = None
    
    def _get_anvil_parser(self, region_file: str):
        """Lazy initialization of AnvilParser."""
        if self._anvil_parser is None:
            try:
                from ...minecraft_map_parser.anvil_parser import AnvilParser
                self._anvil_parser = AnvilParser
            except ImportError:
                # Fallback - spróbuj bezpośrednio
                import sys
                project_root = get_project_root()
                sys.path.insert(0, str(project_root / 'src'))
                from minecraft_map_parser.anvil_parser import AnvilParser
                self._anvil_parser = AnvilParser
        
        return self._anvil_parser(region_file)
    
    def analyze_chunk(self, chunk_x: int, chunk_z: int) -> ChunkAnalysisResult:
        """
        Analizuje pojedynczy chunk w poszukiwaniu bloków EP.
        
        Args:
            chunk_x: Współrzędna X chunka (globalna)
            chunk_z: Współrzędna Z chunka (globalna)
            
        Returns:
            ChunkAnalysisResult z wynikami analizy
        """
        # Oblicz pozycję regionu
        region_x = chunk_x >> 5
        region_z = chunk_z >> 5
        
        # Oblicz lokalne współrzędne chunka w regionie (0-31)
        local_chunk_x = chunk_x & 0x1F  # Równoważne chunk_x % 32
        local_chunk_z = chunk_z & 0x1F  # Równoważne chunk_z % 32
        
        region_file = self.region_path / f'r.{region_x}.{region_z}.mca'
        
        if not region_file.exists():
            return ChunkAnalysisResult(
                chunk_x=chunk_x,
                chunk_z=chunk_z,
                ep_blocks=[],
                total_tile_entities=0
            )
        
        try:
            parser = self._get_anvil_parser(str(region_file))
            # AnvilParser.get_chunk() wymaga lokalnych współrzędnych (0-31)
            chunk_data = parser.get_chunk(local_chunk_x, local_chunk_z)
            
            if chunk_data is None:
                return ChunkAnalysisResult(
                    chunk_x=chunk_x,
                    chunk_z=chunk_z,
                    ep_blocks=[],
                    total_tile_entities=0
                )
            
            # Pobierz tile entities
            tile_entities = chunk_data.get_tile_entities()
            ep_blocks = []
            
            for te in tile_entities:
                if not isinstance(te, dict):
                    continue
                
                block_id = te.get('id', '')
                
                if is_enchantingplus_block(block_id):
                    x = te.get('x', 0)
                    y = te.get('y', 0)
                    z = te.get('z', 0)
                    
                    ep_block = EPBlockInChunk(
                        x=x,
                        y=y,
                        z=z,
                        block_id=block_id,
                        block_name=get_block_name(block_id),
                        chunk_x=chunk_x,
                        chunk_z=chunk_z,
                        tile_entity=te
                    )
                    ep_blocks.append(ep_block)
            
            return ChunkAnalysisResult(
                chunk_x=chunk_x,
                chunk_z=chunk_z,
                ep_blocks=ep_blocks,
                total_tile_entities=len(tile_entities)
            )
            
        except Exception as e:
            # Log error but don't crash
            print(f"EPC-PARSER-WARNING: Error analyzing chunk ({chunk_x}, {chunk_z}): {e}")
            return ChunkAnalysisResult(
                chunk_x=chunk_x,
                chunk_z=chunk_z,
                ep_blocks=[],
                total_tile_entities=0
            )
    
    def analyze_region(self, region_x: int, region_z: int) -> List[ChunkAnalysisResult]:
        """
        Analizuje cały region (32x32 chunków).
        
        Args:
            region_x: Współrzędna X regionu
            region_z: Współrzędna Z regionu
            
        Returns:
            Lista ChunkAnalysisResult dla chunków z blokami EP
        """
        results = []
        base_chunk_x = region_x * 32
        base_chunk_z = region_z * 32
        
        for local_x in range(32):
            for local_z in range(32):
                chunk_x = base_chunk_x + local_x
                chunk_z = base_chunk_z + local_z
                
                result = self.analyze_chunk(chunk_x, chunk_z)
                if result.has_ep_blocks:
                    results.append(result)
        
        return results
    
    def scan_all_regions(self, 
                         progress_callback=None,
                         max_regions: Optional[int] = None) -> Dict[str, Any]:
        """
        Skanuje wszystkie regiony w świecie.
        
        Args:
            progress_callback: Funkcja (percent, message) -> None
            max_regions: Maksymalna liczba regionów do przeskanowania (opcjonalnie)
            
        Returns:
            Słownik z wynikami skanowania
        """
        if not self.region_path.exists():
            return {
                'total_regions': 0,
                'scanned_regions': 0,
                'chunks_with_ep': 0,
                'total_ep_blocks': 0,
                'blocks_by_type': {},
                'results': []
            }
        
        region_files = list(self.region_path.glob('r.*.*.mca'))
        total_regions = len(region_files)
        
        if max_regions and max_regions < total_regions:
            region_files = region_files[:max_regions]
            total_regions = max_regions
        
        all_results = []
        scanned = 0
        total_ep_blocks = 0
        blocks_by_type = {}
        
        for region_file in region_files:
            # Parsuj nazwę regionu
            parts = region_file.stem.split('.')
            if len(parts) != 3:
                continue
            
            try:
                region_x = int(parts[1])
                region_z = int(parts[2])
            except ValueError:
                continue
            
            results = self.analyze_region(region_x, region_z)
            
            for result in results:
                all_results.append(result.to_dict())
                total_ep_blocks += len(result.ep_blocks)
                
                for block in result.ep_blocks:
                    block_type = block.block_id
                    blocks_by_type[block_type] = blocks_by_type.get(block_type, 0) + 1
            
            scanned += 1
            
            if progress_callback:
                percent = (scanned / total_regions) * 100
                progress_callback(percent, f"Skanowanie regionu r.{region_x}.{region_z}.mca...")
        
        return {
            'total_regions': total_regions,
            'scanned_regions': scanned,
            'chunks_with_ep': len(all_results),
            'total_ep_blocks': total_ep_blocks,
            'blocks_by_type': blocks_by_type,
            'results': all_results
        }
    
    def debug_chunk_block_ids(self, chunk_x: int, chunk_z: int) -> Dict[str, Any]:
        """
        DEBUG: Zwraca wszystkie ID bloków z sekcji chunka (z uwzględnieniem Add/AddBlocks).
        
        WAŻNE: W Minecraft 1.7.10 bloki o ID > 255 wymagają odczytu z tablicy Add/AddBlocks.
        Ta metoda pokazuje rzeczywiste ID bloków po złożeniu Blocks + Add.
        
        Args:
            chunk_x: Współrzędna X chunka (globalna)
            chunk_z: Współrzędna Z chunka (globalna)
            
        Returns:
            Słownik z informacjami debugującymi
        """
        from ...minecraft_map_parser.anvil_parser import AnvilParser
        
        region_x = chunk_x >> 5
        region_z = chunk_z >> 5
        local_chunk_x = chunk_x & 0x1F
        local_chunk_z = chunk_z & 0x1F
        region_file = self.region_path / f'r.{region_x}.{region_z}.mca'
        
        if not region_file.exists():
            return {'error': f'Region file not found: {region_file}'}
        
        try:
            parser = AnvilParser(str(region_file))
            chunk_data = parser.get_chunk(local_chunk_x, local_chunk_z)
            
            if chunk_data is None:
                return {'error': 'Chunk not found'}
            
            # Pobierz ID bloków z sekcji (z uwzględnieniem Add/AddBlocks)
            block_ids = chunk_data.get_block_ids_from_sections()
            
            # Podziel na zakresy
            vanilla_ids = [bid for bid in block_ids if bid < 256]
            modded_ids = [bid for bid in block_ids if bid >= 256]
            
            return {
                'chunk_x': chunk_x,
                'chunk_z': chunk_z,
                'total_unique_ids': len(block_ids),
                'vanilla_ids_count': len(vanilla_ids),
                'modded_ids_count': len(modded_ids),
                'vanilla_ids': vanilla_ids[:20],  # Max 20 pierwszych
                'modded_ids': modded_ids[:50],    # Max 50 pierwszych (ważne!)
                'has_add_blocks': True,  # Metoda już uwzględnia Add
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def debug_scan_for_modded_blocks(self, 
                                     max_regions: int = 5,
                                     min_block_id: int = 256) -> Dict[str, Any]:
        """
        DEBUG: Skanuje regiony w poszukiwaniu bloków modowanych (ID >= 256).
        
        Używa poprawnej obsługi Add/AddBlocks.
        
        Args:
            max_regions: Maksymalna liczba regionów do przeskanowania
            min_block_id: Minimalne ID bloku do wykrycia (domyślnie 256 dla modded)
            
        Returns:
            Słownik z wynikami skanowania
        """
        from ...minecraft_map_parser.anvil_parser import AnvilParser
        
        if not self.region_path.exists():
            return {'error': 'Region path not found'}
        
        region_files = list(self.region_path.glob('r.*.*.mca'))[:max_regions]
        
        results = {
            'scanned_regions': 0,
            'chunks_with_modded': 0,
            'total_modded_ids_found': set(),
            'chunks_details': []
        }
        
        for region_file in region_files:
            parts = region_file.stem.split('.')
            if len(parts) != 3:
                continue
            
            try:
                region_x = int(parts[1])
                region_z = int(parts[2])
            except ValueError:
                continue
            
            try:
                parser = AnvilParser(str(region_file))
                
                for local_x in range(32):
                    for local_z in range(32):
                        global_chunk_x = region_x * 32 + local_x
                        global_chunk_z = region_z * 32 + local_z
                        
                        chunk_data = parser.get_chunk(local_x, local_z)
                        if chunk_data is None:
                            continue
                        
                        block_ids = chunk_data.get_block_ids_from_sections()
                        modded_ids = [bid for bid in block_ids if bid >= min_block_id]
                        
                        if modded_ids:
                            results['chunks_with_modded'] += 1
                            results['total_modded_ids_found'].update(modded_ids)
                            
                            if len(results['chunks_details']) < 10:  # Max 10 szczegółów
                                results['chunks_details'].append({
                                    'chunk_x': global_chunk_x,
                                    'chunk_z': global_chunk_z,
                                    'modded_ids': sorted(modded_ids)[:20]
                                })
                
                results['scanned_regions'] += 1
                
            except Exception as e:
                print(f"Error scanning region {region_file}: {e}")
                continue
        
        results['total_modded_ids_found'] = sorted(list(results['total_modded_ids_found']))
        return results


def main():
    """Demo parsera chunków EP."""
    print("=" * 60)
    print("ENCHANTING PLUS CHUNK PARSER - Demo")
    print("=" * 60)
    
    parser = EPChunkParser()
    
    print(f"\nŚcieżka do świata: {parser.world_path}")
    print(f"Ścieżka do regionów: {parser.region_path}")
    
    # Sprawdź czy istnieją regiony
    if not parser.region_path.exists():
        print("\nBrak folderu regionów!")
        return
    
    region_files = list(parser.region_path.glob('r.*.*.mca'))
    print(f"Znaleziono {len(region_files)} plików regionów")
    
    if not region_files:
        print("\nBrak plików regionów do analizy.")
        return
    
    # Demo: skanowanie z callbackiem
    print("\n" + "=" * 60)
    print("Skanowanie mapy (max 10 regionów)...")
    print("=" * 60)
    
    def progress(percent, message):
        print(f"[{percent:5.1f}%] {message}")
    
    results = parser.scan_all_regions(
        progress_callback=progress,
        max_regions=10
    )
    
    print("\n" + "=" * 60)
    print("Wyniki skanowania:")
    print("=" * 60)
    print(f"Przeskanowane regiony: {results['scanned_regions']}")
    print(f"Chunki z blokami EP: {results['chunks_with_ep']}")
    print(f"Całkowita liczba bloków EP: {results['total_ep_blocks']}")
    
    if results['blocks_by_type']:
        print("\nBloki według typu:")
        for block_type, count in results['blocks_by_type'].items():
            print(f"  {block_type}: {count}")
    else:
        print("\nNie znaleziono bloków Enchanting Plus.")
    
    # Zapisz wyniki
    output_dir = Path('output/ep_scan')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / 'chunk_scan_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nWyniki zapisano do: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
