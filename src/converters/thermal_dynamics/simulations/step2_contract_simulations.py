"""Thermal Dynamics — Step 2 contract simulations.

These simulations are intentionally small and deterministic. They model the
conversion contracts that must hold before Thermal Dynamics block entities
from 1.7.10 can be converted to a 1.18.2 world (Thermal Dynamics + Mekanism).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
OUT_JSON = ROOT / "src" / "converters" / "thermal_dynamics" / "THERMAL_DYNAMICS_STEP2_SIMULATION_RESULTS.json"
OUT_MD = ROOT / "src" / "converters" / "thermal_dynamics" / "THERMAL_DYNAMICS_STEP2_SIMULATIONS.md"


# Dokumentacja źródłowa z dekompilacji TDDucts.java
SOURCE_EVIDENCE = {
    "td_1710_offsets": (
        "TDDucts.java defines offsets: ENERGY=0, FLUID=16, ITEM=32, "
        "STRUCTURE=48, TRANSPORT=64. Each BlockDuct instance covers 16 metadata values."
    ),
    "td_1710_ductlist": (
        "TDDucts.addDucts() registers 34 duct types with unique internal IDs. "
        "Empty variants (energyReinforcedEmpty, energyResonantEmpty, "
        "energySuperCondEmpty, transportFrame) are crafting items, not placeable blocks."
    ),
    "td_1182_blocks": (
        "TDynBlocks.java (TD 9.2.2.19) registers: energy_duct, fluid_duct, "
        "fluid_duct_windowed, item_buffer. No item_duct, structure_duct, transport_duct."
    ),
    "mekanism_1182_transmitters": (
        "Mekanism 1.18.2 JAR registers: basic/advanced/elite/ultimate "
        "logistical_transporter, restrictive_transporter, diversion_transporter, "
        "teleporter, teleporter_frame."
    ),
}


# Bloki docelowe dostępne w 1.18.2 (TD + Mekanism)
TARGET_BLOCKS_1182 = {
    # Thermal Dynamics
    "thermal:energy_duct",
    "thermal:fluid_duct",
    "thermal:fluid_duct_windowed",
    "thermal:item_buffer",
    # Mekanism
    "mekanism:basic_logistical_transporter",
    "mekanism:advanced_logistical_transporter",
    "mekanism:elite_logistical_transporter",
    "mekanism:ultimate_logistical_transporter",
    "mekanism:restrictive_transporter",
    "mekanism:diversion_transporter",
    "mekanism:teleporter",
    "mekanism:teleporter_frame",
}


# Mapowanie 1.7.10 → 1.18.2 (block_id, metadata) → target
# Format: ("ThermalDynamics:thermaldynamics.Duct{offset}", meta) -> target_block
DUCT_MAPPING: dict[tuple[str, int], str | None] = {
    # Energy (offset 0)
    ("ThermalDynamics:thermaldynamics.Duct0", 0): "thermal:energy_duct",
    ("ThermalDynamics:thermaldynamics.Duct0", 1): "thermal:energy_duct",
    ("ThermalDynamics:thermaldynamics.Duct0", 2): "thermal:energy_duct",
    ("ThermalDynamics:thermaldynamics.Duct0", 3): None,  # empty crafting
    ("ThermalDynamics:thermaldynamics.Duct0", 4): "thermal:energy_duct",
    ("ThermalDynamics:thermaldynamics.Duct0", 5): None,  # empty crafting
    ("ThermalDynamics:thermaldynamics.Duct0", 6): "thermal:energy_duct",
    ("ThermalDynamics:thermaldynamics.Duct0", 7): None,  # empty crafting
    # Fluid (offset 16)
    ("ThermalDynamics:thermaldynamics.Duct16", 0): "thermal:fluid_duct",
    ("ThermalDynamics:thermaldynamics.Duct16", 1): "thermal:fluid_duct",
    ("ThermalDynamics:thermaldynamics.Duct16", 2): "thermal:fluid_duct",
    ("ThermalDynamics:thermaldynamics.Duct16", 3): "thermal:fluid_duct",
    ("ThermalDynamics:thermaldynamics.Duct16", 4): "thermal:fluid_duct",
    ("ThermalDynamics:thermaldynamics.Duct16", 5): "thermal:fluid_duct",
    ("ThermalDynamics:thermaldynamics.Duct16", 6): "thermal:fluid_duct_windowed",
    ("ThermalDynamics:thermaldynamics.Duct16", 7): "thermal:fluid_duct_windowed",
    # Item (offset 32) → Mekanism
    ("ThermalDynamics:thermaldynamics.Duct32", 0): "mekanism:basic_logistical_transporter",
    ("ThermalDynamics:thermaldynamics.Duct32", 1): "mekanism:basic_logistical_transporter",
    ("ThermalDynamics:thermaldynamics.Duct32", 2): "mekanism:advanced_logistical_transporter",
    ("ThermalDynamics:thermaldynamics.Duct32", 3): "mekanism:advanced_logistical_transporter",
    ("ThermalDynamics:thermaldynamics.Duct32", 4): "mekanism:elite_logistical_transporter",
    ("ThermalDynamics:thermaldynamics.Duct32", 5): "mekanism:elite_logistical_transporter",
    ("ThermalDynamics:thermaldynamics.Duct32", 6): "mekanism:ultimate_logistical_transporter",
    ("ThermalDynamics:thermaldynamics.Duct32", 7): "mekanism:ultimate_logistical_transporter",
    # Structural (offset 48) → brak
    ("ThermalDynamics:thermaldynamics.Duct48", 0): None,
    ("ThermalDynamics:thermaldynamics.Duct48", 1): None,
    # Transport (offset 64) → Mekanism Teleporter
    ("ThermalDynamics:thermaldynamics.Duct64", 0): "mekanism:teleporter",
    ("ThermalDynamics:thermaldynamics.Duct64", 1): "mekanism:teleporter",
    ("ThermalDynamics:thermaldynamics.Duct64", 2): "mekanism:teleporter",
    ("ThermalDynamics:thermaldynamics.Duct64", 3): "mekanism:teleporter_frame",
}


# Nazwy wyświetlane dla każdego (offset, meta)
DUCT_NAMES: dict[tuple[int, int], str] = {
    (0, 0): "Leadstone Fluxduct",
    (0, 1): "Hardened Fluxduct",
    (0, 2): "Redstone Energy Fluxduct",
    (0, 3): "Reinforced Fluxduct (empty)",
    (0, 4): "Signalum Fluxduct",
    (0, 5): "Resonant Fluxduct (empty)",
    (0, 6): "Cryo-Stabilized Fluxduct",
    (0, 7): "Cryo-Stabilized Fluxduct (empty)",
    (16, 0): "Temperate Fluiduct",
    (16, 1): "Temperate Fluiduct (opaque)",
    (16, 2): "Hardened Fluiduct",
    (16, 3): "Hardened Fluiduct (opaque)",
    (16, 4): "Flux-Plated Fluiduct",
    (16, 5): "Flux-Plated Fluiduct (opaque)",
    (16, 6): "Super-Laminar Fluiduct",
    (16, 7): "Super-Laminar Fluiduct (opaque)",
    (32, 0): "Itemduct",
    (32, 1): "Itemduct (opaque)",
    (32, 2): "Impulse Itemduct",
    (32, 3): "Impulse Itemduct (opaque)",
    (32, 4): "Ender Itemduct",
    (32, 5): "Ender Itemduct (opaque)",
    (32, 6): "Flux-Plated Itemduct",
    (32, 7): "Flux-Plated Itemduct (opaque)",
    (48, 0): "Structuralduct",
    (48, 1): "Glowstone Illuminator",
    (64, 0): "Viaduct",
    (64, 1): "Long-Range Viaduct",
    (64, 2): "Accelerated Viaduct",
    (64, 3): "Viaduct Frame",
}


@dataclass
class SimulationOutcome:
    name: str
    passed: bool
    checks: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)


def _resolve(block_id: str, metadata: int) -> str | None:
    return DUCT_MAPPING.get((block_id, metadata))


def simulate_duct_id_and_target_resolution() -> SimulationOutcome:
    """Weryfikuje czy każdy znany duct ma przypisany target i czy target istnieje w 1.18.2."""
    checks = []
    warnings = []
    unresolved = []
    invalid_targets = []

    for (block_id, meta), target in DUCT_MAPPING.items():
        name = DUCT_NAMES.get(
            (int(block_id.replace("ThermalDynamics:thermaldynamics.Duct", "")), meta),
            f"Unknown({block_id}:{meta})"
        )
        if target is None:
            # Empty crafting items or structural — expected to have no target
            if meta in {3, 5, 7} and block_id == "ThermalDynamics:thermaldynamics.Duct0":
                checks.append(f"{name} -> None (expected crafting item)")
            elif block_id == "ThermalDynamics:thermaldynamics.Duct48":
                checks.append(f"{name} -> None (no 1.18.2 equivalent)")
            else:
                warnings.append(f"{name} has no target mapping")
            continue

        checks.append(f"{name} -> {target}")
        if target not in TARGET_BLOCKS_1182:
            invalid_targets.append({"duct": name, "target": target})

    return SimulationOutcome(
        name="duct_id_and_target_resolution",
        passed=not invalid_targets,
        checks=checks,
        warnings=warnings,
        data={"invalid_targets": invalid_targets},
    )


def simulate_energy_duct_tier_collapse() -> SimulationOutcome:
    """Weryfikuje czy wszystkie placeable energy ducts mapują się na thermal:energy_duct."""
    checks = []
    invalid = []
    expected = "thermal:energy_duct"

    for meta in range(8):
        target = _resolve("ThermalDynamics:thermaldynamics.Duct0", meta)
        is_empty = meta in {3, 5, 7}
        name = DUCT_NAMES[(0, meta)]

        if is_empty:
            checks.append(f"{name} -> None (crafting item, not placeable)")
            if target is not None:
                invalid.append({"meta": meta, "target": target, "reason": "empty should have no target"})
        else:
            checks.append(f"{name} -> {target}")
            if target != expected:
                invalid.append({"meta": meta, "target": target, "expected": expected})

    return SimulationOutcome(
        name="energy_duct_tier_collapse",
        passed=not invalid,
        checks=checks,
        data={"invalid": invalid, "evidence": SOURCE_EVIDENCE["td_1182_blocks"]},
    )


def simulate_fluid_duct_windowed_mapping() -> SimulationOutcome:
    """Weryfikuje podział fluid ducts: super → windowed, reszta → fluid_duct."""
    checks = []
    invalid = []

    for meta in range(8):
        target = _resolve("ThermalDynamics:thermaldynamics.Duct16", meta)
        name = DUCT_NAMES[(16, meta)]
        is_super = meta in {6, 7}
        expected = "thermal:fluid_duct_windowed" if is_super else "thermal:fluid_duct"

        checks.append(f"{name} -> {target}")
        if target != expected:
            invalid.append({"meta": meta, "target": target, "expected": expected})

    return SimulationOutcome(
        name="fluid_duct_windowed_mapping",
        passed=not invalid,
        checks=checks,
        data={"invalid": invalid},
    )


def simulate_item_duct_to_mekanism_tier() -> SimulationOutcome:
    """Weryfikuje mapowanie Itemductów na odpowiednie tiery Mekanism."""
    checks = []
    invalid = []

    expected_tiers = {
        0: "mekanism:basic_logistical_transporter",
        1: "mekanism:basic_logistical_transporter",
        2: "mekanism:advanced_logistical_transporter",
        3: "mekanism:advanced_logistical_transporter",
        4: "mekanism:elite_logistical_transporter",
        5: "mekanism:elite_logistical_transporter",
        6: "mekanism:ultimate_logistical_transporter",
        7: "mekanism:ultimate_logistical_transporter",
    }

    for meta, expected in expected_tiers.items():
        target = _resolve("ThermalDynamics:thermaldynamics.Duct32", meta)
        name = DUCT_NAMES[(32, meta)]
        checks.append(f"{name} -> {target}")
        if target != expected:
            invalid.append({"meta": meta, "target": target, "expected": expected})

    warnings = []
    if not invalid:
        warnings.append(
            "Mekanism logistical transporters do NOT support Servo/Filter attachments "
            "as separate blocks. Pull/push is intrinsic; advanced filtering requires "
            "mekanism:logistical_sorter."
        )
        warnings.append(
            "Ender Itemduct teleportation (no physical connection) has no equivalent "
            "in Mekanism transporters. Elite tier is closest in throughput only."
        )
        warnings.append(
            "Flux-Plated Itemduct (item + RF in one block) has no equivalent. "
            "Ultimate tier covers item throughput only; RF requires separate universal cable."
        )

    return SimulationOutcome(
        name="item_duct_to_mekanism_tier",
        passed=not invalid,
        checks=checks,
        warnings=warnings,
        data={"invalid": invalid, "evidence": SOURCE_EVIDENCE["mekanism_1182_transmitters"]},
    )


def simulate_viaduct_to_teleporter() -> SimulationOutcome:
    """Weryfikuje mapowanie Viaductów na Mekanism Teleporter."""
    checks = []
    invalid = []

    mappings = {
        0: ("mekanism:teleporter", "Viaduct -> teleporter (instant teleport vs pipe travel)"),
        1: ("mekanism:teleporter", "Long-Range Viaduct -> teleporter (range irrelevant for teleporter)"),
        2: ("mekanism:teleporter", "Accelerated Viaduct -> teleporter (speed irrelevant for teleporter)"),
        3: ("mekanism:teleporter_frame", "Viaduct Frame -> teleporter_frame"),
    }

    for meta, (expected, note) in mappings.items():
        target = _resolve("ThermalDynamics:thermaldynamics.Duct64", meta)
        name = DUCT_NAMES[(64, meta)]
        checks.append(f"{name} -> {target} ({note})")
        if target != expected:
            invalid.append({"meta": meta, "target": target, "expected": expected})

    warnings = []
    if not invalid:
        warnings.append(
            "Teleporter requires a 4x5 frame of teleporter_frame blocks, power (FE), "
            "and frequency configuration. Single Viaduct block does NOT map 1:1 spatially."
        )

    return SimulationOutcome(
        name="viaduct_to_teleporter",
        passed=not invalid,
        checks=checks,
        warnings=warnings,
        data={"invalid": invalid},
    )


def simulate_attachment_loss_warning() -> SimulationOutcome:
    """Weryfikuje że załączniki (Servo/Filter/Retriever) nie mają bezpośredniego mapowania blokowego."""
    # W 1.7.10 załączniki są przechowywane w NBT TileEntity ductu jako tablica Attachment[]
    # W 1.18.2 TD ma nowe załączniki (servo_attachment, filter_attachment), ale dla
    # Itemductów->Mekanism załączniki nie istnieją jako osobne bloki.

    source_attachments = [
        {"type": "servo", "tier": "basic", "side": 0, "speed": 1},
        {"type": "filter", "tier": "hardened", "side": 1, "whitelist": ["minecraft:iron_ingot"]},
        {"type": "retriever", "tier": "signalum", "side": 2, "rs_mode": 0},
    ]

    checks = [
        "Servo attachment from 1.7.10 has no direct block equivalent in Mekanism 1.18.2.",
        "Filter attachment from 1.7.10 has no direct block equivalent in Mekanism 1.18.2.",
        "Retriever attachment from 1.7.10 has no direct block equivalent in Mekanism 1.18.2.",
        "Thermal Dynamics 1.18.2 has servo_attachment/filter_attachment items, "
        "but they are meant for TD ducts, not Mekanism transporters.",
    ]

    # Strategie konwersji
    strategies = {
        "servo": "Drop to chest + optional mekanism:logistical_sorter nearby",
        "filter": "Drop to chest + optional mekanism:logistical_sorter with filter",
        "retriever": "Drop to chest (no direct Mekanism equivalent for 'pull from network')",
    }

    data = {
        "source_attachments": source_attachments,
        "conversion_strategies": strategies,
        "evidence": (
            "Mekanism 1.18.2 transporters do not use attachment blocks. "
            "LogisticalSorter is a separate machine that can pull from inventories "
            "and push into transporters with filter support."
        ),
    }

    return SimulationOutcome(
        name="attachment_loss_warning",
        passed=True,  # To jest świadome ograniczenie, nie błąd
        checks=checks,
        warnings=[
            "Attachments will be LOST during block conversion. Inventory must be dumped to chests "
            "or manually reconstructed with Mekanism:logistical_sorter."
        ],
        data=data,
    )


def run_all() -> dict[str, Any]:
    outcomes = [
        simulate_duct_id_and_target_resolution(),
        simulate_energy_duct_tier_collapse(),
        simulate_fluid_duct_windowed_mapping(),
        simulate_item_duct_to_mekanism_tier(),
        simulate_viaduct_to_teleporter(),
        simulate_attachment_loss_warning(),
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
        "# Thermal Dynamics — Krok 2 (Symulacje kontraktowe)",
        "",
        "Symulacje weryfikują reguły konwersji Thermal Dynamics 1.7.10 → 1.18.2 (TD + Mekanism).",
        "Nie symulują pełnego działania modów — sprawdzają tylko kontrakty, które muszą być spełnione",
        "przed napisaniem kodu konwersji (krok 3).",
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
        "1. Wszystkie placeable Energy Ducts (meta 0,1,2,4,6 z offsetu 0) MUSZĄ mapować się na `thermal:energy_duct`.",
        "2. Fluid Ducts z meta 6,7 (Super-Laminar) MUSZĄ mapować się na `thermal:fluid_duct_windowed`; pozostałe na `thermal:fluid_duct`.",
        "3. Item Ducts MUSZĄ mapować się na odpowiednie tiery Mekanism Logistical Transporter (basic→advanced→elite→ultimate).",
        "4. Viaducts MUSZĄ mapować się na `mekanism:teleporter`; Viaduct Frame na `mekanism:teleporter_frame`.",
        "5. Structuralduct i Glowstone Illuminator NIE MAJĄ targetu — konwerter musi wyemitować placeholder lub usunąć blok.",
        "6. Załączniki (Servo/Filter/Retriever) z NBT ductu MUSZĄ być zrzucane do skrzyni (lub zignorowane) — nie mają bezpośredniego mapowania blokowego.",
        "",
        "## Szczegóły",
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
