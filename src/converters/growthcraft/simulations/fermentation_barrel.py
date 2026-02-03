"""
Symulacja procesu fermentacji w GrowthCraft (FermentationBarrel)

Porównanie wersji:
- 1.7.10: TileEntityFermentBarrel, ID: "grccellar:ferment_barrel"
- 1.18.2: FermentationBarrelBlockEntity, ID: "growthcraft:fermentation_barrel"

Zmiany w NBT:
- 1.7.10: "time" (int), "Tank" (NBTTagCompound), "lid_on" (boolean), "items" (NBTTagList)
- 1.18.2: "CurrentProcessTicks" (int), "MaxProcessTicks" (int), 
          "fluid_tank_input_0" (CompoundTag), "inventory" (CompoundTag)
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class FermentationStage(Enum):
    """Etap fermentacji"""
    IDLE = "idle"
    FERMENTING = "fermenting"
    COMPLETED = "completed"


@dataclass
class FluidStack:
    """Reprezentacja płynu (analogia do FluidStack z Forge)"""
    fluid_name: str  # np. "growthcraft:apple_juice"
    amount: int      # ilość w mB
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
    """Reprezentacja itemu (analogia do ItemStack z Minecraft)"""
    item_id: str     # np. "growthcraft:yeast"
    count: int = 1
    nbt: Optional[Dict[str, Any]] = None
    
    def shrink(self, amount: int = 1):
        """Zmniejsza ilość itemu"""
        self.count = max(0, self.count - amount)
    
    def grow(self, amount: int = 1):
        """Zwiększa ilość itemu"""
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
class FermentationRecipe:
    """Recepta fermentacji"""
    input_fluid: FluidStack
    catalyst: ItemStack           # np. drożdże
    output_fluid: FluidStack
    processing_time: int          # ticki (20 ticków = 1 sekunda)
    output_multiplier: int = 1    # mnożnik wyjściowy
    bottle_item: Optional[ItemStack] = None  # butelka do napełnienia
    
    def matches(self, catalyst: ItemStack, fluid: FluidStack) -> bool:
        """Sprawdza czy składniki pasują do recepty"""
        return (
            catalyst.item_id == self.catalyst.item_id and
            fluid.fluid_name == self.input_fluid.fluid_name and
            fluid.amount >= self.input_fluid.amount
        )
    
    def get_resulting_amount(self, input_fluid: FluidStack) -> int:
        """Oblicza ilość wynikową z mnożnikiem"""
        multiplier = self.get_multiplier(input_fluid)
        return self.output_fluid.amount * multiplier
    
    def get_multiplier(self, fluid_stack: FluidStack) -> int:
        """
        Oblicza mnożnik wyjściowy na podstawie ilości płynu wejściowego.
        W 1.18.2 mnożnik zależy od ilości płynu.
        """
        # Domyślna logika: co 1000mB = 1x mnożnik
        return max(1, fluid_stack.amount // 1000)


class FermentationBarrelSimulator:
    """
    Symulator beczki fermentacyjnej GrowthCraft
    
    Pojemność: 4000 mB (1.18.2), konfigurowalna w 1.7.10 (domyślnie 3000 mB)
    Inventory: 1 slot na katalizator (np. drożdże)
    
    Przykład użycia:
        barrel = FermentationBarrelSimulator()
        barrel.set_fluid(FluidStack("growthcraft:apple_juice", 1000))
        barrel.set_catalyst(ItemStack("growthcraft:yeast", 1))
        
        recipe = FermentationRecipe(
            input_fluid=FluidStack("growthcraft:apple_juice", 1000),
            catalyst=ItemStack("growthcraft:yeast", 1),
            output_fluid=FluidStack("growthcraft:apple_cider", 1000),
            processing_time=2400  # 2 minuty
        )
        
        for _ in range(3000):
            barrel.tick([recipe])
            if barrel.stage == FermentationStage.COMPLETED:
                break
    """
    
    # Konfiguracja
    CAPACITY_1710: int = 3000  # mB
    CAPACITY_1182: int = 4000  # mB
    
    def __init__(self, version: str = "1.18.2"):
        self.version = version
        self.capacity = self.CAPACITY_1182 if version == "1.18.2" else self.CAPACITY_1710
        
        # Stan procesu
        self.tick_clock: int = 0
        self.tick_max: int = -1
        self.stage: FermentationStage = FermentationStage.IDLE
        
        # Zawartość
        self.fluid_tank: Optional[FluidStack] = None
        self.catalyst_slot: Optional[ItemStack] = None
        
        # NBT dla konwersji
        self.custom_name: Optional[str] = None
        
        # Historia dla debugowania
        self.processing_history: List[Dict[str, Any]] = []
    
    def set_fluid(self, fluid: FluidStack) -> bool:
        """Ustawia płyn w zbiorniku"""
        if fluid.amount > self.capacity:
            return False
        self.fluid_tank = fluid.copy()
        return True
    
    def set_catalyst(self, item: ItemStack) -> bool:
        """Ustawia katalizator (np. drożdże)"""
        self.catalyst_slot = item.copy()
        return True
    
    def tick(self, recipes: List[FermentationRecipe]) -> FermentationStage:
        """
        Wykonuje jeden tick procesu fermentacji.
        W Minecraft 1 tick = 1/20 sekundy (50ms)
        """
        # Sprawdź czy mamy płyn
        if self.fluid_tank is None or self.fluid_tank.is_empty():
            self._reset()
            return self.stage
        
        # Znajdź pasującą receptę
        matching_recipe = self._find_matching_recipe(recipes)
        
        if matching_recipe is None:
            self._reset()
            return self.stage
        
        # Proces fermentacji
        if self.tick_max == -1:
            # Inicjalizacja procesu
            multiplier = matching_recipe.get_multiplier(self.fluid_tank)
            self.tick_max = matching_recipe.processing_time * multiplier
            self.stage = FermentationStage.FERMENTING
            
        elif self.tick_clock < self.tick_max:
            # Kontynuacja fermentacji
            self.tick_clock += 1
            
        else:
            # Zakończenie fermentacji
            self._complete_fermentation(matching_recipe)
        
        return self.stage
    
    def _find_matching_recipe(self, recipes: List[FermentationRecipe]) -> Optional[FermentationRecipe]:
        """Znajduje pasującą receptę"""
        if self.catalyst_slot is None or self.fluid_tank is None:
            return None
        
        for recipe in recipes:
            if recipe.matches(self.catalyst_slot, self.fluid_tank):
                return recipe
        return None
    
    def _complete_fermentation(self, recipe: FermentationRecipe):
        """Kończy proces fermentacji"""
        multiplier = recipe.get_multiplier(self.fluid_tank)
        
        # Zużyj katalizator
        if self.catalyst_slot:
            self.catalyst_slot.shrink(multiplier)
        
        # Zamień płyn
        resulting_amount = recipe.get_resulting_amount(self.fluid_tank)
        self.fluid_tank = FluidStack(
            fluid_name=recipe.output_fluid.fluid_name,
            amount=resulting_amount
        )
        
        self.stage = FermentationStage.COMPLETED
        self.processing_history.append({
            "recipe": recipe,
            "multiplier": multiplier,
            "output": self.fluid_tank.copy()
        })
        self._reset_clock()
    
    def _reset(self):
        """Resetuje stan procesu"""
        self._reset_clock()
        self.stage = FermentationStage.IDLE
    
    def _reset_clock(self):
        """Resetuje zegar procesu"""
        self.tick_clock = 0
        self.tick_max = -1
    
    def get_progress_percent(self) -> float:
        """Zwraca postęp w procentach"""
        if self.tick_max <= 0:
            return 0.0
        return (self.tick_clock / self.tick_max) * 100
    
    def to_nbt_1710(self) -> Dict[str, Any]:
        """Eksportuje stan do formatu NBT 1.7.10"""
        nbt = {
            "id": "grccellar:ferment_barrel",
            "time": self.tick_clock,
        }
        
        if self.fluid_tank:
            nbt["Tank"] = {
                "FluidName": self.fluid_tank.fluid_name,
                "Amount": self.fluid_tank.amount
            }
        
        if self.catalyst_slot:
            nbt["items"] = [{
                "id": self.catalyst_slot.item_id,
                "Count": self.catalyst_slot.count,
                "Slot": 0
            }]
        
        return nbt
    
    def to_nbt_1182(self) -> Dict[str, Any]:
        """Eksportuje stan do formatu NBT 1.18.2"""
        nbt = {
            "id": "growthcraft:fermentation_barrel",
            "CurrentProcessTicks": self.tick_clock,
            "MaxProcessTicks": self.tick_max,
        }
        
        if self.fluid_tank:
            nbt["fluid_tank_input_0"] = {
                "FluidName": self.fluid_tank.fluid_name,
                "Amount": self.fluid_tank.amount
            }
        
        if self.catalyst_slot:
            nbt["inventory"] = {
                "Size": 1,
                "Items": [{
                    "id": self.catalyst_slot.item_id,
                    "Count": self.catalyst_slot.count,
                    "Slot": 0
                }]
            }
        
        if self.custom_name:
            nbt["CustomName"] = f'"{self.custom_name}"'
        
        return nbt
    
    def from_nbt_1710(self, nbt: Dict[str, Any]):
        """Importuje stan z formatu NBT 1.7.10"""
        self.tick_clock = nbt.get("time", 0)
        
        tank_data = nbt.get("Tank", {})
        if tank_data:
            self.fluid_tank = FluidStack(
                fluid_name=tank_data.get("FluidName", ""),
                amount=tank_data.get("Amount", 0)
            )
        
        items = nbt.get("items", [])
        if items and len(items) > 0:
            item = items[0]
            self.catalyst_slot = ItemStack(
                item_id=item.get("id", ""),
                count=item.get("Count", 0)
            )
    
    def from_nbt_1182(self, nbt: Dict[str, Any]):
        """Importuje stan z formatu NBT 1.18.2"""
        self.tick_clock = nbt.get("CurrentProcessTicks", 0)
        self.tick_max = nbt.get("MaxProcessTicks", -1)
        
        tank_data = nbt.get("fluid_tank_input_0", {})
        if tank_data:
            self.fluid_tank = FluidStack(
                fluid_name=tank_data.get("FluidName", ""),
                amount=tank_data.get("Amount", 0)
            )
        
        inventory = nbt.get("inventory", {})
        items = inventory.get("Items", [])
        if items and len(items) > 0:
            item = items[0]
            self.catalyst_slot = ItemStack(
                item_id=item.get("id", ""),
                count=item.get("Count", 0)
            )
        
        self.custom_name = nbt.get("CustomName", "")
    
    def __str__(self) -> str:
        return (
            f"FermentationBarrel[{self.version}] "
            f"stage={self.stage.value}, "
            f"progress={self.get_progress_percent():.1f}%, "
            f"fluid={self.fluid_tank}, "
            f"catalyst={self.catalyst_slot}"
        )


# Przykładowe recepty fermentacji
DEFAULT_FERMENTATION_RECIPES = [
    FermentationRecipe(
        input_fluid=FluidStack("growthcraft:apple_juice", 1000),
        catalyst=ItemStack("growthcraft:yeast", 1),
        output_fluid=FluidStack("growthcraft:apple_cider", 1000),
        processing_time=2400,  # 2 minuty
        bottle_item=ItemStack("growthcraft:bottle_apple_cider", 1)
    ),
    FermentationRecipe(
        input_fluid=FluidStack("growthcraft:grape_juice", 1000),
        catalyst=ItemStack("growthcraft:yeast", 1),
        output_fluid=FluidStack("growthcraft:wine", 1000),
        processing_time=2400,
        bottle_item=ItemStack("growthcraft:bottle_wine", 1)
    ),
    FermentationRecipe(
        input_fluid=FluidStack("growthcraft:hop_infused_water", 1000),
        catalyst=ItemStack("growthcraft:yeast", 1),
        output_fluid=FluidStack("growthcraft:ale", 1000),
        processing_time=2400,
        bottle_item=ItemStack("growthcraft:bottle_ale", 1)
    ),
]
