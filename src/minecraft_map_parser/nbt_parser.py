"""
Parser formatu NBT (Named Binary Tag) dla Minecraft.
Implementacja obsługuje kompresję gzip i zlib.
"""

import struct
import gzip
import zlib
from io import BytesIO
from typing import Any, Dict, List, Tuple, Union


class NBTTag:
    """Bazowa klasa dla tagów NBT."""
    
    TAG_END = 0
    TAG_BYTE = 1
    TAG_SHORT = 2
    TAG_INT = 3
    TAG_LONG = 4
    TAG_FLOAT = 5
    TAG_DOUBLE = 6
    TAG_BYTE_ARRAY = 7
    TAG_STRING = 8
    TAG_LIST = 9
    TAG_COMPOUND = 10
    TAG_INT_ARRAY = 11
    TAG_LONG_ARRAY = 12
    
    def __init__(self, tag_type: int, name: str = "", value: Any = None):
        self.type = tag_type
        self.name = name
        self.value = value
    
    def __repr__(self):
        return f"NBTTag(type={self.type}, name='{self.name}', value={self.value!r})"
    
    def get(self, key: str, default=None):
        """Pobiera wartość z compound tag."""
        if self.type == self.TAG_COMPOUND and isinstance(self.value, dict):
            return self.value.get(key, default)
        return default
    
    def __getitem__(self, key: str):
        """Umożliwia dostęp do compound tag przez []."""
        if self.type == self.TAG_COMPOUND and isinstance(self.value, dict):
            tag = self.value.get(key)
            if tag is None:
                raise KeyError(key)
            return tag.value if isinstance(tag, NBTTag) else tag
        raise TypeError(f"Cannot index NBTTag of type {self.type}")
    
    def __contains__(self, key: str) -> bool:
        """Sprawdza czy klucz istnieje w compound tag."""
        if self.type == self.TAG_COMPOUND and isinstance(self.value, dict):
            return key in self.value
        return False


class NBTParser:
    """Parser danych NBT (Named Binary Tag)."""
    
    def __init__(self, data: bytes):
        self.stream = BytesIO(data)
    
    def _read_byte(self) -> int:
        return struct.unpack('>b', self.stream.read(1))[0]
    
    def _read_ubyte(self) -> int:
        return struct.unpack('>B', self.stream.read(1))[0]
    
    def _read_short(self) -> int:
        return struct.unpack('>h', self.stream.read(2))[0]
    
    def _read_int(self) -> int:
        return struct.unpack('>i', self.stream.read(4))[0]
    
    def _read_long(self) -> int:
        return struct.unpack('>q', self.stream.read(8))[0]
    
    def _read_float(self) -> float:
        return struct.unpack('>f', self.stream.read(4))[0]
    
    def _read_double(self) -> float:
        return struct.unpack('>d', self.stream.read(8))[0]
    
    def _read_string(self) -> str:
        length = self._read_short()
        if length == 0:
            return ""
        return self.stream.read(length).decode('utf-8')
    
    def _read_byte_array(self) -> bytes:
        length = self._read_int()
        return self.stream.read(length)
    
    def _read_int_array(self) -> List[int]:
        length = self._read_int()
        return [self._read_int() for _ in range(length)]
    
    def _read_long_array(self) -> List[int]:
        length = self._read_int()
        return [self._read_long() for _ in range(length)]
    
    def _read_list(self) -> List[NBTTag]:
        tag_type = self._read_ubyte()
        length = self._read_int()
        items = []
        for _ in range(length):
            item = self._read_payload(tag_type)
            items.append(item)
        return items
    
    def _read_compound(self) -> Dict[str, NBTTag]:
        items = {}
        while True:
            tag_type = self._read_ubyte()
            if tag_type == NBTTag.TAG_END:
                break
            name = self._read_string()
            value = self._read_payload(tag_type)
            items[name] = NBTTag(tag_type, name, value)
        return items
    
    def _read_payload(self, tag_type: int) -> Any:
        if tag_type == NBTTag.TAG_BYTE:
            return self._read_byte()
        elif tag_type == NBTTag.TAG_SHORT:
            return self._read_short()
        elif tag_type == NBTTag.TAG_INT:
            return self._read_int()
        elif tag_type == NBTTag.TAG_LONG:
            return self._read_long()
        elif tag_type == NBTTag.TAG_FLOAT:
            return self._read_float()
        elif tag_type == NBTTag.TAG_DOUBLE:
            return self._read_double()
        elif tag_type == NBTTag.TAG_BYTE_ARRAY:
            return self._read_byte_array()
        elif tag_type == NBTTag.TAG_STRING:
            return self._read_string()
        elif tag_type == NBTTag.TAG_LIST:
            return self._read_list()
        elif tag_type == NBTTag.TAG_COMPOUND:
            return self._read_compound()
        elif tag_type == NBTTag.TAG_INT_ARRAY:
            return self._read_int_array()
        elif tag_type == NBTTag.TAG_LONG_ARRAY:
            return self._read_long_array()
        else:
            raise ValueError(f"Unknown tag type: {tag_type}")
    
    def parse(self) -> NBTTag:
        """Parsuje dane NBT i zwraca root tag."""
        tag_type = self._read_ubyte()
        if tag_type == NBTTag.TAG_END:
            raise ValueError("Empty NBT data")
        name = self._read_string()
        value = self._read_payload(tag_type)
        return NBTTag(tag_type, name, value)


def decompress_nbt(data: bytes) -> bytes:
    """Dekompresuje dane NBT (automatycznie wykrywa format)."""
    # Sprawdź magic bytes dla gzip
    if data[:2] == b'\x1f\x8b':
        return gzip.decompress(data)
    # Sprawdź magic bytes dla zlib
    elif data[:2] == b'\x78\x9c' or data[:2] == b'\x78\x01' or data[:2] == b'\x78\xda':
        return zlib.decompress(data)
    else:
        # Brak kompresji
        return data


def parse_nbt(data: bytes) -> NBTTag:
    """Parsuje dane NBT (z automatyczną dekompresją)."""
    decompressed = decompress_nbt(data)
    parser = NBTParser(decompressed)
    return parser.parse()
