"""
Cable Converters

Konwertery dla kabli AE2 (Glass Cable, Covered Cable, Smart Cable, Dense Cable).

UWAGA: Kable w AE2 używają systemu "Part" (multipart), nie standardowych TileEntities.
Są przechowywane w specjalnych multipart block entities (np. BlockCableBus).

Kluczowa różnica:
- 1.7.10: Zapisuje usedChannels w NBT (liczba kanałów na kablu)
- 1.18.2: Nie zapisuje usedChannels w NBT - jest to tylko informacja wizualna
"""

from typing import Dict, Any
from .base_converter import BaseNBTConverter, NBTConversionResult


class CableConverter(BaseNBTConverter):
    """
    Bazowy konwerter dla kabli AE2.
    
    Obsługuje: Glass Cable, Covered Cable, Smart Cable, Dense Cable, Quartz Fiber.
    
    Źródło 1.7.10: appeng.parts.networking.PartCable
        - usedChannels: byte (liczba kanałów - tylko wizualne)
        - connections: EnumSet<ForgeDirection> (połączenia z innymi kablami)
    
    Źródło 1.18.2: appeng.parts.networking.CablePart
        - Nie zapisuje usedChannels w NBT (wizualne tylko)
        - Połączenia są w BlockState lub obliczane dynamicznie
    
    UWAGA: System multipart wymaga specjalnej obsługi w konwerterze świata.
    Kable nie są zapisywane jako osobne TileEntities, ale jako "Part" wewnątrz
    multipart block (BlockCableBus w 1.7.10, podobnie w 1.18.2).
    """
    
    @property
    def converter_name(self) -> str:
        return "cable"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje NBT kabla AE2.
        
        Struktura 1.7.10:
        {
            "usedChannels": 8,  # byte - liczba kanałów (wizualne)
            # Inne pola z AEBasePart (customName, itp.)
        }
        
        Struktura 1.18.2:
        {
            # Brak usedChannels w NBT - jest to wizualne
            # Pola z AEBasePart (customName, mainNode)
        }
        """
        self.reset()
        
        converted = {}
        
        # usedChannels - zgłoś warning, nie można przekonwertować
        if 'usedChannels' in nbt_1710:
            self._add_warning(
                f"Cable has usedChannels={nbt_1710['usedChannels']}, "
                f"but 1.18.2 doesn't store this in NBT. "
                f"Channel count will be recalculated on world load."
            )
        
        # Custom name (jeśli ustawione)
        custom_name = nbt_1710.get('customName')
        if custom_name:
            converted['customName'] = custom_name
        
        # Połączenia (connections) są obliczane dynamicznie w 1.18.2
        # Nie ma potrzeby konwersji
        
        return self._create_result(converted)


class GlassCableConverter(CableConverter):
    """Konwerter dla Glass Cable (przezroczysty kabel)"""
    
    @property
    def converter_name(self) -> str:
        return "glass_cable"


class CoveredCableConverter(CableConverter):
    """Konwerter dla Covered Cable (kabel w osłonie)"""
    
    @property
    def converter_name(self) -> str:
        return "covered_cable"


class SmartCableConverter(CableConverter):
    """Konwerter dla Smart Cable (kabel pokazujący zajętość kanałów)"""
    
    @property
    def converter_name(self) -> str:
        return "smart_cable"


class DenseCableConverter(CableConverter):
    """Konwerter dla Dense Cable (kabel o dużej przepustowości - 32 kanały)"""
    
    @property
    def converter_name(self) -> str:
        return "dense_cable"


class QuartzFiberConverter(CableConverter):
    """
    Konwerter dla Quartz Fiber.
    
    Quartz Fiber łączy sieci ME bez przekazywania kanałów.
    W 1.7.10 może mieć inną strukturę niż standardowe kable.
    """
    
    @property
    def converter_name(self) -> str:
        return "quartz_fiber"
