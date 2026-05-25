"""Routes 1.7.10 TileEntities to the appropriate mod converter and produces Event JSON dicts.

Usage:
    from converters.router import convert_te_to_events

    events = convert_te_to_events(
        te_nbt=te,
        block_numeric_id=block_id,
        metadata=meta,
        global_pos=(x, y, z),
    )
    # events is a list of dicts ready for JSON serialisation (one line per event in .jsonl)

Mod detection is based on the TE's `id` field from the 1.7.10 NBT.
Unknown mods fall back to the placeholder system (conversion_placeholders:block_entity_placeholder).
"""
from __future__ import annotations

from typing import Any

from converters.common.placeholders import make_block_entity_placeholder_event

# ──────────────────────────────────────────────────────────────────────────────
# Lazy converter singletons — imported only when first needed so that missing
# optional deps (numpy etc.) don't crash the whole pipeline.
# ──────────────────────────────────────────────────────────────────────────────

_instances: dict[str, Any] = {}


def _ae2():
    if "ae2" not in _instances:
        from converters.ae2.ae2_converter import AE2Converter
        _instances["ae2"] = AE2Converter()
    return _instances["ae2"]


def _mekanism():
    if "mek" not in _instances:
        from converters.mekanism.mekanism_converter import MekanismConverter
        _instances["mek"] = MekanismConverter()
    return _instances["mek"]


def _bloodmagic():
    if "bm" not in _instances:
        from converters.bloodmagic.converter import BloodMagicConverter
        _instances["bm"] = BloodMagicConverter()
    return _instances["bm"]


def _enchanting():
    if "ep" not in _instances:
        from converters.enchantingplus.enchantingplus_converter import EnchantingPlusConverter
        _instances["ep"] = EnchantingPlusConverter()
    return _instances["ep"]


def _betterstorage(world_path: str | None = None):
    key = "bs"
    if key not in _instances:
        from converters.betterstorage.nbt_converter import BetterStorageConverter
        _instances[key] = BetterStorageConverter(world_path=world_path)
    return _instances[key]


def _thermal_dynamics():
    if "td" not in _instances:
        from converters.thermal_dynamics.thermal_dynamics_converter import ThermalDynamicsConverter
        _instances["td"] = ThermalDynamicsConverter()
    return _instances["td"]


def _ic2():
    if "ic2" not in _instances:
        from converters.ic2.ic2_converter import IC2Converter
        _instances["ic2"] = IC2Converter()
    return _instances["ic2"]


def _forge_multipart():
    if "forgemultipart" not in _instances:
        from converters.forge_multipart.forge_multipart_converter import ForgeMultipartConverter
        _instances["forgemultipart"] = ForgeMultipartConverter()
    return _instances["forgemultipart"]


def _projectred():
    if "projectred" not in _instances:
        from converters.projectred.projectred_converter import ProjectRedConverter
        _instances["projectred"] = ProjectRedConverter()
    return _instances["projectred"]


def _enderstorage():
    if "enderstorage" not in _instances:
        from converters.enderstorage.enderstorage_converter import EnderStorageConverter
        _instances["enderstorage"] = EnderStorageConverter()
    return _instances["enderstorage"]


def _thermal():
    if "thermal" not in _instances:
        from converters.thermal.thermal_converter import ThermalConverter
        _instances["thermal"] = ThermalConverter()
    return _instances["thermal"]


def _buildcraft():
    if "buildcraft" not in _instances:
        from converters.buildcraft.buildcraft_converter import BuildCraftConverter
        _instances["buildcraft"] = BuildCraftConverter()
    return _instances["buildcraft"]


def _mrcrayfish():
    if "mrcrayfish" not in _instances:
        from converters.mrcrayfish_furniture.mrcrayfish_converter import MrCrayfishConverter
        _instances["mrcrayfish"] = MrCrayfishConverter()
    return _instances["mrcrayfish"]


def _bibliocraft():
    if "bibliocraft" not in _instances:
        from converters.bibliocraft.nbt_converter import BiblioCraftNBTConverter
        _instances["bibliocraft"] = BiblioCraftNBTConverter()
    return _instances["bibliocraft"]


def _jammyfurniture():
    if "jammyfurniture" not in _instances:
        from converters.jammyfurniture.jammyfurniture_converter import JammyFurnitureConverter
        _instances["jammyfurniture"] = JammyFurnitureConverter()
    return _instances["jammyfurniture"]


def _growthcraft():
    if "growthcraft" not in _instances:
        from converters.growthcraft.growthcraft_converter import GrowthcraftConverter
        _instances["growthcraft"] = GrowthcraftConverter()
    return _instances["growthcraft"]


def _railcraft():
    if "railcraft" not in _instances:
        from converters.railcraft.railcraft_converter import RailcraftConverter
        _instances["railcraft"] = RailcraftConverter()
    return _instances["railcraft"]


def _enderstorage():
    if "enderstorage" not in _instances:
        from converters.enderstorage.enderstorage_converter import EnderStorageConverter
        _instances["enderstorage"] = EnderStorageConverter()
    return _instances["enderstorage"]


def _bigreactors():
    if "bigreactors" not in _instances:
        from converters.bigreactors.biggerreactors_converter import BiggerReactorsConverter
        _instances["bigreactors"] = BiggerReactorsConverter()
    return _instances["bigreactors"]


# ──────────────────────────────────────────────────────────────────────────────
# Mod detection
# ──────────────────────────────────────────────────────────────────────────────

_AE2_TE_KEYWORDS = frozenset([
    "Controller", "Drive", "Chest", "Interface", "Molecular",
    "Crafting", "Cable", "Energy", "IOPort", "Inscriber",
    "Charger", "Security", "Quantum", "Spatial", "Condenser",
    "Vibration", "SkyChest", "Wireless", "Growth",
])

_BLOODMAGIC_TE_IDS = frozenset([
    "containerAltar", "containerMasterStone", "BPAltar",
])

_CARPENTERS_TE_IDS = frozenset([
    "TileEntityCarpentersBlock",
    "te.skinnable", "te.skinnableChild",
    "te.mannequin", "te.armourLibrary",
])

_CFM_PREFIXES = (
    "cfm", "TileEntityBath", "TileEntityKitchen",
    "TileEntitySofa", "TileEntityCabinet",
)

_BIBLIOCRAFT_PREFIXES = (
    "TileEntityFilingCabinet", "TileEntityBookcase", "TileEntitySeat",
    "TileEntityLabel", "TileEntityPrintingPress", "TileEntityTypeMachine",
    "TileEntityMap", "TileEntityAtlas", "TileEntityLantern",
    "TileEntityBiblioDesk",
)

# TE ids that belong to vanilla Minecraft — Amulet handles these; skip them.
VANILLA_TE_IDS = frozenset([
    "Chest", "TrappedChest", "Furnace", "Brewing", "Dropper", "Dispenser",
    "Hopper", "Beacon", "Jukebox", "MobSpawner", "Sign", "Skull",
    "Banner", "Comparator", "Cauldron", "EnchantTable", "EndPortal",
    "Control", "RecordPlayer", "Music", "Piston", "FlowerPot",
    "noteblock", "DLDetector",
])


def detect_mod(te_id: str) -> str:
    """Return a short mod key for te_id, or 'vanilla' / 'unknown'."""
    if not te_id:
        return "unknown"

    bare = te_id.split(":")[-1]  # strip namespace prefix if present

    if bare in VANILLA_TE_IDS or te_id.startswith("minecraft:"):
        return "vanilla"

    # Applied Energistics 2
    if te_id.startswith("Block") and any(kw in te_id for kw in _AE2_TE_KEYWORDS):
        return "ae2"

    if te_id.startswith("Mekanism:") or te_id.startswith("mekanism:"):
        return "mekanism"

    if te_id in ("DigitalMiner", "QuantumEntangloporter", "EnergyCube", "GasTank", "Bin"):
        return "mekanism"

    if bare in _BLOODMAGIC_TE_IDS or te_id.startswith("AWWayofTime:"):
        return "bloodmagic"

    if te_id.startswith("eplus:"):
        return "enchantingplus"

    # Carpenter's Blocks
    if te_id in _CARPENTERS_TE_IDS:
        return "carpentersblocks"

    # ProjectRed (multiparts, illumination, etc.)
    if te_id == "savedMultipart" or te_id.startswith("tile.projectred.") or te_id.startswith("ProjectRed"):
        return "projectred"

    # Better Storage  (TE id format: container.betterstorage.<type>)
    if te_id.startswith("container.betterstorage.") or te_id.lower().startswith("betterstorage"):
        return "betterstorage"

    # MrCrayfish's Furniture Mod
    if te_id.lower().startswith("cfm") or any(te_id.startswith(p) for p in _CFM_PREFIXES):
        return "mrcraysfish_furniture"

    # BiblioCraft
    if any(te_id.startswith(p) for p in _BIBLIOCRAFT_PREFIXES) or te_id.startswith("BiblioCraft"):
        return "bibliocraft"

    if te_id in _BIBLIO_TE_TO_BLOCK:
        return "bibliocraft"

    # Railcraft
    if te_id.startswith("RC") or te_id.startswith("Railcraft") or te_id == "drum":
        return "railcraft"

    # CustomNPCs
    if te_id.startswith("TileNPC"):
        return "customnpcs"

    # Thaumcraft
    if te_id.startswith("TileMirror") or te_id.startswith("TileThaumcraft") or te_id.startswith("thaumcraft"):
        return "thaumcraft"

    # ComputerCraft
    if te_id in ("monitor", "computer", "turtle", "drive", "speaker"):
        return "computercraft"

    # GrowthCraft
    if te_id.startswith("grc.") or te_id.startswith("Growthcraft"):
        return "growthcraft"

    # Ender Storage
    if te_id.startswith("EnderStorage") or te_id.startswith("enderStorage") or te_id in ("Ender Chest", "Ender Tank"):
        return "enderstorage"

    # Jammy Furniture
    if te_id.startswith("JammyFurniture") or te_id.startswith("jammy") or te_id in _JAMMY_TE_TO_BLOCK:
        return "jammyfurniture"

    # Thermal Dynamics
    if te_id.startswith("thermaldynamics."):
        return "thermaldynamics"

    if te_id.startswith("thermalexpansion.") or te_id.startswith("thermalfoundation."):
        return "thermal"

    # BuildCraft
    if "buildcraft" in te_id.lower():
        return "buildcraft"

    # ForgeMultipart bounding helpers
    if te_id == "AdvancedBoundingBlock" or te_id == "BoundingBlock":
        return "forgemultipart"

    # Generic wooden/ceramic decorative blocks (various mods)
    if te_id.startswith("TileEntityWoodBlocks") or te_id.startswith("TileEntityCeramicBlocks"):
        return "decorative_blocks"

    # Misc furniture/prop tiles without clear prefix
    if te_id in ("TableTile", "LampTile", "seatTile"):
        return "furniture_misc"

    # IndustrialCraft 2. IC2 experimental commonly stores Forge registry ids
    # such as "Macerator", "Cable", and "TECrop", not TileEntity* class names.
    if _is_ic2_te_id(te_id):
        return "ic2"

    # Big Reactors / Bigger Reactors
    if te_id.startswith("BR") and _is_bigreactors_te_id(te_id):
        return "bigreactors"

    return "unknown"


_IC2_TE_IDS: frozenset[str] | None = None


def _ic2_te_ids() -> frozenset[str]:
    global _IC2_TE_IDS
    if _IC2_TE_IDS is None:
        from converters.ic2.mappings.block_inventory import IC2_ALL_BLOCKS
        ids = set()
        for block_id, variants in IC2_ALL_BLOCKS.items():
            for meta, info in variants.items():
                te = info.get("te_class")
                if te:
                    ids.add(te)
        _IC2_TE_IDS = frozenset(ids)
    return _IC2_TE_IDS


def _is_bigreactors_te_id(te_id: str) -> bool:
    from converters.bigreactors.mappings import is_bigreactors_te_id
    return is_bigreactors_te_id(te_id)


def _is_ic2_te_id(te_id: str) -> bool:
    from converters.ic2.mappings.block_mappings import is_ic2_te_id
    return is_ic2_te_id(te_id)


# ──────────────────────────────────────────────────────────────────────────────
# Per-converter serialisers
# ──────────────────────────────────────────────────────────────────────────────

def _ae2_to_events(result: Any) -> list[dict]:
    """Serialise AE2BlockConversion → Event JSON list."""
    c = result.converted
    if not c.success or not c.block_id_1182:
        return []

    pos = list(result.original_pos)
    ev: dict = {"pos": pos, "block": c.block_id_1182}
    if c.nbt_1182:
        ev["op"] = "set_block_entity"
        ev["nbt"] = c.nbt_1182
    else:
        ev["op"] = "set_block"
    if c.blockstate_props:
        ev["blockstate"] = c.blockstate_props

    events = [ev]
    for extra in (c.additional_blocks or []):
        events.extend(_ae2_to_events(extra))
    return events


def _mekanism_to_events(result: Any) -> list[dict]:
    """Serialise MekanismBlockConversion → Event JSON list."""
    c = result.converted
    if not c.success or not c.block_id_1182:
        return []

    pos = list(result.original_pos)
    ev: dict = {"pos": pos, "block": c.block_id_1182}
    if c.nbt_1182:
        ev["op"] = "set_block_entity"
        ev["nbt"] = c.nbt_1182
    else:
        ev["op"] = "set_block"
    if c.blockstate_props:
        ev["blockstate"] = c.blockstate_props
    return [ev]


def _bloodmagic_to_events(result: Any, pos: tuple[int, int, int]) -> list[dict]:
    """Serialise BloodMagic ConversionResult → Event JSON list."""
    if not result.converted or not result.block_id_1182:
        return []

    ev: dict = {"pos": list(pos), "block": result.block_id_1182}
    nbt = result.be_nbt_1182
    if nbt:
        ev["op"] = "set_block_entity"
        ev["nbt"] = nbt
    else:
        ev["op"] = "set_block"
    if result.blockstate_props:
        ev["blockstate"] = result.blockstate_props

    events = [ev]
    for extra in (result.extra_blocks or []):
        if not isinstance(extra, dict):
            continue
        epos = extra.get("pos") or list(pos)
        if not isinstance(epos, list):
            epos = list(epos)
        eid = extra.get("block_id_1182", "")
        if not eid:
            continue
        enbt = extra.get("nbt") or extra.get("be_nbt_1182")
        eev: dict = {"pos": epos, "block": eid}
        if enbt:
            eev["op"] = "set_block_entity"
            eev["nbt"] = enbt
        else:
            eev["op"] = "set_block"
        events.append(eev)
    return events


def _ic2_to_events(result: Any) -> list[dict]:
    """Serialise IC2BlockConversion -> Event JSON list."""
    c = result.converted
    if not c.success or not c.block_id_1182:
        return []

    pos = list(result.original_pos)
    ev: dict = {"pos": pos, "block": c.block_id_1182}
    if c.nbt_1182:
        ev["op"] = "set_block_entity"
        ev["nbt"] = c.nbt_1182
    else:
        ev["op"] = "set_block"
    if c.blockstate_props:
        ev["blockstate"] = c.blockstate_props
    return [ev]


def _projectred_to_events(result: Any) -> list[dict]:
    """Serialise ProjectRedBlockConversion -> Event JSON list."""
    c = result.converted
    if not c.success or c.removed or not c.block_id_1182:
        return []

    pos = list(result.original_pos)
    ev: dict = {"pos": pos, "block": c.block_id_1182}
    if c.nbt_1182:
        ev["op"] = "set_block_entity"
        ev["nbt"] = c.nbt_1182
    else:
        ev["op"] = "set_block"
    if c.blockstate_props:
        ev["blockstate"] = c.blockstate_props
    return [ev]


def _conversion_event_to_events(event: Any) -> list[dict]:
    """Serialise converters.common.conversion_event.ConversionEvent -> Event JSON."""
    if event is None:
        return []

    if getattr(event, "event_type", None) == "remove":
        pos = getattr(event, "position", None)
        if pos is None:
            return []
        return [{"op": "set_block", "pos": list(pos), "block": "minecraft:air"}]

    ev = event.to_set_block_event()
    return [ev] if ev else []


def _simple_dict_to_events(result: dict, pos: tuple[int, int, int]) -> list[dict]:
    """Serialise simple dict converter output to Event JSON."""
    block_id = result.get("target_block_id") or result.get("block_id")
    if not block_id:
        return []

    ev: dict = {
        "op": "set_block_entity" if result.get("target_nbt") or result.get("nbt") else "set_block",
        "pos": list(pos),
        "block": block_id,
    }
    nbt = result.get("target_nbt") or result.get("nbt")
    if nbt:
        ev["nbt"] = nbt
    blockstate = result.get("target_blockstate") or result.get("blockstate") or {}
    if blockstate:
        ev["blockstate"] = blockstate
    return [ev]


def _converted_block_to_events(result: Any, pos: tuple[int, int, int]) -> list[dict]:
    """Serialise BiblioCraft ConvertedBlock -> Event JSON."""
    if not result or not getattr(result, "block_id", None):
        return []
    ev: dict = {
        "op": "set_block_entity" if getattr(result, "tile_entity", None) else "set_block",
        "pos": [getattr(result, "x", pos[0]), getattr(result, "y", pos[1]), getattr(result, "z", pos[2])],
        "block": result.block_id,
    }
    if getattr(result, "tile_entity", None):
        ev["nbt"] = result.tile_entity
    blockstate = getattr(result, "block_state", {}) or {}
    if blockstate:
        ev["blockstate"] = blockstate
    return [ev]


def _jammy_to_events(result: Any, pos: tuple[int, int, int]) -> list[dict]:
    """Serialise JammyFurniture ConversionResult -> Event JSON."""
    if not result or not result.success or not result.target_block_id:
        return []
    ev: dict = {
        "op": "set_block_entity" if result.target_te else "set_block",
        "pos": list(pos),
        "block": result.target_block_id,
    }
    if result.target_te:
        nbt = dict(result.target_te)
        nbt.setdefault("x", pos[0])
        nbt.setdefault("y", pos[1])
        nbt.setdefault("z", pos[2])
        ev["nbt"] = nbt
    if result.target_block_state:
        ev["blockstate"] = result.target_block_state
    return [ev]


def _thermal_dynamics_to_events(result: Any) -> list[dict]:
    """Serialise TDBlockConversion -> Event JSON list."""
    c = result.converted
    if not c.success or not c.block_id_1182:
        return []

    pos = list(result.original_pos)
    ev: dict = {"pos": pos, "block": c.block_id_1182}
    if c.nbt_1182:
        ev["op"] = "set_block_entity"
        ev["nbt"] = c.nbt_1182
    else:
        ev["op"] = "set_block"
    if c.blockstate_props:
        ev["blockstate"] = c.blockstate_props

    events = [ev]

    # Dodatkowe itemy z załączników -> inventory placeholder obok bloku
    if c.extra_items:
        placeholder_ev = make_block_entity_placeholder_event(
            position=(pos[0], pos[1] + 1, pos[2]),
            source_mod="ThermalDynamics",
            source_te_id=result.original_id,
            source_metadata=result.metadata,
            original_nbt={"Items": c.extra_items},
            conversion_reason="attachment_drop",
            inventory_placeholder=True,
        )
        events.append(placeholder_ev)

    return events


def _forge_multipart_to_events(result: Any) -> list[dict]:
    """Serialise ForgeMultipartConversion -> Event JSON list."""
    c = result.converted
    if not c.success or not c.block_id_1182:
        return []

    ev: dict = {
        "op": "set_block_entity" if c.nbt_1182 else "set_block",
        "pos": list(result.original_pos),
        "block": c.block_id_1182,
    }
    if c.nbt_1182:
        ev["nbt"] = c.nbt_1182
    if c.blockstate_props:
        ev["blockstate"] = c.blockstate_props
    if c.warnings:
        ev["warnings"] = list(c.warnings)
    return [ev]


def _generic_to_events(result: Any, pos: tuple[int, int, int]) -> list[dict]:
    """Generic serialiser for converters with a 'converted' sub-object (AE2/Mekanism style)."""
    inner = getattr(result, "converted", result)
    success = getattr(inner, "success", getattr(inner, "converted", False))
    block_id = getattr(inner, "block_id_1182", None)
    if not success or not block_id:
        return []

    nbt = getattr(inner, "nbt_1182", None) or getattr(inner, "be_nbt_1182", None)
    blockstate = getattr(inner, "blockstate_props", {}) or {}
    actual_pos = list(getattr(result, "original_pos", pos))

    ev: dict = {"pos": actual_pos, "block": block_id}
    if nbt:
        ev["op"] = "set_block_entity"
        ev["nbt"] = nbt
    else:
        ev["op"] = "set_block"
    if blockstate:
        ev["blockstate"] = blockstate
    return [ev]


def _buildcraft_to_events(result: Any) -> list[dict]:
    """Serialise BuildCraftBlockConversion -> Event JSON list."""
    c = result.converted
    if not c.success:
        return []

    pos = list(result.original_pos)
    block_id = c.block_id_1182
    if not block_id:
        return []

    # REMOVE action -> air
    if block_id == "minecraft:air":
        return [{"op": "set_block", "pos": pos, "block": "minecraft:air"}]

    ev: dict = {"pos": pos, "block": block_id}
    if c.nbt_1182:
        ev["op"] = "set_block_entity"
        ev["nbt"] = c.nbt_1182
    else:
        ev["op"] = "set_block"
    if c.blockstate_props:
        ev["blockstate"] = dict(c.blockstate_props)
    if c.warnings:
        ev["warnings"] = list(c.warnings)
    return [ev]


def _biggerreactors_to_events(result: Any) -> list[dict]:
    """Serialise BiggerReactorsBlockConversion -> Event JSON list."""
    c = result.converted
    if not c.success:
        return []

    pos = list(result.original_pos)
    block_id = c.block_id_1182
    if not block_id:
        return []

    # REMOVE action -> air
    if block_id == "minecraft:air":
        return [{"op": "set_block", "pos": pos, "block": "minecraft:air"}]

    ev: dict = {"pos": pos, "block": block_id}
    if c.nbt_1182:
        ev["op"] = "set_block_entity"
        ev["nbt"] = c.nbt_1182
    else:
        ev["op"] = "set_block"
    if c.blockstate_props:
        ev["blockstate"] = dict(c.blockstate_props)
    if c.warnings:
        ev["warnings"] = list(c.warnings)
    return [ev]


# ──────────────────────────────────────────────────────────────────────────────
# Blood Magic block_id_1710 mapping
# ──────────────────────────────────────────────────────────────────────────────

_BM_TE_TO_BLOCK: dict[str, str] = {
    "containerAltar": "AWWayofTime:blockBloodAltar",
    "BPAltar":        "AWWayofTime:blockBloodAltar",
    "containerMasterStone": "AWWayofTime:blockMasterStone",
}


_CFM_TE_TO_BLOCK: dict[str, str] = {
    "cfmFridge": "cfm:fridge",
    "cfmFreezer": "cfm:freezer",
    "cfmCabinetKitchen": "cfm:kitchencabinet",
    "cfmCounterSink": "cfm:countersink",
    "cfmCabinet": "cfm:cabinet",
    "cfmBedsideCabinet": "cfm:bedsidecabinet",
    "cfmMailBox": "cfm:mailbox",
    "cfmBin": "cfm:bin",
    "cfmWallCabinet": "cfm:wallcabinet",
    "cfmBasin": "cfm:basin",
    "cfmBath": "cfm:bath1",
    "TileEntityBath": "cfm:bath1",
    "cfmMicrowave": "cfm:microwave",
    "cfmOven": "cfm:oven",
    "cfmPrinter": "cfm:printer",
}


_JAMMY_TE_TO_BLOCK: dict[str, str] = {
    "TileEntityWoodBlocksOne": "jammyfurniture:WoodBlocksOne",
    "TileEntityWoodBlocksTwo": "jammyfurniture:WoodBlocksTwo",
    "TileEntityWoodBlocksThree": "jammyfurniture:WoodBlocksThree",
    "TileEntityWoodBlocksFour": "jammyfurniture:WoodBlocksFour",
    "TileEntityIronBlocksOne": "jammyfurniture:IronBlocksOne",
    "TileEntityIronBlocksTwo": "jammyfurniture:IronBlocksTwo",
    "TileEntityCeramicBlocksOne": "jammyfurniture:CeramicBlocksOne",
    "TileEntityBath": "jammyfurniture:Bath",
    "TileEntityLightsOn": "jammyfurniture:LightsOn",
    "TileEntityLightsOff": "jammyfurniture:LightsOff",
    "TileEntitySofa": "jammyfurniture:Sofa",
    "TileEntityMobHeads": "jammyfurniture:MobHeads",
}


_BIBLIO_TE_TO_BLOCK: dict[str, str] = {
    "BookcaseTile": "BiblioCraft:Bookcase",
    "GenericShelfTile": "BiblioCraft:GenericShelf",
    "PotionShelfTile": "BiblioCraft:PotionShelf",
    "ToolRackTile": "BiblioCraft:WeaponRack",
    "WeaponCaseTile": "BiblioCraft:WeaponCase",
    "SwordPedestalTile": "BiblioCraft:SwordPedestal",
    "TableTile": "BiblioCraft:Table",
    "CookieJarTile": "BiblioCraft:CookieJar",
    "dinnerPlateTile": "BiblioCraft:DinnerPlate",
    "FramedChestTile": "BiblioCraft:FramedChest",
    "ArmorStandTile": "BiblioCraft:ArmorStand",
    "biblioPaintingTile": "BiblioCraft:Painting",
    "WoodLabelTile": "BiblioCraft:Label",
    "biblioClipboardTile": "BiblioCraft:Clipboard",
    "DiscRackTile": "BiblioCraft:DiscRack",
    "biblioClockTile": "BiblioCraft:Clock",
    "fancySignTile": "BiblioCraft:FancySign",
    "MapFrameTile": "BiblioCraft:MapFrame",
    "LanternTile": "BiblioCraft:Lantern",
    "LampTile": "BiblioCraft:Lamp",
}


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def convert_te_to_events(
    te_nbt: dict[str, Any],
    block_numeric_id: int,
    metadata: int,
    global_pos: tuple[int, int, int],
) -> list[dict[str, Any]]:
    """Convert a single 1.7.10 TileEntity NBT dict into Event JSON dicts.

    Returns an empty list if the TE is vanilla (handled by Amulet) or has no
    id field.  Returns a placeholder event if no converter is available or if
    the converter raises an exception.
    """
    te_id = str(te_nbt.get("id", ""))
    if not te_id:
        return []

    if te_id == "savedMultipart" and not _saved_multipart_is_projectred_only(te_nbt):
        result = _forge_multipart().convert_block(
            block_id_1710="ForgeMultipart:block",
            metadata=metadata,
            nbt_1710=te_nbt,
            position=global_pos,
        )
        events = _forge_multipart_to_events(result)
        if not events:
            return [_placeholder(te_id, "forgemultipart", metadata, te_nbt, global_pos, "converter_returned_empty")]
        return events

    mod = detect_mod(te_id)
    if mod == "vanilla":
        return []

    try:
        if mod == "ae2":
            block_id_1710 = f"appliedenergistics2:tile.{te_id}"
            result = _ae2().convert_block(
                block_id_1710=block_id_1710,
                nbt_1710=te_nbt,
                metadata=metadata,
                position=global_pos,
            )
            events = _ae2_to_events(result)
            if not events:
                return [_placeholder(te_id, mod, metadata, te_nbt, global_pos, "converter_returned_empty")]
            return events

        if mod == "mekanism":
            result = _mekanism().convert_block(
                block_id_1710=te_id,
                metadata=metadata,
                nbt_1710=te_nbt,
                position=global_pos,
            )
            events = _mekanism_to_events(result)
            if not events:
                return [_placeholder(te_id, mod, metadata, te_nbt, global_pos, "converter_returned_empty")]
            return events

        if mod == "bloodmagic":
            bare = te_id.split(":")[-1]
            block_id_1710 = _BM_TE_TO_BLOCK.get(bare, f"AWWayofTime:{bare}")
            result = _bloodmagic().convert_block(
                block_id_1710=block_id_1710,
                metadata=metadata,
                te_nbt_1710=te_nbt,
                pos=global_pos,
                owner_uuid=None,
            )
            events = _bloodmagic_to_events(result, global_pos)
            if not events:
                return [_placeholder(te_id, mod, metadata, te_nbt, global_pos, "converter_returned_empty")]
            return events

        if mod == "enchantingplus":
            result = _enchanting().convert_block(
                block_id_1710=te_id,
                nbt_1710=te_nbt,
                metadata=metadata,
                position=global_pos,
            )
            events = _generic_to_events(result, global_pos)
            if not events:
                return [_placeholder(te_id, mod, metadata, te_nbt, global_pos, "converter_returned_empty")]
            return events

        if mod == "betterstorage":
            x, y, z = global_pos
            try:
                result = _betterstorage().convert_tile_entity(
                    block_id=te_id,
                    nbt_data=te_nbt,
                    x=x, y=y, z=z,
                )
                new_block = result.get("block_id", "")
                new_nbt = result.get("nbt")
                if new_block and new_block != "minecraft:air":
                    ev: dict = {"pos": list(global_pos), "block": new_block}
                    if new_nbt:
                        ev["op"] = "set_block_entity"
                        ev["nbt"] = new_nbt
                    else:
                        ev["op"] = "set_block"
                    return [ev]
            except Exception as exc:
                return [_placeholder(te_id, mod, metadata, te_nbt, global_pos,
                                     f"converter_error:{type(exc).__name__}:{exc}")]
            return [_placeholder(te_id, mod, metadata, te_nbt, global_pos, "converter_returned_empty")]

        if mod == "thermaldynamics":
            result = _thermal_dynamics().convert_tile_entity(
                te_id=te_id,
                nbt_1710=te_nbt,
                metadata=metadata,
                position=global_pos,
            )
            events = _thermal_dynamics_to_events(result)
            if not events:
                return [_placeholder(te_id, mod, metadata, te_nbt, global_pos, "converter_returned_empty")]
            return events

        if mod == "ic2":
            result = _ic2().convert_tile_entity(
                te_id=te_id,
                nbt_1710=te_nbt,
                metadata=metadata,
                position=global_pos,
            )
            events = _ic2_to_events(result)
            if not events:
                return [_placeholder(te_id, mod, metadata, te_nbt, global_pos, "converter_returned_empty")]
            return events

        if mod == "projectred":
            if te_id == "savedMultipart":
                events: list[dict[str, Any]] = []
                unsupported_parts: list[str] = []
                raw_parts = te_nbt.get("parts") or te_nbt.get("savedParts") or []
                for part in raw_parts:
                    if not isinstance(part, dict):
                        continue
                    part_type = str(part.get("id", ""))
                    if not _projectred().is_projectred_multipart(part_type):
                        unsupported_parts.append(part_type or "<empty>")
                        continue
                    result = _projectred().convert_multipart(
                        part_type=part_type,
                        nbt_1710=part,
                        position=global_pos,
                    )
                    events.extend(_projectred_to_events(result))
                if events:
                    return events
                reason = "no_supported_projectred_parts"
                if unsupported_parts:
                    reason += ":" + ",".join(sorted(set(unsupported_parts))[:5])
                return [_placeholder(te_id, mod, metadata, te_nbt, global_pos, reason)]

            if te_id.startswith("tile.projectred.illumination.lamp"):
                lamp_meta = metadata
                if "|" in te_id:
                    try:
                        lamp_meta = int(te_id.rsplit("|", 1)[1])
                    except ValueError:
                        lamp_meta = metadata
                result = _projectred().convert_block(
                    block_id_1710="ProjRed|Illumination:projectred.illumination.lamp",
                    nbt_1710=te_nbt,
                    metadata=lamp_meta,
                    position=global_pos,
                )
                events = _projectred_to_events(result)
                if not events:
                    return [_placeholder(te_id, mod, metadata, te_nbt, global_pos, "converter_returned_empty")]
                return events

            return [_placeholder(te_id, mod, metadata, te_nbt, global_pos, "unsupported_projectred_te")]

        if mod == "thermal":
            result = _thermal().convert_te_by_id(te_id, te_nbt, global_pos)
            events = _simple_dict_to_events(result, global_pos)
            if not events:
                return [_placeholder(te_id, mod, metadata, te_nbt, global_pos, "converter_returned_empty")]
            return events

        if mod == "mrcraysfish_furniture":
            block_id = _CFM_TE_TO_BLOCK.get(te_id, te_id)
            event = _mrcrayfish().convert_tile_entity(
                te_nbt=te_nbt,
                block_id=block_id,
                metadata=metadata,
                position=global_pos,
            )
            events = _conversion_event_to_events(event)
            if not events:
                return [_placeholder(te_id, mod, metadata, te_nbt, global_pos, "converter_returned_empty")]
            return events

        if mod in ("jammyfurniture", "decorative_blocks"):
            block_id = _JAMMY_TE_TO_BLOCK.get(te_id, te_id)
            result = _jammyfurniture().convert_block(
                source_block_name=block_id,
                source_metadata=metadata,
                tile_entity=te_nbt,
            )
            events = _jammy_to_events(result, global_pos)
            if not events:
                return [_placeholder(te_id, mod, metadata, te_nbt, global_pos, "converter_returned_empty")]
            return events

        if mod in ("bibliocraft", "furniture_misc"):
            block_id = _BIBLIO_TE_TO_BLOCK.get(te_id, te_id)
            result = _bibliocraft().convert_tile_entity(te_nbt, block_id, global_pos)
            events = _converted_block_to_events(result, global_pos)
            if not events:
                return [_placeholder(te_id, mod, metadata, te_nbt, global_pos, "converter_returned_empty")]
            return events

        if mod == "growthcraft":
            gc = _growthcraft()
            block_id = gc.TE_ID_TO_BLOCK_ID.get(te_id, te_id)
            result = gc.convert_block(block_id=block_id, metadata=metadata, nbt=te_nbt)
            events = _generic_to_events(result, global_pos)
            if not events:
                return [_placeholder(te_id, mod, metadata, te_nbt, global_pos, "converter_returned_empty")]
            return events

        if mod == "enderstorage":
            result = _enderstorage().convert_tile_entity(
                te_id=te_id,
                nbt_1710=te_nbt,
                metadata=metadata,
                position=global_pos,
            )
            events = _generic_to_events(result, global_pos)
            if not events:
                return [_placeholder(te_id, mod, metadata, te_nbt, global_pos, "converter_returned_empty")]
            return events

        if mod == "railcraft":
            result = _railcraft().convert_tile_entity(
                te_id=te_id,
                nbt_1710=te_nbt,
                metadata=metadata,
                position=global_pos,
            )
            events = _generic_to_events(result, global_pos)
            if not events:
                return [_placeholder(te_id, mod, metadata, te_nbt, global_pos, "converter_returned_empty")]
            return events

        if mod == "buildcraft":
            result = _buildcraft().convert_tile_entity(
                te_id=te_id,
                nbt_1710=te_nbt,
                metadata=metadata,
                position=global_pos,
            )
            events = _buildcraft_to_events(result)
            if not events:
                return [_placeholder(te_id, mod, metadata, te_nbt, global_pos, "converter_returned_empty")]
            return events

        if mod == "bigreactors":
            result = _bigreactors().convert_block(
                block_id_1710=te_id,
                metadata=metadata,
                nbt_1710=te_nbt,
                position=global_pos,
            )
            events = _biggerreactors_to_events(result)
            if not events:
                return [_placeholder(te_id, mod, metadata, te_nbt, global_pos, "converter_returned_empty")]
            return events

        # All other known-but-unimplemented mods and truly unknown ones
        return [_placeholder(te_id, mod, metadata, te_nbt, global_pos, "no_converter")]

    except Exception as exc:
        return [_placeholder(
            te_id, mod, metadata, te_nbt, global_pos,
            f"converter_error:{type(exc).__name__}:{exc}",
        )]


def _placeholder(
    te_id: str,
    mod: str,
    metadata: int,
    te_nbt: dict,
    pos: tuple[int, int, int],
    reason: str,
) -> dict:
    return make_block_entity_placeholder_event(
        position=pos,
        source_mod=mod,
        source_te_id=te_id,
        source_metadata=metadata,
        original_nbt=te_nbt,
        conversion_reason=reason,
    )


def _saved_multipart_is_projectred_only(te_nbt: dict[str, Any]) -> bool:
    """Return true when a savedMultipart contains only ProjectRed parts."""
    raw_parts = te_nbt.get("parts") or te_nbt.get("savedParts") or []
    if not raw_parts:
        return False
    for part in raw_parts:
        if not isinstance(part, dict):
            return False
        part_type = str(part.get("id", ""))
        if not _projectred().is_projectred_multipart(part_type):
            return False
    return True
