# Czesc 1 - analiza funkcjonalnosci i najlepszych zamiennikow 1.18.2

Data: 2026-05-18

Pliki wynikowe:
- Arkusz: `docs/sprawdzenie_codex/cz1_funkcjonalnosci_mapowanie_1182_2026-05-18.xlsx`
- Dane skanu playerdata/moddata: `docs/sprawdzenie_codex/cz1_playerdata_moddata_scan_2026-05-18.json`

## Wniosek glowny

Dla czesci 1 najlepsze zamienniki sa miejscami inne niz w starym `cz1.md`:

- **Armourer's Workshop**: najlepszym celem jest **Armourer's Workshop 1.18.2**, nie Cosmetic Armor Reworked. Cosmetic Armor jest tylko fallbackiem dla samego noszenia drugiego pancerza i nie zachowuje systemu skinow, bibliotek ani warsztatow.
- **Better Storage**: jako domyslny cel storage lepszy jest **Sophisticated Storage** niz samo Iron Chests, bo lepiej pokrywa modulowy storage i upgrade'y. Iron Chests zostaje dobrym prostym fallbackiem dla reinforced chest.
- **Backpacks (Eydamos)**: **Sophisticated Backpacks** pozostaje najlepszym celem, szczegolnie ze lokalnie jest juz w paczce 1.18.2. Traveler's Backpack jest alternatywa gameplayowa, ale gorsza jako masowy importer danych.
- **Treecapitator**: **FallingTree** najlepiej odtwarza efekt sciecia calego drzewa. **HT's TreeChop** jest ciekawszy balansowo, ale mniej wierny Treecapitator.
- **Baubles**: **Curios API** jest poprawnym celem API. Same itemy z bauble slots trzeba mapowac per-mod.
- **AE2**: najlepszym celem pozostaje **AE2 11.x**. Dodatki typu AE2 Things moga poprawic wygode, ale nie sa zamiennikiem core migracji.

## Kontekst mapy 5GB

Nie ladowalem calej mapy do pamieci. Uzylem istniejacych raportow oraz lekkiego skanu NBT playerdata/moddata:

| Obszar | Wynik |
|---|---:|
| Pliki regionow `.mca` | 1195 |
| AE2-like TileEntities globalnie | 7925 |
| Regiony z AE2-like TE | 555 |
| AE2-like TE w zdefiniowanych strefach | 2473 |
| AE2-like TE poza strefami | 5452 |
| Better Storage TE/bloki w skanie stref | 8396 |
| Pliki `playerdata` przeskanowane | 911 |
| Trafienia `armour/backpack/bauble/appeng/betterstorage` w playerdata | 2420 |
| Pliki `mapa_1710/backpacks` | 1583 |
| Pliki `mapa_1710/AE2` | 3571 |

Najwazniejsze liczby z mapy:

- AE2: `BlockCableBus=3704`, `BlockCraftingUnit=1162`, `BlockCraftingStorage=833`, `BlockSkyChest=776`, `BlockMolecularAssembler=433`.
- Better Storage w strefach: `{'container.betterstorage.armorStand': 2, 'container.betterstorage.reinforcedLocker': 4797, 'container.betterstorage.reinforcedChest': 3414, 'container.betterstorage.locker': 10, 'container.betterstorage.backpack': 19, 'container.betterstorage.craftingStation': 24, 'container.betterstorage.thaumiumChest': 78, 'container.betterstorage.thaumcraftBackpack': 2, 'container.betterstorage.crate': 50}`.
- Armourer's Workshop w playerdata: `{'armourers:chest': 115, 'armourers:head': 110, 'armourers:legs': 80, 'armourers:block': 65, 'armourers:feet': 58, 'armourers:sword': 23, 'armourers:wings': 6, 'armourers:outfit': 6, 'armourers:bow': 5, 'armourers:pickaxe': 2, 'armourers:shovel': 1}`.

## Rekomendowana kolejnosc pracy

1. Poprawic dokument `cz1.md` dla Armourer's Workshop.
2. AE2: dopiac CableBus/parts, storage cells, crafting i P2P/quantum, bo to najwiekszy wolumen i najwieksze ryzyko rozpadania sie baz.
3. Better Storage: przenosic inventory do Sophisticated Storage/Iron Chests; locki i security traktowac jako osobny, stratny etap.
4. Backpacks: napisac importer `mapa_1710/backpacks` oraz skan plecakow w playerdata/EnderItems.
5. Armourer's Workshop: osobny exporter/importer skinow i slotow gracza. Bloki warsztatowe mapowac dopiero po sprawdzeniu registry/TE 3.x.

## Uwagi o arkuszu

Arkusz ma cztery zakladki:

- `Funkcjonalnosci_cz1` - wszystkie funkcje z czesci 1 rozbite na praktyczne wiersze migracji.
- `Kontekst_mapy` - liczby i slady z mapy/projektu.
- `Rekomendacje` - priorytety zmian.
- `Zrodla` - lokalne i publiczne zrodla uzyte do decyzji.
