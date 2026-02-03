# Plan przebudowy: Common Event Handler

## Cel projektu

Stworzenie ujednoliconego systemu gdzie:
- **Python** - odpowiada TYLKO za logikę konwersji (mapowania bloków, transformacje NBT)
- **Kotlin/JVM** - odpowiada za WSZYSTKIE operacje na plikach MCA (odczyt/zapis bloków, BE, entities)

## Problem obecny

```
CHAOS: Każdy konwerter Python robi wszystko po swojemu
├─ BetterStorage → ConversionResult v1 + własny format JSON
├─ BloodMagic   → ConversionResult v2 + inny format
├─ EnderStorage → ConversionResult v3
└─ GrowthCraft  → ConversionResult v4

Brak wspólnego interfejsu do wstawiania danych na mapę docelową!
```

## Rozwiązanie docelowe

```
┌────────────────────────────────────────────────────────────────┐
│  PYTHON (logika konwersji)                                     │
│  ├─ Konwertery modów (mapowania, transformacje NBT)           │
│  ├─ Produkują ustandaryzowane Event JSON                      │
│  └─ ZERO operacji na plikach .mca!                            │
└────────────────────────────────────────────────────────────────┘
                              ↓
                     Event JSON (ustandaryzowany)
                              ↓
┌────────────────────────────────────────────────────────────────┐
│  KOTLIN/JVM EVENT HANDLER                                      │
│  ├─ Parsuje Event JSON                                         │
│  ├─ Grupuje operacje (batch processing)                        │
│  ├─ Obsługuje format 1.7.10 (odczyt) i 1.18.2 (zapis)        │
│  ├─ Waliduje i raportuje błędy                                │
│  └─ Zapisuje atomowo na mapę docelową                         │
└────────────────────────────────────────────────────────────────┘
```

## Dokumenty planu

| Plik | Zawartość |
|------|-----------|
| [01_ARCHITEKTURA.md](01_ARCHITEKTURA.md) | Ogólna architektura systemu |
| [02_EVENT_FORMAT.md](02_EVENT_FORMAT.md) | Specyfikacja formatu Event JSON |
| [03_JVM_WORKER.md](03_JVM_WORKER.md) | Plan rozbudowy workera Kotlin |
| [04_PYTHON_ADAPTERY.md](04_PYTHON_ADAPTERY.md) | Adaptery Python do produkcji eventów |
| [05_MIGRACJA.md](05_MIGRACJA.md) | Plan migracji istniejących konwerterów |
| [06_HARMONOGRAM.md](06_HARMONOGRAM.md) | Fazy wdrożenia i zależności |

## Kluczowe korzyści

| Aspekt | Przed | Po |
|--------|-------|-----|
| Spójność danych | 4 różne formaty | 1 uniwersalny Event JSON |
| Wydajność I/O | Python (wolny) | Kotlin/JVM (10-100x szybszy) |
| Batch processing | Brak | Natywne grupowanie po regionach |
| Transakcyjność | Brak | Atomowy commit z rollback |
| Debugowanie | Trudne | Pełna historia eventów |
| Dodawanie modów | Copy-paste | Implementuj tylko adapter |

## Quick Start (po wdrożeniu)

```bash
# 1. Python generuje eventy
python -m src.converters.betterstorage.batch_converter \
    --source-map maps/1.7.10/world \
    --output events/betterstorage_events.json

# 2. JVM Worker aplikuje eventy na mapę docelową
java -jar jvm/worker/build/libs/worker.jar \
    --apply-events events/betterstorage_events.json \
    --target-world maps/1.18.2/world
```
