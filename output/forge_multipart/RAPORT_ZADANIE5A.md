# Raport: ForgeMultipart/CB Multipart — Zadanie 5A

## Cel
Wykonanie testowej mapy Minecraft 1.7.10 z wszystkimi blokami i TileEntity ForgeMultipart, a następnie konwersja tych danych przy użyciu implementowanego konwertera.

## Testowa mapa 1.7.10

### Lokalizacja
`test_scenarios/forge_multipart_task5a/1710_test_world/`

### Metoda tworzenia
Mapa została wygenerowana za pomocą **Kotlin Hephaistos Worker** (zgodnie ze skillem `skills/mca-sections`).
Zastosowano patch JSON (`forge_multipart_patch.json`) z 30 operacjami (15 bloków + 15 TE).

### Wstawione elementy

| Pozycja (x,y,z) | Block ID | TE ID | Part(y) w TE |
|-----------------|----------|-------|--------------|
| (0,64,0) | 256 | savedMultipart | `mcr_face` |
| (1,64,0) | 256 | savedMultipart | `mcr_edge` |
| (2,64,0) | 256 | savedMultipart | `mcr_corner` |
| (3,64,0) | 256 | savedMultipart | `mcr_post` |
| (4,64,0) | 256 | savedMultipart | `mcr_hollow` |
| (0,64,1) | 256 | savedMultipart | `mc_torch` |
| (1,64,1) | 256 | savedMultipart | `mc_lever` |
| (2,64,1) | 256 | savedMultipart | `mc_button` |
| (3,64,1) | 256 | savedMultipart | `mc_redtorch` |
| (0,64,2) | 256 | savedMultipart | `mcr_face` + `mc_torch` (2 part-y) |
| (1,64,2) | 256 | savedMultipart | `mcr_edge` + `mcr_post` (2 part-y) |
| (2,64,2) | 256 | savedMultipart | `mcr_corner` + `mcr_face` (2 part-y) |
| (3,64,2) | 256 | savedMultipart | `mcr_hollow` + `mcr_edge` (2 part-y) |
| (0,65,0) | 256 | savedMultipart | `mcr_cnr` (alias `mcr_corner`) |
| (1,65,0) | 256 | savedMultipart | `mcr_edge` + `mcr_edge` (ten sam part 2x) |

**Podsumowanie pokrycia:**
- 5 mikrobloków: face, edge, corner, post, hollow
- 4 vanilla parts: torch, lever, button, redstone_torch
- 5 kombinacji wielu partów w jednym TE
- 1 alias (`mcr_cnr` -> `mcr_corner`)
- 1 edge case (podwójny ten sam part)

## Konwersja

### Skrypt
`src/converters/forge_multipart/convert_test_map.py`

### Wyniki
```
Przetworzono: 15
Skonwertowano: 15
Bledy: 0
```

### Mapowanie part IDs (1.7.10 -> 1.18.2)

| Oryginał | Po konwersji | Typ |
|----------|--------------|-----|
| `mcr_face` | `microblockcbe:face` | mikroblok |
| `mcr_edge` | `microblockcbe:edge` | mikroblok |
| `mcr_corner` | `microblockcbe:corner` | mikroblok |
| `mcr_post` | `microblockcbe:post` | mikroblok |
| `mcr_hollow` | `microblockcbe:hollow` | mikroblok |
| `mcr_cnr` | `microblockcbe:corner` | alias mikrobloku |
| `mc_torch` | `cb_multipart:torch` | vanilla part |
| `mc_lever` | `cb_multipart:lever` | vanilla part |
| `mc_button` | `cb_multipart:button` | vanilla part |
| `mc_redtorch` | `cb_multipart:redstone_torch` | vanilla part |

## Weryfikacja symulacji 1.18.2

### Skrypt
`src/converters/forge_multipart/verify_task5a.py`

### Metoda
Dla każdego przekonwertowanego eventu:
1. Załadowano NBT 1.18.2 do symulacji `TileMultipart.load()`
2. Sprawdzono czy liczba zdeserializowanych partów zgadza się z oryginałem

### Wyniki
```
Weryfikacja 15 eventow konwersji...
Wyniki: OK=15, FAIL=0 / 15
```

**100% pokrycia** — wszystkie przekonwertowane TileEntity poprawnie przechodzą deserializację w symulacji 1.18.2.

## Pliki wynikowe

| Plik | Opis |
|------|------|
| `test_scenarios/forge_multipart_task5a/1710_test_world/` | Testowa mapa 1.7.10 |
| `test_scenarios/forge_multipart_task5a/forge_multipart_patch.json` | Patch JSON dla Kotlin workera |
| `output/forge_multipart/task5a_conversion_result.json` | Wyniki konwersji (15 eventów) |
| `output/forge_multipart/task5a_verification.json` | Raport weryfikacji 1.18.2 |
| `output/forge_multipart/RAPORT_ZADANIE5A.md` | Ten raport |

## Wnioski

1. Konwerter ForgeMultipart poprawnie obsługuje wszystkie podstawowe typy partów (mikrobloki + vanilla).
2. Kombinacje wielu partów w jednym TE są poprawnie konwertowane.
3. Alias `mcr_cnr` -> `microblockcbe:corner` działa prawidłowo.
4. Symulacja 1.18.2 akceptuje wszystkie przekonwertowane NBT bez błędów.
5. Brak błędów konwersji na kontrolowanej testowej mapie.

## Otwarte kwestie

- `pr_cagelamp2` (ProjectRed cage lamp) — poza zakresem ForgeMultipart, do obsługi w konwerterze ProjectRed.
- Integracja z routerem głównym — router obecnie kieruje `savedMultipart` do `projectred`, nie `forgemultipart`. Wymaga decyzji architektonicznej czy ProjectRed ma obsługiwać wszystkie multiparty, czy tylko swoje.
