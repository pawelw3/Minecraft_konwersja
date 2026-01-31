# Instrukcja dla agenta: NIE KOŃCZ zadania — doprowadź worker JVM do builda i uruchom testy (bez proszenia użytkownika o wybór)

Twoje “zakończenie zadania” jest przedwczesne. Masz dostarczyć działający pipeline (offline edit + headless test logów), a nie listę opcji do wyboru przez użytkownika.

Poniżej masz dokładną instrukcję, co robisz teraz, krok po kroku.

---

## 0) Zasady (COMPLIANCE)

1) **Nie pytasz użytkownika “którą opcję wybierasz”** dopóki nie wykonasz wszystkich kroków diagnostycznych i nie spróbujesz obejść blokad.
2) **Nie wracasz do `nbtlib`/własnego writer’a `.mca`** (to jest zakazane na tym etapie).
3) **Nie commitujesz gotowych `.jar`** jako “normalnego rozwiązania”. Vendorowanie to ostateczny fallback.
4) Jeśli masz problem ze środowiskiem (JDK/Gradle), to **naprawiasz go** lub przygotowujesz automat, który działa w aktualnych warunkach (JDK 17), zamiast “wymagać JDK 11”.

---

## 1) Najpierw popraw podstawy: OS i wrapper Gradle

### 1.1 Ustal, na jakim systemie działa środowisko build
- Jeśli to Linux/macOS: używasz **`./gradlew`**, nie `gradlew.bat`.
- Jeśli Windows: używasz `gradlew.bat`.

**Zrób to teraz**:
- wypisz wynik `uname -a` (Linux) lub odpowiednik,
- sprawdź, czy `gradlew` ma executable bit: `chmod +x ./gradlew`.

Jeżeli nadal odpalasz `./gradlew.bat` w Linuxie → napraw to natychmiast (to generuje fałszywe problemy).

---

## 2) Nie buduj `hephaistos-src` jako osobnego projektu — buduj własnego workera z zależnością

Twoim celem jest zbudować **`jvm/worker`**. Nie potrzebujesz osobnego “hephaistos-src” jeśli da się pobrać dependency.

### 2.1 Najpierw usuń “Shadow plugin requires Gradle 8+” z drogi
Na tym etapie **nie potrzebujesz** fat-jar (shadow). Najpierw ma się zbudować zwykły jar.

- usuń/wyłącz Shadow plugin,
- zbuduj zwykły jar:
  - `./gradlew clean build` (Linux/macOS)
  - lub `gradlew.bat clean build` (Windows)

Dopiero gdy zwykły jar się buduje, wrócisz do “fat jar”.

---

## 3) Prawidłowa diagnoza: błąd `InaccessibleObjectException` na JDK 17

Twoje zdanie “Hephaistos wymaga JDK 11” jest nieudowodnione.  
Masz zrobić triage, a nie wniosek na skróty.

### 3.1 Zbierz pełny log błędu
Uruchom:
- `./gradlew build --stacktrace --info` (Linux/macOS)
lub
- `gradlew.bat build --stacktrace --info` (Windows)

Zapisz do pliku:
- `artifacts/gradle_build_error.log`

### 3.2 Naprawa typowa dla `InaccessibleObjectException`
Jeśli wyjątek dotyczy refleksji do modułów JDK (np. `java.util`), dodaj do `gradle.properties`:
- `org.gradle.jvmargs=--add-opens=java.base/java.util=ALL-UNNAMED --add-opens=java.base/java.lang=ALL-UNNAMED`

Jeśli błąd jest w Kotlin plugin / Gradle plugin:
- zaktualizuj wersję pluginu Kotlin do zgodnej z Twoim Gradle,
- albo obniż Gradle do wersji, z którą plugin współpracuje.

**Cel**: build workera ma działać na JDK 17 w tym środowisku.

### 3.3 Toolchain ≠ “musisz mieć JDK 11 zainstalowane”
Jeśli projekt wymaga targetowania 11, użyj Gradle toolchain:
- `java { toolchain { languageVersion = JavaLanguageVersion.of(17) } }`
i ustaw `targetCompatibility` / `jvmTarget` na 11, jeśli to potrzebne.

Nie kończ pracy na “braku JDK 11”. Najpierw wyczerp diagnozę.

---

## 4) Dependency Hephaistos: jeśli nie Maven Central, użyj JitPack lub composite build

### 4.1 JitPack (pierwszy wybór)
Jeśli Hephaistos nie jest w Maven Central:
- dodaj repo:
  - `maven { url = uri("https://jitpack.io") }`
- dodaj dependency po tagu/commit:
  - `implementation("com.github.<OWNER>:Hephaistos:<TAG_OR_COMMIT>")`

**Uwaga**: JitPack często wymaga poprawnego `groupId` i nazwy repo. Sprawdź dokładnie owner/repo.

Jeśli widzisz “No build artifacts found”, to:
- sprawdź, czy repo ma `gradle`/`maven` build rozpoznawalny przez JitPack,
- sprawdź, czy wybrałeś poprawny tag/commit,
- sprawdź log JitPack build (JitPack pokazuje szczegóły).

Nie kończ na jednym błędzie — spróbuj 2–3 wersji (tag/commit).

### 4.2 Composite build (drugi wybór)
Jeśli JitPack nie działa:
- dodaj Hephaistos jako git submodule do `jvm/third_party/hephaistos/`
- użyj Gradle composite build:
  - `includeBuild("../third_party/hephaistos")`
i zależność jako project dependency.

To nadal nie jest “vendor jar”; to jest normalny build ze źródeł w ramach repo.

---

## 5) Dopiero po udanym buildzie: minimalny worker, minimalny patch

Gdy `jvm/worker` się buduje, implementujesz minimalną funkcjonalność:

### 5.1 Interfejs CLI
Worker przyjmuje:
- `--world <path>`
- `--patch <patch.json>`

### 5.2 Minimalny patch do weryfikacji
Patch ma wstawić:
- stone w (0,64,0)
- command block (ID=137) w (0,64,1)
- TE command blocka:
  - `id="Control"`
  - `x,y,z`
  - `Command="/say [ROUNDTRIP] ok"`

### 5.3 Walidacja “po zapisie”
Worker po zapisaniu:
- ponownie otwiera zmienione regiony
- czyta chunk i sprawdza, że:
  - blok jest ustawiony
  - TE istnieje i ma `Command`

Jeśli to FAIL → worker zwraca exit != 0 i wypisuje DIAG.

---

## 6) Dopiero potem: test spirali wariant B

Gdy round-trip działa:
- generujesz spiralę R=1, potem R=3,
- uruchamiasz serwer headless,
- parsujesz logi `[PROBE] REACHED ...`.

---

## 7) Jedyny dopuszczalny fallback jeśli Hephaistos nadal blokuje

Jeśli po krokach 1–4 **nie da się** zdobyć/budować Hephaistosa w tym środowisku (masz logi i dowody):
- nie wracasz do “własnego .mca writer na nbtlib”,
- tylko wybierasz inną bibliotekę, która umie **region container**:
  - np. inny JVM anvil/region library,
  - albo pythonowy tool, który jest znany z pracy z legacy.

W każdym przypadku kryterium jest to samo: round-trip + boot serwera.

---

## 8) Co masz dostarczyć jako wynik tej iteracji

1) Działający build `jvm/worker` w tym środowisku (JDK 17) — bez proszenia o instalację JDK 11.
2) Worker, który aplikuje minimalny patch (stone + command block TE `Control`) i waliduje zapis.
3) Round-trip test + log z serwera zawierający `[ROUNDTRIP] ok`.
4) Dopiero wtedy implementacja spirali.

---

## 9) Checklist “nie kończ przed czasem”

- [ ] Nie używam `gradlew.bat` w Linuxie
- [ ] Mam `--stacktrace` logi błędu Gradle w artefaktach
- [ ] Build workera działa na JDK 17
- [ ] Hephaistos dependency rozwiązane (JitPack lub composite build)
- [ ] Minimalny patch działa (offline) i serwer loguje `[ROUNDTRIP] ok`
- [ ] Dopiero potem spirala

---
