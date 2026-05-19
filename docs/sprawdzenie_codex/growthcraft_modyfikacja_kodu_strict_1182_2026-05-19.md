# Growthcraft - start modyfikacji kodu pod strict 1.18.2

Data: 2026-05-19

## Decyzja techniczna

Domyslny konwerter Growthcraft nie mapuje juz bezposrednio na `growthcraft_cellar`, `growthcraft_milk` i `growthcraft_apiary`, bo to nie jest bezpieczny cel strict 1.18.2 wedlug nowej specyfikacji. Stare mapowanie zostaje jako profil:

- `strict_1182_functional` - domyslny, funkcjonalny cel 1.18.2.
- `growthcraft_ce_experimental` - zachowane stare mapowania Growthcraft CE i stare konwertery NBT.

## Nowe mapowanie strict

Najwazniejsze funkcje:

| Growthcraft 1.7.10 | Strict 1.18.2 | Uwagi |
|---|---|---|
| `grccellar:ferment_barrel` | `brewinandchewin:keg` | Dane procesu zachowane w `legacy_growthcraft`. |
| `grccellar:brew_kettle` | `brewinandchewin:keg` | Wymaga pozniejszego dopracowania receptur. |
| `grccellar:fruit_press` | `create:mechanical_press` | Funkcja tloczenia zamiast portu Growthcraft. |
| `grcmilk:cheese_vat` i pokrewne | `farmersdelight:cooking_pot` | Funkcja kulinarna; stare plyny i stan procesu zapisane ratunkowo. |
| `grcbees:bee_box` | `minecraft:beehive` | Bezpieczny blok strict; preferowany mod funkcjonalny: Productive Bees. |
| `grcfishtrap:fish_trap` | `minecraft:barrel` | Brak odpowiednika automatycznej pulapki. |

## Zachowanie NBT

Profil strict nie probuje udawac pelnej zgodnosci NBT z docelowymi modami. Zamiast tego tworzy docelowy blok i dodaje:

- `conversion_profile: strict_1182_functional`
- `legacy_growthcraft.source_block_id`
- `legacy_growthcraft.source_te_id`
- `legacy_growthcraft.process`
- `legacy_growthcraft.items`
- `legacy_growthcraft.fluids`

Dzieki temu nie tracimy informacji z mapy, ale tez nie zapisujemy falszywych struktur NBT dla Brewin' and Chewin', Farmer's Delight, Create ani Productive Bees.

## Zmienione pliki

- `src/converters/growthcraft/mappings/__init__.py`
- `src/converters/growthcraft/growthcraft_converter.py`
- `src/converters/growthcraft/nbt_converters/base_converter.py`
- `src/converters/growthcraft/tests/test_growthcraft_converter.py`

## Testy

Uruchomiono:

```powershell
python -m unittest src.converters.growthcraft.tests.test_growthcraft_converter src.converters.growthcraft.tests.test_nbt_converters
```

Wynik: 34 testy, OK.

## Nastepne kroki

1. Zweryfikowac dokladne ID itemow/blokow z docelowego zestawu JAR dla Brewin' and Chewin', Farmer's Delight, Productive Bees i dodatkow.
2. Dodac raportowanie miejsc na mapie, w ktorych `legacy_growthcraft` zawiera plyny/procesy wymagajace recznego lub polautomatycznego odtworzenia.
3. Dodac osobny postprocessor dla beehive/Productive Bees, jezeli w paczce docelowej potwierdzimy stabilne ID uli i format danych.
