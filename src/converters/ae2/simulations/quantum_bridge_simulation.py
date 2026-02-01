"""
Quantum Bridge Simulation - AE2 1.7.10 vs 1.18.2

Symulacja Quantum Network Bridge - połączenie dwóch sieci ME przez dowolną odległość.
Bazuje na kodzie źródłowym:
- 1.7.10: appeng.tile.qnb.TileQuantumBridge, appeng.me.cluster.implementations.QuantumCluster
- 1.18.2: appeng.blockentity.networking.QuantumBridgeBlockEntity
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set
from uuid import uuid4


# =============================================================================
# TYPY I STAŁE
# =============================================================================

class QuantumBridgeStatus(enum.Enum):
    """Status Quantum Bridge"""
    OFFLINE = "offline"           # Nieaktywny
    FORMING = "forming"           # Formowanie struktury
    ONLINE = "online"             # Aktywny
    ERROR = "error"               # Błąd (brak pary)


# =============================================================================
# SYMULACJA 1.7.10
# =============================================================================

@dataclass
class QuantumSingularity1710:
    """
    Quantum Entangled Singularity w 1.7.10.
    Para singularity łączy ze sobą mosty kwantowe.
    
    Tworzenie: Matter Cannon + Singularity → para entangled
    """
    singularity_id: str
    pair_id: str  # ID pary - dwa singularity mają ten sam pair_id
    
    @classmethod
    def create_pair(cls) -> Tuple[QuantumSingularity1710, QuantumSingularity1710]:
        """Tworzy parę entangled singularity"""
        pair_id = str(uuid4())[:8]
        return (
            cls(singularity_id=f"sing_{pair_id}_A", pair_id=pair_id),
            cls(singularity_id=f"sing_{pair_id}_B", pair_id=pair_id)
        )


@dataclass
class QuantumBridgeNode1710:
    """
    Pojedynczy węzeł Quantum Bridge w 1.7.10.
    
    Struktura 3x3x1:
    [R][R][R]
    [R][L][R]  R = Quantum Ring, L = Link Chamber
    [R][R][R]
    """
    x: int
    y: int
    z: int
    world_id: str = "overworld"
    
    is_link_chamber: bool = False  # Środkowy blok (L)
    is_ring: bool = False          # Obramowanie (R)
    
    # Stan
    status: QuantumBridgeStatus = QuantumBridgeStatus.OFFLINE
    entangled_singularity: Optional[QuantumSingularity1710] = None
    
    def can_form_structure(self, nodes: Dict[Tuple[int, int, int], QuantumBridgeNode1710]) -> bool:
        """
        Sprawdza czy struktura 3x3 jest kompletna.
        Wymaga: 8 ring + 1 link chamber
        """
        if not self.is_link_chamber:
            return False
        
        # Sprawdź sąsiadów (powinno być 8 ringów)
        ring_count = 0
        for dx in [-1, 0, 1]:
            for dz in [-1, 0, 1]:
                if dx == 0 and dz == 0:
                    continue  # Pomijamy środek (sam siebie)
                
                neighbor_pos = (self.x + dx, self.y, self.z + dz)
                if neighbor_pos in nodes:
                    if nodes[neighbor_pos].is_ring:
                        ring_count += 1
        
        return ring_count == 8


@dataclass
class QuantumBridge1710:
    """
    Quantum Network Bridge w 1.7.10.
    
    Odpowiada: appeng.tile.qnb.TileQuantumBridge
    
    Most składa się z:
    - 1x Quantum Link Chamber (środek)
    - 8x Quantum Ring (obramowanie)
    - 1x Quantum Entangled Singularity (w Link Chamber)
    
    Połączenie: Dwa mosty z parą singularity tworzą tunel.
    """
    bridge_id: str
    center_pos: Tuple[int, int, int]
    world_id: str = "overworld"
    
    nodes: Dict[Tuple[int, int, int], QuantumBridgeNode1710] = field(default_factory=dict)
    singularity: Optional[QuantumSingularity1710] = None
    
    # Połączenie
    linked_bridge: Optional[str] = None  # ID połączonego mostu
    status: QuantumBridgeStatus = QuantumBridgeStatus.OFFLINE
    
    def create_structure(self) -> bool:
        """
        Tworzy strukturę 3x3 mostu.
        Zwraca True jeśli struktura poprawna.
        """
        cx, cy, cz = self.center_pos
        
        # Utwórz Link Chamber (środek)
        link_chamber = QuantumBridgeNode1710(
            x=cx, y=cy, z=cz,
            world_id=self.world_id,
            is_link_chamber=True,
            is_ring=False
        )
        self.nodes[(cx, cy, cz)] = link_chamber
        
        # Utwórz Ring (obramowanie)
        for dx in [-1, 0, 1]:
            for dz in [-1, 0, 1]:
                if dx == 0 and dz == 0:
                    continue
                
                ring = QuantumBridgeNode1710(
                    x=cx + dx, y=cy, z=cz + dz,
                    world_id=self.world_id,
                    is_link_chamber=False,
                    is_ring=True
                )
                self.nodes[(cx + dx, cy, cz + dz)] = ring
        
        # Sprawdź strukturę
        return link_chamber.can_form_structure(self.nodes)
    
    def insert_singularity(self, singularity: QuantumSingularity1710) -> bool:
        """Wstawia singularity do Link Chamber"""
        if self.singularity is not None:
            return False
        
        self.singularity = singularity
        self.status = QuantumBridgeStatus.FORMING
        return True
    
    def try_link(self, other_bridge: QuantumBridge1710) -> bool:
        """
        Próbuje połączyć z innym mostem.
        Wymaga: para singularity (ten sam pair_id).
        """
        if not self.singularity or not other_bridge.singularity:
            return False
        
        if self.singularity.pair_id != other_bridge.singularity.pair_id:
            return False
        
        # Połączenie udane!
        self.linked_bridge = other_bridge.bridge_id
        other_bridge.linked_bridge = self.bridge_id
        
        self.status = QuantumBridgeStatus.ONLINE
        other_bridge.status = QuantumBridgeStatus.ONLINE
        
        return True
    
    def get_channel_capacity(self) -> int:
        """Zwraca pojemność kanałową mostu"""
        if self.status != QuantumBridgeStatus.ONLINE:
            return 0
        # Quantum Bridge zawsze przenosi 32 kanały (dense)
        return 32
    
    def to_nbt(self) -> Dict:
        """Eksportuje stan mostu do NBT"""
        return {
            'x': self.center_pos[0],
            'y': self.center_pos[1],
            'z': self.center_pos[2],
            'dim': self.world_id,
            'singularity': self.singularity.singularity_id if self.singularity else None,
            'pairId': self.singularity.pair_id if self.singularity else None,
            'linked': self.linked_bridge,
            'status': self.status.value
        }


# =============================================================================
# SYMULACJA 1.18.2
# =============================================================================

@dataclass
class QuantumSingularity1182:
    """
    Quantum Entangled Singularity w 1.18.2.
    Działa identycznie jak w 1.7.10.
    """
    singularity_id: str
    pair_id: str
    
    @classmethod
    def create_pair(cls) -> Tuple[QuantumSingularity1182, QuantumSingularity1182]:
        pair_id = str(uuid4())[:8]
        return (
            cls(singularity_id=f"sing_{pair_id}_A", pair_id=pair_id),
            cls(singularity_id=f"sing_{pair_id}_B", pair_id=pair_id)
        )


@dataclass
class QuantumBridgeNode1182:
    """Węzeł Quantum Bridge w 1.18.2"""
    x: int
    y: int
    z: int
    world_id: str = "overworld"
    
    is_link_chamber: bool = False
    is_ring: bool = False
    
    status: QuantumBridgeStatus = QuantumBridgeStatus.OFFLINE
    entangled_singularity: Optional[QuantumSingularity1182] = None
    
    def can_form_structure(self, nodes: Dict[Tuple[int, int, int], QuantumBridgeNode1182]) -> bool:
        """Sprawdza strukturę 3x3"""
        if not self.is_link_chamber:
            return False
        
        ring_count = 0
        for dx in [-1, 0, 1]:
            for dz in [-1, 0, 1]:
                if dx == 0 and dz == 0:
                    continue
                
                neighbor_pos = (self.x + dx, self.y, self.z + dz)
                if neighbor_pos in nodes:
                    if nodes[neighbor_pos].is_ring:
                        ring_count += 1
        
        return ring_count == 8


@dataclass
class QuantumBridge1182:
    """
    Quantum Network Bridge w 1.18.2.
    
    Odpowiada: appeng.blockentity.networking.QuantumBridgeBlockEntity
    
    GŁÓWNE RÓŻNICE vs 1.7.10:
    - Lepsza obsługa wielowymiarowości
    - Lepsza synchronizacja NBT
    - Obsługa Spatial Anchor (opcjonalnie)
    """
    bridge_id: str
    center_pos: Tuple[int, int, int]
    world_id: str = "overworld"
    
    nodes: Dict[Tuple[int, int, int], QuantumBridgeNode1182] = field(default_factory=dict)
    singularity: Optional[QuantumSingularity1182] = None
    
    linked_bridge: Optional[str] = None
    status: QuantumBridgeStatus = QuantumBridgeStatus.OFFLINE
    
    # Nowość w 1.18.2
    is_chunk_loaded: bool = False  # Czy chunk jest załadowany
    linked_world: Optional[str] = None  # ID świata połączonego mostu
    
    def create_structure(self) -> bool:
        """Tworzy strukturę 3x3"""
        cx, cy, cz = self.center_pos
        
        link_chamber = QuantumBridgeNode1182(
            x=cx, y=cy, z=cz,
            world_id=self.world_id,
            is_link_chamber=True,
            is_ring=False
        )
        self.nodes[(cx, cy, cz)] = link_chamber
        
        for dx in [-1, 0, 1]:
            for dz in [-1, 0, 1]:
                if dx == 0 and dz == 0:
                    continue
                
                ring = QuantumBridgeNode1182(
                    x=cx + dx, y=cy, z=cz + dz,
                    world_id=self.world_id,
                    is_link_chamber=False,
                    is_ring=True
                )
                self.nodes[(cx + dx, cy, cz + dz)] = ring
        
        return link_chamber.can_form_structure(self.nodes)
    
    def insert_singularity(self, singularity: QuantumSingularity1182) -> bool:
        """Wstawia singularity"""
        if self.singularity is not None:
            return False
        
        self.singularity = singularity
        self.status = QuantumBridgeStatus.FORMING
        return True
    
    def try_link(self, other_bridge: QuantumBridge1182) -> bool:
        """Próbuje połączyć z innym mostem"""
        if not self.singularity or not other_bridge.singularity:
            return False
        
        if self.singularity.pair_id != other_bridge.singularity.pair_id:
            return False
        
        self.linked_bridge = other_bridge.bridge_id
        other_bridge.linked_bridge = self.bridge_id
        
        # Nowość w 1.18.2 - zapisz świat docelowy
        self.linked_world = other_bridge.world_id
        other_bridge.linked_world = self.world_id
        
        self.status = QuantumBridgeStatus.ONLINE
        other_bridge.status = QuantumBridgeStatus.ONLINE
        
        return True
    
    def get_channel_capacity(self) -> int:
        """Zwraca pojemność kanałową"""
        if self.status != QuantumBridgeStatus.ONLINE:
            return 0
        return 32
    
    def to_nbt(self) -> Dict:
        """Eksportuje do NBT 1.18.2"""
        nbt = {
            'x': self.center_pos[0],
            'y': self.center_pos[1],
            'z': self.center_pos[2],
            'dim': self.world_id,
            'singularity': self.singularity.singularity_id if self.singularity else None,
            'pairId': self.singularity.pair_id if self.singularity else None,
            'linked': self.linked_bridge,
            'linkedDim': self.linked_world,
            'status': self.status.value,
            'chunkLoaded': self.is_chunk_loaded
        }
        return nbt


# =============================================================================
# SYMULACJA POŁĄCZENIA
# =============================================================================

@dataclass
class QuantumNetworkConnection:
    """
    Reprezentuje połączenie między dwoma mostami.
    Niezależne od wersji.
    """
    bridge_a_id: str
    bridge_b_id: str
    pair_id: str
    channels_available: int = 32
    is_active: bool = False
    
    def transmit_data(self, data: str) -> bool:
        """Symuluje transmisję danych przez most"""
        if not self.is_active:
            return False
        return True


def simulate_quantum_connection_1710():
    """Symuluje połączenie kwantowe w 1.7.10"""
    print("="*60)
    print("SYMULACJA QUANTUM BRIDGE 1.7.10")
    print("="*60)
    
    # Utwórz parę singularity
    sing_a, sing_b = QuantumSingularity1710.create_pair()
    print(f"\nUtworzono parę singularity: {sing_a.pair_id}")
    print(f"  Singularity A: {sing_a.singularity_id}")
    print(f"  Singularity B: {sing_b.singularity_id}")
    
    # Most 1 (baza główna)
    bridge1 = QuantumBridge1710(
        bridge_id="bridge_main",
        center_pos=(100, 64, 100),
        world_id="overworld"
    )
    
    print(f"\nTworzenie mostu 1 na pozycji {bridge1.center_pos}")
    if bridge1.create_structure():
        print("✓ Struktura 3x3 utworzona poprawnie")
        print(f"  - 1x Quantum Link Chamber")
        print(f"  - 8x Quantum Ring")
    
    # Most 2 (odległa baza)
    bridge2 = QuantumBridge1710(
        bridge_id="bridge_remote",
        center_pos=(1000, 70, -500),  # Daleko!
        world_id="overworld"
    )
    
    print(f"\nTworzenie mostu 2 na pozycji {bridge2.center_pos}")
    if bridge2.create_structure():
        print("✓ Struktura 3x3 utworzona poprawnie")
    
    # Wstaw singularity
    bridge1.insert_singularity(sing_a)
    bridge2.insert_singularity(sing_b)
    print(f"\nWstawiono singularity do obu mostów")
    
    # Połączenie
    if bridge1.try_link(bridge2):
        print("✓ Mosty połączone!")
        print(f"  Kanały dostępne: {bridge1.get_channel_capacity()}")
        print(f"  Odległość: {abs(bridge2.center_pos[0] - bridge1.center_pos[0])} bloków")
        
        # Symulacja transmisji
        connection = QuantumNetworkConnection(
            bridge_a_id=bridge1.bridge_id,
            bridge_b_id=bridge2.bridge_id,
            pair_id=sing_a.pair_id,
            is_active=True
        )
        
        if connection.transmit_data("Test ME Network"):
            print("✓ Dane przesłane przez Quantum Bridge")
    else:
        print("✗ Nie udało się połączyć mostów")
    
    print(f"\nNBT Mostu 1: {bridge1.to_nbt()}")


def simulate_quantum_connection_1182():
    """Symuluje połączenie kwantowe w 1.18.2"""
    print("\n" + "="*60)
    print("SYMULACJA QUANTUM BRIDGE 1.18.2")
    print("="*60)
    
    # Utwórz parę singularity
    sing_a, sing_b = QuantumSingularity1182.create_pair()
    print(f"\nUtworzono parę singularity: {sing_a.pair_id}")
    
    # Most 1 (Overworld)
    bridge1 = QuantumBridge1182(
        bridge_id="bridge_overworld",
        center_pos=(100, 64, 100),
        world_id="minecraft:overworld"
    )
    
    # Most 2 (Nether - nowość w 1.18.2 - lepsza obsługa wymiarów)
    bridge2 = QuantumBridge1182(
        bridge_id="bridge_nether",
        center_pos=(50, 70, 50),
        world_id="minecraft:the_nether"
    )
    
    print(f"\nMost 1: {bridge1.world_id} {bridge1.center_pos}")
    print(f"Most 2: {bridge2.world_id} {bridge2.center_pos}")
    
    if bridge1.create_structure() and bridge2.create_structure():
        print("✓ Obie struktury utworzone")
    
    bridge1.insert_singularity(sing_a)
    bridge2.insert_singularity(sing_b)
    
    if bridge1.try_link(bridge2):
        print("✓ Mosty połączone między wymiarami!")
        print(f"  Świat docelowy: {bridge1.linked_world}")
        print(f"  Kanały: {bridge1.get_channel_capacity()}")
    
    print(f"\nNBT Mostu 1 (1.18.2): {bridge1.to_nbt()}")


def compare_nbt_structures():
    """Porównuje struktury NBT"""
    print("\n" + "="*60)
    print("PORÓWNANIE NBT QUANTUM BRIDGE")
    print("="*60)
    
    print("\n1.7.10 NBT:")
    print("""
  {
    "x": 100, "y": 64, "z": 100,
    "dim": "overworld",
    "singularity": "sing_abc123_A",
    "pairId": "abc123",
    "linked": "bridge_remote",
    "status": "online"
  }
    """)
    
    print("\n1.18.2 NBT:")
    print("""
  {
    "x": 100, "y": 64, "z": 100,
    "dim": "minecraft:overworld",
    "singularity": "sing_abc123_A",
    "pairId": "abc123",
    "linked": "bridge_nether",
    "linkedDim": "minecraft:the_nether",
    "status": "online",
    "chunkLoaded": true
  }
    """)
    
    print("\nRÓŻNICE:")
    print("- 1.18.2: Pełne ID wymiaru (minecraft:overworld)")
    print("- 1.18.2: linkedDim (świat docelowy)")
    print("- 1.18.2: chunkLoaded (do Spatial Anchor)")
    print("- 1.7.10: Prostsza struktura NBT")


def test_invalid_connections():
    """Test niepoprawnych połączeń"""
    print("\n" + "="*60)
    print("TEST NIEPOPRAWNYCH POŁĄCZEŃ")
    print("="*60)
    
    # Próba połączenia niepasujących singularity
    sing1, _ = QuantumSingularity1710.create_pair()
    sing2, _ = QuantumSingularity1710.create_pair()
    
    bridge1 = QuantumBridge1710("b1", (0, 0, 0))
    bridge2 = QuantumBridge1710("b2", (100, 0, 0))
    
    bridge1.create_structure()
    bridge2.create_structure()
    
    bridge1.insert_singularity(sing1)
    bridge2.insert_singularity(sing2)  # Inna para!
    
    print("\nPróba połączenia niepasujących singularity...")
    if not bridge1.try_link(bridge2):
        print("✓ Połączenie odrzucone (różne pair_id)")
    else:
        print("✗ Błąd - powinno być odrzucone!")


def main():
    """Główna funkcja demonstracyjna"""
    print("="*60)
    print("QUANTUM BRIDGE SIMULATION - AE2 1.7.10 vs 1.18.2")
    print("="*60)
    
    simulate_quantum_connection_1710()
    simulate_quantum_connection_1182()
    compare_nbt_structures()
    test_invalid_connections()
    
    print("\n" + "="*60)
    print("SYMULACJA ZAKOŃCZONA POMYŚLNIE")
    print("="*60)
    print("\nWnioski dla konwersji:")
    print("1. Struktura 3x3 identyczna w obu wersjach")
    print("2. System singularity i pair_id bez zmian")
    print("3. 1.18.2: Lepsza obsługa wymiarów (linkedDim)")
    print("4. 1.18.2: Integracja z Spatial Anchor (chunkLoaded)")
    print("5. NBT wymaga transformacji nazw pól")


if __name__ == "__main__":
    main()
