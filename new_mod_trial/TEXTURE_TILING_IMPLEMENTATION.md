# Implementacja Tiling Wycentrowanego (Centered Tiling)

## Podsumowanie

Zaimplementowano system **tiling wycentrowanego** dla tekstur na dużych ścianach cięcia diagonalnego.

## Jak to działa

Zamiast powielać krawędzie (clamp-to-edge), używamy:

1. **Powtarzalny tiling** - tekstura powtarza się w siatce kafelków
2. **Wycinek** - wyświetlamy tylko fragment odpowiadający naszej ścianie
3. **Wycentrowanie** - środek ściany wypada na środku tekstury (8,8)

### Przykład: Ściana 22.6x16 (diagonalna)

```
Tiling 3x2 (48x32 pikseli):
+--------+--------+--------+
|        |        |        |
| Tile   | Tile   | Tile   |
|(-1,1)  | (0,1)  | (1,1)  |
|        |        |        |
+--------+--------+--------+
|XXXXXXXX|XXXXXXXX|XXXXXXXX|
|X Tile X|X Tile X|X Tile X|
|X(-1,0)X|X(0,0) X|X(1,0) X|  <- WYŚWIETLANY FRAGMENT (zielony)
|X      X|X      X|X      X|
+--------+--------+--------+
         ^
         |
    Center tekstury (8,8)
    (środek kafelka 0,0)
```

- Ściana 22.6px szeroka potrzebuje ~1.41 kafelka
- Wyświetlany fragment: od -3.3px do 19.3px (współrzędne tekstury)
- Wzór jest powtarzalny - nie ma szwów!

## Algorytm

```java
// 1. Lokalne współrzędne względem centrum (-0.5 do 0.5)
double uLocal = (vertex.x - center.x) / faceWidth;
double vLocal = (vertex.y - center.y) / faceHeight;

// 2. Przelicz na piksele tekstury
// Center (0) -> 8px (środek tekstury)
// Face extends by faceSize/2 on each side
double uPixelOffset = uLocal * (faceWidth / 2.0);
double vPixelOffset = vLocal * (faceHeight / 2.0);

// 3. Dodaj 8 (środek) i zawijaj (modulo 16)
double uPixel = 8.0 + uPixelOffset;
double vPixel = 8.0 + vPixelOffset;
double uWrapped = ((uPixel % 16.0) + 16.0) % 16.0;  // wrap 0-16
double vWrapped = ((vPixel % 16.0) + 16.0) % 16.0;

// 4. Konwertuj na UV
double uFinal = icon.getInterpolatedU(uWrapped);
double vFinal = icon.getInterpolatedV(vWrapped);
```

## Pliki zmodyfikowane

### AdvancedCutRenderer.java
- `renderCutFace()` - używa tiling centered dla dużych ścian diagonalnych
- `addVertexWithTiledCenteredUV()` - nowa metoda UV mapping

### TextureMapper.java
- `renderTiledCenteredFace()` - alternatywna implementacja

## Wizualizacje

- `tiling_comparison.png` - porównanie: stretch vs clamp vs tiling
- `tiling_centered_visualization.png` - różne rozmiary ścian
- `tiling_uv_mapping.png` - mapowanie UV

## Różnica vs Clamp-to-Edge

| Cecha | Clamp-to-Edge | Tiling Centered |
|-------|---------------|-----------------|
| **Krawędzie** | Powielone piksele | Powtarzalny wzór |
| **Seamless** | Nie (widać krawędzie) | Tak |
| **1:1 pixel ratio** | Tylko w centrum | Cała tekstura |
| **Dla wzorów** | Słabe | Idealne |
