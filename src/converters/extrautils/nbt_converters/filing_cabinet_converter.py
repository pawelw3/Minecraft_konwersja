"""
Konwerter NBT dla Filing Cabinet Extra Utilities 1.7.10 → 1.18.2 placeholder.

Filing Cabinet przechowuje itemy w niestandardowym formacie NBT:
- item_no (int) — liczba slotów
- item_0, item_1, ... (NBTTagCompound) — każdy to ItemStack z dodatkowym polem Size

W 1.18.2 nie ma bezpośredniego odpowiednika, więc używamy inventory placeholdera.
"""
from __future__ import annotations

from typing import Any

from converters.common.placeholders import INVENTORY_PLACEHOLDER_BLOCK_ENTITY_ID


def convert_filing_cabinet_nbt(
    nbt_1710: dict,
    target_id: str,
    source_block_id: str = "extrautils:filing",
) -> dict[str, Any]:
    """Konwertuje NBT Filing Cabinet na NBT inventory placeholdera 1.18.2.

    Returns dict z polami:
        nbt: dict — NBT do zapisu w placeholderze
        blockstate_props: dict | None
        warnings: list[str]
    """
    warnings: list[str] = []
    pos_x = nbt_1710.get("x", 0)
    pos_y = nbt_1710.get("y", 0)
    pos_z = nbt_1710.get("z", 0)

    # Odczytaj itemy z niestandardowego formatu ExU
    items_1182: list[dict] = []
    item_no = nbt_1710.get("item_no", 0)
    if isinstance(item_no, int) and item_no > 0:
        for i in range(item_no):
            key = f"item_{i}"
            item_nbt = nbt_1710.get(key)
            if not isinstance(item_nbt, dict):
                continue
            item_id = item_nbt.get("id", "")
            if not item_id:
                continue
            count = item_nbt.get("Size", item_nbt.get("Count", 1))
            damage = item_nbt.get("Damage", 0)

            # Konwersja item ID (uproszczona)
            new_id = _map_item_id(item_id, damage)

            entry = {
                "Slot": len(items_1182),
                "id": new_id,
                "Count": int(count),
            }
            if "tag" in item_nbt:
                entry["tag"] = item_nbt["tag"]
            items_1182.append(entry)

    if len(items_1182) > 54:
        warnings.append(
            f"EXU-W-FILING-CABINET-OVERFLOW: Filing Cabinet contains {len(items_1182)} "
            f"item stacks; placeholder can only display up to 54. Remaining items "
            f"are preserved in original_nbt."
        )

    # Zbuduj NBT inventory placeholdera
    nbt_1182 = {
        "id": INVENTORY_PLACEHOLDER_BLOCK_ENTITY_ID,
        "x": pos_x,
        "y": pos_y,
        "z": pos_z,
        "source_mod": "extrautils",
        "source_block_id": source_block_id,
        "source_te_id": nbt_1710.get("id", "TileEntityFilingCabinet"),
        "source_metadata": 0,
        "source_pos": [pos_x, pos_y, pos_z],
        "conversion_reason": "filing_cabinet_no_1182_equivalent",
        "conversion_stage": "extrautils_zadanie3",
        "original_nbt": dict(nbt_1710),
    }

    if items_1182:
        nbt_1182["Items"] = items_1182[:54]
        nbt_1182["attached_items"] = items_1182[:54]

    return {
        "nbt": nbt_1182,
        "blockstate_props": None,
        "warnings": warnings,
    }


def _map_item_id(old_id: str, damage: int = 0) -> str:
    """Podstawowe mapowanie ID itemów 1.7.10 → 1.18.2."""
    if not old_id:
        return "minecraft:stone"

    # Usuń numeryczne ID (vanilla czasem używało)
    if old_id.isdigit():
        # Próba mapowania numerycznego — uproszczone
        numeric_id = int(old_id)
        # Najczęstsze vanilla itemy
        _VANILLA_NUMERIC = {
            1: "minecraft:stone", 2: "minecraft:grass", 3: "minecraft:dirt",
            4: "minecraft:cobblestone", 5: "minecraft:oak_planks",
            264: "minecraft:diamond", 265: "minecraft:iron_ingot",
            266: "minecraft:gold_ingot", 331: "minecraft:redstone",
            341: "minecraft:slime_ball",
        }
        return _VANILLA_NUMERIC.get(numeric_id, "minecraft:paper")

    # Modyfikacje namespace
    if old_id.startswith("minecraft:"):
        return old_id
    if ":" not in old_id:
        return f"minecraft:{old_id}"

    # Znane mody
    if old_id.startswith("extrautils:"):
        return old_id.replace("extrautils:", "extrautilitiesreborn:")

    return old_id
