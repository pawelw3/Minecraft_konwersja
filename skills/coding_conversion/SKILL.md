# SKILL.md — Zasady implementacji konwerterów modów (Minecraft 1.7.10 → 1.18.2)

Ten dokument jest „skill guide” dla agenta implementującego **kod konwersji** (mapy/świata + dane modów) między wersjami Minecrafta, w szczególności dla konwersji elementów **modów** (np. AE2) z 1.7.10 do 1.18.2.

Celem jest:
- konwersja **oparta o faktyczne zachowanie moda** (źródła / dekompilacja),
- brak „wymyślonych” struktur danych,
- spójny pipeline: JVM/worker robi IO świata, a konwertery modów robią transformację danych.

---

## 1) Zasada nadrzędna: implementujemy na podstawie źródeł, a nie domysłów

### 1.1. Najpierw kod źródłowy moda
1. Znajdź repozytorium / tag / commit odpowiadający danej wersji moda.
2. Zidentyfikuj klasy odpowiedzialne za:
   - serializację NBT (1.7.10: `readFromNBT()/writeToNBT()`),
   - serializację NBT (1.18.2: `load()/saveAdditional()` lub analogiczne),
   - logikę, która determinuje kształt danych (np. encodowane patterny, inventory, owner/UUID, itp.).
3. Mapuj pola **1:1** zgodnie z tym co faktycznie jest zapisywane/odczytywane.

**Nigdy nie twórz własnych kluczy w NBT** „bo tak będzie wygodniej”.
Jeśli czegoś nie da się odtworzyć, dodaj ostrzeżenie i zastosuj tryb fail-safe.

### 1.2. Jeśli nie ma źródeł → dekompilacja JAR
Jeśli mod nie udostępnia źródeł dla danej wersji:
1. Zdekompiluj `.jar` (np. CFR / FernFlower).
2. Szukaj metod odpowiadających zapisowi/odczytowi danych:
   - 1.7.10: `readFromNBT`, `writeToNBT`, `readFromPacket`, `writeToPacket` (jeśli istotne),
   - 1.18.2: `load`, `saveAdditional`, `getUpdateTag`, `handleUpdateTag` (jeśli występują).
3. Zapisz w kodzie konwertera krótką adnotację: „źródło prawdy” (klasa/metoda).

> Konwerter ma być „udowadnialny”: każda istotna transformacja pola musi mieć odniesienie do kodu źródłowego lub dekompilacji.

---

## 2) Zasada formatu: blockstate ≠ NBT (1.13+)

W 1.13+ (w tym 1.18.2) **większość wariantów i orientacji** jest w **BlockState properties**, a nie w dowolnych tagach w TileEntity/BlockEntity NBT.

### 2.1. Nigdy nie dodawaj „wymyślonych” pól typu `visual`, `rotation`, itp.
Jeśli konwersja ma ustawić orientację lub wariant:
- zwróć `blockstate_props` (np. `{"facing":"north"}`),
- a nie zapisuj nic w NBT typu `visual.rotation`.

Jeżeli dany blok rzeczywiście zapisuje orientację w BE NBT (rzadziej) — musi to wynikać ze źródeł.

---

## 3) Kontrakt danych: co przyjmuje konwerter, co zwraca

### 3.1. Wejście (1.7.10)
Konwerter dostaje **wszystko, co jest potrzebne do poprawnej decyzji**:
- `block_id_1710` (string lub numeric + resolver),
- `metadata` (0–15, legacy),
- `te_nbt_1710` (TileEntity NBT jako dict/JSON),
- `pos` (`x,y,z`) oraz opcjonalny kontekst (wymiar/chunk).

### 3.2. Wyjście (1.18.2)
Konwerter zwraca:
- `block_id_1182`,
- `blockstate_props` (dict),
- `be_nbt_1182` (dict),
- `extra_blocks` (lista dodatkowych bloków do postawienia, jeśli logika moda tego wymaga),
- `warnings/errors` (diagnostyka).

### 3.3. Spójność metadata
**Metadata nigdy nie jest „wyciągana z TE NBT”**, o ile źródła moda nie potwierdzają, że mod tak robi.
Metadata jest parametrem wejściowym z warstwy IO świata.

---

## 4) Fail-safe i diagnostyka zamiast zgadywania

Jeśli czegoś nie da się wiarygodnie przenieść:
- nie generuj „prawie-danych”,
- nie twórz własnych kluczy NBT,
- zwróć ostrzeżenie z kodem, np. `MOD-W-PATTERN-FORMAT-UNKNOWN`,
- zastosuj bezpieczny fallback (np. pomiń patterny, zachowaj tylko blok bez zawartości, itp.).

Ważne: konwersja ma być **deterministyczna** i **audytowalna**.

---

## 5) Testy: snapshoty i przypadki brzegowe

### 5.1. Testy jednostkowe (snapshot NBT / props)
Dla każdego konwertera:
- wejście NBT 1.7.10 + metadata,
- oczekiwane `block_id_1182`,
- oczekiwane `blockstate_props`,
- oczekiwane `be_nbt_1182`,
- oczekiwane ostrzeżenia/błędy.

### 5.2. Testy regresji
Dodaj testy na:
- różne metadata (0..15 tam gdzie ma znaczenie),
- puste sloty/inventory,
- nietypowe tagi itemów,
- brakujące pola w NBT,
- nieznane warianty.

### 5.3. Test integracyjny „end-to-end”
Minimum: batch bloków z jednego chunka → konwersja → wynik w strukturach docelowych.
Jeśli IO jest w JVM, integracja może sprawdzać poprawność kontraktu wymiany danych.

---

## 6) World IO: **Sections w `.mca` obsługuje JVM/worker (Kotlin + hephAIstos)**

### 6.1. Zasada
Warstwa edycji chunków/sections, palet, packed blockstates oraz zapisu/odczytu `.mca` **nie jest implementowana w Pythonie**.

Dla edycji `Sections` w `.mca` należy korzystać z istniejącej, sprawdzonej biblioteki w JVM/worker, opartej o **hephAIstos**.

### 6.2. Rola Pythona
Python dostarcza:
- transformację danych modów,
- mapowanie block_id + metadata + TE NBT → blockstate props + BE NBT,
- reguły „extra_blocks”,
- ostrzeżenia i błędy.

### 6.3. Integracja
JVM/worker:
- czyta świat 1.7.10,
- batchuje dane bloków/TE,
- wywołuje Python (subprocess / HTTP / gRPC) jako transformator,
- zapisuje wynik do świata 1.18.2.

---

## 7) Zasada „wspólnego kodu”: funkcjonalność ogólna wynosimy na poziom wspólnego `src`

Jeśli agent zauważy, że implementowana funkcjonalność:
- nie jest specyficzna dla jednego moda,
- i/lub podobny kod już istnieje w folderze konwersji innego moda,

to należy:
1. **wydzielić** takie pliki/moduły do wspólnego katalogu w `src` (np. `src/common/` lub `src/conversion_core/`),
2. zaktualizować importy w konwerterach modów,
3. usunąć duplikaty z folderów poszczególnych modów.

Przykłady „wspólnej funkcjonalności”:
- resolver ID / mapowania legacy,
- narzędzia do konwersji orientacji i mapowania metadata → blockstate,
- serializacja/deserializacja NBT do JSON dla komunikacji JVM ↔ Python,
- walidatory kontraktów payloadów,
- wspólne typy danych (dataclasses) i narzędzia testowe.

**Cel:** brak kopiowania i rozjazdów wersji tej samej logiki między modami.

---

## 8) Struktura kodu i styl pracy

### 8.1. Jedna „prawda” dla interfejsów
- Wszystkie konwertery NBT implementują ten sam kontrakt.
- Orchestrator nie może „po cichu” wymagać innej sygnatury niż konwertery.

### 8.2. Każdy konwerter musi mieć sekcję „Source mapping”
Na górze pliku/klasy dodaj komentarz:
- wersja moda 1.7.10: klasa/metoda źródłowa,
- wersja moda 1.18.2: klasa/metoda źródłowa,
- krótkie mapowanie pól.

### 8.3. Zero „magic numbers” bez źródła
Stałe i formaty (np. rozmiary, flagi, nazwy kluczy) muszą wynikać ze źródeł.
Jeśli to hipoteza → opisz ją jako hipotezę i dodaj ostrzeżenie w runtime.

---

## 9) Checklist przed merge

1. Brak autorskich pól w output NBT (`visual`, `#c`, itp.).
2. Orientacja i warianty są w `blockstate_props`.
3. Metadata jest przekazywana wejściem, nie odczytywana z TE NBT (chyba że źródła mówią inaczej).
4. World IO (Sections w `.mca`) jest wyłącznie w JVM/worker (hephAIstos).
5. Wspólne komponenty są w wspólnym `src`, nie zduplikowane w folderach modów.
6. Testy snapshotowe + brzegowe przechodzą.
7. Każdy konwerter ma „Source mapping” do źródeł/dekompilacji.

---

**Koniec dokumentu.**
