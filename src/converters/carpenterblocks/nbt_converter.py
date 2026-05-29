"""
Konwerter NBT CarpentersBlocks 1.7.10 -> CuttableBlocks 1.18.2.

Źródła 1.7.10:
  tileentity/TEBase.java         - format cbAttrList, cbMetadata
  util/Attribute.java            - serializacja cbUniqueId + ItemStack
  data/Slope.java                - dekodowanie slopeID z cbMetadata
  data/Stairs.java               - dekodowanie stairsID z cbMetadata
  data/Slab.java                 - dekodowanie slabID z cbMetadata
  data/Collapsible.java          - dekodowanie quad depths z cbMetadata
  data/Barrier.java / Gate.java / Hatch.java / Hinge.java
  data/Ladder.java / Lever.java / Button.java / Torch.java / DaylightSensor.java

Cel 1.18.2:
  pl.pawel.minecraftkonwersja.cuttableblocks (własny mod)
  Każdy blok CB dostaje:
    blockstate_props  - właściwości geometryczne (facing, half, shape, slope_type…)
    nbt_1182          - dane BlockEntity: coverMaterial, per-side covers, cbDesign
    block_id_1182     - docelowy ID bloku (z CB_BLOCK_TO_CB1182)

Kody błędów:
  CB-E-UNKNOWN_BLOCK   - nieznany block_id_1710
  CB-E-GEOM_OOB        - cbMetadata poza dozwolonym zakresem
  CB-W-UNKNOWN_MAT     - nieznany materiał pokrycia (inny mod)
  CB-W-NO_COVER        - brak base cover[6] w cbAttrList
  CB-W-MULTIBLOCK      - blok wielosegmentowy (bed/garage_door) - uproszczona konwersja
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .mappings.block_ids import (
    CB_BLOCK_TO_CB1182,
    ALL_CB_BLOCK_IDS_1710,
    ATTR_COVER_BASE,
    ATTR_COVER,
    ATTR_DYE,
    ATTR_OVERLAY,
    ATTR_ILLUMINATOR,
)
from .mappings.cover_materials import resolve_cover_material
from .mappings.geometry import (
    SLOPE_ID_TO_PROPS,
    STAIRS_ID_TO_PROPS,
    SLAB_ID_TO_PROPS,
    SlopeProps,
    StairsProps,
    SlabProps,
)

# -------------------------------------------------------------------
# Typy wynikowe
# -------------------------------------------------------------------

FORGE_DIR_TO_FACING = {
    0: "down",
    1: "up",
    2: "north",
    3: "south",
    4: "west",
    5: "east",
}

FACING_TO_FORGE_DIR: dict[str, int] = {v: k for k, v in FORGE_DIR_TO_FACING.items()}

# CarpenterBlockEntity flags bitmask (spójne z Java FLAG_* w CarpenterBlockEntity.java)
FLAG_STATE        = 0x01  # ogólny stan (open/on)
FLAG_UPPER_HALF   = 0x02  # górna połowa (door/hatch)
FLAG_RIGHT_HINGE  = 0x04  # prawa zawiasa (door)
FLAG_RIGID        = 0x08  # wymaga redstone (hatch/door)
FLAG_POLARITY_NEG = 0x10  # odwrócona polaryzacja (lever/button/daylight_sensor)
FLAG_SMOLDERING   = 0x20  # tlenie (torch)
FLAG_HAS_POST     = 0x40  # słupek bariery (barrier)


@dataclass
class ParsedAttr:
    """Jeden wpis z cbAttrList po sparsowaniu."""
    attr_id: int          # cbAttribute (0..25)
    cb_unique_id: str     # cbUniqueId (Forge registry name)
    damage: int           # Damage (metadata ItemStack)
    resolved_id: str | None  # 1.18.2 resource location lub None


@dataclass
class ParsedTEBase:
    """Sparsowana reprezentacja TEBase 1.7.10."""
    cb_metadata: int
    cb_design: str
    cb_owner: str
    # covers[0..6], dyes[7..13], overlays[14..20], special[21+]
    attrs: dict[int, ParsedAttr] = field(default_factory=dict)

    @property
    def base_cover(self) -> ParsedAttr | None:
        return self.attrs.get(ATTR_COVER_BASE)

    @property
    def has_illuminator(self) -> bool:
        return ATTR_ILLUMINATOR in self.attrs


@dataclass
class CBConversionResult:
    """Wynik konwersji jednego bloku CB."""
    success: bool
    block_id_1710: str
    block_id_1182: str | None = None
    blockstate_props: dict[str, str] = field(default_factory=dict)
    nbt_1182: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, code: str, msg: str) -> None:
        self.errors.append(f"CB-E-{code}: {msg}")
        self.success = False

    def add_warning(self, code: str, msg: str) -> None:
        self.warnings.append(f"CB-W-{code}: {msg}")


# -------------------------------------------------------------------
# Parser TEBase NBT
# -------------------------------------------------------------------

def _parse_attr_entry(entry: dict[str, Any]) -> ParsedAttr | None:
    """Parsuje jeden wpis z cbAttrList do ParsedAttr."""
    attr_id = int(entry.get("cbAttribute", -1))
    if attr_id < 0:
        return None

    cb_unique_id = entry.get("cbUniqueId", "")
    damage = int(entry.get("Damage", 0))

    # cbUniqueId czasem przechowywany jako "mod:name", czasem tylko "name"
    if cb_unique_id and ":" not in cb_unique_id:
        # Stary format bez namespace → prawdopodobnie minecraft
        cb_unique_id = f"minecraft:{cb_unique_id}"

    resolved = None
    if cb_unique_id:
        resolved = resolve_cover_material(cb_unique_id, damage)

    return ParsedAttr(
        attr_id=attr_id,
        cb_unique_id=cb_unique_id,
        damage=damage,
        resolved_id=resolved,
    )


def parse_te_base(nbt: dict[str, Any]) -> ParsedTEBase:
    """
    Parsuje NBT TEBase z 1.7.10 do ParsedTEBase.

    Obsługuje zarówno nowe (cbAttrList) jak i stare (cbMetadata jako short) formaty.
    """
    cb_metadata = int(nbt.get("cbMetadata", 0))
    cb_design = str(nbt.get("cbDesign", ""))
    cb_owner = str(nbt.get("cbOwner", ""))

    attrs: dict[int, ParsedAttr] = {}
    attr_list = nbt.get("cbAttrList", [])
    if isinstance(attr_list, list):
        for entry in attr_list:
            if isinstance(entry, dict):
                parsed = _parse_attr_entry(entry)
                if parsed is not None:
                    attrs[parsed.attr_id] = parsed

    return ParsedTEBase(
        cb_metadata=cb_metadata,
        cb_design=cb_design,
        cb_owner=cb_owner,
        attrs=attrs,
    )


# -------------------------------------------------------------------
# Budowanie NBT 1.18.2 (wspólna logika)
# -------------------------------------------------------------------

def _build_base_nbt(te: ParsedTEBase, result: CBConversionResult) -> dict[str, Any]:
    """
    Buduje podstawowy NBT 1.18.2 wspólny dla wszystkich bloków CB.

    Zawsze zawiera:
      coverMaterial  - materiał base cover[6] jako ResourceLocation string
      sideCovers     - tablica 6 ResourceLocation (strony 0..5), opcjonalna
      cbDesign       - wzór dłuta (jeśli był ustawiony)
    """
    nbt: dict[str, Any] = {}

    base = te.base_cover
    if base is None:
        result.add_warning("NO_COVER", "Brak base cover (cbAttribute=6) w cbAttrList")
        nbt["coverBlock"] = "minecraft:oak_planks"  # fallback
    else:
        if base.resolved_id is None:
            result.add_warning(
                "UNKNOWN_MAT",
                f"Nieznany materiał pokrycia: cbUniqueId='{base.cb_unique_id}' damage={base.damage}"
            )
            nbt["coverBlock"] = base.cb_unique_id  # zachowaj oryginalny ID
        else:
            nbt["coverBlock"] = base.resolved_id

    # Per-side covers (strony 0..5 bez base)
    side_covers: list[str | None] = []
    for side in range(6):
        side_attr = te.attrs.get(ATTR_COVER[side])
        if side_attr is not None and side_attr.resolved_id:
            side_covers.append(side_attr.resolved_id)
        else:
            side_covers.append(None)

    if any(s is not None for s in side_covers):
        nbt["sideCovers"] = [s or "" for s in side_covers]

    # Barwniki per strona
    dyes: list[str | None] = []
    for dye_id in ATTR_DYE:
        dye_attr = te.attrs.get(dye_id)
        if dye_attr is not None and dye_attr.cb_unique_id:
            dyes.append(dye_attr.cb_unique_id)
        else:
            dyes.append(None)
    if any(d is not None for d in dyes):
        nbt["sideDyes"] = [d or "" for d in dyes]

    if te.cb_design:
        nbt["cbDesign"] = te.cb_design

    if te.has_illuminator:
        nbt["illuminator"] = True

    return nbt


# -------------------------------------------------------------------
# Konwertery per-blok
# -------------------------------------------------------------------

def _convert_slope(te: ParsedTEBase, result: CBConversionResult) -> None:
    """BlockCarpentersSlope: cbMetadata = slopeID (0..64)."""
    slope_id = te.cb_metadata
    if slope_id not in SLOPE_ID_TO_PROPS:
        result.add_error("GEOM_OOB", f"Nieznany slopeID={slope_id} (dozwolone 0..64)")
        slope_id = 0
    props: SlopeProps = SLOPE_ID_TO_PROPS[slope_id]
    result.blockstate_props["slope_type"] = props.slope_type
    result.blockstate_props["facing"] = props.facing
    result.blockstate_props["half"] = props.half
    result.nbt_1182["facing"] = FACING_TO_FORGE_DIR.get(props.facing, 2)
    result.nbt_1182["shape"] = slope_id
    result.nbt_1182["flags"] = 0


def _convert_stairs(te: ParsedTEBase, result: CBConversionResult) -> None:
    """BlockCarpentersStairs: cbMetadata = stairsID (0..27)."""
    stairs_id = te.cb_metadata
    if stairs_id not in STAIRS_ID_TO_PROPS:
        result.add_error("GEOM_OOB", f"Nieznany stairsID={stairs_id} (dozwolone 0..27)")
        stairs_id = 4  # fallback: NORMAL_NEG_N = bottom+north+straight
    props: StairsProps = STAIRS_ID_TO_PROPS[stairs_id]
    result.blockstate_props["facing"] = props.facing
    result.blockstate_props["half"] = props.half
    result.blockstate_props["shape"] = props.shape
    flags = FLAG_UPPER_HALF if props.half == "top" else 0
    result.nbt_1182["facing"] = FACING_TO_FORGE_DIR.get(props.facing, 2)
    result.nbt_1182["shape"] = stairs_id
    result.nbt_1182["flags"] = flags


def _convert_block(te: ParsedTEBase, result: CBConversionResult) -> None:
    """BlockCarpentersBlock (slab/full): cbMetadata = slabID (0..6)."""
    slab_id = te.cb_metadata
    if slab_id not in SLAB_ID_TO_PROPS:
        result.add_error("GEOM_OOB", f"Nieznany slabID={slab_id} (dozwolone 0..6)")
        slab_id = 0
    props: SlabProps = SLAB_ID_TO_PROPS[slab_id]
    result.blockstate_props["type"] = props.type
    result.nbt_1182["facing"] = 1  # UP
    result.nbt_1182["shape"] = slab_id
    result.nbt_1182["flags"] = 0


def _convert_collapsible(te: ParsedTEBase, result: CBConversionResult) -> None:
    """
    BlockCarpentersCollapsibleBlock:
    cbMetadata layout (Collapsible.java):
      bits 2:0   = direction (ForgeDirection ordinal)
      bits 7:3   = quad XZPP depth (0..16)
      bits 12:8  = quad XZPN depth
      bits 17:13 = quad XZNP depth
      bits 22:18 = quad XZNN depth
    """
    data = te.cb_metadata
    direction_ord = data & 0x7
    depth_xzpp = (data & 0xF8) >> 3
    depth_xzpn = (data & 0x1F00) >> 8
    depth_xznp = (data & 0x3E000) >> 13
    depth_xznn = (data & 0x7C0000) >> 18

    # Clamp depths do 16
    depth_xzpp = min(depth_xzpp, 16)
    depth_xzpn = min(depth_xzpn, 16)
    depth_xznp = min(depth_xznp, 16)
    depth_xznn = min(depth_xznn, 16)

    facing = FORGE_DIR_TO_FACING.get(direction_ord, "up")
    result.blockstate_props["facing"] = facing

    result.nbt_1182["facing"] = direction_ord
    result.nbt_1182["shape"] = 0
    result.nbt_1182["flags"] = 0
    result.nbt_1182["quadDepths"] = [depth_xznn, depth_xznp, depth_xzpn, depth_xzpp]


def _convert_barrier(te: ParsedTEBase, result: CBConversionResult) -> None:
    """
    BlockCarpentersBarrier (Barrier.java):
      bits 3:0 = type (0=vanilla, 1=vanilla_x1, 2=vanilla_x2, 3=vanilla_x3,
                       4=picket, 5=shadowbox, 6=wall)
      bit  4   = has_post
    """
    data = te.cb_metadata
    barrier_type = data & 0xF
    has_post = bool((data & 0x10) >> 4)

    _BARRIER_TYPES = {
        0: "vanilla", 1: "vanilla_x1", 2: "vanilla_x2", 3: "vanilla_x3",
        4: "picket", 5: "shadowbox", 6: "wall",
    }
    result.blockstate_props["barrier_type"] = _BARRIER_TYPES.get(barrier_type, "vanilla")
    result.blockstate_props["post"] = "true" if has_post else "false"
    flags = FLAG_HAS_POST if has_post else 0
    result.nbt_1182["facing"] = 0
    result.nbt_1182["shape"] = barrier_type
    result.nbt_1182["flags"] = flags


def _convert_gate(te: ParsedTEBase, result: CBConversionResult) -> None:
    """
    BlockCarpentersGate (Gate.java):
      bits 3:0  = type (0=vanilla .. 6=wall)
      bit  4    = open_dir (0=pos, 1=neg)
      bit  5    = facing (0=on_x, 1=on_z)
      bit  6    = state (0=closed, 1=open)
    """
    data = te.cb_metadata
    gate_type = data & 0xF
    facing_axis = (data & 0x20) >> 5
    is_open = bool((data & 0x40) >> 6)

    _GATE_TYPES = {
        0: "vanilla", 1: "vanilla_x1", 2: "vanilla_x2", 3: "vanilla_x3",
        4: "picket", 5: "shadowbox", 6: "wall",
    }
    facing_str = "west" if facing_axis == 0 else "north"
    result.blockstate_props["gate_type"] = _GATE_TYPES.get(gate_type, "vanilla")
    result.blockstate_props["facing"] = facing_str
    result.blockstate_props["open"] = "true" if is_open else "false"
    flags = FLAG_STATE if is_open else 0
    result.nbt_1182["facing"] = FACING_TO_FORGE_DIR.get(facing_str, 4)
    result.nbt_1182["shape"] = gate_type
    result.nbt_1182["flags"] = flags


def _convert_hatch(te: ParsedTEBase, result: CBConversionResult) -> None:
    """
    BlockCarpentersHatch (Hatch.java):
      bits 2:0 = type (0=hidden, 1=window, 2=screen, 3=french_window, 4=panel)
      bit  3   = position (0=low, 1=high)
      bit  4   = state (0=closed, 1=open)
      bits 6:5 = dir (0=z_neg→north, 1=z_pos→south, 2=x_neg→west, 3=x_pos→east)
      bit  7   = rigid (0=nonrigid, 1=rigid)
    """
    data = te.cb_metadata
    hatch_type = data & 0x7
    position = (data & 0x8) >> 3
    is_open = bool((data & 0x10) >> 4)
    direction = (data & 0x60) >> 5
    rigid = bool((data & 0x80) >> 7)

    _HATCH_TYPES = {0: "hidden", 1: "window", 2: "screen", 3: "french_window", 4: "panel"}
    _HATCH_DIRS = {0: "north", 1: "south", 2: "west", 3: "east"}

    facing_str = _HATCH_DIRS.get(direction, "north")
    result.blockstate_props["hatch_type"] = _HATCH_TYPES.get(hatch_type, "hidden")
    result.blockstate_props["facing"] = facing_str
    result.blockstate_props["half"] = "top" if position == 1 else "bottom"
    result.blockstate_props["open"] = "true" if is_open else "false"
    result.blockstate_props["rigid"] = "true" if rigid else "false"
    flags = 0
    if is_open:
        flags |= FLAG_STATE
    if position == 1:
        flags |= FLAG_UPPER_HALF
    if rigid:
        flags |= FLAG_RIGID
    result.nbt_1182["facing"] = FACING_TO_FORGE_DIR.get(facing_str, 2)
    result.nbt_1182["shape"] = hatch_type
    result.nbt_1182["flags"] = flags


def _convert_door(te: ParsedTEBase, result: CBConversionResult) -> None:
    """
    BlockCarpentersDoor (Hinge.java):
      bits 2:0 = type (0=glass_top, 1=glass_tall, 2=panels, 3=screen_tall,
                       4=french_glass, 5=hidden)
      bit  3   = hinge (0=left, 1=right)
      bits 5:4 = facing (0=XP→east, 1=ZP→south, 2=XN→west, 3=ZN→north)
      bit  6   = state (0=closed, 1=open)
      bit  7   = piece (0=bottom, 1=top)
      bit  8   = rigid (0=nonrigid, 1=rigid)
    """
    data = te.cb_metadata
    door_type = data & 0x7
    hinge_side = (data & 0x8) >> 3
    facing_id = (data & 0x30) >> 4
    is_open = bool((data & 0x40) >> 6)
    piece = (data & 0x80) >> 7
    rigid = bool((data & 0x100) >> 8)

    _DOOR_TYPES = {
        0: "glass_top", 1: "glass_tall", 2: "panels",
        3: "screen_tall", 4: "french_glass", 5: "hidden",
    }
    _DOOR_FACINGS = {0: "east", 1: "south", 2: "west", 3: "north"}

    facing_str = _DOOR_FACINGS.get(facing_id, "north")
    result.blockstate_props["door_type"] = _DOOR_TYPES.get(door_type, "panels")
    result.blockstate_props["facing"] = facing_str
    result.blockstate_props["hinge"] = "right" if hinge_side == 1 else "left"
    result.blockstate_props["open"] = "true" if is_open else "false"
    result.blockstate_props["half"] = "upper" if piece == 1 else "lower"
    flags = 0
    if is_open:
        flags |= FLAG_STATE
    if piece == 1:
        flags |= FLAG_UPPER_HALF
    if hinge_side == 1:
        flags |= FLAG_RIGHT_HINGE
    if rigid:
        flags |= FLAG_RIGID
    result.nbt_1182["facing"] = FACING_TO_FORGE_DIR.get(facing_str, 2)
    result.nbt_1182["shape"] = door_type
    result.nbt_1182["flags"] = flags


def _convert_ladder(te: ParsedTEBase, result: CBConversionResult) -> None:
    """
    BlockCarpentersLadder (Ladder.java):
      bits 2:0 = direction (ForgeDirection ordinal)
      bits 6:3 = type (0=default, 1=rail, 2=pole)
    """
    data = te.cb_metadata
    dir_ord = data & 0x7
    ladder_type = (data & 0x78) >> 3

    _LADDER_TYPES = {0: "default", 1: "rail", 2: "pole"}
    facing = FORGE_DIR_TO_FACING.get(dir_ord, "north")

    result.blockstate_props["facing"] = facing
    result.blockstate_props["ladder_type"] = _LADDER_TYPES.get(ladder_type, "default")
    result.nbt_1182["facing"] = dir_ord
    result.nbt_1182["shape"] = ladder_type
    result.nbt_1182["flags"] = 0


def _convert_lever(te: ParsedTEBase, result: CBConversionResult) -> None:
    """
    BlockCarpentersLever (Lever.java):
      bits 2:0 = direction (ForgeDirection ordinal)
      bit  3   = state (0=off, 1=on)
      bit  4   = polarity (0=positive, 1=negative)
      bit  6   = axis (0=X, 1=Z)
    """
    data = te.cb_metadata
    dir_ord = data & 0x7
    powered = bool((data & 0x8) >> 3)
    polarity_neg = bool((data & 0x10) >> 4)
    axis_z = bool((data & 0x40) >> 6)

    facing = FORGE_DIR_TO_FACING.get(dir_ord, "north")
    result.blockstate_props["facing"] = facing
    result.blockstate_props["powered"] = "true" if powered else "false"
    result.blockstate_props["face"] = "wall" if dir_ord >= 2 else (
        "ceiling" if dir_ord == 0 else "floor"
    )
    result.blockstate_props["polarity"] = "true" if polarity_neg else "false"
    flags = 0
    if powered:
        flags |= FLAG_STATE
    if polarity_neg:
        flags |= FLAG_POLARITY_NEG
    result.nbt_1182["facing"] = dir_ord
    result.nbt_1182["shape"] = 0
    result.nbt_1182["flags"] = flags


def _convert_button(te: ParsedTEBase, result: CBConversionResult) -> None:
    """
    BlockCarpentersButton (Button.java):
      bits 2:0 = direction (ForgeDirection ordinal)
      bit  3   = state (0=off, 1=on)
      bit  4   = polarity (0=positive, 1=negative)
    """
    data = te.cb_metadata
    dir_ord = data & 0x7
    powered = bool((data & 0x8) >> 3)
    polarity_neg = bool((data & 0x10) >> 4)

    facing = FORGE_DIR_TO_FACING.get(dir_ord, "north")
    result.blockstate_props["facing"] = facing
    result.blockstate_props["powered"] = "true" if powered else "false"
    result.blockstate_props["face"] = "wall" if dir_ord >= 2 else (
        "ceiling" if dir_ord == 0 else "floor"
    )
    flags = 0
    if powered:
        flags |= FLAG_STATE
    if polarity_neg:
        flags |= FLAG_POLARITY_NEG
    result.nbt_1182["facing"] = dir_ord
    result.nbt_1182["shape"] = 0
    result.nbt_1182["flags"] = flags


def _convert_pressure_plate(te: ParsedTEBase, result: CBConversionResult) -> None:
    """
    BlockCarpentersPressurePlate: używa ISided, dir = ForgeDirection.
    cbMetadata = ForgeDirection ordinal strony (kierunek mocowania).
    """
    data = te.cb_metadata
    dir_ord = data & 0x7
    powered = bool((data & 0x8) >> 3)

    result.blockstate_props["powered"] = "true" if powered else "false"
    result.nbt_1182["facing"] = dir_ord
    result.nbt_1182["shape"] = 0
    result.nbt_1182["flags"] = FLAG_STATE if powered else 0


def _convert_torch(te: ParsedTEBase, result: CBConversionResult) -> None:
    """
    BlockCarpentersTorch (Torch.java):
      bits 2:0  = direction (ForgeDirection ordinal)
      bits 4:3  = state (0=lit, 1=smoldering, 2=unlit)
      bits 8:5  = type (0=vanilla, 1=lantern)
    """
    data = te.cb_metadata
    dir_ord = data & 0x7
    state_ord = (data & 0x18) >> 3
    torch_type = (data & 0x1E0) >> 5

    _TORCH_TYPES = {0: "vanilla", 1: "lantern"}

    facing = FORGE_DIR_TO_FACING.get(dir_ord, "up")
    result.blockstate_props["facing"] = facing
    result.blockstate_props["lit"] = "false" if state_ord == 2 else "true"
    result.blockstate_props["torch_type"] = _TORCH_TYPES.get(torch_type, "vanilla")
    flags = FLAG_SMOLDERING if state_ord == 1 else 0
    result.nbt_1182["facing"] = dir_ord
    result.nbt_1182["shape"] = torch_type
    result.nbt_1182["flags"] = flags


def _convert_daylight_sensor(te: ParsedTEBase, result: CBConversionResult) -> None:
    """
    BlockCarpentersDaylightSensor (DaylightSensor.java):
      bits 3:0  = light_level (0..15)
      bit  4    = polarity (0=positive, 1=negative)
      bits 6:5  = sensitivity (0=sleep, 1=monsters, 2=dynamic)
      bits 9:7  = direction (ForgeDirection ordinal)
    """
    data = te.cb_metadata
    light_level = data & 0xF
    polarity_neg = bool((data & 0x10) >> 4)
    sensitivity = (data & 0x60) >> 5
    dir_ord = (data & 0x380) >> 7

    _SENSITIVITY = {0: "sleep", 1: "monsters", 2: "dynamic"}
    facing = FORGE_DIR_TO_FACING.get(dir_ord, "up")

    result.blockstate_props["facing"] = facing
    result.blockstate_props["inverted"] = "true" if polarity_neg else "false"
    result.blockstate_props["power"] = str(light_level)
    result.blockstate_props["sensitivity"] = _SENSITIVITY.get(sensitivity, "dynamic")
    flags = FLAG_POLARITY_NEG if polarity_neg else 0
    result.nbt_1182["facing"] = dir_ord
    result.nbt_1182["shape"] = sensitivity
    result.nbt_1182["flags"] = flags
    result.nbt_1182["lightLevel"] = light_level


def _convert_bed(te: ParsedTEBase, result: CBConversionResult) -> None:
    """
    BlockCarpentersBed: cbMetadata zakodowany jak vanilla bed metadata.
      bits 1:0 = facing (0=south, 1=west, 2=north, 3=east)
      bit  2   = occupied (0=false, 1=true)
      bit  3   = part (0=foot, 1=head)
    """
    data = te.cb_metadata
    facing_id = data & 0x3
    occupied = bool((data & 0x4) >> 2)
    part = (data & 0x8) >> 3

    _BED_FACINGS = {0: "south", 1: "west", 2: "north", 3: "east"}
    facing_str = _BED_FACINGS.get(facing_id, "north")

    result.blockstate_props["facing"] = facing_str
    result.blockstate_props["part"] = "head" if part == 1 else "foot"
    result.blockstate_props["occupied"] = "true" if occupied else "false"
    flags = FLAG_UPPER_HALF if part == 1 else 0
    result.nbt_1182["facing"] = facing_id
    result.nbt_1182["shape"] = 0
    result.nbt_1182["flags"] = flags
    result.nbt_1182["cbMetadataRaw"] = te.cb_metadata


def _convert_multiblock(
        te: ParsedTEBase, result: CBConversionResult, block_name: str
) -> None:
    """
    Uproszczona konwersja bloków wielosegmentowych (GarageDoor).
    Zachowujemy cbMetadata jako surową wartość w NBT dla przyszłego modułu.
    """
    result.add_warning("MULTIBLOCK", f"{block_name}: blok wielosegmentowy - uproszczona konwersja")
    result.nbt_1182["cbMetadataRaw"] = te.cb_metadata
    result.nbt_1182["facing"] = 0
    result.nbt_1182["shape"] = 0
    result.nbt_1182["flags"] = 0


def _convert_safe(te: ParsedTEBase, result: CBConversionResult) -> None:
    """BlockCarpentersSafe: tylko cover, brak specjalnej geometrii."""
    result.nbt_1182["facing"] = 0
    result.nbt_1182["shape"] = 0
    result.nbt_1182["flags"] = 0


def _convert_flower_pot(te: ParsedTEBase, result: CBConversionResult) -> None:
    """BlockCarpentersFlowerPot: cover + plant attr."""
    plant_attr = te.attrs.get(22)  # ATTR_PLANT
    if plant_attr and plant_attr.resolved_id:
        result.nbt_1182["plantBlock"] = plant_attr.resolved_id
    soil_attr = te.attrs.get(23)  # ATTR_SOIL
    if soil_attr and soil_attr.resolved_id:
        result.nbt_1182["soilBlock"] = soil_attr.resolved_id
    result.nbt_1182["facing"] = 0
    result.nbt_1182["shape"] = 0
    result.nbt_1182["flags"] = 0


# -------------------------------------------------------------------
# Dispatcher - główna klasa
# -------------------------------------------------------------------

# Mapowanie block_id_1710 -> funkcja konwertera
_GEOMETRY_CONVERTERS: dict[str, Any] = {
    "CarpentersBlocks:blockCarpentersSlope": _convert_slope,
    "CarpentersBlocks:blockCarpentersStairs": _convert_stairs,
    "CarpentersBlocks:blockCarpentersBlock": _convert_block,
    "CarpentersBlocks:blockCarpentersCollapsibleBlock": _convert_collapsible,
    "CarpentersBlocks:blockCarpentersBarrier": _convert_barrier,
    "CarpentersBlocks:blockCarpentersGate": _convert_gate,
    "CarpentersBlocks:blockCarpentersHatch": _convert_hatch,
    "CarpentersBlocks:blockCarpentersDoor": _convert_door,
    "CarpentersBlocks:blockCarpentersLadder": _convert_ladder,
    "CarpentersBlocks:blockCarpentersLever": _convert_lever,
    "CarpentersBlocks:blockCarpentersButton": _convert_button,
    "CarpentersBlocks:blockCarpentersPressurePlate": _convert_pressure_plate,
    "CarpentersBlocks:blockCarpentersTorch": _convert_torch,
    "CarpentersBlocks:blockCarpentersDaylightSensor": _convert_daylight_sensor,
    "CarpentersBlocks:blockCarpentersSafe": _convert_safe,
    "CarpentersBlocks:blockCarpentersFlowerPot": _convert_flower_pot,
    # Multiblock
    "CarpentersBlocks:blockCarpentersBed": _convert_bed,
    "CarpentersBlocks:blockCarpentersGarageDoor":
        lambda te, r: _convert_multiblock(te, r, "GarageDoor"),
}


class CBBlockConverter:
    """
    Główny konwerter bloków CarpentersBlocks.

    Użycie:
        converter = CBBlockConverter()
        result = converter.convert("CarpentersBlocks:blockCarpentersSlope", te_nbt)
        if result.success:
            block_id_1182 = result.block_id_1182
            props = result.blockstate_props
            nbt = result.nbt_1182
    """

    def convert(
        self,
        block_id_1710: str,
        te_nbt: dict[str, Any],
    ) -> CBConversionResult:
        """
        Konwertuje jeden blok CB.

        Args:
            block_id_1710: ID bloku w 1.7.10 (np. "CarpentersBlocks:blockCarpentersSlope")
            te_nbt:        Słownik NBT TileEntity z 1.7.10 (cbAttrList, cbMetadata, …)

        Returns:
            CBConversionResult z block_id_1182, blockstate_props, nbt_1182.
        """
        result = CBConversionResult(success=True, block_id_1710=block_id_1710)

        # Sprawdź czy blok jest znany
        if block_id_1710 not in ALL_CB_BLOCK_IDS_1710:
            result.add_error(
                "UNKNOWN_BLOCK",
                f"Nieznany block_id_1710: '{block_id_1710}'"
            )
            return result

        # Docelowy ID bloku 1.18.2
        result.block_id_1182 = CB_BLOCK_TO_CB1182.get(block_id_1710)

        # Sparsuj TEBase
        te = parse_te_base(te_nbt)

        # Zbuduj bazowy NBT (cover materials)
        result.nbt_1182 = _build_base_nbt(te, result)
        result.nbt_1182["sourceCarpentersTeId"] = block_id_1710

        # Wywołaj konwerter specyficzny dla bloku
        converter_fn = _GEOMETRY_CONVERTERS.get(block_id_1710)
        if converter_fn is not None:
            converter_fn(te, result)

        return result

    def convert_bulk(
        self,
        blocks: list[tuple[str, dict[str, Any]]],
    ) -> list[CBConversionResult]:
        """
        Konwertuje listę bloków (block_id_1710, te_nbt).
        """
        return [self.convert(bid, nbt) for bid, nbt in blocks]
