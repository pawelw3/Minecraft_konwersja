"""Symulacja żółwia (turtle) ComputerCraft 1.7.10 → CC:Tweaked 1.18.2.

Bazuje na kodzie źródłowym:
- 1.7.10: `shared/turtle/blocks/TileTurtle.java`, `shared/turtle/core/TurtleBrain.java`
- 1.18.2: `shared/turtle/blocks/TurtleBlockEntity.java`, `shared/turtle/core/TurtleBrain.java`

Kluczowe wyzwania:
1. Mapowanie legacy numeric upgrade IDs → string IDs
2. Zmiana nazw NBT tagów (camelCase → PascalCase)
3. Turtle Expanded → Turtle Normal (brak expanded w 1.18.2)
4. Owner UUID w 1.18.2 (nie było w 1.7.10)
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Mapowanie upgrade'ów
# ---------------------------------------------------------------------------

LEGACY_UPGRADE_ID_MAP: dict[int, str] = {
    1: "computercraft:wireless_modem",
    2: "minecraft:crafting_table",
    3: "minecraft:diamond_sword",
    4: "minecraft:diamond_shovel",
    5: "minecraft:diamond_pickaxe",
    6: "minecraft:diamond_axe",
    7: "minecraft:diamond_hoe",
    8: "computercraft:speaker",
    -1: "computercraft:advanced_modem",
}

UPGRADE_RENAME_MAP: dict[str, str] = {
    # 1.7.10 → 1.18.2 (bezpośrednie zamienniki)
    "computercraft:wireless_modem": "computercraft:wireless_modem_normal",
    "computercraft:advanced_modem": "computercraft:wireless_modem_advanced",
}

UPGRADE_DIRECT_MATCH: frozenset[str] = frozenset({
    "minecraft:diamond_pickaxe",
    "minecraft:diamond_axe",
    "minecraft:diamond_sword",
    "minecraft:diamond_shovel",
    "minecraft:diamond_hoe",
    "minecraft:crafting_table",
    "computercraft:speaker",
})


def resolve_upgrade_id(value: str | int) -> str | None:
    """Rozwiąż ID upgradu z 1.7.10 na string ID 1.18.2.

    Obsługuje:
    - legacy numeric IDs (short/int)
    - string IDs (z bezpośrednim dopasowaniem lub rename)
    """
    if isinstance(value, int):
        id_1710 = LEGACY_UPGRADE_ID_MAP.get(value)
        if id_1710 is None:
            return None
        return UPGRADE_RENAME_MAP.get(id_1710, id_1710)

    # String ID
    if value in UPGRADE_DIRECT_MATCH:
        return value
    return UPGRADE_RENAME_MAP.get(value, value)


# ---------------------------------------------------------------------------
# Klasy symulacyjne
# ---------------------------------------------------------------------------

@dataclass
class TurtleUpgradeData:
    upgrade_id: str | None = None
    upgrade_nbt: dict | None = None


@dataclass
class Turtle1710:
    """Symulacja żółwia 1.7.10."""

    computer_id: int = -1
    label: str | None = None
    on: bool = False
    dir: int = 2  # facing (NBT)
    selected_slot: int = 0
    fuel_level: int = 0
    colour_hex: int = -1
    overlay: str | None = None  # "modid:path"
    left_upgrade: TurtleUpgradeData = field(default_factory=TurtleUpgradeData)
    right_upgrade: TurtleUpgradeData = field(default_factory=TurtleUpgradeData)
    inventory: list[dict] = field(default_factory=list)  # uproszczone ItemStack NBT
    family: str = "normal"  # normal | advanced

    def write_to_nbt(self) -> dict:
        nbt: dict = {}
        if self.computer_id >= 0:
            nbt["computerID"] = self.computer_id
        if self.label:
            nbt["label"] = self.label
        nbt["on"] = self.on
        nbt["dir"] = self.dir
        nbt["selectedSlot"] = self.selected_slot
        nbt["fuelLevel"] = self.fuel_level
        if self.colour_hex != -1:
            nbt["colour"] = self.colour_hex
        if self.overlay:
            mod, path = self.overlay.split(":", 1)
            nbt["overlay_mod"] = mod
            nbt["overlay_path"] = path
        if self.left_upgrade.upgrade_id:
            nbt["leftUpgrade"] = self.left_upgrade.upgrade_id
        if self.left_upgrade.upgrade_nbt:
            nbt["leftUpgradeNBT"] = self.left_upgrade.upgrade_nbt
        if self.right_upgrade.upgrade_id:
            nbt["rightUpgrade"] = self.right_upgrade.upgrade_id
        if self.right_upgrade.upgrade_nbt:
            nbt["rightUpgradeNBT"] = self.right_upgrade.upgrade_nbt
        if self.inventory:
            nbt["Items"] = self.inventory
        return nbt

    @classmethod
    def read_from_nbt(cls, nbt: dict) -> "Turtle1710":
        t = cls()
        t.computer_id = nbt.get("computerID", -1)
        t.label = nbt.get("label")
        t.on = nbt.get("on", False)
        t.dir = nbt.get("dir", 2)
        t.selected_slot = nbt.get("selectedSlot", 0)
        t.fuel_level = nbt.get("fuelLevel", 0)
        t.colour_hex = nbt.get("colour", -1)
        if "overlay_mod" in nbt and "overlay_path" in nbt:
            t.overlay = f"{nbt['overlay_mod']}:{nbt['overlay_path']}"

        # Upgrades — mogą być string lub short (legacy)
        for side, key in [("left", "leftUpgrade"), ("right", "rightUpgrade")]:
            if key in nbt:
                val = nbt[key]
                if isinstance(val, int):
                    resolved = resolve_upgrade_id(val)
                else:
                    resolved = resolve_upgrade_id(val)
                data = TurtleUpgradeData(upgrade_id=resolved)
                nbt_key = f"{key}NBT"
                if nbt_key in nbt:
                    data.upgrade_nbt = dict(nbt[nbt_key])
                if side == "left":
                    t.left_upgrade = data
                else:
                    t.right_upgrade = data
        t.inventory = list(nbt.get("Items", []))
        return t


@dataclass
class Turtle1182:
    """Symulacja żółwia 1.18.2."""

    computer_id: int = -1
    label: str | None = None
    on: bool = False
    selected_slot: int = 0
    fuel_level: int = 0
    colour_hex: int = -1
    overlay: str | None = None
    left_upgrade: TurtleUpgradeData = field(default_factory=TurtleUpgradeData)
    right_upgrade: TurtleUpgradeData = field(default_factory=TurtleUpgradeData)
    inventory: list[dict] = field(default_factory=list)
    owner: dict | None = None  # {UpperId, LowerId, Name}
    family: str = "normal"

    def write_to_nbt(self) -> dict:
        nbt: dict = {}
        if self.computer_id >= 0:
            nbt["ComputerId"] = self.computer_id
        if self.label:
            nbt["Label"] = self.label
        nbt["On"] = self.on
        nbt["Slot"] = self.selected_slot
        nbt["Fuel"] = self.fuel_level
        if self.colour_hex != -1:
            nbt["Colour"] = self.colour_hex
        if self.overlay:
            nbt["Overlay"] = self.overlay
        if self.left_upgrade.upgrade_id:
            nbt["LeftUpgrade"] = self.left_upgrade.upgrade_id
        if self.left_upgrade.upgrade_nbt:
            nbt["LeftUpgradeNbt"] = self.left_upgrade.upgrade_nbt
        if self.right_upgrade.upgrade_id:
            nbt["RightUpgrade"] = self.right_upgrade.upgrade_id
        if self.right_upgrade.upgrade_nbt:
            nbt["RightUpgradeNbt"] = self.right_upgrade.upgrade_nbt
        if self.inventory:
            nbt["Items"] = self.inventory
        if self.owner:
            nbt["Owner"] = self.owner
        return nbt

    @classmethod
    def read_from_nbt(cls, nbt: dict) -> "Turtle1182":
        t = cls()
        t.computer_id = nbt.get("ComputerId", -1)
        t.label = nbt.get("Label")
        t.on = nbt.get("On", False)
        t.selected_slot = nbt.get("Slot", 0)
        t.fuel_level = nbt.get("Fuel", 0)
        t.colour_hex = nbt.get("Colour", -1)
        t.overlay = nbt.get("Overlay")
        if "LeftUpgrade" in nbt:
            t.left_upgrade = TurtleUpgradeData(
                upgrade_id=nbt["LeftUpgrade"],
                upgrade_nbt=nbt.get("LeftUpgradeNbt"),
            )
        if "RightUpgrade" in nbt:
            t.right_upgrade = TurtleUpgradeData(
                upgrade_id=nbt["RightUpgrade"],
                upgrade_nbt=nbt.get("RightUpgradeNbt"),
            )
        t.inventory = list(nbt.get("Items", []))
        t.owner = nbt.get("Owner")
        return t


def convert_turtle_nbt(nbt_1710: dict) -> dict:
    """Skonwertuj NBT żółwia z 1.7.10 na 1.18.2."""
    result: dict = {}

    # Computer base
    if "computerID" in nbt_1710:
        result["ComputerId"] = nbt_1710["computerID"]
    if "label" in nbt_1710:
        result["Label"] = nbt_1710["label"]
    if "on" in nbt_1710:
        result["On"] = nbt_1710["on"]

    # Brain
    if "fuelLevel" in nbt_1710:
        result["Fuel"] = nbt_1710["fuelLevel"]
    if "selectedSlot" in nbt_1710:
        result["Slot"] = nbt_1710["selectedSlot"]
    if "colour" in nbt_1710:
        result["Colour"] = nbt_1710["colour"]
    if "overlay_mod" in nbt_1710 and "overlay_path" in nbt_1710:
        result["Overlay"] = f"{nbt_1710['overlay_mod']}:{nbt_1710['overlay_path']}"

    # Upgrades
    for old_key, new_key in [
        ("leftUpgrade", "LeftUpgrade"),
        ("rightUpgrade", "RightUpgrade"),
    ]:
        if old_key in nbt_1710:
            val = nbt_1710[old_key]
            if isinstance(val, int):
                resolved = resolve_upgrade_id(val)
            else:
                resolved = resolve_upgrade_id(val)
            if resolved:
                result[new_key] = resolved
        old_nbt_key = f"{old_key}NBT"
        new_nbt_key = f"{new_key[:-7]}UpgradeNbt" if "Upgrade" in new_key else new_key + "Nbt"
        # leftUpgradeNBT → LeftUpgradeNbt
        if old_nbt_key == "leftUpgradeNBT":
            new_nbt_key = "LeftUpgradeNbt"
        elif old_nbt_key == "rightUpgradeNBT":
            new_nbt_key = "RightUpgradeNbt"
        if old_nbt_key in nbt_1710:
            result[new_nbt_key] = dict(nbt_1710[old_nbt_key])

    # Inventory
    if "Items" in nbt_1710:
        result["Items"] = nbt_1710["Items"]

    # Owner — brak w 1.7.10, zostaje None (CC:Tweaked ustawi przy pierwszym użyciu)
    return result


def _run_example():
    print("=" * 60)
    print("ComputerCraft — symulacja żółwia")
    print("=" * 60)

    # Stwórz żółwia 1.7.10 z upgradami
    t_1710 = Turtle1710(
        computer_id=7,
        label="Digger",
        on=True,
        dir=3,
        selected_slot=1,
        fuel_level=5000,
        colour_hex=0xFF0000,
        overlay="minecraft:diamond_pickaxe",
        left_upgrade=TurtleUpgradeData(upgrade_id="computercraft:wireless_modem"),
        right_upgrade=TurtleUpgradeData(upgrade_id="minecraft:diamond_pickaxe"),
    )
    nbt_1710 = t_1710.write_to_nbt()
    print("\n[1.7.10] Turtle NBT:", nbt_1710)

    # Skonwertuj
    nbt_1182 = convert_turtle_nbt(nbt_1710)
    print("[1.18.2] Converted NBT:", nbt_1182)

    t_1182 = Turtle1182.read_from_nbt(nbt_1182)
    print("[1.18.2] Loaded turtle:")
    print(f"  ID={t_1182.computer_id}, label={t_1182.label}, on={t_1182.on}")
    print(f"  fuel={t_1182.fuel_level}, slot={t_1182.selected_slot}, colour={t_1182.colour_hex:#x}")
    print(f"  left={t_1182.left_upgrade.upgrade_id}, right={t_1182.right_upgrade.upgrade_id}")

    # Test legacy numeric ID
    print("\n--- Test legacy numeric upgrade IDs ---")
    for legacy_id, expected in [
        (1, "computercraft:wireless_modem_normal"),
        (2, "minecraft:crafting_table"),
        (5, "minecraft:diamond_pickaxe"),
        (-1, "computercraft:wireless_modem_advanced"),
        (8, "computercraft:speaker"),
    ]:
        resolved = resolve_upgrade_id(legacy_id)
        status = "✓" if resolved == expected else f"✗ (got {resolved})"
        print(f"  legacy {legacy_id:2d} → {resolved:45s} {status}")

    # Test string rename
    print("\n--- Test string ID rename ---")
    for old, expected in [
        ("computercraft:wireless_modem", "computercraft:wireless_modem_normal"),
        ("computercraft:advanced_modem", "computercraft:wireless_modem_advanced"),
        ("minecraft:diamond_pickaxe", "minecraft:diamond_pickaxe"),
    ]:
        resolved = resolve_upgrade_id(old)
        status = "✓" if resolved == expected else f"✗ (got {resolved})"
        print(f"  {old:40s} → {resolved:45s} {status}")

    print("\n✓ Symulacja żółwia zakończona")


if __name__ == "__main__":
    _run_example()
