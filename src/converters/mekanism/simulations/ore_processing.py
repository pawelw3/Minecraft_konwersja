"""
Symulacja linii ore processing Mekanism 1.7.10 i 1.18.2.

Zrodla lokalne:
- 1.7.10: `Mekanism-1.7.10-9.1.1-clienthax.jar`, klasy maszyn i
  `IFactory$RecipeType`.
- 1.18.2: `Mekanism-1.18.2-10.2.5.465.jar`, data pack recipes w
  `data/mekanism/recipes/processing/<material>/...`.

Najwazniejsza roznica semantyczna: 1.7.10 mowi o gas API, a 1.18.2 o chemical
API, ale lancuchy x2/x3/x4/x5 maja zachowac yield.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .common import ItemStack, SimulationEvent, Version


class ProcessingTier(Enum):
    X2 = 2
    X3 = 3
    X4 = 4
    X5 = 5


@dataclass(frozen=True)
class Material:
    name: str
    legacy_ore: str
    target_ore: str
    legacy_ingot: str
    target_ingot: str

    def item(self, version: Version, part: str) -> str:
        prefix = "Mekanism" if version is Version.V1710 else "mekanism"
        material_name = self.name.capitalize()
        names = {
            "dust": f"{prefix}:{material_name}Dust" if version is Version.V1710 else f"mekanism:dust_{self.name}",
            "dirty_dust": f"{prefix}:Dirty{material_name}Dust"
            if version is Version.V1710
            else f"mekanism:dirty_dust_{self.name}",
            "clump": f"{prefix}:{material_name}Clump" if version is Version.V1710 else f"mekanism:clump_{self.name}",
            "shard": f"{prefix}:{material_name}Shard" if version is Version.V1710 else f"mekanism:shard_{self.name}",
            "crystal": f"{prefix}:{material_name}Crystal"
            if version is Version.V1710
            else f"mekanism:crystal_{self.name}",
        }
        return names[part]


OSMIUM = Material(
    name="osmium",
    legacy_ore="Mekanism:OreBlock:0",
    target_ore="mekanism:osmium_ore",
    legacy_ingot="Mekanism:Ingot:1",
    target_ingot="mekanism:ingot_osmium",
)

IRON = Material(
    name="iron",
    legacy_ore="minecraft:iron_ore",
    target_ore="minecraft:iron_ore",
    legacy_ingot="minecraft:iron_ingot",
    target_ingot="minecraft:iron_ingot",
)


@dataclass
class OreProcessingRun:
    version: Version
    tier: ProcessingTier
    material: Material
    ore_count: int = 1
    events: list[SimulationEvent] = field(default_factory=list)

    def run(self) -> ItemStack:
        if self.tier is ProcessingTier.X2:
            return self._x2()
        if self.tier is ProcessingTier.X3:
            return self._x3()
        if self.tier is ProcessingTier.X4:
            return self._x4()
        return self._x5()

    def _ore_id(self) -> str:
        return self.material.legacy_ore if self.version is Version.V1710 else self.material.target_ore

    def _ingot_id(self) -> str:
        return self.material.legacy_ingot if self.version is Version.V1710 else self.material.target_ingot

    def _resource_name(self, legacy: str, modern: str) -> str:
        return legacy if self.version is Version.V1710 else modern

    def _record(
        self,
        step: str,
        inputs: list[ItemStack],
        outputs: list[ItemStack],
        consumed: dict[str, int | float] | None = None,
        note: str | None = None,
    ) -> None:
        notes = [note] if note else []
        self.events.append(SimulationEvent(step, inputs, outputs, consumed or {}, notes))

    def _x2(self) -> ItemStack:
        ore = ItemStack(self._ore_id(), self.ore_count)
        dust = ItemStack(self.material.item(self.version, "dust"), self.ore_count * 2)
        self._record("enrichment_chamber", [ore], [dust], note="ore -> 2 dust")
        ingot = ItemStack(self._ingot_id(), dust.count)
        self._record("energized_smelter", [dust], [ingot], note="dust -> ingot")
        return ingot

    def _x3(self) -> ItemStack:
        ore = ItemStack(self._ore_id(), self.ore_count)
        clump = ItemStack(self.material.item(self.version, "clump"), self.ore_count * 3)
        oxygen = self._resource_name("gas:oxygen", "mekanism:oxygen")
        self._record("purification_chamber", [ore], [clump], {oxygen: self.ore_count}, "ore + oxygen -> 3 clumps")
        return self._clump_to_ingot(clump)

    def _x4(self) -> ItemStack:
        ore = ItemStack(self._ore_id(), self.ore_count)
        shard = ItemStack(self.material.item(self.version, "shard"), self.ore_count * 4)
        hcl = self._resource_name("gas:hydrogen_chloride", "mekanism:hydrogen_chloride")
        self._record("chemical_injection_chamber", [ore], [shard], {hcl: self.ore_count}, "ore + HCl -> 4 shards")
        clump = ItemStack(self.material.item(self.version, "clump"), shard.count)
        oxygen = self._resource_name("gas:oxygen", "mekanism:oxygen")
        self._record("purification_chamber", [shard], [clump], {oxygen: shard.count}, "shards + oxygen -> clumps")
        return self._clump_to_ingot(clump)

    def _x5(self) -> ItemStack:
        ore = ItemStack(self._ore_id(), self.ore_count)
        dirty_slurry = self._resource_name(f"dirty_slurry:{self.material.name}", f"mekanism:dirty_{self.material.name}")
        acid = self._resource_name("gas:sulfuric_acid", "mekanism:sulfuric_acid")
        self._record("chemical_dissolution_chamber", [ore], [], {acid: self.ore_count, dirty_slurry: self.ore_count * 1000}, "ore + acid -> dirty slurry")
        clean_slurry = self._resource_name(f"clean_slurry:{self.material.name}", f"mekanism:clean_{self.material.name}")
        self._record("chemical_washer", [], [], {"minecraft:water": self.ore_count * 1000, clean_slurry: self.ore_count * 1000}, "dirty slurry + water -> clean slurry")
        crystal = ItemStack(self.material.item(self.version, "crystal"), self.ore_count * 5)
        self._record("chemical_crystallizer", [], [crystal], {clean_slurry: self.ore_count * 1000}, "clean slurry -> 5 crystals")
        shard = ItemStack(self.material.item(self.version, "shard"), crystal.count)
        hcl = self._resource_name("gas:hydrogen_chloride", "mekanism:hydrogen_chloride")
        self._record("chemical_injection_chamber", [crystal], [shard], {hcl: crystal.count}, "crystals + HCl -> shards")
        clump = ItemStack(self.material.item(self.version, "clump"), shard.count)
        oxygen = self._resource_name("gas:oxygen", "mekanism:oxygen")
        self._record("purification_chamber", [shard], [clump], {oxygen: shard.count}, "shards + oxygen -> clumps")
        return self._clump_to_ingot(clump)

    def _clump_to_ingot(self, clump: ItemStack) -> ItemStack:
        dirty = ItemStack(self.material.item(self.version, "dirty_dust"), clump.count)
        self._record("crusher", [clump], [dirty], note="clump -> dirty dust")
        dust = ItemStack(self.material.item(self.version, "dust"), dirty.count)
        self._record("enrichment_chamber", [dirty], [dust], note="dirty dust -> dust")
        ingot = ItemStack(self._ingot_id(), dust.count)
        self._record("energized_smelter", [dust], [ingot], note="dust -> ingot")
        return ingot


def compare_yield(material: Material, tier: ProcessingTier, ore_count: int = 1) -> tuple[ItemStack, ItemStack]:
    legacy = OreProcessingRun(Version.V1710, tier, material, ore_count).run()
    modern = OreProcessingRun(Version.V1182, tier, material, ore_count).run()
    if legacy.count != modern.count:
        raise AssertionError(f"Yield mismatch for {material.name} {tier}: {legacy.count} != {modern.count}")
    return legacy, modern


if __name__ == "__main__":
    for processing_tier in ProcessingTier:
        legacy_stack, modern_stack = compare_yield(OSMIUM, processing_tier, 2)
        print(processing_tier.name, legacy_stack, modern_stack)
