from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from src.converters.armourers_workshop.mappings import BLOCK_MAPPINGS


PROJECT_ROOT = Path(__file__).resolve().parents[4]
TASK5A_SCRIPT = PROJECT_ROOT / "test_scenarios" / "armourers_workshop_task5a" / "generate_armourers_workshop_task5a.py"


def load_task5a_module():
    spec = importlib.util.spec_from_file_location("armourers_workshop_task5a", TASK5A_SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_task5a_fixture_covers_all_mapped_source_names() -> None:
    module = load_task5a_module()
    samples = module.build_samples()

    assert {sample.source_name for sample in samples} == set(BLOCK_MAPPINGS)


def test_task5a_fixture_exercises_skinnable_parent_child_and_placeholders() -> None:
    module = load_task5a_module()
    samples = module.build_samples()

    names = {sample.name for sample in samples}
    assert "mannequin_with_items" in names
    assert "doll_placeholder" in names
    assert "mini_armourer_placeholder" in names
    assert {sample.metadata for sample in samples if sample.source_name == "skinnable"} >= {2, 3, 4, 5}
    assert {sample.metadata for sample in samples if sample.source_name == "skinnableChild"} >= {2, 3, 4, 5}


def test_task5a_fixture_converts_without_failures() -> None:
    module = load_task5a_module()
    converter = module.ArmourersWorkshopConverter()
    conversions = [module.convert_sample(converter, sample) for sample in module.build_samples()]

    assert all(item["success"] for item in conversions)
    assert any(item["status"] == "placeholder" for item in conversions)
    assert any(item["status"] == "converted" for item in conversions)
