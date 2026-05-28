# Handoff: Backpack (Eydamos) — Zadanie 2

## Podsumowanie sesji

Wykonano Zadanie 2 (symulacje działania funkcjonalności) dla moda Backpack 1.7.10 i Sophisticated Backpacks 1.18.2.  
Przygotowano trzy symulacje w Pythonie oparte na dokładnym kodzie źródłowym obu modów, które demonstrują tworzenie, zapis, odczyt i konwersję danych plecaków.

## Ukończono

- [x] Symulacja źródłowa 1.7.10 (`backpack_1710_simulation.py`)
  - Tworzenie `ItemStack1710` z damage/meta
  - Inicjalizacja `BackpackSave1710` (UUID, rozmiar, type)
  - Zapis/odczyt inventory w formacie NBT 1.7.10
  - Przypadki: small red, big workbench, ender
- [x] Symulacja docelowa 1.18.2 (`backpack_1182_simulation.py`)
  - Tworzenie `ItemStack1182` z tierem i kolorami RGB
  - Generowanie `contentsUuid` i zapis do `BackpackStorage1182`
  - Format NBT inventory (`ItemStackHandler` z `realCount`)
  - Format NBT upgradeInventory (Crafting Upgrade)
  - Przypadki: leather red, iron + crafting, netherite default
- [x] Symulacja konwersji (`backpack_conversion_simulation.py`)
  - Mapowanie tierów: small→leather, big→iron/copper/gold/diamond/netherite
  - Mapowanie kolorów: nazwa Eydamos → `DyeColor` → RGB int
  - Konwersja inventory: format 1.7.10 → `ItemStackHandler` 1.18.2
  - Generowanie upgrade'ów: workbench → `sophisticatedcore:crafting_upgrade`
  - Obsługa edge-case'ów: ender backpack, size override, customName
  - Symulacja batchowa (3 plecaki do jednego BackpackStorage)
- [x] Pobrano i zweryfikowano repozytoria docelowe:
  - `mod_src/actual_src/1.18.2/SophisticatedBackpacks/`
  - `mod_src/actual_src/1.18.2/SophisticatedCore/`

## Nowe pliki

- `src/converters/backpack/simulations/backpack_1710_simulation.py`
- `src/converters/backpack/simulations/backpack_1182_simulation.py`
- `src/converters/backpack/simulations/backpack_conversion_simulation.py`
- `src/converters/backpack/HANDOFF_BACKPACK_ZADANIE2.md`

## Zmodyfikowane pliki

- `src/converters/backpack/BACKPACK_ELEMENTS_AND_DATA.md` — uzupełniona sekcja 6 i 7.2 o analizę SB 1.18.2

## Kluczowe ustalenia z symulacji

### 1. Architektura danych w SB 1.18.2 jest analogiczna do źródła!
Obie wersje używają **zewnętrznego storage per UUID**:
- 1.7.10: `backpacks/backpacks/<UUID>.dat`
- 1.18.2: `data/sophisticatedbackpacks.dat` → `backpackContents[<UUID>]`

To znacząco upraszcza konwersję — nie trzeba "pakować" inventory do NBT itemu.

### 2. Mapowanie tierów (rozmiarów)

| Rozmiar 1.7.10 | Docelowy item SB |
|----------------|-----------------|
| 9 (workbench small) | `backpack` (leather) z override size=9 |
| 18 (workbench big) | `backpack` (leather) z override size=18 |
| 27 (small / ender) | `backpack` (leather) domyślnie |
| 45-53 (medium?) | `copper_backpack` |
| 54 (big) | `iron_backpack` |
| 55-80 | `gold_backpack` |
| 81-107 | `diamond_backpack` |
| 108+ | `netherite_backpack` |

### 3. Wymagane komponenty do Zadania 3

- **Globalny resolver ID itemów** 1.7.10 → 1.18.2 (numeryczne/string → `minecraft:xxx` / `mod:xxx`)
- **Konwersja `playerdata/`** — znalezienie wszystkich `Backpack:backpack` i `Backpack:workbenchbackpack` w inventory graczy
- **Konwersja `backpacks/player/`** — przeniesienie `personalBackpack` do zwykłego inventory lub Curios slotu
- **Batch processing** — ~700 plików `.dat` w `mapa_1710/backpacks/backpacks/`

## Otwarte pytania (rozstrzygnięte w Zadaniu 2)

1. ✅ **Struktura NBT SB:** Zweryfikowano — `BackpackStorage` + `ItemStack` z `contentsUuid`
2. ✅ **Kolory:** `clothColor` + `borderColor` jako int RGB (domyślne: 13394234 / 6434330)
3. ✅ **Tiers:** leather=27, copper=45, iron=54, gold=81, diamond=108, netherite=120
4. ✅ **Ender backpack:** Brak odpowiednika → `iron_backpack` z warningiem
5. ✅ **Workbench:** `sophisticatedcore:crafting_upgrade` w `upgradeInventory`
6. ✅ **Personal backpack:** Curios API (slot "back") lub zwykłe inventory

## Pozostałe pytania na Zadanie 3

1. Czy w projekcie istnieje już globalny resolver ID itemów 1.7.10 → 1.18.2?
2. Czy docelowy serwer 1.18.2 ma zainstalowany Curios API?
3. Jakie były faktyczne wartości `BACKPACK_SLOTS_S` / `BACKPACK_SLOTS_L` w configu serwera?

---

**Status:** ✅ Zadanie 2 ukończone  
**Następny krok:** Zadanie 3 — Kod konwersji (skrypt Python przetwarzający `mapa_1710/backpacks/` + `playerdata/`)
