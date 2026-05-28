"""
CarpentersBlocks 1.7.10 -> CuttableBlocks 1.18.2 - mapowania ID bloków.

Źródła:
  1.7.10: mod_src/1710/actual_src/1.7.10/CarpentersBlocks/repo/
          BlockRegistry.java, Slope.java, Stairs.java, Slab.java
  1.18.2: pl.pawel.minecraftkonwersja.cuttableblocks (własny mod)

Zasada:
  Bloki CB 1.7.10 zarejestrowane pod kluczem "CarpentersBlocks:<nazwaBloku>"
  (Forge GameRegistry.registerBlock z unlocalized name "blockCarpentersXxx").
  Każdy blok CB ma TileEntity TEBase z:
    cbAttrList  - lista atrybutów (pokrycia, barwniki, nakładki) jako ItemStack
    cbMetadata  - liczba całkowita; znaczenie zależy od typu bloku:
                    Slope  -> slopeID  (0..64), patrz Slope.java
                    Stairs -> stairsID (0..27), patrz Stairs.java
                    Slab (block) -> 0=full 1=X- 2=X+ 3=Y- 4=Y+ 5=Z- 6=Z+
                    Collapsible  -> bitmaska ścian (bits 0..5)
                    inne bloki   -> zależy od bloku
    cbDesign    - opcjonalny wzór dłuta
    cbOwner     - nick właściciela

Konwersja 1:1 do własnego modu cuttableblocks 1.18.2:
  Bloki geometryczne (slope/stairs) -> cuttableblocks:slope / cuttableblocks:stairs
  Bloki funkcjonalne niegeometryczne -> cuttableblocks:block itd.
  Bloki bez odpowiednika w CB 1.18.2 -> placeholder (lista CB_NO_EQUIVALENT)
"""

# -------------------------------------------------------------------
# Wszystkie bloki CarpentersBlocks 1.7.10 (mod ID w Forge: "CarpentersBlocks")
# -------------------------------------------------------------------

ALL_CB_BLOCK_IDS_1710: list[str] = [
    "CarpentersBlocks:blockCarpentersBarrier",
    "CarpentersBlocks:blockCarpentersBed",
    "CarpentersBlocks:blockCarpentersBlock",
    "CarpentersBlocks:blockCarpentersButton",
    "CarpentersBlocks:blockCarpentersCollapsibleBlock",
    "CarpentersBlocks:blockCarpentersDaylightSensor",
    "CarpentersBlocks:blockCarpentersDoor",
    "CarpentersBlocks:blockCarpentersFlowerPot",
    "CarpentersBlocks:blockCarpentersGarageDoor",
    "CarpentersBlocks:blockCarpentersGate",
    "CarpentersBlocks:blockCarpentersHatch",
    "CarpentersBlocks:blockCarpentersLadder",
    "CarpentersBlocks:blockCarpentersLever",
    "CarpentersBlocks:blockCarpentersPressurePlate",
    "CarpentersBlocks:blockCarpentersSafe",
    "CarpentersBlocks:blockCarpentersSlope",
    "CarpentersBlocks:blockCarpentersStairs",
    "CarpentersBlocks:blockCarpentersTorch",
]

# -------------------------------------------------------------------
# Bloki geometryczne (kształt zależy od cbMetadata)
# -------------------------------------------------------------------

CB_GEOMETRIC_BLOCKS: set[str] = {
    "CarpentersBlocks:blockCarpentersSlope",    # slopeID 0..64 (Slope.java)
    "CarpentersBlocks:blockCarpentersStairs",   # stairsID 0..27 (Stairs.java)
    "CarpentersBlocks:blockCarpentersBlock",    # slab: cbMetadata 0..6 (Slab.java)
    "CarpentersBlocks:blockCarpentersCollapsibleBlock",  # bitmask ścian
}

# -------------------------------------------------------------------
# Bloki funkcjonalne zachowujące swoją rolę w 1.18.2
# -------------------------------------------------------------------

CB_FUNCTIONAL_BLOCKS: set[str] = {
    "CarpentersBlocks:blockCarpentersBarrier",
    "CarpentersBlocks:blockCarpentersDoor",
    "CarpentersBlocks:blockCarpentersGate",
    "CarpentersBlocks:blockCarpentersHatch",
    "CarpentersBlocks:blockCarpentersLadder",
    "CarpentersBlocks:blockCarpentersLever",
    "CarpentersBlocks:blockCarpentersPressurePlate",
    "CarpentersBlocks:blockCarpentersTorch",
    "CarpentersBlocks:blockCarpentersDaylightSensor",
    "CarpentersBlocks:blockCarpentersButton",
}

# -------------------------------------------------------------------
# Bloki tylko z pokryciem (bez specjalnej geometrii/funkcji)
# -------------------------------------------------------------------

CB_COVER_ONLY_BLOCKS: set[str] = {
    "CarpentersBlocks:blockCarpentersBed",
    "CarpentersBlocks:blockCarpentersFlowerPot",
    "CarpentersBlocks:blockCarpentersSafe",
    "CarpentersBlocks:blockCarpentersGarageDoor",
}

# -------------------------------------------------------------------
# Mapowanie 1.7.10 -> CuttableBlocks 1.18.2
#
# Klucz: ID bloku 1.7.10
# Wartość: ID bloku w modzie cuttableblocks 1.18.2
#   None  = brak bezpośredniego odpowiednika (wymaga placeholdera lub
#           konwersji na blok vanilla/inny mod)
#
# Mod cuttableblocks używa przestrzeni nazw "cuttableblocks"
# -------------------------------------------------------------------

CB_BLOCK_TO_CB1182: dict[str, str | None] = {
    # Geometryczne - główne bloki moda
    "CarpentersBlocks:blockCarpentersSlope":
        "cuttableblocks:carpenter_slope",
    "CarpentersBlocks:blockCarpentersStairs":
        "cuttableblocks:carpenter_stairs",
    "CarpentersBlocks:blockCarpentersBlock":
        "cuttableblocks:carpenter_block",   # slab / full block
    "CarpentersBlocks:blockCarpentersCollapsibleBlock":
        "cuttableblocks:collapsible_block",

    # Funkcjonalne
    "CarpentersBlocks:blockCarpentersBarrier":
        "cuttableblocks:carpenter_barrier",
    "CarpentersBlocks:blockCarpentersDoor":
        "cuttableblocks:carpenter_door",
    "CarpentersBlocks:blockCarpentersGate":
        "cuttableblocks:carpenter_gate",
    "CarpentersBlocks:blockCarpentersHatch":
        "cuttableblocks:carpenter_hatch",
    "CarpentersBlocks:blockCarpentersLadder":
        "cuttableblocks:carpenter_ladder",
    "CarpentersBlocks:blockCarpentersLever":
        "cuttableblocks:carpenter_lever",
    "CarpentersBlocks:blockCarpentersPressurePlate":
        "cuttableblocks:carpenter_pressure_plate",
    "CarpentersBlocks:blockCarpentersTorch":
        "cuttableblocks:carpenter_torch",
    "CarpentersBlocks:blockCarpentersDaylightSensor":
        "cuttableblocks:carpenter_daylight_sensor",
    "CarpentersBlocks:blockCarpentersButton":
        "cuttableblocks:carpenter_button",

    # Pokrycie tylko - mapowane na CB1182 o ile istnieje odpowiednik
    "CarpentersBlocks:blockCarpentersBed":
        "cuttableblocks:carpenter_bed",
    "CarpentersBlocks:blockCarpentersFlowerPot":
        "cuttableblocks:carpenter_flower_pot",
    "CarpentersBlocks:blockCarpentersSafe":
        "cuttableblocks:carpenter_safe",
    "CarpentersBlocks:blockCarpentersGarageDoor":
        "cuttableblocks:carpenter_garage_door",
}

# -------------------------------------------------------------------
# Indeksy atrybutów w cbAttrList (TEBase.java)
# -------------------------------------------------------------------

# ATTR_COVER[0..6]: 7 stron pokrycia (0=DOWN, 1=UP, 2=N, 3=S, 4=W, 5=E, 6=base)
ATTR_COVER = list(range(7))       # 0..6
ATTR_DYE = list(range(7, 14))     # 7..13
ATTR_OVERLAY = list(range(14, 21))  # 14..20
ATTR_ILLUMINATOR = 21
ATTR_PLANT = 22
ATTR_SOIL = 23
ATTR_FERTILIZER = 24
ATTR_UPGRADE = 25

# Indeks strony bazowej (cover[6]) - klucz dla materiału bloku
ATTR_COVER_BASE = 6

# -------------------------------------------------------------------
# Mapowanie numeric block ID (z mapy 1.7.10) -> string ID bloku CB.
# Źródło: level.dat FML ItemData dla tej konkretnej mapy.
# Jeśli kolejność modów się zmieni, trzeba zaktualizować.
# -------------------------------------------------------------------

CB_NUMERIC_ID_TO_BLOCK_ID: dict[int, str] = {
    247: "CarpentersBlocks:blockCarpentersBlock",
    248: "CarpentersBlocks:blockCarpentersBarrier",
    249: "CarpentersBlocks:blockCarpentersBed",
    250: "CarpentersBlocks:blockCarpentersButton",
    251: "CarpentersBlocks:blockCarpentersCollapsibleBlock",
    252: "CarpentersBlocks:blockCarpentersDaylightSensor",
    253: "CarpentersBlocks:blockCarpentersDoor",
    254: "CarpentersBlocks:blockCarpentersFlowerPot",
    255: "CarpentersBlocks:blockCarpentersGarageDoor",
    409: "CarpentersBlocks:blockCarpentersGate",
    410: "CarpentersBlocks:blockCarpentersHatch",
    411: "CarpentersBlocks:blockCarpentersLadder",
    412: "CarpentersBlocks:blockCarpentersLever",
    413: "CarpentersBlocks:blockCarpentersPressurePlate",
    414: "CarpentersBlocks:blockCarpentersSafe",
    415: "CarpentersBlocks:blockCarpentersSlope",
    416: "CarpentersBlocks:blockCarpentersStairs",
    423: "CarpentersBlocks:blockCarpentersTorch",
}
