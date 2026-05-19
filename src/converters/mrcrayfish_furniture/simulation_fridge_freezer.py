# -*- coding: utf-8 -*-
"""
Symulacja wielobloku Fridge + Freezer — MrCrayfish Furniture Mod 1.7.10 vs 1.18.2

Pokazuje jak dziala wieloblok lodowki w obu wersjach:
- 1.7.10: BlockFridge (gora) + BlockFreezer (dol), TE: TileEntityFridge + TileEntityFreezer
  Freezer niszczy sie jesli nad nim nie ma Fridge.
  Fridge: 16 slotow, Freezer: IInventory (kompan)
- 1.18.2: FridgeBlock (gora) + FreezerBlock (dol), BE: FridgeBlockEntity + FreezerBlockEntity
  FreezerBlockEntity ma 3 sloty (source/fuel/result) + system zamrazania (FuelTime, FreezeTime)

Bazuje na kodzie zrodlowym:
- 1.7.10: BlockFridge.java, BlockFreezer.java, TileEntityFridge.java, TileEntityFreezer.java
- 1.18.2: FridgeBlock.java, FreezerBlock.java, FridgeBlockEntity.java, FreezerBlockEntity.java
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


@dataclass
class BlockPos:
    x: int
    y: int
    z: int

    def offset(self, dy: int) -> "BlockPos":
        return BlockPos(self.x, self.y + dy, self.z)

    def __str__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"


class ItemStack:
    """Uproszczona reprezentacja ItemStack"""
    def __init__(self, item_id: str = "", count: int = 1, nbt: Dict = None):
        self.item_id = item_id
        self.count = count
        self.nbt = nbt or {}

    def is_empty(self) -> bool:
        return self.item_id == "" or self.count <= 0

    def __str__(self) -> str:
        return f"{self.item_id} x{self.count}"


# ============================================================
# 1.7.10 — Wieloblok Fridge + Freezer
# ============================================================

class TileEntityFridge1710:
    """
    Symulacja TileEntityFridge z 1.7.10
    Inventory: 16 slotow (fridgeContents)
    Nie ma wlasnego systemu craftingu — tylko storage.
    """
    SIZE = 16

    def __init__(self):
        self.items: List[ItemStack] = [ItemStack() for _ in range(self.SIZE)]
        self.pos = BlockPos(0, 0, 0)

    def set_item(self, slot: int, item: ItemStack):
        if 0 <= slot < self.SIZE:
            self.items[slot] = item

    def write_to_nbt(self) -> Dict:
        nbt = {"id": "cfmFridge"}
        items_list = []
        for slot, item in enumerate(self.items):
            if not item.is_empty():
                items_list.append({
                    "id": item.item_id, "Count": item.count, "fridgeSlot": slot
                })
        nbt["fridgeItems"] = items_list
        return nbt


class TileEntityFreezer1710:
    """
    Symulacja TileEntityFreezer z 1.7.10
    Freezer to "kompan" lodowki — ma IInventory ale zalezy od Fridge nad soba.
    W oryginale: jesli nad Freezer nie ma Fridge, Freezer niszczy sie (breakBlock).
    Inventory: shared/companion (liczba slotow zalezy od implementacji, zazwyczaj podobna)
    """
    SIZE = 16  # W 1.7.10 Freezer tez ma inventory (kompan)

    def __init__(self):
        self.items: List[ItemStack] = [ItemStack() for _ in range(self.SIZE)]
        self.pos = BlockPos(0, 0, 0)

    def set_item(self, slot: int, item: ItemStack):
        if 0 <= slot < self.SIZE:
            self.items[slot] = item

    def write_to_nbt(self) -> Dict:
        nbt = {"id": "cfmFreezer"}
        # W 1.7.10 Freezer moze przechowywac itemy ale tez niszczy sie bez Fridge
        items_list = []
        for slot, item in enumerate(self.items):
            if not item.is_empty():
                items_list.append({
                    "id": item.item_id, "Count": item.count, "Slot": slot
                })
        if items_list:
            nbt["Items"] = items_list
        return nbt


class FridgeFreezerMultiblock1710:
    """
    Symulacja wielobloku Fridge+Freezer w 1.7.10
    Fridge (y+1) musi byc nad Freezer (y)
    """
    def __init__(self):
        self.fridge_te: Optional[TileEntityFridge1710] = None
        self.freezer_te: Optional[TileEntityFreezer1710] = None
        self.fridge_pos: Optional[BlockPos] = None
        self.freezer_pos: Optional[BlockPos] = None

    def place(self, freezer_pos: BlockPos):
        """Stawiamy Freezer na dole, Fridge automatycznie powinien byc nad nim"""
        self.freezer_pos = freezer_pos
        self.fridge_pos = freezer_pos.offset(1)
        self.freezer_te = TileEntityFreezer1710()
        self.freezer_te.pos = self.freezer_pos
        self.fridge_te = TileEntityFridge1710()
        self.fridge_te.pos = self.fridge_pos

    def validate(self) -> bool:
        """Sprawdza czy wieloblok jest prawidlowy (Fridge nad Freezer)"""
        return (self.fridge_te is not None and self.freezer_te is not None
                and self.fridge_pos.y == self.freezer_pos.y + 1)

    def on_freezer_break(self) -> List[ItemStack]:
        """Gdy Freezer jest niszczony — wysypuje itemy (z obu czesci!)"""
        drops = []
        if self.freezer_te:
            drops.extend([i for i in self.freezer_te.items if not i.is_empty()])
        if self.fridge_te:
            drops.extend([i for i in self.fridge_te.items if not i.is_empty()])
        self.freezer_te = None
        self.fridge_te = None
        return drops

    def get_total_inventory(self) -> List[ItemStack]:
        """Laczny inventory wielobloku"""
        items = []
        if self.fridge_te:
            items.extend(self.fridge_te.items)
        if self.freezer_te:
            items.extend(self.freezer_te.items)
        return items


# ============================================================
# 1.18.2 — Wieloblok Fridge + Freezer
# ============================================================

class FridgeBlockEntity1182:
    """
    Symulacja FridgeBlockEntity z 1.18.2
    Inventory: 27 slotow (ContainerHelper)
    """
    SIZE = 27

    def __init__(self):
        self.items: List[ItemStack] = [ItemStack() for _ in range(self.SIZE)]
        self.pos = BlockPos(0, 0, 0)

    def set_item(self, slot: int, item: ItemStack):
        if 0 <= slot < self.SIZE:
            self.items[slot] = item

    def write_to_nbt(self) -> Dict:
        nbt = {"id": "cfm:fridge"}
        items_list = []
        for slot, item in enumerate(self.items):
            if not item.is_empty():
                items_list.append({"id": item.item_id, "Count": item.count, "Slot": slot})
        nbt["Items"] = items_list
        return nbt


class FreezerBlockEntity1182:
    """
    Symulacja FreezerBlockEntity z 1.18.2
    FreezerBlockEntity ma 3-slotowy inventory (source, fuel, result)
    oraz system zamrazania:
    - FuelTime: pozostaly czas paliwa
    - FreezeTime: postep zamrazania
    - FreezeTimeTotal: calkowity czas zamrazania
    - RecipesUsed: mapa przepisow (do experience)

    Kod zrodlowy: FreezerBlockEntity.java
    """
    SIZE = 3

    def __init__(self):
        self.items: List[ItemStack] = [ItemStack() for _ in range(self.SIZE)]
        self.pos = BlockPos(0, 0, 0)
        self.freeze_time: int = 0
        self.freeze_time_total: int = 200  # ticks
        self.fuel_time: int = 0
        self.recipes_used: Dict[str, int] = {}

    def set_item(self, slot: int, item: ItemStack):
        if 0 <= slot < self.SIZE:
            self.items[slot] = item

    def tick(self):
        """Symulacja ticku FreezerBlockEntity"""
        if self.fuel_time > 0:
            self.fuel_time -= 1
            if not self.items[0].is_empty() and self.items[2].is_empty():
                # Slot 0 = source, Slot 1 = fuel, Slot 2 = result
                self.freeze_time += 1
                if self.freeze_time >= self.freeze_time_total:
                    self.freeze_time = 0
                    # Symulacja zamrozenia: zamien source na frozen variant
                    self.items[2] = ItemStack(f"frozen_{self.items[0].item_id}", self.items[0].count)
                    self.items[0] = ItemStack()
            else:
                self.freeze_time = 0
        else:
            self.freeze_time = 0

    def write_to_nbt(self) -> Dict:
        nbt = {"id": "cfm:freezer"}
        items_list = []
        for slot, item in enumerate(self.items):
            if not item.is_empty():
                items_list.append({"id": item.item_id, "Count": item.count, "Slot": slot})
        nbt["Items"] = items_list
        nbt["FreezeTime"] = self.freeze_time
        nbt["FreezeTimeTotal"] = self.freeze_time_total
        nbt["FuelTime"] = self.fuel_time
        if self.recipes_used:
            nbt["RecipesUsed"] = self.recipes_used
        return nbt


class FridgeFreezerMultiblock1182:
    """
    Symulacja wielobloku Fridge+Freezer w 1.18.2
    FridgeBlock (gora) + FreezerBlock (dol)
    FreezerBlockEntity ma funkcjonalnosc zamrazania!
    """
    def __init__(self):
        self.fridge_be: Optional[FridgeBlockEntity1182] = None
        self.freezer_be: Optional[FreezerBlockEntity1182] = None
        self.fridge_pos: Optional[BlockPos] = None
        self.freezer_pos: Optional[BlockPos] = None

    def place(self, freezer_pos: BlockPos):
        self.freezer_pos = freezer_pos
        self.fridge_pos = freezer_pos.offset(1)
        self.freezer_be = FreezerBlockEntity1182()
        self.freezer_be.pos = self.freezer_pos
        self.fridge_be = FridgeBlockEntity1182()
        self.fridge_be.pos = self.fridge_pos

    def validate(self) -> bool:
        return (self.fridge_be is not None and self.freezer_be is not None
                and self.fridge_pos.y == self.freezer_pos.y + 1)

    def tick(self):
        """Tickuje tylko Freezer (Fridge to tylko storage)"""
        if self.freezer_be:
            self.freezer_be.tick()

    def get_total_inventory(self) -> Tuple[List[ItemStack], List[ItemStack]]:
        """Zwraca (fridge_items, freezer_items)"""
        f_items = self.fridge_be.items if self.fridge_be else []
        z_items = self.freezer_be.items if self.freezer_be else []
        return f_items, z_items


# ============================================================
# Konwersja wielobloku 1.7.10 -> 1.18.2
# ============================================================

def convert_fridge_freezer(source: FridgeFreezerMultiblock1710) -> FridgeFreezerMultiblock1182:
    """
    Konwersja wielobloku Fridge+Freezer z 1.7.10 do 1.18.2

    Problemy konwersyjne:
    1. Fridge 1.7.10 ma 16 slotow, 1.18.2 ma 27 slotow -> itemy mieszcza sie
    2. Freezer 1.7.10 ma 16 slotow (storage), 1.18.2 ma 3 sloty (crafting)
       -> itemy z Freezer 1.7.10 NIE mieszcza sie w 3 slotach 1.18.2!
    3. Decyzja: itemy z Freezer 1.7.10 przenosimy do Fridge 1.18.2 (sloty 16-26)
       lub zrzucamy na ziemie jesli brak miejsca.
    """
    if not source.validate():
        raise ValueError("Invalid source multiblock")

    target = FridgeFreezerMultiblock1182()
    target.place(source.freezer_pos)

    # Konwersja Fridge inventory (16 -> 27 slotow, wszystko sie miesci)
    if source.fridge_te:
        for slot, item in enumerate(source.fridge_te.items):
            if not item.is_empty():
                target.fridge_be.set_item(slot, ItemStack(item.item_id, item.count, item.nbt))

    # Konwersja Freezer inventory (16 -> 3 sloty, OVERFLOW!)
    if source.freezer_te:
        freezer_items = [i for i in source.freezer_te.items if not i.is_empty()]
        # Sloty 0-2 w Freezer 1.18.2 to source/fuel/result — nie nadaja sie na storage
        # Przenosimy wszystko do Fridge (sloty 16+)
        overflow = []
        for slot, item in enumerate(freezer_items):
            fridge_slot = 16 + slot
            if fridge_slot < target.fridge_be.SIZE:
                target.fridge_be.set_item(fridge_slot, ItemStack(item.item_id, item.count, item.nbt))
            else:
                overflow.append(item)

    return target, overflow


# ============================================================
# Demonstracja / Testy
# ============================================================

def demo():
    print("=" * 60)
    print("Symulacja: Fridge + Freezer Multiblock")
    print("1.7.10 (storage-only) vs 1.18.2 (storage + freezing)")
    print("=" * 60)

    # --- 1.7.10 ---
    print("\n--- 1.7.10: Budowa wielobloku ---")
    m1710 = FridgeFreezerMultiblock1710()
    m1710.place(BlockPos(10, 64, 10))
    print(f"Fridge pos: {m1710.fridge_pos}")
    print(f"Freezer pos: {m1710.freezer_pos}")
    print(f"Valid: {m1710.validate()}")

    # Fridge: 16 slotow
    m1710.fridge_te.set_item(0, ItemStack("minecraft:beef", 8))
    m1710.fridge_te.set_item(5, ItemStack("minecraft:chicken", 4))
    # Freezer: 16 slotow (w 1.7.10 to tez storage!)
    m1710.freezer_te.set_item(0, ItemStack("minecraft:water_bucket", 1))
    m1710.freezer_te.set_item(3, ItemStack("minecraft:ice", 32))
    m1710.freezer_te.set_item(7, ItemStack("minecraft:snowball", 16))

    print(f"\nFridge inventory ({m1710.fridge_te.SIZE} slots):")
    for i, item in enumerate(m1710.fridge_te.items):
        if not item.is_empty():
            print(f"  slot {i}: {item}")
    print(f"\nFreezer inventory ({m1710.freezer_te.SIZE} slots):")
    for i, item in enumerate(m1710.freezer_te.items):
        if not item.is_empty():
            print(f"  slot {i}: {item}")

    # --- Konwersja ---
    print("\n--- KONWERSJA 1.7.10 -> 1.18.2 ---")
    m1182, overflow = convert_fridge_freezer(m1710)
    print(f"Converted multiblock valid: {m1182.validate()}")

    f_items, z_items = m1182.get_total_inventory()
    print(f"\n1.18.2 Fridge inventory ({len(f_items)} slots):")
    for i, item in enumerate(f_items):
        if not item.is_empty():
            print(f"  slot {i}: {item}")
    print(f"\n1.18.2 Freezer inventory ({len(z_items)} slots) — crafting slots:")
    for i, item in enumerate(z_items):
        if not item.is_empty():
            print(f"  slot {i}: {item}")
    print(f"\nOverflow items (dropped): {len(overflow)}")
    for item in overflow:
        print(f"  DROPPED: {item}")

    # --- 1.18.2 tick simulation ---
    print("\n--- 1.18.2: Symulacja zamrazania ---")
    m1182.freezer_be.set_item(0, ItemStack("minecraft:water_bucket", 1))  # source
    m1182.freezer_be.set_item(1, ItemStack("minecraft:coal", 1))          # fuel
    m1182.freezer_be.fuel_time = 200
    m1182.freezer_be.freeze_time_total = 100

    print("Before tick:")
    print(f"  source: {m1182.freezer_be.items[0]}")
    print(f"  fuel: {m1182.freezer_be.items[1]}")
    print(f"  result: {m1182.freezer_be.items[2]}")
    print(f"  FreezeTime: {m1182.freezer_be.freeze_time}/{m1182.freezer_be.freeze_time_total}")

    for _ in range(100):
        m1182.tick()

    print("\nAfter 100 ticks:")
    print(f"  source: {m1182.freezer_be.items[0]}")
    print(f"  fuel: {m1182.freezer_be.items[1]}")
    print(f"  result: {m1182.freezer_be.items[2]}")
    print(f"  FreezeTime: {m1182.freezer_be.freeze_time}/{m1182.freezer_be.freeze_time_total}")

    print("\n" + "=" * 60)
    print("Symulacja zakonczona pomyslnie.")
    print("=" * 60)


if __name__ == "__main__":
    demo()
