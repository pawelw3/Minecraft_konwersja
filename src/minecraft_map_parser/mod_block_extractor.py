"""
Ekstraktor bloków i tile entities pochodzących z modów.
Identyfikuje bloki vanilla vs modowane.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set, Tuple, Any
from collections import defaultdict

from .anvil_parser import AnvilParser, ChunkData
from .nbt_parser import NBTTag


# Lista znanych ID bloków vanilla w Minecraft 1.7.10
VANILLA_BLOCKS: Set[int] = set([
    0,    # air
    1,    # stone
    2,    # grass
    3,    # dirt
    4,    # cobblestone
    5,    # planks
    6,    # sapling
    7,    # bedrock
    8,    # flowing_water
    9,    # water
    10,   # flowing_lava
    11,   # lava
    12,   # sand
    13,   # gravel
    14,   # gold_ore
    15,   # iron_ore
    16,   # coal_ore
    17,   # log
    18,   # leaves
    19,   # sponge
    20,   # glass
    21,   # lapis_ore
    22,   # lapis_block
    23,   # dispenser
    24,   # sandstone
    25,   # noteblock
    26,   # bed
    27,   # golden_rail
    28,   # detector_rail
    29,   # sticky_piston
    30,   # web
    31,   # tallgrass
    32,   # deadbush
    33,   # piston
    34,   # piston_head
    35,   # wool
    36,   # piston_extension
    37,   # yellow_flower
    38,   # red_flower
    39,   # brown_mushroom
    40,   # red_mushroom
    41,   # gold_block
    42,   # iron_block
    43,   # double_stone_slab
    44,   # stone_slab
    45,   # brick_block
    46,   # tnt
    47,   # bookshelf
    48,   # mossy_cobblestone
    49,   # obsidian
    50,   # torch
    51,   # fire
    52,   # mob_spawner
    53,   # oak_stairs
    54,   # chest
    55,   # redstone_wire
    56,   # diamond_ore
    57,   # diamond_block
    58,   # crafting_table
    59,   # wheat
    60,   # farmland
    61,   # furnace
    62,   # lit_furnace
    63,   # standing_sign
    64,   # wooden_door
    65,   # ladder
    66,   # rail
    67,   # stone_stairs
    68,   # wall_sign
    69,   # lever
    70,   # stone_pressure_plate
    71,   # iron_door
    72,   # wooden_pressure_plate
    73,   # redstone_ore
    74,   # lit_redstone_ore
    75,   # unlit_redstone_torch
    76,   # redstone_torch
    77,   # stone_button
    78,   # snow_layer
    79,   # ice
    80,   # snow
    81,   # cactus
    82,   # clay
    83,   # reeds
    84,   # jukebox
    85,   # fence
    86,   # pumpkin
    87,   # netherrack
    88,   # soul_sand
    89,   # glowstone
    90,   # portal
    91,   # lit_pumpkin
    92,   # cake
    93,   # unpowered_repeater
    94,   # powered_repeater
    95,   # stained_glass
    96,   # trapdoor
    97,   # monster_egg
    98,   # stonebrick
    99,   # brown_mushroom_block
    100,  # red_mushroom_block
    101,  # iron_bars
    102,  # glass_pane
    103,  # melon_block
    104,  # pumpkin_stem
    105,  # melon_stem
    106,  # vine
    107,  # fence_gate
    108,  # brick_stairs
    109,  # stone_brick_stairs
    110,  # mycelium
    111,  # waterlily
    112,  # nether_brick
    113,  # nether_brick_fence
    114,  # nether_brick_stairs
    115,  # nether_wart
    116,  # enchanting_table
    117,  # brewing_stand
    118,  # cauldron
    119,  # end_portal
    120,  # end_portal_frame
    121,  # end_stone
    122,  # dragon_egg
    123,  # redstone_lamp
    124,  # lit_redstone_lamp
    125,  # double_wooden_slab
    126,  # wooden_slab
    127,  # cocoa
    128,  # sandstone_stairs
    129,  # emerald_ore
    130,  # ender_chest
    131,  # tripwire_hook
    132,  # tripwire
    133,  # emerald_block
    134,  # spruce_stairs
    135,  # birch_stairs
    136,  # jungle_stairs
    137,  # command_block
    138,  # beacon
    139,  # cobblestone_wall
    140,  # flower_pot
    141,  # carrots
    142,  # potatoes
    143,  # wooden_button
    144,  # skull
    145,  # anvil
    146,  # trapped_chest
    147,  # light_weighted_pressure_plate
    148,  # heavy_weighted_pressure_plate
    149,  # unpowered_comparator
    150,  # powered_comparator
    151,  # daylight_detector
    152,  # redstone_block
    153,  # quartz_ore
    154,  # hopper
    155,  # quartz_block
    156,  # quartz_stairs
    157,  # activator_rail
    158,  # dropper
    159,  # stained_hardened_clay
    160,  # stained_glass_pane
    161,  # leaves2
    162,  # log2
    163,  # acacia_stairs
    164,  # dark_oak_stairs
    165,  # slime
    166,  # barrier (ale to vanilla)
    167,  # iron_trapdoor
    168,  # prismarine
    169,  # sea_lantern
    170,  # hay_block
    171,  # carpet
    172,  # hardened_clay
    173,  # coal_block
    174,  # packed_ice
    175,  # double_plant
    176,  # standing_banner
    177,  # wall_banner
    178,  # daylight_detector_inverted
    179,  # red_sandstone
    180,  # red_sandstone_stairs
    181,  # double_stone_slab2
    182,  # stone_slab2
])


# Znane tile entities vanilla
VANILLA_TILE_ENTITIES: Set[str] = set([
    'Sign',
    'MobSpawner',
    'Chest',
    'EnderChest',
    'Furnace',
    'Dropper',
    'Hopper',
    'Dispenser',
    'Trap',
    'EnchantTable',
    'RecordPlayer',  # Jukebox
    'Piston',
    'Banner',
    'Beacon',
    'Skull',
    'Control',
    'Comparator',
    'FlowerPot',
    'BrewingStand',
    'Note',
])


@dataclass
class BlockInfo:
    """Informacje o pojedynczym bloku."""
    x: int
    y: int
    z: int
    block_id: int
    metadata: int
    is_modded: bool
    mod_name: Optional[str] = None
    block_name: Optional[str] = None
    
    @property
    def is_vanilla(self) -> bool:
        return not self.is_modded


@dataclass  
class TileEntityInfo:
    """Informacje o tile entity."""
    x: int
    y: int
    z: int
    id: str
    is_modded: bool
    mod_name: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_vanilla(self) -> bool:
        return not self.is_modded


@dataclass
class EntityInfo:
    """Informacje o encji (mob, przedmiot)."""
    x: float
    y: float
    z: float
    id: str
    is_modded: bool
    mod_name: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_vanilla(self) -> bool:
        return not self.is_modded


class ModBlockExtractor:
    """
    Ekstraktor bloków i tile entities z modów.
    """
    
    def __init__(self, additional_vanilla_blocks: Optional[Set[int]] = None,
                 additional_vanilla_tile_entities: Optional[Set[str]] = None):
        self.vanilla_blocks = VANILLA_BLOCKS.copy()
        self.vanilla_tile_entities = VANILLA_TILE_ENTITIES.copy()
        
        if additional_vanilla_blocks:
            self.vanilla_blocks.update(additional_vanilla_blocks)
        if additional_vanilla_tile_entities:
            self.vanilla_tile_entities.update(additional_vanilla_tile_entities)
        
        # Statystyki
        self.stats = {
            'modded_blocks': 0,
            'vanilla_blocks': 0,
            'modded_tile_entities': 0,
            'vanilla_tile_entities': 0,
            'modded_entities': 0,
            'vanilla_entities': 0,
        }
    
    def is_vanilla_block(self, block_id: int) -> bool:
        """Sprawdza czy blok jest vanilla."""
        return block_id in self.vanilla_blocks
    
    def is_vanilla_tile_entity(self, entity_id: str) -> bool:
        """Sprawdza czy tile entity jest vanilla."""
        return entity_id in self.vanilla_tile_entities
    
    def is_vanilla_entity(self, entity_id: str) -> bool:
        """Sprawdza czy encja jest vanilla."""
        # Podstawowe encje vanilla
        vanilla_entities = {
            'Item', 'XPOrb', 'ThrownEgg', 'LeashKnot', 'Painting', 'Arrow',
            'Snowball', 'Fireball', 'SmallFireball', 'ThrownEnderpearl',
            'EyeOfEnderSignal', 'ThrownPotion', 'ThrownExpBottle', 'ItemFrame',
            'WitherSkull', 'PrimedTnt', 'FallingSand', 'FireworksRocketEntity',
            'Boat', 'MinecartRideable', 'MinecartChest', 'MinecartFurnace',
            'MinecartTNT', 'MinecartHopper', 'MinecartSpawner', 'MinecartCommandBlock',
            # Moby
            'Creeper', 'Skeleton', 'Spider', 'Giant', 'Zombie', 'Slime', 'Ghast',
            'PigZombie', 'Enderman', 'CaveSpider', 'Silverfish', 'Blaze', 'LavaSlime',
            'EnderDragon', 'WitherBoss', 'Bat', 'Pig', 'Sheep', 'Cow', 'Chicken',
            'Squid', 'Wolf', 'MushroomCow', 'SnowMan', 'Ozelot', 'VillagerGolem',
            'EntityHorse', 'Villager', 'Endermite', 'Guardian', 'Rabbit',
        }
        return entity_id in vanilla_entities
    
    def extract_mod_name_from_id(self, block_id: int) -> Optional[str]:
        """
        Próbuje wydobyć nazwę modu z ID bloku (heurystyka).
        W 1.7.10 ID modów zaczynają się zazwyczaj od ~170+ (po vanilla).
        """
        if block_id <= 175:
            return None
        
        # Heurystyczne odgadywanie modu na podstawie ID
        # To jest uproszczone - pełna lista wymagałaby zbadania plików modów
        ranges = [
            (256, 512, "IC2"),      # IndustrialCraft 2
            (512, 768, "BC"),       # BuildCraft
            (768, 1024, "RP2"),     # RedPower 2 (jeśli obecny)
            (1024, 1536, "TE"),     # Thermal Expansion
            (1536, 1792, "AE2"),    # Applied Energistics 2
            (1792, 2048, "MEK"),    # Mekanism
            (2048, 2304, "TC"),     # Tinkers' Construct
        ]
        
        for start, end, mod in ranges:
            if start <= block_id < end:
                return mod
        
        return "UNKNOWN_MOD"
    
    def extract_mod_name_from_tile_entity(self, entity_id: str) -> Optional[str]:
        """Próbuje wydobyć nazwę modu z ID tile entity."""
        # Najpierw sprawdź znane prefixy
        prefixes = {
            'AEMachine': 'AE2',
            'AEPart': 'AE2',
            'AEBlock': 'AE2',
            'appliedenergistics2': 'AE2',
            'Mekanism': 'Mekanism',
            'thermalexpansion': 'TE',
            'ThermalExpansion': 'TE',
            'CarpentersBlock': 'CarpentersBlocks',
            'Carpenters': 'CarpentersBlocks',
            'Railcraft': 'Railcraft',
            'RC': 'Railcraft',
            'IC2': 'IC2',
            'IC2Reactor': 'IC2',
            'IC2NuclearReactor': 'IC2',
            'BuildCraft': 'BC',
            'BC': 'BC',
            'Forestry': 'Forestry',
            'Thaumcraft': 'Thaumcraft',
            'TConstruct': 'TConstruct',
            'IronChest': 'IronChest',
            'EnderIO': 'EnderIO',
            'JABBA': 'JABBA',
            'LogisticsPipes': 'LP',
            'ProjRed': 'ProjectRed',
            'projectred': 'ProjectRed',
            'minefactoryreloaded': 'MFR',
            'opencomputers': 'OC',
            'ComputerCraft': 'CC',
            'savedMultipart': 'ForgeMicroblocks',
            'RCHiddenTile': 'Railcraft',
            'TileEntityCarpentersBlock': 'CarpentersBlocks',
            'tile.mannequin': 'StatuesMod',
            'tile.projectred': 'ProjectRed',
            'te': 'Unknown',  # te.mannequin - trudno stwierdzić
            'tile': 'Unknown',
        }
        
        for prefix, mod in prefixes.items():
            if entity_id.startswith(prefix):
                return mod
        
        # Dodatkowe sprawdzenia dla specyficznych patternów
        if 'projectred' in entity_id.lower():
            return 'ProjectRed'
        
        return "UNKNOWN_MOD"
    
    def parse_chunk_blocks(self, chunk: ChunkData, include_vanilla: bool = False) -> List[BlockInfo]:
        """
        Parsuje wszystkie bloki z chunka.
        Zwraca tylko bloki z modów (chyba że include_vanilla=True).
        """
        blocks = []
        sections = chunk.get_sections()
        
        for section in sections:
            if not isinstance(section, dict):
                continue
            
            # Y pozycja sekcji (0-15, każda to 16 bloków wysokości)
            y_base = section.get('Y', 0)
            if isinstance(y_base, NBTTag):
                y_base = y_base.value
            y_base = int(y_base) * 16
            
            # Dane bloków
            blocks_data = section.get('Blocks')
            add_data = section.get('Add')  # dodatkowe bity dla ID > 255
            meta_data = section.get('Data')  # metadata (4 bity na blok)
            
            # Rozpakuj NBTTag jeśli trzeba
            if isinstance(blocks_data, NBTTag):
                blocks_data = blocks_data.value
            if isinstance(add_data, NBTTag):
                add_data = add_data.value
            if isinstance(meta_data, NBTTag):
                meta_data = meta_data.value
            
            if blocks_data is None:
                continue
            
            # Upewnij się, że mamy bytes
            if isinstance(blocks_data, list):
                blocks_data = bytes(blocks_data)
            if add_data is not None and isinstance(add_data, list):
                add_data = bytes(add_data)
            if meta_data is not None and isinstance(meta_data, list):
                meta_data = bytes(meta_data)
            
            # Parsuj bloki
            for y in range(16):
                for z in range(16):
                    for x in range(16):
                        index = y * 256 + z * 16 + x
                        
                        # ID bloku (12 bitów)
                        block_id = blocks_data[index] & 0xFF
                        
                        # Dodatkowe bity (dla ID > 255)
                        if add_data is not None:
                            add_index = index // 2
                            if add_index < len(add_data):
                                if index % 2 == 0:
                                    block_id |= (add_data[add_index] & 0x0F) << 8
                                else:
                                    block_id |= (add_data[add_index] & 0xF0) << 4
                        
                        # Metadata (4 bity)
                        metadata = 0
                        if meta_data is not None:
                            meta_index = index // 2
                            if meta_index < len(meta_data):
                                if index % 2 == 0:
                                    metadata = meta_data[meta_index] & 0x0F
                                else:
                                    metadata = (meta_data[meta_index] >> 4) & 0x0F
                        
                        is_vanilla = self.is_vanilla_block(block_id)
                        
                        if is_vanilla and not include_vanilla:
                            continue
                        
                        global_x = chunk.x * 16 + x
                        global_y = y_base + y
                        global_z = chunk.z * 16 + z
                        
                        block_info = BlockInfo(
                            x=global_x,
                            y=global_y,
                            z=global_z,
                            block_id=block_id,
                            metadata=metadata,
                            is_modded=not is_vanilla,
                            mod_name=self.extract_mod_name_from_id(block_id) if not is_vanilla else None,
                        )
                        blocks.append(block_info)
                        
                        if is_vanilla:
                            self.stats['vanilla_blocks'] += 1
                        else:
                            self.stats['modded_blocks'] += 1
        
        return blocks
    
    def parse_chunk_tile_entities(self, chunk: ChunkData, include_vanilla: bool = False) -> List[TileEntityInfo]:
        """
        Parsuje tile entities z chunka.
        Zwraca tylko tile entities z modów (chyba że include_vanilla=True).
        """
        tile_entities = []
        raw_entities = chunk.get_tile_entities()
        
        for entity in raw_entities:
            if not isinstance(entity, dict):
                continue
            
            entity_id = entity.get('id', '')
            if isinstance(entity_id, NBTTag):
                entity_id = entity_id.value
            if isinstance(entity_id, bytes):
                entity_id = entity_id.decode('utf-8', errors='ignore')
            if not isinstance(entity_id, str):
                entity_id = str(entity_id) if entity_id else ''
            
            x = entity.get('x', 0)
            y = entity.get('y', 0)
            z = entity.get('z', 0)
            
            # Rozpakuj NBTTag jeśli trzeba
            if isinstance(x, NBTTag):
                x = x.value
            if isinstance(y, NBTTag):
                y = y.value
            if isinstance(z, NBTTag):
                z = z.value
            
            is_vanilla = self.is_vanilla_tile_entity(entity_id)
            
            if is_vanilla and not include_vanilla:
                continue
            
            # Pobierz surowe dane
            raw_data = {k: v for k, v in entity.items()}
            
            te_info = TileEntityInfo(
                x=x,
                y=y,
                z=z,
                id=entity_id,
                is_modded=not is_vanilla,
                mod_name=self.extract_mod_name_from_tile_entity(entity_id) if not is_vanilla else None,
                raw_data=raw_data,
            )
            tile_entities.append(te_info)
            
            if is_vanilla:
                self.stats['vanilla_tile_entities'] += 1
            else:
                self.stats['modded_tile_entities'] += 1
        
        return tile_entities
    
    def parse_chunk_entities(self, chunk: ChunkData, include_vanilla: bool = False) -> List[EntityInfo]:
        """
        Parsuje entities (moby, przedmioty) z chunka.
        Zwraca tylko entities z modów (chyba że include_vanilla=True).
        """
        entities = []
        raw_entities = chunk.get_entities()
        
        for entity in raw_entities:
            if not isinstance(entity, dict):
                continue
            
            entity_id = entity.get('id', '')
            if isinstance(entity_id, NBTTag):
                entity_id = entity_id.value
            if isinstance(entity_id, bytes):
                entity_id = entity_id.decode('utf-8', errors='ignore')
            if not isinstance(entity_id, str):
                entity_id = str(entity_id) if entity_id else ''
            
            # Pobierz pozycję
            pos = entity.get('Pos', [0.0, 0.0, 0.0])
            if isinstance(pos, NBTTag):
                pos = pos.value
            if isinstance(pos, list) and len(pos) >= 3:
                def extract_val(v):
                    if isinstance(v, NBTTag):
                        v = v.value
                    return float(v) if v is not None else 0.0
                x, y, z = extract_val(pos[0]), extract_val(pos[1]), extract_val(pos[2])
            else:
                x = y = z = 0.0
            
            is_vanilla = self.is_vanilla_entity(entity_id)
            
            if is_vanilla and not include_vanilla:
                continue
            
            # Pobierz surowe dane
            raw_data = {k: v for k, v in entity.items()}
            
            entity_info = EntityInfo(
                x=x,
                y=y,
                z=z,
                id=entity_id,
                is_modded=not is_vanilla,
                mod_name=None,  # Trudniejsze do ustalenia
                raw_data=raw_data,
            )
            entities.append(entity_info)
            
            if is_vanilla:
                self.stats['vanilla_entities'] += 1
            else:
                self.stats['modded_entities'] += 1
        
        return entities
    
    def extract_from_region(self, region_file: str, 
                           x_min: Optional[int] = None,
                           x_max: Optional[int] = None,
                           z_min: Optional[int] = None,
                           z_max: Optional[int] = None,
                           include_vanilla: bool = False,
                           include_entities: bool = False) -> Dict[str, List]:
        """
        Ekstrahuje dane z całego pliku regionu.
        Opcjonalnie ogranicza do podanego obszaru.
        """
        parser = AnvilParser(region_file)
        all_blocks = []
        all_tile_entities = []
        all_entities = []
        
        for chunk in parser.get_all_chunks():
            # Sprawdź czy chunk jest w obszarze
            chunk_x_min = chunk.x * 16
            chunk_x_max = chunk_x_min + 15
            chunk_z_min = chunk.z * 16
            chunk_z_max = chunk_z_min + 15
            
            if x_min is not None and chunk_x_max < x_min:
                continue
            if x_max is not None and chunk_x_min > x_max:
                continue
            if z_min is not None and chunk_z_max < z_min:
                continue
            if z_max is not None and chunk_z_min > z_max:
                continue
            
            # Ekstrahuj bloki
            blocks = self.parse_chunk_blocks(chunk, include_vanilla)
            for block in blocks:
                if x_min is not None and (block.x < x_min or block.x > x_max):
                    continue
                if z_min is not None and (block.z < z_min or block.z > z_max):
                    continue
                all_blocks.append(block)
            
            # Ekstrahuj tile entities
            tile_entities = self.parse_chunk_tile_entities(chunk, include_vanilla)
            for te in tile_entities:
                if x_min is not None and (te.x < x_min or te.x > x_max):
                    continue
                if z_min is not None and (te.z < z_min or te.z > z_max):
                    continue
                all_tile_entities.append(te)
            
            # Ekstrahuj entities
            if include_entities:
                entities = self.parse_chunk_entities(chunk, include_vanilla)
                for e in entities:
                    if x_min is not None and (e.x < x_min or e.x > x_max):
                        continue
                    if z_min is not None and (e.z < z_min or e.z > z_max):
                        continue
                    all_entities.append(e)
        
        return {
            'blocks': all_blocks,
            'tile_entities': all_tile_entities,
            'entities': all_entities,
        }
    
    def get_stats(self) -> Dict[str, int]:
        """Zwraca statystyki ekstrakcji."""
        return self.stats.copy()
    
    def reset_stats(self):
        """Resetuje statystyki."""
        self.stats = {
            'modded_blocks': 0,
            'vanilla_blocks': 0,
            'modded_tile_entities': 0,
            'vanilla_tile_entities': 0,
            'modded_entities': 0,
            'vanilla_entities': 0,
        }
