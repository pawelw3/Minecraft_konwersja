# Armourer's Workshop - Krok 4B: runner JVM serializera

## Cel

Krok 4B mial potwierdzic, ze globalne pliki `.armour` z 1.7.10 da sie
przepisywac oficjalnym serializerem Armourer's Workshop 1.18.2, zamiast
kopiowac legacy binaria albo odtwarzac format w Pythonie.

## Wynik

PoC runnera zostal wykonany w `C:\tmp\aw_runner_work`, czyli w klonie roboczym
repo AW 1.18.2. Oryginalne repo:

`mod_src/118/actual_src/1.18.2/ArmourersWorkshop/repo`

pozostalo bez zmian.

## Co dziala

- Kompilacja AW po przelaczeniu `versions/1.18.2` na zrodla 1.18.2.
- Klasa `SkinLibraryConvertCli` czyta legacy `.armour` przez
  `SkinSerializer.readFromStream(...)`.
- Zapis wymusza `SkinSerializer.Versions.LATEST`, co w tej wersji AW daje v25.
- Wynik ma naglowek `SKIN` i wersje `25`.
- Wrapper `scripts/aw_skin_convert_one.ps1` obsluguje sciezki ze spacjami.
- Migrator Pythona przechodzi caly lancuch na pojedynczym pliku:
  `scan -> runner -> walidacja SKIN/v25 -> manifest`.

## Najwazniejsze probki

Konwersja `7.4.armour`:

- source: `43487` bajtow
- target: `14222` bajtow
- header targetu: `53 4B 49 4E 00 00 00 19`

Konwersja pliku ze spacja w nazwie:

- source: `Biret kap_a_ski.armour`
- target: `2487` bajtow
- header targetu: `53 4B 49 4E 00 00 00 19`

Test integracyjny migratora na jednym pliku:

```json
{
  "entry_count": 1,
  "converted_count": 1,
  "skipped_count": 0,
  "error_count": 0,
  "dry_run": false
}
```

## Dlaczego potrzebne sa patche w workdir

Serializer AW 1.18.2 podczas read/write dotyka klas, ktore w normalnym modzie
sa spinane przez Architectury/Forge runtime (`@ExpectPlatform`) oraz rejestracje
blokow i tagow. Runner poza Minecraftem potrzebuje waskiej izolacji:

- bootstrap wersji Minecrafta przed rejestrami:
  `SharedConstants.setVersion(DetectedVersion.BUILT_IN)` i `Bootstrap.bootStrap()`;
- ominiecie platformowego debug-logu w `ModLog.debug`;
- usuniecie zaleznosci `ItemOverrideType` od `ModItemTags`;
- usuniecie zaleznosci `SkinGeometryTypes` od `ModBlocks`.

To nie jest konwersja danych "na skroty"; plik wynikowy nadal jest zapisywany
przez oficjalny `SkinSerializerV20` z AW 1.18.2.

## Pliki projektu

- `jvm/armourers_workshop_skin_runner/SkinLibraryConvertCli.java`
- `jvm/armourers_workshop_skin_runner/README.md`
- `scripts/aw_skin_convert_one.ps1`
- `scripts/aw_skin_convert_one.cmd`

## Komenda do dalszych prob

```powershell
python -m src.converters.armourers_workshop.skin_library_migrator `
  --source-root C:\tmp\aw_runner_onefile_src `
  --target-root C:\tmp\aw_runner_onefile_dst `
  --manifest C:\tmp\aw_runner_onefile_manifest.json `
  --runner .\scripts\aw_skin_convert_one.cmd "{source}" "{target}"
```

## Status

Krok 4B jest wykonany jako dzialajacy PoC i integracja jednoplikowa. Pelna
migracja 146 plikow do `mapa_118/skin-library` powinna byc osobnym krokiem,
bo obecny wrapper uruchamia Gradle per plik i bedzie wolny.
