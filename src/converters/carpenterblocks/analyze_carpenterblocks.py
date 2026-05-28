"""
Krok 1: Analiza bloków CarpentersBlocks w mapie 1.7.10.

Skrypt przeszukuje chunki .mca świata 1.7.10, znajduje bloki CB i raportuje:
  - listę unikalnych ID bloków CB
  - rozkład typów geometrii (slopeID, stairsID, cbMetadata)
  - schematy NBT tile entity
  - przykłady cover materials (cbUniqueId)
  - statystyki count per block type

Użycie:
  python -m src.converters.carpenterblocks.analyze_carpenterblocks \
         --world <ścieżka_do_świata_1.7.10> \
         [--region-dir region] \
         [--sample 200] \
         [--out analysis/carpenterblocks_analysis.json]

Wyjście: plik JSON + skrócony raport na stdout.
"""

from __future__ import annotations

import argparse
import json
import os
import struct
import sys
import zlib
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


# --- NBT helpers (minimalistyczny parser bez zewnętrznych zależności) -----------

TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_INT_ARRAY = 11
TAG_LONG_ARRAY = 12


def _read(buf: bytes, pos: int, fmt: str) -> tuple:
    size = struct.calcsize(fmt)
    return struct.unpack_from(fmt, buf, pos), pos + size


def parse_nbt(buf: bytes, pos: int = 0) -> tuple[dict | None, int]:
    """Parsuje NBT ze strumienia bajtów. Zwraca (tag_value, new_pos)."""
    tag_type = buf[pos]
    pos += 1
    if tag_type == TAG_END:
        return None, pos
    # name (string)
    (name_len,), pos = _read(buf, pos, ">H")
    name = buf[pos: pos + name_len].decode("utf-8", errors="replace")
    pos += name_len
    value, pos = _parse_payload(buf, pos, tag_type)
    return {name: value}, pos


def _parse_payload(buf: bytes, pos: int, tag_type: int) -> tuple[Any, int]:
    if tag_type == TAG_BYTE:
        (v,), pos = _read(buf, pos, ">b")
        return v, pos
    if tag_type == TAG_SHORT:
        (v,), pos = _read(buf, pos, ">h")
        return v, pos
    if tag_type == TAG_INT:
        (v,), pos = _read(buf, pos, ">i")
        return v, pos
    if tag_type == TAG_LONG:
        (v,), pos = _read(buf, pos, ">q")
        return v, pos
    if tag_type == TAG_FLOAT:
        (v,), pos = _read(buf, pos, ">f")
        return v, pos
    if tag_type == TAG_DOUBLE:
        (v,), pos = _read(buf, pos, ">d")
        return v, pos
    if tag_type == TAG_BYTE_ARRAY:
        (length,), pos = _read(buf, pos, ">i")
        data = buf[pos: pos + length]
        pos += length
        return list(data), pos
    if tag_type == TAG_STRING:
        (length,), pos = _read(buf, pos, ">H")
        s = buf[pos: pos + length].decode("utf-8", errors="replace")
        pos += length
        return s, pos
    if tag_type == TAG_LIST:
        (elem_type,), pos = _read(buf, pos, ">b")
        (length,), pos = _read(buf, pos, ">i")
        items = []
        for _ in range(length):
            v, pos = _parse_payload(buf, pos, elem_type)
            items.append(v)
        return items, pos
    if tag_type == TAG_COMPOUND:
        compound: dict[str, Any] = {}
        while True:
            inner_type = buf[pos]
            pos += 1
            if inner_type == TAG_END:
                break
            (name_len,), pos = _read(buf, pos, ">H")
            key = buf[pos: pos + name_len].decode("utf-8", errors="replace")
            pos += name_len
            value, pos = _parse_payload(buf, pos, inner_type)
            compound[key] = value
        return compound, pos
    if tag_type == TAG_INT_ARRAY:
        (length,), pos = _read(buf, pos, ">i")
        items = []
        for _ in range(length):
            (v,), pos = _read(buf, pos, ">i")
            items.append(v)
        return items, pos
    if tag_type == TAG_LONG_ARRAY:
        (length,), pos = _read(buf, pos, ">i")
        items = []
        for _ in range(length):
            (v,), pos = _read(buf, pos, ">q")
            items.append(v)
        return items, pos
    raise ValueError(f"Unknown NBT tag type: {tag_type} at pos {pos}")


def read_nbt_root(buf: bytes) -> dict[str, Any]:
    """Parsuje korzeń NBT (TAG_Compound z nazwą)."""
    tag_type = buf[0]
    if tag_type != TAG_COMPOUND:
        raise ValueError(f"Root tag must be TAG_Compound, got {tag_type}")
    (name_len,), pos = _read(buf, 1, ">H")
    pos += name_len  # pomijamy nazwę korzenia
    compound, _ = _parse_payload(buf, pos, TAG_COMPOUND)
    return compound


# --- Parsowanie regionów Anvil (.mca) -------------------------------------------

def iter_chunks(region_file: Path):
    """Iteruje po skompresowanych danych chunkowych w pliku .mca."""
    with open(region_file, "rb") as f:
        header = f.read(8192)
    for i in range(1024):
        offset_raw = struct.unpack_from(">I", header, i * 4)[0]
        offset = (offset_raw >> 8) * 4096
        sector_count = offset_raw & 0xFF
        if offset == 0 or sector_count == 0:
            continue
        with open(region_file, "rb") as f:
            f.seek(offset)
            length_raw = f.read(4)
            if len(length_raw) < 4:
                continue
            (length,) = struct.unpack(">I", length_raw)
            compression = ord(f.read(1))
            data = f.read(length - 1)
        try:
            if compression == 2:
                decompressed = zlib.decompress(data)
            elif compression == 1:
                import gzip
                decompressed = gzip.decompress(data)
            else:
                continue
            yield read_nbt_root(decompressed)
        except Exception:
            continue


# --- Bloki CarpentersBlocks -------------------------------------------------------

CB_MOD_PREFIX = "CarpentersBlocks:"
CB_TE_IDS = {
    "CarpentersBlocks.blockCarpentersBarrier",
    "CarpentersBlocks.blockCarpentersBed",
    "CarpentersBlocks.blockCarpentersBlock",
    "CarpentersBlocks.blockCarpentersButton",
    "CarpentersBlocks.blockCarpentersCollapsibleBlock",
    "CarpentersBlocks.blockCarpentersDaylightSensor",
    "CarpentersBlocks.blockCarpentersDoor",
    "CarpentersBlocks.blockCarpentersFlowerPot",
    "CarpentersBlocks.blockCarpentersGarageDoor",
    "CarpentersBlocks.blockCarpentersGate",
    "CarpentersBlocks.blockCarpentersHatch",
    "CarpentersBlocks.blockCarpentersLadder",
    "CarpentersBlocks.blockCarpentersLever",
    "CarpentersBlocks.blockCarpentersPressurePlate",
    "CarpentersBlocks.blockCarpentersSafe",
    "CarpentersBlocks.blockCarpentersSlope",
    "CarpentersBlocks.blockCarpentersStairs",
    "CarpentersBlocks.blockCarpentersTorch",
}


def is_cb_te(te: dict) -> bool:
    """Sprawdza czy tile entity należy do CarpentersBlocks."""
    te_id = te.get("id", "")
    if isinstance(te_id, str):
        return te_id in CB_TE_IDS
    return False


def extract_cover_material(attr_entry: dict) -> str | None:
    """Wydobywa identyfikator materiału pokrycia z wpisu cbAttrList."""
    unique_id = attr_entry.get("cbUniqueId", "")
    if unique_id:
        return unique_id
    # Fallback: id numeryczne lub string
    item_id = attr_entry.get("id")
    damage = attr_entry.get("Damage", 0)
    if item_id is not None:
        return f"{item_id}#{damage}"
    return None


# --- Główna logika analizy --------------------------------------------------------

class CBAnalyzer:
    def __init__(self, sample_limit: int = 0):
        self.sample_limit = sample_limit
        self.total_count: Counter[str] = Counter()
        self.metadata_dist: dict[str, Counter[int]] = defaultdict(Counter)
        self.cover_materials: dict[str, Counter[str]] = defaultdict(Counter)
        self.design_names: dict[str, Counter[str]] = defaultdict(Counter)
        self.nbt_schema_samples: dict[str, list[dict]] = defaultdict(list)
        self._te_count = 0

    def process_te(self, te: dict) -> None:
        te_id = te.get("id", "unknown")
        # Normalize: "CarpentersBlocks.blockX" -> "CarpentersBlocks:blockX"
        block_key = te_id.replace(".", ":", 1)

        self.total_count[block_key] += 1
        self._te_count += 1

        # cbMetadata (geometria)
        cb_meta = te.get("cbMetadata")
        if cb_meta is None:
            cb_meta = te.get("cbMetadata")  # czasem short/int
        if cb_meta is not None:
            self.metadata_dist[block_key][int(cb_meta)] += 1

        # cbDesign
        design = te.get("cbDesign", "")
        if design:
            self.design_names[block_key][design] += 1

        # cbAttrList - pokrycia
        attr_list = te.get("cbAttrList", [])
        if isinstance(attr_list, list):
            for attr_entry in attr_list:
                if isinstance(attr_entry, dict):
                    attr_id = attr_entry.get("cbAttribute", -1)
                    material = extract_cover_material(attr_entry)
                    if material:
                        key = f"{block_key}#attr{attr_id}"
                        self.cover_materials[key][material] += 1

        # Zapisz próbkę NBT (max 3 na typ bloku)
        samples = self.nbt_schema_samples[block_key]
        if len(samples) < 3:
            # Przechowaj zredukowany widok NBT
            sample = {
                k: v for k, v in te.items()
                if k in ("id", "cbMetadata", "cbDesign", "cbOwner")
            }
            # Dodaj pierwszy attr jeśli jest
            if isinstance(attr_list, list) and attr_list:
                sample["cbAttrList_first"] = attr_list[0] if isinstance(attr_list[0], dict) else {}
            sample["cbAttrList_count"] = len(attr_list) if isinstance(attr_list, list) else 0
            samples.append(sample)

    def process_chunk(self, chunk_nbt: dict) -> int:
        """Przetwarza chunk, zwraca liczbę przetworzonych TE."""
        count = 0
        # Format 1.7.10 Anvil: chunk["Level"]["TileEntities"]
        level = chunk_nbt.get("Level", {})
        tile_entities = level.get("TileEntities", [])
        if not isinstance(tile_entities, list):
            return 0
        for te in tile_entities:
            if isinstance(te, dict) and is_cb_te(te):
                self.process_te(te)
                count += 1
        return count

    def build_report(self) -> dict:
        total = sum(self.total_count.values())
        return {
            "summary": {
                "total_cb_tile_entities": total,
                "unique_block_types": len(self.total_count),
                "counts_by_block": dict(self.total_count.most_common()),
            },
            "geometry": {
                block: dict(counter.most_common(30))
                for block, counter in self.metadata_dist.items()
            },
            "cover_materials": {
                key: dict(counter.most_common(10))
                for key, counter in self.cover_materials.items()
            },
            "design_names": {
                block: dict(counter.most_common(10))
                for block, counter in self.design_names.items()
            },
            "nbt_samples": dict(self.nbt_schema_samples),
        }


def run(world_path: str, region_dir: str, sample: int, out: str) -> None:
    world = Path(world_path)
    region_path = world / region_dir
    if not region_path.exists():
        print(f"[ERROR] Brak katalogu regionów: {region_path}", file=sys.stderr)
        sys.exit(1)

    region_files = sorted(region_path.glob("r.*.*.mca"))
    if not region_files:
        print(f"[ERROR] Brak plików .mca w {region_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Znaleziono {len(region_files)} plików regionów.")
    analyzer = CBAnalyzer(sample_limit=sample)
    processed_chunks = 0
    processed_te = 0

    for rf in region_files:
        for chunk_nbt in iter_chunks(rf):
            n = analyzer.process_chunk(chunk_nbt)
            processed_te += n
            processed_chunks += 1
            if sample and processed_te >= sample:
                break
        if sample and processed_te >= sample:
            break
        print(f"  {rf.name}: {processed_te} TE łącznie", end="\r")

    print(f"\nPrzeanalizowano {processed_chunks} chunków, znaleziono {processed_te} bloków CB.")

    report = analyzer.build_report()
    report["meta"] = {
        "world": str(world),
        "region_dir": region_dir,
        "sample_limit": sample,
        "processed_chunks": processed_chunks,
    }

    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"Raport zapisano w: {out_path}")

    # Skrócony raport na stdout
    print("\n=== Podsumowanie bloków CB ===")
    for block, count in report["summary"]["counts_by_block"].items():
        short = block.replace("CarpentersBlocks:", "CB:")
        print(f"  {short:<45} {count:>6}")

    geom = report["geometry"]
    if "CarpentersBlocks:blockCarpentersSlope" in geom:
        slope_dist = geom["CarpentersBlocks:blockCarpentersSlope"]
        print(f"\nSlope cbMetadata distribution (top 10):")
        for sid, cnt in list(slope_dist.items())[:10]:
            print(f"  slopeID={sid}: {cnt}")

    if "CarpentersBlocks:blockCarpentersStairs" in geom:
        stairs_dist = geom["CarpentersBlocks:blockCarpentersStairs"]
        print(f"\nStairs cbMetadata distribution (top 10):")
        for sid, cnt in list(stairs_dist.items())[:10]:
            print(f"  stairsID={sid}: {cnt}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analiza bloków CarpentersBlocks w świecie 1.7.10"
    )
    parser.add_argument("--world", required=True, help="Ścieżka do katalogu świata")
    parser.add_argument("--region-dir", default="region", help="Podkatalog z .mca (domyślnie: region)")
    parser.add_argument("--sample", type=int, default=0, help="Limit TE (0=wszystkie)")
    parser.add_argument(
        "--out",
        default="analysis/carpenterblocks_analysis.json",
        help="Ścieżka wyjściowego pliku JSON"
    )
    args = parser.parse_args()
    run(args.world, args.region_dir, args.sample, args.out)


if __name__ == "__main__":
    main()
