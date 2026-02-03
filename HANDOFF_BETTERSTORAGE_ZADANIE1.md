# Handoff: Better Storage - Zadanie 1 (POPRAWIONE po weryfikacji kodu)

## Podsumowanie sesji

Wykonano pełną analizę bloków, Tile Entities i itemów moda **Better Storage** dla wersji 1.7.10.  
**WERYFIKACJA KODU** wykazała kluczowe błędy w pierwotnej analizie, które zostały poprawione.

### Kluczowe poprawki po weryfikacji kodu:

| Błąd w pierwotnej analizie | Poprawiona wersja | Dowód w kodzie |
|---------------------------|-------------------|----------------|
| ContainerMaterial wpływa na tier/pojemność | **Materiał = TYLKO kosmetyka** (tekstury) | `ContainerMaterial.java:82-87` - tylko `getChestResource()` |
| Mapowanie "per materiał" na Iron Chests | **Pojemność zależy od configu** (27/33/39 slotów) | `GlobalConfig.java:136` - `reinforcedColumns` |
| Crate → Storage Drawers | **Crate → Vanilla Chest** (inna mechanika!) | `CratePileCollection.java:73-88` - osobne pliki |
| Iron Chests ma 12 typów | **Iron Chests ma 7 typów** | `IronChestsTypes.java:32-41` - brak emerald/silver/tin/zinc/steel |
| Ender Backpack → Ender Storage | **Ender Backpack → Vanilla Ender Chest** | `ItemEnderBackpack.java:36` - `player.getInventoryEnderChest()` |
| Locker → Drawers | **Locker → Barrel/Chest** | `TileEntityLocker` - wieloslotowy kontener |

---

## Ukończono

- [x] Analiza kodu źródłowego Better Storage 1.7.10 (`mod_src/1710/actual_src/1.7.10/BetterStorage/repo`)
- [x] **WERYFIKACJA:** ContainerMaterial używany TYLKO do tekstur (nie do pojemności!)
- [x] **WERYFIKACJA:** Pojemność skrzyń zależy od configu `reinforcedColumns` (9/11/13)
- [x] **WERYFIKACJA:** Crate Pile przechowuje dane w osobnych plikach (`data/crates/<id>.dat`)
- [x] **WERYFIKACJA:** Iron Chests 1.18.2 ma tylko 7 typów (zweryfikowane w kodzie)
- [x] **WERYFIKACJA:** Ender Backpack używa vanilla `player.getInventoryEnderChest()`
- [x] Identyfikacja wszystkich bloków/tile entities z paczki `net.mcft.copy.betterstorage.tile`
- [x] Identyfikacja wszystkich itemów z paczki `net.mcft.copy.betterstorage.item`
- [x] Analiza struktury NBT dla każdego Tile Entity
- [x] Stworzenie POPRAWIONEGO mapowania funkcjonalnego na mody 1.18.2
- [x] Identyfikacja bloków bez bezpośrednich odpowiedników

---

## Nowe pliki (POPRAWIONE)

| Plik | Opis |
|------|------|
| `src/converters/betterstorage/INSTRUKCJA_DLA_AGENTA_BETTERSTORAGE_Z1.md` | **POPRAWIONA** instrukcja z weryfikacją kodu |
| `src/converters/betterstorage/BETTER_STORAGE_BLOCKS_AND_TE.md` | **POPRAWIONA** dokumentacja techniczna |
| `docs/mod_mapping_indepth/from/betterstorage_1710_bloki_i_te.md` | **POPRAWIONA** lista bloków/TE 1.7.10 |
| `docs/mod_mapping_indepth/to/betterstorage_1182_mapowanie.md` | **POPRAWIONE** mapowanie na 1.18.2 |

---

## Better Storage 1.7.10 - POPRAWIONA lista bloków

### Kluczowa zmiana: ContainerMaterial = KOSMETYKA

**Dowód z kodu (`ContainerMaterial.java:82-87`):**
```java
public ResourceLocation getChestResource(boolean large) {
    return new BetterStorageResource("textures/models/chest" + (large ? "_large/" : "/") + name + ".png");
}
public ResourceLocation getLockerResource(boolean large) {
    return new BetterStorageResource("textures/models/locker" + (large ? "_large/" : "/") + name + ".png");
}
```

Materiał jest używany TYLKO do:
- Tekstur skrzyń (`getChestResource()`)
- Tekstur szafek (`getLockerResource()`)
- Receptur craftingu (`getReinforcedRecipe()`)

**NIE wpływa na:** pojemność, odporność na wybuchy, logikę zamków!

### Kluczowa zmiana: Pojemność zależy od CONFIGU

**Dowód z kodu (`GlobalConfig.java:136`):**
```java
new IntegerSetting(this, reinforcedColumns, 13).setValidValues(9, 11, 13).setComment(
    "Number of columns in reinforced chests and lockers. Valid values are 9, 11 and 13.");
```

- Wszystkie Reinforced Chests/Lockers mają stałe 3 wiersze (`getRows() = 3`)
- Pojemność: **27, 33 lub 39 slotów** (zależy od configu serwera!)
- **NIE zależy od materiału!**

### Bloki storage z TileEntity

| Blok 1.7.10 | Pojemność | Materiał = kosmetyka? | Zawartość w |
|-------------|-----------|----------------------|-------------|
| **Crate** | 18 (wspólne w pile) | N/A | **Osobny plik** `data/crates/<id>.dat` |
| **Reinforced Chest** | 27/33/39 (config) | ✅ TAK | Chunk NBT |
| **Reinforced Locker** | 36 | ✅ TAK | Chunk NBT |
| **Locker** | 36 | N/A | Chunk NBT |
| **Cardboard Box** | 9 (config) | N/A | Chunk NBT |
| **Crafting Station** | 9+1 | N/A | Chunk NBT |
| **Armor Stand** | 4 (zbroja) | N/A | Chunk NBT |
| **Backpack** | 27 (config) | N/A | Chunk NBT |
| **Ender Backpack** | Vanilla ender chest | N/A | **Vanilla ender chest!** |
| **Present** | 9 | N/A | Chunk NBT |
| **Lockable Door** | - | N/A | Chunk NBT |
| **Flint Block** | - | N/A | Chunk NBT |

---

## POPRAWIONE mapowanie na 1.18.2

### 1. Reinforced Chest → Iron Chests (NIE per materiał!)

| Pojemność BS | Config | Target Iron Chests | ID | Uzasadnienie |
|--------------|--------|-------------------|-----|--------------|
| 27 slotów | 9×3 | **Copper Chest** | `ironchest:copper_chest` | Najbliższy większy (45) |
| 33 slotów | 11×3 | **Iron Chest** | `ironchest:iron_chest` | Najbliższy większy (54) |
| 39 slotów | 13×3 | **Iron Chest** | `ironchest:iron_chest` | Najbliższy większy (54) |

**Materiał ignorujemy** (lub zapisujemy w CustomName jako informacja).

**Zweryfikowane typy Iron Chests 1.18.2** (`IronChestsTypes.java:32-41`):
```java
IRON(54), GOLD(81), DIAMOND(108), COPPER(45), CRYSTAL(108), OBSIDIAN(108), DIRT(1)
```
**NIE istnieją:** ~~emerald~~, ~~silver~~, ~~tin~~, ~~zinc~~, ~~steel~~

### 2. Crate → Vanilla Chest (NIE Drawers!)

**Problem:** Crate Pile to wieloslotowy magazyn z wspólnym inventory.
**Drawers** to per-typ storage - INNA MECHANIKA!

**Poprawne mapowanie:**
- Crate → `minecraft:chest` lub `ironchest:*_chest`
- Każdy crate ze stosu → osobna skrzynia
- Zawartość z pliku `data/crates/<id>.dat` rozdzielona proporcjonalnie

**Plan awaryjny:** Wypakować całą zawartość crate pile do skrzyń obok.

### 3. Locker → Barrel / Chest

- Locker (pionowy) → `minecraft:barrel` (pionowy)
- Lub → `ironchest:iron_chest` (więcej slotów)
- `mirror` (kierunek drzwi) ignorujemy - brak odpowiednika

### 4. Ender Backpack → Vanilla Ender Chest

**Dowód z kodu (`ItemEnderBackpack.java:36`):**
```java
return new InventoryEnderBackpackEquipped(player.getInventoryEnderChest());
```

To używa **vanilla** ender chest! Nie potrzeba Ender Storage modu.
- Target: `minecraft:ender_chest`

### 5. Pozostałe bloki

| BS 1.7.10 | Target 1.18.2 | ID | Uwagi |
|-----------|---------------|-----|-------|
| Cardboard Box | Packing Tape | `packingtape:packed` | Inny system zużywania |
| Crafting Station | Crafting Station | `craftingstation:crafting_station` | Ten sam mod (do weryfikacji NBT) |
| Armor Stand | Vanilla Armor Stand | `minecraft:armor_stand` | Wypakować zawartość! |
| Present | Chest + tabliczka | `minecraft:chest` | Funkcja ozdobna tracona |
| Lockable Door | Supplementaries Lock | `supplementaries:lock_block` | Częściowa funkcjonalność |
| Flint Block | Stone | `minecraft:stone` | Placeholder |

---

## Struktury NBT - kluczowe pola

### Crate - UWAGA!

**TileEntity (chunk) - TYLKO ID:**
```java
{
  crateId: int  // ID stosu, -1 = nowy
}
```

**Dane w pliku (`<world>/data/crates/<id>.dat`):**
```java
{
  data: {
    items: [...],      // Wspólna zawartość całego stosu
    numCrates: int,    // Liczba skrzyń w stosie
    region: {...}      // Obszar stosu
  }
}
```

**Konsekwencja:** Musimy odczytać osobne pliki z `data/crates/`!

### Reinforced Chest / Locker

```java
{
  Items: NBTTagList,        // Zawartość
  Lock: NBTTagCompound,     // Zamek (opcjonalny)
  Material: String,         // "iron", "gold", ... (TYLKO kosmetyka!)
  orientation: byte,        // 0-5 (ForgeDirection)
  CustomName: String        // Opcjonalne
}
```

---

## Statystyki konwersji

| Kategoria | Liczba | Uwagi |
|-----------|--------|-------|
| **Bloki Better Storage 1.7.10** | 12 | |
| **Tile Entities Better Storage** | 12 | |
| **Itemy Better Storage** | ~20 | |
| **Dobre zamienniki w 1.18.2** | 6 | |
| **Częściowe zamienniki** | 4 | |
| **Brak zamiennika** | 2 | |

---

## Problemy konwersji (zaktualizowane)

### 🔴 Krytyczne

1. **Crate Pile - osobne pliki danych**
   - Dane w `<world>/data/crates/<id>.dat`
   - Wymaga specjalnej obsługi przy konwersji
   - **Rozwiązanie:** Odczytać pliki, rozdzielić zawartość

2. **ContainerMaterial był błędnie interpretowany**
   - Pierwotnie: "mapowanie per materiał"
   - Poprawka: "materiał = kosmetyka, pojemność = config"
   - **Rozwiązanie:** Mapować per pojemność, nie per materiał

3. **Enchanty zamków**
   - 7 enchantów BS nie ma odpowiedników
   - **Rozwiązanie:** Utrata funkcji

### 🟡 Średnie

4. **Iron Chests - brakujące typy**
   - NIE ma: emerald, silver, tin, zinc, steel
   - **Rozwiązanie:** Fallback na copper/iron

5. **Armor Stand - brak GUI w vanilla**
   - BS ma GUI z 4 slotami
   - **Rozwiązanie:** Wypakować do skrzyni obok

6. **Cardboard Box - inny system zużywania**
   - BS: zużywa się blok
   - Packing Tape: zużywa się taśma
   - **Rozwiązanie:** Konwertować lub wypakować

---

## Następne kroki (Zadanie 2)

1. **Symulacja Crate Pile:**
   - Jak odczytać pliki `data/crates/<id>.dat`
   - Jak połączyć z TileEntity przez `crateId`
   - Jak rozdzielić zawartość na osobne skrzynie

2. **Weryfikacja Crafting Station NBT:**
   - Porównać format NBT 1.7.10 vs 1.18.2
   - Jeśli różne → przygotować konwerter

3. **Testy na mapie testowej:**
   - Postawić każdy typ bloku BS
   - Sprawdzić faktyczne NBT w save
   - Przeprowadzić próbną konwersję

---

## Zalecenia przed Zadaniem 2

1. **Przygotować testowy świat z Crate Pile:**
   - Postawić stos 3-4 crate
   - Wypełnić itemami
   - Sprawdzić strukturę pliku `data/crates/0.dat`

2. **Zweryfikować config serwera 1.7.10:**
   - Jaka wartość `reinforcedColumns`? (9, 11, czy 13?)
   - To wpłynie na mapowanie pojemności

3. **Zainstalować mody docelowe:**
   - Iron Chests (zweryfikowane 7 typów)
   - Packing Tape (dla Cardboard Box)
   - Crafting Station (do weryfikacji NBT)

---

**Status:** ✅ Zadanie 1 ukończone z POPRAWKAMI po weryfikacji kodu  
**Data:** 2026-02-03  
**Agent:** AI Konwersji Better Storage
