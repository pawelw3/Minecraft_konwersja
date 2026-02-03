"""
Testy symulacji GrowthCraft

Uruchom: python -m pytest test_simulations.py -v
lub: python test_simulations.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fermentation_barrel import (
    FermentationBarrelSimulator, FermentationRecipe, FluidStack, ItemStack,
    FermentationStage, DEFAULT_FERMENTATION_RECIPES
)
from brew_kettle import (
    BrewKettleSimulator, BrewKettleRecipe, BrewKettleStage,
    DEFAULT_BREW_KETTLE_RECIPES
)
from bee_box import (
    BeeBoxSimulator, BeeBoxConfig, BeeBoxStage
)
from mixing_vat import (
    MixingVatSimulator, MixingVatFluidRecipe, MixingVatItemRecipe,
    MixingVatStage, MixingVatRecipeType,
    DEFAULT_MIXING_VAT_FLUID_RECIPES, DEFAULT_MIXING_VAT_ITEM_RECIPES
)


def test_fermentation_barrel():
    """Test symulacji beczki fermentacyjnej"""
    print("\n=== Test FermentationBarrel ===")
    
    # Utwórz beczkę
    barrel = FermentationBarrelSimulator(version="1.18.2")
    
    # Ustaw składniki
    barrel.set_fluid(FluidStack("growthcraft:apple_juice", 2000))
    barrel.set_catalyst(ItemStack("growthcraft:yeast", 2))
    
    print(f"Initial: {barrel}")
    
    # Pobierz przykładową receptę
    recipe = DEFAULT_FERMENTATION_RECIPES[0]
    
    # Symuluj proces
    max_ticks = 5000
    for tick in range(max_ticks):
        stage = barrel.tick([recipe])
        if stage == FermentationStage.COMPLETED:
            print(f"Completed at tick {tick}")
            break
    
    print(f"Final: {barrel}")
    print(f"Progress history count: {len(barrel.processing_history)}")
    
    # Test NBT eksport/import
    nbt_1182 = barrel.to_nbt_1182()
    print(f"NBT 1.18.2 keys: {list(nbt_1182.keys())}")
    
    # Test konwersji do 1.7.10
    nbt_1710 = barrel.to_nbt_1710()
    print(f"NBT 1.7.10 keys: {list(nbt_1710.keys())}")
    
    assert barrel.stage == FermentationStage.COMPLETED
    assert len(barrel.processing_history) > 0
    print("[OK] FermentationBarrel test passed")


def test_brew_kettle():
    """Test symulacji kotła warzelnego"""
    print("\n=== Test BrewKettle ===")
    
    kettle = BrewKettleSimulator(version="1.18.2")
    
    # Ustaw składniki
    kettle.set_input_fluid(FluidStack("minecraft:water", 1000))
    kettle.set_input_item(ItemStack("growthcraft:barley", 1))
    kettle.set_heated(True)
    
    print(f"Initial: {kettle}")
    
    recipe = DEFAULT_BREW_KETTLE_RECIPES[0]
    
    # Symuluj
    for tick in range(2000):
        stage = kettle.tick([recipe])
        if stage == BrewKettleStage.COMPLETED:
            print(f"Completed at tick {tick}")
            break
    
    print(f"Final: {kettle}")
    print(f"Output fluid: {kettle.output_tank}")
    
    # Test NBT
    nbt_1182 = kettle.to_nbt_1182()
    print(f"NBT 1.18.2: {len(nbt_1182)} keys")
    
    assert kettle.stage == BrewKettleStage.COMPLETED
    assert kettle.output_tank is not None
    print("[OK] BrewKettle test passed")


def test_bee_box():
    """Test symulacji ula pszczelego"""
    print("\n=== Test BeeBox ===")
    
    config = BeeBoxConfig(
        max_processing_time=100,  # Krótszy czas dla testu
        chance_to_increase_bees=100,  # 100% szansy
        chance_to_replicate_flowers=0
    )
    
    bee_box = BeeBoxSimulator(version="1.18.2", config=config)
    
    # Dodaj pszczoły
    bee_box.set_bees(ItemStack("growthcraft:bee", 8))
    
    # Dodaj puste plastry
    for _ in range(10):
        bee_box.add_comb(ItemStack("growthcraft:honey_comb_empty", 1))
    
    print(f"Initial: {bee_box}")
    print(f"Initial summary: {bee_box.get_summary()}")
    
    # Symuluj
    for tick in range(500):
        bee_box.tick()
    
    summary = bee_box.get_summary()
    print(f"Final summary: {summary}")
    
    # Test NBT
    nbt_1182 = bee_box.to_nbt_1182()
    print(f"NBT 1.18.2 inventory items: {len(nbt_1182.get('inventory', {}).get('Items', []))}")
    
    assert summary['bees'] > 8  # Powinny się rozmnożyć
    assert summary['cycles_completed'] > 0
    print("[OK] BeeBox test passed")


def test_mixing_vat():
    """Test symulacji kadzi do sera"""
    print("\n=== Test MixingVat ===")
    
    vat = MixingVatSimulator(version="1.18.2")
    
    # Test FluidRecipe
    print("\n--- Fluid Recipe Test ---")
    vat.set_input_fluid(FluidStack("growthcraft:milk", 1000))
    vat.set_input_items([ItemStack("growthcraft:rennet", 1)])
    vat.set_heated(True)
    
    recipe = DEFAULT_MIXING_VAT_FLUID_RECIPES[0]
    
    # Aktywuj
    activated = vat.activate(ItemStack("minecraft:wooden_sword", 1))
    print(f"Activated: {activated}")
    
    # Symuluj
    for tick in range(3000):
        stage = vat.tick(DEFAULT_MIXING_VAT_FLUID_RECIPES, [])
        if stage == MixingVatStage.COMPLETED:
            print(f"Fluid recipe completed at tick {tick}")
            break
    
    print(f"After fluid recipe: {vat}")
    print(f"Input tank (now curds): {vat.input_tank}")
    print(f"Output tank (whey): {vat.output_tank}")
    
    assert vat.input_tank.fluid_name == "growthcraft:curds"
    
    # Test ItemRecipe
    print("\n--- Item Recipe Test ---")
    vat2 = MixingVatSimulator(version="1.18.2")
    vat2.set_input_fluid(FluidStack("growthcraft:curds", 1000))
    vat2.set_input_items([ItemStack("growthcraft:salt", 1)])
    vat2.set_heated(True)
    
    item_recipe = DEFAULT_MIXING_VAT_ITEM_RECIPES[0]
    vat2.activate(ItemStack("minecraft:wooden_sword", 1))
    
    for tick in range(1500):
        stage = vat2.tick([], DEFAULT_MIXING_VAT_ITEM_RECIPES)
        if stage == MixingVatStage.COMPLETED:
            print(f"Item recipe completed at tick {tick}")
            break
    
    print(f"Result slot: {vat2.result_slot}")
    assert vat2.result_slot is not None
    
    # Test NBT
    nbt_1182 = vat2.to_nbt_1182()
    print(f"NBT 1.18.2 has IsActivated: {'IsActivated' in nbt_1182}")
    
    print("[OK] MixingVat test passed")


def test_nbt_conversion():
    """Test konwersji NBT między wersjami"""
    print("\n=== Test NBT Conversion ===")
    
    # Test FermentationBarrel
    barrel_1710 = FermentationBarrelSimulator(version="1.7.10")
    barrel_1710.set_fluid(FluidStack("growthcraft:apple_juice", 1000))
    barrel_1710.set_catalyst(ItemStack("growthcraft:yeast", 1))
    
    nbt_1710 = barrel_1710.to_nbt_1710()
    print(f"1.7.10 NBT: {nbt_1710}")
    
    # Import do 1.18.2
    barrel_1182 = FermentationBarrelSimulator(version="1.18.2")
    barrel_1182.from_nbt_1710(nbt_1710)
    
    nbt_converted = barrel_1182.to_nbt_1182()
    print(f"Converted 1.18.2 NBT: {nbt_converted}")
    
    # Weryfikacja
    assert barrel_1182.fluid_tank.fluid_name == "growthcraft:apple_juice"
    assert barrel_1182.catalyst_slot.item_id == "growthcraft:yeast"
    
    print("[OK] NBT conversion test passed")


def run_all_tests():
    """Uruchamia wszystkie testy"""
    print("=" * 60)
    print("GrowthCraft Simulations Tests")
    print("=" * 60)
    
    try:
        test_fermentation_barrel()
        test_brew_kettle()
        test_bee_box()
        test_mixing_vat()
        test_nbt_conversion()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED [OK]")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
