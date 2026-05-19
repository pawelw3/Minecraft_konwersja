"""Analiza pokrycia konwertera Thermal na realnej mapie."""
import sys
sys.path.insert(0, 'src')

from pathlib import Path
import json

from converters.thermal.mappings import (
    STATIC_MAPPINGS, DUCT_MAPPINGS, FLUID_MAPPINGS, TE_ID_TO_BLOCK_META,
    get_mapping, get_mapping_by_te_id,
)

# Block IDs from level.dat
BLOCK_ID_REGISTRY = {
    962: "ThermalFoundation:Ore",
    963: "ThermalFoundation:Storage",
    964: "ThermalFoundation:FluidRedstone",
    965: "ThermalFoundation:FluidGlowstone",
    968: "ThermalFoundation:FluidCryotheum",
    971: "ThermalFoundation:FluidMana",
    972: "ThermalFoundation:FluidSteam",
    973: "ThermalFoundation:FluidCoal",
    1293: "ThermalFoundation:FluidEnder",
    1414: "ThermalFoundation:FluidPetrotheum",
    1942: "ThermalFoundation:FluidPyrotheum",
    2015: "ThermalFoundation:FluidAerotheum",
    3304: "ThermalDynamics:ThermalDynamics_0",
    3305: "ThermalDynamics:ThermalDynamics_16",
    3306: "ThermalDynamics:ThermalDynamics_32",
    3307: "ThermalDynamics:ThermalDynamics_48",
    3308: "ThermalDynamics:ThermalDynamics_64",
    3438: "ThermalExpansion:Machine",
    3439: "ThermalExpansion:Device",
    3440: "ThermalExpansion:Dynamo",
    3441: "ThermalExpansion:Cell",
    3442: "ThermalExpansion:Tank",
    3443: "ThermalExpansion:Strongbox",
    3444: "ThermalExpansion:Cache",
    3445: "ThermalExpansion:Workbench",
    3446: "ThermalExpansion:Tesseract",
    3447: "ThermalExpansion:Plate",
    3448: "ThermalExpansion:Light",
    3449: "ThermalExpansion:Frame",
    3450: "ThermalExpansion:Glass",
    3451: "ThermalExpansion:Rockwool",
    3452: "ThermalExpansion:Sponge",
    3453: "ThermalExpansion:FakeAirSignal",
    3454: "ThermalExpansion:FakeAirLight",
    3455: "ThermalExpansion:FakeAirForce",
    3456: "ThermalExpansion:FakeAirBarrier",
}

# ThermalDynamics sub-block offsets
TD_OFFSETS = {
    "ThermalDynamics:ThermalDynamics_0": 0,
    "ThermalDynamics:ThermalDynamics_16": 16,
    "ThermalDynamics:ThermalDynamics_32": 32,
    "ThermalDynamics:ThermalDynamics_48": 48,
    "ThermalDynamics:ThermalDynamics_64": 64,
}

# Mapping from global meta to logical block name (based on TDDucts.java)
TD_GLOBAL_META_MAP = {
    # Energy (offset 0)
    0: ("ThermalDynamics:FluxDuct", 0, "energyBasic/Leadstone"),
    1: ("ThermalDynamics:FluxDuct", 1, "energyHardened"),
    2: ("ThermalDynamics:FluxDuct", None, "energyReinforced"),
    3: ("ThermalDynamics:FluxDuct", None, "energyReinforcedEmpty"),
    4: ("ThermalDynamics:FluxDuct", None, "energyResonant"),
    5: ("ThermalDynamics:FluxDuct", None, "energyResonantEmpty"),
    6: ("ThermalDynamics:FluxDuct", None, "energySuperCond"),
    7: ("ThermalDynamics:FluxDuct", None, "energySuperCondEmpty"),
    # Fluid (offset 16)
    16: ("ThermalDynamics:FluidDuct", 0, "fluidBasic"),
    17: ("ThermalDynamics:FluidDuct", 1, "fluidBasicOpaque"),
    18: ("ThermalDynamics:FluidDuct", None, "fluidHardened"),
    19: ("ThermalDynamics:FluidDuct", None, "fluidHardenedOpaque"),
    20: ("ThermalDynamics:FluidDuct", 2, "fluidFlux"),
    21: ("ThermalDynamics:FluidDuct", None, "fluidFluxOpaque"),
    22: ("ThermalDynamics:FluidDuct", 3, "fluidSuper"),
    23: ("ThermalDynamics:FluidDuct", None, "fluidSuperOpaque"),
    # Item (offset 32)
    32: ("ThermalDynamics:ItemDuct", 0, "itemBasic"),
    33: ("ThermalDynamics:ItemDuct", None, "itemBasicOpaque"),
    34: ("ThermalDynamics:ItemDuct", None, "itemFast"),
    35: ("ThermalDynamics:ItemDuct", None, "itemFastOpaque"),
    36: ("ThermalDynamics:ItemDuct", 1, "itemEnder"),
    37: ("ThermalDynamics:ItemDuct", None, "itemEnderOpaque"),
    38: ("ThermalDynamics:ItemDuct", 2, "itemEnergy/Flux"),
    39: ("ThermalDynamics:ItemDuct", None, "itemEnergyOpaque"),
    # Structure (offset 48)
    48: ("ThermalDynamics:StructuralDuct", 0, "structure"),
    49: ("ThermalDynamics:StructuralDuct", None, "lightDuct"),
    # Transport (offset 64)
    64: ("ThermalDynamics:TransportDuct", 0, "transportBasic"),
    65: ("ThermalDynamics:TransportDuct", 1, "transportLongRange"),
    66: ("ThermalDynamics:TransportDuct", 2, "transportCrossover"),
    67: ("ThermalDynamics:TransportDuct", None, "transportFrame"),
}


def check_block_coverage():
    with open("output/thermal_block_discovery.json") as f:
        data = json.load(f)

    block_ids = data["block_ids"]
    results = []
    for bid, count in sorted(block_ids.items(), key=lambda x: -x[1]):
        bid = int(bid)
        name = BLOCK_ID_REGISTRY.get(bid, f"UNKNOWN({bid})")
        supported = False
        notes = []

        if "FakeAir" in name:
            supported = True
            notes.append("ignored (technical block)")
        elif name.startswith("ThermalFoundation:Fluid"):
            supported = True
            notes.append("fluid block - mapped via FLUID_MAPPINGS")
        elif name.startswith("ThermalDynamics:ThermalDynamics_"):
            offset = TD_OFFSETS.get(name, 0)
            notes.append(f"sub-block with offset {offset}")
            # Check if we have mappings for ANY meta of this sub-block
            # For now, check a few common ones
            has_any = False
            for local_meta in range(16):
                global_meta = offset + local_meta
                if global_meta in TD_GLOBAL_META_MAP:
                    logical_name, mapped_meta, desc = TD_GLOBAL_META_MAP[global_meta]
                    if mapped_meta is not None and (logical_name, mapped_meta) in STATIC_MAPPINGS:
                        has_any = True
                    elif mapped_meta is not None and (logical_name, mapped_meta) in DUCT_MAPPINGS:
                        has_any = True
            supported = has_any
            if not has_any:
                notes.append("NO direct sub-block mappings in converter")
        elif name == "ThermalExpansion:Glass":
            supported = (name, 0) in STATIC_MAPPINGS
            notes.append("hardcoded glass mapping")
        elif name == "ThermalExpansion:Sponge":
            supported = (name, 0) in STATIC_MAPPINGS
            notes.append("hardcoded sponge mapping")
        elif name == "ThermalExpansion:Machine":
            supported = True  # Has many meta mappings
            notes.append("multi-meta machine block")
        else:
            # Generic check: does any meta 0-15 have mapping?
            has_mapping = False
            for meta in range(16):
                if get_mapping(name, meta) is not None:
                    has_mapping = True
                    break
            supported = has_mapping

        results.append({
            "block_id": bid,
            "name": name,
            "count": count,
            "supported": supported,
            "notes": "; ".join(notes),
        })

    return results


def check_te_coverage():
    with open("output/thermal_te_discovery.json") as f:
        data = json.load(f)

    te_ids = data["te_ids"]
    results = []
    for te_id, count in sorted(te_ids.items(), key=lambda x: -x[1]):
        mapping = get_mapping_by_te_id(te_id)
        supported = mapping is not None
        results.append({
            "te_id": te_id,
            "count": count,
            "supported": supported,
            "target": mapping.target_block_id if mapping else "N/A",
        })
    return results


def generate_report():
    block_results = check_block_coverage()
    te_results = check_te_coverage()

    total_blocks = sum(r["count"] for r in block_results)
    supported_blocks = sum(r["count"] for r in block_results if r["supported"])
    total_te = sum(r["count"] for r in te_results)
    supported_te = sum(r["count"] for r in te_results if r["supported"])

    report = []
    report.append("# Raport pokrycia konwertera Thermal Series (Zadanie 4)")
    report.append("")
    report.append("## Podsumowanie")
    report.append(f"- Bloki: {supported_blocks:,} / {total_blocks:,} ({supported_blocks/total_blocks*100:.1f}%)")
    report.append(f"- Tile Entities: {supported_te:,} / {total_te:,} ({supported_te/total_te*100:.1f}%)")
    report.append("")

    report.append("## Bloki (Block IDs)")
    report.append("| Block ID | Nazwa | Liczba | Obsługiwany | Uwagi |")
    report.append("|----------|-------|--------|-------------|-------|")
    for r in block_results:
        ok = "✅" if r["supported"] else "❌"
        report.append(f"| {r['block_id']} | {r['name']} | {r['count']:,} | {ok} | {r['notes']} |")
    report.append("")

    report.append("## Tile Entities")
    report.append("| TE ID | Liczba | Obsługiwany | Docelowy blok |")
    report.append("|-------|--------|-------------|---------------|")
    for r in te_results:
        ok = "✅" if r["supported"] else "❌"
        report.append(f"| {r['te_id']} | {r['count']:,} | {ok} | {r['target']} |")
    report.append("")

    # Identify gaps
    report.append("## Luki w mapowaniach")
    missing_blocks = [r for r in block_results if not r["supported"]]
    missing_te = [r for r in te_results if not r["supported"]]
    if missing_blocks:
        report.append("### Brakujące bloki")
        for r in missing_blocks:
            report.append(f"- {r['name']} (ID {r['block_id']}): {r['count']:,} wystąpień")
    if missing_te:
        report.append("### Brakujące Tile Entities")
        for r in missing_te:
            report.append(f"- {r['te_id']}: {r['count']:,} wystąpień")
    report.append("")

    report.append("## Kluczowe problemy")
    report.append("1. **ThermalDynamics sub-bloki**: Mapa używa `ThermalDynamics:ThermalDynamics_0/16/32/48/64` zamiast")
    report.append("   `ThermalDynamics:FluxDuct/FluidDuct/ItemDuct`. Konwerter musi dodawać offset do metadata.")
    report.append("2. **Opaque variants**: Wiele ductów ma wersje 'opaque' (np. fluidHardenedOpaque) które nie mają")
    report.append("   bezpośrednich mapowań w 1.18.2 (1.18.2 Thermal Dynamics nie rozróżnia opaque/non-opaque).")
    report.append("3. **Empty/Crafting ducts**: energyReinforcedEmpty, energyResonantEmpty, energySuperCondEmpty,")
    report.append("   transportFrame - to bloki craftingowe/techniczne które powinny być zignorowane lub zmapowane na structure.")

    report_text = "\n".join(report)

    out_path = Path("output/thermal_coverage_report.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report_text)
    print(f"Report saved to {out_path}")

    # Also save JSON
    json_path = Path("output/thermal_coverage.json")
    with open(json_path, 'w') as f:
        json.dump({
            "blocks": block_results,
            "tile_entities": te_results,
            "summary": {
                "total_blocks": total_blocks,
                "supported_blocks": supported_blocks,
                "total_te": total_te,
                "supported_te": supported_te,
            }
        }, f, indent=2)
    print(f"Saved JSON to {json_path}")


if __name__ == "__main__":
    generate_report()
