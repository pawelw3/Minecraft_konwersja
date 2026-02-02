"""
ProjectRed Test Structure Conversion Verifier

Weryfikuje konwersję struktur testowych z 1.7.10 do 1.18.2.
Sprawdza:
1. Czy wszystkie bloki są poprawnie mapowane
2. Czy NBT jest prawidłowo konwertowane
3. Czy multipart są obsługiwane
4. Generuje raport z wynikami

Użycie:
    python verify_conversion.py [--verbose] [--filter PATTERN]
"""

import json
import os
import sys
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

# Dodaj ścieżkę do src
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from src.converters.projectred import ProjectRedConverter
from src.converters.projectred.test_structures import (
    TestStructure,
    StructureType,
    BlockDefinition,
    MultipartDefinition
)


@dataclass
class BlockVerificationResult:
    """Wynik weryfikacji pojedynczego bloku"""
    original_id: str
    position: Tuple[int, int, int]
    success: bool
    new_id: Optional[str] = None
    blockstate_props: Dict[str, str] = field(default_factory=dict)
    nbt_converted: bool = False
    removed: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class StructureVerificationResult:
    """Wynik weryfikacji struktury"""
    structure_name: str
    structure_type: str
    total_blocks: int
    total_multiparts: int
    converted_successfully: int
    converted_with_warnings: int
    failed: int
    removed: int
    block_results: List[BlockVerificationResult] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        total = self.total_blocks + self.total_multiparts
        if total == 0:
            return 100.0
        return (self.converted_successfully / total) * 100

    def to_dict(self) -> Dict[str, Any]:
        return {
            "structure_name": self.structure_name,
            "structure_type": self.structure_type,
            "total_elements": self.total_blocks + self.total_multiparts,
            "converted_successfully": self.converted_successfully,
            "converted_with_warnings": self.converted_with_warnings,
            "failed": self.failed,
            "removed": self.removed,
            "success_rate": f"{self.success_rate:.1f}%",
            "details": [
                {
                    "original_id": r.original_id,
                    "position": list(r.position),
                    "success": r.success,
                    "new_id": r.new_id,
                    "removed": r.removed,
                    "errors": r.errors,
                    "warnings": r.warnings
                }
                for r in self.block_results
            ]
        }


class ConversionVerifier:
    """Weryfikator konwersji struktur testowych"""

    def __init__(self, verbose: bool = False):
        self.converter = ProjectRedConverter()
        self.verbose = verbose
        self.results: List[StructureVerificationResult] = []

    def load_structure(self, json_path: str) -> Dict[str, Any]:
        """Wczytuje strukturę z pliku JSON"""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def verify_block(self, block_data: Dict[str, Any]) -> BlockVerificationResult:
        """Weryfikuje konwersję pojedynczego bloku"""
        pos = tuple(block_data["pos"])
        block_id = block_data["block_id"]
        metadata = block_data.get("metadata", 0)
        nbt = block_data.get("nbt")

        # Sprawdź czy to blok ProjectRed
        if not self.converter.is_projectred_block(block_id):
            # Blok vanilla - nie konwertujemy, ale uznajemy za sukces
            return BlockVerificationResult(
                original_id=block_id,
                position=pos,
                success=True,
                new_id=block_id,  # Bez zmian
                nbt_converted=False
            )

        # Konwertuj blok ProjectRed
        conversion = self.converter.convert_block(
            block_id_1710=block_id,
            nbt_1710=nbt,
            metadata=metadata,
            position=pos
        )

        return BlockVerificationResult(
            original_id=block_id,
            position=pos,
            success=conversion.converted.success,
            new_id=conversion.converted.block_id_1182,
            blockstate_props=conversion.converted.blockstate_props,
            nbt_converted=conversion.converted.nbt_1182 is not None,
            removed=conversion.converted.removed,
            errors=conversion.converted.errors,
            warnings=conversion.converted.warnings
        )

    def verify_multipart(self, mp_data: Dict[str, Any]) -> BlockVerificationResult:
        """Weryfikuje konwersję części multipart"""
        pos = tuple(mp_data["pos"])
        part_type = mp_data["part_type"]
        nbt = mp_data.get("nbt", {})

        # Konwertuj multipart
        conversion = self.converter.convert_multipart(
            part_type=part_type,
            nbt_1710=nbt,
            position=pos
        )

        return BlockVerificationResult(
            original_id=part_type,
            position=pos,
            success=conversion.converted.success,
            new_id=conversion.converted.block_id_1182,
            blockstate_props=conversion.converted.blockstate_props,
            nbt_converted=conversion.converted.nbt_1182 is not None,
            removed=conversion.converted.removed,
            errors=conversion.converted.errors,
            warnings=conversion.converted.warnings
        )

    def verify_structure(self, structure_data: Dict[str, Any]) -> StructureVerificationResult:
        """Weryfikuje konwersję całej struktury"""
        name = structure_data["name"]
        struct_type = structure_data["type"]
        blocks = structure_data.get("blocks", [])
        multiparts = structure_data.get("multiparts", [])

        result = StructureVerificationResult(
            structure_name=name,
            structure_type=struct_type,
            total_blocks=len(blocks),
            total_multiparts=len(multiparts),
            converted_successfully=0,
            converted_with_warnings=0,
            failed=0,
            removed=0
        )

        # Weryfikuj bloki
        for block in blocks:
            block_result = self.verify_block(block)
            result.block_results.append(block_result)

            if block_result.removed:
                result.removed += 1
            elif block_result.success:
                if block_result.warnings:
                    result.converted_with_warnings += 1
                else:
                    result.converted_successfully += 1
            else:
                result.failed += 1

        # Weryfikuj multipart
        for mp in multiparts:
            mp_result = self.verify_multipart(mp)
            result.block_results.append(mp_result)

            if mp_result.removed:
                result.removed += 1
            elif mp_result.success:
                if mp_result.warnings:
                    result.converted_with_warnings += 1
                else:
                    result.converted_successfully += 1
            else:
                result.failed += 1

        return result

    def verify_directory(self, dir_path: str, pattern: str = None) -> List[StructureVerificationResult]:
        """Weryfikuje wszystkie struktury w katalogu"""
        results = []

        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if not file.endswith('.json') or file == 'index.json':
                    continue

                if pattern and pattern not in file:
                    continue

                json_path = os.path.join(root, file)
                structure_data = self.load_structure(json_path)
                result = self.verify_structure(structure_data)
                results.append(result)

                if self.verbose:
                    self._print_result(result)

        self.results = results
        return results

    def _print_result(self, result: StructureVerificationResult):
        """Wypisuje wynik weryfikacji"""
        total = result.total_blocks + result.total_multiparts
        status = "OK" if result.failed == 0 else "FAIL"
        print(f"[{status}] {result.structure_name}: {result.converted_successfully}/{total} "
              f"(warnings: {result.converted_with_warnings}, removed: {result.removed}, failed: {result.failed})")

        if self.verbose and result.failed > 0:
            for br in result.block_results:
                if not br.success and not br.removed:
                    print(f"      FAILED: {br.original_id} at {br.position}")
                    for err in br.errors:
                        print(f"        - {err}")

    def generate_report(self, output_path: str = None) -> Dict[str, Any]:
        """Generuje raport weryfikacji"""
        total_structures = len(self.results)
        total_elements = sum(r.total_blocks + r.total_multiparts for r in self.results)
        total_success = sum(r.converted_successfully for r in self.results)
        total_warnings = sum(r.converted_with_warnings for r in self.results)
        total_failed = sum(r.failed for r in self.results)
        total_removed = sum(r.removed for r in self.results)

        structures_passed = len([r for r in self.results if r.failed == 0])

        report = {
            "summary": {
                "total_structures": total_structures,
                "structures_passed": structures_passed,
                "structures_failed": total_structures - structures_passed,
                "total_elements": total_elements,
                "converted_successfully": total_success,
                "converted_with_warnings": total_warnings,
                "failed": total_failed,
                "removed": total_removed,
                "success_rate": f"{(total_success / total_elements * 100) if total_elements > 0 else 0:.1f}%"
            },
            "unit_tests": {
                "count": len([r for r in self.results if r.structure_type == "unit"]),
                "passed": len([r for r in self.results if r.structure_type == "unit" and r.failed == 0])
            },
            "integration_tests": {
                "count": len([r for r in self.results if r.structure_type == "integration"]),
                "passed": len([r for r in self.results if r.structure_type == "integration" and r.failed == 0])
            },
            "failed_structures": [
                r.to_dict() for r in self.results if r.failed > 0
            ],
            "all_results": [r.to_dict() for r in self.results]
        }

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\nReport saved to: {output_path}")

        return report

    def print_summary(self):
        """Wypisuje podsumowanie weryfikacji"""
        total_structures = len(self.results)
        total_elements = sum(r.total_blocks + r.total_multiparts for r in self.results)
        total_success = sum(r.converted_successfully for r in self.results)
        total_warnings = sum(r.converted_with_warnings for r in self.results)
        total_failed = sum(r.failed for r in self.results)
        total_removed = sum(r.removed for r in self.results)

        structures_passed = len([r for r in self.results if r.failed == 0])

        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)
        print(f"\nStructures: {structures_passed}/{total_structures} passed")
        print(f"Elements:   {total_success}/{total_elements} converted successfully")
        print(f"            {total_warnings} with warnings")
        print(f"            {total_removed} removed (expected)")
        print(f"            {total_failed} FAILED")

        unit_tests = [r for r in self.results if r.structure_type == "unit"]
        integration_tests = [r for r in self.results if r.structure_type == "integration"]

        print(f"\nUnit tests:        {len([r for r in unit_tests if r.failed == 0])}/{len(unit_tests)}")
        print(f"Integration tests: {len([r for r in integration_tests if r.failed == 0])}/{len(integration_tests)}")

        if total_failed > 0:
            print("\nFAILED STRUCTURES:")
            for r in self.results:
                if r.failed > 0:
                    print(f"  - {r.structure_name}: {r.failed} elements failed")

        success_rate = (total_success / total_elements * 100) if total_elements > 0 else 0
        print(f"\nOverall success rate: {success_rate:.1f}%")

        if total_failed == 0:
            print("\n ALL TESTS PASSED!")
        else:
            print(f"\n SOME TESTS FAILED ({total_failed} elements)")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Verify ProjectRed test structure conversions")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--filter", "-f", type=str, help="Filter structures by name pattern")
    parser.add_argument("--output", "-o", type=str, help="Output report JSON path")
    args = parser.parse_args()

    # Znajdź katalog z wygenerowanymi strukturami
    script_dir = os.path.dirname(os.path.abspath(__file__))
    generated_dir = os.path.join(script_dir, "generated")

    if not os.path.exists(generated_dir):
        print(f"ERROR: Generated directory not found: {generated_dir}")
        print("Run structure_generator.py first to create test structures.")
        sys.exit(1)

    print("=" * 60)
    print("PROJECTRED CONVERSION VERIFIER")
    print("=" * 60)
    print(f"\nSource: {generated_dir}")
    print(f"Filter: {args.filter or 'None'}")
    print(f"Verbose: {args.verbose}")
    print()

    verifier = ConversionVerifier(verbose=args.verbose)
    verifier.verify_directory(generated_dir, pattern=args.filter)
    verifier.print_summary()

    # Zapisz raport
    if args.output:
        report_path = args.output
    else:
        report_path = os.path.join(script_dir, "verification_report.json")

    verifier.generate_report(report_path)


if __name__ == "__main__":
    main()
