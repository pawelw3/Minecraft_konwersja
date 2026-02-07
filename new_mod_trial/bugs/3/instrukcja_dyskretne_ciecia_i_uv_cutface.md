# Dyskretne płaszczyzny cięcia (siatka 1/16) + poprawne UV/tiling na ścianie ukośnej

Poniżej jest instrukcja **co konkretnie zmienić w modzie**, żeby:
1) cięcia były **dyskretne** – płaszczyzna przechodzi przez punkty na siatce 1/16 (zgodnej z 16×16 tekstur),
2) tekstura na ścianie ukośnej (cut face) miała **tę samą skalę pikseli** co na ścianach bocznych oraz była **powtarzana (tiled)** tak, żeby pokryć większą powierzchnię (do ~√2).

Dokument jest pisany z myślą o Twojej obecnej architekturze: `ItemCuttingTool` ustawia parametry w `TileEntityCuttable`, a `AdvancedCutRenderer` renderuje geometrię.

---

## A. Dyskretne cięcie: „płaszczyzna przechodzi przez punkty 1/16”

### A1) Co dyskretyzujemy i dlaczego
Żeby cięcie było „minecraftowe”, **nie dyskretyzuj normalnej** (kierunku cięcia) – zostaw normalną ciągłą z `player.getLookVec()`.

Dyskretyzuj **położenie płaszczyzny**, czyli parametr `d` w równaniu:
- `n · p = d`

Wtedy masz ciągły kierunek (ładne kąty), ale płaszczyzna „zatrzaskuje się” na siatce tekstur.

### A2) Dodaj `planeD` do TileEntity (wymagane)
W `TileEntityCuttable` dodaj pole:
```java
public double planeD;
```

Zapis/odczyt do NBT + sync do klienta:
- `writeToNBT`: `tag.setDouble("planeD", planeD);`
- `readFromNBT`: `planeD = tag.getDouble("planeD");`
- do paczki TE (`getDescriptionPacket` / `onDataPacket`) też wchodzi automatycznie, jeśli używasz `writeToNBT` / `readFromNBT` w `getDescriptionPacket`.

> Upewnij się, że renderer **zawsze** bierze `planeD` z TE (nie liczy `d` z `(0.5,0.5,0.5)`).

---

## B. Jak wyznaczyć dyskretną płaszczyznę w `ItemCuttingTool`

### B1) Snap do siatki 1/16
Dodaj helper:
```java
private static float snap16(float v) {
    float s = Math.round(v * 16.0f) / 16.0f;
    if (s < 0f) s = 0f;
    if (s > 1f) s = 1f;
    return s;
}
```

### B2) Punkt zaczepienia `p0` (anchor) na siatce 1/16
Masz w `onItemUse(...)` parametry `hitX, hitY, hitZ` (0..1). Zrób:
```java
float px = snap16(hitX);
float py = snap16(hitY);
float pz = snap16(hitZ);
```

**Wariant rekomendowany (siatka 16×16 na klikniętej ścianie):**  
„Przybij” współrzędną prostopadłą do klikniętej ściany do 0 lub 1. To gwarantuje, że anchor leży na ścianie i jest zgodny z UV:
```java
switch(side) {
  case 0: py = 0f; break; // bottom
  case 1: py = 1f; break; // top
  case 2: pz = 0f; break; // north
  case 3: pz = 1f; break; // south
  case 4: px = 0f; break; // west
  case 5: px = 1f; break; // east
}
```

> Jeśli naprawdę chcesz „tylko punkty na krawędziach”, to dodatkowo przyciągaj jeden z dwóch pozostałych wymiarów do 0/1 (np. gdy `hitX < 1/32` → `px=0`, gdy `hitX > 31/32` → `px=1`). W praktyce siatka 16×16 na ścianie daje najlepszy UX i jest zgodna z teksturą.

### B3) Normalna `n` z lookVec (bez dyskretyzacji)
```java
Vec3 look = player.getLookVec();
double nx = look.xCoord, ny = look.yCoord, nz = look.zCoord;
double len = Math.sqrt(nx*nx + ny*ny + nz*nz);
nx /= len; ny /= len; nz /= len;
```

### B4) Policz `planeD = n·p0` i zapisz do TE
```java
double d = nx*px + ny*py + nz*pz;

te.normalX = (float)nx;
te.normalY = (float)ny;
te.normalZ = (float)nz;
te.planeD = d;
```

### B5) Keep side licz względem nowej płaszczyzny
```java
double plx = player.posX - x;
double ply = (player.posY + player.getEyeHeight()) - y;
double plz = player.posZ - z;
double dist = nx*plx + ny*ply + nz*plz - d;
te.keepPositiveSide = dist >= 0;
```

Na końcu:
- `te.markDirty();`
- `world.markBlockForUpdate(x, y, z);`

---

## C. Zastąp wszędzie „center plane” na `te.planeD`

W rendererze i w logice cięcia **nie wolno** już używać:
- `d = 0.5*(nx+ny+nz)` ani „plane przez (0.5,0.5,0.5)”.

Wszystkie testy „po której stronie” oraz przecięcia krawędzi muszą używać:
- `dist(p) = n·p - te.planeD`

Dotyczy to m.in.:
1) `AdvancedCutRenderer.calculateIntersections(...)`
2) clipowania bocznych ścian (polygon clipping)
3) `isPointOnKeepSide(...)` (jeżeli jeszcze istnieje)

---

# D. Poprawa UV na ścianie ukośnej: skala 1:1 z bokami + powtarzanie do √2

## D1) Wymaganie
- 1 blok długości wzdłuż ściany = 16 „pikseli” tekstury (tak samo jak na ścianie osiowej).
- dla ukośnej ściany (długość do ~√2) tekstura ma się **powtarzać** (tiling), a nie rozciągać.

## D2) Poprawna metoda: tangent/bitangent + UV w pikselach + wrap do 16
Masz normalną `n`. Budujesz bazę płaszczyzny:
- `t` (tangent),
- `b` (bitangent).

### D2.1 Budowa bazy
```java
Vec3 n = Vec3.createVectorHelper(nx, ny, nz).normalize();
Vec3 a = (Math.abs(n.yCoord) < 0.99) ? Vec3.createVectorHelper(0,1,0) : Vec3.createVectorHelper(1,0,0);
Vec3 t = a.crossProduct(n).normalize();
Vec3 b = n.crossProduct(t).normalize();
```

### D2.2 Origin UV (żeby skala i przesunięcie były stabilne)
Najlepiej użyj anchor `p0` (snap16), zapisany w TE jako `anchorX/Y/Z` (opcjonalnie, ale mocno polecane).

Jeśli dodajesz:
```java
public float anchorX, anchorY, anchorZ;
```
to zapisujesz je razem z `planeD`, a w rendererze:
```java
Vec3 origin = Vec3.createVectorHelper(te.anchorX, te.anchorY, te.anchorZ);
```

### D2.3 Wrap do 16 (ważne dla wartości ujemnych)
```java
private static double wrap16(double px) {
    double w = px % 16.0;
    if (w < 0) w += 16.0;
    return w;
}
```

### D2.4 Liczenie UV dla wierzchołka cut-face
Dla punktu `p` (lokalnie 0..1):
1) `v = p - origin`
2) `uBlocks = dot(v, t)`
3) `vBlocks = dot(v, b)`
4) `uPx = uBlocks * 16`
5) `vPx = vBlocks * 16`
6) `uTile = wrap16(uPx)` i `vTile = wrap16(vPx)`
7) `U = icon.getInterpolatedU(uTile)`
8) `V = icon.getInterpolatedV(vTile)`

Czyli 1 jednostka w świecie bloku = 16 jednostek UV (pixeli), a przy długości √2 textura powtórzy się automatycznie.

## D3) Gdzie to wpiąć
W `AdvancedCutRenderer.renderCutFace(...)` (lub helperze dodawania wierzchołków) zamień dotychczasowe mapowanie UV na powyższe.

Najwygodniej:
- stwórz funkcję `addCutFaceVertex(Vec3 pLocal, Vec3 origin, Vec3 t, Vec3 b, IIcon icon, int x,int y,int z)`  
  która doda `tess.addVertexWithUV(x+pLocal.xCoord, y+pLocal.yCoord, z+pLocal.zCoord, U, V)`.

## D4) Wybór ikony dla cut-face
Możesz użyć:
- `originalBlock.getIcon(sideClicked, meta)` (najbardziej intuicyjne),
- albo „najbliższej” strony wg normalnej (największa składowa normalnej).

Skala i tiling będą poprawne niezależnie od tego wyboru.

## D5) Z-fighting na krawędzi (opcjonalnie)
Jeśli po wdrożeniu zobaczysz migotanie na wspólnej krawędzi:
- przesuń *tylko cut-face* minimalnie wzdłuż normalnej: `pLocal += n * 1e-4`,
- albo użyj minimalnie innego eps w clippingu.

---

# E. Minimalna checklista zmian

## E1) Dyskretna płaszczyzna
- [ ] `TileEntityCuttable`: `planeD` + NBT + sync.
- [ ] `ItemCuttingTool`: `p0 = snap16(hit)` + przybicie do `side`.
- [ ] `ItemCuttingTool`: `planeD = dot(n, p0)` → do TE.
- [ ] `ItemCuttingTool`: `keepPositive = sign(n·playerLocal - planeD)` → do TE.
- [ ] Renderer/Clipping: wszędzie `dist = dot(n, p) - te.planeD`.

## E2) UV na cut-face (skala i powtarzanie)
- [ ] Zbuduj `t` i `b` z normalnej.
- [ ] Ustal `origin` (najlepiej anchor zapisany w TE).
- [ ] `uPx/vPx = dot(p-origin, t/b) * 16`.
- [ ] `wrap16` do [0..16).
- [ ] `icon.getInterpolatedU/V(uTile/vTile)`.

---
