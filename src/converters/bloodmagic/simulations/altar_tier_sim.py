"""
Symulacja obliczania tierów ołtarza - Blood Magic 1.7.10 vs 1.18.2

Source mapping:
- 1.7.10: WayofTime/alchemicalWizardry/common/bloodAltarUpgrade/UpgradedAltars.java
  - isAltarValid: linie 30-41
  - checkAltarIsValid: linie 43-192
  - getUpgrades: linie 194-262
  - loadAltars: linie 264-361 (definicje struktur)
  
- 1.7.10: WayofTime/alchemicalWizardry/common/bloodAltarUpgrade/AltarComponent.java
  - Definicja komponentów
  
- 1.7.10: WayofTime/alchemicalWizardry/common/bloodAltarUpgrade/AltarUpgradeComponent.java
  - Zliczanie typów run
  
- 1.18.2: wayoftime/bloodmagic/altar/AltarUtil.java
  - getTier: sprawdzanie tieru
  - getUpgrades: zliczanie run
  
- 1.18.2: wayoftime/bloodmagic/altar/AltarTier.java
  - Definicje tierów
  
- 1.18.2: wayoftime/bloodmagic/altar/AltarUpgrade.java
  - Zliczanie run

Struktury ołtarzy są IDENTYCZNE w obu wersjach.
Zmienia się tylko sposób przechowywania (metadata -> blockstates).
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple, Optional, Set


class AltarTier(Enum):
    """Tier ołtarza"""
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6


class BloodRuneType(Enum):
    """Typy run Blood Magic"""
    BLANK = 0
    SPEED = 1
    EFFICIENCY = 2
    SACRIFICE = 3
    SELF_SACRIFICE = 4
    DISPLACEMENT = 5
    CAPACITY = 6
    ORB = 7
    AUGMENTED_CAPACITY = 8
    ACCELERATION = 9


@dataclass
class AltarComponent:
    """Komponent struktury ołtarza"""
    x: int
    y: int
    z: int
    block_type: str  # "blood_rune", "stone_brick", "glowstone", "beacon", "crystal"
    metadata: int = 0  # Dla 1.7.10 - typ runy
    is_rune: bool = False
    is_upgrade_slot: bool = False


@dataclass
class RuneUpgradeCounts:
    """Zliczone runy w strukturze"""
    speed: int = 0
    efficiency: int = 0
    sacrifice: int = 0
    self_sacrifice: int = 0
    displacement: int = 0
    capacity: int = 0
    augmented_capacity: int = 0
    orb: int = 0
    acceleration: int = 0


class AltarTierCalculator:
    """
    Kalkulator tierów ołtarza Blood Magic
    
    Dokładnie odwzorowuje logikę z kodu źródłowego.
    """
    
    # Struktury ołtarzy - identyczne w 1.7.10 i 1.18.2
    # Source: UpgradedAltars.loadAltars()
    
    TIER_2_STRUCTURE = [
        # Runy na poziomie -1 (wokół ołtarza)
        AltarComponent(-1, -1, -1, "blood_rune", 0, True, False),
        AltarComponent(0, -1, -1, "blood_rune", 0, True, True),
        AltarComponent(1, -1, -1, "blood_rune", 0, True, False),
        AltarComponent(-1, -1, 0, "blood_rune", 0, True, True),
        AltarComponent(1, -1, 0, "blood_rune", 0, True, True),
        AltarComponent(-1, -1, 1, "blood_rune", 0, True, False),
        AltarComponent(0, -1, 1, "blood_rune", 0, True, True),
        AltarComponent(1, -1, 1, "blood_rune", 0, True, False),
    ]
    
    TIER_3_STRUCTURE = TIER_2_STRUCTURE + [
        # Rozszerzenie do 3x3 wszystkie runy
        AltarComponent(-1, -1, -1, "blood_rune", 0, True, True),
        AltarComponent(0, -1, -1, "blood_rune", 0, True, True),
        AltarComponent(1, -1, -1, "blood_rune", 0, True, True),
        AltarComponent(-1, -1, 0, "blood_rune", 0, True, True),
        AltarComponent(1, -1, 0, "blood_rune", 0, True, True),
        AltarComponent(-1, -1, 1, "blood_rune", 0, True, True),
        AltarComponent(0, -1, 1, "blood_rune", 0, True, True),
        AltarComponent(1, -1, 1, "blood_rune", 0, True, True),
        # Pillars na rogach
        AltarComponent(-3, -1, -3, "stone_brick", 0, False, False),
        AltarComponent(-3, 0, -3, "stone_brick", 0, False, False),
        AltarComponent(3, -1, -3, "stone_brick", 0, False, False),
        AltarComponent(3, 0, -3, "stone_brick", 0, False, False),
        AltarComponent(-3, -1, 3, "stone_brick", 0, False, False),
        AltarComponent(-3, 0, 3, "stone_brick", 0, False, False),
        AltarComponent(3, -1, 3, "stone_brick", 0, False, False),
        AltarComponent(3, 0, 3, "stone_brick", 0, False, False),
        # Glowstone na szczycie pillarów
        AltarComponent(-3, 1, -3, "glowstone", 0, False, False),
        AltarComponent(3, 1, -3, "glowstone", 0, False, False),
        AltarComponent(-3, 1, 3, "glowstone", 0, False, False),
        AltarComponent(3, 1, 3, "glowstone", 0, False, False),
        # Runy na poziomie -2 (7x7 perimeter)
        *[AltarComponent(3, -2, i, "blood_rune", 0, True, True) for i in range(-2, 3)],
        *[AltarComponent(-3, -2, i, "blood_rune", 0, True, True) for i in range(-2, 3)],
        *[AltarComponent(i, -2, 3, "blood_rune", 0, True, True) for i in range(-2, 3)],
        *[AltarComponent(i, -2, -3, "blood_rune", 0, True, True) for i in range(-2, 3)],
    ]
    
    TIER_4_STRUCTURE = TIER_3_STRUCTURE + [
        # Runy na poziomie -3 (11x11 perimeter)
        *[AltarComponent(5, -3, i, "blood_rune", 0, True, True) for i in range(-3, 4)],
        *[AltarComponent(-5, -3, i, "blood_rune", 0, True, True) for i in range(-3, 4)],
        *[AltarComponent(i, -3, 5, "blood_rune", 0, True, True) for i in range(-3, 4)],
        *[AltarComponent(i, -3, -5, "blood_rune", 0, True, True) for i in range(-3, 4)],
        # Pillars na zewnętrznych rogach
        *[AltarComponent(5, i, 5, "stone_brick", 0, False, False) for i in range(-2, 2)],
        *[AltarComponent(5, i, -5, "stone_brick", 0, False, False) for i in range(-2, 2)],
        *[AltarComponent(-5, i, 5, "stone_brick", 0, False, False) for i in range(-2, 2)],
        *[AltarComponent(-5, i, -5, "stone_brick", 0, False, False) for i in range(-2, 2)],
        # Large Bloodstone Brick na szczycie
        AltarComponent(5, 2, 5, "large_bloodstone_brick", 0, False, False),
        AltarComponent(5, 2, -5, "large_bloodstone_brick", 0, False, False),
        AltarComponent(-5, 2, 5, "large_bloodstone_brick", 0, False, False),
        AltarComponent(-5, 2, -5, "large_bloodstone_brick", 0, False, False),
    ]
    
    TIER_5_STRUCTURE = TIER_4_STRUCTURE + [
        # Beacony na rogach
        AltarComponent(-8, -3, 8, "beacon", 0, False, False),
        AltarComponent(-8, -3, -8, "beacon", 0, False, False),
        AltarComponent(8, -3, -8, "beacon", 0, False, False),
        AltarComponent(8, -3, 8, "beacon", 0, False, False),
        # Runy na poziomie -4 (17x17 perimeter)
        *[AltarComponent(8, -4, i, "blood_rune", 0, True, True) for i in range(-6, 7)],
        *[AltarComponent(-8, -4, i, "blood_rune", 0, True, True) for i in range(-6, 7)],
        *[AltarComponent(i, -4, 8, "blood_rune", 0, True, True) for i in range(-6, 7)],
        *[AltarComponent(i, -4, -8, "blood_rune", 0, True, True) for i in range(-6, 7)],
    ]
    
    TIER_6_STRUCTURE = TIER_5_STRUCTURE + [
        # Crystal na rogach
        AltarComponent(11, 3, 11, "crystal", 0, False, False),
        AltarComponent(-11, 3, -11, "crystal", 0, False, False),
        AltarComponent(11, 3, -11, "crystal", 0, False, False),
        AltarComponent(-11, 3, 11, "crystal", 0, False, False),
        # Pillars pod crystal
        *[AltarComponent(11, i, 11, "stone_brick", 0, False, False) for i in range(-4, 3)],
        *[AltarComponent(-11, i, -11, "stone_brick", 0, False, False) for i in range(-4, 3)],
        *[AltarComponent(11, i, -11, "stone_brick", 0, False, False) for i in range(-4, 3)],
        *[AltarComponent(-11, i, 11, "stone_brick", 0, False, False) for i in range(-4, 3)],
        # Runy na poziomie -5 (23x23 perimeter)
        *[AltarComponent(11, -5, i, "blood_rune", 0, True, True) for i in range(-9, 10)],
        *[AltarComponent(-11, -5, i, "blood_rune", 0, True, True) for i in range(-9, 10)],
        *[AltarComponent(i, -5, 11, "blood_rune", 0, True, True) for i in range(-9, 10)],
        *[AltarComponent(i, -5, -11, "blood_rune", 0, True, True) for i in range(-9, 10)],
    ]
    
    def __init__(self):
        self.structures = {
            2: self.TIER_2_STRUCTURE,
            3: self.TIER_3_STRUCTURE,
            4: self.TIER_4_STRUCTURE,
            5: self.TIER_5_STRUCTURE,
            6: self.TIER_6_STRUCTURE,
        }
    
    def check_tier(self, blocks: List[Tuple[int, int, int, str, int]]) -> AltarTier:
        """
        Sprawdź tier ołtarza na podstawie bloków wokół niego
        
        Source 1.7.10: UpgradedAltars.isAltarValid() linie 30-41
        Source 1.18.2: AltarUtil.getTier()
        
        Args:
            blocks: Lista bloków jako (x, y, z, block_type, metadata)
                   względem pozycji ołtarza (0, 0, 0)
        
        Returns:
            Najwyższy możliwy tier
        """
        # Sprawdź od najwyższego tieru
        for tier in [6, 5, 4, 3, 2]:
            if self._check_tier_structure(tier, blocks):
                return AltarTier(tier)
        
        return AltarTier.ONE
    
    def _check_tier_structure(self, tier: int, blocks: List[Tuple[int, int, int, str, int]]) -> bool:
        """Sprawdź czy struktura pasuje do danego tieru"""
        required = self.structures.get(tier, [])
        
        for component in required:
            # Sprawdź czy blok jest na swoim miejscu
            found = False
            for block in blocks:
                bx, by, bz, btype, bmeta = block
                if (bx == component.x and by == component.y and bz == component.z):
                    # Sprawdź typ bloku
                    if component.is_rune:
                        # Dla run - sprawdź czy to blood_rune (ignoruj metadata w walidacji struktury)
                        if "rune" in btype or btype == component.block_type:
                            found = True
                            break
                    else:
                        if btype == component.block_type:
                            found = True
                            break
            
            if not found:
                return False
        
        return True
    
    def get_upgrades(self, tier: AltarTier, blocks: List[Tuple[int, int, int, str, int]]) -> RuneUpgradeCounts:
        """
        Zlicz runy ulepszeń w strukturze
        
        Source 1.7.10: UpgradedAltars.getUpgrades() linie 194-262
        Source 1.18.2: AltarUtil.getUpgrades()
        
        Args:
            tier: Tier ołtarza
            blocks: Lista bloków
            
        Returns:
            Zliczone typy run
        """
        counts = RuneUpgradeCounts()
        
        if tier == AltarTier.ONE:
            return counts
        
        required = self.structures.get(tier.value, [])
        
        for component in required:
            if not component.is_upgrade_slot:
                continue
            
            # Znajdź blok na tej pozycji
            for block in blocks:
                bx, by, bz, btype, bmeta = block
                if (bx == component.x and by == component.y and bz == component.z):
                    if "rune" in btype:
                        # Zlicz typ runy na podstawie metadata (1.7.10) lub blockstate (1.18.2)
                        self._count_rune(bmeta, counts)
                    break
        
        return counts
    
    def _count_rune(self, metadata: int, counts: RuneUpgradeCounts) -> None:
        """Zlicz runę na podstawie jej typu (metadata)"""
        # Mapowanie metadata na typ runy
        # Source: BloodRune.java i UpgradedAltars.getUpgrades()
        if metadata == 1:
            counts.speed += 1
        elif metadata == 2:
            counts.efficiency += 1
        elif metadata == 3:
            counts.sacrifice += 1
        elif metadata == 4:
            counts.self_sacrifice += 1
        elif metadata == 5:
            counts.displacement += 1
        elif metadata == 6:
            counts.capacity += 1
        elif metadata == 7:
            counts.orb += 1
        elif metadata == 8:
            counts.augmented_capacity += 1
        elif metadata == 9:
            counts.acceleration += 1
    
    def calculate_multipliers(self, counts: RuneUpgradeCounts) -> Dict[str, float]:
        """
        Oblicz multiplikatory na podstawie zliczonych run
        
        Source 1.7.10: TEAltar.checkAndSetAltar() linie 798-809
        Source 1.18.2: BloodAltar.checkTier() linie 473-490
        
        Formuły z kodu źródłowego:
        - consumptionMultiplier = 0.20 * speed
        - efficiencyMultiplier = 0.85 ^ efficiency
        - sacrificeMultiplier = 0.10 * sacrifice
        - selfSacrificeMultiplier = 0.10 * self_sacrifice
        - capacityMultiplier = (1 * 1.10^aug_cap + 0.20 * cap)
        - dislocationMultiplier = 1.2 ^ displacement
        - orbMultiplier = 1 + 0.02 * orb
        """
        import math
        
        return {
            "consumption_multiplier": 0.20 * counts.speed,
            "efficiency_multiplier": math.pow(0.85, counts.efficiency),
            "sacrifice_multiplier": 0.10 * counts.sacrifice,
            "self_sacrifice_multiplier": 0.10 * counts.self_sacrifice,
            "capacity_multiplier": (1 * math.pow(1.10, counts.augmented_capacity) + 0.20 * counts.capacity),
            "dislocation_multiplier": math.pow(1.2, counts.displacement),
            "orb_multiplier": 1 + 0.02 * counts.orb,
            "acceleration_upgrades": counts.acceleration,
        }


def test_tier_calculation():
    """Test kalkulatora tierów"""
    print("=== Test kalkulatora tierów ołtarza ===\n")
    
    calculator = AltarTierCalculator()
    
    # Test 1: Ołtarz Tier 1 (pusty)
    print("Test 1: Pusty ołtarz")
    blocks = []
    tier = calculator.check_tier(blocks)
    print(f"  Wykryty tier: {tier.name}")
    assert tier == AltarTier.ONE
    print("  ✓ Poprawnie rozpoznany jako Tier 1\n")
    
    # Test 2: Ołtarz Tier 2 (8 run wokół)
    print("Test 2: Tier 2 (8 run)")
    blocks = [
        (-1, -1, -1, "blood_rune", 0),
        (0, -1, -1, "blood_rune", 0),
        (1, -1, -1, "blood_rune", 0),
        (-1, -1, 0, "blood_rune", 0),
        (1, -1, 0, "blood_rune", 0),
        (-1, -1, 1, "blood_rune", 0),
        (0, -1, 1, "blood_rune", 0),
        (1, -1, 1, "blood_rune", 0),
    ]
    tier = calculator.check_tier(blocks)
    print(f"  Wykryty tier: {tier.name}")
    assert tier == AltarTier.TWO
    print("  ✓ Poprawnie rozpoznany jako Tier 2\n")
    
    # Test 3: Ołtarz Tier 3 z różnymi runami
    print("Test 3: Tier 3 z różnymi runami")
    blocks = [
        # 3x3 wszystkie runy
        (-1, -1, -1, "blood_rune", 1),  # Speed
        (0, -1, -1, "blood_rune", 2),   # Efficiency
        (1, -1, -1, "blood_rune", 3),   # Sacrifice
        (-1, -1, 0, "blood_rune", 4),   # Self-Sacrifice
        (1, -1, 0, "blood_rune", 6),    # Capacity
        (-1, -1, 1, "blood_rune", 0),
        (0, -1, 1, "blood_rune", 0),
        (1, -1, 1, "blood_rune", 0),
        # Pillars
        (-3, -1, -3, "stone_brick", 0),
        (-3, 0, -3, "stone_brick", 0),
        (3, -1, -3, "stone_brick", 0),
        (3, 0, -3, "stone_brick", 0),
        (-3, -1, 3, "stone_brick", 0),
        (-3, 0, 3, "stone_brick", 0),
        (3, -1, 3, "stone_brick", 0),
        (3, 0, 3, "stone_brick", 0),
        # Glowstone
        (-3, 1, -3, "glowstone", 0),
        (3, 1, -3, "glowstone", 0),
        (-3, 1, 3, "glowstone", 0),
        (3, 1, 3, "glowstone", 0),
        # Runy na -2
        (3, -2, -2, "blood_rune", 0),
        (3, -2, -1, "blood_rune", 0),
        (3, -2, 0, "blood_rune", 0),
        (3, -2, 1, "blood_rune", 0),
        (3, -2, 2, "blood_rune", 0),
        (-3, -2, -2, "blood_rune", 0),
        (-3, -2, -1, "blood_rune", 0),
        (-3, -2, 0, "blood_rune", 0),
        (-3, -2, 1, "blood_rune", 0),
        (-3, -2, 2, "blood_rune", 0),
        (-2, -2, 3, "blood_rune", 0),
        (-1, -2, 3, "blood_rune", 0),
        (0, -2, 3, "blood_rune", 0),
        (1, -2, 3, "blood_rune", 0),
        (2, -2, 3, "blood_rune", 0),
        (-2, -2, -3, "blood_rune", 0),
        (-1, -2, -3, "blood_rune", 0),
        (0, -2, -3, "blood_rune", 0),
        (1, -2, -3, "blood_rune", 0),
        (2, -2, -3, "blood_rune", 0),
    ]
    tier = calculator.check_tier(blocks)
    print(f"  Wykryty tier: {tier.name}")
    assert tier == AltarTier.THREE
    
    # Zlicz runy
    counts = calculator.get_upgrades(tier, blocks)
    print(f"  Zliczone runy:")
    print(f"    Speed: {counts.speed}")
    print(f"    Efficiency: {counts.efficiency}")
    print(f"    Sacrifice: {counts.sacrifice}")
    print(f"    Self-Sacrifice: {counts.self_sacrifice}")
    print(f"    Capacity: {counts.capacity}")
    
    # Oblicz multiplikatory
    multipliers = calculator.calculate_multipliers(counts)
    print(f"  Multiplikatory:")
    for name, value in multipliers.items():
        print(f"    {name}: {value:.3f}")
    
    print("  ✓ Poprawnie rozpoznany jako Tier 3\n")
    
    print("=== Wszystkie testy zaliczone! ===")


if __name__ == "__main__":
    test_tier_calculation()
