# Open Modular Turrets – Zadanie 1: Bloki i Tile/Block Entities

## Podsumowanie moda

Open Modular Turrets (OMT) to mod obronny skupiony na konfigurowalnych działach strzegących terenu przed wrogami. Architektura moda opiera się na dwóch komponentach: **bazach** (TurretBase) gromadzących energię i zarządzających celowaniem, oraz **głowicach** (TurretHead) montowanych na bazach. Glowice są zasilane z pobliskiej bazy RF. Mod zawiera też **ekspandery** zwiększające pojemność energii lub ekwipunku.

Mod rejestruje się jako `openmodularturrets`. **Zamiennik w 1.18.2: K-Turrets** (wg `docs/MAPAOWANIE_USUNIETYCH_MODOW.md`). Źródła K-Turrets pobrano do `mod_src/118/actual_src/1.18.2/KTurrets/repo/` (branch `1.18`).

---

## Bloki 1.7.10 z TileEntity

Źródło: `TileEntityHandler.java` (registry names) + `Names.java` (block names) + `Blocks.java` (rejestracja).

### Bazy wieżyczek (TurretBase)

Wszystkie bazy dziedziczą z klasy `TurretBase` – mają identyczną strukturę NBT.

| Block registry name (1.7.10) | TE ID (NBT `id`) | Klasa TE | Tier |
|---|---|---|---|
| `openmodularturrets:baseTierWood` | `turretWoodBase` | `TurretBaseTierOneTileEntity` | 1 |
| `openmodularturrets:baseTierOneBlock` | `turretBaseOne` | `TurretBaseTierTwoTileEntity` | 2 |
| `openmodularturrets:baseTierTwoBlock` | `turretBaseTwo` | `TurretBaseTierThreeTileEntity` | 3 |
| `openmodularturrets:baseTierThreeBlock` | `turretBaseThree` | `TurretBaseTierFourTileEntity` | 4 |
| `openmodularturrets:baseTierFourBlock` | `turretBaseFour` | `TurretBaseTierFiveTileEntity` | 5 |

### Głowice wieżyczek (TurretHead)

Wszystkie głowice dziedziczą z klasy `TurretHead` – mają identyczną strukturę NBT.

| Block registry name (1.7.10) | TE ID (NBT `id`) | Klasa TE |
|---|---|---|
| `openmodularturrets:disposeItemTurret` | `disposableItemTurret` | `DisposableItemTurretTileEntity` |
| `openmodularturrets:potatoCannonTurret` | `potatoCannonTurret` | `PotatoCannonTurretTileEntity` |
| `openmodularturrets:machineGunTurret` | `machineGunTurret` | `GunTurretTileEntity` |
| `openmodularturrets:incendiaryTurret` | `incendiaryTurret` | `IncendiaryTurretTileEntity` |
| `openmodularturrets:grenadeTurret` | `grenadeTurret` | `GrenadeLauncherTurretTileEntity` |
| `openmodularturrets:relativisticTurret` | `relativisticTurret` | `RelativisticTurretTileEntity` |
| `openmodularturrets:rocketTurret` | `rocketTurret` | `RocketTurretTileEntity` |
| `openmodularturrets:teleporterTurret` | `teleporterTurret` | `TeleporterTurretTileEntity` |
| `openmodularturrets:laserTurret` | `laserTurret` | `LaserTurretTileEntity` |
| `openmodularturrets:railGunTurret` | `railGunTurret` | `RailGunTurretTileEntity` |

### Ekspandery energii (ExpanderPower)

Brak własnego NBT – tylko standardowe pola pozycji TileEntity.

| Block registry name (1.7.10) | TE ID (NBT `id`) |
|---|---|
| `openmodularturrets:expanderPowerTierOne` | `expanderPowerTierOne` |
| `openmodularturrets:expanderPowerTierTwo` | `expanderPowerTierTwo` |
| `openmodularturrets:expanderPowerTierThree` | `expanderPowerTierThree` |
| `openmodularturrets:expanderPowerTierFour` | `expanderPowerTierFour` |
| `openmodularturrets:expanderPowerTierFive` | `expanderPowerTierFive` |

### Ekspandery ekwipunku (ExpanderInv)

Przechowują inventory 9 slotów (amunicja/surowce dla wieżyczek).

| Block registry name (1.7.10) | TE ID (NBT `id`) |
|---|---|
| `openmodularturrets:expanderInvTierOne` | `expanderInvTierOne` |
| `openmodularturrets:expanderInvTierTwo` | `expanderInvTierTwo` |
| `openmodularturrets:expanderInvTierThree` | `expanderInvTierThree` |
| `openmodularturrets:expanderInvTierFour` | `expanderInvTierFour` |
| `openmodularturrets:expanderInvTierFive` | `expanderInvTierFive` |

### Pozostałe

| Block registry name (1.7.10) | TE ID (NBT `id`) | Uwagi |
|---|---|---|
| `openmodularturrets:leverBlock` | `leverTileEntity` | Dekoracyjna dźwignia powiązana z bazą tier 1; brak własnego NBT |

---

## Bloki 1.7.10 BEZ TileEntity

| Block registry name (1.7.10) | Liczba wariantów | Uwagi |
|---|---|---|
| `openmodularturrets:hardWallTierOne` … `hardWallTierFive` | 5 | Wytrzymałe ściany obronne – tylko blok, bez TE |
| `openmodularturrets:fenceTierOne` … `fenceTierFive` | 5 | Ogrodzenie obronne – tylko blok, bez TE |

---

## Struktury NBT 1.7.10

### 1. TurretBase (wspólna dla wszystkich 5 tierów baz)

Źródło: `TurretBase.java::writeToNBT()`

```nbt
{
  maxStorage: <int>,              # max pojemność RF (zależy od tiera)
  energyStored: <int>,            # aktualny zasób RF
  amountOfPotentia: <float>,      # zasób Potentia (Thaumcraft), domyślnie 0
  maxIO: <int>,                   # max RF/tick
  yAxisDetect: <int>,             # zasięg Y wykrywania celów (0–9, domyślnie 2)
  attacksMobs: <boolean>,         # atakuje hostile moby
  attacksNeutrals: <boolean>,     # atakuje neutral moby
  attacksPlayers: <boolean>,      # atakuje graczy
  owner: <string>,                # UUID właściciela (lub nazwa w trybie offline)
  ownerName: <string>,            # wyświetlana nazwa właściciela
  trustedPlayers: [               # NBTTagList type=10 (compound)
    {
      name: <string>,
      canOpenGUI: <boolean>,
      canChangeTargeting: <boolean>,
      admin: <boolean>,
      UUID: <string>              # opcjonalne w starych zapisach
    }
  ],
  active: <boolean>,              # czy wieżyczka jest aktywna
  inverted: <boolean>,            # inwersja sygnału RS
  redstone: <boolean>,            # aktualny stan RS
  computerAccessible: <boolean>,  # dostęp przez ComputerCraft/OpenComputers
  shouldConcealTurrets: <boolean>,# ukrywanie głowic (addon Concealer)
  multiTargeting: <boolean>,      # obsługa wielu celów jednocześnie
  storageEU: <double>,            # bufor EU z IC2 (opcjonalny)
  Inventory: [                    # NBTTagList type=10, 9 slotów (addony/ulepszenia/amunicja)
    { Slot: <byte>, id: <string>, Count: <byte>, Damage: <short>, tag: {...} }
  ],
  CamoStack: { ... }              # opcjonalny compound – ItemStack kamuflażowego bloku
}
```

**Kluczowe pola dla konwersji placeholder:**
- `owner` / `ownerName` – identyfikacja właściciela
- `energyStored` / `maxStorage` – stan energii
- `Inventory` – addony i ulepszenia montowane w bazie
- `trustedPlayers` – lista zaufanych graczy
- `active` / `inverted` / `attacksMobs` / `attacksPlayers` – konfiguracja

### 2. TurretHead (wspólna dla wszystkich 10 typów głowic)

Źródło: `TurretHead.java::writeToNBT()`

```nbt
{
  rotationXY: <float>,       # kąt celowania (pitch)
  rotationXZ: <float>,       # kąt celowania (yaw)
  ticksBeforeFire: <int>,    # odliczanie do strzału
  shouldConceal: <boolean>   # czy ukryta (addon Concealer)
}
```

**Uwaga:** Dane celowania są przejściowe (runtime-only) – nie mają wartości dla konwersji.

### 3. ExpanderInv (wspólna dla 5 tierów ekspanderów ekwipunku)

Źródło: `AbstractInvExpander.java::writeToNBT()`

```nbt
{
  Inventory: [               # NBTTagList type=10, 9 slotów (amunicja/surowce)
    { Slot: <byte>, id: <string>, Count: <byte>, Damage: <short>, tag: {...} }
  ]
}
```

### 4. ExpanderPower (ekspandery energii – wszystkie 5 tierów)

Brak własnego NBT. Klasa `AbstractPowerExpander` dziedziczy z `TileEntityOMT`, który tylko wywołuje `super.writeToNBT()`.

### 5. LeverTileEntity

Brak własnego NBT – klasa tylko wywołuje `super.writeToNBT()`.

---

## Sytuacja w 1.18.2

### Zamiennik: K-Turrets

Wg `docs/MAPAOWANIE_USUNIETYCH_MODOW.md` dokumentowany zamiennik to **K-Turrets** (`k_turrets`).
- GitHub: `AlexiyOrlov/k-turrets`, branch `1.18` (pokrywa 1.18.2)
- Źródła: `mod_src/118/actual_src/1.18.2/KTurrets/repo/`
- **K-Turrets NIE jest zainstalowany na serwerze `headless_server/1.18.2/mods/`** – wymagana instalacja przed Zadaniem 5b

### Architektura K-Turrets (1.18.2) – diametralna różnica paradygmatu

**K-Turrets jest entity-based, nie block-based.** Wieżyczki to encje (Mob), a nie bloki TileEntity.

| Komponent K-Turrets | Typ w 1.18.2 | Opis |
|---|---|---|
| `arrow_turret` | Mob entity | Wieżyczka strzelająca strzałami |
| `bullet_turret` | Mob entity | Wieżyczka kulkowa |
| `fire_charge_turret` | Mob entity | Wieżyczka z kulami ognia |
| `brick_turret` | Mob entity | Wieżyczka cegłowa |
| `gauss_turret` | Mob entity | Wieżyczka gaussowska (snajperska) |
| `cobble_turret` | Mob entity | Wieżyczka brukowa |
| + 6 wariantów dronów | Mob entity | `brick/bullet/cobble/arrow/gauss/firecharge_drone` |
| `titanium_ore` | Block (bez TE) | Ruda tytanu |
| `deepslate_titanium_ore` | Block (bez TE) | Ruda głębinowa |

Brak jakichkolwiek TileEntity/BlockEntity w K-Turrets – jedyne bloki to rudy bez stanu.

### NBT encji K-Turrets (klasa `Turret.java`)

```nbt
{
  Targets: {                    # CompoundTag: cele do atakowania
    Count: <int>,
    Target#0: <string>,         # np. "minecraft:zombie"
    Target#1: <string>,
    ...
  },
  Owner: <UUID>,                # UUID właściciela (jako IntArray/UUID tag)
  Mobile: <boolean>,            # czy wieżyczka może się poruszać
  "Player protection": <boolean>, # czy chroni graczy
  Team: <string>,               # ręcznie ustawiony team (pusty = brak)
  Exceptions: {                 # CompoundTag: gracze wyłączeni z atakowania
    IgnoredPlayer#0: <string>,
    IgnoredPlayer#1: <string>,
    ...
  }
}
```

### Mapowanie pól OMT → K-Turrets

| Pole OMT (TurretBase) | Pole K-Turrets | Uwagi |
|---|---|---|
| `owner` (string UUID) | `Owner` (UUID tag) | Bezpośrednie mapowanie |
| `attacksMobs` (boolean) | `Targets` list | Dodać typy hostile mobów jeśli true |
| `attacksPlayers` (boolean) | `"Player protection"` | Odwrócona logika: `!attacksPlayers` |
| `trustedPlayers` (list) | `Exceptions` | Zaufani gracze → wyłączeni z ataku |
| `multiTargeting` | `Targets` (wiele wpisów) | Pośrednie mapowanie |
| `active` (boolean) | brak odpowiednika | Pominąć |
| `energyStored` / `Inventory` | brak odpowiednika | K-Turrets nie używa RF ani slotów |
| `shouldConcealTurrets` | brak odpowiednika | Pominąć |

### Wyzwanie konwersji: cross-paradigm (bloki → encje)

OMT reprezentuje wieżyczki jako **bloki z TileEntity** na określonej pozycji.
K-Turrets reprezentuje je jako **encje Mob** spawnowane w świecie.

Konwersja wymaga generowania **entity spawn eventów** (nie `set_block`) na pozycji bazowego bloku OMT:
- Dla każdej bazy wieżyczki OMT → spawning event dla odpowiedniego entity K-Turrets
- Mapowanie tiera bazy OMT → konkretny typ wieżyczki K-Turrets (np. tier wyższy → `gauss_turret`)
- Głowica OMT determinuje typ wieżyczki K-Turrets (np. `railGunTurret` → `gauss_turret`)
- Ekspandery energii/ekwipunku: brak odpowiednika w K-Turrets → placeholder

---

## Priorytety konwersji

| Priorytet | Element OMT | Strategia | Cel K-Turrets |
|---|---|---|---|
| 1 (krytyczny) | Bazy wieżyczek (5 tierów) | Entity spawn event | Typ encji wg głowicy lub tiera bazy |
| 2 (średni) | Głowice wieżyczek (10 typów) | Informacja do spawnu bazy | Determinuje typ entity K-Turrets |
| 3 (średni) | Ekspandery ekwipunku (5 tierów) | Placeholder z Inventory | Brak odpowiednika; amunicja przepada |
| 4 (niski) | Ekspandery energii (5 tierów) | Placeholder minimalny | Brak odpowiednika w K-Turrets |
| 5 (pomiń/zamienna) | HardWall, Fence (10 bloków) | Zastąpić bedrockiem/obsydianem | Bloki obronne bez TE |
| 6 (pomiń) | Lever block | Pominąć | Dekoracja bez istotnego NBT |

### Mapowanie głowicy OMT → encji K-Turrets

| Głowica OMT | Proponowany typ encji K-Turrets |
|---|---|
| `railGunTurret` | `k_turrets:gauss_turret` (najbliższy snajperski) |
| `machineGunTurret` | `k_turrets:bullet_turret` |
| `incendiaryTurret` | `k_turrets:fire_charge_turret` |
| `grenadeTurret` | `k_turrets:brick_turret` |
| `rocketTurret` | `k_turrets:gauss_turret` |
| `laserTurret` | `k_turrets:gauss_turret` |
| `relativisticTurret` | `k_turrets:gauss_turret` |
| `potatoCannonTurret` | `k_turrets:cobble_turret` |
| `disposeItemTurret` | `k_turrets:arrow_turret` |
| `teleporterTurret` | placeholder (brak odpowiednika) |

---

## Identyfikacja TE ID w routerze

Do wykrywania przez `detect_mod()` w `router.py` potrzebne są wzorce:

```python
_OMT_TE_IDS = frozenset([
    # Bazy
    "turretbase", "turretWoodBase",
    "turretBaseOne", "turretBaseTwo", "turretBaseThree", "turretBaseFour",
    # Głowice
    "disposableItemTurret", "potatoCannonTurret", "machineGunTurret",
    "incendiaryTurret", "grenadeTurret", "relativisticTurret",
    "rocketTurret", "teleporterTurret", "laserTurret", "railGunTurret",
    # Ekspandery
    "expanderPowerTierOne", "expanderPowerTierTwo", "expanderPowerTierThree",
    "expanderPowerTierFour", "expanderPowerTierFive",
    "expanderInvTierOne", "expanderInvTierTwo", "expanderInvTierThree",
    "expanderInvTierFour", "expanderInvTierFive",
    # Misc
    "leverTileEntity",
])
```

---

## Statystyki

- **Bloków z TE:** 26 typów (5 baz + 10 głowic + 10 ekspanderów + 1 lever)
- **Bloków bez TE:** 10 (5 HardWall + 5 Fence)
- **Klas TE:** 3 klasy bazowe (`TurretBase`, `TurretHead`, `AbstractInvExpander`)
- **Odpowiednik w 1.18.2:** K-Turrets (`k_turrets`), źródła w `mod_src/118/actual_src/1.18.2/KTurrets/repo/`
- **Strategia konwersji:** entity spawn eventy dla baz+głowic, placeholder dla ekspanderów
- **Uwaga:** K-Turrets musi być zainstalowany na serwerze 1.18.2 przed Zadaniem 5b
