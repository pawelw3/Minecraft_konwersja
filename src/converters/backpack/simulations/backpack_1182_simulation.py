"""
Symulacja funkcjonalności Sophisticated Backpacks 1.18.2.

Bazuje na kodzie źródłowym z repozytoriów:
  - P3pp3rF1y/SophisticatedBackpacks (branch 1.18.x)
  - P3pp3rF1y/SophisticatedCore (branch 1.18.x)

Kluczowe klasy:
  - BackpackWrapper.java (NBT itemu, kolory, UUID)
  - BackpackStorage.java (SavedData: backpackContents)
  - InventoryHandler.java (format NBT inventory z SophisticatedCore)
  - UpgradeHandler.java (format NBT upgradeInventory z SophisticatedCore)
  - Config.java (domyślne sloty per tier)
  - ModItems.java (rejestracja itemów)

Symulacja pokazuje:
  1. Tworzenie itemu SB z tierem i kolorami
  2. Generowanie contentsUuid i zapis do BackpackStorage
  3. Format NBT inventory (ItemStackHandler z realCount)
  4. Format NBT upgradeInventory (Crafting Upgrade)
  5. Odczyt zawartości z BackpackStorage
"""

from __future__ import annotations

import json
import uuid as uuid_module
from dataclasses import dataclass, field
from typing import Any


# --- Stałe z BackpackWrapper.java ---
DEFAULT_CLOTH_COLOR = 13394234
DEFAULT_BORDER_COLOR = 6434330
CLOTH_COLOR_TAG = "clothColor"
BORDER_COLOR_TAG = "borderColor"
CONTENTS_UUID_TAG = "contentsUuid"
INVENTORY_SLOTS_TAG = "inventorySlots"
UPGRADE_SLOTS_TAG = "upgradeSlots"
SETTINGS_TAG = "settings"

# --- Stałe z InventoryHandler.java / UpgradeHandler.java ---
INVENTORY_TAG = "inventory"
UPGRADE_INVENTORY_TAG = "upgradeInventory"

# --- Domyślne sloty z Config.java ---
TIER_DEFAULTS = {
    "backpack": (27, 1),
    "copper_backpack": (45, 1),
    "iron_backpack": (54, 2),
    "gold_backpack": (81, 3),
    "diamond_backpack": (108, 5),
    "netherite_backpack": (120, 7),
}

# --- Kolory z Minecraft DyeColor (RGB int) ---
DYE_COLOR_RGB = {
    "white": 0xF9FFFE,
    "orange": 0xF9801D,
    "magenta": 0xC74EBD,
    "light_blue": 0x3AB3DA,
    "yellow": 0xFED83D,
    "lime": 0x80C71F,
    "pink": 0xF38BAA,
    "gray": 0x474F52,
    "light_gray": 0x9D9D97,
    "cyan": 0x169C9C,
    "purple": 0x8932B8,
    "blue": 0x3C44AA,
    "brown": 0x835432,
    "green": 0x5E7C16,
    "red": 0xB02E26,
    "black": 0x1D1D21,
}


def dye_color_to_rgb(dye_name: str) -> int:
    """Symuluje ColorHelper.getColor(DyeColor.getTextureDiffuseColors())."""
    return DYE_COLOR_RGB.get(dye_name, DEFAULT_CLOTH_COLOR)


def backpack_color_name_to_dye(color_name: str) -> str:
    """Mapowanie nazw kolorów z moda Eydamos na nazwy DyeColor vanilla."""
    mapping = {
        "black": "black",
        "red": "red",
        "green": "green",
        "brown": "brown",
        "blue": "blue",
        "purple": "purple",
        "cyan": "cyan",
        "lightGray": "light_gray",
        "gray": "gray",
        "pink": "pink",
        "lime": "lime",
        "yellow": "yellow",
        "lightBlue": "light_blue",
        "magenta": "magenta",
        "orange": "orange",
        "white": "white",
    }
    return mapping.get(color_name, "")


@dataclass
class ItemStack1182:
    """Reprezentacja ItemStack z NBT w formacie 1.18.2."""
    id: str
    count: int = 1
    tag: dict[str, Any] = field(default_factory=dict)

    def get_main_color(self) -> int:
        return self.tag.get(CLOTH_COLOR_TAG, DEFAULT_CLOTH_COLOR)

    def get_accent_color(self) -> int:
        return self.tag.get(BORDER_COLOR_TAG, DEFAULT_BORDER_COLOR)

    def get_contents_uuid(self) -> str | None:
        return self.tag.get(CONTENTS_UUID_TAG)

    def set_colors(self, cloth: int, border: int) -> None:
        self.tag[CLOTH_COLOR_TAG] = cloth
        self.tag[BORDER_COLOR_TAG] = border

    def set_contents_uuid(self, uid: str) -> None:
        self.tag[CONTENTS_UUID_TAG] = uid

    def set_inventory_slots(self, slots: int) -> None:
        self.tag[INVENTORY_SLOTS_TAG] = slots

    def set_upgrade_slots(self, slots: int) -> None:
        self.tag[UPGRADE_SLOTS_TAG] = slots


class BackpackStorage1182:
    """
    Symulacja net.p3pp3rf1y.sophisticatedbackpacks.backpack.BackpackStorage
    Przechowuje zawartość plecaków per UUID.
    """

    def __init__(self) -> None:
        self.backpack_contents: dict[str, dict] = {}

    def get_or_create_contents(self, backpack_uuid: str) -> dict:
        if backpack_uuid not in self.backpack_contents:
            self.backpack_contents[backpack_uuid] = {}
        return self.backpack_contents[backpack_uuid]

    def set_contents(self, backpack_uuid: str, contents: dict) -> None:
        self.backpack_contents[backpack_uuid] = contents

    def to_saved_data(self) -> dict:
        """Symuluje strukturę SavedData zapisanej do sophisticatedbackpacks.dat"""
        return {
            "backpackContents": [
                {
                    "uuid": uid,
                    "contents": contents,
                }
                for uid, contents in self.backpack_contents.items()
            ]
        }

    @classmethod
    def from_saved_data(cls, data: dict) -> BackpackStorage1182:
        inst = cls()
        for entry in data.get("backpackContents", []):
            uid = entry.get("uuid")
            contents = entry.get("contents", {})
            if uid:
                inst.backpack_contents[uid] = contents
        return inst


class BackpackWrapper1182:
    """
    Symulacja net.p3pp3rf1y.sophisticatedbackpacks.backpack.wrapper.BackpackWrapper
    """

    def __init__(self, stack: ItemStack1182, storage: BackpackStorage1182):
        self.stack = stack
        self.storage = storage
        self._ensure_contents_uuid()

    def _ensure_contents_uuid(self) -> None:
        """BackpackWrapper.getOrCreateContentsUuid()"""
        if CONTENTS_UUID_TAG not in self.stack.tag:
            new_uuid = str(uuid_module.uuid4())
            self.stack.set_contents_uuid(new_uuid)
            # migrateBackpackContents (puste przy nowym)

    def get_contents_uuid(self) -> str:
        return self.stack.tag[CONTENTS_UUID_TAG]

    def get_contents_nbt(self) -> dict:
        return self.storage.get_or_create_contents(self.get_contents_uuid())

    def set_inventory(self, items: list[dict]) -> None:
        """Symuluje zapis przez InventoryHandler (ItemStackHandler NBT)."""
        contents = self.get_contents_nbt()
        num_slots = self.stack.tag.get(INVENTORY_SLOTS_TAG, TIER_DEFAULTS.get(self.stack.id, (27, 1))[0])
        contents[INVENTORY_TAG] = {
            "Size": num_slots,
            "Items": items,
        }

    def set_upgrades(self, upgrades: list[dict]) -> None:
        """Symuluje zapis przez UpgradeHandler."""
        contents = self.get_contents_nbt()
        num_slots = self.stack.tag.get(UPGRADE_SLOTS_TAG, TIER_DEFAULTS.get(self.stack.id, (27, 1))[1])
        contents[UPGRADE_INVENTORY_TAG] = {
            "Size": num_slots,
            "Items": upgrades,
        }

    def set_settings(self, settings: dict) -> None:
        contents = self.get_contents_nbt()
        contents[SETTINGS_TAG] = settings

    def get_inventory(self) -> list[dict]:
        return self.get_contents_nbt().get(INVENTORY_TAG, {}).get("Items", [])

    def get_upgrades(self) -> list[dict]:
        return self.get_contents_nbt().get(UPGRADE_INVENTORY_TAG, {}).get("Items", [])


def create_backpack_item_1182(
    item_id: str = "sophisticatedbackpacks:backpack",
    color_name: str | None = None,
    custom_name: str | None = None,
) -> ItemStack1182:
    """Fabryka itemu plecaka 1.18.2 z NBT."""
    tag: dict[str, Any] = {}
    if custom_name:
        tag["display"] = {"Name": json.dumps({"text": custom_name})}

    stack = ItemStack1182(id=item_id, tag=tag)

    # Ustawienie kolorów (analogia do BackpackItem.fillItemCategory / setColors)
    if color_name:
        dye = backpack_color_name_to_dye(color_name)
        if dye:
            rgb = dye_color_to_rgb(dye)
            stack.set_colors(rgb, rgb)
        else:
            stack.set_colors(DEFAULT_CLOTH_COLOR, DEFAULT_BORDER_COLOR)
    else:
        stack.set_colors(DEFAULT_CLOTH_COLOR, DEFAULT_BORDER_COLOR)

    # Ustawienie domyślnych slotów z Config
    slots, upgrade_slots = TIER_DEFAULTS.get(item_id, (27, 1))
    stack.set_inventory_slots(slots)
    stack.set_upgrade_slots(upgrade_slots)

    return stack


def simulate_1182_leather_backpack_colored() -> None:
    print("=" * 60)
    print("SYMUlACJA 1.18.2: Leather Backpack (red)")
    print("=" * 60)

    storage = BackpackStorage1182()
    stack = create_backpack_item_1182(
        item_id="sophisticatedbackpacks:backpack",
        color_name="red",
        custom_name="Moje Rzeczy",
    )

    wrapper = BackpackWrapper1182(stack, storage)
    print(f"Item: id={stack.id}, tag={json.dumps(stack.tag, indent=2)}")
    print(f"  contentsUuid={wrapper.get_contents_uuid()}")

    # Symulacja inventory (format ItemStackHandler z realCount)
    inventory = [
        {"Slot": 0, "id": "minecraft:iron_ingot", "Count": 64, "realCount": 64},
        {"Slot": 1, "id": "minecraft:diamond", "Count": 16, "realCount": 16},
        {"Slot": 5, "id": "minecraft:stone", "Count": 32, "realCount": 32},
    ]
    wrapper.set_inventory(inventory)

    print(f"\nInventory w BackpackStorage:")
    print(json.dumps(wrapper.get_inventory(), indent=2))

    print(f"\nCały BackpackStorage (saved data format):")
    print(json.dumps(storage.to_saved_data(), indent=2))


def simulate_1182_iron_backpack_with_crafting_upgrade() -> None:
    print("\n" + "=" * 60)
    print("SYMUlACJA 1.18.2: Iron Backpack + Crafting Upgrade")
    print("=" * 60)

    storage = BackpackStorage1182()
    stack = create_backpack_item_1182(
        item_id="sophisticatedbackpacks:iron_backpack",
        color_name="blue",
    )

    wrapper = BackpackWrapper1182(stack, storage)
    print(f"Item: id={stack.id}, slots={stack.tag.get(INVENTORY_SLOTS_TAG)}, upgradeSlots={stack.tag.get(UPGRADE_SLOTS_TAG)}")

    # Inventory
    wrapper.set_inventory([
        {"Slot": 0, "id": "minecraft:cobblestone", "Count": 64, "realCount": 64},
    ])

    # Crafting upgrade w upgradeInventory
    wrapper.set_upgrades([
        {"Slot": 0, "id": "sophisticatedcore:crafting_upgrade", "Count": 1},
    ])

    print(f"\nUpgrades:")
    print(json.dumps(wrapper.get_upgrades(), indent=2))

    print(f"\nCały BackpackStorage:")
    print(json.dumps(storage.to_saved_data(), indent=2))


def simulate_1182_netherite_backpack() -> None:
    print("\n" + "=" * 60)
    print("SYMUlACJA 1.18.2: Netherite Backpack (default color)")
    print("=" * 60)

    storage = BackpackStorage1182()
    stack = create_backpack_item_1182(item_id="sophisticatedbackpacks:netherite_backpack")
    wrapper = BackpackWrapper1182(stack, storage)

    print(f"Item: id={stack.id}, slots={stack.tag.get(INVENTORY_SLOTS_TAG)}, upgradeSlots={stack.tag.get(UPGRADE_SLOTS_TAG)}")
    print(f"  contentsUuid={wrapper.get_contents_uuid()}")
    print(f"  clothColor={stack.get_main_color()} (default={DEFAULT_CLOTH_COLOR})")


def run_all_1182_simulations() -> None:
    simulate_1182_leather_backpack_colored()
    simulate_1182_iron_backpack_with_crafting_upgrade()
    simulate_1182_netherite_backpack()
    print("\n" + "=" * 60)
    print("Symulacje 1.18.2 zakończone.")
    print("=" * 60)


if __name__ == "__main__":
    run_all_1182_simulations()
