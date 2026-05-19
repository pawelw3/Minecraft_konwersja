# Dokumentacja projektu Minecraft 1.7.10 → 1.18.2

## OBOWIĄZUJĄCA SPECYFIKACJA MAPOWANIA MODÓW

> **`docs/sprawdzenie_codex/`** — weryfikacja maja 2026, uwzględnia skanowanie rzeczywistej mapy (5 GB, 1195 region files). To jest jedyne aktualne źródło prawdy dla mapowania modów.

Kluczowe pliki specyfikacji:

| Plik | Zawartość |
|------|-----------|
| [cz1_analiza_funkcjonalnosci_i_zamiennikow_2026-05-18.md](sprawdzenie_codex/cz1_analiza_funkcjonalnosci_i_zamiennikow_2026-05-18.md) | AE2, Better Storage, Armourer's Workshop, Baubles, Backpack, Treecapitator |
| [cz2_analiza_funkcjonalnosci_i_zamiennikow_2026-05-18.md](sprawdzenie_codex/cz2_analiza_funkcjonalnosci_i_zamiennikow_2026-05-18.md) | Carpenter's Blocks, Big Reactors, CustomNPCs, BiblioCraft, Extra Utilities |
| [cz3_analiza_funkcjonalnosci_i_zamiennikow_2026-05-18.md](sprawdzenie_codex/cz3_analiza_funkcjonalnosci_i_zamiennikow_2026-05-18.md) | ForgeMultipart, Growthcraft, IC2, Forestry, Logistics Pipes, Jammy Furniture |
| [cz4_analiza_funkcjonalnosci_i_zamiennikow_2026-05-18.md](sprawdzenie_codex/cz4_analiza_funkcjonalnosci_i_zamiennikow_2026-05-18.md) | MrCrayfish Furniture, Placeable Items, Railcraft, ProjectRed |
| [cz5_analiza_funkcjonalnosci_i_zamiennikow_2026-05-18.md](sprawdzenie_codex/cz5_analiza_funkcjonalnosci_i_zamiennikow_2026-05-18.md) | Thaumcraft, Thermal Series, Witchery, Traincraft, Reliquary |
| [analiza_mod_mapping_indepth_2026-05-18.md](sprawdzenie_codex/analiza_mod_mapping_indepth_2026-05-18.md) | Przegląd i korekty wcześniejszej dokumentacji |
| [audyt_kodu_konwerterow_vs_mapowanie_2026-05-19.md](sprawdzenie_codex/audyt_kodu_konwerterow_vs_mapowanie_2026-05-19.md) | Rozbieżności między kodem konwerterów a specyfikacją |
| [porownanie_sprawdzenia_kimi_2026-05-19.md](sprawdzenie_codex/porownanie_sprawdzenia_kimi_2026-05-19.md) | Porównanie z niezależnym audytem (Kimi); rozstrzygnięcia spornych punktów |

---

## Pozostałe dokumenty

| Plik/katalog | Rola |
|---|---|
| [PLAN.md](PLAN.md) | Architektura i plan konwersji (warstwy A/B/C) |
| [LISTA_KONWERSJI_MODOW.md](LISTA_KONWERSJI_MODOW.md) | Lista docelowa modów 1.18.2 (na bieżąco aktualizowana wg specyfikacji) |
| [ANALIZA_MODOW_SZCZEGOLOWA.md](ANALIZA_MODOW_SZCZEGOLOWA.md) | Szczegółowe uwagi implementacyjne per-mod |
| [MAPAOWANIE_USUNIETYCH_MODOW.md](MAPAOWANIE_USUNIETYCH_MODOW.md) | Mody usunięte bez danych na mapie |
| [IGNORED_BLOCKS.md](IGNORED_BLOCKS.md) | Lista TE/bloków celowo ignorowanych przez konwerter |
| [WORKFLOW.md](WORKFLOW.md) | Workflow pracy z projektem |
| [przebudowa_common_event_handler/](przebudowa_common_event_handler/) | Architektura event handlera JVM |
| [sprawdzenie_kimi/](sprawdzenie_kimi/) | Niezależna weryfikacja mapowania (materiał do `porownanie_sprawdzenia_kimi`) |

---

## Archiwum

| Katalog | Status |
|---|---|
| [archive/mod_mapping_indepth/](archive/mod_mapping_indepth/) | **NIEAKTUALNY** — wczesne robocze analizy, zastąpione przez `sprawdzenie_codex/` |
