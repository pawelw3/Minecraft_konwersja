"""
Block Mappings for AE2 - 1.7.10 to 1.18.2

Mapowanie ID bloków i tile entities AE2.
Źródło: AE2_BLOCKS_AND_TE.md (Zadanie 1)
"""

from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class BlockMapping:
    """Reprezentuje mapowanie bloku między wersjami"""
    id_1710: str
    id_1182: str
    has_tile_entity: bool = False
    nbt_converter: Optional[str] = None  # Nazwa konwertera NBT
    notes: str = ""


# Mapowanie bloków AE2: 1.7.10 -> 1.18.2
BLOCK_MAPPINGS_1710_TO_1182: Dict[str, BlockMapping] = {
    # === CORE NETWORK BLOCKS ===
    "appliedenergistics2:tile.BlockController": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockController",
        id_1182="ae2:controller",
        has_tile_entity=True,
        nbt_converter="controller",
        notes="ME Controller - serce sieci"
    ),
    "appliedenergistics2:tile.BlockDrive": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockDrive",
        id_1182="ae2:drive",
        has_tile_entity=True,
        nbt_converter="drive",
        notes="ME Drive - 10 slotów na storage cells"
    ),
    "appliedenergistics2:tile.BlockChest": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockChest",
        id_1182="ae2:chest",
        has_tile_entity=True,
        nbt_converter="chest",
        notes="ME Chest - 1 slot cell + inventory"
    ),
    "appliedenergistics2:tile.BlockEnergyAcceptor": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockEnergyAcceptor",
        id_1182="ae2:energy_acceptor",
        has_tile_entity=True,
        nbt_converter="energy_acceptor",
        notes="Energy Acceptor - konwersja energii"
    ),
    "appliedenergistics2:tile.BlockEnergyCell": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockEnergyCell",
        id_1182="ae2:energy_cell",
        has_tile_entity=True,
        nbt_converter="energy_cell",
        notes="Energy Cell - magazyn energii"
    ),
    "appliedenergistics2:tile.BlockDenseEnergyCell": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockDenseEnergyCell",
        id_1182="ae2:dense_energy_cell",
        has_tile_entity=True,
        nbt_converter="energy_cell",
        notes="Dense Energy Cell - gęsty magazyn energii"
    ),
    
    # === CRAFTING SYSTEM ===
    "appliedenergistics2:tile.BlockCraftingUnit": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockCraftingUnit",
        id_1182="ae2:crafting_unit",
        has_tile_entity=True,
        nbt_converter="crafting_unit",
        notes="Crafting Unit - podstawowa jednostka CPU"
    ),
    "appliedenergistics2:tile.BlockCraftingStorage": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockCraftingStorage",
        id_1182="ae2:1k_crafting_storage",  # Rozpoznanie przez metadata
        has_tile_entity=True,
        nbt_converter="crafting_storage",
        notes="Crafting Storage - metadata 0=1k, 1=4k, 2=16k, 3=64k"
    ),
    "appliedenergistics2:tile.BlockCraftingMonitor": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockCraftingMonitor",
        id_1182="ae2:crafting_monitor",
        has_tile_entity=True,
        nbt_converter="crafting_monitor",
        notes="Crafting Monitor - wyświetlanie postępu"
    ),
    "appliedenergistics2:tile.BlockMolecularAssembler": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockMolecularAssembler",
        id_1182="ae2:molecular_assembler",
        has_tile_entity=True,
        nbt_converter="molecular_assembler",
        notes="Molecular Assembler - wykonywanie craftingu"
    ),
    
    # === INTERFACE & IO ===
    "appliedenergistics2:tile.BlockInterface": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockInterface",
        id_1182="ae2:interface",
        has_tile_entity=True,
        nbt_converter="interface",
        notes="ME Interface - wymiana itemów + patterny (1.7.10)"
    ),
    "appliedenergistics2:tile.BlockIOPort": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockIOPort",
        id_1182="ae2:io_port",
        has_tile_entity=True,
        nbt_converter="io_port",
        notes="IO Port - transfer między cellami"
    ),
    
    # === QUANTUM NETWORK ===
    "appliedenergistics2:tile.BlockQuantumRing": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockQuantumRing",
        id_1182="ae2:quantum_ring",
        has_tile_entity=True,
        nbt_converter="quantum_ring",
        notes="Quantum Ring - część multibloku"
    ),
    "appliedenergistics2:tile.BlockQuantumLinkChamber": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockQuantumLinkChamber",
        id_1182="ae2:quantum_link",
        has_tile_entity=True,
        nbt_converter="quantum_link",
        notes="Quantum Link Chamber - rdzeń mostu"
    ),
    
    # === SPATIAL IO ===
    "appliedenergistics2:tile.BlockSpatialIOPort": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockSpatialIOPort",
        id_1182="ae2:spatial_io_port",
        has_tile_entity=True,
        nbt_converter="spatial_io_port",
        notes="Spatial IO Port - zapis/odczyt przestrzeni"
    ),
    "appliedenergistics2:tile.BlockSpatialPylon": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockSpatialPylon",
        id_1182="ae2:spatial_pylon",
        has_tile_entity=True,
        nbt_converter="spatial_pylon",
        notes="Spatial Pylon - ramka struktury"
    ),
    
    # === UTILITY BLOCKS ===
    "appliedenergistics2:tile.BlockCharger": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockCharger",
        id_1182="ae2:charger",
        has_tile_entity=True,
        nbt_converter="charger",
        notes="Charger - ładowanie certus quartz"
    ),
    "appliedenergistics2:tile.BlockInscriber": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockInscriber",
        id_1182="ae2:inscriber",
        has_tile_entity=True,
        nbt_converter="inscriber",
        notes="Inscriber - tworzenie procesorów"
    ),
    "appliedenergistics2:tile.BlockVibrationChamber": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockVibrationChamber",
        id_1182="ae2:vibration_chamber",
        has_tile_entity=True,
        nbt_converter="vibration_chamber",
        notes="Vibration Chamber - generator AE"
    ),
    "appliedenergistics2:tile.BlockQuartzGrowthAccelerator": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockQuartzGrowthAccelerator",
        id_1182="ae2:quartz_growth_accelerator",
        has_tile_entity=True,
        nbt_converter="growth_accelerator",
        notes="Crystal Growth Accelerator - przyspieszanie wzrostu"
    ),
    "appliedenergistics2:tile.BlockCondenser": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockCondenser",
        id_1182="ae2:condenser",
        has_tile_entity=True,
        nbt_converter="condenser",
        notes="Matter Condenser - konwersja itemów"
    ),
    "appliedenergistics2:tile.BlockGrinder": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockGrinder",
        id_1182="minecraft:grindstone",
        has_tile_entity=False,
        notes="Quartz Grindstone - lossy fallback, AE2 11.7.6 nie ma tego bloku"
    ),
    "appliedenergistics2:tile.BlockCrank": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockCrank",
        id_1182="minecraft:lever",
        has_tile_entity=False,
        notes="Wooden Crank - lossy fallback, AE2 11.7.6 nie ma tego bloku"
    ),
    "appliedenergistics2:tile.BlockSkyChest": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockSkyChest",
        id_1182="ae2:sky_stone_chest",
        has_tile_entity=True,
        nbt_converter="sky_chest",
        notes="Sky Stone Chest - skrzynia"
    ),
    "appliedenergistics2:tile.BlockTinyTNT": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockTinyTNT",
        id_1182="ae2:tiny_tnt",
        has_tile_entity=False,
        notes="Tiny TNT"
    ),
    "appliedenergistics2:tile.BlockLightDetector": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockLightDetector",
        id_1182="ae2:light_detector",
        has_tile_entity=False,
        notes="Light Detector"
    ),
    "appliedenergistics2:tile.BlockQuartzTorch": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockQuartzTorch",
        id_1182="ae2:quartz_fixture",
        has_tile_entity=False,
        notes="Quartz Fixture - oświetlenie"
    ),
    
    # === WIRELESS ===
    "appliedenergistics2:tile.BlockWireless": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockWireless",
        id_1182="ae2:wireless_access_point",
        has_tile_entity=True,
        nbt_converter="wireless_ap",
        notes="Wireless Access Point"
    ),
    "appliedenergistics2:tile.BlockSecurity": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockSecurity",
        id_1182="ae2:security_station",
        has_tile_entity=True,
        nbt_converter="security_station",
        notes="Security Station - kontrola dostępu"
    ),
    
    # === CABLE BUS (części kablowe) ===
    "appliedenergistics2:tile.BlockCableBus": BlockMapping(
        id_1710="appliedenergistics2:tile.BlockCableBus",
        id_1182="ae2:fluix_block",
        has_tile_entity=False,
        nbt_converter="cable_bus",
        notes="Cable Bus - lossy material fallback; ae2:cable_bus removes itself without AE2 API-created parts"
    ),
}


RAW_NBT_ID_ALIASES: Dict[str, str] = {
    mapping.id_1710.rsplit(".", 1)[-1]: mapping.id_1710
    for mapping in BLOCK_MAPPINGS_1710_TO_1182.values()
    if mapping.id_1710.startswith("appliedenergistics2:tile.Block")
}

RAW_NBT_ID_ALIASES.update(
    {
        # Starsze raporty projektu uzywaly docelowej nazwy "Fixture".
        # Realny rejestr 1.7.10 i kod zrodlowy AE2 rv3 uzywaja BlockQuartzTorch.
        "BlockQuartzFixture": "appliedenergistics2:tile.BlockQuartzTorch",
        "appliedenergistics2:tile.BlockQuartzFixture": "appliedenergistics2:tile.BlockQuartzTorch",
    }
)


def normalize_block_id(block_id_1710: str) -> str:
    """
    Normalizuje ID bloku/TileEntity AE2.

    Realne NBT z mapy 1.7.10 zapisuje czesto samo `BlockDrive`,
    `BlockCableBus` itd., podczas gdy tabela mapowan uzywa pelnego
    `appliedenergistics2:tile.BlockDrive`.
    """
    if block_id_1710 in BLOCK_MAPPINGS_1710_TO_1182:
        return block_id_1710
    return RAW_NBT_ID_ALIASES.get(block_id_1710, block_id_1710)


def get_block_mapping(block_id_1710: str) -> Optional[BlockMapping]:
    """
    Zwraca mapowanie dla bloku 1.7.10.
    
    Args:
        block_id_1710: ID bloku w wersji 1.7.10
        
    Returns:
        BlockMapping lub None jeśli nie znaleziono
    """
    return BLOCK_MAPPINGS_1710_TO_1182.get(normalize_block_id(block_id_1710))


def resolve_crafting_storage_variant(base_id: str, metadata: int) -> str:
    """
    Rozwiązuje wariant Crafting Storage na podstawie metadata.
    
    W 1.7.10 BlockCraftingStorage używa metadata:
    - 0 = 1k
    - 1 = 4k
    - 2 = 16k
    - 3 = 64k
    
    W 1.18.2 są osobne ID:
    - ae2:1k_crafting_storage
    - ae2:4k_crafting_storage
    - ae2:16k_crafting_storage
    - ae2:64k_crafting_storage
    """
    size = metadata & 3
    variants = {
        0: "ae2:1k_crafting_storage",
        1: "ae2:4k_crafting_storage",
        2: "ae2:16k_crafting_storage",
        3: "ae2:64k_crafting_storage",
    }
    return variants.get(size, "ae2:1k_crafting_storage")


def resolve_crafting_unit_variant(metadata: int) -> Tuple[str, str]:
    """
    Rozwiązuje wariant Crafting Unit na podstawie metadata.
    
    W 1.7.10:
    - 0 = Crafting Unit
    - 1 = Crafting Co-Processing Unit
    
    W 1.18.2:
    - ae2:crafting_unit
    - ae2:crafting_accelerator
    """
    variants = {
        0: ("ae2:crafting_unit", "crafting_unit"),
        1: ("ae2:crafting_accelerator", "crafting_accelerator"),
    }
    return variants.get(metadata & 1, ("ae2:crafting_unit", "crafting_unit"))


# Zestaw wszystkich ID bloków AE2 1.7.10
ALL_AE2_BLOCK_IDS_1710 = set(BLOCK_MAPPINGS_1710_TO_1182.keys()) | set(RAW_NBT_ID_ALIASES.keys())

# Zestaw wszystkich ID bloków AE2 1.18.2
ALL_AE2_BLOCK_IDS_1182 = {m.id_1182 for m in BLOCK_MAPPINGS_1710_TO_1182.values()}
