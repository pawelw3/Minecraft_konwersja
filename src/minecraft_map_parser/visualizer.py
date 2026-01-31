"""
Wizualizator mapy - generuje obraz SVG z blokami i tile entities.
"""

import random
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict

from .mod_block_extractor import BlockInfo, TileEntityInfo, EntityInfo


# Predefiniowane kolory dla znanych modów
MOD_COLORS = {
    'IC2': '#FF6B6B',           # Czerwony
    'BC': '#F4A460',           # Brązowy
    'TE': '#FFD700',           # Złoty
    'AE2': '#4169E1',          # Niebieski
    'AE': '#4169E1',           # Niebieski (stare AE)
    'Mekanism': '#00CED1',     # Turkusowy
    'TC': '#8B4513',           # SaddleBrown (Tinkers')
    'TConstruct': '#8B4513',   # SaddleBrown
    'Railcraft': '#708090',    # SlateGray
    'Thaumcraft': '#9932CC',   # DarkOrchid
    'Forestry': '#228B22',     # ForestGreen
    'CarpentersBlocks': '#DEB887',  # Burlywood
    'JABBA': '#DAA520',        # GoldenRod
    'EnderIO': '#4B0082',      # Indigo
    'MFR': '#FF6347',          # Tomato
    'ProjectRed': '#DC143C',   # Crimson
    'LP': '#4682B4',           # SteelBlue
    'IronChest': '#CD853F',    # Peru
    'OC': '#32CD32',           # LimeGreen
    'CC': '#E9967A',           # DarkSalmon
    'UNKNOWN_MOD': '#FF00FF',  # Magenta (nieznany)
}


@dataclass
class ModColorMap:
    """Mapa kolorów dla modów."""
    color_map: Dict[str, str]
    
    @classmethod
    def generate(cls, mod_names: List[str]) -> 'ModColorMap':
        """Generuje mapę kolorów dla listy modów."""
        color_map = {}
        used_colors = set()
        
        for mod in mod_names:
            if mod in MOD_COLORS:
                color_map[mod] = MOD_COLORS[mod]
                used_colors.add(MOD_COLORS[mod])
            else:
                # Generuj losowy kolor
                while True:
                    hue = random.randint(0, 360)
                    sat = random.randint(50, 90)
                    val = random.randint(50, 80)
                    color = f'hsl({hue}, {sat}%, {val}%)'
                    if color not in used_colors:
                        color_map[mod] = color
                        used_colors.add(color)
                        break
        
        return cls(color_map)
    
    def get_color(self, mod_name: Optional[str]) -> str:
        """Zwraca kolor dla modu."""
        if mod_name is None:
            return '#FFFFFF'  # Biały dla vanilla/brak modu
        return self.color_map.get(mod_name, '#FF00FF')  # Magenta dla nieznanych


class MapVisualizer:
    """Generuje wizualizację mapy w formacie SVG."""
    
    def __init__(self, pixel_size: int = 4):
        self.pixel_size = pixel_size
        self.mod_color_map: Optional[ModColorMap] = None
    
    def _generate_unique_mods_list(self, blocks: List[BlockInfo], 
                                    tile_entities: List[TileEntityInfo],
                                    entities: List[EntityInfo]) -> List[str]:
        """Generuje listę unikalnych modów."""
        mod_names = set()
        
        for block in blocks:
            if block.mod_name:
                mod_names.add(block.mod_name)
        
        for te in tile_entities:
            if te.mod_name:
                mod_names.add(te.mod_name)
        
        for entity in entities:
            if entity.mod_name:
                mod_names.add(entity.mod_name)
        
        return sorted(mod_names)
    
    def _calculate_bounds(self, blocks: List[BlockInfo], 
                          tile_entities: List[TileEntityInfo],
                          entities: List[EntityInfo]) -> Tuple[int, int, int, int]:
        """Oblicza granice obszaru do wizualizacji."""
        all_x = []
        all_z = []
        
        for block in blocks:
            all_x.append(block.x)
            all_z.append(block.z)
        
        for te in tile_entities:
            all_x.append(te.x)
            all_z.append(te.z)
        
        for entity in entities:
            all_x.append(int(entity.x))
            all_z.append(int(entity.z))
        
        if not all_x:
            return (0, 0, 100, 100)
        
        return (min(all_x), min(all_z), max(all_x), max(all_z))
    
    def _aggregate_by_column(self, blocks: List[BlockInfo]) -> Dict[Tuple[int, int], BlockInfo]:
        """
        Agreguje bloki po kolumnie (x, z), zachowując tylko jeden blok na kolumnę.
        W przypadku kilku bloków w tej samej kolumnie, wybiera ten najniżej (największy Y).
        """
        columns: Dict[Tuple[int, int], BlockInfo] = {}
        
        for block in blocks:
            key = (block.x, block.z)
            if key not in columns:
                columns[key] = block
            else:
                # Wybierz blok niżej (wyższy Y)
                if block.y > columns[key].y:
                    columns[key] = block
        
        return columns
    
    def generate_svg(self, blocks: List[BlockInfo],
                    tile_entities: List[TileEntityInfo] = None,
                    entities: List[EntityInfo] = None,
                    title: str = "Mod Blocks Visualization",
                    show_legend: bool = True,
                    show_grid: bool = True,
                    grid_spacing: int = 64) -> str:
        """
        Generuje wizualizację SVG.
        
        Args:
            blocks: Lista bloków do wizualizacji
            tile_entities: Lista tile entities (opcjonalnie)
            entities: Lista entities (opcjonalnie)
            title: Tytuł wizualizacji
            show_legend: Czy pokazywać legendę
            show_grid: Czy pokazywać siatkę
            grid_spacing: Odstęp między liniami siatki
        """
        tile_entities = tile_entities or []
        entities = entities or []
        
        # Wygeneruj mapę kolorów
        mod_names = self._generate_unique_mods_list(blocks, tile_entities, entities)
        self.mod_color_map = ModColorMap.generate(mod_names)
        
        # Oblicz granice
        min_x, min_z, max_x, max_z = self._calculate_bounds(blocks, tile_entities, entities)
        
        # Dodaj margines
        margin = 20
        width = (max_x - min_x + 1) * self.pixel_size + margin * 2
        height = (max_z - min_z + 1) * self.pixel_size + margin * 2
        
        # Dodaj miejsce na legendę
        legend_height = 30 + len(mod_names) * 20 if show_legend else 0
        height += legend_height
        
        # Rozpocznij SVG
        svg_parts = [
            f'<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
            f'  <rect width="100%" height="100%" fill="#f0f0f0"/>',
            f'  <text x="{width/2}" y="20" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold">{title}</text>',
        ]
        
        # Przesunięcie dla mapy (po tytule)
        offset_y = 30
        
        # Tło mapy
        svg_parts.append(f'  <rect x="{margin}" y="{offset_y}" width="{width - margin * 2}" height="{height - offset_y - legend_height - margin}" fill="white" stroke="#ccc"/>')
        
        # Siatka
        if show_grid:
            map_width = (max_x - min_x + 1) * self.pixel_size
            map_height = (max_z - min_z + 1) * self.pixel_size
            
            # Pionowe linie
            for x in range(min_x, max_x + 1, grid_spacing):
                px = margin + (x - min_x) * self.pixel_size
                svg_parts.append(f'  <line x1="{px}" y1="{offset_y}" x2="{px}" y2="{offset_y + map_height}" stroke="#eee" stroke-width="1"/>')
                svg_parts.append(f'  <text x="{px}" y="{offset_y - 2}" text-anchor="middle" font-family="Arial" font-size="8" fill="#999">{x}</text>')
            
            # Poziome linie
            for z in range(min_z, max_z + 1, grid_spacing):
                pz = offset_y + (z - min_z) * self.pixel_size
                svg_parts.append(f'  <line x1="{margin}" y1="{pz}" x2="{margin + map_width}" y2="{pz}" stroke="#eee" stroke-width="1"/>')
                svg_parts.append(f'  <text x="{margin - 2}" y="{pz + 4}" text-anchor="end" font-family="Arial" font-size="8" fill="#999">{z}</text>')
        
        # Agreguj bloki po kolumnach (tak aby był tylko 1 piksel na kolumnę X,Z)
        columns = self._aggregate_by_column(blocks)
        
        # Rysuj bloki
        for (x, z), block in columns.items():
            px = margin + (x - min_x) * self.pixel_size
            py = offset_y + (z - min_z) * self.pixel_size
            color = self.mod_color_map.get_color(block.mod_name)
            
            svg_parts.append(f'  <rect x="{px}" y="{py}" width="{self.pixel_size}" height="{self.pixel_size}" fill="{color}"/>')
        
        # Rysuj tile entities (większe punkty)
        te_size = max(self.pixel_size, 6)
        for te in tile_entities:
            px = margin + (te.x - min_x) * self.pixel_size + (self.pixel_size - te_size) / 2
            py = offset_y + (te.z - min_z) * self.pixel_size + (self.pixel_size - te_size) / 2
            color = self.mod_color_map.get_color(te.mod_name)
            
            # Tile entities jako okręgi
            svg_parts.append(f'  <circle cx="{px + te_size/2}" cy="{py + te_size/2}" r="{te_size/2}" fill="{color}" stroke="black" stroke-width="1"/>')
        
        # Rysuj entities (krzyżyki)
        if entities:
            for entity in entities:
                ex = int(entity.x)
                ez = int(entity.z)
                px = margin + (ex - min_x) * self.pixel_size + self.pixel_size / 2
                py = offset_y + (ez - min_z) * self.pixel_size + self.pixel_size / 2
                size = 3
                
                svg_parts.append(f'  <line x1="{px - size}" y1="{py - size}" x2="{px + size}" y2="{py + size}" stroke="red" stroke-width="2"/>')
                svg_parts.append(f'  <line x1="{px + size}" y1="{py - size}" x2="{px - size}" y2="{py + size}" stroke="red" stroke-width="2"/>')
        
        # Legenda
        if show_legend:
            legend_y = height - legend_height + 10
            svg_parts.append(f'  <text x="{margin}" y="{legend_y}" font-family="Arial" font-size="12" font-weight="bold">Mods:</text>')
            
            col_width = width / 3
            items_per_col = max(1, (legend_height - 40) // 20)
            
            for i, mod in enumerate(mod_names):
                col = i // items_per_col
                row = i % items_per_col
                
                lx = margin + col * col_width
                ly = legend_y + 20 + row * 20
                color = self.mod_color_map.get_color(mod)
                
                svg_parts.append(f'  <rect x="{lx}" y="{ly - 10}" width="12" height="12" fill="{color}" stroke="#333" stroke-width="0.5"/>')
                svg_parts.append(f'  <text x="{lx + 16}" y="{ly}" font-family="Arial" font-size="10">{mod}</text>')
        
        # Zakończ SVG
        svg_parts.append('</svg>')
        
        return '\n'.join(svg_parts)
    
    def generate_summary_html(self, blocks: List[BlockInfo],
                             tile_entities: List[TileEntityInfo] = None,
                             entities: List[EntityInfo] = None) -> str:
        """Generuje podsumowanie w formacie HTML."""
        tile_entities = tile_entities or []
        entities = entities or []
        
        # Statystyki per mod
        block_counts: Dict[str, int] = defaultdict(int)
        te_counts: Dict[str, int] = defaultdict(int)
        entity_counts: Dict[str, int] = defaultdict(int)
        unique_block_ids: Dict[str, Set[int]] = defaultdict(set)
        
        for block in blocks:
            mod = block.mod_name or 'Vanilla'
            block_counts[mod] += 1
            unique_block_ids[mod].add(block.block_id)
        
        for te in tile_entities:
            mod = te.mod_name or 'Vanilla'
            te_counts[mod] += 1
        
        for entity in entities:
            mod = entity.mod_name or 'Vanilla'
            entity_counts[mod] += 1
        
        # Generuj HTML
        html = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '  <meta charset="UTF-8">',
            '  <title>Mod Blocks Summary</title>',
            '  <style>',
            '    body { font-family: Arial, sans-serif; margin: 20px; }',
            '    table { border-collapse: collapse; margin: 10px 0; }',
            '    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }',
            '    th { background-color: #4CAF50; color: white; }',
            '    tr:nth-child(even) { background-color: #f2f2f2; }',
            '    .mod-header { background-color: #2196F3; color: white; font-weight: bold; }',
            '  </style>',
            '</head>',
            '<body>',
            '  <h1>Mod Blocks Summary</h1>',
        ]
        
        # Podsumowanie ogólne
        total_modded_blocks = sum(c for m, c in block_counts.items() if m != 'Vanilla')
        total_vanilla_blocks = block_counts.get('Vanilla', 0)
        
        html.append('  <h2>General Statistics</h2>')
        html.append('  <ul>')
        html.append(f'    <li><strong>Modded blocks:</strong> {total_modded_blocks:,}</li>')
        html.append(f'    <li><strong>Vanilla blocks:</strong> {total_vanilla_blocks:,}</li>')
        html.append(f'    <li><strong>Tile entities:</strong> {len(tile_entities)}</li>')
        html.append(f'    <li><strong>Entities:</strong> {len(entities)}</li>')
        html.append('  </ul>')
        
        # Per mod
        html.append('  <h2>Per Mod Statistics</h2>')
        html.append('  <table>')
        html.append('    <tr><th>Mod</th><th>Blocks</th><th>Unique Block IDs</th><th>Tile Entities</th><th>Entities</th></tr>')
        
        all_mods = set(block_counts.keys()) | set(te_counts.keys()) | set(entity_counts.keys())
        for mod in sorted(all_mods):
            if mod == 'Vanilla':
                continue
            html.append(f'    <tr><td>{mod}</td><td>{block_counts.get(mod, 0):,}</td>'
                       f'<td>{len(unique_block_ids.get(mod, set()))}</td>'
                       f'<td>{te_counts.get(mod, 0)}</td>'
                       f'<td>{entity_counts.get(mod, 0)}</td></tr>')
        
        html.append('  </table>')
        
        # Szczegóły tile entities
        if tile_entities:
            te_by_type: Dict[str, List[TileEntityInfo]] = defaultdict(list)
            for te in tile_entities:
                te_by_type[te.id].append(te)
            
            html.append('  <h2>Tile Entity Types</h2>')
            html.append('  <table>')
            html.append('    <tr><th>Type</th><th>Mod</th><th>Count</th></tr>')
            
            for te_type in sorted(te_by_type.keys()):
                te_list = te_by_type[te_type]
                mod = te_list[0].mod_name or 'Vanilla'
                html.append(f'    <tr><td>{te_type}</td><td>{mod}</td><td>{len(te_list)}</td></tr>')
            
            html.append('  </table>')
        
        html.append('</body>')
        html.append('</html>')
        
        return '\n'.join(html)
