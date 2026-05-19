"""Eventy produkowane przez konwerter Mekanism."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConversionEvent:
    mod: str
    source_version: str
    target_version: str
    event_type: str
    source_block_id: str
    source_metadata: int
    target_block_id: str | None
    position: tuple[int, int, int] | None = None
    source_te_id: str | None = None
    target_te_id: str | None = None
    nbt_1182: dict[str, Any] | None = None
    blockstate_props: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "mod": self.mod,
            "source_version": self.source_version,
            "target_version": self.target_version,
            "event_type": self.event_type,
            "source": {
                "block_id": self.source_block_id,
                "metadata": self.source_metadata,
                "te_id": self.source_te_id,
                "position": self.position,
            },
            "target": {
                "block_id": self.target_block_id,
                "te_id": self.target_te_id,
                "blockstate_props": self.blockstate_props,
                "nbt": self.nbt_1182,
            },
            "warnings": self.warnings,
            "errors": self.errors,
        }
