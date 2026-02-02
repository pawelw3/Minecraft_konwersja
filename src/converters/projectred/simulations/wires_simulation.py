"""
ProjectRed Transmission Wires Simulation
=========================================

Symulacja przewodow Transmission dla ProjectRed.
Obejmuje RedWire, InsulatedWire i BundledCable.

Przewody sa multipart - nie standardowymi blokami.
Uzywaja ForgeMultipart/CBMultipart.

Typy przewodow:
- pr_redwire: Podstawowy przewod redstone
- pr_insulated: Izolowany przewod (16 kolorow)
- pr_bundled: Przewod bundled (16 kanalow)
- pr_framed_*: Wersje ramkowane (center parts)

Bazowane na kodzie zrodlowym:
- 1.7.10: mod_src/1710/actual_src/1.7.10/ProjectRed_GTNH/src/main/scala/mrtjp/projectred/transmission/
- 1.18.2: mod_src/118/actual_src/1.18.2/ProjectRed/repo/transmission/
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
from abc import ABC, abstractmethod
from enum import Enum


# =============================================================================
# Enums and Constants
# =============================================================================

class WireType(Enum):
    """Typy przewodow"""
    RED_ALLOY = 0      # Podstawowy przewod redstone
    INSULATED = 1      # Izolowany przewod (kolorowy)
    BUNDLED = 2        # Przewod bundled (16 kanalow)
    FRAMED_RED_ALLOY = 3
    FRAMED_INSULATED = 4
    FRAMED_BUNDLED = 5


class WirePartType(Enum):
    """Typy multipart dla przewodow"""
    PR_REDWIRE = "pr_redwire"
    PR_INSULATED = "pr_insulated"
    PR_BUNDLED = "pr_bundled"
    PR_FRAMED_REDWIRE = "pr_framed_redwire"
    PR_FRAMED_INSULATED = "pr_framed_insulated"
    PR_FRAMED_BUNDLED = "pr_framed_bundled"


class WireColor(Enum):
    """Kolory dla izolowanych przewodow (Minecraft dye colors)"""
    WHITE = 0
    ORANGE = 1
    MAGENTA = 2
    LIGHT_BLUE = 3
    YELLOW = 4
    LIME = 5
    PINK = 6
    GRAY = 7
    LIGHT_GRAY = 8
    CYAN = 9
    PURPLE = 10
    BLUE = 11
    BROWN = 12
    GREEN = 13
    RED = 14
    BLACK = 15


# Connection mask bits
# Face wires use 4 bits per side (0-3 for edge connections on that face)
# Framed wires use 6 bits (one per direction)


# =============================================================================
# Base Wire Classes
# =============================================================================

@dataclass
class WirePart(ABC):
    """
    Bazowa klasa dla wszystkich przewodow.

    NBT Tags (wspolne):
    - orient (Byte): Orientacja (side dla face wires)
    - connMap (Integer): Mapa polaczen
    - signal (Byte/Array): Sila sygnalu

    Dla Face Wires:
    - orientation = side (0-5)
    - connMap: 4 bits per edge, total 16 bits for connections

    Dla Framed Wires:
    - orientation = 0 (center)
    - connMap: 6 bits for 6 directions
    """

    wire_type: WireType
    orientation: int = 0  # Side for face wires, 0 for center
    conn_map: int = 0     # Connection bitmap
    signal: int = 0       # Redstone signal strength (0-255)

    @property
    def side(self) -> int:
        """Strona bloku dla face wires"""
        return self.orientation & 7

    @side.setter
    def side(self, value: int):
        self.orientation = value & 7

    @property
    def is_framed(self) -> bool:
        """Czy to framed (center) wire"""
        return self.wire_type.value >= 3

    def is_connected(self, direction: int) -> bool:
        """Sprawdza czy jest polaczenie w danym kierunku"""
        if self.is_framed:
            return bool(self.conn_map & (1 << direction))
        else:
            # For face wires, direction is edge index (0-3)
            return bool(self.conn_map & (1 << direction))

    def set_connected(self, direction: int, connected: bool):
        """Ustawia polaczenie w danym kierunku"""
        if connected:
            self.conn_map |= (1 << direction)
        else:
            self.conn_map &= ~(1 << direction)

    def get_connection_count(self) -> int:
        """Zwraca liczbe polaczen"""
        return bin(self.conn_map).count('1')

    @abstractmethod
    def propagate_signal(self, input_signals: Dict[int, int]) -> Dict[int, int]:
        """
        Propaguje sygnal przez przewod.

        Args:
            input_signals: Mapa kierunek -> sila sygnalu wejsciowego

        Returns:
            Mapa kierunek -> sila sygnalu wyjsciowego
        """
        pass

    def save_nbt(self) -> Dict:
        """Zapisuje stan do NBT"""
        return {
            "orient": self.orientation,
            "connMap": self.conn_map,
            "signal": self.signal,
        }

    def load_nbt(self, nbt: Dict):
        """Wczytuje stan z NBT"""
        self.orientation = nbt.get("orient", 0)
        self.conn_map = nbt.get("connMap", 0)
        self.signal = nbt.get("signal", 0)


# =============================================================================
# Red Alloy Wire
# =============================================================================

@dataclass
class RedAlloyWire(WirePart):
    """
    Red Alloy Wire - podstawowy przewod redstone.

    Propaguje sygnal redstone z atenuacja 1 na blok.
    Maksymalna sila sygnalu: 255 (wewnetrznie), 15 (do vanilla)
    """

    def __init__(self):
        super().__init__(wire_type=WireType.RED_ALLOY)

    def propagate_signal(self, input_signals: Dict[int, int]) -> Dict[int, int]:
        """
        Propaguje sygnal przez red alloy wire.
        Wyjscie = max(wejscia) - 1 (atenuacja)
        """
        if not input_signals:
            self.signal = 0
            return {}

        max_signal = max(input_signals.values())
        self.signal = max(0, max_signal - 1)  # Atenuacja

        # Output to all connected directions except input
        output = {}
        for direction in range(6 if self.is_framed else 4):
            if self.is_connected(direction) and direction not in input_signals:
                output[direction] = self.signal

        return output

    def get_vanilla_signal(self) -> int:
        """Konwertuje wewnetrzny sygnal na vanilla (0-15)"""
        return min(15, (self.signal + 16) // 17)


# =============================================================================
# Insulated Wire
# =============================================================================

@dataclass
class InsulatedWire(WirePart):
    """
    Insulated Wire - izolowany przewod kolorowy.

    Laczy sie tylko z przewodami tego samego koloru lub bundled.
    16 kolorow.
    """

    color: WireColor = WireColor.WHITE

    def __init__(self, color: WireColor = WireColor.WHITE):
        super().__init__(wire_type=WireType.INSULATED)
        self.color = color

    def can_connect_to(self, other: 'WirePart') -> bool:
        """Sprawdza czy moze polaczyc sie z innym przewodem"""
        if isinstance(other, InsulatedWire):
            return self.color == other.color
        elif isinstance(other, BundledCable):
            return True  # Bundled laczy sie z kazdym kolorem
        elif isinstance(other, RedAlloyWire):
            return True  # Moze polaczyc sie z red alloy
        return False

    def propagate_signal(self, input_signals: Dict[int, int]) -> Dict[int, int]:
        """Propaguje sygnal (z atenuacja)"""
        if not input_signals:
            self.signal = 0
            return {}

        max_signal = max(input_signals.values())
        self.signal = max(0, max_signal - 1)

        output = {}
        for direction in range(6 if self.is_framed else 4):
            if self.is_connected(direction) and direction not in input_signals:
                output[direction] = self.signal

        return output

    def save_nbt(self) -> Dict:
        nbt = super().save_nbt()
        nbt["color"] = self.color.value
        return nbt

    def load_nbt(self, nbt: Dict):
        super().load_nbt(nbt)
        color_value = nbt.get("color", 0)
        self.color = WireColor(color_value)


# =============================================================================
# Bundled Cable
# =============================================================================

@dataclass
class BundledCable(WirePart):
    """
    Bundled Cable - przewod z 16 kanalami.

    Kazdy kanal odpowiada jednemu kolorowi.
    Przekazuje sygnaly dla wszystkich 16 kolorow jednoczesnie.

    NBT:
    - signals (ByteArray/IntArray): 16 sygnalow (jeden na kolor)
    """

    signals: List[int] = field(default_factory=lambda: [0] * 16)
    color: Optional[WireColor] = None  # None = neutral, kolor = colored bundled

    def __init__(self, color: Optional[WireColor] = None):
        super().__init__(wire_type=WireType.BUNDLED)
        self.signals = [0] * 16
        self.color = color

    def get_channel_signal(self, channel: WireColor) -> int:
        """Pobiera sygnal dla danego kanalu"""
        return self.signals[channel.value]

    def set_channel_signal(self, channel: WireColor, signal: int):
        """Ustawia sygnal dla danego kanalu"""
        self.signals[channel.value] = max(0, min(255, signal))

    def can_connect_to(self, other: 'WirePart') -> bool:
        """Sprawdza czy moze polaczyc sie z innym przewodem"""
        if isinstance(other, BundledCable):
            # Neutral laczy sie z wszystkim
            # Colored laczy sie tylko z tym samym kolorem lub neutral
            if self.color is None or other.color is None:
                return True
            return self.color == other.color
        elif isinstance(other, InsulatedWire):
            return True  # Laczy sie z insulated (jeden kanal)
        return False

    def propagate_signal(self, input_signals: Dict[int, int]) -> Dict[int, int]:
        """
        Propaguje sygnaly dla wszystkich 16 kanalow.
        input_signals tutaj to uproszczenie - w rzeczywistosci
        kazdy kierunek ma 16 sygnalow.
        """
        # Simplified - just pass through
        return input_signals

    def propagate_bundled(self, input_bundled: Dict[int, List[int]]) -> Dict[int, List[int]]:
        """
        Propaguje sygnaly bundled (pelna wersja).

        Args:
            input_bundled: Mapa kierunek -> lista 16 sygnalow

        Returns:
            Mapa kierunek -> lista 16 sygnalow wyjsciowych
        """
        if not input_bundled:
            self.signals = [0] * 16
            return {}

        # Merge all inputs - max for each channel
        for channel in range(16):
            max_signal = 0
            for signals in input_bundled.values():
                if signals[channel] > max_signal:
                    max_signal = signals[channel]
            self.signals[channel] = max(0, max_signal - 1)

        # Output to all connected directions except inputs
        output = {}
        for direction in range(6 if self.is_framed else 4):
            if self.is_connected(direction) and direction not in input_bundled:
                output[direction] = self.signals.copy()

        return output

    def save_nbt(self) -> Dict:
        nbt = super().save_nbt()
        nbt["bundledSignals"] = self.signals.copy()
        if self.color is not None:
            nbt["bundledColor"] = self.color.value
        return nbt

    def load_nbt(self, nbt: Dict):
        super().load_nbt(nbt)
        signals = nbt.get("bundledSignals", None)
        if signals:
            self.signals = signals[:16] if len(signals) >= 16 else signals + [0] * (16 - len(signals))
        else:
            self.signals = [0] * 16

        color_value = nbt.get("bundledColor", None)
        if color_value is not None:
            self.color = WireColor(color_value)
        else:
            self.color = None


# =============================================================================
# Wire Network Simulation
# =============================================================================

@dataclass
class WireNetwork:
    """
    Symulacja sieci przewodow.

    Zarzadza propagacja sygnalow przez polaczona siec przewodow.
    """

    wires: Dict[Tuple[int, int, int], WirePart] = field(default_factory=dict)

    def add_wire(self, pos: Tuple[int, int, int], wire: WirePart):
        """Dodaje przewod do sieci"""
        self.wires[pos] = wire

    def remove_wire(self, pos: Tuple[int, int, int]):
        """Usuwa przewod z sieci"""
        if pos in self.wires:
            del self.wires[pos]

    def get_neighbors(self, pos: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        """Zwraca pozycje sasiadujacych przewodow"""
        x, y, z = pos
        potential = [
            (x+1, y, z), (x-1, y, z),
            (x, y+1, z), (x, y-1, z),
            (x, y, z+1), (x, y, z-1),
        ]
        return [p for p in potential if p in self.wires]

    def propagate_from_source(self, source_pos: Tuple[int, int, int], signal: int):
        """
        Propaguje sygnal od zrodla przez siec.

        Uzywamy BFS z atenuacja sygnalu.
        """
        if source_pos not in self.wires:
            return

        # BFS propagation
        visited: Set[Tuple[int, int, int]] = set()
        queue: List[Tuple[Tuple[int, int, int], int]] = [(source_pos, signal)]

        while queue:
            pos, current_signal = queue.pop(0)
            if pos in visited or current_signal <= 0:
                continue

            visited.add(pos)
            wire = self.wires[pos]
            wire.signal = current_signal

            # Propagate to neighbors
            for neighbor_pos in self.get_neighbors(pos):
                if neighbor_pos not in visited:
                    queue.append((neighbor_pos, current_signal - 1))

    def calculate_all_signals(self, sources: Dict[Tuple[int, int, int], int]):
        """
        Oblicza sygnaly dla calej sieci na podstawie zrodel.

        Args:
            sources: Mapa pozycja -> sila sygnalu zrodla
        """
        # Reset all signals
        for wire in self.wires.values():
            wire.signal = 0

        # Propagate from each source
        for source_pos, signal in sources.items():
            self.propagate_from_source(source_pos, signal)


# =============================================================================
# Conversion Utilities
# =============================================================================

def convert_wire_nbt_1710_to_1182(nbt_1710: Dict, wire_type: WireType) -> Dict:
    """
    Konwertuje NBT przewodu z 1.7.10 do 1.18.2+.

    Glowne roznice:
    - Struktura NBT jest bardzo podobna
    - 1.18.2 moze uzywac innych nazw pol
    """
    nbt_1182 = {
        "orient": nbt_1710.get("orient", 0),
        "connMap": nbt_1710.get("connMap", 0),
        "signal": nbt_1710.get("signal", 0),
    }

    # Insulated wire color
    if "color" in nbt_1710:
        nbt_1182["color"] = nbt_1710["color"]

    # Bundled signals
    if "bundledSignals" in nbt_1710:
        nbt_1182["bundledSignals"] = nbt_1710["bundledSignals"]
    if "bundledColor" in nbt_1710:
        nbt_1182["bundledColor"] = nbt_1710["bundledColor"]

    return nbt_1182


def get_wire_type_name(wire_type: WireType, color: Optional[WireColor] = None) -> str:
    """Zwraca nazwe przewodu dla danego typu i koloru"""
    base_names = {
        WireType.RED_ALLOY: "red_alloy_wire",
        WireType.INSULATED: "insulated_wire",
        WireType.BUNDLED: "bundled_cable",
        WireType.FRAMED_RED_ALLOY: "framed_red_alloy_wire",
        WireType.FRAMED_INSULATED: "framed_insulated_wire",
        WireType.FRAMED_BUNDLED: "framed_bundled_cable",
    }

    name = base_names.get(wire_type, "unknown_wire")

    if color is not None and wire_type in [WireType.INSULATED, WireType.FRAMED_INSULATED]:
        name = f"{color.name.lower()}_{name}"

    return name


# =============================================================================
# Tests and Demonstrations
# =============================================================================

def test_red_alloy_wire():
    """Test Red Alloy Wire"""
    print("=== Test Red Alloy Wire ===")

    wire = RedAlloyWire()
    wire.side = 0  # Bottom face

    # Set connections
    wire.set_connected(0, True)  # South
    wire.set_connected(2, True)  # North

    print(f"Connections: {wire.get_connection_count()}")
    assert wire.get_connection_count() == 2

    # Propagate signal
    input_signals = {2: 100}  # Signal from North
    output = wire.propagate_signal(input_signals)

    print(f"Input: {input_signals}")
    print(f"Wire signal: {wire.signal}")
    print(f"Output: {output}")
    print(f"Vanilla signal: {wire.get_vanilla_signal()}")

    assert wire.signal == 99  # Attenuation
    assert 0 in output  # Output to South

    print("Red Alloy Wire: OK")
    print()


def test_insulated_wire():
    """Test Insulated Wire"""
    print("=== Test Insulated Wire ===")

    # Create two wires
    red_wire = InsulatedWire(WireColor.RED)
    blue_wire = InsulatedWire(WireColor.BLUE)
    red_wire2 = InsulatedWire(WireColor.RED)

    # Test connections
    assert red_wire.can_connect_to(red_wire2) == True
    assert red_wire.can_connect_to(blue_wire) == False

    print(f"Red can connect to Red: {red_wire.can_connect_to(red_wire2)}")
    print(f"Red can connect to Blue: {red_wire.can_connect_to(blue_wire)}")

    # Test NBT
    nbt = red_wire.save_nbt()
    print(f"NBT: {nbt}")

    loaded_wire = InsulatedWire()
    loaded_wire.load_nbt(nbt)
    assert loaded_wire.color == WireColor.RED

    print("Insulated Wire: OK")
    print()


def test_bundled_cable():
    """Test Bundled Cable"""
    print("=== Test Bundled Cable ===")

    cable = BundledCable()

    # Set signals for different channels
    cable.set_channel_signal(WireColor.RED, 200)
    cable.set_channel_signal(WireColor.BLUE, 150)
    cable.set_channel_signal(WireColor.GREEN, 100)

    print(f"Red channel: {cable.get_channel_signal(WireColor.RED)}")
    print(f"Blue channel: {cable.get_channel_signal(WireColor.BLUE)}")
    print(f"Green channel: {cable.get_channel_signal(WireColor.GREEN)}")

    # Test bundled propagation
    input_bundled = {
        2: [0] * 16  # North input
    }
    input_bundled[2][WireColor.RED.value] = 200

    cable.set_connected(0, True)  # South
    cable.set_connected(2, True)  # North

    output = cable.propagate_bundled(input_bundled)
    print(f"Bundled output: {output}")

    # Test NBT
    nbt = cable.save_nbt()
    print(f"NBT keys: {list(nbt.keys())}")

    print("Bundled Cable: OK")
    print()


def test_wire_network():
    """Test Wire Network"""
    print("=== Test Wire Network ===")

    network = WireNetwork()

    # Create a simple line of wires
    for i in range(5):
        wire = RedAlloyWire()
        if i > 0:
            wire.set_connected(2, True)  # Connect to previous (North)
        if i < 4:
            wire.set_connected(0, True)  # Connect to next (South)
        network.add_wire((0, 0, i), wire)

    print(f"Network has {len(network.wires)} wires")

    # Propagate from source at start
    network.propagate_from_source((0, 0, 0), 255)

    print("Signal levels after propagation:")
    for i in range(5):
        wire = network.wires[(0, 0, i)]
        print(f"  Position {i}: signal = {wire.signal}")

    # Verify attenuation
    assert network.wires[(0, 0, 0)].signal == 255
    assert network.wires[(0, 0, 1)].signal == 254
    assert network.wires[(0, 0, 4)].signal == 251

    print("Wire Network: OK")
    print()


def test_nbt_conversion():
    """Test konwersji NBT"""
    print("=== Test NBT Conversion ===")

    # Create 1.7.10 wire with state
    wire_1710 = InsulatedWire(WireColor.CYAN)
    wire_1710.signal = 150
    wire_1710.conn_map = 0b1010

    nbt_1710 = wire_1710.save_nbt()
    print(f"1.7.10 NBT: {nbt_1710}")

    nbt_1182 = convert_wire_nbt_1710_to_1182(nbt_1710, WireType.INSULATED)
    print(f"1.18.2 NBT: {nbt_1182}")

    # Load into new wire
    wire_1182 = InsulatedWire()
    wire_1182.load_nbt(nbt_1182)

    assert wire_1182.color == WireColor.CYAN
    assert wire_1182.signal == 150

    print("NBT Conversion: OK")
    print()


def demo_wire_types():
    """Demonstracja typow przewodow"""
    print("=== Wire Types ===")

    for wire_type in WireType:
        print(f"  {wire_type.name}: {get_wire_type_name(wire_type)}")

    print()
    print("Insulated wire colors:")
    for color in WireColor:
        name = get_wire_type_name(WireType.INSULATED, color)
        print(f"  {color.name}: {name}")

    print()


def demo_signal_propagation():
    """Demonstracja propagacji sygnalu"""
    print("=== Demo: Signal Propagation ===")
    print("Siec przewodow z jednym zrodlem sygnalu")
    print()

    # Create a T-shaped network
    #      [2]
    #       |
    # [0]-[1]-[3]-[4]

    network = WireNetwork()

    # Horizontal line
    for i in range(5):
        wire = RedAlloyWire()
        wire.set_connected(1, i > 0)  # West
        wire.set_connected(3, i < 4)  # East
        if i == 1:
            wire.set_connected(0, True)  # Connect to [2] (South)
        network.add_wire((i, 0, 0), wire)

    # Vertical part
    wire2 = RedAlloyWire()
    wire2.set_connected(2, True)  # North (to [1])
    network.add_wire((1, 0, 1), wire2)

    # Signal source at position [0]
    network.propagate_from_source((0, 0, 0), 200)

    print("Siec T-ksztaltna:")
    print("  [0]-[1]-[3]-[4]")
    print("       |")
    print("      [2]")
    print()
    print("Sygnaly po propagacji od [0] z silą 200:")

    positions = [(0,0,0), (1,0,0), (2,0,0), (3,0,0), (4,0,0), (1,0,1)]
    labels = ["[0]", "[1]", "[3]", "[4]", "[5]", "[2]"]

    for pos, label in zip(positions, labels):
        if pos in network.wires:
            print(f"  {label}: signal = {network.wires[pos].signal}")

    print()


if __name__ == "__main__":
    demo_wire_types()
    test_red_alloy_wire()
    test_insulated_wire()
    test_bundled_cable()
    test_wire_network()
    test_nbt_conversion()
    demo_signal_propagation()
