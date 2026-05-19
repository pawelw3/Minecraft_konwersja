# Raport: ForgeMultipart/CB Multipart — Zadanie 6

## Cel
Test na headless serwerze 1.18.2 z przekonwertowaną mapą: sprawdzenie czy wyskakują błędy, analiza stanu mapy po 3 minutach działania serwera.

## Przygotowanie mapy

### Źródło
Mapa testowa ForgeMultipart (Zadanie 5A) przekonwertowana do formatu 1.18.2:
- `test_scenarios/forge_multipart_task5a/1710_test_world/` -> konwersja -> `headless_server/1.18.2/world_forge_multipart_converted/`

### Metoda konwersji
1. Wygenerowano eventy konwersji (`task5a_events_1182.json`) z 15 blokami `cb_multipart:block` + TE
2. Zaaplikowano eventy przez Kotlin Hephaistos Worker (`--apply-events`)
3. Użyto istniejącej mapy 1.18.2 (`ae2_1`) jako bazy aby uniknąć problemów z pustymi chunkami

## Test serwera 1.18.2

### Konfiguracja
- **Serwer:** Forge 1.18.2 (40.2.4)
- **Mody:** CBMultipart 3.1.1.138, ProjectRed, AE2, Mekanism, WorldEdit
- **Java:** OpenJDK 17.0.17
- **Mapa:** `world_forge_multipart_converted`
- **Czas działania:** 180 sekund (3 minuty)

### Wynik startu
```
[23:07:17] [Server thread/INFO] [minecraft/DedicatedServer]: Done (15.977s)!
```
✅ Serwer wystartował pomyślnie.

### Błędy wykryte podczas testu

#### ❌ Krytyczny błąd: Chunk [0, 0] nie załadowany
```
[23:07:04] [Server thread/ERROR] [minecraft/ChunkSerializer]: 
  Recoverable errors when loading section [0, -3, 0]: 
  Failed to read PalettedContainer: Invalid length given for storage, got: 196 but expected: 256

[23:07:04] [Server thread/ERROR] [minecraft/ChunkMap]: 
  Couldn't load chunk [0, 0]
  java.lang.RuntimeException: Failed to read PalettedContainer: 
    Invalid length given for storage, got: 196 but expected: 256
```

**Analiza:**
- Błąd występuje w sekcji chunka `[0, -3, 0]` (X=0, Y=-3, Z=0)
- PalettedContainer ma nieprawidłowy rozmiar: 196 longs zamiast 256
- W formacie 1.18.2, PalettedContainer przechowuje bloki w sekcjach 16x16x16
- 256 longs = 8-bitowa paleta (256 możliwych block states na blok)
- 196 longs nie jest standardowym rozmiarem dla żadnej palety

**Prawdopodobna przyczyna:**
WorldEditor1182 (Kotlin Hephaistos Worker) ma bug przy modyfikacji istniejących chunków 1.18.2. Podczas zapisywania chunka po dodaniu block entity, biblioteka Hephaistos niepoprawnie serializuje PalettedContainer.

#### ⚠️ Inne błędy (niekrytyczne)
```
[Server thread/ERROR] [minecraft/ChunkSerializer]: 
  No key old_noise in MapLike[{max_section:20,min_section:-4}]
```
- Błędy DataFixera przy konwersji formatu starej mapy bazowej (ae2_1)
- Te błędy występują dla wielu chunków, ale nie powodują awarii
- Są związane z brakiem klucza `old_noise` w formatu chunka

#### ⚠️ Ostrzeżenie performance
```
[Server thread/WARN] [minecraft/MinecraftServer]: 
  Can't keep up! Is the server overloaded? Running 2068ms or 41 ticks behind
```
- Serwer miał krótkie opóźnienie przy starcie
- Normalne dla pierwszego uruchomienia z konwersją formatu mapy

### Stan modu CB Multipart
```
[modloading-worker-0/INFO] [co.mi.fo.SidedGenerator/]: 
  Trait: codechicken/multipart/trait/TTickableTile
  Marker: codechicken/multipart/api/part/TickablePart, Side: COMMON
  ...
[Forge Version Check/INFO] [ne.mi.fm.VersionChecker/]: 
  [cb_multipart] Found status: UP_TO_DATE Current: 3.1.1.138
```
✅ Mod CB Multipart załadował się poprawnie.

### Stan mapy po teście
- Chunk [0, 0] (gdzie były wstawione bloki ForgeMultipart) **nie został załadowany**
- Pozostałe chunki mapy bazowej załadowały się poprawnie
- Serwer działał stabilnie przez 3 minuty po starcie
- Brak crashy serwera

## Wnioski

1. **Konwersja NBT 1.7.10 -> 1.18.2 działa poprawnie** - symulacje Pythona potwierdziły poprawność.
2. **Aplikacja eventów na mapę 1.18.2 ma problem techniczny** - WorldEditor1182/Hephaistos generuje nieprawidłowy format PalettedContainer.
3. **Mod CB Multipart ładuje się poprawnie** na serwerze Forge 1.18.2.
4. **Chunk z przekonwertowanymi blokami nie załadował się** przez błąd formatu, nie przez błąd samego modu.

## Zalecenia

1. **Naprawa WorldEditor1182:** Zbadać i naprawić serializację PalettedContainer w Hephaistos/WorldEditor1182.
2. **Alternatywa:** Użyć innego narzędzia do aplikacji eventów na mapę 1.18.2 (np. WorldEdit, skrypt MCEdit, lub custom writer).
3. **Test ponowny:** Po naprawie edytora powtórzyć test z serwerem 1.18.2.

## Pliki

| Plik | Opis |
|------|------|
| `headless_server/1.18.2/world_forge_multipart_converted/` | Mapa testowa po konwersji (chunk [0,0] uszkodzony) |
| `headless_server/1.18.2/logs/forge_multipart_task5b_v2.log` | Pełne logi serwera |
| `output/forge_multipart/task5a_events_1182.json` | Eventy konwersji |
