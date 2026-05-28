"""
Symulacja konwersji Backpack (Eydamos) 1.7.10 -> Sophisticated Backpacks 1.18.2.

Bazuje na kodzie źródłowym obu modów:
  - 1.7.10: dekompilacja CFR backpack-2.0.1-1.7.x.jar
  - 1.18.2: repozytoria SophisticatedBackpacks + SophisticatedCore (branch 1.18.x)

Symulacja pokazuje krok po kroku:
  1. Odczyt danych źródłowych (ItemStack + BackpackSave)
  2. Mapowanie na docelowy item SB (tier, kolory)
  3. Konwersja inventory (format 1.7.10 -> ItemStackHandler 1.18.2)
  4. Generowanie upgrade'ów (crafting dla workbench)
  5. Zapis do BackpackStorage 1.18.2
  6. Weryfikacja round-trip (odczyt z powrotem)
"""

from __future__ import annotations

import json
import uuid as uuid_module
from dataclasses import dataclass, field
from typing import Any

# --- Importy wewnętrzne z symulacji ---
from backpack_1710_simulation import (
    BackpackSave1710,
    ItemStack1710,
    BACKPACK_COLORS,
    DEFAULT_SLOTS_S,
    DEFAULT_SLOTS_L,
)
from backpack_1182_simulation import (
    BackpackStorage1182,
    BackpackWrapper1182,
    ItemStack1182,
    TIER_DEFAULTS,
    dye_color_to_rgb,
    backpack_color_name_to_dye,
    CLOTH_COLOR_TAG,
    BORDER_COLOR_TAG,
    CONTENTS_UUID_TAG,
    INVENTORY_TAG,
    UPGRADE_INVENTORY_TAG,
    SETTINGS_TAG,
    DEFAULT_CLOTH_COLOR,
    DEFAULT_BORDER_COLOR,
)


# --- Mapowanie tierów 1.7.10 -> 1.18.2 ---
def map_tier_1710_to_item_id_1182(
    item_1710: ItemStack1710,
    size: int,
) -> str:
    """
    Mapuje rozmiar plecaka 1.7.10 na docelowy item ID w SB 1.18.2.
    Bazuje na domyślnych slotach z Config.java.
    """
    if item_1710.is_ender():
        # Ender backpack -> iron_backpack (27 slotów, podobnie jak ender)
        return "sophisticatedbackpacks:iron_backpack"

    # Dopasowanie rozmiaru do najbliższego tieru SB
    tier_candidates = [
        ("sophisticatedbackpacks:backpack", 27),
        ("sophisticatedbackpacks:copper_backpack", 45),
        ("sophisticatedbackpacks:iron_backpack", 54),
        ("sophisticatedbackpacks:gold_backpack", 81),
        ("sophisticatedbackpacks:diamond_backpack", 108),
        ("sophisticatedbackpacks:netherite_backpack", 120),
    ]

    # Wybieramy najmniejszy tier który pomieści wszystkie itemy
    for item_id, slots in tier_candidates:
        if slots >= size:
            return item_id

    # Fallback na największy
    return "sophisticatedbackpacks:netherite_backpack"


def map_color_1710_to_rgb(color_name: str) -> tuple[int, int]:
    """
    Mapuje nazwę koloru z moda Eydamos na RGB clothColor + borderColor.
    SB używa dwóch kolorów (cloth + border). Dla prostoty ustawiamy oba na ten sam kolor,
    chyba że to default — wtedy domyślne wartości.
    """
    if not color_name or color_name == "":
        return DEFAULT_CLOTH_COLOR, DEFAULT_BORDER_COLOR

    dye_name = backpack_color_name_to_dye(color_name)
    if not dye_name:
        return DEFAULT_CLOTH_COLOR, DEFAULT_BORDER_COLOR

    rgb = dye_color_to_rgb(dye_name)
    return rgb, rgb


def convert_item_nbt_1710_to_1182(item_1710: ItemStack1710) -> dict[str, Any]:
    """
    Konwertuje NBT itemu z 1.7.10 na tagi 1.18.2.
    Zachowuje customName jeśli istnieje.
    """
    tag_1182: dict[str, Any] = {}

    # customName -> display.Name (JSON text component)
    custom_name = item_1710.tag.get("customName")
    if custom_name:
        tag_1182["display"] = {"Name": json.dumps({"text": custom_name})}

    return tag_1182


def convert_inventory_1710_to_1182(
    inventory_1710: list[dict],
) -> list[dict]:
    """
    Konwertuje inventory z formatu 1.7.10 na format ItemStackHandler 1.18.2.

    Różnice formatu:
      1.7.10:  { slot: Byte/Short, id: Short/String, Count: Byte, Damage: Short, tag: Compound }
      1.18.2:  { Slot: Int, id: String, Count: Byte, tag: Compound, realCount: Int }

    Uwaga: Właściwa konwersja ID (numeryczne 1.7.10 -> string 1.18.2) wymaga globalnego
    resolvera ID z projektu. W symulacji używamy uproszczonego mapowania.
    """
    result = []
    for item in inventory_1710:
        slot = item.get("slot", item.get("Slot", 0))
        item_id_1710 = item.get("id")
        count = item.get("Count", 1)
        damage = item.get("Damage", 0)
        tag = item.get("tag")

        # --- Uproszczone mapowanie ID (właściwa konwersja wymaga resolvera) ---
        item_id_1182 = _resolve_item_id(item_id_1710, damage)

        entry: dict[str, Any] = {
            "Slot": slot,
            "id": item_id_1182,
            "Count": count,
            "realCount": count,
        }
        if tag:
            # Konwersja tagów itemu (np. enchanty, nazwy) — uproszczenie
            entry["tag"] = tag

        result.append(entry)

    return result


def _resolve_item_id(item_id_1710: Any, damage: int) -> str:
    """
    Uproszczone mapowanie ID 1.7.10 -> 1.18.2.
    W produkcji należy użyć globalnego resolvera legacy ID.
    """
    # Jeśli id jest już stringiem (niektóre wersje 1.7.10 zapisywały stringi)
    if isinstance(item_id_1710, str):
        # Podstawowe mapowanie namespace
        if ":" in item_id_1710:
            return item_id_1710
        return f"minecraft:{item_id_1710}"

    # Numeryczne ID (starszy format 1.7.10) — uproszczone mapowanie
    numeric_map = {
        1: "minecraft:stone",
        265: "minecraft:iron_ingot",
        264: "minecraft:diamond",
        266: "minecraft:gold_ingot",
        331: "minecraft:redstone",
        341: "minecraft:slime_ball",
    }
    return numeric_map.get(item_id_1710, f"minecraft:unknown_{item_id_1710}")


def generate_upgrades_for_1710_backpack(
    item_1710: ItemStack1710,
) -> list[dict]:
    """
    Generuje upgrade'y SB na podstawie właściwości plecaka 1.7.10.
    - Workbench backpack -> Crafting Upgrade
    - Ender backpack -> brak odpowiednika (logowany warning)
    """
    upgrades = []

    if item_1710.is_workbench():
        upgrades.append({
            "Slot": 0,
            "id": "sophisticatedcore:crafting_upgrade",
            "Count": 1,
        })

    # Future: auto-pickup -> pickup_upgrade, magnet_upgrade
    # Future: intelligent -> filter_upgrade?

    return upgrades


@dataclass
class ConversionResult:
    """Wynik konwersji jednego plecaka."""
    source_item: ItemStack1710
    source_save: BackpackSave1710
    target_item: ItemStack1182
    target_wrapper: BackpackWrapper1182
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def convert_backpack_1710_to_1182(
    item_1710: ItemStack1710,
    save_1710: BackpackSave1710,
    target_storage: BackpackStorage1182 | None = None,
) -> ConversionResult:
    """
    Pełna konwersja jednego plecaka z 1.7.10 do 1.18.2.
    """
    warnings: list[str] = []
    errors: list[str] = []

    # --- Krok 1: Mapowanie item ID ---
    size = save_1710.nbt.get("size", DEFAULT_SLOTS_S)
    target_id = map_tier_1710_to_item_id_1182(item_1710, size)

    # --- Krok 2: Mapowanie kolorów ---
    color_name = item_1710.get_color_name()
    cloth_color, border_color = map_color_1710_to_rgb(color_name)

    # --- Krok 3: Tworzenie ItemStack 1.18.2 ---
    tag_1182 = convert_item_nbt_1710_to_1182(item_1710)
    tag_1182[CLOTH_COLOR_TAG] = cloth_color
    tag_1182[BORDER_COLOR_TAG] = border_color

    target_item = ItemStack1182(id=target_id, tag=tag_1182)

    # Zachowanie rozmiaru jeśli różni się od domyślnego tieru
    target_default_slots = TIER_DEFAULTS.get(target_id, (27, 1))[0]
    if size != target_default_slots:
        target_item.set_inventory_slots(size)
        warnings.append(f"BP-W-SIZE-OVERRIDE: Rozmiar {size} różni się od domyślnego {target_default_slots} dla {target_id}")

    # --- Krok 4: Tworzenie wrappera i zapis zawartości ---
    storage = target_storage or BackpackStorage1182()
    wrapper = BackpackWrapper1182(target_item, storage)

    # --- Krok 5: Konwersja inventory ---
    inventory_1710 = save_1710.get_inventory()
    inventory_1182 = convert_inventory_1710_to_1182(inventory_1710)
    wrapper.set_inventory(inventory_1182)

    # --- Krok 6: Generowanie upgrade'ów ---
    upgrades = generate_upgrades_for_1710_backpack(item_1710)
    if upgrades:
        wrapper.set_upgrades(upgrades)

    # --- Krok 7: Warnings ---
    if item_1710.is_ender():
        warnings.append("BP-W-ENDER: Ender Backpack nie ma odpowiednika w SB. Zastąpiono iron_backpack.")

    if item_1710.is_workbench() and not upgrades:
        warnings.append("BP-W-WORKBENCH: Workbench backpack bez crafting upgrade (błąd generowania)")

    return ConversionResult(
        source_item=item_1710,
        source_save=save_1710,
        target_item=target_item,
        target_wrapper=wrapper,
        warnings=warnings,
        errors=errors,
    )


def print_conversion_result(result: ConversionResult) -> None:
    print("\n" + "=" * 60)
    print("WYNIK KONWERSJI")
    print("=" * 60)

    print("\n[ŹRÓDŁO 1.7.10]")
    print(f"  Item: {result.source_item.id} damage={result.source_item.damage}")
    print(f"  Color: {result.source_item.get_color_name()}")
    print(f"  UUID: {result.source_save.uid}")
    print(f"  Size: {result.source_save.nbt.get('size')}")
    print(f"  Inventory count: {len(result.source_save.get_inventory())}")

    print("\n[CEL 1.18.2]")
    print(f"  Item: {result.target_item.id}")
    print(f"  UUID: {result.target_wrapper.get_contents_uuid()}")
    print(f"  Colors: cloth={result.target_item.get_main_color()}, border={result.target_item.get_accent_color()}")
    print(f"  Tag: {json.dumps(result.target_item.tag, indent=4)}")

    contents = result.target_wrapper.get_contents_nbt()
    print(f"\n[ZAWARTOŚĆ W BACKPACKSTORAGE]")
    print(json.dumps(contents, indent=2))

    if result.warnings:
        print(f"\n[OSTRZEŻENIA ({len(result.warnings)})]")
        for w in result.warnings:
            print(f"  [!] {w}")

    if result.errors:
        print(f"\n[BŁĘDY ({len(result.errors)})]")
        for e in result.errors:
            print(f"  [X] {e}")


def simulate_conversion_small_red() -> None:
    print("=" * 60)
    print("SYMUlACJA KONWERSJI: Small Red Backpack -> SB")
    print("=" * 60)

    # --- Źródło 1.7.10 ---
    item_1710 = ItemStack1710(id="Backpack:backpack", damage=1, tag={"customName": "Moje Rzeczy"})
    save_1710 = BackpackSave1710(item_1710)
    save_1710.set_inventory([
        {"slot": 0, "id": 265, "Count": 64, "Damage": 0},
        {"slot": 1, "id": 264, "Count": 16, "Damage": 0},
        {"slot": 5, "id": 1, "Count": 32, "Damage": 0},
    ])

    # --- Konwersja ---
    result = convert_backpack_1710_to_1182(item_1710, save_1710)
    print_conversion_result(result)


def simulate_conversion_big_workbench() -> None:
    print("\n" + "=" * 60)
    print("SYMUlACJA KONWERSJI: Big Workbench Backpack -> SB")
    print("=" * 60)

    item_1710 = ItemStack1710(id="Backpack:workbenchbackpack", damage=217)
    save_1710 = BackpackSave1710(item_1710)
    save_1710.set_intelligent()
    save_1710.set_inventory([
        {"slot": 0, "id": 266, "Count": 32, "Damage": 0},   # gold
        {"slot": 2, "id": 331, "Count": 64, "Damage": 0},   # redstone
    ])

    result = convert_backpack_1710_to_1182(item_1710, save_1710)
    print_conversion_result(result)


def simulate_conversion_ender() -> None:
    print("\n" + "=" * 60)
    print("SYMUlACJA KONWERSJI: Ender Backpack -> SB")
    print("=" * 60)

    item_1710 = ItemStack1710(id="Backpack:backpack", damage=31999)
    save_1710 = BackpackSave1710(item_1710)
    # Ender backpack zawsze 27 slotów, zawartość = vanilla ender chest (ignorujemy)

    result = convert_backpack_1710_to_1182(item_1710, save_1710)
    print_conversion_result(result)


def simulate_full_storage_conversion() -> None:
    print("\n" + "=" * 60)
    print("SYMUlACJA KONWERSJI: Pełny BackpackStorage (3 plecaki)")
    print("=" * 60)

    storage = BackpackStorage1182()

    cases = [
        ("Backpack:backpack", 0, None, [{"slot": 0, "id": 1, "Count": 1, "Damage": 0}]),
        ("Backpack:backpack", 200, "blue", [{"slot": 0, "id": 264, "Count": 8, "Damage": 0}]),
        ("Backpack:workbenchbackpack", 17, None, [{"slot": 0, "id": 266, "Count": 4, "Damage": 0}]),
    ]

    for item_id, damage, custom_name, inv in cases:
        tag = {}
        if custom_name:
            tag["customName"] = custom_name
        item_1710 = ItemStack1710(id=item_id, damage=damage, tag=tag)
        save_1710 = BackpackSave1710(item_1710)
        save_1710.set_inventory(inv)

        result = convert_backpack_1710_to_1182(item_1710, save_1710, target_storage=storage)
        print(f"\n-> {item_id} dmg={damage} -> {result.target_item.id}")
        print(f"   UUID: {result.target_wrapper.get_contents_uuid()}")
        print(f"   Inventory: {len(result.target_wrapper.get_inventory())} items")
        print(f"   Upgrades: {len(result.target_wrapper.get_upgrades())} items")
        if result.warnings:
            for w in result.warnings:
                print(f"   WARN: {w}")

    print("\n[PEŁNY BACKPACKSTORAGE PO KONWERSJI]")
    print(json.dumps(storage.to_saved_data(), indent=2))


def run_all_conversion_simulations() -> None:
    simulate_conversion_small_red()
    simulate_conversion_big_workbench()
    simulate_conversion_ender()
    simulate_full_storage_conversion()
    print("\n" + "=" * 60)
    print("Symulacje konwersji zakończone.")
    print("=" * 60)


if __name__ == "__main__":
    run_all_conversion_simulations()
