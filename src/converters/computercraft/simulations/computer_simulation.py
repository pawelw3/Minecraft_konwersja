"""Symulacja komputera ComputerCraft 1.7.10 → CC:Tweaked 1.18.2.

Bazuje na kodzie źródłowym:
- 1.7.10: `shared/computer/blocks/TileComputerBase.java`
- 1.18.2: `shared/computer/blocks/AbstractComputerBlockEntity.java`
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Computer1710:
    """Symulacja tile entity komputera w 1.7.10."""

    computer_id: int = -1
    label: str | None = None
    on: bool = False

    # Rodzina jest zakodowana w metadata bloku (0-7 = normal, 8-15 = advanced)
    # command_computer to osobny block ID
    family: str = "normal"  # "normal" | "advanced" | "command"

    def write_to_nbt(self) -> dict:
        """Symuluje TileComputerBase.writeToNBT."""
        nbt: dict = {}
        if self.computer_id >= 0:
            nbt["computerID"] = self.computer_id
        if self.label is not None:
            nbt["label"] = self.label
        nbt["on"] = self.on
        return nbt

    @classmethod
    def read_from_nbt(cls, nbt: dict) -> "Computer1710":
        """Symuluje TileComputerBase.readFromNBT."""
        comp = cls()
        if "computerID" in nbt:
            comp.computer_id = nbt["computerID"]
        elif "userDir" in nbt:
            # Pre-1.6 fallback
            try:
                comp.computer_id = int(nbt["userDir"])
            except ValueError:
                pass
        comp.label = nbt.get("label")
        comp.on = nbt.get("on", False)
        return comp


@dataclass
class Computer1182:
    """Symulacja block entity komputera w 1.18.2."""

    computer_id: int = -1
    label: str | None = None
    on: bool = False
    family: str = "normal"  # "normal" | "advanced" | "command"

    def write_to_nbt(self) -> dict:
        """Symuluje AbstractComputerBlockEntity.saveAdditional."""
        nbt: dict = {}
        if self.computer_id >= 0:
            nbt["ComputerId"] = self.computer_id
        if self.label is not None:
            nbt["Label"] = self.label
        nbt["On"] = self.on
        return nbt

    @classmethod
    def read_from_nbt(cls, nbt: dict) -> "Computer1182":
        """Symuluje AbstractComputerBlockEntity.loadServer."""
        comp = cls()
        comp.computer_id = nbt.get("ComputerId", -1)
        comp.label = nbt.get("Label")
        comp.on = nbt.get("On", False)
        return comp


def convert_computer_nbt(nbt_1710: dict) -> dict:
    """Skonwertuj NBT komputera z 1.7.10 na 1.18.2.

    Mapowanie tagów:
        computerID → ComputerId
        label      → Label
        on         → On
    """
    result: dict = {}
    if "computerID" in nbt_1710:
        result["ComputerId"] = nbt_1710["computerID"]
    if "label" in nbt_1710:
        result["Label"] = nbt_1710["label"]
    if "on" in nbt_1710:
        result["On"] = nbt_1710["on"]
    return result


def convert_computer_family(block_id_1710: str, metadata: int = 0) -> str:
    """Wydedukuj rodzinę komputera z block ID i metadata 1.7.10."""
    if block_id_1710 == "computercraft:command_computer":
        return "command"
    if block_id_1710 == "computercraft:computer":
        return "advanced" if metadata >= 8 else "normal"
    return "normal"


def _run_example():
    print("=" * 60)
    print("ComputerCraft — symulacja komputera")
    print("=" * 60)

    # Stwórz komputer 1.7.10
    comp_1710 = Computer1710(computer_id=42, label="Miner", on=True, family="normal")
    nbt_1710 = comp_1710.write_to_nbt()
    print("\n[1.7.10] Computer NBT:", nbt_1710)

    # Skonwertuj
    nbt_1182 = convert_computer_nbt(nbt_1710)
    print("[1.18.2] Converted NBT:", nbt_1182)

    # Odczytaj w 1.18.2
    comp_1182 = Computer1182.read_from_nbt(nbt_1182)
    print("[1.18.2] Loaded computer:", comp_1182)

    # Family mapping
    print("\nFamily mapping examples:")
    for bid, meta in [
        ("computercraft:computer", 2),
        ("computercraft:computer", 10),
        ("computercraft:command_computer", 0),
    ]:
        family = convert_computer_family(bid, meta)
        print(f"  {bid} meta={meta} → family={family}")

    # Test równoważności
    assert comp_1182.computer_id == comp_1710.computer_id
    assert comp_1182.label == comp_1710.label
    assert comp_1182.on == comp_1710.on
    print("\n✓ Test równoważności NBT przeszedł pomyślnie")


if __name__ == "__main__":
    _run_example()
