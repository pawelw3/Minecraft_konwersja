from src.converters.logistics_pipes.simulations.step2_contract_simulations import (
    CHASSIS_SLOTS_1710,
    convert_chassis_modules,
    lp_provider_offer,
    pretty_pipe_speed,
    run_all,
    simulate_chassis_module_dispatch,
    simulate_crafting_request,
    simulate_provider_request_flow,
    simulate_supplier_stockkeeping,
)


def test_all_step2_simulations_pass() -> None:
    result = run_all()
    assert result["status"] == "pass"
    assert result["passed"] == result["total"] == 5


def test_provider_offer_respects_reserved_promises() -> None:
    from src.converters.logistics_pipes.simulations.step2_contract_simulations import Inventory

    inventory = Inventory({"minecraft:iron_ingot": 64})
    assert lp_provider_offer(inventory, "minecraft:iron_ingot", requested=40, reserved=16) == 40
    assert lp_provider_offer(inventory, "minecraft:iron_ingot", requested=60, reserved=16) == 48


def test_chassis_mk5_overflow_is_explicit() -> None:
    converted = convert_chassis_modules(
        "PipeLogisticsChassiMk5",
        ["ModuleProvider", "ModuleActiveSupplier", "ModuleCrafter", "ModulePassiveSupplier"],
    )
    assert CHASSIS_SLOTS_1710["PipeLogisticsChassiMk5"] == 8
    assert len(converted["pretty_modules"]) == 3
    assert converted["overflow"] == ["prettypipes:low_priority_module"]


def test_pretty_pressurizer_speed_contract() -> None:
    assert pretty_pipe_speed(module_speed=0.10, has_pressurizer=False, pressurizer_energy=0) == 0.15
    assert pretty_pipe_speed(module_speed=0.10, has_pressurizer=True, pressurizer_energy=100) == 0.60


def test_individual_contracts_pass() -> None:
    outcomes = [
        simulate_provider_request_flow(),
        simulate_supplier_stockkeeping(),
        simulate_crafting_request(),
        simulate_chassis_module_dispatch(),
    ]
    assert all(outcome.passed for outcome in outcomes)

