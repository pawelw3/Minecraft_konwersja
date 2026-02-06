# Naprawa artefaktów renderowania ukośnych cięć (Minecraft 1.7.10 / Forge) — instrukcja dla agenta

Ten dokument opisuje **konkretne kroki naprawy** problemów, które widzisz przy ukośnych (diagonalnych) cięciach:
- „przezroczyste” lub znikające ściany (zła strona / backface),
- losowe, długie „płachty” łączące się między kolejnymi blokami,
- wierzchołki jednej bryły „podpinające się” pod następną.

Kod, którego dotyczą poprawki, jest głównie w:
- `client/render/AdvancedCutRenderer.java` (render ukośnych cięć),
- `client/render/RenderHelper.java` (router: axis-aligned vs advanced),
- opcjonalnie `util/Plane.java` (lepsze przecięcia + deduplikacja),
- `items/ItemCuttingTool.java` i `tileentities/TileEntityCuttable.java` tylko do testów/diagnostyki.

---

## 0) TL;DR: Dlaczego to się psuje?

### A. Największy błąd: wysyłasz trójkąty do Tessellatora, który renderuje quady
W `AdvancedCutRenderer#renderCutFace(...)` robisz triangulację wielokąta i dodajesz **3 wierzchołki** na trójkąt (triangle fan).  
W renderowaniu bloków w świecie `Tessellator` w MC 1.7.10 jest zwykle w trybie **GL_QUADS** (batchuje po 4 wierzchołki = 1 quad).

**Skutek**: twoje „paczki po 3” nie są domykane. 4‑ty wierzchołek quada zostaje „pożyczony” z kolejnego trójkąta albo nawet kolejnego bloku (renderowanego później w tym samym batchu).  
To daje:
- długie płachty,
- łączenie z poprzednim/następnym blokiem,
- losowe ściany.

### B. Drugi błąd: sortowanie wierzchołków jest niepoprawne dla dowolnej płaszczyzny
`sortPointsByAngle` używa `atan2` w rzucie na jedną z osiowych płaszczyzn albo nawet tylko XY.
Dla dowolnie nachylonej płaszczyzny to bywa błędne → wielokąt ma zły „winding” (CW/CCW) lub samoprzecinające się kolejności.

**Skutek**: culling/backface sprawia, że część ścian znika („przezroczystość” jednej ściany lub większości).

### C. Dodatkowo: brak deduplikacji punktów przecięć
Gdy płaszczyzna trafia idealnie w wierzchołek sześcianu albo krawędź, algorytm może dodać ten sam punkt kilka razy (bo kilka krawędzi ma ten sam punkt przecięcia).  
To pogarsza sortowanie i triangulację.

---

## 1) Cel naprawy (definicja „DONE”)

Naprawa jest zakończona, gdy:
1. Render ukośnych cięć **nie generuje** długich płacht ani łączeń między różnymi blokami, nawet gdy postawisz kilkanaście takich bloków obok siebie.
2. Cut face (płaszczyzna przekroju) **zawsze** jest widoczna z poprawnej strony (a nie znika losowo).
3. Widoczne „oryginalne” ściany sześcianu (te, które zostają po cięciu) nie mają losowych zaników.
4. Patch nie psuje axis-aligned half-blocków (render prosty) oraz nie wymaga przebudowy całego systemu renderowania.

---

## 2) Plan naprawy — kolejność wdrożenia

Wdrażaj po kolei. Po każdym kroku testuj.

1) **Emitowanie QUADów zamiast TRIANGLE fan** w `AdvancedCutRenderer#renderCutFace(...)`  
   (największy efekt: usuwa łączenie wierzchołków między blokami).

2) **Stabilne sortowanie wierzchołków na płaszczyźnie cięcia + wymuszenie windingu**  
   (największy efekt: usuwa znikające/„przezroczyste” ściany).

3) **Deduplikacja punktów przecięć** (epsilon merge) przed sortowaniem.

4) (Opcjonalnie) użycie `Plane.getIntersectionsWithUnitCube(...)` jako wspólnego źródła logiki przecięć, żeby uniknąć rozjazdów.

---

## 3) Krok 1 — QUADS zamiast TRIANGLES (blokuje „płachty” i łączenia)

### 3.1 Co zmieniamy
W `AdvancedCutRenderer#renderCutFace(...)` są pętle:

```java
for (int i = 1; i < sortedPoints.size() - 1; i++) {
    addVertex(... p0 ...)
    addVertex(... pi ...)
    addVertex(... pi+1 ...)
}
```

To generuje **trójkąty**, ale Tessellator w świecie oczekuje **quadów**.

### 3.2 Najprostsza poprawka bez rozwalania batchingu
Każdy trójkąt zamień na „degenerowany quad” przez duplikat ostatniego wierzchołka:
- zamiast `A, B, C`
- dodaj `A, B, C, C`

Daje to quad o zerowym polu na jednym boku, który w praktyce renderuje się jak trójkąt, ale **liczba wierzchołków jest wielokrotnością 4**.

#### Implementacja
W obu miejscach (gałąź `addVertexWithTiledCenteredUV(...)` oraz gałąź `addVertexWithClippedUV(...)`) zrób:

- Dodaj czwarty wierzchołek równy trzeciemu.

Przykład (pseudo‑patch):

```java
for (int i = 1; i < sortedPoints.size() - 1; i++) {
    Vec3 a = sortedPoints.get(0);
    Vec3 b = sortedPoints.get(i);
    Vec3 c = sortedPoints.get(i + 1);

    addVertexWithClippedUV(... a ...);
    addVertexWithClippedUV(... b ...);
    addVertexWithClippedUV(... c ...);
    addVertexWithClippedUV(... c ...); // DUPE: domyka QUAD
}
```

Analogicznie w `addVertexWithTiledCenteredUV(...)`.

### 3.3 Test po kroku 1
- Postaw 20 ukośnych cięć w linii.
- Poruszaj kamerą, oddal się i przybliż.
- „Płachty” łączące się między blokami powinny zniknąć całkowicie.
- Jeśli dalej widzisz długie trójkąty między blokami: upewnij się, że **wszystkie** ścieżki dodawania wierzchołków w `renderCutFace` kończą się liczbą wierzchołków podzielną przez 4.

---

## 4) Krok 2 — poprawne sortowanie punktów na płaszczyźnie cięcia + winding

To naprawia „złą stronę / przezroczystość”.

### 4.1 Problem w aktualnym kodzie
Aktualnie `sortPointsByAngle(...)` w `AdvancedCutRenderer` sortuje po `atan2(dy, dx)` w przestrzeni świata, często w rzucie na XY (lub inny prosty rzut).  
To działa tylko dla płaszczyzn prawie równoległych do osi.

Dla dowolnej normalnej wielokąt może dostać:
- odwrócony winding (CW zamiast CCW),
- samoprzecinającą się kolejność,
- losowe różnice zależne od epsilonów i kolejności punktów.

### 4.2 Docelowe rozwiązanie: rzut na bazę płaszczyzny (tangent/bitangent)
Z normalnej `n = (nx, ny, nz)` budujemy dwa wektory leżące na płaszczyźnie:
- `t` (tangent),
- `b` (bitangent),
tak żeby `{t, b, n}` tworzyły ortonormalną bazę.

#### Algorytm budowy bazy
1. Wybierz „pomocniczy” wektor `a` nie równoległy do `n`, np.:
   - jeśli `abs(ny) < 0.99` → `a=(0,1,0)`
   - w przeciwnym razie → `a=(1,0,0)`

2. `t = normalize(cross(a, n))`
3. `b = cross(n, t)` (już znormalizowany jeśli `n` i `t` są)

#### Rzut punktu na 2D
Dla punktu `p` i środka `c`:
- `v = p - c`
- `u = dot(v, t)`
- `w = dot(v, b)`
- kąt = `atan2(w, u)`

Sortujesz rosnąco po tym kącie.

### 4.3 Wymuszenie poprawnego windingu (bardzo ważne)
Nawet przy dobrym sortowaniu, czasem (zależnie od definicji strony „keepPositive”) chcesz odwrócić kolejność, aby normalna wielokąta była zgodna z tym, co uznajesz za „front face”.

Zrób tak:
1. Po sortowaniu weź trzy kolejne punkty `p0, p1, p2`.
2. Policz normalną wielokąta:
   - `polyN = normalize(cross(p1-p0, p2-p0))`
3. Sprawdź znak z oczekiwaną normalną:
   - jeśli cut face ma „patrzeć” w stronę `n`, to oczekujesz `dot(polyN, n) > 0`
   - jeśli ma patrzeć w stronę `-n`, to oczekujesz `dot(polyN, n) < 0`
4. Gdy znak nie pasuje → `Collections.reverse(sortedPoints)`.

#### Jak zdecydować, czy cut face ma patrzeć w stronę `n` czy `-n`?
Masz w TE informację `keepPositiveSide`. W praktyce:
- geometrycznie „zachowana bryła” to strona, dla której `planeDist` ma odpowiedni znak.
- cut face jest nową „zewnętrzną” ścianą tej zachowanej bryły, więc **jej zewnętrzna normalna** powinna wskazywać _na zewnątrz_ bryły.

Najprostsze (działa i daje stabilność):  
**Zawsze orientuj cut face tak, by normalna polygonu wskazywała w stronę „odciętej” części** (czyli odwrotnie do strony zachowanej), wtedy kamera stojąca „na zewnątrz” zwykle zobaczy ją poprawnie.  
Jeśli w Twojej grze użytkownik częściej stoi po stronie zachowanej, odwróć regułę.

Praktyczny test:
- po implementacji, jeżeli cut face znika gdy stoisz po jednej stronie, a jest widoczna po drugiej, odwróć warunek (zamień `reverse`/brak `reverse`).

### 4.4 Gdzie to wdrożyć
W `AdvancedCutRenderer.java`:
- zastąp `sortPointsByAngle(...)` implementacją opartą o tangent/bitangent,
- po sortowaniu wykonaj check windingu i ewentualny reverse.

**Uwaga**: w projekcie jest też drugi sorter w `CutFaceRenderer.java`. Jeżeli ten renderer kiedykolwiek będzie używany do ukośnych cut face, warto go ujednolicić tym samym algorytmem.

### 4.5 Test po kroku 2
- Postaw ukośny blok i obejdź go dookoła.
- Cut face ma być widoczna z zewnątrz tak samo dla różnych normalnych (patrzenie w górę, w dół, pod kątem).
- Jeśli znika tylko z jednej strony: problem to winding/culling → popraw regułę reverse.

---

## 5) Krok 3 — deduplikacja punktów przecięć (stabilność)

### 5.1 Problem
`calculateIntersections(...)` w `AdvancedCutRenderer` sprawdza 12 krawędzi i dodaje punkt, jeśli parametr `t` mieści się w [0,1].  
Gdy płaszczyzna trafia w narożnik, ten sam punkt może pojawić się wielokrotnie (z różnych krawędzi).

### 5.2 Rozwiązanie: merge punktów w epsilonie
Zrób funkcję:

- Wejście: `List<Vec3> raw`
- Wyjście: `List<Vec3> unique`

Logika:
- iteruj po `raw`,
- dla każdego punktu sprawdź, czy już masz punkt w `unique` w promieniu `eps` (np. `1e-5` albo `1e-4`),
- jeśli nie ma → dodaj,
- jeśli jest → pomiń.

Odległość możesz liczyć jako:
- `dx*dx + dy*dy + dz*dz < eps*eps` (szybciej).

### 5.3 Gdzie wpiąć
W `renderAdvancedCut(...)`:
- po `calculateIntersections(...)` wykonaj deduplikację,
- dopiero potem `if (points.size() < 3) return false;`,
- i dopiero potem sortowanie.

### 5.4 Test po kroku 3
- Przetestuj normalne bliskie osi (np. (0.99, 0.01, 0.01)) i bardzo „równe” diagonalne (np. (0.577, 0.577, 0.577)).
- Render nie powinien „wariować” w zależności od mikrozmian w wektorze.

---

## 6) Krok 4 (opcjonalny) — ujednolicenie z `Plane.java`

W projekcie istnieje `util/Plane.java` z funkcją `getIntersectionsWithUnitCube(...)`, która robi podobne obliczenia.  
Możesz:
- użyć jej w `AdvancedCutRenderer` zamiast własnego `calculateIntersections`,
- dzięki temu utrzymujesz jedną implementację.

Jeżeli to zrobisz:
- dodaj deduplikację i tak (Plane też może zwracać duplikaty),
- upewnij się, że punkty wracają w tych samych współrzędnych [0..1].

---

## 7) Dodatkowe wskazówki/debug (opcjonalnie, ale ułatwia)

### 7.1 Debug wierzchołków i ich liczby
W `renderCutFace` tuż przed dodawaniem wierzchołków:
- wypisz do loga (albo do chat w trybie dev) `sortedPoints.size()` i spodziewaną liczbę wierzchołków wysyłanych do tessellatora.

Po kroku 1:
- liczba dodanych wierzchołków = `(sortedPoints.size() - 2) * 4`
- i MUSI być wielokrotnością 4.

### 7.2 Debug windingu
Wypisz:
- `polyN` oraz `n`,
- `dot(polyN, n)`,
- i informację czy wykonano `reverse`.

To szybko pokaże, czy znikanie ścian wynika z odwróconego windingu.

### 7.3 Uwaga: RenderBlocks może czasem rysować część ścian jako „standard”
W `renderVisibleFaces(...)` rysujesz 6 ścian sześcianu, ale tylko te „po stronie keep”.  
Upewnij się, że logika `isPointOnKeepSide(...)` ma spójny epsilon i nie przeskakuje przy bardzo małych odchyleniach normalnej (tu jest `checkDist` 0.001).  
Jeśli ściany potrafią migać przy minimalnych zmianach normalnej, rozważ stabilniejsze `epsilon` albo dokładniejszy test (np. kilka punktów na ścianie).

---

## 8) Checklist wdrożenia (dla agenta)

1. [ ] Zmiana w `AdvancedCutRenderer#renderCutFace`: każda triangulacja → degenerowane quady (A,B,C,C).  
2. [ ] W `AdvancedCutRenderer#sortPointsByAngle`: implementacja sortowania na bazie tangent/bitangent.  
3. [ ] Po sortowaniu: sprawdzanie windingu (cross) i ewentualne `reverse`.  
4. [ ] Deduplikacja punktów przecięć przed sortowaniem (epsilon merge).  
5. [ ] Testy: seria bloków, różne normalne, obejście dookoła, brak płacht i brak znikających ścian.  
6. [ ] (Opcjonalnie) Ujednolicenie przecięć z `util/Plane.java`.

---

## 9) Minimalny zestaw testów manualnych

Wykonaj w świecie testowym:

1) Normalne losowe:
- stawiasz 10 bloków,
- za każdym razem celujesz w inny kierunek,
- nie może powstać żadna „płachta” między blokami.

2) Normalne prawie osiowe:
- (0.98, 0.10, 0.00), (0.00, 0.98, 0.10), (0.10, 0.00, 0.98)
- nie może migać.

3) Normalna diagonalna „równa”:
- (0.577, 0.577, 0.577) (czyli normalize(1,1,1))
- cut face musi być stabilna i poprawnie widoczna.

4) Normalna z ujemnymi składowymi:
- (-0.6, 0.2, -0.77) (zależnie od lookVec)
- brak zaniku ścian.

---

## 10) Notatka o dalszym rozwoju (po naprawie)
Po wyeliminowaniu artefaktów renderu warto rozważyć:
- poprawną kolizję dla ukośnych brył (obecnie AABB pełny blok),
- przenoszenie danych TileEntity oryginalnych bloków (na razie cięcie niszczy TE).

To jednak nie jest wymagane do naprawienia opisanych artefaktów renderowania.
