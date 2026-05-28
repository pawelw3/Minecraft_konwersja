"""
Symulacja funkcjonalności moda Backpack (Eydamos) 1.7.10.

Bazuje na dekompilacji JAR backpack-2.0.1-1.7.x.jar (CFR 0.152).
Kluczowe klasy:
  - BackpackSave.java (zapis/odczyt pliku .dat)
  - ItemBackpackBase.java (NBT itemu, damage/meta)
  - ItemsBackpack.java (tablice tierów i kolorów)
  - BackpackUtil.java (typy, UUID)

Symulacja pokazuje:
  1. Tworzenie itemu plecaka z damage/meta
  2. Inicjalizacja BackpackSave (generowanie UUID, rozmiar)
  3. Zapis inventory do pliku .dat
  4. Odczyt inventory z pliku .dat
"""

from __future__ import annotations

import json
import uuid as uuid_module
from dataclasses import dataclass, field
from typing import Any


# --- Stałe z ItemsBackpack.java ---
BACKPACK_TIERS = ["", "medium", "big"]
BACKPACK_COLORS = [
    "", "black", "red", "green", "brown", "blue", "purple", "cyan",
    "lightGray", "gray", "pink", "lime", "yellow", "lightBlue", "magenta",
    "orange", "white", "ender",
]
ENDERBACKPACK_DAMAGE = 31999

# --- Domyślne wartości z ConfigurationBackpack.java ---
DEFAULT_SLOTS_S = 27
DEFAULT_SLOTS_L = 54


@dataclass
class ItemStack1710:
    """Reprezentacja ItemStack z NBT w formacie 1.7.10."""
    id: str
    damage: int
    count: int = 1
    tag: dict[str, Any] = field(default_factory=dict)

    def get_tier(self) -> int:
        tier = self.damage // 100
        return tier if tier < 3 else 0

    def get_meta(self) -> int:
        return self.damage % 100

    def is_ender(self) -> bool:
        return self.damage == ENDERBACKPACK_DAMAGE or self.get_meta() == 99

    def is_workbench(self) -> bool:
        return self.get_meta() == 17

    def get_color_name(self) -> str:
        meta = self.get_meta()
        if 0 <= meta <= 17:
            return BACKPACK_COLORS[meta]
        return ""

    def get_tier_name(self) -> str:
        tier = self.get_tier()
        if 0 <= tier <= 2:
            return BACKPACK_TIERS[tier]
        return ""


class BackpackSave1710:
    """
    Symulacja de.eydamos.backpack.saves.BackpackSave
    Odpowiada za zawartość pliku <world>/backpacks/backpacks/<UUID>.dat
    """

    def __init__(self, backpack_item: ItemStack1710, force_init: bool = False):
        self.item = backpack_item
        self.nbt: dict[str, Any] = {}
        self.uid: str | None = None

        # Logika z BackpackSave.__init__ (ItemStack backpack, boolean force)
        if "backpack-UID" not in backpack_item.tag:
            self._initialize()
        elif backpack_item.id in ("Backpack:backpack", "Backpack:workbenchbackpack"):
            self.uid = backpack_item.tag.get("backpack-UID")
            if force_init:
                self._initialize()

    def _initialize(self) -> None:
        """BackpackSave.initialize(ItemStack backpack)"""
        self.uid = str(uuid_module.uuid4())
        self.item.tag["name"] = self._compute_default_name()
        self.item.tag["backpack-UID"] = self.uid

        damage = self.item.damage
        tier = damage // 100 if damage // 100 < 3 else 0
        meta = damage % 100

        # Obliczenie rozmiaru (BackpackSave.java:64-77)
        size = self._compute_size(tier, meta)

        self.nbt = {
            "backpack-UID": self.uid,
            "size": size,
            "slotsPerRow": 9,
            "type": self._compute_type(),
            "backpackInventories": {
                "backpack": [],  # NBTTagList type 10
            },
        }

    def _compute_default_name(self) -> str:
        # ItemBackpackBase.func_77667_c + ".name"
        # Uproszczona wersja
        tier_name = self.item.get_tier_name()
        color_name = self.item.get_color_name()
        base = "item.backpack"
        if self.item.id == "Backpack:workbenchbackpack":
            base = "item.workbenchbackpack"
        parts = [base]
        if tier_name:
            parts.append(tier_name)
        if color_name:
            sep = "_" if tier_name else "."
            parts.append(f"{sep}{color_name}")
        return "".join(parts) + ".name"

    def _compute_size(self, tier: int, meta: int) -> int:
        if meta == 99:
            return 27
        elif meta < 17 and tier == 2:
            return DEFAULT_SLOTS_L
        elif meta < 17 and tier == 0:
            return DEFAULT_SLOTS_S
        elif meta == 17 and tier == 0:
            return 9
        elif meta == 17 and tier == 2:
            return 18
        return DEFAULT_SLOTS_S

    def _compute_type(self) -> int:
        # BackpackUtil.getType(ItemStack)
        if self.item.id == "Backpack:backpack":
            return 1
        if self.item.id == "Backpack:workbenchbackpack":
            return 2
        return 0

    def set_intelligent(self) -> None:
        """BackpackSave.setIntelligent()"""
        self.nbt["intelligent"] = True

    def get_inventory(self) -> list[dict]:
        """BackpackSave.getInventory('backpack')"""
        return list(self.nbt.get("backpackInventories", {}).get("backpack", []))

    def set_inventory(self, items: list[dict]) -> None:
        """BackpackSave.setInventory('backpack', NBTTagList)"""
        if "backpackInventories" not in self.nbt:
            self.nbt["backpackInventories"] = {}
        self.nbt["backpackInventories"]["backpack"] = items

    def to_dat_file(self) -> dict:
        """Symuluje zawartość pliku .dat (CompressedStreamTools.write)"""
        return dict(self.nbt)

    @classmethod
    def from_dat_file(cls, data: dict, item: ItemStack1710) -> BackpackSave1710:
        """Symuluje odczyt z pliku .dat"""
        inst = cls.__new__(cls)
        inst.item = item
        inst.nbt = dict(data)
        inst.uid = data.get("backpack-UID")
        if inst.uid and "backpack-UID" not in item.tag:
            item.tag["backpack-UID"] = inst.uid
        return inst


def create_backpack_item_1710(
    item_id: str = "Backpack:backpack",
    damage: int = 0,
    custom_name: str | None = None,
) -> ItemStack1710:
    """Fabryka itemu plecaka 1.7.10 z NBT."""
    tag: dict[str, Any] = {}
    if custom_name:
        tag["customName"] = custom_name
    return ItemStack1710(id=item_id, damage=damage, tag=tag)


def simulate_1710_small_red_backpack() -> None:
    print("=" * 60)
    print("SYMUlACJA 1.7.10: Small Red Backpack (damage=1)")
    print("=" * 60)

    item = create_backpack_item_1710(damage=1, custom_name="Moje Rzeczy")
    print(f"Item: id={item.id}, damage={item.damage}, tag={json.dumps(item.tag, indent=2)}")
    print(f"  tier={item.get_tier()}, meta={item.get_meta()}, color={item.get_color_name()}")

    save = BackpackSave1710(item)
    print(f"\nPo inicjalizacji BackpackSave:")
    print(f"  UUID={save.uid}")
    print(f"  NBT={json.dumps(save.nbt, indent=2)}")

    # Symulacja włożenia itemów
    inventory = [
        {"Slot": 0, "id": 265, "Count": 64, "Damage": 0},   # iron_ingot
        {"Slot": 1, "id": 264, "Count": 16, "Damage": 0},   # diamond
        {"Slot": 5, "id": 1, "Count": 32, "Damage": 0},     # stone
    ]
    save.set_inventory(inventory)

    print(f"\nPo dodaniu itemów:")
    print(f"  Inventory={json.dumps(save.get_inventory(), indent=2)}")

    # Symulacja zapisu do .dat
    dat_content = save.to_dat_file()
    print(f"\nZawartość pliku .dat (symulacja):")
    print(json.dumps(dat_content, indent=2))


def simulate_1710_big_workbench_backpack() -> None:
    print("\n" + "=" * 60)
    print("SYMUlACJA 1.7.10: Big Workbench Backpack (damage=217)")
    print("=" * 60)

    item = create_backpack_item_1710(item_id="Backpack:workbenchbackpack", damage=217)
    print(f"Item: id={item.id}, damage={item.damage}")
    print(f"  tier={item.get_tier()}, meta={item.get_meta()}, workbench={item.is_workbench()}")

    save = BackpackSave1710(item)
    save.set_intelligent()
    print(f"\nPo inicjalizacji:")
    print(f"  UUID={save.uid}")
    print(f"  NBT={json.dumps(save.nbt, indent=2)}")


def simulate_1710_ender_backpack() -> None:
    print("\n" + "=" * 60)
    print("SYMUlACJA 1.7.10: Ender Backpack (damage=31999)")
    print("=" * 60)

    item = create_backpack_item_1710(damage=31999)
    print(f"Item: id={item.id}, damage={item.damage}, ender={item.is_ender()}")

    save = BackpackSave1710(item)
    print(f"\nPo inicjalizacji:")
    print(f"  UUID={save.uid}")
    print(f"  size={save.nbt.get('size')} (zawsze 27 dla ender)")
    print(f"  NBT={json.dumps(save.nbt, indent=2)}")


def run_all_1710_simulations() -> None:
    simulate_1710_small_red_backpack()
    simulate_1710_big_workbench_backpack()
    simulate_1710_ender_backpack()
    print("\n" + "=" * 60)
    print("Symulacje 1.7.10 zakończone.")
    print("=" * 60)


if __name__ == "__main__":
    run_all_1710_simulations()
