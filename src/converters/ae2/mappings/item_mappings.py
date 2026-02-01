"""
Item Mappings for AE2 - 1.7.10 to 1.18.2

Mapowanie ID itemów AE2 (storage cells, komponenty, materiały).
Źródło: AE2_BLOCKS_AND_TE.md (sekcja 6)
"""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class ItemMapping:
    """Reprezentuje mapowanie itemu między wersjami"""
    id_1710: str
    id_1182: str
    notes: str = ""


# Mapowanie itemów AE2: 1.7.10 -> 1.18.2
ITEM_MAPPINGS_1710_TO_1182: Dict[str, ItemMapping] = {
    # === STORAGE CELLS (Item) ===
    "appliedenergistics2:item.ItemBasicStorageCell.1k": ItemMapping(
        id_1710="appliedenergistics2:item.ItemBasicStorageCell.1k",
        id_1182="ae2:item_storage_cell_1k",
        notes="Item Storage Cell 1k"
    ),
    "appliedenergistics2:item.ItemBasicStorageCell.4k": ItemMapping(
        id_1710="appliedenergistics2:item.ItemBasicStorageCell.4k",
        id_1182="ae2:item_storage_cell_4k",
        notes="Item Storage Cell 4k"
    ),
    "appliedenergistics2:item.ItemBasicStorageCell.16k": ItemMapping(
        id_1710="appliedenergistics2:item.ItemBasicStorageCell.16k",
        id_1182="ae2:item_storage_cell_16k",
        notes="Item Storage Cell 16k"
    ),
    "appliedenergistics2:item.ItemBasicStorageCell.64k": ItemMapping(
        id_1710="appliedenergistics2:item.ItemBasicStorageCell.64k",
        id_1182="ae2:item_storage_cell_64k",
        notes="Item Storage Cell 64k"
    ),
    
    # === STORAGE CELLS (Fluid) ===
    "appliedenergistics2:item.ItemBasicFluidStorageCell.1k": ItemMapping(
        id_1710="appliedenergistics2:item.ItemBasicFluidStorageCell.1k",
        id_1182="ae2:fluid_storage_cell_1k",
        notes="Fluid Storage Cell 1k"
    ),
    "appliedenergistics2:item.ItemBasicFluidStorageCell.4k": ItemMapping(
        id_1710="appliedenergistics2:item.ItemBasicFluidStorageCell.4k",
        id_1182="ae2:fluid_storage_cell_4k",
        notes="Fluid Storage Cell 4k"
    ),
    "appliedenergistics2:item.ItemBasicFluidStorageCell.16k": ItemMapping(
        id_1710="appliedenergistics2:item.ItemBasicFluidStorageCell.16k",
        id_1182="ae2:fluid_storage_cell_16k",
        notes="Fluid Storage Cell 16k"
    ),
    "appliedenergistics2:item.ItemBasicFluidStorageCell.64k": ItemMapping(
        id_1710="appliedenergistics2:item.ItemBasicFluidStorageCell.64k",
        id_1182="ae2:fluid_storage_cell_64k",
        notes="Fluid Storage Cell 64k"
    ),
    
    # === SPATIAL CELLS ===
    "appliedenergistics2:item.ItemSpatialStorageCell.2Cubed": ItemMapping(
        id_1710="appliedenergistics2:item.ItemSpatialStorageCell.2Cubed",
        id_1182="ae2:spatial_cell_2",
        notes="Spatial Storage Cell 2³"
    ),
    "appliedenergistics2:item.ItemSpatialStorageCell.16Cubed": ItemMapping(
        id_1710="appliedenergistics2:item.ItemSpatialStorageCell.16Cubed",
        id_1182="ae2:spatial_cell_16",
        notes="Spatial Storage Cell 16³"
    ),
    "appliedenergistics2:item.ItemSpatialStorageCell.128Cubed": ItemMapping(
        id_1710="appliedenergistics2:item.ItemSpatialStorageCell.128Cubed",
        id_1182="ae2:spatial_cell_128",
        notes="Spatial Storage Cell 128³"
    ),
    
    # === VIEW CELL ===
    "appliedenergistics2:item.ItemViewCell": ItemMapping(
        id_1710="appliedenergistics2:item.ItemViewCell",
        id_1182="ae2:view_cell",
        notes="View Cell - filtrowanie widoku"
    ),
    
    # === PORTABLE CELLS ===
    "appliedenergistics2:item.ItemPortableCell": ItemMapping(
        id_1710="appliedenergistics2:item.ItemPortableCell",
        id_1182="ae2:portable_item_cell_1k",
        notes="Portable Cell -> 1k (najbliższy odpowiednik)"
    ),
    
    # === PROCESSORS ===
    "appliedenergistics2:item.ItemMultiMaterial": ItemMapping(
        id_1710="appliedenergistics2:item.ItemMultiMaterial",
        id_1182="ae2:logic_processor",  # Metadata decyduje o typie
        notes="Logic Processor - metadata: 22"
    ),
    
    # === MATERIALS ===
    "appliedenergistics2:item.ItemMultiMaterial.certus_quartz_crystal": ItemMapping(
        id_1710="appliedenergistics2:item.ItemMultiMaterial",
        id_1182="ae2:certus_quartz_crystal",
        notes="Certus Quartz Crystal - metadata: 1"
    ),
    "appliedenergistics2:item.ItemMultiMaterial.charged_certus_quartz_crystal": ItemMapping(
        id_1710="appliedenergistics2:item.ItemMultiMaterial",
        id_1182="ae2:charged_certus_quartz_crystal",
        notes="Charged Certus Quartz Crystal - metadata: 2"
    ),
}


def get_item_mapping(item_id_1710: str, metadata: int = 0) -> Optional[ItemMapping]:
    """
    Zwraca mapowanie dla itemu 1.7.10.
    
    Args:
        item_id_1710: ID itemu w wersji 1.7.10
        metadata: Metadata itemu (dla ItemMultiMaterial)
        
    Returns:
        ItemMapping lub None jeśli nie znaleziono
    """
    # Specjalne mapowanie dla ItemMultiMaterial z różnymi metadata
    if item_id_1710 == "appliedenergistics2:item.ItemMultiMaterial":
        return _resolve_multi_material(metadata)
    
    return ITEM_MAPPINGS_1710_TO_1182.get(item_id_1710)


def _resolve_multi_material(metadata: int) -> Optional[ItemMapping]:
    """
    Rozwiązuje ItemMultiMaterial na podstawie metadata.
    
    W 1.7.10 ItemMultiMaterial używa metadata dla różnych materiałów:
    """
    material_map = {
        # Certus Quartz
        1: ("ae2:certus_quartz_crystal", "Certus Quartz Crystal"),
        2: ("ae2:charged_certus_quartz_crystal", "Charged Certus Quartz Crystal"),
        3: ("ae2:certus_quartz_dust", "Certus Quartz Dust"),
        
        # Fluix
        8: ("ae2:fluix_crystal", "Fluix Crystal"),
        9: ("ae2:fluix_dust", "Fluix Dust"),
        10: ("ae2:fluix_pearl", "Fluix Pearl"),
        
        # Silicon
        5: ("ae2:silicon", "Silicon"),
        20: ("ae2:printed_silicon", "Printed Silicon"),
        
        # Processors (Printed)
        16: ("ae2:printed_logic_processor", "Printed Logic Circuit"),
        17: ("ae2:printed_calculation_processor", "Printed Calculation Circuit"),
        18: ("ae2:printed_engineering_processor", "Printed Engineering Circuit"),
        
        # Processors (Finished)
        22: ("ae2:logic_processor", "Logic Processor"),
        23: ("ae2:calculation_processor", "Calculation Processor"),
        24: ("ae2:engineering_processor", "Engineering Processor"),
        
        # Matter
        6: ("ae2:matter_ball", "Matter Ball"),
        7: ("ae2:singularity", "Singularity"),
        
        # Sky Stone
        45: ("ae2:sky_stone_block", "Sky Stone"),
    }
    
    if metadata in material_map:
        id_1182, desc = material_map[metadata]
        return ItemMapping(
            id_1710=f"appliedenergistics2:item.ItemMultiMaterial:{metadata}",
            id_1182=id_1182,
            notes=desc
        )
    
    return None


def resolve_storage_cell_type(cell_id: str) -> tuple:
    """
    Rozpoznaje typ storage cell.
    
    Returns:
        (item_type, size, variant) gdzie:
        - item_type: 'item' lub 'fluid'
        - size: 1, 4, 16, 64, 256
        - variant: 'storage' lub 'portable'
    """
    cell_patterns = {
        # Items
        "ae2:item_storage_cell_1k": ("item", 1, "storage"),
        "ae2:item_storage_cell_4k": ("item", 4, "storage"),
        "ae2:item_storage_cell_16k": ("item", 16, "storage"),
        "ae2:item_storage_cell_64k": ("item", 64, "storage"),
        "ae2:item_storage_cell_256k": ("item", 256, "storage"),
        # Fluids
        "ae2:fluid_storage_cell_1k": ("fluid", 1, "storage"),
        "ae2:fluid_storage_cell_4k": ("fluid", 4, "storage"),
        "ae2:fluid_storage_cell_16k": ("fluid", 16, "storage"),
        "ae2:fluid_storage_cell_64k": ("fluid", 64, "storage"),
        "ae2:fluid_storage_cell_256k": ("fluid", 256, "storage"),
        # Portables
        "ae2:portable_item_cell_1k": ("item", 1, "portable"),
        "ae2:portable_item_cell_4k": ("item", 4, "portable"),
        "ae2:portable_item_cell_16k": ("item", 16, "portable"),
        "ae2:portable_item_cell_64k": ("item", 64, "portable"),
        "ae2:portable_item_cell_256k": ("item", 256, "portable"),
    }
    
    return cell_patterns.get(cell_id, ("item", 1, "storage"))


# Zestaw wszystkich ID itemów AE2 1.7.10
ALL_AE2_ITEM_IDS_1710 = set(ITEM_MAPPINGS_1710_TO_1182.keys())

# Zestaw wszystkich ID itemów AE2 1.18.2
ALL_AE2_ITEM_IDS_1182 = {m.id_1182 for m in ITEM_MAPPINGS_1710_TO_1182.values()}
