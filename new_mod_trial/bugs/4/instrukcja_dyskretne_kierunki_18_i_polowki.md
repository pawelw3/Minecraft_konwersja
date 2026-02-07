# Instrukcja: dyskretny zbiór kierunków (18 klas) + aproksymacja lookVec oraz naprawa błędu „dokładnych połówek”

Ten dokument opisuje jak zmodyfikować mod, aby:
1) cięcie zawsze przechodziło przez **geometryczny środek bloku** (jak dotąd),
2) normalna płaszczyzny była **aproksymowana** do **dyskretnego zbioru kierunków** (18 klas),
3) w TileEntity zapisywać tylko **rotację + id kierunku + keepPositive**,
4) naprawić błędy renderowania dla przypadków „dokładnych połówek” (znikające ściany, zielony tint, miganie na czarno).

Zakładam, że nadal renderujesz:
- proste cięcia osiowe (`RenderHelper.renderHorizontalCut`, `renderXCut`, `renderZCut`) dla prawie osiowych normalnych,
- ukośne cięcia przez `AdvancedCutRenderer` dla reszty.

---

## 0) Założenia i terminologia

- Pracujemy w lokalnych współrzędnych bloku `p = (x,y,z)` w zakresie `[0..1]`.
- Środek bloku: `C = (0.5,0.5,0.5)`.
- Płaszczyzna cięcia zawsze przechodzi przez C:
  - `n · (p - C) = 0`
  - równoważnie `n·p = d`, gdzie `d = n·C = 0.5*(nx+ny+nz)`

**Dyskretność** ma dotyczyć tylko **kierunku normalnej** `n`, nie przesunięcia `d`.

---

## 1) Dodaj dyskretny zbiór kierunków (18 klas)

### 1.1 Reprezentanty 18 klas (kanoniczne wektory całkowite)
Wprowadź stałą tablicę w kodzie (np. `CutDirections.java` lub w `ItemCuttingTool` / `AdvancedCutRenderer`):

> Uwaga: to są reprezentanty „klas pod rotacjami sześcianu” – w runtime możesz je obracać rotacją bloku.

```java
public static final int[][] BASE_DIRS_18 = new int[][] {
    {-1,  0,  0},
    {-1, -1,  0},
    {-1, -1, -1},

    {-2, -1,  0},
    {-2, -1, -1},
    {-2, -2, -1},

    {-4, -1,  0},
    {-4, -1, -1},
    {-4, -2,  1},
    {-4, -2, -1},
    {-4, -4, -1},

    {-8, -1,  0},
    {-8, -1, -1},
    {-8, -2,  1},
    {-8, -2, -1},
    {-8, -4,  1},
    {-8, -4, -1},
    {-8, -8, -1}
};
```

### 1.2 Normalizacja do floata
Zrób helper:

```java
public static Vec3 normalizeIntDir(int a, int b, int c) {
    double len = Math.sqrt(a*a + b*b + c*c);
    return Vec3.createVectorHelper(a/len, b/len, c/len);
}
```

*(Możesz też trzymać od razu znormalizowane `float[]`.)*

---

## 2) Rotacja bloku jako ID 0..23 (opcjonalne, ale zalecane)

Jeśli chcesz kompresować warianty TE, przechowuj orientację bloku jako `rotId` (24 możliwe rotacje sześcianu, det=+1).

### 2.1 Najprostsza reprezentacja rotacji: permutacja osi + znaki
Zdefiniuj `Rot` jako:
- `perm[3]` – skąd bierzesz komponenty (0=X,1=Y,2=Z),
- `sign[3]` – +1 lub -1.

Wtedy:
```java
// v = (x,y,z)
out[i] = sign[i] * v[ perm[i] ]
```

Zbuduj listę wszystkich 24 rotacji:
- wszystkie permutacje osi (6),
- dla każdej permutacji wszystkie kombinacje znaków (8),
- zostaw tylko te z wyznacznikiem +1 (czyli 24).

Możesz wygenerować tę listę offline i wkleić jako stałą tablicę, albo wygenerować w runtime podczas init.

> Jeśli Twój blok i tak nie ma rotacji (zawsze „tak samo” w świecie), możesz pominąć `rotId` i zapisywać tylko `dirId + keepPositive`. Ale skoro chcesz mieć „rotację jak TE”, to `rotId` jest OK.

### 2.2 Zastosowanie rotacji do normalnej
- `nWorld = R(rotId) * nLocal`
- `nLocal = R(rotId)^{-1} * nWorld` (dla wyboru najbliższego kierunku)

Dla rotacji opartej o perm+sign, inverse jest łatwe do wyliczenia (odwrócenie permutacji i odpowiednie znaki).

---

## 3) Aproksymacja lookVec → (rotId, dirId)

### 3.1 Wybór rotId
Opcje:
1) Jeśli rotacja wynika z metadanych/TE/Twojego bloku — użyj jej.
2) Jeśli blok nie ma rotacji — ustaw `rotId = 0`.

### 3.2 Sprowadzenie lookVec do przestrzeni lokalnej
W `ItemCuttingTool.onItemUse`:

1) policz `look = player.getLookVec()` i znormalizuj → `nWorld`.
2) policz `nLocal = inverseRotate(rotId, nWorld)`.

### 3.3 Wybór najbliższego dyskretnego kierunku
Policz dot-product z każdą bazową normalną:

```java
int bestId = 0;
double bestDot = -1e9;
for (int i=0; i<BASE_DIRS_18.length; i++) {
    Vec3 b = normalizeIntDir(BASE_DIRS_18[i][0], BASE_DIRS_18[i][1], BASE_DIRS_18[i][2]);
    double d = nLocal.xCoord*b.xCoord + nLocal.yCoord*b.yCoord + nLocal.zCoord*b.zCoord;
    if (d > bestDot) { bestDot = d; bestId = i; }
}
dirId = bestId;
```

> To jest stabilne: zawsze wybierasz najbliższy „katalogowy” kierunek.

### 3.4 Zapis do TileEntity
W TE zapisujesz:
- `byte rotId`
- `byte dirId`
- `boolean keepPositive`

Normalną `normalX/Y/Z` możesz:
- albo nadal trzymać jako float (redundantne),
- albo **wyliczać na żywo w rendererze** z `(rotId,dirId)` (zalecane).

---

## 4) Rekonstrukcja normalnej w rendererze i logice

W `AdvancedCutRenderer` (i wszędzie gdzie używasz normalnej):
1) `Vec3 nBase = normalizeIntDir(BASE_DIRS_18[dirId])`
2) `Vec3 nWorld = rotate(rotId, nBase)`
3) używaj `nx,ny,nz = nWorld` wszędzie

Parametr `d` (płaszczyzna przez środek) zostaje:
- `d = nx*0.5 + ny*0.5 + nz*0.5` (albo `0.5*(nx+ny+nz)`)

---

# 5) Ile jest wektorów „dla danej rotacji bloku”?
Jeżeli trzymasz bazę w układzie lokalnym i obracasz ją rotacją:
- **na jedną rotację przypada dokładnie 18 kierunków** (dirId 0..17).

Jeżeli dodatkowo utożsamisz `n` i `-n` (i stronę trzymasz w `keepPositive`), możesz zejść do mniejszej liczby, ale **w tej instrukcji zostawiamy 18**, bo jest prostsze do debugowania i stabilniejsze przy porównaniach dot.

---

# 6) Naprawa błędu „dokładnych połówek” (missing faces / zielony tint / czarne miganie)

To, co nazywasz „dokładne połówki”, to w praktyce cięcia, dla których normalna jest osiowa albo prawie osiowa.
Po wprowadzeniu dyskretnych kierunków problem zwykle się nasila, bo często wybierzesz kierunki typu `(-1,0,0)` albo `(-1,-1,0)` i trafisz w przypadki brzegowe.

Poniżej konkretne przyczyny i naprawy.

---

## 6.1 Przyczyna A: ścieżka osiowa vs ukośna wybierana niestabilnie (progi)
Masz w kodzie progi typu:
- „axis aligned jeśli |nx|>0.95 i |ny|<0.05 ...”

Po dyskretyzacji kierunków:
- część kierunków jest idealnie osiowa,
- część bardzo bliska osiowej,
- przy floatach i rotacji potrafi raz wpaść w axis path, raz w advanced path.

### Naprawa
Zrób deterministyczny wybór na podstawie `dirId`, nie na podstawie progów float.

Przykład:
- jeśli `dirId` wskazuje dokładnie wektor osiowy (`(-1,0,0)`, `(0,-1,0)`, `(0,0,-1)` po rotacji) → zawsze używaj osiowego renderera,
- jeśli `dirId` jest „prawie osiowy” (np. `(-2,-1,0)` po rotacji) → decyzja zależy od tego, czy chcesz go traktować jako ukośny.

Najprościej: zrób mapę `dirId -> RenderMode`:
- `AXIS_X`, `AXIS_Y`, `AXIS_Z`, albo `ADVANCED`.

---

## 6.2 Przyczyna B: z-fighting na granicy przy połówkach
W połówkach nowa ściana i pozostałe ściany potrafią spotykać się w sposób, który generuje bardzo cienkie/degenerowane wielokąty.
Jeśli masz clipping ścian, to na granicy (dokładnie na płaszczyźnie) część punktów może wpadać raz „in”, raz „out” (epsilon).

### Naprawa
- Ustal spójny `EPS` (np. `1e-6`) dla:
  - testu strony płaszczyzny,
  - clippingu,
  - deduplikacji punktów.
- Dla cut-face dodaj minimalny offset wzdłuż normalnej (tylko render):
  - `p = p + n * 1e-4` w lokalnych coords
  - to eliminuje miganie na czarno (depth fighting).

---

## 6.3 Przyczyna C: brakujące ściany w osiowym rendererze (half-block)
W wersji osiowej często renderujesz tylko część ścian, ale przy dokładnej połówce musisz mieć:
- poprawne AABB bounds,
- poprawne renderowanie wszystkich „zewnętrznych” ścian,
- plus nową ścianę przekroju.

### Naprawa (render osiowy)
Sprawdź funkcje w `RenderHelper` dla `renderHorizontalCut/renderXCut/renderZCut`:
1) Upewnij się, że renderujesz:
   - wszystkie 5 ścian zewnętrznych zachowanej części,
   - plus ścianę przekroju.
2) W osiowej ścianie przekroju używaj tego samego systemu UV co na bocznych:
   - 1 blok = 16 px,
   - bez rozciągania.

---

## 6.4 Przyczyna D: zielony tint / czarne miganie = dziedziczenie stanu Tessellatora
W MC 1.7.10 jeśli nie ustawisz jawnie koloru/brightness przed każdym face, możesz odziedziczyć kolor z poprzedniego renderu (np. trawa/biome) i dostajesz „zielonkawy” blok.
Czarne miganie bywa efektem brightness=0 na części wierzchołków albo z-fightingu.

### Naprawa
W każdej funkcji renderującej face (zarówno osiowej, jak i advanced):
- ustaw brightness: `tess.setBrightness(...)`
- ustaw kolor na biały lub colorMultiplier:
  - `tess.setColorOpaque_F(1f,1f,1f)` (jeśli nie chcesz tintu)
  - albo dokładnie jak vanilla dla danego bloku/side

I rób to **zawsze** przed dodaniem wierzchołków danej ściany.

---

# 7) Checklist wdrożenia (skrót)

## Dyskretne kierunki
- [ ] Dodaj `BASE_DIRS_18`.
- [ ] Dodaj system `rotId` (0..23) lub ustaw stałe 0.
- [ ] W `ItemCuttingTool`: `lookVec -> nLocal -> dirId` (max dot).
- [ ] W TE: zapisz `rotId, dirId, keepPositive`.
- [ ] W rendererze: rekonstruuj `nWorld` z `(rotId,dirId)`.

## Naprawa połówek
- [ ] Przestań wybierać axis/advanced po progach float; wybieraj deterministycznie po `dirId`.
- [ ] Ujednolić EPS w testach/clippingu/deduplikacji.
- [ ] Dodać mały offset renderowy dla cut-face (anty z-fighting).
- [ ] Ustawić brightness + color przed każdym face (eliminuje zielony/czarny).

---

## 8) Notatki implementacyjne (praktyczne)
- Jeśli chcesz jeszcze mocniej ograniczyć warianty: możesz zmapować 18 → 15 utożsamiając `n` i `-n`, ale wtedy musisz bardzo konsekwentnie używać `keepPositive` jako „wyboru strony”.
- Na start zostaw 18: łatwiej debugować (wiesz, jaki wektor wziąłeś).
