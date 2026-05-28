"""
Simulation of Traincraft 1.7.10 switch logic based on exact source code.
Source: train.common.tile.TileTCRail (TileTCRail.java)
       train.common.items.ItemTCRail (ItemTCRail.java)

This simulates:
- Switch types: MEDIUM_RIGHT_SWITCH, MEDIUM_LEFT_SWITCH, LARGE_RIGHT_SWITCH,
  LARGE_LEFT_SWITCH, MEDIUM_RIGHT_PARALLEL_SWITCH, MEDIUM_LEFT_PARALLEL_SWITCH
- Redstone state changes
- Manual override (minecart detection)
- changeSwitchState() which mutates neighbor rail types (SMALL_STRAIGHT <-> TURN)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class TrackType(Enum):
    SMALL_STRAIGHT = "SMALL_STRAIGHT"
    MEDIUM_STRAIGHT = "MEDIUM_STRAIGHT"
    LONG_STRAIGHT = "LONG_STRAIGHT"
    MEDIUM_RIGHT_TURN = "MEDIUM_RIGHT_TURN"
    MEDIUM_LEFT_TURN = "MEDIUM_LEFT_TURN"
    LARGE_RIGHT_TURN = "LARGE_RIGHT_TURN"
    LARGE_LEFT_TURN = "LARGE_LEFT_TURN"
    MEDIUM_RIGHT_SWITCH = "MEDIUM_RIGHT_SWITCH"
    MEDIUM_LEFT_SWITCH = "MEDIUM_LEFT_SWITCH"
    LARGE_RIGHT_SWITCH = "LARGE_RIGHT_SWITCH"
    LARGE_LEFT_SWITCH = "LARGE_LEFT_SWITCH"
    MEDIUM_RIGHT_PARALLEL_SWITCH = "MEDIUM_RIGHT_PARALLEL_SWITCH"
    MEDIUM_LEFT_PARALLEL_SWITCH = "MEDIUM_LEFT_PARALLEL_SWITCH"


SWITCH_TYPES = {
    TrackType.MEDIUM_RIGHT_SWITCH,
    TrackType.MEDIUM_LEFT_SWITCH,
    TrackType.LARGE_RIGHT_SWITCH,
    TrackType.LARGE_LEFT_SWITCH,
    TrackType.MEDIUM_RIGHT_PARALLEL_SWITCH,
    TrackType.MEDIUM_LEFT_PARALLEL_SWITCH,
}

# Mapping: which TURN type is used when switch is active
SWITCH_TO_TURN = {
    TrackType.MEDIUM_RIGHT_SWITCH: TrackType.MEDIUM_RIGHT_TURN,
    TrackType.MEDIUM_LEFT_SWITCH: TrackType.MEDIUM_LEFT_TURN,
    TrackType.LARGE_RIGHT_SWITCH: TrackType.LARGE_RIGHT_TURN,
    TrackType.LARGE_LEFT_SWITCH: TrackType.LARGE_LEFT_TURN,
    TrackType.MEDIUM_RIGHT_PARALLEL_SWITCH: TrackType.MEDIUM_RIGHT_TURN,
    TrackType.MEDIUM_LEFT_PARALLEL_SWITCH: TrackType.MEDIUM_LEFT_TURN,
}

# From ItemTCRail.java: which neighbor offsets are modified per facingMeta
# For MEDIUM_SWITCH (facingMeta 0=N,1=E,2=S,3=W in Minecraft terms but here 0=S,1=W,2=N,3=E based on code)
# Actually from code:
# facingMeta 0 -> neighbor at z+1 (south)
# facingMeta 1 -> neighbor at x-1 (west)
# facingMeta 2 -> neighbor at z-1 (north)
# facingMeta 3 -> neighbor at x+1 (east)
NEIGHBOR_OFFSET = {
    0: (0, 0, 1),
    1: (-1, 0, 0),
    2: (0, 0, -1),
    3: (1, 0, 0),
}

# For LARGE_SWITCH and PARALLEL_SWITCH, a second neighbor at distance 2 is also modified
SECOND_NEIGHBOR_OFFSET = {
    0: (0, 0, 2),
    1: (-2, 0, 0),
    2: (0, 0, -2),
    3: (2, 0, 0),
}


@dataclass
class SimulatedWorld:
    """Simplified world grid storing TileTCRail at positions."""
    rails: Dict[Tuple[int, int, int], "TileTCRail"] = field(default_factory=dict)
    redstone_power: Dict[Tuple[int, int, int], bool] = field(default_factory=dict)

    def get_tile(self, x: int, y: int, z: int) -> Optional["TileTCRail"]:
        return self.rails.get((x, y, z))

    def set_tile(self, x: int, y: int, z: int, tile: "TileTCRail") -> None:
        self.rails[(x, y, z)] = tile
        tile.x = x
        tile.y = y
        tile.z = z

    def is_block_indirectly_getting_powered(self, x: int, y: int, z: int) -> bool:
        return self.redstone_power.get((x, y, z), False)

    def remove_tile(self, x: int, y: int, z: int) -> None:
        self.rails.pop((x, y, z), None)


@dataclass
class TileTCRail:
    """
    Python simulation of Traincraft's TileTCRail.
    Replicates key fields and logic from TileTCRail.java.
    """
    x: int = 0
    y: int = 0
    z: int = 0
    rail_type: TrackType = TrackType.SMALL_STRAIGHT
    facing_meta: int = 0  # 0,1,2,3

    # Switch state
    switch_active: bool = False
    previous_redstone_state: bool = False
    manual_override: bool = False
    can_type_be_modified_by_switch: bool = False

    # Multiblock links
    is_linked_to_rail: bool = False
    linked_x: int = 0
    linked_y: int = 0
    linked_z: int = 0

    # Curve parameters (for turns)
    r: float = 0.0
    cx: float = 0.0
    cy: float = 0.0
    cz: float = 0.0

    # Slope parameters
    slope_height: float = 0.0
    slope_length: float = 0.0
    slope_angle: float = 0.0

    # Drop item
    id_drop: Optional[str] = None

    # Ticking
    update_ticks: int = 0
    update_ticks2: int = 0
    has_rotated: bool = False
    is_left_flag: int = -5

    def get_type(self) -> TrackType:
        return self.rail_type

    def set_type(self, new_type: TrackType) -> None:
        self.rail_type = new_type
        # In real code: worldObj.markBlockForUpdate(xCoord, yCoord, zCoord)

    def get_switch_state(self) -> bool:
        return self.switch_active

    def set_switch_state(self, state: bool, manual_override: bool) -> None:
        self.switch_active = state
        self.manual_override = manual_override
        if manual_override:
            self.update_ticks = 0

    def is_switch(self) -> bool:
        return self.rail_type in SWITCH_TYPES

    def update_entity(self, world: SimulatedWorld) -> List[str]:
        """
        Simulates TileTCRail.updateEntity() logic.
        Returns list of log messages describing what happened.
        """
        logs = []

        if not self.can_type_be_modified_by_switch:
            return logs

        self.update_ticks2 += 1

        # Check redstone state every 11 ticks (from original code: updateTicks2 % 11 == 0)
        if self.update_ticks2 % 11 == 0:
            self.update_ticks2 = 0
            tile1 = self._get_neighbor_tile(world, 1)  # Check neighbor based on facing

            if tile1 and tile1.is_switch():
                flag1 = world.is_block_indirectly_getting_powered(self.x, self.y, self.z)
                if tile1.previous_redstone_state != flag1:
                    tile1.change_switch_state(world, tile1, tile1.x, tile1.y, tile1.z)
                    tile1.previous_redstone_state = flag1
                    logs.append(f"Redstone triggered switch at ({tile1.x},{tile1.y},{tile1.z})")

        # Manual override countdown (minecart detection simulation)
        if self.manual_override:
            self.update_ticks += 1
            if self.update_ticks > 60:
                # Original: check for minecarts in bounding box
                # Simulated: always clear after timeout for simplicity
                self.manual_override = False
                self.change_switch_state(world, self, self.x, self.y, self.z)
                self.set_switch_state(self.previous_redstone_state, False)
                self.update_ticks = 0
                logs.append(f"Manual override expired at ({self.x},{self.y},{self.z})")

        # Train proximity auto-switch (for non-active switches)
        if not self.get_switch_state() and self.update_ticks2 % 10 == 0:
            if self._detect_train_proximity(world):
                self.change_switch_state(world, self, self.x, self.y, self.z)
                self.set_switch_state(True, True)
                logs.append(f"Train proximity triggered switch at ({self.x},{self.y},{self.z})")

        return logs

    def _get_neighbor_tile(self, world: SimulatedWorld, distance: int = 1) -> Optional["TileTCRail"]:
        """Get neighbor tile based on facingMeta."""
        dx, dy, dz = NEIGHBOR_OFFSET[self.facing_meta]
        nx = self.x + dx * distance
        ny = self.y + dy * distance
        nz = self.z + dz * distance
        tile = world.get_tile(nx, ny, nz)
        return tile if isinstance(tile, TileTCRail) else None

    def _detect_train_proximity(self, world: SimulatedWorld) -> bool:
        """
        Simulates train proximity detection from updateEntity().
        Original uses AABB checks; here we simulate based on isLeftFlag and facing.
        """
        if self.is_left_flag == -5:
            if self.rail_type in {
                TrackType.MEDIUM_RIGHT_SWITCH,
                TrackType.LARGE_RIGHT_SWITCH,
                TrackType.MEDIUM_RIGHT_PARALLEL_SWITCH,
            }:
                self.is_left_flag = 1
            elif self.rail_type in {
                TrackType.MEDIUM_LEFT_SWITCH,
                TrackType.LARGE_LEFT_SWITCH,
                TrackType.MEDIUM_LEFT_PARALLEL_SWITCH,
            }:
                self.is_left_flag = -1
            else:
                self.is_left_flag = 0

        if self.is_left_flag == 0:
            return False

        # Simulated: return True every 3rd check to show behavior
        # In real code this checks EntityMinecart AABB intersection
        return (self.x + self.y + self.z + self.update_ticks2) % 30 == 0

    def change_switch_state(self, world: SimulatedWorld, tile_entity: "TileTCRail",
                           i: int, j: int, k: int) -> List[str]:
        """
        Replicates TileTCRail.changeSwitchState() from source code.
        This is the CRITICAL method for conversion: it shows how switch rails
        mutate their neighbor types between SMALL_STRAIGHT and TURN.
        """
        logs = []
        if not tile_entity.is_switch():
            return logs

        turn_type = SWITCH_TO_TURN.get(tile_entity.rail_type)
        if not turn_type:
            return logs

        meta = tile_entity.facing_meta

        if tile_entity.get_switch_state():
            # DEACTIVATE: switch was ON, turn neighbors back to SMALL_STRAIGHT
            tile_entity.set_switch_state(False, False)
            self._set_neighbor_type(world, tile_entity, meta, 1, TrackType.SMALL_STRAIGHT, logs)

            # For parallel and large switches, also modify second neighbor
            if tile_entity.rail_type in {
                TrackType.MEDIUM_RIGHT_PARALLEL_SWITCH,
                TrackType.MEDIUM_LEFT_PARALLEL_SWITCH,
                TrackType.LARGE_RIGHT_SWITCH,
                TrackType.LARGE_LEFT_SWITCH,
            }:
                self._set_neighbor_type(world, tile_entity, meta, 2, TrackType.SMALL_STRAIGHT, logs)

        else:
            # ACTIVATE: switch was OFF, turn neighbors to TURN type
            tile_entity.set_switch_state(True, False)
            self._set_neighbor_type(world, tile_entity, meta, 1, turn_type, logs)

            if tile_entity.rail_type in {
                TrackType.MEDIUM_RIGHT_PARALLEL_SWITCH,
                TrackType.MEDIUM_LEFT_PARALLEL_SWITCH,
                TrackType.LARGE_RIGHT_SWITCH,
                TrackType.LARGE_LEFT_SWITCH,
            }:
                self._set_neighbor_type(world, tile_entity, meta, 2, turn_type, logs)

        logs.append(f"Switch at ({i},{j},{k}) -> {'ON' if tile_entity.switch_active else 'OFF'}")
        return logs

    def _set_neighbor_type(self, world: SimulatedWorld, switch_tile: "TileTCRail",
                           meta: int, distance: int, new_type: TrackType, logs: List[str]) -> None:
        offset = NEIGHBOR_OFFSET if distance == 1 else SECOND_NEIGHBOR_OFFSET
        dx, dy, dz = offset[meta]
        nx = switch_tile.x + dx
        ny = switch_tile.y + dy
        nz = switch_tile.z + dz
        neighbor = world.get_tile(nx, ny, nz)
        if neighbor and isinstance(neighbor, TileTCRail):
            old_type = neighbor.rail_type
            neighbor.set_type(new_type)
            logs.append(f"  Neighbor at ({nx},{ny},{nz}): {old_type.value} -> {new_type.value}")

    def to_nbt_dict(self) -> dict:
        """Simulates NBT serialization (writeToNBT)."""
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
            "type": self.rail_type.value,
            "isLinkedToRail": self.is_linked_to_rail,
            "hasModel": True,
            "switchActive": self.switch_active,
            "canTypeBeModifiedBySwitch": self.can_type_be_modified_by_switch,
            "manualOverride": self.manual_override,
            "hasRotated": self.has_rotated,
            "previousRedstoneState": self.previous_redstone_state,
        }


def demo_medium_right_switch() -> None:
    """Demonstrate MEDIUM_RIGHT_SWITCH behavior."""
    print("=" * 60)
    print("DEMO: MEDIUM_RIGHT_SWITCH")
    print("=" * 60)

    world = SimulatedWorld()

    # Place switch at (0, 10, 0) facing north (meta=2)
    switch = TileTCRail(
        rail_type=TrackType.MEDIUM_RIGHT_SWITCH,
        facing_meta=2,
        can_type_be_modified_by_switch=True,
    )
    world.set_tile(0, 10, 0, switch)

    # Place neighbor rails that will be modified
    # For meta=2, neighbor at z-1 is (0,10,-1)
    neighbor1 = TileTCRail(rail_type=TrackType.SMALL_STRAIGHT, facing_meta=2)
    world.set_tile(0, 10, -1, neighbor1)

    print(f"Initial switch state: {switch.get_switch_state()}")
    print(f"Initial neighbor type: {neighbor1.get_type().value}")

    # Activate switch (simulate redstone ON)
    world.redstone_power[(0, 10, 0)] = True
    logs = switch.change_switch_state(world, switch, 0, 10, 0)
    for log in logs:
        print(f"  {log}")

    print(f"After activation: switch={switch.get_switch_state()}, neighbor={neighbor1.get_type().value}")

    # Deactivate switch (simulate redstone OFF)
    world.redstone_power[(0, 10, 0)] = False
    logs = switch.change_switch_state(world, switch, 0, 10, 0)
    for log in logs:
        print(f"  {log}")

    print(f"After deactivation: switch={switch.get_switch_state()}, neighbor={neighbor1.get_type().value}")

    print(f"NBT: {switch.to_nbt_dict()}")
    print()


def demo_large_left_switch() -> None:
    """Demonstrate LARGE_LEFT_SWITCH with two modified neighbors."""
    print("=" * 60)
    print("DEMO: LARGE_LEFT_SWITCH")
    print("=" * 60)

    world = SimulatedWorld()

    # Place switch at (5, 10, 5) facing south (meta=0)
    switch = TileTCRail(
        rail_type=TrackType.LARGE_LEFT_SWITCH,
        facing_meta=0,
        can_type_be_modified_by_switch=True,
    )
    world.set_tile(5, 10, 5, switch)

    # For meta=0: neighbor1 at z+1 -> (5,10,6), neighbor2 at z+2 -> (5,10,7)
    n1 = TileTCRail(rail_type=TrackType.SMALL_STRAIGHT, facing_meta=0)
    n2 = TileTCRail(rail_type=TrackType.SMALL_STRAIGHT, facing_meta=0)
    world.set_tile(5, 10, 6, n1)
    world.set_tile(5, 10, 7, n2)

    print(f"Initial: switch={switch.get_switch_state()}, n1={n1.get_type().value}, n2={n2.get_type().value}")

    logs = switch.change_switch_state(world, switch, 5, 10, 5)
    for log in logs:
        print(f"  {log}")

    print(f"Activated: switch={switch.get_switch_state()}, n1={n1.get_type().value}, n2={n2.get_type().value}")
    print()


def demo_switch_tick_cycle() -> None:
    """Simulate several ticks showing redstone detection and manual override."""
    print("=" * 60)
    print("DEMO: Switch tick cycle with redstone")
    print("=" * 60)

    world = SimulatedWorld()
    switch = TileTCRail(
        rail_type=TrackType.MEDIUM_RIGHT_SWITCH,
        facing_meta=1,
        can_type_be_modified_by_switch=True,
    )
    world.set_tile(0, 10, 0, switch)

    n1 = TileTCRail(rail_type=TrackType.SMALL_STRAIGHT, facing_meta=1)
    world.set_tile(-1, 10, 0, n1)

    for tick in range(35):
        # Toggle redstone at tick 5 and 20
        if tick == 5:
            world.redstone_power[(0, 10, 0)] = True
            print(f"[Tick {tick}] Redstone ON")
        if tick == 20:
            world.redstone_power[(0, 10, 0)] = False
            print(f"[Tick {tick}] Redstone OFF")

        logs = switch.update_entity(world)
        if logs:
            print(f"[Tick {tick}] {' | '.join(logs)}")

    print(f"Final state: switch={switch.get_switch_state()}, neighbor={n1.get_type().value}")
    print()


if __name__ == "__main__":
    demo_medium_right_switch()
    demo_large_left_switch()
    demo_switch_tick_cycle()
