# Instrukcja naprawy moda – poprawne kierunki cięcia (kamera), połówki i UV

Ten dokument opisuje **konkretnie co trzeba zmienić**, żeby:

1. **Płaszczyzna cięcia była zawsze równoległa do płaszczyzny widoku gracza**  
   → czyli jej normalna wynika **wyłącznie z kierunku patrzenia (look vector)** (po aproksymacji do dyskretnych kierunków), a **nie** z punktu kliknięcia / rogu / face’a.

2. Aproksymacja do dyskretnych kierunków (np. 18 klas) **nie zmienia** idei:  
   nadal tniemy płaszczyzną „ekranu” (screen-plane) przechodzącą przez **środek** bloku, tylko wybieramy najbliższą normalną z ograniczonego zbioru.

3. Znikają błędy:
   - brakujące ściany w „dokładnych połówkach”,
   - miganie na czarno,
   - zielone/losowe przebarwienia (atlas bleeding),
   - UV na ścianie cięcia o zmiennej skali zależnej od płaszczyzny.

---

## A. Zasada nadrzędna: geometria cięcia = tylko `lookDir` (po dyskretyzacji)

### A1) Definicja płaszczyzny cięcia

Dla bloku w `(x,y,z)`:

- **center** = `(x+0.5, y+0.5, z+0.5)`
- **normal** = `n = discrete( normalize(playerLookVec) )`
- **plane equation**: `dot(n, P - center) = 0`  
  równoważnie: `dot(n,P) - dot(n,center) = 0` czyli `D = dot(n, center)`.

**Ważne:** Nie wolno, aby `hitX/hitY/hitZ` (punkt kliknięcia) wpływał na `D` ani na `n`.

### A2) Co *może* zależeć od kliknięcia

Punkt kliknięcia może wpływać jedynie na:
- wybór **keepPositive/keepNegative** (po której stronie zachować), *jeśli chcesz*,  
  ale nawet to powinno być liczone konsekwentnie w oparciu o **ten sam** `center` i `n`.

**Nie wolno używać hitpointa jako `origin` UV** ani jako „kotwicy” geometrii.

---

## B. Usuń źródło „klikam w róg, a tnie jak z przodu” (anchor/hitpoint w złym miejscu)

### B1) Przestań zapisywać i używać `anchorX/Y/Z` do geometrii i UV

Jeżeli w TE zapisujesz `anchorX/Y/Z` (snap do 1/16) – to jest *główne* ryzyko, że:
- UV lub projekcja zaczyna zależeć od kliknięcia,
- blok „ciągnie” z rogu,
- powstają inne warianty mimo tego samego `lookDir`.

**Zmień kontrakt TE:**
- zapisuj tylko:
  - `rotId` (jeśli obrót bloku ma sens),
  - `dirId` (dyskretny kierunek normalnej),
  - `keepPositive` (bool),
  - ewentualnie `version`/`flags`.
- **usuń** wpływ `anchor` na render/clip.

Jeśli `anchor` jest potrzebny do debugowania – niech nie wpływa na nic poza logiem.

### B2) KeepPositive licz w 100% deterministycznie

Zalecana metoda (stabilna i intuicyjna):

- policz `distPlayer = dot(n, playerEyePos - center)`
- jeśli `distPlayer >= 0` → `keepPositive = true` (zachowaj stronę „bliżej kamery”)
- else → `keepPositive = false`.

To gwarantuje, że:
- zawsze zachowujesz „połowę bliżej gracza”
- i **nie zależy to** od rogu kliknięcia.

---

## C. Napraw „dokładne połówki” – EPS i logika stron płaszczyzny

### C1) Zakaz ostrych porównań `>0` i `<0`

Jeżeli testujesz stronę płaszczyzny jako:
- `dist > 0` / `dist < 0`  
to punkty dokładnie na płaszczyźnie (`dist==0`) wypadają z obu stron → **dziury**.

**Wszędzie** (clipper, selekcja, generowanie krawędzi przecięcia) wprowadź EPS:

- `keepPositive`: akceptuj `dist >= -EPS`
- `keepNegative`: akceptuj `dist <= +EPS`

Ustal jedno EPS w całym systemie, np. `EPS = 1e-6` w jednostkach świata.

### C2) Deduplikacja i stabilność wierzchołków

Po klipowaniu i liczeniu przecięć:
- scalaj punkty, które są bliżej niż EPS,
- nie dopuszczaj do polygonów z < 3 unikalnymi wierzchołkami,
- przy tworzeniu cut-face sortuj punkty po kącie wokół środka (na płaszczyźnie).

To usuwa przypadki „prawie połówka” = degenerat.

---

## D. Napraw miganie/czernienie – przestań rysować trójkąty jako zdegenerowane QUADS

Jeśli obecnie generujesz wachlarz trójkątów i „udajesz” quady (A,B,C,C):
- to jest niestabilne i potrafi migać/czernieć przy degeneratach.

**Zmień render na `GL_TRIANGLES`** dla wszystkich powierzchni nienależących do osiowego sześcianu:

- ściany przycięte (polygony 3+),
- cut-face.

W 1.7.10 Tessellator działa w TRIANGLES bez problemu.

---

## E. UV ściany cięcia – stała skala, niezależna od płaszczyzny

### E1) Jeden poprawny model UV dla cut-face

**Nie** licz UV na podstawie min/max AABB klipowanego polygona (to daje skalę zależną od normalnej i keepSide).

Zamiast tego:

1. Weź `n` = normalna płaszczyzny cięcia (z `dirId`).
2. Zbuduj bazę na płaszczyźnie:
   - wybierz wektor pomocniczy `a`:
     - jeśli `abs(n.y) < 0.9` → `a = (0,1,0)` else `a=(1,0,0)`
   - `tangent = normalize(cross(a, n))`
   - `bitangent = cross(n, tangent)`
3. Wybierz origin UV:
   - **zawsze** `origin = center` (środek bloku!)  
     (nie hitpoint, nie corner)
4. Dla każdego wierzchołka `p` na cut-face:
   - `u_world = dot(p - origin, tangent)`
   - `v_world = dot(p - origin, bitangent)`
5. Skala Minecraft:
   - `u_px = u_world * 16`
   - `v_px = v_world * 16`
6. Tiling:
   - `u_px = wrap16(u_px)`  
   - `v_px = wrap16(v_px)`
7. Konwersja do ikony:
   - `U = icon.getInterpolatedU(u_px)`
   - `V = icon.getInterpolatedV(v_px)`

**Efekt:** skala tekstury na cut-face jest zawsze jak na ścianie bocznej, a przy dłuższej przekątnej po prostu się **powtarza**.

### E2) Atlas bleeding (zielone przebarwienia)

Nie clampuj do dokładnie 0 lub 1 „wewnątrz ikony”.

Zastosuj inset:
- w pikselach: `0.5` texela,
- czyli w skali 0..16:  
  `u_px = clamp(u_px, 0.5, 15.5)` jeśli używasz clip (gdybyś gdzieś musiał),
- albo w skali 0..1: `epsilon = 0.5/16`.

Dla tilingu zwykle nie clampujesz, tylko wrapujesz, ale jeśli gdzieś masz clamp – **nigdy** nie dobijaj do brzegów.

---

## F. UV ścian bocznych – spójność z cut-face

Ściany boczne (przycięte) powinny mieć UV jak vanilla:
- dla osi-aligned face’ów: mapuj po odpowiednich osiach (x/y/z) *w świecie*,
- bez normalizacji do AABB polygona.

Jeżeli przycinasz ścianę X+ i zostaje trapez/tri:
- UV liczone jak dla oryginalnej ściany X+ (u=z, v=y, w skali 16).

To zapewnia, że wzór cegieł jest spójny między ścianą i cut-face.

---

## G. Dyskretne kierunki (np. 18) – jak to ma działać, żeby NIE zmieniało sensu cięcia

### G1) Dyskretyzacja = wybór najbliższego wektora normalnego

`n_raw = normalize(playerLookVec)`

`n = argmax_k dot(n_raw, dirs[k])`

gdzie `dirs[k]` to Twoje 18 wektorów (unit length).

**Kluczowe:**  
To tylko wybór najbliższego kierunku – nic więcej.  
Nie wolno potem „korygować” `D` na podstawie hitpointa, bo to zmienia geometrię.

### G2) Ile wariantów dla rotacji

Jeśli `rotId` ma 24 orientacje sześcianu (albo 6/24), a `dirId` ma 18 klas:
- na rotację wypada dokładnie **18** wektorów (w lokalnym układzie bloku),
- ale w NBT zapisujesz tylko `(rotId, dirId)`.

Implementacyjnie:
- trzymaj `dirsLocal[18]` w układzie „blok-local”,
- w renderze przelicz do świata: `n_world = applyRotation(rotId, dirsLocal[dirId])`.

---

## H. Najważniejszy test poprawności (do odpalenia po zmianach)

1) Postaw blok.
2) Patrz na niego pod stałym kątem (np. w dół pod 45°) i tnij kilka razy z różnych stron/rogów.
   - **Oczekiwane:** wynik identyczny dla tego samego lookDir (po dyskretyzacji), niezależnie od tego, czy klikasz w róg czy środek.
3) Zrób „dokładną połówkę” (lookDir ≈ (0,1,0) / (1,0,0) / (0,0,1)).
   - **Oczekiwane:** bryła zawsze zamknięta, brak dziur, brak migania.
4) Sprawdź cegły:
   - na ścianie bocznej wzór = vanilla,
   - na cut-face wzór ma tę samą skalę i ewentualnie się powtarza.

---

## I. Minimalna checklist “co usunąć/wyłączyć”, żeby nie mieszały się pipeline’y

Jeżeli masz równolegle stare i nowe implementacje (duplikaty klas):
- zostaw **jedną** gałąź (docelową: `rotId/dirId/keepPositive`),
- usuń lub wyłącz z builda:
  - starą wersję `ItemCuttingTool`,
  - starą `TileEntityCuttable` zapisującą float normalX/Y/Z,
  - stare `CutFaceRenderer` / `TextureMapper` oparte o min/max scaling.

Jeśli build raz używa starego renderera, a raz nowego – będziesz widzieć „losowe” regresje.

---

## J. Co dokładnie ma być prawdą po poprawkach (kontrakt)

- `dirId` zależy **tylko** od `playerLookVec`.
- płaszczyzna zawsze przechodzi przez `center`.
- `keepPositive` zależy **tylko** od położenia kamery względem `center` i `n`.
- UV cut-face liczone z projekcji na (tangent, bitangent) i *wrap 16*.
- Żadna część geometrii/UV nie zależy od `hitX/hitY/hitZ`.
- żadnych ostrych `>0/<0` bez EPS.
- żadnych „triangle as quad (A,B,C,C)”.

---

Jeśli wdrożysz punkty A–F, problem „klikam w róg, a wygląda jak z przodu” przestanie być możliwy – bo w kodzie nie będzie żadnej ścieżki, która mogłaby przemycić informację o rogu do geometrii/UV.
