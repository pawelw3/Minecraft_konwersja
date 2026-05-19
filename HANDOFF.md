# Handoff: Growthcraft strict 1.18.2 - start modyfikacji kodu

## Podsumowanie sesji

Rozpoczeto modyfikacje konwertera Growthcraft zgodnie z nowa specyfikacja funkcjonalna. Domyslny profil konwersji nie celuje juz w Growthcraft CE, tylko w zamienniki strict 1.18.2, a poprzednia sciezka Growthcraft CE zostala zachowana jako profil eksperymentalny.

## Ukończono

- [x] Dodano profile `strict_1182_functional` i `growthcraft_ce_experimental`.
- [x] Ustawiono profil strict jako domyslny w `GrowthcraftConverter`.
- [x] Dodano strict mapowanie blokow Growthcraft na Brewin' and Chewin', Farmer's Delight, Create, vanilla beehive/barrel i inne bezpieczne zamienniki.
- [x] Dodano zachowanie danych procesow, itemow i plynow w `legacy_growthcraft` dla strict NBT.
- [x] Zachowano stare konwertery NBT jako profil `growthcraft_ce_experimental`.
- [x] Zaktualizowano testy integracyjne Growthcraft pod oba profile.
- [x] Zweryfikowano lokalne JAR-y dla Create, Mekanism, Supplementaries i Productive Bees.
- [x] Poprawiono `grcbees:bee_box` na potwierdzone `productivebees:advanced_*_beehive`.

## Nowe pliki

- `docs/sprawdzenie_codex/growthcraft_modyfikacja_kodu_strict_1182_2026-05-19.md`

## Zmodyfikowane pliki

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

Ponownie uruchomiono po poprawce Productive Bees: 34 testy, OK.

## Następne kroki

1. [ ] Dostarczyc albo pobrac docelowe JAR-y Brewin' and Chewin' i Farmer's Delight, jesli maja byc twardym celem konwersji strict.
2. [ ] Dodac raport wystapien Growthcraft na mapie z agregacja `legacy_growthcraft`, bez ladowania calej mapy.
3. [ ] Przygotowac postprocessor dla Productive Bees/Brewin' and Chewin' tam, gdzie format NBT docelowego moda jest potwierdzony.
