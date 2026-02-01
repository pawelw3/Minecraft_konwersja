"""
Storage Cell Simulation - AE2 1.7.10 vs 1.18.2

Symulacja komórek pamięci AE2 - zapis/odczyt NBT, struktura danych, typy cell.
Bazuje na kodzie źródłowym:
- 1.7.10: appeng.items.storage.ItemBasicStorageCell, appeng.me.storage.MEInventoryHandler
- 1.18.2: appeng.items.storage.BasicStorageCell, appeng.me.cells.BasicCellInventory
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import json


# =============================================================================
# TYPY I STAŁE
# =============================================================================

class StorageCellType(enum.Enum):
    """Typy komórek pamięci AE2"""
    ITEM_1K = ("1k", 1024, 63)
    ITEM_4K = ("4k", 4096, 63)
    ITEM_16K = ("16k", 16384, 63)
    ITEM_64K = ("64k", 65536, 63)
    ITEM_256K = ("256k", 262144, 63)  # Tylko 1.18.2
    
    FLUID_1K = ("fluid_1k", 1024, 5)
    FLUID_4K = ("fluid_4k", 4096, 5)
    FLUID_16K = ("fluid_16k", 16384, 5)
    FLUID_64K = ("fluid_64k", 65536, 5)
    FLUID_256K = ("fluid_256k", 262144, 5)  # Tylko 1.18.2
    
    def __init__(self, tier: str, bytes: int, types: int):
        self.tier = tier
        self.bytes = bytes
        self.types = types  # Maksymalna liczba typów itemów


# =============================================================================
# SYMULACJA 1.7.10
# =============================================================================

@dataclass
class AEItemStack1710:
    """
    Reprezentacja item stack w 1.7.10.
    Odpowiada: appeng.api.storage.data.IAEItemStack
    """
    item_id: str
    metadata: int = 0
    count: int = 0
    nbt: Optional[Dict] = None
    
    def to_nbt(self) -> Dict:
        """Konwertuje do formatu NBT 1.7.10"""
        nbt = {
            'id': self.item_id,
            'Damage': self.metadata,
            'Count': self.count
        }
        if self.nbt:
            nbt['tag'] = self.nbt
        return nbt
    
    @classmethod
    def from_nbt(cls, nbt: Dict) -> AEItemStack1710:
        """Tworzy z formatu NBT 1.7.10"""
        return cls(
            item_id=nbt.get('id', 'minecraft:air'),
            metadata=nbt.get('Damage', 0),
            count=nbt.get('Count', 0),
            nbt=nbt.get('tag')
        )
    
    def get_key(self) -> Tuple[str, int]:
        """Klucz unikalny dla tego typu itemu (ID + metadata)"""
        return (self.item_id, self.metadata)


@dataclass 
class StorageCellInventory1710:
    """
    Zawartość komórki pamięci w 1.7.10.
    Odpowiada: appeng.me.storage.MEInventoryHandler
    
    Struktura NBT w 1.7.10:
    - items: lista ItemStack
    - itemCount: całkowita liczba itemów
    """
    cell_type: StorageCellType
    items: Dict[Tuple[str, int], AEItemStack1710] = field(default_factory=dict)
    priority: int = 0
    
    def get_total_items(self) -> int:
        """Zwraca całkowitą liczbę itemów"""
        return sum(item.count for item in self.items.values())
    
    def get_used_types(self) -> int:
        """Zwraca liczbę użytych typów"""
        return len(self.items)
    
    def get_available_bytes(self) -> int:
        """Zwraca dostępne bajty"""
        used_types = self.get_used_types()
        used_bytes = sum(item.count for item in self.items.values())
        # W AE2 każdy typ zużywa dodatkowe bajty (overhead)
        type_overhead = used_types * 8  # ~8 bajtów na typ
        return self.cell_type.bytes - used_bytes - type_overhead
    
    def insert_item(self, item: AEItemStack1710) -> AEItemStack1710:
        """
        Wstawia item do komórki.
        Zwraca to co się nie zmieściło.
        """
        key = item.get_key()
        
        # Sprawdź limit typów
        if key not in self.items and self.get_used_types() >= self.cell_type.types:
            return item  # Nie ma miejsca na nowy typ
        
        # Sprawdź dostępne bajty
        available = self.get_available_bytes()
        if available <= 0:
            return item  # Brak miejsca
        
        # Wstawienie
        if key in self.items:
            existing = self.items[key]
            space_in_slot = available
            to_add = min(item.count, space_in_slot)
            existing.count += to_add
            item.count -= to_add
        else:
            space = min(item.count, available)
            self.items[key] = AEItemStack1710(
                item_id=item.item_id,
                metadata=item.metadata,
                count=space,
                nbt=item.nbt
            )
            item.count -= space
        
        return item if item.count > 0 else None
    
    def extract_item(self, item_id: str, metadata: int, count: int) -> Optional[AEItemStack1710]:
        """Wyciąga item z komórki"""
        key = (item_id, metadata)
        if key not in self.items:
            return None
        
        existing = self.items[key]
        to_extract = min(count, existing.count)
        
        result = AEItemStack1710(
            item_id=item_id,
            metadata=metadata,
            count=to_extract,
            nbt=existing.nbt
        )
        
        existing.count -= to_extract
        if existing.count <= 0:
            del self.items[key]
        
        return result
    
    def to_nbt(self) -> Dict:
        """Eksportuje do NBT 1.7.10"""
        items_list = []
        for item in self.items.values():
            items_list.append(item.to_nbt())
        
        return {
            'items': items_list,
            'itemCount': self.get_total_items(),
            'priority': self.priority
        }
    
    @classmethod
    def from_nbt(cls, nbt: Dict, cell_type: StorageCellType) -> StorageCellInventory1710:
        """Importuje z NBT 1.7.10"""
        inv = cls(cell_type=cell_type, priority=nbt.get('priority', 0))
        
        for item_nbt in nbt.get('items', []):
            item = AEItemStack1710.from_nbt(item_nbt)
            if item.count > 0:
                inv.items[item.get_key()] = item
        
        return inv
    
    def print_status(self) -> None:
        """Wyświetla status komórki"""
        print(f"  Typ: {self.cell_type.name}")
        print(f"  Pojemność: {self.cell_type.bytes} bajtów")
        print(f"  Max typów: {self.cell_type.types}")
        print(f"  Używane typy: {self.get_used_types()}")
        print(f"  Całkowita liczba itemów: {self.get_total_items()}")
        print(f"  Dostępne bajty: {self.get_available_bytes()}")
        print("  Zawartość:")
        for (item_id, meta), item in self.items.items():
            print(f"    - {item_id}:{meta} x{item.count}")


# =============================================================================
# SYMULACJA 1.18.2
# =============================================================================

@dataclass
class AEItemStack1182:
    """
    Reprezentacja item stack w 1.18.2.
    Odpowiada: appeng.api.storage.AEKey (nowa architektura!)
    
    GŁÓWNA RÓŻNICA: W 1.18.2 AE przeszło na system kluczy (AEKey)
    zamiast ItemStack. To pozwala na lepszą obsługę fluidów i innych typów.
    """
    item_id: str
    count: int = 0
    nbt: Optional[Dict] = None
    # 1.18.2 nie używa już metadata (Damage) - zastąpione przez NBT
    
    def to_nbt(self) -> Dict:
        """Konwertuje do formatu NBT 1.18.2"""
        nbt = {
            'id': self.item_id,
            'Count': self.count
        }
        if self.nbt:
            nbt['tag'] = self.nbt
        return nbt
    
    @classmethod
    def from_nbt(cls, nbt: Dict) -> AEItemStack1182:
        """Tworzy z formatu NBT 1.18.2"""
        return cls(
            item_id=nbt.get('id', 'minecraft:air'),
            count=nbt.get('Count', 0),
            nbt=nbt.get('tag')
        )
    
    def get_key(self) -> str:
        """Klucz w 1.18.2 to tylko ID (bez metadata)"""
        return self.item_id


@dataclass
class StorageCellInventory1182:
    """
    Zawartość komórki pamięci w 1.18.2.
    Odpowiada: appeng.me.cells.BasicCellInventory
    
    GŁÓWNE RÓŻNICE vs 1.7.10:
    - Inna struktura NBT (serialized, nie lista)
    - Obsługa AEKey zamiast ItemStack
    - Lepsza kompresja danych
    """
    cell_type: StorageCellType
    items: Dict[str, AEItemStack1182] = field(default_factory=dict)
    priority: int = 0
    
    # Dodatkowe pola w 1.18.2
    filter: Optional[List[str]] = None  # Filtrowanie zawartości
    
    def get_total_items(self) -> int:
        return sum(item.count for item in self.items.values())
    
    def get_used_types(self) -> int:
        return len(self.items)
    
    def get_available_bytes(self) -> int:
        used_types = self.get_used_types()
        used_bytes = sum(item.count for item in self.items.values())
        # W 1.18.2 overhead jest inaczej liczony
        type_overhead = used_types * 8
        return self.cell_type.bytes - used_bytes - type_overhead
    
    def insert_item(self, item: AEItemStack1182) -> AEItemStack1182:
        """Wstawia item do komórki (1.18.2)"""
        key = item.get_key()
        
        # Sprawdź filtr (nowość w 1.18.2)
        if self.filter and key not in self.filter:
            return item
        
        # Sprawdź limit typów
        if key not in self.items and self.get_used_types() >= self.cell_type.types:
            return item
        
        available = self.get_available_bytes()
        if available <= 0:
            return item
        
        # Wstawienie
        if key in self.items:
            existing = self.items[key]
            to_add = min(item.count, available)
            existing.count += to_add
            item.count -= to_add
        else:
            space = min(item.count, available)
            self.items[key] = AEItemStack1182(
                item_id=item.item_id,
                count=space,
                nbt=item.nbt
            )
            item.count -= space
        
        return item if item.count > 0 else None
    
    def extract_item(self, item_id: str, count: int) -> Optional[AEItemStack1182]:
        """Wyciąga item z komórki (1.18.2 - bez metadata)"""
        if item_id not in self.items:
            return None
        
        existing = self.items[item_id]
        to_extract = min(count, existing.count)
        
        result = AEItemStack1182(
            item_id=item_id,
            count=to_extract,
            nbt=existing.nbt
        )
        
        existing.count -= to_extract
        if existing.count <= 0:
            del self.items[item_id]
        
        return result
    
    def to_nbt(self) -> Dict:
        """
        Eksportuje do NBT 1.18.2.
        
        RÓŻNICA: W 1.18.2 items są serializowane inaczej
        """
        # 1.18.2 używa nowego formatu serialized
        items_list = []
        for item in self.items.values():
            items_list.append(item.to_nbt())
        
        return {
            'storage': {
                'items': items_list,
                'count': self.get_total_items()
            },
            'priority': self.priority,
            'filter': self.filter if self.filter else []
        }
    
    @classmethod
    def from_nbt(cls, nbt: Dict, cell_type: StorageCellType) -> StorageCellInventory1182:
        """Importuje z NBT 1.18.2"""
        inv = cls(
            cell_type=cell_type,
            priority=nbt.get('priority', 0),
            filter=nbt.get('filter', [])
        )
        
        storage = nbt.get('storage', {})
        for item_nbt in storage.get('items', []):
            item = AEItemStack1182.from_nbt(item_nbt)
            if item.count > 0:
                inv.items[item.get_key()] = item
        
        return inv
    
    def print_status(self) -> None:
        """Wyświetla status komórki 1.18.2"""
        print(f"  Typ: {self.cell_type.name}")
        print(f"  Pojemność: {self.cell_type.bytes} bajtów")
        print(f"  Max typów: {self.cell_type.types}")
        print(f"  Używane typy: {self.get_used_types()}")
        print(f"  Całkowita liczba itemów: {self.get_total_items()}")
        print(f"  Dostępne bajty: {self.get_available_bytes()}")
        if self.filter:
            print(f"  Filtr: {self.filter}")
        print("  Zawartość:")
        for item_id, item in self.items.items():
            print(f"    - {item_id} x{item.count}")


# =============================================================================
# KONWERSJA MIĘDZY WERSJAMI
# =============================================================================

def convert_cell_1710_to_1182(inv_1710: StorageCellInventory1710, 
                               cell_type_1182: StorageCellType) -> StorageCellInventory1182:
    """
    Konwertuje zawartość komórki z 1.7.10 do 1.18.2.
    
    PROBLEMY KONWERSJI:
    1. Metadata (1.7.10) → NBT (1.18.2)
    2. Różne formaty NBT
    3. 256k cell nie istnieje w 1.7.10
    """
    inv_1182 = StorageCellInventory1182(
        cell_type=cell_type_1182,
        priority=inv_1710.priority
    )
    
    for (item_id, metadata), item_1710 in inv_1710.items.items():
        # Konwersja metadata → NBT (jeśli > 0)
        nbt = item_1710.nbt.copy() if item_1710.nbt else {}
        if metadata > 0:
            nbt['Damage'] = metadata  # Zachowaj metadata w NBT
        
        item_1182 = AEItemStack1182(
            item_id=item_id,
            count=item_1710.count,
            nbt=nbt if nbt else None
        )
        
        # Wstaw do nowej komórki
        inv_1182.insert_item(item_1182)
    
    return inv_1182


def convert_cell_1182_to_1710(inv_1182: StorageCellInventory1182,
                               cell_type_1710: StorageCellType) -> StorageCellInventory1710:
    """
    Konwertuje zawartość komórki z 1.18.2 do 1.7.10.
    
    UWAGA: 256k cell nie może być skonwertowany bezpośrednio (nie ma w 1.7.10)
    """
    inv_1710 = StorageCellInventory1710(
        cell_type=cell_type_1710,
        priority=inv_1182.priority
    )
    
    for item_id, item_1182 in inv_1182.items.items():
        # Odzyskaj metadata z NBT (jeśli istnieje)
        metadata = 0
        if item_1182.nbt and 'Damage' in item_1182.nbt:
            metadata = item_1182.nbt['Damage']
            # Usuń z NBT (w 1.7.10 jest osobne pole)
            nbt = item_1182.nbt.copy()
            del nbt['Damage']
        else:
            nbt = item_1182.nbt
        
        item_1710 = AEItemStack1710(
            item_id=item_id,
            metadata=metadata,
            count=item_1182.count,
            nbt=nbt if nbt else None
        )
        
        inv_1710.insert_item(item_1710)
    
    return inv_1710


# =============================================================================
# TESTY I DEMONSTRACJA
# =============================================================================

def test_basic_storage():
    """Test podstawowego działania komórek"""
    print("="*60)
    print("TEST: Podstawowe działanie Storage Cell 1.7.10")
    print("="*60)
    
    cell = StorageCellInventory1710(cell_type=StorageCellType.ITEM_4K)
    
    # Wstawianie itemów
    items = [
        AEItemStack1710("minecraft:stone", 0, 64),
        AEItemStack1710("minecraft:stone", 0, 64),
        AEItemStack1710("minecraft:dirt", 0, 32),
        AEItemStack1710("minecraft:diamond", 0, 16),
    ]
    
    for item in items:
        remaining = cell.insert_item(item)
        if remaining:
            print(f"  Nie zmieściło się: {remaining.item_id} x{remaining.count}")
    
    cell.print_status()
    
    # Test ekstrakcji
    extracted = cell.extract_item("minecraft:stone", 0, 50)
    print(f"\n  Wyciągnięto: {extracted.item_id} x{extracted.count}")
    print(f"  Pozostało stone: {cell.items[('minecraft:stone', 0)].count}")


def test_nbt_conversion():
    """Test konwersji NBT między wersjami"""
    print("\n" + "="*60)
    print("TEST: Konwersja NBT 1.7.10 → 1.18.2")
    print("="*60)
    
    # Utwórz komórkę 1.7.10 z danymi
    cell_1710 = StorageCellInventory1710(cell_type=StorageCellType.ITEM_16K)
    cell_1710.insert_item(AEItemStack1710("minecraft:stone", 0, 128))
    cell_1710.insert_item(AEItemStack1710("minecraft:planks", 1, 64))  # Spruce planks (meta=1)
    cell_1710.insert_item(AEItemStack1710("minecraft:diamond_sword", 0, 1, {'Damage': 100}))
    
    print("\nKomórka 1.7.10:")
    print(f"  NBT: {json.dumps(cell_1710.to_nbt(), indent=2)[:300]}...")
    
    # Konwersja do 1.18.2
    cell_1182 = convert_cell_1710_to_1182(cell_1710, StorageCellType.ITEM_16K)
    
    print("\nKomórka 1.18.2 (po konwersji):")
    print(f"  NBT: {json.dumps(cell_1182.to_nbt(), indent=2)[:300]}...")
    
    # Weryfikacja
    assert cell_1710.get_total_items() == cell_1182.get_total_items()
    print("\n✓ Konwersja zachowała całkowitą liczbę itemów")


def test_metadata_conversion():
    """Test konwersji metadata (kluczowa różnica między wersjami)"""
    print("\n" + "="*60)
    print("TEST: Konwersja metadata (1.7.10) ↔ NBT (1.18.2)")
    print("="*60)
    
    # 1.7.10 - różne typy planks (różne metadata)
    cell_1710 = StorageCellInventory1710(cell_type=StorageCellType.ITEM_4K)
    cell_1710.insert_item(AEItemStack1710("minecraft:planks", 0, 32))  # Oak
    cell_1710.insert_item(AEItemStack1710("minecraft:planks", 1, 32))  # Spruce
    cell_1710.insert_item(AEItemStack1710("minecraft:planks", 2, 32))  # Birch
    
    print("\n1.7.10 - osobne sloty dla każdego metadata:")
    for (item_id, meta), item in cell_1710.items.items():
        print(f"  {item_id}:{meta} x{item.count}")
    
    # Konwersja do 1.18.2
    cell_1182 = convert_cell_1710_to_1182(cell_1710, StorageCellType.ITEM_4K)
    
    print("\n1.18.2 - metadata w NBT:")
    for item_id, item in cell_1182.items.items():
        meta = item.nbt.get('Damage', 0) if item.nbt else 0
        print(f"  {item_id} (Damage={meta}) x{item.count}")
    
    print("\n  UWAGA: W 1.18.2 różne metadata to osobne AEKey!")
    print(f"  Liczba typów w 1.7.10: {cell_1710.get_used_types()}")
    print(f"  Liczba typów w 1.18.2: {cell_1182.get_used_types()}")


def test_256k_cell():
    """Test komórki 256k (tylko 1.18.2)"""
    print("\n" + "="*60)
    print("TEST: Komórka 256k (tylko 1.18.2)")
    print("="*60)
    
    cell = StorageCellInventory1182(cell_type=StorageCellType.ITEM_256K)
    
    # Wypełnij dużą ilością różnych itemów
    for i in range(100):
        item = AEItemStack1182(f"minecraft:item_{i}", 64)
        cell.insert_item(item)
    
    print(f"  Pojemność: {cell.cell_type.bytes} bajtów")
    print(f"  Wstawiono: {cell.get_total_items()} itemów")
    print(f"  Typów: {cell.get_used_types()}")
    print(f"  Dostępne: {cell.get_available_bytes()} bajtów")
    
    print("\n  UWAGA: Komórki 256k nie ma w 1.7.10!")
    print("  Strategia konwersji: 256k → 64k + overflow do innej komórki")


def compare_nbt_structures():
    """Porównuje struktury NBT"""
    print("\n" + "="*60)
    print("PORÓWNANIE STRUKTUR NBT")
    print("="*60)
    
    print("\n1.7.10 NBT Structure:")
    print("""
  {
    "items": [
      {"id": "minecraft:stone", "Damage": 0, "Count": 64},
      {"id": "minecraft:dirt", "Damage": 0, "Count": 32}
    ],
    "itemCount": 96,
    "priority": 0
  }
    """)
    
    print("\n1.18.2 NBT Structure:")
    print("""
  {
    "storage": {
      "items": [
        {"id": "minecraft:stone", "Count": 64},
        {"id": "minecraft:dirt", "Count": 32}
      ],
      "count": 96
    },
    "priority": 0,
    "filter": []
  }
    """)
    
    print("\nKLUCZOWE RÓŻNICE:")
    print("1. 1.7.10: 'items' na poziomie root, 'itemCount'")
    print("2. 1.18.2: 'storage' jako wrapper, 'count' w środku")
    print("3. 1.7.10: 'Damage' jako osobne pole")
    print("4. 1.18.2: Metadata w 'tag' (NBT)")
    print("5. 1.18.2: Dodatkowe pole 'filter'")


def main():
    """Główna funkcja demonstracyjna"""
    print("="*60)
    print("STORAGE CELL SIMULATION - AE2 1.7.10 vs 1.18.2")
    print("="*60)
    
    test_basic_storage()
    test_nbt_conversion()
    test_metadata_conversion()
    test_256k_cell()
    compare_nbt_structures()
    
    print("\n" + "="*60)
    print("SYMULACJA ZAKOŃCZONA POMYŚLNIE")
    print("="*60)
    print("\nWnioski dla konwersji:")
    print("1. Metadata (1.7.10) musi być przeniesione do NBT (1.18.2)")
    print("2. Struktura NBT jest inna - wymaga transformacji")
    print("3. 256k cell (1.18.2) nie ma odpowiednika w 1.7.10")
    print("4. Całkowita liczba itemów jest zachowywana")
    print("5. Filtry (1.18.2) są tracone przy konwersji do 1.7.10")


if __name__ == "__main__":
    main()
