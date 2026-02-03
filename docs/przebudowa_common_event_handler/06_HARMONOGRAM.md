# 06. Harmonogram wdrożenia

## Diagram faz

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FAZA 0: PRZYGOTOWANIE                                │
│  • Analiza obecnego kodu                                                    │
│  • Definicja interfejsów                                                    │
│  • Setup testów                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FAZA 1: INFRASTRUKTURA PYTHON                          │
│  • src/common/events/ (types, emitter, serializer)                         │
│  • src/common/adapters/ (base_adapter)                                      │
│  • Testy jednostkowe                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FAZA 2: ROZBUDOWA JVM WORKER                          │
│  • EventTypes.kt, EventParser.kt                                            │
│  • EventProcessor.kt                                                        │
│  • WorldEditor1182.kt (nowy format)                                         │
│  • Testy integracyjne                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FAZA 3: MIGRACJA KONWERTERÓW                             │
│  • BetterStorage (wzorcowy)                                                 │
│  • BloodMagic, EnderStorage, GrowthCraft                                    │
│  • Testy porównawcze                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FAZA 4: INTEGRACJA I PIPELINE                            │
│  • Pipeline konwersji end-to-end                                            │
│  • Skrypty uruchomieniowe                                                   │
│  • Dokumentacja użytkownika                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FAZA 5: CLEANUP I FINALIZACJA                          │
│  • Usunięcie starego kodu                                                   │
│  • Optymalizacja wydajności                                                 │
│  • Dokumentacja techniczna                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Szczegółowy harmonogram

### FAZA 0: Przygotowanie (1-2 dni)

| Zadanie | Opis | Output |
|---------|------|--------|
| 0.1 | Analiza istniejących ConversionResult | Lista pól do ujednolicenia |
| 0.2 | Analiza formatu NBT 1.7.10 vs 1.18.2 | Tabela różnic |
| 0.3 | Setup środowiska testowego | Mapy testowe, fixtures |
| 0.4 | Definicja JSON Schema dla eventów | `event_schema.json` |

**Deliverables:**
- [ ] Dokument analizy różnic między wersjami
- [ ] Mapy testowe (mała mapa z każdego moda)
- [ ] JSON Schema dla Event JSON

---

### FAZA 1: Infrastruktura Python (3-4 dni)

| Zadanie | Plik | Zależności |
|---------|------|------------|
| 1.1 | `src/common/__init__.py` | - |
| 1.2 | `src/common/events/__init__.py` | 1.1 |
| 1.3 | `src/common/events/types.py` | 1.2 |
| 1.4 | `src/common/events/serializer.py` | 1.3 |
| 1.5 | `src/common/events/validator.py` | 1.3 |
| 1.6 | `src/common/events/emitter.py` | 1.3, 1.4, 1.5 |
| 1.7 | `src/common/adapters/__init__.py` | 1.1 |
| 1.8 | `src/common/adapters/base_adapter.py` | 1.6 |
| 1.9 | Testy: `tests/common/test_events.py` | 1.6 |
| 1.10 | Testy: `tests/common/test_adapters.py` | 1.8 |

**Graf zależności:**
```
1.1 ──► 1.2 ──► 1.3 ──┬──► 1.4 ──┐
                      │          │
                      ├──► 1.5 ──┼──► 1.6 ──► 1.8
                      │          │
1.1 ──► 1.7 ──────────┴──────────┘
```

**Deliverables:**
- [ ] `src/common/events/` - kompletny moduł
- [ ] `src/common/adapters/base_adapter.py`
- [ ] Testy z pokryciem >80%
- [ ] Przykładowy Event JSON

---

### FAZA 2: Rozbudowa JVM Worker (4-5 dni)

| Zadanie | Plik | Zależności |
|---------|------|------------|
| 2.1 | `jvm/worker/.../events/EventTypes.kt` | - |
| 2.2 | `jvm/worker/.../nbt/NbtJsonConverter.kt` | 2.1 |
| 2.3 | `jvm/worker/.../events/EventParser.kt` | 2.1, 2.2 |
| 2.4 | `jvm/worker/.../events/EventValidator.kt` | 2.1 |
| 2.5 | `jvm/worker/.../handlers/BlockHandler.kt` | 2.1 |
| 2.6 | `jvm/worker/.../handlers/BlockEntityHandler.kt` | 2.1, 2.2 |
| 2.7 | `jvm/worker/.../handlers/EntityHandler.kt` | 2.1, 2.2 |
| 2.8 | `jvm/worker/.../handlers/HandlerRegistry.kt` | 2.5, 2.6, 2.7 |
| 2.9 | `jvm/worker/.../world/WorldEditor1182.kt` | 2.8 |
| 2.10 | `jvm/worker/.../events/EventProcessor.kt` | 2.3, 2.4, 2.8, 2.9 |
| 2.11 | Rozbudowa `Main.kt` | 2.10 |
| 2.12 | Testy integracyjne | 2.11 |

**Graf zależności:**
```
2.1 ──┬──► 2.2 ──┬──► 2.3 ──┐
      │          │          │
      ├──► 2.4 ──┼──────────┤
      │          │          │
      ├──► 2.5 ──┤          │
      │          │          │
      ├──► 2.6 ──┼──► 2.8 ──┼──► 2.9 ──► 2.10 ──► 2.11
      │          │          │
      └──► 2.7 ──┘          │
                            │
                    2.4 ────┘
```

**Deliverables:**
- [ ] `jvm/worker/.../events/` - kompletny pakiet
- [ ] `jvm/worker/.../handlers/` - kompletny pakiet
- [ ] `WorldEditor1182.kt` działający
- [ ] CLI z `--apply-events`
- [ ] Testy: apply events → verify world

---

### FAZA 3: Migracja konwerterów (5-7 dni)

#### 3.1 BetterStorage (wzorcowy) - 2 dni

| Zadanie | Opis |
|---------|------|
| 3.1.1 | Stwórz `src/converters/betterstorage/adapter.py` |
| 3.1.2 | Przenieś mapowania z `mapping.py` |
| 3.1.3 | Zaimplementuj `convert_block()` |
| 3.1.4 | Zaimplementuj konwersję NBT |
| 3.1.5 | Testy jednostkowe |
| 3.1.6 | Test porównawczy ze starym konwerterem |

#### 3.2 Pozostałe konwertery (równolegle) - 3-4 dni

| Konwerter | Estymacja | Specyfika |
|-----------|-----------|-----------|
| BloodMagic | 1.5 dnia | Rune mappings, altar structure |
| EnderStorage | 0.5 dnia | Prosty, frequency colors |
| GrowthCraft | 1 dzień | Wiele typów bloków |

#### 3.3 Testy porównawcze - 1 dzień

```bash
# Dla każdego konwertera:
python scripts/compare_conversion.py \
    --old-converter src/converters/X/old_converter.py \
    --new-adapter src/converters/X/adapter.py \
    --test-map maps/test/X_test \
    --output comparison_X.json
```

**Deliverables:**
- [ ] `src/converters/betterstorage/adapter.py`
- [ ] `src/converters/bloodmagic/adapter.py`
- [ ] `src/converters/enderstorage/adapter.py`
- [ ] `src/converters/growthcraft/adapter.py`
- [ ] Raporty porównawcze dla każdego

---

### FAZA 4: Integracja i pipeline (2-3 dni)

| Zadanie | Plik/Output |
|---------|-------------|
| 4.1 | `src/pipeline/full_conversion.py` - główny skrypt |
| 4.2 | `scripts/convert_world.sh` - wrapper bash |
| 4.3 | `scripts/convert_world.bat` - wrapper Windows |
| 4.4 | Dokumentacja użytkownika `docs/USAGE.md` |
| 4.5 | Test end-to-end na pełnej mapie |

**Pipeline docelowy:**
```bash
# Pojedyncza komenda do pełnej konwersji
python -m src.pipeline.full_conversion \
    --source maps/1.7.10/world \
    --target maps/1.18.2/world \
    --mods betterstorage,bloodmagic,enderstorage,growthcraft
```

**Deliverables:**
- [ ] Działający pipeline end-to-end
- [ ] Skrypty uruchomieniowe (bash/bat)
- [ ] Dokumentacja użytkownika
- [ ] Test na pełnej mapie produkcyjnej

---

### FAZA 5: Cleanup i finalizacja (1-2 dni)

| Zadanie | Opis |
|---------|------|
| 5.1 | Archiwizacja starego kodu do `legacy/` |
| 5.2 | Usunięcie deprecation warnings |
| 5.3 | Profilowanie wydajności |
| 5.4 | Optymalizacja (jeśli potrzebna) |
| 5.5 | Dokumentacja techniczna |
| 5.6 | Code review całości |

**Deliverables:**
- [ ] Czysty kod bez legacy
- [ ] Raport wydajności
- [ ] Kompletna dokumentacja
- [ ] Tag release v2.0

---

## Podsumowanie czasowe

| Faza | Estymacja | Kumulatywnie |
|------|-----------|--------------|
| Faza 0: Przygotowanie | 1-2 dni | 1-2 dni |
| Faza 1: Python infra | 3-4 dni | 4-6 dni |
| Faza 2: JVM Worker | 4-5 dni | 8-11 dni |
| Faza 3: Migracja | 5-7 dni | 13-18 dni |
| Faza 4: Integracja | 2-3 dni | 15-21 dni |
| Faza 5: Cleanup | 1-2 dni | 16-23 dni |

**Całkowity czas: ~3-4 tygodnie**

---

## Kamienie milowe

| Milestone | Faza | Kryteria akceptacji |
|-----------|------|---------------------|
| M1: Event System Ready | 1 | EventEmitter produkuje valid JSON |
| M2: JVM Handler Ready | 2 | JVM Worker aplikuje eventy na mapę |
| M3: First Adapter | 3.1 | BetterStorage produkuje identyczne wyniki |
| M4: All Adapters | 3 | Wszystkie konwertery zmigrowane |
| M5: Pipeline Ready | 4 | End-to-end konwersja działa |
| M6: Release | 5 | v2.0 gotowe do użycia |

---

## Ryzyka i mitygacja

| Ryzyko | Prawdopodobieństwo | Wpływ | Mitygacja |
|--------|-------------------|-------|-----------|
| Format 1.18.2 bardziej skomplikowany niż oczekiwano | Średnie | Wysoki | Dodatkowy czas na Fazę 2 |
| Różnice w NBT między wersjami | Wysokie | Średni | Dokładna analiza w Fazie 0 |
| Wydajność JVM workera | Niskie | Średni | Profilowanie w Fazie 5 |
| Brakujące mapowania bloków | Średnie | Niski | Fallback do air + warning |

---

## Kolejność priorytetów

Jeśli czas jest ograniczony, realizuj w kolejności:

1. **Krytyczne:** Faza 1 + Faza 2 (event system + JVM handler)
2. **Ważne:** Faza 3.1 (BetterStorage jako proof-of-concept)
3. **Normalne:** Faza 3.2-3.3 (pozostałe konwertery)
4. **Nice-to-have:** Faza 4-5 (pipeline, cleanup)

Minimum viable: Po Fazie 3.1 system jest użyteczny dla jednego moda.
