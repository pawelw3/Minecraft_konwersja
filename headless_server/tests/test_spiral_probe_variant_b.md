# Test headless wariant B: spiralny kabel + command block w każdym chunku (PROBE REACHED)

Ten test pozwala agentowi uruchomić serwer **bez wchodzenia gracza** i z logów (konsoli) odczytać,
**jak daleko sygnał redstone dotarł po spiralnej trasie chunków**.

Wariant B to *jeden ciągły* “wąż” redstone/repeaterów przechodzący przez chunki w spiralę.
W każdym chunku jest command block, który loguje do konsoli:  
`[PROBE] REACHED cx cz step=<n>` gdy sygnał dotrze do tego chunku.

> Uwaga: brak wpisów dalej może oznaczać **granica załadowania** *albo* **błąd kabla**.
> Żeby test był praktyczny, ta instrukcja zawiera walidacje minimalizujące ryzyko “kabel się urwał”.

---

## 0) Warunki wstępne (agent MUSI spełnić)

### 0.1 Ustawienia serwera
W `server.properties`:
- `enable-command-block=true`

Opcjonalnie, ale zalecane:
- `spawn-protection=0` (żeby nic nie blokowało command blocków przy spawnie)

### 0.2 Lokalizacja startu
Początek spirali (start sygnału + `step=0`) ma być w pobliżu world spawna (Overworld), np.:
- chunk (0,0) w okolicy (x≈8, z≈8)

To zwiększa szansę, że test działa headless w spawn-chunkach.

### 0.3 Bez udziału gracza
Agent:
- uruchamia serwer headless,
- zbiera logi przez określony czas,
- nie wymaga wchodzenia gracza.

---

## 1) Definicja testu: co ma się pojawić w logach

### 1.1 Format logu
W każdym chunku na trasie ma paść wpis:
- `/say [PROBE] REACHED cx=<cx> cz=<cz> step=<n>`

gdzie:
- `cx,cz` to koordynaty chunku,
- `n` to indeks kroku w spiralnej kolejności odwiedzin.

### 1.2 Kryterium PASS/FAIL
- PASS: w logu pojawia się **ciąg rosnący step=0..K** bez “dziur” (0,1,2,...,K) w czasie T.
- FAIL: brak `step=0` w czasie T₀, albo step przestaje rosnąć (brak nowych logów), albo pojawiają się kroki poza kolejnością.

Rekomendowane okna czasu:
- T₀ (start) = 30 s (musi paść `step=0` i kilka kolejnych)
- T (pełny) = 120 s (dla krótkich spiral i umiarkowanych opóźnień)

---

## 2) Trasa: kwadratowa spirala po chunkach

### 2.1 Krok spirali
Spirala ma “skok” dokładnie 1 chunk:
- każdy następny punkt jest przesunięty o 16 bloków w osi X lub Z.

### 2.2 Kolejność spiralna (chunk-space)
Standardowa kwadratowa spirala:
- start: (0,0)
- potem: (1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1), (2,-1), ...

Agent generuje listę `(cx,cz,step)` do promienia R (np. 50).

### 2.3 Pozycja checkpoint w chunku
Checkpoint w środku chunku:
- `x = cx*16 + 8`
- `z = cz*16 + 8`
- `y = stałe` (np. 64)

Zalecenie: zbudować wszystko na jednej platformie (stone) na stałym Y.

---

## 3) Konstrukcja elektryczna: kabel przez granice chunków

### 3.1 Zasada odległości (limit redstone)
Redstone dust działa na ~15 bloków. Między środkami chunków jest 16 bloków,
więc musisz używać repeaterów.

**Reguła: na każdym odcinku 16 bloków MUSI być co najmniej 1 repeater.**  
Zalecenie: 2 repeatery na odcinek (mniej ryzyka).

### 3.2 Zalecany segment między checkpointami
Dla każdego przejścia z chunku A do chunku B:
1) w checkpointcie A stawiasz repeater skierowany do B,
2) 6–8 bloków dust,
3) drugi repeater,
4) dust do checkpointu B.

To stabilizuje propagację i ułatwia debug.

### 3.3 Tryb sygnału (zalecany dla tego testu): STAŁE zasilanie
Ten wariant ma mierzyć “jak daleko doszło”. Najprościej:
- start sygnału = ON na stałe,
- wtedy fala zasilania przechodzi po repeaterach,
- a każdy command block odpala raz na zboczu 0→1 gdy fala dojdzie.

**Zalecenie:** start sygnału to `minecraft:redstone_block` (100% headless, bez TE/NBT).

---

## 4) Command block w każdym chunku: montaż

### 4.1 Typ
Używaj **Impulse Command Block** (“Needs Redstone”).

### 4.2 Podłączenie do kabla
W checkpointcie chunku:
1) odgałęzienie z głównego kabla przez repeater (żeby nie osłabiać magistrali),
2) repeater zasila command block.

### 4.3 Komenda
W chunku `(cx,cz)` o kroku `n` ustaw:
- `/say [PROBE] REACHED cx=<cx> cz=<cz> step=<n>`

Przykład:
- `/say [PROBE] REACHED cx=3 cz=-7 step=128`

---

## 5) Generator startowy (chunk 0,0)

### 5.1 Najprostszy headless start
Na wejściu kabla ustaw `minecraft:redstone_block`.

To eliminuje:
- przełączniki,
- hopper clock,
- tile entity NBT,
- ryzyko “nie wystartowało”.

---

## 6) Walidacje konstrukcyjne (agent MUSI wykonać przed uruchomieniem)

### 6.1 Walidacja spirali
- [ ] brak duplikatów `(cx,cz)`
- [ ] kolejne punkty różnią się dokładnie o 1 chunk w osi X lub Z
- [ ] `step` rośnie o 1 bez przerw

### 6.2 Walidacja kabla
- [ ] repeatery co max 12–14 bloków dust
- [ ] repeatery skierowane poprawnie (w stronę kolejnego checkpointu)
- [ ] dust/repeatery stoją na pełnym bloku
- [ ] command blocki podłączone przez odgałęzienie repeaterem

### 6.3 Walidacja komend
- [ ] każdy command block ma właściwy `step`
- [ ] format logu jednolity (łatwy do parsowania)

---

## 7) Procedura wykonania (agent-run)

1) Wygeneruj i wstaw schematic do świata testowego.
2) Uruchom serwer headless.
3) Zbieraj logi przez T₀=30s:
   - jeśli nie ma `step=0` → FAIL (CB wyłączone lub start źle wpięty).
4) Zbieraj logi przez T=120s:
   - znajdź maksymalny `step=K`,
   - sprawdź, czy kroki 0..K są bez dziur.
5) Zatrzymaj serwer.
6) Raport:
   - `K`, ostatni `(cx,cz)`, lista brakujących `step` jeśli są.

Jeśli FAIL:
- agent ma wyłączyć serwer,
- wykonać walidację kabla (6.2) i wskazać pierwsze miejsce przerwania.

---

## 8) Interpretacja wyniku
- `K` przybliża “granicę reachable” od startu przez tickujące chunki.
- Jeśli wynik jest podejrzanie mały:
  - najpierw szukaj błędu kabla (wariant B jest wrażliwy),
  - dopiero potem wnioskuj o granicy spawn-chunków.

---

## 9) Zalecenie praktyczne: zacznij od małego promienia
Zanim zrobisz R=50:
1) uruchom z R=5,
2) upewnij się, że loguje rosnąco 0..N,
3) dopiero wtedy skaluj do R=50.

To oszczędza masę czasu.

---
