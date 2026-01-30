# Workflow pracy z Claude Code

> **STATUS: WSTĘPNY PLAN**
> Dokument opisuje metodykę pracy. Może ewoluować w trakcie projektu.

---

## 1. Filozofia podejścia

### Problem: Ograniczony kontekst LLM
- Claude ma ograniczoną "pamięć roboczą" (kontekst)
- Długie sesje = degradacja jakości odpowiedzi
- Duże pliki/mapy mogą zapchać kontekst

### Rozwiązanie: Praca w izolowanych sesjach
- Podział na małe, zamknięte zadania
- Dokładna dokumentacja na końcu każdego zadania
- Możliwość "świeżego startu" bez utraty postępu

---

## 2. Hierarchia pracy

```
PROJEKT
└── ETAP (np. konwersja jednego modu)
    └── ZADANIE (np. implementacja konwertera tile entities)
        └── SESJA CLAUDE (jedna rozmowa)
```

### Zasady

| Poziom | Czas trwania | Dokumentacja |
|--------|--------------|--------------|
| Projekt | Tygodnie/miesiące | MASTER_MANIFEST.md |
| Etap | Dni | etap_XX/MANIFEST.md |
| Zadanie | Godziny | HANDOFF.md |
| Sesja | Minuty-godziny | Wyczyszczenie po zakończeniu |

---

## 3. Struktura dokumentów

### 3.1 MASTER_MANIFEST.md (root projektu)

```markdown
# Master Manifest

## Status projektu
- Aktualny etap: 3
- Ukończone etapy: 0, 1, 2
- Data rozpoczęcia: YYYY-MM-DD

## Ukończone mody
- [x] ModA - Etap 1
- [x] ModB - Etap 2
- [ ] ModC - Etap 3 (w trakcie)

## Globalne decyzje architektoniczne
- Język: Python 3.11
- Format mapowań: YAML
- ...

## Znane problemy globalne
- Problem X: opis
```

### 3.2 etap_XX/MANIFEST.md

```markdown
# Etap XX: Konwersja ModuY

## Cel
Konwersja wszystkich bloków i tile entities z ModuY (1.7.10)
na ModuY (1.18) lub odpowiednik.

## Status: W TRAKCIE / UKOŃCZONY

## Zadania
- [x] Zadanie 1: Analiza struktury NBT
- [x] Zadanie 2: Mapowanie bloków
- [ ] Zadanie 3: Konwerter tile entities
- [ ] Zadanie 4: Testy

## Pliki utworzone/zmodyfikowane
- src/converters/mod_y.py (nowy)
- src/mappings/mod_y_blocks.yaml (nowy)
- src/core/converter.py (zmodyfikowany - dodano hook)

## Decyzje podjęte w tym etapie
- Energia EU konwertowana na FE w stosunku 1:4
- Blok X nie ma odpowiednika → zamiana na stone
```

### 3.3 etap_XX/HANDOFF.md (kluczowy!)

```markdown
# Handoff: Etap X, Zadanie Y → Zadanie Z

## Podsumowanie sesji
Co zostało zrobione w tej sesji (2-3 zdania).

## Ukończono
- [x] Konkretna rzecz 1
- [x] Konkretna rzecz 2
- [x] Konkretna rzecz 3

## Nie ukończono (jeśli dotyczy)
- [ ] Rzecz 4 - powód: ...

## Stan kodu

### Nowe pliki
- `src/converters/mod_y.py` - główny konwerter
- `tests/test_mod_y.py` - testy jednostkowe

### Zmodyfikowane pliki
- `src/core/registry.py:45-60` - dodano rejestrację ModY

### Kluczowe funkcje/klasy
- `ModYConverter.convert_tile_entity()` - główna logika
- `map_block_id()` - mapowanie ID bloków

## Kontekst dla następnej sesji

### Przeczytaj przed rozpoczęciem
1. Ten plik (HANDOFF.md)
2. `src/converters/mod_y.py` - cały plik (~150 linii)
3. `docs/CONVENTIONS.md` - jeśli nowa sesja

### Zrozum przed rozpoczęciem
- Format NBT maszyny X (przykład w ANALYSIS.md)
- System rejestracji konwerterów

## Następne kroki
1. [ ] Zaimplementować konwersję inventory
2. [ ] Dodać obsługę edge case: puste sloty
3. [ ] Napisać testy dla inventory

## Komendy na start
```bash
# Sprawdź czy testy przechodzą
python -m pytest tests/test_mod_y.py -v

# Uruchom konwerter na testowym świecie
python -m converter convert tests/worlds/mod_y_test
```

## Otwarte pytania (jeśli są)
- Czy blok X powinien być konwertowany na Y czy Z?
  → Wymaga decyzji użytkownika
```

### 3.4 etap_XX/SIDE_EFFECTS.md

```markdown
# Side Effects - Etap XX

## Zmiany globalne
Zmiany wykraczające poza zakres tego etapu.

### Zmodyfikowane pliki wspólne
| Plik | Zmiana | Powód |
|------|--------|-------|
| src/core/nbt.py | Dodano `parse_legacy_id()` | Potrzebne dla ModY |
| src/utils/energy.py | Nowa funkcja `convert_eu_to_fe()` | Konwersja energii |

### Nowe zależności
- Dodano `pyyaml>=6.0` do requirements.txt

### Zmiany w konfiguracji
- Nowy klucz w config.yaml: `mod_y.energy_ratio`

## Wpływ na inne moduły
- Konwerter ModX może teraz używać `convert_eu_to_fe()`
- Registry wymaga aktualizacji przy dodaniu nowego modu

## Potencjalne breaking changes
- Funkcja `parse_block_id()` zmieniona sygnatura
  - Stara: `parse_block_id(id: int)`
  - Nowa: `parse_block_id(id: int, metadata: int = 0)`
  - Wpływ: żaden (domyślna wartość)
```

### 3.5 etap_XX/LESSONS_LEARNED.md

```markdown
# Lessons Learned - Etap XX

## Co poszło dobrze
- Testy jednostkowe złapały 3 bugi przed integracją
- Format YAML dla mapowań jest czytelny

## Co poszło źle
- Zbyt późno odkryto że ModY ma 2 wersje tile entity
- Testy integracyjne trwały 10 minut (za długo)

## Wnioski na przyszłość
1. Zawsze sprawdzać wersje tile entities NA POCZĄTKU
2. Rozważyć cache dla testów integracyjnych
3. Dokumentować edge cases od razu

## Przydatne snippety
```python
# Szybkie sprawdzenie typu tile entity
def get_te_version(nbt):
    if "EnergyNew" in nbt:
        return 2
    return 1
```
```

---

## 4. Przepływ zadania (szczegółowy)

```
┌─────────────────────────────────────────────────────────────┐
│                     ROZPOCZĘCIE SESJI                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. ODCZYT KONTEKSTU (Claude robi automatycznie)           │
│     ├── Przeczytaj HANDOFF.md poprzedniego zadania         │
│     ├── Przeczytaj wskazane pliki źródłowe                 │
│     ├── Uruchom komendy diagnostyczne                       │
│     └── Potwierdź zrozumienie z użytkownikiem              │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                     IMPLEMENTACJA                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  2. KODOWANIE                                               │
│     ├── Implementuj zgodnie z planem                       │
│     ├── Pisz testy równolegle z kodem                      │
│     ├── Commituj małe, logiczne zmiany                     │
│     └── Dokumentuj decyzje inline                          │
│                                                             │
│  3. WERYFIKACJA LOKALNA                                     │
│     ├── pytest tests/ -v                                   │
│     ├── ruff check . (lub inny linter)                     │
│     └── Napraw błędy przed kontynuacją                     │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                    ZAKOŃCZENIE SESJI                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  4. DOKUMENTACJA (OBOWIĄZKOWA!)                            │
│     ├── Aktualizuj MANIFEST.md etapu                       │
│     ├── Zapisz SIDE_EFFECTS.md (jeśli były)                │
│     ├── Napisz HANDOFF.md dla następnej sesji              │
│     └── Aktualizuj MASTER_MANIFEST.md (jeśli potrzeba)     │
│                                                             │
│  5. COMMIT KOŃCOWY                                          │
│     └── git commit -m "Etap X, Zadanie Y: opis"            │
│                                                             │
│  6. POTWIERDZENIE                                           │
│     └── Poinformuj użytkownika że można czyścić kontekst   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Przepływ etapu (end-to-end)

```
ETAP X: Konwersja ModuY
│
├── Zadanie 1: Analiza
│   ├── Zbadaj strukturę modu w 1.7.10
│   ├── Zbadaj strukturę modu w 1.18
│   ├── Udokumentuj różnice
│   └── → HANDOFF.md
│
├── Zadanie 2: Mapowanie bloków
│   ├── Utwórz tabelę: stary ID → nowy ID
│   ├── Zidentyfikuj bloki bez odpowiednika
│   ├── Zapisz w YAML
│   └── → HANDOFF.md
│
├── Zadanie 3: Konwerter podstawowy
│   ├── Implementuj konwersję bloków
│   ├── Testy jednostkowe
│   └── → HANDOFF.md
│
├── Zadanie 4: Konwerter tile entities
│   ├── Implementuj konwersję NBT
│   ├── Obsłuż inventory, energię, etc.
│   ├── Testy jednostkowe
│   └── → HANDOFF.md
│
├── Zadanie 5: Testowy świat
│   ├── Utwórz mały świat z blokami modu
│   ├── Zdefiniuj oczekiwane stany
│   └── → HANDOFF.md
│
├── Zadanie 6: Test integracyjny
│   ├── Uruchom konwersję testowego świata
│   ├── Uruchom headless serwer
│   ├── Sprawdź logi, wykonaj asercje
│   ├── Napraw błędy
│   └── → HANDOFF.md
│
├── Zadanie 7: Test na właściwej mapie
│   ├── Uruchom konwersję (tylko bloki tego modu)
│   ├── Użytkownik weryfikuje wynik
│   ├── Poprawki jeśli potrzebne
│   └── → HANDOFF.md + LESSONS_LEARNED.md
│
└── KONIEC ETAPU
    ├── Aktualizuj MASTER_MANIFEST.md
    └── Rozpocznij Etap X+1
```

---

## 6. Czyszczenie kontekstu

### Kiedy czyścić?
- Po każdym ukończonym zadaniu (opcjonalnie)
- Obowiązkowo po ukończeniu etapu
- Gdy kontekst staje się "ciężki" (długie rozmowy)
- Gdy Claude zaczyna się mylić lub zapominać

### Jak czyścić?
1. Upewnij się że HANDOFF.md jest kompletny
2. Sprawdź że wszystko jest commitnięte
3. Zamknij sesję / wyczyść historię
4. Rozpocznij nową sesję

### Co Claude robi na początku nowej sesji?
```
1. Przeczytaj HANDOFF.md
2. Przeczytaj pliki wskazane w "Przeczytaj przed rozpoczęciem"
3. Uruchom komendy z "Komendy na start"
4. Potwierdź z użytkownikiem: "Rozumiem że mam [opis zadania]. Czy to poprawne?"
5. Kontynuuj pracę
```

---

## 7. Praca z dużą mapą

### Zasada: NIGDY nie ładuj całej mapy do kontekstu

### Dozwolone operacje
```python
# TAK - próbkowanie
analyzer.find_mod_blocks("ThermalExpansion", sample_size=50)

# TAK - agregacja
analyzer.get_tile_entity_schemas("ThermalExpansion")

# TAK - zwięzłe raporty
analyzer.generate_summary_report("ThermalExpansion")  # → ~5KB
```

### Zabronione operacje
```python
# NIE - cała mapa
world.load_all_chunks()

# NIE - wszystkie bloki
world.find_all_blocks("ThermalExpansion")  # może być 100k+

# NIE - surowe dane
print(chunk.raw_nbt)  # może być ogromne
```

### Strategia analizy

```
1. Uruchom narzędzie analizy (poza Claude)
   → python tools/analyze_map.py --mod "ThermalExpansion"

2. Narzędzie generuje zwięzły raport
   → analysis/thermal_expansion.md (~5KB)

3. Claude czyta raport
   → Zawiera: typy bloków, schematy NBT, statystyki

4. Claude implementuje na podstawie raportu
   → Nie potrzebuje surowych danych
```

---

## 8. Testowanie

### 8.1 Testy jednostkowe (każde zadanie)

```python
# tests/test_thermal.py

def test_block_id_mapping():
    """Mapowanie ID bloków"""
    assert map_block("ThermalExpansion:Machine:1") == "thermal:machine_furnace"

def test_energy_conversion():
    """Przeliczanie RF → FE"""
    assert convert_energy(10000, "RF") == 10000  # 1:1

def test_inventory_slots():
    """Zachowanie inventory"""
    old = {"Items": [{"Slot": 0, "id": 264, "Count": 5}]}
    new = convert_tile_entity(old)
    assert new["Items"][0]["id"] == "minecraft:diamond"
```

### 8.2 Testy integracyjne (koniec etapu)

```yaml
# tests/integration/thermal_furnace.yaml
name: "Thermal Furnace Processing"

setup:
  world: "test_worlds/thermal_furnace"

initial_state:
  - pos: [100, 64, 100]
    block: "thermal:machine_furnace"
    nbt:
      input: "minecraft:raw_iron x16"
      output: "empty"
      energy: 50000

wait_ticks: 6000

expected:
  - pos: [100, 64, 100]
    nbt:
      input: "empty"
      output: "minecraft:iron_ingot x16"

assertions:
  - no_errors_in_log
  - block_exists: [100, 64, 100]
```

### 8.3 Uruchamianie headless serwera

```bash
# Skrypt testowy
python tests/run_integration.py \
    --world tests/test_worlds/thermal_furnace \
    --config tests/integration/thermal_furnace.yaml \
    --timeout 300
```

---

## 9. Komunikacja z użytkownikiem

### Punkty synchronizacji

| Moment | Akcja |
|--------|-------|
| Początek etapu | Potwierdź plan z użytkownikiem |
| Decyzja architektoniczna | Zapytaj użytkownika |
| Koniec zadania | Poinformuj o gotowości do czyszczenia |
| Koniec etapu | Review użytkownika na właściwej mapie |
| Problem/blocker | Natychmiast informuj |

### Format informacji o zakończeniu zadania

```
✓ Zadanie X ukończone

Zrobione:
- Punkt 1
- Punkt 2

Następne zadanie: [opis]

Dokumentacja zapisana w:
- etap_XX/HANDOFF.md
- etap_XX/MANIFEST.md (zaktualizowany)

Możesz teraz wyczyścić kontekst jeśli chcesz.
```

---

## 10. Checklist przed czyszczeniem kontekstu

```
□ Kod działa (testy przechodzą)
□ Zmiany commitnięte
□ HANDOFF.md napisany i kompletny
□ MANIFEST.md zaktualizowany
□ SIDE_EFFECTS.md zapisany (jeśli były)
□ Użytkownik poinformowany
```

---

*Ostatnia aktualizacja: 2026-01-30*
