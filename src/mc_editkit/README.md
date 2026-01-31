# mc_editkit - Narzędzie do OFFLINE edycji światów Minecraft 1.7.10

## Opis

Pakiet `mc_editkit` to narzędzie do edycji światów Minecraft **offline** (bez uruchamiania serwera).
Wspiera:
- Wstawianie bloków i TileEntities (TE)
- Struktury (schematy) z plików `voxel_grid.json`
- Command blocki z komendami
- Bloki vanilla i modowe (przez rejestr)
- Headless testy z weryfikacją po logach

## Instalacja zależności

```bash
pip install PyAnvilEditor
```

## Struktura pakietu

```
mc_editkit/
├── blocks/
│   └── registry.py          # Rejestr bloków (vanilla + mody)
├── world/
│   ├── types.py             # Typy pomocnicze (Pos, ChunkPos, RegionPos)
│   ├── editor.py            # WorldEditor API
│   ├── validate.py          # Walidatory świata
│   └── backends/
│       └── anvil_backend.py # Backend PyAnvilEditor
├── structures/
│   ├── palette.py           # Paleta bloków dla struktur
│   └── structure.py         # Klasa Structure + import voxel_grid
└── tests/
    ├── test_smoke_small_paste.py
    ├── test_tileentities_roundtrip.py
    └── test_variant_b_spiral_probe.py
```

## Szybki start

### Edycja świata przez context manager

```python
from mc_editkit.world.editor import edit_world
from mc_editkit.world.types import Pos

with edit_world("path/to/world", backup=True) as editor:
    # Ustaw blok
    editor.set_block_by_name(Pos(100, 64, 100), "minecraft:stone")
    
    # Ustaw command block
    editor.set_command_block(Pos(101, 64, 100), "/say Hello!")
```

### CLI - Wstawianie struktury

```bash
python -m mc_editkit paste \
    --world "headless_server/1.7.10/world" \
    --voxel "test_scenarios/digital_counter_vanilla/schematics/voxel_grid.json" \
    --origin 0 64 0
```

### CLI - Test Variant B (spirala)

```bash
python -m mc_editkit run-test \
    --world "headless_server/1.7.10/world" \
    --test variant_b \
    --radius 3 \
    --duration 120
```

## API WorldEditor

### Operacje atomowe

- `set_block(pos, block_id, meta=0)` - ustawia blok
- `set_block_by_name(pos, name)` - ustawia blok po nazwie (np. "minecraft:stone")
- `get_block(pos)` → (block_id, meta)
- `set_tile_entity(pos, te_data)` - ustawia TileEntity
- `get_tile_entity(pos)` → dict lub None
- `set_command_block(pos, command, ...)` - ustawia command block z komendą

### Operacje hurtowe

- `paste(structure, origin, overwrite=True)` - wstawia strukturę

### Transakcje

- `commit()` - zapisuje zmiany
- `rollback()` - przywraca backup
- `close()` - zamyka edytor

Context manager (`with edit_world(...)`) automatycznie robi commit lub rollback w razie błędu.

## Rejestr bloków

Rejestr mapuje nazwy logiczne na (block_id, meta):

```python
from mc_editkit.blocks.registry import get_registry

registry = get_registry()
stone_id, stone_meta = registry.get("minecraft:stone")
# (1, 0)
```

Wbudowane bloki vanilla: stone, redstone_wire, repeater, command_block, dropper, hopper, chest, itp.

## Testy

### Smoke test

```bash
cd src
python -m mc_editkit.tests.test_smoke_small_paste
```

### Round-trip TileEntities

```bash
cd src
python -m mc_editkit.tests.test_tileentities_roundtrip
```

### Test Variant B (spirala)

```bash
cd src
python -m mc_editkit.tests.test_variant_b_spiral_probe --world "headless_server/1.7.10/world"
```

## Architektura

### Backend

Domyślnie używany jest `AnvilBackend` oparty na `PyAnvilEditor`:
- Odczyt/zapis regionów `.mca`
- Cache chunków w pamięci
- Automatyczny backup przed edycją
- Grupowanie operacji per region

### Walidacja

Po każdej większej edycji należy uruchomić walidator:

```python
from mc_editkit.world.validate import validate_world

if validate_world("path/to/world"):
    print("Świat jest poprawny")
```

## Uwagi

- **Zawsze pracuj na kopii świata** - użyj `WorldCopier.create_copy()`
- **Backup automatyczny** - tworzony przed pierwszą modyfikacją regionu
- **Thread-unsafe** - nie używaj wielu edytorów równolegle na tym samym świecie
