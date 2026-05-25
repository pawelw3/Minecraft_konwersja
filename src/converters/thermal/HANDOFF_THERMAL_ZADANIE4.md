# Handoff: Thermal Series - Zadanie 4 (Sprawdzenie stref glownej mapy)

## Podsumowanie sesji
Przeskanowano 17 regionow z 5 stref + 3 dodatkowe regiony. Znaleziono 3 004 Tile Entities Thermal (18 typow) oraz 346 817 blokow Thermal (13 typow). Wszystkie znalezione elementy sa obslugiwane przez konwerter (100% pokrycia). Naprawiono mapowanie sub-blokow ThermalDynamics (ThermalDynamics_0/16/32/48/64).

## Ukonczono
- [x] Odkrycie TE ID na realnej mapie 1.7.10 (18 typow, 3 004 instancje)
- [x] Odkrycie block IDs na realnej mapie (13 typow, 346 817 instancji)
- [x] Sprawdzenie pokrycia: 100% TE, 100% blokow
- [x] Naprawa mapowan sub-blokow ThermalDynamics w `mappings.py`
- [x] Porownanie symulacji 1.7.10 vs 1.18.2
- [x] Wygenerowanie raportow w `output/`
- [x] 40/40 testow pytest przechodzi

## Nowe pliki
- `src/converters/thermal/discover_te_ids_fast.py`
- `src/converters/thermal/discover_block_ids_fast.py`
- `src/converters/thermal/analyze_coverage.py`
- `output/thermal_te_discovery.json`
- `output/thermal_block_discovery.json`
- `output/thermal_coverage_report.md`
- `output/thermal_coverage.json`
- `output/thermal_zadanie4_report.md`

## Zmodyfikowane pliki
- `src/converters/thermal/mappings.py` - dodano obsluge sub-blokow ThermalDynamics:ThermalDynamics_0/16/32/48/64

## Kluczowe odkrycia
1. **ThermalDynamics sub-bloki**: Mapa uzywa `ThermalDynamics:ThermalDynamics_*` zamiast `ThermalDynamics:FluxDuct/FluidDuct/ItemDuct`. Konwerter musi dodawac offset do metadata.
2. **Najwiecej blokow**: ThermalFoundation:Ore (342 369 blokow) - rudy rozrzucone po calej mapie.
3. **Najwiecej TE**: thermaldynamics.ItemDuct (1 582) i thermaldynamics.FluxDuctSuperConductor (1 106) - logistyka i energia dominuja.
4. **Symulacje**: Uproszczone w porownaniu do 1.18.2, ale wystarczajace dla konwersji NBT.

## Ograniczenia (akceptowalne)
- Tier loss: Wszystkie energy ducts -> `thermal:energy_duct`
- ItemDuct loss: Fallback na `thermal:item_buffer` lub Mekanism
- Opaque variants: Traca przezroczystosc

## Nastepne kroki
1. [ ] Zadanie 5A: Wykonanie testowej mapy 1.7.10 ze wszystkimi blokami Thermal + konwersja
2. [ ] Zadanie 5B: Headless serwer vanilla 1.7.10 -> konwersja -> headless 1.18.2
3. [ ] Zadanie 6: Test integracyjny na headless serwerze (3 min tickow)
