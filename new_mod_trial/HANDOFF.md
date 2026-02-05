# Handoff: Wizualizacje Ukośnych Cięć Bloków

## Podsumowanie sesji

Wygenerowano wizualizacje pokazujące różne typy ukośnych cięć bloków (diagonal cuts) z różnymi kątami nachylenia.

## Wygenerowane wizualizacje

### 1. `diagonal_cuts_3d.png`
Pokazuje 6 różnych typów cięć w 3D:
- **Pełny blok** - bez cięcia (referencja)
- **45° XY** - przekątna w płaszczyźnie poziomej
- **45° XZ** - przekątna w płaszczyźnie pionowej XZ
- **45° YZ** - przekątna w płaszczyźnie pionowej YZ
- **60° XYZ** - równomiernie ukośna (wszystkie osie)
- **30° X** - płaska przekątna

Każdy pokazuje:
- Przezroczysty sześcian (kontekst)
- Czerwoną płaszczyznę cięcia
- Żółte punkty przecięcia z krawędziami
- Rozmiar ściany cięcia

### 2. `diagonal_cuts_textured.png`
Ściany cięcia z nałożoną teksturą (tiling centered):
- Pokazuje jak wygląda tekstura na każdej ścianie
- Zielony prostokąt = wycinek wyświetlany
- Rozmiar w pikselach (np. 22.6x16px dla 45°)
- Powtarzalny wzór (seamless tiling)

### 3. `diagonal_cuts_comparison.png`
Porównanie blok 3D vs ściana z teksturą:
- Lewa kolumna: blok z płaszczyzną cięcia
- Prawa kolumna: tekstura na ścianie cięcia
- Pokazuje 3 reprezentatywne przypadki

## Rozmiary ścian cięcia

| Typ cięcia | Rozmiar | Piksele |
|-----------|---------|---------|
| 45° XY/XZ/YZ | √2 × 1 | 22.6 × 16px |
| 60° XYZ | √(2/3) × √(2/3) | 19.6 × 19.6px |
| 30° X | ~1.12 × 1 | 17.9 × 16px |
| 22.5° | ~1.08 × 1 | 17.3 × 16px |

## Algorytm obliczania przecięcia

```python
# Płaszczyzna: nx*x + ny*y + nz*z = d*(nx+ny+nz)
# Sprawdź każdą z 12 krawędzi sześcianu [0,1]³

# Krawędź równoległa do X (y=const, z=const)
t = (d*(nx+ny+nz) - ny*y - nz*z) / nx
if 0 <= t <= 1:
    punkt_przecięcia = (t, y, z)
```

## Pliki

- `diagonal_cuts_showcase.py` - skrypt generujący wizualizacje
- `diagonal_cuts_3d.png` - wizualizacje 3D
- `diagonal_cuts_textured.png` - ściany z teksturą
- `diagonal_cuts_comparison.png` - porównanie 3D vs 2D
