# Instrukcja dla agenta: TRIAGE problemu “NaN w NBT” + utrzymanie PyAnvilEditor (bez pisania własnego backendu na `nbtlib`) — Minecraft 1.7.10

Masz skłonność do natychmiastowego “uciekania” w implementację własnego backendu (np. `nbtlib` + ręczny zapis `.mca`).  
**Nie rób tego teraz.** To jest najwyższe ryzyko korupcji świata i cofnie projekt o tygodnie.

W tej iteracji masz:
1) **dowieść** (przez minimalne testy), czy PyAnvilEditor faktycznie nie daje rady w write-path dla 1.7.10,
2) jeśli problemem są “NaN w NBT” (najczęściej w modowych TE), to **odizolować** je od obszaru testowego,
3) zrealizować test spirali (wariant B) na **czystym świecie testowym** bez modowych TE w chunkach, które dotykasz,
4) dopiero jeśli to wszystko jest niemożliwe — przygotować plan migracji na inną bibliotekę (np. anvil-parser / pymclevel / PyAnvilEditor fork), ale nadal **nie pisać** własnego writer’a `.mca` od zera.

---

## 0) Twarde zasady (COMPLIANCE)

### 0.1 Zakaz na tę iterację
- **Nie wolno** tworzyć własnego backendu “anvil writer” na `nbtlib`.
- **Nie wolno** edytować/rekonstruować plików `region/r.*.*.mca` ręcznie przez własne offsety/sektory/kompresję.
- **Nie wolno** używać `amulet-core` jako writer dla świata 1.7.10.

Jeśli czujesz pokusę: wróć do sekcji 1–4 i wykonaj triage.

### 0.2 Cel minimalny
Masz doprowadzić do sytuacji, gdzie:
- edytujesz świat offline przez **PyAnvilEditor**,
- wklejasz minimalną strukturę (command block + redstone),
- serwer headless loguje `[PROBE] ...` bez wejścia gracza.

---

## 1) Zrozum problem: “NaN w NBT” nie oznacza, że biblioteka jest bezużyteczna

NBT potrafi zawierać `float`/`double`, a wartości NaN są legalne (to normalny bitpattern IEEE-754).
Problem “biblioteka ma problem z NaN” często oznacza jedną z rzeczy:

A) biblioteka próbuje konwertować NBT do SNBT/JSON i tam NaN nie przechodzi (np. JSON nie ma NaN),  
B) biblioteka ma bug w serializacji float/double,  
C) NaN jest w chunkach spoza obszaru testu i dotykasz ich niepotrzebnie,  
D) świat testowy jest “brudny”: chunk zawiera modowe TE o niestandardowej strukturze, których nie musisz ruszać.

Wariant B testu spirali **nie wymaga** modowych TE w żadnym miejscu.  
Wymaga tylko:
- redstone/repeatery,
- command block TE (`id="Control"` w 1.7.10) z `Command="/say ..."`.

---

## 2) Zrób CZYSTY świat testowy (must-have)

### 2.1 Wymóg
Utwórz nowy świat testowy 1.7.10:
- najlepiej superflat/creative,
- bez budowli i bez modowych maszyn (nie wklejaj nic “na start”),
- jeśli mody są w paczce — OK, ale NIE stawiaj modowych bloków w chunkach testowych.

### 2.2 Dlaczego to rozwiązuje 80% problemów
Jeśli NaN siedzi w TE modów, to czysty świat nie będzie miał takich TE, więc:
- PyAnvilEditor nie powinien natknąć się na te tagi,
- a Ty możesz wykonać swoje testy (round-trip + spirala).

---

## 3) Minimalny dowód: czy PyAnvilEditor działa w write-path (round-trip)

Zanim cokolwiek większego, wykonaj **dwufazowy test round-trip**.

### 3.1 Test Round-Trip #1 (bez TE)
1) Otwórz czysty świat PyAnvilEditor.
2) Wstaw 1 blok stone w (0,64,0).
3) Zapisz.
4) Odczytaj ponownie i potwierdź, że blok istnieje.

Jeśli to FAIL → PyAnvilEditor nie działa nawet dla bloków → wtedy dopiero rozważ zmianę biblioteki (sekcja 7).

### 3.2 Test Round-Trip #2 (command block TE)
1) Wstaw command block (ID=137) w (0,64,1).
2) Dodaj TE:
   - `id = "Control"` (ważne dla 1.7.10)
   - `x,y,z` absolutne
   - `Command = "/say [ROUNDTRIP] ok"`
3) Zapisz.
4) Odczytaj ponownie i sprawdź, że:
   - TE istnieje,
   - `id == "Control"`,
   - `Command` ma dokładnie tę komendę.

Jeśli FAIL: zapisz wyjątek + lokalizację chunku + zobacz sekcję 4 (triage NaN).

> Ważne: NIE konwertuj NBT do JSON. Pracuj na NBT jako binarnym tree/obiekcie biblioteki.

---

## 4) TRIAGE: znajdź gdzie jest NaN i czy dotyczy obszaru testu

Jeśli PyAnvilEditor wywala się na NaN, nie wolno pisać nowego backendu.
Najpierw **zlokalizuj** problem.

### 4.1 Minimalny skrypt diagnostyczny (w `src/tools/nbt_triage.py`)
Zaimplementuj skrypt, który:
- iteruje po regionach `.mca` w świecie (albo tylko po regionach w promieniu testu),
- w każdym regionie po chunkach,
- próbuje wczytać chunk i wypisuje:
  - który region i chunk powoduje wyjątek,
  - stack trace (w logu),
  - jeśli biblioteka podaje ścieżkę do tagu — zapisz ją.

Wynik ma być listą “bad chunks”.

### 4.2 Ogranicz obszar edycji
Jeżeli “bad chunk” jest poza AABB testu spirali:
- nie dotykaj go,
- ogranicz paste/patch do regionów w obrębie testu.

W praktyce: edytuj tylko regiony/chunki, które zawierają Twoją strukturę.

---

## 5) Implementacja testu spirali (wariant B) — na czystym świecie

Po przejściu round-trip przechodzisz do spirali.

### 5.1 Najpierw R=1 (mikro)
- zrób spiralę obejmującą tylko kilka chunków,
- wstaw start sygnału (redstone block) + 2–3 command blocki,
- uruchom serwer i potwierdź logi.

### 5.2 Potem R=3 (smoke)
- dopiero po sukcesie R=1.

### 5.3 Dopiero potem skalowanie
- R=50 to dopiero gdy:
  - zapis świata jest stabilny,
  - logi są deterministyczne,
  - walidator “ciągłości kabla” przechodzi.

---

## 6) Co robić, jeśli PyAnvilEditor ma problem tylko na “brudnym świecie” z modami

Jeśli PyAnvilEditor działa na czystym świecie, a wywala się na Twoim świecie z modami:
- to NIE jest problem test harnessu,
- tylko problem wejściowego świata/TE.

Rozwiązanie w tym projekcie:
- trzymaj osobny “świat testowy CI” czysty,
- testuj mechanikę redstone i harness na czystym świecie,
- dopiero potem przechodź do modowych TE.

---

## 7) Jeśli PyAnvilEditor faktycznie nie daje rady (po dowodach), co wtedy — bez własnego writer’a

Dopiero gdy:
- Test Round-Trip #1 i #2 FAILują na czystym świecie,
- i masz logi/stack trace,

wtedy wolno Ci przejść na alternatywę pythonową:

### 7.1 Alternatywy
- `anvil-parser` (jeśli ma stabilny write-path w Twojej wersji)
- `pymclevel`/MCEdit backend (jeśli środowisko pozwala)

Twoim zadaniem jest wtedy:
- podmienić backend w `anvil_backend.py`,
- utrzymać to samo API `WorldEditor`,
- przejść te same testy round-trip + spiral.

**Nadal zakaz**: pisanie własnego `.mca` writer’a.

---

## 8) Wymagane artefakty po tej iteracji

1) `src/mc_editkit/world/backends/anvil_backend.py` oparty o PyAnvilEditor (writer).
2) `src/mc_editkit/tests/test_tileentities_roundtrip.py` przechodzący na czystym świecie.
3) `src/mc_editkit/tests/test_variant_b_spiral_probe.py` przechodzący (R=1 i R=3).
4) `src/tools/nbt_triage.py` generujący listę “bad chunks” (jeśli problem z NaN pojawia się gdziekolwiek).

---

## 9) Kryterium końcowe (Definition of Done)

- Nie ma `amulet-core` w write-path.
- Nie ma własnego backendu `.mca` na `nbtlib`.
- Round-trip bloków i command block TE przechodzi na czystym świecie.
- Spiralny test loguje `[PROBE] REACHED ...` headless bez udziału gracza.
- Jeśli NaN występuje w “brudnym świecie”, masz raport “bad chunks” i edycje ograniczone do AABB testu.

---
