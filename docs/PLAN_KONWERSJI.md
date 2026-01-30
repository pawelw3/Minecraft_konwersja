# Plan konwersji mapy Minecraft 1.7.10 → 1.18

> **STATUS: WSTĘPNY PLAN**
> Ten dokument opisuje wstępną koncepcję. Plan będzie ewoluował po:
> - Doprecyzowaniu listy modów do konwersji
> - Przesłaniu właściwej mapy (5GB)
> - Przesłaniu mapy po wstępnej konwersji vanilla

---

## 1. Problematyka konwersji

### 1.1 Główne wyzwania techniczne

| Problem | Opis |
|---------|------|
| **Zmiana systemu ID bloków** | 1.7.10 używa numerycznych ID (0-4095) + metadata, 1.18 używa string ID (`minecraft:stone`) |
| **Rozszerzenie wysokości świata** | 1.7.10: Y=0-255, 1.18: Y=-64 do 320 |
| **Zmiany formatu NBT** | Nowa struktura danych chunk, biomy per-block |
| **Bloki modowane** | Brak odpowiedników w vanilla, mody mogą nie istnieć dla 1.18 |
| **Tile Entities** | Maszyny, skrzynie tracą dane przy braku modu |
| **Multibloki** | Struktury wieloblokowe rozpadają się |

### 1.2 Możliwe scenariusze dla modów

| Scenariusz | Opis | Złożoność |
|------------|------|-----------|
| Ten sam mod | Mod istnieje dla 1.18, konwersja struktur NBT | Średnia |
| Odpowiednik | Mapowanie na inny mod o podobnej funkcjonalności | Wysoka |
| Nowy mod | Napisanie uproszczonej wersji modu od zera | Bardzo wysoka |
| Porzucenie | Bloki zamienione na placeholder lub usunięte | Niska |

---

## 2. Koncepcja rozwiązania

### 2.1 Podejście hybrydowe

```
WARSTWA 1: Konwersja Vanilla
└── Standardowa konwersja Minecraft (automatyczna)

WARSTWA 2: Program konwertujący mody
├── Moduł A: Mod X (1.7.10) → Mod X (1.18)
├── Moduł B: Mod Y (1.7.10) → Mod Z (1.18) [odpowiednik]
└── Moduł C: Mod W (1.7.10) → CustomMod (1.18) [nowy]
```

### 2.2 Architektura konwertera

```
┌─────────────────────────────────────────────────────────┐
│                    KONWERTER                            │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │   Parser    │  │   Mapper    │  │    Writer       │  │
│  │   NBT/MCA   │→ │  Block IDs  │→ │  Nowy format    │  │
│  │   1.7.10    │  │  + NBT data │  │    1.18         │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────┤
│  Moduły konwersji per-mod                               │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Plan implementacji przez Claude Code

### 3.1 Podział na etapy

```
Etap 0: Infrastruktura bazowa
        ├── Parser NBT
        ├── Parser regionów MCA
        ├── Writer format 1.18
        └── Framework testowy

Etap 1-N: Konwersja poszczególnych modów
        └── Od najprostszych do najtrudniejszych

Etap N+1, N+2: Własne mody (uproszczone wersje)
```

### 3.2 Struktura pojedynczego etapu

Każdy etap dzieli się na zadania. Po każdym zadaniu:
- Testy weryfikujące poprawność
- Dokumentacja (MANIFEST, SIDE_EFFECTS)
- HANDOFF.md umożliwiający wyczyszczenie kontekstu

```
ETAP X: Konwersja ModuY
├── Zadanie 1: Analiza starego modu (struktura NBT)
├── Zadanie 2: Mapowanie bloków
├── Zadanie 3: Konwerter tile entities
├── Zadanie 4: Testy jednostkowe
├── Zadanie 5: Przygotowanie testowego świata
├── Zadanie 6: Test z headless serwerem
└── Zadanie 7: Test na właściwej mapie + review użytkownika
```

### 3.3 Zarządzanie kontekstem

Dokumenty utrzymywane między sesjami:

```
project/
├── MASTER_MANIFEST.md          # Ogólny stan projektu
├── docs/
│   ├── ARCHITECTURE.md         # Architektura konwertera
│   ├── BLOCK_MAPPINGS.yaml     # Wszystkie mapowania bloków
│   └── CONVENTIONS.md          # Konwencje kodu
├── etapy/
│   ├── etap_01/
│   │   ├── MANIFEST.md         # Co zostało zrobione
│   │   ├── SIDE_EFFECTS.md     # Efekty uboczne
│   │   ├── LESSONS_LEARNED.md  # Wnioski
│   │   └── HANDOFF.md          # Instrukcja dla następnej sesji
│   └── current/
│       └── TASK_CONTEXT.md     # Aktualny kontekst
└── tests/
    ├── test_worlds/            # Testowe światy
    └── snapshots/              # Snapshoty do porównań
```

---

## 4. System testowania

### 4.1 Poziomy testów

| Poziom | Opis | Kiedy |
|--------|------|-------|
| **Unit** | Testy funkcji konwersji | Po każdym zadaniu |
| **Integracyjne** | Headless serwer + testowy świat | Koniec etapu |
| **E2E** | Właściwa mapa + review użytkownika | Koniec etapu |

### 4.2 Testy z headless serwerem

Scenariusze testowe sprawdzające:
- Czy bloki się ładują bez błędów
- Czy tile entities działają (maszyny przetwarzają itemy)
- Czy systemy energii funkcjonują
- Czy transport itemów działa

Przykładowe testowe światy:
- Pojedyncza maszyna z inventory
- Sieć energetyczna
- System transportu itemów
- Zautomatyzowana farma

### 4.3 Snapshoty i asercje

```yaml
# Przykład testu
initial_state:
  - position: [100, 64, 100]
    tile_entity:
      input_slot: "minecraft:raw_iron x16"
      output_slot: "empty"

wait_ticks: 6000

expected_state:
  - position: [100, 64, 100]
    tile_entity:
      input_slot: "empty"
      output_slot: "minecraft:iron_ingot x16"
```

---

## 5. Praca z dużą mapą (5GB)

### 5.1 Problem
- Mapa 5GB = tysiące plików regionów
- Nie można załadować do kontekstu Claude

### 5.2 Rozwiązanie: Inteligentne próbkowanie

```python
# Narzędzie do analizy
class LargeMapAnalyzer:
    def find_mod_blocks(self, mod_prefix, sample_size=100):
        """Znajdź reprezentatywną próbkę bloków z modu"""

    def get_tile_entity_schemas(self, mod_prefix):
        """Wyekstrahuj unikalne schematy (nie wszystkie instancje)"""

    def generate_summary_report(self, mod_prefix):
        """Zwięzłe podsumowanie dla Claude (~2-5 KB)"""
```

---

## 6. Przepływ zadania

```
1. START
   └── Claude czyta: HANDOFF.md z poprzedniego zadania

2. IMPLEMENTACJA
   ├── Kod
   ├── Testy jednostkowe
   └── Dokumentacja inline

3. WERYFIKACJA
   ├── pytest tests/
   ├── ruff check .
   └── Poprawki

4. DOKUMENTACJA
   ├── MANIFEST.md
   ├── SIDE_EFFECTS.md
   └── HANDOFF.md

5. COMMIT
   └── git commit

6. KONIEC → możliwe wyczyszczenie kontekstu
```

---

## 7. Szacunkowa kolejność modów

> **UWAGA:** Lista zostanie doprecyzowana po podaniu konkretnych modów

```
Etap 0: Infrastruktura
Etap 1: Prosty mod (tylko bloki dekoracyjne)
Etap 2: Mod ze storage (proste tile entities)
Etap 3: Mod z maszynami (bez energii)
Etap 4: Mod z systemem energii
Etap 5: Mod → odpowiednik (mapowanie koncepcji)
Etap 6: Mod z multiblock (najtrudniejsze)
Etap 7+: Własne mody (uproszczone)
```

---

## 8. Ryzyka i mitygacja

| Ryzyko | Prawdopodobieństwo | Mitygacja |
|--------|-------------------|-----------|
| Zbyt duży zakres | Wysokie | Priorytetyzacja, MVP |
| Korupcja świata | Średnie | Backupy, testy |
| Niezadowolenie graczy | Wysokie | Komunikacja, kompensacja |
| Własne mody zbyt czasochłonne | Wysokie | Maksymalne uproszczenie |
| Utrata kontekstu między sesjami | Średnie | Dokładna dokumentacja HANDOFF |

---

## 9. Co potrzebne do kontynuacji

- [ ] Lista modów na serwerze 1.7.10
- [ ] Kategoryzacja modów (ten sam / odpowiednik / nowy / porzucony)
- [ ] Właściwa mapa 1.7.10 (do analizy)
- [ ] Mapa po wstępnej konwersji vanilla (do testów)
- [ ] Priorytetyzacja: które mody są najważniejsze dla graczy

---

## 10. Narzędzia zewnętrzne

| Narzędzie | Zastosowanie |
|-----------|--------------|
| **MCA Selector** | Przeglądanie/edycja chunków, filtrowanie |
| **NBTExplorer** | Ręczna edycja danych NBT |
| **Amulet Editor** | Zaawansowana edycja światów |
| **Chunker** | Konwerter formatów (Hive) |

---

*Ostatnia aktualizacja: 2026-01-30*
