"""
ProjectRed Main Converter

Główny konwerter dla moda ProjectRed.
Integruje wszystkie komponenty i obsługuje konwersję bloków,
TileEntity/BlockEntity oraz multipart (bramki, przewody).

Source mapping:
- 1.7.10: mod_src/1710/actual_src/1.7.10/ProjectRed_GTNH/
- 1.18.2: mod_src/118/actual_src/1.18.2/ProjectRed/repo/
- Dokumentacja: docs/mod_mapping_indepth/from/projectred_*.md

Zgodność z SKILL.md:
- Implementacja na podstawie źródeł (Source mapping w każdym konwerterze)
- Orientacja w blockstate_props, nie w NBT
- Metadata jako parametr wejściowy
- Fail-safe z kodami błędów (PR-E-*, PR-W-*)
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple

from .mappings import (
    get_block_mapping,
    get_all_mappings,
    ALL_PROJECTRED_BLOCK_IDS_1710,
    BlockMapping
)
from .nbt_converters import (
    BaseNBTConverter,
    NBTConversionResult,
    IdentityConverter,
    # Expansion
    BatteryBoxConverter,
    ChargingBenchConverter,
    ElectrotineGeneratorConverter,
    FrameMotorConverter,
    FrameActuatorConverter,
    BlockBreakerConverter,
    FireStarterConverter,
    ProjectBenchConverter,
    AutoCrafterConverter,
    DeployerConverter,
    # Multipart
    GatePartConverter,
    RedstoneGatePartConverter,
    SequentialGatePartConverter,
    ArrayGatePartConverter,
    RedwirePartConverter,
    InsulatedWirePartConverter,
    BundledCablePartConverter,
    FramedWirePartConverter,
    get_gate_block_id_1182,
    get_wire_block_id_1182
)


@dataclass
class ConversionResult:
    """Wynik konwersji bloku/części"""
    success: bool
    block_id_1182: Optional[str] = None
    blockstate_props: Dict[str, str] = field(default_factory=dict)
    nbt_1182: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    removed: bool = False  # True jeśli blok został usunięty w 1.18.2


@dataclass
class ProjectRedBlockConversion:
    """
    Reprezentuje konwersję pojedynczego bloku/części ProjectRed.
    """
    original_id: str
    original_pos: Tuple[int, int, int]
    metadata: int
    converted: ConversionResult

    def to_dict(self) -> Dict[str, Any]:
        """Eksportuje do słownika"""
        return {
            'original_id': self.original_id,
            'original_pos': self.original_pos,
            'original_metadata': self.metadata,
            'new_id': self.converted.block_id_1182,
            'blockstate_props': self.converted.blockstate_props,
            'nbt': self.converted.nbt_1182,
            'errors': self.converted.errors,
            'warnings': self.converted.warnings,
            'removed': self.converted.removed
        }


class ProjectRedConverter:
    """
    Główny konwerter ProjectRed.

    Obsługuje:
    - Mapowanie ID bloków (1.7.10 -> 1.18.2)
    - Konwersję NBT TileEntity/BlockEntity
    - Specjalne przypadki:
      * Metadata -> osobne bloki (rudy, kamienie, maszyny)
      * Usunięte bloki (z ostrzeżeniem)
      * Multipart (bramki, przewody)
    """

    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"

    def __init__(self):
        self._init_converters()
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def _init_converters(self):
        """Inicjalizuje mapę konwerterów NBT"""
        self.nbt_converters: Dict[str, BaseNBTConverter] = {
            # Expansion machines
            'battery_box': BatteryBoxConverter(),
            'charging_bench': ChargingBenchConverter(),
            'electrotine_generator': ElectrotineGeneratorConverter(),
            'frame_motor': FrameMotorConverter(),
            'frame_actuator': FrameActuatorConverter(),
            'block_breaker': BlockBreakerConverter(),
            'fire_starter': FireStarterConverter(),
            'project_bench': ProjectBenchConverter(),
            'auto_crafter': AutoCrafterConverter(),
            'deployer': DeployerConverter(),

            # Multipart - gates
            'gate_part': GatePartConverter(),
            'redstone_gate_part': RedstoneGatePartConverter(),
            'sequential_gate_part': SequentialGatePartConverter(),
            'array_gate_part': ArrayGatePartConverter(),

            # Multipart - wires
            'redwire_part': RedwirePartConverter(),
            'insulated_wire_part': InsulatedWirePartConverter(),
            'bundled_cable_part': BundledCablePartConverter(),
            'framed_wire_part': FramedWirePartConverter(),

            # Default (identity)
            'default': IdentityConverter(),
            'lamp': IdentityConverter(),  # Lampy nie mają specjalnego NBT
            'ic_workbench': IdentityConverter(),  # Placeholder
        }

    def convert_block(self,
                      block_id_1710: str,
                      nbt_1710: Optional[Dict[str, Any]] = None,
                      metadata: int = 0,
                      position: Tuple[int, int, int] = (0, 0, 0)) -> ProjectRedBlockConversion:
        """
        Konwertuje blok ProjectRed z 1.7.10 do 1.18.2.

        Args:
            block_id_1710: ID bloku w wersji 1.7.10
            nbt_1710: NBT TileEntity (opcjonalnie)
            metadata: Metadata bloku (0-15) - WEJŚCIE, nie z NBT!
            position: Pozycja (x, y, z)

        Returns:
            ProjectRedBlockConversion z wynikiem konwersji
        """
        self.errors.clear()
        self.warnings.clear()

        # Krok 1: Znajdź mapowanie bloku
        mapping = get_block_mapping(block_id_1710, metadata)

        if not mapping:
            error_msg = f"PR-E-BLOCK-NOT-MAPPED: Nie znaleziono mapowania dla {block_id_1710} meta={metadata}"
            self.errors.append(error_msg)
            return ProjectRedBlockConversion(
                original_id=block_id_1710,
                original_pos=position,
                metadata=metadata,
                converted=ConversionResult(
                    success=False,
                    errors=[error_msg]
                )
            )

        # Krok 2: Sprawdź czy blok został usunięty
        if mapping.removed:
            warning_msg = f"PR-W-BLOCK-REMOVED: {block_id_1710} meta={metadata} został usunięty w 1.18.2. {mapping.notes}"
            self.warnings.append(warning_msg)
            return ProjectRedBlockConversion(
                original_id=block_id_1710,
                original_pos=position,
                metadata=metadata,
                converted=ConversionResult(
                    success=True,  # "Sukces" ale z flagą removed
                    block_id_1182=None,
                    warnings=[warning_msg],
                    removed=True
                )
            )

        # Krok 3: Konwertuj NBT (jeśli jest BlockEntity)
        nbt_result = None
        if mapping.has_block_entity and nbt_1710 and mapping.nbt_converter:
            nbt_result = self._convert_nbt(
                mapping.nbt_converter,
                nbt_1710,
                block_id_1710,
                metadata
            )

        # Krok 4: Zbuduj wynik
        blockstate_props = {}
        if nbt_result and nbt_result.blockstate_props:
            blockstate_props = nbt_result.blockstate_props

        converted = ConversionResult(
            success=True,
            block_id_1182=mapping.id_1182,
            blockstate_props=blockstate_props,
            nbt_1182=nbt_result.converted_nbt if nbt_result else None,
            errors=nbt_result.errors if nbt_result else [],
            warnings=nbt_result.warnings if nbt_result else []
        )

        return ProjectRedBlockConversion(
            original_id=block_id_1710,
            original_pos=position,
            metadata=metadata,
            converted=converted
        )

    def convert_multipart(self,
                          part_type: str,
                          nbt_1710: Dict[str, Any],
                          position: Tuple[int, int, int] = (0, 0, 0)) -> ProjectRedBlockConversion:
        """
        Konwertuje część multipart (bramka lub przewód).

        Args:
            part_type: Typ części (pr_sgate, pr_igate, pr_agate, pr_bgate,
                                   pr_redwire, pr_insulated, pr_bundled)
            nbt_1710: NBT części
            position: Pozycja (x, y, z)

        Returns:
            ProjectRedBlockConversion z wynikiem konwersji
        """
        self.errors.clear()
        self.warnings.clear()

        # Określ konwerter i typ bloku na podstawie part_type
        if part_type.startswith("pr_") and "gate" in part_type:
            return self._convert_gate_part(part_type, nbt_1710, position)
        elif part_type in ("pr_redwire", "pr_insulated", "pr_bundled", "pr_framed"):
            return self._convert_wire_part(part_type, nbt_1710, position)
        else:
            error_msg = f"PR-E-UNKNOWN-PART-TYPE: Nieznany typ części: {part_type}"
            return ProjectRedBlockConversion(
                original_id=part_type,
                original_pos=position,
                metadata=0,
                converted=ConversionResult(
                    success=False,
                    errors=[error_msg]
                )
            )

    def _convert_gate_part(self,
                           part_type: str,
                           nbt_1710: Dict[str, Any],
                           position: Tuple[int, int, int]) -> ProjectRedBlockConversion:
        """Konwertuje bramkę logiczną"""

        # Wybierz odpowiedni konwerter
        if part_type == "pr_sgate":
            converter_name = "redstone_gate_part"
        elif part_type == "pr_igate":
            converter_name = "sequential_gate_part"
        elif part_type == "pr_agate":
            converter_name = "array_gate_part"
        elif part_type == "pr_bgate":
            converter_name = "gate_part"
        else:
            converter_name = "gate_part"

        # Konwertuj NBT
        nbt_result = self._convert_nbt(converter_name, nbt_1710, part_type, 0)

        # Pobierz subID do określenia typu bramki
        sub_id = nbt_1710.get("subID", 0)
        block_id_1182 = get_gate_block_id_1182(sub_id, part_type)

        # Usuń wewnętrzne pola pomocnicze z NBT
        if nbt_result.converted_nbt:
            nbt_result.converted_nbt.pop("__gate_type", None)
            nbt_result.converted_nbt.pop("__gate_sub_id", None)

        return ProjectRedBlockConversion(
            original_id=part_type,
            original_pos=position,
            metadata=sub_id,
            converted=ConversionResult(
                success=nbt_result.success,
                block_id_1182=block_id_1182,
                blockstate_props=nbt_result.blockstate_props,
                nbt_1182=nbt_result.converted_nbt,
                errors=nbt_result.errors,
                warnings=nbt_result.warnings
            )
        )

    def _convert_wire_part(self,
                           part_type: str,
                           nbt_1710: Dict[str, Any],
                           position: Tuple[int, int, int]) -> ProjectRedBlockConversion:
        """Konwertuje przewód"""

        # Mapowanie typ części -> konwerter
        converter_map = {
            "pr_redwire": "redwire_part",
            "pr_insulated": "insulated_wire_part",
            "pr_bundled": "bundled_cable_part",
            "pr_framed": "framed_wire_part"
        }

        converter_name = converter_map.get(part_type, "redwire_part")
        nbt_result = self._convert_nbt(converter_name, nbt_1710, part_type, 0)

        # Określ kolor (jeśli dotyczy)
        colour = nbt_1710.get("colour", -1)

        # Mapowanie typ -> wire_type dla get_wire_block_id_1182
        wire_type_map = {
            "pr_redwire": "redwire",
            "pr_insulated": "insulated",
            "pr_bundled": "bundled",
            "pr_framed": "framed"
        }
        wire_type = wire_type_map.get(part_type, "redwire")
        block_id_1182 = get_wire_block_id_1182(wire_type, colour)

        # Usuń wewnętrzne pola pomocnicze
        if nbt_result.converted_nbt:
            nbt_result.converted_nbt.pop("__colour", None)

        return ProjectRedBlockConversion(
            original_id=part_type,
            original_pos=position,
            metadata=colour if colour >= 0 else 0,
            converted=ConversionResult(
                success=nbt_result.success,
                block_id_1182=block_id_1182,
                blockstate_props=nbt_result.blockstate_props,
                nbt_1182=nbt_result.converted_nbt,
                errors=nbt_result.errors,
                warnings=nbt_result.warnings
            )
        )

    def _convert_nbt(self, converter_name: str,
                     nbt_1710: Dict[str, Any],
                     block_id: str = None,
                     metadata: int = 0) -> NBTConversionResult:
        """Wykonuje konwersję NBT używając odpowiedniego konwertera"""
        converter = self.nbt_converters.get(converter_name)
        if not converter:
            converter = self.nbt_converters['default']

        converter.reset()
        return converter.convert(nbt_1710, block_id, metadata)

    def is_projectred_block(self, block_id: str) -> bool:
        """Sprawdza czy blok należy do ProjectRed"""
        # Sprawdź dokładne dopasowanie
        if block_id in ALL_PROJECTRED_BLOCK_IDS_1710:
            return True

        # Sprawdź czy zawiera prefix ProjectRed
        projectred_prefixes = [
            "ProjRed|",
            "projectred.",
            "projectred_"
        ]
        return any(block_id.startswith(p) or p in block_id for p in projectred_prefixes)

    def is_projectred_multipart(self, part_type: str) -> bool:
        """Sprawdza czy część multipart należy do ProjectRed"""
        pr_part_types = {
            "pr_sgate", "pr_igate", "pr_agate", "pr_bgate",
            "pr_redwire", "pr_insulated", "pr_bundled", "pr_framed"
        }
        return part_type in pr_part_types

    def get_supported_blocks(self) -> List[str]:
        """Zwraca listę obsługiwanych bloków ProjectRed"""
        return list(ALL_PROJECTRED_BLOCK_IDS_1710)

    def get_conversion_report(self) -> Dict[str, Any]:
        """Generuje raport o możliwościach konwersji"""
        all_mappings = get_all_mappings()
        removed_count = len([m for m in all_mappings if m.removed])

        return {
            'source_version': self.SOURCE_VERSION,
            'target_version': self.TARGET_VERSION,
            'supported_blocks': len(all_mappings),
            'removed_blocks': removed_count,
            'nbt_converters': list(self.nbt_converters.keys()),
            'special_cases': [
                'Metadata -> osobne bloki (rudy, kamienie, maszyny)',
                'Usunięte bloki z ostrzeżeniem (TileInductiveFurnace, TileItemImporter, etc.)',
                'Multipart gates: subID -> osobne typy bloków',
                'Multipart wires: colour -> osobne bloki',
                'ElectrotineGenerator przeniesiony z Expansion do Core',
                'BlockPlacer zastąpiony przez Deployer',
                'ICPrinter zastąpiony przez 3 nowe stoły'
            ],
            'source_mapping': {
                '1.7.10': 'mod_src/1710/actual_src/1.7.10/ProjectRed_GTNH/',
                '1.18.2': 'mod_src/118/actual_src/1.18.2/ProjectRed/repo/'
            }
        }


def main():
    """Demo konwertera ProjectRed"""
    converter = ProjectRedConverter()

    print("=" * 60)
    print("PROJECTRED CONVERTER - Demo")
    print("=" * 60)

    # Raport
    report = converter.get_conversion_report()
    print("\nRaport konwersji:")
    print(f"  Wersja źródłowa: {report['source_version']}")
    print(f"  Wersja docelowa: {report['target_version']}")
    print(f"  Obsługiwane bloki: {report['supported_blocks']}")
    print(f"  Usunięte bloki: {report['removed_blocks']}")
    print(f"  Konwertery NBT: {len(report['nbt_converters'])}")

    # Przykład konwersji BatteryBox
    print("\n" + "=" * 60)
    print("Przykład: Konwersja BatteryBox")
    print("=" * 60)

    battery_nbt = {
        "storage": 5000,
        "items": [
            {"Slot": 0, "id": "minecraft:redstone", "Count": 64}
        ]
    }

    result = converter.convert_block(
        "ProjRed|Expansion:projectred.expansion.machine2",
        battery_nbt,
        metadata=5,  # BatteryBox
        position=(100, 64, 100)
    )

    print(f"\nOryginalny blok: {result.original_id} meta={result.metadata}")
    print(f"Nowy blok: {result.converted.block_id_1182}")
    print(f"NBT: {result.converted.nbt_1182}")

    # Przykład konwersji bramki
    print("\n" + "=" * 60)
    print("Przykład: Konwersja bramki AND")
    print("=" * 60)

    gate_nbt = {
        "orient": 0x23,  # side=2, rotation=3
        "subID": 3,      # AND gate
        "shape": 0,
        "connMap": 0xF,
        "schedTime": 0,
        "state": 0b00001111
    }

    result = converter.convert_multipart(
        "pr_sgate",
        gate_nbt,
        position=(100, 64, 101)
    )

    print(f"\nOryginalny typ: pr_sgate subID=3")
    print(f"Nowy blok: {result.converted.block_id_1182}")
    print(f"BlockState: {result.converted.blockstate_props}")
    print(f"NBT: {result.converted.nbt_1182}")

    # Przykład usuniętego bloku
    print("\n" + "=" * 60)
    print("Przykład: Usunięty blok (TileItemImporter)")
    print("=" * 60)

    result = converter.convert_block(
        "ProjRed|Expansion:projectred.expansion.machine2",
        {},
        metadata=1,  # TileItemImporter
        position=(100, 64, 102)
    )

    print(f"\nOryginalny blok: {result.original_id} meta={result.metadata}")
    print(f"Usunięty: {result.converted.removed}")
    print(f"Ostrzeżenia: {result.converted.warnings}")

    print("\n" + "=" * 60)
    print("Demo zakończone!")
    print("=" * 60)


if __name__ == "__main__":
    main()
