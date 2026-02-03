"""
Symulacje funkcjonalności Blood Magic dla konwersji 1.7.10 -> 1.18.2

Ten pakiet zawiera symulacje działania kluczowych mechanik Blood Magic,
bazujące na dokładnej analizie kodu źródłowego obu wersji moda.

Source mapping:
- 1.7.10: WayofTime/alchemicalWizardry/common/tileEntity/TEAltar.java
- 1.18.2: wayoftime/bloodmagic/altar/BloodAltar.java
- 1.18.2: wayoftime/bloodmagic/common/tile/TileAltar.java
"""

from .blood_altar_sim import BloodAltarSimulation, AltarTier, BloodRuneType
from .soul_network_sim import SoulNetworkSimulation, BloodOrb
from .ritual_stone_sim import MasterRitualStoneSimulation, RitualType
from .altar_tier_sim import AltarTierCalculator
from .well_of_suffering_sim import WellOfSufferingSimulation

__all__ = [
    'BloodAltarSimulation',
    'AltarTier',
    'BloodRuneType',
    'SoulNetworkSimulation',
    'BloodOrb',
    'MasterRitualStoneSimulation',
    'RitualType',
    'AltarTierCalculator',
    'WellOfSufferingSimulation',
]
