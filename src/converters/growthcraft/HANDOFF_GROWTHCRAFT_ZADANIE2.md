# Handoff: Zadanie 2 - GrowthCraft (Symulacje funkcjonalności i porównanie NBT)

## Podsumowanie sesji

Wykonano kompletną analizę kodu źródłowego **GrowthCraft Community Edition 7.1.1** dla Minecraft 1.18.2 oraz przygotowano szczegółowe symulacje funkcjonalności w Pythonie dla czterech kluczowych procesów:
1. Fermentacja (FermentationBarrel)
2. Warzenie (BrewKettle)
3. Produkcja miodu (BeeBox)
4. Produkcja sera (MixingVat/CheeseVat)

Wszystkie symulacje zostały przetestowane i zawierają pełną obsługę konwersji NBT między wersjami 1.7.10 a 1.18.2.

---

## 1. Kod źródłowy GrowthCraft 1.18.2

### 1.1 Pobrano repozytorium
```
mod_src/actual_src/1.18.2/Growthcraft/
├── src/main/java/growthcraft/
│   ├── apiary/          # Pszczelarstwo (BeeBox)
│   ├── apples/          # Jabłka
│   ├── bamboo/          # Bambus
│   ├── cellar/          # Browarnictwo (FermentationBarrel, BrewKettle, FruitPress, CultureJar)
│   ├── core/            # Rdzeń (Rope)
│   ├── milk/            # Mleczarstwo (MixingVat, CheesePress, Churn, Pancheon)
│   └── rice/            # Ryż
```

### 1.2 Kluczowe klasy BlockEntity (1.18.2)

| Moduł | Klasa | Odpowiednik 1.7.10 |
|-------|-------|-------------------|
| Cellar | `FermentationBarrelBlockEntity` | `TileEntityFermentBarrel` |
| Cellar | `BrewKettleBlockEntity` | `TileEntityBrewKettle` |
| Cellar | `FruitPressBlockEntity` | `TileEntityFruitPress` |
| Cellar | `CultureJarBlockEntity` | `TileEntityCultureJar` |
| Apiary | `BeeBoxBlockEntity` | `TileEntityBeeBox` |
| Milk | `MixingVatBlockEntity` | `TileEntityCheeseVat` |
| Milk | `CheesePressBlockEntity` | `TileEntityCheesePress` |
| Milk | `ChurnBlockEntity` | `TileEntityButterChurn` |
| Milk | `PancheonBlockEntity` | `TileEntityPancheon` |

---

## 2. Szczegółowe porównanie struktur NBT

### 2.1 FermentationBarrel (Beczka fermentacyjna)

#### 1.7.10 → 1.18.2 Mapowanie NBT

| 1.7.10 (grccellar:ferment_barrel) | 1.18.2 (growthcraft:fermentation_barrel) | Uwagi |
|-----------------------------------|------------------------------------------|-------|
| `time` (int) | `CurrentProcessTicks` (int) | Bezpośrednie mapowanie |
| - | `MaxProcessTicks` (int) | Nowość w 1.18.2 |
| `Tank` (NBTTagCompound) | `fluid_tank_input_0` (CompoundTag) | Zmiana nazwy |
| `lid_on` (boolean) | - | Usunięte - brak pokrywki w 1.18.2 |
| `items` (NBTTagList) | `inventory` (CompoundTag) | Zmiana struktury |
| - | `CustomName` (string) | Opcjonalna nazwa |

**Zmiany funkcjonalne:**
- Pojemność: 3000 mB → 4000 mB
- Brak pokrywki w 1.18.2
- System mnożnika wyjściowego zależny od ilości płynu

---

### 2.2 BrewKettle (Kocioł warzelny)

#### 1.7.10 → 1.18.2 Mapowanie NBT

| 1.7.10 (grccellar:brew_kettle) | 1.18.2 (growthcraft:brew_kettle) | Uwagi |
|--------------------------------|----------------------------------|-------|
| `brew_kettle.time` (float) | `CurrentProcessTicks` (int) | Zmiana typu |
| `brew_kettle.time_max` (float) | `MaxProcessTicks` (int) | Zmiana typu |
| `brew_kettle.heat_multiplier` (float) | - | Usunięte - sprawdzane dynamicznie |
| `TankInput` (NBTTagCompound) | `fluid_tank_input_0` (CompoundTag) | Zmiana nazwy |
| `TankOutput` (NBTTagCompound) | `fluid_tank_output_0` (CompoundTag) | Zmiana nazwy |
| `items[0]` (input) | `inventory.Items[1]` | Slot 1 w 1.18.2 |
| `items[1]` (byproduct) | `inventory.Items[2]` | Slot 2 w 1.18.2 |
| - | `inventory.Items[0]` | NOWOŚĆ: slot na pokrywkę (lid) |
| - | `CustomName` (string) | Opcjonalna nazwa |

**Zmiany funkcjonalne:**
- NOWOŚĆ: Slot na pokrywkę (BrewKettleLid) - wymagany dla niektórych receptur
- System byproduct z szansą (0-100%)
- Automatyczne wykrywanie ciepła (BlockStateUtils.isHeated)

---

### 2.3 BeeBox (Ul pszczeli)

#### 1.7.10 → 1.18.2 Mapowanie NBT

| 1.7.10 (grcbees:bee_box) | 1.18.2 (growthcraft:bee_box) | Uwagi |
|--------------------------|------------------------------|-------|
| `bee_box.bonus_time` (int) | - | Usunięte |
| `bee_box.bee_count` (int) | - | Usunięte - liczone z inventory |
| `BeeBox.version` (int) | - | Usunięte |
| - | `CurrentProcessTicks` (int) | Nowość w 1.18.2 |
| `items` (NBTTagList) | `inventory` (CompoundTag) | Zmiana struktury |
| - | `CustomName` (string) | Opcjonalna nazwa |

**Zmiany funkcjonalne:**
- Konfigurowalny czas procesu (config)
- Szansa na rozmnażanie pszczół (config)
- Szansa na replikację kwiatów (config)
- Obsługa vanillowych plastrów (minecraft:honeycomb)
- Slot 0: pszczoły (musi być w tagu BEE)
- Slot 1-27: plastry (puste/pełne/vanillowe)

---

### 2.4 MixingVat (Kadź do sera) - NAJWAŻNIEJSZE ZMIANY

#### UWAGA: W 1.18.2 nazwa zmieniła się z CheeseVat na MixingVat!

#### 1.7.10 → 1.18.2 Mapowanie NBT

| 1.7.10 (grcmilk:cheese_vat) | 1.18.2 (growthcraft:mixing_vat) | Uwagi |
|-----------------------------|---------------------------------|-------|
| `progress` (float) | `CurrentProcessTicks` (int) | Zmiana typu i nazwy |
| `progress_max` (int) | `MaxProcessTicks` (int) | Bezpośrednie mapowanie |
| `vat_state` (String) | - | Usunięte - wnioskowane z stanu |
| `heat_component.heat_multiplier` (float) | `RequiresHeatSource` (boolean) | Zmiana koncepcji |
| `TankPrimary` (NBTTagCompound) | `InputFluidTank` (CompoundTag) | Zmiana nazwy |
| `TankRennet` (NBTTagCompound) | - | Usunięte - sloty inventory |
| `TankWaste` (NBTTagCompound) | `ReagentFluidTank` (CompoundTag) | Zmiana nazwy |
| `TankRecipe` (NBTTagCompound) | - | Usunięte - sloty inventory |
| `items` (NBTTagList) | `inventory` (CompoundTag) | Zmiana struktury |
| - | `IsActivated` (boolean) | **NOWOŚĆ - KLUCZOWA ZMIANA!** |
| - | `ActivationTool` (CompoundTag) | **NOWOŚĆ** |
| - | `ResultActivationTool` (CompoundTag) | **NOWOŚĆ** |
| - | `CustomName` (string) | Opcjonalna nazwa |

**KLUCZOWE zmiany funkcjonalne w 1.18.2:**
1. **System aktywacji**: Proces WYMAGA aktywacji narzędziem (np. mieczem)!
2. **Dwa typy receptur**:
   - `MixingVatFluidRecipe` - wynikiem jest płyn (curds, ricotta)
   - `MixingVatItemRecipe` - wynikiem jest item (blok sera)
3. **Sloty inventory**:
   - Slot 0-2: składniki (sól, kultura, itp.)
   - Slot 3: wynik (tylko dla ItemRecipe)
4. **Narzędzia**:
   - `ActivationTool`: Narzędzie do rozpoczęcia procesu (miecz)
   - `ResultActivationTool`: Narzędzie do pobrania wyniku (cheese_cloth)

---

## 3. Symulacje w Pythonie

### 3.1 Struktura modułu

```
src/growthcraft_simulations/
├── __init__.py                  # Eksport klas
├── fermentation_barrel.py       # Fermentacja
├── brew_kettle.py              # Warzenie
├── bee_box.py                  # Produkcja miodu
├── mixing_vat.py               # Produkcja sera
└── test_simulations.py         # Testy
```

### 3.2 Klasy symulatorów

| Plik | Klasa | Funkcjonalność |
|------|-------|----------------|
| `fermentation_barrel.py` | `FermentationBarrelSimulator` | Symulacja fermentacji z obsługą mnożnika |
| `brew_kettle.py` | `BrewKettleSimulator` | Warzenie z obsługą pokrywki i byproduct |
| `bee_box.py` | `BeeBoxSimulator` | Produkcja miodu z rozmnażaniem pszczół |
| `mixing_vat.py` | `MixingVatSimulator` | Produkcja sera z systemem aktywacji |

### 3.3 Wspólne klasy pomocnicze

- `FluidStack` - reprezentacja płynu (fluid_name, amount, nbt)
- `ItemStack` - reprezentacja itemu (item_id, count, nbt)
- Enumy dla stanów procesów (FermentationStage, BrewKettleStage, itp.)

### 3.4 Metody konwersji NBT

Każdy symulator posiada metody:
- `to_nbt_1710()` - eksport do formatu 1.7.10
- `to_nbt_1182()` - eksport do formatu 1.18.2
- `from_nbt_1710(nbt)` - import z formatu 1.7.10
- `from_nbt_1182(nbt)` - import z formatu 1.18.2

---

## 4. Przykłady użycia symulacji

### 4.1 Fermentacja (FermentationBarrel)

```python
from growthcraft_simulations import (
    FermentationBarrelSimulator, FermentationRecipe,
    FluidStack, ItemStack, DEFAULT_FERMENTATION_RECIPES
)

# Utwórz beczkę
barrel = FermentationBarrelSimulator(version="1.18.2")
barrel.set_fluid(FluidStack("growthcraft:apple_juice", 2000))
barrel.set_catalyst(ItemStack("growthcraft:yeast", 2))

# Symuluj proces
recipe = DEFAULT_FERMENTATION_RECIPES[0]
for tick in range(5000):
    stage = barrel.tick([recipe])
    if stage.name == "COMPLETED":
        break

# Eksportuj NBT
nbt_1182 = barrel.to_nbt_1182()
nbt_1710 = barrel.to_nbt_1710()
```

### 4.2 Produkcja sera (MixingVat)

```python
from growthcraft_simulations import (
    MixingVatSimulator, MixingVatFluidRecipe,
    FluidStack, ItemStack
)

# Utwórz kadź
vat = MixingVatSimulator(version="1.18.2")
vat.set_input_fluid(FluidStack("growthcraft:milk", 1000))
vat.set_input_items([ItemStack("growthcraft:rennet", 1)])
vat.set_heated(True)

# AKTYWUJ proces (wymagane w 1.18.2!)
vat.activate(ItemStack("minecraft:wooden_sword", 1))

# Symuluj
recipe = MixingVatFluidRecipe(...)
for tick in range(3000):
    stage = vat.tick([recipe], [])
    if stage.name == "COMPLETED":
        break
```

---

## 5. Wyniki testów

```
============================================================
GrowthCraft Simulations Tests
============================================================

=== Test FermentationBarrel ===
Completed at tick 4801
Final fluid: growthcraft:apple_cider (2000mB)
[OK] FermentationBarrel test passed

=== Test BrewKettle ===
Completed at tick 1201
Output fluid: growthcraft:wort (1000mB)
[OK] BrewKettle test passed

=== Test BeeBox ===
Final: bees=12 (rozmnożone!), full_combs=12
[OK] BeeBox test passed

=== Test MixingVat ===
Fluid recipe completed at tick 2401
Input tank: growthcraft:curds (1000mB)
Output tank: growthcraft:whey (500mB)
[OK] MixingVat test passed

=== Test NBT Conversion ===
[OK] NBT conversion test passed

============================================================
ALL TESTS PASSED [OK]
============================================================
```

---

## 6. Kluczowe wyzwania konwersji

### 6.1 MixingVat - System aktywacji

**Problem**: W 1.18.2 proces wymaga aktywacji narzędziem, co nie istnieje w 1.7.10.

**Rozwiązanie konwersji**:
1. Jeśli CheeseVat z 1.7.10 ma składniki i ciepło -> automatycznie aktywować w 1.18.2
2. Domyślne narzędzie aktywacji: `minecraft:wooden_sword`
3. Dla CheeseVat w stanie "preparing_cheese" -> użyć ItemRecipe
4. Dla CheeseVat w stanie "preparing_curds" -> użyć FluidRecipe

### 6.2 BrewKettle - Pokrywka

**Problem**: 1.18.2 ma slot na pokrywkę, którego nie było w 1.7.10.

**Rozwiązanie**: 
- Jeśli receptura wymaga pokrywki -> dodać `growthcraft:brew_kettle_lid` do slotu 0
- Jeśli nie -> zostawić slot 0 pusty

### 6.3 BeeBox - Konfiguracja

**Problem**: 1.18.2 używa konfiguracji dla czasów i szans.

**Rozwiązanie**:
- Użyć domyślnych wartości z configu 1.18.2
- Zachować tick_clock jako "CurrentProcessTicks"

---

## 7. Utworzone pliki

| Plik | Opis |
|------|------|
| `src/growthcraft_simulations/__init__.py` | Eksport klas modułu |
| `src/growthcraft_simulations/fermentation_barrel.py` | Symulacja + NBT |
| `src/growthcraft_simulations/brew_kettle.py` | Symulacja + NBT |
| `src/growthcraft_simulations/bee_box.py` | Symulacja + NBT |
| `src/growthcraft_simulations/mixing_vat.py` | Symulacja + NBT |
| `src/growthcraft_simulations/test_simulations.py` | Testy jednostkowe |
| `mod_src/actual_src/1.18.2/Growthcraft/` | Kod źródłowy 1.18.2 |
| `HANDOFF_GROWTHCRAFT_ZADANIE2.md` | Ten dokument |

---

## 8. Następne kroki (Zadanie 3)

1. **Przygotować mappery NBT** dla konwersji świata:
   - `FermentationBarrelNBTMapper`
   - `BrewKettleNBTMapper`
   - `BeeBoxNBTMapper`
   - `MixingVatNBTMapper`

2. **Obsługa inventory**:
   - Mapowanie slotów między wersjami
   - Konwersja itemów (zmiany ID)
   - Obsługa płynów (FluidRegistry)

3. **Testy integracyjne**:
   - Utworzyć testowy świat 1.7.10 z maszynami GrowthCraft
   - Przeprowadzić konwersję
   - Zweryfikować w headless serwerze 1.18.2

---

## 9. Dokumentacja źródłowa

- Kod źródłowy GrowthCraft 1.7.10: dokumentacja z zadania 1
- Kod źródłowy GrowthCraft 1.18.2: `mod_src/actual_src/1.18.2/Growthcraft/`
- Dokumentacja API Minecraft 1.18.2: Forge docs

---

*Dokument utworzony: 2026-02-03*
*Autor: AI Assistant*
