# Raport analizy ForgeMultipart na mapie 1.7.10

Przeskanowane regiony: `1195`
Znalezione unikalne TE ID: `1`

## Znalezione TileEntity ID

| TileEntity ID | Liczba | Przykładowe part-y |
|---------------|--------|-------------------|
| `savedMultipart` | 284323 | mcr_face(64), mc_torch(22), mcr_edge(18) |

## Analiza partów (wszystkie próbki)

| Part ID 1.7.10 | Liczba | Obsługiwany | Mapowanie 1.18.2 |
|----------------|--------|-------------|------------------|
| `mcr_face` | 64 | ✅ | `microblockcbe:face` |
| `mc_torch` | 22 | ✅ | `cb_multipart:torch` |
| `mcr_edge` | 18 | ✅ | `microblockcbe:edge` |
| `pr_cagelamp2` | 7 | ❌ | BRAK |
| `mcr_post` | 3 | ✅ | `microblockcbe:post` |
| `mcr_cnr` | 2 | ✅ | `microblockcbe:corner` |

## ⚠️ Nieobsługiwane part-y

Następujące part-y zostały znalezione na mapie ale NIE są obecnie mapowane:

- `pr_cagelamp2`

**Rekomendacja:** Rozszerzyć `PART_ID_1710_TO_1182` w `mappings.py` o powyższe ID.
