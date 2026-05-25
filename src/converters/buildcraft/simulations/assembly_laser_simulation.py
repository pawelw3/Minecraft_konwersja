"""
Symulacja konwersji Assembly Table + Laser + Integration Table + Zone Plan.

BuildCraft 1.7.10:
- TileAssemblyTable: owner, inv[12 slotów], plannedIds[], energy
- TileIntegrationTable: owner, inv[], energy
- TileLaser: owner, battery(maxEnergy, maxReceive, maxExtract, energy)
- TileZonePlan: owner, inv(Items), selectedArea[chunkMapping...]

Problem:
- Brak bezpośredniego odpowiednika dla Assembly Table, Integration Table i Laser w 1.18.2.
- Zone Plan można częściowo zastąpić RFTools Builder (Shape Card), ale Zone Plan
  służył do planowania obszarów (podobnie do blueprintów), nie do automatycznego budowania.

Decyzje:
- Assembly Table + Integration Table + Laser:
  -> Opcja A: REMOVE (usunąć, strata dekoracyjna/functionalna)
  -> Opcja B: DECORATIVE_REPLACE (zastąpić dekoracyjnymi blokami z Supplementaries/Handcrafted)
  -> Opcja C: CONVERT_TO_RFTools (jeśli były używane do auto-craftingu, ale RFTools nie robi
    tego samego co Assembly Table)

Rekomendacja: Opcja A (REMOVE) dla większości, Opcja B tylko jeśli gracz wyraźnie prosi
o zachowanie estetyki.

- Zone Plan:
  -> Opcja A: REMOVE
  -> Opcja B: RFTools Builder + Shape Card (jeśli był używany do planowania obszarów)

Rekomendacja: Opcja A (REMOVE) - Zone Plan był rzadko używany.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class AssemblyTableState1710:
    """Stan Assembly Table BuildCraft 1.7.10."""
    te_id: str
    x: int
    y: int
    z: int
    owner: Optional[str] = None
    inventory: list[dict[str, Any]] = field(default_factory=list)
    planned_ids: list[int] = field(default_factory=list)
    energy: int = 0

    @classmethod
    def from_nbt(cls, nbt: dict[str, Any]) -> "AssemblyTableState1710":
        return cls(
            te_id=nbt.get("id", ""),
            x=nbt.get("x", 0),
            y=nbt.get("y", 0),
            z=nbt.get("z", 0),
            owner=nbt.get("owner"),
            inventory=nbt.get("inv", []),
            planned_ids=nbt.get("plannedIds", []),
            energy=nbt.get("energy", 0),
        )


@dataclass
class LaserState1710:
    """Stan Laser BuildCraft 1.7.10."""
    te_id: str
    x: int
    y: int
    z: int
    owner: Optional[str] = None
    battery_energy: int = 0
    battery_max: int = 10000
    battery_max_receive: int = 250

    @classmethod
    def from_nbt(cls, nbt: dict[str, Any]) -> "LaserState1710":
        battery = nbt.get("battery", {})
        return cls(
            te_id=nbt.get("id", ""),
            x=nbt.get("x", 0),
            y=nbt.get("y", 0),
            z=nbt.get("z", 0),
            owner=nbt.get("owner"),
            battery_energy=battery.get("energy", 0),
            battery_max=battery.get("maxEnergy", 10000),
            battery_max_receive=battery.get("maxReceive", 250),
        )


@dataclass
class ZonePlanState1710:
    """Stan Zone Plan BuildCraft 1.7.10."""
    te_id: str
    x: int
    y: int
    z: int
    owner: Optional[str] = None
    items: list[dict[str, Any]] = field(default_factory=list)
    selected_area: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_nbt(cls, nbt: dict[str, Any]) -> "ZonePlanState1710":
        inv = nbt.get("inv", {})
        items = inv.get("Items", []) if isinstance(inv, dict) else []
        # selectedArea może być lista obiektów chunkMapping
        area = []
        i = 0
        while f"selectedArea[{i}]" in nbt:
            area.append(nbt[f"selectedArea[{i}]"])
            i += 1
        return cls(
            te_id=nbt.get("id", ""),
            x=nbt.get("x", 0),
            y=nbt.get("y", 0),
            z=nbt.get("z", 0),
            owner=nbt.get("owner"),
            items=items,
            selected_area=area,
        )


def simulate_assembly_table_conversion(state_1710: AssemblyTableState1710) -> dict[str, Any]:
    """Symuluje konwersję Assembly Table."""
    # Assembly Table w BC służyła do craftowania chipsetów i advanced pipe items.
    # W 1.18.2 nie ma odpowiednika.
    # Jeśli w inventory są cenne itemy, zalecamy wydropienie ich (przeniesienie do skrzyni).
    # W przeciwnym razie REMOVE.

    has_valuable_items = len(state_1710.inventory) > 0

    return {
        "action": "REMOVE",
        "reason": "Assembly Table nie ma odpowiednika w 1.18.2; logika craftowania chipsetów jest unikalna dla BC.",
        "recommendation": "Wydropić inventory do najbliższej skrzyni przed usunięciem" if has_valuable_items else "Bezpieczne do usunięcia",
        "original": {
            "te_id": state_1710.te_id,
            "x": state_1710.x,
            "y": state_1710.y,
            "z": state_1710.z,
            "inventory_slots": len(state_1710.inventory),
            "planned_recipes": len(state_1710.planned_ids),
        },
        "items_to_drop": state_1710.inventory if has_valuable_items else [],
    }


def simulate_integration_table_conversion(state_1710: AssemblyTableState1710) -> dict[str, Any]:
    """Symuluje konwersję Integration Table."""
    # Integration Table była używana do upgrade'owania chipsetów i robienia advanced gates.
    # Brak odpowiednika.
    return {
        "action": "REMOVE",
        "reason": "Integration Table nie ma odpowiednika w 1.18.2.",
        "original": {
            "te_id": state_1710.te_id,
            "x": state_1710.x,
            "y": state_1710.y,
            "z": state_1710.z,
        },
    }


def simulate_laser_conversion(state_1710: LaserState1710) -> dict[str, Any]:
    """Symuluje konwersję Laser."""
    # Laser w BC zasilał energią Assembly Table i Integration Table.
    # W 1.18.2 nie ma odpowiednika.
    # Można rozważyć zastąpienie go dekoracyjnym blokiem (np. Create: Display Link, Redstone Link),
    # ale najlepiej REMOVE.
    return {
        "action": "REMOVE",
        "reason": "Laser BC jest unikalny dla systemu Assembly Table; brak odpowiednika w 1.18.2.",
        "alternative": "Można zastąpić dekoracyjnym blokiem (np. create:display_link) jeśli estetyka jest kluczowa.",
        "original": {
            "te_id": state_1710.te_id,
            "x": state_1710.x,
            "y": state_1710.y,
            "z": state_1710.z,
            "energy": state_1710.battery_energy,
        },
    }


def simulate_zone_plan_conversion(state_1710: ZonePlanState1710) -> dict[str, Any]:
    """Symuluje konwersję Zone Plan."""
    # Zone Plan służył do planowania obszarów budowy (chunk-based mapping).
    # RFTools Builder + Shape Card pozwala na podobne planowanie, ale jest to
    # znacznie bardziej zaawansowane narzędzie (automatyczne budowanie).
    # Decyzja: REMOVE - Zone Plan był rzadko używany, a RFTools to overkill.

    has_area = len(state_1710.selected_area) > 0

    return {
        "action": "REMOVE",
        "reason": "Zone Plan nie ma bezpośredniego odpowiednika; RFTools Builder to overkill dla prostego planowania.",
        "note": "Jeśli gracz intensywnie używał Zone Plan, można rozważyć RFTools Builder + Shape Card (Void/Quarry).",
        "original": {
            "te_id": state_1710.te_id,
            "x": state_1710.x,
            "y": state_1710.y,
            "z": state_1710.z,
            "selected_chunks": len(state_1710.selected_area),
        },
    }


def print_special_report(result: dict[str, Any]) -> None:
    """Drukuje czytelny raport z konwersji specjalnej maszyny."""
    action = result["action"]
    orig = result.get("original", {})
    te_id = orig.get("te_id", "?")
    print(f"[Special] {te_id} @ ({orig.get('x')},{orig.get('y')},{orig.get('z')}) -> {action}")
    print(f"  Powód: {result['reason']}")
    if result.get("recommendation"):
        print(f"  Rekomendacja: {result['recommendation']}")
    if result.get("alternative"):
        print(f"  Alternatywa: {result['alternative']}")
    if result.get("note"):
        print(f"  Uwaga: {result['note']}")
    if result.get("items_to_drop"):
        print(f"  Itemy do wydropienia: {len(result['items_to_drop'])} slotów")
    print()


# =============================================================================
# TESTY / PRZYKŁADY UŻYCIA
# =============================================================================

if __name__ == "__main__":
    # Przykład 1: Assembly Table z inventory
    assembly_nbt = {
        "id": "net.minecraft.src.buildcraft.factory.TileAssemblyTable",
        "x": 300, "y": 64, "z": 400,
        "owner": "DerFurher",
        "inv": [
            {"Slot": 0, "id": 331, "Count": 50, "Damage": 0},
            {"Slot": 1, "id": 406, "Count": 60, "Damage": 0},
        ],
        "plannedIds": [],
        "energy": 5261,
    }
    assembly = AssemblyTableState1710.from_nbt(assembly_nbt)
    result = simulate_assembly_table_conversion(assembly)
    print_special_report(result)
    assert result["action"] == "REMOVE"
    assert len(result["items_to_drop"]) == 2
    assert "Wydropić inventory" in result["recommendation"]

    # Przykład 2: Integration Table (pusta)
    integration_nbt = {
        "id": "net.minecraft.src.buildcraft.factory.TileIntegrationTable",
        "x": 301, "y": 64, "z": 400,
        "owner": "DerFurher",
        "inv": [],
        "energy": 0,
    }
    integration = AssemblyTableState1710.from_nbt(integration_nbt)
    result = simulate_integration_table_conversion(integration)
    print_special_report(result)
    assert result["action"] == "REMOVE"

    # Przykład 3: Laser
    laser_nbt = {
        "id": "net.minecraft.src.buildcraft.factory.TileLaser",
        "x": 302, "y": 64, "z": 400,
        "owner": "DerFurher",
        "battery": {"maxEnergy": 10000, "maxReceive": 250, "maxExtract": 0, "energy": 10000},
    }
    laser = LaserState1710.from_nbt(laser_nbt)
    result = simulate_laser_conversion(laser)
    print_special_report(result)
    assert result["action"] == "REMOVE"
    assert "dekoracyjnym blokiem" in result["alternative"]

    # Przykład 4: Zone Plan z zaznaczonym obszarem
    zone_nbt = {
        "id": "net.minecraft.src.buildcraft.commander.TileZonePlan",
        "x": 303, "y": 64, "z": 400,
        "owner": "DerFurher",
        "inv": {"Items": []},
        "selectedArea[0]": {"x": 10, "z": 20, "fullSet": 1},
        "selectedArea[1]": {"x": 10, "z": 21, "fullSet": 1},
    }
    zone = ZonePlanState1710.from_nbt(zone_nbt)
    result = simulate_zone_plan_conversion(zone)
    print_special_report(result)
    assert result["action"] == "REMOVE"
    assert result["original"]["selected_chunks"] == 2

    print("=" * 60)
    print("Wszystkie symulacje specjalnych maszyn zakończone sukcesem.")
    print("=" * 60)
