"""
Symulacje konwersji NBT Railcraft 1.7.10 → strict 1.18.2.

Źródło prawdy (1.7.10):
- mods/railcraft/common/blocks/tracks/TileTrack.java (writeToNBT/readFromNBT)
- mods/railcraft/common/blocks/machine/TileMachineBase.java
- mods/railcraft/common/blocks/machine/TileMultiBlock.java
- mods/railcraft/common/blocks/machine/TileMachineItem.java
- mods/railcraft/common/blocks/signals/TileSignalFoundation.java
- mods/railcraft/common/blocks/detector/TileDetector.java

UWAGA: Mody docelowe (Create, Steam'n'Rails, IE, Mekanism, Thermal) nie zostały
zweryfikowane lokalnie dla 1.18.2. Struktury NBT targetów to hipotezy oparte
na dokumentacji projektu i ogólnej znajomości modów.
"""

from __future__ import annotations

from typing import Any


def convert_track_nbt(te_nbt: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, str], list[str]]:
    """Konwertuje NBT TileTrack na blockstate props i ostrzeżenia.

    Wejście (1.7.10):
        te_nbt = {
            "id": "RailcraftTrackTile" | "RailcraftTrackTESRTile",
            "trackTag": "railcraft:track.switch",
            # lub legacy: "trackId": 7 (short)
            # Dodatkowe pola z TrackBaseRailcraft (np. facing, redstone, routing)
        }

    Wyjście (1.18.2):
        - nbt_1182: None (Create track nie używa BE NBT dla typu toru)
        - blockstate_props: {"shape": "...", "waterlogged": "false"} itp.
        - warnings: lista ostrzeżeń
    """
    warnings: list[str] = []
    props: dict[str, str] = {}

    track_tag = te_nbt.get("trackTag", "")
    if not track_tag and "trackId" in te_nbt:
        # Legacy mapping — zostawiamy do weryfikacji
        warnings.append(f"RC-W-TRACK-LEGACY-ID: trackId={te_nbt['trackId']} bez trackTag")

    # Create track w 1.18.2 używa blockstate "shape" dla geometrii.
    # Nie ma odpowiednika "trackTag" w BE — typ toru jest w block ID / blockstate.
    # Wszystkie specjalne funkcje (booster, launcher, routing) są TRACONE.
    if track_tag:
        if "switch" in track_tag or "wye" in track_tag or "junction" in track_tag:
            props["shape"] = "north_south"  # Create obsługuje zwrotnice automatycznie
        elif "east_west" in track_tag:
            props["shape"] = "east_west"
        else:
            props["shape"] = "north_south"

    # Wszystkie specjalne właściwości torów Railcrafta są tracone
    special_tracks = {"booster", "boost", "launcher", "priming", "embarking", "disembarking",
                      "boarding", "holding", "locking", "routing", "whistle",
                      "locomotive", "limiter", "control", "detector", "gated",
                      "oneway", "buffer.stop", "disposal", "force"}
    if any(s in track_tag for s in special_tracks):
        warnings.append(f"RC-W-TRACK-SPECIAL-LOST: {track_tag} — special track behavior lost in 1.18.2")

    return None, props, warnings


def convert_machine_inventory_nbt(te_nbt: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    """Konwertuje inventory z TileMachineItem na format 1.18.2.

    Wejście:
        te_nbt może zawierać "Items" (NBTTagList, legacy 1.7.10 format)
        lub "InvSlots" (dict z nazwanymi slotami — nie potwierdzone dla Railcraft).

    Wyjście:
        - nbt_1182 z "Items" (ListTag) jeśli istnieje inventory
        - warnings
    """
    warnings: list[str] = []
    out_nbt: dict[str, Any] = {}

    if "Items" in te_nbt:
        # Format 1.7.10: Items jest listą dictów z kluczami id, Count, Damage, Slot
        # W 1.18.2 ten sam format jest akceptowany (z drobnymi różnicami w ID)
        # Ale ID itemów 1.7.10 muszą zostać przekonwertowane w osobnym etapie.
        out_nbt["Items"] = te_nbt["Items"]
        warnings.append("RC-W-ITEM-IDS: Item IDs require global 1.7.10→1.18.2 remapping (not done here)")

    return out_nbt if out_nbt else None, warnings


def convert_multiblock_nbt(te_nbt: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    """Konwertuje NBT maszyny wieloblokowej (Coke Oven, Blast Furnace, Tank, Boiler).

    Wejście (1.7.10):
        te_nbt = {
            "master": True/False,
            "pattern": {...},  # struktura wielobloku
            # inventory, płyny, temperatura itp.
        }

    Wyjście (1.18.2):
        - Dla IE Coke Oven / Blast Furnace: NBT zachowane jako legacy_railcraft
          (IE ma inny system wielobloków i NIE odczyta tych danych bezpośrednio).
        - Ostrzeżenie o konieczności ręcznej rekonstrukcji struktury.
    """
    warnings: list[str] = []
    out_nbt: dict[str, Any] = {}

    # Zabezpieczamy oryginalne dane wielobloku dla ewentualnej ręcznej migracji
    if te_nbt.get("master") is not None:
        out_nbt["legacy_railcraft"] = {
            "master": te_nbt.get("master"),
            # Nie kopiujemy całego NBT — tylko flagi master
        }
        warnings.append("RC-W-MULTIBLOCK: Multiblock data preserved as legacy; structure must be rebuilt manually in 1.18.2")

    return out_nbt if out_nbt else None, warnings


def convert_signal_nbt(te_nbt: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, str], list[str]]:
    """Konwertuje NBT sygnału kolejowego.

    Wejście (1.7.10):
        te_nbt = {
            "id": "RCTileStructureBlockSignal" | "RCTileStructureControllerBox" itp.
            # Sygnały Railcrafta przechowują konfigurację wireless (pary block coords)
        }

    Wyjście (1.18.2):
        - Steam'n'Rails Semaphore — brak BE NBT w podstawowej wersji
        - Vanilla comparator/repeater — proste blockstate
        - Wszystkie zaawansowane funkcje sygnałów (pary, czasy, kierunki) TRACONE
    """
    warnings: list[str] = []
    props: dict[str, str] = {}
    out_nbt: dict[str, Any] | None = None

    te_id = te_nbt.get("id", "")
    if "Signal" in te_id or "Semaphore" in te_id:
        warnings.append("RC-W-SIGNAL-LOST: Advanced rail signal configuration lost (pairs, aspects, directions)")
        # Steam'n'Rails semaphore w 1.18.2 może mieć blockstate dla pozycji ramienia
        props["rotation"] = "0"
    elif "Box" in te_id or "Controller" in te_id or "Receiver" in te_id:
        warnings.append("RC-W-SIGNAL-BOX-LOST: Signal box logic (capacitance, sequencing, interlocking) lost")

    return out_nbt, props, warnings


def convert_detector_nbt(te_nbt: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, str], list[str]]:
    """Konwertuje NBT detektora.

    Wejście:
        te_nbt = {"id": "RCDetectorTile", ...}

    Wyjście:
        - Observer — brak BE NBT (blockstate wystarcza)
        - Wszystkie specyficzne funkcje detekcji (mob, player, train, routing) TRACONE
    """
    warnings: list[str] = ["RC-W-DETECTOR-LOST: Cart-specific detection (type, routing, energy) lost → generic observer"]
    return None, {"facing": "north"}, warnings


def convert_anchor_nbt(te_nbt: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    """Konwertuje NBT anchorów (chunk loaders).

    Wejście:
        te_nbt = {"id": "RCWorldAnchorTile" | "RCPersonalAnchorTile" ...}

    Wyjście:
        - Placeholder — brak modu chunk loaderów w 1.18.2
        - Ostrzeżenie o utracie chunk loading
    """
    warnings: list[str] = ["RC-W-ANCHOR-LOST: Chunk loader removed — area may stop loading after conversion"]
    return None, warnings


def convert_slab_nbt(te_nbt: dict[str, Any], metadata: int) -> tuple[dict[str, Any] | None, dict[str, str], list[str]]:
    """Konwertuje NBT Railcraft Slab na Framed Slab blockstate.

    Wejście:
        te_nbt = {"id": "RCSlabTile", "slab": "IRON" | "STEEL" | ..., "owner": "..."}
        metadata: 0-7 bottom half, 8-15 top half (material in lower 3 bits)

    Wyjście:
        - blockstate_props: {"type": "bottom" | "top"}
        - warnings
    """
    material = te_nbt.get("slab", "UNKNOWN")
    warnings: list[str] = [f"RC-W-SLAB-MATERIAL-LOST: Railcraft slab material '{material}' lost → FramedBlocks default texture"]
    props: dict[str, str] = {"type": "top" if metadata >= 8 else "bottom"}
    return None, props, warnings


def convert_stair_nbt(te_nbt: dict[str, Any], metadata: int) -> tuple[dict[str, Any] | None, dict[str, str], list[str]]:
    """Konwertuje NBT Railcraft Stair na Framed Stairs blockstate.

    Wejście:
        te_nbt = {"id": "RCStairTile", "stair": "IRON" | "STEEL" | ..., "owner": "..."}
        metadata: vanilla stair format (0-3 facing, +4 upside-down)

    Wyjście:
        - blockstate_props: {"facing": "...", "half": "bottom" | "top", "shape": "straight"}
        - warnings
    """
    material = te_nbt.get("stair", "UNKNOWN")
    warnings: list[str] = [f"RC-W-STAIR-MATERIAL-LOST: Railcraft stair material '{material}' lost → FramedBlocks default texture"]
    facing_map = {0: "east", 1: "west", 2: "south", 3: "north"}
    facing = facing_map.get(metadata % 4, "north")
    half = "top" if (metadata // 4) % 2 == 1 else "bottom"
    props: dict[str, str] = {"facing": facing, "half": half, "shape": "straight"}
    return None, props, warnings


def simulate_railcraft_conversion(
    block_id_1710: str,
    metadata: int,
    te_nbt: dict[str, Any] | None,
) -> dict[str, Any]:
    """Symulacja end-to-end konwersji jednego bloku/TE Railcrafta.

    Zwraca dict z polami:
        - block_id_1182
        - blockstate_props
        - nbt_1182
        - warnings
        - errors
    """
    from ..mappings.block_mappings import get_mapping

    result: dict[str, Any] = {
        "block_id_1182": None,
        "blockstate_props": {},
        "nbt_1182": None,
        "warnings": [],
        "errors": [],
    }

    mapping = get_mapping(block_id_1710, metadata)
    if mapping is None:
        result["errors"].append(f"RC-E-UNKNOWN-BLOCK: {block_id_1710}:{metadata}")
        result["block_id_1182"] = "conversion_placeholders:block_entity_placeholder"
        return result

    result["block_id_1182"] = mapping.target_block_id
    if mapping.blockstate_props:
        result["blockstate_props"] = dict(mapping.blockstate_props)

    if te_nbt is None:
        return result

    te_id = te_nbt.get("id", "")
    nbt_1182: dict[str, Any] | None = None
    warnings: list[str] = []
    extra_props: dict[str, str] = {}

    # Routing per TE type
    if te_id in ("RailcraftTrackTile", "RailcraftTrackTESRTile"):
        nbt_1182, extra_props, warnings = convert_track_nbt(te_nbt)
    elif te_id.startswith("RC") and "Tank" in te_id:
        nbt_1182, warnings = convert_multiblock_nbt(te_nbt)
        inv, w2 = convert_machine_inventory_nbt(te_nbt)
        warnings.extend(w2)
        if inv:
            nbt_1182 = {**(nbt_1182 or {}), **inv}
    elif te_id.startswith("RC") and ("BlastFurnace" in te_id or "CokeOven" in te_id or "Boiler" in te_id):
        nbt_1182, warnings = convert_multiblock_nbt(te_nbt)
    elif te_id.startswith("RCTileStructure"):
        nbt_1182, extra_props, warnings = convert_signal_nbt(te_nbt)
    elif te_id == "RCDetectorTile":
        nbt_1182, extra_props, warnings = convert_detector_nbt(te_nbt)
    elif te_id in ("RCWorldAnchorTile", "RCPersonalAnchorTile", "RCAdminAnchorTile", "RCPassiveAnchorTile"):
        nbt_1182, warnings = convert_anchor_nbt(te_nbt)
    elif te_id == "RCHiddenTile":
        result["warnings"].append("RC-W-IGNORED: RCHiddenTile (residual heat) removed per project rules")
        result["block_id_1182"] = "minecraft:air"
        return result
    elif te_id == "RCSlabTile":
        nbt_1182, extra_props, warnings = convert_slab_nbt(te_nbt, metadata)
    elif te_id == "RCStairTile":
        nbt_1182, extra_props, warnings = convert_stair_nbt(te_nbt, metadata)
    else:
        # Generic machine inventory preservation
        nbt_1182, warnings = convert_machine_inventory_nbt(te_nbt)

    result["nbt_1182"] = nbt_1182
    result["blockstate_props"].update(extra_props)
    result["warnings"].extend(warnings)

    # Dodaj ostrzeżenie o konwerterze z mappingu
    if mapping.notes and "lossy" in mapping.notes.lower():
        result["warnings"].append(f"RC-W-LOSSY: {mapping.notes}")

    return result
