"""
Autocrafting Simulation - AE2 1.7.10 vs 1.18.2

Symulacja systemu autocraftingu AE2:
- Crafting CPU (obliczanie crafting)
- Patterns (wzorce receptur)
- Molecular Assembler (wykonywanie)
- Crafting Storage (pamięć dla CPU)

Bazuje na kodzie źródłowym:
- 1.7.10: appeng.tile.crafting.*, appeng.helpers.CraftingPattern
- 1.18.2: appeng.blockentity.crafting.*, appeng.crafting.CraftingPlan
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict


# =============================================================================
# TYPY I STAŁE
# =============================================================================

class CraftingStatus(enum.Enum):
    """Status zadania crafting"""
    PENDING = "pending"           # Oczekuje
    CALCULATING = "calculating"   # Obliczanie planu
    CRAFTING = "crafting"         # W trakcie
    COMPLETED = "completed"       # Zakończone
    CANCELLED = "cancelled"       # Anulowane
    ERROR = "error"               # Błąd


# =============================================================================
# SYMULACJA 1.7.10
# =============================================================================

@dataclass
class ItemStack1710:
    """Item stack dla symulacji"""
    item_id: str
    count: int = 1
    metadata: int = 0


@dataclass
class CraftingPattern1710:
    """
    Wzorzec craftingu w 1.7.10.
    Odpowiada: appeng.helpers.CraftingPattern
    
    Pattern przechowuje:
    - Wejścia (input) - co jest potrzebne
    - Wyjścia (output) - co powstaje
    - Czy to crafting czy processing
    """
    pattern_id: str
    inputs: List[ItemStack1710] = field(default_factory=list)
    outputs: List[ItemStack1710] = field(default_factory=list)
    is_crafting: bool = True  # True=crafting table, False=processing
    
    # W 1.7.10 pattern jest przechowywany jako ItemStack (Encoded Pattern)
    encoded_item: Optional[ItemStack1710] = None
    
    def can_craft(self, available_items: Dict[str, int]) -> bool:
        """Sprawdza czy pattern może być wykonany"""
        for input_item in self.inputs:
            key = f"{input_item.item_id}:{input_item.metadata}"
            if available_items.get(key, 0) < input_item.count:
                return False
        return True
    
    def to_nbt(self) -> Dict:
        """Serializacja pattern do NBT"""
        return {
            'in': [{'id': i.item_id, 'Damage': i.metadata, 'Count': i.count} for i in self.inputs],
            'out': [{'id': o.item_id, 'Damage': o.metadata, 'Count': o.count} for o in self.outputs],
            'crafting': self.is_crafting
        }


@dataclass
class CraftingTask1710:
    """
    Zadanie craftingu w 1.7.10.
    Odpowiada: appeng.crafting.CraftingJob (uproszczone)
    """
    task_id: str
    pattern: CraftingPattern1710
    requested_amount: int
    status: CraftingStatus = CraftingStatus.PENDING
    
    # Progress
    completed_amount: int = 0
    remaining_inputs: Dict[str, int] = field(default_factory=dict)
    
    def calculate_plan(self, network_storage: Dict[str, int]) -> bool:
        """
        Oblicza plan craftingu.
        Sprawdza czy są dostępne składniki.
        """
        self.status = CraftingStatus.CALCULATING
        
        # Sprawdź czy pattern może być wykonany
        if not self.pattern.can_craft(network_storage):
            self.status = CraftingStatus.ERROR
            return False
        
        # Oblicz ile razy można wykonać pattern
        times = self.requested_amount // self.pattern.outputs[0].count
        
        # Przygotuj listę potrzebnych składników
        for input_item in self.pattern.inputs:
            key = f"{input_item.item_id}:{input_item.metadata}"
            self.remaining_inputs[key] = input_item.count * times
        
        self.status = CraftingStatus.CRAFTING
        return True
    
    def tick(self) -> bool:
        """
        Symuluje jeden tick craftingu.
        Zwraca True jeśli zadanie jest aktywne.
        """
        if self.status != CraftingStatus.CRAFTING:
            return False
        
        # Symulacja postępu
        self.completed_amount += 1
        
        if self.completed_amount >= self.requested_amount:
            self.status = CraftingStatus.COMPLETED
            return False
        
        return True


@dataclass
class CraftingCPU1710:
    """
    CPU craftingu w 1.7.10.
    Odpowiada: appeng.tile.crafting.TileCraftingTile
    
    CPU składa się z:
    - Crafting Unit (podstawowa jednostka)
    - Crafting Storage (pamięć - 1k, 4k, 16k, 64k)
    - Crafting Co-Processing Unit (przyspieszenie)
    - Crafting Monitor (wyświetlanie)
    """
    cpu_id: str
    storage_size: int = 1024  # Bajty pamięci
    co_processors: int = 0    # Liczba akceleratorów
    
    active_tasks: List[CraftingTask1710] = field(default_factory=list)
    pending_tasks: List[CraftingTask1710] = field(default_factory=list)
    
    def can_accept_task(self, task: CraftingTask1710) -> bool:
        """Sprawdza czy CPU może przyjąć zadanie"""
        # Sprawdź czy jest miejsce w pamięci
        used_memory = sum(t.requested_amount * 8 for t in self.active_tasks)  # ~8 bajtów na item
        task_memory = task.requested_amount * 8
        
        return (used_memory + task_memory) <= self.storage_size
    
    def submit_task(self, task: CraftingTask1710, network_storage: Dict[str, int]) -> bool:
        """Zleca zadanie do wykonania"""
        if not self.can_accept_task(task):
            return False
        
        if task.calculate_plan(network_storage):
            self.active_tasks.append(task)
            return True
        
        self.pending_tasks.append(task)
        return False
    
    def tick(self) -> None:
        """Jeden tick CPU - wykonuje aktywne zadania"""
        # W 1.7.10 CPU może wykonywać równolegle zadania równolegle do liczby co-processors
        max_parallel = self.co_processors + 1
        
        active_count = 0
        for task in self.active_tasks:
            if task.status == CraftingStatus.CRAFTING:
                if active_count < max_parallel:
                    task.tick()
                    active_count += 1
        
        # Usuń zakończone zadania
        self.active_tasks = [t for t in self.active_tasks if t.status == CraftingStatus.CRAFTING]
    
    def get_status(self) -> Dict:
        """Zwraca status CPU"""
        return {
            'storage_size': self.storage_size,
            'co_processors': self.co_processors,
            'active_tasks': len(self.active_tasks),
            'pending_tasks': len(self.pending_tasks),
            'used_memory': sum(t.requested_amount * 8 for t in self.active_tasks)
        }


class MolecularAssembler1710:
    """
    Molecular Assembler w 1.7.10.
    Wykonuje faktyczny crafting (w crafting table).
    
    Odpowiada: appeng.tile.crafting.TileMolecularAssembler
    """
    def __init__(self):
        self.active_pattern: Optional[CraftingPattern1710] = None
        self.progress: int = 0
        self.crafting_time: int = 10  # Ticks na crafting
    
    def start_crafting(self, pattern: CraftingPattern1710) -> bool:
        """Rozpoczyna craftingu patternu"""
        if self.active_pattern is not None:
            return False
        
        self.active_pattern = pattern
        self.progress = 0
        return True
    
    def tick(self) -> Optional[List[ItemStack1710]]:
        """
        Jeden tick assemblera.
        Zwraca output gdy crafting zakończony.
        """
        if self.active_pattern is None:
            return None
        
        self.progress += 1
        
        if self.progress >= self.crafting_time:
            result = self.active_pattern.outputs.copy()
            self.active_pattern = None
            self.progress = 0
            return result
        
        return None


# =============================================================================
# SYMULACJA 1.18.2
# =============================================================================

@dataclass
class ItemStack1182:
    """Item stack dla symulacji 1.18.2"""
    item_id: str
    count: int = 1
    # W 1.18.2 nie ma metadata - zastąpione przez NBT


@dataclass
class CraftingPattern1182:
    """
    Wzorzec craftingu w 1.18.2.
    Odpowiada: appeng.crafting.pattern.EncodedPattern
    
    GŁÓWNE ZMIANY vs 1.7.10:
    - Pattern Provider (nowy blok) dostarcza patterny
    - Lepsza obsługa substytucji
    - Wsparcie dla Processing Pattern
    """
    pattern_id: str
    inputs: List[ItemStack1182] = field(default_factory=list)
    outputs: List[ItemStack1182] = field(default_factory=list)
    is_crafting: bool = True
    
    # Nowość w 1.18.2 - substytucje
    allow_substitutions: bool = False
    
    # Nowość w 1.18.2 - Pattern Provider reference
    pattern_provider_id: Optional[str] = None
    
    def can_craft(self, available_items: Dict[str, int]) -> bool:
        """Sprawdza czy pattern może być wykonany"""
        for input_item in self.inputs:
            # W 1.18.2 obsługa substytucji
            if self.allow_substitutions:
                # Sprawdź czy jest jakikolwiek odpowiednik (simplified)
                if available_items.get(input_item.item_id, 0) < input_item.count:
                    return False
            else:
                if available_items.get(input_item.item_id, 0) < input_item.count:
                    return False
        return True
    
    def to_nbt(self) -> Dict:
        """Serializacja pattern do NBT 1.18.2"""
        nbt = {
            'input': [{'#c': i.item_id, 'count': i.count} for i in self.inputs],
            'output': [{'#c': o.item_id, 'count': o.count} for o in self.outputs],
            'crafting': self.is_crafting,
            'substitute': self.allow_substitutions
        }
        if self.pattern_provider_id:
            nbt['provider'] = self.pattern_provider_id
        return nbt


@dataclass
class CraftingPlan1182:
    """
    Plan craftingu w 1.18.2.
    Odpowiada: appeng.crafting.CraftingPlan
    
    Nowość w 1.18.2 - oddzielenie planu od wykonania.
    Plan jest tworzony przed rozpoczęciem craftingu.
    """
    plan_id: str
    final_output: ItemStack1182
    required_items: Dict[str, int] = field(default_factory=dict)
    missing_items: Dict[str, int] = field(default_factory=dict)
    to_craft: List[Tuple[str, int]] = field(default_factory=list)  # (pattern_id, count)
    
    def is_possible(self) -> bool:
        """Sprawdza czy plan jest wykonalny"""
        return len(self.missing_items) == 0
    
    def to_nbt(self) -> Dict:
        return {
            'output': {'id': self.final_output.item_id, 'count': self.final_output.count},
            'required': self.required_items,
            'missing': self.missing_items,
            'toCraft': self.to_craft
        }


@dataclass
class CraftingTask1182:
    """
    Zadanie craftingu w 1.18.2.
    Używa CraftingPlan zamiast obliczać na bieżąco.
    """
    task_id: str
    plan: CraftingPlan1182
    status: CraftingStatus = CraftingStatus.PENDING
    
    completed_patterns: int = 0
    total_patterns: int = 0
    
    def start(self) -> bool:
        """Rozpoczyna wykonanie planu"""
        if not self.plan.is_possible():
            self.status = CraftingStatus.ERROR
            return False
        
        self.total_patterns = len(self.plan.to_craft)
        self.status = CraftingStatus.CRAFTING
        return True
    
    def tick(self) -> bool:
        """Jeden tick zadania"""
        if self.status != CraftingStatus.CRAFTING:
            return False
        
        self.completed_patterns += 1
        
        if self.completed_patterns >= self.total_patterns:
            self.status = CraftingStatus.COMPLETED
            return False
        
        return True
    
    def get_progress(self) -> float:
        """Zwraca postęp w procentach"""
        if self.total_patterns == 0:
            return 100.0
        return (self.completed_patterns / self.total_patterns) * 100


@dataclass
class CraftingCPU1182:
    """
    CPU craftingu w 1.18.2.
    Odpowiada: appeng.blockentity.crafting.CraftingBlockEntity
    
    GŁÓWNE ZMIANY vs 1.7.10:
    - Crafting Accelerator zamiast Co-Processing Unit
    - Lepsza obsługa wielu zadań
    - Pattern Provider dla wzorców
    """
    cpu_id: str
    storage_size: int = 1024
    accelerators: int = 0  # Zamiast co-processors
    
    active_tasks: List[CraftingTask1182] = field(default_factory=list)
    completed_tasks: List[CraftingTask1182] = field(default_factory=list)
    
    # Nowość w 1.18.2 - crafting storage unit type
    unit_type: str = "1k"  # 1k, 4k, 16k, 64k, 256k
    
    def can_accept_job(self, plan: CraftingPlan1182) -> bool:
        """Sprawdza czy CPU może przyjąć zadanie"""
        used_memory = sum(t.plan.required_items.get('bytes', 0) for t in self.active_tasks)
        task_memory = sum(plan.required_items.values()) * 8
        
        return (used_memory + task_memory) <= self.storage_size
    
    def submit_job(self, plan: CraftingPlan1182) -> Optional[CraftingTask1182]:
        """Zleca nowe zadanie craftingu"""
        if not self.can_accept_job(plan):
            return None
        
        task = CraftingTask1182(
            task_id=f"task_{len(self.active_tasks)}",
            plan=plan
        )
        
        if task.start():
            self.active_tasks.append(task)
            return task
        
        return None
    
    def tick(self) -> None:
        """Jeden tick CPU"""
        # W 1.18.2 accelerator zwiększa prędkość
        speed_multiplier = self.accelerators + 1
        
        for task in self.active_tasks:
            if task.status == CraftingStatus.CRAFTING:
                # Symulacja przyspieszenia
                for _ in range(speed_multiplier):
                    if not task.tick():
                        break
        
        # Przenieś zakończone
        completed = [t for t in self.active_tasks if t.status == CraftingStatus.COMPLETED]
        self.completed_tasks.extend(completed)
        self.active_tasks = [t for t in self.active_tasks if t.status == CraftingStatus.CRAFTING]
    
    def get_status(self) -> Dict:
        return {
            'unit_type': self.unit_type,
            'storage_size': self.storage_size,
            'accelerators': self.accelerators,
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'progress': [t.get_progress() for t in self.active_tasks]
        }


class MolecularAssembler1182:
    """
    Molecular Assembler w 1.18.2.
    
    GŁÓWNE ZMIANY:
    - Współpraca z Pattern Provider
    - Lepsza obsługa fluix
    """
    def __init__(self):
        self.active_pattern: Optional[CraftingPattern1182] = None
        self.progress: int = 0
        self.crafting_time: int = 10
        self.pattern_provider: Optional[str] = None  # Ref do Pattern Provider
    
    def start_crafting(self, pattern: CraftingPattern1182, provider_id: str) -> bool:
        """Rozpoczyna crafting z pattern od Pattern Provider"""
        if self.active_pattern is not None:
            return False
        
        self.active_pattern = pattern
        self.pattern_provider = provider_id
        self.progress = 0
        return True
    
    def tick(self) -> Optional[List[ItemStack1182]]:
        """Jeden tick assemblera"""
        if self.active_pattern is None:
            return None
        
        self.progress += 1
        
        if self.progress >= self.crafting_time:
            result = self.active_pattern.outputs.copy()
            self.active_pattern = None
            self.pattern_provider = None
            self.progress = 0
            return result
        
        return None


# =============================================================================
# PORÓWNANIE I KONWERSJA
# =============================================================================

def compare_cpu_architectures():
    """Porównuje architekturę CPU między wersjami"""
    print("="*60)
    print("PORÓWNANIE ARCHITEKTURY CRAFTING CPU")
    print("="*60)
    
    print("\n1.7.10:")
    print("  - Crafting Unit (podstawowa)")
    print("  - Crafting Co-Processing Unit (przyspieszenie)")
    print("  - Crafting Storage 1k/4k/16k/64k")
    print("  - Crafting Monitor")
    print("  - Pattern w Interface")
    
    print("\n1.18.2:")
    print("  - Crafting Unit (podstawowa)")
    print("  - Crafting Accelerator (przyspieszenie)")
    print("  - Crafting Unit 1k/4k/16k/64k/256k")
    print("  - Crafting Monitor")
    print("  - Pattern Provider (NOWOŚĆ!)")
    
    print("\nKLUCZOWE RÓŻNICE:")
    print("1. Co-Processing Unit → Crafting Accelerator (zmiana nazwy)")
    print("2. Dodano 256k storage")
    print("3. Pattern Provider - osobny blok dla patternów")
    print("4. Interface nie przechowuje już patternów do craftingu")
    print("5. Lepszy system planowania (CraftingPlan)")


def simulate_crafting_1710():
    """Symulacja craftingu w 1.7.10"""
    print("\n" + "="*60)
    print("SYMULACJA CRAFTINGU 1.7.10")
    print("="*60)
    
    # Utwórz CPU
    cpu = CraftingCPU1710(
        cpu_id="cpu1",
        storage_size=4096,  # 4k
        co_processors=1
    )
    
    # Utwórz pattern (Stone Pickaxe)
    pattern = CraftingPattern1710(
        pattern_id="pickaxe",
        inputs=[
            ItemStack1710("minecraft:cobblestone", 3),
            ItemStack1710("minecraft:stick", 2),
        ],
        outputs=[ItemStack1710("minecraft:stone_pickaxe", 1)],
        is_crafting=True
    )
    
    # Symulacja storage
    network_storage = {
        "minecraft:cobblestone:0": 64,
        "minecraft:stick:0": 32,
    }
    
    # Zleć zadanie
    task = CraftingTask1710(
        task_id="task1",
        pattern=pattern,
        requested_amount=1
    )
    
    print(f"\nZadanie: Craft 1x {pattern.outputs[0].item_id}")
    print(f"Wymagane: {[(i.item_id, i.count) for i in pattern.inputs]}")
    
    if cpu.submit_task(task, network_storage):
        print("✓ Zadanie przyjęte przez CPU")
        
        # Symulacja ticków
        for tick in range(20):
            cpu.tick()
            if task.status == CraftingStatus.COMPLETED:
                print(f"✓ Crafting zakończony po {tick+1} tickach")
                break
    else:
        print("✗ Nie udało się przyjąć zadania")
    
    print(f"\nStatus CPU: {cpu.get_status()}")


def simulate_crafting_1182():
    """Symulacja craftingu w 1.18.2"""
    print("\n" + "="*60)
    print("SYMULACJA CRAFTINGU 1.18.2")
    print("="*60)
    
    # Utwórz CPU
    cpu = CraftingCPU1182(
        cpu_id="cpu1",
        storage_size=4096,
        accelerators=1,
        unit_type="4k"
    )
    
    # Utwórz pattern
    pattern = CraftingPattern1182(
        pattern_id="pickaxe",
        inputs=[
            ItemStack1182("minecraft:cobblestone", 3),
            ItemStack1182("minecraft:stick", 2),
        ],
        outputs=[ItemStack1182("minecraft:stone_pickaxe", 1)],
        is_crafting=True,
        pattern_provider_id="provider1"  # NOWOŚĆ
    )
    
    # Utwórz plan (NOWOŚĆ w 1.18.2)
    plan = CraftingPlan1182(
        plan_id="plan1",
        final_output=ItemStack1182("minecraft:stone_pickaxe", 1),
        required_items={
            "minecraft:cobblestone": 3,
            "minecraft:stick": 2
        },
        to_craft=[("pickaxe", 1)]
    )
    
    print(f"\nPlan: Craft 1x {plan.final_output.item_id}")
    print(f"Wymagane: {plan.required_items}")
    print(f"Możliwy: {plan.is_possible()}")
    
    # Zleć zadanie
    task = cpu.submit_job(plan)
    
    if task:
        print(f"✓ Zadanie przyjęte (Task ID: {task.task_id})")
        
        # Symulacja ticków
        for tick in range(20):
            cpu.tick()
            if task.status == CraftingStatus.COMPLETED:
                print(f"✓ Crafting zakończony po {tick+1} tickach")
                print(f"  Postęp: {task.get_progress():.1f}%")
                break
    else:
        print("✗ Nie udało się przyjąć zadania")
    
    print(f"\nStatus CPU: {cpu.get_status()}")


def demonstrate_pattern_provider():
    """Demonstracja Pattern Provider (tylko 1.18.2)"""
    print("\n" + "="*60)
    print("DEMONSTRACJA: Pattern Provider (1.18.2)")
    print("="*60)
    
    print("""
Pattern Provider to NOWOŚĆ w 1.18.2!

W 1.7.10:
  - Interface przechowywał patterny
  - Interface + Molecular Assembler = autocrafting
  - Patterny w Interface = storage + crafting

W 1.18.2:
  - Pattern Provider przechowuje patterny dla craftingu
  - Interface = tylko storage (9 slotów)
  - Pattern Provider = tylko patterny (9 slotów)
  - Molecular Assembler pobiera patterny z Pattern Provider

Konwersja 1.7.10 → 1.18.2:
  - Patterny z Interface → Pattern Provider
  - Interface bez patternów → zwykły Interface
    """)


def main():
    """Główna funkcja demonstracyjna"""
    print("="*60)
    print("AUTOCRAFTING SIMULATION - AE2 1.7.10 vs 1.18.2")
    print("="*60)
    
    compare_cpu_architectures()
    simulate_crafting_1710()
    simulate_crafting_1182()
    demonstrate_pattern_provider()
    
    print("\n" + "="*60)
    print("SYMULACJA ZAKOŃCZONA POMYŚLNIE")
    print("="*60)
    print("\nWnioski dla konwersji:")
    print("1. Interface z patternami (1.7.10) → Interface + Pattern Provider (1.18.2)")
    print("2. Crafting Co-Processing Unit → Crafting Accelerator")
    print("3. Dodano Crafting Unit 256k (1.18.2)")
    print("4. System planowania bardziej zaawansowany w 1.18.2")
    print("5. Pattern Provider wymaga osobnego bloku!")


if __name__ == "__main__":
    main()
