# BuildCraft Task 5A – Testowa mapa i konwersja (Raport)

## Podsumowanie

Wykonano testową mapę 1.7.10 z 12 reprezentatywnymi blokami i TE BuildCraft, uruchomiono konwersję do 1.18.2 (Pipez / Thermal / Mekanism) i zaaplikowano skonwertowane eventy na docelowym świecie 1.18.2.

## Świat źródłowy (1.7.10)

- **Lokalizacja:** `test_scenarios/buildcraft_task5a/buildcraft_task5a_world`
- **Baza:** lekki template `ic2_task5a_world` (level.dat z FML/ItemData zawierającym rejestr BuildCraft)
- **Region:** `r.0.0.mca` (chunk 2,2)
- **Bloki wstawione:** 12 samples (24 edits: set_block + set_te)
- **ID bloków BuildCraft z rejestru:** 217-246 (30 entries)

## Samples (kategorie)

| Kategoria | Blok | TE | Akcja | Cel 1.18.2 |
|-----------|------|-----|-------|-----------|
| engines | Engine Block (meta 0/1/2) | TileEngineWood/Stone/Iron | REMOVE / CONVERT | air / thermal:dynamo_steam / thermal:dynamo_compression |
| factory | Tank Block | TileTank | CONVERT | mekanism:basic_fluid_tank |
| factory | Pump Block | TilePump | CONVERT | mekanism:electric_pump |
| factory | Refinery Block | Refinery | CONVERT | thermal:machine_refinery |
| transport | Pipe Block | GenericPipe | CONVERT | pipez:universal_pipe |
| silicon | Laser Block | TileLaser | REMOVE | air |
| silicon | Laser Table Block (meta 0/1) | TileAssemblyTable / TileIntegrationTable | REMOVE | air |
| robotics | Zone Plan Block | TileZonePlan | REMOVE | air |
| factory | Auto Workbench Block | TileAutoWorkbench | REMOVE | air |

## Konwersja (1.18.2)

- **Skonwertowane:** 12/12 bloków (100%)
- **Niepowodzenie:** 0
- **Target mody:** Pipez, Thermal Expansion, Mekanism
- **Lokalizacja target world:** `test_scenarios/buildcraft_task5a/buildcraft_task5a_converted`

## Wyniki konwersji per sample

| Sample | TE ID | Cel 1.18.2 | Status |
|--------|-------|-----------|--------|
| EngineWood | TileEngineWood | `minecraft:air` | REMOVE ✅ |
| EngineStone | TileEngineStone | `thermal:dynamo_steam` + facing + NBT | CONVERT ✅ |
| EngineIron | TileEngineIron | `thermal:dynamo_compression` + facing + NBT | CONVERT ✅ |
| Tank | TileTank | `mekanism:basic_fluid_tank` + fluids | CONVERT ✅ |
| Pump | TilePump | `mekanism:electric_pump` + fluids + energy | CONVERT ✅ |
| Refinery | Refinery | `thermal:machine_refinery` + fluids | CONVERT ✅ |
| GenericPipe | GenericPipe | `pipez:universal_pipe` | CONVERT ✅ |
| Laser | TileLaser | `minecraft:air` | REMOVE ✅ |
| AssemblyTable | TileAssemblyTable | `minecraft:air` | REMOVE ✅ |
| IntegrationTable | TileIntegrationTable | `minecraft:air` | REMOVE ✅ |
| ZonePlan | TileZonePlan | `minecraft:air` | REMOVE ✅ |
| AutoWorkbench | TileAutoWorkbench | `minecraft:air` | REMOVE ✅ |

## Weryfikacja docelowego świata

- Worker Hephaistos zaaplikował 12/12 eventów bez błędów
- Chunk (2,2) w regionie r.0.0 zawiera `block_entities` (potwierdzone przez worker read)

## Pliki wygenerowane

- `buildcraft_task5a_source_patch_1710.json` — patch 1.7.10 (24 edits)
- `buildcraft_task5a_converted_patch_1182.json` — patch 1.18.2 (12 edits)
- `buildcraft_task5a_events_1182.json` — eventy w formacie worker 1.18.2
- `buildcraft_task5a_conversion_report.json` — pełny raport z wynikami per sample

## Otwarte kwestie

1. **Custom receptura oil->fuel** — wymaga dodania do data packa przed testami w grze
2. **Testy headless serwer (Task 5B/6)** — do przygotowania jeśli wymagane
