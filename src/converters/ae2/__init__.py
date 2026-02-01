"""
AE2 Converter - Konwersja AE2 z Minecraft 1.7.10 do 1.18.2

Główny moduł konwertera AE2.

Użycie:
    from src.converters.ae2 import AE2Converter
    
    converter = AE2Converter()
    result = converter.convert_block(block_id_1710, nbt_1710)
"""

from .ae2_converter import AE2Converter, ConversionResult, AE2BlockConversion

__all__ = [
    'AE2Converter',
    'ConversionResult', 
    'AE2BlockConversion',
]

__version__ = '1.0.0'
__author__ = 'AE2 Conversion Team'
