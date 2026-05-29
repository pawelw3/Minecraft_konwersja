# Handoff: progres konwersji custom_area_1800_574

## Podsumowanie sesji
Dopisano jawne raportowanie postepu do `convert_area.py`, szczegolnie dla etapow, ktore wczesniej byly ciche. Ustalono, ze Amulet wisial w `load_level` przed kopiowaniem chunkow, wiec w tym miejscu nie da sie podac uczciwego licznika "chunkow zaladowanych"; skrypt pokazuje teraz zakres chunkow i przerywa ten etap po limicie.

## Ukończono
- [x] Dodano `ProgressReporter` z procentem, licznikami, czasem, tempem i ETA dla etapow z policzalnym `total`.
- [x] Dodano licznik slotow chunkow w obszarze konwersji (`chunk_slots_in_area=N/1148`).
- [x] Dodano preflight Amulet `load_level` z limitem 180 sekund.
- [x] Dodano twardy watchdog dla faktycznego `Amulet load source/target world`, zeby proces nie wisial godzinami.
- [x] Dodano progres dla: kopiowania chunkow Amulet, patchowania `minecraft:numerical`, generowania eventow i JVM workera.
- [x] Sprawdzono skladnie: `python -m py_compile tasks\custom_area_1800_574\convert_area.py`.

## Zmodyfikowane pliki
- `tasks/custom_area_1800_574/convert_area.py`
- `tasks/custom_area_1800_574/HANDOFF_PROGRESS_INSTRUMENTATION_2026-05-29.md`

## Obserwacja diagnostyczna
Poprzedni run wisial okolo 100 minut na `Amulet load source world`. To oznacza, ze Amulet nie zaczal jeszcze przetwarzac zadnych z 1148 chunkow z wybranego obszaru.

## Następne kroki
1. [ ] Uruchomic `python -u tasks\custom_area_1800_574\convert_area.py`.
2. [ ] Jesli preflight Amulet przekroczy 180 sekund, pominac Amulet dla tej strefy albo zastapic etap 2 innym mechanizmem konwersji terenu.
3. [ ] Po udanej glownej konwersji osobno uruchomic konwersje skin-library Armourer's Workshop, jesli ten save ma zawierac skiny.
