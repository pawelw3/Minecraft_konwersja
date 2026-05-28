# Handoff: Open Modular Turrets – Zadanie 1 (Ukończone)

## Podsumowanie sesji

Ukończono **Zadanie 1** konwersji moda Open Modular Turrets z wersji 1.7.10 na 1.18.2.
Zadanie polegało na wypisaniu wszystkich bloków i Tile/Block Entities dodawanych przez mod oraz opisaniu ich funkcjonalności i struktury NBT.

Kluczowe odkrycie: **Open Modular Turrets nie posiada portu na 1.18.2** – brak źródeł w `mod_src/118/` i brak JARa w `headless_server/1.18.2/mods/`. Całość konwersji będzie oparta na placeholder eventach.

## Ukończono

- [x] Analiza kodu źródłowego OMT 1.7.10 (`TileEntityHandler.java`, `Blocks.java`, `Names.java`)
- [x] Analiza klasy `TurretBase.java` – pełna struktura NBT baz wieżyczek
- [x] Analiza klasy `TurretHead.java` – struktura NBT głowic
- [x] Analiza `AbstractInvExpander.java` – struktura NBT ekspanderów ekwipunku
- [x] Analiza `AbstractPowerExpander.java` / `LeverTileEntity.java` – brak własnego NBT
- [x] Weryfikacja 1.18.2: brak moda OMT w `mod_src/118/` i `headless_server/1.18.2/mods/`
- [x] Identyfikacja 26 bloków z TE i 10 bloków bez TE
- [x] Dokument analizy `OMT_BLOCKS_AND_TE.md`

## Nowe pliki

| Plik | Opis |
|------|------|
| `src/converters/openmodularturrets/__init__.py` | Inicjalizacja pakietu |
| `src/converters/openmodularturrets/OMT_BLOCKS_AND_TE.md` | Pełna analiza: lista bloków, TE IDs, struktury NBT, K-Turrets architektura, priorytety |
| `src/converters/openmodularturrets/HANDOFF_OMT_ZADANIE1.md` | Ten plik |
| `mod_src/118/actual_src/1.18.2/KTurrets/repo/` | Klonowane źródła K-Turrets (branch 1.18) |

## Kluczowe wnioski

### Architektura moda w 1.7.10
- **Bazy (5 tierów):** `TurretBase` – bogate NBT: owner/UUID, trustedPlayers, inventory 9 slotów (addony/ulepszenia), energia RF, flagi celowania
- **Głowice (10 typów):** `TurretHead` – minimalne NBT: rotacja (runtime), shouldConceal; dane są przejściowe
- **Ekspandery energii (5 tierów):** brak własnego NBT
- **Ekspandery ekwipunku (5 tierów):** tylko Inventory 9 slotów
- **Bloki bez TE:** HardWall (5), Fence (5) – bloki obronne bez stanu

### Zamiennik: K-Turrets – całkowita zmiana paradygmatu
- Zamiennik wg `docs/MAPAOWANIE_USUNIETYCH_MODOW.md`: **K-Turrets** (`k_turrets`)
- Źródła pobrane do: `mod_src/118/actual_src/1.18.2/KTurrets/repo/`
- **K-Turrets NIE jest zainstalowany na serwerze 1.18.2** – wymagana instalacja przed Zadaniem 5b
- OMT używa **bloków z TileEntity**, K-Turrets używa **encji Mob** – to zupełnie inny paradygmat
- K-Turrets ma 6 typów wieżyczek (arrow/bullet/fire_charge/brick/gauss/cobble) + 6 dronów
- K-Turrets nie ma systemu energii RF, ekspanderów, ani slotów amunicji

### Strategia konwersji (zaktualizowana)
- **Bazy + głowice:** entity spawn event na pozycji bazy; typ encji determinuje głowica OMT
- **Owner/targeting:** mapowalne: `owner`→`Owner`, `attacksPlayers`→`"Player protection"` (odwrócone), `trustedPlayers`→`Exceptions`
- **Ekspandery ekwipunku (priorytet 2):** placeholder – amunicja przepada (brak odpowiednika)
- **Ekspandery energii (priorytet 4):** placeholder minimalny
- **Głowice wieżyczek:** nie tworzą osobnego obiektu w 1.18.2 – informacja z głowicy koduje typ encji K-Turrets

## Następne kroki (Zadanie 2)

Zadanie 2 to symulacje zachowania – ale ze względu na brak symulacji po stronie K-Turrets (entity spawn jest deterministyczny), można przejść bezpośrednio do **Zadania 3 (konwerter)**:

1. Implementacja `OpenModularTurretsConverter` generującego entity spawn eventy (bazy+głowice) i placeholder eventy (ekspandery)
2. Dodanie `detect_mod()` w `router.py` rozpoznającego wszystkie TE IDs OMT
3. Podpięcie do routera (mod key: `openmodularturrets`)
4. Testy jednostkowe dla kluczowych TE IDs
5. Instalacja K-Turrets JAR na serwerze (przed Zadaniem 5b)

---

**Status:** ✅ Zadanie 1 ukończone  
**Data:** 2026-05-28
