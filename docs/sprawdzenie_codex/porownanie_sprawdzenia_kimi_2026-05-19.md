# Porownanie sprawdzenia Kimi z analiza Codex

Data: 2026-05-19  
Zakres: `docs/sprawdzenie_kimi/` vs `docs/sprawdzenie_codex/`  
Wynik: moje sprawdzenie wymaga malego uzupelnienia, ale nie wymaga zmiany glownych decyzji dla Railcraft/Growthcraft.

## Werdykt krotki

Kimi potwierdza wiekszosc korekt, ktore sa juz w raportach Codex: port Armourer's Workshop 1.18.2, port MrCrayfish Furniture, Placeable Items jako mod do konwersji, CustomNPCs jako realnie uzyte dekoracje, K-Turrets jako lepszy cel dla OMT, hybrydowe Extra Utilities i koniecznosc osobnego skanu encji Traincraft/Flan's.

Do uzupelnienia po Kimi:

1. **Carpenter's Blocks / CuttableBlocks** - Kimi slusznie zauwazyl, ze w repo sa juz gotowe JAR-y i zrodla `CuttableBlocks`, wiec nie nalezy pisac w dokumentach, ze wlasny mod jest dopiero planowany. To nie zmienia faktu, ze pierwszym celem nadal powinien byc `FramedBlocks`, ale `CuttableBlocks-1.0.0_with_collapsible.jar` powinien byc formalnie wpisany jako lokalny fallback dla Collapsible/niestandardowych ksztaltow.
2. **LISTA_KONWERSJI_MODOW.md: Better Storage/JABBA** - Kimi trafnie wskazuje blad redakcyjny: Better Storage i JABBA to osobne mody. W raporcie Codex cz1 mapowanie Better Storage jest poprawne, ale glowna lista projektu nadal miesza nazewnictwo.
3. **LISTA_KONWERSJI_MODOW.md: BiblioCraft** - Kimi trafnie wskazuje duplikat/niejednoznaczna klasyfikacje BiblioCraft w glownej liscie. Raport Codex cz2 juz rekomenduje split funkcjonalny, ale dokument zrodlowy warto uporzadkowac.
4. **Priorytet implementacyjny** - w raporcie Codex warto dopisac jawnie, ze `CuttableBlocks` nalezy przetestowac razem z `FramedBlocks`, zamiast zostawiac go jako abstrakcyjny "custom mod".

Nie zmieniam po Kimi:

1. **Railcraft Reborn jako cel 1.18.2** - teza Kimi, ze Railcraft Reborn 5.x jest dobrym bezposrednim celem dla strict 1.18.2, jest obecnie za mocna. Publiczny CurseForge pokazuje wersje gry 1.20.1/1.21.x, a lokalne repo w `mod_src/118/actual_src/1.18.2/RailcraftReborn/repo/gradle.properties` ma `minecraft_version=1.21.1`. Dla twardego targetu 1.18.2 zostaje kierunek z raportu Codex: Create/Steam'n'Rails/Little Logistics + IE/Mekanism/Thermal, chyba ze projekt zmieni target na 1.20.1/1.21.x.
2. **Growthcraft CE jako pewny port 1.18.2** - Kimi traktuje Growthcraft CE jako najlepszy target A/B. Oficjalne pliki CurseForge pokazuja 1.16.5, 1.19.4 i 1.20.1, ale nie stabilne 1.18.2. Istnienie repo `Growthcraft-1.18` na GitHub nie wystarcza jako produkcyjny cel konwersji mapy. Dla 1.18.2 zostaje decyzja Codex: Farmer's Delight + Brewin' and Chewin' + Productive Bees/Croptopia per funkcja.
3. **Enchanting Plus** - Kimi preferuje Apotheosis jako glowny zamiennik. Codex zostawia `Enchanting Infuser` jako lepszy zamiennik konkretnej funkcji Enchanting Plus, bo chodzi o kontrolowany wybor enchantow w pojedynczym bloku. `Apotheosis` moze byc globalnym overhaulem paczki, ale nie powinien zastapic prostego mapowania stolika.
4. **Liczby TE Kimi** - Kimi operuje innym/lzejszym skanem i mniejszymi licznikami, np. `ForgeMultipart` 278k vs Codex 798105, `Railcraft` 23203 vs Codex 85818, `Thaumcraft` 19187 vs Codex 118387. Do priorytetow konwersji nalezy dalej uzywac celowanych skanow Codex, bo sa zapisane w JSON-ach i raportuja 2 447 396 Tile Entities w regionach.

## Tabela decyzji

| Temat | Kimi | Status po weryfikacji | Wplyw na sprawdzenie Codex |
|---|---|---|---|
| Armourer's Workshop | Jest port 1.18.2 | Potwierdzone | Juz uwzglednione w cz1 |
| MrCrayfish Furniture | Jest port 1.18.2 | Potwierdzone | Juz uwzglednione w cz4 |
| Placeable Items | Nie ignorowac | Potwierdzone | Juz uwzglednione w cz4 |
| CustomNPCs | Nie ignorowac, dekoracje realnie uzyte | Potwierdzone | Juz uwzglednione w cz2 |
| Open Modular Turrets | K-Turrets > samo IE | Potwierdzone | Juz uwzglednione w cz4 |
| Carpenter's Blocks | CuttableBlocks juz istnieje | Potwierdzone lokalnie | Uzupelnic: dodac jako gotowy lokalny fallback |
| Better Storage/JABBA | Nazewnictwo w glownej liscie bledne | Potwierdzone w `docs/LISTA_KONWERSJI_MODOW.md` | Uzupelnic dokumenty glowne, arkusz Codex bez zmiany |
| BiblioCraft | Duplikat/niejasna klasyfikacja | Potwierdzone w `docs/LISTA_KONWERSJI_MODOW.md` | Uzupelnic dokumenty glowne, arkusz Codex bez zmiany |
| Railcraft Reborn | Traktowac jako port 1.18.2 | Nie potwierdzone dla strict 1.18.2 | Nie zmieniac decyzji Codex |
| Growthcraft CE | Traktowac jako port 1.18.2 | Nie potwierdzone jako stabilny plik 1.18.2 | Nie zmieniac decyzji Codex |
| Enchanting Plus | Apotheosis jako glowny | Dyskusyjne | Zostawic Enchanting Infuser jako funkcjonalnie blizszy cel |

## Lokalna weryfikacja CuttableBlocks

Znalezione pliki:

| Plik | Wniosek |
|---|---|
| `CuttableBlocks-1.0.0.jar` | gotowy JAR w katalogu glownym |
| `CuttableBlocks-1.0.0_with_collapsible.jar` | szczegolnie wazny wariant dla Collapsible Block |
| `new_mod_trial/src/main/java/com/cuttableblocks/...` | zrodla lokalnego moda |
| `new_mod_trial/build/libs/CuttableBlocks-1.0.0.jar` | wynik lokalnego builda |

Rekomendacja: traktowac `CuttableBlocks` jako istniejacy lokalny komponent ratunkowy, ale nie jako zamiennik calych Carpenter's Blocks. Dla masowych camo blockow nadal najlepszy pierwszy target to `FramedBlocks`; `CuttableBlocks` powinien wejsc tam, gdzie FramedBlocks nie przenosi ksztaltu lub Collapsible zachowania.

## Zrodla

- Kimi: `docs/sprawdzenie_kimi/analiza_konwersji_1710_1182_weryfikacja.md`
- Kimi: `docs/sprawdzenie_kimi/analiza_funkcjonalnosci_w_kontekscie_mapy_5gb.md`
- Kimi: `docs/sprawdzenie_kimi/funkcjonalnosci_1710_1182_najlepsze_zamienniki.csv`
- Codex: `docs/sprawdzenie_codex/cz1-5_funkcjonalnosci_mapowanie_1182_2026-05-18.xlsx`
- Codex: `docs/sprawdzenie_codex/cz2_analiza_funkcjonalnosci_i_zamiennikow_2026-05-18.md`
- Codex: `docs/sprawdzenie_codex/cz3_analiza_funkcjonalnosci_i_zamiennikow_2026-05-18.md`
- Codex: `docs/sprawdzenie_codex/cz4_analiza_funkcjonalnosci_i_zamiennikow_2026-05-18.md`
- CurseForge Railcraft Reborn: https://www.curseforge.com/minecraft/mc-mods/railcraft-reborn
- CurseForge Growthcraft CE: https://www.curseforge.com/minecraft/mc-mods/growthcraft-community-edition/files/all
- CurseForge Armourer's Workshop 1.18.2: https://www.curseforge.com/minecraft/mc-mods/armourers-workshop/files/7165517
- K-Turrets 1.18.2: https://www.curseforge.com/minecraft/mc-mods/k-turrets/files/4861825
