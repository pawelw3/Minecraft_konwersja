"""
Patch Generator for ProjectRed Test Structures

Converts JSON structure definitions to Kotlin worker patch format.
Handles both regular blocks and CB Multipart (ForgeMultipart) elements.

Multipart blocks in 1.7.10:
- Block: forge_microblock (id from config, typically 177 or similar)
- TileEntity: "savedMultipart" with "parts" list
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class PatchConfig:
    """Configuration for patch generation"""
    # Block IDs (1.7.10 numeric IDs)
    block_ids: Dict[str, int] = field(default_factory=lambda: {
        # Vanilla
        "minecraft:stone": 1,
        "minecraft:redstone_wire": 55,
        "minecraft:lever": 69,
        "minecraft:stone_button": 77,
        "minecraft:command_block": 137,
        "minecraft:unpowered_repeater": 93,
        "minecraft:powered_repeater": 94,

        # ForgeMultipart (needs config check)
        "forge_microblock": 177,  # Default, may vary
    })

    # ProjectRed block IDs (1.7.10)
    projectred_ids: Dict[str, int] = field(default_factory=lambda: {
        # Core
        "ProjRed|Core:projectred.core.machine": 450,

        # Expansion
        "ProjRed|Expansion:projectred.expansion.machine1": 451,
        "ProjRed|Expansion:projectred.expansion.machine2": 452,

        # Illumination
        "ProjRed|Illumination:projectred.illumination.lamp": 461,
        "ProjRed|Illumination:projectred.illumination.lamp_inverted": 462,

        # Exploration
        "ProjRed|Exploration:projectred.exploration.ore": 470,
        "ProjRed|Exploration:projectred.exploration.stone": 471,

        # Fabrication
        "ProjRed|Fabrication:projectred.fabrication.icblock": 480,
    })

    # Multipart type to part NBT mapping
    multipart_types: Dict[str, dict] = field(default_factory=lambda: {
        "pr_sgate": {"type": "pr_sgate"},  # Simple gates
        "pr_igate": {"type": "pr_igate"},  # Complex gates (timer, counter)
        "pr_redwire": {"type": "pr_redwire"},  # Red alloy wire
        "pr_insulated": {"type": "pr_insulated"},  # Insulated wire
        "pr_bundled": {"type": "pr_bundled"},  # Bundled cable
    })


class PatchGenerator:
    """
    Generator for Kotlin worker patches from JSON structures.

    Structure JSON format (from structure_generator.py):
    {
        "name": "...",
        "type": "unit|integration",
        "blocks": [{"pos": [x,y,z], "block_id": "...", "metadata": 0, "nbt": {...}}],
        "multiparts": [{"pos": [x,y,z], "part_type": "pr_sgate", "nbt": {...}}]
    }

    Output patch format:
    {
        "metadata": {...},
        "edits": [
            {"op": "set_block", "x": ..., "y": ..., "z": ..., "id": ..., "meta": ...},
            {"op": "set_te", "x": ..., "y": ..., "z": ..., "nbt": {...}}
        ]
    }
    """

    def __init__(self, config: Optional[PatchConfig] = None):
        self.config = config or PatchConfig()

    def get_block_id(self, block_name: str) -> int:
        """Get numeric block ID from name"""
        if block_name in self.config.block_ids:
            return self.config.block_ids[block_name]
        if block_name in self.config.projectred_ids:
            return self.config.projectred_ids[block_name]
        raise ValueError(f"Unknown block: {block_name}")

    def _block_to_edit(
            self,
            block: Dict[str, Any],
            offset: Tuple[int, int, int]
    ) -> List[Dict[str, Any]]:
        """Convert block definition to edit(s)"""
        edits = []
        pos = block["pos"]
        x = pos[0] + offset[0]
        y = pos[1] + offset[1]
        z = pos[2] + offset[2]

        block_id = self.get_block_id(block["block_id"])
        meta = block.get("metadata", 0)

        # Block edit
        edits.append({
            "op": "set_block",
            "x": x, "y": y, "z": z,
            "id": block_id,
            "meta": meta
        })

        # Tile Entity if present
        if "nbt" in block and block["nbt"]:
            te_nbt = dict(block["nbt"])
            # Add required TE fields
            te_nbt["x"] = x
            te_nbt["y"] = y
            te_nbt["z"] = z

            # Set TE id based on block type
            if block["block_id"] == "minecraft:command_block":
                te_nbt.setdefault("id", "Control")
            elif "ProjRed|Expansion" in block["block_id"]:
                te_nbt.setdefault("id", "projectred_core_machine")
            elif "ProjRed|Fabrication" in block["block_id"]:
                te_nbt.setdefault("id", "pr_icworkbench")

            edits.append({
                "op": "set_te",
                "x": x, "y": y, "z": z,
                "nbt": te_nbt
            })

        return edits

    def _multipart_to_edit(
            self,
            multipart: Dict[str, Any],
            offset: Tuple[int, int, int]
    ) -> List[Dict[str, Any]]:
        """
        Convert multipart definition to edit(s).

        Multipart blocks use ForgeMultipart:
        - Block: forge_microblock
        - TE: savedMultipart with parts list
        """
        edits = []
        pos = multipart["pos"]
        x = pos[0] + offset[0]
        y = pos[1] + offset[1]
        z = pos[2] + offset[2]

        # Place forge_microblock
        edits.append({
            "op": "set_block",
            "x": x, "y": y, "z": z,
            "id": self.config.block_ids["forge_microblock"],
            "meta": 0
        })

        # Create savedMultipart TE
        part_nbt = dict(multipart["nbt"])
        part_nbt["id"] = multipart["part_type"]

        te_nbt = {
            "id": "savedMultipart",
            "x": x, "y": y, "z": z,
            "parts": [part_nbt]
        }

        edits.append({
            "op": "set_te",
            "x": x, "y": y, "z": z,
            "nbt": te_nbt
        })

        return edits

    def generate_patch(
            self,
            structure: Dict[str, Any],
            offset: Tuple[int, int, int] = (0, 0, 0),
            name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate patch from structure definition.

        Args:
            structure: Structure JSON dictionary
            offset: Global position offset (x, y, z)
            name: Override structure name

        Returns:
            Patch dictionary for Kotlin worker
        """
        edits = []

        # Process blocks
        for block in structure.get("blocks", []):
            edits.extend(self._block_to_edit(block, offset))

        # Process multiparts
        for multipart in structure.get("multiparts", []):
            edits.extend(self._multipart_to_edit(multipart, offset))

        # Build metadata
        size = structure.get("size", [1, 1, 1])
        metadata = {
            "name": name or structure.get("name", "unnamed"),
            "version": "1.7.10",
            "generated_by": "projectred_patch_generator",
            "structure_type": structure.get("type", "unknown"),
            "offset": {"x": offset[0], "y": offset[1], "z": offset[2]},
            "size": {"x": size[0], "y": size[1], "z": size[2]},
            "total_edits": len(edits)
        }

        # Add test info for integration tests
        if structure.get("type") == "integration":
            test_info = structure.get("test_info", {})
            metadata["test_info"] = {
                "expected_output": test_info.get("expected_output", ""),
                "input_description": test_info.get("input_description", ""),
            }

            # Calculate power source position for RCON activation
            # First lever/button in the structure
            for block in structure.get("blocks", []):
                if "lever" in block["block_id"] or "button" in block["block_id"]:
                    pos = block["pos"]
                    metadata["activation_point"] = {
                        "x": pos[0] + offset[0],
                        "y": pos[1] + offset[1],
                        "z": pos[2] + offset[2],
                        "block_type": block["block_id"]
                    }
                    break

        return {
            "metadata": metadata,
            "edits": edits
        }

    def generate_test_world_patch(
            self,
            structures: List[Dict[str, Any]],
            start_offset: Tuple[int, int, int] = (600, 70, -100),
            spacing: int = 20
    ) -> Dict[str, Any]:
        """
        Generate patch for all structures in a test world.

        Structures are placed in a row with given spacing.

        Args:
            structures: List of structure definitions
            start_offset: Starting position
            spacing: Distance between structures (X axis)

        Returns:
            Combined patch dictionary
        """
        all_edits = []
        structure_map = []

        current_x = start_offset[0]

        for i, structure in enumerate(structures):
            offset = (current_x, start_offset[1], start_offset[2])
            patch = self.generate_patch(structure, offset)

            all_edits.extend(patch["edits"])
            structure_map.append({
                "index": i,
                "name": structure.get("name", f"structure_{i}"),
                "type": structure.get("type", "unknown"),
                "offset": {"x": offset[0], "y": offset[1], "z": offset[2]},
                "metadata": patch["metadata"]
            })

            # Move to next position
            size = structure.get("size", [1, 1, 1])
            current_x += max(size[0], 1) + spacing

        return {
            "metadata": {
                "name": "ProjectRed Test World",
                "version": "1.7.10",
                "generated_by": "projectred_patch_generator",
                "total_structures": len(structures),
                "total_edits": len(all_edits),
                "start_offset": {"x": start_offset[0], "y": start_offset[1], "z": start_offset[2]},
                "spacing": spacing,
                "structures": structure_map
            },
            "edits": all_edits
        }


def load_structures_from_dir(dir_path: str) -> List[Dict[str, Any]]:
    """Load all structure JSON files from directory"""
    structures = []
    dir_path = Path(dir_path)

    for json_file in sorted(dir_path.rglob("*.json")):
        if json_file.name == "index.json":
            continue
        if json_file.name == "verification_report.json":
            continue

        with open(json_file, 'r', encoding='utf-8') as f:
            structure = json.load(f)
            structures.append(structure)

    return structures


def generate_projectred_test_patch(
        structures_dir: str,
        output_path: str,
        start_offset: Tuple[int, int, int] = (600, 70, -100),
        spacing: int = 15
):
    """
    Generate complete test world patch from structure directory.

    Args:
        structures_dir: Path to generated structures directory
        output_path: Output patch JSON file path
        start_offset: Starting world coordinates
        spacing: Space between structures
    """
    structures = load_structures_from_dir(structures_dir)
    print(f"Loaded {len(structures)} structures")

    # Separate unit and integration tests
    unit_tests = [s for s in structures if s.get("type") == "unit"]
    integration_tests = [s for s in structures if s.get("type") == "integration"]

    print(f"  Unit tests: {len(unit_tests)}")
    print(f"  Integration tests: {len(integration_tests)}")

    # Generate patch with integration tests first (they need RCON activation)
    all_structures = integration_tests + unit_tests

    generator = PatchGenerator()
    patch = generator.generate_test_world_patch(
        all_structures,
        start_offset=start_offset,
        spacing=spacing
    )

    # Save patch
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(patch, f, indent=2, ensure_ascii=False)

    print(f"\nPatch saved to: {output_path}")
    print(f"Total edits: {len(patch['edits'])}")

    # Print activation points for integration tests
    print("\nIntegration test activation points (for RCON):")
    for struct in patch["metadata"]["structures"]:
        if struct["type"] == "integration":
            meta = struct.get("metadata", {})
            act = meta.get("activation_point", {})
            if act:
                print(f"  {struct['name']}: {act['x']}, {act['y']}, {act['z']}")

    return patch


def main():
    """Generate patch from ProjectRed test structures"""
    base_dir = Path(__file__).parent.parent
    structures_dir = base_dir / "generated"
    output_path = base_dir / "headless_test" / "projectred_test_patch.json"

    os.makedirs(output_path.parent, exist_ok=True)

    generate_projectred_test_patch(
        str(structures_dir),
        str(output_path),
        start_offset=(600, 70, -100),
        spacing=15
    )


if __name__ == "__main__":
    main()
