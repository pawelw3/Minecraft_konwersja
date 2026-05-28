"""
Armourer's Workshop - Zadanie 1.

Inwentaryzuje bloki, tile entities i globalne pliki modeli .armour dla
Armourer's Workshop 1.7.10. Skrypt jest tylko odczytowy: nie dotyka mapy ani
oryginalnych globalnych danych serwera.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_1710 = (
    PROJECT_ROOT
    / "mod_src"
    / "1710"
    / "actual_src"
    / "1.7.10"
    / "ArmourersWorkshop"
    / "repo"
)
SOURCE_1182_DIR = PROJECT_ROOT / "mod_src" / "118"
GLOBAL_SERVER_1710 = PROJECT_ROOT / "pliki_globalne_serwer_1710"
GLOBAL_LIBRARY_1710 = GLOBAL_SERVER_1710 / "armourersWorkshop"
GLOBAL_DATABASE_1710 = GLOBAL_SERVER_1710 / "global-skin-database"
OUTPUT_DIR = PROJECT_ROOT / "output" / "armourers_workshop_step1"
CONVERTER_DIR = PROJECT_ROOT / "src" / "converters" / "armourers_workshop"


BLOCK_DESCRIPTIONS = {
    "armourerBrain": "Glowny blok budowy skinow; ustawia obszar roboczy i zbiera Equipment Cubes w model.",
    "miniArmourer": "Niedokonczony mini wariant Armourera; w 0.48.5 istnieje jako blok/TE, ale nie jest glowna sciezka migracji.",
    "armourLibrary": "Biblioteka zapisu i odczytu plikow .armour z katalogu serwera/klienta.",
    "globalSkinLibrary": "Blok dostepu do globalnej biblioteki skinow; dane modeli sa poza chunkami.",
    "awBoundingBox6": "Techniczny blok granicy/modelu uzywany przy skinach blokowych i multiblokach.",
    "colourable": "Podstawowy malowalny Equipment Cube uzywany jako voxel modelu.",
    "colourableGlowing": "Malowalny Equipment Cube z efektem swiecenia.",
    "colourableGlass": "Przezroczysty malowalny Equipment Cube.",
    "colourableGlassGlowing": "Przezroczysty malowalny Equipment Cube ze swieceniem.",
    "colourMixer": "Stol do mieszania kolorow dla narzedzi malarskich.",
    "mannequin": "Manekin pokazujacy skiny/ekwipunek i ustawienia pozy.",
    "doll": "Maly wariant manekina.",
    "skinningTable": "Stol nakladania i zdejmowania skinow z itemow.",
    "skinnable": "Blok reprezentujacy zapisany skin blokowy w swiecie.",
    "skinnableGlowing": "Swiecacy wariant bloku skinnable.",
    "skinnableChild": "Blok pomocniczy dla wieloblokowego skina blokowego; linkuje do glownego skinnable.",
    "skinnableChildGlowing": "Swiecacy blok pomocniczy wielobloku skinnable.",
    "dyeTable": "Stol do farbowania/edycji kolorow skinow.",
    "hologramProjector": "Projektor podgladu skinow bez postawienia finalnego modelu.",
}

LEGACY_SKIN_TYPES = {
    0: "armourers:head",
    1: "armourers:chest",
    2: "armourers:legs",
    3: "armourers:legs",
    4: "armourers:feet",
    5: "armourers:sword",
    6: "armourers:bow",
    7: "armourers:bow",
}

LEGACY_PART_TYPES = {
    0: "armourers:head.base",
    1: "armourers:chest.base",
    2: "armourers:chest.leftArm",
    3: "armourers:chest.rightArm",
    4: "armourers:legs.leftLeg",
    5: "armourers:legs.rightLeg",
    6: "armourers:legs.skirt",
    7: "armourers:feet.leftFoot",
    8: "armourers:feet.rightFoot",
    9: "armourers:sword.base",
    10: "armourers:bow.frame1",
}


TILE_CLASSES = {
    "armourerBrain": "TileEntityArmourer",
    "miniArmourer": "TileEntityMiniArmourer",
    "armourLibrary": "TileEntitySkinLibrary",
    "globalSkinLibrary": "TileEntityGlobalSkinLibrary",
    "colourable": "TileEntityColourable",
    "colourMixer": "TileEntityColourMixer",
    "awBoundingBox6": "TileEntityBoundingBox",
    "mannequin": "TileEntityMannequin",
    "skinningTable": "TileEntitySkinningTable",
    "skinnable": "TileEntitySkinnable",
    "dyeTable": "TileEntityDyeTable",
    "skinnableChild": "TileEntitySkinnableChild",
    "hologramProjector": "TileEntityHologramProjector",
}


@dataclass
class BlockInfo:
    field_name: str
    block_id: str
    block_registry: str
    item_registry: str
    class_name: str
    source_file: str
    has_tile_entity: bool
    tile_entity_registry: str | None = None
    tile_entity_class: str | None = None
    description: str = ""


@dataclass
class SkinFileInfo:
    path: str
    category: str
    size: int
    sha256: str
    file_version: int | None = None
    skin_type: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)
    has_paint_data: bool | None = None
    part_count: int | None = None
    part_types: list[str] = field(default_factory=list)
    cube_count: int | None = None
    marker_count: int | None = None
    parse_status: str = "not_parsed"
    parse_error: str | None = None


class ArmourFileReader:
    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0

    def remaining(self) -> int:
        return len(self.data) - self.offset

    def read(self, size: int) -> bytes:
        if self.offset + size > len(self.data):
            raise EOFError(f"Need {size} bytes at {self.offset}, file has {len(self.data)}")
        chunk = self.data[self.offset : self.offset + size]
        self.offset += size
        return chunk

    def read_int(self) -> int:
        return struct.unpack(">i", self.read(4))[0]

    def read_unsigned_short(self) -> int:
        return struct.unpack(">H", self.read(2))[0]

    def read_byte(self) -> int:
        return struct.unpack(">b", self.read(1))[0]

    def read_bool(self) -> bool:
        return self.read(1) != b"\x00"

    def read_double(self) -> float:
        return struct.unpack(">d", self.read(8))[0]

    def read_string(self, encoding: str) -> str:
        size = self.read_unsigned_short()
        return self.read(size).decode(encoding, errors="replace")

    def read_utf(self) -> str:
        return self.read_string("utf-8")

    def expect_ascii(self, expected: str) -> None:
        actual = self.read_string("ascii")
        if actual != expected:
            raise ValueError(f"Expected {expected!r}, got {actual!r} at offset {self.offset}")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_lib_block_names() -> dict[str, str]:
    path = SOURCE_1710 / "src/main/java/riskyken/armourersWorkshop/common/lib/LibBlockNames.java"
    names: dict[str, str] = {}
    if not path.exists():
        return names
    for match in re.finditer(r'public static final String\s+(\w+)\s*=\s*"([^"]+)";', read_text(path)):
        names[match.group(1)] = match.group(2)
    return names


def collect_blocks_1710() -> list[BlockInfo]:
    names = parse_lib_block_names()
    mod_blocks = SOURCE_1710 / "src/main/java/riskyken/armourersWorkshop/common/blocks/ModBlocks.java"
    if not mod_blocks.exists():
        return []
    text = read_text(mod_blocks)

    field_to_class: dict[str, str] = {}
    for match in re.finditer(r"^\s*(\w+)\s*=\s*new\s+(\w+)\(", text, re.MULTILINE):
        field_to_class[match.group(1)] = match.group(2)

    constructor_to_id = {
        "BlockArmourer": names.get("ARMOURER_BRAIN", "armourerBrain"),
        "BlockMiniArmourer": names.get("MINI_ARMOURER", "miniArmourer"),
        "BlockSkinLibrary": names.get("ARMOUR_LIBRARY", "armourLibrary"),
        "BlockGlobalSkinLibrary": names.get("GLOBAL_SKIN_LIBRARY", "globalSkinLibrary"),
        "BlockBoundingBox": names.get("BOUNDING_BOX", "awBoundingBox6"),
        "BlockColourMixer": names.get("COLOUR_MIXER", "colourMixer"),
        "BlockMannequin": names.get("MANNEQUIN", "mannequin"),
        "BlockDoll": names.get("DOLL", "doll"),
        "BlockSkinningTable": names.get("SKINNING_TABLE", "skinningTable"),
        "BlockSkinnable": names.get("SKINNABLE", "skinnable"),
        "BlockSkinnableGlowing": names.get("SKINNABLE_GLOWING", "skinnableGlowing"),
        "BlockSkinnableChild": names.get("SKINNABLE_CHILD", "skinnableChild"),
        "BlockSkinnableChildGlowing": names.get("SKINNABLE_CHILD_GLOWING", "skinnableChildGlowing"),
        "BlockDyeTable": names.get("DYE_TABLE", "dyeTable"),
        "BlockHologramProjector": names.get("HOLOGRAM_PROJECTOR", "hologramProjector"),
    }
    field_to_id = {
        "colourable": names.get("COLOURABLE", "colourable"),
        "colourableGlowing": names.get("COLOURABLE_GLOWING", "colourableGlowing"),
        "colourableGlass": names.get("COLOURABLE_GLASS", "colourableGlass"),
        "colourableGlassGlowing": names.get("COLOURABLE_GLASS_GLOWING", "colourableGlassGlowing"),
    }

    blocks: list[BlockInfo] = []
    for field_name, class_name in sorted(field_to_class.items()):
        block_id = field_to_id.get(field_name, constructor_to_id.get(class_name, field_name))
        tile_class = TILE_CLASSES.get(block_id)
        blocks.append(
            BlockInfo(
                field_name=field_name,
                block_id=block_id,
                block_registry=f"armourersworkshop:block.{block_id}",
                item_registry=f"armourersworkshop:block.{block_id}",
                class_name=class_name,
                source_file=rel(mod_blocks),
                has_tile_entity=tile_class is not None,
                tile_entity_registry=f"te.{block_id}" if tile_class else None,
                tile_entity_class=tile_class,
                description=BLOCK_DESCRIPTIONS.get(block_id, "Blok Armourer's Workshop wymagajacy recznej weryfikacji opisu."),
            )
        )
    return blocks


def parse_skin_properties(reader: ArmourFileReader, version: int) -> dict[str, Any]:
    if version < 12:
        props = {
            "authorName": reader.read_utf(),
            "customName": reader.read_utf(),
        }
        if version >= 4:
            tags = reader.read_utf()
            if tags:
                props["tags"] = tags
        return props

    count = reader.read_int()
    props: dict[str, Any] = {}
    for _ in range(count):
        key = reader.read_utf() if version > 12 else reader.read_utf()
        value_type = reader.read_byte()
        if value_type == 0:
            value: Any = reader.read_utf()
        elif value_type == 1:
            value = reader.read_int()
        elif value_type == 2:
            value = reader.read_double()
        elif value_type == 3:
            value = reader.read_bool()
        else:
            raise ValueError(f"Unknown skin property type {value_type}")
        props[key] = value
    return props


def parse_armour_file(path: Path) -> SkinFileInfo:
    data = path.read_bytes()
    info = SkinFileInfo(
        path=rel(path),
        category=category_for_skin_file(path),
        size=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
    )
    reader = ArmourFileReader(data)
    try:
        version = reader.read_int()
        info.file_version = version
        if version > 13:
            raise ValueError(f"Newer file version {version}; local 1.7.10 code supports 13")

        if version > 12:
            reader.expect_ascii("AW-SKIN-START")
            reader.expect_ascii("PROPS-START")
        info.properties = parse_skin_properties(reader, version)
        if version > 12:
            reader.expect_ascii("PROPS-END")
            reader.expect_ascii("TYPE-START")
        if version < 5:
            info.skin_type = LEGACY_SKIN_TYPES.get(reader.read_byte() - 1, "legacy:unknown")
        else:
            info.skin_type = reader.read_utf()
            if info.skin_type in {"armourers:skirt"}:
                info.skin_type = "armourers:legs"
        if version > 12:
            reader.expect_ascii("TYPE-END")
            reader.expect_ascii("PAINT-START")
        if version > 7:
            info.has_paint_data = reader.read_bool()
            if info.has_paint_data:
                reader.read(64 * 32 * 4)
        if version > 12:
            reader.expect_ascii("PAINT-END")

        part_count = reader.read_byte()
        info.part_count = part_count
        cube_count = 0
        marker_count = 0
        for _ in range(part_count):
            if version > 12:
                reader.expect_ascii("PART-START")
            if version < 6:
                part_type = LEGACY_PART_TYPES.get(reader.read_byte(), "legacy:unknown")
            elif version > 12:
                part_type = reader.read_string("ascii")
            else:
                part_type = reader.read_utf()
                if part_type == "armourers:skirt.base":
                    part_type = "armourers:legs.skirt"
                elif part_type == "armourers:bow.base":
                    part_type = "armourers:bow.frame1"
                elif part_type == "armourers:arrow.base":
                    part_type = "armourers:bow.arrow"
            info.part_types.append(part_type)
            cubes = reader.read_int()
            cube_count += cubes
            if version < 3:
                bytes_per_cube = 8
            elif version < 7:
                bytes_per_cube = 8
            elif version < 10:
                bytes_per_cube = 22
            else:
                bytes_per_cube = 28
            reader.read(cubes * bytes_per_cube)
            if version > 8:
                markers = reader.read_int()
                marker_count += markers
                reader.read(markers * 4)
            if version > 12:
                reader.expect_ascii("PART-END")
        info.cube_count = cube_count
        info.marker_count = marker_count
        if version > 12:
            reader.expect_ascii("AW-SKIN-END")
        info.parse_status = "ok"
    except Exception as exc:  # noqa: BLE001 - raport musi zachowac blad per plik.
        info.parse_status = "error"
        info.parse_error = str(exc)
    return info


def category_for_skin_file(path: Path) -> str:
    try:
        relative = path.relative_to(GLOBAL_LIBRARY_1710)
    except ValueError:
        return "outside_library"
    parts = relative.parts
    if len(parts) == 1:
        return "public_root"
    if parts[0].lower() == "official":
        return "official"
    if parts[0].lower() == "private":
        return "private"
    return parts[0]


def collect_global_skins(limit: int | None = None) -> list[SkinFileInfo]:
    if not GLOBAL_LIBRARY_1710.exists():
        return []
    files = sorted(GLOBAL_LIBRARY_1710.rglob("*.armour"))
    if limit is not None:
        files = files[:limit]
    return [parse_armour_file(path) for path in files]


def detect_1182_artifacts() -> dict[str, Any]:
    candidates: list[str] = []
    exact_dir_names = {
        "armourersworkshop",
        "armourers_workshop",
        "armourers-workshop",
        "armourer's workshop",
    }
    exact_file_markers = {
        "armourers-workshop",
        "armourers_workshop",
        "armourersworkshop",
    }
    for base in [SOURCE_1182_DIR / "actual_src" / "1.18.2", SOURCE_1182_DIR / "mod_jars"]:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            name = path.name.lower()
            stem = path.stem.lower()
            if path.is_dir() and name in exact_dir_names:
                candidates.append(rel(path))
            elif path.is_file() and path.suffix.lower() == ".jar" and any(marker in stem for marker in exact_file_markers):
                candidates.append(rel(path))
    return {
        "local_artifacts_found": sorted(candidates),
        "status": "missing" if not candidates else "present",
        "expected_modid": "armourers_workshop",
        "note": (
            "Zadanie 1 wymaga porownania z 1.18.2, ale lokalnie nie znaleziono "
            "JAR/source Armourer's Workshop 3.x w mod_src/118. Raport zachowuje "
            "miejsce na te dane i nie zgaduje formatu modeli 1.18.2."
            if not candidates
            else "Znaleziono lokalne kandydaty 1.18.2; nastepny przebieg powinien zdekompilowac/przeskanowac registry."
        ),
    }


def summarize_skins(skins: list[SkinFileInfo]) -> dict[str, Any]:
    by_category = Counter(skin.category for skin in skins)
    by_type = Counter(skin.skin_type or "unknown" for skin in skins)
    by_status = Counter(skin.parse_status for skin in skins)
    total_size = sum(skin.size for skin in skins)
    total_cubes = sum(skin.cube_count or 0 for skin in skins)
    return {
        "file_count": len(skins),
        "total_size_bytes": total_size,
        "total_cube_count": total_cubes,
        "by_category": dict(sorted(by_category.items())),
        "by_skin_type": dict(sorted(by_type.items())),
        "by_parse_status": dict(sorted(by_status.items())),
    }


def write_json(data: dict[str, Any]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / "armourers_workshop_step1_inventory.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_report(data: dict[str, Any]) -> Path:
    blocks = data["blocks_1710"]
    skins = data["global_skins_1710"]
    summary = data["global_skins_summary"]
    artifact_1182 = data["artifacts_1182"]
    report = CONVERTER_DIR / "ARMOURERS_WORKSHOP_ZADANIE1_ANALIZA.md"
    lines: list[str] = []
    lines.extend(
        [
            "# Armourer's Workshop - Zadanie 1: analiza blokow, TE i modeli",
            "",
            "## Podsumowanie",
            "",
            f"- 1.7.10: wykryto {len(blocks)} blokow z `ModBlocks.java`.",
            f"- 1.7.10: wykryto {sum(1 for block in blocks if block['has_tile_entity'])} tile entities rejestrowanych jako `te.<id>`.",
            f"- Globalna biblioteka serwera: {summary['file_count']} plikow `.armour`, {summary['total_size_bytes']} bajtow, {summary['total_cube_count']} voxel-cubes.",
            f"- Parser `.armour`: statusy {summary['by_parse_status']}.",
            f"- 1.18.2: lokalne artefakty Armourer's Workshop: {artifact_1182['status']}.",
            f"- Pelna lista maszynowa: `output/armourers_workshop_step1/armourers_workshop_step1_inventory.json`.",
            "",
            "## Zrodla internetowe i lokalne",
            "",
            "- CurseForge Armourer's Workshop: https://www.curseforge.com/minecraft/mc-mods/armourers-workshop - dokumentacja projektu wskazuje port 1.18.2 3.2.7-beta.",
            "- Minecraft Forum Armourer's Workshop: http://www.minecraftforum.net/forums/mapping-and-modding/minecraft-mods/wip-mods/2309193-wip-alpha-armourers-workshop-weapon-armour-skins - link jest wpisany w `global-skin-database/readme.txt` jako opis globalnej bazy skinow.",
            "- Lokalny source 1.7.10: `mod_src/1710/actual_src/1.7.10/ArmourersWorkshop/repo`.",
            "- Lokalna dokumentacja projektu: `docs/LISTA_KONWERSJI_MODOW.md` i `docs/ANALIZA_MODOW_SZCZEGOLOWA.md` potwierdzaja, ze celem jest Armourer's Workshop 3.2.7-beta, a ryzykiem jest format skinow/modeli.",
            "",
            "## 1.7.10 - Bloki",
            "",
            "| Field | Block registry | Klasa | TE | Opis |",
            "|---|---|---|---|---|",
        ]
    )
    for block in blocks:
        lines.append(
            f"| `{block['field_name']}` | `{block['block_registry']}` | `{block['class_name']}` | "
            f"`{block['tile_entity_registry'] or '-'}` | {block['description']} |"
        )
    lines.extend(
        [
            "",
            "Dowod z kodu rejestracji blokow:",
            "",
            "```java",
            "armourerBrain = new BlockArmourer();",
            "armourLibrary = new BlockSkinLibrary();",
            "skinnable = new BlockSkinnable();",
            "hologramProjector = new BlockHologramProjector();",
            "```",
            "",
            "Plik: `mod_src/1710/actual_src/1.7.10/ArmourersWorkshop/repo/src/main/java/riskyken/armourersWorkshop/common/blocks/ModBlocks.java`.",
            "",
            "## 1.7.10 - Tile Entities",
            "",
            "| Element | Klasa Java | Registry string | Ma prefiks moda? |",
            "|---|---|---|---|",
        ]
    )
    for block in blocks:
        if block["has_tile_entity"]:
            lines.append(
                f"| `{block['block_id']}` | `{block['tile_entity_class']}` | `{block['tile_entity_registry']}` | NIE (`te.` zamiast modid) |"
            )
    lines.extend(
        [
            "",
            "Dowod z kodu rejestracji TE:",
            "",
            "```java",
            "registerTileEntity(TileEntityArmourer.class, LibBlockNames.ARMOURER_BRAIN);",
            "registerTileEntity(TileEntitySkinnable.class, LibBlockNames.SKINNABLE);",
            "registerTileEntity(TileEntitySkinnableChild.class, LibBlockNames.SKINNABLE_CHILD);",
            "GameRegistry.registerTileEntity(tileEntityClass, \"te.\" + id);",
            "```",
            "",
            "To jest krytyczne dla skanu mapy: na mapie nalezy szukac np. `te.skinnable`, `te.skinnableChild`, `te.mannequin`, a nie prefiksu moda.",
            "",
            "## Globalne modele 1.7.10 - pliki `.armour`",
            "",
            "Modele nie sa tylko w chunkach. AW 0.48.5 zapisuje biblioteke skinow w katalogu serwera, u nas: `pliki_globalne_serwer_1710/armourersWorkshop`. Parser odczytuje wersje pliku, typ skina, properties, liczbe partow, voxel-cubes i markerow bez modyfikowania plikow.",
            "",
            f"- Kategorie: `{summary['by_category']}`",
            f"- Typy skinow: `{summary['by_skin_type']}`",
            "",
            "| Plik | Typ | Wersja | Cubes | Parts | SHA-256 |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for skin in sorted(skins, key=lambda item: (item["category"], item["path"]))[:40]:
        lines.append(
            f"| `{skin['path']}` | `{skin.get('skin_type') or 'unknown'}` | {skin.get('file_version') or '-'} | "
            f"{skin.get('cube_count') or 0} | {skin.get('part_count') or 0} | `{skin['sha256'][:16]}...` |"
        )
    if len(skins) > 40:
        lines.append(f"| ... | ... | ... | ... | ... | jeszcze {len(skins) - 40} plikow w JSON |")
    lines.extend(
        [
            "",
            "Dowod z kodu formatu pliku:",
            "",
            "```java",
            "stream.writeInt(Skin.FILE_VERSION);",
            "StreamUtils.writeString(stream, Charsets.US_ASCII, TAG_SKIN_HEADER);",
            "stream.writeUTF(skin.getSkinType().getRegistryName());",
            "SkinPartSerializer.saveSkinPart(skinPart, stream);",
            "```",
            "",
            "Plik: `.../common/skin/data/serialize/SkinSerializer.java`. `Skin.FILE_VERSION` w 0.48.5 wynosi `13`; ten numer jest zapisany w pierwszych 4 bajtach kazdego pliku `.armour`.",
            "",
            "## 1.18.2 - Bloki",
            "",
            artifact_1182["note"],
            "",
            "Na podstawie dokumentacji projektu spodziewane docelowe odpowiedniki to m.in. `armourers_workshop:armourer`, `armourers_workshop:skin_library`, `armourers_workshop:skinning_table`, `armourers_workshop:dye_table`, `armourers_workshop:hologram_projector`, `armourers_workshop:mannequin`. Ten raport nie zatwierdza finalnych registry names bez lokalnego JAR/source 3.x.",
            "",
            "## 1.18.2 - Block Entities",
            "",
            "Brak lokalnego artefaktu 1.18.2 oznacza brak bezpiecznej listy BlockEntityType i brak potwierdzenia formatu danych modeli. Nastepny krok przed konwerterem modeli powinien dodac/dekompilowac JAR Armourer's Workshop 3.2.7-beta i porownac parser zapisu skina 3.x z `SkinSerializer` 0.48.5.",
            "",
            "## Porownanie 1.7.10 vs 1.18.2",
            "",
            "- Bloki warsztatowe prawdopodobnie maja bezposrednia migracje A -> A, ale registry names i BlockEntityType 3.x musza byc potwierdzone lokalnie.",
            "- Najwieksze ryzyko nie jest w blokach, tylko w modelach: 146 plikow `.armour` z globalnego katalogu serwera plus referencje skinow w TE/playerdata.",
            "- Konwerter docelowy musi traktowac globalna biblioteke jako osobny strumien migracji: najpierw parse/manifest/checksum, potem konwersja formatu 0.48.5 -> 3.x, dopiero na koncu remap TE wskazujacych na te modele.",
            "- `te.skinnable` i `te.skinnableChild` wymagaja szczegolnej ostroznosci, bo skin blokowy moze skladac sie z glownego bloku i child-blockow linkowanych po NBT.",
            "",
            "## Kryteria dla nastepnego kroku",
            "",
            "1. Dostarczyc lokalny JAR/source Armourer's Workshop 1.18.2 3.x do `mod_src/118`.",
            "2. Uruchomic analogiczny skan rejestracji 1.18.2 i serializerow modelu.",
            "3. Zbudowac test zgodnosci dla kilku plikow `.armour`: head/chest/block/multiblock, z porownaniem properties, cube_count, marker_count i part_types.",
        ]
    )
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit-skins", type=int, default=None, help="Ogranicz liczbe parsowanych plikow .armour.")
    args = parser.parse_args()

    blocks = collect_blocks_1710()
    skins = collect_global_skins(args.limit_skins)
    data = {
        "blocks_1710": [asdict(block) for block in blocks],
        "global_skins_1710": [asdict(skin) for skin in skins],
        "global_skins_summary": summarize_skins(skins),
        "global_database_1710": {
            "path": rel(GLOBAL_DATABASE_1710),
            "readme_present": (GLOBAL_DATABASE_1710 / "readme.txt").exists(),
        },
        "artifacts_1182": detect_1182_artifacts(),
    }
    json_path = write_json(data)
    report_path = write_report(data)
    print(f"Wrote {rel(json_path)}")
    print(f"Wrote {rel(report_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
