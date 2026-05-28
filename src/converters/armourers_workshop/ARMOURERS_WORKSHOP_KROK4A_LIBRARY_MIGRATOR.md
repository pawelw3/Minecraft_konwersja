# Armourer's Workshop - Krok 4A: migrator biblioteki `.armour`

## Podsumowanie

Dodano wykonawczy kontrakt migracji globalnej biblioteki skinow Armourer's Workshop. Modul skanuje katalog 1.7.10, zachowuje relatywne sciezki, przygotowuje target `skin-library` i waliduje, ze wynikowy plik zostal zapisany jako nowoczesny format v25 z naglowkiem `SKIN`.

## Pliki

- `src/converters/armourers_workshop/skin_library_migrator.py`
- `src/converters/armourers_workshop/tests/test_skin_library_migrator.py`
- `output/armourers_workshop_step4/skin_library_migration_manifest.json`

## Kontrakt runnera

Python nie reimplementuje binarnego formatu `.armour`. Runner musi uzyc source/JAR 1.18.2:

1. `SkinSerializer.readFromStream(...)` dla pliku v12/v13/v20.
2. `SkinFileOptions.FileVersion = SkinSerializer.Versions.LATEST`.
3. `SkinSerializer.writeToStream(...)`, co dla v20+ zapisuje naglowek `SKIN` i wersje v25.

Migrator przyjmie wynik tylko wtedy, gdy pierwsze 8 bajtow pliku to:

- int `0x534B494E`, czyli `SKIN`,
- int `25`.

## Dry-run na realnym katalogu

Komenda:

```powershell
python -m src.converters.armourers_workshop.skin_library_migrator --source-root pliki_globalne_serwer_1710\armourersWorkshop --target-root mapa_118\skin-library --manifest output\armourers_workshop_step4\skin_library_migration_manifest.json --dry-run
```

Wynik:

- `entry_count`: `146`
- `converted_count`: `0`
- `skipped_count`: `146`
- `error_count`: `0`
- `dry_run`: `true`

## Weryfikacja

- `python -m pytest src\converters\armourers_workshop\tests -q` -> `22 passed`.
- `python -m py_compile src\converters\armourers_workshop\skin_library_migrator.py src\converters\armourers_workshop\tests\test_skin_library_migrator.py` -> OK.

