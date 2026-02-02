"""
Symulacja systemu FramedBlocks (1.18.2) - Konwersja z BiblioCraft (1.7.10)

Ta symulacja pokazuje:
1. Jak FramedBlocks przechowuje "camo" (teksturę bloku)
2. Jak konwertować dane z BiblioCraft Furniture Paneler
3. Jak mapować meble BC na kształty FramedBlocks
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json


class FramedShape(Enum):
    """Dostępne kształty w FramedBlocks"""
    BLOCK = "framed_block"
    SLAB = "framed_slab"
    STAIRS = "framed_stairs"
    PANEL = "framed_panel"
    CORNER = "framed_corner"
    SLOPE = "framed_slope"
    DOOR = "framed_door"
    TRAPDOOR = "framed_trapdoor"
    FENCE = "framed_fence"
    GATE = "framed_gate"
    BUTTON = "framed_button"
    PRESSURE_PLATE = "framed_pressure_plate"
    SIGN = "framed_sign"
    CHEST = "framed_chest"
    LADDER = "framed_ladder"
    LEVER = "framed_lever"
    TORCH = "framed_torch"
    WALL_TORCH = "framed_wall_torch"
    PRISM = "framed_prism"
    SLICE = "framed_slice"
    THRESHOLD = "framed_threshold"


@dataclass
class BlockState:
    """Reprezentacja BlockState z Minecraft"""
    block_id: str  # np. "minecraft:oak_planks"
    properties: Dict[str, str] = field(default_factory=dict)
    
    def to_string(self) -> str:
        if not self.properties:
            return self.block_id
        props = ",".join(f"{k}={v}" for k, v in self.properties.items())
        return f"{self.block_id}[{props}]"
    
    @classmethod
    def from_string(cls, state_str: str) -> "BlockState":
        if "[" in state_str:
            block_id, props_str = state_str[:-1].split("[")
            props = {}
            for prop in props_str.split(","):
                k, v = prop.split("=")
                props[k] = v
            return cls(block_id, props)
        return cls(state_str)


@dataclass
class ItemStack:
    """Reprezentacja ItemStack z Minecraft"""
    item_id: str
    count: int = 1
    nbt: Dict = field(default_factory=dict)
    
    def to_nbt(self) -> Dict:
        return {
            "id": self.item_id,
            "Count": self.count,
            **({"tag": self.nbt} if self.nbt else {})
        }
    
    @classmethod
    def from_nbt(cls, nbt: Dict) -> "ItemStack":
        return cls(
            item_id=nbt.get("id", ""),
            count=nbt.get("Count", 1),
            nbt=nbt.get("tag", {})
        )


@dataclass
class FramedBlockEntity:
    """
    Symulacja FramedBlockEntity z FramedBlocks 1.18.2
    
    Kluczowe pola:
    - camo_stack: ItemStack użyty do ustawienia tekstury
    - camo_state: BlockState użyty jako tekstura
    - glowing: czy blok świeci (światłość 15)
    - intangible: czy blok niematerialny (przepuszcza gracza)
    - reinforced: czy blok wzmocniony (odporność jak obsydian)
    """
    pos: Tuple[int, int, int]
    shape: FramedShape
    camo_stack: Optional[ItemStack] = None
    camo_state: Optional[BlockState] = None
    glowing: bool = False
    intangible: bool = False
    reinforced: bool = False
    
    def set_camo(self, stack: ItemStack, state: BlockState):
        """Ustawia teksturę (camo) dla bloku"""
        self.camo_stack = stack
        self.camo_state = state
        print(f"  [FramedBlock] Ustawiono camo: {state.to_string()}")
    
    def clear_camo(self):
        """Czyści teksturę"""
        self.camo_stack = None
        self.camo_state = None
        print(f"  [FramedBlock] Wyczyszczono camo")
    
    def to_nbt(self) -> Dict:
        """Serializacja do NBT (1.18.2 format)"""
        nbt = {
            "shape": self.shape.value,
            "glowing": self.glowing,
            "intangible": self.intangible,
            "reinforced": self.reinforced
        }
        
        if self.camo_stack:
            nbt["camo_stack"] = self.camo_stack.to_nbt()
        else:
            nbt["camo_stack"] = {}
            
        if self.camo_state:
            # W 1.18.2 BlockState jest zapisywany przez NbtUtils.writeBlockState
            nbt["camo_state"] = {
                "Name": self.camo_state.block_id,
                "Properties": self.camo_state.properties
            }
        else:
            nbt["camo_state"] = {"Name": "minecraft:air"}
            
        return nbt
    
    @classmethod
    def from_nbt(cls, nbt: Dict, pos: Tuple[int, int, int]) -> "FramedBlockEntity":
        """Deserializacja z NBT"""
        shape = FramedShape(nbt.get("shape", "framed_block"))
        
        camo_stack = None
        if nbt.get("camo_stack"):
            camo_stack = ItemStack.from_nbt(nbt["camo_stack"])
        
        camo_state = None
        if nbt.get("camo_state"):
            state_data = nbt["camo_state"]
            camo_state = BlockState(
                block_id=state_data.get("Name", "minecraft:air"),
                properties=state_data.get("Properties", {})
            )
        
        return cls(
            pos=pos,
            shape=shape,
            camo_stack=camo_stack,
            camo_state=camo_state,
            glowing=nbt.get("glowing", False),
            intangible=nbt.get("intangible", False),
            reinforced=nbt.get("reinforced", False)
        )
    
    def get_light_level(self) -> int:
        """Zwraca poziom światła (0-15)"""
        if self.glowing:
            return 15
        # W rzeczywistości pobierane z camo_state
        return 0
    
    def __str__(self) -> str:
        camo_str = self.camo_state.to_string() if self.camo_state else "brak"
        return f"FramedBlockEntity({self.shape.value}, camo={camo_str})"


# Mapowanie mebli BiblioCraft na kształty FramedBlocks
BC_TO_FRAMED_MAP = {
    # Meble BC -> kształty FramedBlocks
    "FramedChest": FramedShape.CHEST,
    "FramedBookcase": FramedShape.BLOCK,  # Brak dedykowanego, używamy bloku
    "FramedShelf": FramedShape.SLAB,
    "FramedLabel": FramedShape.PANEL,
    "FramedTable": FramedShape.BLOCK,
    "FramedDesk": FramedShape.BLOCK,
    "FramedSeat": FramedShape.SLAB,
    "FramedSign": FramedShape.SIGN,
    "FramedDoor": FramedShape.DOOR,
    "FramedTrapDoor": FramedShape.TRAPDOOR,
    "FramedFence": FramedShape.FENCE,
    "FramedGate": FramedShape.GATE,
    "FramedButton": FramedShape.BUTTON,
    "FramedPressurePlate": FramedShape.PRESSURE_PLATE,
    "FramedLadder": FramedShape.LADDER,
    "FramedLever": FramedShape.LEVER,
    "FramedTorch": FramedShape.TORCH,
}

# Mapowanie tekstur drewna z 1.7.10 na 1.18.2
WOOD_TEXTURE_MAP = {
    # BC 1.7.10 -> Minecraft 1.18.2
    "minecraft:planks": "minecraft:oak_planks",
    "minecraft:planks:0": "minecraft:oak_planks",
    "minecraft:planks:1": "minecraft:spruce_planks",
    "minecraft:planks:2": "minecraft:birch_planks",
    "minecraft:planks:3": "minecraft:jungle_planks",
    "minecraft:planks:4": "minecraft:acacia_planks",
    "minecraft:planks:5": "minecraft:dark_oak_planks",
    # Dodatkowe bloki
    "minecraft:log": "minecraft:oak_log",
    "minecraft:log2": "minecraft:acacia_log",
    "minecraft:stone": "minecraft:stone",
    "minecraft:cobblestone": "minecraft:cobblestone",
    "minecraft:stonebrick": "minecraft:stone_bricks",
    "minecraft:brick_block": "minecraft:bricks",
    "minecraft:sandstone": "minecraft:sandstone",
    "minecraft:wool": "minecraft:white_wool",
}


class BiblioCraftFurnitureConverter:
    """
    Konwerter mebli BiblioCraft z systemem tekstur (Furniture Paneler)
    na FramedBlocks 1.18.2
    """
    
    def __init__(self):
        self.block_id_map = WOOD_TEXTURE_MAP
    
    def convert_texture_id(self, bc_texture: str) -> str:
        """
        Konwertuje ID tekstury z BC 1.7.10 na 1.18.2
        
        BC przechowywał teksturę jako String (np. "minecraft:planks:0")
        FramedBlocks używa BlockState (np. "minecraft:oak_planks")
        """
        if bc_texture in self.block_id_map:
            return self.block_id_map[bc_texture]
        
        # Jeśli nie ma w mapie, zwróć oryginał (może być już w formacie 1.18.2)
        return bc_texture
    
    def convert_framed_furniture(self, bc_block_id: str, bc_texture: str, 
                                  pos: Tuple[int, int, int]) -> FramedBlockEntity:
        """
        Konwertuje mebel BC z teksturą na FramedBlock
        
        Args:
            bc_block_id: np. "FramedChest", "FramedBookcase"
            bc_texture: np. "minecraft:planks:0" (oak)
            pos: pozycja (x, y, z)
        """
        print(f"\n[Konwersja BC -> FramedBlocks]")
        print(f"  BC block: {bc_block_id}")
        print(f"  BC texture: {bc_texture}")
        
        # 1. Mapuj kształt
        shape = BC_TO_FRAMED_MAP.get(bc_block_id, FramedShape.BLOCK)
        print(f"  -> FramedBlocks shape: {shape.value}")
        
        # 2. Konwertuj teksturę
        new_block_id = self.convert_texture_id(bc_texture)
        camo_state = BlockState(new_block_id)
        print(f"  -> Camo state: {camo_state.to_string()}")
        
        # 3. Utwórz ItemStack (w 1.18.2 potrzebny do prawidłowego zapisu)
        camo_stack = ItemStack(new_block_id, 1)
        
        # 4. Utwórz FramedBlockEntity
        framed_be = FramedBlockEntity(
            pos=pos,
            shape=shape
        )
        framed_be.set_camo(camo_stack, camo_state)
        
        return framed_be


def run_simulation():
    """Uruchamia symulację konwersji"""
    print("=" * 60)
    print("SYMULACJA: BiblioCraft -> FramedBlocks (1.18.2)")
    print("=" * 60)
    
    converter = BiblioCraftFurnitureConverter()
    
    # Scenariusz 1: Skrzynia z teksturą dębowych desek
    print("\n--- Scenariusz 1: FramedChest (oak) ---")
    chest = converter.convert_framed_furniture(
        bc_block_id="FramedChest",
        bc_texture="minecraft:planks:0",
        pos=(100, 64, 200)
    )
    print(f"  Wynik: {chest}")
    print(f"  NBT: {json.dumps(chest.to_nbt(), indent=2)}")
    
    # Scenariusz 2: Półka z teksturą świerkowych desek
    print("\n--- Scenariusz 2: FramedShelf (spruce) ---")
    shelf = converter.convert_framed_furniture(
        bc_block_id="FramedShelf",
        bc_texture="minecraft:planks:1",
        pos=(101, 64, 200)
    )
    print(f"  Wynik: {shelf}")
    
    # Scenariusz 3: Drzwi z teksturą brzozowych desek
    print("\n--- Scenariusz 3: FramedDoor (birch) ---")
    door = converter.convert_framed_furniture(
        bc_block_id="FramedDoor",
        bc_texture="minecraft:planks:2",
        pos=(102, 64, 200)
    )
    print(f"  Wynik: {door}")
    
    # Scenariusz 4: Blok z teksturą kamienia
    print("\n--- Scenariusz 4: FramedTable (stone) ---")
    table = converter.convert_framed_furniture(
        bc_block_id="FramedTable",
        bc_texture="minecraft:stone",
        pos=(103, 64, 200)
    )
    print(f"  Wynik: {table}")
    
    # Test odczytu/zapisu NBT
    print("\n--- Test round-trip (zapis -> odczyt NBT) ---")
    nbt_data = chest.to_nbt()
    restored = FramedBlockEntity.from_nbt(nbt_data, chest.pos)
    print(f"  Oryginał: {chest}")
    print(f"  Przywrócony: {restored}")
    print(f"  Zgodność: {chest.camo_state.to_string() == restored.camo_state.to_string()}")
    
    print("\n" + "=" * 60)
    print("Symulacja zakończona pomyślnie!")
    print("=" * 60)


if __name__ == "__main__":
    run_simulation()
