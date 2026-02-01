# Instrukcja poprawek dla Zadania 3 (kod konwersji AE2 1.7.10 → 1.18.2)

Ten dokument opisuje **co dokładnie agent ma poprawić** w implementacji konwersji z Zadania 3, aby:
- konwersja przestała być „modelowa/umowna” i zaczęła odpowiadać **realnym formatom świata Minecraft**,
- dane AE2 były przenoszone zgodnie z **rzeczywistą serializacją NBT** (z kodu źródłowego AE2, a nie z założeń),
- pipeline dało się zastosować na mapie / chunkach (a nie tylko na ręcznie podanych słownikach),
- testy weryfikowały poprawność na „twardych” przypadkach.

> **UWAGA**: obecny kod wygląda jak „biblioteka transformująca słowniki”. Aby spełnić definicję „konwertera świata”, trzeba wdrożyć warstwę I/O (odczyt 1.7.10 + zapis 1.18.2) oraz doprecyzować formaty NBT zgodnie ze źródłami AE2.

---

## 0) Priorytety (kolejność prac)

### P0 — poprawki krytyczne (bez nich wynik i tak będzie niepoprawny)
1. Usunąć / zastąpić „wymyślone” pola docelowe (np. `visual.rotation`) realnym mechanizmem 1.18.2 (**blockstate** + poprawna struktura BE NBT).
2. Poprawić przepływ `metadata` do konwerterów NBT (bug spójności API).
3. Urealnić format przenoszenia *encoded patterns* (Interface → Pattern Provider) – obecny format (`'#c'`) wygląda na autorski placeholder.
4. Zaimplementować realne czytanie mapowania ID z `level.dat` (lub innego źródła Forge) dla 1.7.10, albo jasno zadeklarować i obsłużyć tryb „tylko string-id” – bez udawania.

### P1 — poprawki funkcjonalne (żeby dane AE2 były sensownie przenoszone)
5. Zweryfikować i poprawić nazwy kluczy NBT dla AE2 1.18.2 (Drive, Cells, IO Port, Security Station, itp.) na podstawie metod `load()/saveAdditional()` w kodzie AE2.
6. Dopracować orientację: uwzględnić `forward` **i** `up` albo mapować do pełnego `BlockState` (często to nie jest tylko 6 facingów).

### P2 — kompletność i jakość
7. Wydzielić warstwę I/O (chunk/region) i dodać testy integracyjne (konwersja prawdziwego fragmentu świata).
8. Dodać raportowanie i „tryb ostrożny”: jeśli dane są nieobsługiwane, emitować ostrzeżenia i nie tworzyć „zmyślonych” struktur.

---

## 1) Poprawić architekturę: „NBT transform” ≠ „konwerter świata”

### 1.1. Dodaj warstwę wejścia/wyjścia świata
Agent ma dopisać moduł (np. `world_io/`), który:
- potrafi odczytać **regiony 1.7.10** (`.mca`) i wyciągnąć:
  - `block_id` (lub numeric id + meta),
  - `metadata`,
  - Tile Entity NBT (1.7.10).
- potrafi wygenerować dane dla **1.18.2**:
  - `BlockState` (palette + packed states),
  - Block Entity NBT w formacie oczekiwanym przez 1.18.2,
  - ewentualne entity/item-y jeśli dotyczy.

**Dlaczego?**  
W 1.13+ większość orientacji i wariantów siedzi w **blockstates**, nie w „dowolnych tagach” tile entity.

### 1.2. Ustal jeden kontrakt danych wejściowych/wyjściowych
Zdefiniuj dataclass / interfejs:
- `BlockInput1710`: `block_id|numeric_id`, `metadata`, `te_nbt`, `pos`.
- `BlockOutput1182`: `block_id`, `blockstate_props`, `be_nbt`, `additional_blocks`.

I dopiero na tym kontrakcie buduj `AE2Converter`.

---

## 2) Usunąć „wymyślone” pola i zastąpić je realnym formatem

### 2.1. Usuń wszędzie `converted['visual'] = {'rotation': ...}`
To pole nie jest standardowym polem BE w 1.18.2.
**Zamiast tego:**
- orientacja → **blockstate properties** (np. `facing=north`, `powered=true`, itp.) zależnie od konkretnego bloku,
- BE NBT zawiera tylko to, co AE2 rzeczywiście zapisuje.

**Konkretnie do poprawy:**
- `nbt_converters/crafting_converter.py` (CraftingUnit/Storage/Accelerator),
- `nbt_converters/utility_converters.py` (Charger/Inscriber/itd.),
- `nbt_converters/drive_converter.py`,
- wszędzie gdzie jest `visual`.

**Akceptacja:** w wyniku konwersji NIE pojawia się `visual` jeśli nie istnieje w docelowym AE2.

### 2.2. Zmień `_get_orientation()`
Obecnie `_get_orientation()` zwraca `forward/up` ale realnie używacie tylko `facing`.
Agent ma:
- zmapować `forward+up` do pełnej reprezentacji orientacji docelowego bloku (często to kombinacja właściwości blockstate),
- albo jawnie oznaczyć „nieobsługiwane orientacje” i dodać ostrzeżenie.

---

## 3) Naprawić bug: metadata nie trafia do konwerterów NBT

### Problem
`AE2Converter.convert_block(..., metadata=...)` używa metadata do wariantu ID, ale **NBT konwerter** (np. `CraftingStorageConverter`) czyta metadata z `nbt_1710.get('metadata')`, którego zwykle nie ma.

### Wymagane poprawki (jedna z opcji)
**Opcja A (zalecana):** zmień sygnaturę `BaseNBTConverter.convert()` na:
```python
convert(self, nbt_1710: Dict[str, Any], block_id: str = None, metadata: int = 0) -> NBTConversionResult
```
i przekaż `metadata` z `AE2Converter._convert_nbt()`.

**Opcja B:** przed wywołaniem konwertera wstrzyknij `metadata` do kopii NBT:
```python
nbt_copy = dict(nbt_1710)
nbt_copy['__metadata'] = metadata
```
i w konwerterach czytaj `__metadata`.

**Akceptacja:**
- `CraftingStorageConverter` i inne zależne od metadata działają poprawnie dla metadata=0..3 bez sztucznych obejść.

---

## 4) Interface → Pattern Provider: urealnić format przenoszenia patternów

### Problem
`InterfaceConverter` tworzy patterny w formacie z kluczem `'#c'` oraz ustawia `id='ae2:crafting_pattern'` „w ciemno”.
To wygląda jak placeholder, nie jak realny format AE2.

### Co agent ma zrobić
1. W źródłach AE2 1.18.2 odnaleźć klasę odpowiedzialną za zapis/odczyt encoded patternów (item + NBT).
2. Zaimplementować konwersję:
   - jeśli 1.7.10 trzyma encoded pattern jako item z NBT, to w 1.18.2 należy zachować/odtworzyć EXACT NBT oczekiwany przez AE2,
   - rozróżnić crafting vs processing (jeżeli to ma konsekwencje w NBT / item id).
3. Usunąć `'#c'` i zastąpić prawdziwą strukturą NBT.

### Minimalny kompromis (jeśli nie da się 1:1)
Jeśli nie da się odtworzyć formatu, agent ma:
- przenosić pattern jako „niezmieniony blob NBT” (jeśli możliwe),
- albo emitować ostrzeżenie i NIE generować Pattern Provider, tylko zachować Interface bez patternów (fail-safe).

**Akceptacja:**
- Patterny po konwersji są rozpoznawane przez AE2 w 1.18.2 (manualny test w grze lub testy snapshot NBT zgodne ze źródłem).

---

## 5) IDResolver: przestać udawać „dynamiczne ID” bez parsowania

### Problem
`IDResolver.load_from_map()` ma TODO i „zakłada standardowe ID”.

### Wymagane poprawki
1. Jeśli celem jest konwersja świata 1.7.10:
   - agent ma wdrożyć parsowanie `level.dat` NBT i sekcji Forge dotyczącej mapowania bloków,
   - albo wprost wspierać odczyt z chunków, gdzie Forge może przechowywać string-id (zależnie od sposobu zapisu).
2. Jeśli tego nie robimy:
   - `load_from_map()` ma zwracać błąd/ostrzeżenie „nieobsługiwane”,
   - a konwerter ma działać w trybie `string-id only` i nie tworzyć fałszywej pewności.

**Akceptacja:**
- nie ma „cichego sukcesu” bez realnego mapowania,
- jest deterministyczny tryb działania + komunikaty.

---

## 6) Zweryfikować każdy konwerter NBT z rzeczywistym źródłem AE2 1.18.2

Poniżej lista miejsc, gdzie agent ma przejść po kodzie AE2 i potwierdzić:
- które klucze są prawdziwe,
- co jest blockstate, a co w BE,
- jak wygląda serializacja list itemów.

### 6.1. DriveConverter (`drive_converter.py`)
- Potwierdzić format inventory w 1.18.2 (klucz `items` / slotowanie / typ item stack).
- Potwierdzić, czy `fuzzyMode` jest stringiem i jakie są dokładne wartości.

### 6.2. StorageCellConverter (`storage_cell_converter.py`)
- Potwierdzić docelowe klucze: czy jest `storage.items/storage.count` czy inaczej.
- Sprawdzić jak AE2 zapisuje dane celli jako item (NBT itemu).
- Potwierdzić format `partition` i `fuzzyMode`.

### 6.3. IO Port / Security Station / Wireless Access Point (`utility_converters.py`)
- **Security Station**: obecnie jest TODO dot. UUID → w 1.18.2 UUID jest krytyczny; agent ma wdrożyć realną konwersję:
  - jeśli 1.7.10 ma nazwy graczy, to spróbować mapowania (jeśli brak danych – oznaczyć nieobsługiwane),
  - nie zapisywać pustych UUID „na siłę”.
- IO Port: potwierdzić klucze i semantykę transferu (czy te stany w ogóle mają sens przenosić).

### 6.4. Crafting converters (`crafting_converter.py`)
- Crafting Monitor / Molecular Assembler: potwierdzić jakie stany są istotne i jak są serializowane w 1.18.2.
- Wszędzie usunąć `visual`.

**Akceptacja ogólna:**  
Każdy konwerter ma w komentarzu/README sekcję:
- „Źródło 1.7.10: klasa/metoda…”
- „Źródło 1.18.2: klasa/metoda…”
- „Mapowanie pól: …”

---

## 7) Testy: rozbudować poza „czy mapping istnieje”

Obecne testy głównie sprawdzają, że mapping zwraca `ae2:*`. To za mało.

### 7.1. Testy jednostkowe NBT (snapshot)
Dla każdego konwertera:
- wejściowe NBT 1.7.10 (przykład),
- oczekiwane NBT 1.18.2 (snapshot),
- oraz oczekiwane blockstate properties (jeśli dotyczy).

### 7.2. Testy regresji na „trudnych przypadkach”
- Interface z patternami: czy generuje dodatkowy blok i czy usuwa patterny z Interface.
- Crafting Storage: metadata=0..3 → poprawny wariant + spójne NBT (size).
- Drive: 10 slotów z różnymi cellami + puste sloty + różne tagi itemów.

### 7.3. Test integracyjny (mini-świat)
Agent ma dodać fixture: mały „wycinek” świata 1.7.10 (np. 1 chunk) i oczekiwany wynik 1.18.2 w postaci zrzutu chunk NBT.
Jeśli nie da się dołączyć binarek, to przynajmniej:
- surowe NBT chunk jako JSON (z narzędzia),
- test porównujący strukturę.

---

## 8) Raportowanie i tryby działania

Agent ma dodać:
- tryb `strict=True`: jeśli pole nieznane / brak danych – błąd i brak konwersji bloku,
- tryb `lenient=True`: tworzy wynik, ale z ostrzeżeniami i bez „zmyślonych” pól.

Wynik ma zwracać:
- listę ostrzeżeń z kodami (np. `AE2C-W-PATTERN-FORMAT-UNKNOWN`),
- listę błędów z kodami.

---

## 9) Checklist „Definition of Done” dla Zadania 3

Agent może uznać Zadanie 3 za poprawione, jeśli:

1. Nie ma w output NBT sztucznych pól typu `visual`, `#c`, itp.
2. Metadata jest przekazywana spójnie do NBT konwersji.
3. Interface→Pattern Provider działa na podstawie realnej serializacji patternów, albo w trybie fail-safe (bez generowania śmieci).
4. IDResolver nie udaje „dynamicznych ID” – albo realnie je czyta, albo jawnie nie wspiera.
5. Każdy konwerter ma sekcję „source mapping” do klas/metod w AE2.
6. Testy jednostkowe obejmują NBT snapshoty dla Drive/Cells/Interface/Crafting Storage.
7. Jest chociaż jeden test integracyjny end-to-end na danych chunk (lub ich reprezentacji).

---

## 10) Konkretne miejsca do edycji (szybka mapa plików)

- `src/converters/ae2/ae2_converter.py`
  - przekazywanie metadata do konwerterów NBT,
  - przekazywanie blockstate props w wyniku.

- `src/converters/ae2/nbt_converters/base_converter.py`
  - zmiana kontraktu `convert(..., metadata=0)` lub wstrzyknięcie metadata,
  - poprawa orientacji.

- `src/converters/ae2/nbt_converters/interface_converter.py`
  - usunąć `#c`, wdrożyć prawdziwy format patternów,
  - jasne rozróżnienie crafting/processing.

- `src/converters/ae2/nbt_converters/crafting_converter.py`
  - usunąć `visual`,
  - poprawić odczyt metadata.

- `src/converters/ae2/utils/id_resolver.py`
  - wdrożyć parsowanie `level.dat` albo jawny brak wsparcia.

- `src/converters/ae2/tests/test_ae2_converter.py`
  - dodać testy snapshot NBT i testy trudnych przypadków.

---

## 11) Proponowany plan pracy (2–4 iteracje)

### Iteracja 1: naprawa kontraktów i usunięcie placeholderów
- metadata flow
- usunięcie `visual`
- lepsza orientacja (min. facing jako blockstate prop)

### Iteracja 2: urealnienie Interface/Patterns
- źródła AE2 → odtworzenie NBT patternów
- testy snapshot patternów

### Iteracja 3: urealnienie storage/drive
- klucze i struktury z AE2 1.18.2
- testy snapshoty

### Iteracja 4: warstwa I/O świata
- chunk/region read/write
- test integracyjny

---

**Koniec instrukcji.**
