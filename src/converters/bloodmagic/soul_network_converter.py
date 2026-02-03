"""
Konwerter Soul Network - Blood Magic 1.7.10 -> 1.18.2

Source mapping:
- 1.7.10: WayofTime/alchemicalWizardry/api/soulNetwork/LifeEssenceNetwork.java
  - Dane przechowywane w MapStorage (globalne dla świata)
  - Klucz: "ownerName" (nazwa gracza jako string)
  - Pola: currentEssence (int), maxOrb (int) - najwyższy użyty tier
  
- 1.18.2: wayoftime/bloodmagic/core/data/SoulNetwork.java
  - Dane przechowywane w Capability (per-gracz)
  - Klucz: UUID gracza
  - Pola: currentEssence (int), orbTier (int)
  
- 1.18.2: wayoftime/bloodmagic/util/helper/NetworkHelper.java
  - Zarządzanie sieciami graczy

Konwersja:
- ownerName (string) -> UUID (z mapowania nazwa->UUID z playerdata)
- currentEssence -> currentEssence (bez zmian)
- maxOrb (int) -> orbTier (int) (bez zmian, ten sam zakres 1-6)
"""

from typing import Dict, Any, Optional, Tuple, List
from uuid import UUID
from dataclasses import dataclass


@dataclass
class SoulNetworkData:
    """Dane Soul Network dla gracza"""
    owner_name: str  # Nazwa gracza z 1.7.10
    owner_uuid: Optional[UUID]  # UUID w 1.18.2
    current_essence: int
    max_orb_tier: int  # maxOrb z 1.7.10 / orbTier w 1.18.2
    warnings: List[str]


class SoulNetworkConverter:
    """
    Konwerter Soul Network z 1.7.10 na 1.18.2
    
    Soul Network to globalny zbiornik LP dla każdego gracza.
    Dane są przechowywane w NBT świata, nie w blokach.
    """
    
    # Mapowanie nazwy gracza na UUID (do uzupełnienia z playerdata)
    _name_to_uuid: Dict[str, UUID] = {}
    
    def __init__(self, name_to_uuid_mapping: Optional[Dict[str, UUID]] = None):
        """
        Args:
            name_to_uuid_mapping: Opcjonalne mapowanie nazw graczy na UUID
        """
        self.warnings = []
        if name_to_uuid_mapping:
            self._name_to_uuid = name_to_uuid_mapping
    
    def set_name_to_uuid_mapping(self, mapping: Dict[str, UUID]) -> None:
        """
        Ustaw mapowanie nazw graczy na UUID
        
        Args:
            mapping: Słownik {nazwa_gracza: UUID}
        """
        self._name_to_uuid = mapping
    
    def convert_player_network(
        self, 
        owner_name: str,
        nbt_1710: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], list]:
        """
        Konwertuj Soul Network jednego gracza z 1.7.10 na 1.18.2
        
        Args:
            owner_name: Nazwa gracza z 1.7.10
            nbt_1710: Dane Soul Network z 1.7.10
            
        Returns:
            Tuple (nbt_1182, warnings)
        """
        self.warnings = []
        result = {}
        
        # Podstawowe pola
        result["currentEssence"] = nbt_1710.get("currentEssence", 0)
        result["orbTier"] = nbt_1710.get("maxOrb", 0)
        result["playerName"] = owner_name  # Zachowana dla czytelności
        
        # Konwersja nazwy na UUID
        owner_uuid = self._resolve_uuid(owner_name)
        
        if owner_uuid:
            result["ownerUUID"] = str(owner_uuid)
        else:
            self.warnings.append(
                f"BM-W-NETWORK-NO-UUID: Nie znaleziono UUID dla gracza '{owner_name}' - "
                f"Soul Network może nie działać poprawnie w 1.18.2"
            )
        
        # Sprawdź czy gracz ma LP w sieci
        if result["currentEssence"] > 0:
            max_capacity = self._get_orb_capacity(result["orbTier"])
            if result["currentEssence"] > max_capacity:
                self.warnings.append(
                    f"BM-W-NETWORK-OVERFLOW: Gracz '{owner_name}' ma {result['currentEssence']} LP, "
                    f"ale jego orb tier {result['orbTier']} pozwala na max {max_capacity} - "
                    f"nadmiar może zostać utracony"
                )
        
        return result, self.warnings
    
    def convert_all_networks(
        self, 
        networks_1710: Dict[str, Dict[str, Any]]
    ) -> Tuple[Dict[str, Dict[str, Any]], List[str]]:
        """
        Konwertuj wszystkie Soul Networks z 1.7.10 na 1.18.2
        
        Args:
            networks_1710: Słownik {nazwa_gracza: dane_network}
            
        Returns:
            Tuple (networks_1182, all_warnings)
            - networks_1182: Słownik {UUID: dane_network}
            - all_warnings: Lista wszystkich ostrzeżeń
        """
        all_warnings = []
        result = {}
        
        for owner_name, nbt_1710 in networks_1710.items():
            nbt_1182, warnings = self.convert_player_network(owner_name, nbt_1710)
            all_warnings.extend(warnings)
            
            # Użyj UUID jako klucza jeśli dostępny
            owner_uuid = self._resolve_uuid(owner_name)
            if owner_uuid:
                result[str(owner_uuid)] = nbt_1182
            else:
                # Fallback na nazwę jeśli brak UUID
                result[owner_name] = nbt_1182
        
        return result, all_warnings
    
    def _resolve_uuid(self, owner_name: str) -> Optional[UUID]:
        """
        Rozwiąż nazwę gracza na UUID
        
        Args:
            owner_name: Nazwa gracza z 1.7.10
            
        Returns:
            UUID gracza lub None
        """
        if owner_name in self._name_to_uuid:
            return self._name_to_uuid[owner_name]
        
        # Sprawdź czy nazwa to już UUID
        try:
            return UUID(owner_name)
        except ValueError:
            pass
        
        return None
    
    def _get_orb_capacity(self, tier: int) -> int:
        """
        Pobierz maksymalną pojemność dla danego tieru orba
        
        Source: SoulNetworkHandler.getMaximumForOrbTier()
        
        Args:
            tier: Tier orba (1-6)
            
        Returns:
            Maksymalna pojemność w LP
        """
        capacities = {
            0: 0,  # Brak orba
            1: 5000,  # Weak
            2: 25000,  # Apprentice
            3: 150000,  # Magician
            4: 1000000,  # Master
            5: 10000000,  # Archmage
            6: 30000000,  # Transcendent (tylko 1.7.10, w 1.18.2 traktowany jako Archmage)
        }
        return capacities.get(tier, 5000)


class BloodOrbConverter:
    """
    Konwerter Blood Orbs (item NBT) z 1.7.10 na 1.18.2
    
    Blood Orbs przechowują binding do gracza w swoim NBT.
    """
    
    # Mapowanie ID orbów
    ORB_ID_MAPPING = {
        "AWWayofTime:weakBloodOrb": "bloodmagic:weak_blood_orb",
        "AWWayofTime:apprenticeBloodOrb": "bloodmagic:apprentice_blood_orb",
        "AWWayofTime:magicianBloodOrb": "bloodmagic:magician_blood_orb",
        "AWWayofTime:masterBloodOrb": "bloodmagic:master_blood_orb",
        "AWWayofTime:archmageBloodOrb": "bloodmagic:archmage_blood_orb",
        "AWWayofTime:transcendentBloodOrb": "bloodmagic:archmage_blood_orb",  # Transcendent -> Archmage
    }
    
    def __init__(self, name_to_uuid_mapping: Optional[Dict[str, UUID]] = None):
        self.warnings = []
        self._name_to_uuid = name_to_uuid_mapping or {}
    
    def set_name_to_uuid_mapping(self, mapping: Dict[str, UUID]) -> None:
        """Ustaw mapowanie nazw graczy na UUID"""
        self._name_to_uuid = mapping
    
    def convert_orb_item(
        self, 
        item_nbt_1710: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], list]:
        """
        Konwertuj Blood Orb z 1.7.10 na 1.18.2
        
        Args:
            item_nbt_1710: NBT przedmiotu z 1.7.10
            
        Returns:
            Tuple (item_nbt_1182, warnings)
        """
        self.warnings = []
        result = {}
        
        # Mapowanie ID
        old_id = item_nbt_1710.get("id", "")
        new_id = self._map_orb_id(old_id)
        result["id"] = new_id
        result["Count"] = item_nbt_1710.get("Count", 1)
        
        # Konwersja bindingu
        old_tag = item_nbt_1710.get("tag", {})
        old_owner = old_tag.get("ownerName", "")
        
        if old_owner:
            # Orb jest zbindowany
            owner_uuid = self._resolve_uuid(old_owner)
            
            if owner_uuid:
                result["tag"] = {
                    "binding": {
                        "ownerUUID": str(owner_uuid),
                        "ownerName": old_owner,
                    }
                }
            else:
                # Nie znaleziono UUID - zachowujemy starą nazwę
                result["tag"] = {
                    "binding": {
                        "ownerName": old_owner,
                    }
                }
                self.warnings.append(
                    f"BM-W-ORB-NO-UUID: Nie znaleziono UUID dla właściciela '{old_owner}' - "
                    f"orb może wymagać ponownego zbindowania"
                )
        else:
            # Orb niezbindowany - przenosimy pozostałe tagi
            if old_tag:
                result["tag"] = old_tag.copy()
        
        return result, self.warnings
    
    def _map_orb_id(self, old_id: str) -> str:
        """Mapuj ID orba z 1.7.10 na 1.18.2"""
        if old_id in self.ORB_ID_MAPPING:
            return self.ORB_ID_MAPPING[old_id]
        
        # Fallback - zamiana namespace
        if old_id.startswith("AWWayofTime:"):
            return old_id.replace("AWWayofTime:", "bloodmagic:")
        
        return old_id
    
    def _resolve_uuid(self, owner_name: str) -> Optional[UUID]:
        """Rozwiąż nazwę gracza na UUID"""
        if owner_name in self._name_to_uuid:
            return self._name_to_uuid[owner_name]
        
        try:
            return UUID(owner_name)
        except ValueError:
            pass
        
        return None
