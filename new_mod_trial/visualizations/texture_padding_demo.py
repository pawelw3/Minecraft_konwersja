#!/usr/bin/env python3
"""
Demonstracja paddingu tekstur na ścianach cięcia.
Padding = powielanie brzegowych pikseli zamiast rozciągania lub powtarzania.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
import os

def load_texture(texture_name):
    """Wczytuje teksturę 16x16."""
    base_path = "bloodmagic_textures/assets/alchemicalwizardry/textures/blocks"
    path = os.path.join(base_path, f"{texture_name}.png")
    if os.path.exists(path):
        img = Image.open(path).convert('RGB')
        return np.array(img.resize((16, 16), Image.NEAREST))
    return None

def apply_padding(texture, target_size):
    """
    Aplikuje padding do tekstury aby uzyskać target_size.
    - Środkowa część (16x16) = oryginalna tekstura
    - Brzegi = powielone piksele brzegowe
    """
    h, w = texture.shape[:2]
    th, tw = target_size
    
    result = np.zeros((th, tw, 3), dtype=np.uint8)
    
    # Oblicz offsety aby wycentrować oryginalną teksturę
    offset_y = (th - h) // 2
    offset_x = (tw - w) // 2
    
    # Krok 1: Wypełnij środek oryginalną teksturą
    result[offset_y:offset_y+h, offset_x:offset_x+w] = texture
    
    # Krok 2: Padding górny (powiel górny wiersz)
    if offset_y > 0:
        top_row = texture[0, :]
        for i in range(offset_y):
            result[i, offset_x:offset_x+w] = top_row
    
    # Krok 3: Padding dolny (powiel dolny wiersz)
    if offset_y + h < th:
        bottom_row = texture[-1, :]
        for i in range(offset_y + h, th):
            result[i, offset_x:offset_x+w] = bottom_row
    
    # Krok 4: Padding lewy (powiel lewą kolumnę)
    if offset_x > 0:
        left_col = texture[:, 0]
        for i in range(h):
            result[offset_y+i, :offset_x] = left_col[i]
    
    # Krok 5: Padding prawy (powiel prawą kolumnę)
    if offset_x + w < tw:
        right_col = texture[:, -1]
        for i in range(h):
            result[offset_y+i, offset_x+w:] = right_col[i]
    
    # Krok 6: Narożniki (średnia z sąsiednich paddingów lub po prostu kopia)
    if offset_y > 0 and offset_x > 0:
        result[:offset_y, :offset_x] = texture[0, 0]  # Lewy górny
    if offset_y > 0 and offset_x + w < tw:
        result[:offset_y, offset_x+w:] = texture[0, -1]  # Prawy górny
    if offset_y + h < th and offset_x > 0:
        result[offset_y+h:, :offset_x] = texture[-1, 0]  # Lewy dolny
    if offset_y + h < th and offset_x + w < tw:
        result[offset_y+h:, offset_x+w:] = texture[-1, -1]  # Prawy dolny
    
    return result

def create_padding_visualization():
    """Tworzy wizualizację pokazującą padding."""
    
    texture = load_texture('BloodAltar_Top')
    if texture is None:
        return
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Texture Padding na ścianach cięcia\n' +
                 'Powielanie brzegowych pikseli zamiast rozciągania', 
                 fontsize=14, fontweight='bold')
    
    # Scenariusze: (size, title, description)
    scenarios = [
        ((16, 16), 'Oryginalna tekstura', '16x16 - bazowy rozmiar'),
        ((20, 16), 'Mały padding', '20x16 - lekki padding po bokach'),
        ((16, 24), 'Padding pionowy', '16x24 - padding góra/dół'),
        ((24, 24), 'Średni padding', '24x24 - padding po wszystkich stronach'),
        ((32, 16), 'Duży poziomy', '32x16 - szeroka ściana z paddingiem'),
        ((32, 32), 'Duży padding', '32x32 - duża ściana z paddingiem'),
    ]
    
    for idx, (size, title, desc) in enumerate(scenarios):
        ax = axes[idx // 3, idx % 3]
        
        # Zastosuj padding
        padded = apply_padding(texture, size)
        
        # Wyświetl
        ax.imshow(padded)
        ax.set_title(f"{title}\n{desc}\n{size[0]}x{size[1]}", fontsize=10, fontweight='bold')
        ax.axis('off')
        
        # Dodaj oznaczenia
        h, w = texture.shape[:2]
        offset_y = (size[0] - h) // 2
        offset_x = (size[1] - w) // 2
        
        # Zaznacz oryginalną teksturę (niebieska ramka)
        rect = Rectangle((offset_x-0.5, offset_y-0.5), w, h, 
                         fill=False, edgecolor='blue', linewidth=2)
        ax.add_patch(rect)
        
        # Dodaj tekst "ORYGINAŁ"
        ax.text(offset_x + w/2, offset_y + h/2, 'ORYGINAŁ', 
               ha='center', va='center', fontsize=8, color='blue',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
        
        # Zaznacz padding (czerwone ramki)
        if offset_y > 0:
            rect_top = Rectangle((offset_x-0.5, -0.5), w, offset_y, 
                                fill=False, edgecolor='red', linewidth=1.5, linestyle='--')
            ax.add_patch(rect_top)
            ax.text(w/2, offset_y/2, 'PADDING', ha='center', va='center', 
                   fontsize=7, color='red')
        
        if offset_y + h < size[0]:
            rect_bottom = Rectangle((offset_x-0.5, offset_y+h-0.5), w, size[0]-offset_y-h, 
                                   fill=False, edgecolor='red', linewidth=1.5, linestyle='--')
            ax.add_patch(rect_bottom)
        
        if offset_x > 0:
            rect_left = Rectangle((-0.5, offset_y-0.5), offset_x, h, 
                                 fill=False, edgecolor='red', linewidth=1.5, linestyle='--')
            ax.add_patch(rect_left)
        
        if offset_x + w < size[1]:
            rect_right = Rectangle((offset_x+w-0.5, offset_y-0.5), size[1]-offset_x-w, h, 
                                  fill=False, edgecolor='red', linewidth=1.5, linestyle='--')
            ax.add_patch(rect_right)
    
    plt.tight_layout()
    plt.savefig('texture_padding_visualization.png', dpi=150, bbox_inches='tight', facecolor='white')
    print("Zapisano: texture_padding_visualization.png")
    plt.close()

def create_comparison_stretch_vs_padding():
    """Porównanie: rozciąganie vs tiling vs padding."""
    
    texture = load_texture('BloodAltar_Top')
    if texture is None:
        return
    
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    fig.suptitle('Porównanie metod teksturowania dla dużych ścian cięcia', 
                 fontsize=14, fontweight='bold')
    
    target_size = (32, 32)  # 2x większa niż oryginał
    
    # 1. Rozciąganie (STRETCH) - ŹLE
    ax1 = axes[0]
    stretched = Image.fromarray(texture).resize(target_size[::-1], Image.BILINEAR)
    ax1.imshow(stretched)
    ax1.set_title('❌ ROZCIĄGANIE (stretch)\nTekstura rozmyta!', 
                 fontsize=11, fontweight='bold', color='red')
    ax1.axis('off')
    
    # 2. Tiling - nie najlepsze dla tego zastosowania
    ax2 = axes[1]
    tiled = np.tile(texture, (2, 2, 1))
    ax2.imshow(tiled)
    ax2.set_title('⚠️ TILING (repeat)\nWidać szwy!', 
                 fontsize=11, fontweight='bold', color='orange')
    ax2.axis('off')
    
    # 3. Padding - DOBRZE
    ax3 = axes[2]
    padded = apply_padding(texture, target_size)
    ax3.imshow(padded)
    ax3.set_title('✅ PADDING (clamp)\nBrzegowe piksele!', 
                 fontsize=11, fontweight='bold', color='green')
    ax3.axis('off')
    
    # Dodaj oznaczenia
    h, w = texture.shape[:2]
    offset = (target_size[0] - h) // 2
    rect = Rectangle((offset-0.5, offset-0.5), w, h, 
                     fill=False, edgecolor='blue', linewidth=2)
    ax3.add_patch(rect)
    ax3.text(16, 16, 'ORYGINAŁ', ha='center', va='center', 
            fontsize=8, color='blue', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # 4. Legenda
    ax4 = axes[3]
    ax4.text(0.5, 0.9, 'DLACZEGO PADDING?', ha='center', va='top',
            fontsize=12, fontweight='bold', transform=ax4.transAxes)
    
    explanation = (
        "Ściana cięcia może być większa\n"
        "niż 1x1 (np. √2 ≈ 1.41x)\n\n"
        "ROZCIĄGANIE:\n"
        "• Tekstura rozmyta\n"
        "• Tracone szczegóły\n\n"
        "TILING:\n"
        "• Widać szwy między kafelkami\n"
        "• Nienaturalny wzór\n\n"
        "PADDING:\n"
        "• Tekstura w oryginalnej skali\n"
        "• Brzegowe piksele wypełniają\n"
        "  większą powierzchnię\n"
        "• Efekt 'clamp to edge'"
    )
    
    ax4.text(0.5, 0.5, explanation, ha='center', va='center',
            fontsize=10, transform=ax4.transAxes, family='monospace')
    ax4.axis('off')
    
    plt.tight_layout()
    plt.savefig('stretch_vs_padding_comparison.png', dpi=150, bbox_inches='tight', facecolor='white')
    print("Zapisano: stretch_vs_padding_comparison.png")
    plt.close()

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("Generowanie wizualizacji paddingu tekstur...")
    create_padding_visualization()
    create_comparison_stretch_vs_padding()
    print("\nGotowe! Pokazano efekt paddingu (clamp to edge)")
