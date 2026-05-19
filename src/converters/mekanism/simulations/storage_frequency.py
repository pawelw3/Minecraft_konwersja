"""
Symulacje magazynow energii/gazu i frequency ownerow Mekanism.

Najwazniejsze obserwacje z lokalnych JAR-ow:
- 1.7.10 `TileEntityEnergyCube` zapisuje `tier` jako nazwe base tieru i
  dziedziczy energie po `TileEntityElectricBlock`.
- 1.7.10 `TileEntityGasTank` zapisuje `tier` jako ordinal, `gasTank` compound
  oraz `dumping`.
- 1.18.2 rozbija tier na osobne registry ID, np. `basic_energy_cube` i
  `basic_chemical_tank`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .common import StackTank, Tier


ENERGY_CUBE_1710: dict[Tier, tuple[float, float]] = {
    Tier.BASIC: (2_000_000.0, 800.0),
    Tier.ADVANCED: (8_000_000.0, 3_200.0),
    Tier.ELITE: (32_000_000.0, 12_800.0),
    Tier.ULTIMATE: (128_000_000.0, 51_200.0),
    Tier.CREATIVE: (float("inf"), float("inf")),
}

GAS_TANK_1710: dict[Tier, tuple[int, int]] = {
    Tier.BASIC: (64_000, 256),
    Tier.ADVANCED: (128_000, 512),
    Tier.ELITE: (256_000, 1_028),
    Tier.ULTIMATE: (512_000, 2_056),
}


class DumpingMode(Enum):
    IDLE = 0
    DUMPING = 1
    DUMPING_EXCESS = 2


@dataclass
class EnergyCube1710:
    tier: Tier
    energy_joules: float

    @property
    def capacity(self) -> float:
        return ENERGY_CUBE_1710[self.tier][0]

    @property
    def output(self) -> float:
        return ENERGY_CUBE_1710[self.tier][1]

    def to_1182(self, target_capacity: float | None = None) -> "EnergyCube1182":
        capacity = target_capacity or self.capacity
        ratio = 1.0 if self.tier is Tier.CREATIVE else max(0.0, min(1.0, self.energy_joules / self.capacity))
        return EnergyCube1182(self.tier, capacity * ratio, capacity, "ratio_preserved")


@dataclass
class EnergyCube1182:
    tier: Tier
    energy: float
    capacity: float
    conversion_policy: str

    @property
    def block_id(self) -> str:
        return f"mekanism:{self.tier.value}_energy_cube"


@dataclass
class GasTank1710:
    tier: Tier
    gas_id: str | None
    amount: int
    dumping: DumpingMode = DumpingMode.IDLE

    @property
    def capacity(self) -> int:
        return GAS_TANK_1710[self.tier][0]

    @property
    def output(self) -> int:
        return GAS_TANK_1710[self.tier][1]

    def to_1182(self) -> "ChemicalTank1182":
        chemical_id = gas_to_chemical_id(self.gas_id)
        tank = StackTank(chemical_id, min(self.amount, self.capacity), self.capacity)
        return ChemicalTank1182(self.tier, tank, self.dumping)


@dataclass
class ChemicalTank1182:
    tier: Tier
    chemical_tank: StackTank
    dumping: DumpingMode

    @property
    def block_id(self) -> str:
        return f"mekanism:{self.tier.value}_chemical_tank"


@dataclass
class Frequency1710:
    name: str
    owner_name: str | None
    public: bool = False

    def to_1182(self, owner_uuid: str | None = None) -> "Frequency1182":
        warnings = []
        if self.owner_name and not owner_uuid:
            warnings.append("missing_owner_uuid")
        return Frequency1182(self.name, owner_uuid, self.owner_name, self.public, warnings)


@dataclass
class Frequency1182:
    name: str
    owner_uuid: str | None
    owner_name_legacy: str | None
    public: bool
    warnings: list[str]


def gas_to_chemical_id(gas_id: str | None) -> str | None:
    if gas_id is None:
        return None
    stripped = gas_id.replace("gas:", "").replace("Mekanism:", "").lower()
    aliases = {
        "hydrogenchloride": "hydrogen_chloride",
        "sulfuricacid": "sulfuric_acid",
        "sulfurdioxide": "sulfur_dioxide",
        "sulfurtrioxide": "sulfur_trioxide",
    }
    return f"mekanism:{aliases.get(stripped, stripped)}"


def compare_storage_roundtrip() -> tuple[EnergyCube1182, ChemicalTank1182, Frequency1182]:
    cube = EnergyCube1710(Tier.ADVANCED, 4_000_000).to_1182()
    tank = GasTank1710(Tier.BASIC, "gas:hydrogen_chloride", 32_000).to_1182()
    freq = Frequency1710("Baza", "pawel").to_1182()
    if cube.block_id != "mekanism:advanced_energy_cube" or cube.energy != 4_000_000:
        raise AssertionError("Energy cube conversion did not preserve tier/fill ratio")
    if tank.block_id != "mekanism:basic_chemical_tank" or tank.chemical_tank.content_id != "mekanism:hydrogen_chloride":
        raise AssertionError("GasTank -> ChemicalTank conversion mismatch")
    if "missing_owner_uuid" not in freq.warnings:
        raise AssertionError("Frequency conversion should flag missing UUID")
    return cube, tank, freq


if __name__ == "__main__":
    print(compare_storage_roundtrip())
