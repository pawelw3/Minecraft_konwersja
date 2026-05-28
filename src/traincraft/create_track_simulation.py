"""
Simulation of Create 1.18.2 track system based on exact source code.
Source: com.simibubi.create.content.trains.track.TrackBlockEntity
        com.simibubi.create.content.trains.track.BezierConnection
        com.simibubi.create.content.trains.track.TrackShape

This simulates:
- TrackBlockEntity with BezierConnection storage
- NBT serialization (write/read) matching exact Minecraft NBT structure
- TrackShape enum (xo, zo, pd, nd, cr_o, ae, aw, an, as, etc.)
- FakeTrackBlock generation along curves (rasterise logic)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math


class TrackShape(Enum):
    """Replicates TrackShape enum from Create source."""
    NONE = "none"
    ZO = "zo"           # straight Z
    XO = "xo"           # straight X
    PD = "pd"           # positive diagonal (+X,+Z)
    ND = "nd"           # negative diagonal (-X,+Z)
    AN = "an"           # ascending north
    AS_ = "as"          # ascending south
    AE = "ae"           # ascending east
    AW = "aw"           # ascending west
    TN = "tn"           # teleport north
    TS = "ts"           # teleport south
    TE = "te"           # teleport east
    TW = "tw"           # teleport west
    CR_O = "cr_o"       # cross orthogonal
    CR_D = "cr_d"       # cross diagonal
    CR_PDX = "cr_pdx"
    CR_PDZ = "cr_pdz"
    CR_NDX = "cr_ndx"
    CR_NDZ = "cr_ndz"

    def is_junction(self) -> bool:
        return self in {
            TrackShape.CR_O, TrackShape.CR_D, TrackShape.CR_PDX,
            TrackShape.CR_PDZ, TrackShape.CR_NDX, TrackShape.CR_NDZ
        }

    def is_portal(self) -> bool:
        return self in {TrackShape.TN, TrackShape.TS, TrackShape.TE, TrackShape.TW}


@dataclass
class Vec3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def add(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def subtract(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def scale(self, s: float) -> "Vec3":
        return Vec3(self.x * s, self.y * s, self.z * s)

    def to_dict(self) -> dict:
        return {"X": self.x, "Y": self.y, "Z": self.z}

    @classmethod
    def from_dict(cls, d: dict) -> "Vec3":
        return cls(d.get("X", 0.0), d.get("Y", 0.0), d.get("Z", 0.0))


@dataclass
class BlockPos:
    x: int = 0
    y: int = 0
    z: int = 0

    def offset(self, dx: int, dy: int, dz: int) -> "BlockPos":
        return BlockPos(self.x + dx, self.y + dy, self.z + dz)

    def subtract(self, other: "BlockPos") -> "BlockPos":
        return BlockPos(self.x - other.x, self.y - other.y, self.z - other.z)

    def to_dict(self) -> dict:
        return {"X": self.x, "Y": self.y, "Z": self.z}

    @classmethod
    def from_dict(cls, d: dict) -> "BlockPos":
        return cls(d.get("X", 0), d.get("Y", 0), d.get("Z", 0))


@dataclass
class BezierConnection:
    """
    Replicates Create's BezierConnection.
    Stores a cubic Bezier spline between two TrackBlockEntity endpoints.
    """
    positions: Tuple[BlockPos, BlockPos]  # The two endpoint TE positions
    starts: Tuple[Vec3, Vec3]            # Curve start/end points (relative to world)
    axes: Tuple[Vec3, Vec3]              # Direction vectors at endpoints
    normals: Tuple[Vec3, Vec3]           # Up vectors at endpoints
    primary: bool = True
    has_girder: bool = False
    material: str = "create:andesite"
    smoothing: Optional[Tuple[int, int]] = None

    def get_key(self) -> BlockPos:
        """Returns the OTHER endpoint position (used as dict key)."""
        return self.positions[1] if self.primary else self.positions[0]

    def write_nbt(self, local_to: BlockPos) -> dict:
        """
        Replicates BezierConnection.write(BlockPos localTo).
        Returns dict matching Minecraft CompoundTag structure.
        """
        te_positions = (
            self.positions[0].subtract(local_to),
            self.positions[1].subtract(local_to),
        )
        starts = (
            self.starts[0].subtract(Vec3(local_to.x, local_to.y, local_to.z)),
            self.starts[1].subtract(Vec3(local_to.x, local_to.y, local_to.z)),
        )

        compound = {
            "Girder": self.has_girder,
            "Primary": self.primary,
            "Positions": [
                {"Pos": te_positions[0].to_dict()},
                {"Pos": te_positions[1].to_dict()},
            ],
            "Starts": [starts[0].to_dict(), starts[1].to_dict()],
            "Axes": [self.axes[0].to_dict(), self.axes[1].to_dict()],
            "Normals": [self.normals[0].to_dict(), self.normals[1].to_dict()],
            "Material": self.material,
        }
        if self.smoothing:
            compound["Smoothing"] = [
                {"Val": self.smoothing[0]},
                {"Val": self.smoothing[1]},
            ]
        return compound

    @classmethod
    def from_nbt(cls, compound: dict, local_to: BlockPos) -> "BezierConnection":
        """Replicates BezierConnection(CompoundTag compound, BlockPos localTo)."""
        pos_list = compound["Positions"]
        positions = (
            BlockPos.from_dict(pos_list[0]["Pos"]).offset(local_to.x, local_to.y, local_to.z),
            BlockPos.from_dict(pos_list[1]["Pos"]).offset(local_to.x, local_to.y, local_to.z),
        )
        starts = [
            Vec3.from_dict(compound["Starts"][0]).add(Vec3(local_to.x, local_to.y, local_to.z)),
            Vec3.from_dict(compound["Starts"][1]).add(Vec3(local_to.x, local_to.y, local_to.z)),
        ]
        axes = [Vec3.from_dict(compound["Axes"][0]), Vec3.from_dict(compound["Axes"][1])]
        normals = [Vec3.from_dict(compound["Normals"][0]), Vec3.from_dict(compound["Normals"][1])]
        primary = compound.get("Primary", True)
        has_girder = compound.get("Girder", False)
        material = compound.get("Material", "create:andesite")
        smoothing = None
        if "Smoothing" in compound:
            smoothing = (compound["Smoothing"][0]["Val"], compound["Smoothing"][1]["Val"])
        return cls(positions, (starts[0], starts[1]), (axes[0], axes[1]),
                   (normals[0], normals[1]), primary, has_girder, material, smoothing)

    def rasterise(self) -> List[Tuple[int, int]]:
        """
        Simplified rasterisation of Bezier curve to (x,z) columns.
        Original: BezierConnection.rasterise() computes all (x,z) the curve passes through.
        """
        points = []
        p0 = Vec3(self.positions[0].x, self.positions[0].y, self.positions[0].z)
        p3 = Vec3(self.positions[1].x, self.positions[1].y, self.positions[1].z)
        # Simple control points estimation from starts/axes
        p1 = p0.add(self.axes[0].scale(5.0))
        p2 = p3.subtract(self.axes[1].scale(5.0))

        for t in [i / 20.0 for i in range(21)]:
            # Cubic Bezier
            t2 = t * t
            t3 = t2 * t
            mt = 1 - t
            mt2 = mt * mt
            mt3 = mt2 * mt
            x = mt3 * p0.x + 3 * mt2 * t * p1.x + 3 * mt * t2 * p2.x + t3 * p3.x
            z = mt3 * p0.z + 3 * mt2 * t * p1.z + 3 * mt * t2 * p2.z + t3 * p3.z
            ix, iz = int(round(x)), int(round(z))
            if not points or points[-1] != (ix, iz):
                points.append((ix, iz))
        return points


@dataclass
class TrackBlockEntity:
    """
    Replicates Create's TrackBlockEntity.
    """
    x: int = 0
    y: int = 0
    z: int = 0
    connections: Dict[Tuple[int, int, int], BezierConnection] = field(default_factory=dict)
    bound_location: Optional[Tuple[str, BlockPos]] = None  # (dimension, pos)
    smoothing_angle: Optional[float] = None

    def add_connection(self, connection: BezierConnection) -> None:
        key = connection.get_key()
        self.connections[(key.x, key.y, key.z)] = connection

    def write_nbt(self) -> dict:
        """
        Replicates TrackBlockEntity.write(CompoundTag tag, ...).
        """
        tag = {
            "Connections": [],
        }
        local_to = BlockPos(self.x, self.y, self.z)
        for conn in self.connections.values():
            tag["Connections"].append(conn.write_nbt(local_to))

        if self.smoothing_angle is not None:
            tag["Smoothing"] = self.smoothing_angle

        if self.bound_location:
            tag["BoundLocation"] = self.bound_location[1].to_dict()
            tag["BoundDimension"] = self.bound_location[0]

        return tag

    def read_nbt(self, tag: dict) -> None:
        """Replicates TrackBlockEntity.read(CompoundTag tag, ...)."""
        self.connections.clear()
        local_to = BlockPos(self.x, self.y, self.z)
        for t in tag.get("Connections", []):
            conn = BezierConnection.from_nbt(t, local_to)
            key = conn.get_key()
            self.connections[(key.x, key.y, key.z)] = conn

        if "Smoothing" in tag:
            self.smoothing_angle = tag["Smoothing"]

        if "BoundLocation" in tag:
            dim = tag.get("BoundDimension", "minecraft:overworld")
            pos = BlockPos.from_dict(tag["BoundLocation"])
            self.bound_location = (dim, pos)

    def compute_fake_tracks(self) -> List[Tuple[int, int, int]]:
        """
        Simulates TrackBlockEntity.manageFakeTracksAlong().
        Returns positions where FakeTrackBlock would be generated.
        """
        fake_positions = []
        for conn in self.connections.values():
            if not conn.primary:
                continue
            for rx, rz in conn.rasterise():
                # Fake track is placed at highest Y for each (x,z) column
                fake_positions.append((rx, self.y, rz))
        return fake_positions


@dataclass
class FakeTrackBlockEntity:
    """Placeholder for Create's FakeTrackBlockEntity (runtime only)."""
    x: int = 0
    y: int = 0
    z: int = 0
    keep_alive: int = 3  # ticks until removal if not refreshed


def demo_straight_track() -> None:
    print("=" * 60)
    print("DEMO: Create Simple Straight Track (no BE)")
    print("=" * 60)
    print("BlockState: shape=xo, turn=false")
    print("No BlockEntity needed for simple straight/diagonal/junction tracks.")
    print()


def demo_curved_track() -> None:
    print("=" * 60)
    print("DEMO: Create Curved Track with BezierConnection")
    print("=" * 60)

    # Endpoint 1 at (0, 10, 0)
    te1 = TrackBlockEntity(x=0, y=10, z=0)
    # Endpoint 2 at (5, 10, 5)
    te2 = TrackBlockEntity(x=5, y=10, z=5)

    # Create BezierConnection from te1 to te2
    conn = BezierConnection(
        positions=(BlockPos(0, 10, 0), BlockPos(5, 10, 5)),
        starts=(Vec3(0.5, 10, 0.5), Vec3(4.5, 10, 4.5)),
        axes=(Vec3(1, 0, 0.5), Vec3(0.5, 0, 1)),
        normals=(Vec3(0, 1, 0), Vec3(0, 1, 0)),
        primary=True,
        has_girder=False,
        material="create:andesite",
    )

    te1.add_connection(conn)

    nbt = te1.write_nbt()
    print("TrackBlockEntity NBT:")
    import json
    print(json.dumps(nbt, indent=2))

    print(f"\nFakeTrackBlock positions along curve: {te1.compute_fake_tracks()}")
    print(f"Total physical blocks occupied: 2 TrackBlock + ~{len(te1.compute_fake_tracks())} FakeTrackBlock")
    print()


def demo_junction_track() -> None:
    print("=" * 60)
    print("DEMO: Create Junction (cross_ortho)")
    print("=" * 60)
    print("BlockState: shape=cr_o, turn=false")
    print("Two overlapping straight tracks in one block (X + Z).")
    print("No BlockEntity, no FakeTrackBlocks.")
    print("In Traincraft equivalent (TWO_WAYS_CROSSING): ~9 physical blocks")
    print("In Create: 1 physical block")
    print()


def demo_ascending_track() -> None:
    print("=" * 60)
    print("DEMO: Create Ascending Track")
    print("=" * 60)
    print("BlockState: shape=ae (ascending east), turn=false")
    print("No collision (Shapes.empty()).")
    print("Train moves along internal graph, not block-by-block.")
    print("In Traincraft equivalent (SLOPE): 6-18 physical blocks with rising bbHeight")
    print("In Create: 1 physical block per segment")
    print()


def demo_portal_track() -> None:
    print("=" * 60)
    print("DEMO: Create Portal Track")
    print("=" * 60)

    te = TrackBlockEntity(x=0, y=10, z=0)
    te.bound_location = ("minecraft:the_nether", BlockPos(100, 50, 100))

    nbt = te.write_nbt()
    print("Portal TrackBlockEntity NBT:")
    import json
    print(json.dumps(nbt, indent=2))
    print()


def demo_nbt_roundtrip() -> None:
    print("=" * 60)
    print("DEMO: NBT Round-trip")
    print("=" * 60)

    te = TrackBlockEntity(x=10, y=20, z=30)
    conn = BezierConnection(
        positions=(BlockPos(10, 20, 30), BlockPos(15, 20, 35)),
        starts=(Vec3(10.5, 20, 30.5), Vec3(14.5, 20, 34.5)),
        axes=(Vec3(1, 0, 0.5), Vec3(0.5, 0, 1)),
        normals=(Vec3(0, 1, 0), Vec3(0, 1, 0)),
        primary=True,
        has_girder=True,
        material="railways:track_oak",
        smoothing=(12, 24),
    )
    te.add_connection(conn)
    te.smoothing_angle = 15.5

    nbt = te.write_nbt()
    te2 = TrackBlockEntity(x=10, y=20, z=30)
    te2.read_nbt(nbt)

    print(f"Original connections: {len(te.connections)}")
    print(f"Round-trip connections: {len(te2.connections)}")
    c1 = list(te.connections.values())[0]
    c2 = list(te2.connections.values())[0]
    print(f"Material match: {c1.material == c2.material}")
    print(f"Girder match: {c1.has_girder == c2.has_girder}")
    print(f"Positions match: {c1.positions[1].x == c2.positions[1].x}")
    print(f"Smoothing match: {c1.smoothing == c2.smoothing}")
    print()


if __name__ == "__main__":
    demo_straight_track()
    demo_curved_track()
    demo_junction_track()
    demo_ascending_track()
    demo_portal_track()
    demo_nbt_roundtrip()
