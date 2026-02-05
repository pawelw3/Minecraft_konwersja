"""
Wizualizacja różnych ukośnych cięć bloków (diagonal cuts)
Pokazuje różne kąty nachylenia i jak wygląda ściana cięcia
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.patches as mpatches

def create_texture():
    """Tworzy teksturę 16x16"""
    texture = np.zeros((16, 16, 3))
    base_red = np.array([0.6, 0.1, 0.1])
    dark_red = np.array([0.4, 0.05, 0.05])
    
    for i in range(16):
        for j in range(16):
            if (i // 4 + j // 4) % 2 == 0:
                texture[i, j] = base_red
            else:
                texture[i, j] = dark_red
    
    # Ornament w środku
    for i in range(4, 12):
        for j in range(4, 12):
            dist = max(abs(i - 8), abs(j - 8))
            if dist < 4:
                intensity = 1.0 - (dist / 4.0) * 0.3
                texture[i, j] = np.array([0.8, 0.2, 0.15]) * intensity
    return texture

def calculate_cut_plane(normal, d=0.5):
    """
    Oblicza wielokąt przecięcia płaszczyzny z sześcianem [0,1]x[0,1]x[0,1]
    Płaszczyzna: nx*x + ny*y + nz*z = d*(nx+ny+nz)
    """
    nx, ny, nz = normal
    points = []
    
    # Sprawdź wszystkie 12 krawędzi sześcianu
    # Krawędzie równoległe do X (y=0/1, z=0/1)
    for y in [0, 1]:
        for z in [0, 1]:
            if abs(nx) > 0.0001:
                t = (d * (nx + ny + nz) - ny * y - nz * z) / nx
                if 0 <= t <= 1:
                    points.append([t, y, z])
    
    # Krawędzie równoległe do Y (x=0/1, z=0/1)
    for x in [0, 1]:
        for z in [0, 1]:
            if abs(ny) > 0.0001:
                t = (d * (nx + ny + nz) - nx * x - nz * z) / ny
                if 0 <= t <= 1:
                    points.append([x, t, z])
    
    # Krawędzie równoległe do Z (x=0/1, y=0/1)
    for x in [0, 1]:
        for y in [0, 1]:
            if abs(nz) > 0.0001:
                t = (d * (nx + ny + nz) - nx * x - ny * y) / nz
                if 0 <= t <= 1:
                    points.append([x, y, t])
    
    return np.array(points) if points else None

def sort_polygon_points(points, normal):
    """Sortuje punkty wielokąta w kolejności zgodnej z ruchem wskazówek zegara"""
    if points is None or len(points) < 3:
        return points
    
    # Centroid
    center = np.mean(points, axis=0)
    
    # Wektor referencyjny (prostopadły do normalnej)
    nx, ny, nz = normal
    if abs(nz) < abs(nx) and abs(nz) < abs(ny):
        ref = np.array([0, 0, 1])
    elif abs(ny) < abs(nx):
        ref = np.array([0, 1, 0])
    else:
        ref = np.array([1, 0, 0])
    
    # Wektor prostopadły do normalnej i referencyjnego
    u = np.cross(normal, ref)
    u = u / np.linalg.norm(u)
    v = np.cross(normal, u)
    
    # Sortuj według kąta
    angles = []
    for p in points:
        vec = p - center
        angle = np.arctan2(np.dot(vec, v), np.dot(vec, u))
        angles.append(angle)
    
    sorted_indices = np.argsort(angles)
    return points[sorted_indices]

def draw_cube(ax, alpha=0.1):
    """Rysuje przezroczysty sześcian"""
    # Wierzchołki sześcianu
    vertices = np.array([
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],  # dolna ściana
        [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]   # górna ściana
    ])
    
    # Ściany sześcianu
    faces = [
        [vertices[0], vertices[1], vertices[2], vertices[3]],  # dół
        [vertices[4], vertices[5], vertices[6], vertices[7]],  # góra
        [vertices[0], vertices[1], vertices[5], vertices[4]],  # przód
        [vertices[2], vertices[3], vertices[7], vertices[6]],  # tył
        [vertices[0], vertices[3], vertices[7], vertices[4]],  # lewo
        [vertices[1], vertices[2], vertices[6], vertices[5]],  # prawo
    ]
    
    face_collection = Poly3DCollection(faces, alpha=alpha, facecolor='lightblue', 
                                        edgecolor='blue', linewidth=0.5)
    ax.add_collection3d(face_collection)

def draw_cut_face(ax, points, color='red', alpha=0.8):
    """Rysuje ścianę cięcia"""
    if points is None or len(points) < 3:
        return
    
    # Utwórz wielokąt
    verts = [points]
    face_collection = Poly3DCollection(verts, alpha=alpha, facecolor=color, 
                                        edgecolor='darkred', linewidth=2)
    ax.add_collection3d(face_collection)
    
    # Dodaj punkty
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
              color='yellow', s=50, depthshade=False, edgecolors='black')

def visualize_diagonal_cuts():
    """Główna wizualizacja różnych cięć ukośnych"""
    
    # Definicje różnych cięć (normalne)
    cuts = [
        {"name": "Pełny blok", "normal": None, "desc": "Bez cięcia"},
        {"name": "45° XY", "normal": [1, 1, 0], "desc": "Przekątna w płaszczyźnie XY"},
        {"name": "45° XZ", "normal": [1, 0, 1], "desc": "Przekątna w płaszczyźnie XZ"},
        {"name": "45° YZ", "normal": [0, 1, 1], "desc": "Przekątna w płaszczyźnie YZ"},
        {"name": "60° XYZ", "normal": [1, 1, 1], "desc": "Równomiernie ukośna"},
        {"name": "30° X", "normal": [2, 1, 0], "desc": "Płaska przekątna"},
    ]
    
    fig = plt.figure(figsize=(18, 12))
    
    for idx, cut in enumerate(cuts):
        ax = fig.add_subplot(2, 3, idx + 1, projection='3d')
        
        # Rysuj sześcian
        draw_cube(ax, alpha=0.15)
        
        if cut["normal"] is not None:
            # Oblicz i narysuj płaszczyznę cięcia
            normal = np.array(cut["normal"])
            normal = normal / np.linalg.norm(normal)  # Normalizuj
            
            points = calculate_cut_plane(cut["normal"])
            if points is not None and len(points) >= 3:
                points = sort_polygon_points(points, normal)
                draw_cut_face(ax, points, color='crimson', alpha=0.7)
                
                # Oblicz rozmiar ściany
                if len(points) >= 2:
                    # Przybliżony rozmiar
                    extents = np.max(points, axis=0) - np.min(points, axis=0)
                    size_2d = np.sqrt(extents[0]**2 + extents[1]**2 + extents[2]**2)
                    size_text = f"Rozmiar: ~{size_2d:.2f}"
                else:
                    size_text = ""
            else:
                size_text = "Brak przecięcia"
        else:
            size_text = "Brak cięcia"
        
        # Ustawienia osi
        ax.set_xlim(-0.2, 1.2)
        ax.set_ylim(-0.2, 1.2)
        ax.set_zlim(-0.2, 1.2)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        
        title = f"{cut['name']}\n{cut['desc']}"
        if size_text:
            title += f"\n{size_text}"
        ax.set_title(title, fontsize=11, fontweight='bold')
        
        # Ustaw kąt widzenia
        ax.view_init(elev=20, azim=45)
    
    plt.suptitle('Różne typy ukośnych cięć bloków (Diagonal Cuts)', 
                 fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig('diagonal_cuts_3d.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("Zapisano: diagonal_cuts_3d.png")
    plt.close()

def visualize_cut_faces_with_texture():
    """Wizualizuje same ściany cięcia z nałożoną teksturą (tiling)"""
    
    texture = create_texture()
    
    cuts = [
        {"name": "45° XY (płaszczyzna Z)", "normal": [1, 1, 0], "face_size": (1.414, 1.0)},
        {"name": "45° XZ (płaszczyzna Y)", "normal": [1, 0, 1], "face_size": (1.414, 1.0)},
        {"name": "45° YZ (płaszczyzna X)", "normal": [0, 1, 1], "face_size": (1.414, 1.0)},
        {"name": "60° XYZ (równomierna)", "normal": [1, 1, 1], "face_size": (1.225, 1.225)},
        {"name": "30° X (płaska)", "normal": [2, 1, 0], "face_size": (1.12, 1.0)},
        {"name": "22.5° (łagodna)", "normal": [2.414, 1, 0], "face_size": (1.08, 1.0)},
    ]
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    for idx, cut in enumerate(cuts):
        ax = axes[idx // 3, idx % 3]
        
        normal = np.array(cut["normal"])
        points = calculate_cut_plane(normal)
        
        if points is not None and len(points) >= 3:
            # Sortuj punkty
            normal_norm = normal / np.linalg.norm(normal)
            points = sort_polygon_points(points, normal_norm)
            
            # Oblicz rozmiar ściany w pikselach
            face_w, face_h = cut["face_size"]
            face_w_px = face_w * 16
            face_h_px = face_h * 16
            
            # Rysuj teksturę z tiling
            # Ile kafelków potrzeba?
            tiles_x = int(np.ceil(face_w_px / 16)) + 1
            tiles_y = int(np.ceil(face_h_px / 16)) + 1
            
            # Stwórz tiling
            from scipy.ndimage import zoom
            tiled = np.tile(texture, (tiles_y, tiles_x, 1))
            
            # Wyświetl
            ax.imshow(tiled[:32, :32], origin='lower', interpolation='nearest')
            
            # Narysuj kontur wielokąta (uproszczony jako prostokąt)
            margin = (32 - face_w_px) / 2
            rect = plt.Rectangle((margin, 8), face_w_px, face_h_px,
                                  fill=False, edgecolor='lime', linewidth=3)
            ax.add_patch(rect)
            
            # Dodaj tekst
            ax.text(16, 30, f'{face_w_px:.1f}x{face_h_px:.1f}px', 
                   ha='center', fontsize=10, color='white',
                   bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        
        ax.set_title(cut['name'], fontsize=11, fontweight='bold')
        ax.set_xlim(0, 32)
        ax.set_ylim(0, 32)
        ax.axis('off')
    
    plt.suptitle('Ściany cięcia z teksturą (Tiling Centered)', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('diagonal_cuts_textured.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("Zapisano: diagonal_cuts_textured.png")
    plt.close()

def visualize_side_by_side_comparison():
    """Porównanie: blok 3D vs ściana cięcia z teksturą"""
    
    fig = plt.figure(figsize=(16, 10))
    
    # Wybierz 3 reprezentatywne cięcia
    cuts = [
        {"name": "45° XY - Przekątna pozioma", "normal": [1, 1, 0], "view": (20, 30)},
        {"name": "45° XYZ - Ukośna przestrzenna", "normal": [1, 1, 1], "view": (30, 45)},
        {"name": "30° X - Płaska przekątna", "normal": [2, 1, 0], "view": (15, 60)},
    ]
    
    for idx, cut in enumerate(cuts):
        # Lewy panel: blok 3D z cięciem
        ax3d = fig.add_subplot(3, 2, idx * 2 + 1, projection='3d')
        
        draw_cube(ax3d, alpha=0.1)
        
        normal = np.array(cut["normal"])
        points = calculate_cut_plane(normal)
        if points is not None and len(points) >= 3:
            normal_norm = normal / np.linalg.norm(normal)
            points = sort_polygon_points(points, normal_norm)
            draw_cut_face(ax3d, points, color='crimson', alpha=0.8)
        
        ax3d.set_xlim(-0.2, 1.2)
        ax3d.set_ylim(-0.2, 1.2)
        ax3d.set_zlim(-0.2, 1.2)
        ax3d.set_title(f'{cut["name"]}\n[Blok 3D]', fontsize=11, fontweight='bold')
        ax3d.view_init(elev=cut["view"][0], azim=cut["view"][1])
        
        # Prawy panel: ściana cięcia z teksturą
        ax2d = fig.add_subplot(3, 2, idx * 2 + 2)
        
        if points is not None:
            # Oblicz rozmiar
            extents = np.max(points, axis=0) - np.min(points, axis=0)
            face_size = np.sqrt(extents[0]**2 + extents[1]**2 + extents[2]**2)
            face_px = face_size * 16
            
            # Rysuj reprezentację tekstury
            texture = create_texture()
            tiles = int(np.ceil(face_px / 16)) + 1
            tiled = np.tile(texture, (tiles, tiles, 1))
            
            display_size = min(32, tiled.shape[0])
            ax2d.imshow(tiled[:display_size, :display_size], origin='lower', 
                       interpolation='nearest')
            
            # Zaznacz obszar
            center = display_size / 2
            half_size = face_px / 2
            rect = plt.Rectangle((center - half_size, center - 8), 
                                  face_px, 16,
                                  fill=False, edgecolor='lime', linewidth=3)
            ax2d.add_patch(rect)
            
            ax2d.text(center, display_size - 2, 
                     f'Ściana cięcia: {face_px:.1f}x16px', 
                     ha='center', fontsize=10, color='white',
                     bbox=dict(boxstyle='round', facecolor='black', alpha=0.8))
        
        ax2d.set_title('[Ściana cięcia z teksturą]', fontsize=11, fontweight='bold')
        ax2d.axis('off')
    
    plt.suptitle('Porównanie: Blok 3D vs Ściana cięcia z teksturą', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig('diagonal_cuts_comparison.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("Zapisano: diagonal_cuts_comparison.png")
    plt.close()

if __name__ == '__main__':
    print("Generowanie wizualizacji cięć ukośnych...")
    visualize_diagonal_cuts()
    visualize_cut_faces_with_texture()
    visualize_side_by_side_comparison()
    print("\nWszystkie wizualizacje zapisane!")
