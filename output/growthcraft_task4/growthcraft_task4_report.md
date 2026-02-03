# GrowthCraft - Zadanie 4: Raport analizy

**Data:** 2026-02-03 20:43:20.320104

## 1. Analiza mapy zrodlowej

**Calkowita liczba blokow GrowthCraft:** 162

### Per strefa:

| Strefa | Bloki |
|--------|-------|
| billund | 0 |
| choroszcz | 0 |
| iii_rzesza | 0 |
| rzym | 0 |
| zsrr | 0 |

### Znalezione TileEntity ID:

- `PamFishTrap`: 17 blokow
- `grc.tileentity.beeBox`: 3 blokow
- `grc.tileentity.fermentBarrel`: 135 blokow
- `grc.tileentity.fishTrap`: 7 blokow

## 2. Weryfikacja symulacji

### FermentationBarrel - OK

**Pola NBT w 1.18.2:** inventory, fluid_tank_input_0, CurrentProcessTicks, MaxProcessTicks, CustomName

- Tank pojemnosc: 4000mB
- Inventory: 1 slot (katalizator)
- Logika: tickClock++ do tickMax, potem zamiana plynu
- tickMax = recipe.processingTime * outputMultiplier

### BrewKettle - OK

**Pola NBT w 1.18.2:** inventory, fluid_tank_input_0, fluid_tank_output_0, CurrentProcessTicks, MaxProcessTicks, CustomName

- Tanki pojemnosc: 4000mB kazdy
- Inventory: 3 sloty (0=pokrywka, 1=input, 2=byproduct)
- Logika: Wymaga pokrywki dla niektorych receptur
- Byproduct: Losowy drop z szansa z receptury

### BeeBox - OK

**Pola NBT w 1.18.2:** inventory, CurrentProcessTicks, CustomName

- Inventory: 28 slotow (slot 0 = pszczoly)
- tickMax: Z configu (GrowthcraftApiaryConfig.getBeeBoxMaxProcessingTime())
- Logika: Co tickMax tickow - rozmnażanie pszczol, produkcji plastrow
- Slot 0: Pszczyoly musza miec tag BEE=1

### MixingVat (CheeseVat) - OK

**Pola NBT w 1.18.2:** inventory, InputFluidTank, ReagentFluidTank, CurrentProcessTicks, MaxProcessTicks, IsActivated, RequiresHeatSource, ActivationTool, ResultActivationTool, CustomName

- InputTank pojemnosc: 4000mB
- ReagentTank pojemnosc: 1000mB
- KLUCZOWA ZMIANA: Wymagana aktywacja (IsActivated)
- Aktywacja: Narzedziem (miecz) + cieplo
- Result: Pobierany specjalnym narzedziem (cheese_cloth)
- ROZNICA: W 1.7.10 brak automatycznej aktywacji - konwerter musi ja symulowac

## 3. Pokrycie kodu konwertera

- **Obslugiwane bloki:** 138 (85.19%)
- **Nieobslugiwane:** 7
- **Inne mody:** 17
- **Nieznane:** 17

### Szczegoly per TileEntity:

| TileEntity | Liczba | Status |
|------------|--------|--------|
| `grc.tileentity.fermentBarrel` | 135 | [OK] |
| `PamFishTrap` | 17 | [OTHER_MOD] |
| `grc.tileentity.fishTrap` | 7 | [MISSING] |
| `grc.tileentity.beeBox` | 3 | [OK] |

## 4. Wnioski i rekomendacje

### Pokrycie kodu: DOBRE

Konwerter obsluguje 85.19% blokow GrowthCraft na mapie.

### Nieobslugiwane TileEntity wymagajace konwerterow:

- [ ] `grc.tileentity.fermentBarrel` (135 blokow na mapie)
- [ ] `PamFishTrap` (17 blokow na mapie)
- [ ] `grc.tileentity.fishTrap` (7 blokow na mapie)
- [ ] `grc.tileentity.beeBox` (3 blokow na mapie)

### Zgodnosc symulacji z kodem 1.18.2:

Wszystkie zaimplementowane symulacje (FermentationBarrel, BrewKettle, BeeBox, MixingVat) zostaly zweryfikowane z kodem zrodlowym GrowthCraft 1.18.2 i sa zgodne z jego logika.

