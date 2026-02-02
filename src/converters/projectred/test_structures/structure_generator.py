"""
ProjectRed Test Structure Generator

Generator struktur testowych dla moda ProjectRed.
Tworzy struktury do testowania konwersji oraz testów integracyjnych
na headless serwerze.

Typy struktur:
1. UNIT - pojedynczy blok/BE do testowania konwersji
2. INTEGRATION - układ PR <-> vanilla redstone z command blockiem

Format integracyjny:
  [Input: lever/button] -> [PR: bramki/przewody] -> [Output: redstone -> command block]

Command block wykonuje /say <test_name> co pozwala na automatyczne testowanie.
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import os


class StructureType(Enum):
    """Typ struktury testowej"""
    UNIT = "unit"                    # Test jednostkowy jednego bloku
    INTEGRATION = "integration"       # Test integracyjny PR <-> vanilla
    SHOWCASE = "showcase"            # Prezentacja wszystkich wariantów


@dataclass
class BlockDefinition:
    """Definicja bloku w strukturze"""
    x: int
    y: int
    z: int
    block_id: str                     # ID bloku (1.7.10 format)
    metadata: int = 0
    nbt: Optional[Dict[str, Any]] = None
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "pos": [self.x, self.y, self.z],
            "block_id": self.block_id,
            "metadata": self.metadata
        }
        if self.nbt:
            result["nbt"] = self.nbt
        if self.description:
            result["description"] = self.description
        return result


@dataclass
class MultipartDefinition:
    """Definicja części multipart (bramki, przewody)"""
    x: int
    y: int
    z: int
    part_type: str                    # np. pr_sgate, pr_redwire
    nbt: Dict[str, Any]
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pos": [self.x, self.y, self.z],
            "part_type": self.part_type,
            "nbt": self.nbt,
            "description": self.description
        }


@dataclass
class CommandBlockDef:
    """Definicja command blocka do testów"""
    x: int
    y: int
    z: int
    command: str
    auto: bool = False                # Auto-trigger
    conditional: bool = False
    facing: str = "up"                # up, down, north, south, east, west

    def to_block(self) -> BlockDefinition:
        """Konwertuje na BlockDefinition"""
        # Command block metadata w 1.7.10:
        # 0=down, 1=up, 2=north, 3=south, 4=west, 5=east
        facing_map = {
            "down": 0, "up": 1, "north": 2,
            "south": 3, "west": 4, "east": 5
        }
        meta = facing_map.get(self.facing, 1)

        nbt = {
            "Command": self.command,
            "auto": 1 if self.auto else 0,
            "conditionMet": 0,
            "powered": 0,
            "id": "Control",          # 1.7.10 TE ID
            "SuccessCount": 0
        }

        return BlockDefinition(
            x=self.x, y=self.y, z=self.z,
            block_id="minecraft:command_block",
            metadata=meta,
            nbt=nbt,
            description=f"Command: {self.command}"
        )


@dataclass
class TestStructure:
    """Struktura testowa"""
    name: str
    structure_type: StructureType
    description: str
    blocks: List[BlockDefinition] = field(default_factory=list)
    multiparts: List[MultipartDefinition] = field(default_factory=list)

    # Dla testów integracyjnych
    input_description: str = ""       # Opis inputu (np. "lever na pozycji X")
    expected_output: str = ""         # Oczekiwany output (tekst command blocka)
    test_steps: List[str] = field(default_factory=list)

    # Bounding box
    size: Tuple[int, int, int] = (1, 1, 1)

    def add_block(self, block: BlockDefinition):
        self.blocks.append(block)

    def add_multipart(self, mp: MultipartDefinition):
        self.multiparts.append(mp)

    def add_command_block(self, cmd: CommandBlockDef):
        self.blocks.append(cmd.to_block())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.structure_type.value,
            "description": self.description,
            "size": list(self.size),
            "blocks": [b.to_dict() for b in self.blocks],
            "multiparts": [m.to_dict() for m in self.multiparts],
            "test_info": {
                "input_description": self.input_description,
                "expected_output": self.expected_output,
                "test_steps": self.test_steps
            }
        }

    def save_json(self, path: str):
        """Zapisuje strukturę do pliku JSON"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


class ProjectRedTestStructureGenerator:
    """
    Generator struktur testowych dla ProjectRed.
    """

    # Kolory Minecraft (dla przewodów, lamp)
    COLORS = [
        "white", "orange", "magenta", "light_blue",
        "yellow", "lime", "pink", "gray",
        "light_gray", "cyan", "purple", "blue",
        "brown", "green", "red", "black"
    ]

    # Typy bramek ProjectRed
    GATE_TYPES = {
        0: ("or", "OR Gate"),
        1: ("nor", "NOR Gate"),
        2: ("not", "NOT Gate"),
        3: ("and", "AND Gate"),
        4: ("nand", "NAND Gate"),
        5: ("xor", "XOR Gate"),
        6: ("xnor", "XNOR Gate"),
        7: ("buffer", "Buffer Gate"),
        8: ("multiplexer", "Multiplexer"),
        9: ("pulse", "Pulse Former"),
        10: ("repeater", "Repeater"),
        11: ("randomizer", "Randomizer"),
        12: ("sr_latch", "SR Latch"),
        13: ("toggle_latch", "Toggle Latch"),
        14: ("transparent_latch", "Transparent Latch"),
        15: ("timer", "Timer"),
        16: ("counter", "Counter"),
        17: ("sequencer", "Sequencer"),
        18: ("state_cell", "State Cell"),
        19: ("synchronizer", "Synchronizer"),
        20: ("bus_transceiver", "Bus Transceiver"),
        26: ("comparator", "Comparator"),
    }

    def __init__(self):
        self.structures: List[TestStructure] = []

    # =========================================================================
    # UNIT TESTS - Pojedyncze bloki
    # =========================================================================

    def create_battery_box_test(self, storage: int = 4000) -> TestStructure:
        """Test jednostkowy BatteryBox"""
        structure = TestStructure(
            name="unit_battery_box",
            structure_type=StructureType.UNIT,
            description=f"BatteryBox z {storage} jednostek energii",
            size=(1, 1, 1)
        )

        structure.add_block(BlockDefinition(
            x=0, y=0, z=0,
            block_id="ProjRed|Expansion:projectred.expansion.machine2",
            metadata=5,  # BatteryBox
            nbt={
                "storage": storage,
                "rot": 0,
                "items": []
            },
            description="BatteryBox"
        ))

        return structure

    def create_electrotine_generator_test(self) -> TestStructure:
        """Test jednostkowy ElectrotineGenerator"""
        structure = TestStructure(
            name="unit_electrotine_generator",
            structure_type=StructureType.UNIT,
            description="ElectrotineGenerator z paliwem",
            size=(1, 1, 1)
        )

        structure.add_block(BlockDefinition(
            x=0, y=0, z=0,
            block_id="ProjRed|Expansion:projectred.expansion.machine1",
            metadata=1,
            nbt={
                "storage": 1000,
                "btime": 200,
                "items": [
                    {"Slot": 0, "id": "ProjRed|Core:projectred.core.part",
                     "Damage": 56, "Count": 32}  # Electrotine
                ]
            },
            description="ElectrotineGenerator"
        ))

        return structure

    def create_project_bench_test(self) -> TestStructure:
        """Test jednostkowy ProjectBench"""
        structure = TestStructure(
            name="unit_project_bench",
            structure_type=StructureType.UNIT,
            description="ProjectBench z zapisaną recepturą",
            size=(1, 1, 1)
        )

        structure.add_block(BlockDefinition(
            x=0, y=0, z=0,
            block_id="ProjRed|Expansion:projectred.expansion.machine2",
            metadata=10,  # ProjectBench
            nbt={
                "rot": 0,
                "items": [
                    {"Slot": 0, "id": "minecraft:iron_ingot", "Count": 1},
                    {"Slot": 1, "id": "minecraft:iron_ingot", "Count": 1},
                    {"Slot": 2, "id": "minecraft:iron_ingot", "Count": 1},
                ],
                "planslot": 0
            },
            description="ProjectBench"
        ))

        return structure

    def create_block_breaker_test(self) -> TestStructure:
        """Test jednostkowy BlockBreaker"""
        structure = TestStructure(
            name="unit_block_breaker",
            structure_type=StructureType.UNIT,
            description="BlockBreaker skierowany na north",
            size=(1, 1, 1)
        )

        structure.add_block(BlockDefinition(
            x=0, y=0, z=0,
            block_id="ProjRed|Expansion:projectred.expansion.machine2",
            metadata=0,  # BlockBreaker
            nbt={
                "rot": 2,  # Facing north
            },
            description="BlockBreaker"
        ))

        return structure

    def create_fire_starter_test(self) -> TestStructure:
        """Test jednostkowy FireStarter"""
        structure = TestStructure(
            name="unit_fire_starter",
            structure_type=StructureType.UNIT,
            description="FireStarter",
            size=(1, 1, 1)
        )

        structure.add_block(BlockDefinition(
            x=0, y=0, z=0,
            block_id="ProjRed|Expansion:projectred.expansion.machine2",
            metadata=4,  # FireStarter
            nbt={"rot": 0},
            description="FireStarter"
        ))

        return structure

    def create_frame_motor_test(self) -> TestStructure:
        """Test jednostkowy FrameMotor"""
        structure = TestStructure(
            name="unit_frame_motor",
            structure_type=StructureType.UNIT,
            description="FrameMotor naładowany",
            size=(1, 1, 1)
        )

        structure.add_block(BlockDefinition(
            x=0, y=0, z=0,
            block_id="ProjRed|Expansion:projectred.expansion.machine2",
            metadata=8,  # FrameMotor
            nbt={
                "ch": True,   # isCharged
                "pow": False  # isPowered
            },
            description="FrameMotor"
        ))

        return structure

    def create_lamp_test(self, color: int = 0, inverted: bool = False) -> TestStructure:
        """Test jednostkowy lampy"""
        color_name = self.COLORS[color] if 0 <= color < 16 else "white"
        inv_str = "inverted" if inverted else "normal"

        structure = TestStructure(
            name=f"unit_lamp_{color_name}_{inv_str}",
            structure_type=StructureType.UNIT,
            description=f"Lampa {color_name} ({inv_str})",
            size=(1, 1, 1)
        )

        # Lampy mają meta = color, inverted to osobny blok
        block_suffix = "_inverted" if inverted else ""

        structure.add_block(BlockDefinition(
            x=0, y=0, z=0,
            block_id=f"ProjRed|Illumination:projectred.illumination.lamp{block_suffix}",
            metadata=color,
            nbt={
                "inv": inverted,
                "pow": False
            },
            description=f"Lamp {color_name}"
        ))

        return structure

    def create_gate_test(self, gate_id: int) -> TestStructure:
        """Test jednostkowy bramki logicznej"""
        gate_info = self.GATE_TYPES.get(gate_id, (f"unknown_{gate_id}", f"Unknown Gate {gate_id}"))
        gate_name, gate_desc = gate_info

        structure = TestStructure(
            name=f"unit_gate_{gate_name}",
            structure_type=StructureType.UNIT,
            description=f"Bramka: {gate_desc}",
            size=(1, 1, 1)
        )

        # Bramki są multipart
        structure.add_multipart(MultipartDefinition(
            x=0, y=0, z=0,
            part_type="pr_sgate",
            nbt={
                "orient": 0x01,      # side=0 (down), rotation=1 (east)
                "subID": gate_id,
                "shape": 0,
                "connMap": 0xF,
                "nolegacy": True,
                "schedTime": 0,
                "state": 0
            },
            description=gate_desc
        ))

        return structure

    def create_wire_test(self, wire_type: str, color: int = -1) -> TestStructure:
        """Test jednostkowy przewodu"""
        if color >= 0 and color < 16:
            color_name = self.COLORS[color]
            name = f"unit_wire_{wire_type}_{color_name}"
            desc = f"Przewód {wire_type} ({color_name})"
        else:
            name = f"unit_wire_{wire_type}"
            desc = f"Przewód {wire_type}"

        structure = TestStructure(
            name=name,
            structure_type=StructureType.UNIT,
            description=desc,
            size=(1, 1, 1)
        )

        nbt = {"signal": 0}
        if wire_type == "bundled":
            nbt["signal"] = [0] * 16
        if color >= 0:
            nbt["colour"] = color

        structure.add_multipart(MultipartDefinition(
            x=0, y=0, z=0,
            part_type=f"pr_{wire_type}",
            nbt=nbt,
            description=desc
        ))

        return structure

    def create_ore_test(self, ore_meta: int) -> TestStructure:
        """Test jednostkowy rudy"""
        ore_names = {
            0: "ruby", 1: "sapphire", 2: "peridot",
            3: "copper", 4: "tin", 5: "silver", 6: "electrotine"
        }
        ore_name = ore_names.get(ore_meta, f"unknown_{ore_meta}")

        structure = TestStructure(
            name=f"unit_ore_{ore_name}",
            structure_type=StructureType.UNIT,
            description=f"Ruda: {ore_name}",
            size=(1, 1, 1)
        )

        structure.add_block(BlockDefinition(
            x=0, y=0, z=0,
            block_id="ProjRed|Exploration:projectred.exploration.ore",
            metadata=ore_meta,
            description=f"Ore {ore_name}"
        ))

        return structure

    def create_stone_test(self, stone_meta: int) -> TestStructure:
        """Test jednostkowy bloku dekoracyjnego"""
        stone_names = {
            0: "marble", 1: "marble_brick", 2: "basalt",
            3: "basalt_cobble", 4: "basalt_brick",
            5: "ruby_block", 6: "sapphire_block", 7: "peridot_block",
            8: "copper_block", 9: "tin_block", 10: "silver_block",
            11: "electrotine_block"
        }
        stone_name = stone_names.get(stone_meta, f"unknown_{stone_meta}")

        structure = TestStructure(
            name=f"unit_stone_{stone_name}",
            structure_type=StructureType.UNIT,
            description=f"Blok: {stone_name}",
            size=(1, 1, 1)
        )

        structure.add_block(BlockDefinition(
            x=0, y=0, z=0,
            block_id="ProjRed|Exploration:projectred.exploration.stone",
            metadata=stone_meta,
            description=f"Stone {stone_name}"
        ))

        return structure

    def create_ic_workbench_test(self) -> TestStructure:
        """Test jednostkowy IC Workbench"""
        structure = TestStructure(
            name="unit_ic_workbench",
            structure_type=StructureType.UNIT,
            description="IC Workbench (Fabrication)",
            size=(1, 1, 1)
        )

        structure.add_block(BlockDefinition(
            x=0, y=0, z=0,
            block_id="ProjRed|Fabrication:projectred.fabrication.icblock",
            metadata=0,  # ICWorkbench
            nbt={},
            description="IC Workbench"
        ))

        return structure

    # =========================================================================
    # INTEGRATION TESTS - PR <-> Vanilla Redstone
    # =========================================================================

    def create_integration_and_gate(self) -> TestStructure:
        """
        Test integracyjny: AND Gate

        Układ:
        [Lever1] -> [Redstone] -> [AND Gate] -> [Redstone] -> [Command Block]
        [Lever2] -> [Redstone] /

        Oczekiwane zachowanie:
        - Oba levery ON -> command block wykonuje /say TEST_AND_GATE_OK
        """
        structure = TestStructure(
            name="integration_and_gate",
            structure_type=StructureType.INTEGRATION,
            description="Test AND Gate z dwoma leverami",
            size=(7, 2, 3),
            input_description="Dwa levery: (0,1,0) i (0,1,2)",
            expected_output="TEST_AND_GATE_OK",
            test_steps=[
                "1. Aktywuj lever na (0,1,0)",
                "2. Aktywuj lever na (0,1,2)",
                "3. Sprawdź czy command block wypisał TEST_AND_GATE_OK"
            ]
        )

        # Podstawa - kamienne bloki
        for x in range(7):
            for z in range(3):
                structure.add_block(BlockDefinition(
                    x=x, y=0, z=z,
                    block_id="minecraft:stone",
                    metadata=0
                ))

        # Lever 1 (input A)
        structure.add_block(BlockDefinition(
            x=0, y=1, z=0,
            block_id="minecraft:lever",
            metadata=5,  # Facing east on floor
            description="Input A"
        ))

        # Lever 2 (input B)
        structure.add_block(BlockDefinition(
            x=0, y=1, z=2,
            block_id="minecraft:lever",
            metadata=5,
            description="Input B"
        ))

        # Redstone dust od leverów do bramki
        structure.add_block(BlockDefinition(
            x=1, y=1, z=0,
            block_id="minecraft:redstone_wire",
            metadata=0
        ))
        structure.add_block(BlockDefinition(
            x=1, y=1, z=2,
            block_id="minecraft:redstone_wire",
            metadata=0
        ))
        structure.add_block(BlockDefinition(
            x=2, y=1, z=0,
            block_id="minecraft:redstone_wire",
            metadata=0
        ))
        structure.add_block(BlockDefinition(
            x=2, y=1, z=2,
            block_id="minecraft:redstone_wire",
            metadata=0
        ))

        # AND Gate (na środku)
        structure.add_multipart(MultipartDefinition(
            x=3, y=1, z=1,
            part_type="pr_sgate",
            nbt={
                "orient": 0x01,      # side=0 (down), rotation=1 (east)
                "subID": 3,          # AND gate
                "shape": 0,
                "connMap": 0xF,
                "nolegacy": True,
                "schedTime": 0,
                "state": 0
            },
            description="AND Gate"
        ))

        # Przewody PR od inputów do bramki
        structure.add_multipart(MultipartDefinition(
            x=3, y=1, z=0,
            part_type="pr_redwire",
            nbt={"signal": 0},
            description="Wire to AND input A"
        ))
        structure.add_multipart(MultipartDefinition(
            x=3, y=1, z=2,
            part_type="pr_redwire",
            nbt={"signal": 0},
            description="Wire to AND input B"
        ))

        # Przewód PR od wyjścia bramki
        structure.add_multipart(MultipartDefinition(
            x=4, y=1, z=1,
            part_type="pr_redwire",
            nbt={"signal": 0},
            description="Wire from AND output"
        ))

        # Redstone dust do command blocka
        structure.add_block(BlockDefinition(
            x=5, y=1, z=1,
            block_id="minecraft:redstone_wire",
            metadata=0
        ))

        # Command block
        structure.add_command_block(CommandBlockDef(
            x=6, y=1, z=1,
            command="say TEST_AND_GATE_OK",
            facing="west"
        ))

        return structure

    def create_integration_or_gate(self) -> TestStructure:
        """Test integracyjny: OR Gate"""
        structure = TestStructure(
            name="integration_or_gate",
            structure_type=StructureType.INTEGRATION,
            description="Test OR Gate z dwoma leverami",
            size=(7, 2, 3),
            input_description="Dwa levery: (0,1,0) i (0,1,2)",
            expected_output="TEST_OR_GATE_OK",
            test_steps=[
                "1. Aktywuj jeden lever",
                "2. Sprawdź czy command block wypisał TEST_OR_GATE_OK"
            ]
        )

        # Podstawa
        for x in range(7):
            for z in range(3):
                structure.add_block(BlockDefinition(
                    x=x, y=0, z=z,
                    block_id="minecraft:stone",
                    metadata=0
                ))

        # Levery
        structure.add_block(BlockDefinition(
            x=0, y=1, z=0, block_id="minecraft:lever", metadata=5, description="Input A"
        ))
        structure.add_block(BlockDefinition(
            x=0, y=1, z=2, block_id="minecraft:lever", metadata=5, description="Input B"
        ))

        # Redstone do bramki
        for z in [0, 2]:
            structure.add_block(BlockDefinition(
                x=1, y=1, z=z, block_id="minecraft:redstone_wire", metadata=0
            ))
            structure.add_block(BlockDefinition(
                x=2, y=1, z=z, block_id="minecraft:redstone_wire", metadata=0
            ))

        # OR Gate
        structure.add_multipart(MultipartDefinition(
            x=3, y=1, z=1,
            part_type="pr_sgate",
            nbt={
                "orient": 0x01, "subID": 0,  # OR gate
                "shape": 0, "connMap": 0xF, "nolegacy": True, "schedTime": 0, "state": 0
            },
            description="OR Gate"
        ))

        # Przewody PR
        structure.add_multipart(MultipartDefinition(
            x=3, y=1, z=0, part_type="pr_redwire", nbt={"signal": 0}
        ))
        structure.add_multipart(MultipartDefinition(
            x=3, y=1, z=2, part_type="pr_redwire", nbt={"signal": 0}
        ))
        structure.add_multipart(MultipartDefinition(
            x=4, y=1, z=1, part_type="pr_redwire", nbt={"signal": 0}
        ))

        # Redstone do command blocka
        structure.add_block(BlockDefinition(
            x=5, y=1, z=1, block_id="minecraft:redstone_wire", metadata=0
        ))

        # Command block
        structure.add_command_block(CommandBlockDef(
            x=6, y=1, z=1, command="say TEST_OR_GATE_OK", facing="west"
        ))

        return structure

    def create_integration_not_gate(self) -> TestStructure:
        """Test integracyjny: NOT Gate (Inverter)"""
        structure = TestStructure(
            name="integration_not_gate",
            structure_type=StructureType.INTEGRATION,
            description="Test NOT Gate - output aktywny gdy input nieaktywny",
            size=(6, 2, 1),
            input_description="Lever na (0,1,0) - początkowo OFF",
            expected_output="TEST_NOT_GATE_OK (gdy lever OFF)",
            test_steps=[
                "1. Lever jest OFF -> command block powinien być aktywny",
                "2. Aktywuj lever -> command block powinien być nieaktywny"
            ]
        )

        # Podstawa
        for x in range(6):
            structure.add_block(BlockDefinition(
                x=x, y=0, z=0, block_id="minecraft:stone", metadata=0
            ))

        # Lever (OFF)
        structure.add_block(BlockDefinition(
            x=0, y=1, z=0, block_id="minecraft:lever", metadata=5, description="Input"
        ))

        # Redstone input
        structure.add_block(BlockDefinition(
            x=1, y=1, z=0, block_id="minecraft:redstone_wire", metadata=0
        ))

        # NOT Gate
        structure.add_multipart(MultipartDefinition(
            x=2, y=1, z=0,
            part_type="pr_sgate",
            nbt={
                "orient": 0x01, "subID": 2,  # NOT gate
                "shape": 0, "connMap": 0xF, "nolegacy": True, "schedTime": 0, "state": 0
            },
            description="NOT Gate"
        ))

        # Przewód PR i redstone output
        structure.add_multipart(MultipartDefinition(
            x=3, y=1, z=0, part_type="pr_redwire", nbt={"signal": 0}
        ))
        structure.add_block(BlockDefinition(
            x=4, y=1, z=0, block_id="minecraft:redstone_wire", metadata=0
        ))

        # Command block
        structure.add_command_block(CommandBlockDef(
            x=5, y=1, z=0, command="say TEST_NOT_GATE_OK", facing="west"
        ))

        return structure

    def create_integration_timer(self) -> TestStructure:
        """Test integracyjny: Timer Gate"""
        structure = TestStructure(
            name="integration_timer_gate",
            structure_type=StructureType.INTEGRATION,
            description="Test Timer Gate - pulsuje co określony czas",
            size=(5, 2, 1),
            input_description="Lever na (0,1,0) - aktywuje timer",
            expected_output="TEST_TIMER_OK (pulsuje)",
            test_steps=[
                "1. Aktywuj lever",
                "2. Timer zaczyna pulsować",
                "3. Command block wypisuje TEST_TIMER_OK przy każdym pulsie"
            ]
        )

        # Podstawa
        for x in range(5):
            structure.add_block(BlockDefinition(
                x=x, y=0, z=0, block_id="minecraft:stone", metadata=0
            ))

        # Lever
        structure.add_block(BlockDefinition(
            x=0, y=1, z=0, block_id="minecraft:lever", metadata=5, description="Timer Enable"
        ))

        # Timer Gate (pr_igate)
        structure.add_multipart(MultipartDefinition(
            x=1, y=1, z=0,
            part_type="pr_igate",  # Sequential gate
            nbt={
                "orient": 0x01, "subID": 15,  # Timer
                "shape": 0, "connMap": 0xF, "nolegacy": True,
                "schedTime": 0, "state": 0,
                "pointer_max": 20,  # Timer interval (ticks)
                "pointer_start": 0
            },
            description="Timer Gate"
        ))

        # Output
        structure.add_multipart(MultipartDefinition(
            x=2, y=1, z=0, part_type="pr_redwire", nbt={"signal": 0}
        ))
        structure.add_block(BlockDefinition(
            x=3, y=1, z=0, block_id="minecraft:redstone_wire", metadata=0
        ))

        # Command block
        structure.add_command_block(CommandBlockDef(
            x=4, y=1, z=0, command="say TEST_TIMER_OK", facing="west"
        ))

        return structure

    def create_integration_insulated_wire_signal(self) -> TestStructure:
        """Test integracyjny: Izolowane przewody z kolorami"""
        structure = TestStructure(
            name="integration_insulated_wires",
            structure_type=StructureType.INTEGRATION,
            description="Test izolowanych przewodów - 2 kolory nie interferują",
            size=(8, 2, 3),
            input_description="Lever czerwony (0,1,0), Lever niebieski (0,1,2)",
            expected_output="TEST_RED_WIRE_OK lub TEST_BLUE_WIRE_OK",
            test_steps=[
                "1. Aktywuj czerwony lever -> tylko czerwony command block",
                "2. Aktywuj niebieski lever -> tylko niebieski command block",
                "3. Przewody nie powinny się krzyżować"
            ]
        )

        # Podstawa
        for x in range(8):
            for z in range(3):
                structure.add_block(BlockDefinition(
                    x=x, y=0, z=z, block_id="minecraft:stone", metadata=0
                ))

        # Lever czerwony
        structure.add_block(BlockDefinition(
            x=0, y=1, z=0, block_id="minecraft:lever", metadata=5, description="Red Input"
        ))
        # Lever niebieski
        structure.add_block(BlockDefinition(
            x=0, y=1, z=2, block_id="minecraft:lever", metadata=5, description="Blue Input"
        ))

        # Redstone inputs
        structure.add_block(BlockDefinition(x=1, y=1, z=0, block_id="minecraft:redstone_wire", metadata=0))
        structure.add_block(BlockDefinition(x=1, y=1, z=2, block_id="minecraft:redstone_wire", metadata=0))

        # Izolowane przewody (krzyżują się w środku ale nie interferują)
        # Czerwony (kolor 14)
        for x in range(2, 6):
            structure.add_multipart(MultipartDefinition(
                x=x, y=1, z=0,
                part_type="pr_insulated",
                nbt={"signal": 0, "colour": 14},  # Red
                description="Red insulated wire"
            ))

        # Niebieski (kolor 11)
        for x in range(2, 6):
            structure.add_multipart(MultipartDefinition(
                x=x, y=1, z=2,
                part_type="pr_insulated",
                nbt={"signal": 0, "colour": 11},  # Blue
                description="Blue insulated wire"
            ))

        # Punkt krzyżowania (oba kolory przechodzą przez z=1)
        structure.add_multipart(MultipartDefinition(
            x=4, y=1, z=1,
            part_type="pr_insulated",
            nbt={"signal": 0, "colour": 14},  # Red przechodzi
            description="Red crossing"
        ))

        # Redstone outputs
        structure.add_block(BlockDefinition(x=6, y=1, z=0, block_id="minecraft:redstone_wire", metadata=0))
        structure.add_block(BlockDefinition(x=6, y=1, z=2, block_id="minecraft:redstone_wire", metadata=0))

        # Command blocks
        structure.add_command_block(CommandBlockDef(
            x=7, y=1, z=0, command="say TEST_RED_WIRE_OK", facing="west"
        ))
        structure.add_command_block(CommandBlockDef(
            x=7, y=1, z=2, command="say TEST_BLUE_WIRE_OK", facing="west"
        ))

        return structure

    def create_integration_bundled_cable(self) -> TestStructure:
        """Test integracyjny: Bundled Cable z wieloma kanałami"""
        structure = TestStructure(
            name="integration_bundled_cable",
            structure_type=StructureType.INTEGRATION,
            description="Test Bundled Cable - wiele sygnałów w jednym kablu",
            size=(8, 2, 1),
            input_description="Lever na (0,1,0)",
            expected_output="TEST_BUNDLED_OK",
            test_steps=[
                "1. Aktywuj lever",
                "2. Sygnał przechodzi przez bundled cable",
                "3. Command block wypisuje TEST_BUNDLED_OK"
            ]
        )

        # Podstawa
        for x in range(8):
            structure.add_block(BlockDefinition(
                x=x, y=0, z=0, block_id="minecraft:stone", metadata=0
            ))

        # Lever
        structure.add_block(BlockDefinition(
            x=0, y=1, z=0, block_id="minecraft:lever", metadata=5
        ))

        # Redstone input
        structure.add_block(BlockDefinition(x=1, y=1, z=0, block_id="minecraft:redstone_wire", metadata=0))

        # Izolowany przewód (kolor 0 - white) do bundled
        structure.add_multipart(MultipartDefinition(
            x=2, y=1, z=0,
            part_type="pr_insulated",
            nbt={"signal": 0, "colour": 0},
            description="White insulated to bundled"
        ))

        # Bundled cable
        for x in range(3, 6):
            structure.add_multipart(MultipartDefinition(
                x=x, y=1, z=0,
                part_type="pr_bundled",
                nbt={"signal": [0]*16, "colour": -1},  # Neutral bundled
                description="Bundled cable"
            ))

        # Izolowany przewód z bundled
        structure.add_multipart(MultipartDefinition(
            x=6, y=1, z=0,
            part_type="pr_insulated",
            nbt={"signal": 0, "colour": 0},
            description="White insulated from bundled"
        ))

        # Redstone output
        structure.add_block(BlockDefinition(x=7, y=1, z=0, block_id="minecraft:redstone_wire", metadata=0))

        # Command block (pod spodem, z=1)
        structure.add_block(BlockDefinition(
            x=7, y=0, z=0, block_id="minecraft:stone", metadata=0
        ))
        structure.add_command_block(CommandBlockDef(
            x=7, y=1, z=0, command="say TEST_BUNDLED_OK", facing="down"
        ))

        return structure

    def create_integration_lamp_toggle(self) -> TestStructure:
        """Test integracyjny: Lampa sterowana przez bramkę"""
        structure = TestStructure(
            name="integration_lamp_toggle",
            structure_type=StructureType.INTEGRATION,
            description="Test Toggle Latch + Lampa",
            size=(6, 2, 1),
            input_description="Button na (0,1,0) - przełącza stan",
            expected_output="TEST_LAMP_ON / TEST_LAMP_OFF",
            test_steps=[
                "1. Naciśnij button - lampa ON, command block TEST_LAMP_ON",
                "2. Naciśnij ponownie - lampa OFF"
            ]
        )

        # Podstawa
        for x in range(6):
            structure.add_block(BlockDefinition(
                x=x, y=0, z=0, block_id="minecraft:stone", metadata=0
            ))

        # Button
        structure.add_block(BlockDefinition(
            x=0, y=1, z=0,
            block_id="minecraft:stone_button",
            metadata=5,  # Facing east
            description="Toggle Button"
        ))

        # Redstone
        structure.add_block(BlockDefinition(x=1, y=1, z=0, block_id="minecraft:redstone_wire", metadata=0))

        # Toggle Latch
        structure.add_multipart(MultipartDefinition(
            x=2, y=1, z=0,
            part_type="pr_sgate",
            nbt={
                "orient": 0x01, "subID": 13,  # Toggle Latch
                "shape": 0, "connMap": 0xF, "nolegacy": True, "schedTime": 0, "state": 0
            },
            description="Toggle Latch"
        ))

        # Przewód PR
        structure.add_multipart(MultipartDefinition(
            x=3, y=1, z=0, part_type="pr_redwire", nbt={"signal": 0}
        ))

        # Lampa
        structure.add_block(BlockDefinition(
            x=4, y=1, z=0,
            block_id="ProjRed|Illumination:projectred.illumination.lamp",
            metadata=14,  # Red lamp
            nbt={"inv": False, "pow": False},
            description="Red Lamp"
        ))

        # Redstone output do command blocka
        structure.add_block(BlockDefinition(x=5, y=0, z=0, block_id="minecraft:stone", metadata=0))
        structure.add_command_block(CommandBlockDef(
            x=5, y=1, z=0, command="say TEST_LAMP_ON", facing="west"
        ))

        return structure

    def create_integration_comparator_test(self) -> TestStructure:
        """Test integracyjny: Comparator Gate"""
        structure = TestStructure(
            name="integration_comparator",
            structure_type=StructureType.INTEGRATION,
            description="Test Comparator Gate - porównuje siłę sygnału",
            size=(8, 2, 3),
            input_description="Lever silny (0,1,0), Lever słaby przez repeater (0,1,2)",
            expected_output="TEST_COMPARATOR_OK gdy A > B",
            test_steps=[
                "1. Aktywuj lever A (silny sygnał)",
                "2. Aktywuj lever B (słabszy przez repeater)",
                "3. Comparator przepuszcza sygnał gdy A > B"
            ]
        )

        # Podstawa
        for x in range(8):
            for z in range(3):
                structure.add_block(BlockDefinition(
                    x=x, y=0, z=z, block_id="minecraft:stone", metadata=0
                ))

        # Lever A (silny)
        structure.add_block(BlockDefinition(
            x=0, y=1, z=0, block_id="minecraft:lever", metadata=5, description="Input A (strong)"
        ))

        # Lever B (słaby)
        structure.add_block(BlockDefinition(
            x=0, y=1, z=2, block_id="minecraft:lever", metadata=5, description="Input B (weak)"
        ))

        # Redstone paths
        for z in [0, 2]:
            structure.add_block(BlockDefinition(x=1, y=1, z=z, block_id="minecraft:redstone_wire", metadata=0))
            structure.add_block(BlockDefinition(x=2, y=1, z=z, block_id="minecraft:redstone_wire", metadata=0))

        # Repeater na ścieżce B (osłabia sygnał przez delay)
        # W 1.7.10: repeater metadata = direction * 4 + delay
        structure.add_block(BlockDefinition(
            x=3, y=1, z=2,
            block_id="minecraft:unpowered_repeater",
            metadata=1 + 12,  # East facing, max delay (osłabia sygnał efektywnie)
            description="Signal weakener"
        ))

        # Przewody PR do comparatora
        structure.add_multipart(MultipartDefinition(
            x=3, y=1, z=0, part_type="pr_redwire", nbt={"signal": 0}
        ))

        # Comparator Gate
        structure.add_multipart(MultipartDefinition(
            x=4, y=1, z=1,
            part_type="pr_sgate",
            nbt={
                "orient": 0x01, "subID": 26,  # Comparator
                "shape": 0, "connMap": 0xF, "nolegacy": True, "schedTime": 0, "state": 0
            },
            description="Comparator Gate"
        ))

        # Połączenia
        structure.add_multipart(MultipartDefinition(
            x=4, y=1, z=0, part_type="pr_redwire", nbt={"signal": 0}
        ))
        structure.add_multipart(MultipartDefinition(
            x=4, y=1, z=2, part_type="pr_redwire", nbt={"signal": 0}
        ))

        # Output
        structure.add_multipart(MultipartDefinition(
            x=5, y=1, z=1, part_type="pr_redwire", nbt={"signal": 0}
        ))
        structure.add_block(BlockDefinition(x=6, y=1, z=1, block_id="minecraft:redstone_wire", metadata=0))

        # Command block
        structure.add_command_block(CommandBlockDef(
            x=7, y=1, z=1, command="say TEST_COMPARATOR_OK", facing="west"
        ))

        return structure

    # =========================================================================
    # GENERATOR
    # =========================================================================

    def generate_all_unit_tests(self) -> List[TestStructure]:
        """Generuje wszystkie testy jednostkowe"""
        structures = []

        # Maszyny Expansion
        structures.append(self.create_battery_box_test())
        structures.append(self.create_battery_box_test(storage=0))  # Empty
        structures.append(self.create_battery_box_test(storage=8000))  # Full
        structures.append(self.create_electrotine_generator_test())
        structures.append(self.create_project_bench_test())
        structures.append(self.create_block_breaker_test())
        structures.append(self.create_fire_starter_test())
        structures.append(self.create_frame_motor_test())

        # Lampy (kilka kolorów)
        for color in [0, 7, 14, 15]:  # white, gray, red, black
            structures.append(self.create_lamp_test(color, inverted=False))
            structures.append(self.create_lamp_test(color, inverted=True))

        # Bramki (wszystkie typy)
        for gate_id in self.GATE_TYPES.keys():
            structures.append(self.create_gate_test(gate_id))

        # Przewody
        structures.append(self.create_wire_test("redwire"))
        for color in [0, 7, 14]:  # white, gray, red
            structures.append(self.create_wire_test("insulated", color))
        structures.append(self.create_wire_test("bundled", -1))
        structures.append(self.create_wire_test("bundled", 0))

        # Rudy (wszystkie)
        for ore_meta in range(7):
            structures.append(self.create_ore_test(ore_meta))

        # Bloki dekoracyjne
        for stone_meta in range(12):
            structures.append(self.create_stone_test(stone_meta))

        # IC Workbench
        structures.append(self.create_ic_workbench_test())

        return structures

    def generate_all_integration_tests(self) -> List[TestStructure]:
        """Generuje wszystkie testy integracyjne"""
        return [
            self.create_integration_and_gate(),
            self.create_integration_or_gate(),
            self.create_integration_not_gate(),
            self.create_integration_timer(),
            self.create_integration_insulated_wire_signal(),
            self.create_integration_bundled_cable(),
            self.create_integration_lamp_toggle(),
            self.create_integration_comparator_test(),
        ]

    def generate_all(self) -> List[TestStructure]:
        """Generuje wszystkie struktury testowe"""
        return self.generate_all_unit_tests() + self.generate_all_integration_tests()

    def save_all(self, output_dir: str):
        """Zapisuje wszystkie struktury do plików JSON"""
        os.makedirs(output_dir, exist_ok=True)

        unit_dir = os.path.join(output_dir, "unit")
        integration_dir = os.path.join(output_dir, "integration")
        os.makedirs(unit_dir, exist_ok=True)
        os.makedirs(integration_dir, exist_ok=True)

        all_structures = self.generate_all()

        for structure in all_structures:
            if structure.structure_type == StructureType.UNIT:
                path = os.path.join(unit_dir, f"{structure.name}.json")
            else:
                path = os.path.join(integration_dir, f"{structure.name}.json")

            structure.save_json(path)
            print(f"Saved: {path}")

        # Zapisz indeks
        index = {
            "unit_tests": [s.name for s in all_structures if s.structure_type == StructureType.UNIT],
            "integration_tests": [s.name for s in all_structures if s.structure_type == StructureType.INTEGRATION],
            "total_count": len(all_structures)
        }

        index_path = os.path.join(output_dir, "index.json")
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        print(f"\nIndex saved: {index_path}")
        print(f"Total structures: {len(all_structures)}")


def main():
    """Generuje wszystkie struktury testowe"""
    generator = ProjectRedTestStructureGenerator()

    output_dir = os.path.join(os.path.dirname(__file__), "generated")
    generator.save_all(output_dir)

    print("\n" + "=" * 60)
    print("PROJECTRED TEST STRUCTURES GENERATED")
    print("=" * 60)

    # Podsumowanie
    all_structures = generator.generate_all()
    unit_count = len([s for s in all_structures if s.structure_type == StructureType.UNIT])
    integration_count = len([s for s in all_structures if s.structure_type == StructureType.INTEGRATION])

    print(f"\nUnit tests: {unit_count}")
    print(f"Integration tests: {integration_count}")
    print(f"Total: {len(all_structures)}")

    print("\nIntegration tests for headless server:")
    for s in all_structures:
        if s.structure_type == StructureType.INTEGRATION:
            print(f"  - {s.name}: expects '{s.expected_output}'")


if __name__ == "__main__":
    main()
