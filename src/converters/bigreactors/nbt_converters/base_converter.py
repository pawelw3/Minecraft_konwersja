"""Bazowe klasy konwerterow NBT dla Big Reactors -> Bigger Reactors."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class NBTConversionResult:
    converted_nbt: dict[str, Any] | None = None
    blockstate_props: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class IdentityBiggerReactorsConverter:
    """Prosty konwerter tozsamosciowy — zachowuje x,y,z, id; ignoruje reszte."""

    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        metadata: int = 0,
    ) -> NBTConversionResult:
        nbt_1182: dict[str, Any] = {}
        warnings: list[str] = []

        # Podstawowe wspolrzedne
        for key in ("x", "y", "z"):
            if key in nbt_1710:
                nbt_1182[key] = nbt_1710[key]

        # Block entity ID w 1.18.2
        nbt_1182["id"] = target_block_id

        # Facing / orientation — czesto zapisane jako byte "facing"
        if "facing" in nbt_1710:
            nbt_1182["facing"] = nbt_1710["facing"]

        # Keep any custom name
        if "CustomName" in nbt_1710:
            nbt_1182["CustomName"] = nbt_1710["CustomName"]

        return NBTConversionResult(
            converted_nbt=nbt_1182,
            warnings=warnings,
        )
