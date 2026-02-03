"""
Konwerter EnderStorage dla Minecraft 1.7.10 -> 1.18.2

Ten moduł zawiera konwerter dla wszystkich bloków, Tile Entities i itemów
z moda EnderStorage.

Główne komponenty:
- EnderStorageConverter: Główna klasa konwertera
- mappings: Mapowania bloków, itemów i kolorów
- nbt_converters: Konwertery NBT dla Tile Entities

Przykład użycia:
    from src.converters.enderstorage import EnderStorageConverter
    
    converter = EnderStorageConverter()
    result = converter.convert_block(
        block_id="EnderStorage:blockEnderStorage",
        metadata=0,
        nbt={"freq": 3803, "owner": "global"}
    )
    
    if result.success:
        print(f"Nowe ID: {result.block_id_1182}")
        print(f"Nowe NBT: {result.nbt_1182}")
"""

from .enderstorage_converter import EnderStorageConverter, convert_enderstorage_te
from .mappings import (
    EnumColour,
    Frequency,
    convert_block_id,
    convert_item_id,
    convert_frequency_nbt,
    is_enderstorage_block,
    is_enderstorage_item,
)
from .nbt_converters import (
    EnderChestNBTConverter,
    EnderTankNBTConverter,
)

__all__ = [
    'EnderStorageConverter',
    'convert_enderstorage_te',
    'EnumColour',
    'Frequency',
    'convert_block_id',
    'convert_item_id',
    'convert_frequency_nbt',
    'is_enderstorage_block',
    'is_enderstorage_item',
    'EnderChestNBTConverter',
    'EnderTankNBTConverter',
]
