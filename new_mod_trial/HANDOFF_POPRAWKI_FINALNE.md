# Handoff: Poprawki finalne - keepPositive, UV, połówki

## Podsumowanie wprowadzonych poprawek

### 1. Definicja A dla keepPositive
**Definicja:** `keepPositive == true` oznacza zostawienie strony, dla której `dist(p) >= 0`

W `ItemCuttingTool.java`:
```java
// UX: zostaw stronę przeciwną do gracza
// Definicja A: keepPositive == true oznacza keep dist >= 0 side
boolean keepPositive = playerDist < 0;
```

W `AdvancedCutRenderer.java`:
```java
// Użycie zgodne z definicją A
boolean keepTop = (ny > 0) == keepPositive;
boolean keepEast = (nx > 0) == keepPositive;
boolean keepSouth = (nz > 0) == keepPositive;
```

### 2. Stabilne UV na cut-face
- **Origin** = środek bloku `(0.5, 0.5, 0.5)` (spójny "pattern phase")
- **Skala** = 1 blok = 16 pikseli (niezależna od kierunku)
- **Tiling** = wrap16 dla wartości ujemnych
- **Wybór helper** = deterministyczny po największej składowej normalnej

Kod:
```java
// Deterministyczny wybór helpera
double absNx = Math.abs(n.x), absNy = Math.abs(n.y), absNz = Math.abs(n.z);
Vec3 helper;
if (absNx >= absNy && absNx >= absNz) helper = (0,1,0);
else if (absNy >= absNz) helper = (0,0,1);
else helper = (0,1,0);

// UV w pikselach (16 per block)
double uPx = uBlocks * 16.0;
double vPx = vBlocks * 16.0;
double uTile = wrap16(uPx);
```

### 3. Naprawa połówek

#### Deterministyczny wybór trybu
```java
// Bez progów float - sprawdzenie czy DOKŁADNIE osiowy
boolean isAxisY = absNy > 0.999999 && absNx < 0.000001 && absNz < 0.000001;
```

#### Anti z-fighting offset dla osiowych
W `RenderHelper.java` dla wszystkich trzech metod:
```java
// Horizontal
double yOffset = topHalf ? 1e-4 : -1e-4;
tess.addVertexWithUV(x, y + 0.5 + yOffset, z, ...);

// Vertical X
double xOffset = eastHalf ? 1e-4 : -1e-4;
tess.addVertexWithUV(x + 0.5 + xOffset, y, z, ...);

// Vertical Z
double zOffset = southHalf ? 1e-4 : -1e-4;
tess.addVertexWithUV(x, y, z + 0.5 + zOffset, ...);
```

#### Reset koloru i brightness
Ustawiane przed każdą ścianą:
```java
tess.setBrightness(brightness);
tess.setColorOpaque_F(1.0f, 1.0f, 1.0f); // Biały - brak tintu
```

## Pliki wynikowe
```
CuttableBlocks-1.0.0_FIXED.jar       44.56 KB
new_mod_trial_all_java_files.txt    110.04 KB
```

## Testy regresji
1. **Połówki osiowe** - brak migania, komplet ścian
2. **Ukośne** - stała gęstość pikseli na cut-face
3. **Kolor** - brak zielonego tintu obok trawy/liści
