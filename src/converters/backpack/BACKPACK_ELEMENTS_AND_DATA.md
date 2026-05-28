# Backpack (Eydamos) 1.7.10 — Dokumentacja elementów i danych

> **Mod:** Backpack 2.0.1 (Eydamos) 1.7.10 → Sophisticated Backpacks 1.18.2  
> **Data:** 2026-05-28  
> **Status:** Zadanie 1 ukończone  
> **Źródło prawdy:** Dekompilacja JAR `backpack-2.0.1-1.7.x.jar` (CFR 0.152)

---

## ⚠️ Kluczowe ustalenie wstępne

**Mod Backpack (Eydamos) NIE dodaje żadnych bloków ani Tile Entities w świecie.**  
Jedyne elementy to itemy (przedmioty) oraz zewnętrzne pliki `.dat` w folderze `backpacks/`.

Konwersja tego moda to **wyłącznie konwersja danych pozachunkowych** (item NBT + pliki `.dat` + `playerdata`), a nie remap bloków w regionach `.mca`.

---

## 1. Elementy dodawane przez mod

### 1.1. Itemy

| ID (unlocalized → registry) | Klasa | Opis |
|-----------------------------|-------|------|
| `Backpack:backpack` | `ItemBackpack` extends `ItemBackpackBase` | Plecaki w wielu tierach i kolorach, w tym ender |
| `Backpack:workbenchbackpack` | `ItemWorkbenchBackpack` extends `ItemBackpackBase` | Plecaki z wbudowanym craftingiem (9 lub 18 slotów) |
| `Backpack:boundLeather` | `ItemLeather` | Materiał craftingowy |
| `Backpack:tannedLeather` | `ItemLeather` | Materiał craftingowy |

### 1.2. System zapisu danych

| Lokalizacja | Klasa odpowiedzialna | Zawartość |
|-------------|----------------------|-----------|
| `<world>/backpacks/backpacks/<UUID>.dat` | `BackpackSave` | Zawartość plecaków (inventory per UUID) |
| `<world>/backpacks/player/<UUID>.dat` | `PlayerSave` | Dane gracza: personalBackpack, personalBackpackOpen |
| `<world>/backpacks/backpacks/<UUID>.dat_old` | `SaveFileHandler` | Plik awaryjny (fallback) |

---

## 2. ItemBackpack — struktura i logika

### 2.1. Damage / metadata

`damage` (meta) określa **tier** i **wariant/kolor**:

```java
int tier = damage / 100;  // 0 = small, 1 = medium, 2 = big
int meta = damage % 100;  // 0 = default, 1-16 = kolory, 17 = workbench, 99 = ender
```

**Tablice referencyjne** (`ItemsBackpack.java:44-47`):

```java
BACKPACK_TIERS = {"", "medium", "big"};
BACKPACK_COLORS = {"", "black", "red", "green", "brown", "blue", "purple", "cyan",
    "lightGray", "gray", "pink", "lime", "yellow", "lightBlue", "magenta", "orange",
    "white", "ender"};
```

**Warianty `Backpack:backpack`:**

| Damage | Tier | Meta | Kolor | Uwagi |
|--------|------|------|-------|-------|
| 0 | small | 0 | default | |
| 1-16 | small | 1-16 | 16 kolorów | |
| 99 | small | 99 | ender | Ender Backpack (zawsze 27 slotów, vanilla ender chest) |
| 100-116 | medium | 0-16 | 16 kolorów | Medium (istnieje w kodzie, pominięty w ikonach) |
| 200-216 | big | 0-16 | 16 kolorów | Big |
| 31999 | — | — | ender | Specjalna wartość `ENDERBACKPACK` |

**Warianty `Backpack:workbenchbackpack`:**

| Damage | Tier | Meta | Rozmiar | Uwagi |
|--------|------|------|---------|-------|
| 17 | small | 17 | 9 slotów | Workbench backpack |
| 217 | big | 17 | 18 slotów | Big workbench backpack |

### 2.2. NBT itemu (ItemStack tag)

Każdy plecak w inwentarzu gracza (lub na ziemi) przechowuje:

```java
{
  backpack-UID: String   // UUID generowany przy pierwszym użyciu (BackpackSave.initialize)
  name: String           // Unlocalized name + ".name", np. "item.backpack_big_red.name"
  customName: String     // Opcjonalna nazwa nadana przez gracza (Shift+PPM)
}
```

**Źródło:** `ItemBackpackBase.java:71-106`, `BackpackSave.java:40-86`

---

## 3. BackpackSave — struktura pliku `.dat`

Plik `<world>/backpacks/backpacks/<UUID>.dat` zawiera NBT Compound z następującymi polami:

| Pole | Typ | Opis | Źródło |
|------|-----|------|--------|
| `backpack-UID` | String | UUID plecaka (taki sam jak nazwa pliku) | `BackpackSave.java:30-34` |
| `size` | Int | Liczba slotów inventory | `BackpackSave.java:111-120` |
| `slotsPerRow` | Int | Zazwyczaj 9 | `BackpackSave.java:122-130` |
| `type` | Byte | 1 = normal backpack, 2 = workbench backpack | `BackpackSave.java:134-144`, `BackpackUtil.java:52-59` |
| `intelligent` | Boolean | `true` jeśli workbench backpack ma crafting (zwykle tak) | `BackpackSave.java:100-109` |
| `backpackInventories` | Compound | Wrapper na listy inventory | `BackpackSave.java:146-157` |
| `backpackInventories.backpack` | NBTTagList (type 10) | Lista itemów w głównym inventory | `BackpackSave.java:146-157` |

### 3.1. Format itemu w liście `backpack`

Standardowy format Minecraft 1.7.10 `NBTTagCompound` per slot:

```java
{
  slot: Byte/Short   // Numer slotu
  id: Short/String   // ID itemu (zależnie od wersji zapisu)
  Count: Byte        // Ilość
  Damage: Short      // Meta/damage itemu
  tag: Compound      // Opcjonalne NBT itemu
}
```

### 3.2. Rozmiary slotów (logika inicializacji)

```java
// BackpackSave.java:64-77
if (meta == 99) {
    size = 27;                          // Ender backpack
} else if (meta < 17 && tier == 2) {
    size = ConfigurationBackpack.BACKPACK_SLOTS_L;  // Big (domyślnie 54)
} else if (meta < 17 && tier == 0) {
    size = ConfigurationBackpack.BACKPACK_SLOTS_S;  // Small (domyślnie 27)
} else if (meta == 17 && tier == 0) {
    size = 9;                           // Workbench small
} else if (meta == 17 && tier == 2) {
    size = 18;                          // Workbench big
}
```

**Uwaga:** Wartości `BACKPACK_SLOTS_S` i `BACKPACK_SLOTS_L` pochodzą z configu moda. W naszej mapie mogą być inne niż domyślne (27 / 54).

---

## 4. PlayerSave — struktura pliku `.dat`

Plik `<world>/backpacks/player/<UUID>.dat` zawiera:

| Pole | Typ | Opis | Źródło |
|------|-----|------|--------|
| `personalBackpack` | Compound (ItemStack NBT) | ItemStack plecaka osobistego (np. noszonego na plecach) | `PlayerSave.java:54-76` |
| `personalBackpackOpen` | String | UUID aktualnie otwartego plecaka osobistego | `PlayerSave.java:36-52` |

**Plecak osobisty** to ten sam `ItemStack` z tagiem `backpack-UID`, więc jego zawartość jest w `backpacks/backpacks/<UUID>.dat`.

---

## 5. Event Handlery (kontekst konwersji)

### 5.1. Pickup item (`BackpackUtil.java:62-78`)

Jeśli gracz ma plecak osobisty (`personalBackpack`) z włączonym auto-pickupem, mod próbuje włożyć podobne itemy do tego plecaka.  
**Konwersja:** Mechanizm auto-pickup jest specyficzny dla moda Eydamos; Sophisticated Backpacks ma własny system (upgrades). Nie da się bezpośrednio przenieść.

### 5.2. Personal backpack slot

Mod dodaje dodatkowy slot na plecak (renderowany na plecach gracza). W `PlayerSave` przechowywany jest ItemStack tego plecaka.  
**Konwersja:** W 1.18.2 plecaki są trzymane w zwykłym inventory lub w Curios/Back slot (jeśli zainstalowany). Do rozstrzygnięcia w Zadaniu 3.

---

## 6. Mapowanie na Sophisticated Backpacks 1.18.2

### 6.1. Architektura danych w SB 1.18.2

Sophisticated Backpacks **również używa zewnętrznego storage** per UUID plecaka — nie przechowuje inventory bezpośrednio w NBT itemStack!

**ItemStack NBT** (tagi na itemie plecaka):
```java
{
  clothColor: Int,          // Kolor główny (domyślnie 13394234)
  borderColor: Int,         // Kolor obramowania (domyślnie 6434330)
  contentsUuid: IntArray[4] // UUID zawartości (zapisany jako int[])
  inventorySlots: Int,      // Opcjonalne nadpisanie domyślnej liczby slotów
  upgradeSlots: Int,        // Opcjonalne nadpisanie liczby slotów upgrade'ów
  sortBy: String,           // "NAME", "COUNT", "TAGS"
  columnsTaken: Int         // Zajęte kolumny (Inception)
}
```

**BackpackStorage** (SavedData w `<world>/data/sophisticatedbackpacks.dat`):
```java
{
  backpackContents: [
    {
      uuid: IntArray[4],
      contents: {
        inventory: {          // ItemStackHandler NBT
          Size: Int,
          Items: [{ Slot: Int, id: String, Count: Int, tag: Compound, realCount: Int }]
        },
        upgradeInventory: {   // ItemStackHandler NBT
          Size: Int,
          Items: [{ Slot: Int, id: String, Count: Int, tag: Compound }]
        },
        settings: Compound    // Ustawienia (memory, noSort, itemDisplay, itp.)
      }
    }
  ]
}
```

**Źródła:** `BackpackWrapper.java:40-53`, `BackpackStorage.java:25-87`, `InventoryHandler.java:30-32`

### 6.2. Itemy plecaków w SB (tiers)

| ID itemu | Domyślne sloty | Upgrade slots | Uwagi |
|----------|---------------|---------------|-------|
| `sophisticatedbackpacks:backpack` | 27 | 1 | Leather (domyślny) |
| `sophisticatedbackpacks:copper_backpack` | 45 | 1 | |
| `sophisticatedbackpacks:iron_backpack` | 54 | 2 | |
| `sophisticatedbackpacks:gold_backpack` | 81 | 3 | |
| `sophisticatedbackpacks:diamond_backpack` | 108 | 5 | |
| `sophisticatedbackpacks:netherite_backpack` | 120 | 7 | Fire resistant |

**Źródło:** `Config.java:140-145`, `ModItems.java:141-152`

### 6.3. Mapowanie elementów

| Element 1.7.10 | Docelowy element 1.18.2 | Uwagi |
|----------------|-------------------------|-------|
| `Backpack:backpack` small (27 slotów) | `sophisticatedbackpacks:backpack` (leather) | Domyślny plecak, 27 slotów |
| `Backpack:backpack` big (54 slotów) | `sophisticatedbackpacks:iron_backpack` | 54 slotów, 2 upgrade slots |
| `Backpack:backpack` medium (jeśli używany) | `sophisticatedbackpacks:copper_backpack` | 45 slotów |
| `Backpack:backpack` ender (99/31999) | `sophisticatedbackpacks:iron_backpack` | Brak ender upgrade w SB; zachować customName |
| `Backpack:workbenchbackpack` | `sophisticatedbackpacks:backpack` + `sophisticatedcore:crafting_upgrade` | Włożyć upgrade do `upgradeInventory` |
| `backpacks/backpacks/<UUID>.dat` | `data/sophisticatedbackpacks.dat` → `backpackContents[]` | Stworzyć nowy UUID lub przenieść istniejący |
| `backpacks/player/<UUID>.dat` | `playerdata/<UUID>.dat` (inventory) / Curios | Plecak osobisty → ręka/Curios slot |

### 6.4. Kolory

SB używa **dwóch kolorów RGB** (`clothColor` + `borderColor`) zamiast jednego koloru dye.  
Kolory z `Backpack:backpack` (meta 0-16) mapować na `DyeColor.values()` i obliczyć RGB przez `ColorHelper.getColor(dyeColor.getTextureDiffuseColors())`.

**Źródło:** `BackpackItem.java:126-141`, `BackpackWrapper.java:40-43`

### 6.5. Upgrade'y

| Funkcja 1.7.10 | Upgrade SB 1.18.2 | ID |
|----------------|-------------------|-----|
| Workbench (crafting) | Crafting Upgrade | `sophisticatedcore:crafting_upgrade` |
| Auto-pickup | Pickup Upgrade / Magnet Upgrade | `sophisticatedbackpacks:pickup_upgrade` itp. |

Ender Backpack nie ma bezpośredniego odpowiednika. Vanilla ender chest to osobny blok/item.

---

## 7. Source Mapping

### 7.1. Kod źródłowy 1.7.10 (dekompilacja)

| Klasa | Lokalizacja dekompilacji | Kluczowe metody/pola |
|-------|--------------------------|----------------------|
| `Backpack.java` | `mod_src/code_from_jar/backpack_1710/de/eydamos/backpack/Backpack.java` | Rejestracja itemów, init moda |
| `ItemsBackpack.java` | `mod_src/code_from_jar/backpack_1710/de/eydamos/backpack/item/ItemsBackpack.java` | Definicje itemów, tablice tierów i kolorów |
| `ItemBackpackBase.java` | `mod_src/code_from_jar/backpack_1710/de/eydamos/backpack/item/ItemBackpackBase.java` | Logika użycia, NBT itemu, tooltip |
| `ItemBackpack.java` | `mod_src/code_from_jar/backpack_1710/de/eydamos/backpack/item/ItemBackpack.java` | Ikony, warianty wizualne |
| `ItemWorkbenchBackpack.java` | `mod_src/code_from_jar/backpack_1710/de/eydamos/backpack/item/ItemWorkbenchBackpack.java` | Workbench backpack, intelligent |
| `BackpackSave.java` | `mod_src/code_from_jar/backpack_1710/de/eydamos/backpack/saves/BackpackSave.java` | Zapis/odczyt pliku .dat plecaka |
| `PlayerSave.java` | `mod_src/code_from_jar/backpack_1710/de/eydamos/backpack/saves/PlayerSave.java` | Zapis/odczyt pliku .dat gracza |
| `SaveFileHandler.java` | `mod_src/code_from_jar/backpack_1710/de/eydamos/backpack/handler/SaveFileHandler.java` | IO plików .dat |
| `BackpackUtil.java` | `mod_src/code_from_jar/backpack_1710/de/eydamos/backpack/util/BackpackUtil.java` | Typy, porównywanie UUID, pickup |
| `ConfigurationBackpack.java` | `mod_src/code_from_jar/backpack_1710/de/eydamos/backpack/misc/ConfigurationBackpack.java` | Config: BACKPACK_SLOTS_S, BACKPACK_SLOTS_L |

### 7.2. Kod źródłowy 1.18.2

Repozytoria pobrane do `mod_src/actual_src/1.18.2/`:

| Klasa | Lokalizacja | Kluczowe metody/pola |
|-------|-------------|----------------------|
| `BackpackItem.java` | `SophisticatedBackpacks/.../backpack/BackpackItem.java` | Rejestracja, kolory, place, use |
| `BackpackWrapper.java` | `SophisticatedBackpacks/.../backpack/wrapper/BackpackWrapper.java` | NBT itemu: `clothColor`, `borderColor`, `contentsUuid` |
| `BackpackStorage.java` | `SophisticatedBackpacks/.../backpack/BackpackStorage.java` | SavedData: `backpackContents`, `accessLogRecords` |
| `BackpackInventoryHandler.java` | `SophisticatedBackpacks/.../backpack/wrapper/BackpackInventoryHandler.java` | Inventory handler (limit slotów, inception) |
| `ModItems.java` | `SophisticatedBackpacks/.../init/ModItems.java` | Definicje itemów: backpack, copper, iron, gold, diamond, netherite + upgrade'y |
| `Config.java` | `SophisticatedBackpacks/.../Config.java` | Domyślne sloty: leather=27, copper=45, iron=54, gold=81, diamond=108, netherite=120 |
| `InventoryHandler.java` | `SophisticatedCore/.../inventory/InventoryHandler.java` | Format NBT `inventory`: `Size`, `Items[]`, `realCount` |
| `UpgradeHandler.java` | `SophisticatedCore/.../upgrades/UpgradeHandler.java` | Format NBT `upgradeInventory`: `Size`, `Items[]` |
| `BackpackSettingsHandler.java` | `SophisticatedBackpacks/.../backpack/wrapper/BackpackSettingsHandler.java` | NBT `settings` |
| `CuriosCompat.java` | `SophisticatedBackpacks/.../compat/curios/CuriosCompat.java` | Wsparcie dla Curios API (slot "back") |

---

## 8. Dane na mapie źródłowej

| Lokalizacja | Liczba plików | Opis |
|-------------|---------------|------|
| `mapa_1710/backpacks/backpacks/` | ~700 plików `.dat` | Zawartość plecaków (różne rozmiary, od 81 B do ~100 KB) |
| `mapa_1710/backpacks/player/` | ~20 plików `.dat` | Plecaki osobiste graczy |

**Weryfikacja obecności w regionach `.mca`:**  
Mod Backpack nie rejestruje bloków ani Tile Entities, więc nie ma wpisów w chunkach. Itemy plecaków mogą występować wyłącznie jako:
- EntityItem (wyrzucone na ziemię) — w `.mca` jako entity
- ItemStack w `playerdata/` — w plikach graczy
- ItemStack w Tile Entities innych modów (skrzynie, itp.)

---

## 9. Otwarte pytania na Zadanie 2/3

1. **Konwersja itemów 1.7.10 → 1.18.2:** Jak dokładnie wygląda format `id` w itemach z 1.7.10 (numeryczny vs string)? Czy istnieje już w projekcie resolver ID?
2. **Ender backpack:** Brak odpowiednika w SB. Rozwiązanie: zastąpić `iron_backpack` z customName="Ender Backpack"? Czy po prostu `backpack` (leather)?
3. **Personal backpack slot:** W SB plecak może być noszony w Curios API (slot "back") lub trzymany w ręce. W 1.7.10 mod Eydamos miał dedykowany slot. Czy na docelowym serwerze jest Curios API?
4. **Config rozmiarów:** Jakie były faktyczne wartości `BACKPACK_SLOTS_S` i `BACKPACK_SLOTS_L` na serwerze? (sprawdzić w `modpack_1710/config/` lub `pliki_globalne_serwer_1710/config/`)
5. **Auto-pickup / intelligent:** Czy przenosić te funkcje jako upgrade'y (Pickup/Magnet), czy zostawić bez upgrade'ów?
6. **Crafting upgrade NBT:** Czy `crafting_upgrade` wymaga dodatkowych tagów w NBT itemu upgrade'u (np. zawartość grid crafting)?

---

**Status:** ✅ Zadanie 1 ukończone (z analizą kodu źródłowego 1.18.2)  
**Następny krok:** Zadanie 2 — Symulacje działania funkcjonalności (tworzenie `BackpackSave` 1.7.10 → `BackpackStorage` + `BackpackWrapper` 1.18.2)
