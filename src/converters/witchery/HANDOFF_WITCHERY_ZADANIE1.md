# Handoff: Witchery – Zadanie 1 (Ukończone)

## Podsumowanie sesji

Ukończono **Zadanie 1** konwersji moda Witchery z wersji 1.7.10 na 1.18.2.
Zadanie polegało na wypisaniu wszystkich bloków i TileEntities dodawanych przez mod
oraz opisaniu ich funkcjonalności i struktury NBT.

Kluczowe odkrycie: **Witchery nie ma portu na 1.18.2** – brak JARa w
`headless_server/1.18.2/mods/`. Całość konwersji będzie oparta na placeholder eventach
(identyczna strategia jak Open Modular Turrets).

## Ukończono

- [x] Analiza `WitcheryBlocks.java` – pełna lista bloków i ich TE klas
- [x] Analiza `BlockBaseContainer.java` – mechanizm rejestracji TE IDs
- [x] Weryfikacja bloków bez TileEntity (ok. 35 bloków)
- [x] Identyfikacja TE z bogatym NBT (12 bloków funkcjonalnych)
- [x] Identyfikacja TE specjalnych z danymi gracza/portalu (9 bloków)
- [x] Identyfikacja TE dekoracyjnych z minimalnym NBT (21 bloków)
- [x] Weryfikacja wyjątków rejestracji (WitchesOven, Distillery, FumeFunnel – tylko idle rejestruje TE)
- [x] Weryfikacja 1.18.2: brak Witchery w `headless_server/1.18.2/mods/`
- [x] Zapis dokumentu analizy `WITCHERY_BLOCKS_AND_TE.md`

## Nowe pliki

| Plik | Opis |
|------|------|
| `src/converters/witchery/__init__.py` | Inicjalizacja pakietu |
| `src/converters/witchery/WITCHERY_BLOCKS_AND_TE.md` | Pełna analiza: grupy TE, TE IDs, kluczowe pola NBT, strategia |
| `src/converters/witchery/HANDOFF_WITCHERY_ZADANIE1.md` | Ten plik |

## Kluczowe wnioski

### Architektura moda w 1.7.10

- **Mechanizm TE:** `BlockBaseContainer.func_149663_c(blockName)` rejestruje TE z kluczem
  równym nazwie bloku (np. `witchery:altar`). To oznacza że TE ID w NBT = `witchery:<nazwa>`.
- **Wyjątek "burning/filtered":** WitchesOven, Distillery, FumeFunnel mają dwa warianty bloku
  (idle + aktywny), ale TE rejestruje tylko wariant idle. Oba warianty bloku zapisują TE ID
  taki jak wariant idle.
- **Łączna liczba TE IDs:** ok. 52, podzielone na 5 grup wg złożoności NBT.
- **Detekcja w routerze:** prosta – wszystkie TE Witchery mają prefiks `witchery:`.

### Grupy funkcjonalne (priorytety konwersji):
- **Priorytet 1 – maszyny z inwentarzem:** Altar, Kettle, Cauldron, SpinningWheel,
  WitchesOven, Distillery, PoppetShelf, SilverVat, Brazier, BloodCrucible,
  LeechChest, RefillingChest
- **Priorytet 2 – stan gracza/specjalny:** Mirror, DreamCatcher, CrystalBall,
  Coffin, PlacedItem, AreaMarker (decurse), SpiritPortal
- **Priorytet 3 – dekoracyjne/minimalne:** Fetish (scarecrow/trent/witchsladder),
  statuy, pułapki, bloki cursed redstone, płyny brew

### Brak odpowiednika 1.18.2
- Nie zainstalowano żadnego zamiennika Witchery (Hexerei, Enchanted: Witchcraft)
- Strategia: **100% placeholdery** – te same co OMT
- Dane graczy (inwentarze w Kettle/WitchesOven, powiązania Mirror/DreamCatcher)
  zostaną zachowane w NBT placeholder eventach

## Następne kroki (Zadanie 2)

1. Stworzenie `src/converters/witchery/mappings.py` z:
   - `WITCHERY_TE_IDS` – frozenset wszystkich ok. 52 TE IDs
   - `TE_ID_TO_BLOCK_REGISTRY` – mapowanie TE ID → blok 1.7.10 (do pola `source_block_id`)
2. Stworzenie `src/converters/witchery/witchery_converter.py`:
   - Klasa `WitcheryConverter` analogiczna do `OpenModularTurretsConverter`
   - Metoda `convert_tile_entity()` generująca placeholder event
3. Dodanie `detect_mod()` w `router.py`:
   - Detekcja: `te_id.startswith("witchery:")`
   - Mod key: `"witchery"`
4. Podpięcie do dispatch w `convert_te_to_events()`
5. Testy jednostkowe dla kluczowych TE IDs
6. Testy: `python -m pytest src/converters/witchery/tests -q`

---

**Status:** ✅ Zadanie 1 ukończone  
**Data:** 2026-05-28
