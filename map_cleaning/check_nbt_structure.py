#!/usr/bin/env python3
"""
Sprawdź strukturę NBT chunków
"""
import struct
import zlib
import sys

class NBTReader:
    def __init__(self, data):
        self.data = data
        self.pos = 0
    
    def read_byte(self):
        val = self.data[self.pos]
        self.pos += 1
        return val
    
    def read_short(self):
        val = struct.unpack('>h', self.data[self.pos:self.pos+2])[0]
        self.pos += 2
        return val
    
    def read_int(self):
        val = struct.unpack('>i', self.data[self.pos:self.pos+4])[0]
        self.pos += 4
        return val
    
    def read_string(self):
        length = self.read_short()
        if length < 0 or self.pos + length > len(self.data):
            return None
        val = self.data[self.pos:self.pos+length].decode('utf-8', errors='ignore')
        self.pos += length
        return val
    
    def skip_type(self, type_id):
        if type_id == 1:  # Byte
            self.pos += 1
        elif type_id == 2:  # Short
            self.pos += 2
        elif type_id == 3:  # Int
            self.pos += 4
        elif type_id == 4:  # Long
            self.pos += 8
        elif type_id == 5:  # Float
            self.pos += 4
        elif type_id == 6:  # Double
            self.pos += 8
        elif type_id == 7:  # Byte Array
            length = self.read_int()
            self.pos += length
        elif type_id == 8:  # String
            self.read_string()
        elif type_id == 9:  # List
            elem_type = self.read_byte()
            length = self.read_int()
            for _ in range(length):
                if elem_type == 10:
                    self.read_compound()
                else:
                    self.skip_type(elem_type)
        elif type_id == 10:  # Compound
            self.read_compound()
        elif type_id == 11:  # Int Array
            length = self.read_int()
            self.pos += length * 4
    
    def read_compound(self):
        while True:
            if self.pos >= len(self.data):
                return
            type_id = self.read_byte()
            if type_id == 0:
                return
            name = self.read_string()
            self.skip_type(type_id)
    
    def analyze_structure(self):
        """Analizuje strukturę główną NBT"""
        try:
            root_type = self.read_byte()
            if root_type != 10:
                return f"Root type={root_type} (expected 10)"
            
            root_name = self.read_string()
            result = [f"Root: '{root_name}' (type={root_type})"]
            
            # Czytaj zawartość root
            while self.pos < len(self.data):
                type_id = self.read_byte()
                if type_id == 0:
                    break
                name = self.read_string()
                
                if name == "Level" and type_id == 10:
                    result.append(f"  Level: COMPOUND")
                    level_result = self.analyze_level()
                    result.extend([f"    {r}" for r in level_result])
                    break
                else:
                    self.skip_type(type_id)
            
            return "\n".join(result)
        except Exception as e:
            return f"ERROR: {e} at pos {self.pos}"
    
    def analyze_level(self):
        """Analizuje zawartość Level"""
        result = []
        try:
            while self.pos < len(self.data):
                type_id = self.read_byte()
                if type_id == 0:
                    break
                name = self.read_string()
                
                if name == "Sections" and type_id == 9:
                    elem_type = self.read_byte()
                    length = self.read_int()
                    result.append(f"Sections: LIST of {length} elements (type={elem_type})")
                    # Sprawdź pierwszą sekcję
                    if length > 0 and elem_type == 10:
                        section_result = self.analyze_section()
                        result.extend([f"      {r}" for r in section_result])
                    return result
                else:
                    self.skip_type(type_id)
        except Exception as e:
            result.append(f"ERROR: {e}")
        return result
    
    def analyze_section(self):
        """Analizuje pierwszą sekcję"""
        result = []
        has_blocks = False
        try:
            while self.pos < len(self.data):
                type_id = self.read_byte()
                if type_id == 0:
                    break
                name = self.read_string()
                
                if name == "Blocks" and type_id == 7:
                    length = self.read_int()
                    has_blocks = True
                    result.append(f"Blocks: byte[{length}]")
                    # Sprawdź czy są bloki z modów
                    mod_blocks = 0
                    max_id = 0
                    for i in range(length):
                        b = self.data[self.pos + i]
                        block_id = b if b >= 0 else b + 256
                        if block_id > max_id:
                            max_id = block_id
                        if block_id > 175 and block_id != 0:
                            mod_blocks += 1
                    result.append(f"  Max block ID: {max_id}")
                    result.append(f"  Mod blocks (ID>175): {mod_blocks}")
                    self.pos += length
                else:
                    self.skip_type(type_id)
        except Exception as e:
            result.append(f"ERROR: {e}")
        
        if not has_blocks:
            result.append("No Blocks array found!")
        
        return result

def decompress_zlib(data):
    try:
        return zlib.decompress(data)
    except:
        return None

def analyze_first_chunk(region_path):
    """Analizuje pierwszy niepusty chunk w regionie"""
    with open(region_path, 'rb') as f:
        header = f.read(4096)
        timestamps = f.read(4096)
        
        for chunk_z in range(32):
            for chunk_x in range(32):
                index = chunk_x + chunk_z * 32
                offset = ((header[index * 4] << 16) | 
                         (header[index * 4 + 1] << 8) | 
                         header[index * 4 + 2])
                sector_count = header[index * 4 + 3]
                
                if offset == 0 or sector_count == 0:
                    continue
                
                f.seek(offset * 4096)
                length = struct.unpack('>I', f.read(4))[0]
                compression = f.read(1)[0]
                
                if compression != 2:
                    continue
                
                compressed = f.read(length - 1)
                data = decompress_zlib(compressed)
                
                if data:
                    print(f"Chunk {chunk_x},{chunk_z}:")
                    reader = NBTReader(data)
                    print(reader.analyze_structure())
                    return

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Użycie: python check_nbt_structure.py <region.mca>")
        sys.exit(1)
    
    analyze_first_chunk(sys.argv[1])
