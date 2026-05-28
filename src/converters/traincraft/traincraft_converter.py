"""Traincraft 1.7.10 → 1.18.2 converter.

Maps Traincraft rails and machines to Create / Steam'n'Rails equivalents.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from converters.common.conversion_event import ConversionEvent
from converters.traincraft.mappings.block_mappings import (
    classify_track_type,
    get_non_rail_mapping,
    get_track_target,
    is_traincraft_block_id,
    is_traincraft_te_id,
)

logger = logging.getLogger(__name__)


class TraincraftConverter:
    """
    Converts Traincraft 1.7.10 blocks and tile entities to 1.18.2.

    Key design decisions:
    - tcRail (main rail) + tcRailGag (fillers) are converted to single Create
      tracks where possible, or to railswitches for switches.
    - All tcRailGag blocks are removed (air).
    - Rolling stock entities are lost (Create requires building trains from
      scratch); only track infrastructure survives.
    - Machines without 1.18.2 equivalent become placeholders.
    """

    def __init__(self, event_logger: logging.Logger | None = None,
                 removals: set[tuple[int, int, int]] | None = None,
                 removals_path: str | Path | None = None):
        self.event_logger = event_logger or logger
        self.removals = removals or set()
        if removals_path:
            self._load_removals(removals_path)
        elif not self.removals:
            # Try default path
            default = Path("output/traincraft_task4/track_removals.json")
            if default.exists():
                self._load_removals(default)

    def _load_removals(self, path: str | Path) -> None:
        import json
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.removals = {tuple(p) for p in data.get("removals", [])}
        self.event_logger.info(f"[Traincraft] Loaded {len(self.removals)} removals from {path}")

    # ─── Detector helpers (used by router) ───

    @staticmethod
    def is_traincraft_tile_entity_id(te_id: str) -> bool:
        return is_traincraft_te_id(te_id)

    @staticmethod
    def is_traincraft_block(block_id: str) -> bool:
        return is_traincraft_block_id(block_id)

    # ─── Conversion entry point (per-chunk) ───

    def convert_tile_entity(self, te_id: str, te_nbt: dict[str, Any], block_id: str, metadata: int,
                            pos: tuple[int, int, int]) -> tuple[str, int, dict[str, str], dict[str, Any] | None] | None:
        """
        Convert a Traincraft tile entity to 1.18.2.
        Returns (new_block_id, metadata_hint, blockstate_props, new_te_nbt) or None.
        """
        self.event_logger.info(f"[Traincraft] Converting TE {te_id!r} at {pos}")

        # Conflict resolution: if this rail was marked for removal, delete it.
        if pos in self.removals:
            self.event_logger.info(f"[Traincraft] Removing rail at {pos} (track conflict)")
            return "minecraft:air", 0, {}, None

        if te_id == "tileTCRail":
            return self._convert_tc_rail(te_nbt, pos)

        if te_id == "tileTCRailGag":
            # Gag blocks are always removed.
            return "minecraft:air", 0, {}, None

        # Non-rail machines: map via block ID instead.
        new_id, props = get_non_rail_mapping(block_id, metadata)
        if new_id:
            return new_id, 0, props, None

        # Fallback
        return "conversion_placeholders:block_entity_placeholder", 0, {}, None

    def convert_block_only(self, block_id: str, metadata: int = 0,
                           te_id: str | None = None, te_nbt: dict[str, Any] | None = None,
                           pos: tuple[int, int, int] | None = None) -> tuple[str, int, dict[str, str], dict[str, Any] | None] | None:
        """
        Convert a Traincraft block without relying on tile entity.
        Called for blocks whose TE has already been removed or missing.
        """
        if block_id == "tc:tcRailGag":
            return "minecraft:air", 0, {}, None

        new_id, props = get_non_rail_mapping(block_id, metadata)
        if new_id:
            return new_id, 0, props, None

        return None

    # ─── Internal: rail conversion ───

    def _convert_tc_rail(self, te_nbt: dict[str, Any], pos: tuple[int, int, int]) -> tuple[str, int, dict[str, str], dict[str, Any] | None]:
        """Convert TileTCRail to Create track."""
        rail_type = te_nbt.get("type", "")
        facing_meta = te_nbt.get("facingMeta", 0)

        if not rail_type:
            self.event_logger.warning(f"[Traincraft] tcRail at {pos} missing 'type', using placeholder")
            return "conversion_placeholders:block_entity_placeholder", 0, {}, None

        new_id, props, nbt = get_track_target(rail_type, facing_meta)
        category = classify_track_type(rail_type)
        self.event_logger.info(f"[Traincraft] {category} {rail_type} → {new_id} props={props} at {pos}")
        return new_id, 0, props, nbt

    # ─── Batch / helper methods for chunk processing ───

    def process_chunk(self, chunk_1710: dict[str, Any]) -> list[ConversionEvent]:
        """
        Process a single 1.7.10 chunk dict, returning a list of ConversionEvents.
        This is a high-level helper intended for the main conversion pipeline.
        """
        events: list[ConversionEvent] = []
        level = chunk_1710.get("Level", chunk_1710)
        tile_entities = level.get("TileEntities", [])
        sections = level.get("Sections", level.get("sections", []))

        # Index tile entities by position for quick lookup
        te_by_pos: dict[tuple[int, int, int], dict[str, Any]] = {}
        for te in tile_entities:
            x = te.get("x", te.get("X", 0))
            y = te.get("y", te.get("Y", 0))
            z = te.get("z", te.get("Z", 0))
            te_by_pos[(x, y, z)] = te

        # Build a set of all gag positions to know which blocks are part of a multiblock
        gag_positions: set[tuple[int, int, int]] = set()
        for te in tile_entities:
            if te.get("id", "").lower() == "tiletcrailgag":
                ox = te.get("originX", te.get("x", 0))
                oy = te.get("originY", te.get("y", 0))
                oz = te.get("originZ", te.get("z", 0))
                # The gag itself is at its own position; origin points to the main rail.
                # We add both for cleanup.
                px = te.get("x", 0)
                py = te.get("y", 0)
                pz = te.get("z", 0)
                gag_positions.add((px, py, pz))
                gag_positions.add((ox, oy, oz))

        # Now iterate through blocks in sections
        for section in sections:
            y_base = section.get("Y", 0) << 4
            blocks = section.get("Blocks", [])
            data = section.get("Data", [])
            block_states = section.get("BlockStates", [])  # palette format (unlikely in 1.7.10)
            # 1.7.10 format: blocks[y][z][x] (4096 bytes), data[y][z][x] (2048 nibbles)
            # Flatten if needed.
            # ... simplified processing ...
            pass

        # Since per-section block iteration is complex, this method is kept as a stub
        # and the caller is expected to handle the actual block iteration.
        return events

    def convert_rail_gag_at(self, pos: tuple[int, int, int]) -> tuple[str, int, dict[str, str], dict[str, Any] | None] | None:
        """Convert a tcRailGag block (always remove)."""
        return "minecraft:air", 0, {}, None

    # ─── Event helpers ───

    def log_conversion(self, msg: str, level: int = logging.INFO) -> None:
        self.event_logger.log(level, msg)
