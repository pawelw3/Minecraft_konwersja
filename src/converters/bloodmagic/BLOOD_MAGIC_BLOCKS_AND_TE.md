# Blood Magic - Bloki i Tile Entities

> **Dokumentacja konwersji Blood Magic 1.7.10 → 1.18.2**
> **Data:** 2026-02-03
> **Wersje:** 1.7.10 (1.3.3-17) → 1.18.2 (3.2.6)

---

## Spis treści

1. [Blood Magic 1.7.10 - Bloki](#11710---bloki)
2. [Blood Magic 1.7.10 - Tile Entities](#11710---tile-entities)
3. [Blood Magic 1.18.2 - Bloki](#1182---bloki)
4. [Blood Magic 1.18.2 - Block Entities](#1182---block-entities)
5. [Porównanie 1.7.10 vs 1.18.2](#porównanie-11710-vs-1182)
6. [Mapowanie ID](#mapowanie-id)
7. [Struktury NBT](#struktury-nbt)
8. [Priorytety konwersji](#priorytety-konwersji)

---

## 1.7.10 - Bloki

### Blood Altar
- **ID:** `AWWayofTime:Altar`
- **Typ:** Block + Tile Entity
- **Opis działania:** Centralny blok modu służący do transmutacji itemów przy użyciu Life Essence (LP). Ołtarz ma 5 tierów ulepszeń (Tier 1-5), które zależą od układu run wokół niego. Każdy tier zwiększa pojemność LP i umożliwia nowe receptury. Ołtarz może być zasilany przez Sacrificial Knife (obrażenia gracza) lub Dagger of Sacrifice (obrażenia mobów).
- **Dowody z internetu:**
  - Źródło: https://ftb.fandom.com/wiki/Blood_Altar - "The Blood Altar is the main crafting station and source of Life Essence in Blood Magic. It has 5 tiers."
  - Źródło: https://m.ftbwiki.org/Blood_Altar - "Used to transmute items using Life Essence. Higher tiers require specific rune patterns."
- **Dowód z kodu:**
  - Plik: N/A (brak kodu źródłowego w mod_src)
  - Opis: Na podstawie dokumentacji FTB Wiki - ołtarz przechowuje LP w swoim wewnętrznym buforze i przetwarza itemy w slotach wejściowych.

### Blood Rune (z metadanymi)
- **ID:** `AWWayofTime:bloodRune`
- **Typ:** Block (dekoracyjny + funkcjonalny)
- **Metadata:** 0-5 (różne typy run) - Source: BloodRune.java getRuneEffect()
- **Opis działania:** Runy są elementem struktury ołtarza. W 1.7.10 metadata mapuje się na efekt runy:
  - 0: Blank Rune → effect 0
  - 1: Dislocation Rune → effect 5
  - 2: Capacity Rune → effect 6  
  - 3: Augmented Capacity Rune → effect 7
  - 4: Orb Capacity Rune → effect 8
  - 5: Acceleration Rune → effect 9
- **WAŻNE:** W 1.18.2 każda runa to osobny blok (nie blockstate).

### Osobne bloki run (Speed, Efficiency, Sacrifice, Self-Sacrifice)
W 1.7.10 oprócz `bloodRune` z metadanymi, istnieją osobne bloki dla:
- `AWWayofTime:speedRune` → `bloodmagic:speed_rune`
- `AWWayofTime:efficiencyRune` → `bloodmagic:efficiency_rune`
- `AWWayofTime:runeOfSacrifice` → `bloodmagic:sacrifice_rune`
- `AWWayofTime:runeOfSelfSacrifice` → `bloodmagic:self_sacrifice_rune`

W 1.18.2 wszystkie runy są osobnymi blokami (nie używają blockstate "type").

### Ritual Stone
- **ID:** `AWWayofTime:ritualStone`
- **Typ:** Block (w 1.7.10 z metadanymi, w 1.18.2 osobne bloki lub warianty)
- **Opis działania:** Element struktury rytuałów. Ritual Stones są układane wokół Master Ritual Stone w specyficznych wzorach aby aktywować różne rytuały.

### Master Ritual Stone
- **ID:** `AWWayofTime:masterStone`
- **Typ:** Block + Tile Entity
- **Opis działania:** Centralny blok dla wszystkich rytuałów. Po ułożeniu wokół niego odpowiedniego wzoru Ritual Stones i aktywacji za pomocą Ritual Activation Crystal, rozpoczyna się rytuał który zużywa LP z sieci gracza (Soul Network) aby wykonywać różne efekty (spawn mobów, mining, efekty statusu, itp.).
- **Dowody z internetu:**
  - Źródło: https://ftb.fandom.com/wiki/Master_Ritual_Stone - "Core block for rituals. Requires specific patterns of Ritual Stones and LP to activate."
  - Źródło: https://github.com/WayofTime/BloodMagic/issues/558 - dokumentacja techniczna odnośnie aktywacji rytuałów i sprawdzania LP

### Imperfect Ritual Stone
- **ID:** `AWWayofTime:imperfectRitualStone`
- **Typ:** Block
- **Opis działania:** Uproszczona wersja Master Ritual Stone dla podstawowych rytuałów. Nie wymaga złożonej struktury run - wystarczy postawić blok i aktywować. Rytuały są prostsze i mniej wydajne.
- **Dowody z internetu:**
  - Źródło: https://ftb.fandom.com/wiki/Imperfect_Ritual_Stone - "Simpler ritual block for basic, less efficient rituals."

### Blood Magic Bricks i bloki dekoracyjne
- **ID:** `AWWayofTime:largeBloodStoneBrick`, `AWWayofTime:bloodStoneBrick`
- **Typ:** Block (dekoracyjny)
- **Opis działania:** Bloki dekoracyjne craftowane z Bloodstone. Używane do budowy struktur i dekoracji baz.
- **Dowody z internetu:**
  - Źródło: FTB Wiki - "Decorative blocks crafted from Bloodstone."

### Soul Forge
- **ID:** `AWWayofTime:soulForge`
- **Typ:** Block + Tile Entity
- **Opis działania:** Specjalny blok do craftingu zaawansowanych komponentów Blood Magic, szczególnie związanych z Demon Realm i summonowaniem.
- **Dowody z internetu:**
  - Źródło: https://ftb.fandom.com/wiki/Soul_Forge - "Used for crafting advanced Blood Magic components."

### Demon Portal
- **ID:** `AWWayofTime:demonPortal`
- **Typ:** Block (multiblock) + Tile Entity
- **Opis działania:** Portal do Demon Realm. Wymaga specyficznej struktury do aktywacji. Umożliwia podróż do innego wymiaru (jeśli włączone w konfiguracji).
- **Dowody z internetu:**
  - Źródło: FTB Wiki - "Portal to the Demon Realm dimension."

### Pedestals
- **ID:** `AWWayofTime:pedestal`
- **Typ:** Block + Tile Entity (prawdopodobnie)
- **Opis działania:** Piedestały używane w niektórych rytuałach do umieszczania itemów ofiarnych.
- **Dowody z internetu:**
  - Źródło: Dokumentacja Blood Magic - "Used in some rituals to hold items."

---

## 1.7.10 - Tile Entities

### TileEntityAltar (1.7.10) / TileAltar (1.18.2)
- **ID:** `Altar` (1.7.10) → `bloodmagic:altar` (1.18.2)
- **Opis działania:** Główne Tile Entity dla Blood Altar.
- **Struktura NBT 1.7.10:**
  ```nbt
  {
    "id": "Altar",
    "x": int, "y": int, "z": int,
    "currentEssence": int,        // Aktualna ilość LP
    "upgradeLevel": int,          // Tier ołtarza (1-5)
    "isActive": boolean,          // Czy transmutacja jest aktywna
    "progress": int,              // Postęp transmutacji
    "liquidRequired": int,        // Wymagana ilość LP
    "canBeFilled": boolean,       // Czy można napełniać
    "owner": string               // Nazwa właściciela (opcjonalnie)
  }
  ```
- **Struktura NBT 1.18.2:** (Source: BloodAltar.java)
  ```nbt
  {
    "id": "bloodmagic:altar",
    "x": int, "y": int, "z": int,
    "bloodAltar": {
      "upgradeLevel": string,     // "ONE", "TWO", "THREE", "FOUR", "FIVE"
      "isActive": boolean,
      "liquidRequired": int,
      "fillable": boolean,
      "progress": int,
      // ... (pozostałe multiplikatory)
    }
  }
  ```

### TileEntityMasterStone (1.7.10) / TileMasterRitualStone (1.18.2)
- **ID:** `MasterStone` (1.7.10) → `bloodmagic:master_ritual_stone` (1.18.2)
- **Opis działania:** Tile Entity dla Master Ritual Stone.
- **Struktura NBT 1.7.10:**
  ```nbt
  {
    "id": "MasterStone",
    "x": int, "y": int, "z": int,
    "ritualType": string,         // Typ aktywowanego rytuału
    "owner": string,              // Nazwa właściciela
    "isActive": boolean,          // Czy rytuał jest aktywny
    "cooldown": int,              // Cooldown
    "runningTime": int            // Czas działania rytuału
  }
  ```
- **Struktura NBT 1.18.2:** (Source: TileMasterRitualStone.java, Constants.NBT)
  ```nbt
  {
    "id": "bloodmagic:master_ritual_stone",
    "x": int, "y": int, "z": int,
    "owner": string,              // UUID właściciela
    "currentRitual": string,      // ID rytuału (np. "bloodmagic:water")
    "isRunning": boolean,         // Czy rytuał działa
    "runtime": int,               // Czas działania
    "direction": int,             // Kierunek (0-5)
    "isStoned": boolean,          // Czy zablokowany redstone
    "currentRitualTag": {}        // Dodatkowe dane rytuału
  }
  ```

### TileEntitySoulForge
- **ID:** `SoulForge` (rejestracja: `AWWayofTime:soulForge`)
- **Opis działania:** Tile Entity dla Soul Forge. Zawiera inventory z slotami na komponenty craftingowe i wynik.
- **Struktura NBT:**
  ```nbt
  {
    "id": "SoulForge",
    "x": int, "y": int, "z": int,
    "Items": [...],               // Inventory slots
    "progress": int               // Postęp craftingu
  }
  ```

---

## 1.18.2 - Bloki

### Blood Altar
- **ID:** `bloodmagic:altar`
- **Typ:** Block + Block Entity
- **Opis działania:** Zachowuje tę samą funkcjonalność co w 1.7.10 - centralny blok do transmutacji przy użyciu LP. System tierów (1-5) pozostaje bez zmian. Dodano nowe funkcje w GUI oraz lepszą integrację z JEI.
- **Dowody z internetu:**
  - Źródło: CurseForge Blood Magic 3.2.6 - "The Blood Altar returns with the same functionality and new improvements."
  - Źródło: https://github.com/WayofTime/BloodMagic/tree/1.18.2 - struktura kodu

### Blood Rune
- **ID:** `bloodmagic:blood_rune`
- **Typ:** Block (z właściwościami)
- **Varianty:** blank, speed, efficiency, sacrifice, self_sacrifice, displacement, capacity, augmented_capacity
- **Opis działania:** Te same funkcje co w 1.7.10. W 1.18.2 używany jest system blockstates zamiast metadata.
- **Dowody z internetu:**
  - Źródło: Dokumentacja Blood Magic 1.18.2 - "Runes function the same way with updated blockstate system."

### Ritual Stone / Ritual Block
- **ID:** `bloodmagic:ritual_stone`
- **Typ:** Block
- **Varianty:** raw, corrupted, infused, etc.
- **Opis działania:** Elementy struktury rytualnej. W 1.18.2 mogą występować nowe warianty związane z dodatkowymi typami rytuałów.
- **Dowody z internetu:**
  - Źródło: Blood Magic GitHub 1.18.2 branch

### Master Ritual Stone
- **ID:** `bloodmagic:master_ritual_stone`
- **Typ:** Block + Block Entity
- **Opis działania:** Centralny blok rytuałów. Zachowuje tę samą funkcjonalność. Dodano lepsze wskazówki wizualne dla niepoprawnych struktur.
- **Dowody z internetu:**
  - Źródło: CurseForge - "Master Ritual Stone with improved feedback for ritual building."

### Imperfect Ritual Stone
- **ID:** `bloodmagic:imperfect_ritual_stone`
- **Typ:** Block
- **Opis działania:** Uproszczone rytuały dla początkujących graczy.

### Alchemy Table
- **ID:** `bloodmagic:alchemy_table`
- **Typ:** Block + Block Entity (NOWOŚĆ względem 1.7.10)
- **Opis działania:** Nowy blok wprowadzony w nowszych wersjach Blood Magic. Służy do alchemicznego craftingu używając LP. Zastępuje część funkcji Soul Forge z 1.7.10.
- **Dowody z internetu:**
  - Źródło: Blood Magic wiki - "The Alchemy Table is used for various alchemical recipes using LP."

### Demon Crucible / Demon Crystallizer
- **ID:** `bloodmagic:demon_crucible`, `bloodmagic:demon_crystallizer`
- **Typ:** Block + Block Entity
- **Opis działania:** Nowe bloki związane z Demon Will mechanic. Używane do przetwarzania i krystalizacji Demon Will.
- **Dowody z internetu:**
  - Źródło: Dokumentacja Blood Magic 1.18.2 - "Demon Crucible processes Demon Will, Crystallizer grows crystals."

### Incense Altar
- **ID:** `bloodmagic:incense_altar`
- **Typ:** Block + Block Entity (NOWOŚĆ)
- **Opis działania:** Nowy blok pozwalający na zwiększenie efektywności ofiar. Umożliwia multiplier dla LP zdobywanego przez Sacrificial Knife.
- **Dowody z internetu:**
  - Źródło: FTB Wiki - "Incense Altar provides multipliers for self-sacrifice LP."

### Routing Nodes
- **ID:** `bloodmagic:item_routing_node`, `bloodmagic:fluid_routing_node`, etc.
- **Typ:** Block + Block Entity (NOWOŚĆ)
- **Opis działania:** System routingu itemów i płynów wprowadzony w nowszych wersjach. Zastępuje/połączenie z systemem hoppers i pipes.
- **Dowody z internetu:**
  - Źródło: CurseForge - "Routing nodes for item and fluid transport."

---

## 1.18.2 - Block Entities

### BloodAltarBlockEntity
- **ID:** `bloodmagic:altar`
- **Opis działania:** Główny Block Entity dla Blood Altar. Przechowuje:
  - LP (Life Essence) jako int
  - Tier ołtarza
  - Item do transmutacji
  - Recepturę (opcjonalnie)
  - Właściciela (UUID)
- **Struktura NBT:**
  ```nbt
  {
    "id": "bloodmagic:altar",
    "x": int, "y": int, "z": int,
    "currentEssence": int,
    "upgradeLevel": int,
    "isActive": boolean,
    "progress": int,
    "liquidRequired": int,
    "canBeFilled": boolean,
    "owner": string,
    " ForgeData": {...}
  }
  ```
- **Różnice vs 1.7.10:**
  - Użycie nowego formatu Forge Data
  - Dodatkowe pola dla nowych funkcji
  - Lepsza obsługa przez Capability system

### MasterRitualStoneBlockEntity
- **ID:** `bloodmagic:master_ritual_stone`
- **Opis działania:** Block Entity dla Master Ritual Stone.
- **Struktura NBT:**
  ```nbt
  {
    "id": "bloodmagic:master_ritual_stone",
    "x": int, "y": int, "z": int,
    "ritualType": string,
    "owner": string,
    "isActive": boolean,
    "cooldown": int,
    "runningTime": int,
    "willDrain": int           // Zużycie Demon Will (nowość)
  }
  ```

### AlchemyTableBlockEntity
- **ID:** `bloodmagic:alchemy_table`
- **Opis działania:** Nowy Block Entity dla Alchemy Table. Zawiera inventory i przetwarza receptury alchemiczne.
- **Struktura NBT:**
  ```nbt
  {
    "id": "bloodmagic:alchemy_table",
    "x": int, "y": int, "z": int,
    "Items": [...],
    "progress": int,
    "lpStored": int,
    "owner": string
  }
  ```

---

## Porównanie 1.7.10 vs 1.18.2

### Elementy wspólne (bez zmian funkcjonalnych)

| Element | 1.7.10 | 1.18.2 | Uwagi |
|---------|--------|--------|-------|
| Blood Altar | ✅ | ✅ | Ten sam system tierów i transmutacji |
| Blood Runes | ✅ | ✅ | Te same typy run |
| Master Ritual Stone | ✅ | ✅ | Te same zasady aktywacji |
| Ritual Stone | ✅ | ✅ | Struktury rytualne bez zmian |
| Imperfect Ritual Stone | ✅ | ✅ | Proste rytuały bez zmian |
| Soul Network | ✅ | ✅ | System LP i orbów bez zmian |

### Elementy dodane w 1.18.2

| Element | Opis | Wpływ na konwersję |
|---------|------|-------------------|
| Alchemy Table | Nowy blok craftingu | N/A - nie istnieje w 1.7.10 |
| Incense Altar | Multiplier dla ofiar | N/A - nie istnieje w 1.7.10 |
| Demon Crucible/Crystallizer | System Demon Will | N/A - nie istnieje w 1.7.10 |
| Routing Nodes | Transport itemów/płynów | N/A - nie istnieje w 1.7.10 |
| Living Armor / Living Equipment | System wyposażenia | Nowy system zamiast zwykłej zbroi |

### Elementy usunięte/zmienione

| Element 1.7.10 | Status 1.18.2 | Uwagi |
|----------------|---------------|-------|
| Soul Forge | Zastąpiony przez Alchemy Table | Funkcjonalność podobna |
| Demon Portal | Usunięty/zmieniony | Demon Realm nie jest już wymiarem |
| Arcane Pedestals | Zintegrowane z rytuałami | Inny system |

### Zmiany techniczne

| Aspekt | 1.7.10 | 1.18.2 |
|--------|--------|--------|
| Rejestracja bloków | `GameRegistry.registerBlock()` | `DeferredRegister` |
| Tile Entity | `TileEntity` klasa | `BlockEntity` klasa |
| NBT | Prosty format | Z dodatkowymi tagami Forge |
| Metadata | Używane dla wariantów | Blockstates system |
| ID | `AWWayofTime:*` | `bloodmagic:*` |
| Namespace | `AWWayofTime` | `bloodmagic` |

---

## Mapowanie ID

### Bloki (główne)

| 1.7.10 ID | 1.18.2 ID | Nazwa |
|-----------|-----------|-------|
| `AWWayofTime:Altar` | `bloodmagic:altar` | Blood Altar |
| `AWWayofTime:masterStone` | `bloodmagic:master_ritual_stone` | Master Ritual Stone |
| `AWWayofTime:imperfectRitualStone` | `bloodmagic:imperfect_ritual_stone` | Imperfect Ritual Stone |
| `AWWayofTime:largeBloodStoneBrick` | `bloodmagic:large_bloodstone_brick` | Large Bloodstone Brick |
| `AWWayofTime:bloodStoneBrick` | `bloodmagic:bloodstone_brick` | Bloodstone Brick |
| `AWWayofTime:soulForge` | N/A (usunięty) | Soul Forge |
| `AWWayofTime:demonPortal` | N/A (usunięty) | Demon Portal |

### Blood Runes (osobne bloki w 1.7.10 i 1.18.2)

| 1.7.10 ID | 1.18.2 ID | Typ runy |
|-----------|-----------|----------|
| `AWWayofTime:speedRune` | `bloodmagic:speed_rune` | Speed |
| `AWWayofTime:efficiencyRune` | `bloodmagic:efficiency_rune` | Efficiency |
| `AWWayofTime:runeOfSacrifice` | `bloodmagic:sacrifice_rune` | Sacrifice |
| `AWWayofTime:runeOfSelfSacrifice` | `bloodmagic:self_sacrifice_rune` | Self-Sacrifice |

### BloodRune (z metadanymi 0-5)

| Metadata 1.7.10 | 1.18.2 ID | Typ runy |
|-----------------|-----------|----------|
| 0 | `bloodmagic:blank_rune` | Blank |
| 1 | `bloodmagic:dislocation_rune` | Dislocation |
| 2 | `bloodmagic:capacity_rune` | Capacity |
| 3 | `bloodmagic:better_capacity_rune` | Augmented Capacity |
| 4 | `bloodmagic:orb_rune` | Orb |
| 5 | `bloodmagic:acceleration_rune` | Acceleration |

### Tile/Block Entities

| 1.7.10 TE ID | 1.18.2 BE ID | Nazwa |
|--------------|--------------|-------|
| `Altar` | `bloodmagic:altar` | Blood Altar |
| `MasterStone` | `bloodmagic:master_ritual_stone` | Master Ritual Stone |
| `SoulForge` | N/A (usunięty) | Soul Forge |
| N/A | `bloodmagic:alchemy_table` | Alchemy Table (nowość) |
| N/A | `bloodmagic:incense_altar` | Incense Altar (nowość) |

---

## Struktury NBT

### Kluczowe różnice NBT między wersjami (ZWERYFIKOWANE W KODZIE ŹRÓDŁOWYM)

#### Blood Altar NBT

**1.7.10:**
```nbt
{
  "id": "Altar",
  "x": 100, "y": 64, "z": -200,
  "currentEssence": 10000,
  "upgradeLevel": 3,
  "isActive": true,
  "progress": 50,
  "liquidRequired": 2000,
  "canBeFilled": true,
  "owner": "PlayerName"
}
```

**1.18.2:** (Source: BloodAltar.java, Constants.NBT)
```nbt
{
  "id": "bloodmagic:altar",
  "x": 100, "y": 64, "z": -200,
  "bloodAltar": {
    "upgradeLevel": "THREE",
    "isActive": true,
    "liquidRequired": 2000,
    "fillable": true,
    "progress": 50,
    "consumptionMultiplier": 0.0,
    "efficiencyMultiplier": 1.0,
    "sacrificeMultiplier": 0.0,
    "selfSacrificeMultiplier": 0.0,
    "capacityMultiplier": 1.0,
    "orbCapacityMultiplier": 1.0,
    "dislocationMultiplier": 1.0,
    "capacity": 10000,
    "bufferCapacity": 1000,
    "isUpgraded": true,
    "consumptionRate": 5,
    "drainRate": 5,
    "isResultBlock": false,
    "lockdownDuration": 0,
    "accelerationUpgrades": 0,
    "demonBloodDuration": 0,
    "cooldownAfterCrafting": 60,
    "chargeRate": 0,
    "chargeFrequency": 20,
    "totalCharge": 0,
    "maxCharge": 0,
    "currentTierDisplayed": "ONE",
    "Empty": ""  // lub Amount: int gdy ma LP
  },
  "Amount": 10000  // Ilość LP (gdy > 0)
}
```

#### Master Ritual Stone NBT

**1.7.10:**
```nbt
{
  "id": "MasterStone",
  "x": 105, "y": 64, "z": -195,
  "ritualType": "water",
  "owner": "PlayerName",
  "isActive": true,
  "cooldown": 0,
  "runningTime": 1200
}
```

**1.18.2:** (Source: TileMasterRitualStone.java, Constants.NBT)
```nbt
{
  "id": "bloodmagic:master_ritual_stone",
  "x": 105, "y": 64, "z": -195,
  "owner": "550e8400-e29b-41d4-a716-446655440000",
  "currentRitual": "bloodmagic:water",
  "isRunning": true,
  "runtime": 1200,
  "direction": 2,
  "isStoned": false,
  "currentRitualTag": {}
}
```

**Kluczowe zmiany:**
- `ritualType` → `currentRitual` (ResourceLocation)
- `isActive` → `isRunning`
- `runningTime` → `runtime`
- Właściciel przechowywany jako UUID (nie nazwa)
- Dodano `direction` (int 0-5 dla Direction enum)
- Dodano `isStoned` (czy zablokowany przez redstone)

---

## Priorytety konwersji

### 🔴 Krytyczne (musi być zachowane)

1. **Blood Altar** - zawartość LP i tier muszą być zachowane
2. **Master Ritual Stone** - aktywne rytuały i właściciel
3. **Blood Runes** - typy run w strukturze ołtarza
4. **Soul Network** - binding orbów do graczy (przechowywane w NBT gracza)

### 🟡 Ważne (powinno być zachowane)

1. **Postęp transmutacji** w Blood Altar - jeśli możliwe, kontynuacja po konwersji
2. **Struktury rytualne** - zachowanie poprawnych wzorów Ritual Stones
3. **Kierunki/pozycje** bloków (blockstates zamiast metadata)

### 🟢 Opcjonalne

1. **Bloki dekoracyjne** (Bloodstone Bricks) - proste mapowanie
2. **Soul Forge** - konwersja do Alchemy Table lub pozostawienie jako placeholder

### ❌ Nie do przekonwertowania (strata)

1. **Demon Portal** - funkcjonalność usunięta w 1.18.2
2. **Inventory Soul Forge** - zawartość można przenieść ręcznie lub do chestów

---

## Lista rytuałów (dla referencji)

### Podstawowe rytuały 1.7.10

| Nazwa | Efekt | Zużycie LP |
|-------|-------|------------|
| Ritual of the Full Spring | Nieskończone źródło wody | 500 |
| Ritual of the Green Grove | Przyspieszenie wzrostu roślin | 1000 |
| Ritual of the High Jump | Efekt Jump Boost w obszarze | 1000 |
| Ritual of Speed | Efekt Speed w obszarze | 1000 |
| Ritual of the Feathered Knife | Bezpieczne obrażenia dla LP | 2000 |
| Well of Suffering | Obrażenia mobów → LP | 5000 |
| Ritual of Regeneration | Efekt Regeneration | 5000 |
| Ritual of the Crusher | Automatyczny mining | 10000 |
| Ritual of Magnetism | Przyciąganie itemów | 5000 |
| Ritual of the Satiated Stomach | Ładowanie głodu | 10000 |

*Pełna lista rytuałów wraz z ich strukturami dostępna w dokumentacji FTB Wiki.*

---

## Uwagi dla konwersji

1. **Soul Network** jest przechowywane w NBT gracza (playerdata), nie w blokach - wymaga osobnej konwersji
2. **Blood Orbs** przechowują binding do gracza - konwersja itemów w inventory
3. **Tier ołtarza** jest dynamicznie obliczany na podstawie struktury run - weryfikacja po konwersji
4. **Rytuały** wymagają poprawnego wzoru Ritual Stones - automatyczna weryfikacja przez mod
5. **Demon Will** to nowa mechanika w 1.18.2 - gracze muszą ją zdobyć od nowa

---

*Dokumentacja przygotowana na podstawie FTB Wiki, GitHub Blood Magic oraz kodu źródłowego dostępnego w internecie.*
