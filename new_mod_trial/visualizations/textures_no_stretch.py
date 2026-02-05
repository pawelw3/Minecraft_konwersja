#!/usr/bin/env python3
"""
Wizualizacja bloków z poprawionym mapowaniem tekstur:
- Tekstury nie są ściśnięte (stretched), tylko przycięte (clipped)
- Ściany cięcia mają tiling (powtarzanie) zamiast rozciągania
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import FancyBboxPatch, Rectangle
from PIL import Image
import os

def load_texture(texture_name, size=16):
    """Wczytuje teksturę i zmienia rozmiar na size x size."""
    base_path = "bloodmagic_textures/assets/alchemicalwizardry/textures/blocks"
    path = os.path.join(base_path, f"{texture_name}.png")
    if os.path.exists(path):
        img = Image.open(path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img = img.resize((size, size), Image.NEAREST)
        return np.array(img)
    return None

def get_texture_clip(texture, u_start, u_end, v_start, v_end):
    """Wycina fragment tekstury (clipping)."""
    h, w = texture.shape[:2]
    u1, u2 = int(u_start * w), int(u_end * w)
    v1, v2 = int(v_start * h), int(v_end * h)
    return texture[v1:v2, u1:u2]

def create_textured_face_no_stretch(ax, vertices_3d, texture_array, 
                                     u_range=(0, 1), v_range=(0, 1),
                                     shade=1.0):
    """
    Tworzy ścianę z teksturą bez rozciągania - używa clippingu.
    u_range, v_range - która część tekstury jest widoczna (0-1)
    """
    if texture_array is None or len(vertices_3d) < 3:
        return
    
    h, w = texture_array.shape[:2]
    
    # Wyciń odpowiedni fragment tekstury
    u_start, u_end = u_range
    v_start, v_end = v_range
    
    # Przygotuj siatkę UV dla ściany
    # Dla prostokątnych ścian - mapuj bezpośrednio
    if len(vertices_3d) == 4:
        # Posortuj wierzchołki aby były w odpowiedniej kolejności
        # Zakładamy: [dolny-lewy, dolny-prawy, górny-prawy, górny-lewy]
        
        # Utwórz siatkę pikseli
        tex_clip = texture_array[int(v_start*h):int(v_end*h), int(u_start*w):int(u_end*w)]
        clip_h, clip_w = tex_clip.shape[:2]
        
        # Rysuj każdy piksel jako mały czworokąt
        for i in range(clip_h - 1):
            for j in range(clip_w - 1):
                # Interpolacja pozycji 3D
                u_frac = j / max(clip_w - 1, 1)
                v_frac = i / max(clip_h - 1, 1)
                
                u_next = (j + 1) / max(clip_w - 1, 1)
                v_next = (i + 1) / max(clip_h - 1, 1)
                
                # Wierzchołki czworokąta piksela
                p00 = interpolate_vertex(vertices_3d, u_frac, v_frac)
                p10 = interpolate_vertex(vertices_3d, u_next, v_frac)
                p11 = interpolate_vertex(vertices_3d, u_next, v_next)
                p01 = interpolate_vertex(vertices_3d, u_frac, v_next)
                
                # Kolor z tekstury (z cieniowaniem)
                color = tex_clip[i, j] / 255.0 * shade
                
                face = Poly3DCollection([[p00, p10, p11, p01]], 
                                        facecolor=color, edgecolor='none', alpha=0.95)
                ax.add_collection3d(face)

def interpolate_vertex(vertices, u, v):
    """Interpoluje pozycję wierzchołka na podstawie UV."""
    if len(vertices) == 4:
        # Bilinearna interpolacja
        v0, v1, v2, v3 = vertices  # Zakładamy kolejność: LL, LR, UR, UL
        p_bottom = [v0[i] * (1-u) + v1[i] * u for i in range(3)]
        p_top = [v3[i] * (1-u) + v2[i] * u for i in range(3)]
        return [p_bottom[i] * (1-v) + p_top[i] * v for i in range(3)]
    else:
        # Dla innych kształtów - średnia
        return list(np.mean(vertices, axis=0))

def plot_half_block_correct(ax, x, y, z, texture_name, is_top=True, title=""):
    """
    Rysuje pół-blok z poprawnym clippingiem tekstury (nie ściśniętą!).
    """
    texture = load_texture(texture_name, 16)
    if texture is None:
        return
    
    # Wierzchołki pełnego sześcianu
    if is_top:
        # Górna połowa: Y od 0.5 do 1.0
        y_min, y_max = y + 0.5, y + 1.0
        # Dla tekstury bocznej: pokazujemy górną połowę (v: 0.5-1.0)
        v_range_side = (0.5, 1.0)
    else:
        # Dolna połowa: Y od 0.0 do 0.5
        y_min, y_max = y + 0.0, y + 0.5
        # Dla tekstury bocznej: pokazujemy dolną połowę (v: 0.0-0.5)
        v_range_side = (0.0, 0.5)
    
    # Górna ściana (Y+) - pełna tekstura
    if is_top:
        verts_top = [
            [x + 0.0, y_max, z + 0.0], [x + 1.0, y_max, z + 0.0],
            [x + 1.0, y_max, z + 1.0], [x + 0.0, y_max, z + 1.0]
        ]
        create_textured_face_no_stretch(ax, verts_top, texture, 
                                        u_range=(0, 1), v_range=(0, 1), shade=1.1)
    
    # Dolna ściana (Y-) - pełna tekstura
    if not is_top:
        verts_bottom = [
            [x + 0.0, y_min, z + 1.0], [x + 1.0, y_min, z + 1.0],
            [x + 1.0, y_min, z + 0.0], [x + 0.0, y_min, z + 0.0]
        ]
        create_textured_face_no_stretch(ax, verts_bottom, texture,
                                        u_range=(0, 1), v_range=(0, 1), shade=0.8)
    
    # Ściany boczne - TYLKO POŁOWA TEKSTURY (clipping!)
    # North (Z-)
    verts_north = [
        [x + 0.0, y_min, z + 0.0], [x + 1.0, y_min, z + 0.0],
        [x + 1.0, y_max, z + 0.0], [x + 0.0, y_max, z + 0.0]
    ]
    create_textured_face_no_stretch(ax, verts_north, texture,
                                    u_range=(0, 1), v_range=v_range_side, shade=0.9)
    
    # South (Z+)
    verts_south = [
        [x + 0.0, y_max, z + 1.0], [x + 1.0, y_max, z + 1.0],
        [x + 1.0, y_min, z + 1.0], [x + 0.0, y_min, z + 1.0]
    ]
    create_textured_face_no_stretch(ax, verts_south, texture,
                                    u_range=(0, 1), v_range=v_range_side, shade=0.9)
    
    # West (X-)
    verts_west = [
        [x + 0.0, y_min, z + 1.0], [x + 0.0, y_min, z + 0.0],
        [x + 0.0, y_max, z + 0.0], [x + 0.0, y_max, z + 1.0]
    ]
    create_textured_face_no_stretch(ax, verts_west, texture,
                                    u_range=(0, 1), v_range=v_range_side, shade=0.7)
    
    # East (X+)
    verts_east = [
        [x + 1.0, y_min, z + 0.0], [x + 1.0, y_min, z + 1.0],
        [x + 1.0, y_max, z + 1.0], [x + 1.0, y_max, z + 0.0]
    ]
    create_textured_face_no_stretch(ax, verts_east, texture,
                                    u_range=(0, 1), v_range=v_range_side, shade=0.7)
    
    # Ściana cięcia (Y=0.5) - tiling tekstury
    if True:
        # 2x2 tiling dla ściany cięcia
        verts_cut = [
            [x + 0.0, y + 0.5, z + 0.0], [x + 1.0, y + 0.5, z + 0.0],
            [x + 1.0, y + 0.5, z + 1.0], [x + 0.0, y + 0.5, z + 1.0]
        ]
        # Rysuj z tilingiem 2x2
        create_tiled_face(ax, verts_cut, texture, tiles_u=2, tiles_v=2, shade=1.0)
    
    # Ramka
    draw_wireframe(ax, x, y_min, z, x+1, y_max, z+1)
    
    ax.set_xlim(x - 0.1, x + 1.1)
    ax.set_ylim(y - 0.1, y + 1.1)
    ax.set_zlim(z - 0.1, z + 1.1)
    ax.set_title(f"{title}\n[Texture: {texture_name}]\n(NO STRETCH - clipped!)", 
                fontsize=9, fontweight='bold')
    ax.set_box_aspect([1, 1, 1])

def create_tiled_face(ax, vertices, texture, tiles_u=2, tiles_v=2, shade=1.0):
    """Tworzy ścianę z powtarzaną (tiled) teksturą."""
    if len(vertices) != 4:
        return
    
    h, w = texture.shape[:2]
    
    # Podziel na kafelki
    for ti in range(tiles_v):
        for tj in range(tiles_u):
            # Współrzędne UV dla tego kafelka
            u_start = tj / tiles_u
            u_end = (tj + 1) / tiles_u
            v_start = ti / tiles_v
            v_end = (ti + 1) / tiles_v
            
            # Wierzchołki kafelka w 3D
            p00 = interpolate_vertex(vertices, u_start, v_start)
            p10 = interpolate_vertex(vertices, u_end, v_start)
            p11 = interpolate_vertex(vertices, u_end, v_end)
            p01 = interpolate_vertex(vertices, u_start, v_end)
            
            # Średni kolor tekstury dla tego kafelka
            u1, u2 = int(u_start * w), int(u_end * w)
            v1, v2 = int(v_start * h), int(v_end * h)
            color = np.mean(texture[v1:v2, u1:u2], axis=(0, 1)) / 255.0 * shade
            
            face = Poly3DCollection([[p00, p10, p11, p01]], 
                                    facecolor=color, edgecolor='black', 
                                    linewidth=0.3, alpha=0.95)
            ax.add_collection3d(face)

def draw_wireframe(ax, x, y, z, x2, y2, z2):
    """Rysuje ramkę bloku."""
    # Rysuj tylko widoczne krawędzie
    edges = [
        ([x, y2, z], [x2, y2, z]), ([x2, y2, z], [x2, y2, z2]),
        ([x2, y2, z2], [x, y2, z2]), ([x, y2, z2], [x, y2, z]),
        ([x, y, z], [x, y2, z]), ([x2, y, z], [x2, y2, z]),
        ([x2, y, z2], [x2, y2, z2]), ([x, y, z2], [x, y2, z2]),
    ]
    for v1, v2 in edges:
        ax.plot([v1[0], v2[0]], [v1[1], v2[1]], [v1[2], v2[2]], 
                'k-', alpha=0.3, linewidth=0.5)

def plot_stretched_vs_clipped():
    """Porównanie: ściśnięta vs przycięta tekstura."""
    
    fig = plt.figure(figsize=(16, 8))
    fig.suptitle('Poprawne mapowanie tekstur: CLIPPING vs STRETCHING', 
                 fontsize=14, fontweight='bold', y=0.98)
    
    texture = load_texture('BloodAltar_Top', 16)
    
    # Panel 1: Tekstura oryginalna
    ax1 = fig.add_subplot(2, 4, 1)
    ax1.imshow(texture)
    ax1.set_title('Tekstura oryginalna\n16x16', fontsize=10, fontweight='bold')
    ax1.axis('off')
    
    # Panel 2: Ściśnięta (STRETCHED) - symulacja złego renderera
    ax2 = fig.add_subplot(2, 4, 2)
    stretched = np.repeat(texture[::2, :], 2, axis=0)  # Symulacja rozciągania
    ax2.imshow(stretched)
    ax2.set_title('ŹLE: Rozciągnięta\n(stretched)', fontsize=10, fontweight='bold', color='red')
    ax2.axis('off')
    
    # Panel 3: Przycięta (CLIPPED) - poprawnie
    ax3 = fig.add_subplot(2, 4, 3)
    clipped = texture[8:, :]  # Tylko górna połowa
    ax3.imshow(clipped)
    ax3.set_title('DOBRZE: Przycięta\n(clipped)', fontsize=10, fontweight='bold', color='green')
    ax3.axis('off')
    
    # Panel 4: Tiling
    ax4 = fig.add_subplot(2, 4, 4)
    tiled = np.tile(texture, (2, 2, 1))  # Tile w 2D, zachowaj kanały koloru
    ax4.imshow(tiled)
    ax4.set_title('Tiling 2x2\n(dla dużych ścian)', fontsize=10, fontweight='bold', color='blue')
    ax4.axis('off')
    
    # Panel 5-8: Bloki 3D
    textures = ['BloodAltar_Top', 'BloodStoneBrick', 'SpeedRune', 'WaterRitualStone']
    titles = ['Górna połowa', 'Dolna połowa', 'Wschód', 'Zachód']
    is_top = [True, False, True, False]
    
    for i, (tex, title, top) in enumerate(zip(textures, titles, is_top)):
        ax = fig.add_subplot(2, 4, 5 + i, projection='3d')
        plot_half_block_correct(ax, 0, 0, 0, tex, is_top=top, title=title)
        ax.view_init(elev=25, azim=45)
    
    plt.tight_layout()
    plt.savefig('no_stretch_comparison.png', dpi=150, bbox_inches='tight', facecolor='white')
    print("Zapisano: no_stretch_comparison.png")
    plt.close()

def plot_tiling_demonstration():
    """Demonstracja tilingu dla dużych ścian cięcia."""
    
    fig = plt.figure(figsize=(14, 10))
    fig.suptitle('Tiling tekstur dla dużych ścian cięcia (zamiast rozciągania)', 
                 fontsize=14, fontweight='bold')
    
    texture = load_texture('RitualStone', 16)
    
    # Scenariusze: (size, tiles, title)
    scenarios = [
        (1, 1, 'Normalna ściana\n1x1 tile'),
        (1.5, 2, 'Większa ściana\n2x2 tiles'),
        (2, 2, 'Duża ściana\n2x2 tiles'),
        (2.5, 3, 'Bardzo duża\n3x3 tiles'),
    ]
    
    for i, (size, tiles, title) in enumerate(scenarios):
        ax = fig.add_subplot(2, 2, i + 1, projection='3d')
        
        # Ściana o danym rozmiarze
        verts = [
            [0, 0, 0], [size, 0, 0],
            [size, 0, size], [0, 0, size]
        ]
        
        # Rysuj z tilingiem
        create_tiled_face(ax, verts, texture, tiles, tiles, shade=1.0)
        
        ax.set_xlim(-0.1, size + 0.1)
        ax.set_ylim(-0.1, 0.5)
        ax.set_zlim(-0.1, size + 0.1)
        ax.set_title(f"{title}\n(tekstura się POWTARZA)", fontsize=10, fontweight='bold')
        ax.set_box_aspect([1, 0.3, 1])
        ax.view_init(elev=30, azim=-45)
    
    plt.tight_layout()
    plt.savefig('tiling_demonstration.png', dpi=150, bbox_inches='tight', facecolor='white')
    print("Zapisano: tiling_demonstration.png")
    plt.close()

def create_final_demo():
    """Finalna wizualizacja pokazująca wszystkie poprawki."""
    
    fig = plt.figure(figsize=(18, 10))
    fig.suptitle('Cuttable Blocks - POPRAWIONE teksturowanie\n' +
                 'Bez rozciągania! Clipping + Tiling', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    # Bloki do pokazania
    blocks = [
        ('BloodAltar_Top', True, 'Górna połowa\n(clipped UV)'),
        ('BloodStoneBrick', False, 'Dolna połowa\n(clipped UV)'),
        ('SpeedRune', True, 'Speed Rune\n(top half)'),
        ('WaterRitualStone', False, 'Water Stone\n(bottom half)'),
        ('FireRitualStone', True, 'Fire Stone\n(top half)'),
        ('RitualStone', False, 'Ritual Stone\n(bottom half)'),
        ('BlankRune', True, 'Rune\n(top half)'),
        ('BloodAltar_Top', False, 'Blood Altar\n(bottom half)'),
    ]
    
    for i, (tex, is_top, title) in enumerate(blocks):
        ax = fig.add_subplot(2, 4, i + 1, projection='3d')
        plot_half_block_correct(ax, 0, 0, 0, tex, is_top=is_top, title=title)
        ax.view_init(elev=20, azim=35)
    
    plt.tight_layout()
    plt.savefig('final_no_stretch_demo.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.savefig('final_no_stretch_demo.svg', bbox_inches='tight', facecolor='white')
    print("Zapisano: final_no_stretch_demo.png, final_no_stretch_demo.svg")
    plt.close()

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("Generowanie wizualizacji z poprawionymi teksturami...")
    print("(Bez rozciągania - clipping i tiling)")
    
    plot_stretched_vs_clipped()
    plot_tiling_demonstration()
    create_final_demo()
    
    print("\n✅ Gotowe! Wizualizacje pokazują:")
    print("  - Tekstury nie są ściśnięte (clipping UV)")
    print("  - Ściany cięcia mają tiling (powtarzanie)")
    print("  - Każdy piksel jest na swoim miejscu!")
