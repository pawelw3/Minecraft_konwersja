"""Wspolne helpery do konwersji inventory miedzy 1.7.10 a 1.18.2.

Uzywane przez wiele modow (MrCrayfish, BiblioCraft, Thermal, Mekanism, ...).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import copy


def convert_inventory_1710_to_1182(
    items_1710: list[dict[str, Any]],
    slot_tag: str,
    target_size: int,
    damage_mapper: dict[tuple[str, int], str] | None = None,
    item_id_resolver: callable | None = None,
) -> list[dict[str, Any]]:
    """Konwertuje liste itemow z formatu 1.7.10 na standard 1.18.2.

    Args:
        items_1710: Lista itemow z custom slot tag (np. [{"id": "...", "Count": 1, "fridgeSlot": 0}, ...])
        slot_tag: Nazwa custom slot tag w 1.7.10 (np. "fridgeSlot", "cabinetSlot", "mailBoxSlot")
        target_size: Docelowa liczba slotow w 1.18.2
        damage_mapper: Opcjonalne mapowanie (item_id, damage) -> nowe item_id 1.18.2
        item_id_resolver: Opcjonalna funkcja (str) -> str do mapowania numerycznych ID na string ID

    Returns:
        Lista itemow w formacie 1.18.2 (ze standardowym "Slot")
    """
    result: list[dict[str, Any]] = []
    seen_slots: set[int] = set()

    for item in items_1710:
        if not isinstance(item, dict):
            continue

        slot = item.get(slot_tag, item.get("Slot", item.get("slot", 0)))
        try:
            slot = int(slot)
        except (TypeError, ValueError):
            slot = 0

        # Unikamy duplikatow slotow
        while slot in seen_slots and slot < target_size:
            slot += 1
        if slot >= target_size:
            continue
        seen_slots.add(slot)

        item_id = str(item.get("id", ""))
        damage = item.get("Damage", 0)

        # Mapowanie numerycznych ID na string ID (1.7.10 -> 1.18.2)
        if item_id_resolver is not None:
            item_id = item_id_resolver(item_id)

        # Mapowanie damage na nowe ID
        if damage_mapper and (item_id, damage) in damage_mapper:
            item_id = damage_mapper[(item_id, damage)]
            damage = 0

        count = item.get("Count", 1)
        try:
            count = max(1, min(64, int(count)))
        except (TypeError, ValueError):
            count = 1

        new_item: dict[str, Any] = {
            "id": item_id,
            "Count": count,
            "Slot": slot,
        }

        # Zachowujemy NBT tag
        tag = item.get("tag")
        if isinstance(tag, dict) and tag:
            new_item["tag"] = copy.deepcopy(tag)

        result.append(new_item)

    return result


def convert_inventory_list_to_container_helper(
    items_1710: list[dict[str, Any]],
    slot_tag: str,
    target_size: int,
) -> dict[str, Any]:
    """Konwertuje inventory 1.7.10 na format ContainerHelper 1.18.2 (NBT Compound).

    Zwraca dict gotowy do uzycia jako nbt_1182["Items"].
    """
    converted = convert_inventory_1710_to_1182(items_1710, slot_tag, target_size)
    return {"Items": converted}


def extract_items_from_legacy_nbt(
    nbt: dict[str, Any] | None,
    possible_keys: list[str],
    slot_tags: list[str],
) -> tuple[list[dict[str, Any]], str, str]:
    """Probuje wyciagnac inventory z legacy NBT.

    Args:
        nbt: NBT compound z 1.7.10
        possible_keys: Mozliwe nazwy kluczy listy itemow (np. ["fridgeItems", "Items", "items"])
        slot_tags: Mozliwe nazwy slot tagow (np. ["fridgeSlot", "Slot", "slot"])

    Returns:
        (lista_itemow, znaleziony_klucz, znaleziony_slot_tag)
    """
    if not nbt:
        return [], "", ""

    for key in possible_keys:
        if key in nbt and isinstance(nbt[key], list):
            items = nbt[key]
            if not items:
                return [], key, ""
            # Sprawdzamy jaki slot tag jest uzywany
            first = items[0]
            if isinstance(first, dict):
                for tag in slot_tags:
                    if tag in first:
                        return items, key, tag
                # Brak slot tagu — zakladamy Slot=0,1,2...
                return items, key, ""
    return [], "", ""
