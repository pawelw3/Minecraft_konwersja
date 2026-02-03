"""
Symulacja funkcjonalności EnderStorage dla wersji 1.7.10 i 1.18.2
Zadanie 2: Symulacja działania przed implementacją konwersji
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple, Any
from enum import Enum
import uuid


class EnumColour(Enum):
    """Kolory dostępne w EnderStorage (1.18.2 style)"""
    WHITE = 0
    ORANGE = 1
    MAGENTA = 2
    LIGHT_BLUE = 3
    YELLOW = 4
    LIME = 5
    PINK = 6
    GRAY = 7
    LIGHT_GRAY = 8
    CYAN = 9
    PURPLE = 10
    BLUE = 11
    BROWN = 12
    GREEN = 13
    RED = 14
    BLACK = 15


@dataclass
class Frequency:
    """
    Reprezentacja częstotliwości w 1.18.2
    Zawiera 3 kolory (lewy, środkowy, prawy) i opcjonalnego właściciela
    """
    left: EnumColour = EnumColour.WHITE
    middle: EnumColour = EnumColour.WHITE
    right: EnumColour = EnumColour.WHITE
    owner: Optional[uuid.UUID] = None
    owner_name: Optional[str] = None  # Dla celów debugowania
    
    def to_int(self) -> int:
        """Konwersja do int (0-4095) jak w 1.7.10"""
        return (self.left.value << 8) | (self.middle.value << 4) | self.right.value
    
    @classmethod
    def from_int(cls, freq_int: int, owner: Optional[uuid.UUID] = None) -> 'Frequency':
        """Tworzy Frequency z int (format 1.7.10)"""
        left = EnumColour((freq_int >> 8) & 0xF)
        middle = EnumColour((freq_int >> 4) & 0xF)
        right = EnumColour(freq_int & 0xF)
        return cls(left=left, middle=middle, right=right, owner=owner)
    
    def get_colours(self) -> Tuple[EnumColour, EnumColour, EnumColour]:
        """Zwraca tuple (left, middle, right)"""
        return (self.left, self.middle, self.right)
    
    def is_global(self) -> bool:
        """Czy to skrzynia/zbiornik globalny (bez właściciela)?"""
        return self.owner is None
    
    def get_storage_key(self) -> str:
        """
        Generuje klucz do storage backend.
        Format 1.18.2: "left,middle,right|owner_uuid" lub "left,middle,right|global"
        """
        colors = f"{self.left.name},{self.middle.name},{self.right.name}"
        if self.owner:
            return f"{colors}|{self.owner}"
        return f"{colors}|global"
    
    def get_legacy_key(self) -> str:
        """
        Generuje klucz w formacie 1.7.10: "freq|owner|type"
        """
        owner_str = "global" if self.owner is None else (self.owner_name or str(self.owner))
        return f"{self.to_int()}|{owner_str}"
    
    def __hash__(self):
        return hash(self.get_storage_key())
    
    def __eq__(self, other):
        if not isinstance(other, Frequency):
            return False
        return (self.left == other.left and 
                self.middle == other.middle and 
                self.right == other.right and
                self.owner == other.owner)


@dataclass
class ItemStack:
    """Symulacja ItemStack (uproszczona)"""
    item_id: str
    count: int = 1
    damage: int = 0  # Dla 1.7.10 compatibility
    nbt: Optional[Dict] = None
    
    def is_empty(self) -> bool:
        """1.18.2: EMPTY zamiast null"""
        return self.count <= 0 or self.item_id == "minecraft:air"
    
    @classmethod
    def empty(cls) -> 'ItemStack':
        """Tworzy pusty ItemStack (1.18.2 style)"""
        return cls(item_id="minecraft:air", count=0)


@dataclass
class FluidStack:
    """Symulacja FluidStack"""
    fluid_id: str
    amount: int  # w mB
    nbt: Optional[Dict] = None
    
    def is_empty(self) -> bool:
        return self.amount <= 0 or self.fluid_id == "empty"
    
    def copy(self) -> 'FluidStack':
        return FluidStack(self.fluid_id, self.amount, self.nbt.copy() if self.nbt else None)


class EnderItemStorage:
    """
    Symulacja backend storage dla skrzyń Ender.
    Wszystkie skrzynie o tej samej Frequency dzielą ten sam EnderItemStorage.
    """
    
    SIZE = 27  # 3x9 slots
    
    def __init__(self, frequency: Frequency):
        self.frequency = frequency
        # 1.7.10: ItemStack[] (null = empty)
        # 1.18.2: ItemStack[] (ItemStack.EMPTY = empty)
        self.items: List[ItemStack] = [ItemStack.empty() for _ in range(self.SIZE)]
        self.num_open = 0  # Licznik otwarć (dla animacji)
        self.change_count = 0  # Wersja do synchronizacji
        
    def get_storage_key(self) -> str:
        return self.frequency.get_storage_key()
    
    def get_item(self, slot: int) -> ItemStack:
        """Pobiera item z slotu"""
        if 0 <= slot < self.SIZE:
            return self.items[slot]
        return ItemStack.empty()
    
    def set_item(self, slot: int, item: ItemStack):
        """Ustawia item w slocie"""
        if 0 <= slot < self.SIZE:
            self.items[slot] = item
            self.change_count += 1
            self.mark_dirty()
    
    def is_empty(self) -> bool:
        """Czy skrzynia jest pusta?"""
        return all(item.is_empty() for item in self.items)
    
    def get_num_open(self) -> int:
        """Liczba graczy aktualnie przeglądających skrzynię"""
        return self.num_open
    
    def open_inventory(self):
        """Gracz otworzył skrzynię"""
        self.num_open += 1
        
    def close_inventory(self):
        """Gracz zamknął skrzynię"""
        self.num_open = max(0, self.num_open - 1)
        
    def mark_dirty(self):
        """Oznacza storage jako zmieniony (do zapisu)"""
        pass  # W rzeczywistości: flaga do zapisu NBT
    
    def to_nbt_1710(self) -> Dict:
        """Serializacja do formatu NBT 1.7.10"""
        items_nbt = []
        for i, item in enumerate(self.items):
            if not item.is_empty():
                items_nbt.append({
                    "Slot": i,
                    "id": item.item_id,
                    "Count": item.count,
                    "Damage": item.damage
                })
        return {
            "Items": items_nbt,
            "freq": self.frequency.to_int(),
            "owner": self.frequency.owner_name or "global"
        }
    
    def to_nbt_1182(self) -> Dict:
        """Serializacja do formatu NBT 1.18.2"""
        items_nbt = []
        for i, item in enumerate(self.items):
            if not item.is_empty():
                item_data = {"Slot": i, "id": item.item_id, "Count": item.count}
                if item.nbt:
                    item_data["tag"] = item.nbt
                items_nbt.append(item_data)
        
        freq_nbt = {
            "left": self.frequency.left.name.lower(),
            "middle": self.frequency.middle.name.lower(),
            "right": self.frequency.right.name.lower()
        }
        if self.frequency.owner:
            freq_nbt["owner"] = str(self.frequency.owner)
            
        return {
            "Items": items_nbt,
            "Frequency": freq_nbt
        }


class EnderLiquidStorage:
    """
    Symulacja backend storage dla zbiorników Ender.
    Pojemność: 16,000 mB
    """
    
    CAPACITY = 16000  # mB
    
    def __init__(self, frequency: Frequency):
        self.frequency = frequency
        self.fluid: Optional[FluidStack] = None
        self.change_count = 0
        
    def get_storage_key(self) -> str:
        return self.frequency.get_storage_key()
    
    def get_capacity(self) -> int:
        return self.CAPACITY
    
    def get_fluid(self) -> Optional[FluidStack]:
        """Pobiera kopię aktualnej cieczy"""
        return self.fluid.copy() if self.fluid else None
    
    def get_fluid_amount(self) -> int:
        return self.fluid.amount if self.fluid else 0
    
    def fill(self, resource: FluidStack, simulate: bool = False) -> int:
        """
        Napełnia zbiornik. Zwraca ilość faktycznie dodaną.
        simulate=True: tylko symulacja, nie modyfikuje
        """
        if resource.is_empty():
            return 0
            
        if self.fluid is None:
            # Pusty zbiornik - możemy dodać dowolną ciecz
            fill_amount = min(resource.amount, self.CAPACITY)
            if not simulate:
                self.fluid = FluidStack(resource.fluid_id, fill_amount, 
                                       resource.nbt.copy() if resource.nbt else None)
                self.change_count += 1
            return fill_amount
        elif self.fluid.fluid_id == resource.fluid_id:
            # Ten sam typ cieczy
            space = self.CAPACITY - self.fluid.amount
            fill_amount = min(resource.amount, space)
            if not simulate and fill_amount > 0:
                self.fluid.amount += fill_amount
                self.change_count += 1
            return fill_amount
        else:
            # Inny typ cieczy - nie możemy mieszać
            return 0
    
    def drain(self, max_drain: int, simulate: bool = False) -> Optional[FluidStack]:
        """
        Opróżnia zbiornik. Zwraca wyciągniętą ciecz.
        """
        if self.fluid is None or max_drain <= 0:
            return None
            
        drain_amount = min(max_drain, self.fluid.amount)
        result = FluidStack(self.fluid.fluid_id, drain_amount,
                           self.fluid.nbt.copy() if self.fluid.nbt else None)
        
        if not simulate:
            self.fluid.amount -= drain_amount
            if self.fluid.amount <= 0:
                self.fluid = None
            self.change_count += 1
            
        return result
    
    def is_empty(self) -> bool:
        return self.fluid is None


class EnderStorageManager:
    """
    Symulacja manager'a storage - singleton zarządzający wszystkimi 
    EnderItemStorage i EnderLiquidStorage.
    
    W Minecraft: osobne instancje dla client/server
    """
    
    def __init__(self, is_client: bool = False):
        self.is_client = is_client
        self.item_storages: Dict[str, EnderItemStorage] = {}
        self.liquid_storages: Dict[str, EnderLiquidStorage] = {}
        
    def get_item_storage(self, frequency: Frequency) -> EnderItemStorage:
        """Pobiera lub tworzy EnderItemStorage dla danej częstotliwości"""
        key = frequency.get_storage_key()
        if key not in self.item_storages:
            self.item_storages[key] = EnderItemStorage(frequency)
        return self.item_storages[key]
    
    def get_liquid_storage(self, frequency: Frequency) -> EnderLiquidStorage:
        """Pobiera lub tworzy EnderLiquidStorage dla danej częstotliwości"""
        key = frequency.get_storage_key()
        if key not in self.liquid_storages:
            self.liquid_storages[key] = EnderLiquidStorage(frequency)
        return self.liquid_storages[key]


@dataclass
class EnderChestBlock:
    """Symulacja bloku EnderChest (TileEnderChest)"""
    frequency: Frequency
    rotation: int = 0  # 0-3 (N/E/S/W)
    
    # Animacja
    lid_angle: float = 0.0
    prev_lid_angle: float = 0.0
    num_open: int = 0
    
    def get_storage(self, manager: EnderStorageManager) -> EnderItemStorage:
        """Pobiera współdzielony storage dla tej skrzyni"""
        return manager.get_item_storage(self.frequency)
    
    def update_animation(self):
        """Aktualizuje animację pokrywy"""
        self.prev_lid_angle = self.lid_angle
        target = 1.0 if self.num_open > 0 else 0.0
        # Liniowe zbliżanie się do targetu
        step = 0.1
        if self.lid_angle < target:
            self.lid_angle = min(self.lid_angle + step, target)
        elif self.lid_angle > target:
            self.lid_angle = max(self.lid_angle - step, target)
    
    def interact(self, player: str, manager: EnderStorageManager) -> bool:
        """Symulacja kliknięcia prawym przyciskiem na skrzynię"""
        storage = self.get_storage(manager)
        
        # Sprawdź własność
        if not self.frequency.is_global():
            # W 1.18.2 sprawdzamy UUID, tu uproszczenie
            pass
            
        storage.open_inventory()
        self.num_open = storage.get_num_open()
        return True
    
    def close(self, manager: EnderStorageManager):
        """Gracz zamyka GUI skrzyni"""
        storage = self.get_storage(manager)
        storage.close_inventory()
        self.num_open = storage.get_num_open()


@dataclass
class EnderTankBlock:
    """Symulacja bloku EnderTank (TileEnderTank)"""
    frequency: Frequency
    
    # Stan ciśnieniowy
    pressure_state: bool = False
    invert_redstone: bool = False
    rotation: float = 0.0
    
    def get_storage(self, manager: EnderStorageManager) -> EnderLiquidStorage:
        """Pobiera współdzielony storage dla tego zbiornika"""
        return manager.get_liquid_storage(self.frequency)
    
    def update_pressure(self, redstone_signal: bool):
        """Aktualizuje stan ciśnieniowy na podstawie sygnału redstone"""
        active = redstone_signal != self.invert_redstone
        self.pressure_state = active
        if active:
            self.rotation += 0.1  # Animacja obrotu
    
    def eject_liquid(self, manager: EnderStorageManager, neighbors: List[Any]) -> int:
        """
        Wyrzuca ciecz do sąsiednich zbiorników.
        Zwraca ilość przeniesionej cieczy.
        """
        if not self.pressure_state:
            return 0
            
        storage = self.get_storage(manager)
        total_ejected = 0
        
        # Symulacja: próbujemy drenować do 100mB do każdego sąsiada
        for neighbor in neighbors:
            if isinstance(neighbor, EnderTankBlock):
                neighbor_storage = neighbor.get_storage(manager)
                
                # Symulacja drenowania
                to_drain = storage.drain(100, simulate=True)
                if to_drain:
                    filled = neighbor_storage.fill(to_drain, simulate=True)
                    if filled > 0:
                        # Wykonaj faktyczne operacje
                        drained = storage.drain(filled, simulate=False)
                        neighbor_storage.fill(drained, simulate=False)
                        total_ejected += filled
                        
        return total_ejected


@dataclass
class EnderPouchItem:
    """Symulacja itemu Ender Pouch"""
    frequency: Frequency
    
    def use(self, player: str, manager: EnderStorageManager) -> bool:
        """Otwiera GUI skrzyni odpowiadającej częstotliwości torby"""
        storage = manager.get_item_storage(self.frequency)
        storage.open_inventory()
        print(f"[{player}] Otwarto Ender Pouch: {self.frequency.get_colours()}")
        return True
    
    def sync_with_chest(self, chest: EnderChestBlock):
        """Shift+klik synchronizuje kolor torby ze skrzynią"""
        self.frequency = chest.frequency


# ============================================================================
# SCENARIUSZE TESTOWE
# ============================================================================

def scenario_1_frequency_system():
    """
    Scenariusz 1: System Frequency i kolorów
    Demonstruje konwersję między int (1.7.10) a Frequency (1.18.2)
    """
    print("=" * 60)
    print("SCENARIUSZ 1: System Frequency i kolorów")
    print("=" * 60)
    
    # Tworzenie frequency z kolorów
    freq = Frequency(
        left=EnumColour.RED,
        middle=EnumColour.GREEN,
        right=EnumColour.BLUE
    )
    
    print(f"\nFrequency z kolorów:")
    print(f"  Left: {freq.left.name} ({freq.left.value})")
    print(f"  Middle: {freq.middle.name} ({freq.middle.value})")
    print(f"  Right: {freq.right.name} ({freq.right.value})")
    print(f"  Int value (1.7.10 style): {freq.to_int()}")
    print(f"  Storage key: {freq.get_storage_key()}")
    
    # Konwersja do int i z powrotem
    freq_int = freq.to_int()
    freq_restored = Frequency.from_int(freq_int)
    print(f"\nKonwersja int -> Frequency:")
    print(f"  Oryginal: {freq.get_colours()}")
    print(f"  Po konwersji: {freq_restored.get_colours()}")
    print(f"  Zgodność: {freq == freq_restored}")
    
    # Wszystkie możliwe kombinacje
    print(f"\nLiczba możliwych kombinacji kolorów: 16^3 = {16**3}")
    
    # Personal vs Global
    player_uuid = uuid.uuid4()
    personal_freq = Frequency(
        left=EnumColour.WHITE,
        middle=EnumColour.WHITE,
        right=EnumColour.WHITE,
        owner=player_uuid,
        owner_name="Player123"
    )
    print(f"\nPersonal frequency:")
    print(f"  Is global: {personal_freq.is_global()}")
    print(f"  Owner: {personal_freq.owner}")
    print(f"  Storage key: {personal_freq.get_storage_key()}")
    
    # Porównanie kluczy storage
    global_white = Frequency(EnumColour.WHITE, EnumColour.WHITE, EnumColour.WHITE)
    print(f"\nPorównanie storage keys:")
    print(f"  Global WHITE: {global_white.get_storage_key()}")
    print(f"  Personal WHITE: {personal_freq.get_storage_key()}")
    print(f"  Te same? {global_white.get_storage_key() == personal_freq.get_storage_key()}")


def scenario_2_shared_inventory():
    """
    Scenariusz 2: Współdzielenie inventory między skrzyniami
    Demonstruje, że skrzynie o tej samej frequency dzielą storage
    """
    print("\n" + "=" * 60)
    print("SCENARIUSZ 2: Współdzielenie inventory")
    print("=" * 60)
    
    manager = EnderStorageManager()
    
    # Tworzymy dwie skrzynie o tej samej częstotliwości (RED-GREEN-BLUE)
    freq_rgb = Frequency(EnumColour.RED, EnumColour.GREEN, EnumColour.BLUE)
    chest1 = EnderChestBlock(frequency=freq_rgb, rotation=0)
    chest2 = EnderChestBlock(frequency=freq_rgb, rotation=2)
    
    # Tworzymy trzecią skrzynię o innej częstotliwości (WHITE-WHITE-WHITE)
    chest3 = EnderChestBlock(
        frequency=Frequency(EnumColour.WHITE, EnumColour.WHITE, EnumColour.WHITE),
        rotation=1
    )
    
    print(f"\nUtworzono 3 skrzynie:")
    print(f"  Chest 1: {chest1.frequency.get_colours()} @ rot={chest1.rotation}")
    print(f"  Chest 2: {chest2.frequency.get_colours()} @ rot={chest2.rotation}")
    print(f"  Chest 3: {chest3.frequency.get_colours()} @ rot={chest3.rotation}")
    
    # Pobieramy storage
    storage1 = chest1.get_storage(manager)
    storage2 = chest2.get_storage(manager)
    storage3 = chest3.get_storage(manager)
    
    print(f"\nStorage comparison:")
    print(f"  Chest 1 storage == Chest 2 storage: {storage1 is storage2}")
    print(f"  Chest 1 storage == Chest 3 storage: {storage1 is storage3}")
    
    # Dodajemy item przez pierwszą skrzynię
    diamond = ItemStack(item_id="minecraft:diamond", count=64)
    storage1.set_item(0, diamond)
    
    print(f"\nDodano do Chest 1 slot 0: {diamond.item_id} x{diamond.count}")
    
    # Sprawdzamy czy widać w drugiej skrzyni
    item_in_chest2 = storage2.get_item(0)
    print(f"  Chest 2 slot 0: {item_in_chest2.item_id} x{item_in_chest2.count}")
    
    # Sprawdzamy trzecią skrzynię (inna frequency = inny storage)
    item_in_chest3 = storage3.get_item(0)
    print(f"  Chest 3 slot 0: {'pusty' if item_in_chest3.is_empty() else item_in_chest3.item_id}")
    
    # Torba - dostęp do tego samego storage
    pouch = EnderPouchItem(frequency=freq_rgb)
    pouch_storage = manager.get_item_storage(pouch.frequency)
    
    print(f"\nEnder Pouch z tymi samymi kolorami:")
    print(f"  Pouch storage == Chest 1 storage: {pouch_storage is storage1}")
    
    # Dodajemy item przez torbę
    iron = ItemStack(item_id="minecraft:iron_ingot", count=32)
    pouch_storage.set_item(1, iron)
    print(f"  Dodano przez torbę slot 1: {iron.item_id} x{iron.count}")
    print(f"  Widać w Chest 1 slot 1: {storage1.get_item(1).item_id} x{storage1.get_item(1).count}")
    
    # Animacja otwierania
    print(f"\nSymulacja animacji:")
    chest1.interact("Player1", manager)
    for i in range(15):
        chest1.update_animation()
        if i % 5 == 0:
            print(f"  Frame {i}: lid_angle = {chest1.lid_angle:.2f}")
    
    chest1.close(manager)
    print(f"  Po zamknięciu:")
    for i in range(15):
        chest1.update_animation()
        if i % 5 == 0:
            print(f"  Frame {i}: lid_angle = {chest1.lid_angle:.2f}")


def scenario_3_liquid_transfer():
    """
    Scenariusz 3: Transfer cieczy w zbiornikach
    Demonstruje działanie EnderTank i systemu ciśnieniowego
    """
    print("\n" + "=" * 60)
    print("SCENARIUSZ 3: Transfer cieczy w zbiornikach")
    print("=" * 60)
    
    manager = EnderStorageManager()
    
    # Tworzymy dwa zbiorniki o tej samej częstotliwości
    freq_water = Frequency(EnumColour.BLUE, EnumColour.BLUE, EnumColour.BLUE)
    tank1 = EnderTankBlock(frequency=freq_water)
    tank2 = EnderTankBlock(frequency=freq_water)
    
    # Trzeci zbiornik o innej częstotliwości (używamy pomarańczowego jak lava)
    tank3 = EnderTankBlock(
        frequency=Frequency(EnumColour.ORANGE, EnumColour.ORANGE, EnumColour.ORANGE)
    )
    
    print(f"\nUtworzono 3 zbiorniki:")
    print(f"  Tank 1 (Water): {tank1.frequency.get_colours()}")
    print(f"  Tank 2 (Water): {tank2.frequency.get_colours()}")
    print(f"  Tank 3 (Lava): {tank3.frequency.get_colours()}")
    
    # Napełniamy pierwszy zbiornik
    storage1 = tank1.get_storage(manager)
    water = FluidStack("minecraft:water", 10000)
    filled = storage1.fill(water)
    print(f"\nNapełniono Tank 1 wodą: {filled}mB / {storage1.CAPACITY}mB")
    
    # Sprawdzamy drugi zbiornik (ta sama frequency)
    storage2 = tank2.get_storage(manager)
    print(f"  Tank 2 (ta sama freq): {storage2.get_fluid_amount()}mB")
    
    # Sprawdzamy trzeci zbiornik (inna frequency)
    storage3 = tank3.get_storage(manager)
    print(f"  Tank 3 (inna freq): {storage3.get_fluid_amount()}mB")
    
    # System ciśnieniowy - tank1 wyrzuca do tank2
    print(f"\nSystem ciśnieniowy:")
    print(f"  Przed ejekcją: Tank 1 = {storage1.get_fluid_amount()}mB")
    
    # Aktywujemy ciśnienie w tank1
    tank1.update_pressure(redstone_signal=True)
    print(f"  Pressure state tank1: {tank1.pressure_state}")
    
    # Symulujemy ejekcję
    ejected = tank1.eject_liquid(manager, [tank2])
    print(f"  Wyrzucono do sąsiadów: {ejected}mB")
    print(f"  Po ejekcji: Tank 1 = {storage1.get_fluid_amount()}mB")
    
    # Test drain
    print(f"\nTest drain:")
    drained = storage1.drain(500)
    print(f"  Wyciągnięto: {drained.amount}mB {drained.fluid_id}")
    print(f"  Pozostało: {storage1.get_fluid_amount()}mB")
    
    # Test napełniania - próba mieszania cieczy
    print(f"\nTest mieszania cieczy:")
    lava = FluidStack("minecraft:lava", 5000)
    fill_result = storage1.fill(lava)
    print(f"  Próba dodania lawy do wody: {fill_result}mB (powinno być 0)")
    
    # Inny zbiornik może mieć lawę
    lava_storage = tank3.get_storage(manager)
    lava_fill = lava_storage.fill(lava)
    print(f"  Dodanie lawy do pustego zbiornika: {lava_fill}mB")


def scenario_4_nbt_conversion():
    """
    Scenariusz 4: Konwersja NBT między wersjami
    Demonstruje jak wyglądają dane w 1.7.10 vs 1.18.2
    """
    print("\n" + "=" * 60)
    print("SCENARIUSZ 4: Konwersja NBT")
    print("=" * 60)
    
    manager = EnderStorageManager()
    
    # Tworzymy skrzynię z zawartością
    freq = Frequency(EnumColour.YELLOW, EnumColour.PURPLE, EnumColour.CYAN)
    chest = EnderChestBlock(frequency=freq, rotation=2)
    storage = chest.get_storage(manager)
    
    # Dodajemy różne itemy
    storage.set_item(0, ItemStack("minecraft:diamond", 32))
    storage.set_item(5, ItemStack("minecraft:gold_ingot", 16))
    storage.set_item(13, ItemStack("minecraft:iron_pickaxe", 1, damage=15))
    
    print(f"\nSkrzynia z częstotliwością: {freq.get_colours()}")
    print(f"  Zawartość: {sum(1 for i in storage.items if not i.is_empty())} slot(y) zajęte")
    
    # Format 1.7.10
    nbt_1710 = storage.to_nbt_1710()
    print(f"\nFormat NBT 1.7.10:")
    print(f"  freq: {nbt_1710['freq']} (int)")
    print(f"  owner: {nbt_1710['owner']}")
    print(f"  Items: {len(nbt_1710['Items'])} elementów")
    for item in nbt_1710['Items'][:3]:
        print(f"    Slot {item['Slot']}: {item['id']} x{item['Count']} (damage: {item.get('Damage', 0)})")
    
    # Format 1.18.2
    nbt_1182 = storage.to_nbt_1182()
    print(f"\nFormat NBT 1.18.2:")
    print(f"  Frequency: {nbt_1182['Frequency']}")
    print(f"  Items: {len(nbt_1182['Items'])} elementów")
    
    # Konwersja TileEnderChest 1.7.10 -> 1.18.2
    print(f"\nKonwersja TileEnderChest:")
    print(f"  1.7.10 -> freq={freq.to_int()}, owner='global'")
    print(f"  1.18.2 -> left={freq.left.name}, middle={freq.middle.name}, right={freq.right.name}")
    print(f"         -> owner=null (global)")
    
    # Konwersja personal
    player_uuid = uuid.uuid4()
    personal_freq = Frequency(
        EnumColour.RED, EnumColour.RED, EnumColour.RED,
        owner=player_uuid,
        owner_name="TestPlayer"
    )
    print(f"\nKonwersja personal:")
    print(f"  1.7.10 -> freq={personal_freq.to_int()}, owner='{personal_freq.owner_name}'")
    print(f"  1.18.2 -> owner={personal_freq.owner} (UUID)")


def scenario_5_edge_cases():
    """
    Scenariusz 5: Edge cases i graniczne przypadki
    """
    print("\n" + "=" * 60)
    print("SCENARIUSZ 5: Edge cases")
    print("=" * 60)
    
    manager = EnderStorageManager()
    
    # Pusta skrzynia
    print(f"\n1. Pusta skrzynia:")
    empty_freq = Frequency(EnumColour.BLACK, EnumColour.BLACK, EnumColour.BLACK)
    empty_chest = EnderChestBlock(frequency=empty_freq)
    empty_storage = empty_chest.get_storage(manager)
    print(f"   Is empty: {empty_storage.is_empty()}")
    print(f"   Storage key: {empty_freq.get_storage_key()}")
    
    # Pełny zbiornik
    print(f"\n2. Pełny zbiornik:")
    full_freq = Frequency(EnumColour.WHITE, EnumColour.ORANGE, EnumColour.MAGENTA)
    full_tank = EnderTankBlock(frequency=full_freq)
    full_storage = full_tank.get_storage(manager)
    full_storage.fill(FluidStack("minecraft:water", 20000))  # Przekracza pojemność
    print(f"   Pojemność: {full_storage.CAPACITY}mB")
    print(f"   Wypełniono: {full_storage.get_fluid_amount()}mB")
    print(f"   Próba dodania więcej: {full_storage.fill(FluidStack('minecraft:water', 1000))}mB")
    
    # Wiele graczy otwiera tę samą skrzynię
    print(f"\n3. Wielu graczy otwiera skrzynię:")
    multi_freq = Frequency(EnumColour.GREEN, EnumColour.GREEN, EnumColour.GREEN)
    multi_chest = EnderChestBlock(frequency=multi_freq)
    multi_storage = multi_chest.get_storage(manager)
    
    for player in ["Player1", "Player2", "Player3"]:
        multi_chest.interact(player, manager)
        print(f"   {player} otwiera -> num_open = {multi_storage.get_num_open()}")
    
    for player in ["Player1", "Player2", "Player3"]:
        multi_chest.close(manager)
        print(f"   {player} zamyka -> num_open = {multi_storage.get_num_open()}")
    
    # Maksymalna liczba otwarć i animacja
    print(f"\n4. Animacja przy wielu otwarciach:")
    multi_chest.interact("P1", manager)
    multi_chest.interact("P2", manager)
    multi_chest.update_animation()
    print(f"   2 otwarcia -> lid_angle = {multi_chest.lid_angle}")
    multi_chest.close(manager)
    multi_chest.update_animation()
    print(f"   1 zamknięcie (1 pozostaje) -> lid_angle = {multi_chest.lid_angle}")
    multi_chest.close(manager)
    for _ in range(20):
        multi_chest.update_animation()
    print(f"   Po zamknięciu wszystkich -> lid_angle = {multi_chest.lid_angle:.2f}")
    
    # Wszystkie możliwe kolory
    print(f"\n5. Wszystkie kolory:")
    print(f"   Dostępne kolory: {len(EnumColour)}")
    print(f"   Nazwy: {[c.name for c in EnumColour][:5]}... (pierwsze 5)")


def run_all_scenarios():
    """Uruchamia wszystkie scenariusze testowe"""
    print("\n" + "=" * 60)
    print("SYMULACJA ENDERSTORAGE - ZADANIE 2")
    print("=" * 60)
    
    scenario_1_frequency_system()
    scenario_2_shared_inventory()
    scenario_3_liquid_transfer()
    scenario_4_nbt_conversion()
    scenario_5_edge_cases()
    
    print("\n" + "=" * 60)
    print("WSZYSTKIE SCENARIUSZE ZAKOŃCZONE")
    print("=" * 60)


if __name__ == "__main__":
    run_all_scenarios()
