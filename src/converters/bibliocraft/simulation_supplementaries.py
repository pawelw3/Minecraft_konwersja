"""
Symulacja systemu Supplementaries (1.18.2) - Konwersja z BiblioCraft (1.7.10)

Ta symulacja pokazuje:
1. Jak Supplementaries przechowuje inventory w BlockEntities
2. Konwersja: Bookcase -> Book Pile, Shelf -> Item Shelf
3. Obsługa NBT dla różnych typów storage
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json


@dataclass
class ItemStack:
    """Reprezentacja ItemStack z Minecraft"""
    item_id: str
    count: int = 1
    nbt: Dict = field(default_factory=dict)
    
    def to_nbt(self) -> Dict:
        result = {
            "id": self.item_id,
            "Count": self.count
        }
        if self.nbt:
            result["tag"] = self.nbt
        return result
    
    @classmethod
    def from_nbt(cls, nbt: Dict) -> "ItemStack":
        return cls(
            item_id=nbt.get("id", ""),
            count=nbt.get("Count", 1),
            nbt=nbt.get("tag", {})
        )
    
    def is_empty(self) -> bool:
        return self.item_id == "" or self.count <= 0
    
    def __str__(self) -> str:
        return f"{self.item_id} x{self.count}"


class ContainerHelper:
    """
    Symulacja ContainerHelper z Minecraft 1.18.2
    
    Używany do zapisu/odczytu inventory w BlockEntities
    """
    
    @staticmethod
    def save_all_items(nbt: Dict, items: List[ItemStack], tag_name: str = "Items") -> Dict:
        """Zapisuje wszystkie itemy do NBT"""
        items_list = []
        for slot, item in enumerate(items):
            if not item.is_empty():
                item_nbt = item.to_nbt()
                item_nbt["Slot"] = slot
                items_list.append(item_nbt)
        nbt[tag_name] = items_list
        return nbt
    
    @staticmethod
    def load_all_items(nbt: Dict, container_size: int, tag_name: str = "Items") -> List[ItemStack]:
        """Wczytuje wszystkie itemy z NBT"""
        items = [ItemStack("") for _ in range(container_size)]
        
        for item_nbt in nbt.get(tag_name, []):
            slot = item_nbt.get("Slot", 0)
            if 0 <= slot < container_size:
                items[slot] = ItemStack.from_nbt(item_nbt)
        
        return items


@dataclass
class BookPileBlockEntity:
    """
    Symulacja BookPileBlockTile z Supplementaries
    
    Przechowuje 4 książki w stosie (pionowo lub poziomo)
    """
    pos: Tuple[int, int, int]
    items: List[ItemStack] = field(default_factory=list)
    horizontal: bool = False  # czy stos jest poziomy
    
    # Sloty: 0-3 (max 4 książki)
    MAX_SLOTS = 4
    
    def __post_init__(self):
        if not self.items:
            self.items = [ItemStack("") for _ in range(self.MAX_SLOTS)]
    
    def add_book(self, book: ItemStack) -> bool:
        """Dodaje książkę do stosu"""
        for i, slot in enumerate(self.items):
            if slot.is_empty():
                self.items[i] = book
                print(f"  [BookPile] Dodano książkę na slot {i}: {book}")
                return True
        print(f"  [BookPile] Stos pełny!")
        return False
    
    def to_nbt(self) -> Dict:
        """Serializacja do NBT (1.18.2 format)"""
        nbt = {
            "horizontal": self.horizontal
        }
        ContainerHelper.save_all_items(nbt, self.items)
        return nbt
    
    @classmethod
    def from_nbt(cls, nbt: Dict, pos: Tuple[int, int, int]) -> "BookPileBlockEntity":
        """Deserializacja z NBT"""
        be = cls(
            pos=pos,
            horizontal=nbt.get("horizontal", False)
        )
        be.items = ContainerHelper.load_all_items(nbt, cls.MAX_SLOTS)
        return be
    
    def get_book_count(self) -> int:
        """Zwraca liczbę książek w stosie"""
        return sum(1 for item in self.items if not item.is_empty())
    
    def __str__(self) -> str:
        count = self.get_book_count()
        orient = "poziomy" if self.horizontal else "pionowy"
        return f"BookPileBlockEntity({count} książek, {orient})"


@dataclass
class ItemShelfBlockEntity:
    """
    Symulacja ItemShelfBlockTile z Supplementaries
    
    Półka na 3-4 przedmioty (wyświetlane na ścianie)
    """
    pos: Tuple[int, int, int]
    items: List[ItemStack] = field(default_factory=list)
    
    MAX_SLOTS = 4
    
    def __post_init__(self):
        if not self.items:
            self.items = [ItemStack("") for _ in range(self.MAX_SLOTS)]
    
    def set_item(self, slot: int, item: ItemStack) -> bool:
        """Ustawia przedmiot w danym slocie"""
        if 0 <= slot < self.MAX_SLOTS:
            self.items[slot] = item
            print(f"  [ItemShelf] Ustawiono slot {slot}: {item}")
            return True
        return False
    
    def to_nbt(self) -> Dict:
        """Serializacja do NBT"""
        nbt = {}
        ContainerHelper.save_all_items(nbt, self.items)
        return nbt
    
    @classmethod
    def from_nbt(cls, nbt: Dict, pos: Tuple[int, int, int]) -> "ItemShelfBlockEntity":
        """Deserializacja z NBT"""
        be = cls(pos=pos)
        be.items = ContainerHelper.load_all_items(nbt, cls.MAX_SLOTS)
        return be
    
    def __str__(self) -> str:
        count = sum(1 for item in self.items if not item.is_empty())
        return f"ItemShelfBlockEntity({count}/{self.MAX_SLOTS} slotów zajętych)"


@dataclass
class JarBlockEntity:
    """
    Symulacja JarBlockTile z Supplementaries
    
    Słoik na dowolne przedmioty (różni się od BC Cookie Jar)
    """
    pos: Tuple[int, int, int]
    items: List[ItemStack] = field(default_factory=list)
    
    MAX_SLOTS = 4  # Różne słoiki mają różną pojemność
    
    def __post_init__(self):
        if not self.items:
            self.items = [ItemStack("") for _ in range(self.MAX_SLOTS)]
    
    def to_nbt(self) -> Dict:
        nbt = {}
        ContainerHelper.save_all_items(nbt, self.items)
        return nbt
    
    @classmethod
    def from_nbt(cls, nbt: Dict, pos: Tuple[int, int, int]) -> "JarBlockEntity":
        be = cls(pos=pos)
        be.items = ContainerHelper.load_all_items(nbt, cls.MAX_SLOTS)
        return be


# Konwersja z BC na Supplementaries

@dataclass
class BCBookcaseTE:
    """Symulacja TileEntityBookcase z BC 1.7.10"""
    items: List[ItemStack] = field(default_factory=list)  # 16 slotów
    book_count: int = 0
    
    MAX_SLOTS = 16
    
    def __post_init__(self):
        if not self.items:
            self.items = [ItemStack("") for _ in range(self.MAX_SLOTS)]
    
    def to_nbt(self) -> Dict:
        """NBT format z BC 1.7.10"""
        return {
            "Items": [item.to_nbt() for item in self.items],
            "bookCount": self.book_count
        }
    
    @classmethod
    def from_nbt(cls, nbt: Dict) -> "BCBookcaseTE":
        te = cls()
        items_nbt = nbt.get("Items", [])
        te.items = [ItemStack.from_nbt(item_nbt) if i < len(items_nbt) else ItemStack("") 
                    for i in range(cls.MAX_SLOTS)]
        te.book_count = nbt.get("bookCount", 0)
        return te


@dataclass
class BCShelfTE:
    """Symulacja TileEntityGenericShelf z BC 1.7.10"""
    items: List[ItemStack] = field(default_factory=list)  # 4 sloty
    
    MAX_SLOTS = 4
    
    def __post_init__(self):
        if not self.items:
            self.items = [ItemStack("") for _ in range(self.MAX_SLOTS)]
    
    def to_nbt(self) -> Dict:
        return {
            "Items": [item.to_nbt() for item in self.items]
        }
    
    @classmethod
    def from_nbt(cls, nbt: Dict) -> "BCShelfTE":
        te = cls()
        items_nbt = nbt.get("Items", [])
        te.items = [ItemStack.from_nbt(item_nbt) if i < len(items_nbt) else ItemStack("") 
                    for i in range(te.MAX_SLOTS)]
        return te


class SupplementariesConverter:
    """Konwerter z BC na Supplementaries"""
    
    def convert_bookcase_to_pile(self, bc_bookcase: BCBookcaseTE,
                                  pos: Tuple[int, int, int]) -> BookPileBlockEntity:
        """
        Konwertuje Bookcase (16 slotów) na Book Pile (4 sloty)
        
        Uwaga: Tylko pierwsze 4 książki zostaną przeniesione!
        Reszta zostanie utracona lub przeniesiona do innego storage
        """
        print(f"\n[Konwersja BC Bookcase -> Supplementaries Book Pile]")
        print(f"  BC Bookcase: {bc_bookcase.book_count} książek (max 16)")
        
        pile = BookPileBlockEntity(pos=pos, horizontal=False)
        
        # Przenieś pierwsze 4 książki
        transferred = 0
        for i, book in enumerate(bc_bookcase.items[:16]):
            if not book.is_empty() and transferred < 4:
                # W BC książki mogą być w dowolnych slotach, w Supplementaries upychamy
                pile.items[transferred] = book
                print(f"    Przeniesiono: {book} (z slotu BC {i})")
                transferred += 1
        
        # Uwaga: pozostałe książki (jeśli > 4) wymagają dodatkowych Book Pile
        # lub innego storage (np. vanilla chest)
        remaining = bc_bookcase.book_count - transferred
        if remaining > 0:
            print(f"  UWAGA: {remaining} książek nie zmieściło się! Wymaga dodatkowego storage.")
        
        print(f"  -> Book Pile: {pile.get_book_count()}/4 książek")
        return pile
    
    def convert_shelf_to_item_shelf(self, bc_shelf: BCShelfTE,
                                     pos: Tuple[int, int, int]) -> ItemShelfBlockEntity:
        """
        Konwertuje Shelf (4 sloty) na Item Shelf (4 sloty)
        
        To jest prawie 1:1 konwersja - obie mają 4 sloty
        """
        print(f"\n[Konwersja BC Shelf -> Supplementaries Item Shelf]")
        print(f"  BC Shelf: 4 sloty")
        
        shelf = ItemShelfBlockEntity(pos=pos)
        
        # Bezpośrednie kopiowanie
        for i in range(4):
            shelf.items[i] = bc_shelf.items[i] if i < len(bc_shelf.items) else ItemStack("")
            if not shelf.items[i].is_empty():
                print(f"    Przeniesiono slot {i}: {shelf.items[i]}")
        
        print(f"  -> Item Shelf: {shelf}")
        return shelf
    
    def convert_cookie_jar(self, bc_items: List[ItemStack],
                           pos: Tuple[int, int, int]) -> JarBlockEntity:
        """
        Konwertuje Cookie Jar (tylko ciastka) na Jar (dowolne przedmioty)
        
        BC Cookie Jar mógł zawierać tylko ciastka
        Supplementaries Jar może zawierać dowolne przedmioty
        """
        print(f"\n[Konwersja BC Cookie Jar -> Supplementaries Jar]")
        
        jar = JarBlockEntity(pos=pos)
        
        # Przenieś ciastka (lub inne przedmioty)
        for i, item in enumerate(bc_items[:4]):
            if not item.is_empty():
                jar.items[i] = item
                print(f"    Przeniesiono: {item}")
        
        print(f"  -> Jar: {sum(1 for i in jar.items if not i.is_empty())}/4 slotów")
        return jar


def run_simulation():
    """Uruchamia symulację konwersji"""
    print("=" * 60)
    print("SYMULACJA: BiblioCraft -> Supplementaries (1.18.2)")
    print("=" * 60)
    
    converter = SupplementariesConverter()
    
    # Scenariusz 1: Konwersja Bookcase (pełna)
    print("\n--- Scenariusz 1: Bookcase (16 książek) -> Book Pile ---")
    bc_bookcase = BCBookcaseTE()
    # Dodaj książki
    for i in range(10):
        bc_bookcase.items[i] = ItemStack(f"minecraft:book_{i}", 1)
    bc_bookcase.book_count = 10
    
    pile = converter.convert_bookcase_to_pile(bc_bookcase, (100, 64, 200))
    print(f"  NBT Book Pile: {json.dumps(pile.to_nbt(), indent=2)}")
    
    # Scenariusz 2: Konwersja Shelf
    print("\n--- Scenariusz 2: Shelf (4 sloty) -> Item Shelf ---")
    bc_shelf = BCShelfTE()
    bc_shelf.items[0] = ItemStack("minecraft:diamond_sword", 1)
    bc_shelf.items[1] = ItemStack("minecraft:apple", 16)
    bc_shelf.items[3] = ItemStack("minecraft:book", 3)
    
    item_shelf = converter.convert_shelf_to_item_shelf(bc_shelf, (101, 64, 200))
    print(f"  NBT Item Shelf: {json.dumps(item_shelf.to_nbt(), indent=2)}")
    
    # Scenariusz 3: Konwersja Cookie Jar
    print("\n--- Scenariusz 3: Cookie Jar -> Jar ---")
    bc_cookies = [ItemStack("minecraft:cookie", 8) for _ in range(3)]
    
    jar = converter.convert_cookie_jar(bc_cookies, (102, 64, 200))
    print(f"  NBT Jar: {json.dumps(jar.to_nbt(), indent=2)}")
    
    # Scenariusz 4: Round-trip NBT
    print("\n--- Scenariusz 4: Test round-trip NBT ---")
    nbt_data = pile.to_nbt()
    restored = BookPileBlockEntity.from_nbt(nbt_data, pile.pos)
    print(f"  Oryginał: {pile}")
    print(f"  Przywrócony: {restored}")
    print(f"  Zgodność książek: {pile.get_book_count() == restored.get_book_count()}")
    
    # Scenariusz 5: Przeniesienie enchantowanej książki
    print("\n--- Scenariusz 5: Enchanted Book ---")
    enchanted_book = ItemStack(
        "minecraft:enchanted_book",
        1,
        {"StoredEnchantments": [{"id": "minecraft:mending", "lvl": 1}]}
    )
    bc_bookcase_ench = BCBookcaseTE()
    bc_bookcase_ench.items[0] = enchanted_book
    bc_bookcase_ench.book_count = 1
    
    pile_ench = converter.convert_bookcase_to_pile(bc_bookcase_ench, (103, 64, 200))
    print(f"  Przeniesiono: {pile_ench.items[0]}")
    print(f"  NBT: {json.dumps(pile_ench.to_nbt(), indent=2)}")
    
    print("\n" + "=" * 60)
    print("Symulacja zakończona pomyślnie!")
    print("=" * 60)


if __name__ == "__main__":
    run_simulation()
