"""Base types for BuildCraft NBT converters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class NBTConversionResult:
    success: bool
    converted_nbt: dict[str, Any] | None = None
    blockstate_props: dict[str, str] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class BaseBuildCraftNBTConverter(ABC):
    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"

    @abstractmethod
    def convert(
        self,
        nbt_1710: dict[str, Any],
        target_block_id: str,
        source_block_id: str = "",
        source_metadata: int = 0,
    ) -> NBTConversionResult:
        ...
