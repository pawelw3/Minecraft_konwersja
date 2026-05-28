# Handoff: Traincraft — Etap 14, Zadanie 1 + Zadanie 2

## Podsumowanie sesji
Wykonano Zadanie 1 (analiza bloków i TE) oraz Zadanie 2 (symulacje funkcjonalności) dla moda Traincraft 1.7.10 oraz docelowego zamiennika Create + Steam'n'Rails 1.18.2. Zebrano dokładne nazwy rejestracji bloków i tile entities z kodu źródłowego, opisano fizyczną strukturę wieloblokowych torów Traincraft, wygenerowano wizualne porównanie SVG, oraz stworzono trzy symulacje w Pythonie replikujące kluczową logikę modów.

## Ukończono
### Zadanie 1 — Analiza
- [x] Pełna inwentaryzacja bloków Traincraft 1.7.10 z rejestracjami
- [x] Pełna inwentaryzacja tile entities Traincraft 1.7.10 z dokładnymi registry names
- [x] Analiza block entities Create 1.18.2 (tory, stacje, sygnały, wózki)
- [x] Analiza bloków i BE Steam'n'Rails 1.18.2 (tory, zwrotnice, bufory)
- [x] Dokładna analiza fizycznej struktury torów Traincraft (tcRail + tcRailGag) na podstawie kodu ItemTCRail.java
- [x] Tabela porównawcza zajęcia bloków per typ toru
- [x] Wizualizacja SVG porównująca 11 typów torów Traincraft vs odpowiedniki w Create

### Zadanie 2 — Symulacje
- [x] `switch_simulation.py` — symulacja zwrotnic Traincraft (changeSwitchState, redstone, manual override, mutacja sąsiadów)
- [x] `rail_multiblock_simulation.py` — symulacja systemu wieloblokowego tcRail+tcRailGag (linki, niszczenie, NBT slope)
- [x] `create_track_simulation.py` — symulacja torów Create (TrackBlockEntity, BezierConnection, NBT serialization, fake tracks, track shapes)

## Nowe pliki
- `output/traincraft_step1/traincraft_analysis_task1.md` — raport analizy bloków/TE
- `output/traincraft_step1/generate_track_comparison_svg.py` — skrypt generujący SVG
- `output/traincraft_step1/traincraft_vs_create_tracks.svg` — wizualizacja porównawcza torów
- `src/traincraft/switch_simulation.py` — symulacja zwrotnic Traincraft
- `src/traincraft/rail_multiblock_simulation.py` — symulacja wieloblokowych torów
- `src/traincraft/create_track_simulation.py` — symulacja torów Create

## Zmodyfikowane pliki
- Brak (tylko nowe pliki)

## Kluczowe odkrycia techniczne dla kolejnych zadań
- **Traincraft TE bez prefiksu moda:** Wszystkie tile entities są rejestrowane jako `"tileTCRail"`, `"tileTCRailGag"`, `"Tile Distil"` itp. — bez `tc:` prefixu. To krytyczne dla wyszukiwania na mapie.
- **Wieloblokowość torów:** Zakręt 10×10 (VERY_LARGE_TURN) zajmuje **25 fizycznych bloków** (1 tcRail + 24 gag). W Create ten sam zakręt to **1 blok TrackBlock + krzywa Beziera** w BlockEntity.
- **Zwrotnica parallel switch:** MEDIUM_PARALLEL_SWITCH zajmuje obszar **4×11** i zawiera dwa osobne turny połączone blokami straight — konwersja wymaga zastąpienia jednym blokiem `track_switch_andesite` plus połączeniem grafu torów.
- **Slope:** W Traincraft slope to fizyczny ciąg 6-18 bloków z rosnącym `bbHeight`. W Create slope to pojedynczy blok z `TrackShape.AE/AW/AN/AS` (bez kolizji).
- **FakeTrackBlock:** W Create nie trzeba konwertować fake_track — są generowane runtime przy ładowaniu chunka.
- **NBT Create:** TrackBlockEntity przechowuje `Connections` (lista BezierConnection), każda z polami: `Positions`, `Starts`, `Axes`, `Normals`, `Primary`, `Girder`, `Material`, opcjonalnie `Smoothing`.

## Następne kroki
1. [ ] Zadanie 3: Kod konwersji — mapowanie tcRail/tcRailGag na create:track z BezierConnection
2. [ ] Zadanie 4: Sprawdzenie pokrycia na strefach głównej mapy
3. [ ] Zadanie 5A: Testowa mapa 1.7.10 ze wszystkimi typami torów Traincraft
4. [ ] Zadanie 5B+6: Testy na headless serwerze

---
*Czy kontynuować Zadanie 3 (kod konwersji)?*
