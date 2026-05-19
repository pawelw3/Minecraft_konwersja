"""
Szczegółowa analiza bloków Thermal Dynamics w mapie 1.7.10.

Krok 1 konwersji: wypisanie wszystkich bloków i Tile Entities moda
Thermal Dynamics na podstawie danych z rzeczywistej mapy.

Mapowanie docelowe:
- Energy Ducts → thermal:energy_duct
- Fluid Ducts → thermal:fluid_duct / thermal:fluid_duct_windowed
- Item Ducts → mekanism:*_logistical_transporter
- Transport Ducts → mekanism:teleporter / mekanism:teleporter_frame
- Structural Ducts → BRAK (placeholder)
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent))

from minecraft_map_parser import ModBlockExtractor


# Mapowanie metadata → (internal_name, display_name, category, target_block_1.18.2)
# Źródło: dekompilacja TDDucts.java z ThermalDynamics-[1.7.10]1.2.1-172.jar
# Target: weryfikacja kodu TD 1.18.2 + Mekanism 1.18.2
DUCT_OFFSETS = {
    0: {
        0: ("energyBasic", "Leadstone Fluxduct", "energy", "thermal:energy_duct"),
        1: ("energyHardened", "Hardened Fluxduct", "energy", "thermal:energy_duct"),
        2: ("energyReinforced", "Redstone Energy Fluxduct", "energy", "thermal:energy_duct"),
        3: ("energyReinforcedEmpty", "Reinforced Fluxduct (empty)", "crafting", None),
        4: ("energyResonant", "Signalum Fluxduct", "energy", "thermal:energy_duct"),
        5: ("energyResonantEmpty", "Resonant Fluxduct (empty)", "crafting", None),
        6: ("energySuperCond", "Cryo-Stabilized Fluxduct", "energy", "thermal:energy_duct"),
        7: ("energySuperCondEmpty", "Cryo-Stabilized Fluxduct (empty)", "crafting", None),
    },
    16: {
        0: ("fluidBasic", "Temperate Fluiduct", "fluid", "thermal:fluid_duct"),
        1: ("fluidBasicOpaque", "Temperate Fluiduct (opaque)", "fluid", "thermal:fluid_duct"),
        2: ("fluidHardened", "Hardened Fluiduct", "fluid", "thermal:fluid_duct"),
        3: ("fluidHardenedOpaque", "Hardened Fluiduct (opaque)", "fluid", "thermal:fluid_duct"),
        4: ("fluidFlux", "Flux-Plated Fluiduct", "fluid", "thermal:fluid_duct"),
        5: ("fluidFluxOpaque", "Flux-Plated Fluiduct (opaque)", "fluid", "thermal:fluid_duct"),
        6: ("fluidSuper", "Super-Laminar Fluiduct", "fluid", "thermal:fluid_duct_windowed"),
        7: ("fluidSuperOpaque", "Super-Laminar Fluiduct (opaque)", "fluid", "thermal:fluid_duct_windowed"),
    },
    32: {
        0: ("itemBasic", "Itemduct", "item", "mekanism:basic_logistical_transporter"),
        1: ("itemBasicOpaque", "Itemduct (opaque)", "item", "mekanism:basic_logistical_transporter"),
        2: ("itemFast", "Impulse Itemduct", "item", "mekanism:advanced_logistical_transporter"),
        3: ("itemFastOpaque", "Impulse Itemduct (opaque)", "item", "mekanism:advanced_logistical_transporter"),
        4: ("itemEnder", "Ender Itemduct", "item", "mekanism:elite_logistical_transporter"),
        5: ("itemEnderOpaque", "Ender Itemduct (opaque)", "item", "mekanism:elite_logistical_transporter"),
        6: ("itemEnergy", "Flux-Plated Itemduct", "item", "mekanism:ultimate_logistical_transporter"),
        7: ("itemEnergyOpaque", "Flux-Plated Itemduct (opaque)", "item", "mekanism:ultimate_logistical_transporter"),
    },
    48: {
        0: ("structure", "Structuralduct", "structural", None),
        1: ("lightDuct", "Glowstone Illuminator", "structural", None),
    },
    64: {
        0: ("transportBasic", "Viaduct", "transport", "mekanism:teleporter"),
        1: ("transportLongRange", "Long-Range Viaduct", "transport", "mekanism:teleporter"),
        2: ("transportCrossover", "Accelerated Viaduct", "transport", "mekanism:teleporter"),
        3: ("transportFrame", "Viaduct Frame", "crafting", "mekanism:teleporter_frame"),
    },
}


def resolve_duct(block_id: str, metadata: int):
    """Rozwija block_id + metadata na konkretny typ ductu i cel konwersji."""
    if not block_id.startswith("ThermalDynamics:thermaldynamics.Duct"):
        return None
    try:
        offset = int(block_id.replace("ThermalDynamics:thermaldynamics.Duct", ""))
    except ValueError:
        return None

    mapping = DUCT_OFFSETS.get(offset, {})
    return mapping.get(
        metadata,
        (f"unknown_{offset + metadata}", f"Unknown duct (offset={offset}, meta={metadata})", "unknown", None)
    )


def analyze_thermal_dynamics():
    project_root = Path(__file__).parent.parent.parent
    region_dir = project_root / 'mapa_1710' / 'region'

    extractor = ModBlockExtractor()

    # Analizujemy wszystkie regiony (próbkowanie — nie ładujemy wszystkich chunków naraz)
    all_td_blocks = []
    te_counts = Counter()

    if region_dir.exists():
        region_files = list(region_dir.glob("*.mca"))
        print(f"Znaleziono {len(region_files)} plików regionów.")

        for region_file in region_files:
            try:
                data = extractor.extract_from_region(
                    str(region_file),
                    sample_size=50,  # próbkowanie — nie analizujemy każdego chunka
                    include_vanilla=False,
                    include_entities=True,
                )

                blocks = data.get('blocks', [])
                tile_entities = data.get('tile_entities', [])

                # Filtruj tylko ThermalDynamics
                td_blocks = [b for b in blocks if getattr(b, 'mod_name', '') == 'ThermalDynamics']
                all_td_blocks.extend(td_blocks)

                for te in tile_entities:
                    if te.get('id', '').startswith('thermaldynamics.'):
                        te_counts[te['id']] += 1
            except Exception as e:
                print(f"  Błąd przy {region_file.name}: {e}")
    else:
        print(f"Katalog regionów nie istnieje: {region_dir}")
        return

    print("=" * 70)
    print("ANALIZA BLOKÓW THERMAL DYNAMICS — KROK 1")
    print("=" * 70)

    print(f"\n1. Łączna liczba bloków Thermal Dynamics: {len(all_td_blocks)}")

    # Analiza ID bloków (raw block IDs)
    id_counts = Counter(b.block_id for b in all_td_blocks)
    print("\n2. Rozkład raw block IDs:")
    for block_id, count in id_counts.most_common():
        print(f"   {block_id}: {count} bloków")

    # Analiza z rozwiązaniem typów ductów
    print("\n3. Rozkład typów ductów (block_id + metadata → nazwa → cel):")
    duct_type_counts = Counter()
    duct_category_counts = Counter()
    target_block_counts = Counter()
    problematic_ducts = []

    for b in all_td_blocks:
        resolved = resolve_duct(b.block_id, b.metadata)
        if resolved:
            internal_name, display_name, category, target = resolved
            duct_type_counts[display_name] += 1
            duct_category_counts[category] += 1
            if target:
                target_block_counts[target] += 1
            else:
                problematic_ducts.append((b.x, b.y, b.z, display_name))
        else:
            duct_type_counts[f"{b.block_id}:{b.metadata}"] += 1

    for name, count in duct_type_counts.most_common():
        print(f"   {name}: {count} bloków")

    print("\n4. Podsumowanie kategorii:")
    for cat, count in duct_category_counts.most_common():
        print(f"   {cat}: {count} bloków")

    print("\n5. Tile Entities (z próbkowanych chunków):")
    for te_id, count in te_counts.most_common():
        print(f"   {te_id}: {count}")

    # Analiza przestrzenna
    print("\n6. Analiza przestrzenna:")
    by_category = defaultdict(list)
    for b in all_td_blocks:
        resolved = resolve_duct(b.block_id, b.metadata)
        if resolved:
            by_category[resolved[2]].append((b.x, b.y, b.z))

    for cat, coords in by_category.items():
        ys = [c[1] for c in coords]
        print(f"   {cat}: {len(coords)} bloków, Y={min(ys)}–{max(ys)}")

    # Mapowanie docelowe
    print("\n7. Mapowanie docelowe (bloki 1.18.2):")
    for target, count in target_block_counts.most_common():
        print(f"   → {target}: {count} bloków")

    # Problematyczne bloki (bez odpowiednika)
    if problematic_ducts:
        print(f"\n8. ⚠️ Bloki BEZ odpowiednika 1.18.2 ({len(problematic_ducts)}):")
        for x, y, z, name in problematic_ducts[:10]:
            print(f"      [{x}, {y}, {z}] {name}")
        if len(problematic_ducts) > 10:
            print(f"      ... oraz {len(problematic_ducts) - 10} innych")

    print("\n" + "=" * 70)
    print("Koniec raportu krok 1 — Thermal Dynamics")
    print("=" * 70)

    # Zapisz wyniki do JSON (opcjonalnie)
    import json
    output_dir = Path(__file__).parent
    report = {
        "total_blocks": len(all_td_blocks),
        "by_raw_id": dict(id_counts),
        "by_duct_type": dict(duct_type_counts),
        "by_category": dict(duct_category_counts),
        "target_blocks": dict(target_block_counts),
        "tile_entities": dict(te_counts),
        "problematic_positions": [
            {"x": x, "y": y, "z": z, "type": name}
            for x, y, z, name in problematic_ducts
        ],
    }
    report_path = output_dir / "thermal_dynamics_step1_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nRaport zapisano do: {report_path}")


if __name__ == '__main__':
    analyze_thermal_dynamics()
