"""
Mapowania dla konwersji Backpack (Eydamos) 1.7.10 → Sophisticated Backpacks 1.18.2.

Źródła:
  - 1.7.10: ItemsBackpack.java, BackpackSave.java, ConfigurationBackpack.java
  - 1.18.2: Config.java, ModItems.java, BackpackWrapper.java
"""

from __future__ import annotations

# --- Kolory z Minecraft DyeColor (RGB int) ---
# Symuluje ColorHelper.getColor(DyeColor.getTextureDiffuseColors())
DYE_COLOR_RGB = {
    "white": 0xF9FFFE,
    "orange": 0xF9801D,
    "magenta": 0xC74EBD,
    "light_blue": 0x3AB3DA,
    "yellow": 0xFED83D,
    "lime": 0x80C71F,
    "pink": 0xF38BAA,
    "gray": 0x474F52,
    "light_gray": 0x9D9D97,
    "cyan": 0x169C9C,
    "purple": 0x8932B8,
    "blue": 0x3C44AA,
    "brown": 0x835432,
    "green": 0x5E7C16,
    "red": 0xB02E26,
    "black": 0x1D1D21,
}

# --- Domyślne kolory SB ---
DEFAULT_CLOTH_COLOR = 13394234
DEFAULT_BORDER_COLOR = 6434330

# --- Domyślne sloty z Config.java (SB 1.18.2) ---
# Format: item_id -> (inventory_slots, upgrade_slots)
SB_TIER_DEFAULTS = {
    "sophisticatedbackpacks:backpack": (27, 1),
    "sophisticatedbackpacks:copper_backpack": (45, 1),
    "sophisticatedbackpacks:iron_backpack": (54, 2),
    "sophisticatedbackpacks:gold_backpack": (81, 3),
    "sophisticatedbackpacks:diamond_backpack": (108, 5),
    "sophisticatedbackpacks:netherite_backpack": (120, 7),
}

# --- Kandydaci tierów SB (rosnąco po slotach) ---
SB_TIER_CANDIDATES = [
    ("sophisticatedbackpacks:backpack", 27),
    ("sophisticatedbackpacks:copper_backpack", 45),
    ("sophisticatedbackpacks:iron_backpack", 54),
    ("sophisticatedbackpacks:gold_backpack", 81),
    ("sophisticatedbackpacks:diamond_backpack", 108),
    ("sophisticatedbackpacks:netherite_backpack", 120),
]

# --- Tablice z ItemsBackpack.java ---
BACKPACK_TIERS = ["", "medium", "big"]
BACKPACK_COLORS = [
    "", "black", "red", "green", "brown", "blue", "purple", "cyan",
    "lightGray", "gray", "pink", "lime", "yellow", "lightBlue", "magenta",
    "orange", "white", "ender",
]

ENDERBACKPACK_DAMAGE = 31999


def map_tier_1710_to_sb_item_id(
    source_size: int,
    is_ender: bool = False,
    is_workbench: bool = False,
) -> str:
    """
    Mapuje rozmiar plecaka 1.7.10 na docelowy item ID w SB 1.18.2.
    Wybiera najmniejszy tier który pomieści wszystkie itemy.
    """
    if is_ender:
        # Ender backpack → iron_backpack (27 slotów, podobnie jak ender)
        return "sophisticatedbackpacks:iron_backpack"

    for item_id, slots in SB_TIER_CANDIDATES:
        if slots >= source_size:
            return item_id

    return "sophisticatedbackpacks:netherite_backpack"


def map_color_name_to_rgb(color_name: str) -> tuple[int, int]:
    """
    Mapuje nazwę koloru z moda Eydamos na RGB clothColor + borderColor.
    Dla prostoty oba kolory są takie same (jak po użyciu jednego dye).
    """
    if not color_name:
        return DEFAULT_CLOTH_COLOR, DEFAULT_BORDER_COLOR

    # Mapowanie nazw Eydamos → DyeColor vanilla
    dye_name = _eydamos_color_to_dye(color_name)
    if not dye_name:
        return DEFAULT_CLOTH_COLOR, DEFAULT_BORDER_COLOR

    rgb = DYE_COLOR_RGB.get(dye_name, DEFAULT_CLOTH_COLOR)
    return rgb, rgb


def _eydamos_color_to_dye(color_name: str) -> str:
    mapping = {
        "black": "black",
        "red": "red",
        "green": "green",
        "brown": "brown",
        "blue": "blue",
        "purple": "purple",
        "cyan": "cyan",
        "lightGray": "light_gray",
        "gray": "gray",
        "pink": "pink",
        "lime": "lime",
        "yellow": "yellow",
        "lightBlue": "light_blue",
        "magenta": "magenta",
        "orange": "orange",
        "white": "white",
    }
    return mapping.get(color_name, "")


def compute_size_from_damage(damage: int, slots_s: int = 27, slots_l: int = 54) -> int:
    """
    Symuluje logikę BackpackSave.initialize() do obliczenia rozmiaru.
    """
    tier = damage // 100 if damage // 100 < 3 else 0
    meta = damage % 100

    if meta == 99:
        return 27
    elif meta < 17 and tier == 2:
        return slots_l
    elif meta < 17 and tier == 0:
        return slots_s
    elif meta == 17 and tier == 0:
        return 9
    elif meta == 17 and tier == 2:
        return 18
    return slots_s


def compute_type_from_id(item_id: str) -> int:
    """BackpackUtil.getType(ItemStack)"""
    if item_id == "Backpack:backpack":
        return 1
    if item_id == "Backpack:workbenchbackpack":
        return 2
    return 0


def get_color_name_from_damage(damage: int) -> str:
    """Zwraca nazwę koloru z damage/meta."""
    meta = damage % 100
    if 0 <= meta <= 17:
        return BACKPACK_COLORS[meta]
    return ""


def is_ender_backpack(damage: int) -> bool:
    return damage == ENDERBACKPACK_DAMAGE or (damage % 100) == 99


def is_workbench_backpack(item_id: str, damage: int) -> bool:
    return item_id == "Backpack:workbenchbackpack" or (item_id == "Backpack:backpack" and damage % 100 == 17)
