"""
Symulacja lodówki i zamrażarki z Jammy Furniture Reborn (1.7.10).

Na podstawie kodu źródłowego:
- TileEntityIronBlocksOne.java (subBlock 0 = lodówka, subBlock 4 = zamrażarka)

Funkcjonalność:
- Lodówka i zamrażarka to proste kontenery z inventory
- Lodówka: 9 slotów (INV_SIZE_FRIDGE = 9)
- Zamrażarka: 9 slotów (to samo co lodówka - ta sama klasa TE)
- Nie ma żadnej aktywnej logiki (nie chłodzi, nie mrozi) - tylko storage
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class FridgeType(Enum):
    """Typ bloku lodówkowego."""
    FRIDGE = 0  # subBlock 0 - lodówka dolna
    FREEZER = 4  # subBlock 4 - zamrażarka / lodówka górna


@dataclass
class ItemStack:
    """Reprezentacja stosu itemów w Minecraft."""
    item_id: str
    count: int = 1
    damage: int = 0  # Metadata/durability
    tag: Optional[Dict[str, Any]] = None
    
    def is_empty(self) -> bool:
        return self.count <= 0
    
    def copy(self) -> 'ItemStack':
        return ItemStack(
            item_id=self.item_id,
            count=self.count,
            damage=self.damage,
            tag=self.tag.copy() if self.tag else None
        )


@dataclass
class FridgeFreezerInventory:
    """
    Symulacja inventory lodówki/zamrażarki z Jammy Furniture 1.7.10.
    
    Na podstawie TileEntityIronBlocksOne:
    - INV_SIZE_FRIDGE = 9 slotów
    - Sloty: 0-8 dla przedmiotów
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
    
    def is_empty(self) -> bool:
        return all(slot is None for slot in self.slots)
    
    def add_item(self, item: ItemStack) -> bool:
        """Dodaje item do pierwszego wolnego slotu lub stackuje."""
        # Najpierw spróbuj stackować
        for i, slot in enumerate(self.slots):
            if slot is not None and slot.item_id == item.item_id:
                if slot.count + item.count <= 64:  # Max stack size
                    slot.count += item.count
                    return True
        
        # Potem znajdź pusty slot
        for i, slot in enumerate(self.slots):
            if slot is None:
                self.slots[i] = item.copy()
                return True
        
        return False  # Inventory pełne
    
    def to_nbt_1710(self) -> Dict[str, Any]:
        """Eksportuje inventory do formatu NBT 1.7.10."""
        items = []
        for i, slot in enumerate(self.slots):
            if slot is not None:
                items.append({
                    "Slot": i,
                    "id": slot.item_id,
                    "Count": slot.count,
                    "Damage": slot.damage,
                    "tag": slot.tag
                })
        return {
            "Items": items
        }
    
    @classmethod
    def from_nbt_1710(cls, nbt_data: Dict[str, Any]) -> 'FridgeFreezerInventory':
        """Tworzy inventory z formatu NBT 1.7.10."""
        inv = cls()
        for item_data in nbt_data.get("Items", []):
            slot = item_data.get("Slot", 0)
            if 0 <= slot < 9:
                inv.slots[slot] = ItemStack(
                    item_id=item_data.get("id", "minecraft:air"),
                    count=item_data.get("Count", 1),
                    damage=item_data.get("Damage", 0),
                    tag=item_data.get("tag")
                )
        return inv
    
    def to_nbt_1182(self) -> Dict[str, Any]:
        """Eksportuje inventory do formatu NBT 1.18.2 (Macaw's Furniture)."""
        # Format podobny, ale Macaw's może mieć inne wymagania
        items = []
        for i, slot in enumerate(self.slots):
            if slot is not None:
                items.append({
                    "Slot": i,
                    "id": slot.item_id,
                    "Count": slot.count,
                    "tag": slot.tag
                })
        return {
            "Items": items
        }


class FridgeFreezerSimulator:
    """
    Symulator lodówki/zamrażarki Jammy Furniture 1.7.10.
    
    Na podstawie TileEntityIronBlocksOne.java:
    - subBlock 0: Lodówka (Fridge)
    - subBlock 4: Zamrażarka (Freezer)
    - Oba mają to samo inventory (9 slotów)
    - Brak aktywnej logiki - tylko przechowywanie
    
    Mapowanie na 1.18.2:
    - mcwfurnitures:refrigerator[part=lower] - lodówka
    - mcwfurnitures:refrigerator[part=upper] - zamrażarka
    """
    
    def __init__(self, fridge_type: FridgeType, facing: str = "north"):
        self.fridge_type = fridge_type
        self.facing = facing
        self.inventory = FridgeFreezerInventory()
        
        # Dane z TileEntity
        self.x = 0
        self.y = 0
        self.z = 0
    
    def get_block_name_1710(self) -> str:
        """Zwraca nazwę bloku w 1.7.10."""
        return "jammyfurniture:IronBlocksOne"
    
    def get_metadata_1710(self) -> int:
        """
        Zwraca metadata dla 1.7.10.
        
        Metadata = orientacja (0-3) + subBlock
        - N=0, E=1, S=2, W=3
        - Fridge (subBlock 0): meta 0-3
        - Freezer (subBlock 4): meta 4-7
        """
        facing_map = {"north": 0, "east": 1, "south": 2, "west": 3}
        orientation = facing_map.get(self.facing, 0)
        return orientation + self.fridge_type.value
    
    def get_block_state_1182(self) -> Dict[str, str]:
        """Zwraca blockstate dla 1.18.2 (Macaw's Furniture)."""
        part = "lower" if self.fridge_type == FridgeType.FRIDGE else "upper"
        return {
            "facing": self.facing,
            "part": part
        }
    
    def get_block_id_1182(self) -> str:
        """Zwraca ID bloku w 1.18.2."""
        return "mcwfurnitures:refrigerator"
    
    def tick(self) -> None:
        """
        Symulacja ticku (update'u).
        
        W oryginalnym kodzie (TileEntityIronBlocksOne.updateEntity):
        - Dla lodówki/zamrażarki (subBlock 0 i 4): BRAK AKCJI
        - Brak procesowania, brak zużycia paliwa, etc.
        """
        # Lodówka i zamrażarka w Jammy są tylko kontenerami
        # Nie ma żadnej logiki w tick() dla nich
        pass
    
    def to_nbt_1710(self) -> Dict[str, Any]:
        """Eksportuje stan do NBT 1.7.10."""
        nbt = {
            "id": "TileEntityIronBlocksOne",
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "FriFreItems": self.inventory.to_nbt_1710()["Items"]
        }
        return nbt
    
    def to_nbt_1182(self) -> Dict[str, Any]:
        """Eksportuje stan do NBT 1.18.2."""
        # Macaw's Furniture używa podobnego formatu
        nbt = {
            "id": "mcwfurnitures:refrigerator",
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "Items": self.inventory.to_nbt_1182()["Items"]
        }
        return nbt
    
    @classmethod
    def from_nbt_1710(cls, nbt_data: Dict[str, Any]) -> 'FridgeFreezerSimulator':
        """Tworzy symulator z NBT 1.7.10."""
        sub_block = nbt_data.get("metadata", 0) // 4 * 4  # Przybliżone
        fridge_type = FridgeType.FRIDGE if sub_block < 4 else FridgeType.FREEZER
        
        sim = cls(fridge_type=fridge_type)
        sim.x = nbt_data.get("x", 0)
        sim.y = nbt_data.get("y", 0)
        sim.z = nbt_data.get("z", 0)
        
        if "FriFreItems" in nbt_data:
            sim.inventory = FridgeFreezerInventory.from_nbt_1710(
                {"Items": nbt_data["FriFreItems"]}
            )
        
        return sim


def run_simulation_tests():
    """Uruchamia testy symulacji."""
    print("=" * 60)
    print("SYMPULACJA: Lodówka i Zamrażarka Jammy Furniture")
    print("=" * 60)
    
    # Test 1: Lodówka
    print("\n[TEST 1] Lodówka (Fridge)")
    fridge = FridgeFreezerSimulator(FridgeType.FRIDGE, facing="north")
    
    # Dodaj przedmioty
    apple = ItemStack("minecraft:apple", count=16)
    bread = ItemStack("minecraft:bread", count=8)
    fridge.inventory.add_item(apple)
    fridge.inventory.add_item(bread)
    
    print(f"  Metadata 1.7.10: {fridge.get_metadata_1710()}")
    print(f"  BlockState 1.18.2: {fridge.get_block_state_1182()}")
    print(f"  Inventory slots: {fridge.inventory.get_size()}")
    print(f"  Items: {[(s.item_id, s.count) if s else None for s in fridge.inventory.slots[:3]]}")
    
    # Test NBT
    nbt_1710 = fridge.to_nbt_1710()
    print(f"  NBT 1.7.10: {nbt_1710}")
    
    # Test 2: Zamrażarka
    print("\n[TEST 2] Zamrażarka (Freezer)")
    freezer = FridgeFreezerSimulator(FridgeType.FREEZER, facing="east")
    
    beef = ItemStack("minecraft:beef", count=32)
    freezer.inventory.add_item(beef)
    
    print(f"  Metadata 1.7.10: {freezer.get_metadata_1710()}")
    print(f"  BlockState 1.18.2: {freezer.get_block_state_1182()}")
    print(f"  Items: {[(s.item_id, s.count) if s else None for s in freezer.inventory.slots[:2]]}")
    
    nbt_1182 = freezer.to_nbt_1182()
    print(f"  NBT 1.18.2: {nbt_1182}")
    
    # Test 3: Tick (brak akcji)
    print("\n[TEST 3] Tick simulation")
    print("  Lodówka przed tick: items =", sum(1 for s in fridge.inventory.slots if s))
    fridge.tick()
    print("  Lodówka po tick: items =", sum(1 for s in fridge.inventory.slots if s))
    print("  (Brak zmian - lodówka to tylko kontener)")
    
    print("\n" + "=" * 60)
    print("TESTY ZAKOŃCZONE POMYŚLNIE")
    print("=" * 60)


if __name__ == "__main__":
    run_simulation_tests()
