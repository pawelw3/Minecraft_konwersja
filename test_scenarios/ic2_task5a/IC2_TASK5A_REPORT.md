# IC2 Task 5A — Testowa mapa i konwersja (Raport)

## Podsumowanie

Wykonano testową mapę 1.7.10 z 32 reprezentatywnymi blokami i BE IC2, uruchomiono konwersję do 1.18.2 (indreb/ftbic) i zaaplikowano skonwertowane eventy na docelowym świecie 1.18.2.

## Świat źródłowy (1.7.10)

- **Lokalizacja:** `lightweigh_map_templates/1710_modded/ic2_task5a_world`
- **Baza:** lekki template `betterstorage_test` + `level.dat` z `mapa_1710` (zawiera FML/ItemData z IC2)
- **Region:** `r.0.0.mca` (chunk 6,6)
- **Bloki wstawione:** 32 samples (51 edits: set_block + set_te)
- **ID bloków IC2 z mapa_1710:** 466–521 (56 entries)

## Samples (kategorie)

| Kategoria | Bloki | BE |
|-----------|-------|-----|
| machines | Machine Block, Macerator, Electric Furnace, Compressor, Induction Furnace, Mass Fabricator | ✅ 5 TE |
| machines2 | Teleporter, Thermal Centrifuge, Metal Former | ✅ 3 TE |
| machines3 | Blast Furnace | ❌ niezmapowany (meta=13) |
| generators | Generator, Solar Panel, Nuclear Reactor | ✅ 3 TE |
| storage | BatBox, MFE, MFSU, CESU | ✅ 4 TE |
| transformers | LV, MV, HV Transformer | ✅ 3 TE |
| cables | Copper, Glass Fibre, Gold, Tin | ❌ brak TE |
| resources | Copper ore, Uranium ore, Rubber wood | ❌ brak TE |
| personal | Chargepad | ✅ 1 TE |
| reactor | Chamber, Fluid Port, Access Hatch, Redstone Port, Vessel | ❌ brak TE |

## Konwersja (1.18.2)

- **Skonwertowane:** 31/32 bloków
- **Niepowodzenie:** Blast Furnace (`IC2:blockMachine3` meta=13) — brak mapowania
- **Target moddy:** indreb (primary), ftbic (fallback)
- **Lokalizacja target world:** `lightweigh_map_templates/118_modded/ic2_task5a_converted`

## Weryfikacja docelowych bloków (chunk 6,6, sekcja Y=4)

Palette 1.18.2 zawiera 26 entries, w tym wszystkie skonwertowane bloki:
- `indreb:crusher`, `indreb:electric_furnace`, `indreb:compressor`
- `ftbic:antimatter_constructor`, `ftbic:teleporter`
- `indreb:battery_box`, `indreb:mfe`, `indreb:mfsu`
- `indreb:generator`, `indreb:solar_generator`, `indreb:semifluid_generator`
- `indreb:lv_transformer`, `indreb:hv_transformer`, `indreb:ev_transformer`
- `indreb:copper_cable_insulated`, `indreb:gold_cable`, itp.

## Pliki wygenerowane

- `ic2_task5a_source_patch_1710.json` — patch 1.7.10 (51 edits)
- `ic2_task5a_converted_patch_1182.json` — patch 1.18.2 (31 edits)
- `ic2_task5a_events_1182.json` — eventy w formacie worker 1182 (`pos`, `block`, `nbt`)
- `ic2_task5a_conversion_report.json` — pełny raport z warnings/errors per sample

## Otwarte kwestie

1. **Thermal Centrifuge** — zmapowany na placeholder (brak odpowiednika w indreb)
2. **Testy redstone** — do przygotowania jako Zadanie 5B/6 (headless serwer)
