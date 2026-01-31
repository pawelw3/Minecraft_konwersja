# Instrukcja: generowanie spirali chunków (R=20) i wstawianie struktury PROBE przez Hephaistos (JVM) — Minecraft 1.7.10

Ta instrukcja opisuje, jak zbudować **spiralę chunków** wychodzącą ze środka (chunk 0,0 lub “środkowy chunk testu”) do promienia **R=20 chunków**, oraz jak **wstawić** w świecie 1.7.10 strukturę testową (platforma + redstone + command blocki logujące) **wyłącznie w workerze JVM opartym o Hephaistos** (bez generowania świata w Pythonie).

> **Założenie:** masz już działający read/write `.mca` przez Hephaistos (Test 2 PASS: read → write unchanged → read) oraz potrafisz:
> - `set_block(x,y,z,id,meta)` dla 1.7.10 (`Blocks/Data/AddBlocks`),
> - `set_tile_entity(x,y,z,nbt)` (lista `Level/TileEntities`),
> - uruchomić serwer headless i parsować logi.

---

## 0) Cel testu spirali

Chcemy sprawdzić:
1) **Jakie chunki są załadowane** bez gracza (spawn chunks),
2) Czy nasza edycja mapy jest poprawna (brak crashy, brak `Couldn't load chunk`),
3) Czy sygnał redstone przechodzi przez kolejne chunki i odpala command blocki logujące do konsoli.

**Mechanizm:** kabel “idzie” po chunkach spiralą. W każdym chunku jest “checkpoint”:
- command block z `/say [PROBE] REACHED cx=<cx> cz=<cz> step=<n>`
- (opcjonalnie) repeater dla regeneracji sygnału co <=15 bloków.

---

## 1) Parametry wejściowe (CLI workera)

Worker JVM ma przyjmować:
- `--world <path>` (ścieżka do świata)
- `--radius 20` (R)
- `--y 64` (wysokość platformy)
- `--origin-chunk 0 0` (start cx,cz)
- `--origin-block 0 64 0` (opcjonalnie: start w bloku, default: (cx*16, y, cz*16))
- `--mode spiral_probe` (tryb)

Wynik:
- edycja `.mca` offline,
- zapis,
- walidacja read-back,
- (opcjonalnie) wypisanie “plan.txt” z listą chunków/stepów.

---

## 2) Generowanie spiralnej listy chunków (R=20)

### 2.1 Wymaganie: deterministyczna spirala “kwadratowa”
Algorytm klasyczny:
- start w (0,0)
- ruchy: E (1), S (1), W (2), N (2), E (3), S (3), W (4), N (4), ...
- długość kroku rośnie co dwa kierunki.

Pseudo:
```
cx, cz = 0, 0
stepLen = 1
dirCycle = [E, S, W, N]
emit(cx,cz)
while max(|cx|,|cz|) <= R:
  for dir in dirCycle:
     repeat stepLen times:
        cx += dir.dx
        cz += dir.dz
        if max(|cx|,|cz|) <= R: emit(cx,cz)
     if dir is S or N: stepLen += 1
```

### 2.2 Warunek stopu
Emituj tylko chunki spełniające:
- `abs(cx) <= R` i `abs(cz) <= R`

**Uwaga:** To daje wszystkie chunki w kwadracie (2R+1)^2, ale w kolejności spiralnej od środka.

### 2.3 Indeks kroku
Każdy emitted chunk ma:
- `step = 0..N-1`
- `cx,cz`

---

## 3) Mapowanie chunk → współrzędne bloków (ścieżka kablowa)

W każdym chunku budujesz “checkpoint” w stałym miejscu chunku, np.:
- `baseX = cx*16 + 8`
- `baseZ = cz*16 + 8`
- `Y = y`

To daje punkt w środku chunku.

### 3.1 Połączenie między kolejnymi chunkami
Dla kolejnych punktów `(x1,z1)` i `(x2,z2)`:
- różnica jest zawsze “o 16 w X” albo “o 16 w Z” (bo sąsiedni chunk),
- budujesz prosty “korytarz” redstone:
  - platforma stone na Y,
  - dust na Y+1 (lub na Y) — wybierz konsekwentnie,
  - repeater(y) tak, by sygnał się nie kończył.

**Redstone zasady 1.7.10 (praktycznie):**
- dust przenosi sygnał do 15 bloków,
- przejście 16 bloków wymaga:
  - repeatera po drodze, lub
  - segmentu krótszego (np. start w edge chunku).
Najprościej: zawsze dawaj repeater mniej więcej w połowie odcinka 16.

### 3.2 Prosty, “idiotoodporny” wzór połączenia 16
Jeśli idziesz o 16 w X:
- zrób linię dust długości 7,
- repeater (delay 1),
- dust długości 7,
- ostatni dust łączy się z checkpointem.

Analogicznie w Z.

To gwarantuje brak spadku sygnału.

---

## 4) Struktura w chunku: checkpoint PROBE

Dla każdego chunku w spiralnej kolejności wstaw:

### 4.1 Platforma
- stone (ID=1 meta=0) w kwadracie 3x3 na poziomie Y pod checkpointem:
  - `(baseX-1..baseX+1, Y, baseZ-1..baseZ+1)`

### 4.2 Linia redstone (trasa)
- na poziomie Y+1 (zalecane) staw:
  - dust (ID=55) na trasie,
  - repeater (ID=93/94 zależnie od stanu; w schemacie offline zwykle ustawiasz “unpowered” i potem sygnał z redstone_block startuje).

**Uwaga:** repeater i comparator mają “facing” zapisany w metadata. Musisz ustawić meta zgodnie z kierunkiem.

### 4.3 Command block
Wstaw command block (ID=137 meta=0) w pobliżu checkpointu, np.:
- `(baseX, Y+1, baseZ)` albo `(baseX, Y+1, baseZ+1)` — byle nie kolidował z kablem.

### 4.4 TileEntity command block (1.7.10)
Dodaj TE do `Level/TileEntities`:
- `id: "Control"`
- `x,y,z`
- `Command: "/say [PROBE] REACHED cx=<cx> cz=<cz> step=<step>"`
- (opcjonalnie) `TrackOutput: 0` (żeby nie spamował wewnętrznym outputem)

**Ważne:** TE musi mieć poprawne `x,y,z` jako int.

---

## 5) Start sygnału: auto-start po uruchomieniu serwera

Chcemy, by test “sam ruszył” bez gracza.

### 5.1 Najprostszy start: redstone block
Postaw **redstone block** (ID=152) obok pierwszego dusta w chunku startowym (step 0), np.:
- jeśli pierwszy segment idzie w stronę E, to postaw go tak, aby zasilił dust.

To daje sygnał stale aktywny.

### 5.2 Reset/stop (opcjonalnie)
Na potrzeby testu integracyjnego wystarczy stały sygnał. Serwer po 30–120s ma zostać wyłączony przez harness.

---

## 6) Najtrudniejszy element: metadata kierunkowe (repeatery/command blocki)

### 6.1 Repeatery (1.7.10)
Repeater metadata koduje:
- kierunek (4 wartości)
- opóźnienie (2 bity)

Musisz mieć funkcję:
- `repeater_meta(facing, delayTicks)` gdzie delayTicks ∈ {1,2,3,4}

Zasada:
- budując trasę, znasz kierunek od (x1,z1) do (x2,z2), więc repeater “patrzy” w stronę sygnału.

### 6.2 Command block orientation
Command block może mieć metadata kierunku, ale dla samego wykonania komendy najważniejsza jest TE. Ustaw meta=0 jeśli nie masz potrzeby rotacji.

---

## 7) Implementacja w workerze: plan działania

### 7.1 Faza 1 — plan (bez edycji)
- wygeneruj listę chunków spirali R=20,
- wylicz dla każdego chunku `baseX,baseZ`,
- wylicz trasę połączeń między krokami,
- wypisz `plan_spiral.txt`:
  - step, cx,cz, baseX,baseZ, nextDir

**Cel:** szybka inspekcja, czy spirala jest poprawna.

### 7.2 Faza 2 — edycja świata
- grupuj zmiany po chunku:
  - `set_block` do platformy,
  - `set_block` do korytarzy redstone,
  - `set_block` do repeaterów z meta,
  - `set_block` do command block,
  - `set_te` z `id=Control`.

Ważne: edytuj tylko chunki w AABB spirali (spawn-adjacent) — unikniesz dotknięcia “brudnych” chunków.

### 7.3 Faza 3 — walidacja read-back
Po zapisie:
- odczytaj kilka losowych chunków (np. step 0, 1, 2, 10, 50, N-1),
- potwierdź:
  - że w `Level/TileEntities` jest TE na `x,y,z`,
  - że w sekcji `Y>>4` jest blockID 137 w odpowiednim indeksie.

Jeśli fail → exit != 0 i DIAG.

---

## 8) Test headless (po stronie harness, ale wymagania dla mapy)

Po uruchomieniu serwera:
- w logach ma się pojawić seria:
  - `[PROBE] REACHED ... step=0`
  - potem kolejne step-y.

**PASS minimalny:** pojawia się co najmniej `step=0..5`.  
**PASS docelowy:** pojawia się ciąg bez dziur do określonego K (np. 200).

Jeśli brak `step=0`:
- start sygnału nie zasila dust,
- command blocki nie dostają sygnału,
- chunk startowy nie jest załadowany (sprawdź spawn chunks).

---

## 9) “Najpierw prosto”: rekomendowana progresja

Nie startuj od R=20.

1) R=1 (kilka–kilkanaście chunków) → musi przejść
2) R=3 → smoke
3) R=10 → stabilność
4) R=20 → docelowo

---

## 10) Checklist dla implementacji

- [ ] Spiral generator daje deterministyczną listę chunków
- [ ] `baseX/baseZ` są zawsze wewnątrz chunku (np. +8)
- [ ] Każdy odcinek 16 bloków ma repeater(y), sygnał nie gaśnie
- [ ] Command block ma TE `id="Control"` i poprawne `x,y,z`
- [ ] Start sygnału jest w chunku startowym i zasila dust
- [ ] Po zapisie jest read-back walidacja
- [ ] Headless logi zawierają `[PROBE] REACHED ...`

---
