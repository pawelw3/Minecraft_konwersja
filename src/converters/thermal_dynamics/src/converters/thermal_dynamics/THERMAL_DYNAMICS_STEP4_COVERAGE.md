# Thermal Dynamics — Krok 4 (Pokrycie na mapie)

> Analiza rzeczywistych bloków Thermal Dynamics na mapie 1.7.10

## Wyniki

- **Próbkowane regiony:** 400/1195
- **Regiony z TD:** 11
- **Sprawdzone chunki:** 196,101
- **Znalezione TE TD:** 5967

## Pokrycie konwersji

| Tile Entity ID | Liczba | Mapowanie | Uwagi |
|----------------|--------|-----------|-------|
| thermaldynamics.ItemDuct | 3206 | [OK] | ma załączniki, ma facady |
| thermaldynamics.FluxDuctSuperConductor | 2480 | [OK] | ma facady |
| thermaldynamics.FluidDuctSuper | 225 | [OK] | ma załączniki |
| thermaldynamics.FluxDuct | 33 | [OK] | - |
| thermaldynamics.FluidDuct | 21 | [OK] | ma załączniki |
| thermaldynamics.FluidDuctFragile | 2 | [OK] | - |

## Podsumowanie

- **Zmapowane TE:** 5967/5967 (100%)
- **Niezmapowane TE:** 0
- **TE z załącznikami:** 135
- **TE z facadami:** 33

## Błędy (1)

- r.-10.2.mca: error: Error -5 while decompressing data: incomplete or truncated stream
