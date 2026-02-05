#!/usr/bin/env python3
"""
Wizualizacja przyciętych bloków z RZECZYWISTYMI pikselami tekstur BloodMagic.
Każda ściana pokazuje faktyczne piksele 16x16 z tekstury.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.colors import ListedColormap
from PIL import Image
import os

def load_texture(texture_name):
    """Wczytuje teksturę 16x16 z BloodMagic."""
    base_path = "bloodmagic_textures/assets/alchemicalwizardry/textures/blocks"
    path = os.path.join(base_path, f"{texture_name}.png")
    if os.path.exists(path):
        img = Image.open(path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        # Zmień rozmiar na dokładnie 16x16
        img = img.resize((16, 16), Image.NEAREST)
        return np.array(img)
    return None

def create_textured_polygon_16x16(ax, vertices_3d, texture_array, alpha=1.0):
    """
    Tworzy ścianę z rzeczywistymi pikselami tekstury 16x16.
    vertices_3d - 4 wierzchołki ściany [(x1,y1,z1), ...]
    """
    if texture_array is None or len(vertices_3d) < 3:
        return
    
    h, w = texture_array.shape[:2]
    
    # Utwórz siatkę punktów na ścianie
    # Dla prostokąta 16x16 segmentów
    n_segments = 16
    
    # Współrzędne tekstury (0-15)
    u = np.linspace(0, w-1, w)
    v = np.linspace(0, h-1, h)
    uu, vv = np.meshgrid(u, v)
    
    # Interpoluj pozycje 3D dla każdego piksela
    # Zakładamy że ściana jest prostokątna i mapujemy UV linearnie
    v0, v1, v2, v3 = vertices_3d[:4]
    
    # Mapowanie UV na 3D (bilinearna interpolacja)
    # U = 0 to v0, U = 1 to v1, V = 0 to v0, V = 1 to v3
    u_norm = uu / (w - 1)
    v_norm = vv / (h - 1)
    
    # X = (1-u)*(1-v)*v0.x + u*(1-v)*v1.x + u*v*v2.x + (1-u)*v*v3.x
    X = ((1-u_norm)*(1-v_norm)*v0[0] + u_norm*(1-v_norm)*v1[0] + 
         u_norm*v_norm*v2[0] + (1-u_norm)*v_norm*v3[0])
    Y = ((1-u_norm)*(1-v_norm)*v0[1] + u_norm*(1-v_norm)*v1[1] + 
         u_norm*v_norm*v2[1] + (1-u_norm)*v_norm*v3[1])
    Z = ((1-u_norm)*(1-v_norm)*v0[2] + u_norm*(1-v_norm)*v1[2] + 
         u_norm*v_norm*v2[2] + (1-u_norm)*v_norm*v3[2])
    
    # Rysuj każdy piksel jako mały wielokąt
    for i in range(h-1):
        for j in range(w-1):
            # Wierzchołki piksela
            pixel_verts = [
                [X[i,j], Y[i,j], Z[i,j]],
                [X[i,j+1], Y[i,j+1], Z[i,j+1]],
                [X[i+1,j+1], Y[i+1,j+1], Z[i+1,j+1]],
                [X[i+1,j], Y[i+1,j], Z[i+1,j]]
            ]
            
            # Kolor z tekstury
            color = texture_array[i, j] / 255.0
            
            # Dodaj ścianę dla tego piksela
            face = Poly3DCollection([pixel_verts], facecolor=color, 
                                   edgecolor='none', alpha=alpha)
            ax.add_collection3d(face)

def plot_real_textured_block(ax, x, y, z, normal, keep_positive, 
                             texture_name, title):
    """Rysuje blok z RZECZYWISTYMI pikselami tekstury 16x16."""
    
    texture = load_texture(texture_name)
    if texture is None:
        print(f"Brak tekstury: {texture_name}")
        return
    
    nx, ny, nz = normal
    
    # Zaokrąglij do siatki 16x16
    segments = 16
    nx_g = round(nx * segments) / segments
    ny_g = round(ny * segments) / segments
    nz_g = round(nz * segments) / segments
    
    length = np.sqrt(nx_g**2 + ny_g**2 + nz_g**2)
    if length > 0:
        nx_g, ny_g, nz_g = nx_g/length, ny_g/length, nz_g/length
    
    cx, cy, cz = x + 0.5, y + 0.5, z + 0.5
    d = nx_g * cx + ny_g * cy + nz_g * cz
    
    # Wierzchołki sześcianu
    verts = {
        '000': [x, y, z], '100': [x+1, y, z], '110': [x+1, y+1, z], '010': [x, y+1, z],
        '001': [x, y, z+1], '101': [x+1, y, z+1], '111': [x+1, y+1, z+1], '011': [x, y+1, z+1]
    }
    
    # Oblicz punkty przecięcia
    cut_points = []
    
    # Krawędzie X
    for py in [y, y+1]:
        for pz in [z, z+1]:
            if abs(nx_g) > 0.001:
                t = (d - ny_g * py - nz_g * pz) / nx_g
                t_r = round(t * segments) / segments
                if x <= t_r <= x+1:
                    cut_points.append([t_r, py, pz])
    
    # Krawędzie Y
    for px in [x, x+1]:
        for pz in [z, z+1]:
            if abs(ny_g) > 0.001:
                t = (d - nx_g * px - nz_g * pz) / ny_g
                t_r = round(t * segments) / segments
                if y <= t_r <= y+1:
                    cut_points.append([px, t_r, pz])
    
    # Krawędzie Z
    for px in [x, x+1]:
        for py in [y, y+1]:
            if abs(nz_g) > 0.001:
                t = (d - nx_g * px - ny_g * py) / nz_g
                t_r = round(t * segments) / segments
                if z <= t_r <= z+1:
                    cut_points.append([px, py, t_r])
    
    # Usuń duplikaty
    seen = set()
    unique_cut = []
    for p in cut_points:
        k = (round(p[0],3), round(p[1],3), round(p[2],3))
        if k not in seen:
            seen.add(k)
            unique_cut.append(p)
    
    # Znajdź zachowane wierzchołki
    kept = []
    for k, v in verts.items():
        dist = nx_g*(v[0]-cx) + ny_g*(v[1]-cy) + nz_g*(v[2]-cz)
        if keep_positive:
            if dist >= -0.001:
                kept.append(v)
        else:
            if dist <= 0.001:
                kept.append(v)
    
    # Rysuj ściany Z (góra/dół) z teksturą
    for z_level, z_key in [(z, '0'), (z+1, '1')]:
        face_verts = [v for v in kept if abs(v[2] - z_level) < 0.001]
        cut_z = [p for p in unique_cut if abs(p[2] - z_level) < 0.001]
        all_v = face_verts + cut_z
        
        if len(all_v) >= 3:
            # Posortuj wokół centroidu
            cen = np.mean(all_v, axis=0)
            sorted_v = sorted(all_v, key=lambda p: np.arctan2(p[1]-cen[1], p[0]-cen[0]))
            
            if len(sorted_v) == 4:  # Prostokąt - idealne mapowanie tekstury
                create_textured_polygon_16x16(ax, sorted_v, texture)
            else:  # Wielokąt - użyj jednolitego koloru
                color = np.mean(texture, axis=(0,1)) / 255.0
                coll = Poly3DCollection([sorted_v], facecolor=color, 
                                       edgecolor='black', linewidth=0.5)
                ax.add_collection3d(coll)
    
    # Rysuj ściany Y (przód/tył)
    for y_level in [y, y+1]:
        face_verts = [v for v in kept if abs(v[1] - y_level) < 0.001]
        cut_y = [p for p in unique_cut if abs(p[1] - y_level) < 0.001]
        all_v = face_verts + cut_y
        
        if len(all_v) >= 3:
            cen = np.mean(all_v, axis=0)
            sorted_v = sorted(all_v, key=lambda p: np.arctan2(p[2]-cen[2], p[0]-cen[0]))
            
            if len(sorted_v) == 4:
                create_textured_polygon_16x16(ax, sorted_v, texture)
            else:
                color = np.mean(texture, axis=(0,1)) / 255.0 * 0.8  # Ciemniejsze dla boku
                coll = Poly3DCollection([sorted_v], facecolor=color, 
                                       edgecolor='black', linewidth=0.5)
                ax.add_collection3d(coll)
    
    # Rysuj ściany X (lewo/prawo)
    for x_level in [x, x+1]:
        face_verts = [v for v in kept if abs(v[0] - x_level) < 0.001]
        cut_x = [p for p in unique_cut if abs(p[0] - x_level) < 0.001]
        all_v = face_verts + cut_x
        
        if len(all_v) >= 3:
            cen = np.mean(all_v, axis=0)
            sorted_v = sorted(all_v, key=lambda p: np.arctan2(p[2]-cen[2], p[1]-cen[1]))
            
            if len(sorted_v) == 4:
                create_textured_polygon_16x16(ax, sorted_v, texture)
            else:
                color = np.mean(texture, axis=(0,1)) / 255.0 * 0.6  # Najciemniejsze
                coll = Poly3DCollection([sorted_v], facecolor=color, 
                                       edgecolor='black', linewidth=0.5)
                ax.add_collection3d(coll)
    
    # Ściana cięcia - jaśniejsza wersja tekstury
    if len(unique_cut) >= 3:
        cen = np.mean(unique_cut, axis=0)
        if abs(nz_g) > 0.9:
            sorted_c = sorted(unique_cut, key=lambda p: np.arctan2(p[1]-cen[1], p[0]-cen[0]))
        elif abs(ny_g) > 0.9:
            sorted_c = sorted(unique_cut, key=lambda p: np.arctan2(p[2]-cen[2], p[0]-cen[0]))
        else:
            sorted_c = sorted(unique_cut, key=lambda p: np.arctan2(p[2]-cen[2], p[1]-cen[1]))
        
        if len(sorted_c) == 4:
            # Użyj tekstury z jaśniejszym odcieniem
            bright_tex = np.clip(texture.astype(float) * 1.2, 0, 255).astype(np.uint8)
            create_textured_polygon_16x16(ax, sorted_c, bright_tex)
        else:
            color = np.mean(texture, axis=(0,1)) / 255.0 * 1.1
            coll = Poly3DCollection([sorted_c], facecolor=color, 
                                   edgecolor='cyan', linewidth=1)
            ax.add_collection3d(coll)
    
    # Ramka oryginalnego bloku (przezroczysta)
    cube_edges = [
        ([x,y,z], [x+1,y,z]), ([x+1,y,z], [x+1,y+1,z]), ([x+1,y+1,z], [x,y+1,z]), ([x,y+1,z], [x,y,z]),
        ([x,y,z+1], [x+1,y,z+1]), ([x+1,y,z+1], [x+1,y+1,z+1]), ([x+1,y+1,z+1], [x,y+1,z+1]), ([x,y+1,z+1], [x,y,z+1]),
        ([x,y,z], [x,y,z+1]), ([x+1,y,z], [x+1,y,z+1]), ([x+1,y+1,z], [x+1,y+1,z+1]), ([x,y+1,z], [x,y+1,z+1])
    ]
    for v1, v2 in cube_edges:
        ax.plot([v1[0], v2[0]], [v1[1], v2[1]], [v1[2], v2[2]], 'k--', alpha=0.15, linewidth=0.5)
    
    # Wektor normalny
    ax.quiver(cx, cy, cz, nx_g*0.35, ny_g*0.35, nz_g*0.35,
              color='yellow', arrow_length_ratio=0.25, linewidth=2)
    
    ax.set_xlim(x-0.15, x+1.15)
    ax.set_ylim(y-0.15, y+1.15)
    ax.set_zlim(z-0.15, z+1.15)
    ax.set_title(f"{title}\n[{texture_name}]\n(Z PRAWDZIWYMI TEKSTURAMI!)", 
                fontsize=9, fontweight='bold')
    ax.set_box_aspect([1,1,1])

def create_real_texture_demo():
    """Główna wizualizacja z prawdziwymi pikselami tekstur."""
    
    fig = plt.figure(figsize=(18, 10))
    fig.suptitle('Cuttable Blocks z PRAWDZIWYMI pikselami tekstur BloodMagic 16x16!\n' + 
                 'Każdy piksel tekstury jest widoczny na ścianach bloków', 
                 fontsize=14, fontweight='bold', y=0.98)
    
    scenarios = [
        ([0, 1, 0], True, 'Górna połowa - teksturowana', 'BloodAltar_Top'),
        ([0, -1, 0], False, 'Dolna połowa - teksturowana', 'BloodStoneBrick'),
        ([1, 0, 0], True, 'Wschód - teksturowany', 'SpeedRune'),
        ([-1, 0, 0], False, 'Zachód - teksturowany', 'BlankRune'),
        ([0, 0, 1], True, 'Południe - teksturowane', 'WaterRitualStone'),
        ([0.7, 0.7, 0], True, 'Diag X+Y+ - teksturowany', 'FireRitualStone'),
        ([-0.7, 0.7, 0.3], True, 'Diag X-Y+Z+ - teksturowany', 'BloodAltar_Top'),
        ([0.5, 0.5, 0.5], True, 'Diag XYZ - teksturowany', 'RitualStone'),
    ]
    
    for i, (normal, keep, title, tex) in enumerate(scenarios):
        ax = fig.add_subplot(2, 4, i+1, projection='3d')
        plot_real_textured_block(ax, 0, 0, 0, normal, keep, tex, title)
        ax.view_init(elev=25, azim=45)
    
    plt.tight_layout()
    plt.savefig('real_textured_blocks.png', dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print("Zapisano: real_textured_blocks.png")
    plt.close()

def create_texture_comparison():
    """Porównanie: tekstura 2D vs na bloku 3D."""
    
    fig = plt.figure(figsize=(14, 6))
    fig.suptitle('Porównanie: Tekstura 2D vs Tekstura na przyciętym bloku 3D', 
                 fontsize=14, fontweight='bold')
    
    # Tekstura 2D
    ax1 = fig.add_subplot(1, 3, 1)
    texture = load_texture('BloodAltar_Top')
    if texture is not None:
        ax1.imshow(texture)
        ax1.set_title('Tekstura 2D\n[BloodAltar_Top]\n16x16 pikseli', fontweight='bold')
    ax1.axis('off')
    
    # Strzałka
    ax2 = fig.add_subplot(1, 3, 2)
    ax2.annotate('', xy=(0.85, 0.5), xytext=(0.15, 0.5),
                arrowprops=dict(arrowstyle='->', lw=6, color='green'))
    ax2.text(0.5, 0.65, 'RENDERER MODA', fontsize=14, ha='center', 
             fontweight='bold', color='green')
    ax2.text(0.5, 0.45, 'mapuje każdy piksel', fontsize=11, ha='center')
    ax2.text(0.5, 0.35, 'na geometrię 3D', fontsize=11, ha='center')
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.axis('off')
    
    # Blok 3D z teksturą
    ax3 = fig.add_subplot(1, 3, 3, projection='3d')
    plot_real_textured_block(ax3, 0, 0, 0, [0.7, 0.7, 0], True, 
                            'BloodAltar_Top', 'Blok 3D z teksturą')
    ax3.view_init(elev=20, azim=45)
    
    plt.tight_layout()
    plt.savefig('texture_2d_vs_3d.png', dpi=150, bbox_inches='tight', facecolor='white')
    print("Zapisano: texture_2d_vs_3d.png")
    plt.close()

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("Generowanie wizualizacji z PRAWDZIWYMI teksturami...")
    print("(Każdy piksel 16x16 będzie widoczny)")
    create_real_texture_demo()
    create_texture_comparison()
    print("\nGotowe! Teraz widać faktyczne piksele tekstur na blokach!")
