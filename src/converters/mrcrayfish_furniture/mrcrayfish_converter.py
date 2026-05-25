# -*- coding: utf-8 -*-
"""
Konwerter MrCrayfish Furniture Mod 1.7.10 -> 1.18.2

Produkuje ConversionEvent per blok / tile entity.
Zgodny z ogolnym handlerem wstawiajacym dane na podkladowa mape vanilla 1.18.2.

Bazuje na analizie z ANALIZA_BLOKOW_TE_ZADANIE1.md oraz symulacjach z Zadania 2.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from converters.common.conversion_event import ConversionEvent
from converters.common.inventory_helpers import (
    convert_inventory_1710_to_1182,
    extract_items_from_legacy_nbt,
)
from converters.common.uuid_helpers import uuid_string_to_int_array
from converters.common.placeholders import make_block_entity_placeholder_event
from converters.common.item_id_resolver import resolve_item_id


# ============================================================
# Mapowania blokow 1.7.10 -> 1.18.2
# ============================================================

# Bloki z wariantem wood/stone w 1.7.10 -> material_block 1.18.2
WOOD_STONE_BLOCK_MAP = {
    "tablewood": ("oak_table", "wood"),
    "tablestone": ("stone_table", "stone"),
    "chairwood": ("oak_chair", "wood"),
    "chairstone": ("stone_chair", "stone"),
    "coffeetablewood": ("oak_coffee_table", "wood"),
    "coffeetablestone": ("stone_coffee_table", "stone"),
    "coffetablewood": ("oak_coffee_table", "wood"),
    "coffetablestone": ("stone_coffee_table", "stone"),
}

# Bloki drewniane w 1.7.10 (domyslnie oak)
WOOD_ONLY_BLOCK_MAP = {
    "cabinet": "oak_cabinet",
    "bedsidecabinet": "oak_bedside_cabinet",
    "mailbox": "oak_mail_box",
    "blinds": "oak_blinds",
    "blindon": "oak_blinds",
    "blindoff": "oak_blinds",
    "curtains": "oak_curtains",
    "curtainon": "oak_curtains",
    "curtainoff": "oak_curtains",
    "hedge": "oak_hedge",
}

# Zamienniki dla usunietych blokow (decyzja projektowa)
REPLACEMENT_MAP = {
    "bin": "oak_crate",
    "wallcabinet": "oak_cabinet",
    "counterdoored": "white_kitchen_counter",
    "kitchencabinet": "white_kitchen_drawer",
    "countersink": "kitchen_sink",
}

# Zmienione nazwy
RENAMED_MAP = {
    "stonepath": "rock_path",
    "whitefence": "white_picket_fence",
    "ovenoverhead": "range_hood",
}

# Bloki zachowane 1:1 (bez materialu)
DIRECT_MAP = {
    "fridge": "fridge_light",
    "freezer": "freezer_light",
}

# Kolory sofy (metadata 0-15 -> color_name)
COUCH_COLORS = [
    "white", "orange", "magenta", "light_blue", "yellow", "lime",
    "pink", "gray", "light_gray", "cyan", "purple", "blue",
    "brown", "green", "red", "black"
]

# Bloki usuniete -> strata (air)
REMOVED_BLOCKS = {
    "oven", "microwave", "computer", "printer", "tv", "stereo",
    "washingmachine", "dishwasher", "toaster", "blender", "plate",
    "cup", "choppingboard", "cookiejar", "present", "electricfence",
    "doorbell", "firealarmoff", "firealarmon", "ceilinglightoff",
    "ceilinglighton", "lampoff", "lampon", "tree", "birdbath",
}

# Bloki lazienkowe / dekoracyjne -> placeholder
PLACEHOLDER_BLOCKS = {
    "basin", "bath1", "bath2", "showerbottom", "showertop",
    "showerheadoff", "showerheadon", "toilet", "tap",
    "barstool", "hey", "nyan", "pattern", "yellowglow", "whiteglass",
}


# ============================================================
# Tile Entity registry names 1.7.10 -> 1.18.2
# ============================================================

TE_MAP = {
    "cfmOven": None,
    "cfmFridge": "cfm:fridge",
    "cfmCabinet": "cfm:cabinet",
    "cfmFreezer": "cfm:freezer",
    "cfmBedsideCabinet": "cfm:bedside_cabinet",
    "cfmMailBox": "cfm:mail_box",
    "cfmComputer": None,
    "cfmPrinter": None,
    "cfmTV": None,
    "cfmStereo": None,
    "cfmPresent": None,
    "cfmBin": "cfm:crate",  # Bin -> Crate
    "cfmWallCabinet": "cfm:cabinet",  # WallCabinet -> Cabinet
    "cfmBath": None,
    "cfmBasin": "cfm:kitchen_sink",  # Basin -> KitchenSink
    "cfmShowerHead": None,
    "cfmCookieJar": None,
    "cfmPlate": None,
    "cfmCouch": None,  # SofaBlock 1.18.2 nie ma BE
    "cfmToaster": None,
    "cfmChoppingBoard": None,
    "cfmBlender": None,
    "cfmMicrowave": None,
    "cfmWashingMachine": None,
    "cfmDishwasher": None,
    "cfmCabinetKitchen": "cfm:kitchen_drawer",
    "cfmCounterSink": "cfm:kitchen_sink",
    "cfmCup": None,
}

# Rozmiary inventory w 1.18.2 (ContainerHelper)
TE_INVENTORY_SIZE = {
    "cfm:cabinet": 18,
    "cfm:bedside_cabinet": 9,
    "cfm:desk_cabinet": 9,
    "cfm:crate": 9,
    "cfm:mail_box": 9,
    "cfm:trampoline": 0,
    "cfm:cooler": 9,
    "cfm:grill": 0,  # Grill ma skomplikowany NBT
    "cfm:door_mat": 0,
    "cfm:kitchen_drawer": 9,
    "cfm:kitchen_sink": 0,
    "cfm:fridge": 27,
    "cfm:freezer": 3,
}

# Custom slot tags w 1.7.10 per TE
TE_SLOT_TAGS = {
    "cfmOven": "OvenSlot",        # heurystyka, w rzeczywistosci uzywa Items/Slot
    "cfmFridge": "fridgeSlot",
    "cfmCabinet": "cabinetSlot",
    "cfmFreezer": "Slot",
    "cfmBedsideCabinet": "bedsideCabinetSlot",
    "cfmMailBox": "mailBoxSlot",
    "cfmBin": "BinSlot",
    "cfmWallCabinet": "wallCabinetSlot",
    "cfmCabinetKitchen": "kitchenCabinetSlot",
    "cfmCounterSink": "Slot",
    "cfmBasin": "Slot",
}


# ============================================================
# Glowna klasa konwertera
# ============================================================

class MrCrayfishConverter:
    """Konwerter blokow i Tile Entities MrCrayfish Furniture Mod."""

    MOD_ID = "cfm"
    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"

    def __init__(self, level_dat_path: str | None = None):
        self.warnings: List[str] = []
        self.errors: List[str] = []
        self.level_dat_path = level_dat_path
        self._item_resolver = None
        if level_dat_path:
            try:
                from converters.common.item_id_resolver import load_item_id_mapping
                load_item_id_mapping(level_dat_path)
                self._item_resolver = resolve_item_id
            except Exception:
                pass  # Brak mapowania - zostaw numeryczne ID

    # ------------------------------------------------------------------
    # Bloki (bez TE)
    # ------------------------------------------------------------------

    def convert_block(
        self,
        block_id: str,
        metadata: int = 0,
        position: Optional[Tuple[int, int, int]] = None,
    ) -> ConversionEvent:
        """Konwertuje blok (bez Tile Entity) i zwraca ConversionEvent."""
        name = block_id.lower().replace("cfm:", "").replace("tile.", "")

        # 1. Wood/stone variants
        if name in WOOD_STONE_BLOCK_MAP:
            target, material_type = WOOD_STONE_BLOCK_MAP[name]
            return ConversionEvent(
                mod=self.MOD_ID,
                source_version=self.SOURCE_VERSION,
                target_version=self.TARGET_VERSION,
                event_type="remap",
                source_block_id=block_id,
                source_metadata=metadata,
                target_block_id=f"{self.MOD_ID}:{target}",
                position=position,
                blockstate_props={},
            )

        # 2. Wood only blocks
        if name in WOOD_ONLY_BLOCK_MAP:
            target = WOOD_ONLY_BLOCK_MAP[name]
            return ConversionEvent(
                mod=self.MOD_ID,
                source_version=self.SOURCE_VERSION,
                target_version=self.TARGET_VERSION,
                event_type="remap",
                source_block_id=block_id,
                source_metadata=metadata,
                target_block_id=f"{self.MOD_ID}:{target}",
                position=position,
            )

        # 3. Replacements (Bin -> Crate, etc.)
        if name in REPLACEMENT_MAP:
            target = REPLACEMENT_MAP[name]
            return ConversionEvent(
                mod=self.MOD_ID,
                source_version=self.SOURCE_VERSION,
                target_version=self.TARGET_VERSION,
                event_type="remap",
                source_block_id=block_id,
                source_metadata=metadata,
                target_block_id=f"{self.MOD_ID}:{target}",
                position=position,
                warnings=[f"Converted from {name} to {target}"],
            )

        # 4. Renamed blocks
        if name in RENAMED_MAP:
            target = RENAMED_MAP[name]
            return ConversionEvent(
                mod=self.MOD_ID,
                source_version=self.SOURCE_VERSION,
                target_version=self.TARGET_VERSION,
                event_type="remap",
                source_block_id=block_id,
                source_metadata=metadata,
                target_block_id=f"{self.MOD_ID}:{target}",
                position=position,
            )

        # 5. Direct 1:1
        if name in DIRECT_MAP:
            target = DIRECT_MAP[name]
            return ConversionEvent(
                mod=self.MOD_ID,
                source_version=self.SOURCE_VERSION,
                target_version=self.TARGET_VERSION,
                event_type="remap",
                source_block_id=block_id,
                source_metadata=metadata,
                target_block_id=f"{self.MOD_ID}:{target}",
                position=position,
            )

        # 6. Couch (metadata = color)
        if name == "couch":
            color_idx = metadata % 16
            color_name = COUCH_COLORS[color_idx]
            return ConversionEvent(
                mod=self.MOD_ID,
                source_version=self.SOURCE_VERSION,
                target_version=self.TARGET_VERSION,
                event_type="remap",
                source_block_id=block_id,
                source_metadata=metadata,
                target_block_id=f"{self.MOD_ID}:{color_name}_sofa",
                position=position,
                blockstate_props={"color": color_name},
            )

        # 7. Removed -> air
        if name in REMOVED_BLOCKS:
            return ConversionEvent(
                mod=self.MOD_ID,
                source_version=self.SOURCE_VERSION,
                target_version=self.TARGET_VERSION,
                event_type="remove",
                source_block_id=block_id,
                source_metadata=metadata,
                target_block_id="minecraft:air",
                position=position,
                warnings=[f"Block {name} removed in 1.18.2 — items lost"],
            )

        # 8. Placeholder
        if name in PLACEHOLDER_BLOCKS:
            return ConversionEvent(
                mod=self.MOD_ID,
                source_version=self.SOURCE_VERSION,
                target_version=self.TARGET_VERSION,
                event_type="placeholder",
                source_block_id=block_id,
                source_metadata=metadata,
                target_block_id="minecraft:barrier",
                position=position,
                warnings=[f"Block {name} has no 1.18.2 equivalent — placeholder"],
            )

        # 9. Unknown
        return ConversionEvent(
            mod=self.MOD_ID,
            source_version=self.SOURCE_VERSION,
            target_version=self.TARGET_VERSION,
            event_type="placeholder",
            source_block_id=block_id,
            source_metadata=metadata,
            target_block_id="minecraft:barrier",
            position=position,
            warnings=[f"Unknown block {name} — placeholder"],
        )

    # ------------------------------------------------------------------
    # Tile Entities
    # ------------------------------------------------------------------

    def convert_tile_entity(
        self,
        te_nbt: Dict[str, Any],
        block_id: str = "",
        metadata: int = 0,
        position: Optional[Tuple[int, int, int]] = None,
    ) -> Optional[ConversionEvent]:
        """Konwertuje Tile Entity 1.7.10 i zwraca ConversionEvent z NBT 1.18.2."""
        te_id = te_nbt.get("id", "")
        if not te_id:
            return None

        # Znajdujemy docelowe TE ID
        target_te_id = TE_MAP.get(te_id)

        # Jesli TE ma mapping na None, a blok jest usuniety -> remove event
        if target_te_id is None:
            block_event = self.convert_block(block_id, metadata, position)
            block_event.source_te_id = te_id
            block_event.source_nbt = dict(te_nbt)
            return block_event

        # Tworzymy NBT 1.18.2
        nbt_1182 = self._convert_te_nbt(te_id, target_te_id, te_nbt)

        # Mapujemy blok
        block_event = self.convert_block(block_id, metadata, position)
        block_event.source_te_id = te_id
        block_event.target_te_id = target_te_id
        block_event.nbt_1182 = nbt_1182
        block_event.source_nbt = dict(te_nbt)

        # Jesli byl placeholder/remove, ale mamy TE -> dostosuj
        if block_event.event_type in ("remove", "placeholder"):
            # Niektore TE mapowane na istniejace bloki mimo ze oryginalny blok usuniety
            # (np. Basin ma mapping na kitchen_sink)
            if te_id in ("cfmBasin", "cfmCounterSink"):
                block_event.event_type = "remap"
                block_event.target_block_id = f"{self.MOD_ID}:kitchen_sink"
                block_event.warnings = [f"TE {te_id} mapped to {target_te_id}"]
            elif te_id == "cfmBin":
                block_event.event_type = "remap"
                block_event.target_block_id = f"{self.MOD_ID}:oak_crate"
                block_event.warnings = [f"TE {te_id} mapped to {target_te_id}"]
            elif te_id == "cfmWallCabinet":
                block_event.event_type = "remap"
                block_event.target_block_id = f"{self.MOD_ID}:oak_cabinet"
                block_event.warnings = [f"TE {te_id} mapped to {target_te_id}"]
            elif te_id == "cfmCabinetKitchen":
                block_event.event_type = "remap"
                block_event.target_block_id = f"{self.MOD_ID}:white_kitchen_drawer"
                block_event.warnings = [f"TE {te_id} mapped to {target_te_id}"]

        return block_event

    def _convert_te_nbt(
        self,
        source_te_id: str,
        target_te_id: str,
        te_nbt: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Konwertuje NBT Tile Entity z 1.7.10 na 1.18.2."""
        nbt_1182: Dict[str, Any] = {"id": target_te_id}

        # Pozycja (bedzie nadpisana przez handler mapy, ale zachowujemy dla pewnosci)
        for coord in ("x", "y", "z"):
            if coord in te_nbt:
                nbt_1182[coord] = te_nbt[coord]

        # --- Inventory ---
        target_size = TE_INVENTORY_SIZE.get(target_te_id, 0)
        if target_size > 0:
            slot_tag = TE_SLOT_TAGS.get(source_te_id, "Slot")
            possible_keys = ["Items", f"{source_te_id.lower().replace('cfm', '')}Items"]
            # Prosta heurystyka nazw
            if source_te_id == "cfmFridge":
                possible_keys = ["fridgeItems", "Items"]
            elif source_te_id == "cfmCabinet":
                possible_keys = ["cabinetItems", "Items"]
            elif source_te_id == "cfmBedsideCabinet":
                possible_keys = ["bedsideCabinetItems", "Items"]
            elif source_te_id == "cfmMailBox":
                possible_keys = ["mailBoxItems", "Items"]
            elif source_te_id == "cfmBin":
                possible_keys = ["binItems", "Items"]
            elif source_te_id == "cfmWallCabinet":
                possible_keys = ["wallCabinetItems", "Items"]

            items, found_key, found_tag = extract_items_from_legacy_nbt(
                te_nbt, possible_keys, [slot_tag, "Slot", "slot"]
            )
            if items:
                converted = convert_inventory_1710_to_1182(
                    items, found_tag or "Slot", target_size,
                    item_id_resolver=self._item_resolver,
                )
                nbt_1182["Items"] = converted

        # --- MailBox specyficzne ---
        if source_te_id == "cfmMailBox":
            nbt_1182.update(self._convert_mailbox_nbt(te_nbt))

        # --- Fridge/Freezer specyficzne ---
        if source_te_id == "cfmFreezer":
            # Freezer 1.18.2 ma dodatkowe pola dla zamrazania
            nbt_1182["FreezeTime"] = 0
            nbt_1182["FreezeTimeTotal"] = 200
            nbt_1182["FuelTime"] = 0
            nbt_1182["RecipesUsed"] = {}

        # --- KitchenSink / CounterSink / Basin ---
        if target_te_id == "cfm:kitchen_sink":
            nbt_1182.update(self._convert_fluid_nbt(source_te_id, te_nbt))

        # --- Couch color (jako BE 1.18.2 nie ma, ale zachowujemy w extra) ---
        if source_te_id == "cfmCouch":
            color = te_nbt.get("Colour", 0)
            nbt_1182["Colour"] = color  # Tylko informacyjnie, BE nie istnieje w 1.18.2

        return nbt_1182

    def _convert_mailbox_nbt(self, te_nbt: Dict[str, Any]) -> Dict[str, Any]:
        """Konwersja MailBox NBT: UUID string -> int-array, locked -> boolean."""
        result: Dict[str, Any] = {}

        # OwnerName
        owner_name = te_nbt.get("OwnerName", "")
        if owner_name:
            result["OwnerName"] = owner_name

        # OwnerUUID string -> int-array
        owner_uuid_str = te_nbt.get("OwnerUUID")
        if owner_uuid_str and isinstance(owner_uuid_str, str):
            try:
                result["OwnerUUID"] = uuid_string_to_int_array(owner_uuid_str)
            except Exception:
                result["OwnerUUID"] = uuid_string_to_int_array(str(uuid.uuid4()))

        # MailBoxUUID (generujemy nowe)
        result["MailBoxUUID"] = str(uuid.uuid4())
        result["MailBoxName"] = owner_name or "Mailbox"

        return result

    def _convert_fluid_nbt(
        self,
        source_te_id: str,
        te_nbt: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Konwersja plynow: boolean/level -> FluidTank.

        Forge 1.18.2 FluidTank.writeToNBT zapisuje bezposrednio do CompoundTag:
        {FluidName: "minecraft:water", Amount: 5000}
        (bez wrappera "Tank" - patrz FluidHandlerSyncedBlockEntity.saveAdditional)
        """
        result: Dict[str, Any] = {}
        amount = 0

        if source_te_id == "cfmCounterSink":
            has_water = bool(te_nbt.get("HasWater", 0))
            amount = 5000 if has_water else 0
        elif source_te_id == "cfmBasin":
            level = te_nbt.get("WaterLevel", 0)
            amount = int((level / 8.0) * 10000)

        if amount > 0:
            # Forge FluidTank format - bezpośrednio w root compound
            result["FluidName"] = "minecraft:water"
            result["Amount"] = amount

        return result

    # ------------------------------------------------------------------
    # Placeholder event (dla blokow bez TE ale wymagajacych placeholdera)
    # ------------------------------------------------------------------

    def make_placeholder_event(
        self,
        block_id: str,
        metadata: int = 0,
        position: Optional[Tuple[int, int, int]] = None,
        te_nbt: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Tworzy event placeholdera zgodny z common.placeholders."""
        return make_block_entity_placeholder_event(
            position=position or (0, 0, 0),
            source_mod=self.MOD_ID,
            source_block_id=block_id,
            source_metadata=metadata,
            original_nbt=te_nbt,
            conversion_reason="no_1182_equivalent",
        )


# ============================================================
# Funkcje pomocnicze na poziomie modulu
# ============================================================

def convert_single_block(
    block_id: str,
    metadata: int = 0,
    position: Optional[Tuple[int, int, int]] = None,
    te_nbt: Optional[Dict[str, Any]] = None,
) -> ConversionEvent:
    """Funkcja convenience — konwertuje pojedynczy blok (z opcjonalnym TE)."""
    converter = MrCrayfishConverter()
    if te_nbt:
        return converter.convert_tile_entity(te_nbt, block_id, metadata, position)
    return converter.convert_block(block_id, metadata, position)


def convert_blocks_batch(
    blocks: List[Tuple[str, int, Tuple[int, int, int], Optional[Dict[str, Any]]]]
) -> List[ConversionEvent]:
    """Konwertuje wsad blokow i zwraca liste ConversionEvent."""
    converter = MrCrayfishConverter()
    results = []
    for block_id, metadata, position, te_nbt in blocks:
        if te_nbt:
            event = converter.convert_tile_entity(te_nbt, block_id, metadata, position)
        else:
            event = converter.convert_block(block_id, metadata, position)
        if event:
            results.append(event)
    return results
