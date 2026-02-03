"""
Symulacja produkcji miodu w GrowthCraft (BeeBox)

Porównanie wersji:
- 1.7.10: TileEntityBeeBox, ID: "grcbees:bee_box"
- 1.18.2: BeeBoxBlockEntity, ID: "growthcraft:bee_box"

Zmiany w NBT:
- 1.7.10: "bee_box" (CompoundTag) z "bonus_time", "bee_count"
         Inventory: 28 slotów
           - Slot 0: Pszczoły (ItemBee)
           - Slot 1-27: Plastry miodu (puste i pełne)
         "BeeBox.version" (int) - wersja danych (3)
- 1.18.2: "CurrentProcessTicks" (int) - aktualny tick
         "inventory" (CompoundTag) - 28 slotów
           - Slot 0: Pszczoły (musi być w tagu BEE)
           - Slot 1-27: Plastry (mogą być puste, pełne lub vanillowe)

Nowości w 1.18.2:
- Konfigurowalny czas procesu (GrowthcraftApiaryConfig.getBeeBoxMaxProcessingTime())
- Szansa na rozmnaianie pszczół
- Szansa na replikację kwiatów wokół ula
- Obsługa vanillowych plastrów (Items.HONEYCOMB)

Warianty drewna (1.7.10 i 1.18.2):
- Oak, Spruce, Birch, Jungle, Acacia, Dark Oak
- Bamboo (dodatkowe w 1.18.2)
- Integracje z innymi modami (Forestry, Natura, BiomesOPlenty, itp.)
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set
from enum import Enum
import random


class BeeBoxStage(Enum):
    """Etap pracy ula"""
    IDLE = "idle"                    # Brak pszczół
    WORKING = "working"              # Pszczoły pracują
    PRODUCING = "producing"          # Produkowanie plastrów


@dataclass
class ItemStack:
    """Reprezentacja itemu"""
    item_id: str
    count: int = 1
    nbt: Optional[Dict[str, Any]] = None
    
    def shrink(self, amount: int = 1):
        self.count = max(0, self.count - amount)
    
    def grow(self, amount: int = 1):
        self.count += amount
    
    def is_empty(self) -> bool:
        return self.count <= 0
    
    def copy(self) -> 'ItemStack':
        return ItemStack(
            item_id=self.item_id,
            count=self.count,
            nbt=self.nbt.copy() if self.nbt else None
        )
    
    def __str__(self) -> str:
        return f"{self.item_id} x{self.count}"


@dataclass
class BeeBoxConfig:
    """Konfiguracja ula (z 1.18.2)"""
    max_processing_time: int = 1200  # ticki (1 minuta domyślnie)
    chance_to_increase_bees: int = 10  # 10% szansa na rozmnażanie
    chance_to_replicate_flowers: int = 5  # 5% szansa na replikację kwiatów
    bee_box_flower_range: int = 5  # zasięg poszukiwania kwiatów
    replicate_flowers: bool = True  # czy replikować kwiaty


class BeeBoxSimulator:
    """
    Symulator ula pszczelego GrowthCraft
    
    Inventory: 28 slotów
        - Slot 0: Pszczoły (ItemBee) - wymagane do pracy
        - Slot 1-27: Plastry miodu (puste, pełne, lub vanillowe)
    
    Mechanika:
    1. Wymaga pszczół w slocie 0 aby pracować
    2. Co tick_max ticków wykonuje cykl pracy
    3. Każda pszczoła ma szansę wykonać zadanie:
       - Nic nie rób
       - Zamień pusty plaster na pełny
       - Zamień vanillowy plaster na pełny (GC)
       - Replikuj kwiat w pobliżu
       - Dodaj nowy pusty plaster
    4. Szansa na zwiększenie populacji pszczół
    
    Przykład użycia:
        config = BeeBoxConfig(max_processing_time=1200)
        bee_box = BeeBoxSimulator(config=config)
        
        # Dodaj pszczoły
        bee_box.set_bees(ItemStack("growthcraft:bee", 16))
        
        # Dodaj puste plastry
        for i in range(5):
            bee_box.add_comb(ItemStack("growthcraft:honey_comb_empty", 1))
        
        # Symuluj
        for tick in range(5000):
            bee_box.tick()
            if tick % 100 == 0:
                print(f"Tick {tick}: {bee_box.get_summary()}")
    """
    
    TOTAL_SLOTS: int = 28
    BEE_SLOT: int = 0
    FIRST_COMB_SLOT: int = 1
    
    def __init__(self, version: str = "1.18.2", config: Optional[BeeBoxConfig] = None):
        self.version = version
        self.config = config or BeeBoxConfig()
        
        # Stan procesu
        self.tick_clock: int = 0
        self.stage: BeeBoxStage = BeeBoxStage.IDLE
        
        # Inventory
        self.bee_slot: Optional[ItemStack] = None  # Slot 0
        self.comb_slots: List[Optional[ItemStack]] = [None] * (self.TOTAL_SLOTS - 1)  # Slot 1-27
        
        # Statystyki
        self.total_honey_produced: int = 0
        self.total_bees_bred: int = 0
        self.total_flowers_replicated: int = 0
        self.cycle_count: int = 0
        
        # Historia
        self.history: List[Dict[str, Any]] = []
    
    def set_bees(self, bees: ItemStack):
        """Ustawia pszczoły w slocie 0"""
        self.bee_slot = bees.copy()
        self._update_stage()
    
    def add_comb(self, comb: ItemStack) -> bool:
        """Dodaje plaster do pierwszego wolnego slotu"""
        slot = self._get_empty_comb_slot()
        if slot == -1:
            return False
        self.comb_slots[slot] = comb.copy()
        return True
    
    def set_comb_in_slot(self, slot: int, comb: ItemStack) -> bool:
        """Ustawia plaster w konkretnym slocie (0-indexed dla comb_slots)"""
        if slot < 0 or slot >= len(self.comb_slots):
            return False
        self.comb_slots[slot] = comb.copy()
        return True
    
    def get_bee_count(self) -> int:
        """Zwraca liczbę pszczół"""
        if self.bee_slot is None or self.bee_slot.is_empty():
            return 0
        return self.bee_slot.count
    
    def get_empty_comb_slot(self) -> int:
        """Zwraca indeks pierwszego wolnego slotu na plaster lub -1"""
        return self._get_empty_comb_slot()
    
    def _get_empty_comb_slot(self) -> int:
        """Pomocnicza metoda znajdująca pusty slot"""
        for i, slot in enumerate(self.comb_slots):
            if slot is None or slot.is_empty():
                return i
        return -1
    
    def _get_slot_with_empty_comb(self) -> int:
        """Znajduje slot z pustym plastrem GC"""
        for i, slot in enumerate(self.comb_slots):
            if slot and slot.item_id == "growthcraft:honey_comb_empty":
                return i
        return -1
    
    def _get_slot_with_vanilla_comb(self) -> int:
        """Znajduje slot z vanillowym plastrem"""
        for i, slot in enumerate(self.comb_slots):
            if slot and slot.item_id == "minecraft:honeycomb":
                return i
        return -1
    
    def _update_stage(self):
        """Aktualizuje stan ula"""
        if self.get_bee_count() == 0:
            self.stage = BeeBoxStage.IDLE
        else:
            self.stage = BeeBoxStage.WORKING
    
    def tick(self):
        """Wykonuje jeden tick procesu produkcji"""
        bee_count = self.get_bee_count()
        
        # Brak pszczół = brak pracy
        if bee_count == 0:
            self._update_stage()
            return
        
        self.stage = BeeBoxStage.WORKING
        
        # Sprawdź czy minął czas cyklu
        if self.tick_clock >= self.config.max_processing_time:
            self._execute_work_cycle()
            self.tick_clock = 0
        else:
            self.tick_clock += 1
    
    def _execute_work_cycle(self):
        """Wykonuje cykl pracy pszczół"""
        bee_count = self.get_bee_count()
        workers = bee_count
        
        # Szansa na zwiększenie populacji
        if bee_count < 64 and random.randint(0, 100) <= self.config.chance_to_increase_bees:
            self.bee_slot.grow(1)
            self.total_bees_bred += 1
        
        # Każda pszczoła wykonuje zadanie
        for _ in range(workers):
            job_id = random.randint(0, 3)
            
            if job_id == 0:
                # Nic nie rób
                pass
                
            elif job_id == 1:
                # Sprawdź czy można zamienić plaster na pełny
                vanilla_slot = self._get_slot_with_vanilla_comb()
                empty_slot = self._get_slot_with_empty_comb()
                
                target_slot = vanilla_slot if vanilla_slot >= 0 else empty_slot
                
                if target_slot >= 0:
                    self.comb_slots[target_slot] = ItemStack("growthcraft:honey_comb_full", 1)
                    self.total_honey_produced += 1
                    
            elif job_id == 2:
                # Spróbuj replikować kwiaty
                if self.config.replicate_flowers and random.randint(0, 100) <= self.config.chance_to_replicate_flowers:
                    self.total_flowers_replicated += 1
                    
            else:
                # Dodaj nowy pusty plaster
                empty_slot = self._get_empty_comb_slot()
                if empty_slot >= 0:
                    self.comb_slots[empty_slot] = ItemStack("growthcraft:honey_comb_empty", 1)
        
        self.cycle_count += 1
        self.history.append({
            "cycle": self.cycle_count,
            "bees": self.get_bee_count(),
            "honey_produced": self.total_honey_produced,
            "flowers_replicated": self.total_flowers_replicated
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """Zwraca podsumowanie stanu ula"""
        empty_combs = sum(1 for s in self.comb_slots if s and s.item_id == "growthcraft:honey_comb_empty")
        full_combs = sum(1 for s in self.comb_slots if s and s.item_id == "growthcraft:honey_comb_full")
        vanilla_combs = sum(1 for s in self.comb_slots if s and s.item_id == "minecraft:honeycomb")
        
        return {
            "stage": self.stage.value,
            "progress": (self.tick_clock / self.config.max_processing_time) * 100,
            "bees": self.get_bee_count(),
            "empty_combs": empty_combs,
            "full_combs": full_combs,
            "vanilla_combs": vanilla_combs,
            "total_slots_used": sum(1 for s in self.comb_slots if s is not None and not s.is_empty()),
            "total_honey_produced": self.total_honey_produced,
            "cycles_completed": self.cycle_count
        }
    
    def to_nbt_1710(self) -> Dict[str, Any]:
        """Eksportuje do NBT 1.7.10"""
        nbt = {
            "id": "grcbees:bee_box",
            "BeeBox.version": 3,
        }
        
        # Dane bee_box
        bee_box_data = {
            "bonus_time": 0,
            "bee_count": self.get_bee_count()
        }
        nbt["bee_box"] = bee_box_data
        
        # Inventory
        items = []
        if self.bee_slot:
            items.append({
                "id": self.bee_slot.item_id,
                "Count": self.bee_slot.count,
                "Slot": 0
            })
        
        for i, slot in enumerate(self.comb_slots):
            if slot and not slot.is_empty():
                items.append({
                    "id": slot.item_id,
                    "Count": slot.count,
                    "Slot": i + 1
                })
        
        nbt["items"] = items
        return nbt
    
    def to_nbt_1182(self) -> Dict[str, Any]:
        """Eksportuje do NBT 1.18.2"""
        nbt = {
            "id": "growthcraft:bee_box",
            "CurrentProcessTicks": self.tick_clock,
        }
        
        # Inventory (wszystkie 28 slotów)
        items = []
        if self.bee_slot:
            items.append({
                "id": self.bee_slot.item_id,
                "Count": self.bee_slot.count,
                "Slot": 0
            })
        
        for i, slot in enumerate(self.comb_slots):
            if slot and not slot.is_empty():
                items.append({
                    "id": slot.item_id,
                    "Count": slot.count,
                    "Slot": i + 1
                })
        
        nbt["inventory"] = {
            "Size": 28,
            "Items": items
        }
        
        return nbt
    
    def from_nbt_1710(self, nbt: Dict[str, Any]):
        """Importuje z NBT 1.7.10"""
        bee_box_data = nbt.get("bee_box", {})
        self.tick_clock = 0  # W 1.7.10 nie ma tick_clock
        
        items = nbt.get("items", [])
        for item in items:
            slot = item.get("Slot", 0)
            stack = ItemStack(
                item_id=item.get("id", ""),
                count=item.get("Count", 0)
            )
            if slot == 0:
                self.bee_slot = stack
            else:
                self.comb_slots[slot - 1] = stack
        
        self._update_stage()
    
    def from_nbt_1182(self, nbt: Dict[str, Any]):
        """Importuje z NBT 1.18.2"""
        self.tick_clock = nbt.get("CurrentProcessTicks", 0)
        
        inventory = nbt.get("inventory", {})
        items = inventory.get("Items", [])
        
        for item in items:
            slot = item.get("Slot", 0)
            stack = ItemStack(
                item_id=item.get("id", ""),
                count=item.get("Count", 0)
            )
            if slot == 0:
                self.bee_slot = stack
            else:
                self.comb_slots[slot - 1] = stack
        
        self._update_stage()
    
    def __str__(self) -> str:
        summary = self.get_summary()
        return (
            f"BeeBox[{self.version}] "
            f"stage={summary['stage']}, "
            f"bees={summary['bees']}, "
            f"combs={summary['empty_combs']}E/{summary['full_combs']}F/{summary['vanilla_combs']}V, "
            f"progress={summary['progress']:.1f}%, "
            f"cycles={summary['cycles_completed']}"
        )
