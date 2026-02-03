"""
Konwerter Blood Altar NBT - Blood Magic 1.7.10 -> 1.18.2

Source mapping 1.18.2: wayoftime/bloodmagic/altar/BloodAltar.java
- writeToNBT(CompoundTag tagCompound) - linie 139-181
- readFromNBT(CompoundTag tagCompound) - linie 87-137
- Constants.NBT - definicje kluczy

Struktura NBT w 1.18.2:
- Dane są zagnieżdżone w tagu "bloodAltar"
- Klucze wewnątrz (z Constants.NBT):
  - "upgradeLevel" (string) - tier ołtarza ("ONE", "TWO", ...)
  - "isActive" (boolean)
  - "liquidRequired" (int)
  - "fillable" (boolean)
  - "isUpgraded" (boolean)
  - "consumptionRate" (int)
  - "drainRate" (int)
  - "consumptionMultiplier" (float)
  - "efficiencyMultiplier" (float)
  - "selfSacrificeMultiplier" (float)
  - "sacrificeMultiplier" (float)
  - "capacityMultiplier" (float)
  - "orbCapacityMultiplier" (float)
  - "dislocationMultiplier" (float)
  - "capacity" (int)
  - "bufferCapacity" (int)
  - "progress" (int)
  - "isResultBlock" (boolean)
  - "lockdownDuration" (int)
  - "accelerationUpgrades" (int)
  - "demonBloodDuration" (int)
  - "cooldownAfterCrafting" (int)
  - "chargeRate" (int)
  - "chargeFrequency" (int)
  - "totalCharge" (int)
  - "maxCharge" (int)
  - "currentTierDisplayed" (string)
  - "Empty" (string) - specjalny znacznik gdy brak płynu
  - "outputAmount" (int) - ilość płynu wyjściowego
  - "inputAmount" (int) - ilość płynu wejściowego

Struktura NBT w 1.7.10 (z dokumentacji):
- "currentEssence" (int) - ilość LP
- "upgradeLevel" (int 1-5) - tier
- "isActive" (boolean)
- "progress" (int)
- "liquidRequired" (int)
- "canBeFilled" (boolean)
- "owner" (string) - opcjonalnie
"""

from typing import Dict, Any, Optional, Tuple
from uuid import UUID


class BloodAltarConverter:
    """
    Konwerter TileEntity Blood Altar z 1.7.10 na BlockEntity 1.18.2
    
    Source mapping:
    - 1.7.10: WayofTime/alchemicalWizardry/common/tileEntity/TEAltar.java
    - 1.18.2: wayoftime/bloodmagic/altar/BloodAltar.java
    """
    
    # Mapowanie tierów: int (1.7.10) -> string (1.18.2 AltarTier enum)
    # Source 1.18.2: wayoftime/bloodmagic/altar/AltarTier.java
    TIER_MAPPING = {
        1: "ONE",
        2: "TWO", 
        3: "THREE",
        4: "FOUR",
        5: "FIVE",
        6: "SIX",
    }
    
    def __init__(self):
        self.warnings = []
    
    def convert(
        self, 
        nbt_1710: Dict[str, Any],
        owner_uuid: Optional[UUID] = None
    ) -> Tuple[Dict[str, Any], list]:
        """
        Konwertuj NBT Blood Altar z 1.7.10 na 1.18.2
        
        Args:
            nbt_1710: NBT TileEntity z 1.7.10
            owner_uuid: UUID właściciela w 1.18.2 (opcjonalnie)
            
        Returns:
            Tuple (nbt_1182, warnings)
            - nbt_1182: Słownik z danymi BlockEntity dla 1.18.2
                       (z zagnieżdżonym tagiem "bloodAltar")
            - warnings: Lista ostrzeżeń z konwersji
        """
        self.warnings = []
        
        # Główny słownik - zgodny z TileAltar.serialize()
        result = {}
        
        # Dane ołtarza są zagnieżdżone w tagu "bloodAltar"
        altar_data = {}
        
        # Konwersja tieru: int -> string enum
        # "upgradeLevel" w obu wersjach, ale różne typy
        old_tier = nbt_1710.get("upgradeLevel", 1)
        new_tier = self._convert_tier(old_tier)
        altar_data["upgradeLevel"] = new_tier
        
        # Aktywność: "isActive" -> "isActive" (bez zmiany nazwy)
        altar_data["isActive"] = nbt_1710.get("isActive", False)
        
        # LP (currentEssence) w 1.18.2 jest przechowywane jako FluidStack
        # w głównym tagu (nie w bloodAltar), ale dla uproszczenia
        # przechowujemy też jako int
        current_essence = nbt_1710.get("currentEssence", 0)
        
        # Płyn jest zapisywany bezpośrednio w tagu głównym (FluidStack)
        # Zapisujemy ilość jako int dla kompatybilności
        if current_essence > 0:
            # Symulacja FluidStack - w prawdziwym NBT byłyby tu dane płynu
            result["Amount"] = current_essence
        else:
            # Pusty zbiornik
            altar_data["Empty"] = ""
        
        # Pozostałe pola - bez zmian nazw
        altar_data["liquidRequired"] = nbt_1710.get("liquidRequired", 0)
        altar_data["fillable"] = nbt_1710.get("canBeFilled", False)
        
        # Progress
        altar_data["progress"] = nbt_1710.get("progress", 0)
        
        # Multiplikatory z run (jeśli dostępne w NBT 1.7.10)
        altar_data["consumptionMultiplier"] = nbt_1710.get("consumptionMultiplier", 0.0)
        altar_data["efficiencyMultiplier"] = nbt_1710.get("efficiencyMultiplier", 1.0)
        altar_data["sacrificeMultiplier"] = nbt_1710.get("sacrificeEfficiencyMultiplier", 0.0)
        altar_data["selfSacrificeMultiplier"] = nbt_1710.get("selfSacrificeEfficiencyMultiplier", 0.0)
        altar_data["capacityMultiplier"] = nbt_1710.get("capacityMultiplier", 1.0)
        altar_data["orbCapacityMultiplier"] = nbt_1710.get("orbCapacityMultiplier", 1.0)
        altar_data["dislocationMultiplier"] = nbt_1710.get("dislocationMultiplier", 1.0)
        
        # Dodatkowe pola obliczane z tieru (domyślne wartości)
        altar_data["isUpgraded"] = old_tier > 1
        altar_data["consumptionRate"] = nbt_1710.get("consumptionRate", 5)
        altar_data["drainRate"] = nbt_1710.get("drainRate", 5)
        altar_data["capacity"] = nbt_1710.get("capacity", 10000)
        altar_data["bufferCapacity"] = nbt_1710.get("bufferCapacity", 1000)
        altar_data["isResultBlock"] = False
        altar_data["lockdownDuration"] = 0
        altar_data["accelerationUpgrades"] = nbt_1710.get("accelerationUpgrades", 0)
        altar_data["demonBloodDuration"] = 0
        
        # Nowe pola w 1.18.2 (mechanika charging)
        altar_data["cooldownAfterCrafting"] = nbt_1710.get("cooldownAfterCrafting", 60)
        altar_data["chargeRate"] = 0
        altar_data["chargeFrequency"] = 20
        altar_data["totalCharge"] = 0
        altar_data["maxCharge"] = 0
        
        # currentTierDisplayed - domyślnie ONE
        altar_data["currentTierDisplayed"] = "ONE"
        
        # outputAmount i inputAmount dla buforów
        altar_data["outputAmount"] = 0
        altar_data["inputAmount"] = 0
        
        # Dodaj zagnieżdżone dane ołtarza
        result["bloodAltar"] = altar_data
        
        # Sprawdź czy ołtarz jest w trakcie craftingu
        if altar_data["isActive"] and altar_data["progress"] > 0:
            self.warnings.append(
                f"BM-W-ALTAR-ACTIVE: Ołtarz jest w trakcie craftingu "
                f"(progress: {altar_data['progress']}/{altar_data['liquidRequired']})"
            )
        
        return result, self.warnings
    
    def _convert_tier(self, tier: int) -> str:
        """
        Konwertuj tier z formatu int (1.7.10) na string enum (1.18.2)
        
        Args:
            tier: Tier ołtarza jako int (1-5, lub 6 dla transcendent)
            
        Returns:
            String enum (ONE, TWO, THREE, FOUR, FIVE, SIX)
        """
        if tier in self.TIER_MAPPING:
            return self.TIER_MAPPING[tier]
        
        # Nieznany tier - domyślnie ONE
        self.warnings.append(
            f"BM-W-ALTAR-TIER-UNKNOWN: Nieznany tier ołtarza: {tier}, "
            f"użyto 'ONE'"
        )
        return "ONE"
    
    def get_conversion_report(self, nbt_1710: Dict[str, Any], nbt_1182: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generuj raport konwersji dla Blood Altar
        
        Returns:
            Słownik z informacjami o konwersji
        """
        altar_data = nbt_1182.get("bloodAltar", {})
        return {
            "blockType": "Blood Altar",
            "sourceVersion": "1.7.10",
            "targetVersion": "1.18.2",
            "preservedData": {
                "currentEssence": nbt_1710.get("currentEssence", 0),
                "tier": {
                    "old": nbt_1710.get("upgradeLevel", 1),
                    "new": altar_data.get("upgradeLevel", "ONE"),
                },
                "isActive": altar_data.get("isActive", False),
                "progress": altar_data.get("progress", 0),
            },
            "newFields": [
                "chargeRate", "chargeFrequency", "totalCharge", 
                "maxCharge", "cooldownAfterCrafting", "currentTierDisplayed"
            ],
            "warnings": self.warnings,
        }
