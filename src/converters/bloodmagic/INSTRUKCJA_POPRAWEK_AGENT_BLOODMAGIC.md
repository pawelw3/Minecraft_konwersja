# Instrukcja dla agenta – poprawki konwersji Blood Magic 1.7.10 → 1.18.2

Cel: doprowadzić konwerter do stanu, w którym **format docelowy (1.18.2) jest zgodny z rzeczywistym NBT / BlockEntity** Blood Magic oraz nie ma sprzeczności *specyfikacja ↔ implementacja ↔ testy*.

Repozytorium/obszar zmian (z tego handoffa):
- `src/converters/bloodmagic/block_mappings.py`
- `src/converters/bloodmagic/converter.py`
- `src/converters/bloodmagic/ritual_converter.py`
- `src/converters/bloodmagic/altar_converter.py`
- `src/converters/bloodmagic/soul_network_converter.py`
- `src/converters/bloodmagic/test_converters.py`
- dokument: `BLOOD_MAGIC_BLOCKS_AND_TE.md`

---

## 0) Zasada nadrzędna (wymóg zadania)
Konwersja ma bazować na **dokładnym kodzie źródłowym** moda.

Dlatego przed poprawkami:
1. Zidentyfikuj w 1.18.2 (Blood Magic 3.2.6 dla 1.18.2) klasy odpowiedzialne za odczyt/zapis danych:
   - Master Ritual Stone BlockEntity (read/save NBT)
   - Blood Altar BlockEntity (read/save NBT)
   - Blood Rune blockstate properties (enum/codec)
   - Soul Network storage (capability / saved data) oraz Binding dla Blood Orb (ItemStack tag)
2. Wypisz **dokładne nazwy kluczy NBT** oraz typy danych (bool/int/string/compound) i na tej podstawie dopiero popraw konwertery i dokumentację.

Akceptacja: po tej weryfikacji wszystkie mapowania w kodzie mają wskazywać na konkretne pola z kodu źródłowego (np. w komentarzu “Source mapping”) i nie mogą być „domyślone”.

---

## 1) Krytyczna poprawka: Blood Rune – błędne mapowanie metadata 7
### Problem
W `block_mappings.py` dokumentacja mówi, że typy w 1.18.2 to m.in. `augmented_capacity`,
ale Enum mapuje `metadata=7` na `"orb"`.

To jest sprzeczne z `BLOOD_MAGIC_BLOCKS_AND_TE.md`, gdzie metadata 7 jest opisane jako **Augmented Capacity Rune**.

### Zadanie
1. Ustal z kodu źródłowego 1.18.2 **prawidłowe wartości property `type`** dla Blood Rune (np. `blank/speed/.../augmented_capacity`).
2. Popraw `BloodRuneType` tak, aby **metadata 0–7 mapowały 1:1** na prawdziwe wartości.
3. Popraw / rozszerz test `TestBlockMappings.test_blood_rune_types` tak, aby łapał ten błąd.

Akceptacja:
- `metadata=7` mapuje na właściwą wartość zgodną ze źródłem 1.18.2.
- Testy wymuszają poprawne mapowanie wszystkich wartości 0–7.

Pliki:
- `block_mappings.py`
- `test_converters.py`
- `BLOOD_MAGIC_BLOCKS_AND_TE.md` (sekcja run)

---

## 2) Krytyczna poprawka: Master Ritual Stone – klucze NBT i brakujące pola
### Problem
Dokumentacja (`BLOOD_MAGIC_BLOCKS_AND_TE.md`) opisuje klucze 1.18.2 jako np. `ritualType`, `isActive`, `runningTime`,
a konwerter zapisuje `ritualID`, `active`, `ownerUUID` i pomija `runningTime`.

To jest sprzeczność spec ↔ kod; dodatkowo grozi tym, że 1.18.2 **nie odczyta** rytuału/aktywacji.

### Zadanie
1. Zweryfikuj w kodzie źródłowym 1.18.2, **jakie klucze są czytane/zapisywane** przez BlockEntity Master Ritual Stone.
   - Czy to `ritualID` (ResourceLocation) czy `ritualType` (string)?
   - Czy flaga aktywacji to `active` czy `isActive`?
   - Czy istnieje `runningTime` / inny licznik czasu i jak się nazywa?
   - Czy `willDrain` jest realnym polem NBT czy wartością runtime/konfig?
2. Zaktualizuj `ritual_converter.py` tak, by zapisywał **dokładnie** te klucze i typy.
3. Zaktualizuj `BLOOD_MAGIC_BLOCKS_AND_TE.md`, by opisywał ten sam format co kod.
4. Zaktualizuj testy konwersji rytuału tak, by oczekiwały poprawnych kluczy.

Akceptacja:
- Brak sprzeczności pomiędzy `ritual_converter.py` a `BLOOD_MAGIC_BLOCKS_AND_TE.md`.
- Testy sprawdzają konkretne klucze, które odpowiadają realnemu NBT w 1.18.2.

Pliki:
- `ritual_converter.py`
- `test_converters.py`
- `BLOOD_MAGIC_BLOCKS_AND_TE.md`

---

## 3) BlockEntity NBT: zapewnij pozycję (x/y/z) lub jawny kontrakt
### Problem
`converter.py` ustawia `be_nbt_1182["id"]`, ale nigdzie nie widać, by zapewniał `x/y/z`.
W wielu zapisach BE pozycja jest wymagana (lub musi być w innym miejscu struktury chunk).

### Zadanie (wybierz 1 z 2 podejść i udokumentuj)
**Podejście A (zalecane, jeśli output to “NBT list of BE”):**
1. Dodaj do `BloodMagicConverter.convert_block(...)` parametr pozycji (lub użyj już istniejącego, jeśli jest w sygnaturze wyżej).
2. Dopisz `x`, `y`, `z` do `result.be_nbt_1182`, jeśli w input było TE.

**Podejście B (jeśli pipeline wyżej zawsze wstrzykuje pozycję):**
1. Dopisz w docstringach i README konwertera wyraźny kontrakt: “x/y/z są dodawane na warstwie zapisu chunków, nie w tym konwerterze”.
2. Dodaj test, który wymusza obecność pozycji na etapie, na którym jest to wymagane (albo test kontraktu).

Akceptacja:
- Jest jasne, gdzie powstają `x/y/z` i testy nie pozwalają tego przypadkiem zgubić.

Pliki:
- `converter.py`
- (opcjonalnie) `test_converters.py`
- dokumentacja w `.md`

---

## 4) Blood Altar: zweryfikuj nazwy kluczy 1.18.2 i typ `altarTier`
### Problem
`altar_converter.py` mapuje `upgradeLevel` → `altarTier` jako string `"ONE"..."SIX"` i używa kluczy typu `altarLiquidReq`.
To może być poprawne, ale wymaga potwierdzenia w źródle 1.18.2 (czy to string/enum/int i jakie są nazwy pól).

### Zadanie
1. Z kodu źródłowego 1.18.2 spisz listę kluczy NBT ołtarza.
2. Upewnij się, że konwerter zapisuje:
   - poprawny typ `altarTier` (string/int/ordinal) i poprawny zakres
   - poprawne nazwy kluczy (`altarActive`, `altarLiquidReq`, `altarFillable`, itd.)
3. Jeśli w 1.18.2 jakieś wartości są wyliczane runtime (np. multiplikatory z run), **nie zapisuj ich** do NBT lub zapisuj tylko, jeśli źródło tak robi.

Akceptacja:
- Klucze i typy w NBT po konwersji są zgodne ze źródłem 1.18.2.
- Testy odzwierciedlają realne klucze, nie “wewnętrzną umowę” projektu.

Pliki:
- `altar_converter.py`
- `test_converters.py`
- `BLOOD_MAGIC_BLOCKS_AND_TE.md`

---

## 5) Soul Network / Blood Orb: potwierdź docelowy storage i NBT itemu
### Problem
W 1.18.2 Soul Network jest zwykle capability/per-player, więc sama transformacja dictów może być niewystarczająca bez miejsca zapisu.
Dla Blood Orb: klucze `binding.ownerUUID/ownerName` muszą odpowiadać rzeczywistemu NBT itemu.

### Zadanie
1. Zweryfikuj w kodzie źródłowym 1.18.2:
   - gdzie i jak zapisuje się Soul Network (capability/serialized)
   - jak wygląda NBT Blood Orb (klucze w ItemStack tag)
2. Jeśli obecny format w `soul_network_converter.py` jest tylko „formatem pośrednim”, opisz to w dokumentacji i dodaj ostrzeżenie w kodzie (warnings) kiedy output nie jest bezpośrednio zapisywalny w świecie 1.18.2.
3. Popraw klucze NBT Blood Orb zgodnie ze źródłem.

Akceptacja:
- Format “docelowy” nie jest mylony z “pośrednim”.
- Klucze Blood Orb są zgodne z 1.18.2.

Pliki:
- `soul_network_converter.py`
- `test_converters.py`
- `BLOOD_MAGIC_BLOCKS_AND_TE.md`

---

## 6) Uporządkowanie: testy mają łapać rozjazdy spec ↔ kod
### Zadanie
1. Rozszerz testy tak, żeby:
   - wymuszały konkretne klucze NBT dla Master Ritual Stone i Blood Altar (zgodne ze źródłem 1.18.2)
   - sprawdzały pełne mapowanie run 0–7
2. Dodaj test “spójności dokumentacji” (opcjonalnie): prosty test, który porównuje listę kluczy z dokumentacji `.md` z tym, co emituje konwerter (żeby nie rozjeżdżało się w przyszłości).

Akceptacja:
- Po poprawkach nie da się “przypadkiem” wrócić do złych kluczy (testy failują).

Pliki:
- `test_converters.py`
- (opcjonalnie) dodatkowy test util

---

## 7) Checklist do zakończenia PR
- [ ] Poprawiono mapowanie Blood Rune `metadata=7` i testy.
- [ ] Master Ritual Stone: klucze NBT i typy są zgodne ze źródłem; dokumentacja i testy zaktualizowane.
- [ ] Ustalono gdzie powstają `x/y/z` dla BlockEntity; testy/kontrakt dopisane.
- [ ] Blood Altar: zweryfikowane klucze i `altarTier`.
- [ ] Soul Network/Blood Orb: zweryfikowane miejsce zapisu i klucze item NBT; dodane ostrzeżenia jeśli to format pośredni.
- [ ] Brak sprzeczności pomiędzy `BLOOD_MAGIC_BLOCKS_AND_TE.md` a implementacją.

