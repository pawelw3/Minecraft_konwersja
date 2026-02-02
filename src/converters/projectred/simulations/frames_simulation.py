"""
ProjectRed Frames System Simulation
====================================

Symulacja systemu ramek (Frames) dla ProjectRed.
Obejmuje Frame, FrameMotor i FrameActuator.

System ramek pozwala na przesuwanie polaczonych blokow jako jednosc.

Bazowane na kodzie zrodlowym:
- 1.7.10: mod_src/1710/actual_src/1.7.10/ProjectRed_GTNH/src/main/scala/mrtjp/projectred/expansion/TileFrameMotor.scala
- 1.7.10: mod_src/1710/actual_src/1.7.10/ProjectRed_GTNH/src/main/scala/mrtjp/projectred/expansion/TileFrameActuator.scala
- 1.18.2: mod_src/118/actual_src/1.18.2/ProjectRed/repo/expansion/
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
from abc import ABC, abstractmethod
from enum import Enum


# =============================================================================
# Enums and Constants
# =============================================================================

class Direction(Enum):
    """Kierunki w Minecraft"""
    DOWN = 0
    UP = 1
    NORTH = 2
    SOUTH = 3
    WEST = 4
    EAST = 5


# Direction vectors
DIRECTION_VECTORS = {
    Direction.DOWN: (0, -1, 0),
    Direction.UP: (0, 1, 0),
    Direction.NORTH: (0, 0, -1),
    Direction.SOUTH: (0, 0, 1),
    Direction.WEST: (-1, 0, 0),
    Direction.EAST: (1, 0, 0),
}


def get_opposite(direction: Direction) -> Direction:
    """Zwraca przeciwny kierunek"""
    opposites = {
        Direction.DOWN: Direction.UP,
        Direction.UP: Direction.DOWN,
        Direction.NORTH: Direction.SOUTH,
        Direction.SOUTH: Direction.NORTH,
        Direction.WEST: Direction.EAST,
        Direction.EAST: Direction.WEST,
    }
    return opposites[direction]


def add_direction(pos: Tuple[int, int, int], direction: Direction) -> Tuple[int, int, int]:
    """Dodaje wektor kierunku do pozycji"""
    vec = DIRECTION_VECTORS[direction]
    return (pos[0] + vec[0], pos[1] + vec[1], pos[2] + vec[2])


# =============================================================================
# Frame Block
# =============================================================================

@dataclass
class Frame:
    """
    Blok ramki (Frame Block).

    Ramki laczą sie z innymi ramkami i blokami, tworzac strukture
    ktora moze byc przesuwana przez FrameMotor lub FrameActuator.

    W 1.7.10: Brak TileEntity (prosty blok)
    W 1.18.2: Blok bez BlockEntity

    Kazda ramka ma maska polaczen (6 bitow, jedna strona = jeden bit).
    """

    position: Tuple[int, int, int] = (0, 0, 0)
    connection_mask: int = 0b111111  # Default: polaczenia we wszystkich kierunkach

    def is_connected(self, direction: Direction) -> bool:
        """Sprawdza czy ramka jest polaczona w danym kierunku"""
        return bool(self.connection_mask & (1 << direction.value))

    def set_connected(self, direction: Direction, connected: bool):
        """Ustawia polaczenie w danym kierunku"""
        if connected:
            self.connection_mask |= (1 << direction.value)
        else:
            self.connection_mask &= ~(1 << direction.value)

    def toggle_connection(self, direction: Direction):
        """Przelacza polaczenie w danym kierunku (screwdriver)"""
        self.connection_mask ^= (1 << direction.value)

    def get_connected_directions(self) -> List[Direction]:
        """Zwraca liste polaczonych kierunkow"""
        return [d for d in Direction if self.is_connected(d)]


# =============================================================================
# Frame Motor
# =============================================================================

@dataclass
class FrameMotor:
    """
    Frame Motor - silnik napedzajacy system ramek.

    Przesuwa polaczona strukture ramek w kierunku przeciwnym do strony
    na ktorej jest zamontowany, gdy otrzyma sygnal redstone.

    NBT Tags:
    - rot (Byte): Orientacja (side + rotation)
    - Conductor NBT (dla energii)

    Wymaga energii Electrotine do pracy.
    """

    position: Tuple[int, int, int] = (0, 0, 0)
    orientation: int = 0  # side | (rotation << 3)

    # Stan
    is_powered: bool = False
    is_moving: bool = False
    move_progress: float = 0.0  # 0.0 - 1.0

    # Energia
    charge: int = 0  # Energia z PowerConductor

    # Limity
    MAX_BLOCKS: int = 256  # Maksymalna liczba blokow do przesuniecia
    MOVE_SPEED: float = 0.05  # Predkosc ruchu na tick (1/20 = 1 blok/sekunde)
    ENERGY_PER_BLOCK: int = 100  # Energia na blok

    @property
    def side(self) -> Direction:
        """Strona na ktorej jest zamontowany motor"""
        return Direction(self.orientation & 7)

    @side.setter
    def side(self, value: Direction):
        self.orientation = (self.orientation & ~7) | value.value

    @property
    def move_direction(self) -> Direction:
        """Kierunek przesuwania (przeciwny do strony montazu)"""
        return get_opposite(self.side)

    def can_work(self) -> bool:
        """Sprawdza czy motor ma wystarczajaco energii"""
        return self.charge > 600

    def get_blocks_to_move(self, world: 'FrameWorld') -> Optional[Set[Tuple[int, int, int]]]:
        """
        Zbiera wszystkie bloki polaczone przez ramki do przesuniecia.

        Returns:
            Set pozycji blokow do przesuniecia, lub None jesli nie mozna
        """
        # Pozycja startowa (przed motorem)
        start_pos = add_direction(self.position, self.move_direction)

        if start_pos not in world.blocks:
            return None  # Nic przed motorem

        # BFS przez polaczone ramki
        to_move: Set[Tuple[int, int, int]] = set()
        queue: List[Tuple[int, int, int]] = [start_pos]

        while queue and len(to_move) < self.MAX_BLOCKS:
            pos = queue.pop(0)
            if pos in to_move:
                continue

            # Nie przesuwamy samego motora
            if pos == self.position:
                continue

            block = world.blocks.get(pos)
            if block is None:
                continue

            to_move.add(pos)

            # Jesli to ramka, sprawdz polaczenia
            if isinstance(block, Frame):
                for direction in block.get_connected_directions():
                    neighbor_pos = add_direction(pos, direction)
                    if neighbor_pos not in to_move and neighbor_pos in world.blocks:
                        queue.append(neighbor_pos)

        if len(to_move) >= self.MAX_BLOCKS:
            return None  # Za duzo blokow

        return to_move

    def try_move(self, world: 'FrameWorld') -> bool:
        """
        Probuje rozpoczac ruch.

        Returns:
            True jesli ruch zostal rozpoczety
        """
        if self.is_moving or not self.can_work():
            return False

        blocks = self.get_blocks_to_move(world)
        if blocks is None or len(blocks) == 0:
            return False

        # Sprawdz czy docelowe pozycje sa wolne
        for pos in blocks:
            target = add_direction(pos, self.move_direction)
            if target not in blocks and target in world.blocks:
                return False  # Blokada

        # Sprawdz energie
        energy_needed = len(blocks) * self.ENERGY_PER_BLOCK
        if self.charge * 10 < energy_needed:  # charge jest 0-1000, energia to 0-10000
            return False

        self.is_moving = True
        self.move_progress = 0.0
        return True

    def update(self, world: 'FrameWorld'):
        """Aktualizacja motora"""
        if not self.is_moving:
            if self.is_powered and self.can_work():
                self.try_move(world)
            return

        # Kontynuuj ruch
        self.move_progress += self.MOVE_SPEED

        if self.move_progress >= 1.0:
            # Ruch zakonczony - przesuń bloki
            blocks = self.get_blocks_to_move(world)
            if blocks:
                world.move_blocks(blocks, self.move_direction)

            self.is_moving = False
            self.move_progress = 0.0

    def save_nbt(self) -> Dict:
        """Zapisuje stan do NBT"""
        return {
            "rot": self.orientation,
            "moving": self.is_moving,
            "progress": self.move_progress,
        }

    def load_nbt(self, nbt: Dict):
        """Wczytuje stan z NBT"""
        self.orientation = nbt.get("rot", 0)
        self.is_moving = nbt.get("moving", False)
        self.move_progress = nbt.get("progress", 0.0)


# =============================================================================
# Frame Actuator
# =============================================================================

@dataclass
class FrameActuator:
    """
    Frame Actuator - liniowy silownik dla systemu ramek.

    Dziala podobnie do FrameMotor, ale:
    - Przesuwa bloki w obu kierunkach (push/pull)
    - Moze dzialac jako tlok

    NBT Tags:
    - rot (Byte): Orientacja
    - extended (Boolean): Czy wysuniety
    """

    position: Tuple[int, int, int] = (0, 0, 0)
    orientation: int = 0
    is_extended: bool = False
    is_moving: bool = False
    move_progress: float = 0.0

    charge: int = 0

    MAX_BLOCKS: int = 64  # Mniejszy limit niz motor
    MOVE_SPEED: float = 0.05

    @property
    def side(self) -> Direction:
        return Direction(self.orientation & 7)

    @side.setter
    def side(self, value: Direction):
        self.orientation = (self.orientation & ~7) | value.value

    @property
    def push_direction(self) -> Direction:
        """Kierunek wypychania"""
        return get_opposite(self.side)

    @property
    def pull_direction(self) -> Direction:
        """Kierunek wciagania"""
        return self.side

    def can_work(self) -> bool:
        return self.charge > 600

    def try_extend(self, world: 'FrameWorld') -> bool:
        """Probuje wysunac actuator"""
        if self.is_extended or self.is_moving:
            return False

        self.is_moving = True
        self.move_progress = 0.0
        return True

    def try_retract(self, world: 'FrameWorld') -> bool:
        """Probuje schowac actuator"""
        if not self.is_extended or self.is_moving:
            return False

        self.is_moving = True
        self.move_progress = 0.0
        return True

    def update(self, world: 'FrameWorld', powered: bool):
        """Aktualizacja actuatora"""
        if not self.is_moving:
            if powered and not self.is_extended and self.can_work():
                self.try_extend(world)
            elif not powered and self.is_extended and self.can_work():
                self.try_retract(world)
            return

        self.move_progress += self.MOVE_SPEED

        if self.move_progress >= 1.0:
            self.is_extended = not self.is_extended
            self.is_moving = False
            self.move_progress = 0.0

    def save_nbt(self) -> Dict:
        return {
            "rot": self.orientation,
            "extended": self.is_extended,
            "moving": self.is_moving,
            "progress": self.move_progress,
        }

    def load_nbt(self, nbt: Dict):
        self.orientation = nbt.get("rot", 0)
        self.is_extended = nbt.get("extended", False)
        self.is_moving = nbt.get("moving", False)
        self.move_progress = nbt.get("progress", 0.0)


# =============================================================================
# Frame World Simulation
# =============================================================================

@dataclass
class FrameWorld:
    """
    Symulacja swiata z ramkami i blokami.

    Zarzadza pozycjami blokow i ich przesuwaniem.
    """

    blocks: Dict[Tuple[int, int, int], object] = field(default_factory=dict)
    motors: Dict[Tuple[int, int, int], FrameMotor] = field(default_factory=dict)
    actuators: Dict[Tuple[int, int, int], FrameActuator] = field(default_factory=dict)

    def add_block(self, pos: Tuple[int, int, int], block: object):
        """Dodaje blok do swiata"""
        self.blocks[pos] = block
        if isinstance(block, Frame):
            block.position = pos
        elif isinstance(block, FrameMotor):
            block.position = pos
            self.motors[pos] = block
        elif isinstance(block, FrameActuator):
            block.position = pos
            self.actuators[pos] = block

    def remove_block(self, pos: Tuple[int, int, int]):
        """Usuwa blok ze swiata"""
        if pos in self.blocks:
            block = self.blocks[pos]
            del self.blocks[pos]
            if pos in self.motors:
                del self.motors[pos]
            if pos in self.actuators:
                del self.actuators[pos]

    def move_blocks(self, positions: Set[Tuple[int, int, int]], direction: Direction):
        """
        Przesuwa zestaw blokow w danym kierunku.

        Args:
            positions: Pozycje blokow do przesuniecia
            direction: Kierunek przesuniecia
        """
        # Zbierz bloki do przesuniecia
        moving_blocks: Dict[Tuple[int, int, int], object] = {}
        for pos in positions:
            if pos in self.blocks:
                moving_blocks[pos] = self.blocks[pos]
                del self.blocks[pos]

        # Usun z motors/actuators
        for pos in list(self.motors.keys()):
            if pos in positions:
                del self.motors[pos]
        for pos in list(self.actuators.keys()):
            if pos in positions:
                del self.actuators[pos]

        # Przenies bloki na nowe pozycje
        for old_pos, block in moving_blocks.items():
            new_pos = add_direction(old_pos, direction)

            # Aktualizuj pozycje w bloku
            if isinstance(block, Frame):
                block.position = new_pos
            elif isinstance(block, FrameMotor):
                block.position = new_pos
            elif isinstance(block, FrameActuator):
                block.position = new_pos

            self.add_block(new_pos, block)

    def tick(self):
        """Tick swiata - aktualizuje wszystkie motory i actuatory"""
        for motor in list(self.motors.values()):
            motor.update(self)

        for actuator in list(self.actuators.values()):
            # Simplified - w rzeczywistosci sprawdzalibysmy redstone
            actuator.update(self, False)


# =============================================================================
# Conversion Utilities
# =============================================================================

def convert_frame_motor_nbt(nbt_1710: Dict) -> Dict:
    """Konwertuje NBT FrameMotor z 1.7.10 do 1.18.2+"""
    return {
        "rot": nbt_1710.get("rot", 0),
        "moving": nbt_1710.get("moving", False),
        "progress": nbt_1710.get("progress", 0.0),
    }


def convert_frame_actuator_nbt(nbt_1710: Dict) -> Dict:
    """Konwertuje NBT FrameActuator z 1.7.10 do 1.18.2+"""
    return {
        "rot": nbt_1710.get("rot", 0),
        "extended": nbt_1710.get("extended", False),
        "moving": nbt_1710.get("moving", False),
        "progress": nbt_1710.get("progress", 0.0),
    }


# =============================================================================
# Tests and Demonstrations
# =============================================================================

def test_frame():
    """Test Frame block"""
    print("=== Test Frame ===")

    frame = Frame(position=(0, 0, 0))

    # Default - wszystkie polaczenia aktywne
    assert frame.connection_mask == 0b111111
    assert frame.is_connected(Direction.UP) == True
    assert frame.is_connected(Direction.NORTH) == True

    # Wylacz polaczenie
    frame.set_connected(Direction.UP, False)
    assert frame.is_connected(Direction.UP) == False

    # Toggle
    frame.toggle_connection(Direction.UP)
    assert frame.is_connected(Direction.UP) == True

    # Lista polaczen
    dirs = frame.get_connected_directions()
    print(f"Connected directions: {[d.name for d in dirs]}")
    assert len(dirs) == 6

    print("Frame: OK")
    print()


def test_frame_motor():
    """Test Frame Motor"""
    print("=== Test Frame Motor ===")

    motor = FrameMotor(position=(0, 0, 0))
    motor.side = Direction.DOWN  # Zamontowany na dole bloku powyzej
    motor.charge = 800  # Wystarczajaco energii

    print(f"Motor side: {motor.side.name}")
    print(f"Move direction: {motor.move_direction.name}")
    print(f"Can work: {motor.can_work()}")

    # NBT
    nbt = motor.save_nbt()
    print(f"NBT: {nbt}")

    motor2 = FrameMotor()
    motor2.load_nbt(nbt)
    assert motor2.orientation == motor.orientation

    print("Frame Motor: OK")
    print()


def test_frame_actuator():
    """Test Frame Actuator"""
    print("=== Test Frame Actuator ===")

    actuator = FrameActuator(position=(0, 0, 0))
    actuator.side = Direction.DOWN
    actuator.charge = 800

    print(f"Actuator side: {actuator.side.name}")
    print(f"Push direction: {actuator.push_direction.name}")
    print(f"Pull direction: {actuator.pull_direction.name}")
    print(f"Is extended: {actuator.is_extended}")

    # NBT
    nbt = actuator.save_nbt()
    print(f"NBT: {nbt}")

    print("Frame Actuator: OK")
    print()


def test_frame_world():
    """Test Frame World"""
    print("=== Test Frame World ===")

    world = FrameWorld()

    # Tworzymy linie ramek
    # [Motor] [Frame] [Frame] [Frame]
    #   (0,0,0)  (1,0,0)  (2,0,0)  (3,0,0)

    motor = FrameMotor(position=(0, 0, 0))
    motor.side = Direction.WEST  # Mounted on west side, pushes east
    motor.charge = 1000
    world.add_block((0, 0, 0), motor)

    for i in range(1, 4):
        frame = Frame(position=(i, 0, 0))
        # Polaczenia tylko wschod-zachod
        frame.connection_mask = (1 << Direction.WEST.value) | (1 << Direction.EAST.value)
        world.add_block((i, 0, 0), frame)

    print(f"World has {len(world.blocks)} blocks")
    print(f"World has {len(world.motors)} motors")

    # Sprawdz bloki do przesuniecia
    blocks_to_move = motor.get_blocks_to_move(world)
    print(f"Blocks to move: {blocks_to_move}")
    assert len(blocks_to_move) == 3

    # Symuluj ruch
    motor.is_powered = True
    for tick in range(25):
        world.tick()

    print(f"After 25 ticks:")
    print(f"  Motor is_moving: {motor.is_moving}")
    for pos, block in world.blocks.items():
        print(f"  Block at {pos}: {type(block).__name__}")

    print("Frame World: OK")
    print()


def test_nbt_conversion():
    """Test konwersji NBT"""
    print("=== Test NBT Conversion ===")

    motor_nbt_1710 = {
        "rot": 5,
        "moving": True,
        "progress": 0.5,
    }

    motor_nbt_1182 = convert_frame_motor_nbt(motor_nbt_1710)
    print(f"1.7.10 Motor NBT: {motor_nbt_1710}")
    print(f"1.18.2 Motor NBT: {motor_nbt_1182}")

    actuator_nbt_1710 = {
        "rot": 3,
        "extended": True,
        "moving": False,
        "progress": 0.0,
    }

    actuator_nbt_1182 = convert_frame_actuator_nbt(actuator_nbt_1710)
    print(f"1.7.10 Actuator NBT: {actuator_nbt_1710}")
    print(f"1.18.2 Actuator NBT: {actuator_nbt_1182}")

    print("NBT Conversion: OK")
    print()


def demo_frame_structure():
    """Demonstracja struktury ramek"""
    print("=== Demo: Frame Structure ===")
    print("Tworzymy strukture ramek w ksztalcie L")
    print()

    world = FrameWorld()

    # L-ksztaltna struktura:
    # [1][2][3]
    # [4]
    # [5]

    positions = [
        (0, 0, 0),  # 1
        (1, 0, 0),  # 2
        (2, 0, 0),  # 3
        (0, 0, 1),  # 4
        (0, 0, 2),  # 5
    ]

    for i, pos in enumerate(positions):
        frame = Frame(position=pos)
        # Wszystkie polaczenia aktywne
        world.add_block(pos, frame)
        print(f"Frame {i+1} at {pos}")

    # Dodajemy motor
    motor = FrameMotor(position=(-1, 0, 0))
    motor.side = Direction.WEST
    motor.charge = 1000
    world.add_block((-1, 0, 0), motor)
    print(f"Motor at {motor.position}, pushing {motor.move_direction.name}")

    # Sprawdz co zostanie przesuniete
    blocks = motor.get_blocks_to_move(world)
    print(f"\nBlocks that would be moved: {len(blocks)}")
    for pos in sorted(blocks):
        print(f"  {pos}")

    # Symuluj przesuniecie
    print("\nSimulating movement...")
    world.move_blocks(blocks, motor.move_direction)

    print("New positions:")
    for pos in sorted(world.blocks.keys()):
        block = world.blocks[pos]
        print(f"  {type(block).__name__} at {pos}")

    print()


if __name__ == "__main__":
    test_frame()
    test_frame_motor()
    test_frame_actuator()
    test_frame_world()
    test_nbt_conversion()
    demo_frame_structure()
