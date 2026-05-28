# Handoff: Backpack (Eydamos) — Zadanie 1

## Podsumowanie sesji

Wykonano Zadanie 1 (wypisanie i opis elementów moda Backpack 1.7.10) dla moda Eydamos.  
Mod okazał się **nie dodawać żadnych bloków ani Tile Entities** w świecie — konwersja ogranicza się do itemów (plecaków w inventory) oraz zewnętrznych plików `.dat` w folderze `backpacks/`.

## Ukończono

- [x] Dekompilacja JAR moda `backpack-2.0.1-1.7.x.jar` do `mod_src/code_from_jar/backpack_1710/`
- [x] Analiza kodu źródłowego: `Backpack.java`, `ItemsBackpack.java`, `ItemBackpackBase.java`, `ItemBackpack.java`, `ItemWorkbenchBackpack.java`, `BackpackSave.java`, `PlayerSave.java`, `SaveFileHandler.java`, `BackpackUtil.java`, `ConfigurationBackpack.java`
- [x] Identyfikacja wszystkich itemów: `Backpack:backpack`, `Backpack:workbenchbackpack`, `Backpack:boundLeather`, `Backpack:tannedLeather`
- [x] Opis struktury NBT itemu plecaka (`backpack-UID`, `name`, `customName`)
- [x] Opis struktury plików `.dat` w `backpacks/backpacks/` (inventory, size, type, intelligent)
- [x] Opis struktury plików `.dat` w `backpacks/player/` (personalBackpack, personalBackpackOpen)
- [x] Dokumentacja mapowania damage/metadata → tier + kolor
- [x] Wstępne mapowanie na Sophisticated Backpacks 1.18.2
- [x] Utworzenie dokumentacji w `src/converters/backpack/BACKPACK_ELEMENTS_AND_DATA.md`

## Nowe pliki

- `src/converters/backpack/BACKPACK_ELEMENTS_AND_DATA.md` — pełna dokumentacja moda Backpack (Zadanie 1)
- `src/converters/backpack/HANDOFF_BACKPACK_ZADANIE1.md` — ten plik

## Zmodyfikowane pliki

- Brak

## Dekompilacja (nowy folder)

- `mod_src/code_from_jar/backpack_1710/` — zdekompilowane źródła moda Backpack 2.0.1

## Następne kroki

1. **Zadanie 2** — Przygotowanie symulacji działania funkcjonalności:
   - Symulacja `BackpackSave` (1.7.10) — jak itemy są przechowywane w pliku `.dat`
   - Symulacja `sophisticatedbackpacks:backpack` (1.18.2) — jak itemy są przechowywane w NBT itemu docelowego
   - Wymaga pobrania/analizy kodu źródłowego Sophisticated Backpacks 1.18.2

2. **Zadanie 3** — Kod konwersji:
   - Scalanie plików `backpacks/backpacks/<UUID>.dat` z itemami w `playerdata/` do NBT `sophisticatedbackpacks:backpack`
   - Mapowanie kolorów, tierów, rozmiarów
   - Obsługa workbench backpack (crafting upgrade)

## Uwagi

- Sophisticated Backpacks nie jest obecny w `mod_src/actual_src/1.18.2/` — trzeba go pobrać z GitHub (P3pp3rF1y/SophisticatedBackpacks, branch 1.18.x) przed Zadaniem 2.
- Config moda (`Backpack.cfg`) nie został odnaleziony w `modpack_1710/config/` — przyjąłem domyślne wartości 27/54 slotów.
- Wszystkie dane na mapie źródłowej znajdują się w `mapa_1710/backpacks/` (~700 plecaków, ~20 graczy z personal backpack).
