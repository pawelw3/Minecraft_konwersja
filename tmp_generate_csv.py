import csv
import json

# Wczytaj dane z mapy
with open('tmp_te_summary.json', 'r') as f:
    te_summary = json.load(f)

# Przygotuj dane CSV
rows = []

# Nagłówki
headers = [
    'Mod 1.7.10',
    'Funkcjonalność',
    'Blok/TE/Item 1.7.10',
    'Liczba na mapie',
    'Zamiennik w dokumentacji',
    'Najlepszy zamiennik 1.18.2',
    'Wersja 1.18.2',
    'Uzasadnienie',
    'Złożoność konwersji',
    'Kategoria (A/B/C)'
]

# --- Applied Energistics 2 ---
ae2_items = [
    ('ME Network / Storage', 'BlockDrive / ME Chest', te_summary.get('Applied Energistics 2', []), 'AE2 11.7.6', 'A'),
    ('Autocrafting', 'BlockMolecularAssembler / BlockCraftingUnit', [], 'AE2 11.7.6', 'A'),
    ('P2P Tunnels', 'BlockP2P (w kablach)', [], 'AE2 11.7.6', 'A'),
    ('Energy Storage', 'BlockDenseEnergyCell / BlockEnergyCell', [], 'AE2 11.7.6', 'A'),
    ('Import/Export', 'BlockInterface / BlockIOPort', [], 'AE2 11.7.6', 'A'),
    ('Spatial IO', 'BlockSpatialPylon / BlockSpatialIOPort', [], 'AE2 11.7.6', 'A'),
    ('Kable / części', 'BlockCableBus', [], 'AE2 11.7.6', 'A'),
]
for func, block, items, ver, cat in ae2_items:
    count = sum(i['count'] for i in items if i['te'] in block.split(' / ')) if items else 0
    rows.append([
        'Applied Energistics 2',
        func,
        block,
        count,
        'Applied Energistics 2',
        'Applied Energistics 2',
        ver,
        'Ten sam mod, wymaga remapu ID i NBT (storage celli, patterns, kanały)',
        'Wysoka',
        cat
    ])

# --- Armourer's Workshop ---
aw_items = te_summary.get('Armourer\'s Workshop', [])
aw_count = sum(i['count'] for i in aw_items)
rows.append([
    'Armourer\'s Workshop',
    'Skinny pancerza/broni/bloków',
    'te.skinnable / te.skinnableChild / te.mannequin / te.armourLibrary / te.globalSkinLibrary / te.skinningTable / te.hologramProjector / te.colourMixer / te.dyeTable',
    aw_count,
    'Cosmetic Armor Reworked (cz1.md - BŁĄD: brak wersji)',
    'Armourer\'s Workshop 3.2.7-beta',
    '1.18.2 Forge',
    'JEST oficjalny port na 1.18.2! Dokumentacja cz1.md jest nieaktualna. NBT skinów może wymagać migracji formatu (0.48.5 → 3.x).',
    'Średnia',
    'A'
])

# --- Backpacks (Eydamos) ---
rows.append([
    'Backpacks (Eydamos)',
    'Plecaki (Small/Middle/Big/Ender)',
    'Itemy (brak TE na mapie)',
    0,
    'Sophisticated Backpacks / Traveler\'s Backpack',
    'Sophisticated Backpacks',
    '1.18.2 Forge',
    'Najpopularniejszy zamiennik, integracja z Curios, system upgrade\'ów. NBT plecaków nieprzenośne — wypakować przed konwersją.',
    'Niska (itemy)',
    'B'
])

# --- Baubles ---
rows.append([
    'Baubles',
    'Sloty akcesoriów (amulet, belt, ring)',
    'API (brak bloków)',
    0,
    'Curios API',
    'Curios API',
    '1.18.2 Forge',
    'Bezpośredni odpowiednik slotów. Itemy "bauble" z innych modów wymagają per-mod konwersji.',
    'Niska',
    'C'
])

# --- Better Storage ---
bs_items = te_summary.get('Better Storage', [])
bs_count = sum(i['count'] for i in bs_items)
rows.append([
    'Better Storage',
    'Reinforced Chests / Lockers / Storage Crate / Cardboard Box',
    'container.betterstorage.reinforcedChest / reinforcedLocker / crate / thaumiumChest / locker / armorStand / craftingStation / backpack',
    bs_count,
    'Iron Chests + Sophisticated Storage + Packing Tape',
    'Sophisticated Storage (chests/barrels/shulkers + upgrades) + Iron Chests',
    '1.18.2 Forge',
    'Sophisticated Storage oferuje najbliższy poziom funkcjonalności (upgrade\'y, sortowanie). Iron Chests jako prostsza alternatywa. Cardboard Box → Carry On / Packing Tape.',
    'Średnia',
    'B'
])

# --- bspkrsCore / AsieLib ---
rows.append([
    'bspkrsCore',
    'Biblioteka dependency',
    'Brak bloków/TE',
    0,
    'Brak (ignoruj)',
    'Brak (ignoruj)',
    '-',
    'Tylko biblioteka dla Treecapitator. Nie zostawia bloków.',
    'Brak',
    'C'
])
rows.append([
    'AsieLib',
    'Biblioteka dependency',
    'Brak bloków/TE',
    0,
    'Brak (ignoruj)',
    'Brak (ignoruj)',
    '-',
    'Tylko biblioteka dla Statues (starego). Nowy Statues (ShyNieke) nie wymaga.',
    'Brak',
    'C'
])

# --- Treecapitator ---
rows.append([
    'Treecapitator',
    'Ścinanie całych drzew',
    'Brak bloków/TE (modyfikuje logi)',
    0,
    'FallingTree',
    'FallingTree',
    '1.18.2 Forge',
    'Ten sam efekt — zniszczenie 1 loga = spadnie całe drzewo. Brak bloków do konwersji.',
    'Brak',
    'C'
])

with open('docs/sprawdzenie_kimi/funkcjonalnosci_cz1_najlepsze_zamienniki.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(headers)
    writer.writerows(rows)

print(f'Zapisano {len(rows)} wierszy do CSV.')
