"""
ProjectRed Logic Gates Simulation
=================================

Symulacja bramek logicznych ProjectRed dla wersji 1.7.10 oraz 1.18.2+.

Bramki sa multipart - nie standardowymi blokami.
Uzywaja ForgeMultipart/CBMultipart.

Typy bramek:
- Simple Gates (pr_sgate): AND, OR, NOT, NOR, NAND, XOR, XNOR, Buffer, Multiplexer
- Sequential Gates (pr_igate): Timer, Counter, Sequencer, Pulse, StateCell
- Array Gates (pr_agate): NullCell, InvertCell, BufferCell, ANDCell
- Bundled Gates (pr_bgate): BusTransceiver, BusRandomizer, BusConverter, BusInputPanel

Bazowane na kodzie zrodlowym:
- 1.7.10: mod_src/1710/actual_src/1.7.10/ProjectRed_GTNH/src/main/scala/mrtjp/projectred/integration/
- 1.18.2: mod_src/118/actual_src/1.18.2/ProjectRed/repo/integration/src/main/java/mrtjp/projectred/integration/
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Callable
from abc import ABC, abstractmethod
from enum import Enum, auto
import random


# =============================================================================
# Enums and Constants
# =============================================================================

class GateType(Enum):
    """Typy bramek - wspólne dla obu wersji"""
    # Simple Gates (pr_sgate)
    AND = 0
    OR = 1
    NOT = 2
    SR_LATCH = 3
    TOGGLE_LATCH = 4
    TRANSPARENT_LATCH = 5
    NOR = 6
    NAND = 7
    XOR = 8
    XNOR = 9
    BUFFER = 10
    MULTIPLEXER = 11
    REPEATER = 12

    # Sequential Gates (pr_igate)
    TIMER = 13
    COUNTER = 14
    SEQUENCER = 15
    PULSE = 16
    RANDOMIZER = 17
    STATE_CELL = 18
    SYNCHRONIZER = 19

    # Sensor Gates
    LIGHT_SENSOR = 20
    RAIN_SENSOR = 21

    # Bundled Gates (pr_bgate)
    BUS_TRANSCEIVER = 22

    # Array Gates (pr_agate)
    NULL_CELL = 23
    INVERT_CELL = 24
    BUFFER_CELL = 25
    COMPARATOR = 26
    AND_CELL = 27

    # More Bundled Gates
    BUS_RANDOMIZER = 28
    BUS_CONVERTER = 29
    BUS_INPUT_PANEL = 30
    STACKING_LATCH = 31
    SEGMENT_DISPLAY = 32
    DEC_RANDOMIZER = 33

    # IC Gate (Fabrication)
    IC_GATE = 34


class GatePartType(Enum):
    """Typy multipart dla bramek"""
    PR_SGATE = "pr_sgate"  # Simple/Combo gates
    PR_IGATE = "pr_igate"  # Sequential gates
    PR_AGATE = "pr_agate"  # Array gates
    PR_BGATE = "pr_bgate"  # Bundled gates
    PR_TGATE = "pr_tgate"  # Additional sequential
    PR_ICGATE = "pr_icgate"  # IC gates (Fabrication)


# Mapowanie GateType -> GatePartType
GATE_PART_TYPE_MAP = {
    GateType.AND: GatePartType.PR_SGATE,
    GateType.OR: GatePartType.PR_SGATE,
    GateType.NOT: GatePartType.PR_SGATE,
    GateType.SR_LATCH: GatePartType.PR_SGATE,
    GateType.TOGGLE_LATCH: GatePartType.PR_SGATE,
    GateType.TRANSPARENT_LATCH: GatePartType.PR_SGATE,
    GateType.NOR: GatePartType.PR_SGATE,
    GateType.NAND: GatePartType.PR_SGATE,
    GateType.XOR: GatePartType.PR_SGATE,
    GateType.XNOR: GatePartType.PR_SGATE,
    GateType.BUFFER: GatePartType.PR_SGATE,
    GateType.MULTIPLEXER: GatePartType.PR_SGATE,
    GateType.REPEATER: GatePartType.PR_SGATE,
    GateType.TIMER: GatePartType.PR_IGATE,
    GateType.COUNTER: GatePartType.PR_IGATE,
    GateType.SEQUENCER: GatePartType.PR_IGATE,
    GateType.PULSE: GatePartType.PR_IGATE,
    GateType.RANDOMIZER: GatePartType.PR_SGATE,
    GateType.STATE_CELL: GatePartType.PR_IGATE,
    GateType.SYNCHRONIZER: GatePartType.PR_SGATE,
    GateType.LIGHT_SENSOR: GatePartType.PR_SGATE,
    GateType.RAIN_SENSOR: GatePartType.PR_SGATE,
    GateType.BUS_TRANSCEIVER: GatePartType.PR_BGATE,
    GateType.NULL_CELL: GatePartType.PR_AGATE,
    GateType.INVERT_CELL: GatePartType.PR_AGATE,
    GateType.BUFFER_CELL: GatePartType.PR_AGATE,
    GateType.COMPARATOR: GatePartType.PR_SGATE,
    GateType.AND_CELL: GatePartType.PR_AGATE,
    GateType.BUS_RANDOMIZER: GatePartType.PR_BGATE,
    GateType.BUS_CONVERTER: GatePartType.PR_BGATE,
    GateType.BUS_INPUT_PANEL: GatePartType.PR_BGATE,
    GateType.STACKING_LATCH: GatePartType.PR_SGATE,
    GateType.SEGMENT_DISPLAY: GatePartType.PR_BGATE,
    GateType.DEC_RANDOMIZER: GatePartType.PR_SGATE,
    GateType.IC_GATE: GatePartType.PR_ICGATE,
}


# Direction constants (relative to gate)
class Direction(Enum):
    SOUTH = 0  # Front (output for most gates)
    WEST = 1   # Right
    NORTH = 2  # Back (input for most gates)
    EAST = 3   # Left


# =============================================================================
# Base Gate Classes
# =============================================================================

@dataclass
class GatePart:
    """
    Bazowa klasa dla wszystkich bramek.

    NBT Tags (wspolne dla 1.7.10 i 1.18.2):
    - orient (Byte): Orientacja (side + rotation zakodowane)
    - subID (Byte): Typ bramki (GateType ordinal)
    - shape (Byte): Ksztalt/wariant bramki
    - connMap (Integer): Mapa polaczen
    - schedTime (Long): Zaplanowany czas tick

    Orientation encoding:
    - side (0-5): Strona bloku na ktorej jest bramka
    - rotation (0-3): Rotacja bramki na tej stronie
    - orientation = (side & 7) | (rotation << 3)
    """

    gate_type: GateType
    orientation: int = 0  # side + rotation encoded
    shape: int = 0
    conn_map: int = 0xF000  # Connection bitmap
    sched_time: int = -1

    # Input/Output state (4 bits each, for 4 directions)
    input_mask: int = 0  # Which directions are inputs
    output_mask: int = 0  # Which directions are outputs
    state: int = 0  # Current state (gate-specific)

    @property
    def side(self) -> int:
        """Strona bloku (0-5)"""
        return self.orientation & 7

    @side.setter
    def side(self, value: int):
        self.orientation = (self.orientation & ~7) | (value & 7)

    @property
    def rotation(self) -> int:
        """Rotacja na stronie (0-3)"""
        return (self.orientation >> 3) & 3

    @rotation.setter
    def rotation(self, value: int):
        self.orientation = (self.orientation & 7) | ((value & 3) << 3)

    def to_internal(self, r: int) -> int:
        """Konwertuje kierunek zewnetrzny do wewnetrznego"""
        return (r + 4 - self.rotation) & 3

    def to_absolute(self, r: int) -> int:
        """Konwertuje kierunek wewnetrzny do zewnetrznego"""
        return (r + self.rotation) & 3

    def get_input(self, direction: int) -> bool:
        """Pobiera stan wejscia dla danego kierunku"""
        return bool(self.state & (1 << direction))

    def set_output(self, direction: int, value: bool):
        """Ustawia stan wyjscia dla danego kierunku"""
        mask = 0x10 << direction
        if value:
            self.state |= mask
        else:
            self.state &= ~mask

    def get_output(self, direction: int) -> bool:
        """Pobiera stan wyjscia dla danego kierunku"""
        return bool(self.state & (0x10 << direction))

    @abstractmethod
    def on_change(self, inputs: List[bool]) -> List[bool]:
        """
        Przetwarza zmiane wejsc i zwraca nowe wyjscia.

        Args:
            inputs: Lista stanow wejsc [S, W, N, E] (True = high)

        Returns:
            Lista stanow wyjsc [S, W, N, E]
        """
        pass

    def scheduled_tick(self) -> Optional[List[bool]]:
        """Wywoływany gdy sched_time zostanie osiagniety"""
        return None

    def on_tick(self, world_time: int):
        """Wywoływany co tick"""
        pass

    def cycle_shape(self) -> bool:
        """Zmienia ksztalt/wariant bramki. Zwraca True jesli zmieniono."""
        return False

    def save_nbt(self) -> Dict:
        """Zapisuje stan do NBT"""
        return {
            "orient": self.orientation,
            "subID": self.gate_type.value,
            "shape": self.shape,
            "connMap": self.conn_map,
            "schedTime": self.sched_time,
            "nolegacy": True,  # 1.7.10 legacy flag
        }

    def load_nbt(self, nbt: Dict):
        """Wczytuje stan z NBT"""
        self.orientation = nbt.get("orient", 0)
        self.shape = nbt.get("shape", 0)
        if nbt.get("nolegacy", False):
            self.conn_map = nbt.get("connMap", 0xF000)
        else:
            # Legacy loading for old saves
            self.conn_map = nbt.get("connMap", 0) | 0xF000
        self.sched_time = nbt.get("schedTime", -1)


# =============================================================================
# Simple Gates Implementation
# =============================================================================

class ANDGate(GatePart):
    """Bramka AND - wyjscie high gdy wszystkie wejscia high"""

    def __init__(self):
        super().__init__(gate_type=GateType.AND)
        self.input_mask = 0b1110  # W, N, E are inputs
        self.output_mask = 0b0001  # S is output

    def on_change(self, inputs: List[bool]) -> List[bool]:
        # AND: output = W AND N AND E
        result = inputs[1] and inputs[2] and inputs[3]
        return [result, False, False, False]


class ORGate(GatePart):
    """Bramka OR - wyjscie high gdy jakiekolwiek wejscie high"""

    def __init__(self):
        super().__init__(gate_type=GateType.OR)
        self.input_mask = 0b1110
        self.output_mask = 0b0001

    def on_change(self, inputs: List[bool]) -> List[bool]:
        result = inputs[1] or inputs[2] or inputs[3]
        return [result, False, False, False]


class NOTGate(GatePart):
    """Bramka NOT - wyjscie odwrotne do wejscia"""

    def __init__(self):
        super().__init__(gate_type=GateType.NOT)
        self.input_mask = 0b0100  # N is input
        self.output_mask = 0b1011  # S, W, E are outputs

    def on_change(self, inputs: List[bool]) -> List[bool]:
        result = not inputs[2]
        return [result, result, False, result]


class NORGate(GatePart):
    """Bramka NOR - NOT OR"""

    def __init__(self):
        super().__init__(gate_type=GateType.NOR)
        self.input_mask = 0b1110
        self.output_mask = 0b0001

    def on_change(self, inputs: List[bool]) -> List[bool]:
        result = not (inputs[1] or inputs[2] or inputs[3])
        return [result, False, False, False]


class NANDGate(GatePart):
    """Bramka NAND - NOT AND"""

    def __init__(self):
        super().__init__(gate_type=GateType.NAND)
        self.input_mask = 0b1110
        self.output_mask = 0b0001

    def on_change(self, inputs: List[bool]) -> List[bool]:
        result = not (inputs[1] and inputs[2] and inputs[3])
        return [result, False, False, False]


class XORGate(GatePart):
    """Bramka XOR - wyjscie high gdy nieparzysta liczba wejsc high"""

    def __init__(self):
        super().__init__(gate_type=GateType.XOR)
        self.input_mask = 0b1010  # N, W are inputs
        self.output_mask = 0b0001

    def on_change(self, inputs: List[bool]) -> List[bool]:
        result = inputs[1] != inputs[3]  # W XOR E
        return [result, False, False, False]


class XNORGate(GatePart):
    """Bramka XNOR - NOT XOR"""

    def __init__(self):
        super().__init__(gate_type=GateType.XNOR)
        self.input_mask = 0b1010
        self.output_mask = 0b0001

    def on_change(self, inputs: List[bool]) -> List[bool]:
        result = inputs[1] == inputs[3]  # W XNOR E
        return [result, False, False, False]


class BufferGate(GatePart):
    """Buffer - przepuszcza sygnal bez zmiany, 3 wyjscia"""

    def __init__(self):
        super().__init__(gate_type=GateType.BUFFER)
        self.input_mask = 0b0100  # N is input
        self.output_mask = 0b1011  # S, W, E are outputs

    def on_change(self, inputs: List[bool]) -> List[bool]:
        result = inputs[2]
        return [result, result, False, result]


class MultiplexerGate(GatePart):
    """Multiplexer - wybiera wejscie na podstawie selektora"""

    def __init__(self):
        super().__init__(gate_type=GateType.MULTIPLEXER)
        self.input_mask = 0b1110  # W=A, N=sel, E=B
        self.output_mask = 0b0001

    def on_change(self, inputs: List[bool]) -> List[bool]:
        # W=A, N=selector, E=B
        # If selector high, output B; else output A
        result = inputs[3] if inputs[2] else inputs[1]
        return [result, False, False, False]


class RepeaterGate(GatePart):
    """Repeater - opoznia sygnal o ustawiany czas"""

    def __init__(self):
        super().__init__(gate_type=GateType.REPEATER)
        self.input_mask = 0b0100
        self.output_mask = 0b0001
        self.delay = 2  # Default delay in ticks (shape controls this)

    def on_change(self, inputs: List[bool]) -> List[bool]:
        # Repeater uses scheduled tick for delay
        return [inputs[2], False, False, False]

    def cycle_shape(self) -> bool:
        self.shape = (self.shape + 1) % 4
        self.delay = (self.shape + 1) * 2  # 2, 4, 6, 8 ticks
        return True


class RandomizerGate(GatePart):
    """Randomizer - wyjscie losowe przy zmianie wejscia"""

    def __init__(self):
        super().__init__(gate_type=GateType.RANDOMIZER)
        self.input_mask = 0b0100
        self.output_mask = 0b1011

    def on_change(self, inputs: List[bool]) -> List[bool]:
        if inputs[2]:  # Input high triggers random
            r = random.randint(0, 7)
            return [bool(r & 1), bool(r & 2), False, bool(r & 4)]
        return [False, False, False, False]


# =============================================================================
# Sequential Gates Implementation
# =============================================================================

class TimerGate(GatePart):
    """
    Timer - generuje impulsy w regularnych odstepach.

    Dodatkowe NBT:
    - pointer (Integer): Aktualny licznik
    - interval (Integer): Interwal miedzy impulsami
    """

    def __init__(self):
        super().__init__(gate_type=GateType.TIMER)
        self.input_mask = 0b1110
        self.output_mask = 0b0001
        self.pointer: int = 0
        self.interval: int = 20  # Default 1 second

    def on_change(self, inputs: List[bool]) -> List[bool]:
        # Timer is paused when any input is high
        return [False, False, False, False]

    def on_tick(self, world_time: int):
        """Timer tick - generuje impulsy"""
        # If paused (any input high), reset
        if self.state & 0x0E:  # Check W, N, E inputs
            self.pointer = 0
            return

        self.pointer += 1
        if self.pointer >= self.interval:
            self.pointer = 0
            # Trigger output pulse

    def scheduled_tick(self) -> Optional[List[bool]]:
        if self.pointer >= self.interval:
            self.pointer = 0
            return [True, False, False, False]
        return None

    def save_nbt(self) -> Dict:
        nbt = super().save_nbt()
        nbt["pointer"] = self.pointer
        nbt["interval"] = self.interval
        return nbt

    def load_nbt(self, nbt: Dict):
        super().load_nbt(nbt)
        self.pointer = nbt.get("pointer", 0)
        self.interval = nbt.get("interval", 20)


class CounterGate(GatePart):
    """
    Counter - liczy impulsy wejsciowe.

    Dodatkowe NBT:
    - value (Integer): Aktualna wartosc licznika
    - max (Integer): Maksymalna wartosc
    - incr (Integer): Inkrementacja
    - decr (Integer): Dekrementacja
    """

    def __init__(self):
        super().__init__(gate_type=GateType.COUNTER)
        self.input_mask = 0b1010  # W=decr, E=incr
        self.output_mask = 0b0101  # S=max, N=zero
        self.value: int = 0
        self.max_val: int = 10
        self.incr: int = 1
        self.decr: int = 1
        self._prev_inputs: List[bool] = [False, False, False, False]

    def on_change(self, inputs: List[bool]) -> List[bool]:
        # Detect rising edges
        incr_edge = inputs[3] and not self._prev_inputs[3]  # E rising
        decr_edge = inputs[1] and not self._prev_inputs[1]  # W rising

        if incr_edge:
            self.value = min(self.value + self.incr, self.max_val)
        if decr_edge:
            self.value = max(self.value - self.decr, 0)

        self._prev_inputs = inputs.copy()

        at_max = self.value >= self.max_val
        at_zero = self.value <= 0
        return [at_max, False, at_zero, False]

    def save_nbt(self) -> Dict:
        nbt = super().save_nbt()
        nbt["value"] = self.value
        nbt["max"] = self.max_val
        nbt["incr"] = self.incr
        nbt["decr"] = self.decr
        return nbt

    def load_nbt(self, nbt: Dict):
        super().load_nbt(nbt)
        self.value = nbt.get("value", 0)
        self.max_val = nbt.get("max", 10)
        self.incr = nbt.get("incr", 1)
        self.decr = nbt.get("decr", 1)


class SequencerGate(GatePart):
    """
    Sequencer - sekwencyjnie aktywuje wyjscia.

    Dodatkowe NBT:
    - pointer (Integer): Aktualny krok (0-3)
    """

    def __init__(self):
        super().__init__(gate_type=GateType.SEQUENCER)
        self.output_mask = 0b1111  # All directions are outputs
        self.pointer: int = 0

    def on_tick(self, world_time: int):
        """Przesuwa sekwencer co interwal"""
        pass

    def scheduled_tick(self) -> Optional[List[bool]]:
        self.pointer = (self.pointer + 1) % 4
        outputs = [False, False, False, False]
        outputs[self.pointer] = True
        return outputs

    def save_nbt(self) -> Dict:
        nbt = super().save_nbt()
        nbt["pointer"] = self.pointer
        return nbt

    def load_nbt(self, nbt: Dict):
        super().load_nbt(nbt)
        self.pointer = nbt.get("pointer", 0)


class PulseGate(GatePart):
    """Pulse - generuje krotki impuls przy zmianie wejscia"""

    def __init__(self):
        super().__init__(gate_type=GateType.PULSE)
        self.input_mask = 0b0100
        self.output_mask = 0b0001
        self._prev_input: bool = False

    def on_change(self, inputs: List[bool]) -> List[bool]:
        rising = inputs[2] and not self._prev_input
        self._prev_input = inputs[2]
        return [rising, False, False, False]


class StateCellGate(GatePart):
    """
    State Cell - przechowuje stan i przesyla go.

    Dodatkowe NBT:
    - state (Boolean): Przechowywany stan
    """

    def __init__(self):
        super().__init__(gate_type=GateType.STATE_CELL)
        self.input_mask = 0b1100  # N=input, E=clock
        self.output_mask = 0b0011  # S=output, W=inverted
        self.stored_state: bool = False

    def on_change(self, inputs: List[bool]) -> List[bool]:
        # On clock rising edge, capture input
        clock = inputs[3]  # E
        data = inputs[2]  # N

        if clock:
            self.stored_state = data

        return [self.stored_state, not self.stored_state, False, False]

    def save_nbt(self) -> Dict:
        nbt = super().save_nbt()
        nbt["state"] = self.stored_state
        return nbt

    def load_nbt(self, nbt: Dict):
        super().load_nbt(nbt)
        self.stored_state = nbt.get("state", False)


class SRLatchGate(GatePart):
    """SR Latch - Set/Reset latch"""

    def __init__(self):
        super().__init__(gate_type=GateType.SR_LATCH)
        self.input_mask = 0b1010  # W=reset, E=set
        self.output_mask = 0b0101  # S=Q, N=!Q
        self.q: bool = False

    def on_change(self, inputs: List[bool]) -> List[bool]:
        set_in = inputs[3]  # E
        reset_in = inputs[1]  # W

        if set_in and not reset_in:
            self.q = True
        elif reset_in and not set_in:
            self.q = False
        # If both high or both low, maintain state

        return [self.q, False, not self.q, False]

    def save_nbt(self) -> Dict:
        nbt = super().save_nbt()
        nbt["q"] = self.q
        return nbt

    def load_nbt(self, nbt: Dict):
        super().load_nbt(nbt)
        self.q = nbt.get("q", False)


class ToggleLatchGate(GatePart):
    """Toggle Latch - przełącza stan przy kazdym impulsie"""

    def __init__(self):
        super().__init__(gate_type=GateType.TOGGLE_LATCH)
        self.input_mask = 0b1010  # W=toggle1, E=toggle2
        self.output_mask = 0b0101  # S=Q, N=!Q
        self.q: bool = False
        self._prev_inputs: List[bool] = [False, False, False, False]

    def on_change(self, inputs: List[bool]) -> List[bool]:
        # Toggle on rising edge of either input
        toggle1_edge = inputs[1] and not self._prev_inputs[1]
        toggle2_edge = inputs[3] and not self._prev_inputs[3]

        if toggle1_edge or toggle2_edge:
            self.q = not self.q

        self._prev_inputs = inputs.copy()
        return [self.q, False, not self.q, False]

    def save_nbt(self) -> Dict:
        nbt = super().save_nbt()
        nbt["q"] = self.q
        return nbt

    def load_nbt(self, nbt: Dict):
        super().load_nbt(nbt)
        self.q = nbt.get("q", False)


class TransparentLatchGate(GatePart):
    """Transparent Latch - przepuszcza dane gdy enable high"""

    def __init__(self):
        super().__init__(gate_type=GateType.TRANSPARENT_LATCH)
        self.input_mask = 0b1100  # N=data, E=enable
        self.output_mask = 0b0001  # S=output
        self.stored: bool = False

    def on_change(self, inputs: List[bool]) -> List[bool]:
        enable = inputs[3]  # E
        data = inputs[2]  # N

        if enable:
            self.stored = data
            return [data, False, False, False]
        return [self.stored, False, False, False]

    def save_nbt(self) -> Dict:
        nbt = super().save_nbt()
        nbt["stored"] = self.stored
        return nbt

    def load_nbt(self, nbt: Dict):
        super().load_nbt(nbt)
        self.stored = nbt.get("stored", False)


# =============================================================================
# Array Gates Implementation
# =============================================================================

class NullCellGate(GatePart):
    """Null Cell - pusta komorka do laczenia przewodow"""

    def __init__(self):
        super().__init__(gate_type=GateType.NULL_CELL)
        self.input_mask = 0b0100
        self.output_mask = 0b0001

    def on_change(self, inputs: List[bool]) -> List[bool]:
        return [inputs[2], False, False, False]


class InvertCellGate(GatePart):
    """Invert Cell - odwraca sygnal"""

    def __init__(self):
        super().__init__(gate_type=GateType.INVERT_CELL)
        self.input_mask = 0b0100
        self.output_mask = 0b0001

    def on_change(self, inputs: List[bool]) -> List[bool]:
        return [not inputs[2], False, False, False]


class BufferCellGate(GatePart):
    """Buffer Cell - buforuje sygnal"""

    def __init__(self):
        super().__init__(gate_type=GateType.BUFFER_CELL)
        self.input_mask = 0b0100
        self.output_mask = 0b0001

    def on_change(self, inputs: List[bool]) -> List[bool]:
        return [inputs[2], False, False, False]


class ANDCellGate(GatePart):
    """AND Cell - AND z dwoma wejsciami"""

    def __init__(self):
        super().__init__(gate_type=GateType.AND_CELL)
        self.input_mask = 0b0110  # N, W
        self.output_mask = 0b0001

    def on_change(self, inputs: List[bool]) -> List[bool]:
        return [inputs[1] and inputs[2], False, False, False]


class ComparatorGate(GatePart):
    """Comparator - porownuje dwa sygnaly analogowe"""

    def __init__(self):
        super().__init__(gate_type=GateType.COMPARATOR)
        self.input_mask = 0b1110  # W, N, E
        self.output_mask = 0b0001

    def on_change(self, inputs: List[bool]) -> List[bool]:
        # Simplified - in reality uses analog signal levels
        main = inputs[2]  # N
        side = inputs[1] or inputs[3]  # W or E

        # Subtract mode (shape 0) vs Compare mode (shape 1)
        if self.shape == 0:
            result = main and not side
        else:
            result = main

        return [result, False, False, False]


# =============================================================================
# Gate Factory
# =============================================================================

GATE_CLASSES = {
    GateType.AND: ANDGate,
    GateType.OR: ORGate,
    GateType.NOT: NOTGate,
    GateType.NOR: NORGate,
    GateType.NAND: NANDGate,
    GateType.XOR: XORGate,
    GateType.XNOR: XNORGate,
    GateType.BUFFER: BufferGate,
    GateType.MULTIPLEXER: MultiplexerGate,
    GateType.REPEATER: RepeaterGate,
    GateType.RANDOMIZER: RandomizerGate,
    GateType.TIMER: TimerGate,
    GateType.COUNTER: CounterGate,
    GateType.SEQUENCER: SequencerGate,
    GateType.PULSE: PulseGate,
    GateType.STATE_CELL: StateCellGate,
    GateType.SR_LATCH: SRLatchGate,
    GateType.TOGGLE_LATCH: ToggleLatchGate,
    GateType.TRANSPARENT_LATCH: TransparentLatchGate,
    GateType.NULL_CELL: NullCellGate,
    GateType.INVERT_CELL: InvertCellGate,
    GateType.BUFFER_CELL: BufferCellGate,
    GateType.AND_CELL: ANDCellGate,
    GateType.COMPARATOR: ComparatorGate,
}


def create_gate(gate_type: GateType) -> Optional[GatePart]:
    """Tworzy bramke danego typu"""
    cls = GATE_CLASSES.get(gate_type)
    if cls:
        return cls()
    return None


def create_gate_from_nbt(nbt: Dict) -> Optional[GatePart]:
    """Tworzy bramke z NBT"""
    sub_id = nbt.get("subID", 0)
    try:
        gate_type = GateType(sub_id)
    except ValueError:
        return None

    gate = create_gate(gate_type)
    if gate:
        gate.load_nbt(nbt)
    return gate


# =============================================================================
# Conversion Utilities
# =============================================================================

def convert_gate_nbt_1710_to_1182(nbt_1710: Dict) -> Dict:
    """
    Konwertuje NBT bramki z 1.7.10 do 1.18.2+.

    Glowne roznice:
    - Struktura NBT jest bardzo podobna
    - Niektore pola moga miec inne nazwy w roznych wersjach
    - 1.18.2 moze miec dodatkowe pola dla BlockState
    """
    nbt_1182 = {
        "orient": nbt_1710.get("orient", 0),
        "subID": nbt_1710.get("subID", 0),
        "shape": nbt_1710.get("shape", 0),
        "connMap": nbt_1710.get("connMap", 0xF000),
        "schedTime": nbt_1710.get("schedTime", -1),
    }

    # Copy gate-specific fields
    for key in ["pointer", "interval", "value", "max", "incr", "decr",
                "state", "q", "stored"]:
        if key in nbt_1710:
            nbt_1182[key] = nbt_1710[key]

    return nbt_1182


def get_gate_type_name(gate_type: GateType) -> str:
    """Zwraca nazwe bramki dla danego typu"""
    names = {
        GateType.AND: "and_gate",
        GateType.OR: "or_gate",
        GateType.NOT: "not_gate",
        GateType.NOR: "nor_gate",
        GateType.NAND: "nand_gate",
        GateType.XOR: "xor_gate",
        GateType.XNOR: "xnor_gate",
        GateType.BUFFER: "buffer_gate",
        GateType.MULTIPLEXER: "multiplexer",
        GateType.REPEATER: "repeater",
        GateType.TIMER: "timer",
        GateType.COUNTER: "counter",
        GateType.SEQUENCER: "sequencer",
        GateType.PULSE: "pulse_gate",
        GateType.RANDOMIZER: "randomizer",
        GateType.STATE_CELL: "state_cell",
        GateType.SR_LATCH: "sr_latch",
        GateType.TOGGLE_LATCH: "toggle_latch",
        GateType.TRANSPARENT_LATCH: "transparent_latch",
    }
    return names.get(gate_type, f"gate_{gate_type.value}")


# =============================================================================
# Tests and Demonstrations
# =============================================================================

def test_simple_gates():
    """Test prostych bramek logicznych"""
    print("=== Test Simple Gates ===")

    # AND Gate
    and_gate = ANDGate()
    assert and_gate.on_change([False, True, True, True]) == [True, False, False, False]
    assert and_gate.on_change([False, True, False, True]) == [False, False, False, False]
    print("AND Gate: OK")

    # OR Gate
    or_gate = ORGate()
    assert or_gate.on_change([False, True, False, False]) == [True, False, False, False]
    assert or_gate.on_change([False, False, False, False]) == [False, False, False, False]
    print("OR Gate: OK")

    # NOT Gate
    not_gate = NOTGate()
    assert not_gate.on_change([False, False, True, False])[0] == False
    assert not_gate.on_change([False, False, False, False])[0] == True
    print("NOT Gate: OK")

    # XOR Gate
    xor_gate = XORGate()
    assert xor_gate.on_change([False, True, False, False])[0] == True
    assert xor_gate.on_change([False, True, False, True])[0] == False
    print("XOR Gate: OK")

    print()


def test_sequential_gates():
    """Test bramek sekwencyjnych"""
    print("=== Test Sequential Gates ===")

    # Counter
    counter = CounterGate()
    counter.max_val = 5

    # Increment
    counter.on_change([False, False, False, False])
    for i in range(5):
        outputs = counter.on_change([False, False, False, True])
        counter.on_change([False, False, False, False])

    print(f"Counter after 5 increments: {counter.value}")
    assert counter.value == 5

    # Decrement
    outputs = counter.on_change([False, True, False, False])
    counter.on_change([False, False, False, False])
    print(f"Counter after decrement: {counter.value}")
    assert counter.value == 4

    print("Counter: OK")

    # Toggle Latch
    toggle = ToggleLatchGate()
    assert toggle.q == False

    toggle.on_change([False, True, False, False])
    assert toggle.q == True

    toggle.on_change([False, False, False, False])
    toggle.on_change([False, False, False, True])
    assert toggle.q == False

    print("Toggle Latch: OK")

    print()


def test_nbt_save_load():
    """Test zapisu i odczytu NBT"""
    print("=== Test NBT Save/Load ===")

    # Create and configure gate
    counter = CounterGate()
    counter.value = 7
    counter.max_val = 15
    counter.orientation = 0b00011  # side=3, rotation=0

    # Save
    nbt = counter.save_nbt()
    print(f"Saved NBT: {nbt}")

    # Load into new gate
    counter2 = CounterGate()
    counter2.load_nbt(nbt)

    assert counter2.value == 7
    assert counter2.max_val == 15
    assert counter2.orientation == 0b00011

    print("NBT Save/Load: OK")
    print()


def test_nbt_conversion():
    """Test konwersji NBT miedzy wersjami"""
    print("=== Test NBT Conversion ===")

    nbt_1710 = {
        "orient": 5,
        "subID": GateType.COUNTER.value,
        "shape": 0,
        "connMap": 0xF123,
        "schedTime": 100,
        "value": 10,
        "max": 20,
        "incr": 1,
        "decr": 1,
        "nolegacy": True,
    }

    nbt_1182 = convert_gate_nbt_1710_to_1182(nbt_1710)
    print(f"1.7.10 NBT: {nbt_1710}")
    print(f"1.18.2 NBT: {nbt_1182}")

    assert nbt_1182["value"] == 10
    assert nbt_1182["max"] == 20

    print("NBT Conversion: OK")
    print()


def demo_logic_circuit():
    """Demonstracja prostego obwodu logicznego"""
    print("=== Demo: Logic Circuit ===")
    print("Symulacja AND -> NOT -> OR")
    print()

    and_gate = ANDGate()
    not_gate = NOTGate()
    or_gate = ORGate()

    test_cases = [
        ([False, True, True, True], "A=1, B=1"),
        ([False, True, False, True], "A=1, B=0"),
        ([False, False, True, False], "A=0, B=1"),
        ([False, False, False, False], "A=0, B=0"),
    ]

    for inputs, desc in test_cases:
        # AND(A, B)
        and_out = and_gate.on_change(inputs)

        # NOT(AND result)
        not_out = not_gate.on_change([False, False, and_out[0], False])

        # OR(NOT result, extra input)
        or_out = or_gate.on_change([False, not_out[0], False, False])

        print(f"{desc}: AND={and_out[0]}, NOT={not_out[0]}, OR={or_out[0]}")

    print()


def demo_gate_list():
    """Lista wszystkich zaimplementowanych bramek"""
    print("=== Implemented Gates ===")

    for gate_type in GateType:
        cls = GATE_CLASSES.get(gate_type)
        part_type = GATE_PART_TYPE_MAP.get(gate_type, "unknown")
        status = "OK" if cls else "Not implemented"
        print(f"  {gate_type.name:20} ({part_type.value if hasattr(part_type, 'value') else part_type:10}): {status}")

    print()
    print(f"Implemented: {len(GATE_CLASSES)} / {len(GateType)}")
    print()


if __name__ == "__main__":
    demo_gate_list()
    test_simple_gates()
    test_sequential_gates()
    test_nbt_save_load()
    test_nbt_conversion()
    demo_logic_circuit()
