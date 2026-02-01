# Map Cleaning - Czyszczenie mapy Minecraft 1.7.10

Ten folder zawiera skrypty do czyszczenia kopii mapy `mapa_1710` z:
- **Entities** (mobów, przedmiotów, projectile, etc.)
- **Block Entities / Tile Entities** (skrzynie, maszyny modów, itp.)
- **Bloków z modów** (zamiana na bedrock)

## Wymagania

### Python
```bash
pip install nbtlib
```

### JVM Worker
JVM worker musi być zbudowany:
```bash
cd ..\jvm\worker
.\gradlew.bat build
```

Sprawdź czy plik `..\jvm\worker\build\libs\mc-editkit-worker-1.0-SNAPSHOT.jar` istnieje.

## Skrypty

### 1. `run_cleaning.py` - Główny skrypt (zalecany)

Najprostszy sposób na wyczyszczenie mapy:

```bash
# Wyczyść całą mapę
python run_cleaning.py

# Wyczyść tylko konkretny region (np. spawn 0,0)
python run_cleaning.py --region 0,0

# Najpierw przeanalizuj, potem wyczyść
python run_cleaning.py --analyze-first

# Tylko analiza bez czyszczenia
python run_cleaning.py --analyze-only
```

### 2. `analyze_map.py` - Analiza mapy

Pokazuje statystyki o tym co jest na mapie:
- Liczbę regionów i chunków
- Bloki z modów (nie-vanilla)
- Tile Entities (z podziałem na typy)
- Entities (z podziałem na typy)

```bash
# Analiza całej mapy
python analyze_map.py

# Analiza konkretnego regionu
python analyze_map.py --region 0,0

# Zapisz szczegółowy raport do JSON
python analyze_map.py --output raport.json
```

### 3. `clean_map.py` - Czyszczenie mapy

Główna logika czyszczenia:

```bash
# Wyczyść domyślną mapę (../mapa_1710) do ./cleaned_map
python clean_map.py

# Wyczyść konkretny region
python clean_map.py --region 0,0

# Wskaż inne źródło i cel
python clean_map.py --source ../inna_mapa --output ./wyczyszczona

# Użyj przeniesienia (move) zamiast kopiowania - szybsze i oszczędza miejsce,
# ALE usuwa oryginał z mapa_1710! Używaj ostrożnie.
python clean_map.py --move
```

### 4. `clean_entities.py` - Czyszczenie samych entities

Pomocniczy skrypt do czyszczenia tylko entities (bez bloków):

```bash
# Wyczyść entities z całej mapy
python clean_entities.py ../mapa_1710

# Wyczyść entities z konkretnego regionu
python clean_entities.py ../mapa_1710 --region 0,0
```

## Proces czyszczenia

1. **Kopiowanie** - Mapa jest kopiowana z `mapa_1710` do `cleaned_map`
2. **Analiza** - Skrypt analizuje wszystkie chunki w poszukiwaniu:
   - Bloków z ID > 197 (nie-vanilla w 1.7.10)
   - Tile Entities (dowolne)
   - Entities (dowolne)
3. **Generowanie patcha** - Tworzony jest plik JSON z operacjami zamiany bloków na bedrock
4. **Aplikowanie patcha** - JVM worker modyfikuje sekcje w plikach .mca
5. **Czyszczenie entities** - Python bezpośrednio modyfikuje NBT chunków usuwając entities

## Format pliku patch JSON

Przykład patcha generowanego przez skrypt:

```json
{
  "edits": [
    {"op": "set_block", "x": 100, "y": 64, "z": 200, "id": 7, "meta": 0},
    {"op": "set_block", "x": 101, "y": 64, "z": 200, "id": 7, "meta": 0}
  ]
}
```

Gdzie:
- `op`: Typ operacji (`set_block` lub `set_te`)
- `x`, `y`, `z`: Współrzędne świata
- `id`: ID bloku (7 = bedrock)
- `meta`: Metadata bloku

## Vanilla Block IDs (Minecraft 1.7.10)

Skrypt uznaje za vanilla bloki z ID 0-197, plus niektóre dodatkowe z nowszych podwersji 1.7.x:
- 0-175: Standardowe bloki vanilla
- 159-175: Dodane w 1.7.x (stained clay, slime block, etc.)

Wszystkie bloki z ID > 197 są traktowane jako bloki z modów i zamieniane na bedrock.

## Uwagi

1. **Bezpieczeństwo**: Skrypt zawsze pracuje na kopii - oryginalna mapa w `mapa_1710` pozostaje nietknięta
2. **Backup**: Przed uruchomieniem upewnij się, że masz backup ważnych danych
3. **Czas wykonania**: Czyszczenie dużej mapy (5GB+) może zająć kilkanaście minut
4. **Pamięć**: Skrypt ładuje pojedyncze regiony, więc nie wymaga dużo RAMu

## Rozwiązywanie problemów

### "Nie znaleziono JVM workera"
```bash
cd ..\jvm\worker
.\gradlew.bat build
```

### "nbtlib nie jest zainstalowany"
```bash
pip install nbtlib
```

### Błędy podczas czyszczenia
Sprawdź czy:
1. Świat źródłowy nie jest używany przez inny proces (Minecraft, serwer)
2. Masz wystarczająco miejsca na dysku
3. Masz uprawnienia do zapisu w folderze docelowym

## Struktura wyjściowa

```
map_1710_no_mods/
├── level.dat            # metadane świata
├── level.dat_old        # backup level.dat
├── session.lock         # plik sesji
├── uid.dat             # UUID świata
├── playerdata/         # dane graczy (inventory, pozycja)
├── stats/              # statystyki graczy
├── data/               # dane map i inne
├── region/             # główny świat (Overworld)
│   ├── r.-1.-1.mca
│   ├── r.0.0.mca
│   └── ...
├── DIM-1/              # Nether (jeśli istnieje)
│   └── region/
└── DIM1/               # End (jeśli istnieje)
    └── region/
```

Skrypt kopiuje wszystkie pliki potrzebne do otwarcia mapy w singleplayerze w Minecraft 1.7.10.
