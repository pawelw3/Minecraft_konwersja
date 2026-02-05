#!/usr/bin/env python3
"""
Wizualizacja 3D przypadków testowych cięcia bloków - wersja 2.
- Faktycznie przycięte bloki (nie pełne)
- Zaokrąglanie płaszczyzn do siatki 16x16 (pikseli tekstury)
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import proj3d
import matplotlib.patches as mpatches
from PIL import Image
import os

# Kolory tekstur BloodMagic
TEXTURE_COLORS = {
    'BloodAltar_Top': '#8B0000',
    'BloodStoneBrick': '#4A0000',
    'RitualStone': '#2D2D2D',
    'SpeedRune': '#6B0000',
    'BlankRune': '#5C0000',
    'WaterRitualStone': '#1E3A5F',
    'FireRitualStone': '#8B4513',
}

def round_to_grid(value, segments=16):
    """Zaokrągla wartość do siatki o podanej liczbie segmentów."""
    return round(value * segments) / segments

def calculate_cut_plane_grid(normal, segments=16):
    """
    Oblicza płaszczyznę cięcia zaokrągloną do siatki 16x16.
    Zwraca: (nx, ny, nz, offset) gdzie offset to przesunięcie od środka
    """
    nx, ny, nz = normal
    
    # Zaokrąglij wektor normalny do najbliższego kierunku na siatce
    # Najpierw znajdź主导方向
    abs_n = [abs(nx), abs(ny), abs(nz)]
    max_idx = abs_n.index(max(abs_n))
    
    # Zaokrąglij komponenty do wartości na siatce
    nx_grid = round_to_grid(nx, segments)
    ny_grid = round_to_grid(ny, segments)
    nz_grid = round_to_grid(nz, segments)
    
    # Jeśli wszystkie są bliskie 0, ustaw domyślnie Y
    if abs(nx_grid) < 0.001 and abs(ny_grid) < 0.001 and abs(nz_grid) < 0.001:
        ny_grid = 1.0
    
    # Normalizuj
    length = np.sqrt(nx_grid**2 + ny_grid**2 + nz_grid**2)
    if length > 0:
        nx_grid /= length
        ny_grid /= length
        nz_grid /= length
    
    return (nx_grid, ny_grid, nz_grid)

def get_intersection_points_grid(nx, ny, nz, keep_positive, segments=16):
    """
    Znajduje punkty przecięcia płaszczyzny z krawędziami sześcianu.
    Punkty są zaokrąglane do siatki 16x16.
    """
    # Środek sześcianu
    cx, cy, cz = 0.5, 0.5, 0.5
    
    # Równanie płaszczyzny: nx*(x-cx) + ny*(y-cy) + nz*(z-cz) = 0
    # czyli: nx*x + ny*y + nz*z = nx*cx + ny*cy + nz*cz = d
    d = nx * cx + ny * cy + nz * cz
    
    points = []
    
    # Sprawdź wszystkie 12 krawędzi sześcianu [0,1]x[0,1]x[0,1]
    # Krawędzie równoległe do X (4 sztuki): (t, 0, 0), (t, 0, 1), (t, 1, 0), (t, 1, 1)
    for y in [0.0, 1.0]:
        for z in [0.0, 1.0]:
            if abs(nx) > 0.001:
                t = (d - ny * y - nz * z) / nx
                t_grid = round_to_grid(t, segments)
                if 0 <= t_grid <= 1:
                    points.append((t_grid, y, z))
    
    # Krawędzie równoległe do Y (4 sztuki): (0, t, 0), (0, t, 1), (1, t, 0), (1, t, 1)
    for x in [0.0, 1.0]:
        for z in [0.0, 1.0]:
            if abs(ny) > 0.001:
                t = (d - nx * x - nz * z) / ny
                t_grid = round_to_grid(t, segments)
                if 0 <= t_grid <= 1:
                    points.append((x, t_grid, z))
    
    # Krawędzie równoległe do Z (4 sztuki): (0, 0, t), (0, 1, t), (1, 0, t), (1, 1, t)
    for x in [0.0, 1.0]:
        for y in [0.0, 1.0]:
            if abs(nz) > 0.001:
                t = (d - nx * x - ny * y) / nz
                t_grid = round_to_grid(t, segments)
                if 0 <= t_grid <= 1:
                    points.append((x, y, t_grid))
    
    # Usuń duplikaty
    unique_points = []
    seen = set()
    for p in points:
        key = (round(p[0], 3), round(p[1], 3), round(p[2], 3))
        if key not in seen:
            seen.add(key)
            unique_points.append(p)
    
    return unique_points

def create_cut_block_faces(nx, ny, nz, keep_positive, segments=16):
    """
    Tworzy ściany przyciętego bloku.
    Zwraca listę wielokątów (każdy wielokąt to lista wierzchołków).
    """
    cx, cy, cz = 0.5, 0.5, 0.5
    
    # Wierzchołki sześcianu
    vertices = [
        (0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),  # dolna ściana (z=0)
        (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1),  # górna ściana (z=1)
    ]
    
    # Punkty przecięcia
    cut_points = get_intersection_points_grid(nx, ny, nz, keep_positive, segments)
    
    if len(cut_points) < 3:
        # Za mało punktów - zwróć pełny sześcian lub nic
        if keep_positive:
            return create_full_cube_faces()
        else:
            return []
    
    # Zdecyduj które wierzchołki zachować
    kept_vertices = []
    for v in vertices:
        # Odległość od płaszczyzny
        dist = nx * (v[0] - cx) + ny * (v[1] - cy) + nz * (v[2] - cz)
        if keep_positive:
            if dist >= -0.001:
                kept_vertices.append(v)
        else:
            if dist <= 0.001:
                kept_vertices.append(v)
    
    # Stwórz ściany
    faces = []
    
    # Ściana dolna (z=0)
    face = create_face_for_z_level(0, kept_vertices, cut_points, keep_positive, nx, ny, nz, cx, cy, cz)
    if face:
        faces.append(face)
    
    # Ściana górna (z=1)
    face = create_face_for_z_level(1, kept_vertices, cut_points, keep_positive, nx, ny, nz, cx, cy, cz)
    if face:
        faces.append(face)
    
    # Ściana przednia (y=0)
    face = create_face_for_y_level(0, kept_vertices, cut_points, keep_positive, nx, ny, nz, cx, cy, cz)
    if face:
        faces.append(face)
    
    # Ściana tylna (y=1)
    face = create_face_for_y_level(1, kept_vertices, cut_points, keep_positive, nx, ny, nz, cx, cy, cz)
    if face:
        faces.append(face)
    
    # Ściana lewa (x=0)
    face = create_face_for_x_level(0, kept_vertices, cut_points, keep_positive, nx, ny, nz, cx, cy, cz)
    if face:
        faces.append(face)
    
    # Ściana prawa (x=1)
    face = create_face_for_x_level(1, kept_vertices, cut_points, keep_positive, nx, ny, nz, cx, cy, cz)
    if face:
        faces.append(face)
    
    # Ściana cięcia (wielokąt z punktów przecięcia)
    if len(cut_points) >= 3:
        # Posortuj punkty wokół centroidu
        centroid = np.mean(cut_points, axis=0)
        
        # Projekcja na płaszczyznę prostopadłą do normalnej
        if abs(nz) > 0.9:
            # Głównie Z - sortuj po kącie w XY
            sorted_points = sorted(cut_points, key=lambda p: np.arctan2(p[1]-centroid[1], p[0]-centroid[0]))
        elif abs(ny) > 0.9:
            # Głównie Y - sortuj po kącie w XZ
            sorted_points = sorted(cut_points, key=lambda p: np.arctan2(p[2]-centroid[2], p[0]-centroid[0]))
        else:
            # Głównie X - sortuj po kącie w YZ
            sorted_points = sorted(cut_points, key=lambda p: np.arctan2(p[2]-centroid[2], p[1]-centroid[1]))
        
        faces.append(sorted_points)
    
    return faces

def create_face_for_z_level(z_level, kept_vertices, cut_points, keep_positive, nx, ny, nz, cx, cy, cz):
    """Tworzy ścianę dla poziomu Z (z=0 lub z=1)."""
    # Znajdź wierzchołki na tym poziomie
    vertices_at_z = [v for v in kept_vertices if abs(v[2] - z_level) < 0.001]
    points_at_z = [p for p in cut_points if abs(p[2] - z_level) < 0.001]
    
    all_points = vertices_at_z + points_at_z
    
    if len(all_points) < 3:
        return None
    
    # Posortuj punkty wokół centroidu (w płaszczyźnie XY)
    centroid = np.mean(all_points, axis=0)
    sorted_points = sorted(all_points, key=lambda p: np.arctan2(p[1]-centroid[1], p[0]-centroid[0]))
    
    return sorted_points

def create_face_for_y_level(y_level, kept_vertices, cut_points, keep_positive, nx, ny, nz, cx, cy, cz):
    """Tworzy ścianę dla poziomu Y (y=0 lub y=1)."""
    vertices_at_y = [v for v in kept_vertices if abs(v[1] - y_level) < 0.001]
    points_at_y = [p for p in cut_points if abs(p[1] - y_level) < 0.001]
    
    all_points = vertices_at_y + points_at_y
    
    if len(all_points) < 3:
        return None
    
    centroid = np.mean(all_points, axis=0)
    sorted_points = sorted(all_points, key=lambda p: np.arctan2(p[2]-centroid[2], p[0]-centroid[0]))
    
    return sorted_points

def create_face_for_x_level(x_level, kept_vertices, cut_points, keep_positive, nx, ny, nz, cx, cy, cz):
    """Tworzy ścianę dla poziomu X (x=0 lub x=1)."""
    vertices_at_x = [v for v in kept_vertices if abs(v[0] - x_level) < 0.001]
    points_at_x = [p for p in cut_points if abs(p[0] - x_level) < 0.001]
    
    all_points = vertices_at_x + points_at_x
    
    if len(all_points) < 3:
        return None
    
    centroid = np.mean(all_points, axis=0)
    sorted_points = sorted(all_points, key=lambda p: np.arctan2(p[2]-centroid[2], p[1]-centroid[1]))
    
    return sorted_points

def create_full_cube_faces():
    """Tworzy ściany pełnego sześcianu."""
    return [
        [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],  # dolna
        [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],  # górna
        [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)],  # przednia
        [(0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)],  # tylna
        [(0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)],  # lewa
        [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)],  # prawa
    ]

def add_cut_plane_visual(ax, nx, ny, nz, segments=16, alpha=0.2):
    """Dodaje wizualizację płaszczyzny cięcia."""
    cx, cy, cz = 0.5, 0.5, 0.5
    
    # Wektory bazowe płaszczyzny
    if abs(nz) > 0.9:
        u = [1, 0, 0]
        v = [0, 1, 0]
    elif abs(ny) > 0.9:
        u = [1, 0, 0]
        v = [0, 0, 1]
    else:
        u = [0, 1, 0]
        v = [0, 0, 1]
    
    # Utwórz siatkę punktów na płaszczyźnie
    t = np.linspace(-0.7, 0.7, 10)
    T1, T2 = np.meshgrid(t, t)
    
    X = cx + u[0] * T1 + v[0] * T2
    Y = cy + u[1] * T1 + v[1] * T2
    Z = cz + u[2] * T1 + v[2] * T2
    
    ax.plot_surface(X, Y, Z, alpha=alpha, color='cyan', edgecolor='blue', linewidth=0.3)

def plot_cut_block_v2(ax, x, y, z, normal, keep_positive, title, texture_color='#8B0000', segments=16):
    """Rysuje przycięty blok wersja 2 - faktycznie przycięty!"""
    
    # Zaokrąglij płaszczyznę do siatki
    nx, ny, nz = calculate_cut_plane_grid(normal, segments)
    
    # Pobierz ściany przyciętego bloku
    faces = create_cut_block_faces(nx, ny, nz, keep_positive, segments)
    
    if not faces:
        ax.text(x + 0.5, y + 0.5, z + 0.5, 'EMPTY', ha='center', fontsize=8)
        return
    
    # Przesuń ściany o pozycję bloku
    translated_faces = []
    for face in faces:
        translated_face = [(p[0] + x, p[1] + y, p[2] + z) for p in face]
        translated_faces.append(translated_face)
    
    # Rysuj ściany
    face_collection = Poly3DCollection(translated_faces, alpha=0.9, 
                                        facecolor=texture_color, 
                                        edgecolor='black', linewidth=0.5)
    ax.add_collection3d(face_collection)
    
    # Dodaj płaszczyznę cięcia (przezroczysta)
    add_cut_plane_visual(ax, nx, ny, nz, segments, alpha=0.15)
    
    # Dodaj wektor normalny (żółta strzałka)
    scale = 0.4
    ax.quiver(x + 0.5, y + 0.5, z + 0.5, 
              nx * scale, ny * scale, nz * scale,
              color='yellow', arrow_length_ratio=0.2, linewidth=2)
    
    # Dodaj siatkę 16x16 (pomocniczo)
    # draw_grid_16x16(ax, x, y, z)
    
    ax.set_xlim(x - 0.2, x + 1.2)
    ax.set_ylim(y - 0.2, y + 1.2)
    ax.set_zlim(z - 0.2, z + 1.2)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title, fontsize=10, fontweight='bold')
    ax.set_box_aspect([1, 1, 1])

def draw_grid_16x16(ax, x, y, z):
    """Rysuje siatkę 16x16 na ścianach bloku (pomocniczo)."""
    color = 'gray'
    alpha = 0.2
    linewidth = 0.3
    
    # Linie na ścianach X (x i x+1)
    for i in range(17):
        pos = y + i / 16
        ax.plot([x, x], [pos, pos], [z, z + 1], color=color, alpha=alpha, linewidth=linewidth)
        ax.plot([x + 1, x + 1], [pos, pos], [z, z + 1], color=color, alpha=alpha, linewidth=linewidth)
    
    for i in range(17):
        pos = z + i / 16
        ax.plot([x, x], [y, y + 1], [pos, pos], color=color, alpha=alpha, linewidth=linewidth)
        ax.plot([x + 1, x + 1], [y, y + 1], [pos, pos], color=color, alpha=alpha, linewidth=linewidth)
    
    # Linie na ścianach Y
    for i in range(17):
        pos = x + i / 16
        ax.plot([pos, pos], [y, y], [z, z + 1], color=color, alpha=alpha, linewidth=linewidth)
        ax.plot([pos, pos], [y + 1, y + 1], [z, z + 1], color=color, alpha=alpha, linewidth=linewidth)
    
    # Linie na ścianach Z
    for i in range(17):
        pos = x + i / 16
        ax.plot([pos, pos], [y, y + 1], [z, z], color=color, alpha=alpha, linewidth=linewidth)
        ax.plot([pos, pos], [y, y + 1], [z + 1, z + 1], color=color, alpha=alpha, linewidth=linewidth)

def create_test_visualization_v2():
    """Tworzy główną wizualizację v2 z faktycznie przyciętymi blokami."""
    
    fig = plt.figure(figsize=(18, 12))
    fig.suptitle('Cuttable Blocks v2 - Przycięte bloki z siatką 16x16', 
                 fontsize=14, fontweight='bold', y=0.98)
    
    # Przypadki testowe z różnymi typami cięcia (zaokrąglone do siatki 16)
    test_cases = [
        # (normal, keep_positive, title, color)
        # Cięcia poziome (różne poziomy)
        ([0, 1, 0], True, 'Cięcie poziome Y+\n(top 8/16)', 'BloodAltar_Top'),
        ([0, -1, 0], False, 'Cięcie poziome Y-\n(bottom 4/16)', 'BloodAltar_Top'),
        ([0, 0.5, 0], True, 'Cięcie poziome\n(custom 12/16)', 'BloodStoneBrick'),
        
        # Cięcia pionowe X
        ([1, 0, 0], True, 'Cięcie X+\n(east 8/16)', 'BloodStoneBrick'),
        ([-0.5, 0, 0], False, 'Cięcie X-\n(west 12/16)', 'RitualStone'),
        
        # Cięcia pionowe Z
        ([0, 0, 1], True, 'Cięcie Z+\n(south 6/16)', 'RitualStone'),
        ([0, 0, -0.7], False, 'Cięcie Z-\n(north 10/16)', 'SpeedRune'),
        
        # Cięcia diagonalne
        ([0.5, 0.5, 0], True, 'Diag X+Y+\n(ukos 1)', 'BlankRune'),
        ([-0.5, 0.5, 0.3], True, 'Diag X-Y+Z+\n(ukos 2)', 'WaterRitualStone'),
        ([0.3, 0.7, -0.3], False, 'Diag custom\n(ukos 3)', 'FireRitualStone'),
        ([0.8, 0.3, 0.2], True, 'Diag custom\n(ukos 4)', 'BloodAltar_Top'),
    ]
    
    positions = [(i // 5, i % 5) for i in range(10)]
    
    for i, ((row, col), (normal, keep_pos, title, texture_key)) in enumerate(zip(positions, test_cases)):
        ax = fig.add_subplot(2, 5, i + 1, projection='3d')
        
        color = TEXTURE_COLORS.get(texture_key, '#8B0000')
        plot_cut_block_v2(ax, 0, 0, 0, normal, keep_pos, title, color, segments=16)
        
        ax.view_init(elev=20, azim=45)
    
    plt.tight_layout()
    plt.savefig('test_cases_3d_v2.png', dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.savefig('test_cases_3d_v2.svg', bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print("Zapisano: test_cases_3d_v2.png, test_cases_3d_v2.svg")
    plt.close()

def create_grid_demonstration():
    """Demonstruje zaokrąglanie do siatki 16x16."""
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Zaokrąglanie do siatki 16x16 (pikseli tekstury)', fontsize=14, fontweight='bold')
    
    # Przykłady różnych cięć z siatką
    examples = [
        ([0, 0.33, 0], True, 'Cięcie na 5/16 (Y=0.3125)'),
        ([0, 0.67, 0], True, 'Cięcie na 11/16 (Y=0.6875)'),
        ([0.25, 0, 0], True, 'Cięcie na 4/16 (X=0.25)'),
        ([0.75, 0, 0], True, 'Cięcie na 12/16 (X=0.75)'),
        ([0, 0, 0.5], True, 'Cięcie na 8/16 (Z=0.5)'),
        ([0.3, 0.6, 0], True, 'Cięcie diagonalne (zaokrąglone)'),
    ]
    
    for idx, (normal, keep_pos, title) in enumerate(examples):
        ax = axes[idx // 3, idx % 3]
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.set_title(title, fontweight='bold')
        
        # Rysuj siatkę 16x16
        for i in range(17):
            pos = i / 16
            ax.axhline(y=pos, color='lightgray', linewidth=0.5, alpha=0.5)
            ax.axvline(x=pos, color='lightgray', linewidth=0.5, alpha=0.5)
        
        # Zaokrąglij normalną
        nx, ny, nz = calculate_cut_plane_grid(normal, 16)
        
        # Oblicz punkt cięcia na krawędzi
        if abs(ny) > abs(nx) and abs(ny) > abs(nz):
            # Cięcie poziome
            d = nx * 0.5 + ny * 0.5 + nz * 0.5
            if abs(ny) > 0.001:
                cut_y = (d - nx * 0.5 - nz * 0.5) / ny
                cut_y_grid = round_to_grid(cut_y, 16)
                ax.axhline(y=cut_y_grid, color='red', linewidth=3, label=f'Y={cut_y_grid:.4f}')
                ax.fill_between([0, 1], [cut_y_grid, cut_y_grid], [1, 1], alpha=0.3, color='darkred')
        elif abs(nx) > abs(nz):
            # Cięcie pionowe X
            d = nx * 0.5 + ny * 0.5 + nz * 0.5
            if abs(nx) > 0.001:
                cut_x = (d - ny * 0.5 - nz * 0.5) / nx
                cut_x_grid = round_to_grid(cut_x, 16)
                ax.axvline(x=cut_x_grid, color='blue', linewidth=3, label=f'X={cut_x_grid:.4f}')
                ax.fill_betweenx([0, 1], [cut_x_grid, cut_x_grid], [1, 1], alpha=0.3, color='darkblue')
        
        ax.legend(loc='lower right', fontsize=8)
        ax.set_xlabel('X')
        ax.set_ylabel('Y/Z')
    
    plt.tight_layout()
    plt.savefig('grid_demonstration.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("Zapisano: grid_demonstration.png")
    plt.close()

def create_comparison():
    """Porównanie cięć z różnymi ustawieniami siatki."""
    
    fig = plt.figure(figsize=(16, 6))
    fig.suptitle('Porównanie: bez zaokrąglenia vs siatka 16x16', fontsize=14, fontweight='bold')
    
    # Ten sam kierunek, różne zaokrąglenia
    normal = [0.3, 0.7, 0.1]
    
    # Bez zaokrąglenia
    ax1 = fig.add_subplot(1, 3, 1, projection='3d')
    plot_cut_block_v2(ax1, 0, 0, 0, normal, True, 'Bez zaokrąglenia\n(raw normal)', '#8B0000', segments=1000)
    ax1.view_init(elev=20, azim=45)
    
    # Siatka 16x16
    ax2 = fig.add_subplot(1, 3, 2, projection='3d')
    plot_cut_block_v2(ax2, 0, 0, 0, normal, True, 'Siatka 16x16\n(zaokrąglone)', '#8B0000', segments=16)
    ax2.view_init(elev=20, azim=45)
    
    # Siatka 8x8 (grubsze cięcia)
    ax3 = fig.add_subplot(1, 3, 3, projection='3d')
    plot_cut_block_v2(ax3, 0, 0, 0, normal, True, 'Siatka 8x8\n(bardziej zaokrąglone)', '#8B0000', segments=8)
    ax3.view_init(elev=20, azim=45)
    
    plt.tight_layout()
    plt.savefig('comparison_grid.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("Zapisano: comparison_grid.png")
    plt.close()

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("Generowanie wizualizacji 3D v2...")
    create_test_visualization_v2()
    create_grid_demonstration()
    create_comparison()
    print("\nWszystkie wizualizacje zapisane!")
