"""
Symulacja Crate Pile z Better Storage 1.7.10

Crate Pile to system magazynowania gdzie:
- Każdy crate w świecie ma tylko crateId (w TileEntity)
- Właściwa zawartość jest w osobnych plikach: <world>/data/crates/<id>.dat
- Wiele crate'ów może dzielić to samo inventory (Crate Pile)
"""

import os
import struct
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import gzip


@dataclass
class CratePileRegion:
    """Region zajmowany przez Crate Pile"""
    min_x: int
    min_y: int
    min_z: int
    max_x: int
    max_y: int
    max_z: int
    
    @property
    def volume(self) -> int:
        """Objętość regionu w blokach"""
        return (self.max_x - self.min_x + 1) * \
               (self.max_y - self.min_y + 1) * \
               (self.max_z - self.min_z + 1)
    
    def contains(self, x: int, y: int, z: int) -> bool:
        """Sprawdza czy współrzędne są w regionie"""
        return (self.min_x <= x <= self.max_x and
                self.min_y <= y <= self.max_y and
                self.min_z <= z <= self.max_z)


@dataclass
class CratePileData:
    """Dane pojedynczego Crate Pile z pliku <id>.dat"""
    pile_id: int
    items: List[Dict[str, Any]] = field(default_factory=list)
    num_crates: int = 0
    region: Optional[CratePileRegion] = None
    
    @property
    def slots_per_crate(self) -> int:
        """Liczba slotów per crate (stałe 18 w BS)"""
        return 18
    
    def get_items_for_crate(self, crate_index: int) -> List[Dict[str, Any]]:
        """
        Rozdziela itemy dla konkretnego crate'a z pile.
        
        Args:
            crate_index: Indeks crate'a w pile (0-based)
            
        Returns:
            Lista itemów przypisanych do tego crate'a
        """
        if not self.items:
            return []
        
        # Rozdzielamy proporcjonalnie lub sekwencyjnie
        slots_per_crate = self.slots_per_crate
        start_slot = crate_index * slots_per_crate
        end_slot = start_slot + slots_per_crate
        
        # Filtrujemy itemy które mieszczą się w zakresie slotów
        crate_items = []
        for item in self.items:
            slot = item.get('Slot', 0)
            if start_slot <= slot < end_slot:
                # Dostosowujemy slot do nowego zakresu (0-17)
                new_item = item.copy()
                new_item['Slot'] = slot - start_slot
                crate_items.append(new_item)
        
        return crate_items


@dataclass
class CrateLocation:
    """Lokalizacja crate'a w świecie"""
    x: int
    y: int
    z: int
    crate_id: int
    pile_data: Optional[CratePileData] = None
    
    @property
    def is_valid(self) -> bool:
        """Czy crate ma przypisane dane pile"""
        return self.pile_data is not None


class CratePileLoader:
    """
    Ładuje dane Crate Pile z plików <world>/data/crates/<id>.dat
    
    Format pliku (NBT):
    {
        data: {
            items: NBTTagList (wspólna zawartość całego pile)
            numCrates: int (liczba crate'ów w pile)
            region: {minX, minY, minZ, maxX, maxY, maxZ}
        }
    }
    """
    
    def __init__(self, world_path: str):
        """
        Args:
            world_path: Ścieżka do folderu świata (mapa_1710)
        """
        self.world_path = Path(world_path)
        self.crates_dir = self.world_path / "data" / "crates"
        self._pile_cache: Dict[int, CratePileData] = {}
        self._crate_locations: Dict[Tuple[int, int, int], CrateLocation] = {}
    
    def load_all_piles(self) -> Dict[int, CratePileData]:
        """
        Wczytuje wszystkie pliki Crate Pile.
        
        Returns:
            Słownik: pile_id -> CratePileData
        """
        if not self.crates_dir.exists():
            return {}
        
        piles = {}
        for file_path in self.crates_dir.glob("*.dat"):
            try:
                pile_id = int(file_path.stem)
                pile_data = self._read_pile_file(file_path, pile_id)
                if pile_data:
                    piles[pile_id] = pile_data
                    self._pile_cache[pile_id] = pile_data
            except (ValueError, OSError) as e:
                print(f"Warning: Nie można odczytać {file_path}: {e}")
                continue
        
        return piles
    
    def _read_pile_file(self, file_path: Path, pile_id: int) -> Optional[CratePileData]:
        """
        Odczytuje pojedynczy plik .dat Crate Pile.
        
        Obsługuje format:
        - Skompresowany GZIP (zwykły format NBT)
        - Nieskompresowany (jak w oryginalnym BS)
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            
            # Próbujemy odczytać jako NBT
            nbt_data = self._parse_nbt(raw_data)
            
            if nbt_data is None:
                return None
            
            # Ekstrahujemy dane
            data = nbt_data.get('data', {})
            
            items = data.get('items', [])
            num_crates = data.get('numCrates', 0)
            
            # Region
            region_data = data.get('region', {})
            region = None
            if region_data:
                region = CratePileRegion(
                    min_x=region_data.get('minX', 0),
                    min_y=region_data.get('minY', 0),
                    min_z=region_data.get('minZ', 0),
                    max_x=region_data.get('maxX', 0),
                    max_y=region_data.get('maxY', 0),
                    max_z=region_data.get('maxZ', 0)
                )
            
            return CratePileData(
                pile_id=pile_id,
                items=items,
                num_crates=num_crates,
                region=region
            )
            
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    
    def _parse_nbt(self, data: bytes) -> Optional[Dict]:
        """
        Prosty parser NBT (uncompressed lub gzip).
        Dla pełnego parsera użyć zewnętrznej biblioteki nbtlib.
        """
        # Sprawdzamy czy to gzip
        if data[:2] == b'\x1f\x8b':  # Magic number dla gzip
            try:
                data = gzip.decompress(data)
            except Exception:
                pass
        
        # Tutaj użylibyśmy pełnego parsera NBT
        # Na razie zwracamy placeholder - w prawdziwej implementacji
        # użylibyśmy biblioteki nbtlib lub podobnej
        #
        # Struktura oczekiwana:
        # TAG_Compound("data"):
        #   TAG_List("items"): lista ItemStack
        #   TAG_Int("numCrates"): liczba crate'ów
        #   TAG_Compound("region"): region
        
        # Placeholder - zwracamy pusty dict
        # W prawdziwej implementacji parsujemy NBT
        return self._mock_parse_nbt(data)
    
    def _mock_parse_nbt(self, data: bytes) -> Dict:
        """
        Mock dla parsowania NBT - używane w testach.
        W produkcji użyć prawdziwego parsera.
        """
        # TODO: Zastąpić prawdziwym parserem NBT
        return {
            'data': {
                'items': [],
                'numCrates': 1,
                'region': None
            }
        }
    
    def get_pile(self, pile_id: int) -> Optional[CratePileData]:
        """Pobiera dane pojedynczego pile (z cache lub z dysku)"""
        if pile_id in self._pile_cache:
            return self._pile_cache[pile_id]
        
        file_path = self.crates_dir / f"{pile_id}.dat"
        if file_path.exists():
            pile_data = self._read_pile_file(file_path, pile_id)
            if pile_data:
                self._pile_cache[pile_id] = pile_data
            return pile_data
        
        return None
    
    def register_crate_location(self, x: int, y: int, z: int, crate_id: int):
        """
        Rejestruje lokalizację crate'a z TileEntity.
        
        Args:
            x, y, z: Współrzędne bloku
            crate_id: ID z TileEntity (pole crateId)
        """
        pile_data = self.get_pile(crate_id) if crate_id >= 0 else None
        
        location = CrateLocation(
            x=x, y=y, z=z,
            crate_id=crate_id,
            pile_data=pile_data
        )
        
        self._crate_locations[(x, y, z)] = location
    
    def get_crate_at(self, x: int, y: int, z: int) -> Optional[CrateLocation]:
        """Pobiera dane crate'a na danych współrzędnych"""
        return self._crate_locations.get((x, y, z))
    
    def get_all_crate_locations(self) -> List[CrateLocation]:
        """Zwraca wszystkie zarejestrowane lokalizacje crate'ów"""
        return list(self._crate_locations.values())
    
    def get_pile_for_crate(self, x: int, y: int, z: int) -> Optional[CratePileData]:
        """Pobiera dane pile dla crate'a na danych współrzędnych"""
        location = self._crate_locations.get((x, y, z))
        if location:
            return location.pile_data
        return None


class CratePileConverter:
    """
    Konwertuje Crate Pile na osobne skrzynie.
    
    Strategia:
    1. Każdy crate z pile → osobna Vanilla Chest lub Iron Chest
    2. Itemy z pile dzielone proporcjonalnie między crate'y
    3. Jeśli za dużo itemów → wypakować do skrzyń obok
    """
    
    def __init__(self, crate_pile_loader: CratePileLoader):
        self.loader = crate_pile_loader
    
    def convert_crate(self, x: int, y: int, z: int) -> Dict[str, Any]:
        """
        Konwertuje pojedynczy crate na target BlockEntity.
        
        Returns:
            Słownik z:
            - target_block: ID bloku docelowego
            - nbt: dane NBT dla BlockEntity
            - overflow: lista itemów które się nie zmieściły
        """
        location = self.loader.get_crate_at(x, y, z)
        
        if not location or not location.pile_data:
            # Brak danych pile - zwracamy pustą skrzynię
            return {
                'target_block': 'minecraft:chest',
                'nbt': {'Items': []},
                'overflow': []
            }
        
        pile = location.pile_data
        
        # Znajdujemy indeks tego crate'a w pile
        # (po pozycji w regionie lub kolejności rejestracji)
        crate_index = self._get_crate_index_in_pile(location)
        
        # Pobieramy itemy dla tego crate'a
        items = pile.get_items_for_crate(crate_index)
        
        # Konwertujemy itemy do formatu 1.18.2
        converted_items = [self._convert_item(item) for item in items]
        
        # Sprawdzamy czy mieszczą się w vanilla chest (27 slotów)
        # Crate ma 18 slotów, więc zwykle się zmieszczą
        target_block = 'minecraft:chest'
        max_slots = 27
        
        # Jeśli za dużo itemów, używamy Iron Chest
        if len(converted_items) > max_slots:
            target_block = 'ironchest:iron_chest'  # 54 sloty
            max_slots = 54
        
        # Dzielimy na zmieszczone i overflow
        fitting_items = converted_items[:max_slots]
        overflow = converted_items[max_slots:]
        
        return {
            'target_block': target_block,
            'nbt': {'Items': fitting_items},
            'overflow': overflow
        }
    
    def _get_crate_index_in_pile(self, location: CrateLocation) -> int:
        """
        Określa indeks crate'a w pile.
        
        W oryginalnym BS crate'y są uporządkowane po pozycji.
        """
        if not location.pile_data or not location.pile_data.region:
            return 0
        
        region = location.pile_data.region
        
        # Obliczamy indeks na podstawie pozycji w regionie
        # (kolejność: Y, Z, X)
        idx = ((location.y - region.min_y) * 
               (region.max_z - region.min_z + 1) * 
               (region.max_x - region.min_x + 1) +
               (location.z - region.min_z) * 
               (region.max_x - region.min_x + 1) +
               (location.x - region.min_x))
        
        return max(0, idx)
    
    def _convert_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konwertuje ItemStack z formatu 1.7.10 na 1.18.2
        
        1.7.10: {id: "modid:item", Damage: short, Count: byte, Slot: byte, tag: {...}}
        1.18.2: {id: "modid:item", Count: byte, Slot: byte, tag: {...}}
        """
        converted = {
            'id': item.get('id', 'minecraft:air'),
            'Count': item.get('Count', 1),
            'Slot': item.get('Slot', 0)
        }
        
        # Konwertujemy tagi jeśli istnieją
        if 'tag' in item:
            converted['tag'] = self._convert_item_tags(item['tag'])
        
        # Usuwamy Damage (w 1.18.2 jest w tagu)
        if 'Damage' in item and item['Damage'] != 0:
            if 'tag' not in converted:
                converted['tag'] = {}
            converted['tag']['Damage'] = item['Damage']
        
        return converted
    
    def _convert_item_tags(self, tags: Dict) -> Dict:
        """Konwertuje tagi itemu"""
        # Placeholder - pełna konwersja zależy od mapowania itemów
        return tags.copy()
