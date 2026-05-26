import importlib.util
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
TASK5B_SCRIPT = PROJECT_ROOT / "test_scenarios" / "logistics_pipes_task5a" / "materialize_logistics_pipes_task5b.py"


def load_task5b_module():
    spec = importlib.util.spec_from_file_location("logistics_pipes_task5b", TASK5B_SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_task5b_setblock_command_keeps_pretty_pipe_nbt() -> None:
    module = load_task5b_module()
    command = module.setblock_command(
        {
            "op": "set_block_entity",
            "pos": [1, 70, 2],
            "block": "prettypipes:pipe",
            "nbt": {
                "id": "prettypipes:pipe",
                "x": 1,
                "y": 70,
                "z": 2,
                "modules": {"Size": 3, "Items": [{"Slot": 0, "id": "prettypipes:high_extraction_module", "Count": 1}]},
            },
        }
    )
    assert command.startswith("setblock 1 70 2 prettypipes:pipe{")
    assert 'id:"prettypipes:pipe"' in command
    assert 'id:"prettypipes:high_extraction_module"' in command
    assert command.endswith(" replace")


def test_task5b_blockstate_validation_sees_installed_targets() -> None:
    module = load_task5b_module()
    validation = module.validate_mod_targets(
        module.DEFAULT_SERVER_DIR,
        {"prettypipes:pipe", "prettypipes:item_terminal", "ae2:pattern_provider"},
    )
    assert validation["status"] == "ok"
    assert validation["missing"] == []
