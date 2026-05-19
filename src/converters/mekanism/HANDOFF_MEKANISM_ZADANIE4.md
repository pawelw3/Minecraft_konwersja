# Handoff: Mekanism - Zadanie 4

## Podsumowanie sesji

Wykonano Zadanie 4 dla **Mekanism core**: sprawdzono pokrycie konwertera na strefach glownej mapy `mapa_1710` bez edycji mapy. Skaner czyta dynamiczne ID blokow z `level.dat` / FML `ItemData`, skanuje tylko chunki przecinajace strefy i zapisuje raporty do `output/mekanism/`.

## Ukonczono

- [x] Dodano skaner pokrycia `src/converters/mekanism/analyze_map_coverage.py`.
- [x] Przeskanowano strefy: billund, choroszcz, iii_rzesza, rzym, zsrr.
- [x] Zweryfikowano rzeczywiste TE ID Mekanism na mapie.
- [x] Uruchomiono konwerter z Zadania 3 na znalezionych TE.
- [x] Wygenerowano raport JSON i Markdown.
- [x] Uruchomiono testy konwertera i symulacji po skanie.

## Wyniki

- Regiony sprawdzone: 17.
- Chunks sprawdzone: 7676.
- Bloki Mekanism w strefach: 157492.
- Tile Entities Mekanism w strefach: 199.
- TE skonwertowane przez kod: 199.
- TE nieobslugiwane: 0.
- Warianty blokow z mapowaniem: 36.
- Warianty blokow bez mapowania: 11.

Najczestsze TE:

- `QuantumEntangloporter`: 41.
- `Bin`: 39.
- `ElectricPump`: 20.
- `UltimateSmeltingFactory`: 18.
- `DigitalMiner`: 18.
- `MekanismTeleporter`: 17.
- `EnergyCube`: 11.

Najczestsze bloki:

- `Mekanism:OreBlock:1`: 54503.
- `Mekanism:OreBlock:2`: 48753.
- `Mekanism:OreBlock:0`: 39085.
- `Mekanism:SlickPlasticBlock:8`: 10819.

## Pliki

Nowe:

- `src/converters/mekanism/analyze_map_coverage.py`
- `output/mekanism/mekanism_coverage_report.json`
- `output/mekanism/mekanism_coverage_report.md`
- `src/converters/mekanism/HANDOFF_MEKANISM_ZADANIE4.md`

Zmodyfikowane:

- `HANDOFF.md`

## Luki wykryte w pokryciu blokow

Konwerter pokrywa wszystkie TE, ale brakuje mapowania dla 11 wariantow blokow:

- `Mekanism:BoundingBlock:0`
- `Mekanism:BoundingBlock:1`
- `Mekanism:ObsidianTNT:0`
- `Mekanism:PlasticBlock:7`
- `Mekanism:PlasticBlock:8`
- `Mekanism:PlasticBlock:12`
- `Mekanism:PlasticBlock:15`
- `Mekanism:RoadPlasticBlock:3`
- `Mekanism:SaltBlock:0`
- `Mekanism:SlickPlasticBlock:8`
- `Mekanism:SlickPlasticBlock:15`

Proponowana naprawa:

1. `Mekanism:SaltBlock:0` -> `mekanism:block_salt` (target istnieje w JAR 1.18.2).
2. `Mekanism:BoundingBlock:*` -> sprawdzic czy mozna mapowac do `mekanism:bounding_block` / `mekanism:advanced_bounding_block`, albo usuwac jako cache bounding multibloku z eventem.
3. Plastiki (`PlasticBlock`, `SlickPlasticBlock`, `RoadPlasticBlock`) nie wygladaja na dostepne jako bloki w Mekanism 10.2.5; wymagaja decyzji zamiennika dekoracyjnego albo placeholdera.
4. `ObsidianTNT` nie ma oczywistego targetu w Mekanism 10.2.5; proponowane targety do decyzji: `minecraft:tnt`, blok dekoracyjny/placeholder, albo raport do recznej naprawy.

## Warningi z konwersji TE

Warningi sa spodziewane:

- Energy: konwerter zapisuje polityke `preserve_legacy_joules_or_fill_ratio`, bo przelicznik J -> FE/energy wymaga potwierdzenia.
- Owner/frequency: czesc TE ma legacy owner name bez UUID.
- Digital Miner: `running=false`, bo cache `oresToMine` musi zostac przeliczony w target.
- Cache NBT typu `isActive` / `numPowering` jest pomijany.

## Weryfikacja

- `python -B src/converters/mekanism/analyze_map_coverage.py` - OK, raport wygenerowany.
- `python -B -m unittest src.converters.mekanism.tests.test_mekanism_converter src.converters.mekanism.simulations.test_simulations` - 26 testow OK.

## Nastepne kroki

1. [ ] Naprawic mapowania 11 brakujacych wariantow blokow albo oznaczyc je jawnie jako placeholder/removed.
2. [ ] Uruchomic ponownie Zadanie 4 po naprawie i oczekiwac `unsupported_block_variants = 0`.
3. [ ] W Zadaniu 5A zbudowac mape testowa obejmujaca znalezione realne przypadki: QuantumEntangloporter, Bin, DigitalMiner, elite factories, teleportery, EnergyCube, plastiki/bounding.
