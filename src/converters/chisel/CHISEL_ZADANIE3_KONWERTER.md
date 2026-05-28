# Chisel - Zadanie 3: konwerter eventow

## Podsumowanie

Dodano konwerter `ChiselConverter`, ktory produkuje eventy zgodne z handlerem mapy 1.18.2.

Zakres:

- Bloki dekoracyjne Chisel 1.7.10 -> Rechiseled/Chipped/minecraft fallback.
- Dynamiczne numeric ID -> rodzina Chisel przez przekazana tabele `DynamicChiselIdEntry`.
- Tile entities Chisel bez odpowiednika 1.18.2 -> placeholder z pelnym NBT.
- Integracja TE Chisela z `converters.router`.

## Pliki

- `src/converters/chisel/mappings.py`
- `src/converters/chisel/chisel_converter.py`
- `src/converters/chisel/tests/test_chisel_converter.py`
- `src/converters/router.py`

## Decyzje konwersji

### Dekoracyjne bloki bez TE

W 1.7.10 Chisel zapisuje dekoracje jako numeric ID + metadata. Konwerter celowo nie zgaduje nieznanych numeric ID bez tabeli dynamicznej, bo moglby przypadkiem przekonwertowac cudzy blok. Dla numeric ID wymagane jest:

```python
{
    2001: DynamicChiselIdEntry(
        numeric_id=2001,
        family="factory",
        meta_variants={7: "rust_plate"},
    )
}
```

Jesli wejscie jest nazwane (`chisel:andesite`, `chisel:factory`, itd.), konwerter dobiera target przez `resolve_visual_target()`.

### Polityka wizualna

Priorytet mapowania:

1. Rechiseled: rodzina materialu i pattern (`tiles`, `bricks`, `polished`, `chiseled`, `pillar`, `bordered`).
2. Specjalne fallbacki wizualne, np. `factory`/`technical` -> industrialne warianty `iron_block`.
3. Chipped: fallback po patternie, gdy Rechiseled nie ma bliskiego odpowiednika.
4. Vanilla fallback, np. `andesite` -> `minecraft:polished_andesite`.

To jest pierwszy dzialajacy krok. Dokladniejsze dopasowanie po histogramach tekstur powinno wejsc przy Zadaniu 4/5, po skanie realnych wystapien na mapie.

### Tile entities

Wykrywane TE:

- `TileEntityAutoChisel`
- `TileEntityCarvableBeacon`
- `TileEntityPresent`
- warianty z `autoChisel` / `auto_chisel` w nazwie

Rechiseled 1.18.2 nie ma analogicznej maszyny/block entity, wiec TE sa konwertowane na `conversion_placeholders:*` z:

- oryginalnym NBT,
- pozycja,
- metadata,
- rekomendowana akcja manualna,
- informacja, ze dekoracyjne bloki trzeba konwertowac osobno po ID/meta.

## API

```python
from converters.chisel.chisel_converter import ChiselConverter
from converters.chisel.mappings import DynamicChiselIdEntry

converter = ChiselConverter(dynamic_id_map={
    2001: DynamicChiselIdEntry(2001, "factory", {7: "rust_plate"}),
})

conversion = converter.convert_block(2001, metadata=7, position=(0, 70, 0))
events = converter.to_events(conversion)
```

TE przez router:

```python
from converters.router import convert_te_to_events

events = convert_te_to_events(
    {"id": "TileEntityAutoChisel", "Items": []},
    block_numeric_id=0,
    metadata=0,
    global_pos=(8, 65, 9),
)
```

## Weryfikacja

Komendy:

- `python -m pytest src\converters\chisel\tests -q`
- `python -m py_compile src\converters\router.py src\converters\chisel\chisel_converter.py src\converters\chisel\mappings.py`

Wynik:

- `14 passed`
- compile bez bledow

## Ograniczenia swiadome

- Brak jeszcze skanu realnej mapy, wiec dynamiczne ID trzeba przekazac z zewnatrz.
- Metadata Chisel nie jest jeszcze rozwinieta do dokladnej starej tekstury; jest obslugiwane jako `variant_hint`, gdy dynamiczny skan go dostarczy.
- Chipped jest traktowany jako fallback po nazwach blockstates; dokladniejsze wykorzystanie wymaga porownania tekstur.

