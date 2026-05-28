from __future__ import annotations

import importlib.util
import json
import sys
from argparse import Namespace
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
SCRIPT = PROJECT_ROOT / "test_scenarios" / "armourers_workshop_task5a" / "materialize_armourers_workshop_task5b.py"
PATCH = PROJECT_ROOT / "test_scenarios" / "armourers_workshop_task5a" / "armourers_workshop_task5a_converted_patch_1182.json"


def load_module():
    spec = importlib.util.spec_from_file_location("aw_task5b_materializer", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_task5b_materializer_preserves_aw_nbt_as_placeholder_when_jar_missing(tmp_path: Path):
    module = load_module()
    server_dir = tmp_path / "server"
    base_world = server_dir / "world"
    target_world = server_dir / "world_aw_task5b"
    mods = server_dir / "mods"
    mods.mkdir(parents=True)
    base_world.mkdir(parents=True)
    (mods / "conversion-placeholders-1.0.0.jar").write_text("", encoding="utf-8")
    (server_dir / "server.properties").write_text("level-name=world\n", encoding="utf-8")
    module.REPORT_MD = tmp_path / "report.md"
    module.HANDOFF = tmp_path / "handoff.md"

    report = module.materialize(
        Namespace(
            patch=PATCH,
            server_dir=server_dir,
            base_world=base_world,
            target_world=target_world,
            report=tmp_path / "report.json",
            server_properties_out=tmp_path / "server_aw.properties",
            overwrite=True,
        )
    )

    assert report["aw_registry_preflight"]["status"] == "missing_aw_jar"
    assert report["stats"]["commands"] == 26
    assert report["stats"]["fallback_reasons"]["aw_be_placeholder"] == 19
    assert report["skin_library"]["copied_count"] == 2

    apply_function = target_world / "datapacks" / "armourers_workshop_task5b" / "data" / "armourers_workshop_task5b" / "functions" / "apply.mcfunction"
    text = apply_function.read_text(encoding="utf-8")
    assert "[AW_TASK5B] apply complete" in text
    assert "conversion_placeholders:block_entity_placeholder" in text
    assert "original_target_block_1182" in text
    assert (target_world / "skin-library" / "official" / "Barrel.armour").exists()


def test_task5b_report_matches_generated_world():
    report_path = PROJECT_ROOT / "test_scenarios" / "armourers_workshop_task5a" / "armourers_workshop_task5b_headless_materialization_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["target_world"].endswith("world_armourers_workshop_task5b")
    assert report["stats"]["commands"] == 26
    assert report["skin_library"]["copied_count"] == 2
    assert report["aw_registry_preflight"]["status"] in {"ok", "missing_aw_jar", "missing_targets"}
