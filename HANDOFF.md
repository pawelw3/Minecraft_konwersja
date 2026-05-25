# Handoff: ForgeMultipart i Thermal Dynamics - korekta routera/NBT

## Podsumowanie sesji
Naprawiono realne błędy integracyjne w skryptach konwersji ForgeMultipart i Thermal Dynamics. Lokalne konwertery przechodziły testy, ale globalny router kierował część danych z mapy do złej ścieżki albo produkował niepełne eventy.

## Ukończono
- [x] `savedMultipart` z mikroblokami (`mcr_face`, `mcr_edge`, itd.) trafia teraz do `ForgeMultipartConverter`, nie do ProjectRed.
- [x] `savedMultipart` zawierający wyłącznie party ProjectRed nadal może iść specjalistyczną ścieżką ProjectRed.
- [x] Thermal Dynamics używa domyślnego metadata z `TE_ID_TO_BLOCK` dla konkretnych TE, np. `ItemDuctEnder` i `FluidDuctSuper`.
- [x] NBT Thermal Dynamics dla `set_block_entity` dostaje pole `id`.
- [x] Dodano testy regresyjne dla powyższych przypadków.

## Zmodyfikowane pliki
- `src/converters/router.py`
- `src/converters/thermal_dynamics/mappings.py`
- `src/converters/thermal_dynamics/thermal_dynamics_converter.py`
- `src/converters/thermal_dynamics/nbt_converters/__init__.py`
- `src/converters/forge_multipart/tests/test_forge_multipart_converter.py`

## Nowe pliki
- `src/converters/thermal_dynamics/test_thermal_dynamics_regressions.py`

## Weryfikacja
```powershell
python -m py_compile src\converters\router.py src\converters\thermal_dynamics\mappings.py src\converters\thermal_dynamics\thermal_dynamics_converter.py src\converters\thermal_dynamics\nbt_converters\__init__.py src\converters\thermal_dynamics\test_thermal_dynamics_regressions.py
$env:PYTHONPATH='src'; python -m pytest src\converters\forge_multipart\tests src\converters\thermal_dynamics\test_thermal_dynamics_regressions.py -q
```
Wynik: `20 passed`.

Smoke:
- `savedMultipart` + `mcr_face` -> `cb_multipart:multipart` + `cb_multipart:saved_multipart`
- `thermaldynamics.ItemDuctEnder` -> `mekanism:elite_logistical_transporter`
- `thermaldynamics.FluidDuctSuper` -> `thermal:fluid_duct_windowed`
- NBT TD zawiera `id`

## Następne kroki
1. Uruchomić próbkę konwersji realnych chunków zawierających ForgeMultipart i Thermal Dynamics.
2. Sprawdzić na headless 1.18.2, czy docelowe BE ID Thermal/Mekanism są akceptowane przez mody.
3. Przy pełnej mapie logować mieszane `savedMultipart` z partami ProjectRed + mikroblokami, bo to wymaga decyzji czy ważniejsza jest rekonstrukcja PR czy zachowanie całego kontenera.
