"""
GrowthCraft Converter Module

Moduł do konwersji moda GrowthCraft z Minecraft 1.7.10 na 1.18.2.

Obsługiwane Tile Entities:
- FermentationBarrel (Beczka fermentacyjna)
- BrewKettle (Kocioł warzelny)
- BeeBox (Ul pszczeli)
- MixingVat (Kadź do sera, dawniej CheeseVat)
- FruitPress (Prasa do owoców)
- CultureJar (Słoik na kultury)
- Pancheon (Pojemnik do mleka)
- Churn (Ubiaczka do masła)
- CheesePress (Prasa do sera)
- FishTrap (Pułapka na ryby)

Autor: AI Assistant
Data: 2026-02-03
"""

from .growthcraft_converter import GrowthcraftConverter, convert_growthcraft_te
from .mappings import (
    get_block_mapping,
    get_item_mapping,
    get_fluid_mapping,
    convert_block_id,
    convert_item_id,
    convert_fluid_id,
)
from .nbt_converters import (
    FermentationBarrelNBTConverter,
    BrewKettleNBTConverter,
    BeeBoxNBTConverter,
    MixingVatNBTConverter,
)

__version__ = "1.0.0"

__all__ = [
    # Główny konwerter
    'GrowthcraftConverter',
    'convert_growthcraft_te',
    
    # Mapowania
    'get_block_mapping',
    'get_item_mapping',
    'get_fluid_mapping',
    'convert_block_id',
    'convert_item_id',
    'convert_fluid_id',
    
    # Konwertery NBT
    'FermentationBarrelNBTConverter',
    'BrewKettleNBTConverter',
    'BeeBoxNBTConverter',
    'MixingVatNBTConverter',
]
