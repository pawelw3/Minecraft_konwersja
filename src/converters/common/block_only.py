"""Shared types for direct block-only conversion.

Block-only conversion is for legacy 1.7.10 blocks stored as numeric
ID + metadata in chunk Sections, without TileEntity/BlockEntity state.
"""

from __future__ import annotations

from dataclasses import dataclass, field


Position = tuple[int, int, int]


@dataclass(frozen=True)
class BlockOnlyResult:
    success: bool
    target_block: str = ""
    blockstate_props: dict[str, str] = field(default_factory=dict)
    confidence: str = "low"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @classmethod
    def ok(
        cls,
        target_block: str,
        *,
        blockstate_props: dict[str, str] | None = None,
        confidence: str = "medium",
        warnings: list[str] | None = None,
    ) -> "BlockOnlyResult":
        return cls(
            success=True,
            target_block=target_block,
            blockstate_props=dict(blockstate_props or {}),
            confidence=confidence,
            warnings=list(warnings or []),
        )

    @classmethod
    def fail(
        cls,
        error: str,
        *,
        target_block: str = "",
        confidence: str = "low",
        warnings: list[str] | None = None,
    ) -> "BlockOnlyResult":
        return cls(
            success=False,
            target_block=target_block,
            confidence=confidence,
            warnings=list(warnings or []),
            errors=[error],
        )


def normalize_metadata(metadata: int) -> int:
    return int(metadata) & 0xF


def explicit_fallback(
    target_block: str,
    warning: str,
    *,
    confidence: str = "low",
) -> BlockOnlyResult:
    return BlockOnlyResult.ok(
        target_block,
        confidence=confidence,
        warnings=[warning],
    )
