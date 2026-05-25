"""
Konwerter NBT TileMultipart 1.7.10 -> 1.18.2

Source mapping:
- 1.7.10: codechicken.multipart.TileMultipart.func_145841_b / createFromNBT
          codechicken.microblock.Microblock.save/load
          codechicken.multipart.minecraft.McMetaPart.save/load
- 1.18.2: codechicken.multipart.block.TileMultipart (BlockEntity API)

Zasady konwersji (zgodne ze SKILL.md):
- Nie tworzymy własnych kluczy NBT.
- Shape, material, meta przenoszone 1:1.
- Zmieniamy tylko namespace part IDs.
- ID TileMultipart zmienia się na cb_multipart:saved_multipart.
"""

from __future__ import annotations
from typing import Any
from copy import deepcopy

from .mappings import map_part_id, map_te_id


class TileMultipartNBTConverter:
    """
    Konwerter NBT TileMultipart.
    """

    @classmethod
    def convert(cls, nbt_1710: dict[str, Any]) -> dict[str, Any] | None:
        """
        Konwertuje NBT TileMultipart z 1.7.10 na 1.18.2.

        Wejście: dict reprezentujący NBT compound z 1.7.10 (zawiera "id", "x", "y", "z", "parts")
        Wyjście: dict reprezentujący NBT compound gotowy do zapisu w 1.18.2
                 (zawiera "id", "x", "y", "z", "parts")
        """
        if not nbt_1710:
            return None

        old_id = nbt_1710.get("id", "")
        new_id = map_te_id(old_id)
        if new_id is None:
            # Fallback — jeśli exact string nie jest w mapowaniu, używamy domyślnego
            new_id = "cb_multipart:saved_multipart"

        # Głęboka kopia żeby nie modyfikować oryginału
        nbt_1182 = deepcopy(nbt_1710)
        nbt_1182["id"] = new_id

        # Konwersja partów
        parts = nbt_1182.get("parts", [])
        if isinstance(parts, list):
            converted_parts = []
            for part in parts:
                converted_part = cls._convert_part(part)
                if converted_part is not None:
                    converted_parts.append(converted_part)
            nbt_1182["parts"] = converted_parts

        return nbt_1182

    @classmethod
    def _convert_part(cls, part: dict[str, Any]) -> dict[str, Any] | None:
        """
        Konwertuje pojedynczy part NBT.
        Zmienia tylko klucz 'id' zgodnie z mapowaniem; pozostałe dane (shape, material, meta) bez zmian.
        """
        if not part or "id" not in part:
            return None

        converted = deepcopy(part)
        old_part_id = converted["id"]
        new_part_id = map_part_id(old_part_id)
        converted["id"] = new_part_id
        return converted
