"""
Mapowania geometrii CarpentersBlocks -> CuttableBlocks 1.18.2.

Źródło: Slope.java, Stairs.java, Slab.java z CB 1.7.10.

Każdy wpis zawiera:
  slope_id   / stairs_id / slab_id  -> int (klucz, cbMetadata w TEBase)
  cb1182_props -> dict blockstate properties dla cuttableblocks 1.18.2

Nazwy stałych geometrycznych (facings) tłumaczą się na blockstate props
według konwencji cuttableblocks:
  facing   = N/S/W/E (główny kierunek)
  half     = bottom/top  (czy blok w dolnej czy górnej połowie)
  shape    = straight/inner_left/inner_right/outer_left/outer_right  (schody)
  slope_type = wedge_side/wedge/wedge_int/wedge_ext/
               oblique_int/oblique_ext/
               prism/prism_1p/prism_2p/prism_3p/prism_4p/prism_wedge
"""

from typing import NamedTuple


class SlopeProps(NamedTuple):
    """Właściwości blockstate dla cuttableblocks:slope."""
    slope_type: str   # patrz Slope.Type
    facing: str       # primary horizontal facing (north/south/west/east) lub "" dla prism
    half: str         # bottom / top (isPositive -> top)
    shape: str        # "" dla wedge, "inner"/"outer" dla int/ext itp.


class StairsProps(NamedTuple):
    """Właściwości blockstate dla cuttableblocks:stairs."""
    facing: str   # north/south/west/east
    half: str     # bottom/top
    shape: str    # straight/inner_left/inner_right/outer_left/outer_right


class SlabProps(NamedTuple):
    """Właściwości blockstate dla cuttableblocks:block (slab)."""
    type: str    # bottom/top/double
    axis: str    # y/x/z  (kierunek prostopadły do płaszczyzny podziału)


# -------------------------------------------------------------------
# SLOPE - 65 wariantów, slopeID 0..64 (Slope.java)
# -------------------------------------------------------------------
# Konwencja nazw slope_type odpowiada Slope.Type w Slope.java:
#   WEDGE_SIDE -> "wedge_side"
#   WEDGE      -> "wedge"
#   WEDGE_INT  -> "wedge_int"
#   WEDGE_EXT  -> "wedge_ext"
#   OBLIQUE_INT -> "oblique_int"
#   OBLIQUE_EXT -> "oblique_ext"
#   PRISM      -> "prism"
#   PRISM_1P   -> "prism_1p"
#   PRISM_2P   -> "prism_2p"
#   PRISM_3P   -> "prism_3p"
#   PRISM_4P   -> "prism_4p"
#   PRISM_WEDGE -> "prism_wedge"
#
# Dla WEDGE_SIDE: facing to kierunek "pochylenia" (compound, np. NW/SE)
# Dla pozostałych: facing to primary horizontal direction

SLOPE_ID_TO_PROPS: dict[int, SlopeProps] = {
    # --- WEDGE_SIDE (ID 0-3): ukośne w poziomie, bez góry/dołu ---
    0:  SlopeProps("wedge_side", "south_east", "bottom", ""),
    1:  SlopeProps("wedge_side", "north_west", "bottom", ""),
    2:  SlopeProps("wedge_side", "north_east", "bottom", ""),
    3:  SlopeProps("wedge_side", "south_west", "bottom", ""),

    # --- WEDGE (ID 4-11): podstawowy skos w jednym kierunku ---
    4:  SlopeProps("wedge", "north", "bottom", ""),   # NEG_N: DOWN+NORTH -> top=UP -> half=bottom
    5:  SlopeProps("wedge", "south", "bottom", ""),   # NEG_S: DOWN+SOUTH
    6:  SlopeProps("wedge", "west",  "bottom", ""),   # NEG_W: DOWN+WEST
    7:  SlopeProps("wedge", "east",  "bottom", ""),   # NEG_E: DOWN+EAST
    8:  SlopeProps("wedge", "north", "top",    ""),   # POS_N: UP+NORTH
    9:  SlopeProps("wedge", "south", "top",    ""),   # POS_S: UP+SOUTH
    10: SlopeProps("wedge", "west",  "top",    ""),   # POS_W: UP+WEST
    11: SlopeProps("wedge", "east",  "top",    ""),   # POS_E: UP+EAST

    # --- WEDGE_INT (ID 12-19): wewnętrzny narożnik ---
    12: SlopeProps("wedge_int", "south_east", "bottom", ""),
    13: SlopeProps("wedge_int", "north_west", "bottom", ""),
    14: SlopeProps("wedge_int", "north_east", "bottom", ""),
    15: SlopeProps("wedge_int", "south_west", "bottom", ""),
    16: SlopeProps("wedge_int", "south_east", "top",    ""),
    17: SlopeProps("wedge_int", "north_west", "top",    ""),
    18: SlopeProps("wedge_int", "north_east", "top",    ""),
    19: SlopeProps("wedge_int", "south_west", "top",    ""),

    # --- WEDGE_EXT (ID 20-27): zewnętrzny narożnik ---
    20: SlopeProps("wedge_ext", "south_east", "bottom", ""),
    21: SlopeProps("wedge_ext", "north_west", "bottom", ""),
    22: SlopeProps("wedge_ext", "north_east", "bottom", ""),
    23: SlopeProps("wedge_ext", "south_west", "bottom", ""),
    24: SlopeProps("wedge_ext", "south_east", "top",    ""),
    25: SlopeProps("wedge_ext", "north_west", "top",    ""),
    26: SlopeProps("wedge_ext", "north_east", "top",    ""),
    27: SlopeProps("wedge_ext", "south_west", "top",    ""),

    # --- OBLIQUE_INT (ID 28-35): skośny wewnętrzny narożnik ---
    28: SlopeProps("oblique_int", "south_east", "bottom", ""),
    29: SlopeProps("oblique_int", "north_west", "bottom", ""),
    30: SlopeProps("oblique_int", "north_east", "bottom", ""),
    31: SlopeProps("oblique_int", "south_west", "bottom", ""),
    32: SlopeProps("oblique_int", "south_east", "top",    ""),
    33: SlopeProps("oblique_int", "north_west", "top",    ""),
    34: SlopeProps("oblique_int", "north_east", "top",    ""),
    35: SlopeProps("oblique_int", "south_west", "top",    ""),

    # --- OBLIQUE_EXT (ID 36-43): skośny zewnętrzny narożnik ---
    36: SlopeProps("oblique_ext", "south_east", "bottom", ""),
    37: SlopeProps("oblique_ext", "north_west", "bottom", ""),
    38: SlopeProps("oblique_ext", "north_east", "bottom", ""),
    39: SlopeProps("oblique_ext", "south_west", "bottom", ""),
    40: SlopeProps("oblique_ext", "south_east", "top",    ""),
    41: SlopeProps("oblique_ext", "north_west", "top",    ""),
    42: SlopeProps("oblique_ext", "north_east", "top",    ""),
    43: SlopeProps("oblique_ext", "south_west", "top",    ""),

    # --- PRISM (ID 44-45): dach symetryczny (kalenica E-W lub N-S) ---
    44: SlopeProps("prism", "north", "bottom", ""),  # PRISM_NEG: facings=[DOWN]
    45: SlopeProps("prism", "north", "top",    ""),  # PRISM_POS: facings=[UP]

    # --- PRISM_1P (ID 46-49): piramida 1-stronna ---
    46: SlopeProps("prism_1p", "north", "top", ""),
    47: SlopeProps("prism_1p", "south", "top", ""),
    48: SlopeProps("prism_1p", "west",  "top", ""),
    49: SlopeProps("prism_1p", "east",  "top", ""),

    # --- PRISM_2P (ID 50-55): piramida 2-stronna ---
    50: SlopeProps("prism_2p", "north_south", "top", ""),
    51: SlopeProps("prism_2p", "west_east",   "top", ""),
    52: SlopeProps("prism_2p", "south_east",  "top", ""),
    53: SlopeProps("prism_2p", "north_west",  "top", ""),
    54: SlopeProps("prism_2p", "north_east",  "top", ""),
    55: SlopeProps("prism_2p", "south_west",  "top", ""),

    # --- PRISM_3P (ID 56-59): piramida 3-stronna ---
    56: SlopeProps("prism_3p", "north_west_east",  "top", ""),
    57: SlopeProps("prism_3p", "south_west_east",  "top", ""),
    58: SlopeProps("prism_3p", "north_south_west", "top", ""),
    59: SlopeProps("prism_3p", "north_south_east", "top", ""),

    # --- PRISM_4P (ID 60): piramida 4-stronna ---
    60: SlopeProps("prism_4p", "all", "top", ""),

    # --- PRISM_WEDGE (ID 61-64): dach z jedną pełną ścianą ---
    61: SlopeProps("prism_wedge", "north", "top", ""),
    62: SlopeProps("prism_wedge", "south", "top", ""),
    63: SlopeProps("prism_wedge", "west",  "top", ""),
    64: SlopeProps("prism_wedge", "east",  "top", ""),
}


# -------------------------------------------------------------------
# STAIRS - 28 wariantów, stairsID 0..27 (Stairs.java)
# -------------------------------------------------------------------
# Mapowanie na standardowy format schodów 1.18.2 (facing/half/shape).
# facing: north/south/west/east = kierunek, w którym schody "otwierają się"
# half:   bottom (NEG = isPositive=false, schody od dołu)
#         top    (POS = isPositive=true, schody od góry)
# shape:  straight     = NORMAL (ID 4-11)
#         inner_left / inner_right = NORMAL_INT (ID 12-19)
#         outer_left / outer_right = NORMAL_EXT (ID 20-27)
#         "side"                    = NORMAL_SIDE (ID 0-3, ukośne)
#
# Uwaga: NORMAL_SIDE to specjalny wariant CB bez odpowiednika w vanilla stairs.
# W cuttableblocks obsługiwany jako osobny shape="side_XX".

STAIRS_ID_TO_PROPS: dict[int, StairsProps] = {
    # --- NORMAL_SIDE (ID 0-3): ukośne w poziomie ---
    0:  StairsProps("south", "bottom", "side_se"),
    1:  StairsProps("north", "bottom", "side_nw"),
    2:  StairsProps("north", "bottom", "side_ne"),
    3:  StairsProps("south", "bottom", "side_sw"),

    # --- NORMAL (ID 4-11): zwykłe schody (jak vanilla) ---
    4:  StairsProps("north", "bottom", "straight"),   # NEG_N
    5:  StairsProps("south", "bottom", "straight"),   # NEG_S
    6:  StairsProps("west",  "bottom", "straight"),   # NEG_W
    7:  StairsProps("east",  "bottom", "straight"),   # NEG_E
    8:  StairsProps("north", "top",    "straight"),   # POS_N
    9:  StairsProps("south", "top",    "straight"),   # POS_S
    10: StairsProps("west",  "top",    "straight"),   # POS_W
    11: StairsProps("east",  "top",    "straight"),   # POS_E

    # --- NORMAL_INT (ID 12-19): wewnętrzny narożnik ---
    # inner_left / inner_right zależy od kombinacji facing+corner
    12: StairsProps("south", "bottom", "inner_right"),  # INT_NEG_SE
    13: StairsProps("north", "bottom", "inner_left"),   # INT_NEG_NW
    14: StairsProps("north", "bottom", "inner_right"),  # INT_NEG_NE
    15: StairsProps("south", "bottom", "inner_left"),   # INT_NEG_SW
    16: StairsProps("south", "top",    "inner_right"),  # INT_POS_SE
    17: StairsProps("north", "top",    "inner_left"),   # INT_POS_NW
    18: StairsProps("north", "top",    "inner_right"),  # INT_POS_NE
    19: StairsProps("south", "top",    "inner_left"),   # INT_POS_SW

    # --- NORMAL_EXT (ID 20-27): zewnętrzny narożnik ---
    20: StairsProps("south", "bottom", "outer_right"),  # EXT_NEG_SE
    21: StairsProps("north", "bottom", "outer_left"),   # EXT_NEG_NW
    22: StairsProps("north", "bottom", "outer_right"),  # EXT_NEG_NE
    23: StairsProps("south", "bottom", "outer_left"),   # EXT_NEG_SW
    24: StairsProps("south", "top",    "outer_right"),  # EXT_POS_SE
    25: StairsProps("north", "top",    "outer_left"),   # EXT_POS_NW
    26: StairsProps("north", "top",    "outer_right"),  # EXT_POS_NE
    27: StairsProps("south", "top",    "outer_left"),   # EXT_POS_SW
}


# -------------------------------------------------------------------
# SLAB (BlockCarpentersBlock w trybie slab) - cbMetadata 0..6 (Slab.java)
# -------------------------------------------------------------------
# DIR_MAP w Slab.java: { 4, 5, 0, 1, 2, 3 }  (ForgeDirection ordinals)
# SLAB_Y_NEG=3 -> DIR_MAP[2]=0=DOWN  -> half=bottom, axis=y
# SLAB_Y_POS=4 -> DIR_MAP[3]=1=UP    -> half=top,    axis=y
# SLAB_Z_NEG=5 -> DIR_MAP[4]=2=NORTH -> half=bottom, axis=z
# SLAB_Z_POS=6 -> DIR_MAP[5]=3=SOUTH -> half=top,    axis=z
# SLAB_X_NEG=1 -> DIR_MAP[0]=4=WEST  -> half=bottom, axis=x
# SLAB_X_POS=2 -> DIR_MAP[1]=5=EAST  -> half=top,    axis=x
# BLOCK_FULL=0 -> pełny blok

SLAB_ID_TO_PROPS: dict[int, SlabProps] = {
    0: SlabProps("double", "y"),   # BLOCK_FULL
    1: SlabProps("bottom", "x"),   # SLAB_X_NEG  (zachodnia połowa)
    2: SlabProps("top",    "x"),   # SLAB_X_POS  (wschodnia połowa)
    3: SlabProps("bottom", "y"),   # SLAB_Y_NEG  (dolna połowa)
    4: SlabProps("top",    "y"),   # SLAB_Y_POS  (górna połowa)
    5: SlabProps("bottom", "z"),   # SLAB_Z_NEG  (północna połowa)
    6: SlabProps("top",    "z"),   # SLAB_Z_POS  (południowa połowa)
}
