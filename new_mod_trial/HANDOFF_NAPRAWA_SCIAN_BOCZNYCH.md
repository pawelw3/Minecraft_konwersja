# Handoff: Naprawa renderowania ścian bocznych (clipping)

## Podsumowanie sesji
Wprowadzono kompletną przebudowę renderowania ścian bocznych przyciętych bloków. Zamiast binarnej decyzji "cała ściana lub nic" (opartej na teście środka ściany), nowa implementacja używa algorytmu Sutherland-Hodgman do przycinania każdej z 6 ścian sześcianu płaszczyzną cięcia.

## Problem
- Ściany boczne były wyświetlane jako pełne kwadraty albo w ogóle
- Krawędzie ścian bocznych nie pokrywały się z krawędzią ukośnej ściany (cut face)
- Widoczny "próg" - gdy zachowany fragment miał mniej niż ~½ pola, ściana znikała

## Rozwiązanie

### Nowe metody w AdvancedCutRenderer.java

#### 1. `planeDist(px, py, pz, nx, ny, nz)`
Oblicza podpisany dystans punktu od płaszczyzny cięcia.

#### 2. `keepSide(dist, keepPositive, eps)`
Decyduje czy punkt powinien być zachowany po danej stronie płaszczyzny.

#### 3. `clipPolygonByPlane(poly, nx, ny, nz, keepPositive)`
Główny algorytm Sutherland-Hodgman do przycinania wielokąta płaszczyzną.
- Przetwarza każdą krawędź wielokąta
- Dodaje punkty przecięcia gdy krawędź przecina płaszczyznę
- Zachowuje tylko punkty po stronie "keep"

#### 4. `intersectEdgeWithPlane(A, B, dA, dB)`
Oblicza punkt przecięcia odcinka z płaszczyzną.

#### 5. `getFacePolygon(side)`
Zwraca 4 wierzchołki danej ściany sześcianu w kolejności CCW:
- 0: BOTTOM (y=0)
- 1: TOP (y=1)
- 2: NORTH (z=0)
- 3: SOUTH (z=1)
- 4: WEST (x=0)
- 5: EAST (x=1)

#### 6. `getFaceNormal(side)`
Zwraca oczekiwaną normalną dla danej ściany (do korekty windingu).

#### 7. `getUVForPoint(p, side)`
Mapuje punkt 3D na współrzędne UV [0,1] dla danej ściany:
- BOTTOM/TOP: u=x, v=z
- NORTH/SOUTH: u=x, v=1-y
- WEST/EAST: u=z, v=1-y

#### 8. `renderClippedCubeFaces(renderer, originalBlock, x, y, z, meta, nx, ny, nz, keepPositive)`
Główna metoda renderująca wszystkie 6 ścian z clippingiem:
1. Dla każdej ściany (0-5):
   - Pobiera bazowy wielokąt (4 wierzchołki)
   - Przycina płaszczyzną (`clipPolygonByPlane`)
   - Usuwa duplikaty (`deduplicatePoints`)
   - Usuwa zamykający punkt jeśli taki sam jak pierwszy
   - Jeśli ≥3 wierzchołki: koryguje winding i renderuje

#### 9. `ensureFaceWinding(poly, expectedNormal)`
Sprawdza czy normalna wielokąta pokrywa się z oczekiwaną. Jeśli nie - odwraca kolejność wierzchołków.

#### 10. `renderClippedPolygon(poly, side, icon, x, y, z, brightness, r, g, b)`
Renderuje przycięty wielokąt jako fan trójkątów z degenerowanymi quadami (A,B,C,C).

### Zmiany w istniejących metodach

#### `renderAdvancedCut(...)` - linia ~52
Zamieniono:
```java
// STARE:
renderVisibleFaces(renderer, originalBlock, x, y, z, meta, nx, ny, nz, keepPositive);

// NOWE:
renderClippedCubeFaces(renderer, originalBlock, x, y, z, meta, nx, ny, nz, keepPositive);
```

#### `renderVisibleFaces(...)` 
Oznaczona jako `@Deprecated` - nie jest już używana.

## Efekty zmian

### Przed:
- Ściany albo pełne, albo niewidoczne
- Brak wspólnej krawędzi z cut face
- "Próg" przy 50% zachowanego pola

### Po:
- Każda ściana jest dokładnie przycięta do kształtu zachowanego fragmentu
- Wspólna krawędź z cut face (brak szczelin)
- Widoczne nawet małe fragmenty ścian
- Poprawne UV/tekstury na przyciętych fragmentach

## Plik wyjściowy
- `CuttableBlocks-1.0.0_FIXED.jar` (40.17 KB) - zawiera wszystkie poprawki

## Testy do wykonania

1. **Test geometryczny**: Postaw ukośny blok i obejdź dookoła. Każda widoczna ściana boczna powinna być przycięta i mieć wspólną krawędź z cut-face.

2. **Test małego fragmentu**: Wymuś cięcie tak, żeby zostawał mały klin na jednej ścianie. Ten klin musi być widoczny.

3. **Test stabilności**: Postaw 20 ukośnych bloków obok siebie. Nie może powstawać żadna płachta ani szpilki.

## Możliwe dalsze usprawnienia

1. **Flip UV**: Jeśli tekstury na niektórych ścianach są lustrzane, wystarczy zmienić `u = 1 - u` lub `v = 1 - v` w `getUVForPoint` dla danej ściany.

2. **Wydajność**: Dla osiowych cięć (proste pół-bloki) można przywrócić uproszczoną ścieżkę renderowania.

3. **Kolizja**: Obecnie kolizja nadal używa pełnego AABB - można by dodać dokładniejszą kolizję dla przyciętych kształtów.

## Referencje
- Instrukcja naprawy: `bugs/2/instrukcja_naprawa_boczne_sciany_clipping.md`
- Screeny problemu: `bugs/2/*.png`
