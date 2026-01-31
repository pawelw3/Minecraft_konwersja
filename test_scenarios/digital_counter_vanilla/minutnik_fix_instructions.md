# Instrukcja naprawy minutnika (JSON: circuit_design + voxel_grid)

Ten dokument jest instrukcją **dla agenta-edytora**, jak przebudować projekt tak, żeby:
- `circuit_design.json` był logicznie spójny i odpowiadał temu, co jest w świecie,
- **przede wszystkim** `voxel_grid.json` był „perfekcyjny” (brak konfliktów współrzędnych, każdy element ma podparcie, sensowne zasilanie) i działał jako **cyfra 0→9 zmieniana co ~1 sekundę**, w pętli.

> Założenie: konwersję `voxel_grid.json -> schematic` robi inny system; tu tylko poprawiamy JSON i samą topologię.

---

## 0) Najważniejsza zmiana architektury (żeby było naprawdę poprawnie i prosto)

Aktualny projekt próbuje robić:
**zegar → licznik binarny 4-bit → dekoder BCD → 10 wyjść**.

To powoduje problemy:
- potrzebujesz resetu mod-10 (brak),
- dekoder BCD w voxelach jest tylko „placeholderem” (brak realnych bramek),
- w wielu miejscach redstone jest bez podparcia albo nakłada się ze stone.

**Naprawa „najpewniejsza w świecie Minecrafta”**: zamienić część *counter + decoder* na **10‑stanowy ring counter z dropperów (tile entities)**:
- masz **10 dropperów w pętli** i **1 item krążący**,
- co impuls (≈ 1 s) wszystkie droppere dostają zasilanie i item przesuwa się o 1 pozycję,
- dla każdego droppera masz **komparator** czytający zawartość (0/1 item),
- komparator daje sygnał tylko dla aktualnej pozycji → to są bezpośrednio linie `digit_0 … digit_9`,
- **pętla 0–9 jest naturalna**, bez resetu i bez dekodera.

To jest konstrukcyjnie prostsze, czytelne i ma znacznie mniej punktów awarii.

---

## 1) Zmiany w `circuit_design.json`

### 1.1 Usuń / zamień komponenty
1) **Usuń** komponenty:
- `counter_4bit`
- `bcd_decoder`

2) **Dodaj** komponent:
- `ring_counter_10` (nowy)

Przykładowy wpis komponentu (dostosuj styl do reszty pliku):

```json
{
  "id": "ring_counter_10",
  "type": "ring_counter",
  "specification": {
    "states": 10,
    "implementation": "dropper_ring",
    "moving_item": "minecraft:cobblestone",
    "one_hot_outputs": true
  },
  "inputs": ["clock_1hz"],
  "outputs": ["digit_0","digit_1","digit_2","digit_3","digit_4","digit_5","digit_6","digit_7","digit_8","digit_9"]
}
```

> Uwaga: `moving_item` to tylko metadana — faktycznie wrzucasz 1 item ręcznie do droppera startowego.

### 1.2 Połączenia (`connections`)
Zostaw `clock_1hz` oraz `output_digits`, ale przepnij połączenia:

- `clock_1hz.output` → `ring_counter_10.clock`
- `ring_counter_10.digit_X` → `output_digits.cmd_X` (dla X=0..9)

Usuń stare połączenia: `counter_4bit.*` i `bcd_decoder.*`.

### 1.3 Truth table
Jeśli trzymasz `truth_table`, uprość ją do opisu stanu one‑hot (opcjonalnie). Przykład:

```json
"truth_table": {
  "digit_0": {"state": 0},
  "digit_1": {"state": 1},
  ...
  "digit_9": {"state": 9}
}
```

---

## 2) Zmiany w `voxel_grid.json` (KLUCZOWE)

### 2.1 Zasada „perfekcyjnego” voxela
W Minecraft:
- **redstone_wire / repeater / comparator** muszą stać **na pełnym bloku**.
- W JSON nie możesz mieć dwóch bloków w tych samych współrzędnych.
- Dlatego: **zawsze** dawaj podparcie jako stone na `y-1`, a komponent na `y`.

W tej instrukcji przyjmujemy:
- **podłoga** (podparcie) jest na `y=0`,
- większość urządzeń jest na `y=1`,
- magistrala zasilania dropperów jest na `y=3` (wire) na stone na `y=2`.

### 2.2 Usuń stare sekcje
Z `sections` usuń całe:
- `counter_bit0`
- `counter_bit1`
- `counter_bit2`
- `counter_bit3`
- `bcd_decoder`

Zostaw (możesz przebudować ich zawartość):
- `clock_generator`
- `command_blocks`
- `power_supply`

---

## 3) Nowy układ w świecie: Dropper Ring Counter + Command Blocks

### 3.1 Współrzędne ring countera (10 dropperów)
Wszystkie droppere stoją na `y=1`. Pod nimi musi być stone na `y=0`.

**Droppery (D0..D9):**

| Dropper | x | y | z | facing | następny |
|---|---:|---:|---:|---|---|
| D0 | 6 | 1 | 6 | east | D1 |
| D1 | 7 | 1 | 6 | east | D2 |
| D2 | 8 | 1 | 6 | east | D3 |
| D3 | 9 | 1 | 6 | south | D4 |
| D4 | 9 | 1 | 7 | south | D5 |
| D5 | 9 | 1 | 8 | west | D6 |
| D6 | 8 | 1 | 8 | west | D7 |
| D7 | 7 | 1 | 8 | west | D8 |
| D8 | 6 | 1 | 8 | north | D9 |
| D9 | 6 | 1 | 7 | north | D0 |

**Wymóg:** kierunek `facing` musi dokładnie wskazywać na kolejny dropper.

**Item startowy:** wrzuć **1× cobblestone** do `D0` (to jest stan „0”).

---

### 3.2 Magistrala zasilania dropperów (żeby item przesuwał się o 1 krok na impuls)
Każdy dropper ma nad sobą:
- stone na `y=2` w tej samej kolumnie (x,z),
- redstone_wire na `y=3` (x,z).

Te 10 redstone_wire musi być połączone w jedną sieć (one już się łączą, bo droppere są ortogonalnie sąsiadujące jak pętla).

**Dla każdego droppera `Dx` dodaj:**
- `minecraft:stone` na `(x,2,z)` jako `dropper_power_block`
- `minecraft:redstone_wire` na `(x,3,z)` jako `dropper_power_bus`

---

### 3.3 Komparatory: wyjścia `digit_0 … digit_9`
Komparator stoi na `y=1`, pod nim stone na `y=0`. Komparator **czyta droppera** i daje sygnał na wyjściu tylko wtedy, gdy w dropperze jest item.

Ustaw komparatory tak, żeby **ich tył (wejście)** był skierowany do droppera.

**Komparatory (C0..C9):**

| Digit | Comparator x,y,z | comparator facing | czyta droppera |
|---|---|---|---|
| digit_0 | (6,1,5) | north | D0 (6,1,6) |
| digit_1 | (7,1,5) | north | D1 (7,1,6) |
| digit_2 | (8,1,5) | north | D2 (8,1,6) |
| digit_3 | (10,1,6) | east | D3 (9,1,6) |
| digit_4 | (10,1,7) | east | D4 (9,1,7) |
| digit_5 | (10,1,8) | east | D5 (9,1,8) |
| digit_6 | (8,1,9) | south | D6 (8,1,8) |
| digit_7 | (7,1,9) | south | D7 (7,1,8) |
| digit_8 | (5,1,8) | west | D8 (6,1,8) |
| digit_9 | (5,1,7) | west | D9 (6,1,7) |

> Uwaga o `facing`: przyjmujemy semantykę Minecrafta: `facing` wskazuje **kierunek wyjścia** komparatora.

---

### 3.4 Command blocks: bezpośrednio na wyjściach komparatorów
Żeby impulse command block odpalał **raz na wejściu** danej cyfry:
- command block stawiamy **bezpośrednio na wyjściu komparatora** (sąsiedni blok w kierunku `facing` komparatora).

**Command blocki (CMD0..CMD9)** — wszystkie: `minecraft:command_block`, `type: impulse`, `conditional:false`, `facing: up`:

| Digit | Command block x,y,z | Komenda |
|---|---|---|
| 0 | (6,1,4) | `/say 0` |
| 1 | (7,1,4) | `/say 1` |
| 2 | (8,1,4) | `/say 2` |
| 3 | (11,1,6) | `/say 3` |
| 4 | (11,1,7) | `/say 4` |
| 5 | (11,1,8) | `/say 5` |
| 6 | (8,1,10) | `/say 6` |
| 7 | (7,1,10) | `/say 7` |
| 8 | (4,1,8) | `/say 8` |
| 9 | (4,1,7) | `/say 9` |

Pod każdym command blockiem daj stone na `y=0`.

---

## 4) Nowy zegar (`clock_generator`) i podłączenie do magistrali dropperów

### 4.1 Zegar: „torch inverter + repeater delay loop” (≈ 1 s)
Cel: sygnał, który **przełącza się** co ~20 ticków. Droppere reagują na zbocze narastające, więc przesuwają item raz na cykl.

**Lokalizacja zegara:** buduj na warstwie `y=3` (wire/repeatery) z podparciem `y=2`.

#### Elementy:
- Inwerter: stone block + redstone_torch (wall torch) tak, żeby blok mógł być zasilany z powrotu.
- Łańcuch opóźnień: 3 repeatery w szeregu z opóźnieniami `4,4,1` (suma 9 ticków).
- Powrót: redstone_wire wraca do bloku inwertera.

> Jeśli translator nie wspiera wall torch, zamień inwerter na **klasyczny NOT**: torch na boku stone i doprowadzenie sygnału do stone.

#### Konkretne współrzędne (zegar na y=3):
Podparcie:
- stone na `y=2` w miejscach, gdzie stoją wire/repeatery/torch.

Inwerter:
- `minecraft:stone` (clock_inverter_block) na `(1,2,2)`  **(to jest PODPARCIE)**
- `minecraft:stone` (clock_logic_block) na `(1,3,2)`  **(to jest BLOK LOGIKI)**

Torch (wall):
- `minecraft:redstone_torch` na `(2,3,2)` z `properties: {"facing":"east"}` — ma być przyczepiony do `clock_logic_block`.

Repeatery:
- `(3,3,2)` repeater facing east delay 4
- `(4,3,2)` repeater facing east delay 4
- `(5,3,2)` repeater facing east delay 1

Wyjście zegara:
- `minecraft:redstone_wire` na `(6,3,2)` (clock_out)

Powrót (wire):
- `minecraft:redstone_wire` na `(6,3,3)`, `(5,3,3)`, `(4,3,3)`, `(3,3,3)`, `(2,3,3)`, `(1,3,3)`

Sprzężenie do bloku logiki:
- Upewnij się, że wire na `(1,3,3)` zasila `clock_logic_block` na `(1,3,2)` (sąsiadują).

**Start/Stop**:
- Podłącz `master_switch` (z `power_supply`) do odcięcia zegara: najprościej zasilać/odcinać `clock_logic_block` (np. wire doprowadzony z master switch do `(1,3,2)`).

> Jeśli agent nie chce robić start/stop: ustaw zegar „always on” — wtedy cały układ działa od razu.

---

### 4.2 Połączenie zegara z bus dropperów
Bus dropperów jest na `y=3` na współrzędnych dropperów (np. `(6,3,6)` itd.)

Połącz `clock_out` z bus’em linią redstone_wire na `y=3` z podparciem na `y=2`.

Minimalna trasa:
- wire: `(6,3,2) -> (6,3,3) -> (6,3,4) -> (6,3,5) -> (6,3,6)`
- stone podparcia: dodaj `minecraft:stone` na `y=2` w `(6,2,4)` i `(6,2,5)` jeśli nie istnieją.

---

## 5) Jak agent ma zaktualizować `sections` w voxel_grid.json

### 5.1 Nowa sekcja `ring_counter_10`
Dodaj do `sections` nowy obiekt (lub zmodyfikuj istniejący „counter”), który zawiera:
- podparcia (stone y=0) pod droppery/komparatory/commandblocki,
- droppere y=1,
- komparatory y=1,
- command blocki y=1,
- power blocks y=2 nad dropperami,
- redstone_wire y=3 nad power blocks (bus).

**Ważne:**
- żadnych duplikatów (x,y,z),
- każdy wire/repeater/comparator musi mieć stone pod spodem.

### 5.2 Sekcja `command_blocks`
Możesz ją zostawić, ale **przenieś** command blocki na współrzędne z tabeli z pkt 3.4.
Usuń stare „input_to_cmd_*” redstone_wire pod spodem (nie były poprawne).

### 5.3 Sekcja `signal_routing`
Uprość:
- `clock_to_ring_bus`: from `clock_generator.output` to `ring_counter_10.bus`
- brak osobnych `Q*` i `bcd_decoder`.

---

## 6) Checklista „perfekcyjności” (agent ma odhaczyć)

1) **Brak kolizji współrzędnych**: żadna para voxelów nie ma tego samego `(x,y,z)`.
2) **Podparcie redstone**: każda `minecraft:redstone_wire`, `minecraft:repeater`, `minecraft:comparator` ma pod spodem `minecraft:stone`.
3) **Facing droperów**: każdy dropper wskazuje dokładnie na następny w pętli.
4) **Facing komparatorów**: każdy komparator czyta droppera (tył do droppera).
5) **Command blocki**: stoją dokładnie na wyjściu komparatora.
6) **Bus zasilania**: na `y=3` jest jedna spójna sieć zasilająca wszystkie droppery przez stone na `y=2`.
7) **Zegar**: generuje przełączający się sygnał; jego `clock_out` jest połączone z bus’em.
8) **Stan startowy**: 1 item w D0 → przy starcie pierwsze odpalenie powinno być: `/say 1` po ~1 cyklu (bo item przejdzie do D1).

---

## 7) Minimalny test w świecie (co agent powinien „zobaczyć”)
Po uruchomieniu:
- co ~1 sekundę pojawia się w czacie kolejna cyfra,
- po 9 wraca do 0,
- nigdy nie ma „pustych” kroków, nie ma podwójnych przeskoków.

