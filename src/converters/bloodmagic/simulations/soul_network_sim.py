"""
Symulacja Soul Network - Blood Magic 1.7.10 vs 1.18.2

Source mapping:
- 1.7.10: WayofTime/alchemicalWizardry/api/soulNetwork/SoulNetworkHandler.java
  - getCurrentEssence: linie 231-248
  - syphonFromNetwork: linie 111-135
  - addCurrentEssenceToMaximum: linie 278-315
  - getMaximumForOrbTier: linie 79-98
  
- 1.18.2: wayoftime/bloodmagic/core/data/SoulNetwork.java
  - getCurrentEssence: standardowy getter
  - syphon: linie ~150-200
  - add: linie ~100-150
  
- 1.18.2: wayoftime/bloodmagic/util/helper/NetworkHelper.java
  - getSoulNetwork: zarządzanie sieciami

Kluczowe różnice:
- 1.7.10: Dane przechowywane w LifeEssenceNetwork (MapStorage)
  - Klucz: "ownerName" (nazwa gracza jako string)
  - Pola: currentEssence (int), maxOrb (int)
  
- 1.18.2: Dane przechowywane w SoulNetwork (Capability)
  - Klucz: UUID gracza
  - Pola: currentEssence (int), orbTier (int)
  
- Blood Orbs w 1.7.10 przechowują "ownerName" w NBT
- Blood Orbs w 1.18.2 przechowują Binding (UUID + nazwa)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, Tuple
from uuid import UUID


class BloodOrb(Enum):
    """Typy Blood Orbów i ich maksymalna pojemność - identyczne w obu wersjach"""
    WEAK = (1, 5000, "weak_blood_orb")
    APPRENTICE = (2, 25000, "apprentice_blood_orb")
    MAGICIAN = (3, 150000, "magician_blood_orb")
    MASTER = (4, 1000000, "master_blood_orb")
    ARCHMAGE = (5, 10000000, "archmage_blood_orb")
    TRANSCENDENT = (6, 30000000, "transcendent_blood_orb")  # Tylko 1.7.10
    
    def __init__(self, tier: int, capacity: int, item_id: str):
        self.tier = tier
        self.capacity = capacity
        self.item_id = item_id


@dataclass
class SoulNetworkState:
    """Stan Soul Network"""
    owner_name: str = ""  # 1.7.10 - nazwa gracza
    owner_uuid: Optional[UUID] = None  # 1.18.2 - UUID gracza
    current_essence: int = 0
    max_orb_tier: int = 0  # Najwyższy tier orba jakiego użył gracz
    
    # Dodatkowe dla 1.18.2
    orb_tier: int = 0


class SoulNetworkSimulation:
    """
    Symulacja Soul Network dla konwersji 1.7.10 -> 1.18.2
    
    Soul Network to globalny zbiornik LP (Life Essence) dla każdego gracza.
    Wszystkie przedmioty powiązane z danym graczem korzystają z tej samej sieci.
    """
    
    def __init__(self, version: str = "1.7.10"):
        """
        Args:
            version: "1.7.10" lub "1.18.2"
        """
        self.version = version
        self.state = SoulNetworkState()
        
        # Symulacja globalnego storage (wszystkie sieci na serwerze)
        self._networks: Dict[str, SoulNetworkState] = {}
    
    def load_from_nbt_1710(self, nbt_data: Dict[str, Any], owner_name: str) -> None:
        """
        Wczytaj stan z NBT 1.7.10 (LifeEssenceNetwork)
        
        Source: LifeEssenceNetwork.readFromNBT()
        """
        self.state.owner_name = owner_name
        self.state.current_essence = nbt_data.get("currentEssence", 0)
        self.state.max_orb_tier = nbt_data.get("maxOrb", 0)
        
    def load_from_nbt_1182(self, nbt_data: Dict[str, Any], owner_uuid: UUID) -> None:
        """
        Wczytaj stan z NBT 1.18.2 (SoulNetwork)
        
        Source: SoulNetwork.serializeNBT()
        """
        self.state.owner_uuid = owner_uuid
        self.state.owner_name = nbt_data.get("playerName", "")
        self.state.current_essence = nbt_data.get("currentEssence", 0)
        self.state.orb_tier = nbt_data.get("orbTier", 0)
        
    def convert_to_1182_nbt(self, owner_uuid: UUID) -> Dict[str, Any]:
        """
        Konwertuj stan do formatu NBT 1.18.2
        
        Args:
            owner_uuid: UUID gracza w 1.18.2
            
        Returns:
            Dict zgodny ze strukturą NBT 1.18.2
        """
        return {
            "currentEssence": self.state.current_essence,
            "orbTier": self.state.max_orb_tier,  # maxOrb z 1.7.10 -> orbTier w 1.18.2
            "playerName": self.state.owner_name,  # Zachowana dla kompatybilności
        }
    
    def get_maximum_for_orb_tier(self, tier: int) -> int:
        """
        Pobierz maksymalną pojemność dla danego tieru orba
        
        Source 1.7.10: SoulNetworkHandler.getMaximumForOrbTier() linie 79-98
        
        Args:
            tier: Tier orba (1-6)
            
        Returns:
            Maksymalna pojemność w LP
        """
        max_map = {
            1: 5000,
            2: 25000,
            3: 150000,
            4: 1000000,
            5: 10000000,
            6: 30000000,
        }
        return max_map.get(tier, 1)
    
    def syphon_from_network(self, amount: int) -> int:
        """
        Pobierz LP z sieci
        
        Source 1.7.10: SoulNetworkHandler.syphonFromNetwork() linie 111-135
        Source 1.18.2: SoulNetwork.syphon()
        
        Args:
            amount: Ilość LP do pobrania
            
        Returns:
            Rzeczywiście pobrana ilość LP
        """
        if self.state.current_essence >= amount:
            self.state.current_essence -= amount
            return amount
        return 0
    
    def add_to_network(self, amount: int, maximum: int) -> int:
        """
        Dodaj LP do sieci (z limitem)
        
        Source 1.7.10: SoulNetworkHandler.addCurrentEssenceToMaximum() linie 278-315
        Source 1.18.2: SoulNetwork.add()
        
        Args:
            amount: Ilość LP do dodania
            maximum: Maksymalna pojemność (zazwyczaj z orba)
            
        Returns:
            Rzeczywiście dodana ilość LP
        """
        if self.state.current_essence >= maximum:
            return 0
        
        new_essence = min(maximum, self.state.current_essence + amount)
        added = new_essence - self.state.current_essence
        self.state.current_essence = new_essence
        
        return added
    
    def can_syphon(self, amount: int) -> bool:
        """Sprawdź czy można pobrać daną ilość LP"""
        return self.state.current_essence >= amount
    
    def set_orb_tier(self, tier: int) -> None:
        """
        Ustaw najwyższy tier orba użyty przez gracza
        
        Source 1.7.10: SoulNetworkHandler.setMaxOrbToMax() linie 59-77
        """
        self.state.max_orb_tier = max(tier, self.state.max_orb_tier)


class BloodOrbSimulation:
    """
    Symulacja Blood Orbs i ich bindingu do graczy
    
    Source 1.7.10: IBloodOrb interfejs i implementacje
    Source 1.18.2: IBloodOrb, IBindable, BloodOrb
    """
    
    def __init__(self, version: str = "1.7.10"):
        self.version = version
    
    def bind_orb_1710(self, item_nbt: Dict[str, Any], owner_name: str) -> Dict[str, Any]:
        """
        Binduj orb do gracza w formacie 1.7.10
        
        W 1.7.10 binding przechowywany jest jako "ownerName" w NBT przedmiotu
        """
        if "tag" not in item_nbt:
            item_nbt["tag"] = {}
        
        item_nbt["tag"]["ownerName"] = owner_name
        return item_nbt
    
    def bind_orb_1182(self, item_nbt: Dict[str, Any], owner_uuid: UUID, owner_name: str) -> Dict[str, Any]:
        """
        Binduj orb do gracza w formacie 1.18.2
        
        W 1.18.2 binding jest złożonym obiektem z UUID i nazwą
        """
        if "tag" not in item_nbt:
            item_nbt["tag"] = {}
        
        # W 1.18.2 binding jest przechowywany jako osobny obiekt
        item_nbt["tag"]["binding"] = {
            "ownerUUID": str(owner_uuid),
            "ownerName": owner_name,
        }
        return item_nbt
    
    def convert_orb_binding(self, item_nbt_1710: Dict[str, Any], owner_uuid: UUID) -> Dict[str, Any]:
        """
        Konwertuj binding orba z 1.7.10 do 1.18.2
        
        Args:
            item_nbt_1710: NBT przedmiotu z 1.7.10
            owner_uuid: UUID gracza w 1.18.2 (z mapowania nazwa->UUID)
            
        Returns:
            NBT przedmiotu w formacie 1.18.2
        """
        tag = item_nbt_1710.get("tag", {})
        owner_name = tag.get("ownerName", "")
        
        if not owner_name:
            # Niezbindowany orb - zwróć bez zmian struktury
            return item_nbt_1710
        
        # Konwertuj do formatu 1.18.2
        result = {
            "id": self._map_orb_id(item_nbt_1710.get("id", "")),
            "Count": item_nbt_1710.get("Count", 1),
            "tag": {
                "binding": {
                    "ownerUUID": str(owner_uuid),
                    "ownerName": owner_name,
                }
            }
        }
        
        return result
    
    def _map_orb_id(self, old_id: str) -> str:
        """Mapuj ID orba z 1.7.10 do 1.18.2"""
        mapping = {
            "AWWayofTime:weakBloodOrb": "bloodmagic:weak_blood_orb",
            "AWWayofTime:apprenticeBloodOrb": "bloodmagic:apprentice_blood_orb",
            "AWWayofTime:magicianBloodOrb": "bloodmagic:magician_blood_orb",
            "AWWayofTime:masterBloodOrb": "bloodmagic:master_blood_orb",
            "AWWayofTime:archmageBloodOrb": "bloodmagic:archmage_blood_orb",
            "AWWayofTime:transcendentBloodOrb": "bloodmagic:archmage_blood_orb",  # Transcendent -> Archmage
        }
        return mapping.get(old_id, old_id.replace("AWWayofTime:", "bloodmagic:"))


def test_soul_network_simulation():
    """Test symulacji Soul Network"""
    print("=== Test symulacji Soul Network ===\n")
    
    # Symulacja sieci w 1.7.10
    network_1710 = SoulNetworkSimulation("1.7.10")
    network_1710.load_from_nbt_1710(
        {"currentEssence": 50000, "maxOrb": 3},
        owner_name="Player123"
    )
    
    print(f"Sieć 1.7.10:")
    print(f"  Właściciel: {network_1710.state.owner_name}")
    print(f"  LP: {network_1710.state.current_essence}")
    print(f"  Max Orb Tier: {network_1710.state.max_orb_tier}")
    
    # Konwersja do 1.18.2
    from uuid import uuid4
    test_uuid = uuid4()
    
    nbt_1182 = network_1710.convert_to_1182_nbt(test_uuid)
    
    network_1182 = SoulNetworkSimulation("1.18.2")
    network_1182.load_from_nbt_1182(nbt_1182, test_uuid)
    
    print(f"\nPo konwersji do 1.18.2:")
    print(f"  UUID: {network_1182.state.owner_uuid}")
    print(f"  Nazwa: {network_1182.state.owner_name}")
    print(f"  LP: {network_1182.state.current_essence}")
    print(f"  Orb Tier: {network_1182.state.orb_tier}")
    
    # Test zużycia LP
    print("\n=== Test zużycia LP ===")
    
    # Symulacja rytuału zużywającego LP
    ritual_cost = 1000
    syphoned = network_1182.syphon_from_network(ritual_cost)
    print(f"Rytuał próbuje zużyć {ritual_cost} LP")
    print(f"Rzeczywiście zużyto: {syphoned} LP")
    print(f"Pozostało w sieci: {network_1182.state.current_essence} LP")
    
    # Test dodawania LP przez orb
    print("\n=== Test napełniania orba ===")
    orb_capacity = BloodOrb.MAGICIAN.capacity  # 150000
    
    # Symulacja napełniania z ołtarza
    added = network_1182.add_to_network(10000, orb_capacity)
    print(f"Próba dodania 10000 LP (max: {orb_capacity})")
    print(f"Dodano: {added} LP")
    print(f"Stan sieci: {network_1182.state.current_essence} LP")
    
    # Test bindingu orba
    print("\n=== Test bindingu orba ===")
    orb_sim = BloodOrbSimulation()
    
    # 1.7.10
    orb_1710 = {"id": "AWWayofTime:apprenticeBloodOrb", "Count": 1}
    orb_1710_bound = orb_sim.bind_orb_1710(orb_1710, "Player123")
    print(f"Orb 1.7.10 po bindingu: {orb_1710_bound}")
    
    # Konwersja do 1.18.2
    orb_1182 = orb_sim.convert_orb_binding(orb_1710_bound, test_uuid)
    print(f"\nOrb po konwersji do 1.18.2:")
    print(f"  ID: {orb_1182['id']}")
    print(f"  Binding: {orb_1182['tag']['binding']}")


if __name__ == "__main__":
    test_soul_network_simulation()
