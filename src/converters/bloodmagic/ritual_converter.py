"""
Konwerter Master Ritual Stone NBT - Blood Magic 1.7.10 -> 1.18.2

Source mapping 1.18.2: wayoftime/bloodmagic/common/tile/TileMasterRitualStone.java
- serialize(CompoundTag tag) - linie 130-159
- deserialize(CompoundTag tag) - linie 94-127
- Constants.NBT - definicje kluczy

Klucze NBT w 1.18.2:
- "owner" (UUID) - właściciel rytuału
- "currentRitual" (string) - ID rytuału (np. "bloodmagic:water")
- "isRunning" (boolean) - czy rytuał jest aktywny
- "runtime" (int) - czas działania rytuału
- "direction" (int) - kierunek (0-5 dla Direction enum)
- "isStoned" (boolean) - czy zablokowany przez redstone
- "currentRitualTag" (compound) - dodatkowe dane rytuału

Klucze NBT w 1.7.10 (z dokumentacji i analizy):
- "ritualType" (string) - typ rytuału
- "owner" (string) - nazwa właściciela
- "isActive" (boolean) - aktywność
- "cooldown" (int) - cooldown
- "runningTime" (int) - czas działania
"""

from typing import Dict, Any, Optional, Tuple
from enum import Enum
from uuid import UUID


class RitualType(Enum):
    """Mapowanie typów rytuałów 1.7.10 -> 1.18.2"""
    # Podstawowe rytuały
    WATER = ("water", "bloodmagic:water")
    LAVA = ("lava", "bloodmagic:lava")
    GREEN_GROVE = ("greenGrove", "bloodmagic:growth")
    HIGH_JUMP = ("highJump", "bloodmagic:jumping")
    SPEED = ("speed", "bloodmagic:speed")
    
    # Zaawansowane rytuały
    WELL_OF_SUFFERING = ("suffering", "bloodmagic:well_of_suffering")
    REGENERATION = ("regeneration", "bloodmagic:regeneration")
    FEATHERED_KNIFE = ("featheredKnife", "bloodmagic:feathered_knife")
    MAGNETISM = ("magnetism", "bloodmagic:magnetism")
    CRUSHER = ("crushing", "bloodmagic:crushing")
    FULL_STOMACH = ("fullStomach", "bloodmagic:satiated_stomach")
    INTERDICTION = ("interdiction", "bloodmagic:interdiction")
    
    # Inne
    ZEPHYR = ("zephyr", "bloodmagic:zephyr")
    HARVEST = ("harvest", "bloodmagic:harvest")
    MAGNETISM_SUPPRESSED = ("magnetismSuppressed", "bloodmagic:magnetism_deactivated")
    
    def __init__(self, id_1710: str, id_1182: str):
        self.id_1710 = id_1710
        self.id_1182 = id_1182


class MasterRitualStoneConverter:
    """
    Konwerter TileEntity Master Ritual Stone z 1.7.10 na BlockEntity 1.18.2
    
    Source mapping:
    - 1.7.10: WayofTime/alchemicalWizardry/common/tileEntity/TEMasterStone.java
    - 1.18.2: wayoftime/bloodmagic/common/tile/TileMasterRitualStone.java
    """
    
    # Słownik szybkiego wyszukiwania
    _ritual_map: Dict[str, str] = {}
    
    def __init__(self):
        self.warnings = []
        # Inicjalizuj mapowanie rytuałów
        if not self._ritual_map:
            for ritual in RitualType:
                self._ritual_map[ritual.id_1710] = ritual.id_1182
    
    def convert(
        self, 
        nbt_1710: Dict[str, Any],
        owner_uuid: Optional[UUID] = None
    ) -> Tuple[Dict[str, Any], list]:
        """
        Konwertuj NBT Master Ritual Stone z 1.7.10 na 1.18.2
        
        Args:
            nbt_1710: NBT TileEntity z 1.7.10
            owner_uuid: UUID właściciela w 1.18.2 (opcjonalnie)
            
        Returns:
            Tuple (nbt_1182, warnings)
        """
        self.warnings = []
        result = {}
        
        # Mapowanie typu rytuału: "ritualType" -> "currentRitual"
        old_ritual_type = nbt_1710.get("ritualType", "")
        new_ritual_id = self._map_ritual_id(old_ritual_type)
        result["currentRitual"] = new_ritual_id
        
        # Właściciel: "owner" (nazwa w 1.7.10) -> "owner" (UUID w 1.18.2)
        old_owner = nbt_1710.get("owner", "")
        if owner_uuid:
            result["owner"] = str(owner_uuid)
        elif old_owner:
            # Spróbuj sparsować jako UUID
            try:
                parsed_uuid = UUID(old_owner)
                result["owner"] = old_owner
            except ValueError:
                # To nazwa gracza, nie UUID - wymaga mapowania
                result["owner"] = old_owner  # Zachowaj nazwę jako fallback
                self.warnings.append(
                    f"BM-W-RITUAL-OWNER-NAME: Rytuał ma właściciela '{old_owner}' (nazwa, nie UUID) - "
                    f"wymaga konwersji nazwy na UUID"
                )
        
        # Aktywność: "isActive" -> "isRunning"
        result["isRunning"] = nbt_1710.get("isActive", False)
        
        # Czas działania: "runningTime" -> "runtime"
        result["runtime"] = nbt_1710.get("runningTime", 0)
        
        # Cooldown nie jest zapisywany w NBT 1.18.2 (runtime only)
        # direction - nie było w 1.7.10, ustawiamy domyślnie (NORTH = 2)
        result["direction"] = 2  # Direction.NORTH
        
        # isStoned - nie było w 1.7.10
        result["isStoned"] = False
        
        # currentRitualTag - pusty compound dla kompatybilności
        result["currentRitualTag"] = {}
        
        # Ostrzeżenie o aktywnym rytuale
        if result["isRunning"]:
            self.warnings.append(
                f"BM-W-RITUAL-ACTIVE: Rytuał '{old_ritual_type}' jest aktywny (runtime: {result['runtime']}) - "
                f"może wymagać ponownej aktywacji w 1.18.2"
            )
        
        return result, self.warnings
    
    def _map_ritual_id(self, ritual_type_1710: str) -> str:
        """
        Mapuj ID rytuału z 1.7.10 na ResourceLocation 1.18.2
        
        Args:
            ritual_type_1710: Typ rytuału w 1.7.10 (np. "water", "suffering")
            
        Returns:
            ResourceLocation w 1.18.2 (np. "bloodmagic:water")
        """
        if ritual_type_1710 in self._ritual_map:
            return self._ritual_map[ritual_type_1710]
        
        # Nieznany rytuał - próbujemy dodać przedrostek
        if ":" not in ritual_type_1710:
            self.warnings.append(
                f"BM-W-RITUAL-UNKNOWN: Nieznany typ rytuału: '{ritual_type_1710}', "
                f"użyto 'bloodmagic:{ritual_type_1710}'"
            )
            return f"bloodmagic:{ritual_type_1710}"
        
        return ritual_type_1710
    
    def get_conversion_report(
        self, 
        nbt_1710: Dict[str, Any], 
        nbt_1182: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generuj raport konwersji dla Master Ritual Stone
        
        Returns:
            Słownik z informacjami o konwersji
        """
        return {
            "blockType": "Master Ritual Stone",
            "sourceVersion": "1.7.10",
            "targetVersion": "1.18.2",
            "preservedData": {
                "ritualType": {
                    "old": nbt_1710.get("ritualType", ""),
                    "new": nbt_1182.get("currentRitual", ""),
                },
                "owner": nbt_1182.get("owner", ""),
                "isRunning": nbt_1182.get("isRunning", False),
                "runtime": nbt_1182.get("runtime", 0),
            },
            "newFields": ["direction", "isStoned"],
            "removedFields": ["cooldown"],  # cooldown nie jest zapisywany
            "warnings": self.warnings,
        }
