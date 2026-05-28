# Client Pack 1.18.2

Folder zawiera zestaw JAR-ow dla klienta Forge 1.18.2-40.2.0 do wejscia na swiat po konwersji 1.7.10 -> 1.18.2.

## Zawartosc

- `mods/` - komplet skopiowanych/pobranych JAR-ow.
- `MODLIST.txt` - szybka lista plikow i rozmiarow.
- `mod_manifest.json` - manifest z rozmiarem i SHA-256 kazdego JAR-a.

## Status workera konwersji

Aktualny JVM worker to `jvm/worker/build/libs/mc-editkit-worker-1.0-SNAPSHOT.jar`.

- Obsluguje edycje 1.7.10 przez `--world <path> --patch <patch.json>`.
- Obsluguje zapis 1.18.2 przez `--apply-events <events.json|jsonl> --target-world <world>`.
- Dla 1.18.2 wspiera obecnie `set_block`, `set_block_entity` i `remove_block`.
- JSONL jest uzywany dla duzych strumieni eventow, np. Traincraft.
- Czesc testow etapowych nadal materializuje wynik przez datapacki 1.18.2, zanim pelny pipeline trafi bezposrednio do `.mca`.

## Uwagi

- Zestaw nie zawiera starego `Mekanism-1.18.2-10.2.0.459.jar`, bo w paczce jest nowszy `10.2.5.465`.
- Lokalny plik `mod_src/118/mod_jars/bloodmagic-1.18.2-3.2.6-41.jar` byl niepoprawny (`modId=factorium`, Minecraft 1.19), wiec w paczce jest pobrany poprawny `BloodMagic-1.18.2-3.2.6-41.jar`.
- `armourersworkshop-forge-1.18.2-2.0.11.jar` jest wersja sprawdzona w headless Task 5B z fallbackami = 0.
- `cuttableblocks-1.0.0.jar` pochodzi z `jvm/cuttableblocks_mod_1182/build/libs/` i sluzy jako wlasny zamiennik Carpenter's Blocks.
- Nie uruchamiano pelnego klienta graficznego z tym folderem w tej sesji.

## Weryfikacja wykonana

- 66 JAR-ow w `mods/`.
- Wszystkie JAR-y otwieraja sie jako archiwa.
- Parser `mods.toml` nie wykryl brakujacych obowiazkowych zaleznosci.
