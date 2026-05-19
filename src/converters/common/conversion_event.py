"""Wspolna klasa eventow konwersji dla wszystkich modow.

Uzywaj tej klasy zamiast kopiowac ja do kazdego folderu moda.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConversionEvent:
    """Pojedynczy event konwersji bloku lub tile/block entity.

    Format zgodny z handlerami wstawiajacymi dane na podkladowa mape 1.18.2.
    """
    mod: str
    source_version: str
    target_version: str
    event_type: str  # "remap", "placeholder", "remove", "skip"
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
    # Dodatkowe dane zrodlowe do diagnostyki
    source_nbt: dict[str, Any] | None = None

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
                "position": list(self.position) if self.position else None,
                "nbt": self.source_nbt,
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

    def to_set_block_event(self) -> dict[str, Any] | None:
        """Konwertuje na event 'set_block' / 'set_block_entity' dla handlera mapy.

        Zwraca None jesli event_type == 'remove' lub 'skip'.
        """
        if self.event_type in ("remove", "skip"):
            return None

        if self.position is None:
            self.warnings.append("Missing position in to_set_block_event")
            return None

        event: dict[str, Any] = {
            "op": "set_block_entity" if self.target_te_id else "set_block",
            "pos": list(self.position),
            "block": self.target_block_id,
        }
        if self.blockstate_props:
            event["blockstate"] = dict(self.blockstate_props)
        if self.nbt_1182:
            event["nbt"] = dict(self.nbt_1182)
        return event
