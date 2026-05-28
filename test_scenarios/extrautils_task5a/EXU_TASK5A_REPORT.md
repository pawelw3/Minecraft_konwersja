# Extra Utilities Task 5A – raport

Zakres: **Extra Utilities** 1.7.10 → 1.18.2.

## Status

**Zadanie 5A dla Extra Utilities: wykonane.**

Zgodnie z `docs/PLAN.md` wykonano:

- testową mapę 1.7.10 z blokami i BE Extra Utilities,
- kombinacje BE z różnymi metadanymi, tierami generatorów (x1, x8, x64), energią, fluidem, inventory (filing cabinet),
- zapis do `.mca` przez Kotlin/Hephaistos zgodnie z `skills/mca-sections`,
- konwersję kodem konwertera na patch 1.18.2,
- test redstone do późniejszego odpalenia na headless serwerze zgodnie z `skills/integration_test_with_redstone`.

## Liczby

- Sample w scenariuszu: 27.
- Unikalne warianty source `block:metadata`: 20.
- Sample z NBT/BE: 20.
- Edycje patcha source 1.7.10: 47.
- Edycje patcha target 1.18.2: 46.
- Zweryfikowane bloki w realnym `.mca`: 27.
- Zweryfikowane Tile Entities w realnym `.mca`: 20.
- Zweryfikowane zagnieżdżone klucze TE: 65.
- Błędy zapisu/odczytu/konwersji: 0.
- Kolizje harnessa redstone z blokami ExU: 0.

## Poprawki wykryte i zamknięte

Podczas Task 5A wykryto niespójność nazw bloków między dynamicznym rejestrem `mapa_1710/level.dat` a mapowaniami w projekcie:

- `ExtraUtilities:cursedearthside` → brakowało mapowania (dodano alias)
- `ExtraUtilities:trashcan` (małe litery) → brakowało mapowania (dodano alias)
- `ExtraUtilities:sound_muffler` (z underscore) → brakowało mapowania (dodano alias)
- `ExtraUtilities:generator.64` (ID 3205) → było w rejestrze ale nie wszystkie mapowania były testowane

Dodano obsługę normalizacji nazw w `src/converters/extrautils/mappings/block_mappings.py`:
- `is_extrautils_block()` akceptuje teraz `extrautilities:` (format z mapy)
- `get_mapping()` normalizuje `extrautilities:` → `extrautils:` przed lookup
- dodano aliasy dla alternatywnych nazw rejestrowych

Dodatkowe poprawki z Task 5B:
- `thermal:dynamo_alchemical` → `thermal:dynamo_compression` (blok nie istnieje w 1.18.2)
- `torchmaster:mega_torch` → `torchmaster:megatorch` (poprawna nazwa bloku w 1.18.2)

## Artefakty

- `generate_extrautils_task5a.py` – generator scenariusza 5A.
- `convert_extrautils_task5a.py` – konwersja z realnie zapisanej mapy.
- `verify_extrautils_task5a_world.py` – weryfikacja realnego `.mca`.
- `extrautils_task5a_source_patch_1710.json` – source patch 1.7.10.
- `extrautils_task5a_converted_patch_1182.json` – oczekiwany patch 1.18.2 z konwertera.
- `extrautils_task5a_conversion_report.json` – raport konwersji wszystkich próbek.
- `extrautils_task5a_world_verify_report.json` – read-back realnego `.mca`.
- `extrautils_task5a_realworld_converted_patch_1182.json` – patch 1.18.2 wygenerowany z realnie zapisanej mapy.
- `extrautils_task5a_realworld_conversion_report.json` – porównanie real-world conversion z oczekiwanym patchem.
- `extrautils_task5a_redstone_spec.json` – spec testu redstone.

Mapa testowa:

- `lightweigh_map_templates/1710_modded/extrautils_task5a_world`
