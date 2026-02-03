"""
Prosty parser NBT dla plików Crate Pile (nieskompresowanych).

Obsługuje format NBT używany przez Better Storage 1.7.10:
- TAG_Compound
- TAG_List  
- TAG_Int
- TAG_Short
- TAG_Byte
- TAG_String
- TAG_Byte_Array
- TAG_Int_Array
- TAG_Long
- TAG_Float
- TAG_Double
- TAG_Long_Array
"""

import struct
from typing import Dict, List, Any, Optional, Tuple
from io import BytesIO


class NBTParseError(Exception):
    """Błąd parsowania NBT"""
    pass


class NBTReader:
    """Reader dla danych NBT (nieskompresowanych)"""
    
    # Tag types
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
    
    def __init__(self, data: bytes):
        self.stream = BytesIO(data)
    
    def _read_byte(self) -> int:
        """Czyta pojedynczy bajt"""
        byte = self.stream.read(1)
        if not byte:
            raise NBTParseError("Unexpected end of stream")
        return byte[0]
    
    def _read_short(self) -> int:
        """Czyta 2-bajtowy short (big-endian)"""
        data = self.stream.read(2)
        if len(data) < 2:
            raise NBTParseError("Unexpected end of stream")
        return struct.unpack('>h', data)[0]
    
    def _read_int(self) -> int:
        """Czyta 4-bajtowy int (big-endian)"""
        data = self.stream.read(4)
        if len(data) < 4:
            raise NBTParseError("Unexpected end of stream")
        return struct.unpack('>i', data)[0]
    
    def _read_long(self) -> int:
        """Czyta 8-bajtowy long (big-endian)"""
        data = self.stream.read(8)
        if len(data) < 8:
            raise NBTParseError("Unexpected end of stream")
        return struct.unpack('>q', data)[0]
    
    def _read_float(self) -> float:
        """Czyta 4-bajtowy float"""
        data = self.stream.read(4)
        if len(data) < 4:
            raise NBTParseError("Unexpected end of stream")
        return struct.unpack('>f', data)[0]
    
    def _read_double(self) -> float:
        """Czyta 8-bajtowy double"""
        data = self.stream.read(8)
        if len(data) < 8:
            raise NBTParseError("Unexpected end of stream")
        return struct.unpack('>d', data)[0]
    
    def _read_string(self) -> str:
        """Czyta string (short length + UTF-8 bytes)"""
        length = self._read_short()
        if length < 0:
            raise NBTParseError(f"Invalid string length: {length}")
        data = self.stream.read(length)
        if len(data) < length:
            raise NBTParseError("Unexpected end of stream while reading string")
        return data.decode('utf-8')
    
    def _read_byte_array(self) -> List[int]:
        """Czyta tablicę bajtów"""
        length = self._read_int()
        if length < 0:
            raise NBTParseError(f"Invalid byte array length: {length}")
        return [self._read_byte() for _ in range(length)]
    
    def _read_int_array(self) -> List[int]:
        """Czyta tablicę intów"""
        length = self._read_int()
        if length < 0:
            raise NBTParseError(f"Invalid int array length: {length}")
        return [self._read_int() for _ in range(length)]
    
    def _read_long_array(self) -> List[int]:
        """Czyta tablicę longów"""
        length = self._read_int()
        if length < 0:
            raise NBTParseError(f"Invalid long array length: {length}")
        return [self._read_long() for _ in range(length)]
    
    def _read_tag_payload(self, tag_type: int) -> Any:
        """Czyta payload dla danego typu tagu"""
        if tag_type == self.TAG_BYTE:
            return self._read_byte()
        elif tag_type == self.TAG_SHORT:
            return self._read_short()
        elif tag_type == self.TAG_INT:
            return self._read_int()
        elif tag_type == self.TAG_LONG:
            return self._read_long()
        elif tag_type == self.TAG_FLOAT:
            return self._read_float()
        elif tag_type == self.TAG_DOUBLE:
            return self._read_double()
        elif tag_type == self.TAG_BYTE_ARRAY:
            return self._read_byte_array()
        elif tag_type == self.TAG_STRING:
            return self._read_string()
        elif tag_type == self.TAG_LIST:
            return self._read_list()
        elif tag_type == self.TAG_COMPOUND:
            return self._read_compound()
        elif tag_type == self.TAG_INT_ARRAY:
            return self._read_int_array()
        elif tag_type == self.TAG_LONG_ARRAY:
            return self._read_long_array()
        else:
            raise NBTParseError(f"Unknown tag type: {tag_type}")
    
    def _read_list(self) -> List[Any]:
        """Czyta listę tagów"""
        element_type = self._read_byte()
        length = self._read_int()
        if length < 0:
            raise NBTParseError(f"Invalid list length: {length}")
        
        if element_type == self.TAG_END:
            # Pusta lista
            return []
        
        return [self._read_tag_payload(element_type) for _ in range(length)]
    
    def _read_compound(self) -> Dict[str, Any]:
        """Czyta compound tag (słownik)"""
        result = {}
        
        while True:
            tag_type = self._read_byte()
            if tag_type == self.TAG_END:
                break
            
            name = self._read_string()
            value = self._read_tag_payload(tag_type)
            result[name] = value
        
        return result
    
    def parse(self) -> Dict[str, Any]:
        """
        Parsuje cały plik NBT.
        
        Format: TAG_Compound z nazwą główną (zazwyczaj pustą lub "data")
        """
        tag_type = self._read_byte()
        if tag_type != self.TAG_COMPOUND:
            raise NBTParseError(f"Expected TAG_COMPOUND at root, got {tag_type}")
        
        # Nazwa głównego tagu
        name = self._read_string()
        
        # Payload - compound
        data = self._read_compound()
        
        return {
            'name': name,
            'data': data
        }
    
    def parse_simple(self) -> Dict[str, Any]:
        """Parsuje NBT i zwraca tylko dane (bez nazwy root)"""
        result = self.parse()
        return result['data']


def parse_nbt_file(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Parsuje plik NBT (nieskompresowany).
    
    Args:
        file_path: Ścieżka do pliku .dat
        
    Returns:
        Słownik z danymi NBT lub None w przypadku błędu
    """
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        
        reader = NBTReader(data)
        return reader.parse_simple()
        
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None


def parse_nbt_bytes(data: bytes) -> Optional[Dict[str, Any]]:
    """Parsuje bajty NBT"""
    try:
        reader = NBTReader(data)
        return reader.parse_simple()
    except Exception as e:
        print(f"Error parsing NBT bytes: {e}")
        return None
