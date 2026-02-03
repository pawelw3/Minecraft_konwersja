"""
Symulacja kosza na śmieci (Rubbish Bin) i zegara (Clock) z Jammy Furniture (1.7.10).

Na podstawie kodu źródłowego:
- TileEntityIronBlocksOne.java (subBlock 12 = Rubbish Bin)
- TileEntityWoodBlocksOne.java (subBlock 5 = Clock)

Funkcjonalności:

1. Rubbish Bin (Kosz na śmieci):
   - 27 slotów inventory (duży!)
   - Automatycznie opróżnia się co 60 sekund (60000ms)
   - Osobne dźwięki otwierania/zamykania (trashopen/trashclosed)
   - rubishBinOrientation - orientacja w NBT

2. Clock (Zegar):
   - Nie ma inventory
   - Odtwarza dźwięki:
     - "clock-tick" co 2 sekundy (2000ms)
     - "clock-dong" o pełnej godzinie (12:00, 0:00)
   - Liczy czas gry (worldTime)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import time as pytime


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


@dataclass
class RubbishBinInventory:
    """
    Inventory kosza na śmieci.
    
    Na podstawie TileEntityIronBlocksOne:
    - 27 slotów (INV_SIZE_RUBBISHBIN = 27)
    - Automatyczne czyszczenie co 60 sekund
    """
    slots: List[Optional[ItemStack]] = field(default_factory=lambda: [None] * 27)
    
    def get_size(self) -> int:
        return 27
    
    def get_item(self, slot: int) -> Optional[ItemStack]:
        if 0 <= slot < 27:
            return self.slots[slot]
        return None
    
    def set_item(self, slot: int, item: Optional[ItemStack]) -> bool:
        if 0 <= slot < 27:
            self.slots[slot] = item
            return True
        return False
    
    def clear(self) -> None:
        """Czyści całe inventory."""
        for i in range(27):
            self.slots[i] = None
    
    def is_empty(self) -> bool:
        return all(slot is None for slot in self.slots)
    
    def to_nbt_1710(self) -> Dict[str, Any]:
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
    def from_nbt_1710(cls, nbt_data: Dict[str, Any]) -> 'RubbishBinInventory':
        inv = cls()
        for item_data in nbt_data.get("Items", []):
            slot = item_data.get("Slot", 0)
            if 0 <= slot < 27:
                inv.slots[slot] = ItemStack(
                    item_id=item_data.get("id", "minecraft:air"),
                    count=item_data.get("Count", 1),
                    damage=item_data.get("Damage", 0)
                )
        return inv


class RubbishBinSimulator:
    """
    Symulator kosza na śmieci.
    
    Na podstawie TileEntityIronBlocksOne (subBlock 12):
    - 27 slotów inventory
    - Automatyczne czyszczenie co 60 sekund (60000ms)
    - orientacja w NBT (rubishBinOrientation)
    - Dźwięki: trashopen, trashclosed
    
    Mapowanie na 1.18.2:
    - mcwfurnitures:trash_can - ale ma tylko 1 slot lub auto-usuwa
    - Może wymagać zachowania tylko 1 slotu lub zrzucenia itemów
    """
    
    CLEAR_INTERVAL = 60000  # 60 sekund w ms
    
    def __init__(self, facing: str = "north"):
        self.facing = facing
        self.inventory = RubbishBinInventory()
        self.x = self.y = self.z = 0
        
        # Orientacja w NBT
        self.orientation = 0
        
        # Ostatnie czyszczenie
        self.last_clearance = int(pytime.time() * 1000)
    
    def get_block_name_1710(self) -> str:
        return "jammyfurniture:IronBlocksOne"
    
    def get_metadata_1710(self) -> int:
        """subBlock 12 = Rubbish Bin."""
        return 12
    
    def get_block_id_1182(self) -> str:
        """Macaw's Furniture - trash can."""
        return "mcwfurnitures:trash_can"
    
    def tick(self) -> bool:
        """
        Tick - sprawdź czy minęło 60 sekund i wyczyść.
        
        Returns:
            True jeśli wyczyszczono, False w przeciwnym razie
        """
        current_time = int(pytime.time() * 1000)
        if current_time - self.last_clearance >= self.CLEAR_INTERVAL:
            self.inventory.clear()
            self.last_clearance = current_time
            return True
        return False
    
    def to_nbt_1710(self) -> Dict[str, Any]:
        return {
            "id": "TileEntityIronBlocksOne",
            "x": self.x, "y": self.y, "z": self.z,
            "BinItems": self.inventory.to_nbt_1710()["Items"],
            "rubishBinOrientation": self.orientation
        }
    
    def to_nbt_1182(self) -> Dict[str, Any]:
        """
        Eksportuje do NBT 1.18.2.
        
        UWAGA: Macaw's trash_can ma tylko 1 slot lub auto-usuwa itemy.
        Zachowujemy tylko pierwszy item lub zwracamy pusty.
        """
        # Znajdź pierwszy item
        first_item = None
        for slot in self.inventory.slots:
            if slot is not None:
                first_item = slot
                break
        
        items = []
        if first_item:
            items.append({
                "Slot": 0,
                "id": first_item.item_id,
                "Count": first_item.count
            })
        
        return {
            "id": "mcwfurnitures:trash_can",
            "x": self.x, "y": self.y, "z": self.z,
            "Items": items
        }


class ClockSimulator:
    """
    Symulator zegara.
    
    Na podstawie TileEntityWoodBlocksOne (subBlock 5):
    - Nie ma inventory
    - Odtwarza dźwięki:
      - "clock-tick" co 2 sekundy (2000ms)
      - "clock-dong" o pełnej godzinie (12:00, 0:00)
    - Liczy czas gry (worldTime)
    
    Format czasu gry:
    - World time / 1000 = godzina (0-23)
    - Dodaj 6 bo dzień zaczyna się o 6:00
    - Minuty = (worldTime % 1000) * 60 / 1000
    """
    
    TICK_INTERVAL = 2000  # 2 sekundy w ms
    
    def __init__(self, facing: str = "north"):
        self.facing = facing
        self.x = self.y = self.z = 0
        
        # Ostatni tick dźwięku
        self.last_sound_time = 0
        
        # Czy odtworzono dong (żeby nie powtarzać)
        self.sound_dong_played = False
    
    def get_block_name_1710(self) -> str:
        return "jammyfurniture:WoodBlocksOne"
    
    def get_metadata_1710(self) -> int:
        """subBlock 5 = Clock (środek zegara)."""
        return 5
    
    def get_block_id_1182(self) -> str:
        """Supplementaries - clock block."""
        return "supplementaries:clock_block"
    
    def get_game_time(self, world_time: int) -> tuple:
        """
        Konwertuje world time na godzinę i minuty.
        
        Args:
            world_time: Czas świata w tickach
        
        Returns:
            (hour, minute) - godzina 0-23, minuta 0-59
        """
        hour = (world_time // 1000 + 6) % 24
        minute = (world_time - (world_time // 1000) * 1000) * 60 // 1000
        return hour, minute
    
    def tick(self, world_time: int) -> Dict[str, Any]:
        """
        Tick zegara.
        
        Args:
            world_time: Aktualny czas świata
        
        Returns:
            Dict z informacjami o dźwiękach
        """
        result = {
            "tick_sound": False,
            "dong_sound": False,
            "hour": 0,
            "minute": 0
        }
        
        hour, minute = self.get_game_time(world_time)
        result["hour"] = hour
        result["minute"] = minute
        
        current_time = int(pytime.time() * 1000)
        
        # Dong o pełnej godzinie (minuta = 0)
        if minute == 0 and (hour == 0 or hour == 12):
            if not self.sound_dong_played:
                result["dong_sound"] = True
                self.sound_dong_played = True
        else:
            self.sound_dong_played = False
        
        # Tick co 2 sekundy
        if current_time - self.last_sound_time >= self.TICK_INTERVAL:
            result["tick_sound"] = True
            self.last_sound_time = current_time
        
        return result
    
    def to_nbt_1710(self) -> Dict[str, Any]:
        """Zegar nie ma znaczących danych NBT."""
        return {
            "id": "TileEntityWoodBlocksOne",
            "x": self.x, "y": self.y, "z": self.z
        }


def run_simulation_tests():
    """Uruchamia testy."""
    print("=" * 60)
    print("SYMPULACJA: Kosz na śmieci i Zegar")
    print("=" * 60)
    
    # Test 1: Rubbish Bin
    print("\n[TEST 1] Rubbish Bin (auto-clear co 60s)")
    bin_sim = RubbishBinSimulator("north")
    
    # Dodaj śmieci
    for i in range(10):
        bin_sim.inventory.set_item(i, ItemStack(f"minecraft:trash_{i}", count=i+1))
    
    print(f"  Inventory size: {bin_sim.inventory.get_size()} slots")
    print(f"  Items: {sum(1 for s in bin_sim.inventory.slots if s)}")
    print(f"  Czas do czyszczenia: 60s")
    
    # Symulacja (przyspieszona - ustaw last_clearance na dawno temu)
    bin_sim.last_clearance = int(pytime.time() * 1000) - 61000
    cleared = bin_sim.tick()
    print(f"  Wyczyszczono: {cleared}")
    print(f"  Items po czyszczeniu: {sum(1 for s in bin_sim.inventory.slots if s)}")
    
    # NBT 1.18.2 (tylko 1 slot)
    nbt_1182 = bin_sim.to_nbt_1182()
    print(f"  NBT 1.18.2: {len(nbt_1182.get('Items', []))} items (tylko pierwszy)")
    
    # Test 2: Zegar
    print("\n[TEST 2] Zegar (tick co 2s, dong o 12:00)")
    clock = ClockSimulator("east")
    
    # Test czasu gry
    test_times = [
        0,      # 6:00 rano
        6000,   # 12:00 w południe
        12000,  # 18:00 wieczór
        18000,  # 0:00 północ
    ]
    
    print("  Czas gry:")
    for wt in test_times:
        hour, minute = clock.get_game_time(wt)
        print(f"    WorldTime={wt} -> {hour:02d}:{minute:02d}")
    
    # Test tick
    print("  Symulacja ticków:")
    for i in range(5):
        result = clock.tick(world_time=6000)  # 12:00
        status = []
        if result["tick_sound"]:
            status.append("tick")
        if result["dong_sound"]:
            status.append("DONG!")
        if status:
            print(f"    Tick {i}: {', '.join(status)} ({result['hour']:02d}:{result['minute']:02d})")
        # Symulacja czekania
        clock.last_sound_time = int(pytime.time() * 1000) - 2000
    
    # Test 3: Dong o północy
    print("  Test dong o północy (world_time=18000):")
    clock2 = ClockSimulator()
    clock2.last_sound_time = int(pytime.time() * 1000)
    for i in range(3):
        result = clock2.tick(world_time=18000)  # 0:00
        if result["dong_sound"]:
            print(f"    DONG o północy! ({result['hour']:02d}:{result['minute']:02d})")
    
    print("\n" + "=" * 60)
    print("TESTY ZAKOŃCZONE POMYŚLNIE")
    print("=" * 60)


if __name__ == "__main__":
    run_simulation_tests()
