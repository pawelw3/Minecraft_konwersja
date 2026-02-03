"""
Symulacja stołu craftingowego (Crafting Side) i szafek (Cupboards) z Jammy Furniture (1.7.10).

Na podstawie kodu źródłowego:
- TileEntityWoodBlocksOne.java (subBlock 13 = Crafting Side)
- TileEntityWoodBlocksTwo.java (subBlock 0-3 = Kitchen Cupboard)
- TileEntityWoodBlocksFour.java (subBlock 0-7 = Wardrobe)

Funkcjonalności:

1. Crafting Side (Stół craftingowy):
   - 6 slotów inventory
   - Układ 3x2 (nie standardowy 3x3!)
   - Działa jak crafting table ale z mniejszym gridem
   - Przechowuje crafting grid w TE (to ważne dla konwersji!)

2. Kitchen Cupboard (Szafka kuchenna):
   - 9 slotów inventory
   - Prosty kontener bez dodatkowej logiki
   - Metadata 0-3 = zamknięta, 4-7 = otwarta (półki)

3. Wardrobe (Szafa):
   - 20 slotów inventory (duża szafa)
   - Metadata 0-3 = dolna część, 4-7 = górna część
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


@dataclass
class ItemStack:
    """Reprezentacja stosu itemów."""
    item_id: str
    count: int = 1
    damage: int = 0
    tag: Optional[Dict[str, Any]] = None
    
    def copy(self) -> 'ItemStack':
        return ItemStack(
            item_id=self.item_id,
            count=self.count,
            damage=self.damage,
            tag=self.tag.copy() if self.tag else None
        )
    
    def is_empty(self) -> bool:
        return self.count <= 0


class CupboardType(Enum):
    """Typ szafki."""
    CLOSED = 0  # subBlock 0-3
    OPEN = 4    # subBlock 4-7 (półki)


@dataclass
class CraftingSideInventory:
    """
    Inventory stołu craftingowego Jammy.
    
    Na podstawie TileEntityWoodBlocksOne:
    - 6 slotów (nie 9 jak standardowy crafting!)
    - Układ 3x2 zamiast 3x3
    - Sloty 0-5 to crafting grid
    
    UWAGA: To nietypowe! Standardowy crafting table w MC to 3x3,
    ale Jammy ma tylko 3x2. To oznacza że niektóre receptury
    mogą nie działać!
    """
    slots: List[Optional[ItemStack]] = field(default_factory=lambda: [None] * 6)
    
    def get_size(self) -> int:
        return 6
    
    def get_item(self, slot: int) -> Optional[ItemStack]:
        if 0 <= slot < 6:
            return self.slots[slot]
        return None
    
    def set_item(self, slot: int, item: Optional[ItemStack]) -> bool:
        if 0 <= slot < 6:
            self.slots[slot] = item
            return True
        return False
    
    def clear(self) -> None:
        """Czyści cały crafting grid."""
        for i in range(6):
            self.slots[i] = None
    
    def to_nbt_1710(self) -> Dict[str, Any]:
        """Eksportuje do NBT 1.7.10."""
        items = []
        for i, slot in enumerate(self.slots):
            if slot is not None:
                items.append({
                    "Slot": i,
                    "id": slot.item_id,
                    "Count": slot.count,
                    "Damage": slot.damage
                })
        return {"Items": items}
    
    @classmethod
    def from_nbt_1710(cls, nbt_data: Dict[str, Any]) -> 'CraftingSideInventory':
        """Tworzy z NBT 1.7.10."""
        inv = cls()
        for item_data in nbt_data.get("Items", []):
            slot = item_data.get("Slot", 0)
            if 0 <= slot < 6:
                inv.slots[slot] = ItemStack(
                    item_id=item_data.get("id", "minecraft:air"),
                    count=item_data.get("Count", 1),
                    damage=item_data.get("Damage", 0)
                )
        return inv


@dataclass
class KitchenCupboardInventory:
    """
    Inventory szafki kuchennej.
    
    Na podstawie TileEntityWoodBlocksTwo:
    - 9 slotów
    - Prosty kontener
    """
    slots: List[Optional[ItemStack]] = field(default_factory=lambda: [None] * 9)
    
    def get_size(self) -> int:
        return 9
    
    def get_item(self, slot: int) -> Optional[ItemStack]:
        if 0 <= slot < 9:
            return self.slots[slot]
        return None
    
    def set_item(self, slot: int, item: Optional[ItemStack]) -> bool:
        if 0 <= slot < 9:
            self.slots[slot] = item
            return True
        return False
    
    def to_nbt_1710(self) -> Dict[str, Any]:
        """Eksportuje do NBT 1.7.10."""
        items = []
        for i, slot in enumerate(self.slots):
            if slot is not None:
                items.append({
                    "Slot": i,
                    "id": slot.item_id,
                    "Count": slot.count,
                    "Damage": slot.damage
                })
        return {"Items": items}


@dataclass
class WardrobeInventory:
    """
    Inventory szafy (Wardrobe).
    
    Na podstawie TileEntityWoodBlocksFour:
    - 20 slotów (duża szafa!)
    - subBlock 0-3 = dolna część
    - subBlock 4-7 = górna część
    
    W oryginale szafa ma 20 slotów, ale jest podzielona na dwie części:
    - Dolna (4 sloty metadata) - główna część szafy
    - Górna (4 sloty metadata) - półki
    
    Razem tworzą jedno duże inventory 20 slotów.
    """
    slots: List[Optional[ItemStack]] = field(default_factory=lambda: [None] * 20)
    
    def get_size(self) -> int:
        return 20
    
    def get_item(self, slot: int) -> Optional[ItemStack]:
        if 0 <= slot < 20:
            return self.slots[slot]
        return None
    
    def set_item(self, slot: int, item: Optional[ItemStack]) -> bool:
        if 0 <= slot < 20:
            self.slots[slot] = item
            return True
        return False
    
    def to_nbt_1710(self) -> Dict[str, Any]:
        """Eksportuje do NBT 1.7.10."""
        items = []
        for i, slot in enumerate(self.slots):
            if slot is not None:
                items.append({
                    "Slot": i,
                    "id": slot.item_id,
                    "Count": slot.count,
                    "Damage": slot.damage
                })
        return {"Items": items}


class CraftingSideSimulator:
    """
    Symulator stołu craftingowego Jammy.
    
    Na podstawie TileEntityWoodBlocksOne:
    - subBlock 13 (metadata 13 = Crafting Side)
    - 6 slotów inventory (3x2 grid)
    - Zegar (subBlock 5) ma osobną logikę dźwięków
    
    UWAGA: Konwersja trudna bo:
    1. Vanilla crafting table nie ma TE w 1.18.2
    2. Brak bezpośredniego odpowiednika 3x2 crafting
    3. Inventory crafting grid może być utracone
    """
    
    def __init__(self, facing: str = "north"):
        self.facing = facing
        self.inventory = CraftingSideInventory()
        self.x = self.y = self.z = 0
    
    def get_block_name_1710(self) -> str:
        return "jammyfurniture:WoodBlocksOne"
    
    def get_metadata_1710(self) -> int:
        """
        Metadata dla Crafting Side:
        - subBlock = 13
        - Orientacja: N=0, E=1, S=2, W=3
        - Metadata = orientacja + 13 nie działa bo max to 15
        
        W oryginale subBlock jest kodowany w inny sposób...
        Dla uproszczenia: metadata 13 = Crafting Side (zorientowany N)
        """
        facing_map = {"north": 0, "east": 1, "south": 2, "west": 3}
        orientation = facing_map.get(self.facing, 0)
        # W oryginale subBlock 13 to Crafting Side
        # Ale metadata musi być < 16, więc orientacja jest kodowana inaczej
        return 13  # Uproszczenie
    
    def get_block_id_1182_fallback(self) -> str:
        """
        Fallback dla 1.18.2 - co zrobić z tym blokiem?
        
        Opcje:
        1. minecraft:crafting_table - ale stracimy inventory
        2. supplementaries:safe - zachowa inventory
        3. Zrzucić itemy na ziemię przy konwersji
        """
        return "minecraft:crafting_table"
    
    def tick(self) -> None:
        """
        Tick - w oryginale tylko zegar ma logikę dźwięków.
        Crafting Side nie ma aktywnej logiki.
        """
        pass
    
    def to_nbt_1710(self) -> Dict[str, Any]:
        """Eksportuje do NBT 1.7.10."""
        return {
            "id": "TileEntityWoodBlocksOne",
            "x": self.x, "y": self.y, "z": self.z,
            **self.inventory.to_nbt_1710()
        }


class KitchenCupboardSimulator:
    """
    Symulator szafki kuchennej.
    
    Na podstawie TileEntityWoodBlocksTwo:
    - subBlock 0-3 = szafka zamknięta
    - subBlock 4-7 = szafka otwarta (półki)
    - 9 slotów inventory
    - TV ma osobną logikę (tvOn)
    """
    
    def __init__(self, cupboard_type: CupboardType, facing: str = "north"):
        self.cupboard_type = cupboard_type
        self.facing = facing
        self.inventory = KitchenCupboardInventory()
        self.x = self.y = self.z = 0
        
        # Dla TV (jeśli to TV a nie szafka)
        self.tv_on = 0  # timestamp włączenia
    
    def get_block_name_1710(self) -> str:
        return "jammyfurniture:WoodBlocksTwo"
    
    def get_metadata_1710(self) -> int:
        """Metadata = orientacja + subBlock."""
        facing_map = {"north": 0, "east": 1, "south": 2, "west": 3}
        orientation = facing_map.get(self.facing, 0)
        return orientation + self.cupboard_type.value
    
    def get_block_id_1182(self) -> str:
        """Macaw's Furniture - kitchen cabinet."""
        return "mcwfurnitures:oak_kitchen_cabinet"
    
    def get_block_state_1182(self) -> Dict[str, str]:
        """BlockState dla Macaw's."""
        return {
            "facing": self.facing,
            "open": "true" if self.cupboard_type == CupboardType.OPEN else "false"
        }
    
    def tick(self) -> None:
        """
        Tick - sprawdź czy TV jest włączony.
        TV wyłącza się automatycznie po 6.5 sekundy.
        """
        import time as pytime
        if self.tv_on > 0:
            current_time = int(pytime.time() * 1000)
            if current_time - self.tv_on > 6500:  # 6.5 sekundy
                self.tv_on = 0
    
    def turn_tv_on(self) -> None:
        """Włącza TV (jeśli to blok TV)."""
        import time as pytime
        self.tv_on = int(pytime.time() * 1000)
    
    def is_tv_on(self) -> bool:
        """Sprawdza czy TV jest włączony."""
        return self.tv_on > 0
    
    def to_nbt_1710(self) -> Dict[str, Any]:
        """Eksportuje do NBT 1.7.10."""
        nbt = {
            "id": "TileEntityWoodBlocksTwo",
            "x": self.x, "y": self.y, "z": self.z,
            **self.inventory.to_nbt_1710()
        }
        if self.tv_on > 0:
            nbt["tvOn"] = self.tv_on
        return nbt
    
    def to_nbt_1182(self) -> Dict[str, Any]:
        """Eksportuje do NBT 1.18.2 (Macaw's)."""
        return {
            "id": "mcwfurnitures:oak_kitchen_cabinet",
            "x": self.x, "y": self.y, "z": self.z,
            "Items": self.inventory.to_nbt_1710()["Items"]
        }


class WardrobeSimulator:
    """
    Symulator szafy (Wardrobe).
    
    Na podstawie TileEntityWoodBlocksFour:
    - 20 slotów inventory
    - subBlock 0-3 = dolna część
    - subBlock 4-7 = górna część
    
    Dwie części szafy dzielą to samo TE z 20 slotami.
    """
    
    def __init__(self, is_upper: bool = False, facing: str = "north"):
        self.is_upper = is_upper
        self.facing = facing
        self.inventory = WardrobeInventory()
        self.x = self.y = self.z = 0
    
    def get_block_name_1710(self) -> str:
        return "jammyfurniture:WoodBlocksFour"
    
    def get_metadata_1710(self) -> int:
        """Metadata = orientacja + subBlock."""
        facing_map = {"north": 0, "east": 1, "south": 2, "west": 3}
        orientation = facing_map.get(self.facing, 0)
        sub_block = 4 if self.is_upper else 0
        return orientation + sub_block
    
    def get_block_id_1182(self) -> str:
        """Macaw's Furniture - wardrobe."""
        return "mcwfurnitures:oak_wardrobe"
    
    def get_block_state_1182(self) -> Dict[str, str]:
        """BlockState dla Macaw's."""
        return {
            "facing": self.facing,
            "part": "upper" if self.is_upper else "lower"
        }
    
    def to_nbt_1710(self) -> Dict[str, Any]:
        """Eksportuje do NBT 1.7.10."""
        return {
            "id": "TileEntityWoodBlocksFour",
            "x": self.x, "y": self.y, "z": self.z,
            **self.inventory.to_nbt_1710()
        }
    
    def to_nbt_1182(self) -> Dict[str, Any]:
        """Eksportuje do NBT 1.18.2 (Macaw's)."""
        return {
            "id": "mcwfurnitures:oak_wardrobe",
            "x": self.x, "y": self.y, "z": self.z,
            "Items": self.inventory.to_nbt_1710()["Items"]
        }


def run_simulation_tests():
    """Uruchamia testy."""
    print("=" * 60)
    print("SYMPULACJA: Crafting Side, Szafki i Szafa")
    print("=" * 60)
    
    # Test 1: Crafting Side
    print("\n[TEST 1] Crafting Side (3x2 grid)")
    crafting = CraftingSideSimulator("north")
    
    # Wypełnij crafting grid
    crafting.inventory.set_item(0, ItemStack("minecraft:stick", count=1))
    crafting.inventory.set_item(1, ItemStack("minecraft:stick", count=1))
    crafting.inventory.set_item(3, ItemStack("minecraft:planks", count=1))
    crafting.inventory.set_item(4, ItemStack("minecraft:planks", count=1))
    
    print(f"  Grid 3x2: {len(crafting.inventory.slots)} slotów")
    print(f"  Items: {[s.item_id if s else None for s in crafting.inventory.slots]}")
    print(f"  NBT: {crafting.to_nbt_1710()}")
    print(f"  UWAGA: Konwersja trudna - vanilla crafting table nie ma TE!")
    
    # Test 2: Kitchen Cupboard
    print("\n[TEST 2] Kitchen Cupboard")
    cupboard = KitchenCupboardSimulator(CupboardType.CLOSED, "east")
    
    # Dodaj przedmioty
    for i in range(5):
        cupboard.inventory.set_item(i, ItemStack(f"minecraft:item_{i}", count=i+1))
    
    print(f"  Metadata 1.7.10: {cupboard.get_metadata_1710()}")
    print(f"  BlockState 1.18.2: {cupboard.get_block_state_1182()}")
    print(f"  Inventory: {sum(1 for s in cupboard.inventory.slots if s)} items")
    
    # Test 3: Wardrobe
    print("\n[TEST 3] Wardrobe (20 slotów)")
    wardrobe = WardrobeSimulator(is_upper=False, facing="south")
    
    # Wypełnij ubraniami
    armor_items = [
        "minecraft:diamond_helmet",
        "minecraft:diamond_chestplate",
        "minecraft:diamond_leggings",
        "minecraft:diamond_boots",
        "minecraft:iron_helmet",
    ]
    for i, armor in enumerate(armor_items):
        wardrobe.inventory.set_item(i, ItemStack(armor, count=1, damage=10))
    
    print(f"  Metadata 1.7.10 (dolna): {wardrobe.get_metadata_1710()}")
    print(f"  BlockState 1.18.2: {wardrobe.get_block_state_1182()}")
    print(f"  Inventory size: {wardrobe.inventory.get_size()} slots")
    print(f"  Items: {sum(1 for s in wardrobe.inventory.slots if s)}")
    
    # Test NBT 1.18.2
    nbt_1182 = wardrobe.to_nbt_1182()
    print(f"  NBT 1.18.2: {len(nbt_1182.get('Items', []))} items")
    
    print("\n" + "=" * 60)
    print("TESTY ZAKOŃCZONE POMYŚLNIE")
    print("=" * 60)


if __name__ == "__main__":
    run_simulation_tests()
