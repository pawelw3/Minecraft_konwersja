import importlib.util
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
TASK5A_SCRIPT = PROJECT_ROOT / "test_scenarios" / "logistics_pipes_task5a" / "generate_logistics_pipes_task5a.py"


def load_task5a_module():
    spec = importlib.util.spec_from_file_location("logistics_pipes_task5a", TASK5A_SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_task5a_fixture_covers_real_pipe_ids_and_validates() -> None:
    module = load_task5a_module()
    samples = module.build_samples()
    pipe_ids = {
        sample.te_nbt.get("pipeId")
        for sample in samples
        if sample.te_nbt.get("id") == module.GENERIC_PIPE_TE
    }
    assert {8749, 8750, 8754, 8758, 8762, 8763, 8779, 8780}.issubset(pipe_ids)

    _, validations = module.convert_samples(samples)
    assert len(validations) == 13
    assert all(row["status"] == "ok" for row in validations)


def test_task5a_chassis_cases_are_explicit() -> None:
    module = load_task5a_module()
    samples = {sample.name: sample for sample in module.build_samples()}
    assert "chassis_mk4_with_modules" in samples
    assert "chassis_mk4_unknown_modules" in samples

    _, validations = module.convert_samples([
        samples["chassis_mk4_with_modules"],
        samples["chassis_mk4_unknown_modules"],
    ])
    by_name = {row["name"]: row for row in validations}
    assert "LP-W-CHASSIS-OVERFLOW" in by_name["chassis_mk4_with_modules"]["actual_warning_codes"]
    assert "LP-W-CHASSIS-MODULES-UNKNOWN" in by_name["chassis_mk4_unknown_modules"]["actual_warning_codes"]
