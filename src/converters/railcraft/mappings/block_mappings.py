"""
Mapowania bloków Railcraft 1.7.10 → strict 1.18.2 (Create / Steam'n'Rails / IE / Mekanism / Thermal).

Strategia (zgodnie z docs/sprawdzenie_codex/cz4_analiza_funkcjonalnosci_i_zamiennikow_2026-05-18.md):
- Tory/rozjazdy → Create + Steam'n'Rails
- Sygnalizacja → Steam'n'Rails / vanilla redstone
- Maszyny przemysłowe → Immersive Engineering / Thermal / Mekanism per funkcja
- Logistyka (loadery) → Create chutes/funnels / Mekanism logistical pipes
- Anchory → placeholder (brak odpowiednika w 1.18.2)
- Tanks → Create fluid tank / Thermal fluid cell
- Detektory → minecraft:observer (lossy)
- Residual Heat (RCHiddenTile) → IGNORE (usunięcie)

UWAGA: Źródła modów docelowych (Create 1.18.2, Steam'n'Rails 1.18.2, IE 1.18.2)
nie zostały zweryfikowane lokalnie — mapowania oparte są na dokumentacji projektu
i ogólnej znajomości funkcji modów. Wymagają weryfikacji podczas testów E2E.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from converters.common.placeholders import PLACEHOLDER_BLOCK_ID

try:
    from .block_inventory import (
        RAILCRAFT_DETECTORS,
        RAILCRAFT_MACHINE_ALPHA,
        RAILCRAFT_MACHINE_BETA,
        RAILCRAFT_MACHINE_DELTA,
        RAILCRAFT_MACHINE_EPSILON,
        RAILCRAFT_MACHINE_GAMMA,
        RAILCRAFT_SIGNALS,
        RAILCRAFT_TRACKS,
    )
except ImportError:
    RAILCRAFT_TRACKS = []
    RAILCRAFT_MACHINE_ALPHA = []
    RAILCRAFT_MACHINE_BETA = []
    RAILCRAFT_MACHINE_GAMMA = []
    RAILCRAFT_MACHINE_DELTA = []
    RAILCRAFT_MACHINE_EPSILON = []
    RAILCRAFT_SIGNALS = []
    RAILCRAFT_DETECTORS = []


@dataclass(frozen=True)
class BlockMapping:
    source_block_id: str
    metadata: int | None
    target_block_id: str
    has_block_entity: bool = False
    nbt_converter: str = "identity"
    notes: str = ""
    blockstate_props: dict[str, str] | None = None
    # Dodatkowe info dla symulacji
    track_tag: str | None = None  # tylko dla torów


# ──────────────────────────────────────────────────────────────────────────────
# Placeholder i utilities
# ──────────────────────────────────────────────────────────────────────────────

PLACEHOLDER = PLACEHOLDER_BLOCK_ID


def _make_track_mappings() -> dict[tuple[str, int | None], BlockMapping]:
    """Tory Railcraft → Create / Steam'n'Rails / vanilla.

    Steam'n'Rails w 1.18.2 dodaje tory Create z różnymi gauge'ami
    i custom track types, ale NIE ma bezpośrednich odpowiedników
    wszystkich specjalnych torów Railcrafta (booster, launcher,
    priming, embarking, itp.).
    """
    mappings: dict[tuple[str, int | None], BlockMapping] = {}
    block = "railcraft.track"

    # Domyślny fallback dla wszystkich torów
    for entry in RAILCRAFT_TRACKS:
        meta = entry["meta"]
        tag = entry.get("tag", "")
        deprecated = entry.get("deprecated", False)

        if deprecated:
            # Tory deprecated → usuwamy (placeholder z komentarzem)
            mappings[(block, meta)] = BlockMapping(
                block, meta, PLACEHOLDER, False, "ignored",
                f"Deprecated track {tag} — removed in modern versions",
                track_tag=tag,
            )
            continue

        # Mapowanie per trackTag
        if "electric" in tag:
            # Electric tracks → Create track (brak wysokiego napięcia w 1.18.2 Create)
            target = "create:track"
            props = {"shape": "north_south"}
            note = "Electric track → Create standard track (lossy: no electrification)"
        elif "speed" in tag and "boost" not in tag and "transition" not in tag and "switch" not in tag and "wye" not in tag and "junction" not in tag:
            # High Speed Track → Create track (brak boostera wysokiej prędkości)
            target = "create:track"
            props = {"shape": "north_south"}
            note = "High Speed track → Create standard track (lossy: no speed boost)"
        elif "reinforced" in tag:
            target = "create:track"
            props = {"shape": "north_south"}
            note = "Reinforced track → Create standard track (lossy: no explosion resistance)"
        elif "slow" in tag or "wood" in tag:
            # Wooden tracks → Create standard track lub vanilla
            target = "minecraft:rail"
            props = {"shape": "north_south"}
            note = "Wooden track → vanilla rail (lossy: no special behavior)"
        elif "switch" in tag or "wye" in tag or "junction" in tag:
            # Zwrotnice/rozjazdy → Create track (Create obsługuje zwrotnice automatycznie)
            target = "create:track"
            props = {"shape": "north_south"}
            note = "Switch/Junction/Wye → Create track (Create handles switching via train pathing)"
        elif "buffer.stop" in tag:
            target = PLACEHOLDER
            props = None
            note = "Buffer stop → placeholder (no direct equivalent in 1.18.2)"
        elif "coupler" in tag or "decoupler" in tag:
            # Coupler track → Steam'n'Rails ma coupler?
            # W 1.18.2 Steam'n'Rails ma track coupler.
            target = "railways:track_coupler"
            props = None
            note = "Coupler track → Steam'n'Rails track coupler (approximate)"
        elif "embarking" in tag or "disembarking" in tag:
            target = PLACEHOLDER
            props = None
            note = "Embarking/Disembarking → placeholder (no direct equivalent)"
        elif "boarding" in tag or "holding" in tag or "locking" in tag:
            target = PLACEHOLDER
            props = None
            note = "Boarding/Holding/Locking track → placeholder (no direct equivalent)"
        elif "launcher" in tag:
            target = PLACEHOLDER
            props = None
            note = "Launcher track → placeholder (no direct equivalent)"
        elif "priming" in tag:
            target = PLACEHOLDER
            props = None
            note = "Priming track → placeholder (no direct equivalent)"
        elif "routing" in tag:
            target = PLACEHOLDER
            props = None
            note = "Routing track → placeholder (no direct equivalent)"
        elif "whistle" in tag or "locomotive" in tag or "limiter" in tag:
            target = PLACEHOLDER
            props = None
            note = "Whistle/Locomotive/Limiter track → placeholder (no direct equivalent)"
        elif "control" in tag:
            target = "minecraft:powered_rail"
            props = {"shape": "north_south"}
            note = "Control track → vanilla powered rail (lossy)"
        elif "oneway" in tag:
            target = "create:track"
            props = {"shape": "north_south"}
            note = "One-way track → Create track (lossy: no one-way enforcement)"
        elif "gated" in tag:
            target = PLACEHOLDER
            props = None
            note = "Gated track → placeholder (no direct equivalent)"
        elif "suspended" in tag:
            target = "create:track"
            props = {"shape": "north_south"}
            note = "Suspended track → Create track (lossy: no suspension visuals)"
        elif "disposal" in tag:
            target = "minecraft:hopper"
            props = {"facing": "down"}
            note = "Disposal track → hopper (lossy: no cart integration)"
        elif "detector" in tag:
            target = "minecraft:observer"
            props = {"facing": "north"}
            note = "Detector direction track → observer (lossy)"
        elif "force" in tag:
            target = PLACEHOLDER
            props = None
            note = "Force track → placeholder (no direct equivalent)"
        else:
            # Default: standard Railcraft track → Create track
            target = "create:track"
            props = {"shape": "north_south"}
            note = f"{tag} → Create track (default fallback)"

        mappings[(block, meta)] = BlockMapping(
            block, meta, target, True if target != PLACEHOLDER else False,
            "track" if target != PLACEHOLDER else "placeholder",
            note, props, track_tag=tag,
        )

    # Elevator track — osobny blok
    mappings[("railcraft.track.elevator", 0)] = BlockMapping(
        "railcraft.track.elevator", 0, PLACEHOLDER, False, "placeholder",
        "Elevator track → placeholder (no direct equivalent in 1.18.2)"
    )

    return mappings


def _make_machine_alpha_mappings() -> dict[tuple[str, int], BlockMapping]:
    """Maszyny Alpha → IE / Thermal / Mekanism / placeholder."""
    block = "railcraft.machine.alpha"
    return {
        # Anchory → placeholder (brak chunk loaderów w paczce 1.18.2)
        (block, 0): BlockMapping(block, 0, PLACEHOLDER, True, "placeholder", "World Anchor → placeholder (no chunk loader mod in 1.18.2 pack)"),
        (block, 2): BlockMapping(block, 2, PLACEHOLDER, True, "placeholder", "Personal Anchor → placeholder"),
        (block, 4): BlockMapping(block, 4, PLACEHOLDER, True, "placeholder", "Admin Anchor → placeholder"),
        (block, 13): BlockMapping(block, 13, PLACEHOLDER, True, "placeholder", "Passive Anchor → placeholder"),

        # Steam Turbine → Thermal Dynamo (Stirling) / Mekanism Heat Generator
        (block, 1): BlockMapping(block, 1, "thermal:dynamo_stirling", True, "generic_machine", "Steam Turbine → Thermal Stirling Dynamo (lossy: different mechanics)"),

        # Steam Oven → Smoker / Thermal Furnace
        (block, 3): BlockMapping(block, 3, "minecraft:smoker", True, "generic_machine", "Steam Oven → vanilla Smoker (functional approximation)"),

        # Smoker → Campfire (wizualnie podobne, funkcjonalnie inne)
        (block, 5): BlockMapping(block, 5, "minecraft:campfire", False, "identity", "Smoker → Campfire (visual only, lossy)", {"lit": "true"}),

        # Trade Station → placeholder
        (block, 6): BlockMapping(block, 6, PLACEHOLDER, True, "placeholder", "Trade Station → placeholder (no villager trading station in target mods)"),

        # Coke Oven → IE Coke Oven (BEZPOŚREDNI odpowiednik!)
        (block, 7): BlockMapping(block, 7, "immersiveengineering:coke_oven", True, "multiblock", "Coke Oven → IE Coke Oven (multiblock, requires structure validation)"),

        # Rolling Machine → Create Mechanical Press (funkcjonalnie podobne: prasowanie płyt)
        (block, 8): BlockMapping(block, 8, "create:mechanical_press", True, "generic_machine", "Rolling Machine → Create Mechanical Press (lossy: different recipes)"),

        # Steam Traps → placeholder (brak pułapek parowych w targetach)
        (block, 9): BlockMapping(block, 9, PLACEHOLDER, True, "placeholder", "Steam Trap Manual → placeholder"),
        (block, 10): BlockMapping(block, 10, PLACEHOLDER, True, "placeholder", "Steam Trap Auto → placeholder"),

        # Feed Station → Hopper + Dispenser combo (lub placeholder)
        (block, 11): BlockMapping(block, 11, "minecraft:dispenser", True, "generic_machine", "Feed Station → Dispenser (lossy: no automatic animal feeding)"),

        # Blast Furnace → IE Blast Furnace (BEZPOŚREDNI odpowiednik!)
        (block, 12): BlockMapping(block, 12, "immersiveengineering:blast_furnace", True, "multiblock", "Blast Furnace → IE Blast Furnace (multiblock, requires structure validation)"),

        # Water Tank → Create Fluid Tank
        (block, 14): BlockMapping(block, 14, "create:fluid_tank", True, "generic_machine", "Water Tank Siding → Create Fluid Tank (lossy: different multiblock rules)"),

        # Rock Crusher → Create Crushing Wheel / IE Crusher
        (block, 15): BlockMapping(block, 15, "create:crushing_wheel", True, "generic_machine", "Rock Crusher → Create Crushing Wheel (functional: ore crushing)"),
    }


def _make_machine_beta_mappings() -> dict[tuple[str, int], BlockMapping]:
    """Maszyny Beta → Create / Thermal / placeholder."""
    block = "railcraft.machine.beta"
    return {
        # Iron Tank → Create Fluid Tank
        (block, 0): BlockMapping(block, 0, "create:fluid_tank", True, "multiblock", "Iron Tank Wall → Create Fluid Tank (lossy: different multiblock)"),
        (block, 1): BlockMapping(block, 1, "create:fluid_tank", True, "multiblock", "Iron Tank Gauge → Create Fluid Tank (lossy: gauge function lost)"),
        (block, 2): BlockMapping(block, 2, "create:fluid_tank", True, "multiblock", "Iron Tank Valve → Create Fluid Tank (lossy: valve function lost)"),

        # Steel Tank → Thermal Fluid Cell (lub Create Fluid Tank)
        (block, 13): BlockMapping(block, 13, "create:fluid_tank", True, "multiblock", "Steel Tank Wall → Create Fluid Tank"),
        (block, 14): BlockMapping(block, 14, "create:fluid_tank", True, "multiblock", "Steel Tank Gauge → Create Fluid Tank"),
        (block, 15): BlockMapping(block, 15, "create:fluid_tank", True, "multiblock", "Steel Tank Valve → Create Fluid Tank"),

        # Boiler → Thermal Dynamo (Stirling) / placeholder
        (block, 3): BlockMapping(block, 3, "thermal:dynamo_stirling", True, "generic_machine", "Low Pressure Boiler Tank → Stirling Dynamo (functional: heat→energy)"),
        (block, 4): BlockMapping(block, 4, "thermal:dynamo_compression", True, "generic_machine", "High Pressure Boiler Tank → Compression Dynamo (functional: heat→energy)"),
        (block, 5): BlockMapping(block, 5, "thermal:dynamo_stirling", True, "generic_machine", "Solid Firebox → Stirling Dynamo (functional: solid fuel→energy)"),
        (block, 6): BlockMapping(block, 6, "thermal:dynamo_compression", True, "generic_machine", "Liquid Firebox → Compression Dynamo (functional: liquid fuel→energy)"),

        # Steam Engines → Create Steam Engine / Thermal Dynamo
        (block, 7): BlockMapping(block, 7, "create:steam_engine", True, "generic_machine", "Hobbyist Steam Engine → Create Steam Engine (functional approximation)"),
        (block, 8): BlockMapping(block, 8, "create:steam_engine", True, "generic_machine", "Commercial Steam Engine → Create Steam Engine"),
        (block, 9): BlockMapping(block, 9, "create:steam_engine", True, "generic_machine", "Industrial Steam Engine → Create Steam Engine"),

        # Anchor Sentinel → placeholder
        (block, 10): BlockMapping(block, 10, PLACEHOLDER, True, "placeholder", "Anchor Sentinel → placeholder"),

        # Void Chest → Thermal Nullifier / Trash Can
        (block, 11): BlockMapping(block, 11, "thermal:device_nullifier", True, "generic_machine", "Void Chest → Thermal Nullifier (functional: item deletion)"),

        # Metals Chest → Iron Chest
        (block, 12): BlockMapping(block, 12, "ironchest:iron_chest", True, "inventory", "Metals Chest → Iron Chest (lossy: no metal sorting)"),
    }


def _make_machine_gamma_mappings() -> dict[tuple[str, int], BlockMapping]:
    """Maszyny Gamma (loadery/unloaderzy) → Create / Mekanism / Thermal."""
    block = "railcraft.machine.gamma"
    return {
        # Item Loadery → Create Funnel / Chute / Hopper
        (block, 0): BlockMapping(block, 0, "create:chute", True, "generic_machine", "Item Loader → Create Chute (lossy: no cart integration)"),
        (block, 1): BlockMapping(block, 1, "create:chute", True, "generic_machine", "Item Unloader → Create Chute"),
        (block, 2): BlockMapping(block, 2, "create:smart_chute", True, "generic_machine", "Adv. Item Loader → Create Smart Chute (filtering)"),
        (block, 3): BlockMapping(block, 3, "create:smart_chute", True, "generic_machine", "Adv. Item Unloader → Create Smart Chute"),

        # Fluid Loadery → Create Fluid Pipe / Pump
        (block, 4): BlockMapping(block, 4, "create:fluid_pipe", True, "generic_machine", "Fluid Loader → Create Fluid Pipe (lossy: no cart integration)"),
        (block, 5): BlockMapping(block, 5, "create:fluid_pipe", True, "generic_machine", "Fluid Unloader → Create Fluid Pipe"),

        # Energy Loadery (IC2 EU) → Mekanism Universal Cable / Energy Cube
        (block, 6): BlockMapping(block, 6, "mekanism:basic_universal_cable", False, "identity", "Energy Loader (IC2) → Mekanism Universal Cable (lossy: no cart integration)"),
        (block, 7): BlockMapping(block, 7, "mekanism:basic_universal_cable", False, "identity", "Energy Unloader (IC2) → Mekanism Universal Cable"),

        # Cart/Train Dispenser → Create Deployer / Dispenser
        (block, 8): BlockMapping(block, 8, "minecraft:dispenser", True, "generic_machine", "Cart Dispenser → Dispenser (lossy: no railcraft cart spawning logic)"),
        (block, 9): BlockMapping(block, 9, "minecraft:dispenser", True, "generic_machine", "Train Dispenser → Dispenser"),

        # RF Loader/Unloader → Mekanism Universal Cable
        (block, 10): BlockMapping(block, 10, "mekanism:basic_universal_cable", False, "identity", "RF Loader → Mekanism Universal Cable"),
        (block, 11): BlockMapping(block, 11, "mekanism:basic_universal_cable", False, "identity", "RF Unloader → Mekanism Universal Cable"),
    }


def _make_machine_delta_mappings() -> dict[tuple[str, int], BlockMapping]:
    """Maszyny Delta → placeholder / redstone."""
    block = "railcraft.machine.delta"
    return {
        (block, 0): BlockMapping(block, 0, "minecraft:redstone_wire", False, "identity", "Shunting Wire → Redstone Dust (lossy: no electric shunting)"),
        (block, 1): BlockMapping(block, 1, PLACEHOLDER, True, "placeholder", "Spawner Refill → placeholder (no equivalent in 1.18.2)"),
    }


def _make_machine_epsilon_mappings() -> dict[tuple[str, int], BlockMapping]:
    """Maszyny Epsilon → IE / Mekanism / placeholder."""
    block = "railcraft.machine.epsilon"
    return {
        # Electric Feeder → IE Connector
        (block, 0): BlockMapping(block, 0, "immersiveengineering:connector_lv", False, "identity", "Electric Feeder → IE LV Connector (lossy: different power system)"),
        (block, 1): BlockMapping(block, 1, "immersiveengineering:connector_lv", False, "identity", "Admin Electric Feeder → IE LV Connector"),

        # Admin Steam Producer → placeholder
        (block, 2): BlockMapping(block, 2, PLACEHOLDER, True, "placeholder", "Admin Steam Producer → placeholder (admin-only block)"),

        # Force Track Emitter → placeholder
        (block, 3): BlockMapping(block, 3, PLACEHOLDER, True, "placeholder", "Force Track Emitter → placeholder (no equivalent)"),

        # Flux Transformer → Mekanism Energy Cube
        (block, 4): BlockMapping(block, 4, "mekanism:basic_energy_cube", True, "energy_storage", "Flux Transformer → Mekanism Basic Energy Cube (lossy: RF↔EU conversion lost)"),

        # Engraving Bench → placeholder (brak modu emblematów w 1.18.2)
        (block, 5): BlockMapping(block, 5, PLACEHOLDER, True, "placeholder", "Engraving Bench → placeholder (no emblem system in 1.18.2)"),
    }


def _make_signal_mappings() -> dict[tuple[str, int], BlockMapping]:
    """Sygnały → Steam'n'Rails / vanilla redstone / placeholder."""
    block = "railcraft.signal"
    return {
        # Semafory Block Signal → Steam'n'Rails Semaphore
        (block, 1): BlockMapping(block, 1, "railways:semaphore", True, "signal", "Dual-Head Block Signal → Steam'n'Rails Semaphore (approximate)"),
        (block, 3): BlockMapping(block, 3, "railways:semaphore", True, "signal", "Block Signal → Steam'n'Rails Semaphore"),
        (block, 11): BlockMapping(block, 11, "railways:semaphore", True, "signal", "Distant Signal → Steam'n'Rails Semaphore"),
        (block, 12): BlockMapping(block, 12, "railways:semaphore", True, "signal", "Dual-Head Distant Signal → Steam'n'Rails Semaphore"),

        # Switch Motor → Create Clutch / Gearbox
        (block, 2): BlockMapping(block, 2, "create:clutch", True, "redstone_device", "Switch Motor → Create Clutch (lossy: no rail switching)"),
        (block, 5): BlockMapping(block, 5, "create:clutch", True, "redstone_device", "Routing Switch Motor → Create Clutch"),

        # Switch Lever → Create Clutch / Lever
        (block, 4): BlockMapping(block, 4, "minecraft:lever", False, "identity", "Switch Lever → Lever"),

        # Boxy (Controller, Receiver, Capacitor, Sequencer, Interlock, Analog) → redstone components
        (block, 6): BlockMapping(block, 6, "minecraft:repeater", True, "redstone_device", "Sequencer Box → Repeater (lossy: no sequencing)"),
        (block, 7): BlockMapping(block, 7, "minecraft:comparator", True, "redstone_device", "Capacitor Box → Comparator (lossy: no signal storage)"),
        (block, 8): BlockMapping(block, 8, "minecraft:comparator", True, "redstone_device", "Receiver Box → Comparator (lossy: no wireless receiving)"),
        (block, 9): BlockMapping(block, 9, "minecraft:comparator", True, "redstone_device", "Controller Box → Comparator (lossy: no wireless control)"),
        (block, 10): BlockMapping(block, 10, "minecraft:comparator", True, "redstone_device", "Analog Controller Box → Comparator (approximate: analog redstone)"),
        (block, 0): BlockMapping(block, 0, "minecraft:comparator", True, "redstone_device", "Interlock Box → Comparator (lossy: no interlocking)"),

        # Signal Block Relay → Repeater
        (block, 13): BlockMapping(block, 13, "minecraft:repeater", True, "redstone_device", "Signal Block Relay → Repeater (lossy: no block signal logic)"),
    }


def _make_detector_mappings() -> dict[tuple[str, int], BlockMapping]:
    """Detektory → Observer (lossy)."""
    block = "railcraft.detector"
    return {
        (block, meta): BlockMapping(
            block, meta, "minecraft:observer", False, "identity",
            f"Detector {meta} → Observer (lossy: no cart-specific detection)",
            {"facing": "north"},
        )
        for meta in range(17)
    }


def _make_other_mappings() -> dict[tuple[str, int | None], BlockMapping]:
    """Pozostałe bloki."""
    return {
        # Residual Heat → usunięcie (brak targetu, ignorowane)
        ("railcraft.residual.heat", 0): BlockMapping(
            "railcraft.residual.heat", 0, "minecraft:air", False, "ignored",
            "Residual Heat (RCHiddenTile) → air (ignored per user request)"
        ),
        # Frame → placeholder
        ("railcraft.frame", 0): BlockMapping(
            "railcraft.frame", 0, PLACEHOLDER, False, "placeholder", "Track Kit Frame → placeholder"
        ),
        # Cube blocks (dekoracyjne) → placeholder / concrete
        ("railcraft.cube", 0): BlockMapping("railcraft.cube", 0, "minecraft:stone", False, "identity", "Railcraft Cube → Stone (decorative fallback)"),
        ("railcraft.cube", 2): BlockMapping("railcraft.cube", 2, "minecraft:iron_block", False, "identity", "Railcraft Steel Cube → Iron Block (decorative fallback)"),
        # Ores → vanilla / thermal ores (jeśli istnieją)
        ("railcraft.ore", 0): BlockMapping("railcraft.ore", 0, "minecraft:stone", False, "identity", "Railcraft Ore → Stone (ores processed during world gen, no TE)"),
        # Lanterns → vanilla lantern
        ("railcraft.lantern.stone", 0): BlockMapping("railcraft.lantern.stone", 0, "minecraft:lantern", False, "identity", "Railcraft Stone Lantern → Lantern"),
        ("railcraft.lantern.metal", 0): BlockMapping("railcraft.lantern.metal", 0, "minecraft:lantern", False, "identity", "Railcraft Metal Lantern → Lantern"),
        # Anvil → vanilla anvil
        ("railcraft.anvil", 0): BlockMapping("railcraft.anvil", 0, "minecraft:anvil", False, "identity", "Railcraft Anvil → Anvil"),
        # Firestone recharge → placeholder
        ("railcraft.firestone.recharge", 0): BlockMapping("railcraft.firestone.recharge", 0, PLACEHOLDER, False, "placeholder", "Firestone Recharge → placeholder (no equivalent)"),
        # Slabs / Stairs → FramedBlocks (lossy: material lost, orientation partially preserved)
        ("railcraft.slab", None): BlockMapping(
            "railcraft.slab", None, "framedblocks:framed_slab", True, "slab",
            "Railcraft Slab → Framed Slab (lossy: material lost)"
        ),
        ("railcraft.stair", None): BlockMapping(
            "railcraft.stair", None, "framedblocks:framed_stairs", True, "stair",
            "Railcraft Stair → Framed Stairs (lossy: material lost)"
        ),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Agregacja wszystkich mapowań
# ──────────────────────────────────────────────────────────────────────────────

STATIC_MAPPINGS: dict[tuple[str, int | None], BlockMapping] = {}
STATIC_MAPPINGS.update(_make_track_mappings())
STATIC_MAPPINGS.update(_make_machine_alpha_mappings())
STATIC_MAPPINGS.update(_make_machine_beta_mappings())
STATIC_MAPPINGS.update(_make_machine_gamma_mappings())
STATIC_MAPPINGS.update(_make_machine_delta_mappings())
STATIC_MAPPINGS.update(_make_machine_epsilon_mappings())
STATIC_MAPPINGS.update(_make_signal_mappings())
STATIC_MAPPINGS.update(_make_detector_mappings())
STATIC_MAPPINGS.update(_make_other_mappings())


def get_mapping(block_id: str, metadata: int) -> BlockMapping | None:
    """Pobierz mapowanie dla pary (block_id, metadata)."""
    key = (block_id, metadata)
    if key in STATIC_MAPPINGS:
        return STATIC_MAPPINGS[key]
    # Fallback: sprawdź czy istnieje mapping bez metadanych (None)
    key_any = (block_id, None)
    if key_any in STATIC_MAPPINGS:
        return STATIC_MAPPINGS[key_any]
    return None


def is_railcraft_block(block_id: str) -> bool:
    """Sprawdź czy blok należy do Railcrafta."""
    return block_id.startswith("railcraft.")


# Statystyki
_placeholder_count = sum(1 for m in STATIC_MAPPINGS.values() if m.target_block_id == PLACEHOLDER)
_total_count = len(STATIC_MAPPINGS)
CONVERSION_RATE = 1.0 - (_placeholder_count / _total_count) if _total_count else 0.0
