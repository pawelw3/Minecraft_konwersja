# Reliquary – Zadanie 1: Bloki i Tile/Block Entities

## Podsumowanie moda

Reliquary to mod magiczno-przygodowy skupiony na zaklętych przedmiotach (staves, chalices, baubles) i systemu eliksirów (alkahestry/cauldron/mortar). W 1.7.10 pakiet rejestruje się jako `xreliquary`, w 1.18.2 jako `reliquary`.

Mod ma **wyjątkowo małą liczbę bloków z TileEntity** – większość funkcji realizowana jest przez itemy trzymane w ręce. Bloki z TE to tylko trzy: ołtarz alkahestru, kocioł i moździerz.

---

## Bloki 1.7.10 → 1.18.2

### Bloki rejestrowane przez Sandstone (1.7.10 używa nazw stringowych, nie numerycznych ID)

| Nazwa 1.7.10 (string key) | Klasa bloku 1.7.10 | Registry 1.18.2 | Klasa bloku 1.18.2 | Ma TE? |
|---|---|---|---|---|
| `alkahestry_altar` | `BlockAlkahestryAltar` | `reliquary:alkahestry_altar` | `AlkahestryAltarBlock` | TAK |
| `apothecary_cauldron` | `BlockApothecaryCauldron` | `reliquary:apothecary_cauldron` | `ApothecaryCauldronBlock` | TAK |
| `apothecary_mortar` | `BlockApothecaryMortar` | `reliquary:apothecary_mortar` | `ApothecaryMortarBlock` | TAK |
| `fertile_lily_pad` | `BlockFertileLilypad` | `reliquary:fertile_lily_pad` | `FertileLilyPadBlock` | NIE |
| `interdiction_torch` | `BlockInterdictionTorch` | `reliquary:interdiction_torch` | `InterdictionTorchBlock` | NIE |
| `wraith_node` | `BlockWraithNode` | `reliquary:wraith_node` | `WraithNodeBlock` | NIE |
| *(brak)* | *(brak)* | `reliquary:wall_interdiction_torch` | `WallInterdictionTorchBlock` | NIE |
| *(brak)* | *(brak)* | `reliquary:pedestals/<color>_pedestal` | `PedestalBlock` (×16 kolorów) | TAK |
| *(brak)* | *(brak)* | `reliquary:pedestals/passive/<color>_passive_pedestal` | `PassivePedestalBlock` (×16 kolorów) | TAK |

### Bloki nowe w 1.18.2 (brak odpowiednika w 1.7.10)

- **Pedestal** i **Passive Pedestal** – 16 kolorów DyeColor każdy. Zupełnie nowy system pozwalający umieszczać przedmioty na cokołach i automatyzować ich działanie. Nie mają odpowiednika w 1.7.10.
- **Wall Interdiction Torch** – ścienna wersja pochodni, pochodna `InterdictionTorchBlock`.

---

## Tile/Block Entities – szczegóły

### 1. Alkahestry Altar (Ołtarz Alkahestru)

**Funkcja:** Ołtarz alchemiczny aktywowany wbijaniem redstone'a. Po zebraniu wymaganej liczby RS startuje cykl (domyślnie 20 min), w trakcie którego musi mieć dostęp do nieba i trwa za dnia. Po zakończeniu umieszcza blok glowstone nad sobą.

| Parametr | 1.7.10 | 1.18.2 |
|---|---|---|
| TE registry name | `reliquaryAltar` | `reliquary:alkahestry_altar` |
| Klasa TE | `TileEntityAltar` | `AlkahestryAltarBlockEntity` |

**NBT 1.7.10:**
```nbt
{
  cycleTime: <short>,      # pozostały czas cyklu w tickach
  redstoneCount: <short>,  # ilość wbitego redstone
  isActive: <boolean>      # czy cykl trwa
}
```

**NBT 1.18.2:**
```nbt
{
  cycleTime: <short>,      # identyczny
  redstoneCount: <short>,  # identyczny
  isActive: <boolean>      # identyczny
}
```

**Wnioski:** NBT jest **identyczny** między wersjami. Konwersja to wyłącznie zmiana klucza TE: `reliquaryAltar` → `reliquary:alkahestry_altar`.

---

### 2. Apothecary Cauldron (Kocioł Aptekarza)

**Funkcja:** Kocioł do warzenia eliksirów. Wymaga wody (3 poziomy), źródła ciepła pod spodem i składników wrzucanych przez gracza (PotionEssence + netherwart + opcjonalne wzmocnienia). Po ugotowaniu można nabierać eliksiry do fiolek.

| Parametr | 1.7.10 | 1.18.2 |
|---|---|---|
| TE registry name | `reliquaryCauldron` | `reliquary:apothecary_cauldron` |
| Klasa TE | `TileEntityCauldron` | `ApothecaryCauldronBlockEntity` |

**NBT 1.7.10:**
```nbt
{
  cookTime: <int>,
  redstoneCount: <int>,
  hasGlowstone: <boolean>,   # pojedyncza flaga
  hasGunpowder: <boolean>,
  hasNetherwart: <boolean>,
  potionEssence: {            # zagnieżdżony compound PotionEssence
    effects: [ ... ]
  }
  # poziom wody = blockstate metadata (nie w NBT!)
}
```

**NBT 1.18.2:**
```nbt
{
  cookTime: <int>,
  redstoneCount: <int>,
  glowstoneCount: <int>,     # liczba (nie boolean!) – można dodawać wielokrotnie
  hasGunpowder: <boolean>,
  hasDragonBreath: <boolean>, # NOWE – lingering potion
  hasNetherwart: <boolean>,
  liquidLevel: <int>,        # NOWE – poziom wody przeniesiony do NBT
  # potionContents zapisywane przez PotionHelper (klucze: "CustomPotionEffects" itp.)
}
```

**Kluczowe różnice:**
- `hasGlowstone` (bool) → `glowstoneCount` (int): mapper powinien konwertować `true` → `1`, `false` → `0`
- `hasDragonBreath` nie ma odpowiednika w 1.7.10 → domyślnie `false`
- `liquidLevel` w 1.7.10 był w blockstate metadata (0–3), trzeba odczytać z chunk data bloku
- `potionEssence` (format XR) → `potionContents` (format vanilla 1.18.2 `PotionContents`): **wymagana konwersja formatu**

---

### 3. Apothecary Mortar (Moździerz Aptekarza)

**Funkcja:** Moździerz do mielenia składników na PotionEssence. Gracz wkłada do 3 składników, a następnie 5-krotnie używa tłuczka (prawy klik). Wyrzuca gotowy PotionEssence jako item.

| Parametr | 1.7.10 | 1.18.2 |
|---|---|---|
| TE registry name | `apothecaryMortar` | `reliquary:apothecary_mortar` |
| Klasa TE | `TileEntityMortar` | `ApothecaryMortarBlockEntity` |

**NBT 1.7.10:**
```nbt
{
  pestleUsed: <short>,        # liczba użyć tłuczka (0–5)
  Items: [                    # NBTTagList formatu vanilla inventory
    { Slot: <byte>, id: <string>, Count: <byte>, Damage: <short>, tag: {...} },
    ...
  ]
}
```

**NBT 1.18.2:**
```nbt
{
  pestleUsed: <short>,        # identyczny klucz i typ
  items: {                    # compound z ItemStackHandler NeoForge
    Size: 3,
    Items: [
      { Slot: <int>, id: <string>, count: <int>, components: {...} },
      ...
    ]
  }
}
```

**Kluczowe różnice:**
- `Items` (wielka litera, top-level) → `items.Items` (w sub-compound)
- Klucz `items` zawiera format `ItemStackHandler` NeoForge (dodatkowy `Size` i zmieniony format itemów)
- Format poszczególnych itemów: 1.7.10 `{id, Count, Damage, tag}` → 1.18.2 `{id, count, components}`
- `pestleUsed` – klucz i typ identyczne (short)

---

### 4. Pedestal / Passive Pedestal (NOWE w 1.18.2)

**Funkcja:** Cokoły do umieszczania przedmiotów mod-specyficznych (np. staffs, rods). Passive Pedestal przechowuje przedmiot; aktywny Pedestal dodatkowo wykonuje akcje przedmiotu (zależne od `IPedestalActionItem` API).

**Brak odpowiednika w 1.7.10 – nie konwertować ze starszych danych.**

**NBT 1.18.2 (PassivePedestalBlockEntity):**
```nbt
{
  item: { id: <string>, count: <int>, components: {...} }  # opcjonalny
}
```

**NBT 1.18.2 (PedestalBlockEntity, extends Passive):**
```nbt
{
  item: { ... },
  SwitchedOn: <boolean>,
  Powered: <boolean>,
  OnSwitches: [ <long>, ... ]   # lista BlockPos.asLong() połączonych przełączników
}
```

---

## Bloki bez TE

| Blok | 1.7.10 | 1.18.2 | Uwagi |
|---|---|---|---|
| Fertile Lily Pad | `fertile_lily_pad` | `reliquary:fertile_lily_pad` | Bezpośrednie mapowanie bloku, brak NBT |
| Interdiction Torch | `interdiction_torch` | `reliquary:interdiction_torch` | Bezpośrednie mapowanie, brak NBT |
| Wraith Node | `wraith_node` | `reliquary:wraith_node` | Bezpośrednie mapowanie, brak NBT |

---

## Priorytety konwersji

| Priorytet | Element | Trudność | Uzasadnienie |
|---|---|---|---|
| 1 (krytyczny) | Alkahestry Altar | Niska | NBT identyczny, tylko zmiana klucza TE |
| 2 (krytyczny) | Apothecary Mortar | Niska | `pestleUsed` identyczny, tylko remapping formatu inventory |
| 3 (średni) | Apothecary Cauldron | Średnia | Zmiana `hasGlowstone`→`glowstoneCount`, brak `hasDragonBreath`, konwersja `potionEssence` |
| 4 (niski) | Bloki bez TE | Zerowa | Tylko remapping ID bloku |
| 5 (ignoruj) | Pedestal / Passive Pedestal | N/A | Nowe w 1.18.2, brak źródłowych danych |

---

## Kluczowe wnioski dla Zadania 2

1. **Alkahestry Altar** – najprostsza konwersja w całym modzie: zmiana klucza TE + identyczny NBT.
2. **Apothecary Mortar** – `pestleUsed` przechodzi bez zmian; składniki w slotkach wymagają remappingu formatu item (`Count`/`Damage` → `count`/`components`), ale to standardowy pipe konwersji itemów projektu.
3. **Apothecary Cauldron** – wymaga dwóch nietrywialnych mapowań:
   - `potionEssence` (format XR) → `potionContents` (PotionContents vanilla): kluczowy punkt ryzyka, wymaga osobnych symulacji
   - `hasGlowstone` bool → `glowstoneCount` int
4. **liquidLevel kaldron** – poziom wody w 1.7.10 był w blockstate (metadata 0–3), nie w NBT TileEntity. Przy konwersji chunków trzeba odczytać metadata bloku z chunk data i przepisać jako `liquidLevel` do NBT TE.
5. **Pedestal** – nie konwertować (nowy system bez źródła w 1.7.10).

---

## Statystyki

- **Bloków z TE:** 3 w 1.7.10, 5 typów BE w 1.18.2 (3 wspólne + 2 nowe Pedestal)
- **Bloków bez TE:** 3 w obu wersjach (+1 nowy `wall_interdiction_torch`)
- **Bezpośrednie mapowanie bloków:** 100% (wszystkie 1.7.10 mają odpowiedniki w 1.18.2)
- **Bezpośrednie mapowanie TE:** ~33% (tylko Altar – pozostałe wymagają transformacji)
- **Nowe bloki w 1.18.2:** 34 (16 Pedestal + 16 Passive Pedestal + wall torch)
