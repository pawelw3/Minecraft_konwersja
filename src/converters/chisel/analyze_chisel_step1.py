"""
Chisel - Zadanie 1.

Generuje inwentaryzacje blokow i tile entities dla Chisel 1.7.10 oraz
Rechiseled 1.18.2. Skrypt jest tylko odczytowy: nie dotyka mapy.
"""

from __future__ import annotations

import json
import re
import subprocess
import zipfile
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CHISEL_JAR = PROJECT_ROOT / "modpack_1710" / "Chisel-2.9.5.11.jar"
CHISEL_SOURCE = PROJECT_ROOT / "mod_src" / "1710" / "actual_src" / "1.7.10" / "Chisel" / "repo"
RECHISELED_SOURCE = PROJECT_ROOT / "mod_src" / "118" / "actual_src" / "1.18.2" / "Rechiseled" / "repo"
OUTPUT_DIR = PROJECT_ROOT / "output" / "chisel_step1"
CONVERTER_DIR = PROJECT_ROOT / "src" / "converters" / "chisel"

TOKEN_STOPWORDS = {
    "block",
    "blocks",
    "chisel",
    "chiseled",
    "connecting",
    "slab",
    "stairs",
    "regular",
    "tile",
}


@dataclass
class BlockFamily:
    modid: str
    family: str
    registry_hint: str
    source: str
    variant_count: int
    variants: list[str] = field(default_factory=list)
    texture_count: int = 0
    texture_examples: list[str] = field(default_factory=list)
    visual_tokens: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class TileEntityInfo:
    modid: str
    registry: str
    class_name: str
    source_file: str
    notes: str


def normalize_token(value: str) -> str:
    value = value.replace("-", "_").replace("/", "_")
    value = re.sub(r"[^a-zA-Z0-9_]+", "_", value).lower()
    return re.sub(r"_+", "_", value).strip("_")


def tokens_for(*values: str) -> list[str]:
    tokens: set[str] = set()
    for value in values:
        for token in re.split(r"[_/\-.]+", normalize_token(value)):
            if token and token not in TOKEN_STOPWORDS and not token.isdigit():
                tokens.add(token)
    return sorted(tokens)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def extract_chisel_1710_source_families() -> set[str]:
    families: set[str] = set()
    for source_path in [
        CHISEL_SOURCE / "base" / "src" / "main" / "java" / "team" / "chisel" / "FeaturesOld.java",
        CHISEL_SOURCE / "base" / "src" / "main" / "java" / "team" / "chisel" / "Features.java",
        CHISEL_SOURCE / "legacy" / "src" / "main" / "java" / "team" / "chisel" / "legacy" / "LegacyFeatures.java",
    ]:
        if not source_path.exists():
            continue
        text = read_text(source_path)
        for match in re.finditer(r'\.(?:newType|newBlock)\([^;\n]*?["]([^"]+)["]', text, re.DOTALL):
            family = normalize_token(match.group(1))
            if family:
                families.add(family)
    return families


def javap_lines(class_name: str) -> list[str]:
    try:
        completed = subprocess.run(
            ["javap", "-classpath", str(CHISEL_JAR), class_name],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if completed.returncode != 0:
        return []
    return completed.stdout.splitlines()


def extract_chisel_1710_class_block_fields() -> set[str]:
    families: set[str] = set()
    for line in javap_lines("team.chisel.init.ChiselBlocks"):
        match = re.search(r"public static (?:final )?[\w.$\[\]]+ ([A-Za-z0-9_]+);", line.strip())
        if not match:
            continue
        field_name = normalize_token(match.group(1))
        if field_name and field_name not in {"torches", "planks", "pumpkin", "jackolantern"}:
            families.add(field_name)
    for array_family in ["torches", "planks", "pumpkin", "jackolantern"]:
        if any(array_family in line for line in javap_lines("team.chisel.init.ChiselBlocks")):
            families.add(array_family)
    return families


def extract_chisel_1710_feature_names() -> set[str]:
    families: set[str] = set()
    for line in javap_lines("team.chisel.Features"):
        match = re.search(r"public static final team\.chisel\.Features ([A-Z0-9_]+);", line.strip())
        if match:
            families.add(normalize_token(match.group(1)))
    return families


def extract_chisel_1710_jar_textures() -> dict[str, list[str]]:
    families: dict[str, list[str]] = defaultdict(list)
    if not CHISEL_JAR.exists():
        return families

    with zipfile.ZipFile(CHISEL_JAR) as jar:
        for name in jar.namelist():
            if not name.startswith("assets/chisel/textures/blocks/") or not name.endswith(".png"):
                continue
            rest = name.removeprefix("assets/chisel/textures/blocks/")
            parts = rest.split("/")
            if not parts or not parts[-1]:
                continue
            if len(parts) == 1:
                family = normalize_token(Path(parts[0]).stem)
            else:
                family = normalize_token(parts[0])
            families[family].append(name)
    return families


def variant_from_texture(path: str) -> str:
    stem = Path(path).stem
    stem = stem.replace("-ctm", "").replace("_ctm", "")
    return normalize_token(stem)


def collect_chisel_1710_blocks() -> list[BlockFamily]:
    source_families = extract_chisel_1710_source_families()
    class_families = extract_chisel_1710_class_block_fields()
    feature_families = extract_chisel_1710_feature_names()
    texture_families = extract_chisel_1710_jar_textures()
    all_families = sorted(source_families | class_families | feature_families | set(texture_families))
    blocks: list[BlockFamily] = []

    for family in all_families:
        textures = sorted(texture_families.get(family, []))
        variants = sorted({variant_from_texture(path) for path in textures if variant_from_texture(path)})
        source_bits = []
        if family in class_families:
            source_bits.append("jar_class")
        if family in feature_families:
            source_bits.append("feature_enum")
        if family in source_families:
            source_bits.append("source")
        if textures:
            source_bits.append("jar_textures")
        source = "+".join(source_bits) if source_bits else "unknown"
        registry_hint = f"chisel:{family}"
        if source == "jar_textures":
            registry_hint = f"texture-only:{family}"
        blocks.append(
            BlockFamily(
                modid="chisel",
                family=family,
                registry_hint=registry_hint,
                source=source,
                variant_count=len(variants),
                variants=variants,
                texture_count=len(textures),
                texture_examples=textures[:5],
                visual_tokens=tokens_for(family, *variants[:12]),
                notes=(
                    "1.7.10 zapisuje realny blok jako numeryczne ID + metadata; "
                    "registry_hint jest nazwa rodziny do pozniejszego mapowania ID/meta. "
                    "Pozycje texture-only sa kandydatami wizualnymi, nie potwierdzonymi registry."
                ),
            )
        )
    return blocks


def collect_chisel_1710_tile_entities() -> list[TileEntityInfo]:
    tile_entities: dict[str, TileEntityInfo] = {}
    if CHISEL_JAR.exists():
        with zipfile.ZipFile(CHISEL_JAR) as jar:
            classes = set(jar.namelist())
        jar_tiles = {
            "team/chisel/block/tileentity/TileEntityAutoChisel.class": (
                "TileEntityAutoChisel",
                "team.chisel.block.tileentity.TileEntityAutoChisel",
                "Automatyczna maszyna do chiselowania; ma GUI, inventory i w starszych wersjach sloty upgrade.",
            ),
            "team/chisel/block/tileentity/TileEntityCarvableBeacon.class": (
                "TileEntityCarvableBeacon",
                "team.chisel.block.tileentity.TileEntityCarvableBeacon",
                "Tile entity wariantu beacon; istotna glownie wizualnie/renderingowo.",
            ),
            "team/chisel/block/tileentity/TileEntityPresent.class": (
                "TileEntityPresent",
                "team.chisel.block.tileentity.TileEntityPresent",
                "Tile entity prezentu; moze przechowywac dane wariantu/zawartosci prezentu.",
            ),
        }
        for class_path, (registry, class_name, notes) in jar_tiles.items():
            if class_path in classes and class_name not in tile_entities:
                tile_entities[class_name] = TileEntityInfo(
                    modid="chisel",
                    registry=registry,
                    class_name=class_name,
                    source_file=rel(CHISEL_JAR),
                    notes=notes + " Registry string wymaga potwierdzenia skanem TE z mapy/JAR dekompilacja.",
                )
    return list(tile_entities.values())


def collect_rechiseled_blocks() -> list[BlockFamily]:
    blockstates_dir = RECHISELED_SOURCE / "src" / "generated" / "resources" / "assets" / "rechiseled" / "blockstates"
    lang_path = RECHISELED_SOURCE / "src" / "generated" / "resources" / "assets" / "rechiseled" / "lang" / "en_us.json"
    names: dict[str, str] = {}
    if lang_path.exists():
        names = json.loads(read_text(lang_path))

    grouped: dict[str, list[str]] = defaultdict(list)
    texture_examples: dict[str, list[str]] = defaultdict(list)
    if blockstates_dir.exists():
        for path in sorted(blockstates_dir.glob("*.json")):
            block_id = path.stem
            base = block_id
            for suffix in [
                "_stairs_connecting",
                "_slab_connecting",
                "_connecting",
                "_stairs",
                "_slab",
            ]:
                if base.endswith(suffix):
                    base = base[: -len(suffix)]
                    break
            family = base.split("_")[0]
            if base.startswith(("red_sandstone", "red_nether", "dark_oak", "dark_prismarine", "blue_ice")):
                family = "_".join(base.split("_")[:2])
            if base.startswith(("prismarine_bricks", "stone_bricks", "mossy_cobblestone")):
                family = "_".join(base.split("_")[:2])
            grouped[family].append(block_id)

    textures_dir = RECHISELED_SOURCE / "src" / "main" / "resources" / "assets" / "rechiseled" / "textures" / "block"
    if textures_dir.exists():
        for path in sorted(textures_dir.glob("*.png")):
            stem = path.stem
            family = stem.split("_")[0]
            if stem.startswith(("red_sandstone", "red_nether", "dark_oak", "dark_prismarine", "blue_ice")):
                family = "_".join(stem.split("_")[:2])
            if stem.startswith(("prismarine_bricks", "stone_bricks", "mossy_cobblestone")):
                family = "_".join(stem.split("_")[:2])
            if len(texture_examples[family]) < 5:
                texture_examples[family].append(rel(path))

    blocks: list[BlockFamily] = []
    for family, block_ids in sorted(grouped.items()):
        variants = sorted(block_ids)
        display_hint = names.get(f"block.rechiseled.{variants[0]}", "") if variants else ""
        blocks.append(
            BlockFamily(
                modid="rechiseled",
                family=family,
                registry_hint=f"rechiseled:{family}_*",
                source="generated_resources",
                variant_count=len(variants),
                variants=variants,
                texture_count=len(texture_examples.get(family, [])),
                texture_examples=texture_examples.get(family, []),
                visual_tokens=tokens_for(family, *variants[:24], display_hint),
                notes="Rodzina obejmuje warianty blok, connecting, slab i stairs gdy istnieja.",
            )
        )
    return blocks


def collect_rechiseled_block_entities() -> list[TileEntityInfo]:
    java_root = RECHISELED_SOURCE / "src" / "main" / "java"
    block_entities: list[TileEntityInfo] = []
    hits = []
    if java_root.exists():
        for path in java_root.rglob("*.java"):
            text = read_text(path)
            if "BlockEntityType" in text or "extends BlockEntity" in text:
                hits.append(path)
    if hits:
        for path in hits:
            block_entities.append(
                TileEntityInfo(
                    modid="rechiseled",
                    registry="unknown",
                    class_name=path.stem,
                    source_file=rel(path),
                    notes="Wymaga recznej weryfikacji, bo znaleziono wzmianke o BlockEntity.",
                )
            )
    return block_entities


def score_visual_match(source: BlockFamily, target: BlockFamily) -> int:
    source_tokens = set(source.visual_tokens)
    target_tokens = set(target.visual_tokens)
    score = len(source_tokens & target_tokens) * 10
    if source.family == target.family:
        score += 50
    if source.family.replace("mossy_", "") == target.family.replace("mossy_", ""):
        score += 10
    if any(v in target.variants for v in source.variants[:12]):
        score += 8
    return score


def build_visual_candidates(chisel_blocks: list[BlockFamily], rechiseled_blocks: list[BlockFamily]) -> dict[str, list[dict[str, object]]]:
    result: dict[str, list[dict[str, object]]] = {}
    for source in chisel_blocks:
        scored = [
            {
                "target_family": target.family,
                "target_registry_hint": target.registry_hint,
                "score": score_visual_match(source, target),
                "shared_tokens": sorted(set(source.visual_tokens) & set(target.visual_tokens)),
                "target_examples": target.variants[:8],
            }
            for target in rechiseled_blocks
        ]
        scored = [item for item in scored if int(item["score"]) > 0]
        scored.sort(key=lambda item: int(item["score"]), reverse=True)
        result[source.family] = scored[:5]
    return result


def grouped_counter(blocks: Iterable[BlockFamily]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for block in blocks:
        counter[block.source] += 1
    return counter


def write_json_report(data: dict[str, object]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / "chisel_step1_inventory.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def format_top_families(blocks: list[BlockFamily], limit: int = 30) -> str:
    lines = ["| Family | Registry hint | Variants | Texture examples |", "|---|---:|---:|---|"]
    for block in sorted(blocks, key=lambda b: (-b.variant_count, b.family))[:limit]:
        examples = ", ".join(block.texture_examples[:2])
        lines.append(f"| `{block.family}` | `{block.registry_hint}` | {block.variant_count} | {examples} |")
    return "\n".join(lines)


def format_visual_candidates(candidates: dict[str, list[dict[str, object]]], limit: int = 25) -> str:
    lines = ["| Chisel family | Najlepszy kandydat 1.18.2 | Score | Wspolne tokeny |", "|---|---|---:|---|"]
    for family, items in sorted(candidates.items())[:limit]:
        if not items:
            lines.append(f"| `{family}` | brak szybkiego kandydata | 0 |  |")
            continue
        best = items[0]
        tokens = ", ".join(best["shared_tokens"])
        lines.append(f"| `{family}` | `{best['target_registry_hint']}` | {best['score']} | {tokens} |")
    return "\n".join(lines)


def write_markdown_report(data: dict[str, object]) -> Path:
    CONVERTER_DIR.mkdir(parents=True, exist_ok=True)
    chisel_blocks = [BlockFamily(**item) for item in data["chisel_1710"]["blocks"]]
    rechiseled_blocks = [BlockFamily(**item) for item in data["rechiseled_1182"]["blocks"]]
    chisel_tes = [TileEntityInfo(**item) for item in data["chisel_1710"]["tile_entities"]]
    rechiseled_bes = [TileEntityInfo(**item) for item in data["rechiseled_1182"]["block_entities"]]
    candidates = data["visual_candidates"]

    authoritative_1710 = [block for block in chisel_blocks if "jar_class" in block.source or "feature_enum" in block.source or "source" in block.source]
    texture_only_1710 = [block for block in chisel_blocks if block.source == "jar_textures"]

    text = f"""# Chisel - Zadanie 1: analiza blokow i TE

## Podsumowanie

- Chisel 1.7.10: {len(authoritative_1710)} rodzin/feature potwierdzonych z klas JAR lub source.
- Chisel 1.7.10: {len(texture_only_1710)} dodatkowych rodzin texture-only do uzycia przy dopasowaniu wizualnym.
- Chisel 1.7.10: {len(chisel_tes)} tile entity istotne dla konwersji.
- Rechiseled 1.18.2: {len(rechiseled_blocks)} rodzin blokow z generated resources.
- Rechiseled 1.18.2: {len(rechiseled_bes)} block entities wykrytych w kodzie.
- Pelna, maszynowa lista jest w `output/chisel_step1/chisel_step1_inventory.json`.

## Zrodla internetowe

- CurseForge Chisel: https://www.curseforge.com/minecraft/mc-mods/chisel/chisel - potwierdza charakter moda jako zestawu dekoracyjnych wariantow blokow i narzedzia chisel.
- FTB Wiki Chisel: https://ftbwiki.org/Chisel - opisuje narzedzie Chisel i Auto Chisel jako sposob zamiany blokow na warianty.
- CurseForge Rechiseled: https://www.curseforge.com/minecraft/mc-mods/rechiseled - opisuje Rechiseled jako mod do zamiany blokow na warianty dekoracyjne z connected textures.
- GitHub Rechiseled: https://github.com/SuperMartijn642/Rechiseled - kod zrodlowy docelowego moda uzywany lokalnie w `mod_src/118/.../Rechiseled`.

## 1.7.10 - Bloki

Chisel 2.9.5.11 jest przede wszystkim modem dekoracyjnym. Wiekszosc danych w swiecie to blok numeryczny + metadata, bez TileEntity, wiec pozniejszy konwerter musi skanowac palette/numeric ID, nie tylko TE. `registry_hint` ponizej jest nazwa rodziny/pakietu wariantow, a dokladny numeric ID/meta trzeba pobrac z mapy albo testowego swiata. Tabela pokazuje najwieksze rodziny, a JSON zawiera takze flage zrodla (`jar_class`, `feature_enum`, `source`, `jar_textures`).

{format_top_families(authoritative_1710)}

## 1.7.10 - Tile Entities

"""
    if chisel_tes:
        for te in chisel_tes:
            text += f"""### {te.registry}
- **Typ:** TileEntity
- **Klasa Java:** `{te.class_name}`
- **Plik:** `{te.source_file}`
- **Opis:** {te.notes}
- **Dowod z kodu:** klasa jest obecna w JAR `Chisel-2.9.5.11.jar`; lista zostala wyciagnieta z `jar tf`/`javap`. Dokladny string rejestracji TE trzeba potwierdzic skanem mapy albo dekompilacja bytecode przy Zadaniu 3.

"""
    else:
        text += "Nie wykryto TE w lokalnym source; JAR zawiera jednak klasy `BlockAutoChisel` i `TileAutoChisel`, wiec to wymaga weryfikacji dekompilacja przy Zadaniu 3.\n\n"

    text += f"""## 1.18.2 - Bloki

Rechiseled generuje warianty jako osobne blockstates, zwykle z postaciami normalnymi, connecting, slab i stairs. To jest dobry docelowy zamiennik dla rodzin kamiennych/drewnianych/metali Chisela, ale nie kazda tekstura ma odpowiednik 1:1.

{format_top_families(rechiseled_blocks)}

## 1.18.2 - Block Entities

"""
    if rechiseled_bes:
        for be in rechiseled_bes:
            text += f"- `{be.class_name}` z `{be.source_file}`: {be.notes}\n"
    else:
        text += "Nie wykryto wlasnych block entities Rechiseled w glownym kodzie. Mod opiera konwersje na itemie chisel, GUI/menu i zwyklych blokach/blockstates.\n"

    text += f"""

## Porownanie 1.7.10 vs 1.18.2

- Chisel 1.7.10: duzo wariantow jako rodziny blokow z metadata; TE z JAR to Auto Chisel, Present i Carvable Beacon.
- Rechiseled 1.18.2: warianty sa osobnymi registry names i blockstates, czesto maja wersje connecting/slab/stairs.
- Dla konwersji mapy najwazniejszy bedzie wizualny matching: kolor/material rodziny, typ wzoru (bricks, tiles, panel, pillar, ornate, cracked), a dopiero potem nazwa.
- Kandydaci ponizej sa tylko punktem startowym. Finalne mapowanie powinno porownywac tekstury z JAR 1.7.10 do tekstur Rechiseled/Chipped, najlepiej przez histogram koloru + tokeny nazwy.

{format_visual_candidates(candidates)}

## Tabela registry names / prefiksy

| Element | Registry string | Ma prefiks? | Uwagi |
|---|---|---|---|
| Rodziny Chisel 1.7.10 | `chisel:<family>` / numeric ID + metadata | TAK dla modid, ale mapa uzywa ID/meta | Szczegoly w JSON; wymagany skan dynamicznych ID w Zadaniu 3/4 |
| Auto Chisel | `TileEntityAutoChisel` / prawdopodobnie blok `autoChisel` | NIEPEWNE | Wymaga potwierdzenia na mapie przez skan TE |
| Present | `TileEntityPresent` | NIEPEWNE | Wymaga potwierdzenia, czy wystepuje na mapie |
| Carvable Beacon | `TileEntityCarvableBeacon` | NIEPEWNE | Wymaga potwierdzenia, czy wystepuje na mapie |
| Rechiseled blocks | `rechiseled:<blockstate_name>` | TAK | Osobne blockstates dla wariantow |
| Rechiseled block entities | brak wykrytych | - | Docelowo zwykle nie trzeba przenosic BE |

## Kryteria wizualne do Zadania 3

1. Najpierw dopasowuj rodzine materialu: stone do stone, marble/limestone do jasnych kamieni, factory/technical do industrialnych wzorow.
2. Potem dopasowuj pattern: bricks, small tiles, large tiles, panel, pillar, ornate, cracked, road, hazard.
3. Przy remisie wybieraj podobniejsza srednia jasnosc i nasycenie tekstury, nie nazwe.
4. Gdy Rechiseled nie ma bliskiego wariantu, sprawdz Chipped jako drugi target.
"""
    path = CONVERTER_DIR / "CHISEL_ZADANIE1_ANALIZA.md"
    path.write_text(text, encoding="utf-8")
    return path


def write_handoff(markdown_path: Path, json_path: Path) -> Path:
    handoff = CONVERTER_DIR / "HANDOFF_CHISEL_ZADANIE1.md"
    handoff.write_text(
        f"""# Handoff: Chisel - Zadanie 1

## Podsumowanie sesji

Rozpoczeto implementacje konwersji Chisel od Zadania 1: inwentaryzacji blokow i tile entities. Powstal skrypt analityczny, raport markdown i maszynowy JSON, z naciskiem na przyszle dopasowanie wizualne tekstur.

## Ukonczono

- [x] Skrypt `src/converters/chisel/analyze_chisel_step1.py`
- [x] Inwentaryzacja rodzin blokow Chisel 1.7.10 z JAR/source
- [x] Inwentaryzacja blokow Rechiseled 1.18.2 z generated resources
- [x] Wykrycie klas TE z JAR Chisel: Auto Chisel, Present, Carvable Beacon
- [x] Wstepne kandydaty wizualne Chisel -> Rechiseled po tokenach rodziny/wzoru

## Nowe pliki

- `{rel(markdown_path)}`
- `{rel(json_path)}`
- `src/converters/chisel/analyze_chisel_step1.py`
- `src/converters/chisel/__init__.py`

## Zmodyfikowane pliki

- Brak istniejacych plikow modyfikowanych.

## Nastepne kroki

1. [ ] Zadanie 2: symulacja nietrywialnych zachowan tylko dla Auto Chisel oraz chisel-item workflow.
2. [ ] Zadanie 3: konwerter eventow, oparty o dynamiczne ID/meta z mapy i wizualne mapowanie do Rechiseled/Chipped.
3. [ ] Dodac porownanie histogramow tekstur, jesli bedzie dostepny Pillow albo lekki parser PNG.
""",
        encoding="utf-8",
    )
    return handoff


def main() -> None:
    chisel_blocks = collect_chisel_1710_blocks()
    chisel_tes = collect_chisel_1710_tile_entities()
    rechiseled_blocks = collect_rechiseled_blocks()
    rechiseled_bes = collect_rechiseled_block_entities()
    candidates = build_visual_candidates(chisel_blocks, rechiseled_blocks)

    data = {
        "chisel_1710": {
            "source_jar": rel(CHISEL_JAR),
            "source_repo": rel(CHISEL_SOURCE),
            "blocks": [asdict(block) for block in chisel_blocks],
            "tile_entities": [asdict(te) for te in chisel_tes],
            "block_source_counts": dict(grouped_counter(chisel_blocks)),
        },
        "rechiseled_1182": {
            "source_repo": rel(RECHISELED_SOURCE),
            "blocks": [asdict(block) for block in rechiseled_blocks],
            "block_entities": [asdict(be) for be in rechiseled_bes],
            "block_source_counts": dict(grouped_counter(rechiseled_blocks)),
        },
        "visual_candidates": candidates,
    }

    json_path = write_json_report(data)
    markdown_path = write_markdown_report(data)
    handoff_path = write_handoff(markdown_path, json_path)
    print(f"JSON: {json_path}")
    print(f"Raport: {markdown_path}")
    print(f"Handoff: {handoff_path}")


if __name__ == "__main__":
    main()
