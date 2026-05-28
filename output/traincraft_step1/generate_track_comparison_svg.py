#!/usr/bin/env python3
"""
Generates SVG visual comparison of Traincraft 1.7.10 tracks vs Create 1.18.2 tracks.
Based on exact source code from mod_src.
"""

import os

SVG_HEADER = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <style>
      .title {{ font-family: sans-serif; font-size: 14px; font-weight: bold; }}
      .label {{ font-family: sans-serif; font-size: 11px; }}
      .sub {{ font-family: sans-serif; font-size: 10px; fill: #555; }}
      .tc-main {{ fill: #d9534f; stroke: #333; stroke-width: 1; }}
      .tc-gag {{ fill: #f0ad4e; stroke: #333; stroke-width: 1; }}
      .tc-straight {{ fill: #5bc0de; stroke: #333; stroke-width: 1; }}
      .create-block {{ fill: #5cb85c; stroke: #333; stroke-width: 1; }}
      .create-fake {{ fill: #9e9e9e; stroke: #666; stroke-width: 1; stroke-dasharray: 3,2; }}
      .grid {{ stroke: #ddd; stroke-width: 0.5; }}
      .arrow {{ stroke: #333; stroke-width: 1.5; marker-end: url(#arrowhead); }}
      .bezier {{ fill: none; stroke: #5cb85c; stroke-width: 3; }}
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
    </marker>
  </defs>
  <rect width="100%" height="100%" fill="#fafafa" />
'''

SVG_FOOTER = '</svg>\n'

BLOCK_SIZE = 24
GAP = 2
MARGIN = 20
COL_WIDTH = 380
ROW_HEIGHT = 320

# Colors
C_MAIN = "#d9534f"   # tcRail main (red)
C_GAG = "#f0ad4e"    # tcRailGag (orange)
C_STRAIGHT = "#5bc0de"  # straight tcRail (blue)
C_CREATE = "#5cb85c" # Create track (green)
C_FAKE = "#bdbdbd"   # fake track (grey dashed)


def draw_grid(group, offset_x, offset_y, cols, rows, occupied, title, subtitle, scale=1.0):
    """Draw a grid showing occupied blocks.
    occupied: dict of (c,r) -> (type, label) where type in ('main','gag','straight')
    """
    bs = int(BLOCK_SIZE * scale)
    total_w = cols * (bs + GAP)
    total_h = rows * (bs + GAP)
    
    # Title
    group.append(f'  <text x="{offset_x}" y="{offset_y - 8}" class="title">{title}</text>\n')
    group.append(f'  <text x="{offset_x}" y="{offset_y + 6}" class="sub">{subtitle}</text>\n')
    
    # Grid background
    for r in range(rows):
        for c in range(cols):
            x = offset_x + c * (bs + GAP)
            y = offset_y + 20 + r * (bs + GAP)
            group.append(f'  <rect x="{x}" y="{y}" width="{bs}" height="{bs}" class="grid" fill="white"/>\n')
    
    # Occupied blocks
    for (c, r), (btype, label) in occupied.items():
        x = offset_x + c * (bs + GAP)
        y = offset_y + 20 + r * (bs + GAP)
        if btype == 'main':
            fill = C_MAIN
        elif btype == 'gag':
            fill = C_GAG
        elif btype == 'straight':
            fill = C_STRAIGHT
        else:
            fill = C_CREATE
        group.append(f'  <rect x="{x}" y="{y}" width="{bs}" height="{bs}" fill="{fill}" stroke="#333" stroke-width="1"/>\n')
        if bs >= 20 and label:
            # Center text
            tx = x + bs // 2
            ty = y + bs // 2 + 4
            group.append(f'  <text x="{tx}" y="{ty}" text-anchor="middle" class="label" fill="white" font-size="{max(8, bs//3)}">{label}</text>\n')
    
    # Legend
    lx = offset_x
    ly = offset_y + 30 + total_h
    group.append(f'  <rect x="{lx}" y="{ly}" width="{bs}" height="{bs}" fill="{C_MAIN}" stroke="#333" stroke-width="1"/>\n')
    group.append(f'  <text x="{lx + bs + 4}" y="{ly + bs//2 + 4}" class="sub">tcRail (main)</text>\n')
    group.append(f'  <rect x="{lx + 90}" y="{ly}" width="{bs}" height="{bs}" fill="{C_GAG}" stroke="#333" stroke-width="1"/>\n')
    group.append(f'  <text x="{lx + 90 + bs + 4}" y="{ly + bs//2 + 4}" class="sub">tcRailGag</text>\n')
    group.append(f'  <rect x="{lx + 180}" y="{ly}" width="{bs}" height="{bs}" fill="{C_STRAIGHT}" stroke="#333" stroke-width="1"/>\n')
    group.append(f'  <text x="{lx + 180 + bs + 4}" y="{ly + bs//2 + 4}" class="sub">tcRail straight</text>\n')


def draw_create_simple(group, offset_x, offset_y, title, subtitle, bezier=False, endpoints=1):
    """Draw Create track representation."""
    group.append(f'  <text x="{offset_x}" y="{offset_y - 8}" class="title">{title}</text>\n')
    group.append(f'  <text x="{offset_x}" y="{offset_y + 6}" class="sub">{subtitle}</text>\n')
    
    bs = BLOCK_SIZE
    if bezier:
        # Two endpoints with bezier curve between them
        x1 = offset_x + 20
        y1 = offset_y + 80
        x2 = offset_x + 140
        y2 = offset_y + 80
        # Draw bezier curve
        cx1 = x1 + 30
        cy1 = y1 - 60
        cx2 = x2 - 30
        cy2 = y2 - 60
        group.append(f'  <path d="M {x1+bs//2} {y1} C {cx1} {cy1}, {cx2} {cy2}, {x2+bs//2} {y2}" class="bezier"/>\n')
        
        # Endpoint blocks
        group.append(f'  <rect x="{x1}" y="{y1}" width="{bs}" height="{bs}" fill="{C_CREATE}" stroke="#333" stroke-width="2"/>\n')
        group.append(f'  <text x="{x1+bs//2}" y="{y1+bs//2+4}" text-anchor="middle" class="label" fill="white" font-size="10">TE</text>\n')
        group.append(f'  <rect x="{x2}" y="{y2}" width="{bs}" height="{bs}" fill="{C_CREATE}" stroke="#333" stroke-width="2"/>\n')
        group.append(f'  <text x="{x2+bs//2}" y="{y2+bs//2+4}" text-anchor="middle" class="label" fill="white" font-size="10">TE</text>\n')
        
        # Fake tracks along curve
        fake_positions = [(50, 40), (80, 25), (110, 40)]
        for fx, fy in fake_positions:
            group.append(f'  <rect x="{offset_x + fx}" y="{offset_y + fy}" width="{bs*0.8:.0f}" height="{bs*0.8:.0f}" fill="{C_FAKE}" stroke="#666" stroke-width="1" stroke-dasharray="3,2"/>\n')
        
        group.append(f'  <text x="{offset_x + 20}" y="{offset_y + 130}" class="sub">1 block + BezierConnection NBT per endpoint</text>\n')
        group.append(f'  <text x="{offset_x + 20}" y="{offset_y + 145}" class="sub">fake_track blocks generated at runtime</text>\n')
    else:
        # Simple straight / junction
        x = offset_x + 60
        y = offset_y + 60
        group.append(f'  <rect x="{x}" y="{y}" width="{bs}" height="{bs}" fill="{C_CREATE}" stroke="#333" stroke-width="2"/>\n')
        group.append(f'  <text x="{x+bs//2}" y="{y+bs//2+4}" text-anchor="middle" class="label" fill="white" font-size="10">track</text>\n')
        group.append(f'  <text x="{offset_x + 20}" y="{offset_y + 110}" class="sub">1 block, blockstate only (no BE)</text>\n')
    
    # Legend
    ly = offset_y + 170
    group.append(f'  <rect x="{offset_x}" y="{ly}" width="{bs}" height="{bs}" fill="{C_CREATE}" stroke="#333" stroke-width="1"/>\n')
    group.append(f'  <text x="{offset_x + bs + 4}" y="{ly + bs//2 + 4}" class="sub">TrackBlock (create:track)</text>\n')
    if bezier:
        group.append(f'  <rect x="{offset_x + 150}" y="{ly}" width="{bs}" height="{bs}" fill="{C_FAKE}" stroke="#666" stroke-width="1" stroke-dasharray="3,2"/>\n')
        group.append(f'  <text x="{offset_x + 150 + bs + 4}" y="{ly + bs//2 + 4}" class="sub">FakeTrackBlock</text>\n')


def make_track_occupied(xz_list, is_turn=True, has_enter=False, has_exit=False):
    """Build occupied dict from list of (x,z) relative positions.
    First item is main tcRail, rest are gag. If has_enter, prepend enter straight.
    If has_exit, append exit straight.
    """
    occ = {}
    idx = 0
    if has_enter:
        occ[(0, 0)] = ('straight', 'S')
        idx = 1
    
    # Main turn rail
    main_pos = xz_list[idx]
    occ[main_pos] = ('main', 'M')
    idx += 1
    
    # Gags
    for i in range(idx, len(xz_list)):
        occ[xz_list[i]] = ('gag', 'G')
    
    if has_exit:
        # exit position determined separately
        pass
    return occ


def normalize_positions(occ):
    """Shift all positions so min x and min z are 0."""
    if not occ:
        return occ
    min_c = min(c for c, r in occ)
    min_r = min(r for c, r in occ)
    return {(c - min_c, r - min_r): v for (c, r), v in occ.items()}


def main():
    out_path = os.path.join(os.path.dirname(__file__), 'traincraft_vs_create_tracks.svg')
    
    # Define track layouts from source code analysis
    # Coordinates are (x,z) relative, we map x->column, z->row (but z goes down in SVG)
    # For top-down view, we use z as row (negative z = up = smaller row)
    
    diagrams = []
    
    # --- SMALL STRAIGHT ---
    occ = {(0,0): ('straight', 'S')}
    occ = normalize_positions(occ)
    diagrams.append(('SMALL_STRAIGHT', '1×1  |  1 block', occ, 1, 1, False, 'Straight (Create)', '1 block (track shape xo/zo)'))
    
    # --- MEDIUM STRAIGHT ---
    # 1 tcRail + 2 gag in line (l=2 -> z direction)
    occ = {(0,0): ('straight', 'S'), (0,-1): ('gag','G'), (0,-2): ('gag','G')}
    occ = normalize_positions(occ)
    diagrams.append(('MEDIUM_STRAIGHT', '1×3  |  3 blocks', occ, 1, 3, False, 'Straight (Create)', '1 block per segment'))
    
    # --- LONG STRAIGHT ---
    # 2 tcRail + 4 gag (l=2)
    occ = {(0,0): ('straight','S'), (0,-1): ('gag','G'), (0,-2): ('gag','G'),
           (0,-3): ('straight','S'), (0,-4): ('gag','G'), (0,-5): ('gag','G')}
    occ = normalize_positions(occ)
    diagrams.append(('LONG_STRAIGHT', '1×6  |  6 blocks', occ, 1, 6, False, 'Straight (Create)', '1 block per segment'))
    
    # --- MEDIUM TURN (right, l=2) ---
    # xArray={x, x, x+1, x+1, x+2}, zArray={z, z-1, z-1, z-2, z-2}
    # putDownEnterTrack=false, putDownExitTrack=false
    # main at (0,0), gags at (0,-1),(1,-1),(1,-2),(2,-2)
    occ = {(0,0): ('main','M'), (0,-1): ('gag','G'), (1,-1): ('gag','G'), (1,-2): ('gag','G'), (2,-2): ('gag','G')}
    occ = normalize_positions(occ)
    diagrams.append(('MEDIUM_TURN', '3×3 area  |  5 blocks', occ, 3, 3, True, 'Turn (Create)', '1 block + Bezier curve'))
    
    # --- LARGE TURN (right, l=2) ---
    # xArray={x,x,x,x+1,x+1,x+2,x,x+1,x+2,x+3,x+4,x+3,x+2}
    # zArray={z,z-1,z-2,z-1,z-2,z-2,z-2,z-3,z-3,z-3,z-4,z-4,z-4}
    # Remove duplicate (0,-2) if any
    occ = {}
    positions = [(0,0),(0,-1),(0,-2),(1,-1),(1,-2),(2,-2),(0,-2),(1,-3),(2,-3),(3,-3),(4,-4),(3,-4),(2,-4)]
    seen = set()
    for i, (c,r) in enumerate(positions):
        if (c,r) in seen:
            continue
        seen.add((c,r))
        if i == 0:
            occ[(c,r)] = ('main','M')
        else:
            occ[(c,r)] = ('gag','G')
    occ = normalize_positions(occ)
    diagrams.append(('LARGE_TURN', '5×5 area  |  12 blocks', occ, 5, 5, True, 'Turn (Create)', '1 block + Bezier curve'))
    
    # --- VERY LARGE TURN (right, l=2) ---
    positions = [
        (0,0),(0,-1),(0,-2),(1,-2),(0,-3),(1,-3),(0,-4),(1,-4),(1,-5),(2,-4),(2,-5),(2,-6),
        (3,-6),(3,-7),(4,-7),(4,-8),(5,-7),(5,-8),(5,-9),(6,-8),(6,-9),(7,-8),(7,-9),(8,-9),(9,-9)
    ]
    occ = {}
    seen = set()
    for i, (c,r) in enumerate(positions):
        if (c,r) in seen:
            continue
        seen.add((c,r))
        occ[(c,r)] = ('main','M') if i == 0 else ('gag','G')
    occ = normalize_positions(occ)
    diagrams.append(('VERY_LARGE_TURN', '10×10 area  |  25 blocks', occ, 10, 10, True, 'Turn (Create)', '1 block + Bezier curve'))
    
    # --- MEDIUM RIGHT SWITCH (l=2) ---
    # putDownTurn with enter+exit: xArray={x+1,x+1,x+2}, zArray={z-2,z-3,z-3}
    #   -> enter (x,z), main (x+1,z-2), gags (x+1,z-3),(x+2,z-3), exit (x+3,z-3)
    # switch rail 1: (x,z-1)
    # switch rail 2: (x,z-2)
    # straight exit: (x,z-3)
    occ = {
        (0,0): ('straight','E'),      # enter
        (1,-2): ('main','M'),         # main turn rail
        (1,-3): ('gag','G'),
        (2,-3): ('gag','G'),
        (3,-3): ('straight','X'),     # exit
        (0,-1): ('straight','1'),     # switch rail 1
        (0,-2): ('straight','2'),     # switch rail 2
        (0,-3): ('straight','3'),     # straight exit
    }
    occ = normalize_positions(occ)
    diagrams.append(('MEDIUM_SWITCH', '4×4 area  |  ~8 blocks', occ, 4, 4, False, 'Switch (Create)', '1 block track_switch_andesite'))
    
    # --- LARGE RIGHT SWITCH (l=2) ---
    # xArray={x+1,x+1,x+2,x+1,x+2,x+3,x+4,x+3,x+2}, zArray={z-2,z-3,z-3,z-4,z-4,z-4,z-5,z-5,z-5}
    # enter (x,z), main (x+1,z-2), gags..., exit (x+5,z-5)
    # switch rails: (x,z-1),(x,z-2),(x,z-3)
    # straight exits: (x,z-4),(x,z-5)
    occ = {
        (0,0): ('straight','E'),
        (1,-2): ('main','M'),
        (1,-3): ('gag','G'), (2,-3): ('gag','G'),
        (1,-4): ('gag','G'), (2,-4): ('gag','G'), (3,-4): ('gag','G'),
        (4,-5): ('gag','G'), (3,-5): ('gag','G'), (2,-5): ('gag','G'),
        (5,-5): ('straight','X'),
        (0,-1): ('straight','1'), (0,-2): ('straight','2'), (0,-3): ('straight','3'),
        (0,-4): ('straight','4'), (0,-5): ('straight','5'),
    }
    occ = normalize_positions(occ)
    diagrams.append(('LARGE_SWITCH', '6×6 area  |  ~14 blocks', occ, 6, 6, False, 'Switch (Create)', '1 block track_switch_andesite'))
    
    # --- MEDIUM PARALLEL SWITCH (right, l=2) ---
    # This is complex. Let's use the bounding box 4x11 and approximate structure.
    # From code: two turns + straight blocks spanning ~11 blocks in one direction.
    # We'll draw a schematic representation.
    occ = {}
    # Main branch (straight-ish)
    for i in range(10):
        occ[(0, -i)] = ('straight', 'S' if i==0 else str(i))
    # First turn branch
    occ[(1, -3)] = ('main', 'T1')
    occ[(1, -4)] = ('gag', 'G')
    occ[(2, -4)] = ('gag', 'G')
    occ[(2, -5)] = ('gag', 'G')
    # Second turn branch (parallel)
    occ[(3, -6)] = ('main', 'T2')
    for c in range(3, 6):
        for r in range(-9, -6):
            if (c,r) not in occ:
                occ[(c,r)] = ('gag', 'G')
    occ = normalize_positions(occ)
    diagrams.append(('MEDIUM_PARALLEL_SWITCH', '4×11 area  |  ~22 blocks', occ, 4, 11, False, 'Switch (Create)', '1 block track_switch_andesite'))
    
    # --- SLOPE (1×6) ---
    # 1 tcRail + 5 gag, bbHeight increases
    occ = {}
    occ[(0,0)] = ('main', 'M')
    for i in range(1,6):
        occ[(0,-i)] = ('gag', f'{i}')
    occ = normalize_positions(occ)
    diagrams.append(('SLOPE', '1×6  |  6 blocks', occ, 1, 6, False, 'Slope (Create)', '1 block TrackShape.AE/AW/AN/AS'))
    
    # --- TWO WAYS CROSSING ---
    # Approximate 3x3 crossing
    occ = {
        (0,0): ('main','M'), (0,-1): ('gag','G'), (0,-2): ('straight','S'),
        (1,0): ('gag','G'), (1,-1): ('main','C'), (1,-2): ('gag','G'),
        (2,0): ('straight','S'), (2,-1): ('gag','G'), (2,-2): ('straight','S'),
    }
    occ = normalize_positions(occ)
    diagrams.append(('TWO_WAYS_CROSSING', '3×3 area  |  ~9 blocks', occ, 3, 3, False, 'Crossing (Create)', '1 block TrackShape.CR_O'))
    
    # Generate SVG
    groups = []
    num_diag = len(diagrams)
    cols = 2  # Traincraft left, Create right
    rows_per_col = (num_diag + 0) // 1  # Each diagram is a row
    
    svg_w = COL_WIDTH * 2 + MARGIN * 3
    svg_h = ROW_HEIGHT * ((num_diag + 1) // 2) + MARGIN * 2
    if num_diag % 2 == 1:
        svg_h += ROW_HEIGHT // 2
    
    # Recalculate: each diagram gets full row with two columns
    svg_w = COL_WIDTH * 2 + MARGIN * 3
    svg_h = num_diag * ROW_HEIGHT + MARGIN * 2
    
    header = SVG_HEADER.format(width=svg_w, height=svg_h)
    
    for idx, (name, tc_sub, occ, grid_w, grid_h, bezier, create_title, create_sub) in enumerate(diagrams):
        row_y = MARGIN + idx * ROW_HEIGHT
        
        # Left: Traincraft
        lx = MARGIN
        scale = min(1.0, 280.0 / (grid_w * (BLOCK_SIZE + GAP)))
        if grid_h * (BLOCK_SIZE + GAP) * scale > 200:
            scale = min(scale, 200.0 / (grid_h * (BLOCK_SIZE + GAP)))
        draw_grid(groups, lx, row_y, grid_w, grid_h, occ, name, tc_sub, scale=scale)
        
        # Arrow
        ax = lx + COL_WIDTH - 40
        ay = row_y + ROW_HEIGHT // 2
        groups.append(f'  <line x1="{ax}" y1="{ay}" x2="{ax+30}" y2="{ay}" class="arrow"/>\n')
        
        # Right: Create
        rx = MARGIN + COL_WIDTH + 20
        if bezier:
            draw_create_simple(groups, rx, row_y, create_title, create_sub, bezier=True)
        else:
            draw_create_simple(groups, rx, row_y, create_title, create_sub, bezier=False)
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(header)
        f.writelines(groups)
        f.write(SVG_FOOTER)
    
    print(f"SVG written to: {out_path}")


if __name__ == '__main__':
    main()
