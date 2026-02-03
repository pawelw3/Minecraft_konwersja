"""
Symulacja Master Ritual Stone - Blood Magic 1.7.10 vs 1.18.2

Source mapping:
- 1.7.10: WayofTime/alchemicalWizardry/common/tileEntity/TEMasterStone.java
  - NBT: ritualType, owner, isActive, cooldown, runningTime
  
- 1.7.10: WayofTime/alchemicalWizardry/api/rituals/Rituals.java
  - Rejestracja rytuałów
  
- 1.18.2: wayoftime/bloodmagic/ritual/Ritual.java
  - Nowa struktura rytuałów
  
- 1.18.2: wayoftime/bloodmagic/tile/TileMasterRitualStone.java
  - NBT: ritualID, owner, active, cooldown

Kluczowe różnice:
- 1.7.10: "ritualType" jako string (np. "water", "suffering")
- 1.18.2: "ritualID" jako ResourceLocation (np. "bloodmagic:water")
- 1.18.2 dodaje: demonWill (nowa mechanika)
- Struktury rytualne są identyczne w obu wersjach
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Tuple, Optional
from uuid import UUID


class RitualType(Enum):
    """Typy rytuałów w Blood Magic - mapowanie 1.7.10 -> 1.18.2"""
    # Podstawowe rytuały
    WATER = ("water", "bloodmagic:water", 500)
    LAVA = ("lava", "bloodmagic:lava", 1000)
    GREEN_GROVE = ("greenGrove", "bloodmagic:growth", 1000)
    HIGH_JUMP = ("highJump", "bloodmagic:jumping", 1000)
    SPEED = ("speed", "bloodmagic:speed", 1000)
    
    # Zaawansowane rytuały
    WELL_OF_SUFFERING = ("suffering", "bloodmagic:well_of_suffering", 5000)
    REGENERATION = ("regeneration", "bloodmagic:regeneration", 5000)
    FEATHERED_KNIFE = ("featheredKnife", "bloodmagic:feathered_knife", 2000)
    MAGNETISM = ("magnetism", "bloodmagic:magnetism", 5000)
    CRUSHER = ("crushing", "bloodmagic:crushing", 10000)
    
    # Inne
    FULL_STOMACH = ("fullStomach", "bloodmagic:satiated_stomach", 10000)
    INTERDICTION = ("interdiction", "bloodmagic:interdiction", 1000)
    
    def __init__(self, id_1710: str, id_1182: str, base_cost: int):
        self.id_1710 = id_1710
        self.id_1182 = id_1182
        self.base_cost = base_cost


@dataclass
class RitualComponent:
    """Komponent rytuału (Ritual Stone na określonej pozycji)"""
    x: int
    y: int
    z: int
    type: str  # FIRE, EARTH, WATER, AIR, DUSK, DAWN


@dataclass
class RitualState:
    """Stan Master Ritual Stone"""
    # 1.7.10
    ritual_type: str = ""  # np. "water", "suffering"
    owner: str = ""  # ownerName
    is_active: bool = False
    cooldown: int = 0
    running_time: int = 0
    
    # 1.18.2
    ritual_id: str = ""  # np. "bloodmagic:water"
    owner_uuid: Optional[UUID] = None
    will_drain: int = 0  # Nowa mechanika Demon Will


class MasterRitualStoneSimulation:
    """
    Symulacja Master Ritual Stone dla konwersji 1.7.10 -> 1.18.2
    
    Master Ritual Stone to centralny blok aktywujący rytuały.
    Rytuały zużywają LP z Soul Network właściciela.
    """
    
    def __init__(self, version: str = "1.7.10"):
        """
        Args:
            version: "1.7.10" lub "1.18.2"
        """
        self.version = version
        self.state = RitualState()
        
    def load_from_nbt_1710(self, nbt_data: Dict[str, Any]) -> None:
        """
        Wczytaj stan z NBT 1.7.10
        
        Source: TEMasterStone.readFromNBT()
        """
        self.state.ritual_type = nbt_data.get("ritualType", "")
        self.state.owner = nbt_data.get("owner", "")
        self.state.is_active = nbt_data.get("isActive", False)
        self.state.cooldown = nbt_data.get("cooldown", 0)
        self.state.running_time = nbt_data.get("runningTime", 0)
        
    def load_from_nbt_1182(self, nbt_data: Dict[str, Any]) -> None:
        """
        Wczytaj stan z NBT 1.18.2
        
        Source: TileMasterRitualStone.load()
        """
        self.state.ritual_id = nbt_data.get("ritualID", "")
        self.state.owner = nbt_data.get("owner", "")
        uuid_str = nbt_data.get("ownerUUID", "")
        if uuid_str:
            self.state.owner_uuid = UUID(uuid_str)
        self.state.is_active = nbt_data.get("active", False)
        self.state.cooldown = nbt_data.get("cooldown", 0)
        self.state.will_drain = nbt_data.get("willDrain", 0)
    
    def convert_to_1182_nbt(self, owner_uuid: UUID) -> Dict[str, Any]:
        """
        Konwertuj stan do formatu NBT 1.18.2
        
        Args:
            owner_uuid: UUID właściciela w 1.18.2
            
        Returns:
            Dict zgodny ze strukturą NBT 1.18.2
        """
        # Mapuj typ rytuału
        ritual_id = self._map_ritual_id(self.state.ritual_type)
        
        return {
            "ritualID": ritual_id,
            "owner": self.state.owner,
            "ownerUUID": str(owner_uuid),
            "active": self.state.is_active,
            "cooldown": self.state.cooldown,
            "willDrain": 0,  # Nowa mechanika - ustawiamy na 0
        }
    
    def _map_ritual_id(self, ritual_type_1710: str) -> str:
        """Mapuj ID rytuału z 1.7.10 do 1.18.2"""
        for ritual in RitualType:
            if ritual.id_1710 == ritual_type_1710:
                return ritual.id_1182
        
        # Fallback - przedrostek bloodmagic:
        return f"bloodmagic:{ritual_type_1710}"
    
    def get_ritual_cost(self) -> int:
        """Pobierz koszt rytuału"""
        for ritual in RitualType:
            if ritual.id_1710 == self.state.ritual_type or ritual.id_1182 == self.state.ritual_id:
                return ritual.base_cost
        return 1000  # Domyślny koszt
    
    def simulate_activation(self, soul_network_lp: int) -> Tuple[bool, str]:
        """
        Symuluj aktywację rytuału
        
        Args:
            soul_network_lp: Aktualna ilość LP w sieci właściciela
            
        Returns:
            (czy_aktywowany, komunikat)
        """
        # Sprawdź czy mamy wystarczająco LP
        cost = self.get_ritual_cost()
        
        if soul_network_lp < cost:
            return False, f"Niewystarczająca ilość LP (wymagane: {cost}, dostępne: {soul_network_lp})"
        
        self.state.is_active = True
        self.state.cooldown = 0
        
        return True, f"Rytuał aktywowany (koszt: {cost} LP)"
    
    def simulate_tick(self) -> Tuple[bool, int]:
        """
        Symuluj jeden tick rytuału
        
        Returns:
            (czy_dalej_aktywny, lp_zużyte)
        """
        if not self.state.is_active:
            return False, 0
        
        # Zwiększ czas działania
        self.state.running_time += 1
        
        # Sprawdź cooldown
        if self.state.cooldown > 0:
            self.state.cooldown -= 1
            return True, 0
        
        # Rytuały zużywają LP cyklicznie (zazwyczaj co 25 ticków)
        if self.state.running_time % 25 == 0:
            cost = self.get_ritual_cost()
            return True, cost
        
        return True, 0
    
    def deactivate(self) -> None:
        """Dezaktywuj rytuał"""
        self.state.is_active = False
        self.state.running_time = 0
        self.state.cooldown = 0


class RitualStructureValidator:
    """
    Walidator struktur rytuałów
    
    Rytuały wymagają specyficznego układu Ritual Stones wokół Master Ritual Stone.
    Struktury są identyczne w obu wersjach.
    """
    
    # Struktury rytuałów z kodu źródłowego
    RITUAL_STRUCTURES = {
        "water": [
            RitualComponent(0, 0, 1, "WATER"),
            RitualComponent(0, 0, -1, "WATER"),
            RitualComponent(1, 0, 0, "WATER"),
            RitualComponent(-1, 0, 0, "WATER"),
        ],
        "suffering": [
            # Z kodu RitualEffectWellOfSuffering.java
            RitualComponent(1, 0, 1, "FIRE"),
            RitualComponent(-1, 0, 1, "FIRE"),
            RitualComponent(1, 0, -1, "FIRE"),
            RitualComponent(-1, 0, -1, "FIRE"),
            RitualComponent(2, -1, 2, "FIRE"),
            RitualComponent(2, -1, -2, "FIRE"),
            RitualComponent(-2, -1, 2, "FIRE"),
            RitualComponent(-2, -1, -2, "FIRE"),
            RitualComponent(0, -1, 2, "EARTH"),
            RitualComponent(2, -1, 0, "EARTH"),
            RitualComponent(0, -1, -2, "EARTH"),
            RitualComponent(-2, -1, 0, "EARTH"),
        ],
    }
    
    @classmethod
    def validate_structure(cls, ritual_type: str, blocks: List[Tuple[int, int, int, str]]) -> bool:
        """
        Sprawdź czy struktura rytuału jest poprawna
        
        Args:
            ritual_type: Typ rytuału
            blocks: Lista bloków jako (x, y, z, type)
            
        Returns:
            True jeśli struktura jest poprawna
        """
        required = cls.RITUAL_STRUCTURES.get(ritual_type, [])
        
        if not required:
            return True  # Nieznany rytuał - zakładamy poprawny
        
        # Sprawdź czy wszystkie wymagane bloki są obecne
        for component in required:
            found = False
            for block in blocks:
                if (block[0] == component.x and 
                    block[1] == component.y and 
                    block[2] == component.z):
                    found = True
                    break
            if not found:
                return False
        
        return True


def test_ritual_simulation():
    """Test symulacji Master Ritual Stone"""
    print("=== Test symulacji Master Ritual Stone ===\n")
    
    # Symulacja w 1.7.10
    ritual_1710 = MasterRitualStoneSimulation("1.7.10")
    ritual_1710.load_from_nbt_1710({
        "ritualType": "suffering",
        "owner": "Player123",
        "isActive": True,
        "cooldown": 0,
        "runningTime": 100,
    })
    
    print(f"Rytuał 1.7.10:")
    print(f"  Typ: {ritual_1710.state.ritual_type}")
    print(f"  Właściciel: {ritual_1710.state.owner}")
    print(f"  Aktywny: {ritual_1710.state.is_active}")
    print(f"  Czas działania: {ritual_1710.state.running_time}")
    print(f"  Koszt: {ritual_1710.get_ritual_cost()} LP")
    
    # Konwersja do 1.18.2
    from uuid import uuid4
    test_uuid = uuid4()
    
    nbt_1182 = ritual_1710.convert_to_1182_nbt(test_uuid)
    
    ritual_1182 = MasterRitualStoneSimulation("1.18.2")
    ritual_1182.load_from_nbt_1182(nbt_1182)
    
    print(f"\nPo konwersji do 1.18.2:")
    print(f"  ID: {ritual_1182.state.ritual_id}")
    print(f"  Właściciel: {ritual_1182.state.owner}")
    print(f"  UUID: {ritual_1182.state.owner_uuid}")
    print(f"  Aktywny: {ritual_1182.state.is_active}")
    
    # Test aktywacji
    print("\n=== Test aktywacji ===")
    
    # Próba z małą ilością LP
    success, msg = ritual_1182.simulate_activation(100)
    print(f"Próba aktywacji z 100 LP: {msg}")
    
    # Próba z wystarczającą ilością
    success, msg = ritual_1182.simulate_activation(10000)
    print(f"Próba aktywacji z 10000 LP: {msg}")
    
    # Test ticków
    print("\n=== Test ticków rytuału ===")
    total_cost = 0
    for tick in range(100):
        active, cost = ritual_1182.simulate_tick()
        total_cost += cost
        if cost > 0:
            print(f"Tick {tick}: Zużyto {cost} LP")
    
    print(f"\nCałkowity koszt po 100 tickach: {total_cost} LP")
    
    # Walidacja struktury
    print("\n=== Test walidacji struktury ===")
    validator = RitualStructureValidator()
    
    # Poprawna struktura Well of Suffering
    correct_structure = [
        (1, 0, 1, "FIRE"),
        (-1, 0, 1, "FIRE"),
        (1, 0, -1, "FIRE"),
        (-1, 0, -1, "FIRE"),
        (2, -1, 2, "FIRE"),
        (2, -1, -2, "FIRE"),
        (-2, -1, 2, "FIRE"),
        (-2, -1, -2, "FIRE"),
        (0, -1, 2, "EARTH"),
        (2, -1, 0, "EARTH"),
        (0, -1, -2, "EARTH"),
        (-2, -1, 0, "EARTH"),
    ]
    
    is_valid = validator.validate_structure("suffering", correct_structure)
    print(f"Poprawna struktura: {'TAK' if is_valid else 'NIE'}")
    
    # Niepoprawna struktura (brakuje elementów)
    wrong_structure = [
        (1, 0, 1, "FIRE"),
        (-1, 0, 1, "FIRE"),
    ]
    
    is_valid = validator.validate_structure("suffering", wrong_structure)
    print(f"Niepoprawna struktura: {'TAK' if is_valid else 'NIE'}")


if __name__ == "__main__":
    test_ritual_simulation()
