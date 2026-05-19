"""AE2 step 2 contract simulations.

These simulations are intentionally small and deterministic. They model the
conversion contracts that must hold before AE2 block entities from 1.7.10 can
be trusted in an AE2 11.7.6/MC 1.18.2 world.
"""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
STEP1_JSON = ROOT / "src" / "converters" / "ae2" / "AE2_STEP1_REANALYSIS.json"
OUT_JSON = ROOT / "src" / "converters" / "ae2" / "AE2_STEP2_SIMULATION_RESULTS.json"
OUT_MD = ROOT / "src" / "converters" / "ae2" / "AE2_STEP2_SIMULATIONS.md"


SOURCE_EVIDENCE = {
    "crafting_storage_1710": (
        "BlockCraftingStorage.java uses metadata & (~4): 0=1k, 1=4k, "
        "2=16k, 3=64k, and bit 4 is FLAG_FORMED."
    ),
    "crafting_storage_1182": (
        "AE2 11.7.6 JAR assets expose 1k_crafting_storage, "
        "4k_crafting_storage, 16k_crafting_storage, 64k_crafting_storage, "
        "256k_crafting_storage."
    ),
    "interface_1710": (
        "DualityInterface has separate config, storage and patterns inventories; "
        "NUMBER_OF_PATTERN_SLOTS is 9."
    ),
    "cable_bus_1710": (
        "BlockCableBus stores multipart cable/part data in the TileCableBus host; "
        "the converter must preserve known part classes and flag unknown ones."
    ),
}


TARGET_BLOCKS_1182 = {
    "minecraft:grindstone",
    "minecraft:lever",
    "ae2:fluix_block",
    "ae2:controller",
    "ae2:drive",
    "ae2:chest",
    "ae2:interface",
    "ae2:pattern_provider",
    "ae2:io_port",
    "ae2:condenser",
    "ae2:energy_acceptor",
    "ae2:energy_cell",
    "ae2:dense_energy_cell",
    "ae2:creative_energy_cell",
    "ae2:crafting_unit",
    "ae2:crafting_accelerator",
    "ae2:1k_crafting_storage",
    "ae2:4k_crafting_storage",
    "ae2:16k_crafting_storage",
    "ae2:64k_crafting_storage",
    "ae2:256k_crafting_storage",
    "ae2:crafting_monitor",
    "ae2:molecular_assembler",
    "ae2:quantum_ring",
    "ae2:quantum_link",
    "ae2:spatial_pylon",
    "ae2:spatial_io_port",
    "ae2:charger",
    "ae2:inscriber",
    "ae2:vibration_chamber",
    "ae2:quartz_growth_accelerator",
    "ae2:wireless_access_point",
    "ae2:security_station",
    "ae2:sky_stone_chest",
    "ae2:smooth_sky_stone_chest",
}


RAW_NBT_ID_TO_PREFixed = {
    "BlockCableBus": "appliedenergistics2:tile.BlockCableBus",
    "BlockCraftingUnit": "appliedenergistics2:tile.BlockCraftingUnit",
    "BlockCraftingStorage": "appliedenergistics2:tile.BlockCraftingStorage",
    "BlockSkyChest": "appliedenergistics2:tile.BlockSkyChest",
    "BlockMolecularAssembler": "appliedenergistics2:tile.BlockMolecularAssembler",
    "BlockController": "appliedenergistics2:tile.BlockController",
    "BlockDenseEnergyCell": "appliedenergistics2:tile.BlockDenseEnergyCell",
    "BlockDrive": "appliedenergistics2:tile.BlockDrive",
    "BlockInterface": "appliedenergistics2:tile.BlockInterface",
    "BlockSpatialPylon": "appliedenergistics2:tile.BlockSpatialPylon",
    "BlockQuantumLinkChamber": "appliedenergistics2:tile.BlockQuantumLinkChamber",
    "BlockEnergyCell": "appliedenergistics2:tile.BlockEnergyCell",
    "BlockEnergyAcceptor": "appliedenergistics2:tile.BlockEnergyAcceptor",
    "BlockInscriber": "appliedenergistics2:tile.BlockInscriber",
    "BlockQuartzGrowthAccelerator": "appliedenergistics2:tile.BlockQuartzGrowthAccelerator",
    "BlockIOPort": "appliedenergistics2:tile.BlockIOPort",
    "BlockSecurity": "appliedenergistics2:tile.BlockSecurity",
    "BlockCrank": "appliedenergistics2:tile.BlockCrank",
    "BlockGrinder": "appliedenergistics2:tile.BlockGrinder",
    "BlockCharger": "appliedenergistics2:tile.BlockCharger",
    "BlockCraftingMonitor": "appliedenergistics2:tile.BlockCraftingMonitor",
    "BlockChest": "appliedenergistics2:tile.BlockChest",
    "BlockCondenser": "appliedenergistics2:tile.BlockCondenser",
    "BlockSpatialIOPort": "appliedenergistics2:tile.BlockSpatialIOPort",
    "BlockVibrationChamber": "appliedenergistics2:tile.BlockVibrationChamber",
    "BlockWireless": "appliedenergistics2:tile.BlockWireless",
    "BlockQuartzTorch": "appliedenergistics2:tile.BlockQuartzTorch",
}


BASE_TARGETS = {
    "appliedenergistics2:tile.BlockCableBus": "ae2:fluix_block",
    "appliedenergistics2:tile.BlockCraftingUnit": "ae2:crafting_unit",
    "appliedenergistics2:tile.BlockCraftingStorage": "ae2:1k_crafting_storage",
    "appliedenergistics2:tile.BlockSkyChest": "ae2:sky_stone_chest",
    "appliedenergistics2:tile.BlockMolecularAssembler": "ae2:molecular_assembler",
    "appliedenergistics2:tile.BlockController": "ae2:controller",
    "appliedenergistics2:tile.BlockDenseEnergyCell": "ae2:dense_energy_cell",
    "appliedenergistics2:tile.BlockDrive": "ae2:drive",
    "appliedenergistics2:tile.BlockInterface": "ae2:interface",
    "appliedenergistics2:tile.BlockSpatialPylon": "ae2:spatial_pylon",
    "appliedenergistics2:tile.BlockQuantumLinkChamber": "ae2:quantum_link",
    "appliedenergistics2:tile.BlockEnergyCell": "ae2:energy_cell",
    "appliedenergistics2:tile.BlockEnergyAcceptor": "ae2:energy_acceptor",
    "appliedenergistics2:tile.BlockInscriber": "ae2:inscriber",
    "appliedenergistics2:tile.BlockQuartzGrowthAccelerator": "ae2:quartz_growth_accelerator",
    "appliedenergistics2:tile.BlockIOPort": "ae2:io_port",
    "appliedenergistics2:tile.BlockSecurity": "ae2:security_station",
    "appliedenergistics2:tile.BlockCrank": "minecraft:lever",
    "appliedenergistics2:tile.BlockGrinder": "minecraft:grindstone",
    "appliedenergistics2:tile.BlockCharger": "ae2:charger",
    "appliedenergistics2:tile.BlockCraftingMonitor": "ae2:crafting_monitor",
    "appliedenergistics2:tile.BlockChest": "ae2:chest",
    "appliedenergistics2:tile.BlockCondenser": "ae2:condenser",
    "appliedenergistics2:tile.BlockSpatialIOPort": "ae2:spatial_io_port",
    "appliedenergistics2:tile.BlockVibrationChamber": "ae2:vibration_chamber",
    "appliedenergistics2:tile.BlockWireless": "ae2:wireless_access_point",
}


CRAFTING_STORAGE_VARIANTS = {
    0: "ae2:1k_crafting_storage",
    1: "ae2:4k_crafting_storage",
    2: "ae2:16k_crafting_storage",
    3: "ae2:64k_crafting_storage",
}


CRAFTING_UNIT_VARIANTS = {
    0: "ae2:crafting_unit",
    1: "ae2:crafting_accelerator",
}


PART_TYPE_MAPPING = {
    "appeng.parts.networking.PartCable": "cable",
    "appeng.parts.networking.PartDenseCable": "dense_cable",
    "appeng.parts.networking.PartQuartzFiber": "quartz_fiber",
    "appeng.parts.reporting.PartTerminal": "crafting_terminal",
    "appeng.parts.reporting.PartPatternTerminal": "pattern_encoding_terminal",
    "appeng.parts.reporting.PartPatternTerminalEx": "pattern_encoding_terminal",
    "appeng.parts.reporting.PartInterfaceTerminal": "interface_terminal",
    "appeng.parts.reporting.PartStorageMonitor": "storage_monitor",
    "appeng.parts.reporting.PartConversionMonitor": "conversion_monitor",
    "appeng.parts.reporting.PartPanel": "panel",
    "appeng.parts.reporting.PartSemiDarkPanel": "semi_dark_monitor",
    "appeng.parts.reporting.PartDarkPanel": "dark_monitor",
    "appeng.parts.automation.PartImportBus": "import_bus",
    "appeng.parts.automation.PartExportBus": "export_bus",
    "appeng.parts.automation.PartStorageBus": "storage_bus",
    "appeng.parts.p2p.PartP2PTunnel": "p2p_tunnel",
    "appeng.parts.p2p.PartP2PTunnelLight": "p2p_tunnel_light",
    "appeng.parts.p2p.PartP2PTunnelRedstone": "p2p_tunnel_redstone",
    "appeng.parts.p2p.PartP2PTunnelItem": "p2p_tunnel_item",
    "appeng.parts.p2p.PartP2PTunnelFluid": "p2p_tunnel_fluid",
    "appeng.parts.p2p.PartP2PTunnelFE": "p2p_tunnel_fe",
    "appeng.parts.p2p.PartP2PTunnelME": "p2p_tunnel_me",
    "appeng.parts.misc.PartCableAnchor": "cable_anchor",
    "appeng.parts.misc.PartToggleBus": "toggle_bus",
    "appeng.parts.misc.PartInvertedToggleBus": "inverted_toggle_bus",
}


@dataclass
class SimulationOutcome:
    name: str
    passed: bool
    checks: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)


def normalize_source_id(raw_id: str) -> str | None:
    if raw_id.startswith("appliedenergistics2:tile."):
        return raw_id
    if raw_id.startswith("ae2:"):
        return raw_id
    return RAW_NBT_ID_TO_PREFixed.get(raw_id)


def resolve_target(raw_id: str, metadata: int = 0) -> str | None:
    normalized = normalize_source_id(raw_id)
    if normalized == "appliedenergistics2:tile.BlockCraftingStorage":
        return CRAFTING_STORAGE_VARIANTS.get(metadata & 3)
    if normalized == "appliedenergistics2:tile.BlockCraftingUnit":
        return CRAFTING_UNIT_VARIANTS.get(metadata & 1)
    return BASE_TARGETS.get(normalized or "")


def simulate_id_and_target_resolution(step1: dict[str, Any]) -> SimulationOutcome:
    checks: list[str] = []
    warnings: list[str] = []
    unresolved: list[str] = []
    invalid_targets: list[dict[str, Any]] = []

    for row in step1["map_tile_entities"]:
        nbt_id = row["nbt_id"]
        if nbt_id == "TileChestHungry":
            warnings.append("TileChestHungry is treated as non-core AE2/addon data.")
            continue
        if nbt_id in {"BlockCrank", "BlockGrinder"}:
            warnings.append(
                f"{nbt_id} uses a lossy fallback because AE2 11.7.6 JAR has no AE2 target block."
            )
        normalized = normalize_source_id(nbt_id)
        target = resolve_target(nbt_id)
        if not normalized:
            unresolved.append(nbt_id)
            continue
        checks.append(f"{nbt_id} -> {normalized}")
        if target not in TARGET_BLOCKS_1182:
            invalid_targets.append({"nbt_id": nbt_id, "target": target})

    return SimulationOutcome(
        name="id_and_target_resolution",
        passed=not unresolved and not invalid_targets,
        checks=checks,
        warnings=warnings,
        data={"unresolved": unresolved, "invalid_targets": invalid_targets},
    )


def simulate_crafting_variants() -> SimulationOutcome:
    checks = []
    invalid = []

    for metadata in range(8):
        size = metadata & 3
        formed = bool(metadata & 4)
        target = resolve_target("BlockCraftingStorage", metadata)
        expected = CRAFTING_STORAGE_VARIANTS[size]
        checks.append(f"storage meta {metadata}: size={size}, formed={formed} -> {target}")
        if target != expected or target not in TARGET_BLOCKS_1182:
            invalid.append({"metadata": metadata, "target": target, "expected": expected})

    for metadata in range(4):
        target = resolve_target("BlockCraftingUnit", metadata)
        expected = CRAFTING_UNIT_VARIANTS[metadata & 1]
        checks.append(f"unit meta {metadata}: accelerator={bool(metadata & 1)} -> {target}")
        if target != expected or target not in TARGET_BLOCKS_1182:
            invalid.append({"metadata": metadata, "target": target, "expected": expected})

    return SimulationOutcome(
        name="crafting_storage_and_unit_variants",
        passed=not invalid,
        checks=checks,
        data={"invalid": invalid, "evidence": SOURCE_EVIDENCE["crafting_storage_1710"]},
    )


def simulate_interface_split() -> SimulationOutcome:
    source_interface = {
        "id": "BlockInterface",
        "priority": 25,
        "config": [{"slot": 0, "item": "minecraft:iron_ingot"}],
        "storage": [{"slot": 3, "item": "minecraft:chest", "count": 16}],
        "patterns": [
            {"slot": 0, "item": "appliedenergistics2:item.ItemEncodedPattern", "recipe": "iron_to_chest"},
            {"slot": 1, "item": "appliedenergistics2:item.ItemEncodedPattern", "recipe": "glass_to_quartz_fiber"},
        ],
    }

    converted_interface = {
        "block": "ae2:interface",
        "priority": source_interface["priority"],
        "config": source_interface["config"],
        "storage": source_interface["storage"],
        "patterns": [],
    }
    pattern_provider = {
        "block": "ae2:pattern_provider",
        "patterns": source_interface["patterns"],
        "derived_from": "BlockInterface",
    }

    passed = (
        converted_interface["block"] in TARGET_BLOCKS_1182
        and pattern_provider["block"] in TARGET_BLOCKS_1182
        and len(pattern_provider["patterns"]) == len(source_interface["patterns"])
        and not converted_interface["patterns"]
    )

    return SimulationOutcome(
        name="interface_to_interface_plus_pattern_provider",
        passed=passed,
        checks=[
            "1.7.10 interface keeps config/storage/pattern inventories separately.",
            "1.18.2 conversion keeps storage/config in Interface.",
            "Encoded patterns move into adjacent Pattern Provider.",
        ],
        data={
            "source": source_interface,
            "converted_interface": converted_interface,
            "pattern_provider": pattern_provider,
            "evidence": SOURCE_EVIDENCE["interface_1710"],
        },
    )


def simulate_cable_bus_parts() -> SimulationOutcome:
    source = {
        "def:0": {"class": "appeng.parts.networking.PartDenseCable", "color": "blue"},
        "def:1": {"class": "appeng.parts.reporting.PartTerminal"},
        "def:2": {"class": "appeng.parts.automation.PartImportBus"},
        "def:3": {"class": "appeng.parts.p2p.PartP2PTunnelME"},
        "def:4": {"class": "appeng.parts.automation.PartStorageBus", "priority": 10},
        "def:5": {"class": "unknown.ModPart"},
    }
    converted = []
    warnings = []

    for key, definition in source.items():
        part_class = definition["class"]
        part_type = PART_TYPE_MAPPING.get(part_class)
        if not part_type:
            warnings.append(f"Unknown part class {part_class} in {key}")
            continue
        converted.append({"slot": key.split(":", 1)[1], "type": part_type})

    expected_types = {"dense_cable", "crafting_terminal", "import_bus", "p2p_tunnel_me", "storage_bus"}
    got_types = {part["type"] for part in converted}
    passed = expected_types == got_types and len(warnings) == 1

    return SimulationOutcome(
        name="cable_bus_part_mapping",
        passed=passed,
        checks=[f"{item['slot']} -> {item['type']}" for item in converted],
        warnings=warnings,
        data={"converted": converted, "evidence": SOURCE_EVIDENCE["cable_bus_1710"]},
    )


def simulate_sky_chest_inventory() -> SimulationOutcome:
    source_nbt = {
        "id": "BlockSkyChest",
        "inventory": [
            {"Slot": 0, "id": "minecraft:certus_quartz", "Count": 32},
            {"Slot": 12, "id": "minecraft:diamond", "Count": 3},
        ],
        "sky_type_metadata": 0,
    }
    target = resolve_target(source_nbt["id"])
    converted = {
        "block": target,
        "items": source_nbt["inventory"],
    }
    passed = target in TARGET_BLOCKS_1182 and converted["items"] == source_nbt["inventory"]
    return SimulationOutcome(
        name="sky_chest_inventory_preservation",
        passed=passed,
        checks=[
            f"{source_nbt['id']} -> {target}",
            f"preserved item stacks: {len(converted['items'])}",
        ],
        data={"source": source_nbt, "converted": converted},
    )


@dataclass
class NetworkNode:
    name: str
    kind: str
    dense: bool = False
    neighbors: list[str] = field(default_factory=list)

    @property
    def channel_capacity(self) -> int:
        if self.kind == "controller":
            return 32
        if self.kind == "cable":
            return 32 if self.dense else 8
        return 1


def simulate_me_network_channels() -> SimulationOutcome:
    nodes = {
        "controller": NetworkNode("controller", "controller", neighbors=["dense_a"]),
        "dense_a": NetworkNode("dense_a", "cable", dense=True, neighbors=["controller", "dense_b"]),
        "dense_b": NetworkNode("dense_b", "cable", dense=True, neighbors=["dense_a", "branch_a", "branch_b"]),
        "branch_a": NetworkNode("branch_a", "cable", neighbors=["dense_b", "drive", "interface"]),
        "branch_b": NetworkNode("branch_b", "cable", neighbors=["dense_b", "assembler", "terminal"]),
        "drive": NetworkNode("drive", "device", neighbors=["branch_a"]),
        "interface": NetworkNode("interface", "device", neighbors=["branch_a"]),
        "assembler": NetworkNode("assembler", "device", neighbors=["branch_b"]),
        "terminal": NetworkNode("terminal", "device", neighbors=["branch_b"]),
    }
    used = {name: 0 for name in nodes}
    seen = {"controller"}
    queue = deque(["controller"])
    devices = []

    while queue:
        current = queue.popleft()
        for nxt in nodes[current].neighbors:
            if nxt in seen:
                continue
            seen.add(nxt)
            queue.append(nxt)
            if nodes[nxt].kind == "device":
                devices.append(nxt)
                used[current] += 1
            elif nodes[nxt].kind == "cable":
                used[nxt] += used[current]

    overloaded = [
        {"node": name, "used": count, "capacity": node.channel_capacity}
        for name, node in nodes.items()
        for count in [used[name]]
        if count > node.channel_capacity
    ]
    return SimulationOutcome(
        name="me_network_channel_budget",
        passed=not overloaded and len(devices) == 4,
        checks=[
            "normal cable capacity: 8 channels",
            "dense cable/controller capacity: 32 channels",
            f"devices reached: {', '.join(sorted(devices))}",
        ],
        data={"used_channels": used, "overloaded": overloaded},
    )


def run_all() -> dict[str, Any]:
    step1 = json.loads(STEP1_JSON.read_text(encoding="utf-8"))
    outcomes = [
        simulate_id_and_target_resolution(step1),
        simulate_crafting_variants(),
        simulate_interface_split(),
        simulate_cable_bus_parts(),
        simulate_sky_chest_inventory(),
        simulate_me_network_channels(),
    ]
    return {
        "status": "pass" if all(outcome.passed for outcome in outcomes) else "fail",
        "passed": sum(1 for outcome in outcomes if outcome.passed),
        "total": len(outcomes),
        "outcomes": [outcome.__dict__ for outcome in outcomes],
    }


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# AE2 - Krok 2 wykonany ponownie",
        "",
        "Ten dokument zastepuje stare podejscie do kroku 2 jako kontrakt symulacyjny oparty o reanalize kroku 1.",
        "Symulacje nie probuja udawac calego AE2. Sprawdzaja najwazniejsze reguly, ktore musza byc prawdziwe przed kodem konwersji.",
        "",
        "## Wynik",
        "",
        f"- Status: {result['status'].upper()}",
        f"- Symulacje zaliczone: {result['passed']}/{result['total']}",
        "",
        "## Symulacje",
        "",
        md_table(
            ["Nazwa", "Status", "Ostrzezenia"],
            [
                [
                    outcome["name"],
                    "PASS" if outcome["passed"] else "FAIL",
                    "; ".join(outcome["warnings"]) if outcome["warnings"] else "-",
                ]
                for outcome in result["outcomes"]
            ],
        ),
        "",
        "## Kontrakty dla kroku 3",
        "",
        "1. Surowe NBT ID z mapy (`BlockDrive`, `BlockCableBus`, itd.) musza byc normalizowane do istniejacych kluczy mapowania.",
        "2. `BlockCraftingStorage` musi mapowac metadata `0..3` na `ae2:1k_crafting_storage`, `ae2:4k_crafting_storage`, `ae2:16k_crafting_storage`, `ae2:64k_crafting_storage`; bit `4` jest stanem formed i nie zmienia rozmiaru.",
        "3. `BlockCraftingUnit` metadata `1` musi przejsc na `ae2:crafting_accelerator`, a nie zwykly crafting unit.",
        "4. Interface z patternami musi utworzyc osobny `ae2:pattern_provider` i przeniesc tam encoded patterns.",
        "5. CableBus musi zachowac znane klasy partow i ostrzegac o nieznanych, zamiast cicho je gubic.",
        "6. SkyChest musi zachowac inventory i miec jawnie zarejestrowana obsluge w konwerterze.",
        "",
        "## Szczegoly",
        "",
    ]
    for outcome in result["outcomes"]:
        lines.extend(
            [
                f"### {outcome['name']}",
                "",
                f"Status: {'PASS' if outcome['passed'] else 'FAIL'}",
                "",
            ]
        )
        if outcome["checks"]:
            lines.append("Checks:")
            lines.extend(f"- {check}" for check in outcome["checks"])
            lines.append("")
        if outcome["warnings"]:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in outcome["warnings"])
            lines.append("")
    return "\n".join(lines)


def main() -> None:
    result = run_all()
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    OUT_MD.write_text(render_markdown(result), encoding="utf-8")
    print(json.dumps({"status": result["status"], "passed": result["passed"], "total": result["total"]}, indent=2))
    if result["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
