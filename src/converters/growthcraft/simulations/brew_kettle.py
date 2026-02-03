"""
Symulacja procesu warzenia w GrowthCraft (BrewKettle)

Porównanie wersji:
- 1.7.10: TileEntityBrewKettle, ID: "grccellar:brew_kettle"
- 1.18.2: BrewKettleBlockEntity, ID: "growthcraft:brew_kettle"

Zmiany w NBT:
- 1.7.10: "brew_kettle" (CompoundTag) z "time", "time_max", "heat_multiplier"
         Tanks: 2 zbiorniki (input i output)
         Inventory: 2 sloty (surowce i odpad)
- 1.18.2: "CurrentProcessTicks" (int), "MaxProcessTicks" (int)
         "fluid_tank_input_0" (CompoundTag), "fluid_tank_output_0" (CompoundTag)
         "inventory" (CompoundTag) - 3 sloty: [0]=pokrywka, [1]=input, [2]=output/odpad

Nowości w 1.18.2:
- Slot na pokrywkę (lid) - wymagana do niektórych receptur
- Sygnał ciepła sprawdzany automatycznie (BlockStateUtils.isHeated)
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum


class BrewKettleStage(Enum):
    """Etap warzenia"""
    IDLE = "idle"
    HEATING_REQUIRED = "heating_required"  # Brak ciepła
    BREWING = "brewing"
    COMPLETED = "completed"


@dataclass
class FluidStack:
    """Reprezentacja płynu"""
    fluid_name: str
    amount: int
    nbt: Optional[Dict[str, Any]] = None
    
    def copy(self) -> 'FluidStack':
        return FluidStack(
            fluid_name=self.fluid_name,
            amount=self.amount,
            nbt=self.nbt.copy() if self.nbt else None
        )
    
    def is_empty(self) -> bool:
        return self.amount <= 0
    
    def shrink(self, amount: int):
        self.amount = max(0, self.amount - amount)
    
    def __str__(self) -> str:
        return f"{self.fluid_name} ({self.amount}mB)"


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
class BrewKettleRecipe:
    """Recepta warzenia w kotle"""
    input_fluid: FluidStack
    input_item: ItemStack
    output_fluid: FluidStack
    processing_time: int
    requires_lid: bool = False
    requires_heat: bool = True
    byproduct: Optional[ItemStack] = None
    byproduct_chance: int = 0  # 0-100%
    
    def matches(self, item: ItemStack, fluid: FluidStack, has_lid: bool, is_heated: bool) -> bool:
        """Sprawdza czy składniki pasują do recepty"""
        # Sprawdź item
        if item.item_id != self.input_item.item_id:
            return False
        if item.count < self.input_item.count:
            return False
        
        # Sprawdź płyn
        if fluid.fluid_name != self.input_fluid.fluid_name:
            return False
        if fluid.amount < self.input_fluid.amount:
            return False
        
        # Sprawdź wymagania
        if self.requires_lid and not has_lid:
            return False
        if self.requires_heat and not is_heated:
            return False
        
        return True


class BrewKettleSimulator:
    """
    Symulator kotła warzelnego GrowthCraft
    
    Pojemność: 4000 mB na zbiornik (2 zbiorniki: input i output)
    Inventory: 3 sloty (1.18.2)
        - Slot 0: Pokrywka (BrewKettleLid) - opcjonalna
        - Slot 1: Składnik wejściowy (ziarna, chmiel, itp.)
        - Slot 2: Odpad/byproduct (output)
    
    Ciepło: Wymaga źródła ciepła pod spodem (ogień, lava, inne mody)
    
    Przykład użycia:
        kettle = BrewKettleSimulator()
        kettle.set_input_fluid(FluidStack("minecraft:water", 1000))
        kettle.set_input_item(ItemStack("growthcraft:barley", 1))
        kettle.set_lid(True)  # Jeśli recepta wymaga
        kettle.set_heated(True)
        
        recipe = BrewKettleRecipe(
            input_fluid=FluidStack("minecraft:water", 1000),
            input_item=ItemStack("growthcraft:barley", 1),
            output_fluid=FluidStack("growthcraft:wort", 1000),
            processing_time=1200,
            requires_heat=True
        )
        
        for _ in range(1500):
            kettle.tick([recipe])
    """
    
    CAPACITY: int = 4000  # mB na zbiornik
    
    def __init__(self, version: str = "1.18.2"):
        self.version = version
        
        # Stan procesu
        self.tick_clock: int = 0
        self.tick_max: int = -1
        self.stage: BrewKettleStage = BrewKettleStage.IDLE
        
        # Zawartość zbiorników
        self.input_tank: Optional[FluidStack] = None
        self.output_tank: Optional[FluidStack] = None
        
        # Inventory
        self.lid_slot: Optional[ItemStack] = None      # Slot 0 (tylko 1.18.2)
        self.input_slot: Optional[ItemStack] = None    # Slot 1
        self.output_slot: Optional[ItemStack] = None   # Slot 2 (byproduct/odpad)
        
        # Warunki zewnętrzne
        self.is_heated: bool = False
        
        # NBT
        self.custom_name: Optional[str] = None
        
        # Historia
        self.processing_history: List[Dict[str, Any]] = []
    
    def set_input_fluid(self, fluid: FluidStack) -> bool:
        """Ustawia płyn wejściowy"""
        if fluid.amount > self.CAPACITY:
            return False
        self.input_tank = fluid.copy()
        return True
    
    def set_output_fluid(self, fluid: FluidStack) -> bool:
        """Ustawia płyn wyjściowy (rzadko używane, zazwyczaj wynik procesu)"""
        if fluid.amount > self.CAPACITY:
            return False
        self.output_tank = fluid.copy()
        return True
    
    def set_input_item(self, item: ItemStack):
        """Ustawia składnik wejściowy"""
        self.input_slot = item.copy()
    
    def set_lid(self, has_lid: bool):
        """Ustawia pokrywkę (1.18.2)"""
        if has_lid:
            self.lid_slot = ItemStack("growthcraft:brew_kettle_lid", 1)
        else:
            self.lid_slot = None
    
    def set_heated(self, heated: bool):
        """Ustawia czy kocioł jest ogrzewany"""
        self.is_heated = heated
    
    def has_lid(self) -> bool:
        """Sprawdza czy kocioł ma pokrywkę"""
        return self.lid_slot is not None and not self.lid_slot.is_empty()
    
    def tick(self, recipes: List[BrewKettleRecipe]) -> BrewKettleStage:
        """Wykonuje jeden tick procesu warzenia"""
        # Sprawdź czy mamy składniki
        if (self.input_slot is None or self.input_slot.is_empty() or
            self.input_tank is None or self.input_tank.is_empty()):
            self._reset()
            return self.stage
        
        # Znajdź pasującą receptę
        matching_recipe = self._find_matching_recipe(recipes)
        
        if matching_recipe is None:
            self._reset()
            return self.stage
        
        # Sprawdź ciepło
        if matching_recipe.requires_heat and not self.is_heated:
            self.stage = BrewKettleStage.HEATING_REQUIRED
            return self.stage
        
        # Proces warzenia
        if self.tick_max == -1:
            # Inicjalizacja
            self.tick_max = matching_recipe.processing_time
            self.stage = BrewKettleStage.BREWING
            
        elif self.tick_clock < self.tick_max:
            # Kontynuacja
            self.tick_clock += 1
            
        else:
            # Zakończenie
            self._complete_brewing(matching_recipe)
        
        return self.stage
    
    def _find_matching_recipe(self, recipes: List[BrewKettleRecipe]) -> Optional[BrewKettleRecipe]:
        """Znajduje pasującą receptę"""
        if self.input_slot is None or self.input_tank is None:
            return None
        
        for recipe in recipes:
            if recipe.matches(
                self.input_slot,
                self.input_tank,
                self.has_lid(),
                self.is_heated
            ):
                # Sprawdź czy output pasuje (czy nie ma konfliktu płynów)
                if self.output_tank is not None and not self.output_tank.is_empty():
                    if self.output_tank.fluid_name != recipe.output_fluid.fluid_name:
                        continue
                return recipe
        return None
    
    def _complete_brewing(self, recipe: BrewKettleRecipe):
        """Kończy proces warzenia"""
        # Zużyj składniki
        self.input_slot.shrink(recipe.input_item.count)
        if self.input_tank:
            self.input_tank.shrink(recipe.input_fluid.amount)
        
        # Dodaj wynik
        output = recipe.output_fluid.copy()
        if self.output_tank is None or self.output_tank.is_empty():
            self.output_tank = output
        else:
            self.output_tank.amount += output.amount
        
        # Obsłuż byproduct (1.18.2)
        if recipe.byproduct and self.version == "1.18.2":
            import random
            if random.randint(0, 100) <= recipe.byproduct_chance:
                if self.output_slot is None or self.output_slot.is_empty():
                    self.output_slot = recipe.byproduct.copy()
                elif self.output_slot.item_id == recipe.byproduct.item_id:
                    self.output_slot.grow(recipe.byproduct.count)
        
        self.stage = BrewKettleStage.COMPLETED
        self.processing_history.append({
            "recipe": recipe,
            "output_fluid": self.output_tank.copy() if self.output_tank else None,
            "byproduct": self.output_slot.copy() if self.output_slot else None
        })
        self._reset_clock()
    
    def _reset(self):
        """Resetuje stan"""
        self._reset_clock()
        self.stage = BrewKettleStage.IDLE
    
    def _reset_clock(self):
        """Resetuje zegar"""
        self.tick_clock = 0
        self.tick_max = -1
    
    def get_progress_percent(self) -> float:
        """Zwraca postęp w procentach"""
        if self.tick_max <= 0:
            return 0.0
        return (self.tick_clock / self.tick_max) * 100
    
    def is_processing(self) -> bool:
        """Sprawdza czy trwa proces"""
        return self.tick_clock > 0
    
    def to_nbt_1710(self) -> Dict[str, Any]:
        """Eksportuje do NBT 1.7.10"""
        nbt = {
            "id": "grccellar:brew_kettle",
        }
        
        # Dane procesu
        brew_kettle_data = {
            "time": float(self.tick_clock),
            "time_max": float(self.tick_max),
            "heat_multiplier": 1.0 if self.is_heated else 0.0
        }
        nbt["brew_kettle"] = brew_kettle_data
        
        # Zbiorniki (konwersja nazw)
        if self.input_tank:
            nbt["TankInput"] = {
                "FluidName": self.input_tank.fluid_name,
                "Amount": self.input_tank.amount
            }
        if self.output_tank:
            nbt["TankOutput"] = {
                "FluidName": self.output_tank.fluid_name,
                "Amount": self.output_tank.amount
            }
        
        # Inventory (tylko 2 sloty w 1.7.10)
        items = []
        if self.input_slot and not self.input_slot.is_empty():
            items.append({
                "id": self.input_slot.item_id,
                "Count": self.input_slot.count,
                "Slot": 0
            })
        nbt["items"] = items
        
        return nbt
    
    def to_nbt_1182(self) -> Dict[str, Any]:
        """Eksportuje do NBT 1.18.2"""
        nbt = {
            "id": "growthcraft:brew_kettle",
            "CurrentProcessTicks": self.tick_clock,
            "MaxProcessTicks": self.tick_max,
        }
        
        # Zbiorniki
        if self.input_tank:
            nbt["fluid_tank_input_0"] = {
                "FluidName": self.input_tank.fluid_name,
                "Amount": self.input_tank.amount
            }
        if self.output_tank:
            nbt["fluid_tank_output_0"] = {
                "FluidName": self.output_tank.fluid_name,
                "Amount": self.output_tank.amount
            }
        
        # Inventory (3 sloty)
        inventory_items = []
        if self.lid_slot:
            inventory_items.append({
                "id": self.lid_slot.item_id,
                "Count": self.lid_slot.count,
                "Slot": 0
            })
        if self.input_slot:
            inventory_items.append({
                "id": self.input_slot.item_id,
                "Count": self.input_slot.count,
                "Slot": 1
            })
        if self.output_slot:
            inventory_items.append({
                "id": self.output_slot.item_id,
                "Count": self.output_slot.count,
                "Slot": 2
            })
        
        nbt["inventory"] = {
            "Size": 3,
            "Items": inventory_items
        }
        
        if self.custom_name:
            nbt["CustomName"] = f'"{self.custom_name}"'
        
        return nbt
    
    def __str__(self) -> str:
        return (
            f"BrewKettle[{self.version}] "
            f"stage={self.stage.value}, "
            f"progress={self.get_progress_percent():.1f}%, "
            f"heated={self.is_heated}, "
            f"has_lid={self.has_lid()}, "
            f"input={self.input_tank}, "
            f"output={self.output_tank}"
        )


# Przykładowe recepty
DEFAULT_BREW_KETTLE_RECIPES = [
    BrewKettleRecipe(
        input_fluid=FluidStack("minecraft:water", 1000),
        input_item=ItemStack("growthcraft:barley", 1),
        output_fluid=FluidStack("growthcraft:wort", 1000),
        processing_time=1200,  # 1 minuta
        requires_heat=True
    ),
    BrewKettleRecipe(
        input_fluid=FluidStack("growthcraft:wort", 1000),
        input_item=ItemStack("growthcraft:hops", 1),
        output_fluid=FluidStack("growthcraft:hop_infused_water", 1000),
        processing_time=1200,
        requires_heat=True
    ),
    BrewKettleRecipe(
        input_fluid=FluidStack("minecraft:water", 1000),
        input_item=ItemStack("growthcraft:rice", 1),
        output_fluid=FluidStack("growthcraft:rice_water", 1000),
        processing_time=1200,
        requires_heat=True
    ),
]
