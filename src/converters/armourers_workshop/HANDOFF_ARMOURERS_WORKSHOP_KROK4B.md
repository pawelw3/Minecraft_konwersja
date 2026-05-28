# Handoff: Armourer's Workshop, Krok 4B

## Podsumowanie sesji

Zbudowano i sprawdzono runner JVM, ktory uzywa serializera Armourer's Workshop
1.18.2 do przepisywania legacy `.armour` na format v25. Runner dziala w roboczej
kopii AW `C:\tmp\aw_runner_work`, a oryginalne repo moda pozostalo czyste.

## Ukonczono

- [x] Przelaczono robocza kopie AW na zrodla `1.18.2`.
- [x] Dodano PoC `SkinLibraryConvertCli`.
- [x] Skompilowano runner przez Gradle AW.
- [x] Rozwiazano bootstrap rejestrow Minecrafta dla uruchomienia poza gra.
- [x] Odizolowano serializer od runtime rejestracji blokow/tagow w workdir.
- [x] Przekonwertowano realny plik `7.4.armour` do v25.
- [x] Przekonwertowano realny plik ze spacja w nazwie.
- [x] Dodano wrappery `ps1` i `cmd`.
- [x] Sprawdzono integracje migratora Pythona na jednym pliku.

## Nowe pliki

- `jvm/armourers_workshop_skin_runner/SkinLibraryConvertCli.java`
- `jvm/armourers_workshop_skin_runner/README.md`
- `scripts/aw_skin_convert_one.ps1`
- `scripts/aw_skin_convert_one.cmd`
- `src/converters/armourers_workshop/ARMOURERS_WORKSHOP_KROK4B_JVM_RUNNER.md`
- `src/converters/armourers_workshop/HANDOFF_ARMOURERS_WORKSHOP_KROK4B.md`

## Zmodyfikowane pliki

- `HANDOFF.md`

## Weryfikacja

- `C:\tmp\aw_runner_work\gradlew.bat -p C:\tmp\aw_runner_work :common:compileJava --no-daemon --console=plain --stacktrace` -> OK.
- `C:\tmp\aw_runner_work\gradlew.bat -p C:\tmp\aw_runner_work :forge:runSkinLibraryConvertCli ...` -> OK dla `7.4.armour`.
- `.\scripts\aw_skin_convert_one.ps1 ... "Biret kap_a_ski.armour" ...` -> OK.
- `python -m src.converters.armourers_workshop.skin_library_migrator ... --runner .\scripts\aw_skin_convert_one.cmd "{source}" "{target}"` -> `converted_count=1`, `error_count=0`.

## Nastepne kroki

1. [ ] Zrobic batch runner albo stale JavaExec, ktory konwertuje wiele plikow w jednym uruchomieniu JVM/Gradle.
2. [ ] Uruchomic pelna migracje 146 plikow do kopii `mapa_118/skin-library`.
3. [ ] Wykorzystac manifest `ws:<path>.armour` przy uzupelnianiu TE `skinnable`.
