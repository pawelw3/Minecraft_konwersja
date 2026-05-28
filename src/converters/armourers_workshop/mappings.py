"""Source-backed mappings for Armourer's Workshop 1.7.10 -> 1.18.2."""

from __future__ import annotations

from dataclasses import dataclass, field


SOURCE_MOD_ID = "armourersworkshop"
TARGET_MOD_ID = "armourers_workshop"


@dataclass(frozen=True)
class BlockMapping:
    """A direct block/BE mapping with conversion policy notes."""

    source_name: str
    target_block_id: str | None
    source_te_id: str | None = None
    target_te_id: str | None = None
    policy: str = "remap"
    warnings: tuple[str, ...] = field(default_factory=tuple)


def aw_block(path: str) -> str:
    return f"{TARGET_MOD_ID}:{path}"


def aw_be(path: str) -> str:
    return f"{TARGET_MOD_ID}:{path}"


# Evidence:
# 1.7.10 LibBlockNames.java uses camelCase registry fragments and TE ids
# registered as "te." + fragment.
# 1.18.2 ModBlocks.java / ModConstants.java use the hyphenated ids below.
BLOCK_MAPPINGS: dict[str, BlockMapping] = {
    "armourLibrary": BlockMapping(
        "armourLibrary",
        aw_block("skin-library"),
        "te.armourLibrary",
        aw_be("skin-library"),
    ),
    "globalSkinLibrary": BlockMapping(
        "globalSkinLibrary",
        aw_block("skin-library-global"),
        "te.globalSkinLibrary",
        aw_be("skin-library-global"),
    ),
    "skinningTable": BlockMapping(
        "skinningTable",
        aw_block("skinning-table"),
        "te.skinningTable",
        aw_be("skinning-table"),
    ),
    "dyeTable": BlockMapping(
        "dyeTable",
        aw_block("dye-table"),
        "te.dyeTable",
        aw_be("dye-table"),
    ),
    "colourMixer": BlockMapping(
        "colourMixer",
        aw_block("colour-mixer"),
        "te.colourMixer",
        aw_be("colour-mixer"),
    ),
    "armourerBrain": BlockMapping(
        "armourerBrain",
        aw_block("armourer"),
        "te.armourerBrain",
        aw_be("armourer"),
        warnings=("AW-W-ARMOURER-WORKSPACE-REBUILD: builder area/palette data needs source-backed follow-up.",),
    ),
    "hologramProjector": BlockMapping(
        "hologramProjector",
        aw_block("hologram-projector"),
        "te.hologramProjector",
        aw_be("hologram-projector"),
        warnings=("AW-W-HOLOGRAM-INVENTORY-RESCUE: skin item stack conversion is staged after item converter.",),
    ),
    "outfit_maker": BlockMapping(
        "outfit_maker",
        aw_block("outfit-maker"),
        None,
        None,
        warnings=("AW-W-OUTFIT-MAKER-NBT-REVIEW: 1.18.2 has outfit-maker BE, but no 1.7.10 TE sample was found yet.",),
    ),
    "colourable": BlockMapping("colourable", aw_block("skin-cube"), "te.colourable", aw_be("skin-cube")),
    "colourableGlass": BlockMapping("colourableGlass", aw_block("skin-cube-glass")),
    "colourableGlowing": BlockMapping("colourableGlowing", aw_block("skin-cube-glowing")),
    "colourableGlassGlowing": BlockMapping("colourableGlassGlowing", aw_block("skin-cube-glass-glowing")),
    "awBoundingBox6": BlockMapping(
        "awBoundingBox6",
        aw_block("bounding-box"),
        "te.awBoundingBox6",
        aw_be("bounding-box"),
        warnings=("AW-W-BOUNDING-BOX-RELINK: builder helper bounds need parent/refer validation.",),
    ),
    "skinnable": BlockMapping(
        "skinnable",
        aw_block("skinnable"),
        "te.skinnable",
        aw_be("skinnable"),
        warnings=("AW-W-SKINNABLE-SHAPE-DEFAULT: exact Shape/Markers require converted .armour runtime read.",),
    ),
    "skinnableGlowing": BlockMapping(
        "skinnableGlowing",
        aw_block("skinnable"),
        None,
        aw_be("skinnable"),
        warnings=("AW-W-SKINNABLE-GLOWING-PROP: glow should come from SkinProperties after model conversion.",),
    ),
    "skinnableChild": BlockMapping(
        "skinnableChild",
        aw_block("skinnable"),
        "te.skinnableChild",
        aw_be("skinnable"),
        warnings=("AW-W-SKINNABLE-CHILD-REFERENCE: converted as child Refer offset; parent must also convert.",),
    ),
    "skinnableChildGlowing": BlockMapping(
        "skinnableChildGlowing",
        aw_block("skinnable"),
        None,
        aw_be("skinnable"),
        warnings=("AW-W-SKINNABLE-CHILD-GLOWING-PROP: glow should come from SkinProperties after model conversion.",),
    ),
    "mannequin": BlockMapping(
        "mannequin",
        None,
        "te.mannequin",
        None,
        "placeholder",
        ("AW-W-MANNEQUIN-ENTITY: 1.18.2 target is entity armourers_workshop:mannequin, not a block.",),
    ),
    "doll": BlockMapping(
        "doll",
        None,
        None,
        None,
        "placeholder",
        ("AW-W-DOLL-NO-BLOCK-TARGET: no 1.18.2 block registry equivalent found.",),
    ),
    "miniArmourer": BlockMapping(
        "miniArmourer",
        None,
        "te.miniArmourer",
        None,
        "placeholder",
        ("AW-W-MINI-ARMOURER-UNFINISHED: 1.7.10 mini armourer is not the main 1.18.2 builder path.",),
    ),
}


TE_TO_SOURCE_NAME = {
    mapping.source_te_id: source_name
    for source_name, mapping in BLOCK_MAPPINGS.items()
    if mapping.source_te_id is not None
}


SOURCE_BLOCK_ALIASES: dict[str, str] = {}
for source_name in BLOCK_MAPPINGS:
    SOURCE_BLOCK_ALIASES[source_name] = source_name
    SOURCE_BLOCK_ALIASES[f"block.{source_name}"] = source_name
    SOURCE_BLOCK_ALIASES[f"{SOURCE_MOD_ID}:block.{source_name}"] = source_name


def resolve_source_name(block_id: str | int, te_id: str | None = None) -> str | None:
    if te_id and te_id in TE_TO_SOURCE_NAME:
        return TE_TO_SOURCE_NAME[te_id]
    text = str(block_id)
    if text in SOURCE_BLOCK_ALIASES:
        return SOURCE_BLOCK_ALIASES[text]
    if ":" in text:
        text = text.split(":", 1)[1]
    if text.startswith("block."):
        text = text[len("block.") :]
    return text if text in BLOCK_MAPPINGS else None


# Evidence: BlockSkinnable.convertMetadataToDirection in 1.7.10 maps
# 5 east, 4 north, 3 west, 2 south, default east. 1.18.2 SkinnableBlock
# stores horizontal facing and attach face separately.
SKINNABLE_META_TO_FACING = {
    2: "south",
    3: "west",
    4: "north",
    5: "east",
}


def skinnable_blockstate(metadata: int) -> dict[str, str]:
    return {
        "facing": SKINNABLE_META_TO_FACING.get(int(metadata), "east"),
        "face": "floor",
        "lit": "false",
        "part": "head",
        "occupied": "false",
    }
