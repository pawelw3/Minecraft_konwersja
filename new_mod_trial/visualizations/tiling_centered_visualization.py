"""
Wizualizacja tiling z wycinkiem (centered tiling)

Zamiast clamp-to-edge (powielanie krawędzi), używamy:
1. Powtarzalnego tiling tekstury
2. Wycinka tylko potrzebnego fragmentu
3. Fragment wycentrowany na ścianie
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon
import matplotlib.patches as mpatches

def create_texture_16x16():
    """Tworzy teksturę 16x16 z wzorem jak BloodAltar_Top"""
    texture = np.zeros((16, 16, 3))
    
    # Czerwone tło z ciemniejszymi czerwonymi kwadratami
    base_red = np.array([0.6, 0.1, 0.1])
    dark_red = np.array([0.4, 0.05, 0.05])
    
    for i in range(16):
        for j in range(16):
            if (i // 4 + j // 4) % 2 == 0:
                texture[i, j] = base_red
            else:
                texture[i, j] = dark_red
    
    # Jasniejszy środek (ornament)
    for i in range(4, 12):
        for j in range(4, 12):
            dist = max(abs(i - 8), abs(j - 8))
            if dist < 4:
                intensity = 1.0 - (dist / 4.0) * 0.3
                texture[i, j] = np.array([0.8, 0.2, 0.15]) * intensity
    
    return texture

def tile_texture(texture, tiles_x, tiles_y):
    """Powiela teksturę w siatkę kafelków"""
    h, w = texture.shape[:2]
    tiled = np.zeros((h * tiles_y, w * tiles_x, 3))
    for ty in range(tiles_y):
        for tx in range(tiles_x):
            tiled[ty*h:(ty+1)*h, tx*w:(tx+1)*w] = texture
    return tiled

def visualize_tiling_centered():
    """Wizualizuje tiling wycentrowany na ścianie"""
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Tiling wycentrowany na ścianie (Centered Tiling)', fontsize=16, fontweight='bold')
    
    texture = create_texture_16x16()
    
    # Scenariusze: szerokość ściany w pikselach
    scenarios = [
        (16, 16, "Standard 16x16\n(1 kafelek)"),
        (22.6, 16, "Diagonalna ściana 22.6x16\n(1.41x - √2)"),
        (32, 16, "Szeroka ściana 32x16\n(2 kafelki)"),
        (16, 22.6, "Wysoka ściana 16x22.6\n(√2 w pionie)"),
        (32, 32, "Duża ściana 32x32\n(2x2 kafelki)"),
        (22.6, 22.6, "Kwadratowa diagonalna 22.6x22.6"),
    ]
    
    for idx, (face_w, face_h, title) in enumerate(scenarios):
        ax = axes[idx // 3, idx % 3]
        
        # Ile kafelków potrzeba?
        tiles_x = int(np.ceil(face_w / 16))
        tiles_y = int(np.ceil(face_h / 16))
        
        # Stwórz tiling
        tiled = tile_texture(texture, tiles_x + 2, tiles_y + 2)  # +2 dla marginesu
        
        # Rysuj tiling
        ax.imshow(tiled, extent=[-16, (tiles_x+2)*16 - 16, -16, (tiles_y+2)*16 - 16], 
                  origin='lower', interpolation='nearest')
        
        # Oblicz pozycję ściany (wycentrowanej)
        # Ściana o rozmiarze face_w x face_h, wycentrowana na (8, 8) w układzie pikseli
        face_left = 8 - face_w / 2
        face_right = 8 + face_w / 2
        face_bottom = 8 - face_h / 2
        face_top = 8 + face_h / 2
        
        # Narysuj prostokąt ściany (fragment, który będzie widoczny)
        face_rect = Rectangle((face_left, face_bottom), face_w, face_h,
                               linewidth=4, edgecolor='lime', facecolor='none', linestyle='-')
        ax.add_patch(face_rect)
        
        # Dodaj etykietę
        ax.text(8, face_top + 4, 'WYŚWIETLANY FRAGMENT', 
               ha='center', fontsize=9, color='lime', fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='white', edgecolor='lime', alpha=0.9))
        
        # Oznacz środek układu (gdzie jest tekstura center = 8,8)
        ax.plot(8, 8, 'b+', markersize=15, mew=2, label='Center tekstury')
        
        # Linie siatki kafelków
        for tx in range(-1, tiles_x + 2):
            ax.axvline(x=tx*16, color='white', linestyle='--', alpha=0.5, linewidth=1)
        for ty in range(-1, tiles_y + 2):
            ax.axhline(y=ty*16, color='white', linestyle='--', alpha=0.5, linewidth=1)
        
        # Ustaw zakres widoku
        margin = 8
        ax.set_xlim(face_left - margin, face_right + margin)
        ax.set_ylim(face_bottom - margin, face_top + margin)
        
        ax.set_aspect('equal')
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_xlabel('Piksel U')
        ax.set_ylabel('Piksel V')
        
        # Dodaj legendę
        ax.legend(loc='lower left', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('tiling_centered_visualization.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("Zapisano: tiling_centered_visualization.png")
    plt.close()

def visualize_comparison():
    """Porównuje różne podejścia do teksturowania"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Porównanie metod teksturowania dla ściany 22.6x16 (diagonalna)', 
                 fontsize=14, fontweight='bold')
    
    texture = create_texture_16x16()
    face_w, face_h = 22.6, 16
    
    # Scenariusze
    methods = [
        ("ROZCIĄGANIE\n(Stretch)", "stretch"),
        ("CLAMP-TO-EDGE\n(Powielanie krawędzi)", "clamp"),
        ("TILING CENTERED\n(Tiling z wycinkiem)", "tiling"),
    ]
    
    for idx, (title, method) in enumerate(methods):
        ax = axes[idx]
        
        if method == "stretch":
            # Rozciągnięta tekstura
            stretched = np.zeros((16, 23, 3))
            for i in range(16):
                for j in range(23):
                    u = j / 22.0 * 15
                    v = i
                    stretched[i, j] = texture[int(v), int(u)]
            ax.imshow(stretched, extent=[0, 23, 0, 16], origin='lower', interpolation='nearest')
            ax.text(11.5, 18, 'Tekstura rozciągnięta!\nUtrata szczegółów', 
                   ha='center', fontsize=10, color='red', fontweight='bold')
            
        elif method == "clamp":
            # Clamp-to-edge: centrum + powielone krawędzie
            clamped = np.zeros((16, 23, 3))
            for i in range(16):
                for j in range(23):
                    # Centrum 16px, po bokach powielone krawędzie
                    if j < 3:
                        # Lewa krawędź
                        clamped[i, j] = texture[i, 0]
                    elif j >= 20:
                        # Prawa krawędź
                        clamped[i, j] = texture[i, 15]
                    else:
                        # Środek - skalowane
                        u = (j - 3) / 16.0 * 15
                        clamped[i, j] = texture[i, int(u)]
            ax.imshow(clamped, extent=[0, 23, 0, 16], origin='lower', interpolation='nearest')
            ax.text(11.5, 18, 'Krawędzie powielone\nNienaturalne przejścia', 
                   ha='center', fontsize=10, color='orange', fontweight='bold')
            
        elif method == "tiling":
            # Tiling centered: 2 kafelki, wycentrowane
            tiled = tile_texture(texture, 2, 1)
            # Wycinamy fragment 23x16 wycentrowany na środku
            start_x = int((32 - 23) / 2)
            fragment = tiled[:, start_x:start_x+23]
            ax.imshow(fragment, extent=[0, 23, 0, 16], origin='lower', interpolation='nearest')
            ax.text(11.5, 18, 'Tiling wycentrowany\nPowtarzalny wzór', 
                   ha='center', fontsize=10, color='green', fontweight='bold')
        
        # Oznacz granicę ściany
        face_rect = Rectangle((0, 0), 23, 16, linewidth=3, 
                               edgecolor='blue', facecolor='none', linestyle='--')
        ax.add_patch(face_rect)
        
        ax.set_aspect('equal')
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlabel('Piksel')
        ax.set_ylabel('Piksel')
        ax.set_xlim(-1, 24)
        ax.set_ylim(-1, 17)
    
    plt.tight_layout()
    plt.savefig('tiling_comparison.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("Zapisano: tiling_comparison.png")
    plt.close()

def visualize_uv_mapping():
    """Wizualizuje mapowanie UV dla tiling centered"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    texture = create_texture_16x16()
    
    # Przygotuj tiling 3x2
    tiled = tile_texture(texture, 3, 2)
    
    # Rysuj tiling
    ax.imshow(tiled, extent=[-16, 32, -16, 16], origin='lower', interpolation='nearest')
    
    # Przykład: ściana 22.6px szeroka
    face_w = 22.6
    face_left = 8 - face_w / 2  # = -3.3
    face_right = 8 + face_w / 2  # = 19.3
    
    # Narysuj prostokąt ściany
    face_rect = Rectangle((face_left, 0), face_w, 16,
                           linewidth=4, edgecolor='lime', facecolor='lime', alpha=0.2)
    ax.add_patch(face_rect)
    
    # Dodaj etykiety kafelków
    for tx in range(-1, 3):
        for ty in range(0, 2):
            x_pos = tx * 16 + 8
            y_pos = ty * 16 + 8
            ax.text(x_pos, y_pos, f'Tile\n({tx},{ty})', 
                   ha='center', va='center', fontsize=9, color='white',
                   bbox=dict(boxstyle='round', facecolor='black', edgecolor='white', alpha=0.5))
    
    # Oznacz środek
    ax.plot(8, 8, 'r+', markersize=20, mew=3, label='Center (8,8)')
    
    # Strzałki pokazujące wrapowanie
    ax.annotate('', xy=(16, 8), xytext=(face_right - 2, 8),
               arrowprops=dict(arrowstyle='->', color='yellow', lw=2))
    ax.annotate('', xy=(0, 8), xytext=(face_left + 2, 8),
               arrowprops=dict(arrowstyle='->', color='yellow', lw=2))
    
    ax.text(8, -10, 'TILING: Tekstura powtarza się w nieskończoność\n' +
                    'Wycinek wycentrowany na (8,8) pokazuje tylko potrzebny fragment',
           ha='center', fontsize=11, color='black',
           bbox=dict(boxstyle='round', facecolor='yellow', edgecolor='black', alpha=0.8))
    
    ax.set_xlim(-18, 34)
    ax.set_ylim(-18, 18)
    ax.set_aspect('equal')
    ax.set_title('Mapowanie UV dla Tiling Centered', fontsize=14, fontweight='bold')
    ax.set_xlabel('U (piksel tekstury)')
    ax.set_ylabel('V (piksel tekstury)')
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig('tiling_uv_mapping.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("Zapisano: tiling_uv_mapping.png")
    plt.close()

if __name__ == '__main__':
    visualize_tiling_centered()
    visualize_comparison()
    visualize_uv_mapping()
    print("\nWszystkie wizualizacje zapisane!")
