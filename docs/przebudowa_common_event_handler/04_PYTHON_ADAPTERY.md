# 04. Adaptery Python do produkcji eventów

## Cel

Stworzenie wspólnej biblioteki Python (`src/common/`) która:
1. Definiuje ustandaryzowane typy eventów
2. Dostarcza `EventEmitter` do produkcji eventów
3. Serializuje eventy do JSON zgodnego ze specyfikacją
4. Waliduje eventy przed serializacją

## Struktura modułu

```
src/common/
├── __init__.py
├── events/
│   ├── __init__.py
│   ├── types.py           # Definicje typów eventów
│   ├── emitter.py         # EventEmitter - główna klasa
│   ├── validator.py       # Walidacja eventów
│   └── serializer.py      # Serializacja do JSON
├── mappings/
│   ├── __init__.py
│   ├── block_registry.py  # Centralny rejestr bloków
│   ├── item_registry.py   # Centralny rejestr itemów
│   └── blockstate.py      # Konwersja metadata → blockstate
├── nbt/
│   ├── __init__.py
│   ├── helpers.py         # Funkcje pomocnicze NBT
│   └── transformers.py    # Transformacje NBT między wersjami
└── adapters/
    ├── __init__.py
    └── base_adapter.py    # Bazowa klasa adaptera
```

## Implementacja

### 1. types.py - Definicje typów

```python
"""
src/common/events/types.py

Definicje typów eventów konwersji.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Any, Tuple, Union


class EventType(Enum):
    """Typy operacji eventów"""
    SET_BLOCK = "set_block"
    SET_BLOCK_ENTITY = "set_block_entity"
    REMOVE_BLOCK = "remove_block"
    SET_ENTITY = "set_entity"
    REMOVE_ENTITY = "remove_entity"
    MODIFY_NBT = "modify_nbt"


@dataclass(frozen=True)
class BlockPos:
    """Pozycja bloku w świecie"""
    x: int
    y: int
    z: int

    def to_tuple(self) -> Tuple[int, int, int]:
        return (self.x, self.y, self.z)

    def to_chunk(self) -> Tuple[int, int]:
        return (self.x >> 4, self.z >> 4)

    def to_region(self) -> Tuple[int, int]:
        return (self.x >> 9, self.z >> 9)

    @classmethod
    def from_tuple(cls, pos: Tuple[int, int, int]) -> 'BlockPos':
        return cls(pos[0], pos[1], pos[2])


@dataclass(frozen=True)
class EntityPos:
    """Pozycja entity (floating point)"""
    x: float
    y: float
    z: float

    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)


@dataclass
class EventSource:
    """Informacje o źródle eventu (do debugowania)"""
    mod: str
    block_id: Optional[str] = None
    te_id: Optional[str] = None
    metadata: Optional[int] = None
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"mod": self.mod}
        if self.block_id:
            result["block_id"] = self.block_id
        if self.te_id:
            result["te_id"] = self.te_id
        if self.metadata is not None:
            result["metadata"] = self.metadata
        if self.reason:
            result["reason"] = self.reason
        return result


# Type alias dla blockstate
BlockState = Dict[str, str]


@dataclass
class SetBlockEvent:
    """Event ustawienia bloku (bez BlockEntity)"""
    pos: BlockPos
    block: str
    blockstate: BlockState = field(default_factory=dict)
    source: Optional[EventSource] = None

    event_type: EventType = field(default=EventType.SET_BLOCK, init=False)


@dataclass
class SetBlockEntityEvent:
    """Event ustawienia bloku z BlockEntity"""
    pos: BlockPos
    block: str
    nbt: Dict[str, Any]
    blockstate: BlockState = field(default_factory=dict)
    source: Optional[EventSource] = None

    event_type: EventType = field(default=EventType.SET_BLOCK_ENTITY, init=False)

    def __post_init__(self):
        # Upewnij się że NBT ma wymagane pole 'id'
        if 'id' not in self.nbt:
            raise ValueError("BlockEntity NBT must have 'id' field")


@dataclass
class RemoveBlockEvent:
    """Event usunięcia bloku"""
    pos: BlockPos
    source: Optional[EventSource] = None

    event_type: EventType = field(default=EventType.REMOVE_BLOCK, init=False)


@dataclass
class SetEntityEvent:
    """Event dodania entity"""
    pos: EntityPos
    nbt: Dict[str, Any]
    source: Optional[EventSource] = None

    event_type: EventType = field(default=EventType.SET_ENTITY, init=False)

    def __post_init__(self):
        if 'id' not in self.nbt:
            raise ValueError("Entity NBT must have 'id' field")


@dataclass
class RemoveEntityEvent:
    """Event usunięcia entity"""
    uuid: List[int]  # IntArray [4 elementy]
    source: Optional[EventSource] = None

    event_type: EventType = field(default=EventType.REMOVE_ENTITY, init=False)


@dataclass
class NbtOperation:
    """Pojedyncza operacja modyfikacji NBT"""
    path: str
    op: str  # "set", "remove", "append"
    value: Any = None


@dataclass
class ModifyNbtEvent:
    """Event modyfikacji istniejącego NBT"""
    pos: BlockPos
    target: str  # "block_entity" lub "entity"
    operations: List[NbtOperation]
    source: Optional[EventSource] = None

    event_type: EventType = field(default=EventType.MODIFY_NBT, init=False)


# Union type dla wszystkich eventów
ConversionEvent = Union[
    SetBlockEvent,
    SetBlockEntityEvent,
    RemoveBlockEvent,
    SetEntityEvent,
    RemoveEntityEvent,
    ModifyNbtEvent
]


@dataclass
class EventWarning:
    """Ostrzeżenie podczas konwersji"""
    code: str
    message: str
    pos: Optional[BlockPos] = None
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"code": self.code, "message": self.message}
        if self.pos:
            result["pos"] = list(self.pos.to_tuple())
        if self.details:
            result["details"] = self.details
        return result
```

### 2. emitter.py - EventEmitter

```python
"""
src/common/events/emitter.py

EventEmitter - główna klasa do produkcji eventów.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict

from .types import (
    ConversionEvent, EventWarning, BlockPos,
    SetBlockEvent, SetBlockEntityEvent, RemoveBlockEvent,
    SetEntityEvent, RemoveEntityEvent, ModifyNbtEvent,
    EventSource, BlockState, EntityPos
)
from .validator import EventValidator
from .serializer import EventSerializer


class EventEmitter:
    """
    Główna klasa do produkcji i zarządzania eventami konwersji.

    Użycie:
        emitter = EventEmitter(converter_name="betterstorage")

        # Emituj eventy
        emitter.set_block(BlockPos(100, 64, 200), "minecraft:chest",
                         blockstate={"facing": "north"})
        emitter.set_block_entity(BlockPos(100, 64, 200), "minecraft:chest",
                                nbt={"id": "minecraft:chest", "Items": [...]})

        # Zapisz do pliku
        emitter.save("events/betterstorage_events.json")
    """

    def __init__(
        self,
        converter_name: str,
        source_world: Optional[str] = None,
        target_world: Optional[str] = None,
        validate: bool = True
    ):
        self.converter_name = converter_name
        self.source_world = source_world
        self.target_world = target_world
        self.validate = validate

        self._events: List[ConversionEvent] = []
        self._warnings: List[EventWarning] = []
        self._validator = EventValidator() if validate else None

        # Statystyki
        self._stats = defaultdict(int)

    # ==================== Event emission methods ====================

    def set_block(
        self,
        pos: BlockPos,
        block: str,
        blockstate: BlockState = None,
        source: EventSource = None
    ) -> None:
        """Emituj event ustawienia bloku (bez BlockEntity)"""
        event = SetBlockEvent(
            pos=pos,
            block=block,
            blockstate=blockstate or {},
            source=source
        )
        self._emit(event)
        self._stats["blocks"] += 1

    def set_block_entity(
        self,
        pos: BlockPos,
        block: str,
        nbt: Dict[str, Any],
        blockstate: BlockState = None,
        source: EventSource = None
    ) -> None:
        """Emituj event ustawienia bloku z BlockEntity"""
        event = SetBlockEntityEvent(
            pos=pos,
            block=block,
            nbt=nbt,
            blockstate=blockstate or {},
            source=source
        )
        self._emit(event)
        self._stats["block_entities"] += 1

    def remove_block(
        self,
        pos: BlockPos,
        source: EventSource = None
    ) -> None:
        """Emituj event usunięcia bloku"""
        event = RemoveBlockEvent(pos=pos, source=source)
        self._emit(event)
        self._stats["removed_blocks"] += 1

    def set_entity(
        self,
        pos: EntityPos,
        nbt: Dict[str, Any],
        source: EventSource = None
    ) -> None:
        """Emituj event dodania entity"""
        event = SetEntityEvent(pos=pos, nbt=nbt, source=source)
        self._emit(event)
        self._stats["entities"] += 1

    def remove_entity(
        self,
        uuid: List[int],
        source: EventSource = None
    ) -> None:
        """Emituj event usunięcia entity"""
        event = RemoveEntityEvent(uuid=uuid, source=source)
        self._emit(event)
        self._stats["removed_entities"] += 1

    def add_warning(
        self,
        code: str,
        message: str,
        pos: BlockPos = None,
        details: Dict[str, Any] = None
    ) -> None:
        """Dodaj ostrzeżenie"""
        warning = EventWarning(
            code=code,
            message=message,
            pos=pos,
            details=details
        )
        self._warnings.append(warning)
        self._stats["warnings"] += 1

    # ==================== Internal methods ====================

    def _emit(self, event: ConversionEvent) -> None:
        """Wewnętrzna metoda emisji eventu"""
        if self._validator:
            errors = self._validator.validate_event(event)
            if errors:
                raise ValueError(f"Invalid event: {errors}")

        self._events.append(event)
        self._stats["total_events"] += 1

    # ==================== Output methods ====================

    def to_dict(self) -> Dict[str, Any]:
        """Konwertuj do słownika (format Event JSON)"""
        return {
            "version": "2.0",
            "metadata": {
                "converter": self.converter_name,
                "source_world": self.source_world,
                "target_world": self.target_world,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "stats": dict(self._stats)
            },
            "events": [EventSerializer.serialize_event(e) for e in self._events],
            "warnings": [w.to_dict() for w in self._warnings]
        }

    def to_json(self, indent: int = 2) -> str:
        """Konwertuj do JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, path: str) -> None:
        """Zapisz do pliku JSON"""
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

        print(f"Saved {len(self._events)} events to {path}")
        print(f"Stats: {dict(self._stats)}")

    # ==================== Utility methods ====================

    @property
    def event_count(self) -> int:
        """Liczba eventów"""
        return len(self._events)

    @property
    def warning_count(self) -> int:
        """Liczba ostrzeżeń"""
        return len(self._warnings)

    @property
    def stats(self) -> Dict[str, int]:
        """Statystyki"""
        return dict(self._stats)

    def get_events_by_region(self) -> Dict[tuple, List[ConversionEvent]]:
        """Pogrupuj eventy po regionach"""
        by_region = defaultdict(list)
        for event in self._events:
            if hasattr(event, 'pos') and hasattr(event.pos, 'to_region'):
                region = event.pos.to_region()
                by_region[region].append(event)
        return dict(by_region)

    def clear(self) -> None:
        """Wyczyść wszystkie eventy i ostrzeżenia"""
        self._events.clear()
        self._warnings.clear()
        self._stats.clear()
```

### 3. serializer.py - Serializacja

```python
"""
src/common/events/serializer.py

Serializacja eventów do JSON.
"""

from typing import Dict, Any, List

from .types import (
    ConversionEvent, SetBlockEvent, SetBlockEntityEvent,
    RemoveBlockEvent, SetEntityEvent, RemoveEntityEvent,
    ModifyNbtEvent, NbtOperation
)


class EventSerializer:
    """Serializator eventów do formatu JSON"""

    @staticmethod
    def serialize_event(event: ConversionEvent) -> Dict[str, Any]:
        """Serializuj pojedynczy event"""
        if isinstance(event, SetBlockEvent):
            return EventSerializer._serialize_set_block(event)
        elif isinstance(event, SetBlockEntityEvent):
            return EventSerializer._serialize_set_block_entity(event)
        elif isinstance(event, RemoveBlockEvent):
            return EventSerializer._serialize_remove_block(event)
        elif isinstance(event, SetEntityEvent):
            return EventSerializer._serialize_set_entity(event)
        elif isinstance(event, RemoveEntityEvent):
            return EventSerializer._serialize_remove_entity(event)
        elif isinstance(event, ModifyNbtEvent):
            return EventSerializer._serialize_modify_nbt(event)
        else:
            raise ValueError(f"Unknown event type: {type(event)}")

    @staticmethod
    def _serialize_set_block(event: SetBlockEvent) -> Dict[str, Any]:
        result = {
            "op": "set_block",
            "pos": list(event.pos.to_tuple()),
            "block": event.block
        }
        if event.blockstate:
            result["blockstate"] = event.blockstate
        if event.source:
            result["source"] = event.source.to_dict()
        return result

    @staticmethod
    def _serialize_set_block_entity(event: SetBlockEntityEvent) -> Dict[str, Any]:
        result = {
            "op": "set_block_entity",
            "pos": list(event.pos.to_tuple()),
            "block": event.block,
            "nbt": event.nbt
        }
        if event.blockstate:
            result["blockstate"] = event.blockstate
        if event.source:
            result["source"] = event.source.to_dict()
        return result

    @staticmethod
    def _serialize_remove_block(event: RemoveBlockEvent) -> Dict[str, Any]:
        result = {
            "op": "remove_block",
            "pos": list(event.pos.to_tuple())
        }
        if event.source:
            result["source"] = event.source.to_dict()
        return result

    @staticmethod
    def _serialize_set_entity(event: SetEntityEvent) -> Dict[str, Any]:
        result = {
            "op": "set_entity",
            "pos": list(event.pos.to_tuple()),
            "nbt": event.nbt
        }
        if event.source:
            result["source"] = event.source.to_dict()
        return result

    @staticmethod
    def _serialize_remove_entity(event: RemoveEntityEvent) -> Dict[str, Any]:
        result = {
            "op": "remove_entity",
            "uuid": event.uuid
        }
        if event.source:
            result["source"] = event.source.to_dict()
        return result

    @staticmethod
    def _serialize_modify_nbt(event: ModifyNbtEvent) -> Dict[str, Any]:
        result = {
            "op": "modify_nbt",
            "pos": list(event.pos.to_tuple()),
            "target": event.target,
            "operations": [
                {"path": op.path, "op": op.op, "value": op.value}
                for op in event.operations
            ]
        }
        if event.source:
            result["source"] = event.source.to_dict()
        return result
```

### 4. base_adapter.py - Bazowy adapter

```python
"""
src/common/adapters/base_adapter.py

Bazowa klasa adaptera dla konwerterów modów.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple

from ..events.emitter import EventEmitter
from ..events.types import BlockPos, EntityPos, EventSource, BlockState


class BaseModAdapter(ABC):
    """
    Bazowa klasa adaptera dla konwerterów modów.

    Każdy konwerter moda powinien dziedziczyć po tej klasie
    i implementować metody konwersji.

    Przykład użycia:
        class BetterStorageAdapter(BaseModAdapter):
            MOD_NAME = "betterstorage"

            def convert_block(self, block_id, metadata, te_nbt):
                # Logika konwersji
                self.emitter.set_block_entity(...)
    """

    MOD_NAME: str = "unknown"  # Nadpisz w podklasie

    def __init__(
        self,
        source_world: Optional[str] = None,
        target_world: Optional[str] = None
    ):
        self.emitter = EventEmitter(
            converter_name=self.MOD_NAME,
            source_world=source_world,
            target_world=target_world
        )

    # ==================== Abstract methods ====================

    @abstractmethod
    def can_handle_block(self, block_id: str) -> bool:
        """Sprawdź czy adapter obsługuje dany blok"""
        pass

    @abstractmethod
    def convert_block(
        self,
        pos: BlockPos,
        block_id: str,
        metadata: int,
        te_nbt: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Konwertuj blok.

        Args:
            pos: Pozycja bloku
            block_id: ID bloku źródłowego (np. "betterstorage:reinforcedChest")
            metadata: Metadata bloku (0-15)
            te_nbt: NBT TileEntity (jeśli istnieje)

        Returns:
            True jeśli konwersja się powiodła, False w przeciwnym razie
        """
        pass

    # ==================== Helper methods ====================

    def create_source(
        self,
        block_id: str,
        metadata: int = None,
        te_id: str = None,
        reason: str = None
    ) -> EventSource:
        """Stwórz obiekt źródła dla eventu"""
        return EventSource(
            mod=self.MOD_NAME,
            block_id=block_id,
            metadata=metadata,
            te_id=te_id,
            reason=reason
        )

    def emit_warning(
        self,
        code: str,
        message: str,
        pos: BlockPos = None,
        details: Dict[str, Any] = None
    ) -> None:
        """Emituj ostrzeżenie"""
        self.emitter.add_warning(
            code=f"{self.MOD_NAME.upper()}-{code}",
            message=message,
            pos=pos,
            details=details
        )

    def save_events(self, output_path: str) -> None:
        """Zapisz eventy do pliku"""
        self.emitter.save(output_path)

    @property
    def stats(self) -> Dict[str, int]:
        """Statystyki konwersji"""
        return self.emitter.stats

    # ==================== Common conversion helpers ====================

    def metadata_to_facing(self, metadata: int) -> str:
        """Konwertuj metadata na facing direction"""
        FACING_MAP = {
            0: "down",
            1: "up",
            2: "north",
            3: "south",
            4: "west",
            5: "east"
        }
        return FACING_MAP.get(metadata & 0x7, "north")

    def metadata_to_horizontal_facing(self, metadata: int) -> str:
        """Konwertuj metadata na horizontal facing (tylko N/S/E/W)"""
        HORIZONTAL_FACING_MAP = {
            0: "south",
            1: "west",
            2: "north",
            3: "east"
        }
        return HORIZONTAL_FACING_MAP.get(metadata & 0x3, "north")

    def metadata_to_axis(self, metadata: int) -> str:
        """Konwertuj metadata na axis (x/y/z)"""
        AXIS_MAP = {
            0: "y",
            4: "x",
            8: "z"
        }
        return AXIS_MAP.get(metadata & 0xC, "y")
```

### 5. Przykład użycia - BetterStorage adapter

```python
"""
src/converters/betterstorage/adapter.py

Adapter BetterStorage używający nowego systemu eventów.
"""

from typing import Dict, Any, Optional, List

from src.common.adapters.base_adapter import BaseModAdapter
from src.common.events.types import BlockPos, BlockState


class BetterStorageAdapter(BaseModAdapter):
    """Adapter dla moda BetterStorage"""

    MOD_NAME = "betterstorage"

    # Mapowania bloków
    BLOCK_MAPPINGS = {
        "betterstorage:reinforcedChest": ("minecraft:chest", {}),
        "betterstorage:locker": ("minecraft:barrel", {}),
        "betterstorage:crate": ("minecraft:barrel", {}),
        "betterstorage:reinforcedLocker": ("minecraft:barrel", {}),
    }

    def can_handle_block(self, block_id: str) -> bool:
        return block_id.startswith("betterstorage:")

    def convert_block(
        self,
        pos: BlockPos,
        block_id: str,
        metadata: int,
        te_nbt: Optional[Dict[str, Any]] = None
    ) -> bool:
        if block_id not in self.BLOCK_MAPPINGS:
            self.emit_warning(
                "W-UNKNOWN-BLOCK",
                f"Unknown block: {block_id}",
                pos=pos
            )
            return False

        target_block, extra_props = self.BLOCK_MAPPINGS[block_id]

        # Oblicz blockstate
        blockstate = self._calculate_blockstate(block_id, metadata, extra_props)

        # Jeśli ma TileEntity
        if te_nbt:
            converted_nbt = self._convert_te_nbt(block_id, te_nbt, pos)
            if converted_nbt:
                self.emitter.set_block_entity(
                    pos=pos,
                    block=target_block,
                    blockstate=blockstate,
                    nbt=converted_nbt,
                    source=self.create_source(block_id, metadata, te_nbt.get("id"))
                )
            else:
                # Fallback do zwykłego bloku
                self.emitter.set_block(
                    pos=pos,
                    block=target_block,
                    blockstate=blockstate,
                    source=self.create_source(block_id, metadata)
                )
        else:
            self.emitter.set_block(
                pos=pos,
                block=target_block,
                blockstate=blockstate,
                source=self.create_source(block_id, metadata)
            )

        return True

    def _calculate_blockstate(
        self,
        block_id: str,
        metadata: int,
        extra_props: Dict[str, str]
    ) -> BlockState:
        """Oblicz blockstate z metadata"""
        blockstate = dict(extra_props)

        if "chest" in block_id.lower():
            blockstate["facing"] = self.metadata_to_horizontal_facing(metadata)
            blockstate["type"] = "single"
            blockstate["waterlogged"] = "false"
        elif "locker" in block_id.lower() or "crate" in block_id.lower():
            blockstate["facing"] = self.metadata_to_facing(metadata)
            blockstate["open"] = "false"

        return blockstate

    def _convert_te_nbt(
        self,
        block_id: str,
        te_nbt: Dict[str, Any],
        pos: BlockPos
    ) -> Optional[Dict[str, Any]]:
        """Konwertuj NBT TileEntity"""
        target_block = self.BLOCK_MAPPINGS[block_id][0]

        # Podstawowa struktura
        result = {
            "id": self._get_be_id(target_block),
            "x": pos.x,
            "y": pos.y,
            "z": pos.z,
            "Items": [],
            "Lock": ""
        }

        # Konwertuj itemy
        if "Items" in te_nbt:
            converted_items, overflow = self._convert_items(te_nbt["Items"], target_block)
            result["Items"] = converted_items

            # Obsłuż overflow
            if overflow:
                self._handle_overflow(pos, overflow)

        return result

    def _get_be_id(self, block_id: str) -> str:
        """Pobierz ID BlockEntity dla danego bloku"""
        BE_IDS = {
            "minecraft:chest": "minecraft:chest",
            "minecraft:barrel": "minecraft:barrel",
        }
        return BE_IDS.get(block_id, block_id)

    def _convert_items(
        self,
        items: List[Dict],
        target_block: str
    ) -> tuple[List[Dict], List[Dict]]:
        """Konwertuj listę itemów, zwróć (converted, overflow)"""
        # Określ max slotów
        max_slots = 27 if target_block == "minecraft:chest" else 27

        converted = []
        overflow = []

        for item in items:
            slot = item.get("Slot", 0)
            if slot < max_slots:
                converted.append(self._convert_item(item))
            else:
                overflow.append(item)

        return converted, overflow

    def _convert_item(self, item: Dict) -> Dict:
        """Konwertuj pojedynczy item"""
        # TODO: Pełna konwersja itemów 1.7.10 → 1.18.2
        return {
            "Slot": item.get("Slot", 0),
            "id": self._convert_item_id(item.get("id", "minecraft:air")),
            "Count": item.get("Count", 1)
        }

    def _convert_item_id(self, old_id: str) -> str:
        """Konwertuj ID itemu"""
        # TODO: Pełna mapa konwersji
        if isinstance(old_id, int):
            # Numeryczne ID z 1.7.10
            return f"minecraft:unknown_{old_id}"
        return old_id

    def _handle_overflow(self, pos: BlockPos, overflow: List[Dict]) -> None:
        """Obsłuż nadmiarowe itemy"""
        from src.common.events.types import EntityPos

        self.emit_warning(
            "W-OVERFLOW",
            f"Item overflow: {len(overflow)} items couldn't fit",
            pos=pos,
            details={"overflow_count": len(overflow)}
        )

        # Spawn dropped items
        for i, item in enumerate(overflow):
            entity_pos = EntityPos(
                pos.x + 0.5,
                pos.y + 1.0 + (i * 0.1),
                pos.z + 0.5
            )
            self.emitter.set_entity(
                pos=entity_pos,
                nbt={
                    "id": "minecraft:item",
                    "Item": self._convert_item(item),
                    "Motion": [0.0, 0.0, 0.0],
                    "Pos": list(entity_pos.to_tuple())
                },
                source=self.create_source(
                    block_id="overflow",
                    reason=f"Overflow item {i+1}/{len(overflow)}"
                )
            )
```

## Użycie adaptera

```python
# Przykład użycia BetterStorageAdapter

from src.converters.betterstorage.adapter import BetterStorageAdapter
from src.common.events.types import BlockPos

# Inicjalizacja
adapter = BetterStorageAdapter(
    source_world="maps/1.7.10/world",
    target_world="maps/1.18.2/world"
)

# Konwertuj bloki (np. ze skanowania mapy)
for block_data in scan_map("maps/1.7.10/world"):
    if adapter.can_handle_block(block_data["id"]):
        adapter.convert_block(
            pos=BlockPos.from_tuple(block_data["pos"]),
            block_id=block_data["id"],
            metadata=block_data["metadata"],
            te_nbt=block_data.get("te_nbt")
        )

# Zapisz eventy
adapter.save_events("events/betterstorage_events.json")

# Pokaż statystyki
print(f"Stats: {adapter.stats}")
```
