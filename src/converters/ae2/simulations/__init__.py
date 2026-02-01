"""
AE2 Simulations Package

Symulacje funkcjonalności AE2 dla wersji 1.7.10 i 1.18.2.
Używane do testowania i weryfikacji konwersji.

Autor: AI Konwersji AE2
Data: 2026-02-01
"""

from .me_network_simulation import (
    MENetwork1710,
    MENetwork1182,
    Node1710,
    Node1182,
    AECableType,
    AEColor
)

from .storage_cell_simulation import (
    StorageCellInventory1710,
    StorageCellInventory1182,
    AEItemStack1710,
    AEItemStack1182,
    StorageCellType
)

from .autocrafting_simulation import (
    CraftingCPU1710,
    CraftingCPU1182,
    CraftingPattern1710,
    CraftingPattern1182,
    CraftingTask1710,
    CraftingTask1182,
    CraftingStatus
)

from .quantum_bridge_simulation import (
    QuantumBridge1710,
    QuantumBridge1182,
    QuantumSingularity1710,
    QuantumSingularity1182,
    QuantumBridgeStatus
)

from .spatial_io_simulation import (
    SpatialIOPort1710,
    SpatialIOPort1182,
    SpatialStorageCell1710,
    SpatialStorageCell1182,
    SpatialCellSize,
    SpatialIOStatus
)

__all__ = [
    # ME Network
    'MENetwork1710', 'MENetwork1182',
    'Node1710', 'Node1182',
    'AECableType', 'AEColor',
    
    # Storage Cell
    'StorageCellInventory1710', 'StorageCellInventory1182',
    'AEItemStack1710', 'AEItemStack1182',
    'StorageCellType',
    
    # Autocrafting
    'CraftingCPU1710', 'CraftingCPU1182',
    'CraftingPattern1710', 'CraftingPattern1182',
    'CraftingTask1710', 'CraftingTask1182',
    'CraftingStatus',
    
    # Quantum Bridge
    'QuantumBridge1710', 'QuantumBridge1182',
    'QuantumSingularity1710', 'QuantumSingularity1182',
    'QuantumBridgeStatus',
    
    # Spatial IO
    'SpatialIOPort1710', 'SpatialIOPort1182',
    'SpatialStorageCell1710', 'SpatialStorageCell1182',
    'SpatialCellSize', 'SpatialIOStatus',
]
