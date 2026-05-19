"""
Symulacja Digital Miner Mekanism.

To nie jest pelna symulacja fake player mining. Odtwarza czesc, ktora jest
istotna dla konwersji NBT: zakres, inverse mode, silkTouch, auto pull/eject
oraz lista filtrow. Klucze NBT potwierdzone z JAR-ow:

1.7.10: `radius`, `minY`, `maxY`, `doEject`, `doPull`, `running`,
`silkTouch`, `inverse`, `filters`.

1.18.2: powyzsze plus `inverseReplace`, `replaceStack`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


DEFAULT_RADIUS = 10
DEFAULT_MIN_Y_1710 = 0
DEFAULT_MAX_Y_1710 = 60
DEFAULT_HEIGHT_RANGE_1182 = 60


class MinerFilterType(Enum):
    ITEM_STACK = "item_stack"
    TAG = "tag"
    MOD_ID = "mod_id"


@dataclass(frozen=True)
class BlockSample:
    x: int
    y: int
    z: int
    block_id: str
    tags: frozenset[str] = frozenset()


@dataclass(frozen=True)
class MinerFilter:
    filter_type: MinerFilterType
    value: str
    requires_replacement: bool = False
    replace_target: str | None = None

    def matches(self, block: BlockSample) -> bool:
        if self.filter_type is MinerFilterType.ITEM_STACK:
            return block.block_id == self.value
        if self.filter_type is MinerFilterType.TAG:
            return self.value in block.tags
        if self.filter_type is MinerFilterType.MOD_ID:
            return block.block_id.split(":", 1)[0] == self.value
        raise AssertionError(f"Unhandled filter type: {self.filter_type}")


@dataclass
class DigitalMiner1710:
    radius: int = DEFAULT_RADIUS
    min_y: int = DEFAULT_MIN_Y_1710
    max_y: int = DEFAULT_MAX_Y_1710
    inverse: bool = False
    do_eject: bool = False
    do_pull: bool = False
    silk_touch: bool = False
    running: bool = False
    filters: list[MinerFilter] = field(default_factory=list)

    def in_range(self, block: BlockSample) -> bool:
        return abs(block.x) <= self.radius and abs(block.z) <= self.radius and self.min_y <= block.y <= self.max_y

    def filter_matches(self, block: BlockSample) -> bool:
        return any(miner_filter.matches(block) for miner_filter in self.filters)

    def can_mine(self, block: BlockSample) -> bool:
        if not self.in_range(block):
            return False
        matched = self.filter_matches(block)
        return not matched if self.inverse else matched

    def scan(self, blocks: list[BlockSample]) -> list[BlockSample]:
        return [block for block in blocks if self.can_mine(block)]

    def to_1182(self) -> "DigitalMiner1182":
        return DigitalMiner1182(
            radius=self.radius,
            min_y=self.min_y,
            max_y=self.max_y,
            inverse=self.inverse,
            do_eject=self.do_eject,
            do_pull=self.do_pull,
            silk_touch=self.silk_touch,
            running=False,
            filters=list(self.filters),
            inverse_requires_replacement=False,
            inverse_replace_target=None,
            warnings=["running_reset_for_recalculation"] if self.running else [],
        )

    def legacy_nbt_summary(self) -> dict[str, object]:
        return {
            "radius": self.radius,
            "minY": self.min_y,
            "maxY": self.max_y,
            "doEject": self.do_eject,
            "doPull": self.do_pull,
            "running": self.running,
            "silkTouch": self.silk_touch,
            "inverse": self.inverse,
            "filters": [filter_to_summary(miner_filter) for miner_filter in self.filters],
        }


@dataclass
class DigitalMiner1182(DigitalMiner1710):
    inverse_requires_replacement: bool = False
    inverse_replace_target: str | None = None
    warnings: list[str] = field(default_factory=list)

    def can_mine(self, block: BlockSample) -> bool:
        if not super().can_mine(block):
            return False
        if self.inverse and self.inverse_requires_replacement:
            return self.inverse_replace_target is not None
        return True

    def target_nbt_summary(self) -> dict[str, object]:
        data = self.legacy_nbt_summary()
        data["inverseReplace"] = self.inverse_requires_replacement
        data["replaceStack"] = self.inverse_replace_target
        data["warnings"] = list(self.warnings)
        return data


def filter_to_summary(miner_filter: MinerFilter) -> dict[str, object]:
    return {
        "type": miner_filter.filter_type.value,
        "value": miner_filter.value,
        "requiresReplacement": miner_filter.requires_replacement,
        "replaceTarget": miner_filter.replace_target,
    }


def compare_digital_miner_scan() -> tuple[list[BlockSample], list[BlockSample], DigitalMiner1182]:
    blocks = [
        BlockSample(0, 12, 0, "minecraft:iron_ore", frozenset({"forge:ores/iron"})),
        BlockSample(3, 12, 2, "mekanism:osmium_ore", frozenset({"forge:ores/osmium"})),
        BlockSample(12, 12, 0, "minecraft:gold_ore", frozenset({"forge:ores/gold"})),
        BlockSample(0, 70, 0, "minecraft:diamond_ore", frozenset({"forge:ores/diamond"})),
    ]
    legacy = DigitalMiner1710(filters=[MinerFilter(MinerFilterType.TAG, "forge:ores/osmium")], running=True)
    modern = legacy.to_1182()
    legacy_scan = legacy.scan(blocks)
    modern_scan = modern.scan(blocks)
    if legacy_scan != modern_scan:
        raise AssertionError("Digital Miner scan diverged after conversion")
    if "running_reset_for_recalculation" not in modern.warnings:
        raise AssertionError("Running miner should be reset for safe target recalculation")
    return legacy_scan, modern_scan, modern


if __name__ == "__main__":
    print(compare_digital_miner_scan())
