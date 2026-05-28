# Handoff: Reliquary - Zadanie 1 (Ukończone)

## Podsumowanie sesji

Ukończono **Zadanie 1** konwersji moda Reliquary z wersji 1.7.10 na 1.18.2.
Zadanie polegało na wypisaniu wszystkich bloków i Tile/Block Entities dodawanych przez mod oraz opisaniu ich funkcjonalności i struktury NBT.

Reliquary to mod magiczno-przygodowy (staves, chalice, baubles, system eliksirów). Spośród wszystkich modów w projekcie ma **wyjątkowo małą liczbę bloków** – zaledwie 6 bloków, z czego tylko 3 mają TileEntity.

## Ukończono

- [x] Analiza kodu źródłowego Reliquary 1.7.10 (xreliquary)
- [x] Analiza kodu źródłowego Reliquary 1.18.2 (reliquary / NeoForge)
- [x] Zebranie listy bloków 1.7.10 z CommonProxy i klas bloków
- [x] Zebranie listy bloków 1.18.2 z ModBlocks.java
- [x] Dokumentacja 3 Tile/Block Entities i ich struktury NBT
- [x] Identyfikacja różnic NBT między wersjami
- [x] Identyfikacja nowych bloków w 1.18.2 (Pedestal system – 34 nowe bloki)
- [x] Identyfikacja elementów bez odpowiednika (Pedestal – ignorować)
- [x] Określenie priorytetów konwersji

## Nowe pliki

| Plik | Opis |
|------|------|
| `src/converters/reliquary/RELIQUARY_BLOCKS_AND_TE.md` | Pełna analiza: lista bloków, mapowania ID, struktury NBT obu wersji, różnice, priorytety |

## Kluczowe wnioski

### Konwersja prosta (priorytet 1-2):
- **Alkahestry Altar**: NBT identyczny w obu wersjach, tylko zmiana klucza TE `reliquaryAltar` → `reliquary:alkahestry_altar`
- **Apothecary Mortar**: `pestleUsed` identyczny, inventory wymaga standardowego remappingu formatu item

### Konwersja wymagająca uwagi (priorytet 3):
- **Apothecary Cauldron**:
  - `hasGlowstone` (bool) → `glowstoneCount` (int): `true` → `1`
  - `potionEssence` (format XR) → `potionContents` (vanilla PotionContents): **kluczowy punkt ryzyka**
  - `liquidLevel` w 1.7.10 był w blockstate metadata (nie w NBT!), trzeba odczytać z chunk data
  - `hasDragonBreath` – nowe pole, ustawiać na `false`

### Ignorować:
- **Pedestal / Passive Pedestal** – 34 nowe bloki bez odpowiednika w 1.7.10

## Następne kroki (Zadanie 2)

Zgodnie z wzorcem projektu, kolejne zadanie to przygotowanie **symulacji działania** kluczowych funkcjonalności:

1. Symulacja konwersji `potionEssence` (format 1.7.10 XR) → `potionContents` (vanilla 1.18.2)
2. Symulacja konwersji inventory moździerza (format stary → ItemStackHandler NeoForge)
3. Symulacja odczytu `liquidLevel` z blockstate metadata → NBT kauldron

---

**Status:** ✅ Zadanie 1 ukończone  
**Data:** 2026-05-28
