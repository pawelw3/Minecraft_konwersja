# ForgeMultipart / CBMultipart - Zadanie 5B

## Cel
Zmaterializowac wynik 5A na headless Forge 1.18.2 przez datapack, bez bezposredniego zapisu do `.mca`.

## Wynik
- Swiat docelowy: `headless_server/1.18.2/world_forge_multipart_task5b`.
- Datapack: `headless_server/1.18.2/world_forge_multipart_task5b/datapacks/forge_multipart_task5b`.
- Liczba komend datapacka: 16.
- Liczba materializowanych BlockEntity: 15.
- Marker datapacka: `[FORGE_MULTIPART_TASK5B] apply complete`.

## Pliki
- `test_scenarios/forge_multipart_task5a/materialize_forge_multipart_task5b.py`
- `test_scenarios/forge_multipart_task5a/forge_multipart_task5b_headless_materialization_report.json`
- `test_scenarios/forge_multipart_task5a/server_forge_multipart_task5b.properties`

## Komenda
- `python test_scenarios\forge_multipart_task5a\materialize_forge_multipart_task5b.py`

## Uwagi
Ta wersja 5B wykorzystuje datapack `/setblock`, czyli omija ryzyko bezposredniej serializacji PalettedContainer w `.mca`.
