# Instrukcja naprawy renderowania bocznych ścian po ukośnym cięciu (Minecraft 1.7.10 / Forge)

## Problem (objawy)
Po wprowadzeniu poprawek do ukośnej „nowej” ściany (cut face) nadal źle działają „istniejące” ściany kostki:
- boczne ściany pozostają **pełnymi kwadratami** jak w oryginalnym bloku **albo znikają**,
- zachowanie wygląda jak „próg”: gdy zachowany fragment ma mniej niż ~½ pola — ściana znika; gdy więcej — widać pełny kwadrat,
- krawędź bocznej ściany **nie pokrywa się** z krawędzią ukośnej ściany (brak wspólnej krawędzi).

To jest spodziewane przy aktualnej implementacji, bo w `AdvancedCutRenderer.renderVisibleFaces(...)` podejmujesz decyzję *czy renderować całą ścianę* na podstawie **jednego punktu (centrum ściany)**. Jeśli centrum jest po stronie „odciętej” → ściana znika w całości; jeśli po stronie „zachowanej” → rysujesz pełny kwadrat.

**Naprawa wymaga przycinania (clippingu) każdej z 6 ścian sześcianu płaszczyzną cięcia**, a nie testu jednego punktu.

---

## Cel (definicja „DONE”)
1. Dla ukośnego cięcia każda z 6 ścian (które pozostają) jest **przycięta** płaszczyzną cięcia.
2. Każda przycięta ściana ma **wspólną krawędź** z ukośną ścianą (cut face).
3. Żadna ściana nie „znika progowo” tylko dlatego, że jej środek wypadł po złej stronie.
4. UV/tekstury na przyciętych fragmentach odpowiadają ikonom oryginalnego bloku dla danego `side` i `meta`.
5. Brak artefaktów typu „szpilki/płachty” i brak losowego znikania (backface/winding).

---

## Zakres zmian
Zmiany dotyczą głównie:
- `client/render/AdvancedCutRenderer.java`
  - zastąpić `renderVisibleFaces(...)`
  - dodać clipping polygona
  - dodać render wielokąta (fan → degenerowane quady)
  - dodać UV mapping per ściana

Opcjonalnie (ułatwia spójność):
- `util/Plane.java` (gdy chcesz centralizować logikę dystansu/płaszczyzny)

---

## Krok 1 — Usuń logikę „centrum ściany” (to jest źródło progu)

### Co masz teraz (do usunięcia lub ograniczenia tylko do osiowych cięć)
W `AdvancedCutRenderer.renderAdvancedCut(...)` wołasz:
- `renderVisibleFaces(...)`, które:
  - sprawdza `isPointOnKeepSide(centerOfFace)`
  - i jeśli tak → renderuje *pełny* kwadrat ściany, np. `renderTopFace`, `renderNorthFace` itd.

### Co ma być zamiast tego
Dla ukośnych cięć (`renderAdvancedCut`) zamiast `renderVisibleFaces(...)` wywołaj nową funkcję:
- `renderClippedCubeFaces(...)`  
która:
- buduje polygon (4 wierzchołki) dla każdej ściany
- przycina polygon płaszczyzną
- renderuje wynikowy polygon

> Uwaga: dla osiowych cięć (Twoje proste half-blocki) możesz zostawić starą ścieżkę, bo tam i tak używasz osobnych `RenderHelper.renderHorizontalCut / renderXCut / renderZCut`.

---

## Krok 2 — Zdefiniuj spójną płaszczyznę cięcia i funkcję dystansu

W Twoim kodzie płaszczyzna przechodzi przez środek kostki (0.5,0.5,0.5) i ma normalną `(nx,ny,nz)`.

Zdefiniuj helper (w `AdvancedCutRenderer` jako `static` albo w osobnej klasie):

```java
static double planeDist(double px, double py, double pz, float nx, float ny, float nz) {
    // plane: nx*x + ny*y + nz*z = d, gdzie d = dot(n, center)
    double d = 0.5 * (nx + ny + nz);
    return nx * px + ny * py + nz * pz - d;
}
```

I klasyfikacja strony:

```java
static boolean keepSide(double dist, boolean keepPositive, double eps) {
    return keepPositive ? (dist >= -eps) : (dist <= eps);
}
```

Parametry:
- `eps` użyj np. `1e-6` albo `1e-5` (dla stabilności i eliminacji „migania” na granicy).

---

## Krok 3 — Zaimplementuj clipping polygona (Sutherland–Hodgman)

### 3.1 Dane wejściowe
- `List<Vec3> poly` — 4 wierzchołki ściany w lokalnych coords [0..1].
- `nx,ny,nz`, `keepPositive`.
- `eps`.

### 3.2 Funkcja przecięcia odcinka z płaszczyzną
Dla odcinka A→B:

- `da = planeDist(A)`
- `db = planeDist(B)`
- jeśli `(da - db)` jest bardzo małe → odcinek prawie równoległy, w praktyce intersection pomijaj (albo zwracaj A).

Punkt przecięcia:
- `t = da / (da - db)`  (gdy da i db mają różne znaki)
- `P = A + t*(B-A)`

### 3.3 Algorytm clippingu (Sutherland–Hodgman)
Pseudo:

```java
List<Vec3> out = new ArrayList<>();
for each edge (A,B) around poly:
    da = dist(A), db = dist(B)
    ina = keep(da), inb = keep(db)

    if (ina && inb)          out.add(B)
    else if (ina && !inb)    out.add(intersection(A,B))
    else if (!ina && inb)    out.add(intersection(A,B)); out.add(B)
    else                     // none
return out;
```

**Ważne**:
- wejściowy polygon musi mieć poprawną kolejność (CCW patrząc na zewnątrz ściany),
- clipping zachowuje kolejność, jeśli wejście jest poprawne.

---

## Krok 4 — Dedup (scal) punktów po clipie

Po clippingu (zwłaszcza gdy płaszczyzna trafia w wierzchołek) dostaniesz duplikaty lub punkty bardzo blisko siebie.

Dodaj funkcję:
- usuwa punkty, które są bliżej niż `epsMerge` (np. `1e-5`) w metryce kwadratowej,
- dodatkowo usuń punkt końcowy jeśli jest prawie taki sam jak pierwszy (zamknięcie).

To ogranicza „szpilki” i niestabilne triangulacje.

---

## Krok 5 — Renderuj przycięty polygon (>=3 punkty)

### 5.1 Warunek
- jeśli `clipped.size() < 3` → nic nie rysuj
- jeśli `>=3` → renderuj fanem

### 5.2 Uwaga o Tessellatorze w świecie (QUADS)
Jeśli renderujesz w ISBRH, Tessellator zwykle jest w trybie QUADS.  
Dlatego **nie wysyłaj trójkątów (3 wierzchołki)**. Zamiast tego użyj **degenerowanych quadów**:

Dla trójkąta (A,B,C) wyślij:
- A, B, C, C

Pętla:

```java
Vec3 a = poly.get(0);
for (int i = 1; i < poly.size() - 1; i++) {
    Vec3 b = poly.get(i);
    Vec3 c = poly.get(i+1);

    addVertex(a); addVertex(b); addVertex(c); addVertex(c);
}
```

---

## Krok 6 — UV mapping dla przyciętych ścian (musi odpowiadać oryginalnym ścianom)

### 6.1 Zasada
Bierzesz ikonę:
- `IIcon icon = originalBlock.getIcon(side, meta);`

Następnie dla punktu w lokalnych coords (x,y,z w [0..1]) wyznaczasz (u,v) w [0..1] zależnie od ściany.

### 6.2 Mapowanie (prosty, stabilny wariant)
Poniżej standardowe mapowanie (wystarczające i spójne):

- **BOTTOM (side=0, y=0)**: `u = x`, `v = z`
- **TOP (side=1, y=1)**: `u = x`, `v = z`
- **NORTH (side=2, z=0)**: `u = x`, `v = 1 - y`
- **SOUTH (side=3, z=1)**: `u = x`, `v = 1 - y`
- **WEST (side=4, x=0)**: `u = z`, `v = 1 - y`
- **EAST (side=5, x=1)**: `u = z`, `v = 1 - y`

Potem:
- `U = icon.getInterpolatedU(u * 16.0)`
- `V = icon.getInterpolatedV(v * 16.0)`

### 6.3 Uwaga o odwróceniu (flip)
Jeśli po wdrożeniu zauważysz, że tekstura na jednej/dwóch ścianach jest lustrzana, wystarczy zmienić:
- `u = 1 - u` albo `v = 1 - v` dla tej konkretnej ściany.

Najpierw napraw geometrię, dopiero potem dopieszczaj UV.

---

## Krok 7 — Zadbaj o winding (żeby nie znikało przez backface)

Każda ściana ma mieć wierzchołki CCW patrząc „z zewnątrz” sześcianu.

### 7.1 Bazowe wierzchołki dla 6 ścian (local coords)
Poniżej przykład kolejności CCW dla sześcianu [0..1]^3:

- **BOTTOM (y=0)**: (0,0,0) → (1,0,0) → (1,0,1) → (0,0,1)
- **TOP (y=1)**: (0,1,0) → (0,1,1) → (1,1,1) → (1,1,0)
- **NORTH (z=0)**: (0,0,0) → (0,1,0) → (1,1,0) → (1,0,0)
- **SOUTH (z=1)**: (0,0,1) → (1,0,1) → (1,1,1) → (0,1,1)
- **WEST (x=0)**: (0,0,0) → (0,0,1) → (0,1,1) → (0,1,0)
- **EAST (x=1)**: (1,0,0) → (1,1,0) → (1,1,1) → (1,0,1)

Jeśli Twoje ściany po wdrożeniu clippingu znikają z jednej strony:
- policz normalną polygonu (cross) i porównaj z oczekiwaną normalą ściany,
- jeśli znak się nie zgadza → `Collections.reverse(clipped)` przed renderem.

---

## Krok 8 — Integracja w `AdvancedCutRenderer`

### 8.1 Nowa funkcja renderująca wszystkie ściany
Dodaj np.:

- `renderClippedCubeFaces(RenderBlocks renderer, Block original, int x,int y,int z, int meta, float nx, float ny, float nz, boolean keepPositive)`

Wewnątrz:
1. Dla `side` 0..5:
   - zbuduj `List<Vec3> facePoly` (4 wierzchołki lokalne, CCW)
   - `clipped = clip(facePoly, ...)`
   - `clipped = dedup(clipped, ...)`
   - jeśli `clipped.size() >= 3`: `renderClippedFace(clipped, side, icon, x,y,z, brightness, color)`

### 8.2 Skąd wziąć jasność/kolor
W MC 1.7.10 standardowo:
- jasność: `tess.setBrightness(block.getMixedBrightnessForBlock(world, x, y, z))` lub podobnie,
- kolor: zależy czy chcesz `setColorOpaque_F(...)` jak vanilla.

Najprościej:
- skopiuj podejście z Twoich obecnych `renderTopFace/renderNorthFace` (one już ustawiają brightness i color),
- tylko zamień emitowane wierzchołki na te z przyciętego polygona.

---

## Krok 9 — Testy po wdrożeniu

### 9.1 Test geometryczny (najważniejszy)
- Postaw ukośny blok.
- Obejdź dookoła.
- Sprawdź, że każda widoczna ściana boczna jest przycięta i ma krawędź wspólną z cut-face.

### 9.2 Test „mały fragment”
Wymuś cięcie tak, żeby zostawał mały klin na jednej ścianie.
- Ten klin **musi być widoczny**, a nie znikać.

### 9.3 Test stabilności
Postaw 20 ukośnych bloków obok siebie.
- Nie może powstawać żadna płachta ani szpilki.

---

## Najczęstsze pułapki (i jak je rozpoznać)

1) **Wciąż renderuje pełne kwadraty**  
   → znaczy, że nadal wywołujesz starą ścieżkę `renderVisibleFaces(...)` albo gdzieś zostawione `renderer.renderFace...` bez clipu.

2) **Ściany znikają z jednej strony**  
   → winding/backface; odwróć kolejność punktów (reverse) dla tej ściany albo popraw bazową kolejność wierzchołków.

3) **Pojawiają się szpilki / dziwne trójkąty**  
   → brak deduplikacji po clipie albo nadal wysyłasz trójkąty (3 wierzchołki) do Tessellatora w trybie QUADS.

4) **Tekstury są obrócone/lustrzane**  
   → popraw u/v (flip) tylko dla tej ściany; geometria jest OK.

---

## Minimalny zakres zmian, który MUSI być zrobiony
Jeśli chcesz możliwie najmniej ingerencji, to minimum to:

1. W `renderAdvancedCut` zamienić:
   - `renderVisibleFaces(...)` → `renderClippedCubeFaces(...)`

2. Zaimplementować:
   - `clipPolygonByPlane(poly, nx,ny,nz, keepPositive)`
   - `renderClippedPolygonAsDegenerateQuads(poly, side, icon, ...)`
   - `uvForSide(side, x,y,z)` w lokalnych coords

Bez tego boczne ściany **nigdy** nie będą przycinane poprawnie (bo w obecnym podejściu masz tylko: „cała ściana albo nic”).
