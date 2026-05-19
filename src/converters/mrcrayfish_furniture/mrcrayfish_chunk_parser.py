# -*- coding: utf-8 -*-
"""
Parser chunkow MrCrayfish Furniture Mod — wykrywanie blokow i TE w mapach .mca

Integruje sie z minecraft_map_parser.anvil_parser aby wykrywac bloki CFM
w chunkach mapy 1.7.10 i produkowac ConversionEvent.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path

from minecraft_map_parser.anvil_parser import AnvilParser, ChunkData
from converters.mrcrayfish_furniture.mrcrayfish_converter import MrCrayfishConverter, ConversionEvent


# Znane ID Tile Entities MrCrayfish Furniture Mod 1.7.10
# (z analizy MrCrayfishFurnitureMod.java)
KNOWN_CFM_TE_IDS = {
    "cfmOven", "cfmFridge", "cfmCabinet", "cfmFreezer", "cfmBedsideCabinet",
    "cfmMailBox", "cfmComputer", "cfmPrinter", "cfmTV", "cfmStereo",
    "cfmPresent", "cfmBin", "cfmWallCabinet", "cfmBath", "cfmBasin",
    "cfmShowerHead", "cfmCookieJar", "cfmPlate", "cfmCouch", "cfmToaster",
    "cfmChoppingBoard", "cfmBlender", "cfmMicrowave", "cfmWashingMachine",
    "cfmDishwasher", "cfmCabinetKitchen", "cfmCounterSink", "cfmCup",
}

# Mapowanie numerycznych ID blokow -> nazwy (z level.dat mapy 1.7.10)
# Uzywane przy skanowaniu sekcji blokow (dla blokow bez TE)
CFM_BLOCK_IDS = {
    2728: "cfm:lampon", 2729: "cfm:lampoff",
    2730: "cfm:coffetablewood", 2731: "cfm:coffetablestone",
    2732: "cfm:tablewood", 2733: "cfm:tablestone",
    2734: "cfm:chairwood", 2735: "cfm:chairstone",
    2736: "cfm:freezer", 2737: "cfm:fridge",
    2738: "cfm:cabinet", 2739: "cfm:couch",
    2740: "cfm:blindon", 2741: "cfm:blindoff",
    2742: "cfm:curtainon", 2743: "cfm:curtainoff",
    2744: "cfm:bedsidecabinet", 2745: "cfm:oven",
    2746: "cfm:ovenoverhead", 2747: "cfm:hedge",
    2748: "cfm:birdbath", 2750: "cfm:whitefence",
    2751: "cfm:tap", 2752: "cfm:mailbox",
    2753: "cfm:tv", 2755: "cfm:printer",
    2756: "cfm:electricfence", 2757: "cfm:doorbell",
    2758: "cfm:firealarmoff", 2759: "cfm:firealarmon",
    2760: "cfm:ceilinglightoff", 2761: "cfm:ceilinglighton",
    2762: "cfm:stereo", 2763: "cfm:toilet",
    2764: "cfm:basin", 2765: "cfm:wallcabinet",
    2766: "cfm:bath1", 2767: "cfm:bath2",
    2768: "cfm:showerbottom", 2769: "cfm:showertop",
    2770: "cfm:showerheadoff", 2771: "cfm:showerheadon",
    2772: "cfm:bin", 2773: "cfm:present",
    2774: "cfm:tree", 2775: "cfm:toaster",
    2776: "cfm:microwave", 2777: "cfm:washingmachine",
    2778: "cfm:cookiejar", 2780: "cfm:plate",
    2781: "cfm:cup", 2782: "cfm:counterdoored",
    2783: "cfm:countersink", 2784: "cfm:dishwasher",
    2785: "cfm:kitchencabinet", 2786: "cfm:choppingboard",
    2787: "cfm:barstool", 2788: "cfm:hey",
    2789: "cfm:nyan", 2790: "cfm:pattern",
    2791: "cfm:yellowGlow", 2792: "cfm:whiteGlass",
    2919: "cfm:stonepath", 3201: "cfm:blender",
    3558: "cfm:computer",
}


@dataclass
class CFMBlockInChunk:
    """Blok CFM znaleziony w chunku."""
    x: int
    y: int
    z: int
    block_id: str          # ID bloku w 1.7.10 (np. "cfm:tablewood")
    metadata: int
    chunk_x: int
    chunk_z: int
    tile_entity: Optional[Dict[str, Any]] = None
    section_y: int = 0

    @property
    def absolute_pos(self) -> Tuple[int, int, int]:
        return (self.x, self.y, self.z)

    @property
    def region_pos(self) -> Tuple[int, int]:
        return (self.chunk_x >> 5, self.chunk_z >> 5)


@dataclass
class CFMChunkResult:
    """Wynik analizy chunka pod katem CFM."""
    chunk_x: int
    chunk_z: int
    blocks: List[CFMBlockInChunk] = field(default_factory=list)
    events: List[ConversionEvent] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def block_count(self) -> int:
        return len(self.blocks)

    @property
    def has_cfm(self) -> bool:
        return len(self.blocks) > 0


class MrCrayfishChunkParser:
    """
    Parser wyspecjalizowany dla MrCrayfish Furniture Mod.

    Wykrywa Tile Entities CFM w chunkach mapy 1.7.10 i produkuje ConversionEvent.
    """

    def __init__(self, world_path: str):
        self.world_path = Path(world_path)
        self.region_path = self.world_path / "region"
        self.converter = MrCrayfishConverter()
        self.stats = {
            "chunks_analyzed": 0,
            "chunks_with_cfm": 0,
            "cfm_blocks_found": 0,
            "cfm_te_found": 0,
            "errors": 0,
        }
        self._parser_cache: Dict[Tuple[int, int], Optional[AnvilParser]] = {}

    def _get_parser(self, chunk_x: int, chunk_z: int) -> Optional[AnvilParser]:
        """Pobiera lub tworzy AnvilParser dla danego chunka."""
        region_x = chunk_x >> 5
        region_z = chunk_z >> 5
        cache_key = (region_x, region_z)

        if cache_key not in self._parser_cache:
            region_file = self.region_path / f"r.{region_x}.{region_z}.mca"
            if not region_file.exists():
                self._parser_cache[cache_key] = None
                return None
            try:
                self._parser_cache[cache_key] = AnvilParser(str(region_file))
            except Exception:
                self._parser_cache[cache_key] = None
                return None

        return self._parser_cache[cache_key]

    def analyze_chunk(self, chunk_x: int, chunk_z: int, scan_blocks: bool = False) -> CFMChunkResult:
        """
        Analizuje pojedynczy chunk w poszukiwaniu blokow/TE CFM.

        Args:
            chunk_x: Globalna wspolrzedna X chunka
            chunk_z: Globalna wspolrzedna Z chunka
            scan_blocks: Jesli True, skanuje tez sekcje blokow (dla blokow bez TE)

        Returns:
            CFMChunkResult z blokami i eventami konwersji
        """
        result = CFMChunkResult(chunk_x=chunk_x, chunk_z=chunk_z)

        try:
            parser = self._get_parser(chunk_x, chunk_z)
            if not parser:
                return result

            local_x = chunk_x % 32
            local_z = chunk_z % 32
            chunk_data = parser.get_chunk(local_x, local_z)
            if not chunk_data:
                return result

            self.stats["chunks_analyzed"] += 1

            # Zbior pozycji juz znalezionych przez TE (aby uniknac duplikatow)
            seen_positions = set()

            # Pobierz Tile Entities
            tile_entities = chunk_data.get_tile_entities()

            for te in tile_entities:
                te_id = te.get("id", "") if isinstance(te, dict) else ""
                if isinstance(te_id, bytes):
                    te_id = te_id.decode('utf-8', errors='replace')

                if te_id in KNOWN_CFM_TE_IDS:
                    self.stats["cfm_te_found"] += 1
                    cfm_block = self._extract_from_te(te, chunk_x, chunk_z)
                    if cfm_block:
                        seen_positions.add(cfm_block.absolute_pos)
                        result.blocks.append(cfm_block)
                        self.stats["cfm_blocks_found"] += 1

                        # Konwersja na event
                        event = self.converter.convert_tile_entity(
                            te,
                            cfm_block.block_id,
                            cfm_block.metadata,
                            cfm_block.absolute_pos,
                        )
                        if event:
                            result.events.append(event)

            # Opcjonalne skanowanie sekcji blokow (dla blokow bez TE)
            if scan_blocks:
                block_results = self._scan_block_sections(chunk_data, chunk_x, chunk_z, seen_positions)
                for cfm_block in block_results:
                    result.blocks.append(cfm_block)
                    self.stats["cfm_blocks_found"] += 1
                    event = self.converter.convert_block(
                        cfm_block.block_id,
                        cfm_block.metadata,
                        cfm_block.absolute_pos,
                    )
                    if event:
                        result.events.append(event)

            if result.has_cfm:
                self.stats["chunks_with_cfm"] += 1

        except Exception as e:
            result.errors.append(f"Blad parsowania chunka {chunk_x},{chunk_z}: {e}")
            self.stats["errors"] += 1

        return result

    def _extract_from_te(
        self,
        te: Dict[str, Any],
        chunk_x: int,
        chunk_z: int,
    ) -> Optional[CFMBlockInChunk]:
        """Ekstrahuje CFMBlockInChunk z Tile Entity NBT."""
        x = te.get("x", 0)
        y = te.get("y", 0)
        z = te.get("z", 0)

        # Okreslenie block_id na podstawie te_id
        te_id = te.get("id", "")
        if isinstance(te_id, bytes):
            te_id = te_id.decode('utf-8', errors='replace')

        block_id = self._te_id_to_block_id(te_id)
        metadata = 0  # Metadata nie jest przechowywana w TE, trzeba by czytac sekcje

        return CFMBlockInChunk(
            x=int(x), y=int(y), z=int(z),
            block_id=block_id,
            metadata=metadata,
            chunk_x=chunk_x,
            chunk_z=chunk_z,
            tile_entity=dict(te),
            section_y=int(y) // 16,
        )

    def _scan_block_sections(
        self,
        chunk_data: ChunkData,
        chunk_x: int,
        chunk_z: int,
        seen_positions: set,
    ) -> List[CFMBlockInChunk]:
        """Skanuje sekcje blokow w chunku w poszukiwaniu blokow CFM (bez TE)."""
        results = []
        sections = chunk_data.get_sections()

        for section in sections:
            y_tag = section.get("Y")
            section_y = y_tag.value if hasattr(y_tag, "value") else (y_tag if isinstance(y_tag, int) else 0)

            blocks_tag = section.get("Blocks")
            data_tag = section.get("Data")
            add_tag = section.get("Add") or section.get("AddBlocks")

            if not blocks_tag or not hasattr(blocks_tag, "value"):
                continue

            blocks = bytearray(blocks_tag.value)
            data = bytearray(data_tag.value) if (data_tag and hasattr(data_tag, "value")) else None
            add = bytearray(add_tag.value) if (add_tag and hasattr(add_tag, "value")) else None

            base_x = chunk_x * 16
            base_z = chunk_z * 16

            for idx, b in enumerate(blocks):
                if b == 0:
                    continue

                add_nibble = 0
                if add:
                    ai = idx >> 1
                    if ai < len(add):
                        av = add[ai]
                        add_nibble = (av >> 4) if (idx & 1) else (av & 0x0F)

                full_id = (add_nibble << 8) | (b & 0xFF)

                if full_id not in CFM_BLOCK_IDS:
                    continue

                lx = idx % 16
                lz = (idx // 16) % 16
                ly = idx // 256
                x = base_x + lx
                y = section_y * 16 + ly
                z = base_z + lz

                if (x, y, z) in seen_positions:
                    continue

                meta = 0
                if data:
                    di = idx >> 1
                    if di < len(data):
                        dv = data[di] & 0xFF
                        meta = (dv >> 4) if (idx & 1) else (dv & 0x0F)

                block_name = CFM_BLOCK_IDS[full_id]
                results.append(CFMBlockInChunk(
                    x=x, y=y, z=z,
                    block_id=block_name,
                    metadata=meta,
                    chunk_x=chunk_x,
                    chunk_z=chunk_z,
                    tile_entity=None,
                    section_y=section_y,
                ))

        return results

    @staticmethod
    def _te_id_to_block_id(te_id: str) -> str:
        """Mapuje ID TE na przyblizone ID bloku (do diagnostyki)."""
        mapping = {
            "cfmOven": "cfm:oven",
            "cfmFridge": "cfm:fridge",
            "cfmCabinet": "cfm:cabinet",
            "cfmFreezer": "cfm:freezer",
            "cfmBedsideCabinet": "cfm:bedsidecabinet",
            "cfmMailBox": "cfm:mailbox",
            "cfmComputer": "cfm:computer",
            "cfmPrinter": "cfm:printer",
            "cfmTV": "cfm:tv",
            "cfmStereo": "cfm:stereo",
            "cfmPresent": "cfm:present",
            "cfmBin": "cfm:bin",
            "cfmWallCabinet": "cfm:wallcabinet",
            "cfmBath": "cfm:bath1",
            "cfmBasin": "cfm:basin",
            "cfmShowerHead": "cfm:showerheadoff",
            "cfmCookieJar": "cfm:cookiejar",
            "cfmPlate": "cfm:plate",
            "cfmCouch": "cfm:couch",
            "cfmToaster": "cfm:toaster",
            "cfmChoppingBoard": "cfm:choppingboard",
            "cfmBlender": "cfm:blender",
            "cfmMicrowave": "cfm:microwave",
            "cfmWashingMachine": "cfm:washingmachine",
            "cfmDishwasher": "cfm:dishwasher",
            "cfmCabinetKitchen": "cfm:kitchencabinet",
            "cfmCounterSink": "cfm:countersink",
            "cfmCup": "cfm:cup",
        }
        return mapping.get(te_id, "cfm:unknown")

    def analyze_region(self, region_x: int, region_z: int) -> List[CFMChunkResult]:
        """Analizuje wszystkie chunki w regionie (32x32)."""
        results = []
        for cz in range(32):
            for cx in range(32):
                chunk_x = region_x * 32 + cx
                chunk_z = region_z * 32 + cz
                result = self.analyze_chunk(chunk_x, chunk_z)
                if result.has_cfm:
                    results.append(result)
        return results

    def scan_all_regions(self, progress_callback=None) -> List[CFMChunkResult]:
        """Skanuje wszystkie regiony w folderze world/region."""
        results = []
        if not self.region_path.exists():
            return results

        region_files = sorted(self.region_path.glob("r.*.*.mca"))
        total = len(region_files)

        for i, region_file in enumerate(region_files):
            parts = region_file.stem.split(".")
            if len(parts) != 3:
                continue
            try:
                region_x = int(parts[1])
                region_z = int(parts[2])
            except ValueError:
                continue

            if progress_callback:
                progress = (i / total) * 100 if total else 0
                progress_callback(progress, f"Region {region_x},{region_z}")

            results.extend(self.analyze_region(region_x, region_z))

        if progress_callback:
            progress_callback(100, "Zakonczono")

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Zwraca statystyki skanowania."""
        return dict(self.stats)
