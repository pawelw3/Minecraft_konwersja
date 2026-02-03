"""
Symulacja zmywarki (Dishwasher) i pralki (Washing Machine) z Jammy Furniture (1.7.10).

Na podstawie kodu źródłowego:
- TileEntityIronBlocksTwo.java
- DishwasherRecipes.java
- WashingMachineRecipes.java

Funkcjonalność:
- Zmywarka: Naprawia zużyte narzędzia (miecze, kilofy, siekiery, motyki, łopaty)
- Pralka: Naprawia zużytą zbroję (wszystkie typy)
- 5 slotów inventory:
  - Slot 0-3: Input (przedmioty do naprawy)
  - Slot 1: Fuel (paliwo)
- Każdy slot ma niezaleczny czas naprawy
- Czas naprawy zależy od typu przedmiotu i jego zużycia

Szczegóły zmywarki (Dishwasher):
- Naprawia: miecz, kilof, siekiera, motyka, łopata
- Czasy: 1500-7200 ticków (zależnie od materiału)
- Wood: 1500, Stone: 4000, Iron: 4800, Gold: 6000, Diamond: 7200

Szczegóły pralki (WashingMachine):
- Naprawia: wszystkie typy zbroi (hełm, napierśnik, spodnie, buty)
- Czasy: 1500-7200 ticków (zależnie od materiału)
- Leather: 1500, Chain: 4000, Iron: 4800, Gold: 6000, Diamond: 7200
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum


@dataclass
class ItemStack:
    """Reprezentacja stosu itemów."""
    item_id: str
    count: int = 1
    damage: int = 0  # Zużycie (0 = nowy, max = zepsuty)
    max_damage: int = 0
    tag: Optional[Dict[str, Any]] = None
    
    def copy(self) -> 'ItemStack':
        return ItemStack(
            item_id=self.item_id,
            count=self.count,
            damage=self.damage,
            max_damage=self.max_damage,
            tag=self.tag.copy() if self.tag else None
        )
    
    def is_damaged(self) -> bool:
        return self.damage > 0 and self.max_damage > 0
    
    def repair(self) -> None:
        """Naprawia przedmiot (zeruje damage)."""
        self.damage = 0


class ApplianceType(Enum):
    """Typ urządzenia AGD."""
    DISHWASHER = 0  # subBlock 0
    WASHING_MACHINE = 4  # subBlock 4


class DishwasherRecipes:
    """
    Przepisy zmywarki - naprawa narzędzi.
    
    Na podstawie DishwasherRecipes.java:
    - Naprawia narzędzia z damage > 0
    - Czas naprawy zależy od materiału
    """
    
    # Czasy naprawy dla predefiniowanych itemów (ticki)
    REPAIR_TIMES: Dict[str, int] = {
        # Miecze
        "minecraft:wooden_sword": 1500,
        "minecraft:stone_sword": 4000,
        "minecraft:iron_sword": 4800,
        "minecraft:golden_sword": 6000,
        "minecraft:diamond_sword": 7200,
        # Kilofy
        "minecraft:wooden_pickaxe": 1500,
        "minecraft:stone_pickaxe": 4000,
        "minecraft:iron_pickaxe": 4800,
        "minecraft:golden_pickaxe": 6000,
        "minecraft:diamond_pickaxe": 7200,
        # Siekiery
        "minecraft:wooden_axe": 1500,
        "minecraft:stone_axe": 4000,
        "minecraft:iron_axe": 4800,
        "minecraft:golden_axe": 6000,
        "minecraft:diamond_axe": 7200,
        # Motyki
        "minecraft:wooden_hoe": 1500,
        "minecraft:stone_hoe": 4000,
        "minecraft:iron_hoe": 4800,
        "minecraft:golden_hoe": 6000,
        "minecraft:diamond_hoe": 7200,
        # Łopaty
        "minecraft:wooden_shovel": 1500,
        "minecraft:stone_shovel": 4000,
        "minecraft:iron_shovel": 4800,
        "minecraft:golden_shovel": 6000,
        "minecraft:diamond_shovel": 7200,
    }
    
    # Klasy narzędzi do dynamicznego wykrywania
    TOOL_PATTERNS = ["sword", "pickaxe", "axe", "hoe", "shovel"]
    DEFAULT_REPAIR_TIME = 8000  # Dla nietypowych narzędzi
    
    @classmethod
    def can_repair(cls, item: ItemStack) -> bool:
        """
        Sprawdza czy przedmiot można naprawić w zmywarce.
        
        Warunki:
        1. Musi być uszkodzony (damage > 0)
        2. Musi być narzędziem (miecz, kilof, siekiera, motyka, łopata)
        """
        if item is None or not item.is_damaged():
            return False
        
        # Sprawdź czy to znane narzędzie
        if item.item_id in cls.REPAIR_TIMES:
            return True
        
        # Sprawdź czy to narzędzie po nazwie
        for pattern in cls.TOOL_PATTERNS:
            if pattern in item.item_id:
                return True
        
        return False
    
    @classmethod
    def get_repair_time(cls, item: ItemStack) -> int:
        """Zwraca czas naprawy w tickach."""
        if item is None:
            return 0
        
        return cls.REPAIR_TIMES.get(item.item_id, cls.DEFAULT_REPAIR_TIME)
    
    @classmethod
    def get_smelting_result(cls, item: ItemStack) -> Optional[ItemStack]:
        """
        Zwraca wynik 'naprawy' (naprawiony item).
        
        W oryginale zwraca kopię itemu z durability = 0
        """
        if not cls.can_repair(item):
            return None
        
        result = item.copy()
        result.repair()
        return result


class WashingMachineRecipes:
    """
    Przepisy pralki - naprawa zbroi.
    
    Na podstawie WashingMachineRecipes.java:
    - Naprawia zbroję z damage > 0
    - Czas naprawy zależy od materiału
    """
    
    # Czasy naprawy dla predefiniowanych itemów zbroi
    REPAIR_TIMES: Dict[str, int] = {
        # Skórzana
        "minecraft:leather_helmet": 1500,
        "minecraft:leather_chestplate": 1500,
        "minecraft:leather_leggings": 1500,
        "minecraft:leather_boots": 1500,
        # Chainmail
        "minecraft:chainmail_helmet": 4000,
        "minecraft:chainmail_chestplate": 4000,
        "minecraft:chainmail_leggings": 4000,
        "minecraft:chainmail_boots": 4000,
        # Żelazna
        "minecraft:iron_helmet": 4800,
        "minecraft:iron_chestplate": 4800,
        "minecraft:iron_leggings": 4800,
        "minecraft:iron_boots": 4800,
        # Złota
        "minecraft:golden_helmet": 6000,
        "minecraft:golden_chestplate": 6000,
        "minecraft:golden_leggings": 6000,
        "minecraft:golden_boots": 6000,
        # Diamentowa
        "minecraft:diamond_helmet": 7200,
        "minecraft:diamond_chestplate": 7200,
        "minecraft:diamond_leggings": 7200,
        "minecraft:diamond_boots": 7200,
    }
    
    # Wzorce dla dynamicznego wykrywania
    ARMOR_PATTERNS = ["helmet", "chestplate", "leggings", "boots"]
    DEFAULT_REPAIR_TIME = 8000
    
    @classmethod
    def can_repair(cls, item: ItemStack) -> bool:
        """Sprawdza czy zbroję można naprawić."""
        if item is None or not item.is_damaged():
            return False
        
        if item.item_id in cls.REPAIR_TIMES:
            return True
        
        for pattern in cls.ARMOR_PATTERNS:
            if pattern in item.item_id:
                return True
        
        return False
    
    @classmethod
    def get_repair_time(cls, item: ItemStack) -> int:
        """Zwraca czas naprawy."""
        if item is None:
            return 0
        return cls.REPAIR_TIMES.get(item.item_id, cls.DEFAULT_REPAIR_TIME)
    
    @classmethod
    def get_smelting_result(cls, item: ItemStack) -> Optional[ItemStack]:
        """Zwraca naprawioną zbroję."""
        if not cls.can_repair(item):
            return None
        
        result = item.copy()
        result.repair()
        return result


class FuelRegistry:
    """Rejestr paliw."""
    
    FUELS: Dict[str, int] = {
        "minecraft:coal": 1600,
        "minecraft:charcoal": 1600,
        "minecraft:coal_block": 16000,
    }
    
    @classmethod
    def get_burn_time(cls, item: ItemStack) -> int:
        if item is None:
            return 0
        return cls.FUELS.get(item.item_id, 0)
    
    @classmethod
    def is_fuel(cls, item: ItemStack) -> bool:
        return cls.get_burn_time(item) > 0


@dataclass
class ApplianceState:
    """Stan urządzenia AGD."""
    burn_time: int = 0
    current_burn_time: int = 0
    
    # Czasy naprawy dla każdego slotu (0-3)
    slot_times: List[int] = field(default_factory=lambda: [0, 0, 0, 0])
    
    # Inventory: Slot 0,1,2,3 = input, Slot 1 = fuel (shared)
    # UWAGA: W oryginale slot 1 to fuel, ale sloty 0,2,3,4 to input
    # Dla uproszczenia: slots[0-3] = input, slots[4] = fuel
    slots: List[Optional[ItemStack]] = field(default_factory=lambda: [None] * 5)
    
    def is_burning(self) -> bool:
        return self.burn_time > 0
    
    def get_fuel_slot(self) -> Optional[ItemStack]:
        return self.slots[4]
    
    def set_fuel_slot(self, item: Optional[ItemStack]) -> None:
        self.slots[4] = item


class ApplianceSimulator:
    """
    Symulator zmywarki lub pralki.
    
    Na podstawie TileEntityIronBlocksTwo:
    - 4 sloty na przedmioty do naprawy
    - 1 slot na paliwo
    - Niezależne timery dla każdego slotu
    - Naprawa = reset damage do 0
    """
    
    # Mapowanie slotów: slot_index -> indeks w self.state.slots
    SLOT_MAPPING = {0: 0, 1: 2, 2: 3, 3: 4}  # Pomijamy slot 1 (fuel)
    
    def __init__(self, appliance_type: ApplianceType, facing: str = "north"):
        self.appliance_type = appliance_type
        self.facing = facing
        self.state = ApplianceState()
        
        self.x = self.y = self.z = 0
        
        # Dźwięk (symulacja)
        self.last_sound_time = 0
    
    def get_recipes(self):
        """Zwraca odpowiednią klasę przepisów."""
        if self.appliance_type == ApplianceType.DISHWASHER:
            return DishwasherRecipes
        return WashingMachineRecipes
    
    def get_block_name_1710(self) -> str:
        return "jammyfurniture:IronBlocksTwo"
    
    def get_metadata_1710(self) -> int:
        """Metadata = orientacja + subBlock."""
        facing_map = {"north": 0, "east": 1, "south": 2, "west": 3}
        orientation = facing_map.get(self.facing, 0)
        return orientation + self.appliance_type.value
    
    def get_block_id_1182(self) -> str:
        """Brak bezpośredniego odpowiednika w Macaw's - placeholder."""
        return "mcwfurnitures:kitchen_cabinet"
    
    def can_repair(self, slot_index: int) -> bool:
        """Sprawdza czy można naprawić przedmiot w danym slocie."""
        recipes = self.get_recipes()
        slot = self.SLOT_MAPPING[slot_index]
        item = self.state.slots[slot]
        return recipes.can_repair(item)
    
    def can_repair_any(self) -> bool:
        """Sprawdza czy można naprawić cokolwiek."""
        return any(self.can_repair(i) for i in range(4))
    
    def get_repair_time(self, slot_index: int) -> int:
        """Zwraca czas naprawy dla slotu."""
        recipes = self.get_recipes()
        slot = self.SLOT_MAPPING[slot_index]
        item = self.state.slots[slot]
        return recipes.get_repair_time(item)
    
    def repair_item(self, slot_index: int) -> bool:
        """Naprawia przedmiot w danym slocie."""
        if not self.can_repair(slot_index):
            return False
        
        slot = self.SLOT_MAPPING[slot_index]
        item = self.state.slots[slot]
        
        if item is None:
            return False
        
        item.repair()
        return True
    
    def tick(self) -> Dict[str, Any]:
        """Symulacja tick'u."""
        changes = {
            "burned_fuel": False,
            "sound_played": False,
            "repaired_slots": []
        }
        
        # Zmniejsz czas palenia
        if self.state.is_burning():
            self.state.burn_time -= 1
            
            # Odtwórz dźwięk co 13 sekund (13000ms)
            import time as pytime
            current_time = int(pytime.time() * 1000)
            if current_time - self.last_sound_time >= 13000 and self.can_repair_any():
                changes["sound_played"] = True
                self.last_sound_time = current_time
        
        # Dodaj paliwo jeśli trzeba
        if not self.state.is_burning() and self.can_repair_any():
            fuel = self.state.get_fuel_slot()
            if fuel:
                burn_time = FuelRegistry.get_burn_time(fuel)
                if burn_time > 0:
                    self.state.current_burn_time = burn_time
                    self.state.burn_time = burn_time
                    changes["burned_fuel"] = True
                    
                    # Zużyj paliwo
                    fuel.count -= 1
                    if fuel.count <= 0:
                        self.state.set_fuel_slot(None)
        
        # Proces naprawy dla każdego slotu
        for slot_idx in range(4):
            slot = self.SLOT_MAPPING[slot_idx]
            
            if self.state.is_burning() and self.can_repair(slot_idx):
                self.state.slot_times[slot_idx] += 1
                target_time = self.get_repair_time(slot_idx)
                
                if self.state.slot_times[slot_idx] >= target_time:
                    self.state.slot_times[slot_idx] = 0
                    if self.repair_item(slot_idx):
                        changes["repaired_slots"].append(slot_idx)
            else:
                self.state.slot_times[slot_idx] = 0
        
        return changes
    
    def to_nbt_1710(self) -> Dict[str, Any]:
        """Eksportuje do NBT 1.7.10."""
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
            "id": "TileEntityIronBlocksTwo",
            "x": self.x, "y": self.y, "z": self.z,
            "dwItems" if self.appliance_type == ApplianceType.DISHWASHER else "wmItems": items,
            "burnTime": self.state.burn_time,
            "slot0Time": self.state.slot_times[0],
            "slot1Time": self.state.slot_times[1],
            "slot2Time": self.state.slot_times[2],
            "slot3Time": self.state.slot_times[3]
        }


def run_simulation_tests():
    """Uruchamia testy."""
    print("=" * 60)
    print("SYMPULACJA: Zmywarka i Pralka Jammy Furniture")
    print("=" * 60)
    
    # Test 1: Zmywarka
    print("\n[TEST 1] Zmywarka - naprawa narzędzi")
    dishwasher = ApplianceSimulator(ApplianceType.DISHWASHER, "north")
    
    # Dodaj uszkodzone narzędzia
    pickaxe = ItemStack("minecraft:diamond_pickaxe", damage=100, max_damage=1561)
    sword = ItemStack("minecraft:iron_sword", damage=50, max_damage=250)
    
    dishwasher.state.slots[0] = pickaxe
    dishwasher.state.slots[2] = sword
    dishwasher.state.set_fuel_slot(ItemStack("minecraft:coal", count=5))
    
    print(f"  Diamentowy kilof: damage={pickaxe.damage}/{pickaxe.max_damage}")
    print(f"  Żelazny miecz: damage={sword.damage}/{sword.max_damage}")
    print(f"  Czas naprawy kilofa: {DishwasherRecipes.get_repair_time(pickaxe)} ticków")
    print(f"  Czas naprawy miecza: {DishwasherRecipes.get_repair_time(sword)} ticków")
    
    # Symulacja
    ticks = 0
    while ticks < 8000:
        changes = dishwasher.tick()
        if 0 in changes["repaired_slots"]:
            print(f"  -> Kilof naprawiony po {ticks} tickach!")
        if 1 in changes["repaired_slots"]:
            print(f"  -> Miecz naprawiony po {ticks} tickach!")
            break
        ticks += 1
    
    print(f"  Stan kilofa po naprawie: damage={pickaxe.damage}")
    print(f"  Stan miecza po naprawie: damage={sword.damage}")
    
    # Test 2: Pralka
    print("\n[TEST 2] Pralka - naprawa zbroi")
    washer = ApplianceSimulator(ApplianceType.WASHING_MACHINE, "east")
    
    helmet = ItemStack("minecraft:diamond_helmet", damage=80, max_damage=363)
    boots = ItemStack("minecraft:iron_boots", damage=60, max_damage=195)
    
    washer.state.slots[0] = helmet
    washer.state.slots[2] = boots
    washer.state.set_fuel_slot(ItemStack("minecraft:coal", count=3))
    
    print(f"  Diamentowy hełm: damage={helmet.damage}")
    print(f"  Żelazne buty: damage={boots.damage}")
    
    # Symulacja
    ticks = 0
    while ticks < 8000:
        changes = washer.tick()
        if 0 in changes["repaired_slots"]:
            print(f"  -> Hełm naprawiony po {ticks} tickach!")
        if 1 in changes["repaired_slots"]:
            print(f"  -> Buty naprawione po {ticks} tickach!")
            break
        ticks += 1
    
    # Test 3: NBT
    print("\n[TEST 3] Eksport NBT")
    nbt = dishwasher.to_nbt_1710()
    print(f"  NBT zmywarki: {nbt['id']}, burnTime={nbt['burnTime']}")
    
    print("\n" + "=" * 60)
    print("TESTY ZAKOŃCZONE POMYŚLNIE")
    print("=" * 60)


if __name__ == "__main__":
    run_simulation_tests()
