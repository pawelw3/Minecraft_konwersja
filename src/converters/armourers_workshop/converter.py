"""Armourer's Workshop 1.7.10 -> 1.18.2 conversion events."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from .mappings import (
    BLOCK_MAPPINGS,
    TARGET_MOD_ID,
    BlockMapping,
    resolve_source_name,
    skinnable_blockstate,
)
from .simulations.step2_contract_simulations import (
    SkinIdentifier1710,
    SkinPointer1710,
    migrate_skin_pointer,
    normalize_library_path,
)
from ..common.conversion_event import ConversionEvent
from ..common.placeholders import make_block_entity_placeholder_event


Position = tuple[int, int, int]


@dataclass
class ConversionResult:
    success: bool
    block_id_1182: str | None = None
    blockstate_props: dict[str, str] = field(default_factory=dict)
    nbt_1182: dict[str, Any] | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    event: ConversionEvent | None = None
    event_json: dict[str, Any] | None = None


@dataclass
class ArmourersWorkshopBlockConversion:
    original_id: str
    original_pos: Position
    metadata: int
    converted: ConversionResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "original_id": self.original_id,
            "original_pos": list(self.original_pos),
            "metadata": self.metadata,
            "new_id": self.converted.block_id_1182,
            "blockstate_props": self.converted.blockstate_props,
            "nbt": self.converted.nbt_1182,
            "errors": self.converted.errors,
            "warnings": self.converted.warnings,
            "event": self.converted.event.to_dict() if self.converted.event else self.converted.event_json,
        }


class ArmourersWorkshopConverter:
    """Converts known AW blocks and emits rescue placeholders for unsafe cases."""

    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"
    MOD = "armourers_workshop"

    def __init__(self) -> None:
        self.stats = {
            "processed": 0,
            "converted": 0,
            "placeholder": 0,
            "failed": 0,
            "warnings": 0,
        }

    def convert_block(
        self,
        block_id_1710: str | int,
        metadata: int = 0,
        nbt_1710: dict[str, Any] | None = None,
        position: Position = (0, 0, 0),
    ) -> ArmourersWorkshopBlockConversion:
        self.stats["processed"] += 1
        original_id = str(block_id_1710)
        te_id = _string_or_none((nbt_1710 or {}).get("id"))
        source_name = resolve_source_name(original_id, te_id)
        if source_name is None:
            self.stats["failed"] += 1
            result = ConversionResult(
                success=False,
                errors=[f"AW-E-NOT-ARMOURERS-WORKSHOP-BLOCK: {original_id} te={te_id or '-'}"],
            )
            return ArmourersWorkshopBlockConversion(original_id, position, int(metadata), result)

        mapping = BLOCK_MAPPINGS[source_name]
        if mapping.policy == "placeholder" or mapping.target_block_id is None:
            return self._placeholder(original_id, int(metadata), nbt_1710, position, mapping)

        blockstate = _blockstate_for(source_name, int(metadata))
        nbt_1182 = self._convert_block_entity_nbt(mapping, nbt_1710, position, int(metadata))
        warnings = list(mapping.warnings)
        if nbt_1710 and mapping.target_te_id and nbt_1182 is None:
            warnings.append("AW-W-NBT-DROPPED: source TE has no source-backed 1.18.2 NBT transform yet.")
        if nbt_1182 and nbt_1710:
            warnings.append("AW-W-SOURCE-NBT-PRESERVED: original TE NBT kept on ConversionEvent for audit.")

        event = ConversionEvent(
            mod=self.MOD,
            source_version=self.SOURCE_VERSION,
            target_version=self.TARGET_VERSION,
            event_type="remap",
            source_block_id=original_id,
            source_metadata=int(metadata),
            target_block_id=mapping.target_block_id,
            position=position,
            source_te_id=te_id,
            target_te_id=mapping.target_te_id if nbt_1182 is not None else None,
            nbt_1182=nbt_1182,
            blockstate_props=blockstate,
            warnings=warnings,
            source_nbt=deepcopy(nbt_1710) if nbt_1710 else None,
        )
        self.stats["converted"] += 1
        self.stats["warnings"] += len(warnings)
        return ArmourersWorkshopBlockConversion(
            original_id,
            position,
            int(metadata),
            ConversionResult(
                success=True,
                block_id_1182=mapping.target_block_id,
                blockstate_props=blockstate,
                nbt_1182=nbt_1182,
                warnings=warnings,
                event=event,
            ),
        )

    def to_events(self, conversion: ArmourersWorkshopBlockConversion) -> list[dict[str, Any]]:
        result = conversion.converted
        if not result.success:
            return []
        if result.event_json:
            return [result.event_json]
        if result.event:
            event = result.event.to_set_block_event()
            return [event] if event else []
        return []

    def get_stats(self) -> dict[str, int]:
        return dict(self.stats)

    def _placeholder(
        self,
        source_block_id: str,
        metadata: int,
        nbt_1710: dict[str, Any] | None,
        position: Position,
        mapping: BlockMapping,
    ) -> ArmourersWorkshopBlockConversion:
        warnings = list(mapping.warnings)
        warnings.append("AW-W-PLACEHOLDER-RESCUE: unsupported AW object preserved for manual/entity-stage conversion.")
        event_json = make_block_entity_placeholder_event(
            position=position,
            source_mod=self.MOD,
            original_nbt=nbt_1710 or {},
            source_block_id=source_block_id,
            source_te_id=mapping.source_te_id,
            source_metadata=metadata,
            conversion_reason="armourers_workshop_unsupported_or_entity_target",
            conversion_stage="armourers_workshop_zadanie3",
            extra={
                "target_hint": _target_hint(mapping),
                "source_name": mapping.source_name,
                "warnings": warnings,
            },
        )
        self.stats["placeholder"] += 1
        self.stats["warnings"] += len(warnings)
        result = ConversionResult(
            success=True,
            block_id_1182=event_json["block"],
            nbt_1182=event_json.get("nbt"),
            warnings=warnings,
            event_json=event_json,
        )
        return ArmourersWorkshopBlockConversion(source_block_id, position, metadata, result)

    def _convert_block_entity_nbt(
        self,
        mapping: BlockMapping,
        nbt_1710: dict[str, Any] | None,
        position: Position,
        metadata: int,
    ) -> dict[str, Any] | None:
        if mapping.target_te_id is None:
            return None
        base = {"id": mapping.target_te_id, "x": position[0], "y": position[1], "z": position[2]}
        if not nbt_1710:
            return base
        if mapping.source_name in {"skinnable", "skinnableGlowing"}:
            return _convert_skinnable_parent_nbt(base, nbt_1710, position)
        if mapping.source_name in {"skinnableChild", "skinnableChildGlowing"}:
            return _convert_skinnable_child_nbt(base, nbt_1710, position)
        if mapping.source_name == "hologramProjector":
            return _convert_hologram_nbt(base, nbt_1710)
        return base


def build_library_migration_event(
    source_root: str = "pliki_globalne_serwer_1710/armourersWorkshop",
    target_root: str = "skin-library",
) -> dict[str, Any]:
    """Emit the sidecar work item for binary .armour conversion.

    The actual binary rewrite must use the 1.18.2 SkinSerializer path:
    read v12/v13, then write latest v25.
    """

    return {
        "op": "armourers_workshop_convert_skin_library",
        "source_root": normalize_library_path(source_root, require_extension=False),
        "target_root": normalize_library_path(target_root, require_extension=False),
        "read_serializers": ["SkinSerializerV12", "SkinSerializerV13", "SkinSerializerV20"],
        "write_serializer": "SkinSerializerV20",
        "target_file_version": 25,
        "target_identifier_prefix": "ws:",
        "source_evidence": [
            "1.7.10 SkinPointer stores libraryFile under armourersWorkshop.identifier.libraryFile.",
            "1.18.2 SkinLibraryLoader exposes server library files as ws:<path>.",
        ],
    }


def _convert_skinnable_parent_nbt(base: dict[str, Any], nbt_1710: dict[str, Any], position: Position) -> dict[str, Any]:
    target = dict(base)
    descriptor, descriptor_warnings = _skin_descriptor_from_1710(nbt_1710)
    if descriptor:
        target["Skin"] = descriptor
    related = _related_offsets(nbt_1710.get("relatedBlocks"), position)
    if related:
        target["Refers"] = related
    linked = _linked_pos(nbt_1710.get("linkedBlock"))
    if linked:
        target["LinkedPos"] = linked
    if descriptor_warnings:
        target["conversion_warnings"] = descriptor_warnings
    return target


def _convert_skinnable_child_nbt(base: dict[str, Any], nbt_1710: dict[str, Any], position: Position) -> dict[str, Any]:
    target = dict(base)
    parent = (
        _int_or_none(nbt_1710.get("parentX")),
        _int_or_none(nbt_1710.get("parentY")),
        _int_or_none(nbt_1710.get("parentZ")),
    )
    if all(value is not None for value in parent):
        target["Refer"] = [position[0] - parent[0], position[1] - parent[1], position[2] - parent[2]]
    else:
        target["conversion_warnings"] = ["AW-W-CHILD-PARENT-MISSING: parentX/Y/Z not present."]
    return target


def _convert_hologram_nbt(base: dict[str, Any], nbt_1710: dict[str, Any]) -> dict[str, Any]:
    target = dict(base)
    # Evidence: 1.18.2 HologramProjectorBlockEntity keys are Glowing,
    # Powered, Scale, PowerMode, Angle, Offset, RotSpeed, RotOffset.
    for source_key, target_key in {
        "isGlowing": "Glowing",
        "isPowered": "Powered",
        "modelScale": "Scale",
        "powerMode": "PowerMode",
    }.items():
        if source_key in nbt_1710:
            target[target_key] = nbt_1710[source_key]
    return target


def _skin_descriptor_from_1710(nbt_1710: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    skin_data = nbt_1710.get("armourersWorkshop")
    if not isinstance(skin_data, dict):
        if nbt_1710.get("hasSkin"):
            return None, ["AW-W-SKIN-DATA-MISSING: hasSkin=true but armourersWorkshop compound is absent."]
        return None, []
    identifier = skin_data.get("identifier", {})
    if not isinstance(identifier, dict):
        identifier = {}
    pointer = SkinPointer1710(
        SkinIdentifier1710(
            local_id=int(identifier.get("localId", 0) or 0),
            library_file=_string_or_none(identifier.get("libraryFile")),
            global_id=int(identifier.get("globalId", 0) or 0),
            skin_type=_string_or_none(identifier.get("skinType")),
        ),
        lock_skin=bool(skin_data.get("lock", False)),
        dye={key: value for key, value in skin_data.items() if key not in {"identifier", "lock"}},
    )
    migrated = migrate_skin_pointer(pointer)
    descriptor = {
        "Identifier": migrated.identifier,
    }
    if migrated.skin_type:
        descriptor["SkinType"] = migrated.skin_type
    if migrated.dye:
        descriptor["SkinDyes"] = migrated.dye
    return descriptor, list(migrated.warnings)


def _related_offsets(value: Any, position: Position) -> list[list[int]]:
    if not isinstance(value, list):
        return []
    offsets: list[list[int]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        x = _int_or_none(item.get("x"))
        y = _int_or_none(item.get("y"))
        z = _int_or_none(item.get("z"))
        if x is None or y is None or z is None:
            continue
        offsets.append([x - position[0], y - position[1], z - position[2]])
    return offsets


def _linked_pos(value: Any) -> list[int] | None:
    if isinstance(value, list) and len(value) >= 3:
        return [int(value[0]), int(value[1]), int(value[2])]
    return None


def _blockstate_for(source_name: str, metadata: int) -> dict[str, str]:
    if source_name.startswith("skinnable"):
        return skinnable_blockstate(metadata)
    if source_name == "hologramProjector":
        return _attached_blockstate(metadata)
    if source_name in {"armourerBrain"}:
        return {"facing": "north"}
    return {}


def _attached_blockstate(metadata: int) -> dict[str, str]:
    if metadata == 0:
        return {"face": "ceiling", "facing": "north", "lit": "false"}
    if metadata == 1:
        return {"face": "floor", "facing": "north", "lit": "false"}
    return {"face": "wall", "facing": skinnable_blockstate(metadata)["facing"], "lit": "false"}


def _target_hint(mapping: BlockMapping) -> str:
    if mapping.source_name == "mannequin":
        return f"{TARGET_MOD_ID}:mannequin entity spawn event should be generated in the entity stage."
    return "manual review required"


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _string_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None
