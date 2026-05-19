# Handoff: Thermal Dynamics — Zadanie 3 (Ukończone)

## Podsumowanie sesji

Ukończono **Zadanie 3** — napisanie kodu konwersji bloków i Tile Entities moda Thermal Dynamics z 1.7.10 na 1.18.2 (Thermal Dynamics + Mekanism). Kod produkuje eventy kompatybilne z ogólnym handlerem wstawiającym dane na mapę.

## Ukończono

- [x] `mappings.py` — pełna tabela mapowań `block_id + metadata → target_block_id` dla wszystkich 26 placeable ductów
- [x] `conversion_event.py` — klasa `ConversionEvent` do rejestrowania konwersji
- [x] `thermal_dynamics_converter.py` — główna klasa `ThermalDynamicsConverter` z metodami `convert_block()` i `convert_tile_entity()`
- [x] `nbt_converters/__init__.py` — zestaw konwerterów NBT:
  - `IdentityTDConverter` — minimalny konwerter (x,y,z)
  - `DuctNBTConverter` — obsługa załączników (Servo/Filter/Retriever) i coverów
  - `MekanismTransporterConverter` — konwersja Itemductów z zrzutem załączników
  - `MekanismTeleporterConverter` — konwersja Viaductów z domyślną częstotliwością
- [x] Integracja z `src/converters/router.py` — rejestracja w `detect_mod()`, lazy singleton, serializator `_thermal_dynamics_to_events()`
- [x] Zrzut załączników do skrzyń — załączniki są zrzucane do `conversion_placeholders:inventory_placeholder` nad skonwertowanym blokiem
- [x] Placeholder dla Structuralduct — bloki bez targetu trafiają na `conversion_placeholders:block_entity_placeholder`
- [x] Weryfikacja składniowa wszystkich plików
- [x] Testy manualne konwertera i routera

## Nowe pliki / zmodyfikowane

| Plik | Opis | Status |
|------|------|--------|
| `src/converters/thermal_dynamics/mappings.py` | Tabela mapowań 26 ductów | Nowy |
| `src/converters/thermal_dynamics/conversion_event.py` | Klasa eventu konwersji | Nowy |
| `src/converters/thermal_dynamics/thermal_dynamics_converter.py` | Główny konwerter | Nowy |
| `src/converters/thermal_dynamics/nbt_converters/__init__.py` | 4 konwertery NBT | Nowy |
| `src/converters/router.py` | Rejestracja TD w routerze | Zmodyfikowany |

## Architektura konwertera

```
ThermalDynamicsConverter
├── mappings.py
│   ├── BlockMapping (source_block_id, metadata, target_block_id, has_block_entity, nbt_converter)
│   ├── STATIC_MAPPINGS — 26 wpisów
│   └── TE_ID_TO_BLOCK — mapowanie TE ID → block_id (dla routera)
├── thermal_dynamics_converter.py
│   ├── ThermalDynamicsConverter
│   │   ├── convert_block(block_id, metadata, nbt, position) → TDBlockConversion
│   │   ├── convert_tile_entity(te_id, nbt, metadata, position) → TDBlockConversion
│   │   └── nbt_converters: dict[str, BaseTDNBTConverter]
│   ├── ConversionResult (success, block_id_1182, nbt_1182, warnings, errors, extra_items)
│   └── TDBlockConversion (original_id, original_pos, metadata, converted)
└── nbt_converters/__init__.py
    ├── IdentityTDConverter
    ├── DuctNBTConverter — obsługa attachment0..5, facade0..5
    ├── MekanismTransporterConverter — zrzut załączników do extra_items
    └── MekanismTeleporterConverter — generuje frequency NBT
```

## Mapowania bloków (skrót)

| Kategoria | 1.7.10 | 1.18.2 | NBT converter |
|-----------|--------|--------|---------------|
| Energy (6) | Duct0 meta 0,1,2,4,6 | `thermal:energy_duct` | `energy_duct` |
| Fluid (6) | Duct16 meta 0-5 | `thermal:fluid_duct` | `fluid_duct` |
| Fluid Super (2) | Duct16 meta 6,7 | `thermal:fluid_duct_windowed` | `fluid_duct` |
| Item (8) | Duct32 meta 0-7 | `mekanism:*_logistical_transporter` | `mekanism_transporter` |
| Transport (3) | Duct64 meta 0-2 | `mekanism:teleporter` | `mekanism_teleporter` |
| Transport Frame (1) | Duct64 meta 3 | `mekanism:teleporter_frame` | `identity` |
| Structural (2) | Duct48 meta 0,1 | **BRAK** → placeholder | — |

## Załączniki — zrzut do skrzyń

Załączniki (Servo/Filter/Retriever) są odczytywane z NBT ductu (`attachment0`..`attachment5`) i konwertowane na itemy do zrzutu:
- Typ rozpoznawany po polach NBT (`speed` = Servo, `filter` = Filter, brak = Retriever)
- Tier rozpoznawany po `metadata` (0=basic, 1=hardened, 2=reinforced, 3=signalum, 4=resonant)
- W routerze generowany jest dodatkowy event `conversion_placeholders:inventory_placeholder` nad skonwertowanym blokiem z załącznikami w `attached_items`

## Testy manualne

```python
# Test 1: Energy duct
conv.convert_block('ThermalDynamics:thermaldynamics.Duct0', 0, nbt, pos)
# → thermal:energy_duct, success=True

# Test 2: Item duct + Servo
conv.convert_block('ThermalDynamics:thermaldynamics.Duct32', 0,
    {'attachment0': {'type': 1, 'metadata': 0, 'speed': 2}}, pos)
# → mekanism:basic_logistical_transporter, extra_items=1, warnings=2

# Test 3: Router — Item duct + attachment
events = convert_te_to_events({'id': 'thermaldynamics.ItemDuct', ...}, ...)
# → 2 events: main block + inventory_placeholder z attached_items
```

## Ograniczenia / znane problemy

1. **Ender Itemduct** — brak teleportacji bez fizycznego połączenia w Mekanism (elite = tylko throughput)
2. **Flux-Plated Itemduct** — brak combined item+RF transportu (ultimate = tylko itemy)
3. **Teleporter** — Viaduct nie miał częstotliwości; ustawiamy domyślną 0 (wymaga ręcznej konfiguracji)
4. **Załączniki** — w inventory_placeholder itemy z nieznanych modów stają się `minecraft:paper` tokenami (zachowane oryginalne NBT w tagu)
5. **Facades/covery** — tracone bez zrzutu (tylko warning)

## Następne kroki (Zadanie 4)

Zgodnie z planem (`docs/PLAN.md`):

**Zadanie 4: Sprawdzenie pokrycia dla stref głównej mapy**

- Uruchomić `analyze_thermal_dynamics.py` na całej mapie (`mapa_1710/region/`)
- Sprawdzić czy wszystkie znalezione bloki TD mają mapowania w konwerterze
- Zweryfikować czy załączniki są poprawnie wykrywane w rzeczywistych danych NBT z mapy
- Sprawdzić czy braki (Structuralduct) występują na mapie i w jakiej ilości

---

**Status:** ✅ Zadanie 3 ukończone — konwerter zintegrowany z routerem — gotowe do przeglądu i akceptacji  
**Data:** 2026-05-19  
**Agent:** AI Konwersji Thermal Dynamics
