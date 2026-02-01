"""
P2P Tunnel Converters

Konwertery dla P2P (Point-to-Point) Tunnels AE2.
P2P Tunnels pozwalają na transport energii, itemów, fluidów, światła, sygnałów redstone.

WAŻNE: P2P Tunnels w 1.7.10 i 1.18.2 używają systemu "Part" (multipart),
co oznacza że są przechowywane inaczej niż standardowe TileEntities.
Wymagają specjalnej obsługi w konwerterze świata.
"""

from typing import Dict, Any
from .base_converter import BaseNBTConverter, NBTConversionResult


class P2PTunnelConverter(BaseNBTConverter):
    """
    Konwerter dla P2P Tunnel.
    
    P2P Tunnel łączy się w pary (input-output) na podstawie częstotliwości (frequency).
    
    Źródło 1.7.10: appeng.parts.p2p.PartP2PTunnel
        - output: boolean (true = output, false = input)
        - freq: long (częstotliwość - losowa wartość 64-bitowa)
    
    Źródło 1.18.2: appeng.parts.p2p.P2PTunnelPart
        - output: boolean
        - freq: short (częstotliwość - 16-bitowa!)
    
    UWAGA: ZMIANA FORMATU CZĘSTOTLIWOŚCI!
    - 1.7.10: long (64-bit) - zakres: -9,223,372,036,854,775,808 do 9,223,372,036,854,775,807
    - 1.18.2: short (16-bit) - zakres: -32,768 do 32,767
    
    Jeśli częstotliwość przekracza zakres short, para P2P może się zepsuć!
    """
    
    @property
    def converter_name(self) -> str:
        return "p2p_tunnel"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje NBT P2P Tunnel.
        
        Struktura 1.7.10:
        {
            "output": false,  # true = output, false = input
            "freq": 1234567890123456789  # long!
        }
        
        Struktura 1.18.2:
        {
            "output": false,
            "freq": 12345  # short!
        }
        """
        self.reset()
        
        converted = {}
        
        # Pole output - identyczne w obu wersjach
        is_output = nbt_1710.get('output', False)
        converted['output'] = is_output
        
        # Pole freq - KRYTYCZNA ZMIANA Z LONG NA SHORT!
        freq_1710 = nbt_1710.get('freq', 0)
        
        # Sprawdź czy częstotliwość mieści się w zakresie short
        if freq_1710 < -32768 or freq_1710 > 32767:
            self._add_error(
                f"P2P frequency {freq_1710} exceeds 1.18.2 short range (-32768 to 32767). "
                f"P2P pair will be broken after conversion. "
                f"Consider manually re-pairing P2P tunnels in 1.18.2."
            )
            # Próba zachowania jako wartość modulo (może nie działać)
            converted['freq'] = int(freq_1710 % 65536) - 32768 if freq_1710 > 0 else int(freq_1710 % 65536) + 32768
        else:
            converted['freq'] = int(freq_1710)
        
        # Custom name (jeśli ustawione)
        custom_name = nbt_1710.get('customName')
        if custom_name:
            converted['customName'] = custom_name
        
        return self._create_result(converted)


class P2PLightConverter(P2PTunnelConverter):
    """
    Konwerter dla P2P Light Tunnel.
    
    Specjalny typ P2P do transportu światła.
    Dodatkowe pole: lightLevel (opcjonalne w niektórych wersjach).
    """
    
    @property
    def converter_name(self) -> str:
        return "p2p_light"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje P2P Light Tunnel.
        
        W 1.7.10 może mieć dodatkowe pole lightLevel.
        W 1.18.2 dziedziczy z P2PTunnelPart (output + freq).
        """
        # Użyj podstawowej konwersji P2P
        result = super().convert(nbt_1710, block_id, metadata)
        
        if not result.success:
            return result
        
        # Jeśli jest lightLevel w 1.7.10, zgłoś warning (nie jest używane w 1.18.2)
        if 'lightLevel' in nbt_1710:
            self._add_warning(
                f"P2P Light Tunnel has lightLevel={nbt_1710['lightLevel']}, "
                f"but 1.18.2 doesn't store this in NBT. Light level will be recalculated."
            )
        
        return self._create_result(result.converted_nbt)


class P2PRedstoneConverter(P2PTunnelConverter):
    """
    Konwerter dla P2P Redstone Tunnel.
    
    Transportuje sygnał redstone.
    """
    
    @property
    def converter_name(self) -> str:
        return "p2p_redstone"


class P2PItemConverter(P2PTunnelConverter):
    """
    Konwerter dla P2P Item Tunnel.
    
    Transportuje itemy (podobnie do item duct).
    """
    
    @property
    def converter_name(self) -> str:
        return "p2p_item"


class P2PFluidConverter(P2PTunnelConverter):
    """
    Konwerter dla P2P Fluid Tunnel.
    
    Transportuje fluidy.
    """
    
    @property
    def converter_name(self) -> str:
        return "p2p_fluid"


class P2PFeConverter(P2PTunnelConverter):
    """
    Konwerter dla P2P FE (Forge Energy) Tunnel.
    
    Transportuje energię Forge Energy (FE).
    
    UWAGA: W 1.7.10 może nie istnieć lub być jako RF (Redstone Flux).
    W 1.18.2 jest dedykowany P2P dla FE.
    """
    
    @property
    def converter_name(self) -> str:
        return "p2p_fe"


class P2PMEConverter(P2PTunnelConverter):
    """
    Konwerter dla P2P ME Tunnel.
    
    Transportuje kanały ME (jak kabel, ale bezpośrednio).
    """
    
    @property
    def converter_name(self) -> str:
        return "p2p_me"
