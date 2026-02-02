"""
ProjectRed Simulations
======================

Symulacje dzialania funkcjonalnosci moda ProjectRed dla wersji 1.7.10 oraz 1.18.2+.

Moduly:
- power_system_simulation: System energii Electrotine (PowerConductor, BatteryBox)
- gates_simulation: Bramki logiczne (AND, OR, Timer, Counter, etc.)
- wires_simulation: Przewody Transmission (RedWire, Insulated, Bundled)
- frames_simulation: System ramek (Frame, FrameMotor, FrameActuator)

Kazdy modul zawiera:
- Klasy symulacji dla wersji 1.7.10
- Klasy symulacji dla wersji 1.18.2+
- Funkcje konwersji NBT miedzy wersjami
- Testy i demonstracje

Uzycie:
    from simulations import (
        # Power System
        PowerConductor1710, PowerDrawPoint1710, BatteryBox1710,
        PowerConductor1182, BatteryBox1182,
        convert_battery_box_nbt,

        # Gates
        GateType, ANDGate, ORGate, TimerGate, CounterGate,
        create_gate, create_gate_from_nbt,
        convert_gate_nbt_1710_to_1182,

        # Wires
        WireType, WireColor, RedAlloyWire, InsulatedWire, BundledCable,
        WireNetwork, convert_wire_nbt_1710_to_1182,

        # Frames
        Direction, Frame, FrameMotor, FrameActuator, FrameWorld,
        convert_frame_motor_nbt, convert_frame_actuator_nbt,
    )
"""

# Power System
from .power_system_simulation import (
    # 1.7.10
    PowerConductor1710,
    PowerDrawPoint1710,
    IPowerConnectable1710,
    BatteryBox1710,
    # 1.18.2
    PowerConductor1182,
    IPowerConductorSource1182,
    BatteryBox1182,
    # Conversion
    convert_power_conductor_nbt,
    convert_battery_box_nbt,
)

# Gates
from .gates_simulation import (
    # Enums
    GateType,
    GatePartType,
    Direction,
    GATE_PART_TYPE_MAP,
    # Base classes
    GatePart,
    # Simple gates
    ANDGate,
    ORGate,
    NOTGate,
    NORGate,
    NANDGate,
    XORGate,
    XNORGate,
    BufferGate,
    MultiplexerGate,
    RepeaterGate,
    RandomizerGate,
    # Sequential gates
    TimerGate,
    CounterGate,
    SequencerGate,
    PulseGate,
    StateCellGate,
    SRLatchGate,
    ToggleLatchGate,
    TransparentLatchGate,
    # Array gates
    NullCellGate,
    InvertCellGate,
    BufferCellGate,
    ANDCellGate,
    ComparatorGate,
    # Factory
    GATE_CLASSES,
    create_gate,
    create_gate_from_nbt,
    # Conversion
    convert_gate_nbt_1710_to_1182,
    get_gate_type_name,
)

# Wires
from .wires_simulation import (
    # Enums
    WireType,
    WirePartType,
    WireColor,
    # Wire classes
    WirePart,
    RedAlloyWire,
    InsulatedWire,
    BundledCable,
    # Network
    WireNetwork,
    # Conversion
    convert_wire_nbt_1710_to_1182,
    get_wire_type_name,
)

# Frames
from .frames_simulation import (
    # Enums
    Direction as FrameDirection,
    DIRECTION_VECTORS,
    get_opposite,
    add_direction,
    # Classes
    Frame,
    FrameMotor,
    FrameActuator,
    FrameWorld,
    # Conversion
    convert_frame_motor_nbt,
    convert_frame_actuator_nbt,
)

__all__ = [
    # Power System - 1.7.10
    'PowerConductor1710',
    'PowerDrawPoint1710',
    'IPowerConnectable1710',
    'BatteryBox1710',
    # Power System - 1.18.2
    'PowerConductor1182',
    'IPowerConductorSource1182',
    'BatteryBox1182',
    # Power System - Conversion
    'convert_power_conductor_nbt',
    'convert_battery_box_nbt',

    # Gates - Enums
    'GateType',
    'GatePartType',
    'GATE_PART_TYPE_MAP',
    # Gates - Classes
    'GatePart',
    'ANDGate',
    'ORGate',
    'NOTGate',
    'NORGate',
    'NANDGate',
    'XORGate',
    'XNORGate',
    'BufferGate',
    'MultiplexerGate',
    'RepeaterGate',
    'RandomizerGate',
    'TimerGate',
    'CounterGate',
    'SequencerGate',
    'PulseGate',
    'StateCellGate',
    'SRLatchGate',
    'ToggleLatchGate',
    'TransparentLatchGate',
    'NullCellGate',
    'InvertCellGate',
    'BufferCellGate',
    'ANDCellGate',
    'ComparatorGate',
    # Gates - Factory
    'GATE_CLASSES',
    'create_gate',
    'create_gate_from_nbt',
    # Gates - Conversion
    'convert_gate_nbt_1710_to_1182',
    'get_gate_type_name',

    # Wires - Enums
    'WireType',
    'WirePartType',
    'WireColor',
    # Wires - Classes
    'WirePart',
    'RedAlloyWire',
    'InsulatedWire',
    'BundledCable',
    'WireNetwork',
    # Wires - Conversion
    'convert_wire_nbt_1710_to_1182',
    'get_wire_type_name',

    # Frames - Enums
    'FrameDirection',
    'DIRECTION_VECTORS',
    'get_opposite',
    'add_direction',
    # Frames - Classes
    'Frame',
    'FrameMotor',
    'FrameActuator',
    'FrameWorld',
    # Frames - Conversion
    'convert_frame_motor_nbt',
    'convert_frame_actuator_nbt',
]
