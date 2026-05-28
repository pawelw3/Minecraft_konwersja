# Armourer's Workshop Skin Runner

Ten katalog przechowuje maly runner JVM do przepisywania plikow `.armour`
przez oficjalny serializer Armourer's Workshop 1.18.2.

## PoC wykonany w kroku 4B

Runner zostal sprawdzony w roboczej kopii:

- AW source: `mod_src/118/actual_src/1.18.2/ArmourersWorkshop/repo`
- workdir: `C:\tmp\aw_runner_work`
- wersja aktywowana przez `versions/1.18.2 switchCoreSource applyCoreSources applyCoreProperties`
- klasa CLI: `moe.plushie.armourers_workshop.tools.SkinLibraryConvertCli`

Oryginalne repo AW pozostalo czyste; zmiany byly robione w `C:\tmp\aw_runner_work`.

## Wymagane lokalne poprawki w workdir AW

Standalone runner nie moze uzyc calego common classpath bez srodowiska MC/Forge,
bo serializer dotyka `@ExpectPlatform` i rejestracji blokow/tagow. Do PoC
wystarczyly te izolujace poprawki w roboczej kopii:

- dodac `SkinLibraryConvertCli.java` do `forge/src/main/java/moe/plushie/armourers_workshop/tools/`;
- dodac task `runSkinLibraryConvertCli` do `forge/build.gradle` z argumentami
  `-PawSource` i `-PawTarget`;
- w `common/.../init/ModLog.java` uproscic `debug(...)` do `LOGGER.debug(...)`;
- w `common/.../core/data/slot/ItemOverrideType.java` ustawic tagi itemow na `null`;
- w `common/.../core/skin/geometry/SkinGeometryTypes.java` ustawic holdery blokow
  geometrii na `null`.

Te poprawki nie zmieniaja danych skinow; usuwaja tylko zaleznosci od runtime
rejestracji moda potrzebne przy uruchomieniu serializera poza serwerem.

## Uruchomienie pojedynczej konwersji

Wrapper projektu:

```powershell
.\scripts\aw_skin_convert_one.ps1 `
  "pliki_globalne_serwer_1710\armourersWorkshop\Biret kap_a_ski.armour" `
  "C:\tmp\aw_runner_work\converted_sample\Biret kap_a_ski.armour"
```

Migrator Pythona moze uzyc wrappera CMD:

```powershell
python -m src.converters.armourers_workshop.skin_library_migrator `
  --source-root C:\tmp\aw_runner_onefile_src `
  --target-root C:\tmp\aw_runner_onefile_dst `
  --manifest C:\tmp\aw_runner_onefile_manifest.json `
  --runner .\scripts\aw_skin_convert_one.cmd "{source}" "{target}"
```

Oczekiwany output nowego pliku zaczyna sie od:

```text
53 4B 49 4E 00 00 00 19
```

czyli `SKIN` + wersja `25`.
