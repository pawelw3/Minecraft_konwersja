"""
Spatial IO Simulation - AE2 1.7.10 vs 1.18.2

Symulacja Spatial IO - zapis/odczyt obszarów przestrzeni 3D do komórek.
Bazuje na kodzie źródłowym:
- 1.7.10: appeng.tile.spatial.TileSpatialIOPort, appeng.spatial.StorageHelper
- 1.18.2: appeng.blockentity.spatial.SpatialIOPortBlockEntity
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set
import json


# =============================================================================
# TYPY I STAŁE
# =============================================================================

class SpatialCellSize(enum.Enum):
    """Rozmiary komórek Spatial Storage"""
    CELL_2 = (2, 2, 2)      # 2x2x2 = 8 bloków
    CELL_16 = (16, 16, 16)  # 16x16x16 = 4096 bloków
    CELL_128 = (128, 128, 128)  # 128x128x128 = 2,097,152 bloków
    
    def __init__(self, x: int, y: int, z: int):
        self.size_x = x
        self.size_y = y
        self.size_z = z
        self.volume = x * y * z


class SpatialIOStatus(enum.Enum):
    """Status operacji Spatial IO"""
    IDLE = "idle"
    SCANNING = "scanning"
    TRANSFERRING = "transferring"
    COMPLETED = "completed"
    ERROR_TOO_BIG = "error_too_big"
    ERROR_INVALID = "error_invalid"


# =============================================================================
# SYMULACJA 1.7.10
# =============================================================================

@dataclass
class BlockData1710:
    """
    Reprezentacja bloku w 1.7.10.
    Odpowiada: zapis w Spatial Storage Cell NBT
    """
    block_id: str
    metadata: int = 0
    tile_entity: Optional[Dict] = None
    
    def to_nbt(self) -> Dict:
        """Serializacja do NBT 1.7.10"""
        nbt = {
            'id': self.block_id,
            'meta': self.metadata
        }
        if self.tile_entity:
            nbt['te'] = self.tile_entity
        return nbt
    
    @classmethod
    def from_nbt(cls, nbt: Dict) -> BlockData1710:
        """Deserializacja z NBT 1.7.10"""
        return cls(
            block_id=nbt.get('id', 'minecraft:air'),
            metadata=nbt.get('meta', 0),
            tile_entity=nbt.get('te')
        )


@dataclass
class SpatialStorageCell1710:
    """
    Komórka Spatial Storage w 1.7.10.
    
    Przechowuje:
    - Rozmiar regionu (2, 16 lub 128)
    - Mapę bloków (x,y,z) -> BlockData
    - Pozycję origin (gdzie zostało zapisane)
    """
    cell_size: SpatialCellSize
    blocks: Dict[Tuple[int, int, int], BlockData1710] = field(default_factory=dict)
    origin: Optional[Tuple[int, int, int]] = None
    world_id: Optional[str] = None
    
    def get_block(self, x: int, y: int, z: int) -> Optional[BlockData1710]:
        """Pobiera blok na danej pozycji"""
        return self.blocks.get((x, y, z))
    
    def set_block(self, x: int, y: int, z: int, block: BlockData1710) -> None:
        """Ustawia blok na danej pozycji"""
        self.blocks[(x, y, z)] = block
    
    def is_full(self) -> bool:
        """Sprawdza czy komórka jest pełna"""
        return len(self.blocks) >= self.cell_size.volume
    
    def get_usage(self) -> float:
        """Zwraca procent wypełnienia"""
        if self.cell_size.volume == 0:
            return 0.0
        return (len(self.blocks) / self.cell_size.volume) * 100
    
    def to_nbt(self) -> Dict:
        """Eksportuje do NBT 1.7.10"""
        blocks_list = []
        for (x, y, z), block in self.blocks.items():
            block_nbt = block.to_nbt()
            block_nbt['pos'] = [x, y, z]
            blocks_list.append(block_nbt)
        
        return {
            'size': self.cell_size.name,
            'blocks': blocks_list,
            'origin': list(self.origin) if self.origin else None,
            'world': self.world_id
        }
    
    @classmethod
    def from_nbt(cls, nbt: Dict) -> SpatialStorageCell1710:
        """Importuje z NBT 1.7.10"""
        size_name = nbt.get('size', 'CELL_16')
        cell_size = SpatialCellSize[size_name]
        
        cell = cls(
            cell_size=cell_size,
            origin=tuple(nbt['origin']) if nbt.get('origin') else None,
            world_id=nbt.get('world')
        )
        
        for block_nbt in nbt.get('blocks', []):
            pos = tuple(block_nbt.pop('pos', [0, 0, 0]))
            block = BlockData1710.from_nbt(block_nbt)
            cell.blocks[pos] = block
        
        return cell


@dataclass
class SpatialIOPort1710:
    """
    Spatial IO Port w 1.7.10.
    
    Odpowiada: appeng.tile.spatial.TileSpatialIOPort
    
    Blok odpowiedzialny za zapis/odczyt obszarów do Spatial Cell.
    Wymaga struktury z Spatial Pylon.
    """
    port_id: str
    x: int
    y: int
    z: int
    
    inserted_cell: Optional[SpatialStorageCell1710] = None
    status: SpatialIOStatus = SpatialIOStatus.IDLE
    
    def insert_cell(self, cell: SpatialStorageCell1710) -> bool:
        """Wstawia komórkę do portu"""
        if self.inserted_cell is not None:
            return False
        self.inserted_cell = cell
        return True
    
    def capture_region(self, region_origin: Tuple[int, int, int], 
                      region_size: Tuple[int, int, int],
                      world_blocks: Dict[Tuple[int, int, int], BlockData1710]) -> bool:
        """
        Zapisuje obszar do komórki.
        
        Odpowiada: operacja wklejania obszaru do komórki (capture)
        """
        if not self.inserted_cell:
            return False
        
        self.status = SpatialIOStatus.SCANNING
        
        # Sprawdź czy obszar zmieści się w komórce
        volume = region_size[0] * region_size[1] * region_size[2]
        if volume > self.inserted_cell.cell_size.volume:
            self.status = SpatialIOStatus.ERROR_TOO_BIG
            return False
        
        self.status = SpatialIOStatus.TRANSFERRING
        
        # Kopiuj bloki
        ox, oy, oz = region_origin
        for (wx, wy, wz), block in world_blocks.items():
            # Przelicz względne pozycje
            rx = wx - ox
            ry = wy - oy
            rz = wz - oz
            
            if 0 <= rx < region_size[0] and 0 <= ry < region_size[1] and 0 <= rz < region_size[2]:
                self.inserted_cell.set_block(rx, ry, rz, block)
        
        self.inserted_cell.origin = region_origin
        self.status = SpatialIOStatus.COMPLETED
        return True
    
    def deploy_region(self, target_origin: Tuple[int, int, int]) -> Optional[Dict[Tuple[int, int, int], BlockData1710]]:
        """
        Odtwarza obszar z komórki w świecie.
        
        Zwraca mapę bloków do wstawienia.
        """
        if not self.inserted_cell:
            return None
        
        self.status = SpatialIOStatus.TRANSFERRING
        
        world_blocks = {}
        ox, oy, oz = target_origin
        
        for (rx, ry, rz), block in self.inserted_cell.blocks.items():
            # Przelicz na pozycje świata
            wx = ox + rx
            wy = oy + ry
            wz = oz + rz
            world_blocks[(wx, wy, wz)] = block
        
        self.status = SpatialIOStatus.COMPLETED
        return world_blocks


# =============================================================================
# SYMULACJA 1.18.2
# =============================================================================

@dataclass
class BlockData1182:
    """
    Reprezentacja bloku w 1.18.2.
    
    GŁÓWNE RÓŻNICE vs 1.7.10:
    - Brak metadata (zastąpione przez block state/NBT)
    - Obsługa BlockState
    """
    block_id: str
    block_state: Optional[Dict] = None  # Zamiast metadata
    tile_entity: Optional[Dict] = None
    
    def to_nbt(self) -> Dict:
        """Serializacja do NBT 1.18.2"""
        nbt = {
            'id': self.block_id
        }
        if self.block_state:
            nbt['state'] = self.block_state
        if self.tile_entity:
            nbt['te'] = self.tile_entity
        return nbt
    
    @classmethod
    def from_nbt(cls, nbt: Dict) -> BlockData1182:
        """Deserializacja z NBT 1.18.2"""
        return cls(
            block_id=nbt.get('id', 'minecraft:air'),
            block_state=nbt.get('state'),
            tile_entity=nbt.get('te')
        )


@dataclass
class SpatialStorageCell1182:
    """
    Komórka Spatial Storage w 1.18.2.
    
    GŁÓWNE RÓŻNICE vs 1.7.10:
    - Lepsza kompresja danych
    - Obsługa BlockState zamiast metadata
    - Maksymalny rozmiar 128³ (identyczny)
    """
    cell_size: SpatialCellSize
    blocks: Dict[Tuple[int, int, int], BlockData1182] = field(default_factory=dict)
    origin: Optional[Tuple[int, int, int]] = None
    world_id: Optional[str] = None
    
    # Nowość w 1.18.2 - kompresja paletowa
    block_palette: Dict[str, int] = field(default_factory=dict)
    use_palette: bool = True
    
    def get_block(self, x: int, y: int, z: int) -> Optional[BlockData1182]:
        return self.blocks.get((x, y, z))
    
    def set_block(self, x: int, y: int, z: int, block: BlockData1182) -> None:
        # Dodaj do palety jeśli używana
        if self.use_palette and block.block_id not in self.block_palette:
            self.block_palette[block.block_id] = len(self.block_palette)
        
        self.blocks[(x, y, z)] = block
    
    def is_full(self) -> bool:
        return len(self.blocks) >= self.cell_size.volume
    
    def get_usage(self) -> float:
        if self.cell_size.volume == 0:
            return 0.0
        return (len(self.blocks) / self.cell_size.volume) * 100
    
    def to_nbt(self) -> Dict:
        """Eksportuje do NBT 1.18.2"""
        # Użyj kompresji paletowej
        if self.use_palette:
            blocks_list = []
            for (x, y, z), block in self.blocks.items():
                block_data = {
                    'pos': [x, y, z],
                    'id': self.block_palette.get(block.block_id, 0),
                    'state': block.block_state
                }
                if block.tile_entity:
                    block_data['te'] = block.tile_entity
                blocks_list.append(block_data)
            
            return {
                'size': self.cell_size.name,
                'palette': self.block_palette,
                'blocks': blocks_list,
                'origin': list(self.origin) if self.origin else None,
                'world': self.world_id,
                'compressed': True
            }
        else:
            # Format niekompresowany (jak 1.7.10)
            blocks_list = []
            for (x, y, z), block in self.blocks.items():
                block_nbt = block.to_nbt()
                block_nbt['pos'] = [x, y, z]
                blocks_list.append(block_nbt)
            
            return {
                'size': self.cell_size.name,
                'blocks': blocks_list,
                'origin': list(self.origin) if self.origin else None,
                'world': self.world_id,
                'compressed': False
            }
    
    @classmethod
    def from_nbt(cls, nbt: Dict) -> SpatialStorageCell1182:
        """Importuje z NBT 1.18.2"""
        size_name = nbt.get('size', 'CELL_16')
        cell_size = SpatialCellSize[size_name]
        
        cell = cls(
            cell_size=cell_size,
            origin=tuple(nbt['origin']) if nbt.get('origin') else None,
            world_id=nbt.get('world'),
            use_palette=nbt.get('compressed', False)
        )
        
        # Odtwórz paletę
        if cell.use_palette:
            palette = {v: k for k, v in nbt.get('palette', {}).items()}
            
            for block_nbt in nbt.get('blocks', []):
                pos = tuple(block_nbt.pop('pos', [0, 0, 0]))
                block_id = palette.get(block_nbt.get('id', 0), 'minecraft:air')
                block = BlockData1182(
                    block_id=block_id,
                    block_state=block_nbt.get('state'),
                    tile_entity=block_nbt.get('te')
                )
                cell.blocks[pos] = block
        else:
            for block_nbt in nbt.get('blocks', []):
                pos = tuple(block_nbt.pop('pos', [0, 0, 0]))
                block = BlockData1182.from_nbt(block_nbt)
                cell.blocks[pos] = block
        
        return cell


@dataclass
class SpatialIOPort1182:
    """
    Spatial IO Port w 1.18.2.
    
    GŁÓWNE RÓŻNICE vs 1.7.10:
    - Lepsza obsługa błędów
    - Integracja z Spatial Anchor
    - Obsłaga BlockState
    """
    port_id: str
    x: int
    y: int
    z: int
    
    inserted_cell: Optional[SpatialStorageCell1182] = None
    status: SpatialIOStatus = SpatialIOStatus.IDLE
    
    # Nowość w 1.18.2
    keep_loaded: bool = False  # Utrzymywanie chunka załadowanego
    
    def insert_cell(self, cell: SpatialStorageCell1182) -> bool:
        if self.inserted_cell is not None:
            return False
        self.inserted_cell = cell
        return True
    
    def capture_region(self, region_origin: Tuple[int, int, int],
                      region_size: Tuple[int, int, int],
                      world_blocks: Dict[Tuple[int, int, int], BlockData1182]) -> bool:
        """Zapisuje obszar do komórki (1.18.2)"""
        if not self.inserted_cell:
            return False
        
        self.status = SpatialIOStatus.SCANNING
        
        volume = region_size[0] * region_size[1] * region_size[2]
        if volume > self.inserted_cell.cell_size.volume:
            self.status = SpatialIOStatus.ERROR_TOO_BIG
            return False
        
        self.status = SpatialIOStatus.TRANSFERRING
        
        ox, oy, oz = region_origin
        for (wx, wy, wz), block in world_blocks.items():
            rx = wx - ox
            ry = wy - oy
            rz = wz - oz
            
            if 0 <= rx < region_size[0] and 0 <= ry < region_size[1] and 0 <= rz < region_size[2]:
                self.inserted_cell.set_block(rx, ry, rz, block)
        
        self.inserted_cell.origin = region_origin
        self.status = SpatialIOStatus.COMPLETED
        return True
    
    def deploy_region(self, target_origin: Tuple[int, int, int]) -> Optional[Dict[Tuple[int, int, int], BlockData1182]]:
        """Odtwarza obszar z komórki (1.18.2)"""
        if not self.inserted_cell:
            return None
        
        self.status = SpatialIOStatus.TRANSFERRING
        
        world_blocks = {}
        ox, oy, oz = target_origin
        
        for (rx, ry, rz), block in self.inserted_cell.blocks.items():
            wx = ox + rx
            wy = oy + ry
            wz = oz + rz
            world_blocks[(wx, wy, wz)] = block
        
        self.status = SpatialIOStatus.COMPLETED
        return world_blocks


# =============================================================================
# KONWERSJA MIĘDZY WERSJAMI
# =============================================================================

def convert_metadata_to_blockstate(metadata: int, block_id: str) -> Dict:
    """
    Konwertuje metadata (1.7.10) do BlockState (1.18.2).
    
    To UPROSZCZONA konwersja - w rzeczywistości wymaga mapowania block state.
    """
    # Przykładowa konwersja dla wool
    if "wool" in block_id:
        colors = ["white", "orange", "magenta", "light_blue", "yellow", 
                  "lime", "pink", "gray", "light_gray", "cyan", 
                  "purple", "blue", "brown", "green", "red", "black"]
        if 0 <= metadata < len(colors):
            return {"color": colors[metadata]}
    
    # Przykładowa konwersja dla stairs
    if "stairs" in block_id:
        faces = ["east", "west", "south", "north"]
        if 0 <= metadata < 4:
            return {"facing": faces[metadata]}
    
    # Domyślnie - zachowaj metadata jako wartość
    return {"meta": metadata}


def convert_blockstate_to_metadata(block_state: Dict) -> int:
    """Konwertuje BlockState (1.18.2) do metadata (1.7.10)"""
    if "meta" in block_state:
        return block_state["meta"]
    
    # Przykładowa odwrotna konwersja dla wool
    if "color" in block_state:
        colors = ["white", "orange", "magenta", "light_blue", "yellow",
                  "lime", "pink", "gray", "light_gray", "cyan",
                  "purple", "blue", "brown", "green", "red", "black"]
        try:
            return colors.index(block_state["color"])
        except ValueError:
            return 0
    
    return 0


def convert_spatial_cell_1710_to_1182(cell_1710: SpatialStorageCell1710) -> SpatialStorageCell1182:
    """Konwertuje komórkę Spatial z 1.7.10 do 1.18.2"""
    cell_1182 = SpatialStorageCell1182(
        cell_size=cell_1710.cell_size,
        origin=cell_1710.origin,
        world_id=cell_1710.world_id,
        use_palette=True  # Użyj kompresji
    )
    
    for pos, block_1710 in cell_1710.blocks.items():
        # Konwersja metadata -> block_state
        block_state = convert_metadata_to_blockstate(block_1710.metadata, block_1710.block_id)
        
        block_1182 = BlockData1182(
            block_id=block_1710.block_id,
            block_state=block_state if block_state else None,
            tile_entity=block_1710.tile_entity
        )
        
        cell_1182.set_block(pos[0], pos[1], pos[2], block_1182)
    
    return cell_1182


def convert_spatial_cell_1182_to_1710(cell_1182: SpatialStorageCell1182) -> SpatialStorageCell1710:
    """Konwertuje komórkę Spatial z 1.18.2 do 1.7.10"""
    cell_1710 = SpatialStorageCell1710(
        cell_size=cell_1182.cell_size,
        origin=cell_1182.origin,
        world_id=cell_1182.world_id
    )
    
    for pos, block_1182 in cell_1182.blocks.items():
        # Konwersja block_state -> metadata
        metadata = convert_blockstate_to_metadata(block_1182.block_state or {})
        
        block_1710 = BlockData1710(
            block_id=block_1182.block_id,
            metadata=metadata,
            tile_entity=block_1182.tile_entity
        )
        
        cell_1710.set_block(pos[0], pos[1], pos[2], block_1710)
    
    return cell_1710


# =============================================================================
# TESTY I DEMONSTRACJA
# =============================================================================

def test_spatial_capture_1710():
    """Test zapisu obszaru w 1.7.10"""
    print("="*60)
    print("TEST SPATIAL IO - ZAPIS (1.7.10)")
    print("="*60)
    
    # Utwórz komórkę 16³
    cell = SpatialStorageCell1710(cell_size=SpatialCellSize.CELL_16)
    
    # Symuluj bloki w świecie (mały dom)
    world_blocks = {
        (0, 0, 0): BlockData1710("minecraft:cobblestone", 0),
        (1, 0, 0): BlockData1710("minecraft:cobblestone", 0),
        (0, 0, 1): BlockData1710("minecraft:cobblestone", 0),
        (1, 0, 1): BlockData1710("minecraft:cobblestone", 0),
        (0, 1, 0): BlockData1710("minecraft:planks", 0),  # Oak
        (1, 1, 0): BlockData1710("minecraft:planks", 0),
        (0, 1, 1): BlockData1710("minecraft:planks", 0),
        (1, 1, 1): BlockData1710("minecraft:planks", 0),
        (0, 2, 0): BlockData1710("minecraft:glass", 0),  # Okno
        (1, 2, 0): BlockData1710("minecraft:planks", 0),
    }
    
    # Zapisz do komórki
    port = SpatialIOPort1710("port1", 100, 64, 100)
    port.insert_cell(cell)
    
    region_origin = (0, 0, 0)
    region_size = (16, 16, 16)
    
    print(f"\nZapisywanie obszaru {region_size} z {len(world_blocks)} blokami...")
    
    if port.capture_region(region_origin, region_size, world_blocks):
        print(f"✓ Obszar zapisany!")
        print(f"  Bloków w komórce: {len(cell.blocks)}")
        print(f"  Wypełnienie: {cell.get_usage():.2f}%")
        print(f"  Origin: {cell.origin}")
    
    # Wyświetl NBT
    print(f"\nNBT (fragment): {json.dumps(cell.to_nbt(), indent=2)[:400]}...")


def test_spatial_capture_1182():
    """Test zapisu obszaru w 1.18.2"""
    print("\n" + "="*60)
    print("TEST SPATIAL IO - ZAPIS (1.18.2)")
    print("="*60)
    
    cell = SpatialStorageCell1182(cell_size=SpatialCellSize.CELL_16, use_palette=True)
    
    # Bloki z BlockState
    world_blocks = {
        (0, 0, 0): BlockData1182("minecraft:cobblestone"),
        (1, 0, 0): BlockData1182("minecraft:cobblestone"),
        (0, 1, 0): BlockData1182("minecraft:oak_planks"),  # Zamiast planks:0
        (1, 1, 0): BlockData1182("minecraft:oak_planks"),
        (0, 2, 0): BlockData1182("minecraft:glass"),
    }
    
    port = SpatialIOPort1182("port1", 100, 64, 100)
    port.insert_cell(cell)
    
    print(f"\nZapisywanie obszaru z {len(world_blocks)} blokami...")
    print("(z kompresją paletową)")
    
    if port.capture_region((0, 0, 0), (16, 16, 16), world_blocks):
        print(f"✓ Obszar zapisany!")
        print(f"  Bloków: {len(cell.blocks)}")
        print(f"  Paleta bloków: {cell.block_palette}")
        print(f"  Kompresja: {len(cell.block_palette)} unikalnych typów")
    
    print(f"\nNBT (fragment): {json.dumps(cell.to_nbt(), indent=2)[:500]}...")


def test_conversion():
    """Test konwersji między wersjami"""
    print("\n" + "="*60)
    print("TEST KONWERSJI 1.7.10 → 1.18.2")
    print("="*60)
    
    # Utwórz komórkę 1.7.10 z kolorową wełną (metadata)
    cell_1710 = SpatialStorageCell1710(cell_size=SpatialCellSize.CELL_2)
    
    # Różne kolory wool (metadata 0-3)
    cell_1710.set_block(0, 0, 0, BlockData1710("minecraft:wool", 0))  # White
    cell_1710.set_block(1, 0, 0, BlockData1710("minecraft:wool", 1))  # Orange
    cell_1710.set_block(0, 0, 1, BlockData1710("minecraft:wool", 2))  # Magenta
    cell_1710.set_block(1, 0, 1, BlockData1710("minecraft:wool", 3))  # Light Blue
    
    print("\nKomórka 1.7.10 (metadata):")
    for pos, block in cell_1710.blocks.items():
        print(f"  {pos}: {block.block_id}:{block.metadata}")
    
    # Konwertuj do 1.18.2
    cell_1182 = convert_spatial_cell_1710_to_1182(cell_1710)
    
    print("\nKomórka 1.18.2 (block_state):")
    for pos, block in cell_1182.blocks.items():
        print(f"  {pos}: {block.block_id} {block.block_state}")
    
    print("\n✓ Konwersja zachowała kolory wełny!")


def test_deploy():
    """Test odtworzenia obszaru"""
    print("\n" + "="*60)
    print("TEST ODTWORZENIA OBSZARU (DEPLOY)")
    print("="*60)
    
    # Utwórz i zapisz komórkę
    cell = SpatialStorageCell1710(cell_size=SpatialCellSize.CELL_2)
    cell.set_block(0, 0, 0, BlockData1710("minecraft:diamond_block", 0))
    cell.set_block(1, 0, 0, BlockData1710("minecraft:gold_block", 0))
    cell.origin = (100, 64, 100)
    
    port = SpatialIOPort1710("port1", 200, 70, 200)
    port.insert_cell(cell)
    
    # Odtwórz w nowej lokalizacji
    target = (200, 70, 200)
    world_blocks = port.deploy_region(target)
    
    print(f"\nOdtwarzanie z komórki...")
    print(f"  Początek docelowy: {target}")
    print(f"  Bloki do postawienia:")
    for pos, block in world_blocks.items():
        print(f"    {pos}: {block.block_id}")
    
    print("\n✓ Obszar odtworzony!")


def compare_cell_sizes():
    """Porównuje rozmiary komórek"""
    print("\n" + "="*60)
    print("PORÓWNANIE ROZMIARÓW KOMÓREK SPATIAL")
    print("="*60)
    
    for size in SpatialCellSize:
        print(f"\n{size.name}:")
        print(f"  Wymiary: {size.size_x}×{size.size_y}×{size.size_z}")
        print(f"  Objętość: {size.volume:,} bloków")
        print(f"  Dostępność: 1.7.10 ✓ | 1.18.2 ✓")


def main():
    """Główna funkcja demonstracyjna"""
    print("="*60)
    print("SPATIAL IO SIMULATION - AE2 1.7.10 vs 1.18.2")
    print("="*60)
    
    test_spatial_capture_1710()
    test_spatial_capture_1182()
    test_conversion()
    test_deploy()
    compare_cell_sizes()
    
    print("\n" + "="*60)
    print("SYMULACJA ZAKOŃCZONA POMYŚLNIE")
    print("="*60)
    print("\nWnioski dla konwersji:")
    print("1. Metadata (1.7.10) → BlockState (1.18.2) - wymaga mapowania")
    print("2. 1.18.2 używa kompresji paletowej - mniejsze NBT")
    print("3. Rozmiary komórek identyczne (2, 16, 128)")
    print("4. Struktura Spatial Pylon niezmienna")
    print("5. Origin i world ID zachowywane")


if __name__ == "__main__":
    main()
