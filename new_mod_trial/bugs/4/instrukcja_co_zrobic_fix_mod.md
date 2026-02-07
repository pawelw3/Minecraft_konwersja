# Plan naprawczy (MD): usunięcie brakujących ścian w połówkach, poprawa kierunków i stała skala UV na cut-face

Ten dokument jest **konkretną checklistą “co zrobić”**, aby doprowadzić mod do stabilnego stanu:
- brakujące ściany / miganie / zielony tint dla **dokładnych połówek**,
- „odwrócone” kierunki (cięcie jakby od rogu i odwrotnie),
- stała skala tekstury na **ukośnej ścianie cięcia** (bez zależności od płaszczyzny).

Najważniejsza zasada: **usuń konkurujące implementacje** (duplikaty klas i kilka sposobów UV), a potem ujednolić jeden kontrakt:
- normalna świata pochodzi zawsze z `(rotId, dirId)`,
- `keepPositive` ma jedną semantykę,
- tryb osiowy vs advanced jest wybierany deterministycznie,
- UV cut-face jest liczone “w pikselach” z projekcji na bazę płaszczyzny + tiling (wrap).

---

## 1) Porządek w projekcie: usuń duplikaty klas (OBOWIĄZKOWE)

W aktualnym źródle masz równolegle różne wersje `ItemCuttingTool` i innych klas w dwóch drzewach katalogów.
To powoduje, że:
- możesz poprawiać jedną wersję,
- a w JAR ląduje inna,
co daje wrażenie “losowego” działania.

### 1.1 Zrób jedno źródło prawdy
- Zostaw tylko `src/main/java/...` jako źródło.
- Usuń / wyłącz w gradle:
  - `new_mod_trial/src/main/java/...` (i podobne alternatywne ścieżki),
  - albo zmodyfikuj `sourceSets` tak, aby kompilowany był tylko jeden katalog.

### 1.2 Weryfikacja
- Zrób clean build.
- Otwórz wygenerowany JAR i sprawdź, że dla każdej klasy (np. `ItemCuttingTool.class`) jest dokładnie **jedna** wersja.

---

## 2) Ujednolić dane TE: zapisuj tylko (rotId, dirId, keepPositive) + blok/meta

W `TileEntityCuttable` docelowo trzymaj:
- `byte rotId`
- `byte dirId`  (0..17)
- `boolean keepPositiveSide`
- `Block originalBlock`
- `int originalMeta`

**Opcjonalnie** (tylko jeśli chcesz stałą “fazę” tekstury zależną od kliknięcia):
- `byte originU, originV` lub `float anchorX/Y/Z` – ale to nie jest wymagane do stałej skali.

### 2.1 Usuń / ignoruj `normalX/Y/Z` jako źródło prawdy
Jeśli nadal istnieją `normalX/Y/Z`:
- zostaw je tylko jako cache/debug,
- renderer ma je **ignorować** i zawsze rekonstruować normalną z `rotId+dirId`.

### 2.2 NBT + sync
Upewnij się, że TE zapisuje i synchronizuje:
- `rotId`, `dirId`, `keepPositiveSide`, `originalBlock`, `originalMeta`
- (opcjonalnie anchor/origin)

---

## 3) Jedna semantyka keepPositive (i tylko jedna)

### 3.1 Wybierz semantykę
Przyjmij:
> `keepPositiveSide == true` oznacza: **zostawiamy stronę, dla której** `dist(p) = n·p - d >= 0`.

To jest kluczowe, bo:
- half-block decyzje `ny>0 == keepPositive` zaczynają działać,
- winding i backface stają się jednoznaczne.

### 3.2 Ustal keepPositive w ItemCuttingTool
W `ItemCuttingTool.onItemUse`:
1) wybierz `(rotId, dirId)` z lookVec (patrz sekcja 4),
2) odtwórz `nWorld`,
3) policz `d = nWorld · C = 0.5*(nx+ny+nz)`,
4) policz dystans gracza:
   - `pl = (player.posX - x, player.posY + eyeHeight - y, player.posZ - z)`
   - `playerDist = nWorld·pl - d`
5) jeśli chcesz “zostaw stronę, gdzie stoi gracz”:
   - `keepPositiveSide = (playerDist >= 0)`
   jeśli chcesz “zostaw stronę przeciwną”:
   - `keepPositiveSide = (playerDist < 0)`

**WAŻNE:** niezależnie od UX, po tej linijce `keepPositiveSide` nadal oznacza “zostaw dist>=0” (czyli wybór strony), a nie zmianę definicji.

---

## 4) Dyskretne kierunki: wybór dirId z lookVec (jedna implementacja)

### 4.1 Zostaw tylko jeden moduł kierunków
Wybierz jako “single source” klasę `CutDirections` (albo analogiczną) i usuń inne konkurujące metody wyboru.

W `CutDirections` trzymaj:
- `BASE_DIRS_18` (18 reprezentantów),
- 24 rotacje sześcianu,
- funkcje:
  - `Vec3 getWorldDir(rotId, dirId)`
  - `int findBestDirId(rotId, lookWorld)` (dot-product w local space)

### 4.2 Implementacja wyboru
W itemie:
- `lookWorld = normalize(player.getLookVec())`
- `lookLocal = inverseRotate(rotId, lookWorld)`
- `dirId = argmax dot(lookLocal, normalize(BASE_DIRS_18[i]))`

Zapisz `rotId, dirId` do TE.

---

## 5) Deterministyczny wybór renderera: half-block vs advanced

Masz dziś dwa różne systemy wykrywania “axis aligned”:
- `RenderHelper` (progi 0.95/0.05),
- `AdvancedCutRenderer` (twarde rozpoznanie ≈ 1 / 0).

To powoduje, że połówki czasem idą inną ścieżką i gubią ściany.

### 5.1 Zasada
Wybór ma być deterministyczny na podstawie `nWorld` z `rotId+dirId`, nie na podstawie lookVec float i progów.

### 5.2 Zrób jedną funkcję `isAxisAlignedWorld(nWorld)`
Po rekonstrukcji `nWorld`:
- `ax = abs(nx)`, `ay = abs(ny)`, `az = abs(nz)`
- jeśli `ax > 0.999999 && ay < 1e-6 && az < 1e-6` -> oś X
- analogicznie Y/Z.

Ponieważ nWorld pochodzi z intów i rotacji, to będzie stabilne.

### 5.3 RenderHelper: usuń progi 0.95/0.05
W `RenderHelper.renderCutBlock(...)` usuń `isAxisAligned(...)` oparty o progi.
Zamiast tego:
- albo zawsze wołaj `AdvancedCutRenderer` (najprościej do stabilizacji),
- albo wybieraj osiowy renderer tylko gdy `isAxisAlignedWorld(nWorld)` zwraca true.

---

## 6) Naprawa brakujących ścian w połówkach (axis-aligned)

Są 3 źródła problemu: zły wybór połowy, z-fighting, i dziedziczenie koloru.

### 6.1 Poprawny wybór połowy
Po ujednoliceniu keepPositive (sekcja 3) wyrażenia typu:
- `ny > 0 == keepPositiveSide`
będą działały poprawnie.

Upewnij się, że wszędzie w axis rendererze interpretujesz keepPositive tak samo.

### 6.2 Anti z-fighting: dodaj offset również w axis trybie
Dla half-blocków cut-face leży często w idealnym `0.5`. To powoduje miganie na czarno.

Dodaj w osiowym rendererze przesunięcie:
- dla płaszczyzny X=0.5: rysuj na `0.5 + sign(nx)*1e-4`
- dla Y: `0.5 + sign(ny)*1e-4`
- dla Z: `0.5 + sign(nz)*1e-4`

Uwaga: offset dotyczy **tylko cut-face**, nie bocznych ścian.

### 6.3 Reset koloru/brightness (zielony tint)
W każdej funkcji renderującej ścianę:
- przed dodaniem wierzchołków ustaw:
  - `tess.setBrightness(brightness)`
  - `tess.setColorOpaque_F(1f,1f,1f)` (albo vanilla multiplier, ale zawsze jawnie)
Po zakończeniu renderowania bloku:
- ustaw z powrotem `setColorOpaque_F(1,1,1)`.

To eliminuje “przeciekanie” koloru między blokami w batchu.

---

## 7) Cut-face UV: stała skala (1 blok = 16px) i niezależność od płaszczyzny

Masz dziś kilka implementacji, które robią UV z bounding boxa i normalizują `(u-uMin)/(uMax-uMin)`.
To **musi zniknąć**, bo to jest dokładnie “skala zależna od płaszczyzny”.

### 7.1 Zostaw jedną implementację UV dla cut-face
Wybierz `AdvancedCutRenderer.renderCutFace(...)` jako miejsce, gdzie UV jest liczone.
Wyłącz/usuń:
- `TextureMapper` (jeśli robi u/v z min/max),
- `CutFaceRenderer` (jeśli robi faceWidth/Height scaling),
- albo przynajmniej spraw, by nie były używane w renderze świata.

### 7.2 Stabilna baza (tangent/bitangent) bez skoków
Zbuduj bazę `t,b` deterministycznie:
- wybierz `a` na podstawie największej składowej normalnej:

```
if abs(nx) >= abs(ny) && abs(nx) >= abs(nz): a=(0,1,0)
else if abs(ny) >= abs(nz):                  a=(0,0,1)
else                                         a=(0,1,0)
t = normalize(cross(a,n))
b = cross(n,t)
```

To ogranicza “przeskoki” orientacji UV.

### 7.3 Origin UV
Żeby wyglądało stabilnie na wielu blokach:
- ustaw `origin = C = (0.5,0.5,0.5)`

(Jeśli origin zależy od kliknięcia/anchor, wzór będzie się przesuwał — bywa odbierane jako “inne skalowanie”.)

### 7.4 UV w pikselach + wrap
Dla wierzchołka `pLocal`:

- `uBlocks = dot(pLocal - origin, t)`
- `vBlocks = dot(pLocal - origin, b)`
- `uPx = uBlocks * 16.0`
- `vPx = vBlocks * 16.0`
- `uTile = wrap16(uPx)`, `vTile = wrap16(vPx)`
- `U = icon.getInterpolatedU(uTile)`
- `V = icon.getInterpolatedV(vTile)`

`wrap16`:
```java
static double wrap16(double px) {
  double w = px % 16.0;
  if (w < 0) w += 16.0;
  return w;
}
```

### 7.5 Zakaz: normalizacja po min/max
Usuń wszelkie:
- `u = (u-uMin)/(uMax-uMin)`
- `v = (v-vMin)/(vMax-vMin)`

To jest powód “za dużej skali” i zależności od płaszczyzny.

---

## 8) Finalna checklista wdrożenia

### Porządek
- [ ] Jeden sourceSet w gradle, brak duplikatów klas.
- [ ] Jeden `ItemCuttingTool` w JAR.

### Dane TE
- [ ] TE zapisuje `rotId, dirId, keepPositive, originalBlock, meta`.
- [ ] Renderer ignoruje float normalX/Y/Z jako źródło prawdy.

### Keep / normalna
- [ ] `keepPositive` ma jedną semantykę.
- [ ] Normalna świata zawsze z `(rotId,dirId)`.

### Render tryb
- [ ] `RenderHelper` nie używa progów 0.95/0.05.
- [ ] Axis vs advanced wybierane deterministycznie po `nWorld`.

### Połówki
- [ ] Axis cut-face ma offset (anti z-fighting).
- [ ] Każdy face ustawia brightness + color (brak zieleni/czerni).

### UV cut-face
- [ ] Jedna metoda UV (pixel units + wrap16).
- [ ] Origin = center (stabilny pattern).
- [ ] Brak min/max scaling.

---

## 9) Testy końcowe

1) Połówka osiowa:
- stań z dwóch stron, upewnij się że zawsze zostaje ta sama połówka (zgodna z keepPositive)
- brak migania (z-fighting)

2) 20 ukośnych bloków obok:
- brak płacht, brak odwróconych kierunków

3) Cut-face tekstura:
- porównaj “gęstość pikseli” z boczną ścianą — ma być identyczna niezależnie od kąta.
