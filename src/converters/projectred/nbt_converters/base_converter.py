"""
Base NBT Converter for ProjectRed

Bazowa klasa dla wszystkich konwerterów NBT ProjectRed.
Definiuje interfejs i wspólne funkcjonalności.

Source mapping:
- 1.7.10: mod_src/1710/actual_src/1.7.10/ProjectRed_GTNH/src/main/scala/mrtjp/projectred/
- 1.18.2: mod_src/118/actual_src/1.18.2/ProjectRed/repo/
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple


@dataclass
class NBTConversionResult:
    """Wynik konwersji NBT"""
    success: bool
    converted_nbt: Optional[Dict[str, Any]] = None
    blockstate_props: Dict[str, str] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class BaseNBTConverter(ABC):
    """
    Bazowa klasa dla konwerterów NBT ProjectRed.

    Wszystkie konwertery powinny dziedziczyć po tej klasie
    i implementować metodę convert().

    Zasady (zgodnie z SKILL.md):
    1. Implementacja na podstawie źródeł, nie domysłów
    2. Orientacja w blockstate_props, nie w NBT
    3. Metadata jako parametr wejściowy
    4. Source mapping w każdym konwerterze
    """

    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"

    # Każdy konwerter MUSI zdefiniować źródło prawdy
    SOURCE_1710: str = ""  # Ścieżka do pliku źródłowego 1.7.10
    SOURCE_1182: str = ""  # Ścieżka do pliku źródłowego 1.18.2

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    @abstractmethod
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje NBT z wersji 1.7.10 do 1.18.2.

        Args:
            nbt_1710: Słownik NBT z wersji 1.7.10
            block_id: ID bloku (opcjonalnie, dla kontekstu)
            metadata: Metadata bloku (dla wariantów) - WEJŚCIE, nie z NBT!

        Returns:
            NBTConversionResult z wynikiem konwersji
        """
        pass

    @property
    @abstractmethod
    def converter_name(self) -> str:
        """Zwraca nazwę konwertera"""
        pass

    def _create_result(self, converted_nbt: Dict[str, Any] = None,
                       blockstate_props: Dict[str, str] = None,
                       success: bool = True) -> NBTConversionResult:
        """Tworzy wynik konwersji"""
        return NBTConversionResult(
            success=success,
            converted_nbt=converted_nbt,
            blockstate_props=blockstate_props or {},
            errors=self.errors.copy(),
            warnings=self.warnings.copy()
        )

    def _add_error(self, code: str, message: str):
        """Dodaje błąd z kodem (format: MOD-E-CODE)"""
        self.errors.append(f"PR-E-{code}: {message}")

    def _add_warning(self, code: str, message: str):
        """Dodaje ostrzeżenie z kodem (format: MOD-W-CODE)"""
        self.warnings.append(f"PR-W-{code}: {message}")

    def reset(self):
        """Resetuje stan konwertera"""
        self.errors.clear()
        self.warnings.clear()

    def _convert_inventory(self, nbt_1710: Dict[str, Any],
                          inv_key: str = "items") -> Dict[str, Any]:
        """
        Konwertuje inwentarz z formatu 1.7.10 do 1.18.2.

        1.7.10: Zapisywane przez saveInv() - tablica slotów
        1.18.2: Zapisywane przez inventory.saveTo() - CompoundTag z 'Items'

        Zwraca CompoundTag z kluczem 'Items' (lista slotów).
        """
        if inv_key not in nbt_1710:
            return {"Items": []}

        items_1710 = nbt_1710.get(inv_key, [])
        if not isinstance(items_1710, list):
            return {"Items": []}

        items_1182 = []
        for slot_data in items_1710:
            if not slot_data:
                continue

            item_1182 = {
                "Slot": slot_data.get("Slot", 0),
                "id": self._convert_item_id(slot_data.get("id", "")),
                "Count": slot_data.get("Count", 1)
            }

            # W 1.18.2 Damage jest w tag, nie jako osobne pole
            if "Damage" in slot_data and slot_data["Damage"] != 0:
                item_1182["tag"] = {"Damage": slot_data["Damage"]}

            # Zachowaj istniejący tag
            if "tag" in slot_data:
                if "tag" not in item_1182:
                    item_1182["tag"] = {}
                item_1182["tag"].update(slot_data["tag"])

            items_1182.append(item_1182)

        return {"Items": items_1182}

    def _convert_item_id(self, item_id_1710: str) -> str:
        """
        Konwertuje ID itemu z 1.7.10 do 1.18.2.

        Podstawowe mapowania ProjectRed:
        - ProjRed|Core:projectred.core.* -> projectred_core:*
        - ProjRed|Expansion:projectred.expansion.* -> projectred_expansion:*
        """
        if not item_id_1710:
            return item_id_1710

        # Mapowanie prefixów modułów
        prefix_map = {
            "ProjRed|Core:": "projectred_core:",
            "ProjRed|Expansion:": "projectred_expansion:",
            "ProjRed|Exploration:": "projectred_exploration:",
            "ProjRed|Illumination:": "projectred_illumination:",
            "ProjRed|Integration:": "projectred_integration:",
            "ProjRed|Transmission:": "projectred_transmission:",
            "ProjRed|Fabrication:": "projectred_fabrication:",
            "ProjRed|Transportation:": "projectred_transportation:",
        }

        for old_prefix, new_prefix in prefix_map.items():
            if item_id_1710.startswith(old_prefix):
                name = item_id_1710[len(old_prefix):]
                # Usuń "projectred." prefix z nazwy jeśli istnieje
                if name.startswith("projectred."):
                    name = name[11:]
                # Zamień kropki na podkreślenia
                name = name.replace(".", "_").lower()
                return f"{new_prefix}{name}"

        # Vanilla i inne mody - bez zmian
        return item_id_1710

    def _metadata_to_rotation(self, metadata: int) -> int:
        """
        Konwertuje metadata do rotacji (0-3).
        W 1.7.10 wiele bloków używa metadata 0-3 dla rotacji.
        """
        return metadata & 0x3

    def _metadata_to_side(self, metadata: int) -> int:
        """
        Konwertuje metadata do strony (0-5).
        ForgeDirection: 0=DOWN, 1=UP, 2=NORTH, 3=SOUTH, 4=WEST, 5=EAST
        """
        return metadata & 0x7

    def _side_to_facing(self, side: int) -> str:
        """
        Konwertuje side (int) do facing string dla blockstate.
        """
        facing_map = {
            0: "down",
            1: "up",
            2: "north",
            3: "south",
            4: "west",
            5: "east"
        }
        return facing_map.get(side, "north")


class IdentityConverter(BaseNBTConverter):
    """
    Konwerter tożsamościowy - kopiowanie bez zmian (z usunięciem pól 1.7.10-specific).
    Używany dla bloków bez specjalnych danych NBT.

    Source mapping:
    - Nie wymaga - używany dla bloków bez TE/BE danych
    """

    SOURCE_1710 = "N/A - identity converter"
    SOURCE_1182 = "N/A - identity converter"

    @property
    def converter_name(self) -> str:
        return "identity"

    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """Kopiuje NBT bez zmian (usuwając pola specyficzne dla 1.7.10)"""
        # Usuń pola koordynatów i ID (te są w BlockEntity, nie w NBT payload)
        excluded_keys = {'id', 'x', 'y', 'z'}
        converted = {k: v for k, v in nbt_1710.items() if k not in excluded_keys}

        return self._create_result(converted)
