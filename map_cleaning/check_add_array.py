#!/usr/bin/env python3
"""
Sprawdź czy chunki mają tablicę Add (dla bloków o ID > 255)
"""
import struct
import zlib
import sys

def decompress_zlib(data):
    try:
        return zlib.decompress(data)
    except:
        return None

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
        if type_id == 1:
            self.pos += 1
        elif type_id == 2:
            self.pos += 2
        elif type_id == 3:
            self.pos += 4
        elif type_id == 4:
            self.pos += 8
        elif type_id == 5:
            self.pos += 4
        elif type_id == 6:
            self.pos += 8
        elif type_id == 7:
            length = self.read_int()
            self.pos += length
        elif type_id == 8:
            self.read_string()
        elif type_id == 9:
            elem_type = self.read_byte()
            length = self.read_int()
            for _ in range(length):
                if elem_type == 10:
                    self.read_compound()
                else:
                    self.skip_type(elem_type)
        elif type_id == 10:
            self.read_compound()
        elif type_id == 11:
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
    
    def check_sections(self):
        """Sprawdza sekcje pod kątem tablicy Add"""
        try:
            root_type = self.read_byte()
            if root_type != 10:
                return "Invalid root type"
            
            root_name = self.read_string()
            
            while self.pos < len(self.data):
                type_id = self.read_byte()
                if type_id == 0:
                    break
                name = self.read_string()
                
                if name == "Level" and type_id == 10:
                    return self.check_level()
                else:
                    self.skip_type(type_id)
            
            return "No Level found"
        except Exception as e:
            return f"Error: {e}"
    
    def check_level(self):
        while self.pos < len(self.data):
            type_id = self.read_byte()
            if type_id == 0:
                break
            name = self.read_string()
            
            if name == "Sections" and type_id == 9:
                return self.check_sections_list()
            else:
                self.skip_type(type_id)
        return "No Sections found"
    
    def check_sections_list(self):
        elem_type = self.read_byte()
        length = self.read_int()
        
        sections_with_add = 0
        sections_without_blocks = 0
        total_mod_blocks = 0
        
        for _ in range(length):
            if elem_type == 10:
                has_add = False
                has_blocks = False
                mod_blocks = 0
                
                while self.pos < len(self.data):
                    type_id = self.read_byte()
                    if type_id == 0:
                        break
                    name = self.read_string()
                    
                    if name == "Add" and type_id == 7:
                        has_add = True
                        length = self.read_int()
                        self.pos += length
                    elif name == "Blocks" and type_id == 7:
                        has_blocks = True
                        length = self.read_int()
                        for i in range(length):
                            b = self.data[self.pos + i]
                            block_id = b if b >= 0 else b + 256
                            if block_id > 175 and block_id != 0:
                                mod_blocks += 1
                        self.pos += length
                    else:
                        self.skip_type(type_id)
                
                if has_add:
                    sections_with_add += 1
                if not has_blocks:
                    sections_without_blocks += 1
                total_mod_blocks += mod_blocks
        
        return f"Sections: {length}, z Add: {sections_with_add}, mod blocks: {total_mod_blocks}"

def analyze_region(region_path):
    with open(region_path, 'rb') as f:
        header = f.read(4096)
        timestamps = f.read(4096)
        
        chunks_with_add = 0
        total_chunks = 0
        
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
                    total_chunks += 1
                    reader = NBTReader(data)
                    result = reader.check_sections()
                    if "Add" in result:
                        chunks_with_add += 1
                        print(f"Chunk {chunk_x},{chunk_z}: {result}")
                    elif total_chunks <= 3:
                        print(f"Chunk {chunk_x},{chunk_z}: {result}")
        
        print(f"\nTotal chunks: {total_chunks}, z Add: {chunks_with_add}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Użycie: python check_add_array.py <region.mca>")
        sys.exit(1)
    
    analyze_region(sys.argv[1])
