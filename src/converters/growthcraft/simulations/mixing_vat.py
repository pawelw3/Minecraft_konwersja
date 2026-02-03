"""
Symulacja produkcji sera w GrowthCraft (MixingVat / CheeseVat)

Porównanie wersji:
- 1.7.10: TileEntityCheeseVat, ID: "grcmilk:cheese_vat"
- 1.18.2: MixingVatBlockEntity, ID: "growthcraft:mixing_vat"

UWAGA: W 1.18.2 nazwa zmieniła się z CheeseVat na MixingVat i ma szersze zastosowanie!

Zmiany w NBT:
- 1.7.10: "progress" (float), "progress_max" (int), "vat_state" (String)
         "heat_component" (CompoundTag) z "heat_multiplier"
         Tanks: 4 zbiorniki (PRIMARY, RENNET, WASTE, RECIPE)
         Inventory: 3 sloty na składniki
- 1.18.2: "CurrentProcessTicks" (int), "MaxProcessTicks" (int)
         "IsActivated" (boolean) - NOWOŚĆ!
         "RequiresHeatSource" (boolean)
         "InputFluidTank" (CompoundTag), "ReagentFluidTank" (CompoundTag)
         "ActivationTool" (CompoundTag), "ResultActivationTool" (CompoundTag)
         "inventory" (CompoundTag) - 4 sloty

Nowości w 1.18.2:
- System aktywacji: Proces wymaga aktywacji narzędziem (np. mieczem)
- Dwa typy receptur:
  * MixingVatFluidRecipe - wynikiem jest płyn (np. zsiadłe mleko)
  * MixingVatItemRecipe - wynikiem jest item (np. ser)
- Slot na narzędzie aktywacji i narzędzie wynikowe
- Automatyczne sprawdzanie źródła ciepła

Proces produkcji sera w 1.18.2:
1. Dodaj składniki (płyny + itemy)
2. Aktywuj narzędziem (np. mieczem) - ustawia IsActivated=True
3. Ogrzewaj (jeśli wymagane)
4. Poczekaj na zakończenie procesu
5. Pobierz wynik (w zależności od typu receptury)
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Union
from enum import Enum


class MixingVatStage(Enum):
    """Etap pracy kadzi"""
    IDLE = "idle"
    WAITING_FOR_ACTIVATION = "waiting_for_activation"
    MIXING = "mixing"
    COMPLETED = "completed"


class MixingVatRecipeType(Enum):
    """Typ receptury kadzi"""
    FLUID = "fluid"    # Wynikiem jest płyn
    ITEM = "item"      # Wynikiem jest item


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
class MixingVatFluidRecipe:
    """
    Receptura kadzi - wynikiem jest płyn
    Przykład: Mleko + podpuszczka -> zsiadłe mleko + serwatka
    """
    input_fluid: FluidStack
    input_items: List[ItemStack]
    output_fluid: FluidStack
    waste_fluid: FluidStack  # Odpad/serwatka
    processing_time: int
    activation_tool: ItemStack  # Narzędzie do aktywacji (np. miecz)
    requires_heat: bool = True
    
    def matches(self, fluid: FluidStack, items: List[ItemStack], is_heated: bool) -> bool:
        """Sprawdza czy składniki pasują"""
        if self.requires_heat and not is_heated:
            return False
        if fluid.fluid_name != self.input_fluid.fluid_name:
            return False
        if fluid.amount < self.input_fluid.amount:
            return False
        
        # Sprawdź itemy
        for required_item in self.input_items:
            found = False
            for item in items:
                if item.item_id == required_item.item_id and item.count >= required_item.count:
                    found = True
                    break
            if not found:
                return False
        
        return True


@dataclass
class MixingVatItemRecipe:
    """
    Receptura kadzi - wynikiem jest item
    Przykład: Mleko + kultura + sól -> blok sera
    """
    input_fluid: FluidStack
    input_items: List[ItemStack]
    result_item: ItemStack
    processing_time: int
    activation_tool: ItemStack      # Narzędzie do aktywacji
    result_activation_tool: ItemStack  # Narzędzie do pobrania wyniku
    requires_heat: bool = True
    
    def matches(self, fluid: FluidStack, items: List[ItemStack], is_heated: bool) -> bool:
        """Sprawdza czy składniki pasują"""
        if self.requires_heat and not is_heated:
            return False
        if fluid.fluid_name != self.input_fluid.fluid_name:
            return False
        if fluid.amount < self.input_fluid.amount:
            return False
        
        # Sprawdź itemy
        for required_item in self.input_items:
            found = False
            for item in items:
                if item.item_id == required_item.item_id and item.count >= required_item.count:
                    found = True
                    break
            if not found:
                return False
        
        return True


class MixingVatSimulator:
    """
    Symulator kadzi do sera (MixingVat) GrowthCraft
    
    Pojemność: 
    - Input tank: 4000 mB
    - Output/Reagent tank: 1000 mB
    
    Inventory: 4 sloty
        - Slot 0-2: Składniki (np. sól, kultura, itp.)
        - Slot 3: Wynik (item) - tylko dla MixingVatItemRecipe
    
    Proces wymaga aktywacji narzędziem w 1.18.2!
    
    Przykład użycia (FluidRecipe):
        vat = MixingVatSimulator()
        vat.set_input_fluid(FluidStack("growthcraft:milk", 1000))
        vat.set_input_items([ItemStack("growthcraft:rennet", 1)])
        vat.set_heated(True)
        
        recipe = MixingVatFluidRecipe(
            input_fluid=FluidStack("growthcraft:milk", 1000),
            input_items=[ItemStack("growthcraft:rennet", 1)],
            output_fluid=FluidStack("growthcraft:curds", 1000),
            waste_fluid=FluidStack("growthcraft:whey", 500),
            processing_time=2400,
            activation_tool=ItemStack("minecraft:wooden_sword", 1)
        )
        
        # Aktywuj proces
        vat.activate(ItemStack("minecraft:wooden_sword", 1))
        
        # Symuluj
        for _ in range(3000):
            vat.tick([recipe])
    
    Przykład użycia (ItemRecipe):
        recipe = MixingVatItemRecipe(
            input_fluid=FluidStack("growthcraft:curds", 1000),
            input_items=[ItemStack("growthcraft:salt", 1)],
            result_item=ItemStack("growthcraft:cheese_cheddar", 1),
            processing_time=1200,
            activation_tool=ItemStack("minecraft:wooden_sword", 1),
            result_activation_tool=ItemStack("growthcraft:cheese_cloth", 1)
        )
        
        vat.activate(ItemStack("minecraft:wooden_sword", 1))
        for _ in range(1500):
            vat.tick([recipe])
        
        # Pobierz wynik specjalnym narzędziem
        vat.activate_result(ItemStack("growthcraft:cheese_cloth", 1))
    """
    
    INPUT_CAPACITY: int = 4000   # mB
    OUTPUT_CAPACITY: int = 1000  # mB
    
    def __init__(self, version: str = "1.18.2"):
        self.version = version
        
        # Stan procesu
        self.tick_clock: int = 0
        self.tick_max: int = -1
        self.stage: MixingVatStage = MixingVatStage.IDLE
        self.activated: bool = False
        
        # Zbiorniki
        self.input_tank: Optional[FluidStack] = None
        self.output_tank: Optional[FluidStack] = None
        
        # Inventory (4 sloty)
        self.input_slots: List[Optional[ItemStack]] = [None, None, None]  # Slot 0-2
        self.result_slot: Optional[ItemStack] = None  # Slot 3
        
        # Narzędzia aktywacji (1.18.2)
        self.activation_tool: Optional[ItemStack] = None
        self.result_activation_tool: Optional[ItemStack] = None
        self.requires_heat: bool = True
        
        # Warunki zewnętrzne
        self.is_heated: bool = False
        
        # Aktualna receptura
        self.current_recipe: Optional[Union[MixingVatFluidRecipe, MixingVatItemRecipe]] = None
        self.current_recipe_type: Optional[MixingVatRecipeType] = None
        
        # Historia
        self.history: List[Dict[str, Any]] = []
    
    def set_input_fluid(self, fluid: FluidStack) -> bool:
        """Ustawia płyn wejściowy"""
        if fluid.amount > self.INPUT_CAPACITY:
            return False
        self.input_tank = fluid.copy()
        return True
    
    def set_input_items(self, items: List[ItemStack]):
        """Ustawia składniki (max 3)"""
        for i, item in enumerate(items[:3]):
            self.input_slots[i] = item.copy()
    
    def set_heated(self, heated: bool):
        """Ustawia czy kadź jest ogrzewana"""
        self.is_heated = heated
    
    def can_activate(self, tool: ItemStack) -> bool:
        """Sprawdza czy można aktywować danym narzędziem"""
        if self.activated:
            return False
        
        # Sprawdź czy mamy składniki
        if self.input_tank is None or self.input_tank.is_empty():
            return False
        
        current_items = [s for s in self.input_slots if s is not None and not s.is_empty()]
        if not current_items:
            return False
        
        return True
    
    def activate(self, tool: ItemStack) -> bool:
        """
        Aktywuje proces danym narzędziem.
        W 1.18.2 proces NIE rozpocznie się bez aktywacji!
        """
        if not self.can_activate(tool):
            return False
        
        self.activated = True
        self.activation_tool = tool.copy()
        self.stage = MixingVatStage.WAITING_FOR_ACTIVATION
        return True
    
    def can_activate_result(self, tool: ItemStack) -> bool:
        """Sprawdza czy można pobrać wynik danym narzędziem"""
        if self.result_activation_tool is None:
            return False
        return self.result_activation_tool.item_id == tool.item_id
    
    def activate_result(self, tool: ItemStack) -> Optional[ItemStack]:
        """Pobiera wynik specjalnym narzędziem"""
        if not self.can_activate_result(tool):
            return None
        
        result = self.result_slot.copy() if self.result_slot else None
        self.result_slot = None
        self.result_activation_tool = None
        return result
    
    def tick(self, fluid_recipes: List[MixingVatFluidRecipe], 
             item_recipes: List[MixingVatItemRecipe]) -> MixingVatStage:
        """Wykonuje jeden tick procesu"""
        # Bez aktywacji = brak pracy
        if not self.activated:
            return self.stage
        
        # Znajdź pasującą recepturę
        fluid_recipe = self._find_matching_fluid_recipe(fluid_recipes)
        item_recipe = self._find_matching_item_recipe(item_recipes)
        
        valid_recipe = fluid_recipe or item_recipe
        
        if not valid_recipe:
            self._reset()
            return self.stage
        
        # Sprawdź ciepło
        if self.requires_heat and not self.is_heated:
            self.stage = MixingVatStage.WAITING_FOR_ACTIVATION
            return self.stage
        
        # Zapisz aktualną recepturę
        if fluid_recipe:
            self.current_recipe = fluid_recipe
            self.current_recipe_type = MixingVatRecipeType.FLUID
        else:
            self.current_recipe = item_recipe
            self.current_recipe_type = MixingVatRecipeType.ITEM
            self.result_activation_tool = item_recipe.result_activation_tool
        
        # Proces mieszania
        if self.tick_max == -1:
            # Inicjalizacja
            self.tick_max = self.current_recipe.processing_time
            self.requires_heat = self.current_recipe.requires_heat
            self.stage = MixingVatStage.MIXING
            
        elif self.tick_clock < self.tick_max:
            # Kontynuacja
            self.tick_clock += 1
            
        else:
            # Zakończenie
            if self.current_recipe_type == MixingVatRecipeType.FLUID:
                self._complete_fluid_recipe(self.current_recipe)
            else:
                self._complete_item_recipe(self.current_recipe)
        
        return self.stage
    
    def _find_matching_fluid_recipe(self, recipes: List[MixingVatFluidRecipe]) -> Optional[MixingVatFluidRecipe]:
        """Znajduje pasującą recepturę fluid"""
        if self.input_tank is None:
            return None
        
        current_items = [s for s in self.input_slots if s is not None and not s.is_empty()]
        
        for recipe in recipes:
            if recipe.matches(self.input_tank, current_items, self.is_heated):
                return recipe
        return None
    
    def _find_matching_item_recipe(self, recipes: List[MixingVatItemRecipe]) -> Optional[MixingVatItemRecipe]:
        """Znajduje pasującą recepturę item"""
        if self.input_tank is None:
            return None
        
        current_items = [s for s in self.input_slots if s is not None and not s.is_empty()]
        
        for recipe in recipes:
            if recipe.matches(self.input_tank, current_items, self.is_heated):
                return recipe
        return None
    
    def _complete_fluid_recipe(self, recipe: MixingVatFluidRecipe):
        """Kończy recepturę fluid"""
        # Zużyj składniki
        for slot in self.input_slots:
            if slot:
                slot.shrink(slot.count)
        
        # Ustaw płyny wynikowe
        self.input_tank = recipe.output_fluid.copy()
        self.output_tank = recipe.waste_fluid.copy()
        
        self._complete_common()
    
    def _complete_item_recipe(self, recipe: MixingVatItemRecipe):
        """Kończy recepturę item"""
        # Zużyj składniki
        for slot in self.input_slots:
            if slot:
                slot.shrink(slot.count)
        
        # Zużyj płyn
        self.input_tank = None
        
        # Ustaw wynik
        self.result_slot = recipe.result_item.copy()
        
        self._complete_common()
    
    def _complete_common(self):
        """Wspólne operacje przy kończeniu"""
        self.stage = MixingVatStage.COMPLETED
        self.history.append({
            "recipe": self.current_recipe,
            "type": self.current_recipe_type.value if self.current_recipe_type else None,
            "input": self.input_tank.copy() if self.input_tank else None,
            "output": self.output_tank.copy() if self.output_tank else None,
            "result": self.result_slot.copy() if self.result_slot else None
        })
        self._reset_clock()
    
    def _reset(self):
        """Resetuje stan"""
        self._reset_clock()
        self.activated = False
        self.stage = MixingVatStage.IDLE
        self.current_recipe = None
        self.current_recipe_type = None
    
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
            "id": "grcmilk:cheese_vat",
            "progress": float(self.tick_clock),
            "progress_max": self.tick_max,
            "vat_state": self._get_vat_state_1710()
        }
        
        # Heat component
        nbt["heat_component"] = {
            "heat_multiplier": 1.0 if self.is_heated else 0.0
        }
        
        # Tanks (4 zbiorniki w 1.7.10)
        if self.input_tank:
            nbt["TankPrimary"] = {
                "FluidName": self.input_tank.fluid_name,
                "Amount": self.input_tank.amount
            }
        if self.output_tank:
            nbt["TankWaste"] = {
                "FluidName": self.output_tank.fluid_name,
                "Amount": self.output_tank.amount
            }
        
        # Inventory
        items = []
        for i, slot in enumerate(self.input_slots):
            if slot and not slot.is_empty():
                items.append({
                    "id": slot.item_id,
                    "Count": slot.count,
                    "Slot": i
                })
        nbt["items"] = items
        
        return nbt
    
    def _get_vat_state_1710(self) -> str:
        """Zwraca stan kadzi w formacie 1.7.10"""
        if self.stage == MixingVatStage.IDLE:
            return "idle"
        elif self.stage == MixingVatStage.MIXING:
            return "preparing_curds" if self.current_recipe_type == MixingVatRecipeType.FLUID else "preparing_cheese"
        elif self.stage == MixingVatStage.COMPLETED:
            return "preparing_ricotta"
        return "idle"
    
    def to_nbt_1182(self) -> Dict[str, Any]:
        """Eksportuje do NBT 1.18.2"""
        nbt = {
            "id": "growthcraft:mixing_vat",
            "CurrentProcessTicks": self.tick_clock,
            "MaxProcessTicks": self.tick_max,
            "IsActivated": self.activated,
            "RequiresHeatSource": self.requires_heat
        }
        
        # Tanks
        if self.input_tank:
            nbt["InputFluidTank"] = {
                "FluidName": self.input_tank.fluid_name,
                "Amount": self.input_tank.amount
            }
        if self.output_tank:
            nbt["ReagentFluidTank"] = {
                "FluidName": self.output_tank.fluid_name,
                "Amount": self.output_tank.amount
            }
        
        # Narzędzia
        if self.activation_tool:
            nbt["ActivationTool"] = {
                "id": self.activation_tool.item_id,
                "Count": self.activation_tool.count
            }
        if self.result_activation_tool:
            nbt["ResultActivationTool"] = {
                "id": self.result_activation_tool.item_id,
                "Count": self.result_activation_tool.count
            }
        
        # Inventory
        items = []
        for i, slot in enumerate(self.input_slots):
            if slot and not slot.is_empty():
                items.append({
                    "id": slot.item_id,
                    "Count": slot.count,
                    "Slot": i
                })
        if self.result_slot and not self.result_slot.is_empty():
            items.append({
                "id": self.result_slot.item_id,
                "Count": self.result_slot.count,
                "Slot": 3
            })
        
        nbt["inventory"] = {
            "Size": 4,
            "Items": items
        }
        
        return nbt
    
    def __str__(self) -> str:
        return (
            f"MixingVat[{self.version}] "
            f"stage={self.stage.value}, "
            f"activated={self.activated}, "
            f"progress={self.get_progress_percent():.1f}%, "
            f"heated={self.is_heated}, "
            f"input={self.input_tank}, "
            f"recipe_type={self.current_recipe_type.value if self.current_recipe_type else None}"
        )


# Przykładowe receptury
DEFAULT_MIXING_VAT_FLUID_RECIPES = [
    MixingVatFluidRecipe(
        input_fluid=FluidStack("growthcraft:milk", 1000),
        input_items=[ItemStack("growthcraft:rennet", 1)],
        output_fluid=FluidStack("growthcraft:curds", 1000),
        waste_fluid=FluidStack("growthcraft:whey", 500),
        processing_time=2400,
        activation_tool=ItemStack("minecraft:wooden_sword", 1),
        requires_heat=True
    ),
    MixingVatFluidRecipe(
        input_fluid=FluidStack("growthcraft:milk", 1000),
        input_items=[ItemStack("growthcraft:starter_culture", 1)],
        output_fluid=FluidStack("growthcraft:ricotta", 1000),
        waste_fluid=FluidStack("growthcraft:whey", 200),
        processing_time=1800,
        activation_tool=ItemStack("minecraft:wooden_sword", 1),
        requires_heat=True
    ),
]

DEFAULT_MIXING_VAT_ITEM_RECIPES = [
    MixingVatItemRecipe(
        input_fluid=FluidStack("growthcraft:curds", 1000),
        input_items=[ItemStack("growthcraft:salt", 1)],
        result_item=ItemStack("growthcraft:cheese_cheddar", 4),
        processing_time=1200,
        activation_tool=ItemStack("minecraft:wooden_sword", 1),
        result_activation_tool=ItemStack("growthcraft:cheese_cloth", 1),
        requires_heat=False
    ),
]
