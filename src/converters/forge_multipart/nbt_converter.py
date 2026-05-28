"""
Konwerter NBT TileMultipart 1.7.10 -> CBMultipart 1.18.2.

Zrodla prawdy:
- 1.7.10: codechicken.multipart.TileMultipart oraz McMetaPart/Microblock z
  ForgeMultipart-1.7.10-1.2.0.345.
- 1.18.2: codechicken.multipart.block.TileMultipart,
  codechicken.multipart.minecraft.McStatePart oraz codechicken.microblock.part.

Zasady:
- Mikrobloki zachowuja `shape` i `material`; zmienia sie tylko part ID.
- Vanilla parts nie zapisują juz `meta`; CBMultipart 1.18.x oczekuje compound
  `state` w formacie NbtUtils.writeBlockState.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .mappings import map_microblock_material, map_part_id, map_te_id


DIRECTION_BY_1710_META = {
    1: "east",
    2: "west",
    3: "south",
    4: "north",
}


def _block_state(name: str, properties: dict[str, str] | None = None) -> dict[str, Any]:
    tag: dict[str, Any] = {"Name": name}
    if properties:
        tag["Properties"] = properties
    return tag


def _torch_state(meta: int, redstone: bool = False) -> dict[str, Any]:
    standing = "minecraft:redstone_torch" if redstone else "minecraft:torch"
    wall = "minecraft:redstone_wall_torch" if redstone else "minecraft:wall_torch"
    facing = DIRECTION_BY_1710_META.get(meta)
    if facing is None:
        return _block_state(standing)
    return _block_state(wall, {"facing": facing})


def _face_attached_state(
    block_name: str,
    meta: int,
    powered: bool = False,
) -> dict[str, Any]:
    orientation = meta & 7
    powered_value = "true" if powered else "false"

    # 1.7.x vanilla-like orientation mapping. It is intentionally conservative:
    # it preserves wall/floor/ceiling and facing, while powered state comes from
    # bit 3 for lever/button-like metadata.
    table = {
        0: {"face": "ceiling", "facing": "east"},
        1: {"face": "wall", "facing": "east"},
        2: {"face": "wall", "facing": "west"},
        3: {"face": "wall", "facing": "south"},
        4: {"face": "wall", "facing": "north"},
        5: {"face": "floor", "facing": "south"},
        6: {"face": "floor", "facing": "east"},
        7: {"face": "ceiling", "facing": "south"},
    }
    props = dict(table.get(orientation, table[5]))
    props["powered"] = powered_value
    return _block_state(block_name, props)


def _convert_vanilla_part_state(old_part_id: str, part: dict[str, Any]) -> dict[str, Any] | None:
    meta = int(part.get("meta", 0))
    if old_part_id == "mc_torch":
        return _torch_state(meta, redstone=False)
    if old_part_id == "mc_redtorch":
        return _torch_state(meta, redstone=True)
    if old_part_id == "mc_lever":
        return _face_attached_state("minecraft:lever", meta, powered=bool(meta & 8))
    if old_part_id == "mc_button":
        return _face_attached_state("minecraft:stone_button", meta, powered=bool(meta & 8))
    return None


class TileMultipartNBTConverter:
    """Konwerter NBT TileMultipart."""

    @classmethod
    def convert(cls, nbt_1710: dict[str, Any] | None) -> dict[str, Any] | None:
        """
        Konwertuje NBT TileMultipart z 1.7.10 na 1.18.2.

        Wejscie: dict NBT compound 1.7.10 z `id`, `x`, `y`, `z`, `parts`.
        Wyjscie: dict NBT compound dla BlockEntity `cb_multipart:saved_multipart`.
        """
        if not nbt_1710:
            return None

        old_id = nbt_1710.get("id", "")
        new_id = map_te_id(old_id) or "cb_multipart:saved_multipart"

        nbt_1182 = deepcopy(nbt_1710)
        nbt_1182["id"] = new_id

        converted_parts = []
        for part in nbt_1182.get("parts", []):
            converted_part = cls._convert_part(part)
            if converted_part is None:
                continue
            converted_parts.append(converted_part)
        nbt_1182["parts"] = converted_parts

        return nbt_1182

    @classmethod
    def _convert_part(cls, part: dict[str, Any]) -> dict[str, Any] | None:
        """Konwertuje pojedynczy part NBT."""
        if not part or "id" not in part:
            return None

        converted = deepcopy(part)
        old_part_id = str(converted["id"])
        converted["id"] = map_part_id(old_part_id)

        if "material" in converted:
            converted["material"] = map_microblock_material(str(converted.get("material", "")))

        state = _convert_vanilla_part_state(old_part_id, converted)
        if state is not None:
            converted.pop("meta", None)
            converted["state"] = state

        return converted
