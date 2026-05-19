"""Glowny konwerter dla Thermal Series.

Obsluguje Thermal Expansion, Thermal Foundation i Thermal Dynamics.
Dla elementow bez odpowiednika w 1.18.2 Thermal uzywa funkcjonalnych
odpowiednikow z Mekanism (zgodnie z decyzja projektowa).
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .mappings import get_mapping, get_mapping_by_te_id, DUCT_MAPPINGS, THERMAL_TIER_BY_META
from .nbt_converters.machine_converter import convert_machine_nbt, convert_charger_nbt, convert_insolator_nbt
from .nbt_converters.storage_converter import (
    convert_cell_nbt,
    convert_tank_nbt,
    convert_strongbox_nbt,
    convert_cache_nbt,
    convert_workbench_nbt,
)
from .nbt_converters.dynamo_converter import convert_dynamo_nbt
from .nbt_converters.duct_converter import (
    convert_energy_duct_nbt,
    convert_fluid_duct_nbt,
    convert_item_duct_nbt,
    convert_tesseract_nbt,
)


class ThermalConverter:
    """Konwerter blokow i Tile Entities Thermal Series."""

    def __init__(self):
        self.conversion_log: list[dict] = []

    def convert_block(
        self,
        block_id: str,
        metadata: int,
        nbt: Optional[dict] = None,
        position: Optional[tuple[int, int, int]] = None,
    ) -> dict:
        """Konwertuje blok z 1.7.10 na 1.18.2.

        Returns:
            dict z polami:
            - target_block_id (str)
            - target_blockstate (dict)
            - target_nbt (dict lub None)
            - warnings (list[str])
            - info (str)
        """
        warnings = []
        info = ""

        # Pobierz mapping
        mapping = get_mapping(block_id, metadata)
        if mapping is None:
            warnings.append(f"Brak mappingu dla {block_id}:{metadata}")
            return {
                "target_block_id": "minecraft:stone",
                "target_blockstate": {},
                "target_nbt": None,
                "warnings": warnings,
                "info": "Fallback na stone (brak mappingu)",
            }

        target_id = mapping.target_block_id
        target_nbt = None
        target_blockstate = {}

        # Konwersja NBT jesli jest BE
        if mapping.has_block_entity and nbt is not None:
            target_nbt = self._convert_nbt(nbt, target_id, mapping.nbt_converter)

        # Blockstate properties
        if "rockwool" in mapping.nbt_converter:
            # Rockwool kolor jest juz w target_block_id
            pass
        elif mapping.source_block_id in (
            "ThermalExpansion:Cell",
            "ThermalExpansion:Tank",
            "ThermalExpansion:Strongbox",
            "ThermalExpansion:Cache",
            "ThermalExpansion:Workbench",
        ):
            # Tier w blockstate
            tier = THERMAL_TIER_BY_META.get(metadata, "basic")
            target_blockstate["type"] = tier

        # Log conversion
        self.conversion_log.append({
            "source": f"{block_id}:{metadata}",
            "target": target_id,
            "pos": position,
            "notes": mapping.notes,
        })

        return {
            "target_block_id": target_id,
            "target_blockstate": target_blockstate,
            "target_nbt": target_nbt,
            "warnings": warnings,
            "info": mapping.notes,
        }

    def convert_te_by_id(
        self,
        te_id: str,
        nbt: dict,
        position: Optional[tuple[int, int, int]] = None,
    ) -> dict:
        """Konwertuje Tile Entity na podstawie TE ID z NBT.

        Uzywane gdy many tylko dane NBT (bez informacji o bloku).
        """
        mapping = get_mapping_by_te_id(te_id)
        if mapping is None:
            return {
                "target_block_id": "minecraft:stone",
                "target_blockstate": {},
                "target_nbt": None,
                "warnings": [f"Brak mappingu dla TE {te_id}"],
                "info": "Fallback na stone",
            }

        return self.convert_block(
            mapping.source_block_id,
            mapping.metadata or 0,
            nbt,
            position,
        )

    def _convert_nbt(self, nbt: dict, target_id: str, converter_type: str) -> Optional[dict]:
        """Wybiera i uruchamia odpowiedni konwerter NBT."""
        try:
            if converter_type == "machine":
                return convert_machine_nbt(nbt, target_id)
            elif converter_type == "device":
                return convert_machine_nbt(nbt, target_id)  # podobne do maszyn
            elif converter_type == "charger":
                return convert_charger_nbt(nbt, target_id)
            elif converter_type == "insolator":
                return convert_insolator_nbt(nbt, target_id)
            elif converter_type == "energy_cell":
                return convert_cell_nbt(nbt, target_id)
            elif converter_type == "fluid_cell":
                return convert_tank_nbt(nbt, target_id)
            elif converter_type == "item_cell":
                # Rozrozniaj Strongbox vs Cache na podstawie legacy ID
                te_id = nbt.get("id", "")
                if "Strongbox" in te_id:
                    return convert_strongbox_nbt(nbt, target_id)
                elif "Cache" in te_id:
                    return convert_cache_nbt(nbt, target_id)
                return convert_strongbox_nbt(nbt, target_id)
            elif converter_type == "tinker_bench":
                return convert_workbench_nbt(nbt, target_id)
            elif converter_type == "dynamo":
                return convert_dynamo_nbt(nbt, target_id)
            elif converter_type == "duct_energy":
                return convert_energy_duct_nbt(nbt, target_id)
            elif converter_type == "duct_fluid":
                return convert_fluid_duct_nbt(nbt, target_id)
            elif converter_type == "item_buffer":
                return convert_item_duct_nbt(nbt, target_id)
            elif converter_type == "transporter":
                return convert_item_duct_nbt(nbt, target_id)
            elif converter_type == "frequency":
                return convert_tesseract_nbt(nbt, target_id)
            elif converter_type == "buffer":
                return convert_item_duct_nbt(nbt, target_id)
            else:
                # Identity - zachowaj tylko pozycje i ID
                return {
                    "id": target_id,
                    "x": nbt.get("x", 0),
                    "y": nbt.get("y", 0),
                    "z": nbt.get("z", 0),
                }
        except Exception as e:
            return {
                "id": target_id,
                "x": nbt.get("x", 0),
                "y": nbt.get("y", 0),
                "z": nbt.get("z", 0),
                "conversion_error": str(e),
            }

    def get_stats(self) -> dict:
        """Zwraca statystyki konwersji."""
        from collections import Counter
        targets = Counter(entry["target"] for entry in self.conversion_log)
        return {
            "total_conversions": len(self.conversion_log),
            "unique_targets": len(targets),
            "top_targets": targets.most_common(10),
        }


# Singleton dla latwego importu
_converter = None


def get_converter() -> ThermalConverter:
    global _converter
    if _converter is None:
        _converter = ThermalConverter()
    return _converter
