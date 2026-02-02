# ProjectRed Simulations

Symulacje dzialania funkcjonalnosci moda ProjectRed dla wersji 1.7.10 oraz 1.18.2+.

## Moduly

### 1. Power System (`power_system_simulation.py`)

Symulacja systemu energii Electrotine.

**Klasy 1.7.10:**
- `PowerConductor1710` - Bazowy conductor energii
- `PowerDrawPoint1710` - Conductor z mozliwoscia pobierania mocy
- `BatteryBox1710` - Skrzynka baterii (przechowuje energie)

**Klasy 1.18.2+:**
- `PowerConductor1182` - Uproszczony conductor
- `BatteryBox1182` - Skrzynka baterii

**Kluczowe roznice miedzy wersjami:**
- 1.7.10 uzywa zlozonego modelu z flows[], Vloc, Iloc, Vflow, Iflow
- 1.18.2 uzywa uproszczonego modelu z vCap, iCap
- Logika przechowywania energii jest identyczna

**Uzycie:**
```python
from simulations import BatteryBox1710, BatteryBox1182

# 1.7.10
bb = BatteryBox1710()
bb.cond.apply_power(10000, tick)
bb.update(tick)
print(f"Storage: {bb.storage}")

# 1.18.2
bb2 = BatteryBox1182()
bb2.cond.apply_power(10000)
bb2.update(tick)
```

### 2. Logic Gates (`gates_simulation.py`)

Symulacja bramek logicznych.

**Typy bramek:**
- Simple (pr_sgate): AND, OR, NOT, NOR, NAND, XOR, XNOR, Buffer, Multiplexer, Repeater, Randomizer
- Sequential (pr_igate): Timer, Counter, Sequencer, Pulse, StateCell
- Array (pr_agate): NullCell, InvertCell, BufferCell, ANDCell
- Bundled (pr_bgate): BusTransceiver, BusRandomizer, BusConverter, BusInputPanel

**Uzycie:**
```python
from simulations import ANDGate, TimerGate, create_gate, GateType

# Tworzenie bramki
and_gate = ANDGate()
outputs = and_gate.on_change([False, True, True, True])
# outputs = [True, False, False, False]

# Przez factory
timer = create_gate(GateType.TIMER)
timer.interval = 20  # 1 sekunda

# Z NBT
nbt = timer.save_nbt()
timer2 = create_gate(GateType.TIMER)
timer2.load_nbt(nbt)
```

### 3. Transmission Wires (`wires_simulation.py`)

Symulacja przewodow.

**Typy:**
- `RedAlloyWire` - Podstawowy przewod redstone
- `InsulatedWire` - Izolowany przewod (16 kolorow)
- `BundledCable` - Przewod bundled (16 kanalow)

**Uzycie:**
```python
from simulations import RedAlloyWire, InsulatedWire, WireColor, WireNetwork

# Red Alloy Wire
wire = RedAlloyWire()
wire.set_connected(0, True)  # South
outputs = wire.propagate_signal({2: 100})  # Input from North

# Insulated Wire
red_wire = InsulatedWire(WireColor.RED)
blue_wire = InsulatedWire(WireColor.BLUE)
can_connect = red_wire.can_connect_to(blue_wire)  # False

# Network
network = WireNetwork()
network.add_wire((0, 0, 0), wire)
network.propagate_from_source((0, 0, 0), 255)
```

### 4. Frames System (`frames_simulation.py`)

Symulacja systemu ramek.

**Klasy:**
- `Frame` - Blok ramki
- `FrameMotor` - Silnik napedzajacy ramki
- `FrameActuator` - Liniowy silownik
- `FrameWorld` - Srodowisko symulacji

**Uzycie:**
```python
from simulations import Frame, FrameMotor, FrameWorld, FrameDirection

# Tworzenie swiata
world = FrameWorld()

# Dodawanie ramek
for i in range(3):
    frame = Frame(position=(i, 0, 0))
    world.add_block((i, 0, 0), frame)

# Motor
motor = FrameMotor(position=(-1, 0, 0))
motor.side = FrameDirection.WEST
motor.charge = 1000
world.add_block((-1, 0, 0), motor)

# Ruch
blocks = motor.get_blocks_to_move(world)
world.move_blocks(blocks, motor.move_direction)
```

## Konwersja NBT

Kazdy modul zawiera funkcje konwersji NBT miedzy wersjami:

```python
from simulations import (
    convert_battery_box_nbt,
    convert_gate_nbt_1710_to_1182,
    convert_wire_nbt_1710_to_1182,
    convert_frame_motor_nbt,
)

# Konwersja BatteryBox
nbt_1710 = {"storage": 5000, "vl": 80.0, "chg": 800}
nbt_1182 = convert_battery_box_nbt(nbt_1710)

# Konwersja Gate
gate_nbt_1710 = {"orient": 5, "subID": 14, "value": 10}
gate_nbt_1182 = convert_gate_nbt_1710_to_1182(gate_nbt_1710)
```

## Uruchamianie testow

Kazdy modul zawiera testy i demonstracje:

```bash
cd src/converters/projectred/simulations

# Power System
python power_system_simulation.py

# Gates
python gates_simulation.py

# Wires
python wires_simulation.py

# Frames
python frames_simulation.py
```

## Wnioski dla konwersji

### Power System
- Storage (Integer) - bezposrednie mapowanie
- Conductor NBT - wymaga konwersji struktury
- Charge/Flow - identyczna logika

### Gates
- SubID - identyczne (GateType ordinal)
- Shape - identyczne
- ConnMap - identyczne
- Gate-specific NBT (pointer, interval, value) - bezposrednie mapowanie

### Wires
- Color - identyczne (WireColor ordinal)
- Signal - identyczne
- Bundled signals - bezposrednie mapowanie

### Frames
- Orientation - identyczne
- Moving/Progress - identyczne
- Extended (Actuator) - identyczne

## Pliki zrodlowe

**1.7.10 (Scala):**
- `mod_src/1710/actual_src/1.7.10/ProjectRed_GTNH/src/main/scala/mrtjp/projectred/`

**1.18.2+ (Java):**
- `mod_src/118/actual_src/1.18.2/ProjectRed/repo/`
