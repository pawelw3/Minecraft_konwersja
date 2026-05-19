"""
IC2 Block & Tile Entity Inventory (Zadanie 1)

Kompletna inwentaryzacja bloków i Tile Entities dodawanych przez
IndustrialCraft 2 (experimental 2.2.827) dla Minecraft 1.7.10.

Źródło: dekompilacja industrialcraft-2-2.2.827-experimental.jar
(vineflower) + analiza kodu źródłowego.
"""

# Format: block_id -> lista wariantów (metadata)
# Block ID to InternalName użyty w rejestracji Forge (prefiks "IC2:")

IC2_BLOCK_CATEGORIES = {
    "machines": "Maszyny przetwórcze i użytkowe (BlockMachine, BlockMachine2, BlockMachine3)",
    "generators": "Generatory energii (BlockGenerator)",
    "heat_generators": "Generatory ciepła (BlockHeatGenerator)",
    "kinetic_generators": "Generatory kinetyczne (BlockKineticGenerator)",
    "cables": "Kable i okablowanie (BlockCable)",
    "energy_storage": "Magazyny energii i transformatory (BlockElectric, BlockChargepad)",
    "reactors": "Bloki reaktora jądrowego",
    "personal": "Bloki personalne (BlockPersonal)",
    "decoration": "Bloki dekoracyjne i budowlane",
    "resources": "Rudy i zasoby naturalne",
    "fluid": "Bloki płynów",
    "other": "Pozostałe bloki specjalne",
}

# ============================================================
# MASZYNY (BlockMachine, BlockMachine2, BlockMachine3)
# ============================================================

IC2_MACHINES = {
    # BlockMachine (blockMachine) — meta 0-15
    "IC2:blockMachine": {
        0: {
            "name": "Machine Block",
            "te_class": None,
            "description": "Blok konstrukcyjny używany do craftingu maszyn. Brak TE.",
        },
        1: {
            "name": "Iron Furnace",
            "te_class": "TileEntityIronFurnace",
            "description": "Piec opalany paliwem stałym. Brak elektryczności.",
            "nbt_notes": "Dziedziczy po TileEntityInventory: Items/InvSlots, facing, active.",
        },
        2: {
            "name": "Electric Furnace",
            "te_class": "TileEntityElectricFurnace",
            "description": "Piec elektryczny. Szybszy od żelaznego, zużywa EU.",
            "nbt_notes": "TileEntityStandardMachine: progress (short), energy, input/output slots, upgrades.",
        },
        3: {
            "name": "Macerator",
            "te_class": "TileEntityMacerator",
            "description": "Kruszy rudy i itemy na proszki. Podstawowa maszyna przetwórcza.",
            "nbt_notes": "TileEntityStandardMachine: progress (short), energy, input/output slots, upgrades.",
        },
        4: {
            "name": "Extractor",
            "te_class": "TileEntityExtractor",
            "description": "Wyciąga surowce z itemów (np. gumę z klatek z żywicy).",
            "nbt_notes": "TileEntityStandardMachine: progress, energy, slots.",
        },
        5: {
            "name": "Compressor",
            "te_class": "TileEntityCompressor",
            "description": "Kompresuje itemy (np. proszek → płytę, komórki).",
            "nbt_notes": "TileEntityStandardMachine: progress, energy, slots.",
        },
        6: {
            "name": "Canning Machine",
            "te_class": "TileEntityCanner",
            "description": "Napełnia puszki i komórki płynami/substancjami.",
            "nbt_notes": "TileEntityStandardMachine: progress, energy, slots. Ma tryby pracy (Mode).",
        },
        7: {
            "name": "Miner",
            "te_class": "TileEntityMiner",
            "description": "Automatyczny górnik wiercący w dół i zbierający rudy.",
            "nbt_notes": "TileEntityElectricMachine: energy, facing, pipedrill, scanner (opcjonalnie).",
        },
        8: {
            "name": "Pump",
            "te_class": "TileEntityPump",
            "description": "Pompuje płyny z obszarów pod nim. Współpracuje z Minerem.",
            "nbt_notes": "TileEntityElectricMachine: energy, facing, zbiornik płynu.",
        },
        9: {
            "name": "Magnetizer",
            "te_class": "TileEntityMagnetizer",
            "description": "Magnetyzuje pręty żelazne w płot (szybki transport).",
            "nbt_notes": "TileEntityElectricMachine: energy, facing.",
        },
        10: {
            "name": "Electrolyzer",
            "te_class": "TileEntityElectrolyzer",
            "description": "Elektroliza wody → wodór/tlen (do reaktora i innych procesów).",
            "nbt_notes": "TileEntityElectricMachine: energy, zbiorniki, facing.",
        },
        11: {
            "name": "Recycler",
            "te_class": "TileEntityRecycler",
            "description": "Recykling itemów na Scrap. Losowy proces.",
            "nbt_notes": "TileEntityStandardMachine: progress, energy, slots.",
        },
        12: {
            "name": "Advanced Machine Block",
            "te_class": None,
            "description": "Zaawansowany blok konstrukcyjny. Brak TE.",
        },
        13: {
            "name": "Induction Furnace",
            "te_class": "TileEntityInduction",
            "description": "Szybki piec indukcyjny. Zużywa dużo EU, ma pasek ciepła (heat).",
            "nbt_notes": "TileEntityElectricMachine + heat (int). 2 sloty input, 2 output.",
        },
        14: {
            "name": "Mass Fabricator",
            "te_class": "TileEntityMatter",
            "description": "Produkuje UU-Matter z EU i Scrapu. End-game maszyna.",
            "nbt_notes": "TileEntityElectricMachine: energy (duże wartości), progress, scrapSlot.",
        },
        15: {
            "name": "Terraformer",
            "te_class": "TileEntityTerra",
            "description": "Zmienia biom terenu za pomocą blueprintów TFBP.",
            "nbt_notes": "TileEntityElectricMachine: energy, blueprint slot, zakres.",
        },
    },

    # BlockMachine2 (blockMachine2) — meta 0-15
    "IC2:blockMachine2": {
        0: {
            "name": "Teleporter",
            "te_class": "TileEntityTeleporter",
            "description": "Teleportuje gracza do innego teleportera. Bardzo energochłonny.",
            "nbt_notes": "TileEntityElectricMachine: energy, targetSet (bool), współrzędne celu.",
        },
        1: {
            "name": "Tesla Coil",
            "te_class": "TileEntityTesla",
            "description": "Atakuje pobliskich mobów/graczy wyładowaniami.",
            "nbt_notes": "TileEntityElectricMachine: energy, fireRate, range.",
        },
        2: {
            "name": "Crop-Matron",
            "te_class": "TileEntityCropmatron",
            "description": "Automatycznie nawadnia, nawozi i zabiera uprawy IC2.",
            "nbt_notes": "TileEntityElectricMachine: energy, zbiorniki płynów, sloty itemów.",
        },
        3: {
            "name": "Thermal Centrifuge",
            "te_class": "TileEntityCentrifuge",
            "description": "Wirówka termiczna do rozdziału mieszanin (np. Crushed Ore).",
            "nbt_notes": "TileEntityStandardMachine: progress, energy, heat.",
        },
        4: {
            "name": "Metal Former",
            "te_class": "TileEntityMetalFormer",
            "description": "Formuje metale (rolki, rurki, druty) w różnych trybach.",
            "nbt_notes": "TileEntityStandardMachine: progress, energy, mode (rolling/cutting/etc).",
        },
        5: {
            "name": "Ore Washing Plant",
            "te_class": "TileEntityOreWashing",
            "description": "Myje rudy → Purified Crushed Ore + dodatkowe produkty. Wymaga wody.",
            "nbt_notes": "TileEntityStandardMachine: progress, energy, zbiornik wody.",
        },
        6: {
            "name": "Pattern Storage",
            "te_class": "TileEntityPatternStorage",
            "description": "Przechowuje wzory skanów dla Replicatora.",
            "nbt_notes": "TileEntityElectricMachine: energy, contents (lista wzorów).",
        },
        7: {
            "name": "Scanner",
            "te_class": "TileEntityScanner",
            "description": "Skanuje itemy i zapisuje wzory do Pattern Storage.",
            "nbt_notes": "TileEntityElectricMachine: energy, progress, state.",
        },
        8: {
            "name": "Replicator",
            "te_class": "TileEntityReplicator",
            "description": "Replikuje itemy z UU-Matter na podstawie wzoru.",
            "nbt_notes": "TileEntityElectricMachine: energy, mode, pattern reference.",
        },
        9: {
            "name": "Solid Canner",
            "te_class": "TileEntitySolidCanner",
            "description": "Napełnia komórki stałymi substancjami.",
            "nbt_notes": "TileEntityStandardMachine: progress, energy, slots.",
        },
        10: {
            "name": "Fluid Bottler",
            "te_class": "TileEntityFluidBottler",
            "description": "Nalewa płyny do butelek/komórek.",
            "nbt_notes": "TileEntityStandardMachine: progress, energy, zbiornik płynu.",
        },
        11: {
            "name": "Advanced Miner",
            "te_class": "TileEntityAdvMiner",
            "description": "Zaawansowany górnik z trybami pracy i filtrowaniem.",
            "nbt_notes": "TileEntityElectricMachine: energy, mode, blacklist/whitelist, scanRange.",
        },
        12: {
            "name": "Liquid Heat Exchanger",
            "te_class": "TileEntityLiquidHeatExchanger",
            "description": "Wymiennik ciepła dla systemu cieplnego IC2.",
            "nbt_notes": "TileEntityLiquidTankElectricMachine: energy, zbiorniki, heat.",
        },
        13: {
            "name": "Fermenter",
            "te_class": "TileEntityFermenter",
            "description": "Fermentuje biomasę → biogaz.",
            "nbt_notes": "TileEntityStandardMachine: progress, energy, zbiorniki.",
        },
        14: {
            "name": "Fluid Regulator",
            "te_class": "TileEntityFluidRegulator",
            "description": "Reguluje przepływ płynów w rurach.",
            "nbt_notes": "TileEntityLiquidTankElectricMachine: energy, zbiornik, setting.",
        },
        15: {
            "name": "Condenser",
            "te_class": "TileEntityCondenser",
            "description": "Kondensuje parę z powrotem do wody.",
            "nbt_notes": "TileEntityLiquidTankElectricMachine: energy, zbiorniki.",
        },
    },

    # BlockMachine3 (blockMachine3) — meta 0-8
    "IC2:blockMachine3": {
        0: {
            "name": "Steam Generator",
            "te_class": "TileEntitySteamGenerator",
            "description": "Produkuje parę z wody i ciepła.",
            "nbt_notes": "TileEntityLiquidTankElectricMachine: energy, zbiorniki, temperatura.",
        },
        1: {
            "name": "Blast Furnace",
            "te_class": "TileEntityBlastFurnace",
            "description": "Wytapia stal (Refined Iron) z żelaza. Wymaga ciepła.",
            "nbt_notes": "TileEntityLiquidTankStandardMachine: progress, heat, zbiornik.",
        },
        2: {
            "name": "Block Cutting Machine",
            "te_class": "TileEntityBlockCutter",
            "description": "Tnie bloki na płytki. Wymaga ostrzy.",
            "nbt_notes": "TileEntityStandardMachine: progress, energy, slot ostrza.",
        },
        3: {
            "name": "Solar Distiller",
            "te_class": "TileEntitySolarDestiller",
            "description": "Destyluje wodę słoną/brudną → czysta woda (darmowa energia słoneczna).",
            "nbt_notes": "TileEntityLiquidTankInventory: zbiorniki, progress.",
        },
        4: {
            "name": "Fluid Distributor",
            "te_class": "TileEntityFluidDistributor",
            "description": "Rozdziela płyny na wiele stron.",
            "nbt_notes": "TileEntityLiquidTankInventory: zbiorniki, facing, tryby.",
        },
        5: {
            "name": "Sorting Machine",
            "te_class": "TileEntitySortingMachine",
            "description": "Sortuje itemy do różnych wyjść na podstawie filtrów.",
            "nbt_notes": "TileEntityInventory: slots, filtry, facing.",
        },
        6: {
            "name": "Item Buffer",
            "te_class": "TileEntityItemBuffer",
            "description": "Buforuje itemy między rurami/maszynami.",
            "nbt_notes": "TileEntityInventory: slots, facing.",
        },
        7: {
            "name": "Crop Harvester",
            "te_class": "TileEntityCropHavester",
            "description": "Automatycznie zbiera dojrzałe uprawy IC2.",
            "nbt_notes": "TileEntityElectricMachine: energy, range, slots.",
        },
        8: {
            "name": "Lathe",
            "te_class": "TileEntityLathe",
            "description": "Tokarka do obróbki metalu.",
            "nbt_notes": "TileEntityStandardMachine: progress, energy, slot.",
        },
    },
}

# ============================================================
# GENERATORY ENERGII (BlockGenerator)
# ============================================================

IC2_GENERATORS = {
    "IC2:blockGenerator": {
        0: {
            "name": "Generator",
            "te_class": "TileEntityGenerator",
            "description": "Podstawowy generator spalający paliwo stałe → EU.",
            "nbt_notes": "TileEntityBaseGenerator: fuel, energy, facing, active.",
        },
        1: {
            "name": "Geothermal Generator",
            "te_class": "TileEntityGeoGenerator",
            "description": "Generator geotermalny spalający lawę/komórki lawy.",
            "nbt_notes": "TileEntityBaseGenerator: fuel, energy, zbiornik lawy.",
        },
        2: {
            "name": "Water Mill",
            "te_class": "TileEntityWaterGenerator",
            "description": "Generuje EU z przepływu wody (darmowa, ale słaba energia).",
            "nbt_notes": "TileEntityBaseGenerator: energy, współczynnik wody.",
        },
        3: {
            "name": "Solar Panel",
            "te_class": "TileEntitySolarGenerator",
            "description": "Generuje EU w dzień (darmowa energia).",
            "nbt_notes": "TileEntityBaseGenerator: energy, sky visibility.",
        },
        4: {
            "name": "Wind Mill",
            "te_class": "TileEntityWindGenerator",
            "description": "Generuje EU z wiatru. Wyżej = więcej energii.",
            "nbt_notes": "TileEntityBaseGenerator: energy, rotor (opcjonalnie).",
        },
        5: {
            "name": "Nuclear Reactor",
            "te_class": "TileEntityNuclearReactorElectric",
            "description": "Generuje ogromne ilości EU z reakcji jądrowej. Wymaga chłodzenia.",
            "nbt_notes": "TileEntityNuclearReactorElectric: heat, energy, output, inventory (6x9 slots z komponentami reaktora).",
            "complexity": "CRITICAL",
        },
        6: {
            "name": "RT Generator",
            "te_class": "TileEntityRTGenerator",
            "description": "Radioizotopowy generator termoelektryczny. Długotrwałe, niskie EU.",
            "nbt_notes": "TileEntityBaseGenerator: fuel (RTG pellets), energy.",
        },
        7: {
            "name": "Semifluid Generator",
            "te_class": "TileEntitySemifluidGenerator",
            "description": "Spala półpłynne paliwa (biogaz, itp.).",
            "nbt_notes": "TileEntityBaseGenerator: fuel, energy, zbiornik.",
        },
        8: {
            "name": "Stirling Generator",
            "te_class": "TileEntityStirlingGenerator",
            "description": "Generator Stirlinga przetwarzający ciepło zewnętrzne na EU.",
            "nbt_notes": "TileEntityBaseGenerator: heat buffer, energy.",
        },
        9: {
            "name": "Kinetic Generator",
            "te_class": "TileEntityKineticGenerator",
            "description": "Konwertuje energię kinetyczną na EU.",
            "nbt_notes": "TileEntityBaseGenerator: kinetic input, energy.",
        },
    },
}

# ============================================================
# GENERATORY CIEPŁA (BlockHeatGenerator)
# ============================================================

IC2_HEAT_GENERATORS = {
    "IC2:blockHeatGenerator": {
        0: {
            "name": "Electric Heat Generator",
            "te_class": "TileEntityElectricHeatGenerator",
            "description": "Przetwarza EU na ciepło dla systemu cieplnego.",
            "nbt_notes": "TileEntityElectricMachine: energy, heat output.",
        },
        1: {
            "name": "Fluid Heat Generator",
            "te_class": "TileEntityFluidHeatGenerator",
            "description": "Generuje ciepło spalając płynne paliwa.",
            "nbt_notes": "TileEntityLiquidTankElectricMachine: energy, zbiornik, heat.",
        },
        2: {
            "name": "RT Heat Generator",
            "te_class": "TileEntityRTHeatGenerator",
            "description": "Radioizotopowy generator ciepła.",
            "nbt_notes": "TileEntityBaseHeatGenerator: fuel, heat.",
        },
        3: {
            "name": "Solid Heat Generator",
            "te_class": "TileEntitySolidHeatGenerator",
            "description": "Piec opalany paliwem stałym generujący ciepło.",
            "nbt_notes": "TileEntityBaseHeatGenerator: fuel, heat.",
        },
    },
}

# ============================================================
# GENERATORY KINETYCZNE (BlockKineticGenerator)
# ============================================================

IC2_KINETIC_GENERATORS = {
    "IC2:blockKineticGenerator": {
        0: {
            "name": "Electric Kinetic Generator",
            "te_class": "TileEntityElectricKineticGenerator",
            "description": "Przetwarza EU na energię kinetyczną.",
            "nbt_notes": "TileEntityElectricMachine: energy, kinetic output.",
        },
        1: {
            "name": "Manual Kinetic Generator",
            "te_class": "TileEntityManualKineticGenerator",
            "description": "Generuje energię kinetyczną z ręcznego kręcenia (prawy przycisk).",
            "nbt_notes": "Brak NBT poza standardowym.",
        },
        2: {
            "name": "Steam Kinetic Generator",
            "te_class": "TileEntitySteamKineticGenerator",
            "description": "Turbina parowa. Para → energia kinetyczna.",
            "nbt_notes": "TileEntityLiquidTankInventory: zbiornik pary, zużycie wirnika.",
        },
        3: {
            "name": "Stirling Kinetic Generator",
            "te_class": "TileEntityStirlingKineticGenerator",
            "description": "Silnik Stirlinga → energia kinetyczna.",
            "nbt_notes": "TileEntityBaseGenerator: heat, kinetic output.",
        },
        4: {
            "name": "Water Kinetic Generator",
            "te_class": "TileEntityWaterKineticGenerator",
            "description": "Generator wodny (turbina wodna).",
            "nbt_notes": "TileEntityKineticGenerator: water flow, rotor (opcjonalnie).",
        },
        5: {
            "name": "Wind Kinetic Generator",
            "te_class": "TileEntityWindKineticGenerator",
            "description": "Generator wiatrowy (turbina wiatrowa).",
            "nbt_notes": "TileEntityKineticGenerator: wind strength, rotor.",
        },
    },
}


# ============================================================
# KABLE (BlockCable)
# ============================================================
# Uwaga: BlockCable używa metadaty 0-13 (14 jest remapowane na 13).
# W konstruktorze meta>=13 jest inkrementowane do 14 dla insulated tin.

IC2_CABLES = {
    "IC2:blockCable": {
        0: {
            "name": "Insulated Copper Cable",
            "te_class": "TileEntityCable",
            "te_ctor_args": {"cableType": 0},
            "description": "Kabel miedziany izolowany. 32 EU/t (LV).",
            "nbt_notes": "TileEntityCable: cableType, color, foamed, foamColor, retexture.",
        },
        1: {
            "name": "Copper Cable",
            "te_class": "TileEntityCable",
            "te_ctor_args": {"cableType": 1},
            "description": "Kabel miedziany nieizolowany. 32 EU/t (LV). Porażenie prądem!",
            "nbt_notes": "TileEntityCable: cableType, color, foamed, foamColor, retexture.",
        },
        2: {
            "name": "Gold Cable",
            "te_class": "TileEntityCable",
            "te_ctor_args": {"cableType": 2},
            "description": "Kabel złoty nieizolowany. 128 EU/t (MV). Porażenie!",
            "nbt_notes": "TileEntityCable: cableType, color, foamed, foamColor, retexture.",
        },
        3: {
            "name": "Insulated Gold Cable",
            "te_class": "TileEntityCable",
            "te_ctor_args": {"cableType": 3},
            "description": "Kabel złoty izolowany. 128 EU/t (MV).",
            "nbt_notes": "TileEntityCable: cableType, color, foamed, foamColor, retexture.",
        },
        4: {
            "name": "Double Insulated Gold Cable",
            "te_class": "TileEntityCable",
            "te_ctor_args": {"cableType": 4},
            "description": "Kabel złoty podwójnie izolowany. 128 EU/t (MV).",
            "nbt_notes": "TileEntityCable: cableType, color, foamed, foamColor, retexture.",
        },
        5: {
            "name": "Iron Cable (HV)",
            "te_class": "TileEntityCable",
            "te_ctor_args": {"cableType": 5},
            "description": "Kabel żelazny nieizolowany. 2048 EU/t (HV). Porażenie!",
            "nbt_notes": "TileEntityCable: cableType, color, foamed, foamColor, retexture.",
        },
        6: {
            "name": "Insulated Iron Cable",
            "te_class": "TileEntityCable",
            "te_ctor_args": {"cableType": 6},
            "description": "Kabel żelazny izolowany. 2048 EU/t (HV).",
            "nbt_notes": "TileEntityCable: cableType, color, foamed, foamColor, retexture.",
        },
        7: {
            "name": "Double Insulated Iron Cable",
            "te_class": "TileEntityCable",
            "te_ctor_args": {"cableType": 7},
            "description": "Kabel żelazny podwójnie izolowany. 2048 EU/t (HV).",
            "nbt_notes": "TileEntityCable: cableType, color, foamed, foamColor, retexture.",
        },
        8: {
            "name": "Triple Insulated Iron Cable",
            "te_class": "TileEntityCable",
            "te_ctor_args": {"cableType": 8},
            "description": "Kabel żelazny potrójnie izolowany. 2048 EU/t (HV).",
            "nbt_notes": "TileEntityCable: cableType, color, foamed, foamColor, retexture.",
        },
        9: {
            "name": "Glass Fibre Cable",
            "te_class": "TileEntityCable",
            "te_ctor_args": {"cableType": 9},
            "description": "Światłowód. 8192 EU/t (EV). Bez strat na dystansie.",
            "nbt_notes": "TileEntityCable: cableType, color, foamed, foamColor, retexture.",
        },
        10: {
            "name": "Tin Cable",
            "te_class": "TileEntityCable",
            "te_ctor_args": {"cableType": 10},
            "description": "Kabel cynowy. 5 EU/t (Ultra-LV). Używany w solarnych/mikro.",
            "nbt_notes": "TileEntityCable: cableType, color, foamed, foamColor, retexture.",
        },
        11: {
            "name": "Detector Cable",
            "te_class": "TileEntityCableDetector",
            "te_ctor_args": {"cableType": 11},
            "description": "Kabel detekcyjny. Emituje sygnał redstone przy przepływie EU.",
            "nbt_notes": "TileEntityCableDetector: cableType, energy stats, redstone.",
        },
        12: {
            "name": "Splitter Cable",
            "te_class": "TileEntityCableSplitter",
            "te_ctor_args": {"cableType": 12},
            "description": "Kabel rozdzielający. Może być przełączany redstone.",
            "nbt_notes": "TileEntityCableSplitter: cableType, active (bool).",
        },
        13: {
            "name": "Insulated Tin Cable",
            "te_class": "TileEntityCable",
            "te_ctor_args": {"cableType": 13},
            "description": "Kabel cynowy izolowany. 5 EU/t (Ultra-LV).",
            "nbt_notes": "TileEntityCable: cableType, color, foamed, foamColor, retexture.",
        },
    },
}

# ============================================================
# MAGAZYNY ENERGII I TRANSFORMATORY (BlockElectric)
# ============================================================

IC2_ENERGY_STORAGE = {
    "IC2:blockElectric": {
        0: {
            "name": "BatBox",
            "te_class": "TileEntityElectricBatBox",
            "description": "Podstawowy magazyn energii. 40 000 EU, 32 EU/t.",
            "nbt_notes": "TileEntityElectricBlock: energy (double), redstoneMode (byte), active.",
            "eu_capacity": 40000,
            "eu_tier": 1,  # LV
        },
        1: {
            "name": "MFE",
            "te_class": "TileEntityElectricMFE",
            "description": "Magazyn energii średniej klasy. 4 000 000 EU, 512 EU/t.",
            "nbt_notes": "TileEntityElectricBlock: energy (double), redstoneMode (byte), active.",
            "eu_capacity": 4000000,
            "eu_tier": 3,  # HV
        },
        2: {
            "name": "MFSU",
            "te_class": "TileEntityElectricMFSU",
            "description": "Magazyn energii wysokiej klasy. 40 000 000 EU, 2048 EU/t.",
            "nbt_notes": "TileEntityElectricBlock: energy (double), redstoneMode (byte), active.",
            "eu_capacity": 40000000,
            "eu_tier": 4,  # EV
        },
        3: {
            "name": "LV Transformer",
            "te_class": "TileEntityTransformerLV",
            "description": "Transformator 128→32 EU/t (step-down) lub 32→128 (step-up).",
            "nbt_notes": "TileEntityTransformer: mode (step-up/down), facing, active.",
            "eu_tier": 1,
        },
        4: {
            "name": "MV Transformer",
            "te_class": "TileEntityTransformerMV",
            "description": "Transformator 512→128 EU/t lub 128→512.",
            "nbt_notes": "TileEntityTransformer: mode, facing, active.",
            "eu_tier": 2,
        },
        5: {
            "name": "HV Transformer",
            "te_class": "TileEntityTransformerHV",
            "description": "Transformator 2048→512 EU/t lub 512→2048.",
            "nbt_notes": "TileEntityTransformer: mode, facing, active.",
            "eu_tier": 3,
        },
        6: {
            "name": "EV Transformer",
            "te_class": "TileEntityTransformerEV",
            "description": "Transformator 8192→2048 EU/t lub 2048→8192.",
            "nbt_notes": "TileEntityTransformer: mode, facing, active.",
            "eu_tier": 4,
        },
        7: {
            "name": "CESU",
            "te_class": "TileEntityElectricCESU",
            "description": "Magazyn energii CESU. 300 000 EU, 128 EU/t.",
            "nbt_notes": "TileEntityElectricBlock: energy (double), redstoneMode (byte), active.",
            "eu_capacity": 300000,
            "eu_tier": 2,  # MV
        },
    },
}

# ============================================================
# CHARGEPADY (BlockChargepad)
# ============================================================

IC2_CHARGEPADS = {
    "IC2:blockChargepad": {
        0: {
            "name": "BatBox Chargepad",
            "te_class": "TileEntityChargepadBatBox",
            "description": "Ładuje przedmioty w ekwipunku gracza (BatBox tier).",
            "nbt_notes": "TileEntityChargepadBlock: energy, redstoneMode.",
            "eu_capacity": 40000,
        },
        1: {
            "name": "CESU Chargepad",
            "te_class": "TileEntityChargepadCESU",
            "description": "Ładuje przedmioty w ekwipunku gracza (CESU tier).",
            "nbt_notes": "TileEntityChargepadBlock: energy, redstoneMode.",
            "eu_capacity": 300000,
        },
        2: {
            "name": "MFE Chargepad",
            "te_class": "TileEntityChargepadMFE",
            "description": "Ładuje przedmioty w ekwipunku gracza (MFE tier).",
            "nbt_notes": "TileEntityChargepadBlock: energy, redstoneMode.",
            "eu_capacity": 4000000,
        },
        3: {
            "name": "MFSU Chargepad",
            "te_class": "TileEntityChargepadMFSU",
            "description": "Ładuje przedmioty w ekwipunku gracza (MFSU tier).",
            "nbt_notes": "TileEntityChargepadBlock: energy, redstoneMode.",
            "eu_capacity": 40000000,
        },
    },
}

# ============================================================
# REAKTOR JĄDROWY (bloki konstrukcyjne)
# ============================================================

IC2_REACTORS = {
    "IC2:blockReactorChamber": {
        0: {
            "name": "Reactor Chamber",
            "te_class": "TileEntityReactorChamberElectric",
            "description": "Komora reaktora. Zwiększa pojemność reaktora o 1 slot.",
            "nbt_notes": "TileEntityReactorChamberElectric: referencja do głównego reaktora.",
        },
    },
    "IC2:blockReactorFluidPort": {
        0: {
            "name": "Reactor Fluid Port",
            "te_class": "TileEntityReactorFluidPort",
            "description": "Port płynów dla reaktora (wymiana ciepła/płynów chłodzących).",
            "nbt_notes": "TileEntityReactorFluidPort: facing, zbiornik, referencja do reaktora.",
        },
    },
    "IC2:blockReactorAccessHatch": {
        0: {
            "name": "Reactor Access Hatch",
            "te_class": "TileEntityReactorAccessHatch",
            "description": "Właz do reaktora. Dostęp do inventory komponentów.",
            "nbt_notes": "TileEntityReactorAccessHatch: facing, referencja do reaktora.",
        },
    },
    "IC2:blockReactorRedstonePort": {
        0: {
            "name": "Reactor Redstone Port",
            "te_class": "TileEntityReactorRedstonePort",
            "description": "Port redstone reaktora. Sygnały wejścia/wyjścia.",
            "nbt_notes": "TileEntityReactorRedstonePort: facing, referencja do reaktora, tryb.",
        },
    },
    "IC2:blockreactorvessel": {
        0: {
            "name": "Reactor Pressure Vessel",
            "te_class": None,
            "description": "Blok ścianki reaktora pod ciśnieniem. Brak TE (czysty blok).",
            "nbt_notes": "Brak TE. Dekoracyjny/konstrukcyjny.",
        },
    },
}

# ============================================================
# BLOKI PERSONALNE (BlockPersonal)
# ============================================================

IC2_PERSONAL = {
    "IC2:blockPersonal": {
        0: {
            "name": "Personal Safe",
            "te_class": "TileEntityPersonalChest",
            "description": "Skrzynia dostępna tylko dla właściciela (zabezpieczona).",
            "nbt_notes": "TileEntityPersonalChest: owner (UUID/name), inventory.",
        },
        1: {
            "name": "Trade-O-Mat",
            "te_class": "TileEntityTradeOMat",
            "description": "Automatyczny punkt handlowy między graczami.",
            "nbt_notes": "TileEntityTradeOMat: owner, oferta (wanted/offered), inventory.",
        },
        2: {
            "name": "Energy-O-Mat",
            "te_class": "TileEntityEnergyOMat",
            "description": "Automatyczny punkt sprzedaży energii EU.",
            "nbt_notes": "TileEntityEnergyOMat: owner, cena, energy buffer.",
        },
    },
}

# ============================================================
# RUDY I ZASOBY NATURALNE
# ============================================================

IC2_RESOURCES = {
    "IC2:blockOreCopper": {0: {"name": "Copper Ore", "te_class": None, "description": "Ruda miedzi."}},
    "IC2:blockOreTin": {0: {"name": "Tin Ore", "te_class": None, "description": "Ruda cyny."}},
    "IC2:blockOreUran": {0: {"name": "Uranium Ore", "te_class": None, "description": "Rada uranu."}},
    "IC2:blockOreLead": {0: {"name": "Lead Ore", "te_class": None, "description": "Ruda ołowiu."}},
    "IC2:blockRubWood": {0: {"name": "Rubber Wood", "te_class": None, "description": "Drewno kauczukowca."}},
    "IC2:blockRubLeaves": {0: {"name": "Rubber Leaves", "te_class": None, "description": "Liście kauczukowca."}},
    "IC2:blockRubSapling": {0: {"name": "Rubber Sapling", "te_class": None, "description": "Sadzonka kauczukowca."}},
    "IC2:blockHarz": {0: {"name": "Sticky Resin", "te_class": None, "description": "Kropla żywicy na pniu."}},
    "IC2:blockRubber": {0: {"name": "Rubber Sheet", "te_class": None, "description": "Płytka gumy (spowalnia upadki)."}},
    "IC2:blockCrop": {0: {"name": "Crop", "te_class": "TileEntityCrop", "description": "Uprawa IC2 (rośliny).", "nbt_notes": "TileEntityCrop: crop, growth, gain, resistance, size, nutrients, hydration, weedEx, scanLevel."}},
}

# ============================================================
# BLOKI DEKORACYJNE I BUDOWLANE
# ============================================================

IC2_DECORATION = {
    "IC2:blockAlloy": {0: {"name": "Reinforced Stone", "te_class": None, "description": "Wzmocniony kamień (wysoka odporność na wybuchy)."}},
    "IC2:blockBasalt": {0: {"name": "Basalt", "te_class": None, "description": "Blok bazaltu."}},
    "IC2:blockAlloyGlass": {0: {"name": "Reinforced Glass", "te_class": None, "description": "Wzmocnione szkło."}},
    "IC2:blockWall": {0: {"name": "Construction Foam Wall", "te_class": None, "description": "Ściana z piany konstrukcyjnej."}},
    "IC2:blockScaffold": {0: {"name": "Scaffold", "te_class": None, "description": "Rusztowanie (można wspinać)."}},
    "IC2:blockIronScaffold": {0: {"name": "Iron Scaffold", "te_class": None, "description": "Żelazne rusztowanie (wytrzymalsze)."}},
    "IC2:blockMetal": {
            0: {"name": "Bronze Block", "te_class": None},
            1: {"name": "Copper Block", "te_class": None},
            2: {"name": "Tin Block", "te_class": None},
            3: {"name": "Uranium Block", "te_class": None},
            4: {"name": "Lead Block", "te_class": None},
            5: {"name": "Steel Block", "te_class": None},
    },
    "IC2:blockFenceIron": {0: {"name": "Iron Fence", "te_class": None, "description": "Żelazny płot (magnetyzowany przez Magnetizer)."}},
    "IC2:blockDoorAlloy": {0: {"name": "Reinforced Door", "te_class": None, "description": "Wzmocnione drzwi."}},
    "IC2:blockTexGlass": {
            0: {"name": "Reinforced Glass (tinted)", "te_class": None},
    },
}

# ============================================================
# BLOKI SPECJALNE / INNE
# ============================================================

IC2_OTHER = {
    "IC2:blockLuminator": {0: {"name": "Luminator (active)", "te_class": "TileEntityLuminator", "description": "Świetlówka IC2 (włączona).", "nbt_notes": "TileEntityLuminator: energy, active."}},
    "IC2:blockLuminatorDark": {0: {"name": "Luminator (dark)", "te_class": "TileEntityLuminator", "description": "Świetlówka IC2 (wyłączona).", "nbt_notes": "TileEntityLuminator: energy, active."}},
    "IC2:blockMiningPipe": {0: {"name": "Mining Pipe", "te_class": None, "description": "Rura wiertnicza (Miner)."}},
    "IC2:blockMiningTip": {0: {"name": "Mining Pipe Tip", "te_class": None, "description": "Grot rury wiertniczej."}},
    "IC2:blockITNT": {0: {"name": "Industrial TNT", "te_class": None, "description": "Przemysłowy TNT (większy wybuch)."}},
    "IC2:blockNuke": {0: {"name": "Nuke", "te_class": "TileEntityNuke", "description": "Bomba atomowa (ogromny wybuch).", "nbt_notes": "TileEntityNuke: timer, ignited."}},
    "IC2:blockDynamite": {0: {"name": "Dynamite", "te_class": None, "description": "Dynamit (mały wybuch)."}},
    "IC2:blockDynamiteRemote": {0: {"name": " Dynamite (Remote)", "te_class": None, "description": "Dynamit zdalnie sterowany."}},
    "IC2:blockFoam": {0: {"name": "Construction Foam", "te_class": None, "description": "Piana konstrukcyjna (twardnieje w ścianę)."}},
    "IC2:blockReinforcedFoam": {0: {"name": "Reinforced Foam", "te_class": None, "description": "Wzmocniona piana konstrukcyjna."}},
    "IC2:blockBarrel": {0: {"name": "Barrel", "te_class": "TileEntityBarrel", "description": "Beczka do fermentacji alkoholu IC2.", "nbt_notes": "TileEntityBarrel: time, fluid, quality."}},
}

# ============================================================
# BLOKI PŁYNÓW
# ============================================================
# Płyny IC2 są rejestrowane w FluidRegistry i mają bloki dynamiczne.
# W mapie NBT prawdopodobnie występują jako standardowe bloki płynów Forge.

IC2_FLUIDS = {
    "IC2:fluidUuMatter": {0: {"name": "UU-Matter", "te_class": None, "description": "Ciecz UU-Matter."}},
    "IC2:fluidConstructionFoam": {0: {"name": "Construction Foam (fluid)", "te_class": None}},
    "IC2:fluidCoolant": {0: {"name": "Coolant", "te_class": None, "description": "Ciecz chłodząca."}},
    "IC2:fluidHotCoolant": {0: {"name": "Hot Coolant", "te_class": None, "description": "Gorąca ciecz chłodząca."}},
    "IC2:fluidPahoehoeLava": {0: {"name": "Pahoehoe Lava", "te_class": None, "description": "Zastygła lawa."}},
    "IC2:fluidBiomass": {0: {"name": "Biomass", "te_class": None}},
    "IC2:fluidBiogas": {0: {"name": "Biogas", "te_class": None}},
    "IC2:fluidDistilledWater": {0: {"name": "Distilled Water", "te_class": None}},
    "IC2:fluidSuperheatedSteam": {0: {"name": "Superheated Steam", "te_class": None}},
    "IC2:fluidSteam": {0: {"name": "Steam", "te_class": None}},
    "IC2:fluidHotWater": {0: {"name": "Hot Water", "te_class": None}},
}

# ============================================================
# POŁĄCZONA LISTA WSZYSTKICH BLOKÓW
# ============================================================

IC2_ALL_BLOCKS = {}
for d in (IC2_MACHINES, IC2_GENERATORS, IC2_HEAT_GENERATORS, IC2_KINETIC_GENERATORS,
          IC2_CABLES, IC2_ENERGY_STORAGE, IC2_CHARGEPADS, IC2_REACTORS,
          IC2_PERSONAL, IC2_RESOURCES, IC2_DECORATION, IC2_OTHER, IC2_FLUIDS):
    IC2_ALL_BLOCKS.update(d)


def list_all_tile_entities():
    """Zwraca zbiór wszystkich Tile Entity class names używanych przez IC2."""
    tes = set()
    for block_id, variants in IC2_ALL_BLOCKS.items():
        for meta, info in variants.items():
            te = info.get("te_class")
            if te:
                tes.add(te)
    return sorted(tes)


def get_block_info(block_id: str, metadata: int):
    """Zwraca informacje o bloku IC2 na podstawie ID i metadanych."""
    variants = IC2_ALL_BLOCKS.get(block_id)
    if not variants:
        return None
    return variants.get(metadata)


if __name__ == "__main__":
    print(f"Liczba zarejestrowanych bloków IC2: {len(IC2_ALL_BLOCKS)}")
    print(f"Liczba różnych Tile Entity: {len(list_all_tile_entities())}")
    for te in list_all_tile_entities():
        print(f"  - {te}")
