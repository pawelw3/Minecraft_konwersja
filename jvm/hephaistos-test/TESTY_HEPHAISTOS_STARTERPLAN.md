# Hephaistos-first: zestaw testów prowadzących + instrukcja od zera (Minecraft 1.7.10, edycja `.mca` OFFLINE)

Ta instrukcja ma Cię **nakierować na Hephaistos** i dać serię **bardzo prostych, pewnych testów**, żebyś nie rezygnował po pierwszym błędzie builda lub API.

> **UWAGA (ważne):** Nie budujesz rozwiązania na bazie `flow-nbt`. To jest biblioteka NBT i nie rozwiązuje bezpiecznego zapisu plików **regionów `.mca`**. W tym zadaniu chodzi o **bezpieczną edycję `.mca`** (kontener regionów + chunk payload), więc rozwiązanie ma bazować na **Hephaistos (Anvil region + NBT)** jako warstwie zapisu/odczytu `.mca`.

---

## Cel końcowy (Definition of Done)

1) Masz worker JVM, który:
   - otwiera świat 1.7.10 (Anvil `.mca`),
   - aplikuje patch: `set_block` + `set_tile_entity`,
   - zapisuje `.mca` **bez korupcji**,
   - wykonuje walidację “po zapisie mogę odczytać to samo”.

2) Masz test headless:
   - uruchamia serwer 1.7.10 na świecie po patchu,
   - rozpoznaje PASS/FAIL po logach (`[ROUNDTRIP]`, potem `[PROBE]`).

---

## Zasady (COMPLIANCE)

- ✅ Używaj Hephaistos (region `.mca` + NBT).
- ✅ Jeśli masz problem z buildem na JDK 17, najpierw:
  - napraw wrapper (`./gradlew` vs `.bat`),
  - zbierz `--stacktrace`,
  - spróbuj `--add-opens` w `gradle.properties`,
  - dopiero potem rozważ composite build / JitPack.
- ❌ Nie przechodź na `flow-nbt` jako “zastępstwo Hephaistos”.
- ❌ Nie pisz własnego writer’a `.mca` od zera (offsety sektorów/kompresja).
- ❌ Nie kończ zadania na “wybierz opcję”. Masz doprowadzić do działających testów.

---

# Część A — Start od zera: repo + worker JVM

## A1) Utwórz minimalny projekt `jvm/worker/`
Struktura:
```
jvm/worker/
  settings.gradle.kts
  build.gradle.kts
  gradle.properties
  src/main/kotlin/Main.kt
```

### Minimalny build bez Shadow
Na początku **bez** fat-jar. Celem jest, żeby `./gradlew build` przechodziło.
Dopiero po sukcesie możesz dodać shading.

## A2) Uruchamianie Gradle zależnie od OS
- Linux/macOS: `./gradlew clean build --stacktrace`
- Windows: `gradlew.bat clean build --stacktrace`

Jeśli używasz złego wrappera, dostaniesz fałszywe błędy → popraw to zanim zrobisz cokolwiek.

---

# Część B — Testy prowadzące (od najłatwiejszych)

Poniższe testy są celowo ułożone tak, aby pierwsze 2–3 były **niemal nie do zepsucia**. Masz przechodzić je po kolei.

Każdy test ma:
- **Cel**
- **Kroki**
- **PASS/FAIL**
- **Najczęstsze potknięcia**

---

## Test 0: “Hello Jar” — środowisko i CLI działają
**Cel:** Upewnić się, że worker JVM w ogóle startuje i czyta parametry.

**Kroki:**
1) Zbuduj worker: `./gradlew build`
2) Uruchom: `java -jar build/libs/worker.jar --help`

**PASS:** wypisuje help i exit code 0.  
**FAIL:** napraw build / uruchomienie zanim ruszysz dalej.

**Potknięcia:**
- zły wrapper (`.bat` w Linuxie),
- brak `mainClass`,
- zła konfiguracja Gradle.

---

## Test 1: “Open world + list regions” — zero zapisu
**Cel:** Potwierdzić, że potrafisz znaleźć regiony `.mca` i je otworzyć.

**Kroki:**
1) Przygotuj czysty świat 1.7.10 (superflat).
2) Worker dostaje `--world <path>`.
3) Worker:
   - znajduje `region/r.*.*.mca`,
   - otwiera 1 plik regionu przez Hephaistos,
   - próbuje odczytać 1 chunk (np. (0,0) jeśli istnieje),
   - nic nie zapisuje.

**PASS:** brak wyjątków, exit 0.  
**FAIL:** to jest błąd I/O lub błędnej integracji Hephaistos.

**Potknięcia:**
- zła ścieżka świata (`region/` nie istnieje),
- brak uprawnień do plików.

---

## Test 2: “Read → Write unchanged → Read again” (najważniejszy smoke)
**Cel:** Udowodnić, że możesz bezpiecznie zapisać `.mca` nawet bez zmian.

**Kroki:**
1) Otwórz region `r.0.0.mca`.
2) Odczytaj chunk payload NBT dla jednego chunku.
3) Zapisz go z powrotem **bez modyfikacji**.
4) Ponownie odczytaj ten sam chunk.

**PASS:** read/write/read działa bez wyjątków.  
**FAIL:** to oznacza, że write-path jest zły i nie wolno iść dalej.

**Potknięcia:**
- nadpisywanie regionu nieatomowe (zrób zapis do temp i rename),
- nieprawidłowe zamykanie strumieni.

> Ten test jest bardzo prosty i powinien zadziałać, jeśli Hephaistos jest poprawnie użyty jako region writer.

---

## Test 3: “Set 1 block” — modyfikacja legacy sections 1.7.10
**Cel:** Ustawić 1 blok w chunku w formacie 1.7.10 (Blocks/Data/AddBlocks).

**Kroki:**
1) Wybierz pozycję: (0, 64, 0) w chunku (0,0).
2) W NBT chunku:
   - znajdź/utwórz `Level/Sections`,
   - znajdź/utwórz section `Y = 4` (bo 64>>4=4),
   - ustaw w tablicach `Blocks/Data/AddBlocks` wartość dla `(lx=0,lz=0,ly=0)`:
     - stone: `id=1, meta=0`.

**PASS:** po zapisie ponowny odczyt pokazuje stone w tej pozycji.  
**FAIL:** najczęściej błąd indeksowania albo brak/źle rozmiary tablic.

**Potknięcia:**
- złe indeksowanie `idx`,
- zły rozmiar `Blocks` (musi 4096),
- zły rozmiar `Data` (musi 2048, nibble),
- brak `Level` wrappera (nie duplikuj `Level`).

---

## Test 4: “Set command block + TE” (bez uruchamiania serwera)
**Cel:** Dopisać TE i zobaczyć, że round-trip zachowuje pola.

**Kroki:**
1) Ustaw blok ID 137 na (0,64,1).
2) W `Level/TileEntities` dodaj/replace TE:
   - `id = "Control"` (1.7.10)
   - `x=0,y=64,z=1`
   - `Command="/say [ROUNDTRIP] ok"`

3) Zapisz i odczytaj ponownie chunk:
   - sprawdź, że TE istnieje i ma `Command`.

**PASS:** TE widoczny po read-back.  
**FAIL:** najczęściej:
- TE nie jest w `TileEntities`,
- zły typ tagów (np. liczby jako string),
- duplikaty TE na tej samej pozycji.

---

## Test 5: “Boot server smoke” (pierwszy test headless)
**Cel:** Udowodnić, że świat po patchu jest akceptowany przez serwer 1.7.10 i że command block mówi do logów.

**Kroki:**
1) Na świecie po Test 4 uruchom serwer headless na 20–60 sekund.
2) Parsuj `logs/latest.log` lub stdout.
3) Szukaj `[ROUNDTRIP] ok`.

**PASS:** log zawiera `[ROUNDTRIP] ok`, brak `Couldn't load chunk`.  
**FAIL:** natychmiast wracasz do Test 2–4 i walidujesz region/chunk.

**Potknięcia:**
- command block TE ma zły `id` (musi `Control` dla 1.7.10),
- command block nie dostaje sygnału (na tym etapie możesz użyć redstone_block obok),
- edycja dotknęła złego chunku (błędy współrzędnych).

---

## Test 6: “Multi-chunk patch” (mały batch, nadal łatwe)
**Cel:** Udowodnić, że batch działa i nie psuje regionów.

**Kroki:**
1) Ustaw 4 bloki stone w czterech chunkach wokół spawna:
   - (0,64,0), (16,64,0), (0,64,16), (16,64,16)
2) Zapisz.
3) Read-back potwierdza wszystkie 4.

**PASS:** wszystkie 4 ustawione, serwer nie crashuje.  
**FAIL:** błąd mapowania chunk/region lub brak tworzenia chunków/sectionów.

---

## Test 7: “Mini-spiral R=1” (wariant B, minimalny)
**Cel:** Pierwsza wersja spirali, w kilku chunkach, by zobaczyć `[PROBE]` bez ryzyka.

**Kroki:**
1) Zbuduj spiralę tylko w promieniu R=1 (np. 8–12 chunków).
2) Start sygnału: redstone_block przy pierwszym segmencie.
3) W każdym chunku:
   - 1 impulse command block + TE `Control` z:
     - `/say [PROBE] REACHED cx=<cx> cz=<cz> step=<n>`
4) Uruchom serwer 30–60 sekund i parsuj logi.

**PASS:** `step=0` pojawia się szybko, potem rośnie (0,1,2...).  
**FAIL:** jeśli brak logów:
- kabel ma przerwę / brak repeatera na 16 bloków,
- command block nie ma sygnału,
- chunk nie ładuje się (poza spawn chunkami → przenieś spiralę bliżej spawna).

---

## Test 8: “Spirala R=3” (smoke docelowy)
**Cel:** Stabilny test integracyjny wariant B.

**Kroki:**
1) Spiralę rozszerz do R=3.
2) Ten sam mechanizm logowania.
3) PASS jeśli logi są spójne i nie ma crashy.

---

# Część C — Zasady, które zapobiegają “rezygnacji”

## C1) Nie przeskakuj do trudnych rzeczy
Jeśli Test 2 (read/write unchanged) nie przechodzi, to:
- nie ma sensu robić TE, spirali ani niczego wyżej.

## C2) “Hephaistos nie jest w Maven Central” ≠ “nie da się”
Jeśli dependency jest problemem:
1) spróbuj JitPack (tag/commit),
2) composite build (submodule + includeBuild),
3) dopiero na końcu vendor jar.

## C3) Build na JDK 17
Jeśli masz `InaccessibleObjectException`:
- zbierz `--stacktrace`,
- dodaj `--add-opens` do `gradle.properties`,
- uaktualnij pluginy Gradle/Kotlin,
- i dopiero wtedy wyciągaj wnioski o “wymaganym JDK”.

---

# Część D — Minimalne kryteria akceptacji

Aby uznać, że idziesz w dobrym kierunku, musisz dostarczyć log/artefakty:

1) `Test 2` PASS (read/write unchanged).
2) `Test 4` PASS (TE round-trip).
3) `Test 5` PASS (serwer loguje `[ROUNDTRIP] ok`).
4) `Test 7` PASS (mini-spiral loguje `[PROBE]`).

Dopiero potem skalujesz do większych R.

---
