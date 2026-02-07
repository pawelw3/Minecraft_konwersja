# Handoff: Dyskretne cięcia (siatka 1/16) + poprawne UV cut-face

## Podsumowanie sesji
Wprowadzono trzy kluczowe zmiany:
1. **Dyskretne cięcia** - płaszczyzna przechodzi przez punkty na siatce 1/16 (zgodnej z teksturą 16x16)
2. **Poprawne UV na cut-face** - tekstura ma skalę 1:1 z bokami i się powtarza (tiling)
3. **Zawsze zostaje część dalsza od gracza** - niezależnie od strony, gracz zostawia fragment bloku po przeciwnej stronie

## Zmiany w TileEntityCuttable.java

### Nowe pola:
- `double planeD` - pozycja płaszczyzny (n·p = planeD)
- `float anchorX, anchorY, anchorZ` - punkt zaczepienia na siatce 1/16

### Nowa metoda:
```java
setCutData(Block block, int meta, float nx, float ny, float nz, 
           boolean keepPositive, double planeD, 
           float anchorX, float anchorY, float anchorZ)
```

### NBT:
- Zapis/odczyt `planeD`, `anchorX/Y/Z`
- Kompatybilność wsteczna (domyślne wartości dla starych zapisów)

## Zmiany w ItemCuttingTool.java

### Nowa metoda:
```java
private static float snap16(float v) {
    return Math.round(v * 16.0f) / 16.0f;
}
```

### Logika cięcia:
1. **Anchor (p0)** z snap16(hitX/Y/Z):
   - Współrzędne X,Y,Z zaokrąglone do 1/16
   - Współrzędna prostopadła do klikniętej ściany przybita do 0 lub 1
   
2. **Normalna (n)** z lookVec - ciągła (bez zmian)

3. **PlaneD** = n·p0 (dyskretna pozycja płaszczyzny)

4. **Keep side** - ZAWSZE dalsza od gracza:
   ```java
   double playerDist = n·playerLocal - planeD;
   boolean keepPositive = playerDist < 0; // keep opposite side
   ```

## Zmiany w AdvancedCutRenderer.java

### PlaneD zamiast center plane:
- Wszystkie metody `planeDist()` teraz przyjmują `planeD` jako parametr
- Nie używamy już `d = 0.5*(nx+ny+nz)`

### Poprawne UV na cut-face:
```java
// Tangent/bitangent z normalnej
Vec3 tangent = normalize(cross(helper, n));
Vec3 bitangent = normalize(cross(n, tangent));

// Origin w anchorze
Vec3 origin = Vec3.createVectorHelper(anchorX, anchorY, anchorZ);

// UV w pikselach (16 per block) z wrap do [0,16)
double uPx = dot(p - origin, tangent) * 16.0;
double vPx = dot(p - origin, bitangent) * 16.0;
double uTile = wrap16(uPx);
```

## Efekty

### Przed:
- Płaszczyzna zawsze przez środek bloku (0.5, 0.5, 0.5)
- UV cut-face rozciągnięte/niespójne
- Strona zależna od pozycji gracza względem środka

### Po:
- Płaszczyzna "zatrzaskuje się" na siatce 1/16 (piksel tekstury)
- UV cut-face: 1 blok = 16 pikseli, powtarza się dla długości > 1
- Zawsze zostaje część dalsza od gracza (intuicyjne)

## Plik wyjściowy
- `CuttableBlocks-1.0.0_FIXED.jar` (39.58 KB)

## Testy

1. **Dyskretność**: Klikaj w różne miejsca na ścianie - cięcia powinny "skakać" co 1/16 bloku

2. **UV cut-face**: Tekstura na ukośnej ścianie powinna:
   - Mieć tę samą skalę co na bocznych ścianach
   - Powtarzać się (nie rozciągać) dla dłuższych cięć

3. **Strona cięcia**: Zawsze zostaje część dalsza od gracza, niezależnie z której strony klikasz

## Możliwe usprawnienia

1. **Z-fighting**: Jeśli widać migotanie na krawędzi, dodać `p += n * 1e-4` do cut-face

2. **Wybór ikony cut-face**: Obecnie używa `getIcon(0, meta)` - można zmienić na ikonę klikniętej ściany

3. **Dźwięk cząsteczek**: Dodać efekty dźwiękowe przy cięciu
