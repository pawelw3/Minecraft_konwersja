# -*- coding: utf-8 -*-
"""
Symulacja systemow inventory MrCrayfish Furniture Mod — 1.7.10 vs 1.18.2

Pokazuje roznice w formacie NBT inventory miedzy wersjami:
- 1.7.10: Custom nazwy list (fridgeItems, cabinetItems) z custom slot tagami (fridgeSlot)
- 1.18.2: Standardowy Items list ze slotami 0-N (ContainerHelper / Minecraft standard)

Bazuje na kodzie zrodlowym:
- 1.7.10: TileEntityFridge.java, TileEntityCabinet.java, TileEntityMailBox.java
- 1.18.2: FridgeBlockEntity.java, CabinetBlockEntity.java, MailBoxBlockEntity.java
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import uuid
import struct


@dataclass
class ItemStack1710:
    """Reprezentacja ItemStack z Minecraft 1.7.10"""
    item_id: str
    damage: int = 0
    count: int = 1
    nbt: Dict = field(default_factory=dict)

    def to_nbt_1710(self, slot_tag: str, slot: int) -> Dict:
        """Format NBT uzywany w 1.7.10 (custom slot tag)"""
        result = {
            "id": self.item_id,
            "Damage": self.damage,
            "Count": self.count,
            slot_tag: slot
        }
        if self.nbt:
            result["tag"] = self.nbt
        return result

    @classmethod
    def from_nbt_1710(cls, nbt: Dict, slot_tag: str) -> tuple:
        """Wczytuje ItemStack z NBT 1.7.10, zwraca (slot, ItemStack)"""
        slot = nbt.get(slot_tag, 0)
        return slot, cls(
            item_id=nbt.get("id", ""),
            damage=nbt.get("Damage", 0),
            count=nbt.get("Count", 1),
            nbt=nbt.get("tag", {})
        )

    def is_empty(self) -> bool:
        return self.item_id == "" or self.count <= 0

    def __str__(self) -> str:
        return f"{self.item_id}:{self.damage} x{self.count}"


@dataclass
class ItemStack1182:
    """Reprezentacja ItemStack z Minecraft 1.18.2"""
    item_id: str
    count: int = 1
    nbt: Dict = field(default_factory=dict)

    def to_nbt_1182(self, slot: int) -> Dict:
        """Standardowy format NBT 1.18.2 (Slot tag)"""
        result = {
            "id": self.item_id,
            "Count": self.count,
            "Slot": slot
        }
        if self.nbt:
            result["tag"] = self.nbt
        return result

    @classmethod
    def from_nbt_1182(cls, nbt: Dict) -> tuple:
        """Wczytuje ItemStack z NBT 1.18.2, zwraca (slot, ItemStack)"""
        slot = nbt.get("Slot", 0)
        return slot, cls(
            item_id=nbt.get("id", ""),
            count=nbt.get("Count", 1),
            nbt=nbt.get("tag", {})
        )

    def is_empty(self) -> bool:
        return self.item_id == "" or self.count <= 0

    def __str__(self) -> str:
        return f"{self.item_id} x{self.count}"


class ContainerHelper1182:
    """
    Symulacja ContainerHelper z 1.18.2
    Uzywany przez: CabinetBlockEntity, FridgeBlockEntity, MailBoxBlockEntity, etc.
    """

    @staticmethod
    def save_all_items(nbt: Dict, items: List[ItemStack1182], tag_name: str = "Items") -> Dict:
        items_list = []
        for slot, item in enumerate(items):
            if not item.is_empty():
                items_list.append(item.to_nbt_1182(slot))
        nbt[tag_name] = items_list
        return nbt

    @staticmethod
    def load_all_items(nbt: Dict, container_size: int, tag_name: str = "Items") -> List[ItemStack1182]:
        items = [ItemStack1182("") for _ in range(container_size)]
        for item_nbt in nbt.get(tag_name, []):
            slot, item = ItemStack1182.from_nbt_1182(item_nbt)
            if 0 <= slot < container_size:
                items[slot] = item
        return items


# ============================================================
# 1.7.10 — Tile Entities z custom inventory NBT
# ============================================================

class TileEntityFridge1710:
    """
    Symulacja TileEntityFridge z 1.7.10
    Kod: TileEntityFridge.java — fridgeContents[16], NBT: fridgeItems z fridgeSlot
    """
    SIZE = 16

    def __init__(self):
        self.items = [ItemStack1710("") for _ in range(self.SIZE)]

    def set_item(self, slot: int, item: ItemStack1710):
        if 0 <= slot < self.SIZE:
            self.items[slot] = item

    def write_to_nbt(self) -> Dict:
        nbt = {}
        items_list = []
        for slot, item in enumerate(self.items):
            if not item.is_empty():
                items_list.append(item.to_nbt_1710("fridgeSlot", slot))
        nbt["fridgeItems"] = items_list
        return nbt

    def read_from_nbt(self, nbt: Dict):
        self.items = [ItemStack1710("") for _ in range(self.SIZE)]
        for item_nbt in nbt.get("fridgeItems", []):
            slot, item = ItemStack1710.from_nbt_1710(item_nbt, "fridgeSlot")
            if 0 <= slot < self.SIZE:
                self.items[slot] = item

    def set_item(self, slot: int, item: ItemStack1710):
        if 0 <= slot < self.SIZE:
            self.items[slot] = item


class TileEntityCabinet1710:
    """
    Symulacja TileEntityCabinet z 1.7.10
    Kod: TileEntityCabinet.java — cabinetContents[16], NBT: cabinetItems z cabinetSlot
    """
    SIZE = 16

    def __init__(self):
        self.items = [ItemStack1710("") for _ in range(self.SIZE)]

    def set_item(self, slot: int, item: ItemStack1710):
        if 0 <= slot < self.SIZE:
            self.items[slot] = item

    def write_to_nbt(self) -> Dict:
        nbt = {}
        items_list = []
        for slot, item in enumerate(self.items):
            if not item.is_empty():
                items_list.append(item.to_nbt_1710("cabinetSlot", slot))
        nbt["cabinetItems"] = items_list
        return nbt

    def read_from_nbt(self, nbt: Dict):
        self.items = [ItemStack1710("") for _ in range(self.SIZE)]
        for item_nbt in nbt.get("cabinetItems", []):
            slot, item = ItemStack1710.from_nbt_1710(item_nbt, "cabinetSlot")
            if 0 <= slot < self.SIZE:
                self.items[slot] = item


class TileEntityMailBox1710:
    """
    Symulacja TileEntityMailBox z 1.7.10
    Kod: TileEntityMailBox.java — mailBoxContents[6], NBT: mailBoxItems z mailBoxSlot
    Dodatkowe pola: OwnerUUID (string), OwnerName (string), Locked (boolean)
    """
    SIZE = 6

    def __init__(self):
        self.items = [ItemStack1710("") for _ in range(self.SIZE)]
        self.owner_uuid: Optional[str] = None
        self.owner_name: str = ""
        self.locked: bool = False

    def set_item(self, slot: int, item: ItemStack1710):
        if 0 <= slot < self.SIZE:
            self.items[slot] = item

    def write_to_nbt(self) -> Dict:
        nbt = {}
        items_list = []
        for slot, item in enumerate(self.items):
            if not item.is_empty():
                items_list.append(item.to_nbt_1710("mailBoxSlot", slot))
        nbt["mailBoxItems"] = items_list
        if self.owner_uuid:
            nbt["OwnerUUID"] = self.owner_uuid
        nbt["OwnerName"] = self.owner_name
        nbt["Locked"] = int(self.locked)
        return nbt

    def read_from_nbt(self, nbt: Dict):
        self.items = [ItemStack1710("") for _ in range(self.SIZE)]
        for item_nbt in nbt.get("mailBoxItems", []):
            slot, item = ItemStack1710.from_nbt_1710(item_nbt, "mailBoxSlot")
            if 0 <= slot < self.SIZE:
                self.items[slot] = item
        self.owner_uuid = nbt.get("OwnerUUID")
        self.owner_name = nbt.get("OwnerName", "")
        self.locked = bool(nbt.get("Locked", 0))


# ============================================================
# 1.18.2 — Block Entities ze standardowym inventory NBT
# ============================================================

class FridgeBlockEntity1182:
    """
    Symulacja FridgeBlockEntity z 1.18.2
    Kod: FridgeBlockEntity.java — 27 slotow, standardowy Items list
    """
    SIZE = 27

    def __init__(self):
        self.items = [ItemStack1182("") for _ in range(self.SIZE)]

    def write_to_nbt(self) -> Dict:
        nbt = {}
        return ContainerHelper1182.save_all_items(nbt, self.items, "Items")

    def read_from_nbt(self, nbt: Dict):
        self.items = ContainerHelper1182.load_all_items(nbt, self.SIZE, "Items")


class CabinetBlockEntity1182:
    """
    Symulacja CabinetBlockEntity z 1.18.2
    Kod: CabinetBlockEntity.java — 18 slotow, standardowy Items list
    """
    SIZE = 18

    def __init__(self):
        self.items = [ItemStack1182("") for _ in range(self.SIZE)]

    def write_to_nbt(self) -> Dict:
        nbt = {}
        return ContainerHelper1182.save_all_items(nbt, self.items, "Items")

    def read_from_nbt(self, nbt: Dict):
        self.items = ContainerHelper1182.load_all_items(nbt, self.SIZE, "Items")


class MailBoxBlockEntity1182:
    """
    Symulacja MailBoxBlockEntity z 1.18.2
    Kod: MailBoxBlockEntity.java — 9 slotow, standardowy Items list
    Dodatkowe pola: MailBoxUUID, MailBoxName, OwnerName, OwnerUUID (int-array)
    """
    SIZE = 9

    def __init__(self):
        self.items = [ItemStack1182("") for _ in range(self.SIZE)]
        self.mail_box_uuid: Optional[str] = None
        self.mail_box_name: str = ""
        self.owner_name: str = ""
        self.owner_uuid: Optional[List[int]] = None  # int-array format

    def write_to_nbt(self) -> Dict:
        nbt = ContainerHelper1182.save_all_items({}, self.items, "Items")
        if self.mail_box_uuid:
            nbt["MailBoxUUID"] = self.mail_box_uuid
        nbt["MailBoxName"] = self.mail_box_name
        nbt["OwnerName"] = self.owner_name
        if self.owner_uuid:
            nbt["OwnerUUID"] = self.owner_uuid
        return nbt

    def read_from_nbt(self, nbt: Dict):
        self.items = ContainerHelper1182.load_all_items(nbt, self.SIZE, "Items")
        self.mail_box_uuid = nbt.get("MailBoxUUID")
        self.mail_box_name = nbt.get("MailBoxName", "")
        self.owner_name = nbt.get("OwnerName", "")
        self.owner_uuid = nbt.get("OwnerUUID")


# ============================================================
# Konwertery inventory
# ============================================================

def convert_item_1710_to_1182(item: ItemStack1710) -> ItemStack1182:
    """
    Konwersja ItemStack 1.7.10 -> 1.18.2
    - Usuwa Damage (w 1.18.2 item_id zawiera juz variant, np. minecraft:stone_bricks)
    - Zachowuje count i NBT
    """
    # W 1.18.2 wiele itemow z damage zostalo rozdzielony na osobne ID
    # W pelnym konwerterze nalezy uzyc mapowania damage -> item_id
    item_id = item.item_id
    if item.damage != 0 and ":" not in item.item_id:
        # Prosta heurystyka: w niektorych przypadkach damage jest metadata
        # W pelnym kodzie nalezy uzyc globalnego mappera
        pass
    return ItemStack1182(
        item_id=item_id,
        count=item.count,
        nbt=item.nbt.copy()
    )


def convert_uuid_string_to_int_array(uuid_str: str) -> List[int]:
    """
    Konwersja UUID string (1.7.10) -> int[4] array (1.18.2)
    Format int-array uzywany od Minecraft 1.16+
    """
    u = uuid.UUID(uuid_str)
    # Rozbijamy na 4 x 32-bit int
    msb = u.int >> 64
    lsb = u.int & 0xFFFFFFFFFFFFFFFF
    return [
        (msb >> 32) & 0xFFFFFFFF,
        msb & 0xFFFFFFFF,
        (lsb >> 32) & 0xFFFFFFFF,
        lsb & 0xFFFFFFFF
    ]


def convert_uuid_int_array_to_string(int_array: List[int]) -> str:
    """Konwersja int[4] array -> UUID string"""
    msb = (int_array[0] << 32) | int_array[1]
    lsb = (int_array[2] << 32) | int_array[3]
    u = uuid.UUID(int=(msb << 64) | lsb)
    return str(u)


class InventoryConverter:
    """
    Glowny konwerter inventory dla MrCrayfish Furniture Mod
    Obsluguje konwersje miedzy custom NBT 1.7.10 a standardowym NBT 1.18.2
    """

    @staticmethod
    def convert_fridge(source: TileEntityFridge1710) -> FridgeBlockEntity1182:
        target = FridgeBlockEntity1182()
        for slot, item in enumerate(source.items):
            if slot < target.SIZE and not item.is_empty():
                target.items[slot] = convert_item_1710_to_1182(item)
        # Sloty 16-26 pozostaja puste (1.18.2 ma wiecej miejsca)
        return target

    @staticmethod
    def convert_cabinet(source: TileEntityCabinet1710) -> CabinetBlockEntity1182:
        target = CabinetBlockEntity1182()
        for slot, item in enumerate(source.items):
            if slot < target.SIZE and not item.is_empty():
                target.items[slot] = convert_item_1710_to_1182(item)
        return target

    @staticmethod
    def convert_mailbox(source: TileEntityMailBox1710) -> MailBoxBlockEntity1182:
        target = MailBoxBlockEntity1182()
        for slot, item in enumerate(source.items):
            if slot < target.SIZE and not item.is_empty():
                target.items[slot] = convert_item_1710_to_1182(item)
        # Itemy z slotow 6-8 (jesli bylyby) — zrzucamy (6 slotow -> 9, brak overflow)

        target.owner_name = source.owner_name
        if source.owner_uuid:
            target.owner_uuid = convert_uuid_string_to_int_array(source.owner_uuid)
        # Generujemy nowe MailBoxUUID
        target.mail_box_uuid = str(uuid.uuid4())
        target.mail_box_name = source.owner_name or "Mailbox"
        return target


# ============================================================
# Demonstracja / Testy
# ============================================================

def demo():
    print("=" * 60)
    print("Symulacja: Inventory Systems — MrCrayfish Furniture Mod")
    print("1.7.10 (custom NBT) vs 1.18.2 (ContainerHelper standard)")
    print("=" * 60)

    # --- Fridge ---
    print("\n--- FRIDGE ---")
    fridge_1710 = TileEntityFridge1710()
    fridge_1710.set_item(0, ItemStack1710("minecraft:apple", 0, 16))
    fridge_1710.set_item(3, ItemStack1710("minecraft:cooked_porkchop", 0, 8))
    fridge_1710.set_item(15, ItemStack1710("minecraft:melon", 0, 32))

    nbt_1710 = fridge_1710.write_to_nbt()
    print(f"1.7.10 NBT keys: {list(nbt_1710.keys())}")
    print(f"1.7.10 fridgeItems count: {len(nbt_1710['fridgeItems'])}")
    print(f"1.7.10 sample item: {nbt_1710['fridgeItems'][0]}")

    fridge_1182 = InventoryConverter.convert_fridge(fridge_1710)
    nbt_1182 = fridge_1182.write_to_nbt()
    print(f"\n1.18.2 NBT keys: {list(nbt_1182.keys())}")
    print(f"1.18.2 Items count: {len(nbt_1182['Items'])}")
    print(f"1.18.2 sample item: {nbt_1182['Items'][0]}")
    print(f"1.18.2 container size: {fridge_1182.SIZE} (was {fridge_1710.SIZE})")

    # --- MailBox ---
    print("\n--- MAILBOX ---")
    mb_1710 = TileEntityMailBox1710()
    mb_1710.set_item(0, ItemStack1710("minecraft:diamond", 0, 1))
    mb_1710.set_item(2, ItemStack1710("minecraft:emerald", 0, 5))
    mb_1710.owner_uuid = "550e8400-e29b-41d4-a716-446655440000"
    mb_1710.owner_name = "Steve"
    mb_1710.locked = True

    nbt_mb_1710 = mb_1710.write_to_nbt()
    print(f"1.7.10 NBT: { {k: v for k, v in nbt_mb_1710.items() if k != 'mailBoxItems'} }")
    print(f"1.7.10 OwnerUUID (string): {nbt_mb_1710['OwnerUUID']}")

    mb_1182 = InventoryConverter.convert_mailbox(mb_1710)
    nbt_mb_1182 = mb_1182.write_to_nbt()
    print(f"\n1.18.2 NBT keys: {list(nbt_mb_1182.keys())}")
    print(f"1.18.2 OwnerUUID (int-array): {nbt_mb_1182['OwnerUUID']}")
    print(f"1.18.2 MailBoxUUID (new): {nbt_mb_1182['MailBoxUUID']}")
    print(f"1.18.2 container size: {mb_1182.SIZE} (was {mb_1710.SIZE})")

    # --- Cabinet ---
    print("\n--- CABINET ---")
    cab_1710 = TileEntityCabinet1710()
    cab_1710.set_item(0, ItemStack1710("minecraft:book", 0, 3))
    nbt_cab_1710 = cab_1710.write_to_nbt()
    print(f"1.7.10 NBT keys: {list(nbt_cab_1710.keys())}")
    print(f"1.7.10 cabinetItems sample slot tag: 'cabinetSlot'")

    cab_1182 = InventoryConverter.convert_cabinet(cab_1710)
    nbt_cab_1182 = cab_1182.write_to_nbt()
    print(f"1.18.2 NBT keys: {list(nbt_cab_1182.keys())}")
    print(f"1.18.2 Items sample slot tag: 'Slot'")
    print(f"1.18.2 container size: {cab_1182.SIZE} (was {cab_1710.SIZE})")

    print("\n" + "=" * 60)
    print("Symulacja zakonczona pomyslnie.")
    print("=" * 60)


if __name__ == "__main__":
    demo()
