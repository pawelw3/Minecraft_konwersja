"""
Writer formatu NBT (Named Binary Tag) dla Minecraft.
Obsługuje kompresję gzip i zapis do formatu schematic.
"""

import struct
import gzip
from io import BytesIO
from typing import Any, Dict, List, Union


class NBTWriter:
    """Writer danych NBT (Named Binary Tag)."""
    
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
    
    def __init__(self):
        self.stream = BytesIO()
    
    def _write_byte(self, value: int):
        self.stream.write(struct.pack('>b', value))
    
    def _write_ubyte(self, value: int):
        self.stream.write(struct.pack('>B', value))
    
    def _write_short(self, value: int):
        self.stream.write(struct.pack('>h', value))
    
    def _write_int(self, value: int):
        self.stream.write(struct.pack('>i', value))
    
    def _write_long(self, value: int):
        self.stream.write(struct.pack('>q', value))
    
    def _write_float(self, value: float):
        self.stream.write(struct.pack('>f', value))
    
    def _write_double(self, value: float):
        self.stream.write(struct.pack('>d', value))
    
    def _write_string(self, value: str):
        encoded = value.encode('utf-8')
        self._write_short(len(encoded))
        self.stream.write(encoded)
    
    def _write_byte_array(self, value: bytes):
        self._write_int(len(value))
        self.stream.write(value)
    
    def _write_int_array(self, value: List[int]):
        self._write_int(len(value))
        for i in value:
            self._write_int(i)
    
    def _write_long_array(self, value: List[int]):
        self._write_int(len(value))
        for i in value:
            self._write_long(i)
    
    def _write_list(self, items: List[Any], item_type: int):
        self._write_ubyte(item_type)
        self._write_int(len(items))
        for item in items:
            if isinstance(item, tuple):
                # Item is already (type, value) tuple
                _, value = item
                self._write_payload(value, item_type)
            else:
                self._write_payload(item, item_type)
    
    def _write_compound(self, items: Dict[str, Any]):
        for name, (tag_type, value) in items.items():
            self._write_ubyte(tag_type)
            self._write_string(name)
            self._write_payload(value, tag_type)
        self._write_ubyte(self.TAG_END)
    
    def _write_payload(self, value: Any, tag_type: int):
        if tag_type == self.TAG_BYTE:
            self._write_byte(value)
        elif tag_type == self.TAG_SHORT:
            self._write_short(value)
        elif tag_type == self.TAG_INT:
            self._write_int(value)
        elif tag_type == self.TAG_LONG:
            self._write_long(value)
        elif tag_type == self.TAG_FLOAT:
            self._write_float(value)
        elif tag_type == self.TAG_DOUBLE:
            self._write_double(value)
        elif tag_type == self.TAG_BYTE_ARRAY:
            self._write_byte_array(value)
        elif tag_type == self.TAG_STRING:
            self._write_string(value)
        elif tag_type == self.TAG_LIST:
            if value:
                # Detect item type from first item
                first = value[0]
                if isinstance(first, tuple):
                    item_type = first[0]
                    # Extract just the values from tuples
                    values = [v for _, v in value]
                else:
                    item_type = self.TAG_COMPOUND
                    values = value
                self._write_ubyte(item_type)
                self._write_int(len(values))
                for item in values:
                    self._write_payload(item, item_type)
            else:
                self._write_ubyte(self.TAG_END)
                self._write_int(0)
        elif tag_type == self.TAG_COMPOUND:
            self._write_compound(value)
        elif tag_type == self.TAG_INT_ARRAY:
            self._write_int_array(value)
        elif tag_type == self.TAG_LONG_ARRAY:
            self._write_long_array(value)
        else:
            raise ValueError(f"Unknown tag type: {tag_type}")
    
    def write(self, name: str, tag_type: int, value: Any) -> bytes:
        """Zapisuje dane NBT i zwraca bajty."""
        self._write_ubyte(tag_type)
        self._write_string(name)
        self._write_payload(value, tag_type)
        return self.stream.getvalue()
    
    def get_bytes(self) -> bytes:
        """Zwraca zapisane bajty."""
        return self.stream.getvalue()


def write_nbt_gzipped(name: str, tag_type: int, value: Any) -> bytes:
    """Zapisuje dane NBT i kompresuje je gzip."""
    writer = NBTWriter()
    data = writer.write(name, tag_type, value)
    return gzip.compress(data)


def create_byte(value: int) -> tuple:
    """Tworzy tuple (type, value) dla byte."""
    return (NBTWriter.TAG_BYTE, value)


def create_short(value: int) -> tuple:
    """Tworzy tuple (type, value) dla short."""
    return (NBTWriter.TAG_SHORT, value)


def create_int(value: int) -> tuple:
    """Tworzy tuple (type, value) dla int."""
    return (NBTWriter.TAG_INT, value)


def create_long(value: int) -> tuple:
    """Tworzy tuple (type, value) dla long."""
    return (NBTWriter.TAG_LONG, value)


def create_string(value: str) -> tuple:
    """Tworzy tuple (type, value) dla string."""
    return (NBTWriter.TAG_STRING, value)


def create_byte_array(value: bytes) -> tuple:
    """Tworzy tuple (type, value) dla byte array."""
    return (NBTWriter.TAG_BYTE_ARRAY, value)


def create_int_array(value: List[int]) -> tuple:
    """Tworzy tuple (type, value) dla int array."""
    return (NBTWriter.TAG_INT_ARRAY, value)


def create_list(items: List[Any]) -> tuple:
    """Tworzy tuple (type, value) dla list."""
    return (NBTWriter.TAG_LIST, items)


def create_compound(items: Dict[str, Any]) -> tuple:
    """Tworzy tuple (type, value) dla compound."""
    return (NBTWriter.TAG_COMPOUND, items)
