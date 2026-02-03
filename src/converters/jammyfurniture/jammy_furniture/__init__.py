"""
Moduł symulacji Jammy Furniture Reborn.

Zawiera symulacje funkcjonalności modu dla wersji 1.7.10 i 1.18.2.
"""

from .simulations.fridge_freezer_simulation import (
    FridgeFreezerSimulator,
    FridgeType,
    FridgeFreezerInventory,
    ItemStack
)

from .simulations.cooker_simulation import (
    CookerSimulator,
    CookerRecipes,
    CookerState,
    FuelRegistry
)

from .simulations.dishwasher_washingmachine_simulation import (
    ApplianceSimulator,
    ApplianceType,
    DishwasherRecipes,
    WashingMachineRecipes,
    ApplianceState
)

from .simulations.crafting_cupboard_simulation import (
    CraftingSideSimulator,
    KitchenCupboardSimulator,
    WardrobeSimulator,
    CraftingSideInventory,
    KitchenCupboardInventory,
    WardrobeInventory,
    CupboardType
)

from .simulations.rubbishbin_clock_simulation import (
    RubbishBinSimulator,
    RubbishBinInventory,
    ClockSimulator
)

__all__ = [
    # Fridge/Freezer
    "FridgeFreezerSimulator",
    "FridgeType",
    "FridgeFreezerInventory",
    
    # Cooker
    "CookerSimulator",
    "CookerRecipes",
    "CookerState",
    "FuelRegistry",
    
    # Appliances
    "ApplianceSimulator",
    "ApplianceType",
    "DishwasherRecipes",
    "WashingMachineRecipes",
    "ApplianceState",
    
    # Storage
    "CraftingSideSimulator",
    "KitchenCupboardSimulator",
    "WardrobeSimulator",
    "CraftingSideInventory",
    "KitchenCupboardInventory",
    "WardrobeInventory",
    "CupboardType",
    
    # Misc
    "RubbishBinSimulator",
    "RubbishBinInventory",
    "ClockSimulator",
    
    # Common
    "ItemStack",
]

__version__ = "1.0.0"
