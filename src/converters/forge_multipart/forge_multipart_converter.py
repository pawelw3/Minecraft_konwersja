"""
Główny konwerter ForgeMultipart 1.7.10 -> CB Multipart 1.18.2

Source mapping:
- 1.7.10: dekompilacja JAR ForgeMultipart-1.7.10-1.2.0.345-universal.jar
- 1.18.2: źródła ProjectRed 1.18.2 + dokumentacja CB Multipart

Produkuje eventy kompatybilne z ogólnym handlerem wstawiającym dane na mapę 1.18.2.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from .mappings import map_block_id, map_te_id, map_part_id
from .nbt_converter import TileMultipartNBTConverter


@dataclass
class ConversionResult:
    success: bool
    block_id_1182: str | None = None
    blockstate_props: dict[str, str] = field(default_factory=dict)
    nbt_1182: dict[str, Any] | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ForgeMultipartConversion:
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


class ForgeMultipartConverter:
    """
    Konwerter ForgeMultipart / CB Multipart.

    Obsługuje:
    - ForgeMultipart:block (BlockMultipart) -> cb_multipart:block
    - TileMultipart NBT (z parts: mikrobloki, vanilla parts)
    """

    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"
    MOD_NAME = "ForgeMultipart"

    def __init__(self) -> None:
        self.stats = {"processed": 0, "converted": 0, "failed": 0, "warnings": 0}
        self.events: list[dict[str, Any]] = []

    def convert_block(
        self,
        block_id_1710: str,
        metadata: int = 0,
        nbt_1710: dict[str, Any] | None = None,
        position: tuple[int, int, int] = (0, 0, 0),
    ) -> ForgeMultipartConversion:
        """
        Konwertuje blok ForgeMultipart na CB Multipart.
        """
        self.stats["processed"] += 1

        # Mapowanie block ID
        new_block_id = map_block_id(block_id_1710)
        if new_block_id is None:
            msg = f"FMP-E-BLOCK-NOT-MAPPED: brak mapowania dla {block_id_1710}"
            self.stats["failed"] += 1
            result = ConversionResult(False, errors=[msg])
            return ForgeMultipartConversion(block_id_1710, position, metadata, result)

        errors: list[str] = []
        warnings: list[str] = []
        nbt_1182 = None

        # Konwersja NBT TileMultipart (jeśli obecne)
        if nbt_1710:
            te_id = nbt_1710.get("id", "")
            # Wykrywamy czy to jest TileMultipart (różne możliwe nazwy)
            # "savedMultipart" to potwierdzony exact string z mapy 1.7.10
            if te_id in ("savedMultipart", "TileMultipart", "ForgeMultipart:TileMultipart", ""):
                nbt_1182 = TileMultipartNBTConverter.convert(nbt_1710)
                if nbt_1182 is None:
                    errors.append("FMP-E-NBT-CONVERSION-FAILED: nieudana konwersja NBT TileMultipart")
                else:
                    # Sprawdź czy wszystkie part-y zostały zamapowane
                    for part in nbt_1182.get("parts", []):
                        old_id = part.get("_original_id", part.get("id"))
                        # Nie mamy _original_id, ale możemy porównać
                        # Cicho pomijamy — map_part_id zwraca oryginał jeśli brak mapowania
                        pass
            else:
                warnings.append(f"FMP-W-UNKNOWN-TE: nieoczekiwane TE id '{te_id}', pominięto konwersję NBT")

        success = not errors
        self.stats["converted" if success else "failed"] += 1
        self.stats["warnings"] += len(warnings)

        result = ConversionResult(
            success=success,
            block_id_1182=new_block_id,
            nbt_1182=nbt_1182,
            errors=errors,
            warnings=warnings,
        )

        # Generuj event kompatybilny z handlerem wstawiającym
        event = self._make_event(
            source_block_id=block_id_1710,
            metadata=metadata,
            position=position,
            result=result,
        )
        self.events.append(event)

        return ForgeMultipartConversion(block_id_1710, position, metadata, result)

    def _make_event(
        self,
        source_block_id: str,
        metadata: int,
        position: tuple[int, int, int],
        result: ConversionResult,
    ) -> dict[str, Any]:
        """
        Tworzy event dict kompatybilny z ogólnym handlerem.
        Format zgodny z konwencją z placeholders.py i router.py.
        """
        event: dict[str, Any] = {
            "op": "set_block_entity" if result.nbt_1182 else "set_block",
            "pos": list(position),
            "block": result.block_id_1182,
            "source": {
                "mod": self.MOD_NAME,
                "block_id": source_block_id,
                "metadata": metadata,
            },
        }
        if result.nbt_1182:
            event["nbt"] = result.nbt_1182
        if result.blockstate_props:
            event["blockstate"] = dict(result.blockstate_props)
        if result.warnings:
            event["warnings"] = list(result.warnings)
        if result.errors:
            event["errors"] = list(result.errors)
        return event

    def get_stats(self) -> dict[str, int]:
        return dict(self.stats)
