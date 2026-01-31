# Handoff: Poprawki konwersji JSON → Schematic + Serwer 1.7.10

## Podsumowanie sesji
Wprowadzono poprawki zgodnie z instrukcją `src/instrukcja_poprawek_konwersji_json_schematic.md`:
1. Optymalizacja .gitignore
2. Poprawki w json_to_schematic.py (torch, metadata, lever, NBT)
3. Dodanie chunkloadera (spawn w chunku ze strukturą)
4. Test serwera

## Wprowadzone poprawki

### 1. .gitignore - optymalizacja
Dodano wykluczenia dla:
- `*.cfg`, `*.dat`, `*.dat_old`, `*.dat_mcr`, `session.lock`
- `headless_server/*/config/**/*.cfg`
- `headless_server/*/ops.json`, `whitelist.json`, `banned-*.json`
- `headless_server/*/usercache.json`, `usernamecache.json`
- `headless_server/*/eula.txt`
- Zachowano: `README.md`, `server.properties`, `run.bat`, `run.sh`

### 2. json_to_schematic.py - poprawki

#### 2.1 Redstone torch (ID 76 zamiast 75)
```python
"minecraft:redstone_torch": (76, 0),  # lit (zapalona, domyślna)
```

#### 2.2 Rozdzielone mapowania kierunków
- Repeater/Comparator: south=0, west=1, north=2, east=3
- Dropper/Dispenser/CommandBlock: down=0, up=1, north=2, south=3, west=4, east=5

#### 2.3 Lever - powered opcjonalne
```python
powered = voxel.properties.get("powered", False)
meta = get_direction_meta(facing, "lever", powered=powered)
```

#### 2.4 Strict mode dla nieznanych bloków
```python
if voxel.block not in BLOCK_ID_MAP:
    raise ValueError(f"Unknown block: {voxel.block}")
```

#### 2.5 Item ID jako SHORT (nie STRING)
```python
"id": create_short(item_id),  # SHORT dla 1.7.10
```
Dodano mapowanie itemów: `ITEM_ID_MAP` z podstawowymi itemami.

### 3. Chunkloader (spawn w chunku)
- Utworzono `src/add_chunkloader.py`
- Ustawiono spawn w chunku (0,0): pozycja (8, 64, 8)
- Dzięki temu chunk ze strukturą jest ładowany przy starcie serwera

## Test serwera

### Status: ⚠️ CZĘŚCIOWO DZIAŁA
- Serwer uruchamia się: ✅
- Mody ładują się: ✅ (61 modów)
- Chunkloader działa (spawn ustawiony): ✅
- Problem: Chunk zapisany przez schematic_to_world.py jest uszkodzony (EOFException)

### Problemy do rozwiązania
1. **Podwójna kompresja w schematic_to_world.py** - chunk jest kompresowany dwa razy
   - Rozwiązanie: Naprawić `MCRegionWriter.save()` aby nie kompresował ponownie
   
2. **Format zapisu chunka** - region file może mieć błędne nagłówki
   - Rozwiązanie: Zweryfikować strukturę zapisu w `schematic_to_world.py`

## Pliki zmienione
- `.gitignore` - wykluczenia dla plików tymczasowych
- `src/json_to_schematic.py` - poprawki z instrukcji
- `src/add_chunkloader.py` - nowy plik do ustawiania spawnu

## Pliki wygenerowane
- `output/digital_counter_v2.schematic` - nowa wersja z poprawkami

## Następne kroki
1. [ ] Naprawić `schematic_to_world.py` (podwójna kompresja)
2. [ ] Przetestować ponownie serwer
3. [ ] Zweryfikować czy struktura jest widoczna w grze
4. [ ] Przetestować działanie digital_counter (włączyć lever)

## Komendy testowe
```bash
# Wbudowanie schematica
python src/json_to_schematic.py test_scenarios/digital_counter_vanilla/schematics/voxel_grid.json output/digital_counter_v2.schematic

# Wstawienie do świata
python src/schematic_to_world.py output/digital_counter_v2.schematic headless_server/1.7.10/world 0 60 0

# Ustawienie spawnu (chunkloader)
python src/add_chunkloader.py headless_server/1.7.10/world

# Uruchomienie serwera
cd headless_server/1.7.10
run.bat
```
