# Better Storage - Dokumentacja bloków i Tile Entities (POPRAWIONA)

> **Mod:** Better Storage 1.7.10 → Iron Chests / Storage Drawers / Sophisticated Storage 1.18.2  
> **Data:** 2026-02-03  
> **Status:** Zadanie 1 ukończone z poprawkami po weryfikacji kodu

---

## ⚠️ KLUCZOWE POPRAWKI PO WERYFIKACJI KODU

### 1. ContainerMaterial jest CZYSTO KOSMETYCZNY
- Używany TYLKO do tekstur (`getChestResource()`, `getLockerResource()`)
- NIE wpływa na pojemność, odporność, ani logikę
- Pojemność zależy od configu `reinforcedColumns` (9/11/13) × 3 wiersze = 27/33/39 slotów

### 2. Crate Pile - zawartość w osobnych plikach
- Dane przechowywane w: `<world>/data/crates/<id>.dat`
- TileEntityCrate przechowuje tylko `crateId` (referencję)
- Konwersja wymaga odczytania osobnych plików!

### 3. Iron Chests 1.18.2 ma tylko 7 typów
**Istnieją:** iron, gold, diamond, copper, crystal, obsidian, dirt  
**NIE istnieją:** emerald, silver, tin, zinc, steel

### 4. Ender Backpack używa vanilla ender chest
- `player.getInventoryEnderChest()` - to vanilla!
- Target: `minecraft:ender_chest` (nie Ender Storage)

---

## Bloki i Tile Entities

### 1. Crate (`betterstorage:crate`)

**TileEntity:** `TileEntityCrate`

| Właściwość | Wartość |
|------------|---------|
| Inventory | 18 slotów per crate |
| Łączenie | Tak (pionowe i poziome) - "Crate Pile" |
| Wspólne inv | Tak (w stosie) |
| Zapis danych | Osobny plik `<world>/data/crates/<id>.dat` |

**NBT w chunk (TE):**
```java
{
  crateId: int  // ID stosu, -1 = nowy
}
```

**Dane w pliku crate (`CratePileData`):**
```java
{
  // Struktura z CratePileData.toCompound()
  items: [...],     // Wspólna zawartość całego stosu
  numCrates: int    // Liczba skrzyń w stosie
}
```

**Konwersja:**
- ❌ NIE mapować na Storage Drawers (inna mechanika!)
- ✅ Target: Vanilla Chest / Iron Chests (wieloslotowe)
- Każdy crate z stosu → osobna skrzynia
- Zawartość rozdzielona proporcjonalnie
- **Plan awaryjny:** Wypakować do skrzyń obok

---

### 2. Reinforced Chest (`betterstorage:reinforcedChest`)

**TileEntity:** `TileEntityReinforcedChest`

| Właściwość | Wartość |
|------------|---------|
| Materiały | 9 typów (iron, gold, diamond, emerald, copper, tin, silver, zinc, steel) |
| Inventory | 27, 33 lub 39 slotów (zależy od configu `reinforcedColumns`) |
| Łączenie | Tak (poziome, podwójne) |
| Zamki | Tak |
| **Materiał = kosmetyka** | Tylko tekstury! |

**NBT:**
```java
{
  Items: NBTTagList,        // Zawartość
  Lock: NBTTagCompound,     // Zamek (opcjonalny)
  Material: String,         // "iron", "gold", ... (TYLKO kosmetyka)
  orientation: byte         // 0-5 (ForgeDirection)
}
```

**Konwersja:**
- Target: Iron Chests
- Materiał IGNORUJEMY (lub zapisujemy w CustomName)
- Pojemność BS → najbliższy większy Iron Chests:
  - 27 slotów BS → Copper Chest (45)
  - 33 slotów BS → Iron Chest (54)
  - 39 slotów BS → Iron Chest (54)

**Poprawione mapowanie (nie per materiał!):**

| Pojemność BS | Target Iron Chests | Slotów docelowych |
|--------------|-------------------|-------------------|
| 27 (9×3) | `ironchest:copper_chest` | 45 |
| 33 (11×3) | `ironchest:iron_chest` | 54 |
| 39 (13×3) | `ironchest:iron_chest` | 54 |

---

### 3. Locker (`betterstorage:locker`)

**TileEntity:** `TileEntityLocker`

| Właściwość | Wartość |
|------------|---------|
| Inventory | 36 slotów (12×3) |
| Łączenie | Tak (pionowe) |
| Zamki | Tak |
| Mirror | Tak (drzwi w lewo/prawo) |

**NBT:**
```java
{
  Items: NBTTagList,
  Lock: NBTTagCompound,
  orientation: byte,
  mirror: boolean  // true = drzwi w lewo
}
```

**Konwersja:**
- Target: Barrel (pionowy) / Chest
- Orientację zachowujemy
- `mirror` ignorujemy (brak odpowiednika)

---

### 4. Reinforced Locker (`betterstorage:reinforcedLocker`)

**TileEntity:** `TileEntityReinforcedLocker`

| Właściwość | Wartość |
|------------|---------|
| Materiały | 9 typów (jak Reinforced Chest) |
| Inventory | 36 slotów |
| **Materiał = kosmetyka** | Tak samo jak chest |

**Konwersja:**
- Target: Iron Chests / Sophisticated Storage Barrel
- Materiał ignorujemy

---

### 5. Cardboard Box (`betterstorage:cardboardBox`)

**TileEntity:** `TileEntityCardboardBox`

| Właściwość | Wartość |
|------------|---------|
| Inventory | 9 slotów (config `cardboardBoxRows` × 9) |
| Zużywanie | Tak (`cardboardBoxUses`) |
| Farbowanie | Tak |
| Przenoszenie | Tak (z zawartością) |

**NBT:**
```java
{
  Items: NBTTagList,    // 9 slotów
  uses: int,            // Pozostałe użycia (-1 = ∞)
  color: int            // Kolor RGB (-1 = brak)
}
```

**Konwersja:**
- Target: Packing Tape (`packingtape:packed`)
- Inny system zużywania (taśma vs blok)
- Rozwiązanie:
  - Jeśli `uses` > 0 → spakować Packing Tape
  - Jeśli `uses` = 0 lub -1 → wypakować zawartość

---

### 6. Crafting Station (`betterstorage:craftingStation`)

**TileEntity:** `TileEntityCraftingStation`

| Właściwość | Wartość |
|------------|---------|
| Inventory | 9 slotów crafting + 1 wynik |
| Trwałość | Tak (zachowuje zawartość) |
| Sąsiednie inv | Dostęp z tyłu |

**NBT:**
```java
{
  Items: NBTTagList  // 10 slotów (0-8 crafting, 9 wynik)
}
```

**Konwersja:**
- Target: Crafting Station mod (ten sam mod!)
- Uwaga: Do zweryfikowania kompatybilność NBT w Zadaniu 2

---

### 7. Armor Stand (`betterstorage:armorStand`)

**TileEntity:** `TileEntityArmorStand`

| Właściwość | Wartość |
|------------|---------|
| Inventory | 4 sloty (zbroja) |
| GUI | Tak |

**NBT:**
```java
{
  Items: NBTTagList  // 4 sloty (helmet, chest, legs, boots)
}
```

**Konwersja:**
- Target: Vanilla Armor Stand (`minecraft:armor_stand`)
- Problemy: Brak GUI w vanilla
- **Rozwiązanie:** Wypakować zawartość do skrzyni obok

---

### 8. Backpack (`betterstorage:backpack`)

**TileEntity:** `TileEntityBackpack`

| Właściwość | Wartość |
|------------|---------|
| Inventory | 27 slotów (config `backpackRows` × 9) |
| Farbowanie | Tak |

**NBT:**
```java
{
  Items: NBTTagList,  // 27 slotów
  color: int          // Kolor
}
```

**Konwersja:**
- Target: Sophisticated Backpacks
- Szczegóły: Patrz osobny dokument

---

### 9. Ender Backpack (`betterstorage:enderBackpack`)

**TileEntity:** `TileEntityEnderBackpack`

| Właściwość | Wartość |
|------------|---------|
| Inventory | Vanilla ender chest (wspólny) |

**Kod źródłowy (`ItemEnderBackpack.java:36`):**
```java
return new InventoryEnderBackpackEquipped(player.getInventoryEnderChest());
```

**Konwersja:**
- Target: `minecraft:ender_chest` (vanilla!)
- NIE potrzeba Ender Storage
- To tylko "dostęp" do vanilla ender chest

---

### 10. Present (`betterstorage:present`)

**TileEntity:** `TileEntityPresent`

| Właściwość | Wartość |
|------------|---------|
| Inventory | 9 slotów |
| Dekoracja | Tak (kolor papieru) |

**NBT:**
```java
{
  Items: NBTTagList,
  color: int  // Kolor papieru
}
```

**Konwersja:**
- Target: Vanilla Chest + tabliczka
- Funkcja ozdobna tracona

---

### 11. Lockable Door (`betterstorage:lockableDoor`)

**TileEntity:** `TileEntityLockableDoor`

| Właściwość | Wartość |
|------------|---------|
| Zamki | Tak |

**NBT:**
```java
{
  Lock: NBTTagCompound
}
```

**Konwersja:**
- Target: Drzwi + Lock & Key (jeśli dostępny)
- Alternatywa: Vanilla door + tabliczka

---

### 12. Flint Block (`betterstorage:flintBlock`)

**TileEntity:** `TileEntityFlintBlock`

| Właściwość | Wartość |
|------------|---------|
| Funkcja | Dekoracyjna |

**Konwersja:**
- Target: Stone / Deepslate (placeholder)

---

## System Lock & Key

### Struktura zamka (ItemStack)

```java
{
  id: "betterstorage:lock",
  Count: 1b,
  tag: {
    full: boolean,        // Czy pełny zestaw
    ench: [              // Enchanty zamka
      { id: short, lvl: short }
    ]
  }
}
```

### Struktura klucza (ItemStack)

```java
{
  id: "betterstorage:key",
  Count: 1b,
  tag: {
    lock: {              // Kopia NBT zamka
      full: boolean,
      ench: [...]
    },
    ench: [...]         // Enchanty klucza
  }
}
```

### Enchanty

| Enchant | Konwersja |
|---------|-----------|
| Lockpicking | ❌ Brak |
| Morphing | ❌ Brak |
| Unlocking | ❌ Brak |
| Persistence | ❌ Brak |
| Security | ❌ Brak |
| Shock | ❌ Brak |
| Trigger | ❌ Brak |

**Uwaga:** Wszystkie enchanty BS zostaną utracone.

---

## Podsumowanie mapowania (POPRAWIONE)

### Bloki storage

| BS 1.7.10 | Target 1.18.2 | Uwagi |
|-----------|---------------|-------|
| Reinforced Chest | Iron Chests (Copper/Iron) | Materiał = kosmetyka |
| Reinforced Locker | Iron Chests / Barrel | Materiał = kosmetyka |
| Locker | Barrel / Chest | Pionowa orientacja |
| **Crate** | **Chest / Iron Chests** | ❌ NIE Drawers! Zawartość z osobnych plików |
| Cardboard Box | Packing Tape | Inny system zużywania |
| Crafting Station | Crafting Station | Ten sam mod (do weryfikacji NBT) |

### Pozostałe bloki

| BS 1.7.10 | Target 1.18.2 | Uwagi |
|-----------|---------------|-------|
| Armor Stand | Vanilla Armor Stand | Wypakować zawartość! |
| Ender Backpack | Vanilla Ender Chest | NIE Ender Storage! |
| Present | Chest + tabliczka | Funkcja ozdobna tracona |
| Flint Block | Stone | Placeholder |

---

## Priorytety konwersji

### 🔴 Wysoki priorytet
1. **Reinforced Chest** - główne storage graczy
2. **Crate** - skomplikowane (osobne pliki!)
3. **Cardboard Box** - jeśli zawiera itemy
4. **Backpack** - ekwipunek graczy

### 🟡 Średni priorytet
5. **Locker** - storage dodatkowe
6. **Crafting Station** - stacje craftingowe
7. **Armor Stand** - ekspozycja zbroi

### 🟢 Niski priorytet
8. **Present** - dekoracje
9. **Lockable Door** - drzwi
10. **Flint Block** - dekoracje

---

## Krytyczne uwagi dla Zadania 2

### 1. Crate Pile - wymaga specjalnej obsługi
```
<world>/
  data/
    crates/
      0.dat   ← Dane crate pile o ID 0
      1.dat   ← Dane crate pile o ID 1
      ...
```

### 2. ContainerMaterial - nie mapować na tier
- Wszystkie materiały → ten sam target
- Materiał = tylko wygląd/tekstura

### 3. Ender Backpack = vanilla
- Nie instalować Ender Storage specjalnie dla tego
- Użyć `minecraft:ender_chest`

---

**Status:** ✅ Zadanie 1 ukończone z poprawkami  
**Następny krok:** Zadanie 2 - Symulacje i konwerter NBT
