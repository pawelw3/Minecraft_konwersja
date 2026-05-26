"""Konwerter ComputerCraft 1.7.10 → CC:Tweaked 1.18.2.

Zadanie 1 (DONE): Pełna inwentaryzacja bloków i TE w ZADANIE_1_ANALIZA.md
Zadanie 2 (DONE): Symulacje funkcjonalności w simulations/
Zadanie 3 (DONE): Pełna konwersja NBT i blockstate
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .mappings import (
    BlockMapping,
    get_block_mapping,
    get_mapping_for_te_id,
    is_computercraft_block_id,
    is_computercraft_te_id,
)

# ---------------------------------------------------------------------------
# Upgrade mapping (z turtle_simulation.py)
# ---------------------------------------------------------------------------

_LEGACY_UPGRADE_ID_MAP: dict[int, str] = {
    1: "computercraft:wireless_modem",
    2: "minecraft:crafting_table",
    3: "minecraft:diamond_sword",
    4: "minecraft:diamond_shovel",
    5: "minecraft:diamond_pickaxe",
    6: "minecraft:diamond_axe",
    7: "minecraft:diamond_hoe",
    8: "computercraft:speaker",
    -1: "computercraft:advanced_modem",
}

_UPGRADE_RENAME_MAP: dict[str, str] = {
    "computercraft:wireless_modem": "computercraft:wireless_modem_normal",
    "computercraft:advanced_modem": "computercraft:wireless_modem_advanced",
}

_UPGRADE_DIRECT_MATCH: frozenset[str] = frozenset({
    "minecraft:diamond_pickaxe",
    "minecraft:diamond_axe",
    "minecraft:diamond_sword",
    "minecraft:diamond_shovel",
    "minecraft:diamond_hoe",
    "minecraft:crafting_table",
    "computercraft:speaker",
})

# Mapowanie 1.7.10 monitor dir → 1.18.2 blockstate
_DIR_TO_BLOCKSTATE: dict[int, tuple[str, str]] = {
    2: ("north", "north"),
    3: ("north", "south"),
    4: ("north", "west"),
    5: ("north", "east"),
    8: ("down", "north"),
    9: ("down", "south"),
    10: ("down", "west"),
    11: ("down", "east"),
    14: ("up", "north"),
    15: ("up", "south"),
    16: ("up", "west"),
    17: ("up", "east"),
}


@dataclass
class ConversionResult:
    success: bool
    block_id_1182: str | None = None
    blockstate_props: dict[str, str] = field(default_factory=dict)
    nbt_1182: dict[str, Any] | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ComputerCraftBlockConversion:
    original_id: str
    original_pos: tuple[int, int, int]
    metadata: int
    converted: ConversionResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "original_id": self.original_id,
            "original_pos": self.original_pos,
            "metadata": self.metadata,
            "new_id": self.converted.block_id_1182,
            "blockstate_props": self.converted.blockstate_props,
            "nbt": self.converted.nbt_1182,
            "errors": self.converted.errors,
            "warnings": self.converted.warnings,
        }


class ComputerCraftConverter:
    """Konwerter bloków i tile entities ComputerCraft."""

    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"

    def __init__(self) -> None:
        self.stats = {"processed": 0, "converted": 0, "failed": 0, "warnings": 0}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def convert_block(
        self,
        block_id_1710: str,
        metadata: int = 0,
        nbt_1710: dict[str, Any] | None = None,
        position: tuple[int, int, int] = (0, 0, 0),
    ) -> ComputerCraftBlockConversion:
        """Skonwertuj blok 1.7.10 na 1.18.2."""
        self.stats["processed"] += 1

        mapping = self._resolve_mapping(block_id_1710, metadata, nbt_1710)
        if not mapping:
            msg = f"CC-E-BLOCK-NOT-MAPPED: brak mapowania dla {block_id_1710} meta={metadata}"
            self.stats["failed"] += 1
            result = ConversionResult(False, errors=[msg])
            return ComputerCraftBlockConversion(block_id_1710, position, metadata, result)

        nbt_result = self._convert_nbt(mapping, nbt_1710 or {}, metadata)
        blockstate = self._derive_blockstate(mapping, nbt_1710 or {}, metadata)

        if nbt_result.errors:
            self.stats["failed"] += 1
            result = ConversionResult(
                False,
                block_id_1182=mapping.target_block_id,
                blockstate_props=blockstate,
                nbt_1182=nbt_result.nbt,
                errors=nbt_result.errors,
                warnings=nbt_result.warnings,
            )
        else:
            self.stats["converted"] += 1
            if nbt_result.warnings:
                self.stats["warnings"] += len(nbt_result.warnings)
            result = ConversionResult(
                True,
                block_id_1182=mapping.target_block_id,
                blockstate_props=blockstate,
                nbt_1182=nbt_result.nbt,
                warnings=nbt_result.warnings,
            )

        return ComputerCraftBlockConversion(block_id_1710, position, metadata, result)

    def convert_tile_entity(
        self,
        te_id: str,
        nbt_1710: dict[str, Any],
        metadata: int = 0,
        position: tuple[int, int, int] = (0, 0, 0),
    ) -> ComputerCraftBlockConversion:
        """Skonwertuj tile entity 1.7.10 na 1.18.2.

        Te ID w 1.7.10 mają specyficzny format: "computercraft : <nazwa>" (ze spacjami!).
        """
        self.stats["processed"] += 1

        mapping = get_mapping_for_te_id(te_id, metadata)
        if not mapping:
            msg = f"CC-E-TE-NOT-MAPPED: brak mapowania dla TE {te_id} meta={metadata}"
            self.stats["failed"] += 1
            result = ConversionResult(False, errors=[msg])
            return ComputerCraftBlockConversion(te_id, position, metadata, result)

        return self.convert_block(
            block_id_1710=mapping.source_block_id,
            metadata=mapping.metadata if mapping.metadata is not None else metadata,
            nbt_1710=nbt_1710,
            position=position,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_mapping(
        self,
        block_id_1710: str,
        metadata: int,
        nbt_1710: dict[str, Any] | None,
    ) -> BlockMapping | None:
        """Rozwiąż mapowanie na podstawie block_id i metadata."""
        if is_computercraft_te_id(block_id_1710):
            return get_mapping_for_te_id(block_id_1710, metadata)
        return get_block_mapping(block_id_1710, metadata)

    def _derive_blockstate(
        self,
        mapping: BlockMapping,
        nbt_1710: dict[str, Any],
        metadata: int,
    ) -> dict[str, str]:
        """Wydedukuj blockstate 1.18.2 z metadata 1.7.10 i NBT."""
        blockstate: dict[str, str] = {}
        src = mapping.source_block_id

        # --- Computer / Command Computer ---
        if src == "computercraft:computer":
            facing_idx = metadata & 0x7
            facing_map = {2: "north", 3: "south", 4: "west", 5: "east"}
            if facing_idx in facing_map:
                blockstate["facing"] = facing_map[facing_idx]
            blockstate["state"] = "on" if nbt_1710.get("on", False) else "off"

        if src == "computercraft:command_computer":
            # Command computer nie ma facing w metadata (zawsze 0)
            # W 1.7.10 facing był ustawiany przy stawianiu, ale metadata=0
            # W 1.18.2 command computer też ma facing — domyślnie north
            blockstate["facing"] = "north"
            blockstate["state"] = "on" if nbt_1710.get("on", False) else "off"

        # --- Peripheral (disk drive, printer, speaker, monitor, wireless modem) ---
        if src == "computercraft:peripheral":
            notes = mapping.notes
            if notes == "Disk drive":
                facing_map = {2: "north", 3: "south", 4: "west", 5: "east"}
                if metadata in facing_map:
                    blockstate["facing"] = facing_map[metadata]
                blockstate["state"] = "empty"
            elif notes == "Printer":
                # Printer w 1.7.10 nie ma facing w metadata (meta=11)
                # W 1.18.2 printer ma facing z block placement — domyślnie north
                blockstate["facing"] = "north"
                blockstate["top"] = "false"
                blockstate["bottom"] = "false"
            elif notes == "Monitor":
                blockstate = self._monitor_blockstate(nbt_1710)
            elif notes == "Advanced monitor":
                blockstate = self._monitor_blockstate(nbt_1710)
            elif "Wireless modem" in notes:
                if metadata == 0:
                    blockstate["facing"] = "down"
                elif metadata == 1:
                    blockstate["facing"] = "up"
                else:
                    facing_idx = metadata - 4
                    facing_map = {2: "north", 3: "south", 4: "west", 5: "east"}
                    if facing_idx in facing_map:
                        blockstate["facing"] = facing_map[facing_idx]
                blockstate["on"] = "false"
            elif notes == "Speaker":
                # Speaker w 1.7.10 nie ma facing w metadata (meta=13)
                blockstate["facing"] = "north"

        # --- Advanced Modem (ender modem) ---
        if src == "computercraft:advanced_modem":
            # W 1.7.10 advanced_modem nie ma facing w metadata
            blockstate["facing"] = "north"
            blockstate["on"] = "false"

        # --- Cable ---
        if src == "computercraft:cable":
            if metadata < 6:
                blockstate["cable"] = "false"
                blockstate["modem"] = f"{self._facing_from_meta(metadata)}_off"
            elif metadata < 12:
                blockstate["cable"] = "true"
                blockstate["modem"] = f"{self._facing_from_meta(metadata - 6)}_off"
            elif metadata == 13:
                blockstate["cable"] = "true"
                blockstate["modem"] = "none"
            # Connections — w 1.18.2 są dynamiczne; zostawiamy domyślne false
            for dir_name in ("north", "south", "east", "west", "up", "down"):
                blockstate[dir_name] = "false"

        # --- Turtle ---
        if src in ("computercraft:turtle", "computercraft:turtle_expanded", "computercraft:turtle_advanced"):
            dir_idx = nbt_1710.get("dir", 2)
            facing_map = {2: "north", 3: "south", 4: "west", 5: "east"}
            if dir_idx in facing_map:
                blockstate["facing"] = facing_map[dir_idx]

        return blockstate

    def _monitor_blockstate(self, nbt_1710: dict[str, Any]) -> dict[str, str]:
        """Wydedukuj blockstate monitora 1.18.2 z NBT 1.7.10."""
        dir_1710 = nbt_1710.get("dir", 2)
        orientation, facing = _DIR_TO_BLOCKSTATE.get(dir_1710, ("north", "north"))

        x = nbt_1710.get("xIndex", 0)
        y = nbt_1710.get("yIndex", 0)
        w = nbt_1710.get("width", 1)
        h = nbt_1710.get("height", 1)

        edges = []
        if x > 0:
            edges.append("l")
        if x < w - 1:
            edges.append("r")
        if y > 0:
            edges.append("u")
        if y < h - 1:
            edges.append("d")

        state = "".join(edges) if edges else "none"
        return {"orientation": orientation, "facing": facing, "state": state}

    def _facing_from_meta(self, meta: int) -> str:
        """Zamiana metadata 0-5 na facing string."""
        return {0: "down", 1: "up", 2: "north", 3: "south", 4: "west", 5: "east"}.get(meta, "north")

    def _resolve_upgrade_id(self, value: Any) -> str | None:
        """Rozwiąż ID upgradu z 1.7.10 na string ID 1.18.2."""
        if isinstance(value, int):
            id_1710 = _LEGACY_UPGRADE_ID_MAP.get(value)
            if id_1710 is None:
                return None
            return _UPGRADE_RENAME_MAP.get(id_1710, id_1710)

        if not isinstance(value, str):
            return None

        if value in _UPGRADE_DIRECT_MATCH:
            return value
        return _UPGRADE_RENAME_MAP.get(value, value)

    def _convert_nbt(
        self,
        mapping: BlockMapping,
        nbt_1710: dict[str, Any],
        metadata: int,
    ) -> "NBTConversionResult":
        """Skonwertuj NBT 1.7.10 na 1.18.2."""
        nbt_1182: dict[str, Any] = {}
        warnings: list[str] = []

        target_be = mapping.target_blockentity_id

        # ------------------------------------------------------------------
        # Computer (normal / advanced / command)
        # ------------------------------------------------------------------
        if target_be in (
            "computercraft:computer_normal",
            "computercraft:computer_advanced",
            "computercraft:computer_command",
        ):
            if "computerID" in nbt_1710:
                nbt_1182["ComputerId"] = nbt_1710["computerID"]
            if "label" in nbt_1710:
                nbt_1182["Label"] = nbt_1710["label"]
            if "on" in nbt_1710:
                nbt_1182["On"] = nbt_1710["on"]

        # ------------------------------------------------------------------
        # Turtle
        # ------------------------------------------------------------------
        elif target_be in ("computercraft:turtle_normal", "computercraft:turtle_advanced"):
            if "computerID" in nbt_1710:
                nbt_1182["ComputerId"] = nbt_1710["computerID"]
            if "label" in nbt_1710:
                nbt_1182["Label"] = nbt_1710["label"]
            if "on" in nbt_1710:
                nbt_1182["On"] = nbt_1710["on"]
            if "Items" in nbt_1710:
                nbt_1182["Items"] = nbt_1710["Items"]
            if "fuelLevel" in nbt_1710:
                nbt_1182["Fuel"] = nbt_1710["fuelLevel"]
            if "selectedSlot" in nbt_1710:
                nbt_1182["Slot"] = nbt_1710["selectedSlot"]
            if "colour" in nbt_1710:
                nbt_1182["Colour"] = nbt_1710["colour"]
            if "overlay_mod" in nbt_1710 and "overlay_path" in nbt_1710:
                nbt_1182["Overlay"] = f"{nbt_1710['overlay_mod']}:{nbt_1710['overlay_path']}"

            # Upgrades
            for old_key, new_key, old_nbt_key, new_nbt_key in [
                ("leftUpgrade", "LeftUpgrade", "leftUpgradeNBT", "LeftUpgradeNbt"),
                ("rightUpgrade", "RightUpgrade", "rightUpgradeNBT", "RightUpgradeNbt"),
            ]:
                if old_key in nbt_1710:
                    val = nbt_1710[old_key]
                    resolved = self._resolve_upgrade_id(val)
                    if resolved:
                        nbt_1182[new_key] = resolved
                    else:
                        warnings.append(f"CC-W-UNKNOWN-UPGRADE: nieznany upgrade {val} w {old_key}")
                if old_nbt_key in nbt_1710:
                    nbt_1182[new_nbt_key] = dict(nbt_1710[old_nbt_key])

            # Owner — brak w 1.7.10, CC:Tweaked ustawi przy pierwszym użyciu

        # ------------------------------------------------------------------
        # Monitor
        # ------------------------------------------------------------------
        elif target_be in ("computercraft:monitor_normal", "computercraft:monitor_advanced"):
            if "xIndex" in nbt_1710:
                nbt_1182["XIndex"] = nbt_1710["xIndex"]
            if "yIndex" in nbt_1710:
                nbt_1182["YIndex"] = nbt_1710["yIndex"]
            if "width" in nbt_1710:
                nbt_1182["Width"] = nbt_1710["width"]
            if "height" in nbt_1710:
                nbt_1182["Height"] = nbt_1710["height"]
            # dir nie jest przenoszone do NBT w 1.18.2 (jest w blockstate)

        # ------------------------------------------------------------------
        # Disk Drive
        # ------------------------------------------------------------------
        elif target_be == "computercraft:disk_drive":
            if "item" in nbt_1710:
                nbt_1182["Item"] = nbt_1710["item"]

        # ------------------------------------------------------------------
        # Printer
        # ------------------------------------------------------------------
        elif target_be == "computercraft:printer":
            if "printing" in nbt_1710:
                nbt_1182["Printing"] = nbt_1710["printing"]
            if "pageTitle" in nbt_1710:
                nbt_1182["PageTitle"] = nbt_1710["pageTitle"]
            if "Items" in nbt_1710:
                nbt_1182["Items"] = nbt_1710["Items"]
            # Dane strony (terminal text) są zapisane przez m_page.writeToNBT(nbttagcompound)
            # W 1.18.2 page używa innego formatu terminala — zostawiamy warning
            if any(k.startswith("term_") or k in ("cursorX", "cursorY", "cursorColour", "cursorBlink", "text", "textColour", "backColour") for k in nbt_1710):
                warnings.append("CC-W-PRINTER-PAGE: dane strony drukarki (terminal) mogą wymagać recznej weryfikacji")

        # ------------------------------------------------------------------
        # Cable
        # ------------------------------------------------------------------
        elif target_be == "computercraft:cable":
            if "peripheralID" in nbt_1710:
                pid = nbt_1710["peripheralID"]
                if pid >= 0:
                    nbt_1182["PeripheralId"] = pid
            # peripheralAccess nie ma bezpośredniego odpowiednika w NBT 1.18.2

        # ------------------------------------------------------------------
        # Wireless Modem / Speaker / Wired Modem Full — brak stałego NBT
        # ------------------------------------------------------------------
        elif target_be in (
            "computercraft:wireless_modem_normal",
            "computercraft:wireless_modem_advanced",
            "computercraft:speaker",
            "computercraft:wired_modem_full",
        ):
            pass

        if not nbt_1182:
            nbt_1182 = None  # type: ignore[assignment]

        return NBTConversionResult(nbt=nbt_1182, errors=[], warnings=warnings)


@dataclass
class NBTConversionResult:
    nbt: dict[str, Any] | None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
