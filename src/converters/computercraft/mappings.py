"""Mapowania bloków i tile entities ComputerCraft 1.7.10 → CC:Tweaked 1.18.2."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BlockMapping:
    source_block_id: str
    metadata: int | None
    target_block_id: str
    target_blockentity_id: str | None = None
    notes: str = ""


# ---------------------------------------------------------------------------
# Pomocnicze słowniki metadata → podtyp dla 1.7.10
# ---------------------------------------------------------------------------

# computercraft:computer — meta & 0x7 = facing, meta >= 8 = advanced
COMPUTER_FAMILY_BY_META = {
    "normal": range(0, 8),
    "advanced": range(8, 16),
}

# computercraft:peripheral — meta → typ
PERIPHERAL_BY_META = {
    0: "wireless_modem_down",
    1: "wireless_modem_up",
    2: "disk_drive",
    3: "disk_drive",
    4: "disk_drive",
    5: "disk_drive",
    6: "wireless_modem",
    7: "wireless_modem",
    8: "wireless_modem",
    9: "wireless_modem",
    10: "monitor",
    11: "printer",
    12: "advanced_monitor",
    13: "speaker",
}

# computercraft:cable — meta → typ
CABLE_BY_META = {
    **{i: "wired_modem" for i in range(0, 6)},
    **{i: "wired_modem_with_cable" for i in range(6, 12)},
    13: "cable_only",
}


# ---------------------------------------------------------------------------
# Pełne mapowania (source_block_id, metadata) → BlockMapping
# ---------------------------------------------------------------------------

_STATIC: list[BlockMapping] = [
    # --- computercraft:computer ---
    # Normal (meta 0-7)
    *[
        BlockMapping(
            "computercraft:computer", meta,
            "computercraft:computer_normal",
            "computercraft:computer_normal",
            "Normal computer",
        )
        for meta in range(0, 8)
    ],
    # Advanced (meta 8-15)
    *[
        BlockMapping(
            "computercraft:computer", meta,
            "computercraft:computer_advanced",
            "computercraft:computer_advanced",
            "Advanced computer",
        )
        for meta in range(8, 16)
    ],

    # --- computercraft:command_computer ---
    BlockMapping(
        "computercraft:command_computer", 0,
        "computercraft:computer_command",
        "computercraft:computer_command",
        "Command computer",
    ),

    # --- computercraft:peripheral (meta-driven) ---
    # Disk Drive (meta 2-5)
    *[
        BlockMapping(
            "computercraft:peripheral", meta,
            "computercraft:disk_drive",
            "computercraft:disk_drive",
            "Disk drive",
        )
        for meta in range(2, 6)
    ],
    # Wireless Modem down (meta 0)
    BlockMapping(
        "computercraft:peripheral", 0,
        "computercraft:wireless_modem_normal",
        "computercraft:wireless_modem_normal",
        "Wireless modem facing down",
    ),
    # Wireless Modem up (meta 1)
    BlockMapping(
        "computercraft:peripheral", 1,
        "computercraft:wireless_modem_normal",
        "computercraft:wireless_modem_normal",
        "Wireless modem facing up",
    ),
    # Wireless Modem horizontal (meta 6-9)
    *[
        BlockMapping(
            "computercraft:peripheral", meta,
            "computercraft:wireless_modem_normal",
            "computercraft:wireless_modem_normal",
            "Wireless modem horizontal",
        )
        for meta in range(6, 10)
    ],
    # Monitor (meta 10)
    BlockMapping(
        "computercraft:peripheral", 10,
        "computercraft:monitor_normal",
        "computercraft:monitor_normal",
        "Monitor",
    ),
    # Printer (meta 11)
    BlockMapping(
        "computercraft:peripheral", 11,
        "computercraft:printer",
        "computercraft:printer",
        "Printer",
    ),
    # Advanced Monitor (meta 12)
    BlockMapping(
        "computercraft:peripheral", 12,
        "computercraft:monitor_advanced",
        "computercraft:monitor_advanced",
        "Advanced monitor",
    ),
    # Speaker (meta 13)
    BlockMapping(
        "computercraft:peripheral", 13,
        "computercraft:speaker",
        "computercraft:speaker",
        "Speaker",
    ),

    # --- computercraft:advanced_modem ---
    BlockMapping(
        "computercraft:advanced_modem", 0,
        "computercraft:wireless_modem_advanced",
        "computercraft:wireless_modem_advanced",
        "Advanced (ender) wireless modem",
    ),

    # --- computercraft:cable (meta-driven) ---
    # Wired modem only (meta 0-5)
    *[
        BlockMapping(
            "computercraft:cable", meta,
            "computercraft:cable",
            "computercraft:cable",
            "Wired modem without cable",
        )
        for meta in range(0, 6)
    ],
    # Wired modem + cable (meta 6-11)
    *[
        BlockMapping(
            "computercraft:cable", meta,
            "computercraft:cable",
            "computercraft:cable",
            "Wired modem with cable",
        )
        for meta in range(6, 12)
    ],
    # Cable only (meta 13)
    BlockMapping(
        "computercraft:cable", 13,
        "computercraft:cable",
        "computercraft:cable",
        "Cable only",
    ),

    # --- computercraft:turtle ---
    BlockMapping(
        "computercraft:turtle", 0,
        "computercraft:turtle_normal",
        "computercraft:turtle_normal",
        "Normal turtle",
    ),
    # --- computercraft:turtle_expanded ---
    BlockMapping(
        "computercraft:turtle_expanded", 0,
        "computercraft:turtle_normal",
        "computercraft:turtle_normal",
        "Expanded turtle → normal turtle (expanded variant removed in 1.18.2)",
    ),
    # --- computercraft:turtle_advanced ---
    BlockMapping(
        "computercraft:turtle_advanced", 0,
        "computercraft:turtle_advanced",
        "computercraft:turtle_advanced",
        "Advanced turtle",
    ),
]

STATIC_MAPPINGS: dict[tuple[str, int], BlockMapping] = {}
for m in _STATIC:
    STATIC_MAPPINGS[(m.source_block_id, m.metadata if m.metadata is not None else 0)] = m

# ---------------------------------------------------------------------------
# Mapowanie TE ID (1.7.10 exact strings) → (block_id, metadata)
# UWAGA: W 1.7.10 registry stringi mają SPACJĘ wokół dwukropka!
# ---------------------------------------------------------------------------

TE_ID_TO_BLOCK_META: dict[str, tuple[str, int]] = {
    # Z prefiksem i spacjami (dokładne registry stringi z 1.7.10)
    "computercraft : computer": ("computercraft:computer", 0),
    "computercraft : diskdrive": ("computercraft:peripheral", 2),
    "computercraft : wirelessmodem": ("computercraft:peripheral", 6),
    "computercraft : monitor": ("computercraft:peripheral", 10),
    "computercraft : ccprinter": ("computercraft:peripheral", 11),
    "computercraft : wiredmodem": ("computercraft:cable", 0),
    "computercraft : command_computer": ("computercraft:command_computer", 0),
    "computercraft : advanced_modem": ("computercraft:advanced_modem", 0),
    "computercraft : speaker": ("computercraft:peripheral", 13),
    "computercraft : turtle": ("computercraft:turtle", 0),
    "computercraft : turtleex": ("computercraft:turtle_expanded", 0),
    "computercraft : turtleadv": ("computercraft:turtle_advanced", 0),
    # Bez prefiksu (jak się czasem zdarza w NBT z routera)
    "computer": ("computercraft:computer", 0),
    "monitor": ("computercraft:peripheral", 10),
    "turtle": ("computercraft:turtle", 0),
    "drive": ("computercraft:peripheral", 2),
    "speaker": ("computercraft:peripheral", 13),
    "ccprinter": ("computercraft:peripheral", 11),
    "wirelessmodem": ("computercraft:peripheral", 6),
    "wiredmodem": ("computercraft:cable", 0),
    "command_computer": ("computercraft:command_computer", 0),
    "advanced_modem": ("computercraft:advanced_modem", 0),
    "turtleex": ("computercraft:turtle_expanded", 0),
    "turtleadv": ("computercraft:turtle_advanced", 0),
}

# TE IDs które dzielą block_id z innymi i wymagają metadata z NBT lub blockstate
_TE_IDS_WITH_SHARED_BLOCK: frozenset[str] = frozenset({
    "computercraft : computer",
    "computercraft : diskdrive",
    "computercraft : wirelessmodem",
    "computercraft : monitor",
    "computercraft : ccprinter",
    "computercraft : wiredmodem",
    "computercraft : speaker",
})

ALL_COMPUTERCRAFT_TE_IDS: frozenset[str] = frozenset(TE_ID_TO_BLOCK_META.keys())


# ---------------------------------------------------------------------------
# Funkcje pomocnicze
# ---------------------------------------------------------------------------

def get_block_mapping(block_id_1710: str, metadata: int = 0) -> BlockMapping | None:
    """Zwróć mapowanie na podstawie block_id i metadata."""
    key = (block_id_1710, metadata)
    return STATIC_MAPPINGS.get(key)


def get_mapping_for_te_id(te_id: str, metadata: int = 0) -> BlockMapping | None:
    """Zwróć mapowanie na podstawie TE ID (np. 'computercraft : computer').

    Dla TE które dzielą block_id (np. peripheral) używamy przekazanego metadata.
    """
    if te_id not in TE_ID_TO_BLOCK_META:
        return None
    block_id, default_meta = TE_ID_TO_BLOCK_META[te_id]
    meta = metadata if te_id in _TE_IDS_WITH_SHARED_BLOCK else default_meta
    return get_block_mapping(block_id, meta)


def is_computercraft_te_id(te_id: str) -> bool:
    """Czy te_id należy do ComputerCraft (1.7.10)?"""
    return te_id in ALL_COMPUTERCRAFT_TE_IDS


def is_computercraft_block_id(block_id: str) -> bool:
    """Czy block_id należy do ComputerCraft (1.7.10)?"""
    if block_id.startswith("computercraft:"):
        return True
    if block_id in ALL_COMPUTERCRAFT_TE_IDS:
        return True
    return False
