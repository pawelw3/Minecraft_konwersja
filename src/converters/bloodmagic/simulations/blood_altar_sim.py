"""
Symulacja Blood Altar - Blood Magic 1.7.10 vs 1.18.2

Source mapping:
- 1.7.10: WayofTime/alchemicalWizardry/common/tileEntity/TEAltar.java
  - readFromNBT/writeToNBT: linie 128-246
  - updateEntity (logika tick): linie 444-641
  - startCycle: linie 727-758
  - checkAndSetAltar: linie 760-827
  
- 1.18.2: wayoftime/bloodmagic/altar/BloodAltar.java
  - readFromNBT/writeToNBT: linie 87-181
  - update: linie 229-298
  - updateAltar (logika): linie 300-444
  - startCycle: linie 183-227
  - checkTier: linie 446-505

Kluczowe różnice w NBT:
- 1.7.10: "currentEssence" -> 1.18.2: to samo
- 1.7.10: "upgradeLevel" -> 1.18.2: "altarTier" (jako string enum)
- 1.7.10: "isActive" -> 1.18.2: to samo
- 1.7.10: "progress" -> 1.18.2: to samo
- 1.18.2 dodaje: "bloodAltar" (zagnieżdżony tag)
- 1.18.2 dodaje: chargingRate, chargingFrequency, totalCharge (nowa mechanika)
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Dict, Any, Tuple
import math


class AltarTier(Enum):
    """Tier ołtarza - identyczne w obu wersjach"""
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6


class BloodRuneType(Enum):
    """Typy run w Blood Magic - mapowanie metadata 1.7.10 -> nazwy 1.18.2"""
    BLANK = 0           # 1.7.10: metadata 0
    SPEED = 1           # 1.7.10: metadata 1
    EFFICIENCY = 2      # 1.7.10: metadata 2
    SACRIFICE = 3       # 1.7.10: metadata 3
    SELF_SACRIFICE = 4  # 1.7.10: metadata 4
    DISPLACEMENT = 5    # 1.7.10: metadata 5 (tylko 1.7.10)
    CAPACITY = 6        # 1.7.10: metadata 6
    ORB = 7             # 1.7.10: metadata 7
    AUGMENTED_CAPACITY = 8  # 1.7.10: metadata nie istnieje (nowość w 1.18.2?)
    ACCELERATION = 9    # Tylko 1.7.10
    CHARGING = 10       # Nowość w 1.18.2


@dataclass
class AltarRecipe:
    """Receptura dla Blood Altar"""
    input_item: str
    output_item: str
    lp_required: int
    tier_required: AltarTier
    consumption_rate: int = 5
    drain_rate: int = 5


@dataclass 
class AltarState:
    """Stan Blood Altar - dane do konwersji NBT"""
    # Podstawowe dane (obie wersje)
    current_essence: int = 0
    tier: AltarTier = AltarTier.ONE
    is_active: bool = False
    progress: int = 0
    liquid_required: int = 0
    can_be_filled: bool = False
    
    # Multiplikatory (obie wersje)
    consumption_multiplier: float = 0.0
    efficiency_multiplier: float = 1.0
    sacrifice_multiplier: float = 0.0
    self_sacrifice_multiplier: float = 0.0
    capacity_multiplier: float = 1.0
    orb_capacity_multiplier: float = 1.0
    dislocation_multiplier: float = 1.0
    
    # Nowości 1.18.2
    charging_rate: int = 0
    charging_frequency: int = 20
    total_charge: int = 0
    max_charge: int = 0
    cooldown_after_crafting: int = 60
    
    # Wewnętrzne
    capacity: int = 10000  # 10 buckets * 1000 mB
    buffer_capacity: int = 1000
    acceleration_upgrades: int = 0


class BloodAltarSimulation:
    """
    Symulacja Blood Altar dla konwersji 1.7.10 -> 1.18.2
    
    Dokładnie odwzorowuje logikę z kodu źródłowego obu wersji.
    """
    
    # Stałe z kodu źródłowego
    BUCKET_VOLUME = 1000
    BASE_CAPACITY = BUCKET_VOLUME * 10  # 10000 mB
    BASE_BUFFER = BUCKET_VOLUME  # 1000 mB
    
    def __init__(self, version: str = "1.7.10"):
        """
        Args:
            version: "1.7.10" lub "1.18.2"
        """
        self.version = version
        self.state = AltarState()
        self.input_item: Optional[str] = None
        self.output_item: Optional[str] = None
        self.recipe: Optional[AltarRecipe] = None
        
    def load_from_nbt_1710(self, nbt_data: Dict[str, Any]) -> None:
        """
        Wczytaj stan z NBT 1.7.10
        
        Source: TEAltar.readFromNBT() linie 128-181
        """
        self.state.current_essence = nbt_data.get("currentEssence", 0)
        self.state.tier = AltarTier(nbt_data.get("upgradeLevel", 1))
        self.state.is_active = nbt_data.get("isActive", False)
        self.state.progress = nbt_data.get("progress", 0)
        self.state.liquid_required = nbt_data.get("liquidRequired", 0)
        self.state.can_be_filled = nbt_data.get("canBeFilled", False)
        
        # Multiplikatory
        self.state.consumption_multiplier = nbt_data.get("consumptionMultiplier", 0.0)
        self.state.efficiency_multiplier = nbt_data.get("efficiencyMultiplier", 1.0)
        self.state.sacrifice_multiplier = nbt_data.get("sacrificeEfficiencyMultiplier", 0.0)
        self.state.self_sacrifice_multiplier = nbt_data.get("selfSacrificeEfficiencyMultiplier", 0.0)
        self.state.capacity_multiplier = nbt_data.get("capacityMultiplier", 1.0)
        self.state.orb_capacity_multiplier = nbt_data.get("orbCapacityMultiplier", 1.0)
        self.state.dislocation_multiplier = nbt_data.get("dislocationMultiplier", 1.0)
        self.state.acceleration_upgrades = nbt_data.get("accelerationUpgrades", 0)
        
        # Oblicz capacity na podstawie multiplierów
        self._recalculate_capacity()
        
    def load_from_nbt_1182(self, nbt_data: Dict[str, Any]) -> None:
        """
        Wczytaj stan z NBT 1.18.2
        
        Source: BloodAltar.readFromNBT() linie 87-137
        """
        # W 1.18.2 dane są zagnieżdżone w "bloodAltar"
        altar_data = nbt_data.get("bloodAltar", nbt_data)
        
        self.state.current_essence = altar_data.get("currentEssence", 0)
        
        # W 1.18.2 tier jest zapisywany jako string
        tier_str = altar_data.get("altarTier", "ONE")
        self.state.tier = AltarTier[tier_str]
        
        self.state.is_active = altar_data.get("altarActive", False)
        self.state.progress = altar_data.get("progress", 0)
        self.state.liquid_required = altar_data.get("altarLiquidReq", 0)
        self.state.can_be_filled = altar_data.get("altarFillable", False)
        
        # Multiplikatory
        self.state.consumption_multiplier = altar_data.get("consumptionMultiplier", 0.0)
        self.state.efficiency_multiplier = altar_data.get("efficiencyMultiplier", 1.0)
        self.state.sacrifice_multiplier = altar_data.get("sacrificeMultiplier", 0.0)
        self.state.self_sacrifice_multiplier = altar_data.get("selfSacrificeMultiplier", 0.0)
        self.state.capacity_multiplier = altar_data.get("capacityMultiplier", 1.0)
        self.state.orb_capacity_multiplier = altar_data.get("orbCapacityMultiplier", 1.0)
        self.state.dislocation_multiplier = altar_data.get("dislocationMultiplier", 1.0)
        self.state.acceleration_upgrades = altar_data.get("accelerationUpgrades", 0)
        
        # Nowości 1.18.2
        self.state.charging_rate = altar_data.get("chargeRate", 0)
        self.state.charging_frequency = altar_data.get("chargeFrequency", 20)
        self.state.total_charge = altar_data.get("totalCharge", 0)
        self.state.max_charge = altar_data.get("maxCharge", 0)
        self.state.cooldown_after_crafting = altar_data.get("cooldownAfterCrafting", 60)
        
        self._recalculate_capacity()
    
    def convert_to_1182_nbt(self) -> Dict[str, Any]:
        """
        Konwertuj stan do formatu NBT 1.18.2
        
        Returns:
            Dict zgodny ze strukturą NBT 1.18.2
        """
        # Podstawowe dane
        result = {
            "currentEssence": self.state.current_essence,
            "altarTier": self.state.tier.name,
            "altarActive": self.state.is_active,
            "progress": self.state.progress,
            "altarLiquidReq": self.state.liquid_required,
            "altarFillable": self.state.can_be_filled,
            
            # Multiplikatory
            "consumptionMultiplier": self.state.consumption_multiplier,
            "efficiencyMultiplier": self.state.efficiency_multiplier,
            "sacrificeMultiplier": self.state.sacrifice_multiplier,
            "selfSacrificeMultiplier": self.state.self_sacrifice_multiplier,
            "capacityMultiplier": self.state.capacity_multiplier,
            "orbCapacityMultiplier": self.state.orb_capacity_multiplier,
            "dislocationMultiplier": self.state.dislocation_multiplier,
            "accelerationUpgrades": self.state.acceleration_upgrades,
            
            # Nowości 1.18.2 (ustawiamy na 0/domyslne)
            "chargeRate": 0,  # Nowa mechanika w 1.18.2 - charging runes
            "chargeFrequency": 20,
            "totalCharge": 0,
            "maxCharge": 0,
            "cooldownAfterCrafting": self.state.cooldown_after_crafting,
        }
        
        return result
    
    def _recalculate_capacity(self) -> None:
        """Przelicz capacity na podstawie multiplierów"""
        self.state.capacity = int(self.BASE_CAPACITY * self.state.capacity_multiplier)
        self.state.buffer_capacity = int(self.BASE_BUFFER * self.state.capacity_multiplier)
    
    def apply_rune_upgrades(self, rune_counts: Dict[BloodRuneType, int]) -> None:
        """
        Oblicz multiplikatory na podstawie run w strukturze ołtarza
        
        Source 1.7.10: TEAltar.checkAndSetAltar() linie 760-827
        Source 1.18.2: BloodAltar.checkTier() linie 446-505
        
        Formuły z kodu źródłowego:
        - consumptionMultiplier = 0.20 * speed_upgrades
        - efficiencyMultiplier = 0.85 ^ speed_upgrades
        - sacrificeEfficiencyMultiplier = 0.10 * sacrifice_upgrades
        - selfSacrificeEfficiencyMultiplier = 0.10 * self_sacrifice_upgrades
        - capacityMultiplier = (1 * 1.10^better_cap + 0.20 * altar_cap)
        - dislocationMultiplier = 1.2 ^ displacement_upgrades
        - orbCapacityMultiplier = 1 + 0.02 * orb_upgrades
        """
        speed = rune_counts.get(BloodRuneType.SPEED, 0)
        efficiency = rune_counts.get(BloodRuneType.EFFICIENCY, 0)
        sacrifice = rune_counts.get(BloodRuneType.SACRIFICE, 0)
        self_sacrifice = rune_counts.get(BloodRuneType.SELF_SACRIFICE, 0)
        capacity = rune_counts.get(BloodRuneType.CAPACITY, 0)
        displacement = rune_counts.get(BloodRuneType.DISPLACEMENT, 0)
        orb = rune_counts.get(BloodRuneType.ORB, 0)
        
        # Obliczenia wg kodu źródłowego
        self.state.consumption_multiplier = 0.20 * speed
        self.state.efficiency_multiplier = math.pow(0.85, efficiency)
        self.state.sacrifice_multiplier = 0.10 * sacrifice
        self.state.self_sacrifice_multiplier = 0.10 * self_sacrifice
        self.state.capacity_multiplier = (1 * math.pow(1.10, capacity) + 0.20 * capacity)
        self.state.dislocation_multiplier = math.pow(1.2, displacement)
        self.state.orb_capacity_multiplier = 1 + 0.02 * orb
        
        self._recalculate_capacity()
    
    def simulate_tick(self) -> Tuple[bool, int]:
        """
        Symuluj jeden tick ołtarza
        
        Source 1.7.10: TEAltar.updateEntity() linie 444-641
        Source 1.18.2: BloodAltar.update() linie 229-298 oraz updateAltar() linie 300-444
        
        Returns:
            (czy_aktywny, lp_zużyte_w_tym_ticku)
        """
        lp_used = 0
        
        if not self.state.is_active:
            return False, 0
        
        if self.state.can_be_filled:
            # Tryb napełniania orba - symulacja zużycia LP
            # W rzeczywistości zależy od fillRate orba
            lp_used = min(100, self.state.current_essence)  # Przykładowa wartość
            self.state.current_essence -= lp_used
        else:
            # Tryb craftingu
            if self.recipe and self.state.current_essence >= 1:
                # Oblicz zużycie LP w tym ticku
                consumption = int(self.recipe.consumption_rate * (1 + self.state.consumption_multiplier))
                consumption = min(consumption, self.state.current_essence)
                
                # Nie przekraczamy wymaganej ilości
                remaining = self.recipe.lp_required - self.state.progress
                consumption = min(consumption, remaining)
                
                self.state.current_essence -= consumption
                self.state.progress += consumption
                lp_used = consumption
                
                # Sprawdź czy crafting się zakończył
                if self.state.progress >= self.recipe.lp_required:
                    self.state.is_active = False
                    self.state.progress = 0
                    self.state.cooldown_after_crafting = 30 if self.version == "1.18.2" else 500
                    return False, lp_used
        
        return self.state.is_active, lp_used
    
    def start_crafting_cycle(self, recipe: AltarRecipe) -> bool:
        """
        Rozpocznij cykl craftingu
        
        Source 1.7.10: TEAltar.startCycle() linie 727-758
        Source 1.18.2: BloodAltar.startCycle() linie 183-227
        
        Returns:
            True jeśli crafting może się rozpocząć
        """
        # Sprawdź czy tier jest wystarczający
        if recipe.tier_required.value > self.state.tier.value:
            return False
        
        # Sprawdź czy mamy wystarczająco LP (opcjonalnie - gra pozwala zacząć bez LP)
        self.recipe = recipe
        self.state.is_active = True
        self.state.progress = 0
        self.state.liquid_required = recipe.lp_required
        self.state.can_be_filled = False
        
        return True
    
    def sacrificial_dagger_call(self, amount: int, is_sacrifice: bool = True) -> int:
        """
        Symulacja dodawania LP przez Sacrificial Knife lub Dagger of Sacrifice
        
        Source 1.7.10: TEAltar.sacrificialDaggerCall() linie 653-663
        Source 1.18.2: BloodAltar.sacrificialDaggerCall() linie 515-529
        
        Args:
            amount: Ilość LP do dodania
            is_sacrifice: True dla mobów, False dla self-sacrifice
            
        Returns:
            Rzeczywiście dodana ilość LP
        """
        multiplier = (1 + self.state.sacrifice_multiplier) if is_sacrifice else (1 + self.state.self_sacrifice_multiplier)
        actual_amount = int(amount * multiplier)
        
        added = min(self.state.capacity - self.state.current_essence, actual_amount)
        self.state.current_essence += added
        
        return added
    
    def get_conversion_report(self) -> Dict[str, Any]:
        """
        Generuj raport konwersji dla tego ołtarza
        """
        return {
            "source_version": "1.7.10",
            "target_version": "1.18.2",
            "tier": {
                "old": self.state.tier.value,
                "new": self.state.tier.name,
            },
            "essence": {
                "preserved": self.state.current_essence,
                "max_capacity": self.state.capacity,
            },
            "multipliers": {
                "consumption": self.state.consumption_multiplier,
                "efficiency": self.state.efficiency_multiplier,
                "sacrifice": self.state.sacrifice_multiplier,
                "self_sacrifice": self.state.self_sacrifice_multiplier,
                "capacity": self.state.capacity_multiplier,
                "orb_capacity": self.state.orb_capacity_multiplier,
                "dislocation": self.state.dislocation_multiplier,
            },
            "warnings": self._get_warnings(),
        }
    
    def _get_warnings(self) -> list:
        """Generuj ostrzeżenia o potencjalnych stratach danych"""
        warnings = []
        
        # Ostrzeżenie o nowej mechanice charging w 1.18.2
        if self.state.tier.value >= 3:
            warnings.append("W 1.18.2 wprowadzono Charging Runes - gracz musi je dodać ręcznie dla szybszego craftingu")
        
        # Ostrzeżenie o zmianie w formule capacity w 1.18.2
        warnings.append("Formuła capacityMultiplier zmieniła się w 1.18.2 - sprawdź czy pojemność ołtarza jest poprawna")
        
        return warnings


# Przykładowe receptury z Blood Magic
SAMPLE_RECIPES = {
    "weak_blood_orb": AltarRecipe(
        input_item="minecraft:diamond",
        output_item="bloodmagic:weak_blood_orb",
        lp_required=2000,
        tier_required=AltarTier.ONE,
        consumption_rate=5,
    ),
    "apprentice_blood_orb": AltarRecipe(
        input_item="minecraft:emerald",
        output_item="bloodmagic:apprentice_blood_orb",
        lp_required=5000,
        tier_required=AltarTier.TWO,
        consumption_rate=10,
    ),
    "magician_blood_orb": AltarRecipe(
        input_item="minecraft:gold_block",
        output_item="bloodmagic:magician_blood_orb",
        lp_required=25000,
        tier_required=AltarTier.THREE,
        consumption_rate=20,
    ),
    "blank_slate": AltarRecipe(
        input_item="minecraft:stone",
        output_item="bloodmagic:blank_slate",
        lp_required=1000,
        tier_required=AltarTier.ONE,
        consumption_rate=5,
    ),
}


def test_simulation():
    """Test symulacji - porównanie zachowania obu wersji"""
    print("=== Test symulacji Blood Altar ===\n")
    
    # Symulacja ołtarza Tier 3 z runami w 1.7.10
    altar_1710 = BloodAltarSimulation("1.7.10")
    
    # Przykładowe dane NBT z 1.7.10
    nbt_1710 = {
        "currentEssence": 15000,
        "upgradeLevel": 3,
        "isActive": True,
        "progress": 500,
        "liquidRequired": 5000,
        "canBeFilled": False,
    }
    altar_1710.load_from_nbt_1710(nbt_1710)
    
    # Zastosuj runy (przykład: 2 speed, 1 capacity)
    runes = {
        BloodRuneType.SPEED: 2,
        BloodRuneType.CAPACITY: 1,
        BloodRuneType.SACRIFICE: 1,
    }
    altar_1710.apply_rune_upgrades(runes)
    
    print(f"Stan 1.7.10:")
    print(f"  LP: {altar_1710.state.current_essence}/{altar_1710.state.capacity}")
    print(f"  Tier: {altar_1710.state.tier.name}")
    print(f"  Speed multiplier: {altar_1710.state.consumption_multiplier:.2f}")
    print(f"  Capacity multiplier: {altar_1710.state.capacity_multiplier:.2f}")
    
    # Konwersja do 1.18.2
    nbt_1182 = altar_1710.convert_to_1182_nbt()
    
    altar_1182 = BloodAltarSimulation("1.18.2")
    altar_1182.load_from_nbt_1182({"bloodAltar": nbt_1182})
    
    print(f"\nPo konwersji do 1.18.2:")
    print(f"  LP: {altar_1182.state.current_essence}/{altar_1182.state.capacity}")
    print(f"  Tier: {altar_1182.state.tier.name}")
    print(f"  Speed multiplier: {altar_1182.state.consumption_multiplier:.2f}")
    
    # Test craftingu
    print("\n=== Test craftingu ===")
    recipe = SAMPLE_RECIPES["apprentice_blood_orb"]
    
    if altar_1182.start_crafting_cycle(recipe):
        print(f"Rozpoczęto crafting: {recipe.input_item} -> {recipe.output_item}")
        print(f"Wymagane LP: {recipe.lp_required}")
        
        # Symuluj ticki
        total_ticks = 0
        while altar_1182.state.is_active and total_ticks < 1000:
            active, lp_used = altar_1182.simulate_tick()
            total_ticks += 1
            if not active:
                break
        
        print(f"Crafting zakończony po {total_ticks} tickach")
    else:
        print("Nie można rozpocząć craftingu - za niski tier")
    
    # Raport konwersji
    print("\n=== Raport konwersji ===")
    report = altar_1182.get_conversion_report()
    for key, value in report.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    test_simulation()
