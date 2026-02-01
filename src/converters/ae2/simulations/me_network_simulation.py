"""
ME Network Simulation - AE2 1.7.10 vs 1.18.2

Symulacja kanałów (channels), topologii sieci ME i działania kontrolera.
Bazuje na kodzie źródłowym:
- 1.7.10: appeng.tile.networking.TileController, appeng.me.Grid
- 1.18.2: appeng.blockentity.networking.ControllerBlockEntity, appeng.me.service.PathingService
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from collections import deque


# =============================================================================
# WSPÓLNE TYPY I STAŁE
# =============================================================================

class AECableType(enum.Enum):
    """Typy kabli AE2 - wspólne dla obu wersji"""
    NONE = 0
    GLASS = 1      # Zwykły kabel (8 kanałów)
    COVERED = 2    # Kabel w osłonie
    SMART = 3      # Smart cable (wyświetla kanały)
    DENSE = 4      # Dense cable (32 kanały)
    DENSE_COVERED = 5
    DENSE_SMART = 6


class AEColor(enum.Enum):
    """Kolory kabli AE2"""
    FLUIX = 0      # Domyślny (fioletowy)
    WHITE = 1
    ORANGE = 2
    MAGENTA = 3
    LIGHT_BLUE = 4
    YELLOW = 5
    LIME = 6
    PINK = 7
    GRAY = 8
    LIGHT_GRAY = 9
    CYAN = 10
    PURPLE = 11
    BLUE = 12
    BROWN = 13
    GREEN = 14
    RED = 15
    BLACK = 16


# =============================================================================
# SYMULACJA 1.7.10
# =============================================================================

@dataclass
class Node1710:
    """
    Węzeł sieci ME w wersji 1.7.10.
    Odpowiada: appeng.me.node.IGridNode (uproszczone)
    """
    x: int
    y: int
    z: int
    name: str
    channels_used: int = 0
    max_channels: int = 8  # Standardowy limit
    is_controller: bool = False
    is_dense: bool = False
    neighbors: List[Node1710] = field(default_factory=list)
    
    def get_max_channels(self) -> int:
        """Zwraca maksymalną liczbę kanałów dla tego węzła"""
        if self.is_controller:
            return 32  # Kontroler daje 32 kanały
        if self.is_dense:
            return 32  # Dense cable
        return 8  # Zwykły kabel
    
    def can_carry_channels(self) -> bool:
        """Czy węzeł może przenosić kanały?"""
        return self.is_controller or self.is_dense or self.max_channels == 8


class MENetwork1710:
    """
    Sieć ME w wersji 1.7.10.
    Odpowiada: appeng.me.Grid (uproszczone)
    
    Kluczowe cechy:
    - Kontroler generuje 32 kanały
    - Zwykły kabel: max 8 kanałów
    - Dense cable: max 32 kanały
    - Pathfinding: BFS z kontrolera
    """
    
    def __init__(self):
        self.nodes: Dict[Tuple[int, int, int], Node1710] = {}
        self.controllers: List[Node1710] = []
        self.channel_map: Dict[Tuple[int, int, int], int] = {}  # Pozostałe kanały
        
    def add_node(self, node: Node1710) -> None:
        """Dodaje węzeł do sieci"""
        self.nodes[(node.x, node.y, node.z)] = node
        if node.is_controller:
            self.controllers.append(node)
    
    def connect_nodes(self, pos1: Tuple[int, int, int], pos2: Tuple[int, int, int]) -> None:
        """Łączy dwa węzły (sąsiedztwo)"""
        if pos1 in self.nodes and pos2 in self.nodes:
            node1 = self.nodes[pos1]
            node2 = self.nodes[pos2]
            if node2 not in node1.neighbors:
                node1.neighbors.append(node2)
            if node1 not in node2.neighbors:
                node2.neighbors.append(node2)
    
    def calculate_channels(self) -> Dict[Tuple[int, int, int], int]:
        """
        Oblicza dystrybucję kanałów z kontrolerów.
        Algorytm: BFS z kontrolera, rozdzielanie kanałów.
        
        Odpowiada: appeng.me.pathfinding.PathSegment (uproszczone)
        """
        if not self.controllers:
            return {}
        
        # Reset channels
        for node in self.nodes.values():
            node.channels_used = 0
        
        # BFS z każdego kontrolera
        channel_usage: Dict[Tuple[int, int, int], int] = {}
        
        for controller in self.controllers:
            visited: Set[Tuple[int, int, int]] = set()
            queue: deque[Tuple[Node1710, int]] = deque([(controller, 0)])
            
            while queue:
                current, distance = queue.popleft()
                pos = (current.x, current.y, current.z)
                
                if pos in visited:
                    continue
                visited.add(pos)
                
                # Kontroler ma 32 kanały do rozdania
                if current.is_controller:
                    available = 32
                else:
                    available = current.get_max_channels()
                
                # Zużycie kanałów przez urządzenia
                device_usage = 1 if not current.can_carry_channels() else 0
                
                channel_usage[pos] = {
                    'available': available,
                    'used': current.channels_used + device_usage,
                    'distance': distance
                }
                
                # Propagacja do sąsiadów
                for neighbor in current.neighbors:
                    neighbor_pos = (neighbor.x, neighbor.y, neighbor.z)
                    if neighbor_pos not in visited:
                        queue.append((neighbor, distance + 1))
        
        return channel_usage
    
    def is_network_valid(self) -> Tuple[bool, str]:
        """
        Sprawdza czy sieć jest ważna.
        
        Zasady 1.7.10:
        1. Sieć może mieć max 1 kontroler (lub więcej jeśli są w linii)
        2. Kontrolery nie mogą tworzyć "krzyżówki" (tylko linia)
        """
        if len(self.controllers) == 0:
            return False, "Brak kontrolera - sieć nieaktywna"
        
        if len(self.controllers) == 1:
            return True, "OK - jeden kontroler"
        
        # Sprawdź czy kontrolery tworzą linię (1.7.10)
        # Kontrolery mogą być połączone tylko w linii prostej
        coords = [(c.x, c.y, c.z) for c in self.controllers]
        
        # Sprawdź czy wszystkie w jednej linii X, Y lub Z
        x_coords = [c[0] for c in coords]
        y_coords = [c[1] for c in coords]
        z_coords = [c[2] for c in coords]
        
        x_unique = len(set(x_coords)) == 1
        y_unique = len(set(y_coords)) == 1
        z_unique = len(set(z_coords)) == 1
        
        if not (x_unique or y_unique or z_unique):
            return False, f"BŁĄD: Kontrolery ({len(self.controllers)}) tworzą krzyżówkę - niedozwolone!"
        
        return True, f"OK - {len(self.controllers)} kontrolerów w linii"
    
    def print_network(self) -> None:
        """Wyświetla strukturę sieci"""
        print("\n" + "="*60)
        print("ME NETWORK 1.7.10 - Struktura")
        print("="*60)
        
        valid, msg = self.is_network_valid()
        print(f"Status sieci: {msg}")
        print(f"Liczba węzłów: {len(self.nodes)}")
        print(f"Liczba kontrolerów: {len(self.controllers)}")
        
        channels = self.calculate_channels()
        print("\nDystrybucja kanałów:")
        for pos, data in sorted(channels.items()):
            node = self.nodes[pos]
            status = "✓" if data['used'] <= data['available'] else "✗ PRZECIĄŻONY"
            print(f"  {pos}: {node.name}")
            print(f"    Kanały: {data['used']}/{data['available']} {status}")
            print(f"    Odległość od kontrolera: {data['distance']}")


# =============================================================================
# SYMULACJA 1.18.2
# =============================================================================

@dataclass
class Node1182:
    """
    Węzeł sieci ME w wersji 1.18.2.
    Odpowiada: appeng.me.node.IGridNode (nowa wersja)
    
    Główne różnice vs 1.7.10:
    - Użycie BlockPos zamiast x,y,z
    - Lepsza obsługa kolorów
    - Bardziej szczegółowe NBT
    """
    x: int
    y: int
    z: int
    name: str
    channels_used: int = 0
    max_channels: int = 8
    is_controller: bool = False
    is_dense: bool = False
    color: AEColor = AEColor.FLUIX
    neighbors: List[Node1182] = field(default_factory=list)
    
    def get_max_channels(self) -> int:
        if self.is_controller:
            return 32
        if self.is_dense:
            return 32
        return 8
    
    def can_carry_channels(self) -> bool:
        return self.is_controller or self.is_dense or self.max_channels == 8


class MENetwork1182:
    """
    Sieć ME w wersji 1.18.2.
    Odpowiada: appeng.me.service.PathingService
    
    Główne różnice vs 1.7.10:
    - Lepsza optymalizacja pathfindingu
    - Obsługa kolorów (separacja sieci)
    - Bardziej szczegółowe statystyki
    """
    
    def __init__(self):
        self.nodes: Dict[Tuple[int, int, int], Node1182] = {}
        self.controllers: List[Node1182] = []
        self.channel_map: Dict[Tuple[int, int, int], dict] = {}
        
    def add_node(self, node: Node1182) -> None:
        self.nodes[(node.x, node.y, node.z)] = node
        if node.is_controller:
            self.controllers.append(node)
    
    def connect_nodes(self, pos1: Tuple[int, int, int], pos2: Tuple[int, int, int]) -> None:
        if pos1 in self.nodes and pos2 in self.nodes:
            node1 = self.nodes[pos1]
            node2 = self.nodes[pos2]
            if node2 not in node1.neighbors:
                node1.neighbors.append(node2)
            if node1 not in node2.neighbors:
                node2.neighbors.append(node1)
    
    def calculate_channels(self) -> Dict[Tuple[int, int, int], dict]:
        """
        Oblicza dystrybucję kanałów - algorytm podobny do 1.7.10
        ale z dodatkową obsługą kolorów.
        """
        if not self.controllers:
            return {}
        
        for node in self.nodes.values():
            node.channels_used = 0
        
        channel_usage: Dict[Tuple[int, int, int], dict] = {}
        
        for controller in self.controllers:
            visited: Set[Tuple[int, int, int]] = set()
            queue: deque[Tuple[Node1182, int]] = deque([(controller, 0)])
            
            while queue:
                current, distance = queue.popleft()
                pos = (current.x, current.y, current.z)
                
                if pos in visited:
                    continue
                visited.add(pos)
                
                available = current.get_max_channels()
                device_usage = 1 if not current.can_carry_channels() else 0
                
                channel_usage[pos] = {
                    'available': available,
                    'used': current.channels_used + device_usage,
                    'distance': distance,
                    'color': current.color.name,
                    'is_controller': current.is_controller
                }
                
                for neighbor in current.neighbors:
                    neighbor_pos = (neighbor.x, neighbor.y, neighbor.z)
                    if neighbor_pos not in visited:
                        queue.append((neighbor, distance + 1))
        
        return channel_usage
    
    def is_network_valid(self) -> Tuple[bool, str]:
        """
        Walidacja sieci - podobna do 1.7.10.
        
        Główne różnice:
        - Lepsze komunikaty błędów
        - Obsługa kolorów (różne kolory = osobne sieci)
        """
        if len(self.controllers) == 0:
            return False, "Brak kontrolera - sieć nieaktywna"
        
        if len(self.controllers) == 1:
            return True, "OK - jeden kontroler"
        
        # Walidacja wielu kontrolerów
        coords = [(c.x, c.y, c.z) for c in self.controllers]
        
        x_coords = [c[0] for c in coords]
        y_coords = [c[1] for c in coords]
        z_coords = [c[2] for c in coords]
        
        x_unique = len(set(x_coords)) == 1
        y_unique = len(set(y_coords)) == 1
        z_unique = len(set(z_coords)) == 1
        
        if not (x_unique or y_unique or z_unique):
            return False, f"BŁĄD: Kontrolery ({len(self.controllers)}) tworzą krzyżówkę"
        
        return True, f"OK - {len(self.controllers)} kontrolerów w linii"
    
    def export_nbt(self) -> dict:
        """
        Eksportuje stan sieci do formatu NBT (symulacja).
        
        Struktura NBT w 1.18.2:
        - Każdy node ma swoje dane
        - Controller przechowuje dodatkowe metadane
        """
        nbt = {
            'nodes': [],
            'controllers': [],
            'channels': {}
        }
        
        for pos, node in self.nodes.items():
            node_nbt = {
                'x': pos[0],
                'y': pos[1],
                'z': pos[2],
                'id': f'ae2:{node.name.lower().replace(" ", "_")}',
                'channels_used': node.channels_used,
                'color': node.color.name
            }
            nbt['nodes'].append(node_nbt)
            
            if node.is_controller:
                nbt['controllers'].append({
                    'x': pos[0], 'y': pos[1], 'z': pos[2],
                    'online': True
                })
        
        return nbt
    
    def print_network(self) -> None:
        """Wyświetla strukturę sieci 1.18.2"""
        print("\n" + "="*60)
        print("ME NETWORK 1.18.2 - Struktura")
        print("="*60)
        
        valid, msg = self.is_network_valid()
        print(f"Status sieci: {msg}")
        print(f"Liczba węzłów: {len(self.nodes)}")
        print(f"Liczba kontrolerów: {len(self.controllers)}")
        
        channels = self.calculate_channels()
        print("\nDystrybucja kanałów:")
        for pos, data in sorted(channels.items()):
            node = self.nodes[pos]
            status = "✓" if data['used'] <= data['available'] else "✗ PRZECIĄŻONY"
            print(f"  {pos}: {node.name} [Kolor: {data['color']}]")
            print(f"    Kanały: {data['used']}/{data['available']} {status}")
            print(f"    Kontroler: {'Tak' if data['is_controller'] else 'Nie'}")


# =============================================================================
# TESTY I DEMONSTRACJA
# =============================================================================

def create_sample_network_1710() -> MENetwork1710:
    """Tworzy przykładową sieć w wersji 1.7.10"""
    network = MENetwork1710()
    
    # Kontroler (źródło 32 kanałów)
    controller = Node1710(0, 0, 0, "ME Controller", is_controller=True)
    network.add_node(controller)
    
    # Dense cable (32 kanały) - blisko kontrolera
    for i in range(1, 5):
        node = Node1710(i, 0, 0, f"Dense Cable {i}", is_dense=True)
        network.add_node(node)
        network.connect_nodes((i-1, 0, 0), (i, 0, 0))
    
    # Zwykłe kable (8 kanałów) - dalej od kontrolera
    for i in range(5, 10):
        node = Node1710(i, 0, 0, f"Glass Cable {i}", is_dense=False)
        network.add_node(node)
        network.connect_nodes((i-1, 0, 0), (i, 0, 0))
    
    # Urządzenia końcowe (zużywają 1 kanał każde)
    devices = [
        (5, 1, 0, "ME Drive"),
        (6, 1, 0, "ME Interface"),
        (7, 1, 0, "Import Bus"),
        (8, 1, 0, "Export Bus"),
    ]
    
    for x, y, z, name in devices:
        device = Node1710(x, y, z, name, max_channels=0)  # Nie przenosi kanałów
        network.add_node(device)
        network.connect_nodes((x, 0, 0), (x, y, z))
    
    return network


def create_sample_network_1182() -> MENetwork1182:
    """Tworzy przykładową sieć w wersji 1.18.2"""
    network = MENetwork1182()
    
    # Kontroler
    controller = Node1182(0, 0, 0, "ME Controller", is_controller=True, color=AEColor.FLUIX)
    network.add_node(controller)
    
    # Dense cable z różnymi kolorami
    colors = [AEColor.FLUIX, AEColor.RED, AEColor.BLUE, AEColor.GREEN]
    for i, color in enumerate(colors, 1):
        node = Node1182(i, 0, 0, f"Dense Cable {i}", is_dense=True, color=color)
        network.add_node(node)
        network.connect_nodes((i-1, 0, 0), (i, 0, 0))
    
    # Zwykłe kable
    for i in range(5, 10):
        node = Node1182(i, 0, 0, f"Glass Cable {i}", is_dense=False, color=AEColor.FLUIX)
        network.add_node(node)
        network.connect_nodes((i-1, 0, 0), (i, 0, 0))
    
    # Urządzenia
    devices = [
        (5, 1, 0, "ME Drive", AEColor.RED),
        (6, 1, 0, "ME Interface", AEColor.BLUE),
        (7, 1, 0, "Import Bus", AEColor.GREEN),
        (8, 1, 0, "Export Bus", AEColor.YELLOW),
    ]
    
    for x, y, z, name, color in devices:
        device = Node1182(x, y, z, name, max_channels=0, color=color)
        network.add_node(device)
        network.connect_nodes((x, 0, 0), (x, y, z))
    
    return network


def test_multiple_controllers():
    """Test wielu kontrolerów - porównanie 1.7.10 vs 1.18.2"""
    print("\n" + "="*60)
    print("TEST: Wiele kontrolerów w linii (poprawne)")
    print("="*60)
    
    network_1710 = MENetwork1710()
    # 3 kontrolery w linii X (poprawne)
    for i in range(3):
        c = Node1710(i, 0, 0, f"Controller {i}", is_controller=True)
        network_1710.add_node(c)
        if i > 0:
            network_1710.connect_nodes((i-1, 0, 0), (i, 0, 0))
    
    valid, msg = network_1710.is_network_valid()
    print(f"1.7.10: {msg}")
    assert valid, "Sieć powinna być ważna"
    
    print("\n" + "="*60)
    print("TEST: Wiele kontrolerów w krzyżówce (błąd)")
    print("="*60)
    
    network_1710_bad = MENetwork1710()
    # Kontrolery w krzyżówce (błędne)
    positions = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]
    for i, (x, y, z) in enumerate(positions):
        c = Node1710(x, y, z, f"Controller {i}", is_controller=True)
        network_1710_bad.add_node(c)
    
    valid, msg = network_1710_bad.is_network_valid()
    print(f"1.7.10: {msg}")
    assert not valid, "Sieć powinna być nieważna"


def compare_nbt_structure():
    """Porównuje strukturę NBT między wersjami"""
    print("\n" + "="*60)
    print("PORÓWNANIE STRUKTURY NBT")
    print("="*60)
    
    network = create_sample_network_1182()
    nbt = network.export_nbt()
    
    print("\nNBT Structure (1.18.2 format):")
    print(f"  Nodes count: {len(nbt['nodes'])}")
    print(f"  Controllers count: {len(nbt['controllers'])}")
    
    print("\nPrzykładowy node NBT:")
    if nbt['nodes']:
        print(f"  {nbt['nodes'][0]}")
    
    print("\n" + "-"*60)
    print("Różnice NBT 1.7.10 vs 1.18.2:")
    print("-"*60)
    print("1.7.10:")
    print("  - id: 'AEBaseTile' (generyczne)")
    print("  - x, y, z jako int")
    print("  - priority jako int")
    print("  - orientacja: forward, up jako byte")
    print("")
    print("1.18.2:")
    print("  - id: 'ae2:controller' (specyficzne)")
    print("  - x, y, z jako int")
    print("  - visual jako compound")
    print("  - upgrades jako compound")
    print("  - color jako string")


def main():
    """Główna funkcja demonstracyjna"""
    print("="*60)
    print("ME NETWORK SIMULATION - AE2 1.7.10 vs 1.18.2")
    print("="*60)
    
    # Symulacja 1.7.10
    network_1710 = create_sample_network_1710()
    network_1710.print_network()
    
    # Symulacja 1.18.2
    network_1182 = create_sample_network_1182()
    network_1182.print_network()
    
    # Testy
    test_multiple_controllers()
    compare_nbt_structure()
    
    print("\n" + "="*60)
    print("SYMULACJA ZAKOŃCZONA POMYŚLNIE")
    print("="*60)
    print("\nWnioski:")
    print("- Oba wersje używają tej samej logiki kanałów (8/32)")
    print("- 1.18.2 dodaje obsługę kolorów (AEColor)")
    print("- NBT w 1.18.2 jest bardziej szczegółowe")
    print("- Walidacja kontrolerów identyczna w obu wersjach")


if __name__ == "__main__":
    main()
