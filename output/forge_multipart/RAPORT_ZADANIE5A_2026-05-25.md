# ForgeMultipart / CBMultipart - Zadanie 5A

## Cel
Powtorzyc testowa konwersje po korekcie mapowan na podstawie kodu zrodlowego CBMultipart 1.18.x.

## Wynik
- Konwersja testowej mapy 1.7.10: 15/15 sukces.
- Bledy konwersji: 0.
- Weryfikacja symulacji 1.18.2: 15/15 OK.
- Eventy 1.18.2 wygenerowane: 15.

## Pliki
- `output/forge_multipart/task5a_conversion_result.json`
- `output/forge_multipart/task5a_verification.json`
- `output/forge_multipart/task5a_events_1182.json`

## Komendy
- `python src\converters\forge_multipart\convert_test_map.py`
- `python src\converters\forge_multipart\verify_task5a.py`
- `python src\converters\forge_multipart\generate_1182_events.py`

## Uwagi
Po korekcie eventy uzywaja `cb_microblock:*` dla mikroblokow oraz `minecraft:*` dla vanilla parts CBMultipart.
