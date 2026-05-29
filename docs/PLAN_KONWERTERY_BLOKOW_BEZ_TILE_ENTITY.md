# Plan: konwertery blokow bez TileEntity

## 1. Cel

Ten dokument opisuje standard dodawania do modow w `src/converters/<mod>/` osobnego konwertera dla zwyklych blokow modowych bez TileEntity.

Problem, ktory ma rozwiazac ta warstwa: obecna szybka konwersja direct zapisuje teren vanilla bezposrednio do chunkow, a mody obsluguje glownie przez TileEntity -> eventy. To gubi bloki modowe, ktore sa zwyklymi blokami w `Sections`, ale nie maja NBT/TileEntity. Przykladem jest `chisel:woolen_clay` z numeric ID `1783`, ktory w direct-konwersji spadl do `minecraft:air`, bo nie przeszedl przez `convert_te_to_events()`.

Docelowo kazdy mod, ktory ma istotne bloki bez TE, powinien miec lekki `block_only_converter`, niezalezny od konwerterow TileEntity.

## 2. Zakres i zasady

Konwerter blokow bez TileEntity sluzy tylko do blokow, ktore:

- sa zapisane w chunk `Sections` jako numeric ID + metadata,
- nie maja osobnego TileEntity/BlockEntity na tej pozycji,
- nie wymagaja przenoszenia inventory, energii, fluidow, sieci ani custom NBT,
- moga zostac opisane jako docelowy blockstate 1.18.2.

Nie nalezy uzywac tej warstwy dla:

- maszyn i kontenerow z NBT,
- multipartow z lista partow,
- blokow, ktore musza utworzyc BlockEntity,
- przypadkow wymagajacych specjalnego JVM workera albo post-processu.

Dla takich przypadkow dalej obowiazuje obecny workflow TileEntity/eventow.

## 3. Workflow per mod: tylko 2 kroki

Konwertery blokow bez TE maja krotszy cykl pracy niz pelne konwertery modow. Nie wymagaja osobnych symulacji funkcjonalnych, bo zwykly blok bez TE nie ma trwalego stanu runtime.

### Krok 1: analiza source kodu

Dla danego moda nalezy przygotowac raport w `src/converters/<mod>/`, np. `BLOCK_ONLY_ANALIZA.md`.

Raport musi ustalic:

- jakie bloki moda sa zwyklymi blokami bez TE,
- jakie registry names wystepuja w 1.7.10,
- jak numeric ID sa zapisane w mapie przez FML `ItemData` w `level.dat`,
- jak metadata 0-15 przeklada sie na wariant, kolor, orientacje albo teksture,
- jakie docelowe bloki/blockstates istnieja w paczce 1.18.2,
- jakie sa fallbacki, gdy nie ma odpowiednika 1:1,
- ktore targety sa pewne, a ktore maja niski poziom pewnosci.

Analiza ma bazowac przede wszystkim na lokalnym source/dekompilacji w `mod_src/`, a dopiero pomocniczo na dokumentacji zewnetrznej. Dla modow dekoracyjnych trzeba sprawdzac rowniez tekstury i generated blockstates docelowych modow, bo sama nazwa rodziny czesto nie wystarcza.

Minimalny output kroku 1:

- tabela `numeric_id / registry_name / metadata / source variant / target block / confidence`,
- lista fallbackow,
- lista wariantow odrzuconych albo wymagajacych recznego review,
- handoff z decyzjami mapowania.

### Krok 2: implementacja i test headless

Implementacja powinna powstac w `src/converters/<mod>/` jako osobna warstwa dla blokow bez TE.

Zalecana struktura:

```text
src/converters/<mod>/
├── block_only_converter.py
├── block_only_mappings.py
└── tests/test_block_only_converter.py
```

Interfejs logiczny powinien byc wspolny dla modow:

```python
convert_block_only(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: tuple[int, int, int],
) -> BlockOnlyResult
```

`BlockOnlyResult` powinien zawierac:

- `success: bool`,
- `target_block: str`,
- `blockstate_props: dict[str, str]`,
- `confidence: str`,
- `warnings: list[str]`,
- `errors: list[str]`.

Konwerter nie powinien zwracac NBT ani inventory. Jesli konwersja wymaga NBT, to znaczy, ze blok nie nalezy do warstwy block-only.

## 4. Integracja z glownym konwerterem

Glowny direct terrain writer powinien dzialac w tej kolejnosci:

1. Odczytaj numeric ID + metadata z chunk `Sections`.
2. Jesli blok jest vanilla, mapuj go obecna szybka tabela vanilla i wpisz bezposrednio do palety chunka.
3. Jesli blok nie jest vanilla, odczytaj `registry_name` z FML `ItemData` w `level.dat`.
4. Przekaz `numeric_id`, `registry_name`, `metadata` i `position` do centralnego routera block-only.
5. Jesli router zwroci sukces, wpisz `target_block` i `blockstate_props` bezposrednio do chunkow 1.18.2.
6. Jesli router nie zna bloku, uzyj kontrolowanego fallbacku i zapisz ostrzezenie w audycie.

Kluczowa zasada: zwyklych blokow bez TE nie nalezy masowo przepychac przez JVM worker jako eventow, jesli finalny blockstate mozna wpisac bezposrednio do chunkow. Takich blokow moga byc miliony, wiec eventy `set_block` powinny byc wyjatkiem, nie domyslna sciezka.

Eventy nadal sa wlasciwe dla:

- BlockEntity/NBT,
- multipartow,
- post-processow,
- przypadkow wymagajacych specjalnej walidacji po stronie workera,
- recznego materializowania testowych fixture.

## 5. Centralny router block-only

Nalezy dodac centralna funkcje routera dla blokow bez TE, oddzielna od `convert_te_to_events()`.

Zalecane zachowanie:

- wejscie routera to numeric ID, registry name, metadata i pozycja,
- router wybiera konwerter po namespace `registry_name`, np. `chisel:*` -> Chisel block-only converter,
- router nigdy nie powinien domyslnie zmieniac nieznanego modowego bloku na `minecraft:air`,
- fallback musi byc jawny: np. `minecraft:stone`, `minecraft:white_wool`, placeholder dekoracyjny albo inny blok zatwierdzony w mapowaniu,
- kazdy fallback o niskiej pewnosci musi trafic do audytu.

Centralny router powinien korzystac z registry z `level.dat`, bo mapa 1.7.10 zapisuje bloki w `Sections` jako numeric ID. Przyklad:

```text
1783 -> chisel:woolen_clay
metadata 9 -> wariant/kolor wg mapowania Chisel
```

## 6. Audyt i raportowanie

Kazda konwersja block-only powinna miec lekki raport, niezalezny od eventow TE. Zalecany plik:

```text
block_remap_audit.jsonl
```

Minimalne pola wpisu:

```json
{
  "pos": [-1678, 77, -721],
  "source_numeric_id": 1783,
  "source_registry": "chisel:woolen_clay",
  "source_metadata": 9,
  "target_block": "minecraft:white_wool",
  "blockstate_props": {},
  "confidence": "medium",
  "warnings": [
    "metadata color fallback requires visual verification"
  ]
}
```

Audyt ma sluzyc do:

- szybkiego wykrywania blokow, ktore spadly do fallbacku,
- liczenia pokrycia per mod,
- porownywania kolejnych przebiegow konwersji,
- review wizualnego najczestszych strat.

## 7. Testy i kryteria akceptacji

### Testy jednostkowe per mod

Kazdy `block_only_converter` musi miec testy:

- znane `numeric_id + metadata` mapuje sie na oczekiwany target,
- nieznany wariant daje kontrolowany fallback, nie `minecraft:air`,
- target block istnieje w paczce 1.18.2 albo jest vanilla,
- metadata jest interpretowana deterministycznie,
- ostrzezenia pojawiaja sie dla mapowan o niskiej pewnosci.

### Test mapy testowej

Dla kazdego moda z warstwa block-only nalezy przygotowac maly testowy swiat 1.7.10 zawierajacy reprezentatywne bloki bez TE.

Scenariusz:

1. Wstaw reprezentatywne warianty numeric ID + metadata.
2. Uruchom konwersje do 1.18.2.
3. Uruchom headless server 1.18.2.
4. Sprawdz, ze swiat startuje bez crashy.
5. Zweryfikuj probki blokow przed i po restarcie.

### Test integracyjny direct-worker

Po konwersji wycinka mapy:

- liczba modowych blokow bez TE spadajacych do `minecraft:air` musi wynosic `0`,
- wyjatkiem sa tylko bloki, dla ktorych `air` jest jawnie wpisanym i opisanym fallbackiem,
- audyt musi pokazac liczbe mapowan per mod i liste najczestszych fallbackow.

## 8. Pierwszy kandydat: Chisel

Pierwszym praktycznym modem do wdrozenia tej warstwy powinien byc Chisel.

Powod:

- duzo blokow dekoracyjnych bez TE,
- numeric ID i metadata sa zapisane bezposrednio w chunkach,
- obecna direct-konwersja zamienia nieznane numeric ID na `minecraft:air`,
- realny przyklad straty: `1783/meta 9` na pozycji `-1678,77,-721`, czyli `chisel:woolen_clay`.

Dla Chisela implementacja powinna:

- odczytac dynamiczne ID z FML `ItemData`,
- rozpoznawac rodziny `chisel:*`,
- dekodowac metadata na wariant/kolor tam, gdzie source kod lub tekstury to potwierdzaja,
- mapowac do Rechiseled/Chipped/vanilla,
- oznaczac fallbacki z poziomem pewnosci.

## 9. Relacja do istniejacego workflow

Ta warstwa nie zastepuje pelnych konwerterow modow. Jest dodatkiem do obecnego procesu.

Obecny workflow TE/NBT zostaje dla blokow z danymi i funkcjonalnoscia. Block-only workflow jest uproszczony do dwoch krokow, bo jego celem jest zachowanie geometrii i wygladu zwyklych blokow modowych, a nie odtwarzanie logiki maszyn.

W handoffach per mod nalezy jasno rozdzielac:

- co obsluguje `block_only_converter`,
- co obsluguje dotychczasowy TileEntity/NBT converter,
- jakie bloki pozostaja poza zakresem,
- jakie fallbacki wymagaja review wizualnego.

