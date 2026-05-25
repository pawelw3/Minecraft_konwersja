"""Mapowania blokow Big Reactors 1.7.10 -> Bigger Reactors 1.18.2."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BlockMapping:
    source_block_id: str
    metadata: int | None
    target_block_id: str
    has_block_entity: bool = False
    nbt_converter: str = "identity"
    notes: str = ""


# ---------------------------------------------------------------------------
# Pomocnicze slowniki metadata -> podtyp
# ---------------------------------------------------------------------------

REACTOR_PART_BY_META = {
    0: "casing",
    1: "controller",
    2: "control_rod",
    3: "power_tap",
    4: "access_port",
    5: "coolant_port",
    6: "rednet_port",
    7: "computer_port",
}

TURBINE_PART_BY_META = {
    0: "housing",
    1: "controller",
    2: "power_tap",
    3: "fluid_port",
    4: "bearing",
    5: "computer_port",
}

METAL_BLOCK_BY_META = {
    0: "yellorium",
    1: "cyanite",
    2: "graphite",
    3: "blutonium",
    4: "ludicrite",
}

MULTIBLOCK_GLASS_BY_META = {
    0: "reactor",
    1: "turbine",
}

TURBINE_ROTOR_BY_META = {
    0: "shaft",
    1: "blade",
}

# ---------------------------------------------------------------------------
# Pelne mapowania (source_block_id, metadata) -> BlockMapping
# Uwzgledniamy zarowno nazwy z prefiksem "BigReactors:" jak i same TE ID
# (bez prefixu), poniewaz router moze przekazac te_id jako block_id_1710.
# ---------------------------------------------------------------------------

_STATIC: list[BlockMapping] = [
    # --- Rudy / surowce ---
    BlockMapping("BigReactors:YelloriteOre", 0, "biggerreactors:uranium_ore", False, "identity", "Yellorite -> Uranium"),
    # Yellorite ore bez prefixu (rzadko, ale na wszelki wypadek)
    BlockMapping("YelloriteOre", 0, "biggerreactors:uranium_ore", False, "identity", "Yellorite -> Uranium"),

    # --- Metal blocks ---
    BlockMapping("BigReactors:BRMetalBlock", 0, "biggerreactors:uranium_block", False, "identity", "Yellorium -> Uranium"),
    BlockMapping("BigReactors:BRMetalBlock", 1, "biggerreactors:cyanite_block", False, "identity"),
    BlockMapping("BigReactors:BRMetalBlock", 2, "biggerreactors:graphite_block", False, "identity"),
    BlockMapping("BigReactors:BRMetalBlock", 3, "biggerreactors:blutonium_block", False, "identity"),
    BlockMapping("BigReactors:BRMetalBlock", 4, "biggerreactors:ludicrite_block", False, "identity"),

    # --- Reactor parts ---
    BlockMapping("BigReactors:BRReactorPart", 0, "biggerreactors:reactor_casing", True, "multiblock_reactor"),
    BlockMapping("BigReactors:BRReactorPart", 1, "biggerreactors:reactor_terminal", True, "multiblock_reactor"),
    BlockMapping("BigReactors:BRReactorPart", 2, "biggerreactors:reactor_control_rod", True, "multiblock_reactor"),
    BlockMapping("BigReactors:BRReactorPart", 3, "biggerreactors:reactor_power_tap", True, "multiblock_reactor"),
    BlockMapping("BigReactors:BRReactorPart", 4, "biggerreactors:reactor_access_port", True, "multiblock_reactor_accessport"),
    BlockMapping("BigReactors:BRReactorPart", 5, "biggerreactors:reactor_coolant_port", True, "multiblock_reactor"),
    BlockMapping("BigReactors:BRReactorPart", 6, "biggerreactors:reactor_redstone_port", True, "multiblock_reactor",
                 "RedNet Port z 1.7.10 nie istnieje w 1.18.2; zastapiono Redstone Portem"),
    BlockMapping("BigReactors:BRReactorPart", 7, "biggerreactors:reactor_computer_port", True, "multiblock_reactor"),

    # --- Reactor glass ---
    BlockMapping("BigReactors:BRMultiblockGlass", 0, "biggerreactors:reactor_glass", True, "multiblock_reactor"),
    BlockMapping("BigReactors:BRMultiblockGlass", 1, "biggerreactors:turbine_glass", True, "multiblock_turbine"),

    # --- Reactor redstone port (osobny blok) ---
    BlockMapping("BigReactors:BRReactorRedstonePort", 0, "biggerreactors:reactor_redstone_port", True, "multiblock_reactor"),

    # --- Fuel rod ---
    BlockMapping("BigReactors:YelloriumFuelRod", 0, "biggerreactors:reactor_fuel_rod", True, "multiblock_reactor"),

    # --- Turbine parts ---
    BlockMapping("BigReactors:BRTurbinePart", 0, "biggerreactors:turbine_casing", True, "multiblock_turbine"),
    BlockMapping("BigReactors:BRTurbinePart", 1, "biggerreactors:turbine_terminal", True, "multiblock_turbine"),
    BlockMapping("BigReactors:BRTurbinePart", 2, "biggerreactors:turbine_power_tap", True, "multiblock_turbine"),
    BlockMapping("BigReactors:BRTurbinePart", 3, "biggerreactors:turbine_fluid_port", True, "multiblock_turbine"),
    BlockMapping("BigReactors:BRTurbinePart", 4, "biggerreactors:turbine_rotor_bearing", True, "multiblock_turbine"),
    BlockMapping("BigReactors:BRTurbinePart", 5, "biggerreactors:turbine_computer_port", True, "multiblock_turbine"),

    # --- Turbine rotor parts ---
    BlockMapping("BigReactors:BRTurbineRotorPart", 0, "biggerreactors:turbine_rotor_shaft", True, "multiblock_turbine"),
    BlockMapping("BigReactors:BRTurbineRotorPart", 1, "biggerreactors:turbine_rotor_blade", True, "multiblock_turbine"),

    # --- Device (Cyanite Reprocessor) ---
    BlockMapping("BigReactors:BRDevice", 0, "biggerreactors:cyanite_reprocessor", True, "cyanite_reprocessor"),

    # --- Creative parts (brak bezposredniego odpowiednika; placeholder / skip) ---
    BlockMapping("BigReactors:BRMultiblockCreativePart", 0, "minecraft:air", False, "identity",
                 "Creative Coolant Port nie ma odpowiednika w BiggerReactors 1.18.2"),
    BlockMapping("BigReactors:BRMultiblockCreativePart", 1, "minecraft:air", False, "identity",
                 "Creative Steam Generator nie ma odpowiednika w BiggerReactors 1.18.2"),

    # --- Fluids ---
    BlockMapping("BigReactors:tile.bigreactors.yellorium.still", 0, "biggerreactors:liquid_uranium", False, "fluid",
                 "Yellorium fluid -> Liquid Uranium"),
    BlockMapping("BigReactors:tile.bigreactors.cyanite.still", 0, "minecraft:water", False, "fluid",
                 "Cyanite fluid nie ma odpowiednika; zastapiono woda jako placeholder"),
]

# Zbuduj slownik z lista powyzej
STATIC_MAPPINGS: dict[tuple[str, int], BlockMapping] = {}
for m in _STATIC:
    STATIC_MAPPINGS[(m.source_block_id, m.metadata if m.metadata is not None else 0)] = m

# ---------------------------------------------------------------------------
# Mapowanie TE ID (bez prefixu) -> (block_id, metadata)
# Uzywane gdy router przekazuje tylko te_id jako block_id_1710.
# ---------------------------------------------------------------------------

TE_ID_TO_BLOCK_META: dict[str, tuple[str, int]] = {
    # Reactor
    "BRReactorPart": ("BigReactors:BRReactorPart", 0),
    "BRReactorControlRod": ("BigReactors:BRReactorPart", 2),
    "BRReactorPowerTap": ("BigReactors:BRReactorPart", 3),
    "BRReactorAccessPort": ("BigReactors:BRReactorPart", 4),
    "BRReactorCoolantPort": ("BigReactors:BRReactorPart", 5),
    "BRReactorRedNetPort": ("BigReactors:BRReactorPart", 6),
    "BRReactorComputerPort": ("BigReactors:BRReactorPart", 7),
    "BRReactorRedstonePort": ("BigReactors:BRReactorRedstonePort", 0),
    "BRReactorGlass": ("BigReactors:BRMultiblockGlass", 0),
    "BRFuelRod": ("BigReactors:YelloriumFuelRod", 0),
    # Turbine
    "BRTurbinePart": ("BigReactors:BRTurbinePart", 0),
    "BRTurbinePowerTap": ("BigReactors:BRTurbinePart", 2),
    "BRTurbineFluidPort": ("BigReactors:BRTurbinePart", 3),
    "BRTurbineComputerPort": ("BigReactors:BRTurbinePart", 5),
    "BRTurbineGlass": ("BigReactors:BRMultiblockGlass", 1),
    "BRTurbineRotorBearing": ("BigReactors:BRTurbinePart", 4),
    "BRTurbineRotorPart": ("BigReactors:BRTurbineRotorPart", 0),
    # Device
    "BRCyaniteReprocessor": ("BigReactors:BRDevice", 0),
    # Creative
    "BRReactorCreativeCoolantPort": ("BigReactors:BRMultiblockCreativePart", 0),
    "BRTurbineCreativeSteamGenerator": ("BigReactors:BRMultiblockCreativePart", 1),
}

# Dodatkowe mapowania "per TE id" z bezposrednim targetem (gdy nie da sie
# odgadnac block_id z metadata, np. BRReactorPart moze byc casingiem lub
# controllerm — wtedy metadata jest kluczowe).
# Powyzsze TE_ID_TO_BLOCK_META zaklada domyslne wartosci; funkcja
# get_mapping_for_te_id uzyje metadany z NBT jesli jest dostepna.

# Znane TE ID ktore moga wystapic bez block metadata
ALL_BIGREACTORS_TE_IDS: frozenset[str] = frozenset(TE_ID_TO_BLOCK_META.keys())


# ---------------------------------------------------------------------------
# Funkcje pomocnicze
# ---------------------------------------------------------------------------

def _normalize_block_id(block_id_1710: str) -> str:
    """Normalizuje ID bloku: jesli to znany TE ID bez prefixu, dodaje 'BigReactors:'."""
    if ":" in block_id_1710:
        return block_id_1710
    # Jesli to jeden z znanych TE ID, przeksztalc na pelny block_id
    if block_id_1710 in TE_ID_TO_BLOCK_META:
        full_id, _ = TE_ID_TO_BLOCK_META[block_id_1710]
        return full_id
    # Inaczej dodaj domyslny prefix
    return f"BigReactors:{block_id_1710}"


def get_block_mapping(block_id_1710: str, metadata: int = 0, nbt_1710: dict | None = None) -> BlockMapping | None:
    """Zwroc mapowanie na podstawie block_id i metadata."""
    normalized = _normalize_block_id(block_id_1710)
    key = (normalized, metadata)
    if key in STATIC_MAPPINGS:
        return STATIC_MAPPINGS[key]
    # Fallback: sprobuj bez normalizacji (jesli uzytkownik podal cos nietypowego)
    key2 = (block_id_1710, metadata)
    if key2 in STATIC_MAPPINGS:
        return STATIC_MAPPINGS[key2]
    return None


_TE_IDS_WITH_SHARED_BLOCK = frozenset({"BRReactorPart", "BRTurbinePart", "BRTurbineRotorPart"})


def get_mapping_for_te_id(te_id: str, metadata: int = 0, nbt_1710: dict | None = None) -> BlockMapping | None:
    """Zwroc mapowanie na podstawie TE ID (np. 'BRReactorPowerTap').

    Dla TE ktore dziela block_id z innymi (np. BRReactorPart moze byc casingiem
    lub controllerm) uzywamy przekazanego metadata. Dla unikalnych TE
    (np. BRReactorPowerTap) uzywamy domyslnego metadata z TE_ID_TO_BLOCK_META.
    """
    if te_id not in TE_ID_TO_BLOCK_META:
        return None
    block_id, default_meta = TE_ID_TO_BLOCK_META[te_id]
    if te_id in _TE_IDS_WITH_SHARED_BLOCK:
        meta = metadata
    else:
        meta = default_meta
    return get_block_mapping(block_id, meta, nbt_1710)


def is_bigreactors_block(block_id: str) -> bool:
    """Czy block_id nalezy do Big Reactors (1.7.10)?"""
    if block_id.startswith("BigReactors:"):
        return True
    if block_id in TE_ID_TO_BLOCK_META:
        return True
    return False


def is_bigreactors_te_id(te_id: str) -> bool:
    """Czy te_id nalezy do Big Reactors (1.7.10)?"""
    return te_id in ALL_BIGREACTORS_TE_IDS
