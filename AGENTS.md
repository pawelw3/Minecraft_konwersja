# AGENTS.md - Dokumentacja projektu dla AI

> **Język dokumentacji:** Polski (taki sam jak w dokumentacji projektu)
> **Data utworzenia:** 2026-01-30
> **Ostatnia aktualizacja:** 2026-01-30 (dodano strukturę src/ i mod_src/)

---

## 1. Przegląd projektu

### 1.1 Czym jest ten projekt?

Ten projekt to **konwersja mapy Minecraft z wersji 1.7.10 na 1.18.2**. Jest to złożone przedsięwzięcie wymagające:
- Konwersji bloków i tile entities między formatami NBT różnych wersji
- Mapowania modów 1.7.10 na ich odpowiedniki w 1.18.2 (lub zamienniki)
- Zachowania jak największej ilości danych graczy (inventory, bazy, maszyny)

### 1.2 Dlaczego to trudne?

| Problem techniczny | Opis |
|-------------------|------|
| Zmiana systemu ID bloków | 1.7.10: numeryczne ID (0-4095) + metadata; 1.18.2: string ID (`minecraft:stone`) |
| Rozszerzenie wysokości świata | 1.7.10: Y=0-255; 1.18.2: Y=-64 do 320 |
| Zmiany formatu NBT | Nowa struktura chunk, biomy per-block |
| Mody mogą nie istnieć | Brak odpowiedników dla niektórych modów w 1.18.2 |
| Tile Entities | Maszyny, skrzynie tracą dane przy braku modu |

### 1.3 Struktura projektu

```
Minecraft_konwersja/
├── docs/                          # Dokumentacja projektu
│   ├── PLAN_KONWERSJI.md          # Główny plan konwersji
│   ├── WORKFLOW.md                # Metodyka pracy z Claude
│   ├── LISTA_KONWERSJI_MODOW.md   # Lista modów i ich mapowanie
│   ├── ANALIZA_MODOW_SZCZEGOLOWA.md  # Szczegółowa analiza modów
│   ├── MINECRAFT_MAP_PARSER.md    # Dokumentacja parsera mapy
│   ├── IGNORED_BLOCKS.md          # Lista bloków/TE do ignorowania
│   ├── sc_available_1710.md       # Dostępność modów 1.7.10
│   ├── sc_available_118.md        # Dostępność modów 1.18.2
│   ├── conversion-list.xlsx       # Lista konwersji (Excel)
│   └── mod_mapping_indepth/       # Szczegółowe mapowanie modów
│       ├── from/                  # Analiza modów źródłowych (1.7.10)
│       └── to/                    # Mapowanie na 1.18.2
├── output/                        # Wyniki, wizualizacje, raporty
│   └── visualizations/            # Wizualizacje mapy (SVG, HTML)
├── src/                           # Główny kod projektu (Python)
│   ├── minecraft_map_parser/      # Parser mapy Minecraft
│   │   ├── __init__.py
│   │   ├── nbt_parser.py          # Parser NBT
│   │   ├── anvil_parser.py        # Parser regionów MCA
│   │   ├── mod_block_extractor.py # Ekstraktor bloków z modów
│   │   ├── visualizer.py          # Wizualizator SVG
│   │   └── README.md              # Dokumentacja modułu
│   ├── visualize_choroszcz.py     # Skrypt wizualizacji strefy
│   ├── analyze_shape.py           # Analiza kształtu struktur
│   └── analyze_ae2_blocks.py      # Analiza bloków AE2
├── mod_src/                       # Kody źródłowe modów (repozytoria)
│   └── actual_src/                # Pobrane repozytoria modów
│       ├── 1.7.10/                # Mody źródłowe 1.7.10
│       └── 1.18.2/                # Mody docelowe 1.18.2
├── mapa_1710/                     # Dane mapy źródłowej (1.7.10)
├── mapa_118/                      # Dane mapy docelowej (1.18.2) - pusta
├── modpack_1710/                  # Pliki modpacka 1.7.10 (JARy)
├── lightweigh_map_templates/      # Szablony lekkich map testowych
│   ├── 1710/                      # Mapy testowe 1.7.10
│   └── 118/                       # Mapy testowe 1.18.2
├── strefy/                        # Definicje stref na mapie
│   ├── billund/
│   ├── choroszcz/
│   ├── iii_rzesza/
│   ├── rzym/
│   └── zsrr/
├── brute_force_trial_ae2/         # Testowe konwersje AE2
├── headless_server/               # Serwer headless do testów
└── AGENTS.md                      # Ten plik
```

---

## 2. Kluczowe pliki dokumentacji

### 2.1 Plany i workflow

| Plik | Zawartość |
|------|-----------|
| `docs/PLAN_KONWERSJI.md` | Architektura konwertera, plan etapów, system testowania |
| `docs/WORKFLOW.md` | Metodyka pracy z Claude Code, dokumentacja HANDOFF |
| `docs/LISTA_KONWERSJI_MODOW.md` | Pełna lista 56 modów z paczki i ich mapowanie na 1.18.2 |
| `docs/ANALIZA_MODOW_SZCZEGOLOWA.md` | Szczegółowe mapowanie bloków, tile entities, NBT |

### 2.2 Dokumentacja modów (szczegółowa)

W `docs/mod_mapping_indepth/`:
- `from/mod_funkcjonalnosci_1.7.10_*.md` - Analiza funkcjonalności modów 1.7.10
- `to/konwersja_1710_do_1182_mapowanie_modow_*.md` - Mapowanie na mody 1.18.2

### 2.3 Bloki/Tile Entities do ignorowania

`docs/IGNORED_BLOCKS.md` zawiera listę elementów które **nie będą konwertowane**:
- Techniczne TE (np. `RCHiddenTile` z Railcrafta)
- Markery systemowe
- Placeholdery wewnętrzne modów

---

## 3. Technologia i stack

### 3.1 Kod źródłowy

Projekt zawiera kod źródłowy w folderze `src/`:

| Moduł | Opis |
|-------|------|
| `src/minecraft_map_parser/` | Parser mapy Minecraft 1.7.10 - ekstrakcja bloków, tile entities, wizualizacja |

Pozostała część projektu to:
- **Analityczna** - dokumentacja i planowanie w `docs/`
- **Konfiguracyjna** - mapowania, definicje stref

### 3.2 Stack technologiczny

- **Język:** Python 3.10+
- **Format mapowań:** YAML (planowane)
- **Testowanie:** pytest (planowane)
- **Narzędzia zewnętrzne:**
  - MCA Selector - przeglądanie/edycja chunków
  - NBTExplorer - ręczna edycja danych NBT
  - Amulet Editor - zaawansowana edycja światów

### 3.3 Formaty danych

- **Mapy Minecraft:** Format Anvil (`.mca` w folderze `region/`)
- **Dane NBT:** Named Binary Tag (przechowywanie danych bloków, inventory)
- **Konfiguracja stref:** JSON (`coords.json`)
- **Dokumentacja:** Markdown

---

## 4. Organizacja kodu/danych

### 4.1 Kod źródłowy (src/)

Główny kod projektu w Pythonie:

```
src/
├── minecraft_map_parser/      # Parser mapy Minecraft
│   ├── nbt_parser.py          # Parser NBT
│   ├── anvil_parser.py        # Parser regionów MCA
│   ├── mod_block_extractor.py # Ekstraktor bloków z modów
│   ├── visualizer.py          # Wizualizator SVG
│   └── README.md
├── visualize_choroszcz.py     # Skrypt wizualizacji
├── analyze_shape.py           # Analiza struktur
└── README.md
```

### 4.2 Kody źródłowe modów (mod_src/)

Repozytoria kodów źródłowych modów:
- `actual_src/1.7.10/` - Mody źródłowe (AE2, Mekanism, IC2, ...)
- `actual_src/1.18.2/` - Mody docelowe (AE2 11.x, Mekanism 10.x, ...)
- `code_from_jar/` - Dekompilowane kody z JAR

### 4.3 Mapy Minecraft

#### Mapa źródłowa (mapa_1710/)
Zawiera dane świata 1.7.10:
- `region/` - Pliki chunków (`.mca`)
- `playerdata/` - Dane graczy
- `level.dat` - Główne dane świata
- Foldery modów: `AE2/`, `backpacks/`, `cofh/`, `JABBA/`, etc.

#### Mapa docelowa (mapa_118/)
Obecnie pusta - tu będzie wynik konwersji.

### 4.4 Strefy (strefy/)

Każda strefa to obszar na mapie zdefiniowany współrzędnymi:

```json
{
    "name": "billund",
    "minecraftCoordinates": [
        {"x": 280, "z": -81},
        {"x": 602, "z": -81},
        {"x": 602, "z": -364},
        {"x": 280, "z": -364}
    ]
}
```

Strefy zdefiniowane:
- `billund/` - Billund
- `choroszcz/` - Choroszcz  
- `iii_rzesza/` - III Rzesza
- `rzym/` - Rzym
- `zsrr/` - ZSRR

### 4.5 Modpack (modpack_1710/)

Zawiera 56 modów głównych i 16 bibliotek:
- Mody główne: `appliedenergistics2-*.jar`, `Mekanism-*.jar`, itp.
- Biblioteki: `CodeChickenLib-*.jar`, `CoFHCore-*.jar`, itp.
- Konfiguracje modów w podfolderach: `carpentersblocks/`, `ic2/`, `railcraft/`

### 4.6 Output (output/)

Wyniki analiz, wizualizacji i raportów:
- `visualizations/` - Wizualizacje SVG i podsumowania HTML

---

## 5. Kategorie konwersji modów

### 5.1 Bezpośrednia aktualizacja (21 modów) ✅

Te same mody dostępne dla 1.18.2:
- Applied Energistics 2 → AE2 11.7.6
- Mekanism → Mekanism 10.2.5
- Thermal Series → Thermal Series 9.2.2
- Tinkers' Construct → TiC 3.7.2
- Blood Magic → Blood Magic 3.2.6
- ...i inne (pełna lista w `LISTA_KONWERSJI_MODOW.md`)

### 5.2 Automatyczna konwersja (5 modów) ⚠️

Wymagają mapowania bloków/Tile Entities:
- **IndustrialCraft 2** → Mekanism/Thermal (EU→FE ×4)
- **BuildCraft** → RFTools Builder + Pretty Pipes
- **JABBA** → Storage Drawers
- **Logistics Pipes** → Pretty Pipes
- **BiblioCraft** → Builders Crafts & Additions

### 5.3 Własna implementacja (1 mod) 🔧

- **Carpenter's Blocks** → uproszczony własny mod (Block, Slope, Door, Barrier, Stairs)

### 5.4 Konwersja "w duchu" (8 modów) 🔄

Zastąpienie innymi o zbliżonej tematyce:
- **Thaumcraft** → Ars Nouveau
- **Witchery** → Occultism
- **Flan's Mod** → TaCZ + Realism Vehicle
- **Traincraft** → Create + Steam'n'Rails

### 5.5 Kompletna strata (16 modów) ❌

Brak odpowiedników lub niepotrzebne:
- Extra Utilities, CustomNPCs, Forestry, Statues
- Wszystkie addony Thaumcraft (Thaumic Energistics, Thaumic Tinkerer, etc.)

---

## 6. Konwencje pracy

### 6.1 Dokumentacja HANDOFF (z WORKFLOW.md)

Po każdym zadaniu NALEŻY utworzyć `HANDOFF.md`:

```markdown
# Handoff: Etap X, Zadanie Y

## Podsumowanie sesji
Co zostało zrobione (2-3 zdania).

## Ukończono
- [x] Konkretna rzecz 1
- [x] Konkretna rzecz 2

## Nowe pliki
- `src/converters/mod_y.py`
- `tests/test_mod_y.py`

## Zmodyfikowane pliki
- `src/core/registry.py:45-60`

## Następne kroki
1. [ ] Zaimplementować konwersję inventory
2. [ ] Dodać testy
```

### 6.2 Etapy konwersji (priorytetyzacja)

```
ETAP 0: Infrastruktura
        ├── Parser NBT 1.7.10
        ├── Writer NBT 1.18.2
        └── Framework testowy

ETAP 1: Rechiseled (Chisel) ← NAJŁATWIEJSZY
ETAP 2: Storage (Backpack, JABBA)
ETAP 3: EnderStorage
ETAP 4: Thermal Series
ETAP 5: Applied Energistics 2
ETAP 6: Mekanism
ETAP 7: Bigger Reactors
ETAP 8: Blood Magic
ETAP 9: ProjectRed + CC:Tweaked
ETAP 10: IndustrialCraft 2 → Mekanism
ETAP 11: BuildCraft → RFTools + Pretty Pipes
ETAP 12: Carpenter's Blocks ← WŁASNY MOD
```

### 6.3 Zasady pracy z dużą mapą (5GB)

**NIGDY nie ładować całej mapy do kontekstu!**

Dozwolone:
- Próbkowanie (sample_size=50-100)
- Agregacja schematów NBT
- Zwięzłe raporty (~5KB per mod)

Zabronione:
- `world.load_all_chunks()`
- Wypisywanie surowych danych NBT

---

## 7. Testowanie

### 7.1 Poziomy testów

| Poziom | Opis | Kiedy |
|--------|------|-------|
| **Unit** | Testy funkcji konwersji | Po każdym zadaniu |
| **Integracyjne** | Headless serwer + testowy świat | Koniec etapu |
| **E2E** | Właściwa mapa + review użytkownika | Koniec etapu |

### 7.2 Testowe światy

W `lightweigh_map_templates/`:
- Małe, kontrolowane światy z blokami konkretnego modu
- Używane do testowania konwersji bez ładowania 5GB mapy

### 7.3 Headless serwer

Planowane narzędzie do testowania:
```bash
python tests/run_integration.py \
    --world tests/test_worlds/thermal_furnace \
    --config tests/integration/thermal_furnace.yaml \
    --timeout 300
```

---

## 8. Uwagi bezpieczeństwa

### 8.1 Backup

- ZAWSZE robić backup mapy przed konwersją
- Nigdy nie modyfikować `mapa_1710/` bezpośrednio
- Pracować na kopiach w `mapa_118/` lub testowych światach

### 8.2 Dane wrażliwe

- `playerdata/` zawiera dane graczy (inventory, pozycja)
- `level.dat` zawiera ustawienia świata
- Nie commitować danych osobowych graczy

---

## 9. Przydatne komendy

### 9.1 Analiza modpacka

```powershell
# Lista wszystkich modów JAR
Get-ChildItem modpack_1710/*.jar | Select-Object Name, Length

# Szukanie konkretnego modu
Get-ChildItem modpack_1710 -Recurse -Filter "*thermal*"
```

### 9.2 Analiza mapy

```powershell
# Liczba plików regionów
(Get-ChildItem mapa_1710/region/*.mca).Count

# Rozmiar mapy
(Get-ChildItem mapa_1710 -Recurse | Measure-Object -Property Length -Sum).Sum / 1GB
```

---

## 10. Otwarte pytania i decyzje

### 10.1 Do rozstrzygnięcia

- [ ] Czy pisać własny mod dla Carpenter's Blocks czy szukać alternatywy?
- [ ] Jak obsłużyć Thaumcraft research progress (strata vs kompensacja)?
- [ ] Czy konwertować pociągi Traincraft na Create?
- [ ] Dostępność modów: Growthcraft, Jammy Furniture, Placeable Items

### 10.2 Wymaga weryfikacji na mapie

- [ ] Które bloki Carpenter's Blocks są najczęściej używane?
- [ ] Jakie maszyny IC2 są na mapie?
- [ ] Czy są multibloki Big Reactors?
- [ ] Ile sieci ME (AE2) jest na mapie?

---

## 11. Kontakt i kontekst

### 11.1 Właściciel projektu

Projekt należy do użytkownika `pawel` - wszystkie decyzje architektoniczne wymagają jego akceptacji.

### 11.2 Historia zmian

- **2026-01-30** - Utworzenie dokumentacji AGENTS.md
- **2026-01-30** - Analiza paczki modpack_1710 (56 modów)
- **2026-01-30** - Dokumentacja mapowania modów

---

*Ten dokument jest żywy - należy go aktualizować wraz z postępem projektu.*
