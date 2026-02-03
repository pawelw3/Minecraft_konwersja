"""
Mapowania bloków dla Blood Magic 1.7.10 -> 1.18.2

Source mapping:
- 1.7.10: WayofTime/alchemicalWizardry/common/block/BloodRune.java
  - getRuneEffect() zwraca wartość odpowiadającą BloodRuneType w 1.18.2
  
- 1.18.2: wayoftime/bloodmagic/common/block/BlockBloodRune.java
  - Każdy typ runy to osobny blok (nie blockstate)
  - wayoftime/bloodmagic/block/enums/BloodRuneType.java definiuje typy

IMPORTANT: W 1.18.2 każda runa to osobny blok, nie używa się blockstate "type"
"""

from enum import Enum
from typing import Dict, Any, Tuple, Optional


class BloodRuneType(Enum):
    """
    Typy Blood Runes - mapowanie efektów 1.7.10 -> nazwy bloków 1.18.2
    
    Source 1.18.2: wayoftime/bloodmagic/block/enums/BloodRuneType.java
    Kolejność odpowiada wartościom zwracanym przez getRuneEffect() w 1.7.10
    """
    BLANK = (0, "blank_rune")
    SPEED = (1, "speed_rune")
    EFFICIENCY = (2, "efficiency_rune")
    SACRIFICE = (3, "sacrifice_rune")
    SELF_SACRIFICE = (4, "self_sacrifice_rune")
    DISPLACEMENT = (5, "dislocation_rune")  # W 1.7.10: Dislocation
    CAPACITY = (6, "capacity_rune")  # W 1.7.10: Altar Capacity
    AUGMENTED_CAPACITY = (7, "better_capacity_rune")  # W 1.7.10: Better Capacity
    ORB = (8, "orb_rune")  # W 1.7.10: Orb Capacity
    ACCELERATION = (9, "acceleration_rune")
    CHARGING = (10, "charging_rune")  # Nowość w 1.18.2
    
    def __init__(self, effect_id: int, block_id_1182: str):
        self.effect_id = effect_id
        self.block_id_1182 = block_id_1182


# Mapowanie ID bloków 1.7.10 -> 1.18.2
# Source 1.7.10: WayofTime/alchemicalWizardry/ModBlocks.java
# Source 1.18.2: wayoftime/bloodmagic/common/block/BloodMagicBlocks.java

# Główne bloki (nie runy)
BLOCK_ID_MAPPING: Dict[str, str] = {
    # Bloki z TileEntity
    "AWWayofTime:Altar": "bloodmagic:altar",
    "AWWayofTime:masterStone": "bloodmagic:master_ritual_stone",
    "AWWayofTime:imperfectRitualStone": "bloodmagic:imperfect_ritual_stone",
    
    # Bloki dekoracyjne
    "AWWayofTime:largeBloodStoneBrick": "bloodmagic:large_bloodstone_brick",
    "AWWayofTime:bloodStoneBrick": "bloodmagic:bloodstone_brick",
    
    # Bloki usunięte
    "AWWayofTime:soulForge": None,
    "AWWayofTime:demonPortal": None,
    "AWWayofTime:pedestal": None,
}

# Mapowanie run - osobne bloki w 1.7.10 i 1.18.2
# Source: BloodRune.java (getRuneEffect), SpeedRune.java, EfficiencyRune.java, etc.
RUNE_BLOCK_MAPPING: Dict[str, str] = {
    # 1.7.10 block ID -> 1.18.2 block ID
    "AWWayofTime:speedRune": "bloodmagic:speed_rune",
    "AWWayofTime:efficiencyRune": "bloodmagic:efficiency_rune",
    "AWWayofTime:runeOfSacrifice": "bloodmagic:sacrifice_rune",
    "AWWayofTime:runeOfSelfSacrifice": "bloodmagic:self_sacrifice_rune",
}

# Mapowanie BloodRune (z metadanymi) -> osobne bloki w 1.18.2
# Source 1.7.10: BloodRune.java getRuneEffect() i getIcon()
BLOOD_RUNE_META_MAPPING: Dict[int, str] = {
    0: "bloodmagic:blank_rune",           # Blank Rune
    1: "bloodmagic:dislocation_rune",     # Dislocation (w 1.7.10: metadata 1 -> effect 5)
    2: "bloodmagic:capacity_rune",        # Capacity (w 1.7.10: metadata 2 -> effect 6)
    3: "bloodmagic:better_capacity_rune", # Augmented Capacity (w 1.7.10: metadata 3 -> effect 7)
    4: "bloodmagic:orb_rune",             # Orb Capacity (w 1.7.10: metadata 4 -> effect 8)
    5: "bloodmagic:acceleration_rune",    # Acceleration (w 1.7.10: metadata 5 -> effect 9)
}

# Mapowanie Tile Entity IDs
# UWAGA: TE ID na mapie 1.7.10 to "containerAltar" i "containerMasterStone"
# (zgodnie z kodem źródłowym: WayofTime/alchemicalWizardry/common/block/BlockAltar.java)
TE_ID_MAPPING: Dict[str, str] = {
    # Rzeczywiste TE ID z mapy
    "containerAltar": "bloodmagic:altar",
    "containerMasterStone": "bloodmagic:master_ritual_stone",
    "TileSoulJar": "bloodmagic:soul_snare",  # TODO: zweryfikować w 1.18.2
    # Oczekiwane TE ID (fallback)
    "Altar": "bloodmagic:altar",
    "MasterStone": "bloodmagic:master_ritual_stone",
    "SoulForge": None,  # Usunięty
}


def map_block_id(block_id_1710: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Mapuj ID bloku z 1.7.10 na 1.18.2
    
    Args:
        block_id_1710: ID bloku w formacie 1.7.10 (np. "AWWayofTime:Altar")
        
    Returns:
        Tuple (block_id_1182, warning)
        - block_id_1182: ID w 1.18.2 lub None jeśli usunięty/nieznany
        - warning: Ostrzeżenie jeśli blok usunięty lub zmieniony
    """
    # Najpierw sprawdź mapowanie run (osobne bloki)
    if block_id_1710 in RUNE_BLOCK_MAPPING:
        return RUNE_BLOCK_MAPPING[block_id_1710], None
    
    # Następnie sprawdź BloodRune (będzie obsługiwane przez metadata)
    if block_id_1710 == "AWWayofTime:bloodRune":
        # Wymaga metadata - zwróć specjalny marker
        return "bloodmagic:BLOOD_RUNE_NEEDS_METADATA", None
    
    # Pozostałe bloki
    if block_id_1710 not in BLOCK_ID_MAPPING:
        return None, f"BM-W-UNKNOWN-BLOCK: Nieznany blok Blood Magic: {block_id_1710}"
    
    mapped = BLOCK_ID_MAPPING[block_id_1710]
    
    if mapped is None:
        if block_id_1710 == "AWWayofTime:soulForge":
            return None, "BM-W-SOULFORGE-REMOVED: Soul Forge został usunięty w 1.18.2"
        elif block_id_1710 == "AWWayofTime:demonPortal":
            return None, "BM-W-DEMONPORTAL-REMOVED: Demon Portal został usunięty w 1.18.2"
        else:
            return None, f"BM-W-BLOCK-REMOVED: Blok {block_id_1710} został usunięty w 1.18.2"
    
    return mapped, None


def map_blood_rune(metadata: int) -> Tuple[Optional[str], Optional[str]]:
    """
    Mapuj BloodRune z metadanych na blok 1.18.2
    
    Source 1.7.10: BloodRune.java getRuneEffect() i getIcon()
    
    Args:
        metadata: Wartość metadata 0-5
        
    Returns:
        Tuple (block_id_1182, warning)
    """
    if metadata in BLOOD_RUNE_META_MAPPING:
        return BLOOD_RUNE_META_MAPPING[metadata], None
    
    # Nieznana metadata
    return None, f"BM-W-RUNE-UNKNOWN-META: Nieznana metadata BloodRune: {metadata}"


def map_te_id(te_id_1710: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Mapuj ID Tile Entity z 1.7.10 na Block Entity ID w 1.18.2
    
    Args:
        te_id_1710: ID Tile Entity w 1.7.10 (np. "Altar")
        
    Returns:
        Tuple (be_id_1182, warning)
    """
    if te_id_1710 not in TE_ID_MAPPING:
        return None, f"BM-W-UNKNOWN-TE: Nieznane Tile Entity Blood Magic: {te_id_1710}"
    
    mapped = TE_ID_MAPPING[te_id_1710]
    
    if mapped is None:
        return None, f"BM-W-TE-REMOVED: TileEntity {te_id_1710} nie istnieje w 1.18.2"
    
    return mapped, None
