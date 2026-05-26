"""
Symulacja API CB Multipart 1.18.2
Źródło prawdy:
- Kod źródłowy ProjectRed 1.18.2 (importy codechicken.multipart.block.* / api.part.*)
- Kod zrodlowy CBMultipart 1.18.x (registry names: cb_multipart, cb_microblock)

Kluczowe różnice względem 1.7.10:
1. TileEntity → BlockEntity (zapis w sekcji "block_entities" chunka zamiast "TileEntities")
2. Rejestracja przez DeferredRegister / RegistryObject (Forge 1.18.2)
3. Part ID to ResourceLocation (zamiast string fabryk z MultiPartRegistry)
4. Namespace zmieniony: ForgeMultipart -> cb_multipart (core), microblock -> cb_microblock (microblocks)
"""

from __future__ import annotations
from typing import Dict, List, Optional
import copy


# ---------------------------------------------------------------------------
# MicroMaterialRegistry 1.18.2 (symulacja)
# ---------------------------------------------------------------------------
class MicroMaterialRegistry:
    """
    W 1.18.2 materiał mikrobloku też zapisywany jest jako string,
    ale system rejestracji używa ResourceLocation (np. "minecraft:stone").
    Symulujemy mapowanie nazwa → ID int (jak w 1.7.10) dla kompatybilności,
    ale w NBT 1.18.2 przechowujemy bezpośrednio string.
    """
    _name_to_id: Dict[str, int] = {}
    _id_to_name: Dict[int, str] = {}
    _next_id: int = 0

    @classmethod
    def register(cls, name: str) -> int:
        if name in cls._name_to_id:
            return cls._name_to_id[name]
        mid = cls._next_id
        cls._next_id += 1
        cls._name_to_id[name] = mid
        cls._id_to_name[mid] = name
        return mid

    @classmethod
    def material_name(cls, material_id: int) -> str:
        return cls._id_to_name.get(material_id, "")

    @classmethod
    def material_id(cls, name: str) -> int:
        return cls._name_to_id.get(name, -1)

    @classmethod
    def reset(cls):
        cls._id_to_name.clear()
        cls._name_to_id.clear()
        cls._next_id = 0


# Predefiniowane materiały (zachowane nazwy z 1.7.10)
MicroMaterialRegistry.register("minecraft:stone")
MicroMaterialRegistry.register("minecraft:cobblestone")
MicroMaterialRegistry.register("minecraft:stonebrick")
MicroMaterialRegistry.register("minecraft:glass")
MicroMaterialRegistry.register("minecraft:dirt")
MicroMaterialRegistry.register("minecraft:planks")
MicroMaterialRegistry.register("minecraft:iron_block")


# ---------------------------------------------------------------------------
# MultiPart (1.18.2)
# ---------------------------------------------------------------------------
class MultiPart:
    """
    Symuluje codechicken.multipart.api.part.MultiPart (1.18.2).
    Odpowiednik TMultiPart z 1.7.10.
    """

    def __init__(self):
        self._tile: Optional[TileMultipart] = None

    def get_type(self) -> str:
        """Zwraca ResourceLocation jako string, np. 'minecraft:torch'."""
        raise NotImplementedError

    def bind(self, tile: TileMultipart):
        self._tile = tile

    def tile(self) -> Optional[TileMultipart]:
        return self._tile

    def save(self, tag: dict):
        pass

    def load(self, tag: dict):
        pass

    def does_tick(self) -> bool:
        return False

    def get_drops(self) -> List[dict]:
        return []


# ---------------------------------------------------------------------------
# Microblock (1.18.2)
# ---------------------------------------------------------------------------
class Microblock(MultiPart):
    """
    Symuluje mikroblok w CB Multipart 1.18.2.
    Format NBT pozostaje kompatybilny z 1.7.10:
        tag["shape"] = byte
        tag["material"] = string (ResourceLocation)
    Ale get_type() zwraca teraz pelny ResourceLocation z namespace cb_microblock.
    """

    MICRO_CLASS_NAME: str = "cb_microblock:microblock"

    def __init__(self, material: int = 0):
        super().__init__()
        self._material: int = material
        self._shape: int = 0

    def get_type(self) -> str:
        return self.MICRO_CLASS_NAME

    def get_size(self) -> int:
        return self._shape >> 4

    def get_shape_slot(self) -> int:
        return self._shape & 15

    def set_shape(self, size: int, slot: int):
        self._shape = (size << 4) | (slot & 15)

    def get_material(self) -> int:
        return self._material

    def set_material(self, value: int):
        self._material = value

    def get_material_name(self) -> str:
        return MicroMaterialRegistry.material_name(self._material)

    def save(self, tag: dict):
        tag["shape"] = self._shape
        tag["material"] = self.get_material_name()

    def load(self, tag: dict):
        self._shape = tag.get("shape", 0)
        mat_name = tag.get("material", "")
        self._material = MicroMaterialRegistry.material_id(mat_name)

    def get_drops(self) -> List[dict]:
        return [{
            "item": "cb_microblock:microblock",
            "shape": self._shape,
            "material": self.get_material_name()
        }]

    def __repr__(self):
        return f"<{self.__class__.__name__} mat={self.get_material_name()} size={self.get_size()} slot={self.get_shape_slot()}>"


class FaceMicroblock(Microblock):
    MICRO_CLASS_NAME = "cb_microblock:face"

class HollowMicroblock(Microblock):
    MICRO_CLASS_NAME = "cb_microblock:hollow"

class CornerMicroblock(Microblock):
    MICRO_CLASS_NAME = "cb_microblock:corner"

class EdgeMicroblock(Microblock):
    MICRO_CLASS_NAME = "cb_microblock:edge"

class PostMicroblock(Microblock):
    MICRO_CLASS_NAME = "cb_microblock:post"


# ---------------------------------------------------------------------------
# Vanilla parts (1.18.2)
# ---------------------------------------------------------------------------
class VanillaPart(MultiPart):
    """
    Odpowiednik McMetaPart z 1.7.10.
    W 1.18.2 vanilla parts też są MultiPart, zapisują orientację w meta/byte.
    """
    PART_TYPE: str = "cb_multipart:vanilla"

    def __init__(self, meta: int = 0):
        super().__init__()
        self.meta: int = meta

    def get_type(self) -> str:
        return self.PART_TYPE

    def save(self, tag: dict):
        tag["meta"] = self.meta

    def load(self, tag: dict):
        self.meta = tag.get("meta", 0)

    def __repr__(self):
        return f"<{self.__class__.__name__} meta={self.meta}>"


class TorchPart(VanillaPart):
    PART_TYPE = "minecraft:torch"

class RedstoneTorchPart(VanillaPart):
    PART_TYPE = "minecraft:redstone_torch"

class ButtonPart(VanillaPart):
    PART_TYPE = "minecraft:stone_button"

class LeverPart(VanillaPart):
    PART_TYPE = "minecraft:lever"


# ---------------------------------------------------------------------------
# ItemMicroPart 1.18.2
# ---------------------------------------------------------------------------
class ItemMicroPart:
    @staticmethod
    def create(stack_shape: int, material_name: str) -> Microblock:
        size = stack_shape & 255
        class_id = (stack_shape >> 8) & 255
        mat_id = MicroMaterialRegistry.material_id(material_name)
        cls_map = {
            0: FaceMicroblock,
            1: HollowMicroblock,
            2: CornerMicroblock,
            3: EdgeMicroblock,
            4: PostMicroblock,
        }
        mb_cls = cls_map.get(class_id, FaceMicroblock)
        mb = mb_cls(mat_id)
        mb.set_shape(size, 0)
        return mb


# ---------------------------------------------------------------------------
# Part Registry 1.18.2 (ResourceLocation based)
# ---------------------------------------------------------------------------
class PartRegistry:
    _factories: Dict[str, type] = {}

    @classmethod
    def register(cls, part_type: str, factory: type):
        cls._factories[part_type] = factory

    @classmethod
    def load_part(cls, part_type: str, tag: dict) -> Optional[MultiPart]:
        factory = cls._factories.get(part_type)
        if factory is None:
            return None
        part = factory()
        part.load(tag)
        return part

    @classmethod
    def reset(cls):
        cls._factories.clear()


def register_defaults():
    """Rejestruje domyślne factory partów (używane po reset)."""
    PartRegistry.register("cb_microblock:face", FaceMicroblock)
    PartRegistry.register("cb_microblock:hollow", HollowMicroblock)
    PartRegistry.register("cb_microblock:corner", CornerMicroblock)
    PartRegistry.register("cb_microblock:edge", EdgeMicroblock)
    PartRegistry.register("cb_microblock:post", PostMicroblock)
    PartRegistry.register("minecraft:torch", TorchPart)
    PartRegistry.register("minecraft:redstone_torch", RedstoneTorchPart)
    PartRegistry.register("minecraft:stone_button", ButtonPart)
    PartRegistry.register("minecraft:lever", LeverPart)


register_defaults()


# ---------------------------------------------------------------------------
# TileMultipart 1.18.2 (BlockEntity)
# ---------------------------------------------------------------------------
class TileMultipart:
    """
    Symuluje codechicken.multipart.block.TileMultipart (1.18.2).

    Różnice względem 1.7.10:
    - id w NBT: "cb_multipart:saved_multipart"
    - Zapis w sekcji "block_entities" zamiast "TileEntities"
    - load() / saveAdditional() zamiast readFromNBT / writeToNBT
    """

    def __init__(self, x: int = 0, y: int = 0, z: int = 0):
        self.x = x
        self.y = y
        self.z = z
        self.parts: List[MultiPart] = []
        self._does_tick = False

    def add_part(self, part: MultiPart):
        part.bind(self)
        self.parts.append(part)
        if part.does_tick():
            self._does_tick = True

    def remove_part(self, part: MultiPart):
        if part in self.parts:
            self.parts.remove(part)
            part.bind(None)

    def get_part(self, index: int) -> Optional[MultiPart]:
        if 0 <= index < len(self.parts):
            return self.parts[index]
        return None

    # -- NBT 1.18.2 --
    def save_additional(self) -> dict:
        """
        Symuluje BlockEntity.saveAdditional (1.18.2).
        Zwraca dict z danymi BE (bez standardowych pól x,y,z,id — te dodaje chunk).
        """
        tag = {}
        parts_list = []
        for part in self.parts:
            part_tag = {"id": part.get_type()}
            part.save(part_tag)
            parts_list.append(part_tag)
        tag["parts"] = parts_list
        return tag

    def get_update_tag(self) -> dict:
        """Pakiet synchronizacji — zazwyczaj to samo co saveAdditional."""
        return self.save_additional()

    @classmethod
    def load(cls, tag: dict, pos: tuple) -> TileMultipart:
        """
        Symuluje BlockEntity.load z NBT + BlockPos.
        W 1.18.2 BlockEntityType.create wywołuje load z pełnym tagiem (z id, x, y, z).
        """
        tile = cls(
            x=tag.get("x", pos[0]),
            y=tag.get("y", pos[1]),
            z=tag.get("z", pos[2]),
        )
        parts_list = tag.get("parts", [])
        for part_tag in parts_list:
            part_type = part_tag.get("id", "")
            part = PartRegistry.load_part(part_type, part_tag)
            if part is not None:
                tile.add_part(part)
        return tile

    def __repr__(self):
        return f"<TileMultipart 1182 ({self.x},{self.y},{self.z}) parts={self.parts}>"


# ---------------------------------------------------------------------------
# BlockMultipart (stub 1.18.2)
# ---------------------------------------------------------------------------
class BlockMultipart:
    """
    Stub symulujący codechicken.multipart.block.BlockMultipart (1.18.2).
    Registry name: cb_multipart:block
    """
    REGISTRY_NAME = "cb_multipart:multipart"
