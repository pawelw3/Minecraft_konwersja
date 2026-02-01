# Map Cleaner - Czyszczenie mapy Minecraft 1.7.10

Wydajny i poprawny program czyszczący mapę Minecraft 1.7.10 z modowej zawartości.

## Wymagania

- Java 17+
- Kotlin (do kompilacji)

## Kompilacja

```bash
./gradlew build
```

Plik wynikowy: `build/libs/map-cleaner-1.0-SNAPSHOT.jar`

## Użycie

```bash
java -jar map-cleaner-1.0-SNAPSHOT.jar <ścieżka_świata> [opcje]
```

### Opcje

| Opcja | Opis |
|-------|------|
| `--output PATH` | Ścieżka docelowa (domyślnie: nadpisuje źródło) |
| `--threads N` | Liczba wątków (domyślnie: liczba rdzeni) |
| `--dry-run` | Tylko analiza, bez modyfikacji |
| `--backup` | Utwórz backup przed czyszczeniem |
| `--rules PATH` | Ścieżka do pliku reguł JSON |
| `--dim TYPE` | Wymiar: `overworld`, `nether`, `end`, `all` |
| `--blocks-only` | Tylko bloki (bez TE i Entities) |
| `--blocks-and-te` | Bloki + TileEntities (bez Entities) |
| `--full` | Pełne czyszczenie (domyślne) |

### Przykłady

```bash
# Analiza (tylko statystyki)
java -jar map-cleaner.jar ../mapa_1710 --dry-run

# Czyszczenie z zapisem do nowej lokalizacji
java -jar map-cleaner.jar ../mapa_1710 --output ../mapa_wyczyszczona

# Tylko overworld
java -jar map-cleaner.jar ../mapa_1710 --dim overworld --dry-run

# Pełne czyszczenie w miejscu
java -jar map-cleaner.jar ../mapa_1710
```

## Reguły czyszczenia (rules.json)

```json
{
  "removeBlockIds": [],
  "keepBlockIds": [],
  "removeTileEntityIds": ["appliedenergistics2", "mekanism", ...],
  "removeEntityIds": ["customnpcs", ...],
  "replacementBlock": 0,
  "useHeuristics": true,
  "cleanTileEntities": true,
  "cleanEntities": true
}
```

- `useHeuristics: true` - bloki >= 256 są traktowane jako modowe
- `removeTileEntityIds` - prefiksy ID TE do usunięcia
- `replacementBlock` - ID bloku zastępczego (0 = air, 1 = stone)

## Architektura

```
Main.kt
  └─> WorldScanner (skanuje wszystkie wymiary)
       └─> RegionProcessor (przetwarza .mca, wielowątkowo)
            └─> ChunkCleaner (czyści pojedynczy chunk)
                 ├─> BlockCodec (obsługa Blocks/Add/Data)
                 ├─> CleaningRules (decyzje co usunąć)
                 └─> Hephaistos NBT (round-trip bez strat)
```

## Cechy

- ✅ Round-trip NBT bez strat (używa Hephaistos)
- ✅ Pełna obsługa ID bloków 0-4095 (Blocks + Add)
- ✅ Czyszczenie TileEntities i Entities
- ✅ Wszystkie wymiary (overworld, nether, end, DIM*)
- ✅ Wielowątkowość (per region)
- ✅ Tryb dry-run (analiza bez modyfikacji)

## Testowanie

Testuj tylko na małych mapach z `lightweigh_map_templates/`:

```bash
java -jar map-cleaner.jar ../../lightweigh_map_templates/1710_modded/konwersja1 --dry-run
```

## Uwagi

- ZAWSZE wykonaj `--dry-run` przed czyszczeniem
- Przetestuj na małej mapie przed użyciem na dużej
- Program modyfikuje tylko zmienione chunki (optymalizacja)
