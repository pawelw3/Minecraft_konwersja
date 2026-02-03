# Handoff: Jammy Furniture Reborn - Zadanie 2

## Podsumowanie sesji

Wykonano **Zadanie 2** dla modu Jammy Furniture Reborn - przygotowano **5 symulacji funkcjonalności moda** w Pythonie, bazując na dokładnej analizie kodu źródłowego 1.7.10. Symulacje pokrywają wszystkie nietrywialne funkcjonalności: lodówkę/zamrażarkę, kuchenkę, zmywarkę/pralkę, stół craftingowy/szafki oraz kosz na śmieci/zegar.

---

## Ukończono

### Przygotowano 5 symulacji funkcjonalności

| Symulacja | Plik | Funkcjonalność | Tile Entity 1.7.10 |
|-----------|------|----------------|-------------------|
| **Lodówka/Zamrażarka** | `fridge_freezer_simulation.py` | Storage 9 slotów | `TileEntityIronBlocksOne` (subBlock 0,4) |
| **Kuchenka** | `cooker_simulation.py` | Dual furnace, gotowanie jedzenia | `TileEntityIronBlocksOne` (subBlock 8) |
| **Zmywarka/Pralka** | `dishwasher_washingmachine_simulation.py` | Naprawa narzędzi/zbroi | `TileEntityIronBlocksTwo` (subBlock 0,4) |
| **Crafting/Szafki** | `crafting_cupboard_simulation.py` | Crafting grid 3x2, storage | `TileEntityWoodBlocksOne/Two/Four` |
| **Kosz/Zegar** | `rubbishbin_clock_simulation.py` | Auto-clear, dźwięki | `TileEntityIronBlocksOne/WoodBlocksOne` |

---

## Szczegóły symulacji

### 1. Lodówka i Zamrażarka (`fridge_freezer_simulation.py`)

**Na podstawie:** `TileEntityIronBlocksOne.java`

**Funkcjonalność 1.7.10:**
- subBlock 0 = Lodówka (Fridge) - 9 slotów
- subBlock 4 = Zamrażarka (Freezer) - 9 slotów
- Brak aktywnej logiki - tylko storage

**Kluczowe klasy:**
```python
class FridgeFreezerInventory:
    slots: List[Optional[ItemStack]]  # 9 slotów
    
class FridgeFreezerSimulator:
    def tick() -> None  # Brak akcji - tylko storage
    def to_nbt_1710() -> Dict  # Eksport NBT 1.7.10
    def to_nbt_1182() -> Dict  # Eksport NBT 1.18.2 (Macaw's)
```

**Mapowanie 1.18.2:**
- `mcwfurnitures:refrigerator[part=lower]` - lodówka
- `mcwfurnitures:refrigerator[part=upper]` - zamrażarka

---

### 2. Kuchenka (`cooker_simulation.py`)

**Na podstawie:** `TileEntityIronBlocksOne.java`, `CookerRecipes.java`

**Funkcjonalność 1.7.10:**
- Dual furnace (dwa niezależne sloty gotowania)
- Slot 0: 200 ticków, Slot 1: 150 ticków (szybciej!)
- Tylko ItemFood (jedzenie)
- 5 slotów: 2x input, 1x fuel, 2x output

**Logika tick'u (z kodu źródłowego):**
```java
// Z TileEntityIronBlocksOne.updateEntity()
if (isBurning() && canSmelt(0)) {
    cookerCookTime0++;
    if (cookerCookTime0 == 200) {
        smeltItem(0);
    }
}
if (isBurning() && canSmelt(1)) {
    cookerCookTime1++;
    if (cookerCookTime1 >= 150) {
        smeltItem(1);
    }
}
```

**Symulacja w Pythonie:**
```python
class CookerSimulator:
    def tick() -> Dict[str, Any]:
        # 1. Zmniejsz burn_time
        # 2. Dodaj paliwo jeśli trzeba
        # 3. Gotuj slot 0 (200 ticks)
        # 4. Gotuj slot 1 (150 ticks)
        # 5. Zwróć zmiany
```

**Mapowanie 1.18.2:**
- `mcwfurnitures:stove` - zachowuje 5 slotów inventory

---

### 3. Zmywarka i Pralka (`dishwasher_washingmachine_simulation.py`)

**Na podstawie:** `TileEntityIronBlocksTwo.java`, `DishwasherRecipes.java`, `WashingMachineRecipes.java`

**Funkcjonalność 1.7.10:**
- **Zmywarka:** Naprawia narzędzia (miecze, kilofy, siekiery, motyki, łopaty)
- **Pralka:** Naprawia zbroję (wszystkie typy)
- 4 sloty na przedmioty + 1 slot paliwa
- Niezależne timery dla każdego slotu

**Czasy naprawy (zmywarka):**
| Materiał | Czas (ticki) |
|----------|--------------|
| Wood | 1500 |
| Stone | 4000 |
| Iron | 4800 |
| Gold | 6000 |
| Diamond | 7200 |

**Logika naprawy (z kodu źródłowego):**
```java
// Z DishwasherRecipes.getSmeltingResult()
if (item instanceof ItemSword) {
    rtn = itemStack.copy();
    rtn.setItemDamage(0);  // Reset damage!
}
```

**Symulacja w Pythonie:**
```python
class ApplianceSimulator:
    def can_repair(slot_index: int) -> bool
    def get_repair_time(slot_index: int) -> int
    def repair_item(slot_index: int) -> bool  # Reset damage to 0
    def tick() -> Dict  # Progress + auto-repair
```

**Mapowanie 1.18.2:**
- Brak bezpośredniego odpowiednika!
- Placeholder: `mcwfurnitures:kitchen_cabinet`

---

### 4. Stół Craftingowy i Szafki (`crafting_cupboard_simulation.py`)

**Na podstawie:** `TileEntityWoodBlocksOne.java`, `TileEntityWoodBlocksTwo.java`, `TileEntityWoodBlocksFour.java`

**Crafting Side (subBlock 13):**
- **UWAGA:** Nietypowy grid 3x2 (nie 3x3!)
- 6 slotów inventory
- Przechowuje crafting grid w TE!

**Kitchen Cupboard (subBlock 0-7):**
- 9 slotów
- subBlock 0-3 = zamknięta, 4-7 = otwarta (półki)
- TV ma osobną logikę (tvOn timestamp)

**Wardrobe (subBlock 0-7):**
- 20 slotów inventory (bardzo duża!)
- subBlock 0-3 = dolna, 4-7 = górna

**Problem konwersji Crafting Side:**
```python
def get_block_id_1182_fallback(self) -> str:
    # Problem: vanilla crafting_table nie ma TE w 1.18.2!
    # Opcje:
    # 1. minecraft:crafting_table - stracimy inventory
    # 2. supplementaries:safe - zachowa inventory
    # 3. Zrzucić itemy na ziemię
    return "minecraft:crafting_table"
```

**Mapowanie 1.18.2:**
- Szafka: `mcwfurnitures:oak_kitchen_cabinet`
- Szafa: `mcwfurnitures:oak_wardrobe`

---

### 5. Kosz na śmieci i Zegar (`rubbishbin_clock_simulation.py`)

**Rubbish Bin (subBlock 12):**
- 27 slotów inventory (bardzo duży!)
- Automatyczne czyszczenie co 60 sekund (60000ms)
- Osobne dźwięki: trashopen, trashclosed

**Clock (subBlock 5):**
- Dźwięk "clock-tick" co 2 sekundy
- Dźwięk "clock-dong" o 12:00 i 0:00
- Konwersja czasu gry: `hour = (worldTime / 1000 + 6) % 24`

**Logika czyszczenia kosza:**
```java
// Z TileEntityIronBlocksOne.updateEntity()
if (subBlock == 12) {
    if (System.currentTimeMillis() - lastClearance >= 60000L) {
        removeAllItems();
        lastClearance = System.currentTimeMillis();
    }
}
```

**Problem konwersji kosza:**
- Macaw's trash_can ma tylko 1 slot lub auto-usuwa
- Jammy ma 27 slotów
- **Rozwiązanie:** Zachować tylko pierwszy item lub zrzucić wszystko

---

## Struktura plików

```
src/jammy_furniture/
├── __init__.py                              # Eksportuje wszystkie klasy
└── simulations/
    ├── fridge_freezer_simulation.py         # Lodówka/Zamrażarka
    ├── cooker_simulation.py                 # Kuchenka
    ├── dishwasher_washingmachine_simulation.py  # Zmywarka/Pralka
    ├── crafting_cupboard_simulation.py      # Crafting/Szafki/Szafa
    └── rubbishbin_clock_simulation.py       # Kosz/Zegar
```

---

## Nowe pliki

| Plik | Opis | Linie |
|------|------|-------|
| `src/jammy_furniture/__init__.py` | Moduł Pythona | ~85 |
| `src/jammy_furniture/simulations/fridge_freezer_simulation.py` | Symulacja lodówki | ~280 |
| `src/jammy_furniture/simulations/cooker_simulation.py` | Symulacja kuchenki | ~400 |
| `src/jammy_furniture/simulations/dishwasher_washingmachine_simulation.py` | Symulacja AGD | ~450 |
| `src/jammy_furniture/simulations/crafting_cupboard_simulation.py` | Symulacja storage | ~400 |
| `src/jammy_furniture/simulations/rubbishbin_clock_simulation.py` | Symulacja kosza/zegara | ~300 |
| `HANDOFF_JAMMY_ZADANIE2.md` | Ten dokument | ~250 |

**Łącznie:** ~1900 linii kodu symulacji

---

## Testowanie symulacji

Każda symulacja ma funkcję `run_simulation_tests()`:

```bash
# Test lodówki
python src/jammy_furniture/simulations/fridge_freezer_simulation.py

# Test kuchenki
python src/jammy_furniture/simulations/cooker_simulation.py

# Test zmywarki/pralki
python src/jammy_furniture/simulations/dishwasher_washingmachine_simulation.py

# Test crafting/szafek
python src/jammy_furniture/simulations/crafting_cupboard_simulation.py

# Test kosza/zegara
python src/jammy_furniture/simulations/rubbishbin_clock_simulation.py
```

---

## Problemy konwersji zidentyfikowane przez symulacje

### 1. Crafting Side - brak odpowiednika
- **Problem:** 3x2 crafting grid w Jammy vs 3x3 w vanilla
- **Problem:** Vanilla crafting_table nie ma TE w 1.18.2
- **Rozwiązanie:** Użyć `supplementaries:safe` lub zrzucić itemy

### 2. Zmywarka/Pralka - brak odpowiednika
- **Problem:** Brak funkcjonalności naprawy w Macaw's Furniture
- **Rozwiązanie:** Placeholder `kitchen_cabinet` + strata funkcjonalności

### 3. Kosz na śmieci - różna pojemność
- **Problem:** Jammy ma 27 slotów, Macaw's ma 1 slot
- **Rozwiązanie:** Zachować tylko pierwszy item

### 4. Zegar - brak dźwięków
- **Problem:** Supplementaries clock_block nie ma dźwięków
- **Rozwiązanie:** Akceptowalna strata (tylko dekoracja)

---

## Następne kroki (Zadanie 3)

1. **Stworzyć testowy świat 1.7.10**
   - Postawić wszystkie bloki Jammy Furniture
   - Wypełnić inventory różnymi przedmiotami
   - Przetestować symulacje na rzeczywistych danych

2. **Porównać z 1.18.2**
   - Uruchomić mody 1.18.2 (Macaw's, Supplementaries, Handcrafted)
   - Sprawdzić czy symulacje odpowiadają rzeczywistości
   - Zweryfikować formaty NBT

3. **Zaimplementować konwerter**
   - Użyć symulacji jako bazy dla kodu konwersji
   - Obsłużyć edge cases (np. pełny kosz na śmieci)

---

## Decyzje projektowe

### 1. Granularność symulacji
**Decyzja:** Symulować tick-po-tick dla maszyn (kuchenka, zmywarka).

**Uzasadnienie:**
- Pozwala przetestować logikę czasową
- Ułatwia znalezienie błędów w kodzie źródłowym
- Daje pewność co do zachowania w 1.18.2

### 2. Format NBT
**Decyzja:** Implementować `to_nbt_1710()` i `to_nbt_1182()`.

**Uzasadnienie:**
- Bezpośrednia kompatybilność z Minecraft
- Ułatwia testowanie konwersji
- Dokumentuje różnice między wersjami

### 3. ItemStack
**Decyzja:** Wspólna klasa `ItemStack` we wszystkich symulacjach.

**Uzasadnienie:**
- Spójność między symulacjami
- Łatwiejsza konwersja inventory
- Dokładne odwzorowanie NBT

---

## Referencje

### Kod źródłowy Jammy 1.7.10:
- `mod_src/1710/code_from_jar/1.7.10/JammyFurniture/decompiled/`

### Kluczowe pliki:
- `TileEntityIronBlocksOne.java` - Lodówka, Kuchenka, Kosz
- `TileEntityIronBlocksTwo.java` - Zmywarka, Pralka
- `TileEntityWoodBlocksOne.java` - Crafting, Zegar
- `TileEntityWoodBlocksTwo.java` - Szafki
- `TileEntityWoodBlocksFour.java` - Szafa
- `CookerRecipes.java` - Przepisy kuchenki
- `DishwasherRecipes.java` - Przepisy zmywarki
- `WashingMachineRecipes.java` - Przepisy pralki

---

*Dokument utworzony: 2026-02-03*  
*Status: Zadanie 2 ukończone - symulacje gotowe*
