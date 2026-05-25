# Handoff: BuildCraft – Krok 1 (Ukończony)

## Podsumowanie sesji

Ukończono **Krok 1** konwersji moda BuildCraft z wersji 1.7.10 na ekosystem 1.18.2 (Pipez / RFTools Builder / XNet / Integrated Dynamics).  
Krok polegał na wypisaniu wszystkich bloków i Tile Entities BuildCraft obecnych na mapie źródłowej oraz zebraniu statystyk per strefa.

## Ukończono

- [x] Stworzenie struktury konwertera: `src/converters/buildcraft/`
- [x] Implementacja skanera `step1_analyze.py` (optymalizacja: AnvilParser zamiast ModBlockExtractor)
- [x] Skanowanie stref (billund, choroszcz, iii_rzesza, rzym, zsrr) + regionów dodatkowych
- [x] Identyfikacja wszystkich Tile Entities BuildCraft na mapie
- [x] Identyfikacja bloków BuildCraft (numeryczne ID) w regionach z TE
- [x] Generacja raportu JSON (`buildcraft_step1_analysis.json`)
- [x] Generacja raportu Markdown (`buildcraft_step1_report.md`)

## Nowe pliki

| Plik | Opis |
|------|------|
| `src/converters/buildcraft/__init__.py` | Inicjalizacja pakietu konwertera BuildCraft |
| `src/converters/buildcraft/step1_analyze.py` | Skaner mapy – wykrywa TE i bloki BC, generuje raporty JSON/MD |
| `output/buildcraft_scan/buildcraft_step1_analysis.json` | Pełne dane: rozkład TE/bloków per strefa + pozycje |
| `output/buildcraft_scan/buildcraft_step1_report.md` | Raport podsumowujący w formie czytelnej |

## Kluczowe wyniki

### Statystyki ogólne

| Metryka | Wartość |
|---------|---------|
| Łącznie TileEntities | **403** |
| Unikalne typy TE | **11** |
| Łącznie bloki (bez TE) | **2426** |
| Unikalne ID bloków | **28** |

### Rozkład Tile Entities

| Tile Entity ID | Liczba | Kategoria |
|----------------|--------|-----------|
| `net.minecraft.src.buildcraft.transport.GenericPipe` | 260 | Transport (rury) |
| `net.minecraft.src.buildcraft.energy.TileEngineStone` | 57 | Energia (Stirling Engine) |
| `net.minecraft.src.buildcraft.factory.TileTank` | 30 | Factory (Tank) |
| `net.minecraft.src.buildcraft.energy.TileEngineWood` | 28 | Energia (Redstone Engine) |
| `net.minecraft.src.buildcraft.factory.TileLaser` | 9 | Factory (Laser) |
| `net.minecraft.src.buildcraft.energy.TileEngineIron` | 8 | Energia (Combustion Engine) |
| `net.minecraft.src.buildcraft.factory.TilePump` | 7 | Factory (Pump) |
| `net.minecraft.src.buildcraft.factory.TileIntegrationTable` | 1 | Factory (Integration Table) |
| `net.minecraft.src.buildcraft.factory.TileAssemblyTable` | 1 | Factory (Assembly Table) |
| `net.minecraft.src.buildcraft.commander.TileZonePlan` | 1 | Commander (Zone Plan) |
| `net.minecraft.src.buildcraft.factory.Refinery` | 1 | Factory (Refinery) |

### Rozkład per strefa

| Strefa | TE | Uwagi |
|--------|-----|-------|
| billund | 9 | Same rury (GenericPipe) |
| choroszcz | 0 | Brak BuildCraft |
| iii_rzesza | 91 | Duża baza: rury, lasery, silniki, assembly table, refinery |
| rzym | 146 | Najwięcej: głównie rury + silniki Stirling |
| zsrr | 20 | Rury + pompy + tanki |
| _extra_regions | 104 | Rury + silniki w okolicach spawnu i dalszych regionach |

### Top numeryczne ID bloków (bez TE)

Wykryto bloki z ID: 523 (919 szt.), 665 (543), 706 (302), 629 (240), 721 (85), 578 (77) i 23 innych.  
Wymagają mapowania na konkretne bloki BuildCraft na podstawie źródła 1.7.10 (heurystyka: zakres 512-768).

## Kluczowe wnioski dla kolejnych kroków

### 🔴 Krytyczne elementy wymagające szczególnej uwagi:

1. **GenericPipe (260 szt.)** – najliczniejszy element. Wymaga decyzji:
   - Czy konwertować 1:1 na Pipez (Item/Fluid/Energy)?
   - Czy pominąć (rury są tymczasową infrastrukturą)?
   - Logika gates/filtrów BC jest niemożliwa do przeniesienia bezstratnie.

2. **Silniki (93 szt. łącznie: Wood=28, Stone=57, Iron=8)** – źródła energii BC:
   - Redstone Engine → usuwać lub zastępować basic dynamo/generator
   - Stirling Engine → Thermal Dynamo (Steam/Magmatic) lub Mekanism Heat Generator
   - Combustion Engine → Mekanism Generator (np. Heat) lub Thermal Compression Dynamo

3. **Maszyny fabryczne (50 szt.):**
   - Tank (30) → Pipez/Thermal/Mekanism tanki
   - Pump (7) → Mekanism Electric Pump lub Create Pump
   - Laser (9) + Assembly/Integration Table (2) → **brak bezpośredniego odpowiednika**; do rozstrzygnięcia czy konwertować na inne bloki dekoracyjne/funkcjonalne
   - Refinery (1) → Thermal Refinery / Mekanism
   - Zone Plan (1) → RFTools Builder (Shape Card)

4. **Brak na mapie (co ciekawe):**
   - **Quarry** – nie wykryto żadnego TE Quarry/Builder/Filler ani Pump w kontekście quarry
   - **Auto Workbench** – nie wykryto
   - To sugeruje, że gracze nie używali maszyn wydobywczych/konstrukcyjnych BC lub zostały usunięte.

## Następne kroki (Krok 2)

Zgodnie z planem konwersji (`docs/PLAN.md`), kolejny krok to:

**Krok 2: Symulacje działania funkcjonalności BuildCraft**

Symulacje do przygotowania (w czystym Pythonie, bez mapy):
1. Symulacja transportu rurami (Item/Fluid/Energy) – jak mapować na Pipez
2. Symulacja silników BC (Wood/Stone/Iron) → generatory 1.18.2
3. Symulacja Tank + Pump → odpowiedniki Mekanism/Thermal/Create
4. Symulacja Assembly Table + Laser → brak odpowiednika, wymaga decyzji
5. Symulacja Zone Plan → RFTools Builder (Shape Cards)

Każda symulacja powinna zawierać:
- Dane wejściowe (NBT z 1.7.10)
- Oczekiwane dane wyjściowe (NBT/logika 1.18.2)
- Test weryfikujący poprawność

## Zalecenia przed Krokiem 2

1. Rozstrzygnąć decyzję architektoniczną: **co zrobić z 260 rurami GenericPipe?**
   - Opcja A: Pominąć (najprostsza, strata infrastruktury transportowej)
   - Opcja B: Zamienić na Pipez Item/Fluid/Universal (wymaga odgadnięcia typu z NBT rury)
   - Opcja C: Zamienić na XNet (jeśli były złożone sieci z gates/filtrami)

2. Rozstrzygnąć decyzję: **co zrobić z Laser + Assembly/Integration Table?**
   - Brak odpowiednika w 1.18.2; można zastąpić dekoracyjnymi blokami lub usunąć.

3. Przygotować wstępne mapowania bloków (numeryczne ID → nazwy BuildCraft 1.7.10 → bloki 1.18.2).

---

**Status:** ✅ Krok 1 ukończony – gotowe do przeglądu i akceptacji  
**Data:** 2026-05-24  
**Agent:** AI Konwersji BuildCraft
