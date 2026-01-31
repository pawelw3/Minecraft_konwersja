# src/ - Kod źródłowy projektu

Ten folder zawiera główny kod źródłowy projektu konwersji mapy Minecraft.

## Struktura

```
src/
├── minecraft_map_parser/      # Główny moduł parsowania mapy
│   ├── __init__.py            # Eksporty publiczne
│   ├── nbt_parser.py          # Parser formatu NBT
│   ├── anvil_parser.py        # Parser plików regionów MCA
│   ├── mod_block_extractor.py # Ekstraktor bloków/tile entities
│   ├── visualizer.py          # Generator wizualizacji SVG
│   └── README.md              # Dokumentacja modułu
├── visualize_choroszcz.py     # Skrypt wizualizacji strefy Choroszcz
├── analyze_shape.py           # Analiza kształtu struktur
└── analyze_ae2_blocks.py      # Szczegółowa analiza bloków AE2
```

## Użycie

### Wizualizacja strefy

```bash
cd src
python visualize_choroszcz.py
```

### Analiza struktury

```bash
cd src
python analyze_shape.py
```

### Analiza bloków AE2

```bash
cd src
python analyze_ae2_blocks.py
```

## Importowanie modułu

```python
from minecraft_map_parser import ModBlockExtractor, MapVisualizer

# Ekstrakcja danych
extractor = ModBlockExtractor()
data = extractor.extract_from_region(
    'mapa_1710/region/r.1.-2.mca',
    x_min=763, x_max=916,
    z_min=-787, z_max=-636,
)

# Wizualizacja
visualizer = MapVisualizer(pixel_size=2)
svg = visualizer.generate_svg(data['blocks'], data['tile_entities'])
```

## Wymagania

- Python 3.10+
- Brak zewnętrznych zależności (czysty Python)
