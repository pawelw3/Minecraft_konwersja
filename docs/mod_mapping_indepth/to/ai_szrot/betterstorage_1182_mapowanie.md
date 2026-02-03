# Better Storage → 1.18.2 - Mapowanie modów (POPRAWIONE)

> **Cel:** Mapowanie funkcjonalności Better Storage 1.7.10 na dostępne mody 1.18.2  
> **Mody docelowe:** Iron Chests, Storage Drawers, Sophisticated Storage, Packing Tape, Crafting Station, Lock & Key  
> **Data:** 2026-02-03  
> **Poprawki:** ContainerMaterial = kosmetyka, Crate ≠ Drawers, IronChests = 7 typów

---

## Strategia konwersji

Better Storage nie ma portu na 1.18.2. Konwersja wymaga **zestawu modów zastępczych**.

### Kluczowe zmiany po weryfikacji kodu:

1. **ContainerMaterial = kosmetyka** - nie mapujemy "per materiał"
2. **Crate Pile** - zawartość w osobnych plikach (`data/crates/`)
3. **Iron Chests** - tylko 7 typów (brak emerald/silver/tin/zinc/steel)
4. **Ender Backpack** - używa vanilla ender chest

---

## Mapowanie bloków (POPRAWIONE)

### Reinforced Chest → Iron Chests

**Uwaga:** Materiał (iron/gold/diamond/...) to TYLKO tekstura!
Pojemność zależy od configu BS (`reinforcedColumns`), nie od materiału.

| Pojemność BS | Config BS | Target Iron Chests | ID 1.18.2 | Slotów docelowych |
|--------------|-----------|-------------------|-----------|-------------------|
| 27 slotów | 9×3 | Copper Chest | `ironchest:copper_chest` | 45 |
| 33 slotów | 11×3 | Iron Chest | `ironchest:iron_chest` | 54 |
| 39 slotów | 13×3 | Iron Chest | `ironchest:iron_chest` | 54 |

**NIE mapujemy per materiał!** Materiał zachowujemy jako:
- Custom name (opcjonalnie): `CustomName: "Iron Chest"`
- Lub ignorujemy

**Dostępne typy Iron Chests (zweryfikowane w kodzie):**
```java
// IronChestsTypes.java
IRON(54), GOLD(81), DIAMOND(108), COPPER(45), 
CRYSTAL(108), OBSIDIAN(108), DIRT(1), WOOD(0)
```

**NIE istnieją:** ~~emerald~~, ~~silver~~, ~~tin~~, ~~zinc~~, ~~steel~~

---

### Reinforced Locker → Iron Chests / Barrel

| Pojemność BS | Target | ID 1.18.2 | Uwagi |
|--------------|--------|-----------|-------|
| 36 slotów | Iron Chest | `ironchest:iron_chest` | 54 slotów |
| 36 slotów | Barrel | `minecraft:barrel` | 27 slotów, pionowy |

Materiał ignorujemy (kosmetyka).

---

### Locker → Barrel / Chest

| Cecha BS | Target 1.18.2 | ID | Uwagi |
|----------|---------------|-----|-------|
| Pionowa orientacja | Barrel | `minecraft:barrel` | Pionowy kontener |
| 36 slotów | Iron Chest | `ironchest:iron_chest` | Więcej slotów |
| Mirror (drzwi) | ❌ Brak | - | Ignorujemy |

---

### Crate → Vanilla Chest / Iron Chests ❌ NIE Drawers!

**WAŻNE:** Crate w BS to NIE TO SAMO co Drawers!

| Cecha | BS Crate | Storage Drawers |
|-------|----------|-----------------|
| Zawartość | Wspólna dla stosu (pile) | Per-blok |
| Sloty | 18 per crate | 1/2/4 per drawer |
| Stack | Standard (64) | Duży (512+) |
| Mechanika | Losowy dostęp | Per-typ itemu |
| Zapis | `<world>/data/crates/<id>.dat` | W chunk data |

**Poprawione mapowanie Crate:**

Opcja A (zalecana) - Zachowanie zawartości:
- Crate → Vanilla Chest (`minecraft:chest`)
- Lub → Iron Chests (zależnie od ilości itemów)
- Każdy crate z stosu → osobna skrzynia
- Zawartość z pliku crate rozdzielona

Opcja B - Sophisticated Storage:
- Crate → Barrel/Chest z dużą pojemnością
- Wymaga upgrade'ów w 1.18.2

**Plan awaryjny:**
- Wypakować całą zawartość crate pile do skrzyń obok
- Zostawić tabliczkę z info o oryginalnym układzie

---

### Cardboard Box → Packing Tape

| BS 1.7.10 | Packing Tape 1.18.2 | Uwagi |
|-----------|---------------------|-------|
| `betterstorage:cardboardBox` | `packingtape:packed` | Taśma pakowa |

**Różnice:**
- BS: Pudło zużywa się (`uses`)
- Packing Tape: Zużywa się taśma, nie blok

**Rozwiązanie:**
- Jeśli `uses` > 0 → Spakować Packing Tape
- Jeśli `uses` = 0 lub -1 → Wypakować zawartość

---

### Crafting Station → Crafting Station

| BS 1.7.10 | Crafting Station 1.18.2 | ID |
|-----------|------------------------|-----|
| `betterstorage:craftingStation` | `craftingstation:crafting_station` | Ten sam mod! |

**Uwaga:** Weryfikacja NBT w Zadaniu 2!

---

### Armor Stand → Vanilla Armor Stand

| BS 1.7.10 | Zamiennik 1.18.2 | ID |
|-----------|------------------|-----|
| `betterstorage:armorStand` | `minecraft:armor_stand` | Podstawowa funkcja |

**Problemy:**
- BS: GUI z 4 slotami (łatwy dostęp)
- Vanilla: Brak GUI, ręczna ekspozycja

**Rozwiązanie:** Wypakować zawartość do skrzyni obok

---

### Ender Backpack → Vanilla Ender Chest ✅

| BS 1.7.10 | Zamiennik 1.18.2 | ID |
|-----------|------------------|-----|
| `betterstorage:enderBackpack` | `minecraft:ender_chest` | **VANILLA!** |

**Dowód z kodu (`ItemEnderBackpack.java:36`):**
```java
return new InventoryEnderBackpackEquipped(player.getInventoryEnderChest());
```

**Wniosek:** Ender Backpack używa **vanilla** ender chest!
NIE potrzeba Ender Storage modu.

---

### Present → Vanilla Chest

| BS 1.7.10 | Zamiennik 1.18.2 | ID |
|-----------|------------------|-----|
| `betterstorage:present` | `minecraft:chest` | + tabliczka |

---

### Lockable Door → Supplementaries

| BS 1.7.10 | Supplementaries 1.18.2 | ID |
|-----------|------------------------|-----|
| `betterstorage:lockableDoor` | `supplementaries:lock_block` | System zamków |

---

### Flint Block → Decorative

| BS 1.7.10 | Zamiennik 1.18.2 | ID |
|-----------|------------------|-----|
| `betterstorage:flintBlock` | `minecraft:stone` | Placeholder |

---

## Mapowanie itemów

### Lock & Key System

| BS 1.7.10 | Lock & Key 1.18.2 | ID | Uwagi |
|-----------|-------------------|-----|-------|
| `betterstorage:lock` | `lockandkey:lock` | Zamek | Funkcjonalność podobna |
| `betterstorage:key` | `lockandkey:key` | Klucz | Funkcjonalność podobna |
| `betterstorage:keyring` | ❌ Brak | Pęk kluczy | Pominąć |
| `betterstorage:masterKey` | ❌ Brak | Master key | Pominąć |

**Enchanty zamków:**
- Lockpicking, Morphing, Unlocking, Persistence, Security, Shock, Trigger
- **Wszystkie tracone** - brak odpowiedników

---

### Backpacks

| BS 1.7.10 | Sophisticated Backpacks | ID |
|-----------|------------------------|-----|
| `betterstorage:backpack` | `sophisticatedbackpacks:backpack` | Plecak |
| `betterstorage:enderBackpack` | `minecraft:ender_chest` | **Vanilla!** |

Szczegóły w osobnym dokumencie.

---

### Cardboard Items

| BS 1.7.10 | Zamiennik 1.18.2 | Uwagi |
|-----------|------------------|-------|
| Cardboard Armor (4 części) | ❌ Brak | Usunąć/zastąpić skórzaną |
| Cardboard Tools (5 szt.) | ❌ Brak | Usunąć/zastąpić drewnianymi |
| Cardboard Sheet | `minecraft:paper` | Fallback |

---

### Gadżety

| BS 1.7.10 | Zamiennik 1.18.2 | ID |
|-----------|------------------|-----|
| Drinking Helmet | ❌ Brak | - |
| Slime in a Bucket | `minecraft:slime_ball` | + bucket |
| Present Book | ❌ Brak | Funkcja opakowywania |

---

## Szczegóły modów docelowych

### Iron Chests 1.18.2 ✅ ZWERYFIKOWANE

**Repo:** `mod_src/118/actual_src/1.18.2/IronChests/`

**Potwierdzone typy (`IronChestsTypes.java`):**
```java
IRON(54, 9, ...),      // iron_chest
GOLD(81, 9, ...),      // gold_chest
DIAMOND(108, 12, ...), // diamond_chest
COPPER(45, 9, ...),    // copper_chest
CRYSTAL(108, 12, ...), // crystal_chest
OBSIDIAN(108, 12, ...),// obsidian_chest
DIRT(1, 1, ...),       // dirt_chest
WOOD(0, 0, ...);       // wood (nieużywana)
```

**NIE istnieją:** emerald, silver, tin, zinc, steel

**Registry names:**
```
ironchest:iron_chest
ironchest:gold_chest
ironchest:diamond_chest
ironchest:copper_chest
ironchest:crystal_chest
ironchest:obsidian_chest
ironchest:dirt_chest
ironchest:trapped_iron_chest
...
```

**NBT:**
```java
- Items: NBTTagList
- facing: String ("north", "south", "east", "west")
```

---

### Crate Pile Data - Struktura plików

**Lokalizacja:** `<world>/data/crates/<id>.dat`

**Format:** NBT (uncompressed)

**Struktura:**
```nbt
{
  data: {
    items: [
      {id: "minecraft:stone", Count: 64},
      ...
    ],
    numCrates: int,
    region: {
      minX: int, minY: int, minZ: int,
      maxX: int, maxY: int, maxZ: int
    }
  }
}
```

**Konsekwencje:**
- Musimy odczytać te pliki podczas konwersji
- Połączyć z TileEntity przez `crateId`
- Rozdzielić zawartość na osobne skrzynie

---

## Konwersja NBT

### Ogólna struktura

```
BetterStorage TE (1.7.10)
├── Items: NBTTagList (ItemStack[])
├── Lock: NBTTagCompound (opcjonalny)
├── Material: String (TYLKO kosmetyka!)
├── orientation: byte (kierunek)
└── [dodatkowe pola]
    ↓
Konwersja
    ↓
Target BlockEntity (1.18.2)
├── Items: NBTTagList (przekonwertowane itemy)
└── [dodatkowe pola zależne od modu]
```

### Konwersja ItemStack

```java
// BS 1.7.10 ItemStack NBT
{
  id: String (format: "modid:itemname")
  Damage: short (metadata)
  Count: byte
  tag: NBTTagCompound
}

// 1.18.2 ItemStack NBT
{
  id: String (format: "modid:itemname")
  Count: byte
  tag: NBTTagCompound
}
```

### Konwersja inventory

```java
// BS 1.7.10
Items: [
  { Slot: 0, id: "minecraft:stone", Count: 64, Damage: 0 },
  { Slot: 1, id: "minecraft:diamond", Count: 1, Damage: 0 }
]

// 1.18.2
Items: [
  { Slot: 0b, id: "minecraft:stone", Count: 64b },
  { Slot: 1b, id: "minecraft:diamond", Count: 1b }
]
```

---

## Problemy i ograniczenia

### 🔴 Krytyczne

1. **Crate Pile System**
   - Dane w osobnych plikach (`data/crates/`)
   - Wspólne inventory dla stosu
   - **Rozwiązanie:** Odczytać pliki, rozdzielić zawartość

2. **ContainerMaterial**
   - Był błędnie interpretowany jako "tier"
   - Jest TYLKO kosmetyczny
   - **Rozwiązanie:** Nie mapować per materiał

3. **Enchanty zamków**
   - 7 enchantów BS nie ma odpowiedników
   - **Rozwiązanie:** Utrata funkcji

### 🟡 Średnie

4. **Iron Chests - brakujące typy**
   - NIE ma: emerald, silver, tin, zinc, steel
   - **Rozwiązanie:** Fallback na istniejące typy

5. **Armor Stand GUI**
   - BS ma GUI, vanilla nie
   - **Rozwiązanie:** Wypakować do skrzyni

6. **Cardboard Box durability**
   - Inny system zużywania
   - **Rozwiązanie:** Konwertować na Packing Tape lub wypakować

### 🟢 Łatwe

7. **Kolory**
   - BS: int (RGB)
   - 1.18.2: dye_color enum
   - **Rozwiązanie:** Mapowanie wartości

8. **Orientacja**
   - BS: byte (0-5)
   - 1.18.2: String ("north", "south", ...)
   - **Rozwiązanie:** Mapowanie 0→"north", itd.

---

## Tabela mapowania kolorów

| BS color int | DyeColor 1.18.2 |
|--------------|-----------------|
| -1 | null (brak koloru) |
| 0 | white |
| 1 | orange |
| 2 | magenta |
| 3 | light_blue |
| 4 | yellow |
| 5 | lime |
| 6 | pink |
| 7 | gray |
| 8 | light_gray |
| 9 | cyan |
| 10 | purple |
| 11 | blue |
| 12 | brown |
| 13 | green |
| 14 | red |
| 15 | black |

---

## Podsumowanie zmian po weryfikacji

| Aspekt | Pierwotna analiza | Poprawiona analiza |
|--------|-------------------|-------------------|
| ContainerMaterial | "Tier/pojemność" | **Kosmetyka/tekstury** |
| Pojemność skrzyń | Zależy od materiału | **Zależy od configu** (27/33/39) |
| Crate | "→ Drawers" | **→ Vanilla Chest** (inna mechanika!) |
| Crate zawartość | W TE | **W osobnych plikach** (`data/crates/`) |
| Iron Chests typy | 12 typów | **7 typów** (brak emerald/silver/tin/zinc/steel) |
| Ender Backpack | "→ Ender Storage" | **→ Vanilla Ender Chest** |
| Locker | "→ Drawers" | **→ Barrel/Chest** |
