"""
Symulacja konwersji Apothecary Mortar: 1.7.10 → 1.18.2

Source 1.7.10: xreliquary.blocks.tile.TileEntityMortar (extends TileEntityInventory)
  readFromNBT / writeToNBT:
    pestleUsed: short  (0–5, liczba użyć tłuczka)
    Items: NBTTagList  (vanilla format: [{Slot:<byte>, id:<str>, Count:<byte>, Damage:<short>, tag:{...}}])
    CustomName: string (opcjonalny)

Source 1.18.2: reliquary.block.tile.ApothecaryMortarBlockEntity
  loadAdditional / saveAdditional:
    pestleUsed: short  (identyczny klucz i typ)
    items: CompoundTag (format ItemStackHandler Forge:
              {Size:3, Items:[{Slot:<int>, id:<str>, Count:<byte>, tag:{...}}]})
    UWAGA: CustomName nie jest zapisywany w 1.18.2 (NeoForge CustomName w BlockEntityBase)

Kluczowe zmiany:
  1. pestleUsed – klucz i typ identyczne, wartość przenosi się bez zmian
  2. Items (top-level) → items.Items (w sub-compound ItemStackHandler)
  3. Format itemu:
     - 1.7.10: {Slot:<byte>, id:<str_1710>, Count:<byte>, Damage:<short>, tag:{...}}
     - 1.18.2: {Slot:<int>, id:<str_1182>, Count:<byte>, tag:{...}}
  4. Remapping ID itemów: "xreliquary:<name>" → "reliquary:<name>"
     (dla vanilla ingredientów bez zmiany: "minecraft:<name>" → "minecraft:<name>")
  5. tag (NBT compound) → components (DataComponents format)
  6. Damage (metadata) → obsluga przez components lub ignorowanie dla ingredientów

Ograniczenie konwersji:
  PotionEssence w moździerzu (item xreliquary:potion_essence):
  - 1.7.10: tag = PotionEssence.writeToNBT() = {effects:[{id,duration,potency}]}
  - 1.18.2: components = {minecraft:potion_contents: ...}
  - Wymaga tej samej konwersji co w kaldron (PotionEssenceConverter).
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .potion_essence_sim import PotionEssenceConverter


# Mapowanie ID itemów 1.7.10 → 1.18.2 dla składników moździerza
# Pełna lista wymagałaby mappings.py, tutaj przykładowe kluczowe itemki
ITEM_ID_REMAP = {
    # Reliquary items
    "xreliquary:mob_ingredient":   "reliquary:mob_ingredient",
    "xreliquary:potion_essence":   "reliquary:potion_essence",
    # Vanilla items – bez zmiany (przykładowe, które mogą być w moździerzu)
    "minecraft:sugar":             "minecraft:sugar",
    "minecraft:apple":             "minecraft:apple",
    "minecraft:spider_eye":        "minecraft:spider_eye",
    "minecraft:blaze_powder":      "minecraft:blaze_powder",
    "minecraft:iron_ingot":        "minecraft:iron_ingot",
    "minecraft:ghast_tear":        "minecraft:ghast_tear",
    "minecraft:golden_carrot":     "minecraft:golden_carrot",
    "minecraft:nether_wart":       "minecraft:nether_wart",
    "minecraft:magma_cream":       "minecraft:magma_cream",
    "minecraft:fermented_spider_eye": "minecraft:fermented_spider_eye",
    "minecraft:glowstone_dust":    "minecraft:glowstone_dust",
    "minecraft:redstone":          "minecraft:redstone",
    "minecraft:gunpowder":         "minecraft:gunpowder",
}


@dataclass
class ItemStack1710:
    """Item w slocie moździerza, format 1.7.10."""
    slot: int
    item_id: str      # np. "xreliquary:mob_ingredient"
    count: int
    damage: int       # metadata – dla mob_ingredient = typ składnika
    tag: Optional[Dict[str, Any]] = None  # NBT tag (np. PotionEssence)

    @classmethod
    def from_nbt(cls, nbt: Dict[str, Any]) -> "ItemStack1710":
        return cls(
            slot=nbt.get("Slot", 0),
            item_id=nbt.get("id", "minecraft:air"),
            count=nbt.get("Count", 1),
            damage=nbt.get("Damage", 0),
            tag=nbt.get("tag"),
        )


@dataclass
class ItemStack1182:
    """Item w slocie moździerza, format 1.18.2 ItemStackHandler."""
    slot: int
    item_id: str      # np. "reliquary:mob_ingredient"
    count: int
    components: Optional[Dict[str, Any]] = None

    def to_nbt(self) -> Dict[str, Any]:
        # Forge 1.18.2: ItemStack.save() writes "Count" (uppercase, byte).
        # "count" (lowercase) causes getByte("Count") to return 0 → empty stack.
        nbt: Dict[str, Any] = {
            "Slot": self.slot,
            "id": self.item_id,
            "Count": self.count,
        }
        if self.components:
            nbt["components"] = self.components
        return nbt


class MortarConverter:
    """
    Konwertuje stan Apothecary Mortar 1.7.10 → 1.18.2.

    Główne zadania:
    - Przenieś pestleUsed bez zmian
    - Remapuj format inventory: Items → items.Items
    - Remapuj ID itemów
    - Konwertuj tag PotionEssence → components dla potion_essence
    """

    def __init__(self):
        self._essence_converter = PotionEssenceConverter()

    def remap_item_id(self, id_1710: str) -> str:
        """Remapuje ID itemu 1.7.10 → 1.18.2."""
        if id_1710 in ITEM_ID_REMAP:
            return ITEM_ID_REMAP[id_1710]
        # Fallback: xreliquary: → reliquary:, reszta bez zmian
        if id_1710.startswith("xreliquary:"):
            return "reliquary:" + id_1710[len("xreliquary:"):]
        return id_1710

    def convert_item(
        self, item_1710: ItemStack1710
    ) -> Tuple[ItemStack1182, List[str]]:
        """
        Konwertuje jeden item z formatu 1.7.10 → 1.18.2.

        Obsługuje:
        - Remap ID
        - Konwersja Damage (metadata) → components (gdzie potrzebne)
        - Konwersja tag PotionEssence → components minecraft:potion_contents
        """
        warnings: List[str] = []
        new_id = self.remap_item_id(item_1710.item_id)
        components: Optional[Dict[str, Any]] = None

        if item_1710.item_id in ("xreliquary:mob_ingredient",):
            # mob_ingredient: metadata = typ składnika
            # W 1.18.2 może być zapisany jako damage lub przez custom_data
            # Konserwatywnie: zachowaj jako custom_data
            if item_1710.damage != 0:
                components = {"minecraft:custom_data": {"Damage": item_1710.damage}}

        elif item_1710.item_id == "xreliquary:potion_essence" and item_1710.tag:
            # PotionEssence: konwertuj tag → components minecraft:potion_contents
            effects_tag, eff_warnings = self._essence_converter.build_cauldron_effects_tag(
                item_1710.tag
            )
            warnings.extend(eff_warnings)
            if effects_tag.get("custom_effects"):
                components = {"minecraft:potion_contents": effects_tag}
            else:
                warnings.append("potion_essence nie zawierał efektów – item będzie pusty")

        return (
            ItemStack1182(
                slot=item_1710.slot,
                item_id=new_id,
                count=item_1710.count,
                components=components,
            ),
            warnings,
        )

    def convert(
        self, te_nbt_1710: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], List[str]]:
        """
        Konwertuje NBT TileEntityMortar 1.7.10 → NBT ApothecaryMortarBlockEntity 1.18.2.

        Args:
            te_nbt_1710: surowy NBT TileEntity z 1.7.10

        Returns:
            (nbt_1182, lista ostrzeżeń)
        """
        warnings: List[str] = []

        # pestleUsed – identyczny
        pestle_used = te_nbt_1710.get("pestleUsed", 0)

        # Konwertuj sloty inventory
        raw_items = te_nbt_1710.get("Items", [])
        converted_items: List[Dict[str, Any]] = []

        for raw in raw_items:
            item_1710 = ItemStack1710.from_nbt(raw)
            item_1182, item_warnings = self.convert_item(item_1710)
            warnings.extend(item_warnings)
            converted_items.append(item_1182.to_nbt())

        # ItemStackHandler format: {Size:3, Items:[...]}
        items_handler = {
            "Size": 3,
            "Items": converted_items,
        }

        nbt_1182: Dict[str, Any] = {
            "pestleUsed": pestle_used,
            "items": items_handler,
        }

        # CustomName – w 1.18.2 nie jest obsługiwane przez moździerz (pominięte)
        if "CustomName" in te_nbt_1710:
            warnings.append("CustomName moździerza nie jest obsługiwane w 1.18.2 – pomijam")

        return nbt_1182, warnings


# --- Przykładowe dane 1.7.10 ---

# Moździerz pusty
SAMPLE_MORTAR_EMPTY = {
    "pestleUsed": 0,
    "Items": [],
}

# Moździerz z dwoma vanilla składnikami, 2 użycia tłuczka
SAMPLE_MORTAR_TWO_INGREDIENTS = {
    "pestleUsed": 2,
    "Items": [
        {"Slot": 0, "id": "minecraft:sugar",       "Count": 1, "Damage": 0},
        {"Slot": 1, "id": "minecraft:ghast_tear",  "Count": 1, "Damage": 0},
    ],
}

# Moździerz z mob_ingredient (metadata=3) + spider_eye, 4 użycia
SAMPLE_MORTAR_MOB_INGREDIENT = {
    "pestleUsed": 4,
    "Items": [
        {"Slot": 0, "id": "xreliquary:mob_ingredient", "Count": 1, "Damage": 3},
        {"Slot": 1, "id": "minecraft:spider_eye",       "Count": 1, "Damage": 0},
    ],
}

# Moździerz z PotionEssence (wynik poprzedniego mielenia dodany z powrotem)
SAMPLE_MORTAR_WITH_ESSENCE = {
    "pestleUsed": 1,
    "Items": [
        {
            "Slot": 0,
            "id": "xreliquary:potion_essence",
            "Count": 1,
            "Damage": 0,
            "tag": {
                "effects": [
                    {"id": 1,  "duration": 900, "potency": 0},
                    {"id": 10, "duration": 300, "potency": 0},
                ]
            },
        },
        {"Slot": 1, "id": "minecraft:blaze_powder", "Count": 1, "Damage": 0},
    ],
}

# Moździerz z pełnym zestawem (3 sloty zajęte)
SAMPLE_MORTAR_FULL = {
    "pestleUsed": 3,
    "Items": [
        {"Slot": 0, "id": "minecraft:iron_ingot",    "Count": 1, "Damage": 0},
        {"Slot": 1, "id": "minecraft:magma_cream",   "Count": 1, "Damage": 0},
        {"Slot": 2, "id": "minecraft:golden_carrot", "Count": 1, "Damage": 0},
    ],
}


def run_demo():
    """Demonstracja konwersji stanów moździerza."""
    converter = MortarConverter()
    samples = [
        ("Pusty moździerz", SAMPLE_MORTAR_EMPTY),
        ("2 vanilla składniki", SAMPLE_MORTAR_TWO_INGREDIENTS),
        ("mob_ingredient (meta=3)", SAMPLE_MORTAR_MOB_INGREDIENT),
        ("Z PotionEssence", SAMPLE_MORTAR_WITH_ESSENCE),
        ("Pełny (3 sloty)", SAMPLE_MORTAR_FULL),
    ]

    for name, sample in samples:
        print(f"\n=== {name} ===")
        nbt_1182, warnings = converter.convert(sample)
        print(f"  pestleUsed: {sample['pestleUsed']} → {nbt_1182['pestleUsed']}")
        items_1182 = nbt_1182["items"]["Items"]
        print(f"  Liczba itemów: {len(sample['Items'])} → {len(items_1182)}")
        for item in items_1182:
            print(f"    Slot {item['Slot']}: {item['id']} x{item['Count']}" +
                  (f" components={item['components']}" if item.get('components') else ""))
        if warnings:
            print(f"  OSTRZEŻENIA: {warnings}")


if __name__ == "__main__":
    run_demo()
