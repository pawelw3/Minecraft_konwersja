# -*- coding: utf-8 -*-
"""
Symulacja mapowania blokow dekoracyjnych — MrCrayfish Furniture Mod 1.7.10 vs 1.18.2

Pokazuje jak mapowac bloki dekoracyjne miedzy wersjami:
- 1.7.10: Bloki maja warianty wood/stone (tablewood, tablestone) lub sa jedne na typ
- 1.18.2: Kazdy material to osobny blok (oak_table, spruce_table, stone_table, ...)

Obslugiwane typy: Table, Chair, CoffeeTable, Cabinet, BedsideCabinet, Blinds, Curtains,
Hedge, MailBox, Crate (zamiennik Bin), KitchenCounter, KitchenDrawer

Bazuje na kodzie zrodlowym:
- 1.7.10: MrCrayfishFurnitureMod.java (rejestracja blokow)
- 1.18.2: ModBlocks.java (rejestracja blokow)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


# ============================================================
# Mapowania materialow 1.7.10 -> 1.18.2
# ============================================================

WOOD_TYPES_1182 = [
    "oak", "spruce", "birch", "jungle", "acacia", "dark_oak",
    "crimson", "warped",
    "stripped_oak", "stripped_spruce", "stripped_birch", "stripped_jungle",
    "stripped_acacia", "stripped_dark_oak", "stripped_crimson", "stripped_warped"
]

STONE_TYPES_1182 = ["stone", "granite", "diorite", "andesite"]

# W 1.7.10 "wood" = domyslnie oak (brak metadanych drewna!)
# W 1.7.10 "stone" = stone
DEFAULT_WOOD = "oak"
DEFAULT_STONE = "stone"


class BlockMappingTable:
    """
    Tabela mapowania blokow 1.7.10 -> 1.18.2
    """

    # Bloki z wariantem wood/stone w 1.7.10
    WOOD_STONE_BLOCKS = {
        "tablewood": ("table", DEFAULT_WOOD),
        "tablestone": ("table", DEFAULT_STONE),
        "chairwood": ("chair", DEFAULT_WOOD),
        "chairstone": ("chair", DEFAULT_STONE),
        "coffeetablewood": ("coffee_table", DEFAULT_WOOD),
        "coffeetablestone": ("coffee_table", DEFAULT_STONE),
    }

    # Bloki drewniane w 1.7.10 (brak wariantu stone)
    WOOD_ONLY_BLOCKS = {
        "cabinet": ("cabinet", DEFAULT_WOOD),
        "bedsidecabinet": ("bedside_cabinet", DEFAULT_WOOD),
        "mailbox": ("mail_box", DEFAULT_WOOD),
        "blinds": ("blinds", DEFAULT_WOOD),
        "curtains": ("curtains", DEFAULT_WOOD),
        "hedge": ("hedge", DEFAULT_WOOD),
    }

    # Bloki usuniete w 1.18.2 -> mapowanie na zamienniki (decyzja projektowa)
    REMOVED_TO_REPLACEMENT = {
        "bin": ("crate", DEFAULT_WOOD),           # Bin -> Crate (inventory)
        "wallcabinet": ("cabinet", DEFAULT_WOOD), # WallCabinet -> Cabinet
        "counterdoored": ("kitchen_counter", "white"),  # CounterDoored -> KitchenCounter (white)
        "kitchencabinet": ("kitchen_drawer", "white"),  # KitchenCabinet -> KitchenDrawer (white)
    }

    # Bloki ktore zmienily nazwe registry
    RENAMED_BLOCKS = {
        "stonepath": ("rock_path", None),  # Brak materialu
        "whitefence": ("white_picket_fence", None),
    }

    @classmethod
    def map_block(cls, registry_name_1710: str, metadata: int = 0) -> Optional[Tuple[str, Dict]]:
        """
        Mapuje blok 1.7.10 na blok 1.18.2
        Zwraca: (registry_name_1182, extra_data) lub None jesli air/placeholder
        """
        name = registry_name_1710.lower().replace("cfm:", "")

        # 1. Bezposrednie mapowanie wood/stone
        if name in cls.WOOD_STONE_BLOCKS:
            block_type, material = cls.WOOD_STONE_BLOCKS[name]
            return (f"cfm:{material}_{block_type}", {})

        # 2. Bloki drewniane (domyslnie oak)
        if name in cls.WOOD_ONLY_BLOCKS:
            block_type, material = cls.WOOD_ONLY_BLOCKS[name]
            return (f"cfm:{material}_{block_type}", {})

        # 3. Zamienniki dla usunietych blokow
        if name in cls.REMOVED_TO_REPLACEMENT:
            block_type, material = cls.REMOVED_TO_REPLACEMENT[name]
            return (f"cfm:{material}_{block_type}", {"converted_from": name})

        # 4. Zmienione nazwy
        if name in cls.RENAMED_BLOCKS:
            block_type, material = cls.RENAMED_BLOCKS[name]
            if material:
                return (f"cfm:{material}_{block_type}", {})
            return (f"cfm:{block_type}", {})

        # 5. Fridge / Freezer (multiblok, osobna symulacja)
        if name == "fridge":
            return ("cfm:fridge_light", {})
        if name == "freezer":
            return ("cfm:freezer_light", {})

        # 6. Couch (osobna symulacja z kolorami)
        if name == "couch":
            return ("cfm:white_sofa", {"color": metadata})  # Domyslnie white, metadata override

        # 7. Bloki lazienkowe -> placeholdery (decyzja projektowa)
        if name in ["basin", "bath1", "bath2", "showerbottom", "showertop",
                    "showerheadoff", "showerheadon", "toilet", "tap"]:
            return ("minecraft:barrier", {"placeholder_for": name, "source_mod": "cfm"})

        # 8. Elektryczne/usuniete -> strata (air, decyzja projektowa)
        if name in ["oven", "microwave", "computer", "printer", "tv", "stereo",
                    "washingmachine", "dishwasher", "toaster", "blender", "plate",
                    "cup", "choppingboard", "cookiejar", "present", "electricfence",
                    "doorbell", "firealarmoff", "firealarmon", "ceilinglightoff",
                    "ceilinglighton", "lampoff", "lampon", "tree", "birdbath"]:
            return None  # Air (strata)

        # 9. Dekoracyjne niestandardowe -> placeholder
        if name in ["hey", "nyan", "pattern", "yellowglow", "whiteglass"]:
            return ("minecraft:barrier", {"placeholder_for": name, "source_mod": "cfm", "note": "decorative removed"})

        # 10. BarStool -> brak bezposredniego odpowiednika, placeholder
        if name == "barstool":
            return ("minecraft:barrier", {"placeholder_for": name, "source_mod": "cfm"})

        # Nieznany blok -> placeholder
        return ("minecraft:barrier", {"placeholder_for": name, "source_mod": "cfm", "unknown": True})

    @classmethod
    def get_mapping_table(cls) -> Dict[str, Optional[Tuple[str, Dict]]]:
        """Zwraca pelna tabele mapowan dla wszystkich znanych blokow 1.7.10"""
        all_blocks = [
            # Wood/stone variants
            "tablewood", "tablestone", "chairwood", "chairstone",
            "coffeetablewood", "coffeetablestone",
            # Wood only
            "cabinet", "bedsidecabinet", "mailbox", "blinds", "curtains", "hedge",
            # Removed -> replacement
            "bin", "wallcabinet", "counterdoored", "kitchencabinet",
            # Renamed
            "stonepath", "whitefence",
            # Multiblock
            "fridge", "freezer", "couch",
            # Bathroom -> placeholder
            "basin", "bath1", "bath2", "showerbottom", "showertop",
            "showerheadoff", "showerheadon", "toilet", "tap",
            # Tech -> air
            "oven", "microwave", "computer", "printer", "tv", "stereo",
            "washingmachine", "dishwasher", "toaster", "blender",
            "plate", "cup", "choppingboard", "cookiejar", "present",
            "electricfence", "doorbell", "firealarmoff", "firealarmon",
            "ceilinglightoff", "ceilinglighton", "lampoff", "lampon",
            "tree", "birdbath",
            # Decorative
            "hey", "nyan", "pattern", "yellowglow", "whiteglass", "barstool",
        ]
        return {name: cls.map_block(name) for name in all_blocks}


# ============================================================
# Symulacja postawienia bloku na mapie
# ============================================================

class BlockPlacementSimulator:
    """
    Symuluje konwersje bloku z 1.7.10 na 1.18.2 wraz z NBT
    """

    @staticmethod
    def convert_block_event(block_1710: str, metadata: int = 0, te_nbt: Optional[Dict] = None) -> Dict:
        """
        Tworzy event konwersji dla pojedynczego bloku
        Zwraca dict zgodny z formatem eventow projektu
        """
        result = BlockMappingTable.map_block(block_1710, metadata)

        if result is None:
            return {
                "action": "remove",
                "source_block": block_1710,
                "source_metadata": metadata,
                "target_block": "minecraft:air",
                "reason": "removed_in_1182"
            }

        target_block, extra = result

        if target_block == "minecraft:barrier":
            return {
                "action": "placeholder",
                "source_block": block_1710,
                "source_metadata": metadata,
                "target_block": target_block,
                "placeholder_data": extra
            }

        event = {
            "action": "remap",
            "source_block": block_1710,
            "source_metadata": metadata,
            "target_block": target_block,
            "extra": extra
        }

        # Dodaj NBT jesli przekazano
        if te_nbt:
            event["source_nbt"] = te_nbt

        return event


# ============================================================
# Demonstracja / Testy
# ============================================================

def demo():
    print("=" * 70)
    print("Symulacja: Block Mappings (Decorative Blocks)")
    print("1.7.10 -> 1.18.2 registry name conversion")
    print("=" * 70)

    # --- Tabela pelna ---
    print("\n--- Pelna tabela mapowan ---")
    table = BlockMappingTable.get_mapping_table()
    for src, result in sorted(table.items()):
        if result is None:
            print(f"{src:<25} -> AIR (removed)")
        else:
            tgt, extra = result
            note = f" [{extra}]" if extra else ""
            print(f"{src:<25} -> {tgt:<35}{note}")

    # --- Eventy konwersji ---
    print("\n--- Przykladowe eventy konwersji ---")
    test_cases = [
        ("tablewood", 0, None),
        ("tablestone", 0, None),
        ("chairwood", 0, None),
        ("cabinet", 0, None),
        ("mailbox", 0, None),
        ("couch", 5, {"id": "cfmCouch", "Colour": 5}),
        ("bin", 0, {"id": "cfmBin", "Items": []}),
        ("wallcabinet", 0, {"id": "cfmWallCabinet", "Items": []}),
        ("stonepath", 0, None),
        ("fridge", 0, {"id": "cfmFridge"}),
        ("basin", 0, {"id": "cfmBasin", "WaterLevel": 4}),
        ("oven", 0, {"id": "cfmOven", "Items": []}),
        ("tv", 0, {"id": "cfmTV", "Channel": 3}),
        ("toilet", 0, None),
        ("hey", 0, None),
    ]

    for block, meta, te in test_cases:
        event = BlockPlacementSimulator.convert_block_event(block, meta, te)
        print(f"\nSource: {block}:{meta}")
        print(f"  Event: {event}")

    # --- Statystyki ---
    print("\n--- Statystyki mapowan ---")
    counts = {"remap": 0, "placeholder": 0, "remove": 0}
    for src, result in table.items():
        event = BlockPlacementSimulator.convert_block_event(src)
        counts[event["action"]] = counts.get(event["action"], 0) + 1

    for action, count in counts.items():
        print(f"  {action}: {count}")

    print("\n" + "=" * 70)
    print("Symulacja zakonczona pomyslnie.")
    print("=" * 70)


if __name__ == "__main__":
    demo()
