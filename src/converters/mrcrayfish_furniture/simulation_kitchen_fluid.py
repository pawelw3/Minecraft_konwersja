# -*- coding: utf-8 -*-
"""
Symulacja systemu plynow kuchennych — MrCrayfish Furniture Mod 1.7.10 vs 1.18.2

Pokazuje roznice w obsludze plynow:
- 1.7.10: CounterSink, Basin, Bath, ShowerHead uzywaja prostego boolean / poziomu wody
  TileEntityCounterSink: boolean hasWater
  TileEntityBasin: int waterLevel (0-8)
  TileEntityBath: boolean / poziom
  TileEntityShowerHead: boolean on
- 1.18.2: KitchenSinkBlockEntity uzywa FluidTank (Forge capability)
  FluidTank: max 10000 mB, NBT: Tank {FluidName, Amount}

Bazuje na kodzie zrodlowym:
- 1.7.10: TileEntityCounterSink.java, TileEntityBasin.java, TileEntityBath.java, TileEntityShowerHead.java
- 1.18.2: KitchenSinkBlockEntity.java (FluidTankSyncedBlockEntity)
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


# ============================================================
# 1.7.10 — Proste systemy wodne (boolean / poziom)
# ============================================================

class TileEntityCounterSink1710:
    """
    Symulacja TileEntityCounterSink z 1.7.10
    Przechowuje: boolean hasWater (0 lub 1)
    Kod: TileEntityCounterSink.java
    """
    def __init__(self):
        self.has_water: bool = False

    def write_to_nbt(self) -> Dict:
        return {"id": "cfmCounterSink", "HasWater": int(self.has_water)}

    def read_from_nbt(self, nbt: Dict):
        self.has_water = bool(nbt.get("HasWater", 0))


class TileEntityBasin1710:
    """
    Symulacja TileEntityBasin z 1.7.10
    Przechowuje: poziom wody (int, zakres 0-8, podobnie jak Cauldron)
    Kod: TileEntityBasin.java
    """
    MAX_LEVEL = 8

    def __init__(self):
        self.water_level: int = 0

    def write_to_nbt(self) -> Dict:
        return {"id": "cfmBasin", "WaterLevel": self.water_level}

    def read_from_nbt(self, nbt: Dict):
        self.water_level = nbt.get("WaterLevel", 0)

    def fill(self):
        self.water_level = self.MAX_LEVEL

    def drain(self):
        self.water_level = 0


class TileEntityBath1710:
    """
    Symulacja TileEntityBath z 1.7.10
    Wanna (2-blokowy wieloblok) — przechowuje stan wypelnienia
    Kod: TileEntityBath.java
    """
    def __init__(self):
        self.filled: bool = False
        self.water_level: int = 0  # Prosty poziom

    def write_to_nbt(self) -> Dict:
        return {"id": "cfmBath", "Filled": int(self.filled), "WaterLevel": self.water_level}

    def read_from_nbt(self, nbt: Dict):
        self.filled = bool(nbt.get("Filled", 0))
        self.water_level = nbt.get("WaterLevel", 0)


class TileEntityShowerHead1710:
    """
    Symulacja TileEntityShowerHead z 1.7.10
    Przechowuje: boolean on (czy woda leci)
    Kod: TileEntityShowerHead.java
    """
    def __init__(self):
        self.on: bool = False

    def write_to_nbt(self) -> Dict:
        return {"id": "cfmShowerHead", "On": int(self.on)}

    def read_from_nbt(self, nbt: Dict):
        self.on = bool(nbt.get("On", 0))


# ============================================================
# 1.18.2 — FluidTank w KitchenSink
# ============================================================

@dataclass
class FluidStack:
    """Reprezentacja FluidStack z Forge 1.18.2"""
    fluid_name: str  # np. "minecraft:water", "minecraft:lava"
    amount: int      # mB

    def to_nbt(self) -> Dict:
        return {"FluidName": self.fluid_name, "Amount": self.amount}

    @classmethod
    def from_nbt(cls, nbt: Dict) -> "FluidStack":
        return cls(
            fluid_name=nbt.get("FluidName", ""),
            amount=nbt.get("Amount", 0)
        )

    def is_empty(self) -> bool:
        return self.fluid_name == "" or self.amount <= 0


class FluidTank:
    """
    Symulacja FluidTank z Forge 1.18.2
    Uzywany w KitchenSinkBlockEntity
    """
    def __init__(self, capacity: int = 10000):
        self.capacity = capacity
        self.fluid: Optional[FluidStack] = None

    def fill(self, fluid: FluidStack, action: str = "execute") -> int:
        """
        action: "execute" lub "simulate"
        Zwraca ile mB zostalo przyjetych
        """
        if fluid.is_empty():
            return 0
        current = self.fluid.amount if self.fluid else 0
        space = self.capacity - current
        accepted = min(fluid.amount, space)

        if action == "execute" and accepted > 0:
            if self.fluid and self.fluid.fluid_name == fluid.fluid_name:
                self.fluid.amount += accepted
            else:
                self.fluid = FluidStack(fluid.fluid_name, accepted)
        return accepted

    def drain(self, max_drain: int, action: str = "execute") -> Optional[FluidStack]:
        if not self.fluid or self.fluid.is_empty():
            return None
        drained = min(max_drain, self.fluid.amount)
        if action == "execute":
            self.fluid.amount -= drained
            if self.fluid.amount <= 0:
                self.fluid = None
        return FluidStack(self.fluid.fluid_name if self.fluid else "", drained)

    def write_to_nbt(self) -> Dict:
        if self.fluid and not self.fluid.is_empty():
            return self.fluid.to_nbt()
        return {}

    def read_from_nbt(self, nbt: Dict):
        if nbt:
            self.fluid = FluidStack.from_nbt(nbt)
        else:
            self.fluid = None

    def get_fill_ratio(self) -> float:
        if not self.fluid or self.fluid.is_empty():
            return 0.0
        return self.fluid.amount / self.capacity


class KitchenSinkBlockEntity1182:
    """
    Symulacja KitchenSinkBlockEntity z 1.18.2
    Kod: KitchenSinkBlockEntity.java (extends FluidTankSyncedBlockEntity)
    Przechowuje FluidTank o pojemnosci 10000 mB
    """
    CAPACITY = 10000

    def __init__(self):
        self.tank = FluidTank(self.CAPACITY)

    def write_to_nbt(self) -> Dict:
        nbt = {"id": "cfm:kitchen_sink"}
        # Forge 1.18.2 FluidTank zapisuje bezposrednio do root compound
        tank_nbt = self.tank.write_to_nbt()
        if tank_nbt:
            nbt.update(tank_nbt)
        return nbt

    def read_from_nbt(self, nbt: Dict):
        # Bez wrappera "Tank" - patrz FluidHandlerSyncedBlockEntity
        self.tank.read_from_nbt(nbt)

    def add_water(self, amount_mb: int = 1000):
        """Dodaje wode do zlewu (np. z wiadra)"""
        water = FluidStack("minecraft:water", amount_mb)
        return self.tank.fill(water, "execute")

    def use_water(self, amount_mb: int = 1000):
        """Zuzywa wode (np. mycie)"""
        drained = self.tank.drain(amount_mb, "execute")
        return drained.amount if drained else 0


# ============================================================
# Konwersja 1.7.10 -> 1.18.2
# ============================================================

def convert_counter_sink_to_kitchen_sink(source_nbt: Dict) -> Dict:
    """
    Konwersja TileEntityCounterSink 1.7.10 -> KitchenSinkBlockEntity 1.18.2
    Decyzja projektowa: CounterSink (boolean hasWater) -> KitchenSink (FluidTank)
    Format NBT: Forge zapisuje FluidTank bezposrednio w root compound
    """
    has_water = bool(source_nbt.get("HasWater", 0))
    target = KitchenSinkBlockEntity1182()
    if has_water:
        target.add_water(5000)
    return target.write_to_nbt()


def convert_basin_to_kitchen_sink(source_nbt: Dict) -> Dict:
    """
    Konwersja TileEntityBasin 1.7.10 -> KitchenSinkBlockEntity 1.18.2
    Basin ma poziom 0-8, mapujemy liniowo na 0-10000 mB
    Decyzja: Basin -> KitchenSink (zamiast placeholdera)
    Format NBT: Forge zapisuje FluidTank bezposrednio w root compound
    """
    level = source_nbt.get("WaterLevel", 0)
    target = KitchenSinkBlockEntity1182()
    if level > 0:
        amount = int((level / 8.0) * target.CAPACITY)
        target.add_water(amount)
    return target.write_to_nbt()


def convert_bath_or_shower_to_placeholder(source_nbt: Dict, block_type: str) -> Dict:
    """
    Bath i Shower nie maja odpowiednika w 1.18.2.
    Zgodnie z decyzja: placeholdery.
    Zwraca NBT placeholdera z informacja o zrodle.
    """
    return {
        "id": "minecraft:barrier",  # Placeholder
        "CustomName": f"{block_type}_placeholder",
        "SourceMod": "cfm",
        "SourceBlock": block_type,
        "OriginalNBT": source_nbt
    }


# ============================================================
# Demonstracja / Testy
# ============================================================

def demo():
    print("=" * 60)
    print("Symulacja: Kitchen Fluid Systems")
    print("1.7.10 (boolean/level) -> 1.18.2 (FluidTank)")
    print("=" * 60)

    # --- CounterSink ---
    print("\n--- CounterSink 1.7.10 -> KitchenSink 1.18.2 ---")
    cs = TileEntityCounterSink1710()
    cs.has_water = True
    nbt_cs = cs.write_to_nbt()
    print(f"1.7.10 NBT: {nbt_cs}")

    converted = convert_counter_sink_to_kitchen_sink(nbt_cs)
    print(f"1.18.2 NBT: {converted}")

    cs_empty = TileEntityCounterSink1710()
    cs_empty.has_water = False
    nbt_cs_empty = cs_empty.write_to_nbt()
    converted_empty = convert_counter_sink_to_kitchen_sink(nbt_cs_empty)
    print(f"1.18.2 NBT (empty): {converted_empty}")

    # --- Basin ---
    print("\n--- Basin 1.7.10 -> KitchenSink 1.18.2 ---")
    for level in [0, 2, 4, 8]:
        basin = TileEntityBasin1710()
        basin.water_level = level
        nbt_basin = basin.write_to_nbt()
        converted_basin = convert_basin_to_kitchen_sink(nbt_basin)
        # Forge 1.18.2 zapisuje FluidTank bezposrednio w root compound
        fluid_name = converted_basin.get("FluidName")
        amount = converted_basin.get("Amount", 0)
        print(f"Basin level={level} -> Sink {fluid_name or 'empty'} {amount}mB")

    # --- KitchenSink tick simulation ---
    print("\n--- 1.18.2 KitchenSink: Symulacja uzycia ---")
    sink = KitchenSinkBlockEntity1182()
    print(f"Pusty: fill_ratio={sink.tank.get_fill_ratio():.2%}")

    added = sink.add_water(3000)
    print(f"Dodano 3000 mB -> przyjeto {added}, fill_ratio={sink.tank.get_fill_ratio():.2%}")

    added2 = sink.add_water(8000)
    print(f"Dodano 8000 mB -> przyjeto {added2} (overflow!), fill_ratio={sink.tank.get_fill_ratio():.2%}")

    used = sink.use_water(2000)
    print(f"Zuzyto 2000 mB -> zuzyto {used}, fill_ratio={sink.tank.get_fill_ratio():.2%}")

    nbt_sink = sink.write_to_nbt()
    print(f"Final NBT: {nbt_sink}")

    # --- Bath/Shower -> Placeholder ---
    print("\n--- Bath/Shower -> Placeholder ---")
    bath = TileEntityBath1710()
    bath.filled = True
    bath.water_level = 5
    nbt_bath = bath.write_to_nbt()
    placeholder = convert_bath_or_shower_to_placeholder(nbt_bath, "bath")
    print(f"Bath placeholder: {placeholder}")

    shower = TileEntityShowerHead1710()
    shower.on = True
    nbt_shower = shower.write_to_nbt()
    placeholder_shower = convert_bath_or_shower_to_placeholder(nbt_shower, "shower_head")
    print(f"Shower placeholder: {placeholder_shower}")

    # --- Round-trip test ---
    print("\n--- Round-trip: NBT -> obiekt -> NBT ---")
    sink2 = KitchenSinkBlockEntity1182()
    sink2.read_from_nbt(nbt_sink)
    nbt2 = sink2.write_to_nbt()
    print(f"Original: {nbt_sink}")
    print(f"Round-trip: {nbt2}")
    assert nbt_sink == nbt2, "Round-trip failed!"
    print("Round-trip OK!")

    print("\n" + "=" * 60)
    print("Symulacja zakonczona pomyslnie.")
    print("=" * 60)


if __name__ == "__main__":
    demo()
