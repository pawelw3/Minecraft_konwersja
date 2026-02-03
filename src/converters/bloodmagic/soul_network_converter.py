"""
Konwerter Soul Network i Blood Orbs - Blood Magic 1.7.10 -> 1.18.2

Source mapping Soul Network 1.18.2: wayoftime/bloodmagic/core/data/SoulNetwork.java
- serializeNBT() - linie 263-270
- deserializeNBT() - linie 272-278
- Klucze: "playerId" (string UUID), "currentEssence" (int), "orbTier" (int)

Source mapping Binding 1.18.2: wayoftime/bloodmagic/core/data/Binding.java
- serializeNBT() - linie 30-37
- deserializeNBT() - linie 40-44
- Klucze: "id" (UUID tag), "name" (string)
- W ItemStack tag: "binding" (compound)

WAŻNE: Soul Network w 1.18.2 jest przechowywane w BMWorldSavedData (per świat),
nie w NBT gracza. Konwerter zwraca format pośredni.
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
    max_orb_tier: int  # maxOrb z 1.7.10 -> orbTier w 1.18.2
    warnings: List[str]


class SoulNetworkConverter:
    """
    Konwerter Soul Network z 1.7.10 na 1.18.2
    
    Soul Network to globalny zbiornik LP dla każdego gracza.
    W 1.18.2 dane są przechowywane w BMWorldSavedData.
    
    Source mapping:
    - 1.7.10: WayofTime/alchemicalWizardry/api/soulNetwork/LifeEssenceNetwork.java
    - 1.18.2: wayoftime/bloodmagic/core/data/SoulNetwork.java
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
            
        Note:
            Format wyjściowy to format pośredni. Właściwy zapis w 1.18.2
            wymaga umieszczenia danych w BMWorldSavedData.
        """
        self.warnings = []
        result = {}
        
        # Kluczowe pola
        result["currentEssence"] = nbt_1710.get("currentEssence", 0)
        result["orbTier"] = nbt_1710.get("maxOrb", 0)
        
        # Konwersja nazwy na UUID
        owner_uuid = self._resolve_uuid(owner_name)
        
        if owner_uuid:
            result["playerId"] = str(owner_uuid)
        else:
            # Nie znaleziono UUID
            result["playerId"] = owner_name  # Fallback
            self.warnings.append(
                f"BM-W-NETWORK-NO-UUID: Nie znaleziono UUID dla gracza '{owner_name}' - "
                f"Soul Network wymaga ręcznej konwersji"
            )
        
        # Sprawdź czy gracz ma LP w sieci
        if result["currentEssence"] > 0:
            max_capacity = self._get_orb_capacity(result["orbTier"])
            if result["currentEssence"] > max_capacity:
                self.warnings.append(
                    f"BM-W-NETWORK-OVERFLOW: Gracz '{owner_name}' ma {result['currentEssence']} LP, "
                    f"ale orb tier {result['orbTier']} pozwala na max {max_capacity}"
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
                # Fallback na nazwę
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
        
        Source: SoulNetworkHandler.getMaximumForOrbTier() (1.7.10)
        
        Args:
            tier: Tier orba (1-6)
            
        Returns:
            Maksymalna pojemność w LP
        """
        capacities = {
            0: 0,
            1: 5000,
            2: 25000,
            3: 150000,
            4: 1000000,
            5: 10000000,
            6: 30000000,
        }
        return capacities.get(tier, 5000)


class BloodOrbConverter:
    """
    Konwerter Blood Orbs (item NBT) z 1.7.10 na 1.18.2
    
    Source 1.18.2: wayoftime/bloodmagic/core/data/Binding.java
    - Klucze NBT: "id" (UUID), "name" (string)
    - W ItemStack tag: "binding" (compound)
    
    Source 1.7.10: IBloodOrb interfejs i implementacje
    - Klucz NBT: "ownerName" (string)
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
            # Orb jest zbindowany - konwertuj do formatu 1.18.2
            owner_uuid = self._resolve_uuid(old_owner)
            
            if owner_uuid:
                # Format 1.18.2: "binding" -> {"id": UUID, "name": string}
                result["tag"] = {
                    "binding": {
                        "id": str(owner_uuid),  # UUID jako string
                        "name": old_owner,
                    }
                }
            else:
                # Nie znaleziono UUID - zapisz tylko nazwę
                result["tag"] = {
                    "binding": {
                        "name": old_owner,
                    }
                }
                self.warnings.append(
                    f"BM-W-ORB-NO-UUID: Nie znaleziono UUID dla właściciela '{old_owner}'"
                )
        
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
