"""
Resolve conflicts between parallel Traincraft tracks that are too close
for Create's 3-block-wide tracks.

Create track visually (and collision-wise) spans 3 blocks in the direction
perpendicular to the rail.  If two parallel Traincraft rails have 0 or 1
free blocks between them (distance <= 2 in the perpendicular axis) they
will overlap when converted.  This module detects such conflicts and picks
which rail to keep based on maximum continuity (longer segments win).

Usage:
    resolver = TrackConflictResolver(world_path="mapa_1710")
    removals = resolver.run()   # set of (x, y, z) to remove
    resolver.save("output/traincraft_task4/track_removals.json")
"""

from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from minecraft_map_parser.anvil_parser import AnvilParser


class TrackInfo(NamedTuple):
    x: int
    y: int
    z: int
    facing: int        # 0=S, 1=W, 2=N, 3=E
    track_type: str


class TrackConflictResolver:
    """Two-pass resolver:
    1. Scan the world and collect all tcRail positions.
    2. Group by (y, perpendicular_axis) and detect conflicts.
    """

    # Track types that are actually converted (not removed)
    CONVERTED_TYPES = frozenset([
        "SMALL_STRAIGHT", "MEDIUM_STRAIGHT", "LONG_STRAIGHT",
        "SMALL_ROAD_CROSSING", "SMALL_ROAD_CROSSING_1", "SMALL_ROAD_CROSSING_2",
        "SLOPE_WOOD", "SLOPE_GRAVEL", "SLOPE_BALLAST",
        "LARGE_SLOPE_WOOD", "LARGE_SLOPE_GRAVEL", "LARGE_SLOPE_BALLAST",
        "VERY_LARGE_SLOPE_WOOD", "VERY_LARGE_SLOPE_GRAVEL", "VERY_LARGE_SLOPE_BALLAST",
        # switches approximated as straight
        "MEDIUM_SWITCH", "MEDIUM_RIGHT_SWITCH", "MEDIUM_LEFT_SWITCH",
        "LARGE_SWITCH", "LARGE_RIGHT_SWITCH", "LARGE_LEFT_SWITCH",
        "MEDIUM_PARALLEL_SWITCH", "MEDIUM_RIGHT_PARALLEL_SWITCH", "MEDIUM_LEFT_PARALLEL_SWITCH",
        # crossing kept
        "TWO_WAYS_CROSSING",
    ])

    def __init__(self, world_path: str | Path):
        self.world_path = Path(world_path)
        self.tracks: list[TrackInfo] = []
        self.removals: set[tuple[int, int, int]] = set()

    # ------------------------------------------------------------------
    # Pass 1: scan
    # ------------------------------------------------------------------
    def scan_world(self) -> list[TrackInfo]:
        region_dir = self.world_path / "region"
        files = sorted(region_dir.glob("*.mca"))
        print(f"[Resolver] Scanning {len(files)} regions for tcRail positions...")

        tracks: list[TrackInfo] = []
        t0 = time.time()
        for i, fpath in enumerate(files, 1):
            try:
                parser = AnvilParser(str(fpath))
                for cx in range(32):
                    for cz in range(32):
                        chunk = parser.get_chunk(cx, cz)
                        if chunk is None:
                            continue
                        for te in chunk.get_tile_entities():
                            if te.get("id") != "tileTCRail":
                                continue
                            tt = te.get("type", "")
                            if tt not in self.CONVERTED_TYPES:
                                continue
                            x = int(te.get("x", 0))
                            y = int(te.get("y", 0))
                            z = int(te.get("z", 0))
                            f = int(te.get("facingMeta", 0))
                            tracks.append(TrackInfo(x, y, z, f, tt))
            except Exception:
                pass  # skip corrupted regions

            if i % 100 == 0 or i == len(files):
                print(f"  [{i}/{len(files)}] collected {len(tracks)} rails "
                      f"({time.time()-t0:.1f}s)")

        self.tracks = tracks
        print(f"[Resolver] Total convertible rails: {len(tracks)}")
        return tracks

    # ------------------------------------------------------------------
    # Pass 2: detect & resolve conflicts
    # ------------------------------------------------------------------
    def resolve_conflicts(self) -> set[tuple[int, int, int]]:
        """Build NS/EW groups, find conflicts, return positions to remove."""
        if not self.tracks:
            return set()

        # Separate by orientation
        ns_tracks = [t for t in self.tracks if t.facing in (0, 2)]   # N-S (along Z)
        ew_tracks = [t for t in self.tracks if t.facing in (1, 3)]   # E-W (along X)

        removals: set[tuple[int, int, int]] = set()

        # ---- N-S rails: group by (y, x) ----
        ns_groups = defaultdict(list)   # (y, x) -> list of TrackInfo
        for t in ns_tracks:
            ns_groups[(t.y, t.x)].append(t)

        # Sort each group by Z to get range
        ns_ranges: dict[tuple[int, int], tuple[int, int, int]] = {}
        for key, rails in ns_groups.items():
            zs = [r.z for r in rails]
            ns_ranges[key] = (min(zs), max(zs), len(rails))

        # Check conflicts: groups (y, x) vs (y, x+delta) for delta in (1, 2)
        for (y, x), (z_min, z_max, count) in ns_ranges.items():
            for delta in (1, 2):
                other_key = (y, x + delta)
                if other_key not in ns_ranges:
                    continue
                oz_min, oz_max, ocount = ns_ranges[other_key]
                # overlap in Z?
                if max(z_min, oz_min) <= min(z_max, oz_max):
                    # Conflict! Pick the shorter group (or larger x if equal)
                    if count < ocount:
                        loser = other_key
                    elif count > ocount:
                        loser = (y, x)
                    else:
                        loser = other_key  # tie-break: larger x loses
                    for r in ns_groups[loser]:
                        removals.add((r.x, r.y, r.z))

        # ---- E-W rails: group by (y, z) ----
        ew_groups = defaultdict(list)
        for t in ew_tracks:
            ew_groups[(t.y, t.z)].append(t)

        ew_ranges: dict[tuple[int, int], tuple[int, int, int]] = {}
        for key, rails in ew_groups.items():
            xs = [r.x for r in rails]
            ew_ranges[key] = (min(xs), max(xs), len(rails))

        for (y, z), (x_min, x_max, count) in ew_ranges.items():
            for delta in (1, 2):
                other_key = (y, z + delta)
                if other_key not in ew_ranges:
                    continue
                ox_min, ox_max, ocount = ew_ranges[other_key]
                if max(x_min, ox_min) <= min(x_max, ox_max):
                    if count < ocount:
                        loser = other_key
                    elif count > ocount:
                        loser = (y, z)
                    else:
                        loser = other_key  # tie-break: larger z loses
                    for r in ew_groups[loser]:
                        removals.add((r.x, r.y, r.z))

        self.removals = removals
        print(f"[Resolver] Conflicts resolved.  Rails to remove: {len(removals)}")
        return removals

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def run(self) -> set[tuple[int, int, int]]:
        self.scan_world()
        return self.resolve_conflicts()

    def save(self, path: str | Path) -> None:
        out = {
            "removals": sorted(self.removals),
            "total_removals": len(self.removals),
            "total_tracks": len(self.tracks),
        }
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        print(f"[Resolver] Saved removals to {path}")

    def load(self, path: str | Path) -> set[tuple[int, int, int]]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.removals = {tuple(p) for p in data.get("removals", [])}
        return self.removals
