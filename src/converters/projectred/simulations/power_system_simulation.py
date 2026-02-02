"""
ProjectRed Power System Simulation
==================================

Symulacja systemu energii Electrotine dla ProjectRed.
Obejmuje PowerConductor i BatteryBox dla wersji 1.7.10 oraz 1.18.2+.

Bazowane na kodzie zrodlowym:
- 1.7.10: mod_src/1710/actual_src/1.7.10/ProjectRed_GTNH/src/main/scala/mrtjp/projectred/core/powertraits.scala
- 1.7.10: mod_src/1710/actual_src/1.7.10/ProjectRed_GTNH/src/main/scala/mrtjp/projectred/expansion/TileBatteryBox.scala
- 1.18.2: mod_src/118/actual_src/1.18.2/ProjectRed/repo/core/src/main/java/mrtjp/projectred/core/power/PowerConductor.java
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from abc import ABC, abstractmethod
import math


# =============================================================================
# 1.7.10 - Power System Implementation
# =============================================================================

class PowerConductor1710:
    """
    Symulacja PowerConductor z ProjectRed 1.7.10.

    System energii loosely emulates fizyki przeplywu pradu w obwodzie szeregowym.
    Bazowane na kodzie Scala z powertraits.scala.
    """

    def __init__(self, parent: 'IPowerConnectable1710', connection_ids: List[int]):
        """
        Args:
            parent: Obiekt hostujacy conductor (maszyna, kabel)
            connection_ids: Lista mozliwych polaczen do innych conductors
        """
        self.parent = parent
        self.ids = connection_ids

        # Flow array - przeplyw pradu dla kazdego polaczenia
        max_id = max(connection_ids) if connection_ids else 0
        self.flows: List[float] = [0.0] * (max_id + 1)

        # Stan elektryczny
        self.v_loc: float = 0.0  # Local electric potential (Voltage)
        self.i_loc: float = 0.0  # Local electric current (Amps)
        self.v_flow: float = 0.0  # Acquired uncalculated voltage
        self.i_flow: float = 0.0  # Acquired uncalculated current

        self.time: int = 0  # World tick time

        # Surge tracking
        self.surge_in: set = set()

    @property
    def capacitance(self) -> float:
        """Pojemnosc elektryczna"""
        return 0.0

    @property
    def resistance(self) -> float:
        """Opor elektryczny"""
        return 0.01

    @property
    def scale_of_inductance(self) -> float:
        """Skala indukcyjnosci"""
        return 0.07

    @property
    def scale_of_parallel_flow(self) -> float:
        """Skala przeplywu rownoleglego"""
        return 0.5

    def voltage(self, world_time: int) -> float:
        """
        Przelicza V i I jesli potrzeba.

        Returns:
            Potencjal elektryczny w Voltach (V)
        """
        tick = world_time & 0xFFFF
        if tick != self.time:
            self.time = tick
            # Calculate voltage
            self.i_loc = 0.5 * self.i_flow
            self.i_flow = 0.0
            self.v_loc += 0.05 * self.v_flow * self.capacitance
            self.v_flow = 0.0
        return self.v_loc

    def current(self, world_time: int) -> float:
        """
        Returns:
            Prad (I) w Amperach (A)
        """
        self.voltage(world_time)
        return self.i_loc

    def power(self, world_time: int) -> float:
        """
        Returns:
            Moc (P) w Wattach (W)
        """
        return self.voltage(world_time) * self.i_loc

    def apply_current(self, i: float, world_time: int):
        """Aplikuje prad do conductora"""
        self.voltage(world_time)
        self.v_flow += i
        self.i_flow += abs(i)

    def apply_power(self, p: float, world_time: int):
        """
        Aplikuje moc do conductora.

        Args:
            p: Moc w Wattach
        """
        v = self.voltage(world_time)
        p_tot = v * self.v_loc + 0.1 * p * self.capacitance
        dp = math.sqrt(p_tot) - self.v_loc
        self.apply_current(20.0 * dp / self.capacitance, world_time)

    def draw_power(self, p: float, world_time: int):
        """
        Pobiera moc z conductora.

        Args:
            p: Moc do pobrania w Wattach
        """
        v = self.voltage(world_time)
        p_tot = v * self.v_loc - 0.1 * p * self.capacitance
        dp = 0.0 if p_tot < 0.0 else math.sqrt(p_tot) - self.v_loc
        self.apply_current(20.0 * dp / self.capacitance, world_time)

    def power_total(self, world_time: int) -> float:
        """
        Returns:
            Calkowita moc w systemie
        """
        v = self.voltage(world_time)
        return (v * self.v_loc) / (0.1 * self.capacitance) if self.capacitance > 0 else 0

    def update(self, world_time: int):
        """Aktualizacja conductora - wymiana energii z sasiadami"""
        self.voltage(world_time)
        for conn_id in self.ids:
            neighbor = self.parent.conductor_out(conn_id)
            if not self._surge(neighbor, conn_id, world_time):
                self.flows[conn_id] = 0.0
        self.surge_in.clear()

    def _surge(self, cond: Optional['PowerConductor1710'], conn_id: int, world_time: int) -> bool:
        """Wymiana pradu z sasiednim conductorem"""
        if cond is None:
            return False
        if cond.parent == self.parent:
            return False
        if id(cond) in self.surge_in:
            return True

        r = self.resistance + cond.resistance
        i = self.flows[conn_id]
        v = self.v_loc - cond.voltage(world_time)

        self.flows[conn_id] += (v - i * r) * self.scale_of_inductance
        i += v * self.scale_of_parallel_flow

        self.apply_current(-i, world_time)
        cond.apply_surge(self, i, world_time)

        return True

    def apply_surge(self, from_cond: 'PowerConductor1710', i_in: float, world_time: int):
        """Aplikuje surge od innego conductora"""
        self.surge_in.add(id(from_cond))
        self.apply_current(i_in, world_time)

    def save_nbt(self) -> Dict:
        """
        Zapisuje stan do formatu NBT.

        NBT Tags (1.7.10):
        - flow0, flow1, ... (Double): Przeplyw dla kazdego polaczenia
        - vl (Double): v_loc
        - il (Double): i_loc
        - vf (Double): v_flow
        - if (Double): i_flow
        - tm (Integer): time
        """
        nbt = {}
        for i, flow in enumerate(self.flows):
            nbt[f"flow{i}"] = flow
        nbt["vl"] = self.v_loc
        nbt["il"] = self.i_loc
        nbt["vf"] = self.v_flow
        nbt["if"] = self.i_flow
        nbt["tm"] = self.time
        return nbt

    def load_nbt(self, nbt: Dict):
        """Wczytuje stan z NBT"""
        for i in range(len(self.flows)):
            key = f"flow{i}"
            if key in nbt:
                self.flows[i] = nbt[key]
        self.v_loc = nbt.get("vl", 0.0)
        self.i_loc = nbt.get("il", 0.0)
        self.v_flow = nbt.get("vf", 0.0)
        self.i_flow = nbt.get("if", 0.0)
        self.time = nbt.get("tm", 0)


class PowerDrawPoint1710(PowerConductor1710):
    """
    TPowerDrawPoint - conductor z mozliwoscia pobierania mocy.
    Uzyty przez maszyny jak BatteryBox.
    """

    def __init__(self, parent: 'IPowerConnectable1710', connection_ids: List[int]):
        super().__init__(parent, connection_ids)
        self.charge: int = 0  # 0-1000
        self.flow: int = 0  # Bitfield for flow history

    @property
    def capacitance(self) -> float:
        return 0.25

    def get_charge_scaled(self, scale: int) -> int:
        """Zwraca charge w skali 0-scale"""
        return min(scale, scale * self.charge // 1000)

    def get_flow_scaled(self, scale: int) -> int:
        """Zwraca flow w skali 0-scale"""
        return bin(self.flow).count('1') * scale // 32

    @property
    def can_work(self) -> bool:
        """Czy conductor moze pracowac (dosc energii)"""
        return self.charge > 600

    def update(self, world_time: int):
        """Aktualizacja z tracking charge i flow"""
        super().update(world_time)
        self.charge = int(self.voltage(world_time) * 10.0)
        self.flow <<= 1
        if self.can_work:
            self.flow |= 1
        self.flow &= 0xFFFFFFFF  # Limit to 32 bits

    def save_nbt(self) -> Dict:
        nbt = super().save_nbt()
        nbt["chg"] = self.charge
        nbt["flow"] = self.flow
        return nbt

    def load_nbt(self, nbt: Dict):
        super().load_nbt(nbt)
        self.charge = nbt.get("chg", 0)
        self.flow = nbt.get("flow", 0)


class IPowerConnectable1710(ABC):
    """Interface dla obiektow ktore moga przewodzic energie"""

    @abstractmethod
    def conductor(self, direction: int) -> PowerConductor1710:
        """Getter dla lokalnego conductora"""
        pass

    @abstractmethod
    def conductor_out(self, conn_id: int) -> Optional[PowerConductor1710]:
        """Pobiera conductor od sasiada przez ID polaczenia"""
        pass

    @abstractmethod
    def get_world_time(self) -> int:
        """Czas swiata"""
        pass


@dataclass
class BatteryBox1710(IPowerConnectable1710):
    """
    Symulacja TileBatteryBox z ProjectRed 1.7.10.

    Przechowuje energie Electrotine i moze ladowac/rozladowywac baterie.

    NBT Tags:
    - storage (Integer): Przechowywana energia (0-8000)
    - rot (Byte): Orientacja
    - Inventory tags
    """

    # Stan
    storage: int = 0
    orientation: int = 0

    # Inventory (2 slots: 0=input/charge, 1=output/discharge)
    inventory: List[Optional[Dict]] = field(default_factory=lambda: [None, None])

    # Internal
    _world_time: int = 0
    _cond: Optional[PowerDrawPoint1710] = None
    _prev_storage_scaled: int = 0

    # Constants
    MAX_STORAGE: int = 8000
    DRAW_SPEED: int = 100
    DRAW_CEIL: int = 900
    DRAW_FLOOR: int = 800
    CHARGE_SPEED: int = 25

    def __post_init__(self):
        self._cond = PowerDrawPoint1710(self, list(range(6)))

    @property
    def cond(self) -> PowerDrawPoint1710:
        return self._cond

    def conductor(self, direction: int) -> PowerConductor1710:
        return self._cond

    def conductor_out(self, conn_id: int) -> Optional[PowerConductor1710]:
        # W symulacji zwracamy None - brak polaczonych sasiadow
        return None

    def get_world_time(self) -> int:
        return self._world_time

    def get_storage_scaled(self, scale: int) -> int:
        """Zwraca storage w skali 0-scale"""
        if self.MAX_STORAGE == 0:
            return 0
        return min(scale, scale * self.storage // self.MAX_STORAGE)

    def update(self, world_time: int):
        """
        Glowna petla update BatteryBox.
        Wykonywana co tick.
        """
        self._world_time = world_time

        # Update conductor
        self._cond.update(world_time)

        # Power storage logic - ladowanie/rozladowywanie wewnetrznego storage
        if self._cond.charge > self.DRAW_CEIL and self.storage < self.MAX_STORAGE:
            # Ladowanie storage z conductora
            n = min(self._cond.charge - self.DRAW_CEIL, self.DRAW_SPEED) // 10
            n = min(n, self.MAX_STORAGE - self.storage)
            self._cond.draw_power(n * 1000, world_time)
            self.storage += n
        elif self._cond.charge < self.DRAW_FLOOR and self.storage > 0:
            # Rozladowywanie storage do conductora
            n = min(self.DRAW_FLOOR - self._cond.charge, self.DRAW_SPEED) // 10
            n = min(n, self.storage)
            self._cond.apply_power(n * 1000, world_time)
            self.storage -= n

        # Update render if storage changed
        new_scaled = self.get_storage_scaled(8)
        if new_scaled != self._prev_storage_scaled:
            self._prev_storage_scaled = new_scaled

    def save_nbt(self) -> Dict:
        """
        Zapisuje stan do NBT.

        NBT structure for 1.7.10 BatteryBox:
        - storage (Integer): Przechowywana energia
        - rot (Byte): Orientacja
        - Conductor NBT (zagniezdzone)
        """
        nbt = {
            "storage": self.storage,
            "rot": self.orientation,
        }
        # Merge conductor NBT
        nbt.update(self._cond.save_nbt())
        return nbt

    def load_nbt(self, nbt: Dict):
        """Wczytuje stan z NBT"""
        self.storage = nbt.get("storage", 0)
        self.orientation = nbt.get("rot", 0)
        self._cond.load_nbt(nbt)
        self._prev_storage_scaled = self.get_storage_scaled(8)


# =============================================================================
# 1.18.2+ - Power System Implementation
# =============================================================================

class PowerConductor1182:
    """
    Symulacja PowerConductor z ProjectRed 1.18.2+.

    Uproszczona wersja w porownaniu do 1.7.10.
    Bazowane na kodzie Java z PowerConductor.java.
    """

    def __init__(self, parent: 'IPowerConductorSource1182', resistance: float = 0.01, capacitance: float = 0.25):
        """
        Args:
            parent: Obiekt hostujacy conductor
            resistance: Opor elektryczny
            capacitance: Pojemnosc elektryczna
        """
        self.parent = parent
        self.resistance = resistance
        self.capacitance = capacitance
        self.inverse_capacitance = 1.0 / capacitance

        # Stan elektryczny
        self.v_cap: float = 0.0  # Voltage (napiecie)
        self.i_cap: float = 0.0  # Current accumulator (prad)

        self.time: int = -1  # Ostatni tick

    def get_voltage(self) -> float:
        """
        Pobiera napiecie, przeliczajac jesli potrzeba.

        I = C * dV/dT
        dV = dT * I / C
        """
        t = self.parent.get_time()
        if self.time != t:
            self.time = t
            # dV = dT * I / C, where dT = 0.05 (1/20 tick)
            self.v_cap += 0.05 * self.i_cap * self.inverse_capacitance
            self.i_cap = 0  # Reset - bedzie akumulowany podczas tick
        return self.v_cap

    def get_current(self) -> float:
        """Pobiera prad"""
        return self.i_cap * 0.05

    def get_energy(self) -> float:
        """
        Pobiera energie.
        E = 0.5 * C * V^2
        """
        return 0.5 * self.capacitance * self.v_cap * self.v_cap

    def apply_current(self, i: float):
        """Aplikuje prad"""
        self.get_voltage()
        self.i_cap += i

    def apply_power(self, p: float):
        """
        Aplikuje ciagla moc na 1 tick.
        Ujemne wartosci pobieraja moc.

        Based on:
        P = dE(t) / dt
        P = d(1/2 * C * V(t)^2) / dt

        Args:
            p: Moc (W)
        """
        dv_squared = abs(p) * 0.1 * self.inverse_capacitance

        if p < 0 and dv_squared >= self.v_cap * self.v_cap:
            # Brak wystarczajacej energii
            return

        di = 20 * math.sqrt(dv_squared) * self.capacitance
        self.apply_current(-di if p < 0 else di)

    def tick(self):
        """
        Tick update - wymiana pradu z polaczonymi conductorami.
        """
        # Force voltage recalculation
        self.get_voltage()

        # Exchange current with all connected conductors
        conductors = self.parent.get_connected_conductors()
        for cond in conductors:
            # Only allow higher voltage to do exchange (unika podwojnej wymiany)
            if cond.get_voltage() > self.get_voltage():
                continue

            v = self.get_voltage() - cond.get_voltage()
            r = self.resistance + cond.resistance
            i = v / r

            self.apply_current(-i)
            cond.apply_current(i)

    def save_nbt(self) -> Dict:
        """
        Zapisuje stan do NBT.

        NBT Tags (1.18.2):
        - vCap (Double): Napiecie
        - iCap (Double): Prad
        """
        return {
            "vCap": self.v_cap,
            "iCap": self.i_cap,
        }

    def load_nbt(self, nbt: Dict):
        """Wczytuje stan z NBT"""
        self.v_cap = nbt.get("vCap", 0.0)
        self.i_cap = nbt.get("iCap", 0.0)


class IPowerConductorSource1182(ABC):
    """Interface dla obiektow dostarczajacych conductor w 1.18.2+"""

    @abstractmethod
    def get_time(self) -> int:
        """Zwraca czas swiata"""
        pass

    @abstractmethod
    def get_connected_conductors(self) -> List[PowerConductor1182]:
        """Zwraca liste polaczonych conductors"""
        pass


@dataclass
class BatteryBox1182(IPowerConductorSource1182):
    """
    Symulacja BatteryBox dla ProjectRed 1.18.2+.

    Struktura podobna do 1.7.10, ale uzywa uproszczonego PowerConductor.
    """

    # Stan
    storage: int = 0

    # Internal
    _world_time: int = 0
    _cond: Optional[PowerConductor1182] = None
    _charge: int = 0
    _flow: int = 0

    # Constants (takie same jak 1.7.10)
    MAX_STORAGE: int = 8000
    DRAW_SPEED: int = 100
    DRAW_CEIL: int = 900
    DRAW_FLOOR: int = 800
    CHARGE_SPEED: int = 25

    def __post_init__(self):
        self._cond = PowerConductor1182(self, resistance=0.01, capacitance=0.25)

    @property
    def cond(self) -> PowerConductor1182:
        return self._cond

    @property
    def charge(self) -> int:
        return self._charge

    @property
    def can_work(self) -> bool:
        return self._charge > 600

    def get_time(self) -> int:
        return self._world_time

    def get_connected_conductors(self) -> List[PowerConductor1182]:
        # W symulacji - brak polaczonych
        return []

    def get_storage_scaled(self, scale: int) -> int:
        if self.MAX_STORAGE == 0:
            return 0
        return min(scale, scale * self.storage // self.MAX_STORAGE)

    def update(self, world_time: int):
        """Glowna petla update"""
        self._world_time = world_time

        # Update conductor
        self._cond.tick()

        # Update charge/flow tracking (podobnie do TPowerDrawPoint)
        self._charge = int(self._cond.get_voltage() * 10.0)
        self._flow = (self._flow << 1) & 0xFFFFFFFF
        if self.can_work:
            self._flow |= 1

        # Power storage logic
        if self._charge > self.DRAW_CEIL and self.storage < self.MAX_STORAGE:
            n = min(self._charge - self.DRAW_CEIL, self.DRAW_SPEED) // 10
            n = min(n, self.MAX_STORAGE - self.storage)
            self._cond.apply_power(-n * 1000)  # Negative = draw
            self.storage += n
        elif self._charge < self.DRAW_FLOOR and self.storage > 0:
            n = min(self.DRAW_FLOOR - self._charge, self.DRAW_SPEED) // 10
            n = min(n, self.storage)
            self._cond.apply_power(n * 1000)  # Positive = apply
            self.storage -= n

    def save_nbt(self) -> Dict:
        """Zapisuje stan do NBT"""
        nbt = {
            "storage": self.storage,
            "charge": self._charge,
            "flow": self._flow,
        }
        nbt.update(self._cond.save_nbt())
        return nbt

    def load_nbt(self, nbt: Dict):
        """Wczytuje stan z NBT"""
        self.storage = nbt.get("storage", 0)
        self._charge = nbt.get("charge", 0)
        self._flow = nbt.get("flow", 0)
        self._cond.load_nbt(nbt)


# =============================================================================
# Conversion Utilities
# =============================================================================

def convert_power_conductor_nbt(nbt_1710: Dict) -> Dict:
    """
    Konwertuje NBT PowerConductor z 1.7.10 do 1.18.2+.

    Roznice:
    - 1.7.10 uzywa flow0, flow1, ... plus vl, il, vf, if, tm
    - 1.18.2 uzywa tylko vCap, iCap

    Returns:
        NBT w formacie 1.18.2+
    """
    return {
        "vCap": nbt_1710.get("vl", 0.0),
        "iCap": nbt_1710.get("il", 0.0) * 20,  # Skalowanie
    }


def convert_battery_box_nbt(nbt_1710: Dict) -> Dict:
    """
    Konwertuje NBT BatteryBox z 1.7.10 do 1.18.2+.

    Glowne zmiany:
    - storage pozostaje bez zmian
    - Conductor NBT wymaga konwersji
    """
    nbt_1182 = {
        "storage": nbt_1710.get("storage", 0),
        "charge": nbt_1710.get("chg", 0),
        "flow": nbt_1710.get("flow", 0),
    }

    # Convert conductor part
    conductor_nbt = convert_power_conductor_nbt(nbt_1710)
    nbt_1182.update(conductor_nbt)

    return nbt_1182


# =============================================================================
# Tests and Demonstrations
# =============================================================================

def test_power_conductor_1710():
    """Test PowerConductor dla 1.7.10"""
    print("=== Test PowerConductor 1.7.10 ===")

    class TestParent(IPowerConnectable1710):
        def __init__(self):
            self.cond = None
            self.time = 0

        def conductor(self, direction: int):
            return self.cond

        def conductor_out(self, conn_id: int):
            return None

        def get_world_time(self) -> int:
            return self.time

    parent = TestParent()
    cond = PowerDrawPoint1710(parent, [0, 1, 2, 3, 4, 5])
    parent.cond = cond

    # Simulate adding power
    print(f"Initial voltage: {cond.voltage(0):.4f}")
    print(f"Initial charge: {cond.charge}")
    print(f"Can work: {cond.can_work}")

    # Apply power
    for tick in range(100):
        parent.time = tick
        cond.apply_power(5000, tick)  # 5kW
        cond.update(tick)

    print(f"After 100 ticks with 5kW power:")
    print(f"  Voltage: {cond.voltage(100):.4f}")
    print(f"  Charge: {cond.charge}")
    print(f"  Can work: {cond.can_work}")

    # Save NBT
    nbt = cond.save_nbt()
    print(f"  NBT keys: {list(nbt.keys())}")

    # Test load
    cond2 = PowerDrawPoint1710(parent, [0, 1, 2, 3, 4, 5])
    cond2.load_nbt(nbt)
    print(f"  After load - Charge: {cond2.charge}, vl: {cond2.v_loc:.4f}")

    print()


def test_battery_box_1710():
    """Test BatteryBox dla 1.7.10"""
    print("=== Test BatteryBox 1.7.10 ===")

    bb = BatteryBox1710()
    print(f"Initial storage: {bb.storage}")
    print(f"Max storage: {bb.MAX_STORAGE}")

    # Symuluj ladowanie przez dodanie energii do conductora
    for tick in range(200):
        bb.cond.apply_power(10000, tick)  # 10kW input
        bb.update(tick)

    print(f"After 200 ticks with 10kW input:")
    print(f"  Storage: {bb.storage} / {bb.MAX_STORAGE}")
    print(f"  Storage scaled(8): {bb.get_storage_scaled(8)}")
    print(f"  Conductor charge: {bb.cond.charge}")

    # Save NBT
    nbt = bb.save_nbt()
    print(f"  NBT: storage={nbt.get('storage')}, chg={nbt.get('chg')}")

    # Test load
    bb2 = BatteryBox1710()
    bb2.load_nbt(nbt)
    print(f"  After load - Storage: {bb2.storage}")

    print()


def test_power_conductor_1182():
    """Test PowerConductor dla 1.18.2+"""
    print("=== Test PowerConductor 1.18.2+ ===")

    class TestParent(IPowerConductorSource1182):
        def __init__(self):
            self.time = 0

        def get_time(self) -> int:
            return self.time

        def get_connected_conductors(self):
            return []

    parent = TestParent()
    cond = PowerConductor1182(parent)

    print(f"Initial voltage: {cond.get_voltage():.4f}")
    print(f"Initial energy: {cond.get_energy():.4f}")

    # Apply power
    for tick in range(100):
        parent.time = tick
        cond.apply_power(5000)  # 5kW
        cond.tick()

    print(f"After 100 ticks with 5kW power:")
    print(f"  Voltage: {cond.get_voltage():.4f}")
    print(f"  Energy: {cond.get_energy():.4f}")

    # Save NBT
    nbt = cond.save_nbt()
    print(f"  NBT: {nbt}")

    print()


def test_battery_box_1182():
    """Test BatteryBox dla 1.18.2+"""
    print("=== Test BatteryBox 1.18.2+ ===")

    bb = BatteryBox1182()
    print(f"Initial storage: {bb.storage}")

    # Symuluj ladowanie
    for tick in range(200):
        bb.cond.apply_power(10000)  # 10kW input
        bb.update(tick)

    print(f"After 200 ticks with 10kW input:")
    print(f"  Storage: {bb.storage} / {bb.MAX_STORAGE}")
    print(f"  Charge: {bb.charge}")
    print(f"  Can work: {bb.can_work}")

    # Save NBT
    nbt = bb.save_nbt()
    print(f"  NBT keys: {list(nbt.keys())}")

    print()


def test_nbt_conversion():
    """Test konwersji NBT miedzy wersjami"""
    print("=== Test NBT Conversion ===")

    # Create 1.7.10 BatteryBox with some state
    bb_1710 = BatteryBox1710()
    for tick in range(100):
        bb_1710.cond.apply_power(10000, tick)
        bb_1710.update(tick)

    nbt_1710 = bb_1710.save_nbt()
    print(f"1.7.10 NBT:")
    print(f"  storage: {nbt_1710.get('storage')}")
    print(f"  vl: {nbt_1710.get('vl', 0):.4f}")
    print(f"  chg: {nbt_1710.get('chg')}")

    # Convert to 1.18.2
    nbt_1182 = convert_battery_box_nbt(nbt_1710)
    print(f"Converted to 1.18.2 NBT:")
    print(f"  storage: {nbt_1182.get('storage')}")
    print(f"  vCap: {nbt_1182.get('vCap', 0):.4f}")
    print(f"  charge: {nbt_1182.get('charge')}")

    # Load into 1.18.2 BatteryBox
    bb_1182 = BatteryBox1182()
    bb_1182.load_nbt(nbt_1182)
    print(f"Loaded into 1.18.2 BatteryBox:")
    print(f"  Storage: {bb_1182.storage}")
    print(f"  Charge: {bb_1182.charge}")

    print()


def demo_power_network():
    """Demonstracja sieci energetycznej"""
    print("=== Demo: Power Network ===")
    print("Symulacja prostej sieci energetycznej z generatorem i BatteryBox")
    print()

    # W pelnej symulacji mielibysmy generator i polaczenia
    # Tu symulujemy przez bezposrednie aplikowanie mocy

    bb = BatteryBox1710()

    # Symuluj generator dostarczajacy energie
    print("Generator dostarcza 10kW przez 500 tickow...")
    for tick in range(500):
        bb.cond.apply_power(10000, tick)
        bb.update(tick)

        if tick % 100 == 99:
            print(f"  Tick {tick+1}: Storage={bb.storage}, Charge={bb.cond.charge}, CanWork={bb.cond.can_work}")

    print()
    print(f"Stan koncowy:")
    print(f"  Storage: {bb.storage} / {bb.MAX_STORAGE}")
    print(f"  Storage %: {100 * bb.storage / bb.MAX_STORAGE:.1f}%")
    print()


if __name__ == "__main__":
    test_power_conductor_1710()
    test_battery_box_1710()
    test_power_conductor_1182()
    test_battery_box_1182()
    test_nbt_conversion()
    demo_power_network()
