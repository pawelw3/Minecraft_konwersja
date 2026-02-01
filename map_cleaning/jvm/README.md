# Map Cleaner - Szybkie czyszczenie mapy Minecraft 1.7.10

Napisany w Kotlinie, zoptymalizowany pod kątem prędkości.

## Wydajność

| Operacja | Szacunkowy czas dla 5GB mapy (1195 regionów) |
|----------|---------------------------------------------|
| Analiza (`--dry-run`) | **~2 minuty** |
| Czyszczenie (zapis) | **~5-10 minut** (SSD) / **~30-60 minut** (HDD) |

Porównanie z Python:
- Python: 100+ godzin
- Ten tool: **~10 minut** (60x-600x szybciej!)

## Budowanie

```bash
cd map_cleaning/jvm
.\gradlew.bat jar
```

## Jak to działa?

Program może pracować w **dwóch trybach**:

### 1. Czyszczenie w miejscu (nadpisuje oryginał)
```bash
java -jar build/libs/map-cleaner-1.0-SNAPSHOT.jar ../../mapa_1710
```
**UWAGA:** Modyfikuje pliki bezpośrednio w podanej lokalizacji!

### 2. Czyszczenie z zapisem do nowej lokalizacji (bezpieczniejsze)
```bash
java -jar build/libs/map-cleaner-1.0-SNAPSHOT.jar ../../mapa_1710 --output ../mapa_wyczyszczona
```
W tym trybie:
- Kopiuje wszystkie pliki singleplayer (level.dat, playerdata, stats, itp.)
- Czyści tylko regiony w zakresie -16..16 (domyślnie)
- Zapisuje wynik do nowej lokalizacji
- Oryginał pozostaje nietknięty

## Użycie

### Analiza (bez modyfikacji)
```bash
java -jar build/libs/map-cleaner-1.0-SNAPSHOT.jar ../../mapa_1710 --dry-run
```

### Czyszczenie całej mapy (bezpieczne - do nowej lokalizacji)
```bash
java -jar build/libs/map-cleaner-1.0-SNAPSHOT.jar ../../mapa_1710 --output ../mapa_wyczyszczona
```

### Czyszczenie w miejscu (szybsze, ale nadpisuje oryginał!)
```bash
java -jar build/libs/map-cleaner-1.0-SNAPSHOT.jar ../../mapa_1710
```

### Tylko jeden region
```bash
java -jar build/libs/map-cleaner-1.0-SNAPSHOT.jar ../../mapa_1710 --region 0,0 --output ./region_00
```

### Pełny zakres regionów (domyślnie tylko -16..16)
```bash
# Domyślnie: tylko regiony od -16,-16 do 16,16 (1024 regiony)
java -jar build/libs/map-cleaner-1.0-SNAPSHOT.jar ../../mapa_1710 --output ../mapa_wyczyszczona

# Wszystkie regiony (może być bardzo dużo!)
java -jar build/libs/map-cleaner-1.0-SNAPSHOT.jar ../../mapa_1710 --output ../mapa_wyczyszczona --all-regions
```

## Parametry

| Parametr | Opis |
|----------|------|
| `--output PATH` | Ścieżka docelowa (domyślnie: nadpisuje źródło) |
| `--threads N` | Liczba wątków (domyślnie: liczba rdzeni) |
| `--dry-run` | Tylko analiza, bez modyfikacji |
| `--region x,z` | Przetwórz tylko jeden region |
| `--all-regions` | Przetwórz WSZYSTKIE regiony (bez domyślnego limitu -16..16) |

## Domyślny zakres regionów

Program domyślnie przetwarza tylko regiony w zakresie **-16,-16 do 16,16** (czyli 33×33 = 1089 regionów maksymalnie).

To odpowiada obszarowi świata:
- Od chunków: -256,-256 do 256,256
- Od bloków: -4096,-4096 do 4096,4096

Jeśli mapa ma regiony dalej (np. r.100.100.mca), użyj `--all-regions`.

## Struktura wynikowa (przy --output)

```
mapa_wyczyszczona/
├── level.dat            # metadane świata
├── level.dat_old        # backup
├── session.lock         # plik sesji
├── uid.dat             # UUID świata
├── playerdata/         # dane graczy (inventory, pozycja)
├── stats/              # statystyki graczy
├── data/               # dane map i inne
├── forcedchunks.dat    # wymuszone chunki
├── idcounts.dat        # liczniki ID
└── region/             # główny świat (wyczyszczone regiony)
    ├── r.-16.-16.mca
    ├── r.-16.-15.mca
    ...
    └── r.16.16.mca
```

## Optymalizacje

1. **Memory-mapped files** - pliki mapowane w pamięci (zero-copy)
2. **Równoległość** - każdy region w osobnym wątku
3. **Lazy NBT parsing** - parsowanie tylko potrzebnych sekcji
4. **Brak pośrednich plików** - bez JSONów, bez kopiowania

## Przykładowy workflow

```bash
# 1. Najpierw analiza - sprawdź ile jest bloków z modów
cd map_cleaning/jvm
java -jar build/libs/map-cleaner-1.0-SNAPSHOT.jar ../../mapa_1710 --dry-run

# 2. Wyczyść do nowej lokalizacji (bezpieczne)
java -jar build/libs/map-cleaner-1.0-SNAPSHOT.jar ../../mapa_1710 --output ../mapa_wyczyszczona

# 3. Sprawdź wynik
dir ../mapa_wyczyszczona/region

# 4. Gotowe! mapa_wyczyszczona można otworzyć w Minecraft 1.7.10
```

## Wymagania

- Java 17+
- 2GB+ RAM (dla dużych map zalecane 4GB)
