"""
Symulacja API ForgeMultipart 1.7.10 (1.2.0.345)
Źródło prawdy: dekompilacja JAR ForgeMultipart-1.7.10-1.2.0.345-universal.jar (Vineflower)

Kluczowe klasy zdekompilowane:
- codechicken.multipart.TileMultipart (func_145841_b / createFromNBT)
- codechicken.multipart.minecraft.TorchPart / ButtonPart / LeverPart / RedstoneTorchPart
- codechicken.microblock.Microblock (save/load)
- codechicken.microblock.ItemMicroPart (create)
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple
import copy


# ---------------------------------------------------------------------------
# MicroMaterialRegistry (symulacja)
# ---------------------------------------------------------------------------
class MicroMaterialRegistry:
    """
    Symuluje rejestr materiałów mikrobloków.
    W 1.7.10 material to int ID, zapisywany jako string name w NBT.
    """
    _id_to_name: Dict[int, str] = {}
    _name_to_id: Dict[str, int] = {}
    _next_id: int = 0

    @classmethod
    def register(cls, name: str) -> int:
        if name in cls._name_to_id:
            return cls._name_to_id[name]
        mid = cls._next_id
        cls._next_id += 1
        cls._id_to_name[mid] = name
        cls._name_to_id[name] = mid
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


# Predefiniowane materiały (jak w ForgeMicroblock)
MicroMaterialRegistry.register("minecraft:stone")
MicroMaterialRegistry.register("minecraft:cobblestone")
MicroMaterialRegistry.register("minecraft:stonebrick")
MicroMaterialRegistry.register("minecraft:glass")
MicroMaterialRegistry.register("minecraft:dirt")
MicroMaterialRegistry.register("minecraft:planks")
MicroMaterialRegistry.register("minecraft:iron_block")


# ---------------------------------------------------------------------------
# TMultiPart (bazowa klasa parta)
# ---------------------------------------------------------------------------
class TMultiPart:
    """
    Symuluje codechicken.multipart.TMultiPart.
    W 1.7.10 jest to trait/abstract class; tu uproszczona wersja Python.
    """

    def __init__(self):
        self._tile: Optional[TileMultipart] = None

    def get_type(self) -> str:
        """Zwraca string ID parta (używany jako 'id' w NBT parta)."""
        raise NotImplementedError

    def bind(self, tile: TileMultipart):
        """Wiąże part z TileMultipart."""
        self._tile = tile

    def tile(self) -> Optional[TileMultipart]:
        return self._tile

    def save(self, tag: dict):
        """Zapisz stan parta do NBT dict."""
        pass

    def load(self, tag: dict):
        """Wczytaj stan parta z NBT dict."""
        pass

    def does_tick(self) -> bool:
        return False

    def get_drops(self) -> List[dict]:
        return []


# ---------------------------------------------------------------------------
# Microblock (part mikrobloku)
# ---------------------------------------------------------------------------
class Microblock(TMultiPart):
    """
    Symuluje codechicken.microblock.Microblock.

    NBT (z dekompilacji save/load):
        tag["shape"] = byte  -> (size << 4) | slot
        tag["material"] = string -> MicroMaterialRegistry.materialName(material)

    getType() zwraca microClass().getName() -> np. "mcr_face", "mcr_hollow".
    """

    MICRO_CLASS_NAME: str = "microblock"  # override w podklasach

    def __init__(self, material: int = 0):
        super().__init__()
        self._material: int = material
        self._shape: int = 0  # byte: (size << 4) | slot

    def get_type(self) -> str:
        return self.MICRO_CLASS_NAME

    # -- shape / size / slot --
    def get_size(self) -> int:
        return self._shape >> 4

    def get_shape_slot(self) -> int:
        return self._shape & 15

    def set_shape(self, size: int, slot: int):
        self._shape = (size << 4) | (slot & 15)

    # -- material --
    def get_material(self) -> int:
        return self._material

    def set_material(self, value: int):
        self._material = value

    def get_material_name(self) -> str:
        return MicroMaterialRegistry.material_name(self._material)

    # -- NBT --
    def save(self, tag: dict):
        tag["shape"] = self._shape
        tag["material"] = self.get_material_name()

    def load(self, tag: dict):
        self._shape = tag.get("shape", 0)
        mat_name = tag.get("material", "")
        self._material = MicroMaterialRegistry.material_id(mat_name)

    def get_drops(self) -> List[dict]:
        # Uproszczona symulacja — w prawdziwym kodzie rozdziela na mniejsze części
        return [{
            "item": "ForgeMicroblock:microblock",
            "shape": self._shape,
            "material": self.get_material_name()
        }]

    def __repr__(self):
        return f"<{self.__class__.__name__} mat={self.get_material_name()} size={self.get_size()} slot={self.get_shape_slot()}>"


class FaceMicroblock(Microblock):
    MICRO_CLASS_NAME = "mcr_face"

class HollowMicroblock(Microblock):
    MICRO_CLASS_NAME = "mcr_hollow"

class CornerMicroblock(Microblock):
    MICRO_CLASS_NAME = "mcr_corner"

class EdgeMicroblock(Microblock):
    MICRO_CLASS_NAME = "mcr_edge"

class PostMicroblock(Microblock):
    MICRO_CLASS_NAME = "mcr_post"


# ---------------------------------------------------------------------------
# McMetaPart / Vanilla parts
# ---------------------------------------------------------------------------
class McMetaPart(TMultiPart):
    """
    Symuluje codechicken.multipart.minecraft.McMetaPart.
    NBT: tag["meta"] = byte
    """
    PART_TYPE: str = "mc_meta"

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


class TorchPart(McMetaPart):
    PART_TYPE = "mc_torch"

class RedstoneTorchPart(McMetaPart):
    PART_TYPE = "mc_redtorch"

class ButtonPart(McMetaPart):
    PART_TYPE = "mc_button"

class LeverPart(McMetaPart):
    PART_TYPE = "mc_lever"


# ---------------------------------------------------------------------------
# ItemMicroPart
# ---------------------------------------------------------------------------
class ItemMicroPart:
    """
    Symuluje codechicken.microblock.ItemMicroPart.
    Tworzy mikrobloki na podstawie item stack data.
    """

    @staticmethod
    def create(stack_shape: int, material_name: str) -> Microblock:
        """
        Uproszczona fabryka mikrobloków.
        W 1.7.10 ItemMicroPart.create(int, int, String) zawiera więcej logiki,
        ale kluczowe jest połączenie shape + material.
        """
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
# MultiPartRegistry (symulacja fabryki partów)
# ---------------------------------------------------------------------------
class MultiPartRegistry:
    _factories: Dict[str, type] = {}

    @classmethod
    def register(cls, part_type: str, factory: type):
        cls._factories[part_type] = factory

    @classmethod
    def load_part(cls, part_type: str, tag: dict) -> Optional[TMultiPart]:
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
    MultiPartRegistry.register("mcr_face", FaceMicroblock)
    MultiPartRegistry.register("mcr_hollow", HollowMicroblock)
    MultiPartRegistry.register("mcr_corner", CornerMicroblock)
    MultiPartRegistry.register("mcr_edge", EdgeMicroblock)
    MultiPartRegistry.register("mcr_post", PostMicroblock)
    MultiPartRegistry.register("mc_torch", TorchPart)
    MultiPartRegistry.register("mc_redtorch", RedstoneTorchPart)
    MultiPartRegistry.register("mc_button", ButtonPart)
    MultiPartRegistry.register("mc_lever", LeverPart)


register_defaults()


# ---------------------------------------------------------------------------
# TileMultipart
# ---------------------------------------------------------------------------
class TileMultipart:
    """
    Symuluje codechicken.multipart.TileMultipart (1.7.10).

    NBT format (z func_145841_b / createFromNBT):
    {
        "id": "TileMultipart" | "ForgeMultipart:TileMultipart",  // do weryfikacji
        "x": int, "y": int, "z": int,
        "parts": [
            {"id": "mcr_face", "shape": byte, "material": "minecraft:stone"},
            {"id": "mc_torch", "meta": byte},
            ...
        ]
    }
    """

    def __init__(self, x: int = 0, y: int = 0, z: int = 0):
        self.x = x
        self.y = y
        self.z = z
        self.parts: List[TMultiPart] = []
        self._does_tick = False

    def add_part(self, part: TMultiPart):
        part.bind(self)
        self.parts.append(part)
        if part.does_tick():
            self._does_tick = True

    def remove_part(self, part: TMultiPart):
        if part in self.parts:
            self.parts.remove(part)
            part.bind(None)

    def get_part(self, index: int) -> Optional[TMultiPart]:
        if 0 <= index < len(self.parts):
            return self.parts[index]
        return None

    def is_solid(self, side: int) -> bool:
        # Uproszczenie — w prawdziwym kodzie deleguje do partów
        return len(self.parts) > 0

    # -- NBT 1.7.10 --
    def write_to_nbt(self) -> dict:
        """
        Symuluje func_145841_b (TileEntity.writeToNBT).
        Zwraca dict reprezentujący NBT compound.
        """
        tag = {
            "id": "TileMultipart",  # exact string do weryfikacji na mapie
            "x": self.x,
            "y": self.y,
            "z": self.z,
        }
        parts_list = []
        for part in self.parts:
            part_tag = {"id": part.get_type()}
            part.save(part_tag)
            parts_list.append(part_tag)
        tag["parts"] = parts_list
        return tag

    @classmethod
    def read_from_nbt(cls, tag: dict) -> Optional[TileMultipart]:
        """
        Symuluje createFromNBT z TileMultipart$.
        """
        parts_list = tag.get("parts", [])
        if not parts_list:
            return None

        tile = cls(
            x=tag.get("x", 0),
            y=tag.get("y", 0),
            z=tag.get("z", 0),
        )
        for part_tag in parts_list:
            part_type = part_tag.get("id", "")
            part = MultiPartRegistry.load_part(part_type, part_tag)
            if part is not None:
                tile.add_part(part)
        return tile

    def __repr__(self):
        return f"<TileMultipart ({self.x},{self.y},{self.z}) parts={self.parts}>"


# ---------------------------------------------------------------------------
# BlockMultipart (stub — logika kontenera jest w TileMultipart)
# ---------------------------------------------------------------------------
class BlockMultipart:
    """
    Stub symulujący codechicken.multipart.BlockMultipart.
    W 1.7.10 jest to pojedynczy blok w rejestrze (ForgeMultipart:block).
    Wszystkie interakcje deleguje do TileMultipart.
    """
    REGISTRY_NAME = "ForgeMultipart:block"
