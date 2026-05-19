# -*- coding: utf-8 -*-
"""
Symulacja mapowania kolorow Couch/Sofa — MrCrayfish Furniture Mod 1.7.10 vs 1.18.2

Pokazuje jak mapowac kolory miedzy wersjami:
- 1.7.10: BlockCouch uzywa metadanych (metadata 0-15) odpowiadajacych kolorom welny
  TileEntityCouch przechowuje int colour
- 1.18.2: SofaBlock uzywa DyeColor, kazdy kolor to osobny blok (white_sofa, orange_sofa, ...)

Bazuje na kodzie zrodlowym:
- 1.7.10: BlockCouch.java, TileEntityCouch.java
- 1.18.2: SofaBlock.java, ModBlocks.java (white_sofa, orange_sofa, ...)
"""

from dataclasses import dataclass
from typing import Dict, Optional
from enum import Enum


class DyeColor(Enum):
    """Enum kolorow barwnikow (Minecraft standard)"""
    WHITE = 0
    ORANGE = 1
    MAGENTA = 2
    LIGHT_BLUE = 3
    YELLOW = 4
    LIME = 5
    PINK = 6
    GRAY = 7
    LIGHT_GRAY = 8
    CYAN = 9
    PURPLE = 10
    BLUE = 11
    BROWN = 12
    GREEN = 13
    RED = 14
    BLACK = 15

    @property
    def name_lower(self) -> str:
        return self.name.lower()


# ============================================================
# 1.7.10 — Couch z metadata colour
# ============================================================

class TileEntityCouch1710:
    """
    Symulacja TileEntityCouch z 1.7.10
    Przechowuje: int colour (0-15)
    """
    def __init__(self):
        self.colour: int = 0  # 0 = white, domyslnie

    def write_to_nbt(self) -> Dict:
        return {"id": "cfmCouch", "Colour": self.colour}

    def read_from_nbt(self, nbt: Dict):
        self.colour = nbt.get("Colour", 0)

    def get_dye_color(self) -> DyeColor:
        """Mapuje int 0-15 na DyeColor"""
        try:
            return DyeColor(self.colour)
        except ValueError:
            return DyeColor.WHITE


class BlockCouch1710:
    """
    Symulacja BlockCouch z 1.7.10
    W 1.7.10 couch ma 16 metadanych (0-15) = kolory welny
    Blok jest jeden, metadata decyduje o kolorze
    """
    def __init__(self):
        pass

    @staticmethod
    def get_color_name(metadata: int) -> str:
        """Zwraca nazwe koloru dla danej metadanej"""
        colors = [
            "white", "orange", "magenta", "light_blue", "yellow", "lime",
            "pink", "gray", "light_gray", "cyan", "purple", "blue",
            "brown", "green", "red", "black"
        ]
        if 0 <= metadata < len(colors):
            return colors[metadata]
        return "white"


# ============================================================
# 1.18.2 — SofaBlock z osobnymi blokami per kolor
# ============================================================

class SofaBlock1182:
    """
    Symulacja SofaBlock z 1.18.2
    W 1.18.2 kazdy kolor to osobny blok:
    white_sofa, orange_sofa, magenta_sofa, ...
    Registry names: cfm:<color>_sofa
    """
    def __init__(self, color: DyeColor):
        self.color = color

    @property
    def registry_name(self) -> str:
        return f"cfm:{self.color.name_lower}_sofa"

    @classmethod
    def from_color(cls, color: DyeColor) -> "SofaBlock1182":
        return cls(color)

    @classmethod
    def from_registry_name(cls, name: str) -> Optional["SofaBlock1182"]:
        """Parsuje registry name i zwraca SofaBlock"""
        prefix = "cfm:"
        suffix = "_sofa"
        if name.startswith(prefix) and name.endswith(suffix):
            color_name = name[len(prefix):-len(suffix)]
            for dye in DyeColor:
                if dye.name_lower == color_name:
                    return cls(dye)
        return None


# ============================================================
# Konwersja Couch 1.7.10 -> Sofa 1.18.2
# ============================================================

def convert_couch_metadata_to_block(metadata: int) -> str:
    """
    Konwersja metadanych Couch 1.7.10 -> registry name Sofa 1.18.2
    metadata 0-15 -> cfm:<color>_sofa
    """
    color_name = BlockCouch1710.get_color_name(metadata)
    return f"cfm:{color_name}_sofa"


def convert_couch_te_to_block(te_nbt: Dict) -> str:
    """
    Konwersja NBT TileEntityCouch 1.7.10 -> registry name Sofa 1.18.2
    """
    colour = te_nbt.get("Colour", 0)
    return convert_couch_metadata_to_block(colour)


def convert_couch_full(metadata: int, te_nbt: Optional[Dict] = None) -> Dict:
    """
    Pelna konwersja Couch 1.7.10 -> dane Sofa 1.18.2
    Zwraca dict z informacjami do postawienia bloku 1.18.2
    """
    # Uwzgledniamy zarowno metadata bloku jak i TE NBT (w razie rozbieznosci TE wygrywa)
    effective_color = metadata
    if te_nbt and "Colour" in te_nbt:
        effective_color = te_nbt["Colour"]

    color_name = BlockCouch1710.get_color_name(effective_color)
    dye = DyeColor.WHITE
    try:
        dye = DyeColor(effective_color)
    except ValueError:
        pass

    return {
        "block": f"cfm:{color_name}_sofa",
        "color_name": color_name,
        "dye_color": dye.name,
        "metadata_source": "te" if (te_nbt and "Colour" in te_nbt) else "block",
        "nbt_1182": {}  # SofaBlock 1.18.2 nie ma BE (brak w ModBlockEntities!)
    }


# ============================================================
# Dodatkowe: Curtains i Blinds (tez maja kolory w 1.18.2)
# ============================================================

def convert_curtains_or_blinds(metadata: int, block_type: str = "curtains") -> str:
    """
    W 1.7.10 Curtains i Blinds rowniez uzywaly metadanych/wariantow
    W 1.18.2 sa osobne bloki per material (oak_curtains, spruce_curtains, ...)
    oraz per kolor (white_blinds, orange_blinds, ...)

    UWAGA: W 1.7.10 Curtains/Blinds mialy warianty drewna (oak/spruce/birch/jungle/acacia/dark_oak)
    a nie kolory! W 1.18.2 Blinds maja warianty drewna, Curtains maja warianty drewna.
    Nie ma bezposredniego mapowania colour -> curtains/blinds (to inny system).
    """
    # W 1.7.10 curtains/blinds byly w wariantach drewna (podobnie jak table/chair)
    # W 1.18.2: oak_curtains, spruce_curtains, ... (warianty drewna)
    wood_types = ["oak", "spruce", "birch", "jungle", "acacia", "dark_oak"]
    if 0 <= metadata < len(wood_types):
        return f"cfm:{wood_types[metadata]}_{block_type}"
    return f"cfm:oak_{block_type}"


# ============================================================
# Demonstracja / Testy
# ============================================================

def demo():
    print("=" * 60)
    print("Symulacja: Couch/Sofa Color Mapping")
    print("1.7.10 (metadata 0-15) -> 1.18.2 (block per color)")
    print("=" * 60)

    print("\n--- Pelna tabela mapowania ---")
    print(f"{'Meta':>5} | {'Color':<15} | {'1.18.2 Registry Name':<25}")
    print("-" * 60)
    for meta in range(16):
        color_name = BlockCouch1710.get_color_name(meta)
        registry = convert_couch_metadata_to_block(meta)
        print(f"{meta:>5} | {color_name:<15} | {registry:<25}")

    print("\n--- Konwersja z TileEntity NBT ---")
    for colour_val in [0, 1, 5, 10, 14, 15]:
        te = TileEntityCouch1710()
        te.colour = colour_val
        nbt = te.write_to_nbt()
        result = convert_couch_full(colour_val, nbt)
        print(f"TE Colour={colour_val} -> {result['block']} (source: {result['metadata_source']})")

    print("\n--- Konwersja tylko z metadanych bloku (brak TE) ---")
    for meta in [0, 3, 7, 12]:
        result = convert_couch_full(meta, None)
        print(f"Block meta={meta} -> {result['block']}")

    print("\n--- Walidacja: SofaBlock1182 z registry name ---")
    test_names = ["cfm:white_sofa", "cfm:red_sofa", "cfm:black_sofa", "cfm:invalid_sofa"]
    for name in test_names:
        sofa = SofaBlock1182.from_registry_name(name)
        if sofa:
            print(f"{name} -> color={sofa.color.name}")
        else:
            print(f"{name} -> INVALID")

    print("\n--- Curtains/Blinds (wood variants, not colors) ---")
    for meta in range(6):
        curtains = convert_curtains_or_blinds(meta, "curtains")
        blinds = convert_curtains_or_blinds(meta, "blinds")
        print(f"Meta={meta} -> {curtains}, {blinds}")

    print("\n" + "=" * 60)
    print("Symulacja zakonczona pomyslnie.")
    print("=" * 60)


if __name__ == "__main__":
    demo()
