# Handoff: Traincraft konwersja – Pełna integracja z JVM Worker (Hephaistos)

## Podsumowanie sesji
Konwerter Traincraft został w pełni zintegrowany z istniejącym `jvm/worker` (Kotlin + Hephaistos). Generuje eventy JSONL w formacie natywnie rozumianym przez `WorldEditor1182.applyEvents1182Jsonl()`. Wszystkie przetłumaczalne metadane (kierunki, slope, crossing) są konwertowane na właściwe blockstate properties Create. Test serwera 1.18.2 (pierwszy start + restart) przeszedł bez crashy.

---

## Architektura pipeline

```
mapa_1710 (1.7.10)
    │
    ▼
TraincraftConverter (Python)
    │  • tcRail → create:track (shape/turn/waterlogged)
    │  • tcRailGag → minecraft:air
    │  • Machines → placeholder / vanilla approx
    │  • Track conflict resolver (parallel tracks too close)
    │
    ▼
conversion_events.jsonl
    │  { "op": "set_block", "pos": [x,y,z], "block": "create:track",
    │    "blockstate": { "shape": "zo", "turn": "false", "waterlogged": "false" } }
    │
    ▼
JVM Worker (Kotlin) — mc-editkit-worker-1.0-SNAPSHOT.jar
    │  • Hephaistos BlockState(blockId, properties)
    │  • RegionFile.writeChunkDirect()
    │  • Format 1.18.2 (palette + BlockStates long array)
    │
    ▼
mapa_118 (1.18.2)
```

---

## Konwersja torów — pełna tabela mapowania

| Traincraft type | Create blockstate | Opis |
|----------------|-------------------|------|
| `SMALL_STRAIGHT` | `shape=zo/xo, turn=false` | Prosty tor N-S (zo) lub E-W (xo) |
| `MEDIUM_STRAIGHT` | `shape=zo/xo, turn=false` | 1×3 → 1 blok create:track |
| `LONG_STRAIGHT` | `shape=zo/xo, turn=false` | 1×6 → 1 blok create:track |
| `SLOPE_WOOD/GRAVEL/BALLAST` | `shape=as/aw/an/ae, turn=false` | Ascending South/West/North/East |
| `LARGE_SLOPE_*` | `shape=as/aw/an/ae, turn=false` | 12-blok slope → 1 blok ascending |
| `VERY_LARGE_SLOPE_*` | `shape=as/aw/an/ae, turn=false` | 18-blok slope → 1 blok ascending |
| `TWO_WAYS_CROSSING` | `shape=cr_o, turn=false` | Skrzyżowanie orthogonal |
| `MEDIUM_SWITCH` | `shape=zo/xo, turn=false` | Aproksymacja do prostego toru |
| `*_PARALLEL_SWITCH` | `shape=zo/xo, turn=false` | Aproksymacja do prostego toru |
| `MEDIUM/LARGE/VERY_LARGE_TURN` | `minecraft:air` | **Usunięte** — za skomplikowane |

### facingMeta → shape

| facingMeta | Kierunek Traincraft | Straight | Slope |
|-----------|---------------------|----------|-------|
| 0 | South (+Z) | `zo` | `as` |
| 1 | West (-X) | `xo` | `aw` |
| 2 | North (-Z) | `zo` | `an` |
| 3 | East (+X) | `xo` | `ae` |

---

## Pliki w repo

### Python (konwerter + testy)
- `src/converters/traincraft/mappings/block_mappings.py` — mapowania blockstate
- `src/converters/traincraft/traincraft_converter.py` — główny konwerter + removals
- `src/converters/traincraft/track_conflict_resolver.py` — detekcja konfliktów torów
- `src/converters/traincraft/test_conversion_on_map.py` — generuje JSONL z testowej mapy
- `tests/traincraft/test_traincraft_converter.py` — 30 testów jednostkowych ✅

### JVM Worker (Kotlin + Hephaistos)
- `jvm/worker/src/main/kotlin/mc/editkit/worker/WorldEditor1182.kt` — edytor 1.18.2 (ISTNIEJĄCY)
- `jvm/worker/src/main/kotlin/mc/editkit/worker/Main.kt` — CLI z `--apply-events` (ISTNIEJĄCY)

### Output
- `output/traincraft_task5a/conversion_events.jsonl` — eventy dla JVM workera
- `output/traincraft_task4/track_removals.json` — pozycje do usunięcia (konflikty)
- `output/traincraft_task4/coverage_traincraft.json` — pełny raport skanu mapy

---

## Testy serwera (Zadanie 5B + 6)

| Test | Wynik |
|------|-------|
| JVM Worker applyEvents1182Jsonl | **2415/2415 applied, 0 failed** ✅ |
| Pierwszy start serwera 1.18.2 | `Done (6.342s)!` ✅ |
| Restart serwera | `Done (4.534s)!` ✅ |
| Ticking tile entity / Create errors | **Brak** ✅ |

---

## Ograniczenia i znane problemy

1. **Zakręty (turns)** są usuwane (`minecraft:air`). Gracz musi przebudować krzywe ręcznie w 1.18.2 — Create generuje je dynamicznie przez `BezierConnection` w `TrackBlockEntity`, co wymagałoby analizy sąsiedztwa i nie jest trywialne do zautomatyzowania.

2. **Zwrotnice (switches)** aproksymowane do prostych torów. `railways:track_switch_andesite` wymaga specyficznej topologii sąsiednich torów której nie da się w pełni odwzorować z Traincraft bez analizy redstone.

3. **BlockEntity NBT** dla turn tracków nie jest generowane (turn → air). Dla straight/slope/crossing Create track nie wymaga TileEntity — blockstate wystarcza.

---

## Następne kroki (opcjonalne)
- [ ] Ręczna weryfikacja wizualna w grze (wymaga wejścia użytkownika na serwer)
- [ ] Rozważyć zachowanie `facingMeta` w bardziej złożonych typach (np. `SMALL_ROAD_CROSSING_1/2`)
- [ ] Pełna konwersja całej mapy 1.7.10 → 1.18.2 (pipeline: coverage → resolver → converter → JVM worker)
