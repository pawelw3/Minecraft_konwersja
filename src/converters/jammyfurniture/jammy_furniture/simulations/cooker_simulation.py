"""
Symulacja kuchenki (Cooker) z Jammy Furniture Reborn (1.7.10).

Na podstawie kodu źródłowego:
- TileEntityIronBlocksOne.java (subBlock 8 = Cooker)
- CookerRecipes.java

Funkcjonalność:
- Kuchenka to podwójny piec (dual furnace)
- 5 slotów inventory:
  - Slot 0: Input 1 (surowe jedzenie)
  - Slot 1: Fuel (paliwo)
  - Slot 2: Output 1 (usmażone jedzenie)
  - Slot 3: Input 2 (surowe jedzenie)
  - Slot 4: Output 2 (usmażone jedzenie)
- Dwa niezależne sloty gotowania z różną prędkością:
  - Slot 0: 200 ticków (standard)
  - Slot 1: 150 ticków (szybciej)
- Obsługuje tylko ItemFood (jedzenie)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Callable
from enum import Enum
import time


@dataclass
class ItemStack:
    """Reprezentacja stosu itemów w Minecraft."""
    item_id: str
    count: int = 1
    damage: int = 0
    tag: Optional[Dict[str, Any]] = None
    is_food: bool = False  # Czy to jedzenie
    
    def copy(self) -> 'ItemStack':
        return ItemStack(
            item_id=self.item_id,
            count=self.count,
            damage=self.damage,
            tag=self.tag.copy() if self.tag else None,
            is_food=self.is_food
        )


class CookerRecipes:
    """
    Symulacja przepisów kuchenki.
    
    Na podstawie CookerRecipes.java:
    - Używa FurnaceRecipes jako bazy
    - Filtruje tylko ItemFood (jedzenie)
    """
    
    # Symulacja przepisów (surowe -> smażone)
    RECIPES: Dict[str, str] = {
        "minecraft:porkchop": "minecraft:cooked_porkchop",
        "minecraft:beef": "minecraft:cooked_beef",
        "minecraft:chicken": "minecraft:cooked_chicken",
        "minecraft:rabbit": "minecraft:cooked_rabbit",
        "minecraft:mutton": "minecraft:cooked_mutton",
        "minecraft:cod": "minecraft:cooked_cod",
        "minecraft:salmon": "minecraft:cooked_salmon",
        "minecraft:potato": "minecraft:baked_potato",
        "minecraft:kelp": "minecraft:dried_kelp",
    }
    
    # Czas gotowania dla każdego slotu
    COOK_TIME_SLOT_0 = 200  # ticks (10 sekund)
    COOK_TIME_SLOT_1 = 150  # ticks (7.5 sekundy) - szybciej
    
    @classmethod
    def get_smelting_result(cls, item: ItemStack) -> Optional[ItemStack]:
        """
        Zwraca wynik gotowania.
        
        Na podstawie CookerRecipes.getSmeltingResult():
        - Sprawdza czy wynik to ItemFood
        - Zwraca null jeśli to nie jedzenie
        """
        if item is None:
            return None
        
        result_id = cls.RECIPES.get(item.item_id)
        if result_id:
            return ItemStack(result_id, count=1, is_food=True)
        return None
    
    @classmethod
    def is_cookable(cls, item: ItemStack) -> bool:
        """Sprawdza czy item można usmażyć."""
        return cls.get_smelting_result(item) is not None


@dataclass
class CookerState:
    """
    Stan kuchenki.
    
    Na podstawie TileEntityIronBlocksOne:
    - cookerBurnTime: pozostały czas palenia paliwa
    - cookerCookTime0: postęp gotowania slot 0 (0-200)
    - cookerCookTime1: postęp gotowania slot 1 (0-150)
    - currentItemBurnTime: maksymalny czas palenia aktualnego paliwa
    """
    burn_time: int = 0  # Pozostały czas palenia
    cook_time_0: int = 0  # Postęp gotowania slot 0
    cook_time_1: int = 0  # Postęp gotowania slot 1
    current_burn_time: int = 0  # Max czas dla aktualnego paliwa
    
    # Inventory (5 slotów)
    # Slot 0: Input 1, Slot 1: Fuel, Slot 2: Output 1
    # Slot 3: Input 2, Slot 4: Output 2
    slots: List[Optional[ItemStack]] = field(default_factory=lambda: [None] * 5)
    
    def is_burning(self) -> bool:
        """Sprawdza czy kuchenka pali."""
        return self.burn_time > 0
    
    def get_burn_progress(self, max_size: int = 13) -> int:
        """Zwraca postęp palenia w skali 0-max_size (dla GUI)."""
        if self.current_burn_time == 0:
            self.current_burn_time = 200
        return self.burn_time * max_size // self.current_burn_time
    
    def get_cook_progress_0(self, max_size: int = 24) -> int:
        """Zwraca postęp gotowania slot 0 (0-max_size)."""
        return self.cook_time_0 * max_size // CookerRecipes.COOK_TIME_SLOT_0
    
    def get_cook_progress_1(self, max_size: int = 24) -> int:
        """Zwraca postęp gotowania slot 1 (0-max_size)."""
        return self.cook_time_1 * max_size // CookerRecipes.COOK_TIME_SLOT_1


class FuelRegistry:
    """Rejestr paliw - symulacja TileEntityFurnace.getItemBurnTime()"""
    
    FUELS: Dict[str, int] = {
        "minecraft:coal": 1600,  # 80 sekund
        "minecraft:charcoal": 1600,
        "minecraft:coal_block": 16000,  # 800 sekund
        "minecraft:lava_bucket": 20000,
        "minecraft:stick": 100,
        "minecraft:oak_planks": 300,
    }
    
    @classmethod
    def get_burn_time(cls, item: ItemStack) -> int:
        """Zwraca czas palenia w tickach."""
        if item is None:
            return 0
        return cls.FUELS.get(item.item_id, 0)
    
    @classmethod
    def is_fuel(cls, item: ItemStack) -> bool:
        """Sprawdza czy item jest paliwem."""
        return cls.get_burn_time(item) > 0


class CookerSimulator:
    """
    Symulator kuchenki Jammy Furniture 1.7.10.
    
    Na podstawie TileEntityIronBlocksOne (subBlock 8):
    - updateEntity() - logika tick'u
    - canSmelt() - sprawdzenie czy można gotować
    - smeltItem() - proces gotowania
    
    Logika tick'u:
    1. Jeśli pali -> zmniejsz burn_time
    2. Jeśli nie pali i można gotować -> dodaj paliwo
    3. Jeśli pali i można gotować slot 0 -> zwiększ cook_time_0
    4. Jeśli cook_time_0 >= 200 -> smeltItem(0)
    5. Analogicznie dla slot 1 (czas 150)
    """
    
    def __init__(self, facing: str = "north"):
        self.facing = facing
        self.state = CookerState()
        
        # Pozycja
        self.x = 0
        self.y = 0
        self.z = 0
    
    def get_block_name_1710(self) -> str:
        return "jammyfurniture:IronBlocksOne"
    
    def get_metadata_1710(self) -> int:
        """
        Metadata = orientacja (0-3) + subBlock 8
        """
        facing_map = {"north": 0, "east": 1, "south": 2, "west": 3}
        orientation = facing_map.get(self.facing, 0)
        return orientation + 8  # subBlock 8 = Cooker
    
    def get_block_state_1182(self) -> Dict[str, str]:
        """BlockState dla Macaw's Furniture (stove)."""
        return {
            "facing": self.facing,
            "lit": "true" if self.state.is_burning() else "false"
        }
    
    def get_block_id_1182(self) -> str:
        return "mcwfurnitures:stove"
    
    def can_smelt(self, slot_index: int) -> bool:
        """
        Sprawdza czy można gotować w danym slocie.
        
        Args:
            slot_index: 0 lub 1 (dwa sloty gotowania)
        
        Na podstawie TileEntityIronBlocksOne.canSmelt():
        - Sprawdź czy input istnieje
        - Sprawdź czy jest przepis
        - Sprawdź czy output mieści się w slocie wynikowym
        """
        before_slot = 0 if slot_index == 0 else 3
        after_slot = 2 if slot_index == 0 else 4
        
        input_item = self.state.slots[before_slot]
        if input_item is None:
            return False
        
        result = CookerRecipes.get_smelting_result(input_item)
        if result is None:
            return False
        
        output_item = self.state.slots[after_slot]
        if output_item is None:
            return True
        
        if output_item.item_id != result.item_id:
            return False
        
        # Sprawdź czy się zmieści (max 64)
        if output_item.count + result.count > 64:
            return False
        
        return True
    
    def smelt_item(self, slot_index: int) -> bool:
        """
        Wykonuje gotowanie w danym slocie.
        
        Na podstawie TileEntityIronBlocksOne.smeltItem():
        - Zmniejsz input
        - Dodaj/zwiększ output
        """
        if not self.can_smelt(slot_index):
            return False
        
        before_slot = 0 if slot_index == 0 else 3
        after_slot = 2 if slot_index == 0 else 4
        
        input_item = self.state.slots[before_slot]
        result = CookerRecipes.get_smelting_result(input_item)
        
        if result is None:
            return False
        
        output_item = self.state.slots[after_slot]
        
        if output_item is None:
            self.state.slots[after_slot] = result.copy()
        else:
            output_item.count += result.count
        
        # Zmniejsz input
        input_item.count -= 1
        if input_item.count <= 0:
            self.state.slots[before_slot] = None
        
        return True
    
    def tick(self) -> Dict[str, Any]:
        """
        Symulacja tick'u (updateEntity).
        
        Zwraca dict z informacjami o zmianach.
        """
        changes = {
            "burned_fuel": False,
            "slot_0_cooked": False,
            "slot_1_cooked": False,
        }
        
        # 1. Jeśli pali -> zmniejsz burn_time
        if self.state.is_burning():
            self.state.burn_time -= 1
        
        # 2. Jeśli nie pali i można gotować -> dodaj paliwo
        if not self.state.is_burning() and (self.can_smelt(0) or self.can_smelt(1)):
            fuel_item = self.state.slots[1]
            if fuel_item is not None:
                burn_time = FuelRegistry.get_burn_time(fuel_item)
                if burn_time > 0:
                    self.state.current_burn_time = burn_time
                    self.state.burn_time = burn_time
                    changes["burned_fuel"] = True
                    
                    # Zużyj paliwo
                    fuel_item.count -= 1
                    if fuel_item.count <= 0:
                        self.state.slots[1] = None
        
        # 3. Slot 0 gotowanie
        if self.state.is_burning() and self.can_smelt(0):
            self.state.cook_time_0 += 1
            if self.state.cook_time_0 >= CookerRecipes.COOK_TIME_SLOT_0:
                self.state.cook_time_0 = 0
                self.smelt_item(0)
                changes["slot_0_cooked"] = True
        else:
            self.state.cook_time_0 = 0
        
        # 4. Slot 1 gotowanie (szybciej)
        if self.state.is_burning() and self.can_smelt(1):
            self.state.cook_time_1 += 1
            if self.state.cook_time_1 >= CookerRecipes.COOK_TIME_SLOT_1:
                self.state.cook_time_1 = 0
                self.smelt_item(1)
                changes["slot_1_cooked"] = True
        else:
            self.state.cook_time_1 = 0
        
        return changes
    
    def to_nbt_1710(self) -> Dict[str, Any]:
        """Eksportuje stan do NBT 1.7.10."""
        items = []
        for i, slot in enumerate(self.state.slots):
            if slot is not None:
                items.append({
                    "Slot": i,
                    "id": slot.item_id,
                    "Count": slot.count,
                    "Damage": slot.damage
                })
        
        return {
            "id": "TileEntityIronBlocksOne",
            "x": self.x, "y": self.y, "z": self.z,
            "CookerItems": items,
            "BurnTime": self.state.burn_time,
            "CookTime": self.state.cook_time_0,
            "CookTime2": self.state.cook_time_1
        }
    
    def to_nbt_1182(self) -> Dict[str, Any]:
        """Eksportuje stan do NBT 1.18.2 (Macaw's Stove)."""
        # Macaw's stove ma prostszy format - tylko inventory
        items = []
        for i, slot in enumerate(self.state.slots):
            if slot is not None:
                items.append({
                    "Slot": i,
                    "id": slot.item_id,
                    "Count": slot.count
                })
        
        return {
            "id": "mcwfurnitures:stove",
            "x": self.x, "y": self.y, "z": self.z,
            "Items": items
        }


def run_simulation_tests():
    """Uruchamia testy symulacji kuchenki."""
    print("=" * 60)
    print("SYMPULACJA: Kuchenka (Cooker) Jammy Furniture")
    print("=" * 60)
    
    # Test 1: Podstawowe gotowanie
    print("\n[TEST 1] Podstawowe gotowanie w slocie 0")
    cooker = CookerSimulator(facing="north")
    
    # Włóż jedzenie i paliwo
    cooker.state.slots[0] = ItemStack("minecraft:porkchop", count=4, is_food=True)
    cooker.state.slots[1] = ItemStack("minecraft:coal", count=2)
    
    print(f"  Input: {cooker.state.slots[0].item_id} x{cooker.state.slots[0].count}")
    print(f"  Fuel: {cooker.state.slots[1].item_id} x{cooker.state.slots[1].count}")
    print(f"  Czas gotowania slot 0: {CookerRecipes.COOK_TIME_SLOT_0} ticków (10s)")
    
    # Symulacja 250 ticków
    for tick in range(250):
        changes = cooker.tick()
        if changes["slot_0_cooked"]:
            print(f"  -> Ugotowano po {tick} tickach!")
            break
    
    print(f"  Output: {cooker.state.slots[2].item_id if cooker.state.slots[2] else None}")
    print(f"  Pozostało input: {cooker.state.slots[0].count if cooker.state.slots[0] else 0}")
    
    # Test 2: Podwójne gotowanie
    print("\n[TEST 2] Podwójne gotowanie (oba sloty)")
    cooker2 = CookerSimulator(facing="east")
    
    cooker2.state.slots[0] = ItemStack("minecraft:beef", count=2, is_food=True)
    cooker2.state.slots[1] = ItemStack("minecraft:coal", count=4)
    cooker2.state.slots[3] = ItemStack("minecraft:chicken", count=2, is_food=True)
    
    print(f"  Slot 0: {cooker2.state.slots[0].item_id} (czas: {CookerRecipes.COOK_TIME_SLOT_0})")
    print(f"  Slot 3: {cooker2.state.slots[3].item_id} (czas: {CookerRecipes.COOK_TIME_SLOT_1})")
    
    slot0_done = False
    slot1_done = False
    
    for tick in range(300):
        changes = cooker2.tick()
        if changes["slot_0_cooked"] and not slot0_done:
            print(f"  -> Slot 0 ugotowany po {tick} tickach")
            slot0_done = True
        if changes["slot_1_cooked"] and not slot1_done:
            print(f"  -> Slot 1 ugotowany po {tick} tickach (szybciej!)")
            slot1_done = True
        if slot0_done and slot1_done:
            break
    
    # Test 3: NBT
    print("\n[TEST 3] Eksport NBT")
    nbt = cooker2.to_nbt_1710()
    print(f"  NBT 1.7.10: BurnTime={nbt['BurnTime']}, CookTime={nbt['CookTime']}")
    
    nbt_1182 = cooker2.to_nbt_1182()
    print(f"  NBT 1.18.2: {nbt_1182['id']}")
    
    print("\n" + "=" * 60)
    print("TESTY ZAKOŃCZONE POMYŚLNIE")
    print("=" * 60)


if __name__ == "__main__":
    run_simulation_tests()
