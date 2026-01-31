"""
Konwerter JSON voxel grid na format .schematic (Minecraft 1.7.10).
Obsługuje bloki vanilla i podstawowe Tile Entities.
"""

import json
import struct
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from minecraft_map_parser.nbt_writer import (
    NBTWriter, write_nbt_gzipped, create_short, create_string, 
    create_byte_array, create_int, create_compound, create_list
)


@dataclass
class Voxel:
    """Reprezentacja pojedynczego voksela."""
    x: int
    y: int
    z: int
    block: str
    properties: Optional[Dict[str, Any]] = None
    nbt: Optional[Dict[str, Any]] = None
    purpose: Optional[str] = None


# Mapowanie nazw bloków na ID i metadata dla MC 1.7.10
BLOCK_ID_MAP = {
    # Podstawowe bloki
    "minecraft:air": (0, 0),
    "minecraft:stone": (1, 0),
    "minecraft:grass": (2, 0),
    "minecraft:dirt": (3, 0),
    "minecraft:cobblestone": (4, 0),
    "minecraft:planks": (5, 0),
    "minecraft:bedrock": (7, 0),
    "minecraft:sand": (12, 0),
    "minecraft:gravel": (13, 0),
    "minecraft:gold_ore": (14, 0),
    "minecraft:iron_ore": (15, 0),
    "minecraft:coal_ore": (16, 0),
    "minecraft:log": (17, 0),
    "minecraft:leaves": (18, 0),
    "minecraft:glass": (20, 0),
    "minecraft:lapis_ore": (21, 0),
    "minecraft:lapis_block": (22, 0),
    "minecraft:sandstone": (24, 0),
    "minecraft:wool": (35, 0),
    "minecraft:yellow_flower": (37, 0),
    "minecraft:red_flower": (38, 0),
    "minecraft:brown_mushroom": (39, 0),
    "minecraft:red_mushroom": (40, 0),
    "minecraft:gold_block": (41, 0),
    "minecraft:iron_block": (42, 0),
    "minecraft:stone_slab": (44, 0),
    "minecraft:brick_block": (45, 0),
    "minecraft:tnt": (46, 0),
    "minecraft:bookshelf": (47, 0),
    "minecraft:mossy_cobblestone": (48, 0),
    "minecraft:obsidian": (49, 0),
    "minecraft:torch": (50, 0),
    "minecraft:fire": (51, 0),
    "minecraft:mob_spawner": (52, 0),
    "minecraft:oak_stairs": (53, 0),
    "minecraft:chest": (54, 0),
    "minecraft:diamond_ore": (56, 0),
    "minecraft:diamond_block": (57, 0),
    "minecraft:crafting_table": (58, 0),
    "minecraft:furnace": (61, 0),
    "minecraft:lit_furnace": (62, 0),
    "minecraft:ladder": (65, 0),
    "minecraft:rail": (66, 0),
    "minecraft:stone_stairs": (67, 0),
    "minecraft:lever": (69, 0),
    "minecraft:stone_pressure_plate": (70, 0),
    "minecraft:wooden_pressure_plate": (72, 0),
    "minecraft:redstone_ore": (73, 0),
    "minecraft:lit_redstone_ore": (74, 0),
    "minecraft:redstone_torch": (76, 0),  # lit (zapalona, domyślna)
    "minecraft:unlit_redstone_torch": (75, 0),
    "minecraft:redstone_torch_lit": (76, 0),
    "minecraft:stone_button": (77, 0),
    "minecraft:snow": (80, 0),
    "minecraft:ice": (79, 0),
    "minecraft:snow_block": (80, 0),
    "minecraft:cactus": (81, 0),
    "minecraft:clay": (82, 0),
    "minecraft:fence": (85, 0),
    "minecraft:pumpkin": (86, 0),
    "minecraft:netherrack": (87, 0),
    "minecraft:soul_sand": (88, 0),
    "minecraft:glowstone": (89, 0),
    "minecraft:lit_pumpkin": (91, 0),
    "minecraft:stained_glass": (95, 0),
    "minecraft:trapdoor": (96, 0),
    "minecraft:stone_brick": (98, 0),
    "minecraft:iron_bars": (101, 0),
    "minecraft:glass_pane": (102, 0),
    "minecraft:melon_block": (103, 0),
    "minecraft:vines": (106, 0),
    "minecraft:fence_gate": (107, 0),
    "minecraft:brick_stairs": (108, 0),
    "minecraft:stone_brick_stairs": (109, 0),
    "minecraft:mycelium": (110, 0),
    "minecraft:lily_pad": (111, 0),
    "minecraft:nether_brick": (112, 0),
    "minecraft:nether_brick_fence": (113, 0),
    "minecraft:nether_brick_stairs": (114, 0),
    "minecraft:enchanting_table": (116, 0),
    "minecraft:end_portal_frame": (120, 0),
    "minecraft:end_stone": (121, 0),
    "minecraft:dragon_egg": (122, 0),
    "minecraft:redstone_lamp": (123, 0),
    "minecraft:lit_redstone_lamp": (124, 0),
    "minecraft:wooden_slab": (126, 0),
    "minecraft:sandstone_stairs": (128, 0),
    "minecraft:emerald_ore": (129, 0),
    "minecraft:ender_chest": (130, 0),
    "minecraft:emerald_block": (133, 0),
    "minecraft:spruce_stairs": (134, 0),
    "minecraft:birch_stairs": (135, 0),
    "minecraft:jungle_stairs": (136, 0),
    "minecraft:beacon": (138, 0),
    "minecraft:cobblestone_wall": (139, 0),
    "minecraft:wooden_button": (143, 0),
    "minecraft:anvil": (145, 0),
    "minecraft:trapped_chest": (146, 0),
    "minecraft:light_weighted_pressure_plate": (147, 0),
    "minecraft:heavy_weighted_pressure_plate": (148, 0),
    "minecraft:daylight_detector": (151, 0),
    "minecraft:redstone_block": (152, 0),
    "minecraft:quartz_ore": (153, 0),
    "minecraft:hopper": (154, 0),
    "minecraft:quartz_block": (155, 0),
    "minecraft:quartz_stairs": (156, 0),
    "minecraft:activator_rail": (157, 0),
    "minecraft:dropper": (158, 0),
    "minecraft:stained_hardened_clay": (159, 0),
    "minecraft:stained_glass_pane": (160, 0),
    "minecraft:leaves2": (161, 0),
    "minecraft:log2": (162, 0),
    "minecraft:acacia_stairs": (163, 0),
    "minecraft:dark_oak_stairs": (164, 0),
    "minecraft:hay_block": (170, 0),
    "minecraft:carpet": (171, 0),
    "minecraft:hardened_clay": (172, 0),
    "minecraft:coal_block": (173, 0),
    "minecraft:packed_ice": (174, 0),
    "minecraft:double_plant": (175, 0),
    
    # Redstone i mechanizmy
    "minecraft:redstone_wire": (55, 0),
    "minecraft:repeater": (93, 0),  # unpowered
    "minecraft:unpowered_repeater": (93, 0),
    "minecraft:powered_repeater": (94, 0),
    "minecraft:comparator": (149, 0),  # unpowered
    "minecraft:unpowered_comparator": (149, 0),
    "minecraft:powered_comparator": (150, 0),
    "minecraft:command_block": (137, 0),
    "minecraft:dispenser": (23, 0),
    "minecraft:noteblock": (25, 0),
    "minecraft:piston": (33, 0),
    "minecraft:sticky_piston": (29, 0),
    "minecraft:tripwire_hook": (132, 0),
}

# Mapowanie kierunków na metadata
def get_direction_meta(facing: str, block_type: str = "", powered: bool = False) -> int:
    """Konwertuje kierunek na wartość metadata."""
    # Dla repeaterów i comparatorów (0-3)
    if block_type in ["repeater", "comparator"]:
        directions = {
            "south": 0,
            "west": 1, 
            "north": 2,
            "east": 3,
        }
        return directions.get(facing, 0)
    
    # Dla dropper/dispenser/command_block (0-5)
    if block_type in ["dropper", "dispenser", "command_block"]:
        directions = {
            "down": 0,
            "up": 1,
            "north": 2,
            "south": 3,
            "west": 4,
            "east": 5,
        }
        return directions.get(facing, 0)
    
    # Dla torch
    if block_type == "torch":
        if facing == "up":
            return 5  # Standing torch
        directions = {
            "east": 1,
            "west": 2,
            "south": 3,
            "north": 4,
        }
        return directions.get(facing, 5)
    
    # Dla lever
    if block_type == "lever":
        directions = {
            "south": 1,
            "north": 2,
            "west": 3,
            "east": 4,
        }
        base_meta = directions.get(facing, 6)
        # Add powered flag only if explicitly requested
        if powered:
            base_meta |= 0x8
        return base_meta
    
    return 0


def get_repeater_delay_meta(delay: int) -> int:
    """Konwertuje opóźnienie repeatera na metadata."""
    # Delay 1-4 -> meta 0, 4, 8, 12 (dodane do kierunku)
    return max(0, min(3, delay - 1)) * 4


def get_comparator_mode_meta(mode: str) -> int:
    """Konwertuje tryb komparatora na metadata."""
    # compare = 0, subtract = 1
    return 1 if mode == "subtract" else 0


def parse_voxel_grid(json_path: Path) -> Tuple[List[Voxel], Dict]:
    """Parsuje plik JSON z voxel grid."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    voxels = []
    
    # Sprawdź czy to format z sekcjami (voxel_grid.json)
    if "sections" in data:
        for section_name, section_data in data["sections"].items():
            if "voxels" in section_data:
                for v in section_data["voxels"]:
                    voxel = Voxel(
                        x=v["x"],
                        y=v["y"],
                        z=v["z"],
                        block=v["block"],
                        properties=v.get("properties"),
                        nbt=v.get("nbt"),
                        purpose=v.get("purpose")
                    )
                    voxels.append(voxel)
    # Format płaski (lista voxeli)
    elif "voxels" in data:
        for v in data["voxels"]:
            voxel = Voxel(
                x=v["x"],
                y=v["y"],
                z=v["z"],
                block=v["block"],
                properties=v.get("properties"),
                nbt=v.get("nbt"),
                purpose=v.get("purpose")
            )
            voxels.append(voxel)
    
    return voxels, data


def convert_to_schematic(voxels: List[Voxel], metadata: Dict = None) -> bytes:
    """Konwertuje listę voxeli na format .schematic (NBT gzipped)."""
    
    if not voxels:
        raise ValueError("Brak voxeli do konwersji")
    
    # Znajdź zakres współrzędnych
    min_x = min(v.x for v in voxels)
    max_x = max(v.x for v in voxels)
    min_y = min(v.y for v in voxels)
    max_y = max(v.y for v in voxels)
    min_z = min(v.z for v in voxels)
    max_z = max(v.z for v in voxels)
    
    # Wymiary schematica (short)
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    length = max_z - min_z + 1
    
    print(f"Schematic dimensions: {width}x{height}x{length}")
    print(f"Offset: ({min_x}, {min_y}, {min_z})")
    
    # Inicjalizuj tablice bloków i danych
    blocks = bytearray(width * height * length)
    data = bytearray(width * height * length)
    
    # Tile entities
    tile_entities = []
    
    # Wypełnij tablice
    for voxel in voxels:
        # Relatywne współrzędne w schematicu
        rx = voxel.x - min_x
        ry = voxel.y - min_y
        rz = voxel.z - min_z
        
        # Indeks w tablicy (Y is top-to-bottom in schematic)
        index = ry * width * length + rz * width + rx
        
        # Pobierz ID bloku
        if voxel.block not in BLOCK_ID_MAP:
            raise ValueError(f"Unknown block: {voxel.block}. Add it to BLOCK_ID_MAP or check the JSON.")
        block_id, meta = BLOCK_ID_MAP[voxel.block]
        
        # Zastosuj właściwości
        if voxel.properties:
            facing = voxel.properties.get("facing")
            block_type = voxel.block.split(":")[-1]
            
            if "repeater" in block_type and "delay" in voxel.properties:
                direction_meta = get_direction_meta(facing, "repeater")
                delay_meta = get_repeater_delay_meta(voxel.properties["delay"])
                meta = direction_meta + delay_meta
            elif "comparator" in block_type:
                direction_meta = get_direction_meta(facing, "comparator")
                mode_meta = get_comparator_mode_meta(voxel.properties.get("mode", "compare"))
                meta = direction_meta + mode_meta
            elif "dropper" in block_type or "command_block" in block_type:
                meta = get_direction_meta(facing, "dropper")
            elif "torch" in block_type:
                meta = get_direction_meta(facing, "torch")
            elif "lever" in block_type:
                powered = voxel.properties.get("powered", False)
                meta = get_direction_meta(facing, "lever", powered=powered)
        
        blocks[index] = block_id & 0xFF
        data[index] = meta & 0xFF
        
        # Dodaj Tile Entity jeśli potrzebne
        if voxel.nbt:
            te = create_tile_entity(voxel, rx, ry, rz)
            if te:
                tile_entities.append(te)
    
    # Przygotuj dane NBT dla schematica
    schematic_data = {}
    
    # Wymiary (short)
    schematic_data["Width"] = create_short(width)
    schematic_data["Height"] = create_short(height)
    schematic_data["Length"] = create_short(length)
    
    # Materials
    schematic_data["Materials"] = create_string("Alpha")
    
    # Bloki i dane
    schematic_data["Blocks"] = create_byte_array(bytes(blocks))
    schematic_data["Data"] = create_byte_array(bytes(data))
    
    # Tile Entities
    if tile_entities:
        schematic_data["TileEntities"] = create_list(tile_entities)
    else:
        schematic_data["TileEntities"] = create_list([])
    
    # Entities (pusta lista)
    schematic_data["Entities"] = create_list([])
    
    # Zapisz offsety dla odtworzenia oryginalnych współrzędnych przy wstawianiu
    schematic_data["WEOffsetX"] = create_int(min_x)
    schematic_data["WEOffsetY"] = create_int(min_y)
    schematic_data["WEOffsetZ"] = create_int(min_z)
    
    # Zapisz do NBT
    return write_nbt_gzipped("Schematic", NBTWriter.TAG_COMPOUND, schematic_data)


# Mapowanie nazw itemów na ID (MC 1.7.10)
ITEM_ID_MAP = {
    "minecraft:cobblestone": 4,
    "minecraft:stone": 1,
    "minecraft:dirt": 3,
    "minecraft:sand": 12,
    "minecraft:gravel": 13,
    "minecraft:gold_ingot": 266,
    "minecraft:iron_ingot": 265,
    "minecraft:diamond": 264,
    "minecraft:emerald": 388,
    "minecraft:redstone": 331,
    "minecraft:coal": 263,
    "minecraft:stick": 280,
    "minecraft:planks": 5,
    "minecraft:log": 17,
}


def item_name_to_id(name: str) -> int:
    """Konwertuje nazwę itemu na ID (1.7.10)."""
    if isinstance(name, int):
        return name
    # Jeśli to już liczba w stringu
    if name.isdigit():
        return int(name)
    return ITEM_ID_MAP.get(name, 4)  # Default to cobblestone


def create_tile_entity(voxel: Voxel, x: int, y: int, z: int) -> tuple:
    """Tworzy Tile Entity dla schematica (format MC 1.7.10)."""
    if not voxel.nbt:
        return None
    
    block_type = voxel.block.split(":")[-1]
    
    # Określ typ Tile Entity
    te_id = None
    if "dropper" in block_type or "dispenser" in block_type:
        te_id = "Trap"
    elif "command_block" in block_type:
        te_id = "Control"
    elif "chest" in block_type:
        te_id = "Chest"
    elif "furnace" in block_type:
        te_id = "Furnace"
    elif "hopper" in block_type:
        te_id = "Hopper"
    elif "noteblock" in block_type:
        te_id = "Music"
    
    if not te_id:
        return None
    
    # Buduj dane TE
    te_data = {
        "id": create_string(te_id),
        "x": create_int(x),
        "y": create_int(y),
        "z": create_int(z),
    }
    
    # Dodaj dodatkowe dane z NBT voxela
    if voxel.nbt:
        for key, value in voxel.nbt.items():
            if key == "Items" and isinstance(value, list):
                # Konwertuj items - w 1.7.10 ID to SHORT, nie STRING
                items = []
                for i, item in enumerate(value):
                    item_id = item_name_to_id(item.get("id", "minecraft:cobblestone"))
                    item_compound = {
                        "id": create_short(item_id),  # SHORT dla 1.7.10
                        "Count": (NBTWriter.TAG_BYTE, item.get("Count", 1)),
                        "Slot": (NBTWriter.TAG_BYTE, item.get("Slot", i)),
                        "Damage": create_short(item.get("Damage", 0)),
                    }
                    items.append((NBTWriter.TAG_COMPOUND, item_compound))
                te_data["Items"] = create_list(items)
            elif key == "Command":
                te_data["Command"] = create_string(value)
            elif key == "CustomName":
                te_data["CustomName"] = create_string(value)
    
    return (NBTWriter.TAG_COMPOUND, te_data)


def convert_json_to_schematic(input_path: Path, output_path: Path):
    """Główna funkcja konwertująca JSON na schematic."""
    print(f"Konwertowanie: {input_path}")
    
    # Parsuj JSON
    voxels, metadata = parse_voxel_grid(input_path)
    print(f"Znaleziono {len(voxels)} voxeli")
    
    # Konwertuj
    schematic_data = convert_to_schematic(voxels, metadata)
    
    # Zapisz
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(schematic_data)
    
    print(f"Zapisano schematic: {output_path}")
    print(f"Rozmiar pliku: {len(schematic_data)} bajtów")
    
    return output_path


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Użycie: python json_to_schematic.py <input.json> <output.schematic>")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    
    convert_json_to_schematic(input_path, output_path)
