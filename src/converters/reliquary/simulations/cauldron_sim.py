"""
Symulacja konwersji Apothecary Cauldron: 1.7.10 → 1.18.2

Source 1.7.10: xreliquary.blocks.tile.TileEntityCauldron
  readFromNBT / writeToNBT:
    hasGlowstone: boolean
    hasNetherwart: boolean
    hasGunpowder: boolean
    redstoneCount: int
    cookTime: int
    potionEssence: CompoundTag  (format PotionEssence.writeToNBT)
    UWAGA: liquidLevel NIE jest w NBT – jest w blockstate metadata (0-3)

Source 1.18.2: reliquary.block.tile.ApothecaryCauldronBlockEntity
  loadAdditional / saveAdditional:
    liquidLevel: int  (NOWE – przeniesione z blockstate do NBT)
    glowstoneCount: int  (zmiana: bool → int, można dodawać wielokrotnie)
    hasNetherwart: boolean  (bez zmian)
    hasGunpowder: boolean  (bez zmian)
    hasDragonBreath: boolean  (NOWE – brak w 1.7.10)
    redstoneCount: int  (bez zmian)
    cookTime: int  (bez zmian)
    effects: CompoundTag  (PotionContents codec – zastąpił potionEssence)

Kluczowe zmiany do zasymulowania:
  1. hasGlowstone (bool) → glowstoneCount (int): true → 1, false → 0
  2. liquidLevel: odczytać z blockstate metadata bloku, zapisać do NBT
  3. hasDragonBreath: zawsze false (brak w 1.7.10)
  4. potionEssence → effects: konwersja przez PotionEssenceConverter
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .potion_essence_sim import PotionEssenceConverter


@dataclass
class CauldronState1710:
    """Stan TileEntityCauldron z 1.7.10."""
    liquid_level: int           # z blockstate metadata (0=puste, 1-3=poziom wody)
    has_glowstone: bool
    has_netherwart: bool
    has_gunpowder: bool
    redstone_count: int
    cook_time: int
    potion_essence: Optional[Dict[str, Any]]  # None jeśli pusty

    @classmethod
    def from_nbt(cls, te_nbt: Dict[str, Any], block_meta: int) -> "CauldronState1710":
        """
        Wczytaj stan z NBT TE i blockstate metadata.

        Args:
            te_nbt: NBT TileEntity (zawartość tagu TE z chunku)
            block_meta: metadata bloku (0–3), czytana z chunk data
        """
        raw_essence = te_nbt.get("potionEssence")
        # PotionEssence jest pusta gdy tag istnieje ale effects jest puste
        if raw_essence is not None and not raw_essence.get("effects"):
            raw_essence = None
        return cls(
            liquid_level=block_meta,
            has_glowstone=te_nbt.get("hasGlowstone", False),
            has_netherwart=te_nbt.get("hasNetherwart", False),
            has_gunpowder=te_nbt.get("hasGunpowder", False),
            redstone_count=te_nbt.get("redstoneCount", 0),
            cook_time=te_nbt.get("cookTime", 0),
            potion_essence=raw_essence,
        )


@dataclass
class CauldronState1182:
    """Stan ApothecaryCauldronBlockEntity w 1.18.2."""
    liquid_level: int
    glowstone_count: int        # zastąpił has_glowstone
    has_netherwart: bool
    has_gunpowder: bool
    has_dragon_breath: bool     # nowe, zawsze false po konwersji
    redstone_count: int
    cook_time: int
    effects_tag: Optional[Dict[str, Any]]  # PotionContents codec output, None jeśli pusty

    def to_nbt(self) -> Dict[str, Any]:
        """
        Generuje NBT 1.18.2 zgodny z ApothecaryCauldronBlockEntity.saveAdditional().
        """
        nbt: Dict[str, Any] = {
            "liquidLevel": self.liquid_level,
            "cookTime": self.cook_time,
            "redstoneCount": self.redstone_count,
            "glowstoneCount": self.glowstone_count,
            "hasGunpowder": self.has_gunpowder,
            "hasDragonBreath": self.has_dragon_breath,
            "hasNetherwart": self.has_netherwart,
        }
        # addPotionContentsToCompoundTag pomija zapis gdy brak efektów
        if self.effects_tag is not None and self.effects_tag.get("custom_effects"):
            nbt["effects"] = self.effects_tag
        return nbt


class CauldronConverter:
    """
    Konwertuje stan Apothecary Cauldron 1.7.10 → 1.18.2.

    Symuluje logikę odpowiadającą mapowaniu NBT i blockstate.
    Nie wykonuje rzeczywistego parsowania chunków – przyjmuje block_meta jako argument.
    """

    def __init__(self):
        self._essence_converter = PotionEssenceConverter()

    def convert(
        self,
        te_nbt_1710: Dict[str, Any],
        block_meta: int,
    ) -> Tuple[CauldronState1182, List[str]]:
        """
        Główna metoda konwersji.

        Args:
            te_nbt_1710: surowy NBT TileEntity z 1.7.10
            block_meta: metadata bloku (0–3) odczytana z chunk data 1.7.10

        Returns:
            (CauldronState1182, lista ostrzeżeń)
        """
        warnings: List[str] = []
        state = CauldronState1710.from_nbt(te_nbt_1710, block_meta)

        # 1. hasGlowstone (bool) → glowstoneCount (int)
        glowstone_count = 1 if state.has_glowstone else 0

        # 2. potionEssence → effects (PotionContents codec)
        effects_tag = None
        if state.potion_essence is not None:
            effects_tag, eff_warnings = self._essence_converter.build_cauldron_effects_tag(
                state.potion_essence
            )
            warnings.extend(eff_warnings)
            if not effects_tag.get("custom_effects"):
                warnings.append("potionEssence nie zawierał żadnych rozpoznanych efektów – kauldron będzie pusty")
                effects_tag = None

        # 3. liquidLevel pochodzi z block_meta (nie z NBT TE)
        if block_meta < 0 or block_meta > 3:
            warnings.append(f"Nieprawidłowa wartość blockstate metadata: {block_meta} – ustawiam 0")
            liquid_level = 0
        else:
            liquid_level = block_meta

        # 4. hasDragonBreath – nowe pole, brak w 1.7.10
        has_dragon_breath = False

        state_1182 = CauldronState1182(
            liquid_level=liquid_level,
            glowstone_count=glowstone_count,
            has_netherwart=state.has_netherwart,
            has_gunpowder=state.has_gunpowder,
            has_dragon_breath=has_dragon_breath,
            redstone_count=state.redstone_count,
            cook_time=state.cook_time,
            effects_tag=effects_tag,
        )
        return state_1182, warnings

    def convert_to_nbt(
        self,
        te_nbt_1710: Dict[str, Any],
        block_meta: int,
    ) -> Tuple[Dict[str, Any], List[str]]:
        """
        Wygodna metoda zwracająca gotowy dict NBT 1.18.2.
        """
        state, warnings = self.convert(te_nbt_1710, block_meta)
        return state.to_nbt(), warnings


# --- Przykładowe dane 1.7.10 ---

# Kauldron pusty, wypełniony wodą (meta=3)
SAMPLE_CAULDRON_EMPTY = {
    "te_nbt": {
        "hasGlowstone": False,
        "hasNetherwart": False,
        "hasGunpowder": False,
        "redstoneCount": 0,
        "cookTime": 0,
        "potionEssence": {},
    },
    "block_meta": 3,
}

# Kauldron w trakcie warzenia: essence + netherwart + glowstone + redstone=2
SAMPLE_CAULDRON_BREWING = {
    "te_nbt": {
        "hasGlowstone": True,
        "hasNetherwart": True,
        "hasGunpowder": False,
        "redstoneCount": 2,
        "cookTime": 80,
        "potionEssence": {
            "effects": [
                {"id": 1,  "duration": 900,  "potency": 0},  # Speed I
                {"id": 10, "duration": 300,  "potency": 0},  # Regen I
            ]
        },
    },
    "block_meta": 3,
}

# Kauldron gotowy do nabierania: netherwart + gunpowder (splash) + ugotowany
SAMPLE_CAULDRON_DONE_SPLASH = {
    "te_nbt": {
        "hasGlowstone": False,
        "hasNetherwart": True,
        "hasGunpowder": True,
        "redstoneCount": 0,
        "cookTime": 160,
        "potionEssence": {
            "effects": [
                {"id": 5,  "duration": 1800, "potency": 1},  # Strength II
            ]
        },
    },
    "block_meta": 2,  # 2 porcje wody (2 nabierania)
}

# Kauldron pół pusty (meta=1), stary potion essence już wylany
SAMPLE_CAULDRON_PARTIAL = {
    "te_nbt": {
        "hasGlowstone": True,
        "hasNetherwart": True,
        "hasGunpowder": False,
        "redstoneCount": 5,
        "cookTime": 160,
        "potionEssence": {
            "effects": [
                {"id": 16, "duration": 4800, "potency": 0},  # Night Vision
                {"id": 22, "duration": 1200, "potency": 0},  # Absorption
            ]
        },
    },
    "block_meta": 1,
}


def run_demo():
    """Demonstracja konwersji stanów kauldron."""
    converter = CauldronConverter()
    samples = [
        ("Pusty kauldron (woda=3)", SAMPLE_CAULDRON_EMPTY),
        ("W trakcie warzenia", SAMPLE_CAULDRON_BREWING),
        ("Gotowy splash (woda=2)", SAMPLE_CAULDRON_DONE_SPLASH),
        ("Częściowo opróżniony (woda=1)", SAMPLE_CAULDRON_PARTIAL),
    ]

    for name, sample in samples:
        print(f"\n=== {name} ===")
        nbt_1182, warnings = converter.convert_to_nbt(
            sample["te_nbt"], sample["block_meta"]
        )
        print(f"  Wejście (meta={sample['block_meta']}): hasGlowstone={sample['te_nbt']['hasGlowstone']}, "
              f"hasNetherwart={sample['te_nbt']['hasNetherwart']}, "
              f"redstone={sample['te_nbt']['redstoneCount']}")
        print(f"  Wyjście NBT 1.18.2:")
        for k, v in nbt_1182.items():
            print(f"    {k}: {v}")
        if warnings:
            print(f"  OSTRZEŻENIA: {warnings}")


if __name__ == "__main__":
    run_demo()
