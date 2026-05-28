"""Witchery 1.7.10 – statyczne mapowania dla konwertera.

UWAGA: To jest UPROSZCZONA konwersja – wszystkie TileEntities Witchery
są mapowane na placeholdery, ponieważ mod nie ma portu na 1.18.2.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Grupy TE wg złożoności NBT – używane w polu conversion_stage placeholder
# ---------------------------------------------------------------------------

GROUP_FUNCTIONAL = "witchery_functional_inventory"
GROUP_SPECIAL    = "witchery_special_state"
GROUP_DECORATIVE = "witchery_decorative_minimal"
GROUP_REDSTONE   = "witchery_cursed_redstone"
GROUP_FLUID      = "witchery_brew_fluid"

# ---------------------------------------------------------------------------
# Wszystkie TE IDs Witchery 1.7.10 → klucz bloku źródłowego
# ---------------------------------------------------------------------------
# Klucz TE w NBT równy blockName z GameRegistry.registerTileEntity(clazz, blockName).
# Dla WitchesOven/Distillery/FumeFunnel tylko wariant !burning/!filtered rejestruje
# TE; blok aktywny dzieli tę samą klasę TE, więc też zapisuje idle-TE-ID.

TE_ID_TO_BLOCK_REGISTRY: dict[str, str] = {

    # ── Grupa 1: Funkcjonalne z bogatym NBT ──────────────────────────────
    "witchery:altar":           "witchery:altar",
    "witchery:kettle":          "witchery:kettle",
    "witchery:cauldron":        "witchery:cauldron",
    "witchery:spinningwheel":   "witchery:spinningwheel",
    "witchery:witchesovenidle": "witchery:witchesovenidle",
    "witchery:distilleryidle":  "witchery:distilleryidle",
    "witchery:poppetshelf":     "witchery:poppetshelf",
    "witchery:leechchest":      "witchery:leechchest",
    "witchery:refillingchest":  "witchery:refillingchest",
    "witchery:silvervat":       "witchery:silvervat",
    "witchery:brazier":         "witchery:brazier",
    "witchery:bloodcrucible":   "witchery:bloodcrucible",

    # ── Grupa 2: Specjalne z danymi gracza/portalu ────────────────────────
    "witchery:mirrorblock":     "witchery:mirrorblock",
    "witchery:mirrorblock2":    "witchery:mirrorblock2",
    "witchery:dreamcatcher":    "witchery:dreamcatcher",
    "witchery:crystalball":     "witchery:crystalball",
    "witchery:coffinblock":     "witchery:coffinblock",
    "witchery:decurseteleport": "witchery:decurseteleport",
    "witchery:decursedirected": "witchery:decursedirected",
    "witchery:placeditem":      "witchery:placeditem",
    "witchery:spiritportal":    "witchery:spiritportal",

    # ── Grupa 3: Dekoracyjne / minimalne TE ──────────────────────────────
    "witchery:fumefunnel":      "witchery:fumefunnel",
    "witchery:scarecrow":       "witchery:scarecrow",
    "witchery:trent":           "witchery:trent",
    "witchery:witchsladder":    "witchery:witchsladder",
    "witchery:wolfaltar":       "witchery:wolfaltar",
    "witchery:statueofworship": "witchery:statueofworship",
    "witchery:statuegoddess":   "witchery:statuegoddess",
    "witchery:alluringskull":   "witchery:alluringskull",
    "witchery:candelabra":      "witchery:candelabra",
    "witchery:chalice":         "witchery:chalice",
    "witchery:wolfhead":        "witchery:wolfhead",
    "witchery:glowglobe":       "witchery:glowglobe",
    "witchery:circle":          "witchery:circle",
    "witchery:beartrap":        "witchery:beartrap",
    "witchery:wolftrap":        "witchery:wolftrap",
    "witchery:garlicgarland":   "witchery:garlicgarland",
    "witchery:voidbramble":     "witchery:voidbramble",
    "witchery:grassper":        "witchery:grassper",
    "witchery:bloodrose":       "witchery:bloodrose",
    "witchery:barrier":         "witchery:barrier",
    "witchery:light":           "witchery:light",

    # ── Grupa 4: Przeklęte bloki redstone ────────────────────────────────
    "witchery:clever":               "witchery:clever",
    "witchery:cwoodendoor":          "witchery:cwoodendoor",
    "witchery:cwoodpressureplate":   "witchery:cwoodpressureplate",
    "witchery:cstonepressureplate":  "witchery:cstonepressureplate",
    "witchery:csnowpressureplate":   "witchery:csnowpressureplate",
    "witchery:cbuttonwood":          "witchery:cbuttonwood",
    "witchery:cbuttonstone":         "witchery:cbuttonstone",

    # ── Grupa 5: Płyny brew ───────────────────────────────────────────────
    "witchery:brewgas":    "witchery:brewgas",
    "witchery:brewliquid": "witchery:brewliquid",
    "witchery:slurp":      "witchery:slurp",
}

# Frozenset wszystkich znanych TE IDs Witchery
WITCHERY_TE_IDS: frozenset[str] = frozenset(TE_ID_TO_BLOCK_REGISTRY)

# Mapowanie TE ID → grupa (conversion_stage)
TE_ID_TO_GROUP: dict[str, str] = {
    **{k: GROUP_FUNCTIONAL for k in [
        "witchery:altar", "witchery:kettle", "witchery:cauldron",
        "witchery:spinningwheel", "witchery:witchesovenidle",
        "witchery:distilleryidle", "witchery:poppetshelf",
        "witchery:leechchest", "witchery:refillingchest",
        "witchery:silvervat", "witchery:brazier", "witchery:bloodcrucible",
    ]},
    **{k: GROUP_SPECIAL for k in [
        "witchery:mirrorblock", "witchery:mirrorblock2",
        "witchery:dreamcatcher", "witchery:crystalball",
        "witchery:coffinblock", "witchery:decurseteleport",
        "witchery:decursedirected", "witchery:placeditem",
        "witchery:spiritportal",
    ]},
    **{k: GROUP_DECORATIVE for k in [
        "witchery:fumefunnel", "witchery:scarecrow", "witchery:trent",
        "witchery:witchsladder", "witchery:wolfaltar",
        "witchery:statueofworship", "witchery:statuegoddess",
        "witchery:alluringskull", "witchery:candelabra", "witchery:chalice",
        "witchery:wolfhead", "witchery:glowglobe", "witchery:circle",
        "witchery:beartrap", "witchery:wolftrap", "witchery:garlicgarland",
        "witchery:voidbramble", "witchery:grassper", "witchery:bloodrose",
        "witchery:barrier", "witchery:light",
    ]},
    **{k: GROUP_REDSTONE for k in [
        "witchery:clever", "witchery:cwoodendoor",
        "witchery:cwoodpressureplate", "witchery:cstonepressureplate",
        "witchery:csnowpressureplate", "witchery:cbuttonwood",
        "witchery:cbuttonstone",
    ]},
    **{k: GROUP_FLUID for k in [
        "witchery:brewgas", "witchery:brewliquid", "witchery:slurp",
    ]},
}
