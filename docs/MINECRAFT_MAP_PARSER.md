# Minecraft Map Parser - Dokumentacja

## Opis

System do parsowania mapy Minecraft 1.7.10 z ekstrakcją bloków, tile entities i entities pochodzących z modów. Wygenerowana wizualizacja pokazuje rozmieszczenie elementów z różnych modów na mapie.

## Wyniki testu - Strefa Choroszcz

Wykonano test parsowania strefy **Choroszcz** (X: 763-916, Z: -787 do -636):

### Statystyki

| Kategoria | Liczba |
|-----------|--------|
| Bloki z modów | 40,807 |
| Tile entities z modów | 21,112 |
| Entities z modów | 1 |

### Rozkład per mod

| Mod | Bloki | Tile Entities |
|-----|-------|---------------|
| AE2 (Applied Energistics 2) | 19,694 | 0 |
| BC (BuildCraft) | 14,264 | 0 |
| IC2 (IndustrialCraft 2) | 6,712 | 0 |
| Carpenter's Blocks | 0 | 6,719 |
| ForgeMicroblocks | 0 | 14,257 |
| Railcraft | 0 | 130 |
| ProjectRed | 0 | 5 |

### Typy Tile Entities

| Typ | Mod | Liczba | Uwagi |
|-----|-----|--------|-------|
| savedMultipart | ForgeMicroblocks | 14,257 | Mikrobloki dekoracyjne |
| TileEntityCarpentersBlock | Carpenter's Blocks | 6,719 | Bloki dekoracyjne |
| **RCHiddenTile** | Railcraft | **130** | **IGNOROWANE - TE techniczne do wind** |
| tile.projectred.illumination.lamp\|0 | ProjectRed | 5 | Oświetlenie |
| te.mannequin | Unknown | 1 | Manekin |

> **Uwaga:** `RCHiddenTile` z Railcrafta znajduje się na liście bloków do ignorowania (`docs/IGNORED_BLOCKS.md`)

## Pliki wynikowe

- `output/visualizations/choroszcz_mod_blocks.svg` - Wizualizacja mapy z zaznaczonymi blokami
- `output/visualizations/choroszcz_summary.html` - Podsumowanie statystyczne

## Użycie

```bash
cd src
python visualize_choroszcz.py
```

lub dla innych stref:

```python
from minecraft_map_parser import ModBlockExtractor, MapVisualizer

extractor = ModBlockExtractor()
data = extractor.extract_from_region(
    'mapa_1710/region/r.X.Z.mca',
    x_min=..., x_max=...,
    z_min=..., z_max=...,
)

visualizer = MapVisualizer(pixel_size=2)
svg = visualizer.generate_svg(data['blocks'], data['tile_entities'])
```

## Struktura kodu

- `src/minecraft_map_parser/` - Główny pakiet
  - `nbt_parser.py` - Parser NBT
  - `anvil_parser.py` - Parser plików MCA
  - `mod_block_extractor.py` - Ekstraktor bloków/tile entities
  - `visualizer.py` - Generator wizualizacji SVG
  - `README.md` - Dokumentacja pakietu
