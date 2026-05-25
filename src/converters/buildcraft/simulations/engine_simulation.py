"""
Symulacja konwersji silników BuildCraft -> generatory 1.18.2.

Obsługuje:
- TileEngineWood (Redstone Engine) -> decyzja REMOVE
- TileEngineStone (Stirling Engine) -> Thermal Steam Dynamo
- TileEngineIron (Combustion Engine) -> Thermal Compression Dynamo (lub REMOVE)

Źródło NBT BuildCraft 1.7.10:
- orientation: int (0=down, 1=up, 2=north, 3=south, 4=west, 5=east)
- heat: float
- energy: int (MJ)
- burnTime / totalBurnTime: int (Stone)
- tankFuel / tankCoolant: fluid tanks (Iron)
- Items: inventory (fuel slots)

Docelowe mody 1.18.2:
- Thermal Expansion: Dynamo (Steam, Compression, Magmatic)
- Mekanism: Heat Generator (nieidealny zamiennik)
"""

from __future__ import annotations

import math
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Optional

# Mnożnik energii: BuildCraft MJ -> Forge Energy FE
# Współczynnik przyjęty konserwatywnie; konfigurowalny w zależności od balansu paczki.
MJ_TO_FE = 10.0

# Mapowanie orientacji BuildCraft -> facing string 1.18.2
# BuildCraft engine.orientation: strona wyjścia energii (lub wejścia dla maszyn)
BC_ORIENTATION_TO_FACING = {
    0: "down",
    1: "up",
    2: "north",
    3: "south",
    4: "west",
    5: "east",
}

# Mapowanie typu silnika BC -> docelowy blok 1.18.2
ENGINE_TYPE_MAPPING = {
    "net.minecraft.src.buildcraft.energy.TileEngineWood": {
        "action": "REMOVE",
        "reason": "Redstone Engine jest zbyt słaby; brak sensownego odpowiednika w 1.18.2",
    },
    "net.minecraft.src.buildcraft.energy.TileEngineStone": {
        "action": "CONVERT",
        "target_block": "thermal:dynamo_steam",
        "target_te": "thermal:tile_dynamo_steam",
        "note": "Stirling Engine zasilany solid fuel -> Steam Dynamo",
    },
    "net.minecraft.src.buildcraft.energy.TileEngineIron": {
        "action": "CONVERT",
        "target_block": "thermal:dynamo_compression",
        "target_te": "thermal:tile_dynamo_compression",
        "note": "Combustion Engine zasilany płynami -> Compression Dynamo (jeśli dostępny w paczce); inaczej REMOVE",
    },
}


@dataclass
class EngineState1710:
    """Stan silnika BuildCraft 1.7.10."""
    te_id: str
    x: int
    y: int
    z: int
    owner: Optional[str] = None
    orientation: int = 1  # domyślnie up
    heat: float = 20.0
    energy: int = 0  # MJ
    progress: float = 0.0
    # Stirling only
    burn_time: int = 0
    total_burn_time: int = 0
    items: list[dict[str, Any]] = field(default_factory=list)
    # Combustion only
    tank_fuel: Optional[dict[str, Any]] = None  # {"FluidName": str, "Amount": int}
    tank_coolant: Optional[dict[str, Any]] = None
    penalty_cooling: int = 0

    @classmethod
    def from_nbt(cls, nbt: dict[str, Any]) -> "EngineState1710":
        """Parsuje NBT BuildCraft 1.7.10."""
        return cls(
            te_id=nbt.get("id", ""),
            x=nbt.get("x", 0),
            y=nbt.get("y", 0),
            z=nbt.get("z", 0),
            owner=nbt.get("owner"),
            orientation=nbt.get("orientation", 1),
            heat=nbt.get("heat", 20.0),
            energy=nbt.get("energy", 0),
            progress=nbt.get("progress", 0.0),
            burn_time=nbt.get("burnTime", 0),
            total_burn_time=nbt.get("totalBurnTime", 0),
            items=nbt.get("Items", []),
            tank_fuel=nbt.get("tankFuel") if nbt.get("tankFuel") and not nbt.get("tankFuel", {}).get("Empty") else None,
            tank_coolant=nbt.get("tankCoolant") if nbt.get("tankCoolant") and not nbt.get("tankCoolant", {}).get("Empty") else None,
            penalty_cooling=nbt.get("penaltyCooling", 0),
        )


@dataclass
class GeneratorState1182:
    """Stan generatora 1.18.2 (Thermal Dynamo lub inny)."""
    block_id: str
    te_id: str
    x: int
    y: int
    z: int
    facing: str = "north"
    energy_fe: int = 0
    inventory: list[dict[str, Any]] = field(default_factory=list)
    fluid_tanks: list[dict[str, Any]] = field(default_factory=list)
    # Thermal-specific
    augments: list[str] = field(default_factory=list)
    # Dodatkowe pola zależne od targetu
    extra_nbt: dict[str, Any] = field(default_factory=dict)


def convert_orientation(bc_orientation: int) -> str:
    """Konwertuje orientację BC na facing string 1.18.2."""
    return BC_ORIENTATION_TO_FACING.get(bc_orientation, "north")


def convert_energy_mj_to_fe(energy_mj: float) -> int:
    """Konwertuje energię MJ na FE z zaokrągleniem w dół."""
    return max(0, int(math.floor(energy_mj * MJ_TO_FE)))


def convert_fuel_items(items_1710: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Konwertuje sloty paliwa BC na format 1.18.2.

    BuildCraft 1.7.10 używa formatu:
      {"Slot": 0, "id": 263, "Count": 64, "Damage": 0}
    Thermal 1.18.2 oczekuje podobnego formatu NBT (Items list).
    Zakładamy że konwersja ID itemów nastąpi na późniejszym etapie (item mapping).
    """
    converted = []
    for item in items_1710:
        converted.append({
            "Slot": item.get("Slot", 0),
            "id": item.get("id", 0),      # TODO: mapowanie ID numerycznego -> string ID 1.18.2
            "Count": item.get("Count", 0),
            "Damage": item.get("Damage", 0),
        })
    return converted


def convert_fluid_tank(tank_nbt: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
    """Konwertuje tank BC na format fluid tank 1.18.2."""
    if not tank_nbt:
        return None
    fluid_name = tank_nbt.get("FluidName", "")
    amount = tank_nbt.get("Amount", 0)
    if not fluid_name or amount <= 0:
        return None
    return {
        "FluidName": fluid_name,   # TODO: mapowanie nazwy płynu BC -> 1.18.2 (np. "fuel" -> "thermal:refined_fuel")
        "Amount": amount,
    }


def simulate_engine_conversion(state_1710: EngineState1710) -> dict[str, Any]:
    """Symuluje konwersję silnika BC na generator 1.18.2.

    Zwraca słownik z decyzją i stanem docelowym (lub powód usunięcia).
    """
    mapping = ENGINE_TYPE_MAPPING.get(state_1710.te_id)
    if not mapping:
        return {
            "action": "UNKNOWN",
            "reason": f"Nieznany typ silnika: {state_1710.te_id}",
        }

    if mapping["action"] == "REMOVE":
        return {
            "action": "REMOVE",
            "reason": mapping["reason"],
            "original": {
                "te_id": state_1710.te_id,
                "x": state_1710.x,
                "y": state_1710.y,
                "z": state_1710.z,
            },
        }

    # CONVERT
    facing = convert_orientation(state_1710.orientation)
    energy_fe = convert_energy_mj_to_fe(state_1710.energy)

    # Przygotuj inventory (dla Stirling/Compression)
    inventory = convert_fuel_items(state_1710.items)

    # Przygotuj fluid tanks (dla Compression)
    fluid_tanks = []
    fuel_tank = convert_fluid_tank(state_1710.tank_fuel)
    if fuel_tank:
        fluid_tanks.append({"Tank": 0, **fuel_tank})
    coolant_tank = convert_fluid_tank(state_1710.tank_coolant)
    if coolant_tank:
        fluid_tanks.append({"Tank": 1, **coolant_tank})

    state_1182 = GeneratorState1182(
        block_id=mapping["target_block"],
        te_id=mapping["target_te"],
        x=state_1710.x,
        y=state_1710.y,
        z=state_1710.z,
        facing=facing,
        energy_fe=energy_fe,
        inventory=inventory,
        fluid_tanks=fluid_tanks,
    )

    return {
        "action": "CONVERT",
        "note": mapping.get("note", ""),
        "source_te": state_1710.te_id,
        "target": state_1182,
    }


def print_conversion_report(result: dict[str, Any]) -> None:
    """Drukuje czytelny raport z konwersji."""
    action = result["action"]
    src = result.get("source_te", result.get("original", {}).get("te_id", "?"))
    print(f"[Engine] {src} -> {action}")
    if action == "REMOVE":
        print(f"  Powód: {result['reason']}")
    elif action == "CONVERT":
        tgt = result["target"]
        print(f"  Blok docelowy: {tgt.block_id}")
        print(f"  Facing: {tgt.facing}")
        print(f"  Energia (FE): {tgt.energy_fe}")
        if tgt.inventory:
            print(f"  Inventory slots: {len(tgt.inventory)}")
        if tgt.fluid_tanks:
            print(f"  Fluid tanks: {len(tgt.fluid_tanks)}")
            for tank in tgt.fluid_tanks:
                print(f"    Tank {tank.get('Tank')}: {tank.get('FluidName')} ({tank.get('Amount')} mB)")
    print()


# =============================================================================
# TESTY / PRZYKŁADY UŻYCIA
# =============================================================================

if __name__ == "__main__":
    # Przykład 1: Redstone Engine (Wood) -> REMOVE
    wood_nbt = {
        "id": "net.minecraft.src.buildcraft.energy.TileEngineWood",
        "x": 100, "y": 64, "z": 200,
        "owner": "TestPlayer",
        "orientation": 3,
        "heat": 20.0,
        "energy": 0,
        "progress": 0.0,
    }
    wood_state = EngineState1710.from_nbt(wood_nbt)
    result = simulate_engine_conversion(wood_state)
    print_conversion_report(result)
    assert result["action"] == "REMOVE"

    # Przykład 2: Stirling Engine (Stone) -> Steam Dynamo
    stone_nbt = {
        "id": "net.minecraft.src.buildcraft.energy.TileEngineStone",
        "x": 101, "y": 64, "z": 200,
        "owner": "TestPlayer",
        "orientation": 2,
        "heat": 25.0,
        "energy": 500,
        "progress": 0.5,
        "burnTime": 1200,
        "totalBurnTime": 1600,
        "Items": [
            {"Slot": 0, "id": 263, "Count": 32, "Damage": 0},  # coal
        ],
    }
    stone_state = EngineState1710.from_nbt(stone_nbt)
    result = simulate_engine_conversion(stone_state)
    print_conversion_report(result)
    assert result["action"] == "CONVERT"
    assert result["target"].block_id == "thermal:dynamo_steam"
    assert result["target"].facing == "north"
    assert result["target"].energy_fe == 5000  # 500 MJ * 10

    # Przykład 3: Combustion Engine (Iron) -> Compression Dynamo
    iron_nbt = {
        "id": "net.minecraft.src.buildcraft.energy.TileEngineIron",
        "x": 102, "y": 64, "z": 200,
        "owner": "TestPlayer",
        "orientation": 4,
        "heat": 50.0,
        "energy": 2000,
        "progress": 0.8,
        "burnTime": 800,
        "penaltyCooling": 2,
        "tankFuel": {"FluidName": "fuel", "Amount": 4000},
        "tankCoolant": {"FluidName": "water", "Amount": 2000},
        "Items": [],
    }
    iron_state = EngineState1710.from_nbt(iron_nbt)
    result = simulate_engine_conversion(iron_state)
    print_conversion_report(result)
    assert result["action"] == "CONVERT"
    assert result["target"].block_id == "thermal:dynamo_compression"
    assert result["target"].facing == "west"
    assert result["target"].energy_fe == 20000  # 2000 MJ * 10
    assert len(result["target"].fluid_tanks) == 2

    print("=" * 60)
    print("Wszystkie symulacje silników zakończone sukcesem.")
    print("=" * 60)
