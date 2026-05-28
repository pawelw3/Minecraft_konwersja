"""Open Modular Turrets converter: 1.7.10 → 1.18.2.

OMT has no port to 1.18.2.  All TileEntities are converted to
conversion_placeholders:block_entity_placeholder events that preserve
the full 1.7.10 NBT (owner, trustedPlayers, Inventory, targeting flags).
"""
from __future__ import annotations

from typing import Any

from converters.common.placeholders import make_block_entity_placeholder_event
from converters.openmodularturrets.mappings import OMT_TE_IDS, TE_ID_TO_BLOCK_REGISTRY

_SOURCE_MOD = "openmodularturrets"
_CONVERSION_REASON = "no_118_equivalent"


class OpenModularTurretsConverter:
    """Converts all OMT TileEntities to placeholder events."""

    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"
    MOD = _SOURCE_MOD

    def convert_tile_entity(
        self,
        te_id: str,
        nbt_1710: dict[str, Any],
        metadata: int = 0,
        position: tuple[int, int, int] = (0, 0, 0),
    ) -> list[dict[str, Any]]:
        """Return a single placeholder event for any OMT TileEntity.

        All original NBT fields (owner, trustedPlayers, Inventory, energyStored,
        attacking flags, etc.) are preserved verbatim inside original_nbt.
        """
        block_registry = TE_ID_TO_BLOCK_REGISTRY.get(te_id, "")
        event = make_block_entity_placeholder_event(
            position=position,
            source_mod=_SOURCE_MOD,
            source_te_id=te_id,
            source_block_id=block_registry,
            source_metadata=metadata,
            original_nbt=nbt_1710,
            conversion_reason=_CONVERSION_REASON,
        )
        return [event]

    def is_known_te(self, te_id: str) -> bool:
        return te_id in OMT_TE_IDS
