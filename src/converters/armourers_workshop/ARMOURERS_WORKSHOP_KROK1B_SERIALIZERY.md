# Armourer's Workshop - Krok 1B: porownanie serializerow modeli

## Cel

Ten dodatkowy krok sprawdza, czy modele `.armour` z Armourer's Workshop 1.7.10 mozna bezpiecznie przeniesc do 1.18.2 przez wbudowany serializer nowszego moda, czy trzeba pisac pelny binarny writer w Pythonie.

## Zrodla sprawdzone

- 1.7.10 source: `mod_src/1710/actual_src/1.7.10/ArmourersWorkshop/repo`
- 1.18.2 source: `mod_src/118/actual_src/1.18.2/ArmourersWorkshop/repo`
- 1.7.10 modele serwera: `pliki_globalne_serwer_1710/armourersWorkshop`
- 1.18.2 JAR: `mod_src/118/mod_jars/armourersworkshop-forge-1.18.2-3.2.7-beta.jar`

## Wynik krotki

Serializer Armourer's Workshop 1.18.2 ma wbudowane trzy sciezki:

- `v12` dla plikow starszych niz v13.
- `v13` dla plikow takich jak obecne pliki 1.7.10.
- `v20` dla nowego formatu 1.18.2, z zakresem wersji 20..25.

Pliki z obecnej biblioteki 1.7.10 maja `file_version = 13`, a 1.18.2 ma `SkinSerializerV13`, ktory obsluguje dokladnie `fileVersion == 13`. To oznacza, ze modele nie powinny byc konwertowane przez zgadywanie bajtow od zera. Najbezpieczniejsza sciezka to load przez serializer 1.18.2 i zapis przez jego aktualny writer.

## Najwazniejsze roznice formatu

### 1.7.10 / format v13

Kod 1.7.10 definiuje `Skin.FILE_VERSION = 13`.

Stary format zapisuje kolejno:

- `int` z wersja pliku.
- Tekstowe markery: `AW-SKIN-START`, `PROPS-START`, `TYPE-START`, `PAINT-START`, `PART-START`, `AW-SKIN-END`.
- Properties skorki.
- Typ skorki jako registry string, np. `armourers:head`.
- Dane paint texture starego rozmiaru.
- Liste partow.
- Dla partow: registry string parta, dane geometrii/kostek, marker blocks.

Te same markery i strukture potwierdza nowy `SkinSerializerV13` w source 1.18.2.

### 1.18.2 / format v13

`SkinSerializerV13` w 1.18.2 jest kompatybilnym readerem/writerem starego formatu v13. Dodatkowo mapuje kilka dawnych nazw partow:

- `armourers:skirt.base` -> `armourers:legs.skirt`
- `armourers:bow.base` -> `armourers:bow.frame1`
- `armourers:arrow.base` -> `armourers:bow.arrow`

To jest wazne dla modeli z 1.7.10, bo pozwala zachowac geometrie mimo zmian w nazwach partow.

### 1.18.2 / nowy format v20..v25

Najnowszy serializer w 1.18.2 to `SkinSerializerV20`:

- Minimalna wersja: `20`.
- Najnowsza wersja: `25`.
- Wymaga naglowka `0x534b494e`, czyli `SKIN`.
- Zapisuje dane w nowym chunkowym formacie.
- `SkinSerializer.writeToStream(...)` rejestruje serializery w kolejnosci: v20, v13, v12.

Przy zapisie `SkinSerializer` bierze `fileVersion` z obiektu `Skin` i/lub `SkinFileOptions`. Dlatego docelowy konwerter powinien jawnie wymuszac najnowszy format przez `SkinFileOptions.setFileVersion(SkinSerializer.Versions.LATEST)`, zeby nie zapisac przypadkiem ponownie v13.

## Foldery bibliotek

W 1.7.10 biblioteka modeli jest globalna dla instancji serwera:

- `SkinIOUtils.getSkinLibraryDirectory()` -> `System.getProperty("user.dir") / LibModInfo.ID`
- Dla tej paczki odpowiada to `pliki_globalne_serwer_1710/armourersWorkshop`.

W 1.18.2 biblioteka jest w folderze:

- `EnvironmentManager.getSkinLibraryDirectory()` -> `getRootDirectory() / skin-library`

To znaczy, ze sama mapa nie wystarczy. Migracja AW musi kopiowac albo przepisywac globalna biblioteke z:

- source: `pliki_globalne_serwer_1710/armourersWorkshop`
- target: folder root serwera 1.18.2 + `skin-library`

## Decyzja dla dalszej implementacji

Nie pisac wlasnego pelnego writera `.armour` v25 w Pythonie w nastepnym kroku. Lepiej przygotowac maly helper po stronie 1.18.2/Javy, ktory:

1. Czyta `.armour` v13 przez `SkinSerializer.readFromStream(...)`.
2. Waliduje typ skorki i liczbe partow/kostek.
3. Zapisuje plik do `skin-library` przez `SkinSerializer.writeToStream(...)` z `SkinFileOptions` ustawionym na `Versions.LATEST`.
4. Zachowuje relatywne sciezki i nazwy plikow z `pliki_globalne_serwer_1710/armourersWorkshop`.

Pythonowy skrypt z Zadania 1 zostaje przydatny jako manifest, walidator i raport roznic, ale nie powinien byc glownym autorem nowego binarnego formatu.

## Ryzyka do sprawdzenia w kolejnym kroku

- Czy wszystkie typy z obecnej biblioteki 1.7.10 istnieja w registry 1.18.2.
- Czy `Skin.fileVersion()` po wczytaniu v13 nie wymusi ponownego zapisu v13, jesli nie podamy opcji `LATEST`.
- Czy 1.18.2 akceptuje stare nazwy typow `armourers:*` bez dodatkowego namespace migration.
- Czy prywatne foldery biblioteki trzeba odtworzyc pod `skin-library/private/<uuid>/`.

## Wniosek

Modele z 1.7.10 powinny dac sie poprawnie wczytac w source 1.18.2, bo mod ma natywny `SkinSerializerV13`. Poprawna konwersja do modelu 1.18.2 powinna jednak wykonac read v13 -> write latest v25, zamiast tylko kopiowac stare pliki do nowego folderu.
