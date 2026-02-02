"""
NBT Converters for ProjectRed Multipart (Gates & Wires)

Konwertery dla bramek logicznych i przewodów (Integration/Transmission).
Te elementy używają systemu ForgeMultipart (1.7.10) / CBMultipart (1.18.2).

Source mapping:
1.7.10:
- GatePart: integration/gatepart.scala
  save: orient (Byte), subID (Byte), shape (Byte), connMap (Integer), nolegacy (Boolean), schedTime (Long)
- RedstoneGatePart: integration/gatepartrs.scala
  save: state (Byte)
- SequentialGatePart: integration/gatepartseq.scala
  save: state2 (Byte), pmax (Integer), pelapsed (Long), val/max/inc/dec (Integer)
- RedwirePart: transmission/redwires.scala
  save: signal (Byte)
- BundledCablePart: transmission/bundledwires.scala
  save: signal (ByteArray), colour (Byte)

1.18.2:
- GatePart: integration/part/GatePart.java
  save: orient (byte), shape (byte), connMap (int), schedTime (long)
  UWAGA: Brak subID! Typ bramki określony przez typ części.
- RedwirePart: transmission/part/RedwirePart.java
  save: signal (byte), connMap (int), side (byte)
- BundledCablePart: transmission/part/BundledCablePart.java
  save: signal (byte[16]), connMap (int), side (byte)
"""

from typing import Dict, Any, Optional, Tuple
from .base_converter import BaseNBTConverter, NBTConversionResult


# Mapowanie GateType ordinal (subID) na nazwę bramki
# Źródło: integration/gatepart.scala:GateType enum
GATE_TYPE_NAMES = {
    0: "or",
    1: "nor",
    2: "not",
    3: "and",
    4: "nand",
    5: "xor",
    6: "xnor",
    7: "buffer",
    8: "multiplexer",
    9: "pulse",
    10: "repeater",
    11: "randomizer",
    12: "sr_latch",
    13: "toggle_latch",
    14: "transparent_latch",
    15: "timer",
    16: "sequencer",
    17: "counter",
    18: "state_cell",
    19: "synchronizer",
    20: "bus_transceiver",
    21: "null_cell",
    22: "invert_cell",
    23: "buffer_cell",
    24: "comparator",
    25: "and_cell",
    26: "bus_randomizer",
    27: "bus_converter",
    28: "bus_input_panel",
    29: "stacking_latch",
    30: "segment_display",
    31: "dec_randomizer",
}

# Mapowanie typu części (pr_*gate) na prefix nazwy bloku w 1.18.2
GATE_PART_TYPE_PREFIX = {
    "pr_sgate": "projectred_integration:",  # Simple gates
    "pr_igate": "projectred_integration:",  # Internal gates (Sequential)
    "pr_agate": "projectred_integration:",  # Array gates
    "pr_bgate": "projectred_integration:",  # Bundled gates
}


class GatePartConverter(BaseNBTConverter):
    """
    Konwerter dla GatePart (1.7.10) -> GatePart (1.18.2)

    KLUCZOWA RÓŻNICA:
    - 1.7.10: subID (Byte) określa typ bramki
    - 1.18.2: Typ bramki jest określony przez sam typ części, nie ma subID w NBT

    Source mapping:
    1.7.10 NBT:
    - orient (Byte): orientacja (side 0-5 << 4 | rotation 0-3)
    - subID (Byte): typ bramki (GateType ordinal)
    - shape (Byte): kształt/wariant bramki
    - connMap (Integer): mapa połączeń
    - nolegacy (Boolean): flaga legacy
    - schedTime (Long): zaplanowany tick

    1.18.2 NBT:
    - orient (byte): orientacja
    - shape (byte): kształt
    - connMap (int): mapa połączeń
    - schedTime (long): zaplanowany tick
    """

    SOURCE_1710 = "integration/gatepart.scala:57-74"
    SOURCE_1182 = "integration/part/GatePart.java:151-166"

    @property
    def converter_name(self) -> str:
        return "gate_part"

    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        self.reset()

        # Pobierz tagi z 1.7.10
        orient = nbt_1710.get("orient", 0)
        sub_id = nbt_1710.get("subID", 0)
        shape = nbt_1710.get("shape", 0)
        conn_map = nbt_1710.get("connMap", 0)
        sched_time = nbt_1710.get("schedTime", 0)

        # Obsługa legacy connMap (jeśli nolegacy=False)
        if not nbt_1710.get("nolegacy", True):
            # Legacy format: Short | 0xf000
            conn_map = (conn_map & 0xFFFF) | 0xF000

        # subID jest używany do określenia typu bramki dla mapowania bloku
        # W 1.18.2 typ jest w block ID, nie w NBT
        gate_type_name = GATE_TYPE_NAMES.get(sub_id, f"unknown_{sub_id}")

        # Zapisz typ bramki jako metadata dla warstwy wyższej
        # (do użycia przy mapowaniu block ID)
        converted_nbt = {
            "orient": orient,
            "shape": shape,
            "connMap": conn_map,
            "schedTime": sched_time,
            # Nie w oficjalnym NBT, ale potrzebne dla konwersji:
            "__gate_type": gate_type_name,
            "__gate_sub_id": sub_id
        }

        # Ekstrakcja orientacji do blockstate
        side = (orient >> 4) & 0x7  # Górne 3 bity
        rotation = orient & 0x3  # Dolne 2 bity

        blockstate_props = {
            "side": str(side),
            "rotation": str(rotation)
        }

        return self._create_result(converted_nbt, blockstate_props)


class RedstoneGatePartConverter(GatePartConverter):
    """
    Konwerter dla RedstoneGatePart (1.7.10) - bramki z wejściem/wyjściem redstone

    Source mapping:
    1.7.10 NBT (dodatkowo do GatePart):
    - state (Byte): stan wejść/wyjść (format OOOO IIII)

    1.18.2 NBT:
    - (takie same jak GatePart)
    - state jest w logice bramki, może nie być w NBT
    """

    SOURCE_1710 = "integration/gatepartrs.scala:35-43"
    SOURCE_1182 = "integration/part/GatePart.java (+ logika w subklasach)"

    @property
    def converter_name(self) -> str:
        return "redstone_gate_part"

    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        # Najpierw konwertuj bazowe tagi
        result = super().convert(nbt_1710, block_id, metadata)

        if not result.success:
            return result

        # Dodaj state jeśli istnieje
        state = nbt_1710.get("state", 0)
        result.converted_nbt["state"] = state

        return result


class SequentialGatePartConverter(RedstoneGatePartConverter):
    """
    Konwerter dla bramek sekwencyjnych (Timer, Counter, Sequencer, etc.)

    Source mapping:
    1.7.10 NBT (dodatkowo):
    - state2 (Byte): dodatkowy stan
    - pmax (Integer): maksymalny czas timera
    - pelapsed (Long): upłynięty czas
    - val, max, inc, dec (Integer): dla Counter

    1.18.2: Struktura może się różnić - wymaga weryfikacji
    """

    SOURCE_1710 = "integration/gatepartseq.scala:82-506"
    SOURCE_1182 = "integration/part/ (bramki sekwencyjne)"

    @property
    def converter_name(self) -> str:
        return "sequential_gate_part"

    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        # Najpierw konwertuj bazowe tagi
        result = super().convert(nbt_1710, block_id, metadata)

        if not result.success:
            return result

        nbt = result.converted_nbt

        # Dodatkowe tagi dla bramek sekwencyjnych
        if "state2" in nbt_1710:
            nbt["state2"] = nbt_1710["state2"]

        # Timer gates
        if "pmax" in nbt_1710:
            nbt["pmax"] = nbt_1710["pmax"]
        if "pelapsed" in nbt_1710:
            nbt["pelapsed"] = nbt_1710["pelapsed"]

        # Counter gates
        if "val" in nbt_1710:
            nbt["val"] = nbt_1710["val"]
        if "max" in nbt_1710:
            nbt["max"] = nbt_1710["max"]
        if "inc" in nbt_1710:
            nbt["inc"] = nbt_1710["inc"]
        if "dec" in nbt_1710:
            nbt["dec"] = nbt_1710["dec"]

        self._add_warning("SEQUENTIAL-GATE",
                         "Bramki sekwencyjne mogą wymagać ręcznej weryfikacji stanu po konwersji")

        return result


class ArrayGatePartConverter(GatePartConverter):
    """
    Konwerter dla ArrayGatePart (bramki tablicowe: NullCell, InvertCell, etc.)

    Source mapping:
    1.7.10 NBT (dodatkowo):
    - s1 (Byte): signal1 dla krzyżujących się przewodów
    - s2 (Byte): signal2 dla krzyżujących się przewodów
    - signal (Byte): pojedynczy sygnał

    1.18.2: Podobna struktura
    """

    SOURCE_1710 = "integration/gatepartarray.scala:298-405"
    SOURCE_1182 = "integration/part/ (bramki array)"

    @property
    def converter_name(self) -> str:
        return "array_gate_part"

    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        result = super().convert(nbt_1710, block_id, metadata)

        if not result.success:
            return result

        nbt = result.converted_nbt

        # ArrayGateCrossing
        if "s1" in nbt_1710:
            nbt["s1"] = nbt_1710["s1"]
        if "s2" in nbt_1710:
            nbt["s2"] = nbt_1710["s2"]

        # TArrayCellTopOnly
        if "signal" in nbt_1710:
            nbt["signal"] = nbt_1710["signal"]

        return result


class RedwirePartConverter(BaseNBTConverter):
    """
    Konwerter dla RedwirePart (przewody Red Alloy)

    Source mapping:
    1.7.10 NBT (TRedwireCommons trait):
    - signal (Byte): siła sygnału (0-255)

    1.18.2 NBT:
    - signal (byte): siła sygnału
    - connMap (int): mapa połączeń
    - side (byte): strona bloku
    """

    SOURCE_1710 = "transmission/redwires.scala:43-50"
    SOURCE_1182 = "transmission/part/RedwirePart.java:37-46"

    @property
    def converter_name(self) -> str:
        return "redwire_part"

    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        self.reset()

        signal = nbt_1710.get("signal", 0)

        # W 1.18.2 connMap i side są osobnymi polami
        # W 1.7.10 side może być w orient lub jako osobne pole
        conn_map = nbt_1710.get("connMap", 0)
        side = nbt_1710.get("side", 0)

        # Jeśli side nie jest podany, spróbuj wyciągnąć z metadata
        if side == 0 and metadata > 0:
            side = metadata & 0x7

        converted_nbt = {
            "signal": signal,
            "connMap": conn_map,
            "side": side
        }

        return self._create_result(converted_nbt)


class InsulatedWirePartConverter(RedwirePartConverter):
    """
    Konwerter dla InsulatedWire (kolorowe przewody izolowane)

    Te przewody dziedziczą z RedwirePart i dodają kolor.
    Kolor jest w metadata lub block ID, nie w NBT.
    """

    SOURCE_1710 = "transmission/redwires.scala (InsulatedRedAlloyPart)"
    SOURCE_1182 = "transmission/part/InsulatedRedAlloyPart.java"

    @property
    def converter_name(self) -> str:
        return "insulated_wire_part"

    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        result = super().convert(nbt_1710, block_id, metadata)

        if not result.success:
            return result

        # Kolor jest w block ID lub metadata, nie dodajemy do NBT
        # (zgodnie z SKILL.md - metadata jest parametrem wejściowym)

        return result


class BundledCablePartConverter(BaseNBTConverter):
    """
    Konwerter dla BundledCablePart (16-kanałowe przewody bundled)

    Source mapping:
    1.7.10 NBT (TBundledCableCommons trait):
    - signal (ByteArray): 16 bajtów, jeden na kolor
    - colour (Byte): kolor przewodu (0-15 lub -1 dla neutralnego)

    1.18.2 NBT:
    - signal (byte[16]): tablica sygnałów
    - connMap (int): mapa połączeń
    - side (byte): strona bloku
    """

    SOURCE_1710 = "transmission/bundledwires.scala:43-53"
    SOURCE_1182 = "transmission/part/BundledCablePart.java:65-74"

    @property
    def converter_name(self) -> str:
        return "bundled_cable_part"

    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        self.reset()

        # Pobierz signal array
        signal = nbt_1710.get("signal", [0] * 16)

        # Upewnij się że mamy dokładnie 16 elementów
        if isinstance(signal, list):
            if len(signal) < 16:
                signal = signal + [0] * (16 - len(signal))
            elif len(signal) > 16:
                signal = signal[:16]
                self._add_warning("SIGNAL-TRUNCATED",
                                 f"Bundled signal miał więcej niż 16 kanałów, obcięty")

        # colour w 1.7.10 określa kolor przewodu bundled
        # W 1.18.2 kolor jest w block ID
        colour = nbt_1710.get("colour", -1)

        conn_map = nbt_1710.get("connMap", 0)
        side = nbt_1710.get("side", 0)

        if side == 0 and metadata > 0:
            side = metadata & 0x7

        converted_nbt = {
            "signal": signal,
            "connMap": conn_map,
            "side": side,
            # Kolor dla mapowania block ID (nie w oficjalnym NBT 1.18.2)
            "__colour": colour
        }

        return self._create_result(converted_nbt)


class FramedWirePartConverter(RedwirePartConverter):
    """
    Konwerter dla FramedWire (przewody w ramkach - center wires)

    Te przewody mogą przechodzić przez środek bloku.
    """

    SOURCE_1710 = "transmission/redwires.scala (FramedRedAlloyWirePart)"
    SOURCE_1182 = "transmission/part/FramedRedAlloyWirePart.java"

    @property
    def converter_name(self) -> str:
        return "framed_wire_part"


def get_gate_block_id_1182(sub_id: int, part_type: str = "pr_sgate") -> str:
    """
    Generuje block ID 1.18.2 dla bramki na podstawie subID.

    Args:
        sub_id: GateType ordinal z 1.7.10
        part_type: Typ części (pr_sgate, pr_igate, pr_agate, pr_bgate)

    Returns:
        Block ID w formacie 1.18.2
    """
    gate_name = GATE_TYPE_NAMES.get(sub_id, f"unknown_gate_{sub_id}")
    prefix = GATE_PART_TYPE_PREFIX.get(part_type, "projectred_integration:")
    return f"{prefix}{gate_name}_gate"


def get_wire_block_id_1182(wire_type: str, colour: int = -1) -> str:
    """
    Generuje block ID 1.18.2 dla przewodu.

    Args:
        wire_type: Typ przewodu (redwire, insulated, bundled, framed)
        colour: Kolor (0-15) lub -1 dla neutralnego

    Returns:
        Block ID w formacie 1.18.2
    """
    # Kolory Minecraft
    colors = [
        "white", "orange", "magenta", "light_blue",
        "yellow", "lime", "pink", "gray",
        "light_gray", "cyan", "purple", "blue",
        "brown", "green", "red", "black"
    ]

    if wire_type == "redwire":
        return "projectred_transmission:red_alloy_wire"
    elif wire_type == "insulated":
        if 0 <= colour < 16:
            return f"projectred_transmission:{colors[colour]}_insulated_wire"
        return "projectred_transmission:white_insulated_wire"
    elif wire_type == "bundled":
        if 0 <= colour < 16:
            return f"projectred_transmission:{colors[colour]}_bundled_cable"
        return "projectred_transmission:bundled_cable"
    elif wire_type == "framed":
        return "projectred_transmission:framed_red_alloy_wire"

    return f"projectred_transmission:{wire_type}"
