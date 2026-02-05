#!/usr/bin/env python3
"""
Wizualizacja 3D przypadków testowych cięcia bloków.
Generuje obrazki pokazujące różne scenariusze cięcia.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.patches as mpatches
from PIL import Image
import os

# Wczytaj tekstury z BloodMagic
def load_texture(name):
    path = f"bloodmagic_textures/assets/alchemicalwizardry/textures/blocks/{name}.png"
    if os.path.exists(path):
        return Image.open(path)
    return None

# Kolory tekstur (przybliżone)
TEXTURE_COLORS = {
    'BloodAltar_Top': '#8B0000',      # Ciemna czerwień
    'BloodAltar_SideType1': '#660000', # Bordowy
    'BloodStoneBrick': '#4A0000',     # Ciemny bordowy
    'BlankRune': '#5C0000',           # Rune czerwony
    'RitualStone': '#2D2D2D',         # Ciemny szary
    'SpeedRune': '#6B0000',           # Czerwony rune
    'WaterRitualStone': '#1E3A5F',    # Niebieski
    'FireRitualStone': '#8B4513',     # Pomarańczowy/brązowy
}

def create_cube_faces(x, y, z, size=1.0):
    """Tworzy ściany sześcianu."""
    vertices = [
        [x, y, z],
        [x + size, y, z],
        [x + size, y + size, z],
        [x, y + size, z],
        [x, y, z + size],
        [x + size, y, z + size],
        [x + size, y + size, z + size],
        [x, y + size, z + size]
    ]
    
    faces = [
        [vertices[0], vertices[1], vertices[2], vertices[3]],  # bottom (z)
        [vertices[4], vertices[5], vertices[6], vertices[7]],  # top (z+1)
        [vertices[0], vertices[1], vertices[5], vertices[4]],  # front (y)
        [vertices[2], vertices[3], vertices[7], vertices[6]],  # back (y+1)
        [vertices[0], vertices[3], vertices[7], vertices[4]],  # left (x)
        [vertices[1], vertices[2], vertices[6], vertices[5]],  # right (x+1)
    ]
    return faces

def create_half_cube_faces(x, y, z, normal, keep_positive, size=1.0):
    """Tworzy przycięte ściany sześcianu."""
    nx, ny, nz = normal
    
    # Wszystkie wierzchołki sześcianu
    vertices = np.array([
        [x, y, z],
        [x + size, y, z],
        [x + size, y + size, z],
        [x, y + size, z],
        [x, y, z + size],
        [x + size, y, z + size],
        [x + size, y + size, z + size],
        [x, y + size, z + size]
    ])
    
    # Środek sześcianu
    center = np.array([x + size/2, y + size/2, z + size/2])
    
    # Sprawdź które wierzchołki są po stronie "keep"
    kept_vertices = []
    for v in vertices:
        vec = v - center
        dist = np.dot(vec, normal)
        if keep_positive:
            if dist >= -0.001:  # po stronie dodatniej lub na płaszczyźnie
                kept_vertices.append(v)
        else:
            if dist <= 0.001:  # po stronie ujemnej lub na płaszczyźnie
                kept_vertices.append(v)
    
    kept_vertices = np.array(kept_vertices)
    
    # Dodaj środek dla lepszej wizualizacji
    if len(kept_vertices) > 0:
        kept_vertices = np.vstack([kept_vertices, center])
    
    # Uproszczona wersja - zwracamy pełne ściany ale oznaczamy które są widoczne
    all_faces = create_cube_faces(x, y, z, size)
    
    # Sprawdź które ściany są widoczne (ich środek jest po stronie "keep")
    visible_faces = []
    for face in all_faces:
        face_center = np.mean(face, axis=0)
        vec = face_center - center
        dist = np.dot(vec, normal)
        
        if keep_positive:
            if dist > -0.1:
                visible_faces.append(face)
        else:
            if dist < 0.1:
                visible_faces.append(face)
    
    return visible_faces

def add_cut_plane(ax, x, y, z, normal, size=1.0, alpha=0.3):
    """Dodaje wizualizację płaszczyzny cięcia."""
    nx, ny, nz = normal
    
    # Środek sześcianu
    cx, cy, cz = x + size/2, y + size/2, z + size/2
    
    # Płaszczyzna o równaniu: nx*(x-cx) + ny*(y-cy) + nz*(z-cz) = 0
    # Wektory bazowe płaszczyzny (prostopadłe do normalnej)
    if abs(nx) < 0.9:
        u = np.cross(normal, [1, 0, 0])
    else:
        u = np.cross(normal, [0, 1, 0])
    u = u / np.linalg.norm(u)
    v = np.cross(normal, u)
    v = v / np.linalg.norm(v)
    
    # Punkty płaszczyzny
    t = np.linspace(-size/2, size/2, 10)
    T1, T2 = np.meshgrid(t, t)
    
    X = cx + u[0] * T1 + v[0] * T2
    Y = cy + u[1] * T1 + v[1] * T2
    Z = cz + u[2] * T1 + v[2] * T2
    
    ax.plot_surface(X, Y, Z, alpha=alpha, color='cyan', edgecolor='blue', linewidth=0.5)

def plot_cut_block(ax, x, y, z, normal, keep_positive, title, texture_color='#8B0000'):
    """Rysuje przycięty blok."""
    faces = create_half_cube_faces(x, y, z, normal, keep_positive)
    
    # Rysuj ściany
    face_collection = Poly3DCollection(faces, alpha=0.9, facecolor=texture_color, 
                                        edgecolor='black', linewidth=0.5)
    ax.add_collection3d(face_collection)
    
    # Dodaj płaszczyznę cięcia
    add_cut_plane(ax, x, y, z, normal, alpha=0.2)
    
    # Dodaj wektor normalny
    cx, cy, cz = x + 0.5, y + 0.5, z + 0.5
    scale = 0.6
    ax.quiver(cx, cy, cz, 
              normal[0]*scale, normal[1]*scale, normal[2]*scale,
              color='yellow', arrow_length_ratio=0.2, linewidth=2)
    
    ax.set_xlim(x - 0.2, x + 1.2)
    ax.set_ylim(y - 0.2, y + 1.2)
    ax.set_zlim(z - 0.2, z + 1.2)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title, fontsize=10, fontweight='bold')
    ax.set_box_aspect([1,1,1])

def create_test_visualization():
    """Tworzy główną wizualizację z przypadkami testowymi."""
    
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('Cuttable Blocks - Przypadki Testowe Renderowania 3D', 
                 fontsize=14, fontweight='bold', y=0.98)
    
    # Przypadki testowe: (normal, keep_positive, title, texture)
    test_cases = [
        # 1. Cięcie poziome - górna połowa
        ([0, 1, 0], True, 'Cięcie poziome\n(zachowana góra)', 'BloodAltar_Top'),
        # 2. Cięcie poziome - dolna połowa  
        ([0, -1, 0], False, 'Cięcie poziome\n(zachowana dół)', 'BloodAltar_Top'),
        # 3. Cięcie pionowe X - wschodnia połowa
        ([1, 0, 0], True, 'Cięcie X+\n(zachowana wschód)', 'BloodStoneBrick'),
        # 4. Cięcie pionowe X - zachodnia połowa
        ([-1, 0, 0], False, 'Cięcie X-\n(zachowana zachód)', 'BloodStoneBrick'),
        # 5. Cięcie pionowe Z - południowa połowa
        ([0, 0, 1], True, 'Cięcie Z+\n(zachowana południe)', 'RitualStone'),
        # 6. Cięcie pionowe Z - północna połowa
        ([0, 0, -1], False, 'Cięcie Z-\n(zachowana północ)', 'RitualStone'),
        # 7. Cięcie diagonalne (góra-prawo)
        ([0.5, 0.7, 0.5], True, 'Cięcie diagonalne\n(ukos góra)', 'SpeedRune'),
        # 8. Cięcie diagonalne (dół-lewo)
        ([-0.5, -0.7, -0.5], False, 'Cięcie diagonalne\n(ukos dół)', 'BlankRune'),
    ]
    
    positions = [
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0), (1, 1), (1, 2), (1, 3)
    ]
    
    for i, ((row, col), (normal, keep_pos, title, texture_key)) in enumerate(zip(positions, test_cases)):
        ax = fig.add_subplot(2, 4, i + 1, projection='3d')
        
        color = TEXTURE_COLORS.get(texture_key, '#8B0000')
        plot_cut_block(ax, 0, 0, 0, normal, keep_pos, title, color)
        
        # Ustaw kąt widzenia
        ax.view_init(elev=20, azim=45)
    
    plt.tight_layout()
    plt.savefig('test_cases_3d.png', dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.savefig('test_cases_3d.svg', bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print("Zapisano: test_cases_3d.png, test_cases_3d.svg")
    plt.close()

def create_detailed_view():
    """Tworzy szczegółowy widok jednego bloku z objaśnieniami."""
    
    fig = plt.figure(figsize=(14, 10))
    
    # Główny widok
    ax1 = fig.add_subplot(2, 2, 1, projection='3d')
    normal = [0.5, 0.7, 0.3]
    plot_cut_block(ax1, 0, 0, 0, normal, True, 'Widok 3D - cięcie diagonalne', '#8B0000')
    ax1.view_init(elev=25, azim=45)
    
    # Widok z góry
    ax2 = fig.add_subplot(2, 2, 2, projection='3d')
    plot_cut_block(ax2, 0, 0, 0, [0, 1, 0], True, 'Widok z góry - cięcie poziome', '#660000')
    ax2.view_init(elev=90, azim=0)
    
    # Widok z boku (X)
    ax3 = fig.add_subplot(2, 2, 3, projection='3d')
    plot_cut_block(ax3, 0, 0, 0, [1, 0, 0], True, 'Widok z boku (X) - cięcie pionowe', '#4A0000')
    ax3.view_init(elev=0, azim=0)
    
    # Widok z boku (Z)
    ax4 = fig.add_subplot(2, 2, 4, projection='3d')
    plot_cut_block(ax4, 0, 0, 0, [0, 0, 1], True, 'Widok z boku (Z) - cięcie pionowe', '#5C0000')
    ax4.view_init(elev=0, azim=90)
    
    fig.suptitle('Cuttable Blocks - Szczegółowe widoki cięcia', 
                 fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('detailed_views.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("Zapisano: detailed_views.png")
    plt.close()

def create_algorithm_diagram():
    """Tworzy diagram pokazujący działanie algorytmu."""
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Algorytm Renderowania Cuttable Blocks', fontsize=14, fontweight='bold')
    
    # Krok 1: Oryginalny blok
    ax = axes[0, 0]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    rect = plt.Rectangle((0.1, 0.1), 0.8, 0.8, fill=True, facecolor='#8B0000', 
                          edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    ax.text(0.5, 0.5, 'Blok\noryginalny', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    ax.set_title('Krok 1: Blok oryginalny', fontweight='bold')
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Krok 2: Płaszczyzna cięcia
    ax = axes[0, 1]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    rect = plt.Rectangle((0.1, 0.1), 0.8, 0.8, fill=True, facecolor='#8B0000', 
                          edgecolor='black', linewidth=2, alpha=0.5)
    ax.add_patch(rect)
    # Płaszczyzna
    ax.plot([0.1, 0.9], [0.5, 0.5], 'c-', linewidth=4, label='Płaszczyzna')
    ax.arrow(0.5, 0.5, 0, 0.2, head_width=0.05, head_length=0.05, 
             fc='yellow', ec='yellow', linewidth=2)
    ax.text(0.5, 0.7, 'n', ha='center', fontsize=14, color='yellow', fontweight='bold')
    ax.set_title('Krok 2: Płaszczyzna cięcia', fontweight='bold')
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Krok 3: Punkty przecięcia
    ax = axes[0, 2]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.plot([0.1, 0.1, 0.9, 0.9, 0.1], [0.1, 0.9, 0.9, 0.1, 0.1], 'k--', alpha=0.3)
    # Punkty przecięcia
    ax.plot([0.1, 0.9], [0.5, 0.5], 'ro', markersize=10)
    ax.text(0.1, 0.5, '  P1', fontsize=10, va='center')
    ax.text(0.9, 0.5, 'P2  ', fontsize=10, va='center', ha='right')
    ax.set_title('Krok 3: Punkty przecięcia', fontweight='bold')
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Krok 4: Wybór strony
    ax = axes[1, 0]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    # Górna część
    upper = plt.Polygon([[0.1, 0.5], [0.9, 0.5], [0.9, 0.9], [0.1, 0.9]], 
                        fill=True, facecolor='#8B0000', edgecolor='black', linewidth=2)
    ax.add_patch(upper)
    # Dolna część (przekreślona)
    lower = plt.Polygon([[0.1, 0.1], [0.9, 0.1], [0.9, 0.5], [0.1, 0.5]], 
                        fill=True, facecolor='#330000', edgecolor='black', linewidth=1, alpha=0.3)
    ax.add_patch(lower)
    ax.plot([0.1, 0.9], [0.1, 0.5], 'k--', alpha=0.3)
    ax.plot([0.9, 0.1], [0.1, 0.5], 'k--', alpha=0.3)
    ax.text(0.5, 0.7, 'ZACHOWANA', ha='center', va='center', 
            fontsize=11, fontweight='bold', color='white')
    ax.text(0.5, 0.3, 'USUNIĘTA', ha='center', va='center', 
            fontsize=11, fontweight='bold', color='white', alpha=0.5)
    ax.set_title('Krok 4: Wybór strony', fontweight='bold')
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Krok 5: Renderowanie ścian
    ax = axes[1, 1]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    upper = plt.Polygon([[0.1, 0.5], [0.9, 0.5], [0.9, 0.9], [0.1, 0.9]], 
                        fill=True, facecolor='#8B0000', edgecolor='black', linewidth=2)
    ax.add_patch(upper)
    # Ściana cięcia
    ax.plot([0.1, 0.9], [0.5, 0.5], 'c-', linewidth=4)
    ax.text(0.5, 0.5, 'ŚCIANA CIĘCIA', ha='center', va='bottom', 
            fontsize=9, color='cyan', fontweight='bold')
    ax.set_title('Krok 5: Renderowanie', fontweight='bold')
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Krok 6: Wynik
    ax = axes[1, 2]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    # Przycięty blok z perspektywą
    from matplotlib.patches import FancyBboxPatch
    block = FancyBboxPatch((0.2, 0.3), 0.5, 0.4, boxstyle="round,pad=0.02",
                           fill=True, facecolor='#8B0000', edgecolor='black', linewidth=2)
    ax.add_patch(block)
    top = plt.Polygon([[0.2, 0.7], [0.4, 0.85], [0.9, 0.85], [0.7, 0.7]], 
                      fill=True, facecolor='#AA0000', edgecolor='black', linewidth=2)
    ax.add_patch(top)
    side = plt.Polygon([[0.7, 0.3], [0.9, 0.45], [0.9, 0.85], [0.7, 0.7]], 
                       fill=True, facecolor='#660000', edgecolor='black', linewidth=2)
    ax.add_patch(side)
    ax.text(0.55, 0.5, 'WYNIK', ha='center', va='center', 
            fontsize=14, fontweight='bold', color='white')
    ax.set_title('Krok 6: Wynik końcowy', fontweight='bold')
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('algorithm_diagram.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("Zapisano: algorithm_diagram.png")
    plt.close()

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("Generowanie wizualizacji 3D...")
    create_test_visualization()
    create_detailed_view()
    create_algorithm_diagram()
    print("\nWszystkie wizualizacje zapisane!")
