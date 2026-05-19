# Handoff: ForgeMultipart/CB Multipart — Zadanie 4

## Podsumowanie sesji
Wykonano analizę pokrycia konwertera ForgeMultipart na rzeczywistej mapie 1.7.10. Odkryto exact string rejestracji TileMultipart (`savedMultipart`), przeskanowano wszystkie 5 stref + dodatkowe regiony, zweryfikowano działanie symulacji 1.18.2 na przekonwertowanych danych z mapy. Zidentyfikowano jeden nieobsługiwany part (`pr_cagelamp2`) który należy do ProjectRed i wymaga mapowania w konwerterze ProjectRed.

## Ukończono
- [x] Odkrycie exact TE ID z mapy: `savedMultipart` (TileMultipart 1.7.10)
- [x] Aktualizacja `mappings.py` o potwierdzony string `savedMultipart`
- [x] Skan wszystkich 5 stref (20 regionów) + analiza całej mapy (1195 regionów, sample)
- [x] Znaleziono 284,323 wystąpień `savedMultipart` na całej mapie
- [x] Identyfikacja partów w TileMultipart: `mcr_face`, `mcr_edge`, `mcr_post`, `mc_torch`, `mcr_cnr`, `pr_cagelamp2`
- [x] Dodano alias `mcr_cnr` → `microblockcbe:corner`
- [x] Weryfikacja symulacji 1.18.2 na 50 próbkach z mapy: **45/50 OK**
- [x] Analiza 5 FAILów: wszystkie to `pr_cagelamp2` (ProjectRed cage lamp) — poza zakresem ForgeMultipart
- [x] Raporty zapisane w `output/forge_multipart/`

## Nowe pliki
- `src/converters/forge_multipart/analyze_map.py` — skaner mapy pod kątem ForgeMultipart
- `src/converters/forge_multipart/verify_1182_sim.py` — weryfikacja symulacji 1.18.2 na danych z mapy

## Zmodyfikowane pliki
- `src/converters/forge_multipart/mappings.py` — dodano `savedMultipart`, `mcr_cnr`
- `src/converters/forge_multipart/forge_multipart_converter.py` — rozszerzono wykrywanie TE ID
- `src/converters/forge_multipart/tests/test_forge_multipart_converter.py` — testy dla `savedMultipart`

## Kluczowe odkrycia

### Exact TE ID
W NBT chunka 1.7.10 TileMultipart jest zapisywane jako **`savedMultipart`** (nie `TileMultipart` ani `ForgeMultipart:TileMultipart`). Potwierdzone w kodzie źródłowym (MultipartSaveLoad) oraz na mapie.

### Skala na mapie
- Cała mapa: **284,323** TileMultipart
- Strefy (20 regionów): **~14,000+** (dokładna liczba w `forge_multipart_analysis.json`)

### Pokrycie partów
| Part ID | Obsługiwany | Uwagi |
|---------|-------------|-------|
| `mcr_face` | ✅ | mikroblok płytka |
| `mcr_edge` | ✅ | mikroblok krawędź |
| `mcr_post` | ✅ | mikroblok słup |
| `mcr_cnr` | ✅ | alias `mcr_corner` |
| `mc_torch` | ✅ | vanilla torch part |
| `pr_cagelamp2` | ❌ | **ProjectRed cage lamp** — do obsługi przez konwerter ProjectRed |

### Weryfikacja symulacji 1.18.2
- **45/50** próbek przechodzi round-trip konwersja → deserializacja 1.18.2
- **5/50** FAIL — wszystkie zawierają `pr_cagelamp2` (brak rejestracji w symulacji CB Multipart)
- Dla czystych partów ForgeMultipart (mikrobloki + vanilla): **100% pokrycia**

## Otwarte kwestie
1. **`pr_cagelamp2` mapowanie:** Wymaga analizy w konwerterze ProjectRed (1.7.10 `pr_cagelamp2` + meta kolor → 1.18.2 `projectred-illumination:{color}_cage_light`).
2. **Inne part-y ProjectRed:** Na mapie mogą występować inne part-y PR (przewody, bramki) w TileMultipart — te są obsługiwane przez konwerter ProjectRed.
3. **Exact block ID `ForgeMultipart:block`:** Wymaga weryfikacji czy na mapie występują bloki z tym ID (TileMultipart może być używane przez inne mody jako kontener).

## Następne kroki
1. **Zadanie 5A:** Przygotowanie testowej mapy 1.7.10 z wszystkimi blokami/partami ForgeMultipart i wykonanie konwersji.
2. **Integracja z ProjectRed:** Współpraca konwertera ForgeMultipart z konwerterem ProjectRed przy obsłudze wspólnych TileMultipart.
