# Instrukcja naprawy moda: spójne kierunki/keepPositive, brakujące ściany w połówkach oraz stabilne UV na ścianie cięcia

Ten dokument opisuje **konkretne zmiany**, które trzeba wprowadzić, aby rozwiązać jednocześnie:
1) **odwrócone / „od rogu” kierunki** po wprowadzeniu dyskretnych kierunków,
2) **brakujące ściany i artefakty dla dokładnych połówek** (axis-aligned),
3) **zbyt duża skala tekstury na ścianie cięcia** oraz skala zależna od płaszczyzny.

Wszystkie problemy wynikają z **niespójnej definicji `keepPositive`**, mieszania „lokalnych” i „światowych” normalnych oraz niepoprawnego/niestabilnego systemu UV dla cut-face.

---

## 0) Zasady, które muszą być prawdziwe po poprawkach (kontrakt)

### 0.1 Płaszczyzna cięcia
Płaszczyzna zawsze przechodzi przez środek:
- `n · (p - C) = 0`, `C=(0.5,0.5,0.5)`
- `dist(p) = n·p - d`, gdzie `d = n·C = 0.5*(nx+ny+nz)`

### 0.2 Jedna definicja `keepPositive`
**Wybierz jedną definicję i używaj wszędzie tej samej:**

> Definicja A (zalecana):  
> `keepPositive == true` oznacza, że **zostawiamy stronę, dla której** `dist(p) >= 0`.

Wtedy:
- `keepPositive` jest spójne z „dodatnią stroną normalnej”
- half-block decyzje typu `ny>0` mają sens
- winding dla cut-face można zdefiniować jednoznacznie.

**Nie używaj** definicji typu „zostaw stronę przeciwną do gracza” jako *semantyki keepPositive* — jeśli chcesz taki efekt UX, zrób to jako dodatkową regułę, ale na końcu i nadal mapuj na definicję A.

### 0.3 Normalna jest zawsze wyliczana tak samo
Po wprowadzeniu dyskretnych kierunków normalna świata w rendererze i w itemie musi być identyczna:
- `nWorld = R(rotId) * normalize(BASE_DIRS_18[dirId])`

Nie przechowuj równolegle „starych float normalX/Y/Z” i „dirId” bez jasnej hierarchii; to prowadzi do rozjazdów.

---

## 1) Usuń duplikaty klas / upewnij się, że kompiluje się jedna wersja

W projekcie pojawiają się równoległe wersje `ItemCuttingTool` i innych klas w różnych folderach.
To powoduje, że możesz edytować jedną wersję, a build bierze inną.

### 1.1 Wykonaj porządkowanie
- Zostaw tylko **jedną** ścieżkę źródeł w gradle (`src/main/java`).
- Usuń / wyłącz w buildzie alternatywne katalogi (np. `new_mod_trial/src/...`), albo upewnij się, że nie są dodane do sourceSets.
- Po tej zmianie zrób build i upewnij się, że w jar jest jedna wersja każdej klasy.

---

## 2) Ujednolić `keepPositive` w ItemCuttingTool (i tylko tu)

### 2.1 Oblicz nWorld deterministycznie z dyskretnego wyboru
W `ItemCuttingTool.onItemUse`:
1) policz `lookWorld = normalize(player.getLookVec())`
2) jeśli używasz rotacji bloku:
   - `lookLocal = inverseRotate(rotId, lookWorld)`
3) wybierz `dirId = argmax dot(lookLocal, normalize(BASE_DIRS_18[i]))`
4) odtwórz:
   - `nLocal = normalize(BASE_DIRS_18[dirId])`
   - `nWorld = rotate(rotId, nLocal)`

### 2.2 Ustal keepPositive zgodnie z definicją A
Wyznacz stronę gracza względem płaszczyzny:
- weź punkt gracza w lokalnych coords bloku (0..1):
  - `pl = (player.posX - x, player.posY + eyeHeight - y, player.posZ - z)`
- policz `d = dot(nWorld, C) = 0.5*(nx+ny+nz)`
- `playerDist = dot(nWorld, pl) - d`

Teraz:
- jeśli chcesz „zostaw stronę, po której stoi gracz”: `keepPositive = (playerDist >= 0)`
- jeśli chcesz „zostaw stronę przeciwną do gracza”: `keepPositive = (playerDist < 0)` **ALE** wtedy pamiętaj, że to nadal musi być interpretowane wg definicji A; tzn. to jest już bezpośrednio wybór `keepPositive`, a nie zmiana semantyki.

Najważniejsze: po tej linijce `keepPositive` *ma oznaczać* „dist>=0 zostaje”.

### 2.3 Zapis do TE
Zapisz wyłącznie:
- `rotId` (byte)
- `dirId` (byte)
- `keepPositive` (boolean)
- `originalBlock` + `meta`

Nie zapisuj dodatkowo `normalX/Y/Z` (albo jeśli zapisujesz — to tylko debug i renderer ma ignorować te pola).

---

## 3) Renderer: zawsze rekonstruuj normalną z (rotId, dirId)

W `CuttableBlockRenderer` / `AdvancedCutRenderer` / `RenderHelper`:
- pobierz `rotId, dirId, keepPositive` z TE
- policz `nWorld` dokładnie jak w itemie
- używaj `nx,ny,nz` z tej normalnej we wszystkich obliczeniach:
  - intersections
  - clipping bocznych ścian
  - winding
  - wybór axis-aligned vs advanced

To eliminuje przypadki, gdzie kierunek „wygląda jak od rogu” bo item i renderer używają innej normalnej.

---

## 4) Naprawa brakujących ścian w połówkach: deterministyczny wybór trybu + poprawne renderowanie przekroju

### 4.1 Nie wybieraj trybu po progach float
W `CuttableBlockRenderer.renderWorldBlock` masz:
- if axis-aligned -> `renderAxisAlignedCut` / RenderHelper
- else -> AdvancedCutRenderer

To musi być deterministyczne po `dirId`:
- jeśli `dirId` odpowiada osiowym wektorom (np. klasa „(-1,0,0)” po rotacji): **zawsze** tryb osiowy.
- reszta: tryb advanced.

Najprościej:
- sprawdź `abs(nx)`/`abs(ny)`/`abs(nz)` po rekonstrukcji nWorld, ale bez progów:
  - jeśli jeden komponent jest == 1.0 (albo w praktyce |component| > 0.999999) i pozostałe ~0 → axis.
Ponieważ nWorld jest znormalizowany z intów i obracany, te wartości są stabilniejsze niż lookVec.

### 4.2 Ujednolić znaczenie „topHalf/eastHalf”
W osiowym rendererze masz wyrażenia typu:
- `ny > 0 == keepPositive`

To działa tylko gdy keepPositive ma definicję A.
Po ujednoliceniu keepPositive (sekcja 2) te wyrażenia będą poprawne.

### 4.3 Dodaj offset anty z-fighting dla osiowych cut-face
Masz `Z_FIGHT_OFFSET` w advanced path, ale połówki często renderują cut-face w RenderHelper bez offsetu.

Dodaj w RenderHelper (dla renderu ściany przekroju):
- minimalne przesunięcie wzdłuż normalnej (dla osi Y: w y, dla osi X: w x, itd.)
np. dla horizontal cut:
- jeśli cut-plane jest na y=0.5, to rysuj ją na `0.5 + sign(ny)*1e-4` albo na `0.5 ± 1e-4` zależnie od strony.

To usuwa miganie na czarno.

### 4.4 Reset koloru i brightness po renderze
Na końcu renderowania bloku (po wszystkim):
- `tess.setColorOpaque_F(1f,1f,1f);`
- opcjonalnie przywróć brightness standardowe (albo zawsze ustawiaj brightness przed każdym face).

To usuwa „zielone” artefakty wynikające z dziedziczenia stanu.

---

# 5) Stabilne UV na ścianie cięcia: skala 1:1 z bokami i niezależna od płaszczyzny

Masz dwa wymagania:
- „piksele” na cut-face mają mieć taki sam rozmiar jak na bocznych (1 blok = 16 px),
- tekstura ma się powtarzać (tiling), bo długość może być do √2,
- skala nie może zależeć od kierunku (nie może się „rozciągać” gdy normalna się zmienia).

## 5.1 Najczęstszy błąd, który powoduje zmienną skalę
Jeśli UV liczysz w oparciu o:
- współrzędne świata (x,y,z) bez projekcji na płaszczyznę, albo
- projekcję na `t,b` które nie są stabilne (np. wybór wektora pomocniczego `a` zmienia się skokowo), albo
- centrowanie UV bez poprawnej jednostki (mieszasz „w blokach” i „w pikselach”),

to skala będzie zależeć od normalnej.

## 5.2 Zrób stabilny układ 2D na płaszczyźnie z *kotwicą* i *stałą regułą wyboru osi*
Żeby `t,b` nie „przeskakiwały”:
- wybierz `a` zawsze deterministycznie na podstawie największej składowej normalnej:

Reguła:
- jeśli `abs(nx)` największe -> `a = (0,1,0)`
- else jeśli `abs(ny)` największe -> `a = (0,0,1)`
- else -> `a = (0,1,0)`

Potem:
- `t = normalize(cross(a, n))`
- `b = cross(n, t)`

Ta reguła redukuje skoki orientacji UV.

## 5.3 UV w „pikselach” + wrap do 16 (bez skalowania przez rozmiar)
Ustal `origin` jako stały punkt, najlepiej:
- `origin = C` (środek) – daje spójny „pattern phase” dla wszystkich bloków

Dla wierzchołka `pLocal`:
- `uBlocks = dot(pLocal - origin, t)`
- `vBlocks = dot(pLocal - origin, b)`
- `uPx = uBlocks * 16`
- `vPx = vBlocks * 16`
- `uTile = wrap16(uPx)`, `vTile = wrap16(vPx)`
- `U = icon.getInterpolatedU(uTile)`, `V = icon.getInterpolatedV(vTile)`

**Nigdy nie rób** normalizacji typu `u = (u-uMin)/(uMax-uMin)` — to rozciąga teksturę (większa skala na większej ścianie).

## 5.4 wrap16 dla wartości ujemnych
```java
static double wrap16(double px) {
    double w = px % 16.0;
    if (w < 0) w += 16.0;
    return w;
}
```

## 5.5 Ikona dla cut-face
Wybierz konsekwentnie:
- np. `originalBlock.getIcon( sideBasedOnNormal(nWorld), meta )`
albo `getIcon(clickedSide, meta)` jeśli przechowujesz kliknięty side.

Skala/tiling działa niezależnie od tej decyzji.

---

## 6) Minimalne testy regresji

1) **Połówki osiowe**
- `dirId` wskazuje oś (np. (-1,0,0) po rotacji),
- brak migania i komplet ścian.

2) **Ukośne**
- różne dirId,
- cut-face ma stałą gęstość pikseli niezależnie od kąta.

3) **Kolor**
- brak zielonego tintu po postawieniu obok trawy/liści.

---

## 7) Najczęstsze przyczyny Twoich obecnych objawów (podsumowanie)
- `keepPositive` jest liczone jako „przeciwnie do gracza” i potem używane jak „dodatnia strona normalnej” → odwrócone połówki i znikające ściany.
- normalna jest czasem brana z floatów, a czasem z dirId → „kierunki jak od rogu”.
- UV cut-face jest liczone z niestabilnej bazy lub jest rozciągane przez rozmiar wielokąta → skala zależna od płaszczyzny.
- brak offsetu w osiowej ścianie przekroju + brak resetu koloru/brightness → czarne miganie + zielony tint.
