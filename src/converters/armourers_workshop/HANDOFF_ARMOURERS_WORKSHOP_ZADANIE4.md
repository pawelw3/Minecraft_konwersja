# Handoff: Armourer's Workshop, Zadanie 4

## Podsumowanie sesji

Wykonano standardowe Zadanie 4 dla moda Armourer's Workshop: read-only skan
stref glownej mapy `mapa_1710` oraz dodatkowych regionow kontrolnych. Raport
sprawdza dynamiczne ID blokow z `level.dat`, rzeczywiste TE ID z mapy oraz
pokrycie przez konwerter z Zadania 3, z osobnym rozroznieniem pelnego remapu i
placeholder-rescue.

## Ukonczono

- [x] Dodano skaner `analyze_map_coverage.py`.
- [x] Wczytano dynamiczne ID blokow AW z `mapa_1710/level.dat`.
- [x] Przeskanowano wszystkie strefy z `strefy/*/coords.json`.
- [x] Przeskanowano dodatkowe regiony: `(0,0)`, `(1,1)`, `(-1,-1)`, `(10,10)`, `(-10,-10)`.
- [x] Zweryfikowano rzeczywiste TE ID Armourer's Workshop na mapie.
- [x] Przepuszczono znalezione bloki/TE przez `ArmourersWorkshopConverter`.
- [x] Wygenerowano raport JSON i Markdown w `output/armourers_workshop_task4`.
- [x] Nie modyfikowano `mapa_1710`.

## Wyniki

- Dynamiczne ID blokow AW z `level.dat`: `19`.
- Regiony sprawdzone: `22`.
- Chunki sprawdzone: `11530`.
- Bloki AW znalezione: `36183`.
- Warianty blok/meta AW znalezione: `25`.
- Warianty blok/meta z pelnym remapem: `22`.
- Warianty blok/meta placeholder-rescue: `3`.
- Warianty blok/meta nieobslugiwane: `0`.
- Tile Entities AW znalezione: `35702`.
- TE z pelnym remapem: `35234`.
- TE placeholder-rescue: `468`.
- TE nieobslugiwane: `0`.

## Najwazniejsze TE

- `te.skinnableChild`: `21138`.
- `te.skinnable`: `13946`.
- `te.mannequin`: `468`.
- `te.armourLibrary`: `99`.
- `te.hologramProjector`: `43`.
- `te.globalSkinLibrary`: `5`.
- `te.skinningTable`: `1`.
- `te.dyeTable`: `1`.
- `te.colourMixer`: `1`.

## Nowe pliki

- `src/converters/armourers_workshop/analyze_map_coverage.py`
- `src/converters/armourers_workshop/HANDOFF_ARMOURERS_WORKSHOP_ZADANIE4.md`
- `output/armourers_workshop_task4/armourers_workshop_task4_coverage.json`
- `output/armourers_workshop_task4/ARMOURERS_WORKSHOP_ZADANIE4_COVERAGE.md`

## Zmodyfikowane pliki

- `HANDOFF.md`

## Weryfikacja

- `python -m py_compile src\converters\armourers_workshop\analyze_map_coverage.py` -> OK.
- `python src\converters\armourers_workshop\analyze_map_coverage.py` -> raport wygenerowany.
- `python -m pytest src\converters\armourers_workshop\tests -q` -> `22 passed`.

## Nastepne kroki

1. [ ] Zrobic batch runner `.armour`, zeby pelna migracja 146 plikow nie uruchamiala Gradle per plik.
2. [ ] Uruchomic pelna migracje biblioteki do `mapa_118/skin-library`.
3. [ ] Po migracji uzyc wynikow Zadania 4 do kontroli TE `skinnable`/`skinnableChild` i placeholderow `mannequin`.
