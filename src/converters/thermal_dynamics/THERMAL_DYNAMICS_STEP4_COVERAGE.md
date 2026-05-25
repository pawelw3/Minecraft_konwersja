# Thermal Dynamics — Krok 4 (Pokrycie na mapie)

> Analiza rzeczywistych bloków Thermal Dynamics na mapie 1.7.10

## Wyniki

- **Próbkowane regiony:** 1195/1195
- **Regiony z TD:** 27
- **Sprawdzone chunki:** 664,972
- **Znalezione TE TD:** 13444

## Pokrycie konwersji

| Tile Entity ID | Liczba | Mapowanie | Uwagi |
|----------------|--------|-----------|-------|
| thermaldynamics.ItemDuct | 6518 | [OK] | ma załączniki, ma facady |
| thermaldynamics.FluxDuctSuperConductor | 5940 | [OK] | ma facady |
| thermaldynamics.ItemDuctEnder | 470 | [OK] | ma załączniki |
| thermaldynamics.FluidDuctSuper | 309 | [OK] | ma załączniki |
| thermaldynamics.FluidDuct | 171 | [OK] | ma załączniki, ma facady |
| thermaldynamics.FluxDuct | 34 | [OK] | - |
| thermaldynamics.FluidDuctFragile | 2 | [OK] | - |

## Podsumowanie

- **Zmapowane TE:** 13444/13444 (100%)
- **Niezmapowane TE:** 0
- **TE z załącznikami:** 367
- **TE z facadami:** 525

## Błędy (1)

- r.-10.2.mca: error: Error -5 while decompressing data: incomplete or truncated stream
