"""
Symulacja konwersji maszyn fabrycznych BuildCraft -> 1.18.2.

Obsługuje:
- TileTank -> Mekanism Basic Fluid Tank / Thermal Fluid Cell / Create Fluid Tank
- TilePump -> Mekanism Electric Pump / Create Pump
- TileRefinery -> Thermal Refinery / usunięcie (brak dobrego odpowiednika)

Źródło NBT BuildCraft 1.7.10:
- TileTank: owner, tank {FluidName, Amount} lub {Empty}
- TilePump: owner, battery, tank {acceptedFluid, FluidName, Amount} lub {Empty}, powered, aimY, tubeY
- TileRefinery: owner, tank1/tank2 {acceptedFluid, FluidName, Amount}, result {acceptedFluid}, battery, animationSpeed

Docelowe mody 1.18.2:
- Mekanism: Basic Fluid Tank, Electric Pump
- Thermal: Fluid Cell, various machines
- Create: Fluid Tank, Mechanical Pump
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Optional

# Mapowanie typu maszyny BC -> docelowy blok 1.18.2
FACTORY_TYPE_MAPPING = {
    "net.minecraft.src.buildcraft.factory.TileTank": {
        "action": "CONVERT",
        "target_block": "mekanism:basic_fluid_tank",
        "target_te": "mekanism:tile_basic_fluid_tank",
        "alternatives": ["thermal:fluid_cell", "create:fluid_tank"],
        "note": "Tank BC -> Basic Fluid Tank (Mekanism) - zachowuje zawartość płynu",
    },
    "net.minecraft.src.buildcraft.factory.TilePump": {
        "action": "CONVERT",
        "target_block": "mekanism:electric_pump",
        "target_te": "mekanism:tile_electric_pump",
        "alternatives": ["create:mechanical_pump"],
        "note": "Pump BC -> Electric Pump (Mekanism) - wymaga zasilania FE",
    },
    "net.minecraft.src.buildcraft.factory.Refinery": {
        "action": "CONVERT",
        "target_block": "thermal:machine_refinery",
        "target_te": "thermal:tile_machine_refinery",
        "alternatives": [],
        "fallback_action": "REMOVE",
        "fallback_reason": "Thermal Refinery wymaga konkretnych receptur; brak mapowania oil->fuel z BC",
        "note": "Refinery BC -> Thermal Refinery (jeśli dostępna receptura); inaczej REMOVE",
    },
}

# Mapowanie nazw płynów BC -> nazwy płynów 1.18.2
# Wiele płynów BC ma odpowiedniki w Thermal / Mekanism
FLUID_NAME_MAPPING = {
    "oil": "thermal:crude_oil",           # lub "immersiveengineering:fluid_crude_oil"
    "fuel": "thermal:refined_fuel",       # lub "immersivepetroleum:gasoline"
    "water": "minecraft:water",
    "lava": "minecraft:lava",
    "biofuel": "thermal:tree_oil",        # przybliżenie
}


@dataclass
class TankState1710:
    """Stan tanku BuildCraft 1.7.10."""
    te_id: str
    x: int
    y: int
    z: int
    owner: Optional[str] = None
    fluid_name: Optional[str] = None
    fluid_amount: int = 0

    @classmethod
    def from_nbt(cls, nbt: dict[str, Any]) -> "TankState1710":
        tank = nbt.get("tank", {})
        fluid_name = None
        fluid_amount = 0
        if tank and not tank.get("Empty"):
            fluid_name = tank.get("FluidName")
            fluid_amount = tank.get("Amount", 0)
        return cls(
            te_id=nbt.get("id", ""),
            x=nbt.get("x", 0),
            y=nbt.get("y", 0),
            z=nbt.get("z", 0),
            owner=nbt.get("owner"),
            fluid_name=fluid_name,
            fluid_amount=fluid_amount,
        )


@dataclass
class PumpState1710:
    """Stan pompy BuildCraft 1.7.10."""
    te_id: str
    x: int
    y: int
    z: int
    owner: Optional[str] = None
    powered: int = 0
    aim_y: int = 0
    tube_y: float = 0.0
    battery_energy: int = 0
    battery_max: int = 1000
    fluid_name: Optional[str] = None
    fluid_amount: int = 0

    @classmethod
    def from_nbt(cls, nbt: dict[str, Any]) -> "PumpState1710":
        tank = nbt.get("tank", {})
        fluid_name = None
        fluid_amount = 0
        if tank and not tank.get("Empty"):
            fluid_name = tank.get("FluidName") or tank.get("acceptedFluid")
            fluid_amount = tank.get("Amount", 0)
        battery = nbt.get("battery", {})
        return cls(
            te_id=nbt.get("id", ""),
            x=nbt.get("x", 0),
            y=nbt.get("y", 0),
            z=nbt.get("z", 0),
            owner=nbt.get("owner"),
            powered=nbt.get("powered", 0),
            aim_y=nbt.get("aimY", 0),
            tube_y=nbt.get("tubeY", 0.0),
            battery_energy=battery.get("energy", 0),
            battery_max=battery.get("maxEnergy", 1000),
            fluid_name=fluid_name,
            fluid_amount=fluid_amount,
        )


@dataclass
class RefineryState1710:
    """Stan rafinerii BuildCraft 1.7.10."""
    te_id: str
    x: int
    y: int
    z: int
    owner: Optional[str] = None
    tank1_name: Optional[str] = None
    tank1_amount: int = 0
    tank2_name: Optional[str] = None
    tank2_amount: int = 0
    result_name: Optional[str] = None
    battery_energy: int = 0
    battery_max: int = 10000
    animation_speed: float = 0.0

    @classmethod
    def from_nbt(cls, nbt: dict[str, Any]) -> "RefineryState1710":
        def extract_fluid(tank_nbt):
            if not tank_nbt or tank_nbt.get("Empty"):
                return None, 0
            return tank_nbt.get("FluidName"), tank_nbt.get("Amount", 0)

        t1_name, t1_amt = extract_fluid(nbt.get("tank1"))
        t2_name, t2_amt = extract_fluid(nbt.get("tank2"))
        res = nbt.get("result", {})
        res_name = res.get("acceptedFluid") if not res.get("Empty") else None
        battery = nbt.get("battery", {})
        return cls(
            te_id=nbt.get("id", ""),
            x=nbt.get("x", 0),
            y=nbt.get("y", 0),
            z=nbt.get("z", 0),
            owner=nbt.get("owner"),
            tank1_name=t1_name,
            tank1_amount=t1_amt,
            tank2_name=t2_name,
            tank2_amount=t2_amt,
            result_name=res_name,
            battery_energy=battery.get("energy", 0),
            battery_max=battery.get("maxEnergy", 10000),
            animation_speed=nbt.get("animationSpeed", 0.0),
        )


@dataclass
class MachineState1182:
    """Stan maszyny 1.18.2 (Mekanism / Thermal / Create)."""
    block_id: str
    te_id: str
    x: int
    y: int
    z: int
    fluid_tanks: list[dict[str, Any]] = field(default_factory=list)
    energy_fe: int = 0
    energy_max: int = 0
    extra_nbt: dict[str, Any] = field(default_factory=dict)


def convert_fluid_name(bc_name: Optional[str]) -> Optional[str]:
    """Mapuje nazwę płynu BC na nazwę 1.18.2."""
    if not bc_name:
        return None
    return FLUID_NAME_MAPPING.get(bc_name.lower(), bc_name)


def simulate_tank_conversion(state_1710: TankState1710) -> dict[str, Any]:
    """Symuluje konwersję tanku BC na tank 1.18.2."""
    mapping = FACTORY_TYPE_MAPPING[state_1710.te_id]
    fluid_name_1182 = convert_fluid_name(state_1710.fluid_name)

    fluid_tanks = []
    if fluid_name_1182 and state_1710.fluid_amount > 0:
        fluid_tanks.append({
            "Tank": 0,
            "FluidName": fluid_name_1182,
            "Amount": state_1710.fluid_amount,
        })

    state_1182 = MachineState1182(
        block_id=mapping["target_block"],
        te_id=mapping["target_te"],
        x=state_1710.x,
        y=state_1710.y,
        z=state_1710.z,
        fluid_tanks=fluid_tanks,
        energy_max=14000,  # Basic Fluid Tank capacity w Mekanism
    )

    return {
        "action": "CONVERT",
        "note": mapping["note"],
        "source_te": state_1710.te_id,
        "target": state_1182,
    }


def simulate_pump_conversion(state_1710: PumpState1710) -> dict[str, Any]:
    """Symuluje konwersję pompy BC na pompę 1.18.2."""
    mapping = FACTORY_TYPE_MAPPING[state_1710.te_id]
    fluid_name_1182 = convert_fluid_name(state_1710.fluid_name)

    fluid_tanks = []
    if fluid_name_1182 and state_1710.fluid_amount > 0:
        fluid_tanks.append({
            "Tank": 0,
            "FluidName": fluid_name_1182,
            "Amount": state_1710.fluid_amount,
        })

    # Mekanism Electric Pump wymaga energii FE do pracy
    # Zachowujemy energię z battery BC (zakładając 1:1 lub konwersję)
    energy_fe = state_1710.battery_energy * 10  # MJ->FE przybliżenie

    state_1182 = MachineState1182(
        block_id=mapping["target_block"],
        te_id=mapping["target_te"],
        x=state_1710.x,
        y=state_1710.y,
        z=state_1710.z,
        fluid_tanks=fluid_tanks,
        energy_fe=min(energy_fe, 100000),  # cap dla Electric Pump
        energy_max=100000,
    )

    return {
        "action": "CONVERT",
        "note": mapping["note"],
        "source_te": state_1710.te_id,
        "target": state_1182,
    }


def simulate_refinery_conversion(state_1710: RefineryState1710) -> dict[str, Any]:
    """Symuluje konwersję rafinerii BC na maszynę 1.18.2."""
    mapping = FACTORY_TYPE_MAPPING[state_1710.te_id]

    # Decyzja użytkownika: custom receptura oil -> fuel w Thermal Refinery.
    # Zawsze konwertujemy Refinery na Thermal Refinery, niezależnie od zawartości.

    t1_name = convert_fluid_name(state_1710.tank1_name)
    t2_name = convert_fluid_name(state_1710.tank2_name)

    fluid_tanks = []
    if t1_name and state_1710.tank1_amount > 0:
        fluid_tanks.append({"Tank": 0, "FluidName": t1_name, "Amount": state_1710.tank1_amount})
    if t2_name and state_1710.tank2_amount > 0:
        fluid_tanks.append({"Tank": 1, "FluidName": t2_name, "Amount": state_1710.tank2_amount})

    energy_fe = state_1710.battery_energy * 10

    state_1182 = MachineState1182(
        block_id=mapping["target_block"],
        te_id=mapping["target_te"],
        x=state_1710.x,
        y=state_1710.y,
        z=state_1710.z,
        fluid_tanks=fluid_tanks,
        energy_fe=min(energy_fe, 20000),
        energy_max=20000,
    )

    return {
        "action": "CONVERT",
        "note": mapping["note"],
        "warning": "Wymaga dodania custom receptury oil->fuel w data packu / KubeJS / CraftTweaker",
        "source_te": state_1710.te_id,
        "target": state_1182,
    }


def print_factory_report(result: dict[str, Any]) -> None:
    """Drukuje czytelny raport z konwersji maszyny."""
    action = result["action"]
    src = result.get("source_te", result.get("original", {}).get("te_id", "?"))
    print(f"[Factory] {src} -> {action}")
    if action == "REMOVE":
        print(f"  Powód: {result['reason']}")
    elif action == "CONVERT":
        tgt = result["target"]
        print(f"  Blok docelowy: {tgt.block_id}")
        if tgt.fluid_tanks:
            print(f"  Zawartość płynów:")
            for tank in tgt.fluid_tanks:
                print(f"    Tank {tank.get('Tank')}: {tank.get('FluidName')} ({tank.get('Amount')} mB)")
        if tgt.energy_max > 0:
            print(f"  Energia: {tgt.energy_fe} / {tgt.energy_max} FE")
        if result.get("warning"):
            print(f"  UWAGA: {result['warning']}")
    print()


# =============================================================================
# TESTY / PRZYKŁADY UŻYCIA
# =============================================================================

if __name__ == "__main__":
    # Przykład 1: Pusty tank
    empty_tank_nbt = {
        "id": "net.minecraft.src.buildcraft.factory.TileTank",
        "x": 200, "y": 64, "z": 300,
        "owner": "TestPlayer",
        "tank": {"Empty": ""},
    }
    tank_state = TankState1710.from_nbt(empty_tank_nbt)
    result = simulate_tank_conversion(tank_state)
    print_factory_report(result)
    assert result["action"] == "CONVERT"
    assert result["target"].block_id == "mekanism:basic_fluid_tank"
    assert len(result["target"].fluid_tanks) == 0

    # Przykład 2: Tank z wodą
    water_tank_nbt = {
        "id": "net.minecraft.src.buildcraft.factory.TileTank",
        "x": 201, "y": 64, "z": 300,
        "owner": "TestPlayer",
        "tank": {"FluidName": "water", "Amount": 8000},
    }
    tank_state = TankState1710.from_nbt(water_tank_nbt)
    result = simulate_tank_conversion(tank_state)
    print_factory_report(result)
    assert result["target"].fluid_tanks[0]["FluidName"] == "minecraft:water"
    assert result["target"].fluid_tanks[0]["Amount"] == 8000

    # Przykład 3: Pump (pusta)
    pump_nbt = {
        "id": "net.minecraft.src.buildcraft.factory.TilePump",
        "x": 202, "y": 64, "z": 300,
        "owner": "TestPlayer",
        "powered": 1,
        "aimY": 60,
        "tubeY": 63.5,
        "battery": {"energy": 500, "maxEnergy": 1000},
        "tank": {"Empty": ""},
    }
    pump_state = PumpState1710.from_nbt(pump_nbt)
    result = simulate_pump_conversion(pump_state)
    print_factory_report(result)
    assert result["target"].block_id == "mekanism:electric_pump"
    assert result["target"].energy_fe == 5000

    # Przykład 4: Refinery z oil
    refinery_nbt = {
        "id": "net.minecraft.src.buildcraft.factory.Refinery",
        "x": 203, "y": 64, "z": 300,
        "owner": "TestPlayer",
        "tank1": {"acceptedFluid": "oil", "Empty": ""},
        "tank2": {"acceptedFluid": "oil", "FluidName": "oil", "Amount": 151},
        "result": {"acceptedFluid": "fuel", "Empty": ""},
        "battery": {"energy": 0, "maxEnergy": 10000},
        "animationSpeed": 0.5,
    }
    refinery_state = RefineryState1710.from_nbt(refinery_nbt)
    result = simulate_refinery_conversion(refinery_state)
    print_factory_report(result)
    assert result["action"] == "CONVERT"
    assert result["target"].block_id == "thermal:machine_refinery"

    # Przykład 5: Refinery bez oil -> REMOVE
    refinery_nbt2 = {
        "id": "net.minecraft.src.buildcraft.factory.Refinery",
        "x": 204, "y": 64, "z": 300,
        "owner": "TestPlayer",
        "tank1": {"acceptedFluid": "oil", "Empty": ""},
        "tank2": {"acceptedFluid": "oil", "Empty": ""},
        "result": {"acceptedFluid": "fuel", "Empty": ""},
        "battery": {"energy": 0, "maxEnergy": 10000},
        "animationSpeed": 0.0,
    }
    refinery_state2 = RefineryState1710.from_nbt(refinery_nbt2)
    result2 = simulate_refinery_conversion(refinery_state2)
    print_factory_report(result2)
    assert result2["action"] == "REMOVE"

    print("=" * 60)
    print("Wszystkie symulacje fabryczne zakończone sukcesem.")
    print("=" * 60)
