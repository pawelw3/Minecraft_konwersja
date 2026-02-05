# Implementacja Texture Padding (Clamp-to-Edge)

## Podsumowanie

Zaimplementowano system **padding** (clamp-to-edge) dla tekstur na ścianach cięcia diagonalnych w CuttableBlocks mod.

## Problem

Ściany cięcia diagonalnego mogą być do **√2 ≈ 1.41x** większe niż standardowy blok. Standardowe podejścia:
- **Rozciąganie (stretch)** - tekstura rozmazana, utrata szczegółów ❌
- **Tiling (repeat)** - widać szwy między kafelkami ❌

## Rozwiązanie: Padding (Clamp-to-Edge)

Tekstura zachowuje **1:1 proporcje pikseli** w centrum, a brzegowe piksele są powielane na zewnątrz:

```
+----------+----------+----------+
|  PADDING | PADDING  |  PADDING |
| (powtórz|(powtórz  | (powtórz |
|  krawędź)| krawędź) |  krawędź)|
+----------+----------+----------+
|  PADDING | ORYGINAŁ |  PADDING |
| (powtórz)|(8x8     | (powtórz |
|  krawędź)| center)  |  krawędź)|
+----------+----------+----------+
|  PADDING | PADDING  |  PADDING |
| (powtórz|(powtórz  | (powtórz |
|  krawędź)| krawędź) |  krawędź)|
+----------+----------+----------+
```

## Pliki zmodyfikowane

### 1. TextureMapper.java
Dodano nowe metody:
- `renderPaddedFace()` - renderowanie ściany z padding
- `renderClippedFace()` - renderowanie wycinka tekstury (dla axis-aligned)
- `renderTiledFace()` - renderowanie z tiling (opcjonalne)
- `clampToEdge()` - funkcja clampująca UV do krawędzi

### 2. AdvancedCutRenderer.java
Zaktualizowano:
- `renderCutFace()` - teraz wybiera tryb teksturowania:
  - Dla ścian axis-aligned: CLIPPED (wycinek)
  - Dla ścian diagonalnych > 16px: PADDED (clamp-to-edge)
- `addVertexWithPaddedUV()` - nowa metoda UV mapping z padding
- `addVertexWithClippedUV()` - nowa metoda UV mapping dla wycinków

## Algorytm Padding

1. **Oblicz bounding box** ściany cięcia
2. **Określ rozmiar** w jednostkach tekstury (16 = 1 blok)
3. **Dla UV coordinates**:
   - Normalizuj pozycję względem centrum (-1 do 1)
   - Przeskaluj przez stosunek rozmiaru (faceSize/16)
   - **Clamp**: wartości < -1 → krawędź min, wartości > 1 → krawędź max
   - Wartości w środku → interpolacja w regionie centralnym (4-12 z 16)

## Kod kluczowy (Java)

```java
// Center region (8x8 pixels in center = positions 4-12)
double uCenterStart = icon.getInterpolatedU(4.0);
double uCenterEnd = icon.getInterpolatedU(12.0);

// Clamp to edge
double tU = (uScaled + 1.0) / 2.0;
if (tU <= 0.0) {
    uFinal = uMin;  // Edge pixel
} else if (tU >= 1.0) {
    uFinal = uMax;  // Edge pixel
} else {
    // Interpolate in center region (maintains 1:1 pixel ratio)
    uFinal = uCenterStart + tU * (uCenterEnd - uCenterStart);
}
```

## Wizualizacje

Wygenerowano wizualizacje w `visualizations/`:
- `texture_padding_visualization.png` - różne rozmiary padding
- `stretch_vs_padding_comparison.png` - porównanie metod

## Status kompilacji

⚠️ **Wymaga Java 8** - ForgeGradle 1.2 dla Minecraft 1.7.10 nie wspiera Java 17.

Aby skompilować:
```powershell
# Ustaw JAVA_HOME na Java 8
$env:JAVA_HOME = "C:\Program Files\Java\jdk1.8.0_XXX"
.\gradlew.bat build
```

## Testowanie w grze

1. Zbuduj mod zgodnie z powyższą instrukcją
2. Umieść JAR w `mods/` serwera 1.7.10
3. Użyj narzędzia do cięcia na bloku BloodAltar
4. Obserwuj ścianę cięcia - powinna mieć padding zamiast rozciągania
