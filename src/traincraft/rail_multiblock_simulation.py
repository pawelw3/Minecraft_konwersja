"""
Simulation of Traincraft 1.7.10 multiblock rail system (tcRail + tcRailGag).
Source: train.common.blocks.BlockTCRail, BlockTCRailGag
        train.common.tile.TileTCRail, TileTCRailGag
        train.common.items.ItemTCRail (putDownTurn)

This simulates:
- How turns/switches are physically composed of 1 tcRail + N tcRailGag blocks
- Link destruction (breaking main rail destroys gags, breaking gag destroys main)
- NBT serialization of linked positions
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class TileTCRail:
    x: int = 0
    y: int = 0
    z: int = 0
    rail_type: str = "SMALL_STRAIGHT"
    facing_meta: int = 0

    is_linked_to_rail: bool = False
    linked_x: int = 0
    linked_y: int = 0
    linked_z: int = 0

    r: float = 0.0
    cx: float = 0.0
    cy: float = 0.0
    cz: float = 0.0

    slope_height: float = 0.0
    slope_length: float = 0.0
    slope_angle: float = 0.0

    switch_active: bool = False
    can_type_be_modified_by_switch: bool = False
    previous_redstone_state: bool = False
    has_model: bool = True
    id_drop: Optional[str] = None

    def to_nbt(self) -> dict:
        """Replicates TileTCRail.writeToNBT() logic."""
        return {
            "Orientation": self.facing_meta,
            "r": self.r,
            "cx": self.cx,
            "cy": self.cy,
            "cz": self.cz,
            "slopeHeight": self.slope_height,
            "slopeLength": self.slope_length,
            "slopeAngle": self.slope_angle,
            "linkedX": self.linked_x,
            "linkedY": self.linked_y,
            "linkedZ": self.linked_z,
            "type": self.rail_type,
            "isLinkedToRail": self.is_linked_to_rail,
            "hasModel": self.has_model,
            "switchActive": self.switch_active,
            "canTypeBeModifiedBySwitch": self.can_type_be_modified_by_switch,
            "manualOverride": False,
            "hasRotated": False,
            "previousRedstoneState": self.previous_redstone_state,
            "idDrop": self.id_drop or "",
        }


@dataclass
class TileTCRailGag:
    x: int = 0
    y: int = 0
    z: int = 0
    origin_x: int = 0
    origin_y: int = 0
    origin_z: int = 0
    type: str = "null"
    bb_height: float = 0.125

    def to_nbt(self) -> dict:
        """Replicates TileTCRailGag.writeToNBT() logic."""
        t = self.type if self.type else "null"
        return {
            "originX": self.origin_x,
            "originY": self.origin_y,
            "originZ": self.origin_z,
            "bbHeight": self.bb_height,
            "type": t,
        }


@dataclass
class SimulatedWorld:
    rails: Dict[Tuple[int, int, int], TileTCRail] = field(default_factory=dict)
    gags: Dict[Tuple[int, int, int], TileTCRailGag] = field(default_factory=dict)
    events: List[str] = field(default_factory=list)

    def place_tc_rail(self, x: int, y: int, z: int, tile: TileTCRail) -> None:
        self.rails[(x, y, z)] = tile
        tile.x, tile.y, tile.z = x, y, z

    def place_tc_gag(self, x: int, y: int, z: int, tile: TileTCRailGag) -> None:
        self.gags[(x, y, z)] = tile
        tile.x, tile.y, tile.z = x, y, z

    def break_block(self, x: int, y: int, z: int) -> List[str]:
        """
        Simulates BlockTCRail.breakBlock() and BlockTCRailGag.breakBlock().
        """
        events = []
        pos = (x, y, z)

        # If breaking a tcRail
        if pos in self.rails:
            tile = self.rails[pos]
            events.append(f"Break tcRail at ({x},{y},{z}) type={tile.rail_type}")

            # If linked to another rail, destroy the linked rail too
            if tile.is_linked_to_rail:
                lx, ly, lz = tile.linked_x, tile.linked_y, tile.linked_z
                events.append(f"  -> Linked rail destroyed at ({lx},{ly},{lz})")
                self._remove_rail(lx, ly, lz)
                self._remove_gags_linked_to(lx, ly, lz)

            # Remove this rail and its gags
            self._remove_rail(x, y, z)
            self._remove_gags_linked_to(x, y, z)

        # If breaking a tcRailGag
        elif pos in self.gags:
            tile = self.gags[pos]
            events.append(f"Break tcRailGag at ({x},{y},{z}) origin=({tile.origin_x},{tile.origin_y},{tile.origin_z})")

            # Destroy the origin rail
            ox, oy, oz = tile.origin_x, tile.origin_y, tile.origin_z
            events.append(f"  -> Origin rail destroyed at ({ox},{oy},{oz})")
            self._remove_rail(ox, oy, oz)
            self._remove_gags_linked_to(ox, oy, oz)

        return events

    def _remove_rail(self, x: int, y: int, z: int) -> None:
        self.rails.pop((x, y, z), None)

    def _remove_gags_linked_to(self, ox: int, oy: int, oz: int) -> None:
        to_remove = [pos for pos, gag in self.gags.items()
                     if gag.origin_x == ox and gag.origin_y == oy and gag.origin_z == oz]
        for pos in to_remove:
            del self.gags[pos]
            self.events.append(f"  -> Gag removed at {pos}")

    def get_block_counts(self) -> Tuple[int, int]:
        return len(self.rails), len(self.gags)


def build_medium_turn(world: SimulatedWorld, bx: int, by: int, bz: int) -> None:
    """
    Replicates MEDIUM_RIGHT_TURN placement (facingMeta=2, from ItemTCRail.java).
    xArray = {x, x, x+1, x+1, x+2}
    zArray = {z, z-1, z-1, z-2, z-2}
    putDownEnterTrack=false, putDownExitTrack=false
    """
    positions = [
        (bx, bz, True),      # main tcRail at (0,0)
        (bx, bz - 1, False), # gag
        (bx + 1, bz - 1, False),
        (bx + 1, bz - 2, False),
        (bx + 2, bz - 2, False),
    ]

    main_pos = None
    for i, (px, pz, is_main) in enumerate(positions):
        if is_main:
            tile = TileTCRail(
                x=px, y=by, z=pz,
                rail_type="MEDIUM_RIGHT_TURN",
                facing_meta=2,
                r=2.5,
                cx=bx + 3,
                cy=by + 1,
                cz=bz + 1,
                id_drop="tcRailMediumTurn",
            )
            world.place_tc_rail(px, by, pz, tile)
            main_pos = (px, by, pz)
        else:
            gag = TileTCRailGag(x=px, y=by, z=pz)
            world.place_tc_gag(px, by, pz, gag)

    # Link gags to main rail
    if main_pos:
        mx, my, mz = main_pos
        for pos, gag in world.gags.items():
            if gag.y == by and (gag.x, gag.z) in [(p[0], p[1]) for p in positions[1:]]:
                gag.origin_x, gag.origin_y, gag.origin_z = mx, my, mz
                gag.type = "MEDIUM_RIGHT_TURN"


def build_slope(world: SimulatedWorld, bx: int, by: int, bz: int, length: int = 6) -> None:
    """
    Replicates SLOPE_WOOD placement (facingMeta=2).
    1 tcRail + (length-1) gags with increasing bbHeight.
    """
    tile = TileTCRail(
        x=bx, y=by, z=bz,
        rail_type="SLOPE_WOOD",
        facing_meta=2,
        slope_height=1.0,
        slope_angle=0.13,
        slope_length=length,
        id_drop="tcRailSlopeWood",
    )
    world.place_tc_rail(bx, by, bz, tile)

    for i in range(1, length):
        pz = bz - i
        bb = max(0.125, min(1.0, i / (length - 1)))
        gag = TileTCRailGag(
            x=bx, y=by, z=pz,
            origin_x=bx, origin_y=by, origin_z=bz,
            type="SLOPE_WOOD",
            bb_height=bb,
        )
        world.place_tc_gag(bx, by, pz, gag)


def demo_multiblock_turn() -> None:
    print("=" * 60)
    print("DEMO: Multiblock MEDIUM_RIGHT_TURN")
    print("=" * 60)

    world = SimulatedWorld()
    build_medium_turn(world, 0, 10, 0)

    rails, gags = world.get_block_counts()
    print(f"Placed: {rails} tcRail + {gags} tcRailGag = {rails + gags} total blocks")

    for pos, tile in sorted(world.rails.items()):
        print(f"  tcRail at {pos}: type={tile.rail_type}, r={tile.r}, cx={tile.cx}, cz={tile.cz}")
    for pos, gag in sorted(world.gags.items()):
        print(f"  tcRailGag at {pos}: origin=({gag.origin_x},{gag.origin_y},{gag.origin_z}), type={gag.type}")

    # Break main rail -> all gags should be destroyed
    print("\n-- Breaking MAIN rail at (0,10,0) --")
    events = world.break_block(0, 10, 0)
    for e in events:
        print(f"  {e}")
    rails, gags = world.get_block_counts()
    print(f"Remaining: {rails} tcRail + {gags} tcRailGag")
    print()


def demo_multiblock_gag_break() -> None:
    print("=" * 60)
    print("DEMO: Breaking a GAG destroys origin rail")
    print("=" * 60)

    world = SimulatedWorld()
    build_medium_turn(world, 10, 10, 10)

    rails, gags = world.get_block_counts()
    print(f"Initial: {rails} tcRail + {gags} tcRailGag")

    # Break a gag at (11,10,9)
    print("\n-- Breaking GAG at (11,10,9) --")
    events = world.break_block(11, 10, 9)
    for e in events:
        print(f"  {e}")
    rails, gags = world.get_block_counts()
    print(f"Remaining: {rails} tcRail + {gags} tcRailGag")
    print()


def demo_slope_nbt() -> None:
    print("=" * 60)
    print("DEMO: SLOPE_WOOD NBT serialization")
    print("=" * 60)

    world = SimulatedWorld()
    build_slope(world, 0, 10, 0, length=6)

    main = world.rails[(0, 10, 0)]
    print("Main rail NBT:")
    for k, v in main.to_nbt().items():
        print(f"  {k}: {v}")

    print("\nGag NBT samples:")
    for pos, gag in sorted(world.gags.items())[:3]:
        print(f"  Gag at {pos}: {gag.to_nbt()}")
    print()


def demo_linked_rail_break() -> None:
    """
    Simulate a switch rail where tcRail is linked to another tcRail.
    Breaking one destroys the other.
    """
    print("=" * 60)
    print("DEMO: Linked rails (switch with linked exit)")
    print("=" * 60)

    world = SimulatedWorld()

    # Main switch rail
    switch = TileTCRail(x=0, y=10, z=0, rail_type="MEDIUM_RIGHT_SWITCH",
                        facing_meta=2, is_linked_to_rail=True,
                        linked_x=3, linked_y=10, linked_z=-3)
    world.place_tc_rail(0, 10, 0, switch)

    # Linked exit rail
    exit_rail = TileTCRail(x=3, y=10, z=-3, rail_type="SMALL_STRAIGHT",
                           facing_meta=1, is_linked_to_rail=True,
                           linked_x=0, linked_y=10, linked_z=0)
    world.place_tc_rail(3, 10, -3, exit_rail)

    print("Initial: 2 linked tcRails")
    print(f"  Switch at (0,10,0) linked to ({switch.linked_x},{switch.linked_y},{switch.linked_z})")
    print(f"  Exit at (3,10,-3) linked to ({exit_rail.linked_x},{exit_rail.linked_y},{exit_rail.linked_z})")

    print("\n-- Breaking switch at (0,10,0) --")
    events = world.break_block(0, 10, 0)
    for e in events:
        print(f"  {e}")

    rails, gags = world.get_block_counts()
    print(f"Remaining: {rails} tcRail")
    print()


if __name__ == "__main__":
    demo_multiblock_turn()
    demo_multiblock_gag_break()
    demo_slope_nbt()
    demo_linked_rail_break()
