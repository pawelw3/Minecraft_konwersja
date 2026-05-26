"""Logistics Pipes step 2 contract simulations.

The goal is not to emulate Minecraft or the complete Logistics Pipes routing
stack. These small simulations encode the conversion contracts that must hold
before writing block/entity conversion code for LP 1.7.10 -> Pretty Pipes,
AE2 and XNet on 1.18.2.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
OUT_JSON = ROOT / "src" / "converters" / "logistics_pipes" / "LOGISTICS_PIPES_ZADANIE2_SIMULATION_RESULTS.json"
OUT_MD = ROOT / "src" / "converters" / "logistics_pipes" / "LOGISTICS_PIPES_ZADANIE2_SYMULACJE.md"


SOURCE_EVIDENCE = {
    "lp_provider": (
        "PipeItemsProviderLogistics delegates to ModuleProvider, computes "
        "canProvide() promises and extracts stacks in fullFill()/sendStack()."
    ),
    "lp_request": (
        "PipeItemsRequestLogistics calls RequestTree.request(...) for wanted "
        "ItemStack requests."
    ),
    "lp_supplier": (
        "PipeItemsSupplierLogistics owns ModuleActiveSupplier in-pipe; "
        "ModuleActiveSupplier calculates missing stock and requests partial "
        "or complete supply."
    ),
    "lp_crafting": (
        "PipeItemsCraftingLogistics delegates canProvide(), addCrafting(), "
        "fullFill(), read/write NBT and tick behaviour to ModuleCrafter."
    ),
    "lp_chassis": (
        "PipeLogisticsChassiMk1..Mk5 expose getChassiSize(): 1, 2, 3, 4, 8; "
        "PipeLogisticsChassi forwards provider/crafting calls to installed "
        "modules by slot."
    ),
    "pretty_modules": (
        "Pretty Pipes PipeBlockEntity stores ItemStackHandler modules with 3 "
        "slots and ticks each installed IModule."
    ),
    "pretty_request": (
        "Pretty Pipes ItemTerminalBlockEntity.requestItemLater(...) requests "
        "from network locations and crafting modules."
    ),
    "pretty_crafting": (
        "Pretty Pipes CraftingModuleItem contributes craftables and calls "
        "ItemTerminalBlockEntity.requestItemLater for ingredients."
    ),
    "pretty_speed": (
        "PipeBlockEntity.getItemSpeed returns 0.05 + module speed + 0.45 when "
        "a PressurizerBlockEntity can spend FE; the pressurizer stores energy "
        "in NBT key 'energy'."
    ),
}


CHASSIS_SLOTS_1710 = {
    "PipeLogisticsChassiMk1": 1,
    "PipeLogisticsChassiMk2": 2,
    "PipeLogisticsChassiMk3": 3,
    "PipeLogisticsChassiMk4": 4,
    "PipeLogisticsChassiMk5": 8,
}

PRETTY_PIPE_MODULE_SLOTS = 3

LP_TO_PRETTY_MODULE = {
    "ModuleProvider": "prettypipes:high_extraction_module",
    "ModuleProviderMk2": "prettypipes:high_extraction_module",
    "ModuleActiveSupplier": "prettypipes:high_retrieval_module",
    "ModulePassiveSupplier": "prettypipes:low_priority_module",
    "ModuleCrafter": "prettypipes:high_crafting_module",
    "ModuleCrafterMK2": "prettypipes:high_crafting_module",
    "ModuleCrafterMK3": "prettypipes:high_crafting_module",
}


@dataclass
class ItemStack:
    item: str
    count: int

    def take(self, amount: int) -> "ItemStack":
        taken = min(self.count, max(0, amount))
        self.count -= taken
        return ItemStack(self.item, taken)

    def as_dict(self) -> dict[str, Any]:
        return {"item": self.item, "count": self.count}


@dataclass
class Inventory:
    stacks: dict[str, int] = field(default_factory=dict)

    def count(self, item: str) -> int:
        return self.stacks.get(item, 0)

    def add(self, stack: ItemStack) -> None:
        self.stacks[stack.item] = self.count(stack.item) + stack.count

    def remove(self, item: str, amount: int) -> ItemStack:
        available = self.count(item)
        taken = min(available, max(0, amount))
        if taken:
            self.stacks[item] = available - taken
        return ItemStack(item, taken)

    def as_dict(self) -> dict[str, int]:
        return dict(sorted(self.stacks.items()))


@dataclass
class SimulationOutcome:
    name: str
    passed: bool
    checks: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)


def lp_provider_offer(inventory: Inventory, item: str, requested: int, reserved: int = 0) -> int:
    """Model LP provider promise: available stock minus already promised stock."""

    return min(max(0, inventory.count(item) - reserved), requested)


def lp_request_from_provider(source: Inventory, destination: Inventory, item: str, requested: int) -> int:
    promised = lp_provider_offer(source, item, requested)
    delivered = source.remove(item, promised)
    destination.add(delivered)
    return delivered.count


def pretty_extraction_tick(source: Inventory, destination: Inventory, item: str, max_extraction: int) -> int:
    """Model Pretty Pipes extraction module tick with an allow-list filter."""

    delivered = source.remove(item, max_extraction)
    destination.add(delivered)
    return delivered.count


def simulate_provider_request_flow() -> SimulationOutcome:
    lp_source = Inventory({"minecraft:iron_ingot": 64, "minecraft:cobblestone": 32})
    lp_dest = Inventory()
    pretty_source = Inventory({"minecraft:iron_ingot": 64, "minecraft:cobblestone": 32})
    pretty_dest = Inventory()

    lp_delivered = lp_request_from_provider(lp_source, lp_dest, "minecraft:iron_ingot", 40)
    pretty_delivered = pretty_extraction_tick(pretty_source, pretty_dest, "minecraft:iron_ingot", 40)

    passed = (
        lp_delivered == 40
        and pretty_delivered == 40
        and lp_source.count("minecraft:iron_ingot") == pretty_source.count("minecraft:iron_ingot") == 24
        and lp_dest.count("minecraft:iron_ingot") == pretty_dest.count("minecraft:iron_ingot") == 40
    )
    return SimulationOutcome(
        name="provider_request_flow",
        passed=passed,
        checks=[
            "LP provider promise is bounded by source inventory and requested amount.",
            "Pretty extraction module can preserve the simple provider/request case.",
            "Physical target for conversion: prettypipes:pipe with extraction/filter module plus item terminal for manual requests.",
        ],
        data={
            "lp_delivered": lp_delivered,
            "pretty_delivered": pretty_delivered,
            "lp_source": lp_source.as_dict(),
            "pretty_source": pretty_source.as_dict(),
        },
    )


def lp_supplier_missing(target: Inventory, desired: dict[str, int]) -> dict[str, int]:
    return {
        item: wanted - target.count(item)
        for item, wanted in desired.items()
        if wanted > target.count(item)
    }


def pretty_retrieval_stock_tick(network: Inventory, target: Inventory, desired: dict[str, int], max_per_tick: int) -> dict[str, int]:
    moved: dict[str, int] = {}
    for item, missing in lp_supplier_missing(target, desired).items():
        amount = min(missing, max_per_tick)
        delivered = network.remove(item, amount)
        target.add(delivered)
        if delivered.count:
            moved[item] = delivered.count
    return moved


def simulate_supplier_stockkeeping() -> SimulationOutcome:
    desired = {"minecraft:coal": 32, "minecraft:redstone": 16}
    lp_target = Inventory({"minecraft:coal": 12, "minecraft:redstone": 16})
    pretty_target = Inventory({"minecraft:coal": 12, "minecraft:redstone": 16})
    network = Inventory({"minecraft:coal": 100})

    lp_missing = lp_supplier_missing(lp_target, desired)
    pretty_moved = pretty_retrieval_stock_tick(network, pretty_target, desired, max_per_tick=64)

    passed = lp_missing == {"minecraft:coal": 20} and pretty_moved == {"minecraft:coal": 20}
    return SimulationOutcome(
        name="supplier_stockkeeping",
        passed=passed,
        checks=[
            "LP active supplier computes missing stock against a target inventory.",
            "Pretty retrieval module can pull the missing stack when represented as desired stock plus whitelist.",
        ],
        warnings=[
            "LP pattern supplier target-slot semantics are not 1:1 in Pretty Pipes and must be reported for manual review.",
        ],
        data={
            "desired": desired,
            "lp_missing": lp_missing,
            "pretty_moved": pretty_moved,
            "pretty_target": pretty_target.as_dict(),
        },
    )


@dataclass(frozen=True)
class Recipe:
    output: ItemStack
    ingredients: dict[str, int]
    needs_fluid: bool = False
    has_cleanup_inventory: bool = False


def can_craft(recipe: Recipe, storage: Inventory) -> bool:
    return all(storage.count(item) >= count for item, count in recipe.ingredients.items())


def craft_once(recipe: Recipe, storage: Inventory, output: Inventory) -> bool:
    if recipe.needs_fluid or recipe.has_cleanup_inventory or not can_craft(recipe, storage):
        return False
    for item, count in recipe.ingredients.items():
        storage.remove(item, count)
    output.add(ItemStack(recipe.output.item, recipe.output.count))
    return True


def simulate_crafting_request() -> SimulationOutcome:
    plain_recipe = Recipe(
        output=ItemStack("minecraft:piston", 1),
        ingredients={"minecraft:cobblestone": 4, "minecraft:planks": 3, "minecraft:iron_ingot": 1, "minecraft:redstone": 1},
    )
    fluid_recipe = Recipe(
        output=ItemStack("thermal:machine_frame", 1),
        ingredients={"minecraft:iron_ingot": 4},
        needs_fluid=True,
    )
    storage = Inventory({"minecraft:cobblestone": 64, "minecraft:planks": 64, "minecraft:iron_ingot": 8, "minecraft:redstone": 8})
    output = Inventory()

    plain_ok = craft_once(plain_recipe, storage, output)
    fluid_ok = craft_once(fluid_recipe, storage, output)
    passed = plain_ok and not fluid_ok and output.count("minecraft:piston") == 1

    return SimulationOutcome(
        name="crafting_request",
        passed=passed,
        checks=[
            "Plain LP crafting pipe/table pattern can become Pretty Pipes crafting module or AE2 pattern provider.",
            "Ingredients are consumed only after all required stacks are available.",
            "Fluid crafting and cleanup-inventory cases are rejected from automatic Pretty Pipes conversion.",
        ],
        warnings=[
            "Complex ModuleCrafter NBT with fluids, cleanup inventory or fuzzy matching should route to AE2/manual report.",
        ],
        data={
            "plain_recipe_crafted": plain_ok,
            "fluid_recipe_crafted": fluid_ok,
            "remaining_storage": storage.as_dict(),
            "output": output.as_dict(),
        },
    )


def convert_chassis_modules(chassis_class: str, modules: list[str]) -> dict[str, Any]:
    lp_slots = CHASSIS_SLOTS_1710[chassis_class]
    installed = modules[:lp_slots]
    mapped = [LP_TO_PRETTY_MODULE.get(module, "manual-review") for module in installed]
    pretty_modules = mapped[:PRETTY_PIPE_MODULE_SLOTS]
    overflow = mapped[PRETTY_PIPE_MODULE_SLOTS:]
    return {
        "lp_slots": lp_slots,
        "installed": installed,
        "pretty_modules": pretty_modules,
        "overflow": overflow,
        "target": "prettypipes:pipe" if not overflow else "prettypipes:pipe + xnet/ae2/manual overflow report",
    }


def simulate_chassis_module_dispatch() -> SimulationOutcome:
    mk3 = convert_chassis_modules("PipeLogisticsChassiMk3", ["ModuleProvider", "ModuleActiveSupplier", "ModuleCrafter"])
    mk5 = convert_chassis_modules(
        "PipeLogisticsChassiMk5",
        ["ModuleProvider", "ModuleActiveSupplier", "ModuleCrafter", "ModulePassiveSupplier", "ModuleProviderMk2"],
    )

    passed = (
        len(mk3["pretty_modules"]) == 3
        and not mk3["overflow"]
        and len(mk5["pretty_modules"]) == 3
        and len(mk5["overflow"]) == 2
    )
    return SimulationOutcome(
        name="chassis_module_dispatch",
        passed=passed,
        checks=[
            "LP chassis Mk1..Mk4 can fit into one Pretty pipe only up to 3 installed modules.",
            "LP chassis Mk5 has 8 slots; overflow beyond 3 modules must not be silently dropped.",
            "Known provider/supplier/crafter modules map to extraction/retrieval/crafting Pretty modules.",
        ],
        warnings=[
            "Chassis with more than 3 active modules requires generated conversion event plus manual/XNet/AE2 follow-up.",
        ],
        data={"mk3": mk3, "mk5": mk5, "chassis_slots_1710": CHASSIS_SLOTS_1710},
    )


def pretty_pipe_speed(module_speed: float, has_pressurizer: bool, pressurizer_energy: int, cost: int = 1) -> float:
    pressure_speed = 0.45 if has_pressurizer and pressurizer_energy >= cost else 0.0
    return round(0.05 + module_speed + pressure_speed, 4)


def simulate_power_and_speed() -> SimulationOutcome:
    unpowered = pretty_pipe_speed(module_speed=0.10, has_pressurizer=False, pressurizer_energy=0)
    powered = pretty_pipe_speed(module_speed=0.10, has_pressurizer=True, pressurizer_energy=100)

    passed = unpowered == 0.15 and powered == 0.60
    return SimulationOutcome(
        name="power_and_speed_contract",
        passed=passed,
        checks=[
            "LP power junction/RF/EU providers do not become Pretty Pipes block entities directly.",
            "Pretty Pipes acceleration is represented by a nearby prettypipes:pressurizer with FE energy.",
            "Converted powered LP networks should emit a separate pressurizer placement recommendation.",
        ],
        warnings=[
            "LP internal power amount is not a lossless FE value; preserve it in conversion event metadata, not as live Pretty Pipes NBT.",
        ],
        data={"unpowered_speed": unpowered, "powered_speed": powered},
    )


def run_all() -> dict[str, Any]:
    outcomes = [
        simulate_provider_request_flow(),
        simulate_supplier_stockkeeping(),
        simulate_crafting_request(),
        simulate_chassis_module_dispatch(),
        simulate_power_and_speed(),
    ]
    return {
        "status": "pass" if all(outcome.passed for outcome in outcomes) else "fail",
        "passed": sum(1 for outcome in outcomes if outcome.passed),
        "total": len(outcomes),
        "source_evidence": SOURCE_EVIDENCE,
        "outcomes": [outcome.__dict__ for outcome in outcomes],
    }


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Logistics Pipes - Zadanie 2: symulacje kontraktowe",
        "",
        "Zakres: Logistics Pipes 0.9.3.132 z Minecraft 1.7.10 -> Pretty Pipes 1.12.8 / AE2 / XNet dla Minecraft 1.18.2.",
        "Symulacje sa male i deterministyczne. Ich celem jest zapisanie kontraktow, ktore ma pozniej spelnic kod konwersji.",
        "",
        "## Wynik",
        "",
        f"- Status: {result['status'].upper()}",
        f"- Symulacje zaliczone: {result['passed']}/{result['total']}",
        "",
        "## Symulacje",
        "",
        md_table(
            ["Nazwa", "Status", "Ostrzezenia"],
            [
                [
                    outcome["name"],
                    "PASS" if outcome["passed"] else "FAIL",
                    "; ".join(outcome["warnings"]) if outcome["warnings"] else "-",
                ]
                for outcome in result["outcomes"]
            ],
        ),
        "",
        "## Kontrakty dla Zadania 3",
        "",
        "1. Provider/request: proste rury provider/request moga przejsc na `prettypipes:pipe` z extraction/filter module oraz terminal jako punkt recznego requestu.",
        "2. Supplier: stockkeeping nalezy modelowac jako retrieval module z lista docelowych itemow; tryb pattern/target-slot wymaga raportu manualnego.",
        "3. Crafting: zwykle receptury itemowe moga isc do Pretty Pipes crafting module albo AE2 pattern provider; fuzzy/fluid/cleanup cases ida do AE2/manual report.",
        "4. Chassis: Pretty pipe ma 3 sloty modulow. Chassis LP z wiecej niz 3 aktywnymi modulami musi emitowac overflow event, nie wolno gubic modulow.",
        "5. Power/speed: LP power junction/RF/EU provider nie jest bezposrednim BE Pretty Pipes. Dla aktywnych sieci generuj rekomendacje `prettypipes:pressurizer` i zachowaj stare energy NBT w evencie.",
        "",
        "## Dowody z kodu",
        "",
    ]
    for key, value in result["source_evidence"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Szczegoly", ""])
    for outcome in result["outcomes"]:
        lines.extend([f"### {outcome['name']}", "", f"Status: {'PASS' if outcome['passed'] else 'FAIL'}", ""])
        if outcome["checks"]:
            lines.append("Checks:")
            lines.extend(f"- {check}" for check in outcome["checks"])
            lines.append("")
        if outcome["warnings"]:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in outcome["warnings"])
            lines.append("")
    return "\n".join(lines)


def main() -> None:
    result = run_all()
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    OUT_MD.write_text(render_markdown(result), encoding="utf-8")
    print(json.dumps({"status": result["status"], "passed": result["passed"], "total": result["total"]}, indent=2))
    if result["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
