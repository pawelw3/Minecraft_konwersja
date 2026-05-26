#!/usr/bin/env python3
"""Run Big Reactors Task 6 headless tick/restart verification.

Starts the server with the 5B world, waits for ticks, checks block states,
saves, restarts, and checks persistence.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SERVER_DIR = PROJECT_ROOT / "headless_server/1.18.2"
SCENARIO_DIR = Path(__file__).resolve().parent
DEFAULT_REPORT = SCENARIO_DIR / "bigreactors_task6_headless_tick_restart_report.json"

sys.path.insert(0, str(PROJECT_ROOT))
from src.converters.projectred.test_structures.headless_test.rcon_client import RconClient  # noqa: E402


# Blocks to verify (name -> (x, y, z, expected_id))
# Positions must match the converted patch exactly.
SUT_BLOCKS = {
    "reactor_casing": (200, 64, 202, "biggerreactors:reactor_casing"),
    "uranium_block": (201, 64, 200, "biggerreactors:uranium_block"),
    "reactor_terminal": (201, 64, 202, "biggerreactors:reactor_terminal"),
    "reactor_control_rod": (202, 64, 202, "biggerreactors:reactor_control_rod"),
    "reactor_power_tap": (203, 64, 202, "biggerreactors:reactor_power_tap"),
    "reactor_access_port": (204, 64, 202, "biggerreactors:reactor_access_port"),
    "reactor_fuel_rod": (210, 64, 202, "biggerreactors:reactor_fuel_rod"),
    "turbine_casing": (200, 64, 204, "biggerreactors:turbine_casing"),
    "turbine_rotor_shaft": (207, 64, 204, "biggerreactors:turbine_rotor_shaft"),
    "turbine_rotor_blade": (208, 64, 204, "biggerreactors:turbine_rotor_blade"),
    "cyanite_reprocessor": (200, 64, 206, "biggerreactors:cyanite_reprocessor"),
    "reactor_glass": (209, 64, 202, "biggerreactors:reactor_glass"),
}

APPLY_MARKER = "[BIGREACTORS_TASK5B] apply complete"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def run_server(server_dir: Path, label: str) -> tuple[subprocess.Popen, Path, Path]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_log = server_dir / f"server_bigreactors_task6_{label}_{stamp}_out.log"
    err_log = server_dir / f"server_bigreactors_task6_{label}_{stamp}_err.log"
    out_handle = out_log.open("w", encoding="utf-8", errors="replace")
    err_handle = err_log.open("w", encoding="utf-8", errors="replace")
    proc = subprocess.Popen(
        [
            "java",
            "@user_jvm_args.txt",
            "@libraries/net/minecraftforge/forge/1.18.2-40.2.4/win_args.txt",
            "nogui",
        ],
        cwd=server_dir,
        stdout=out_handle,
        stderr=err_handle,
        text=True,
        creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
    )
    out_handle.close()
    err_handle.close()
    return proc, out_log, err_log


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def wait_for_server(proc: subprocess.Popen, out_log: Path, timeout: int) -> dict[str, Any]:
    deadline = time.time() + timeout
    start = time.time()
    while time.time() < deadline:
        combined = read_text(out_log)
        done = "Done (" in combined
        rcon_ready = "RCON running on" in combined
        ready = done and rcon_ready
        if ready:
            return {
                "ready": True,
                "done": done,
                "rcon_ready": rcon_ready,
                "elapsed_seconds": round(time.time() - start, 1),
            }
        if proc.poll() is not None:
            break
        time.sleep(2)
    combined = read_text(out_log)
    return {
        "ready": False,
        "done": "Done (" in combined,
        "rcon_ready": "RCON running on" in combined,
        "elapsed_seconds": round(time.time() - start, 1),
    }


def connect_rcon(host: str, port: int, password: str, timeout: int) -> RconClient:
    deadline = time.time() + timeout
    last_error: str | None = None
    while time.time() < deadline:
        client = RconClient(host, port, password, timeout=30.0)
        try:
            if client.connect():
                return client
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
            client.disconnect()
        time.sleep(2)
    raise RuntimeError(f"RCON not ready: {last_error}")


def forceload_chunks(client: RconClient) -> None:
    """Force-load all chunks containing SUT blocks."""
    chunks = set()
    for x, y, z, _ in SUT_BLOCKS.values():
        chunks.add((x >> 4, z >> 4))
    for cx, cz in sorted(chunks):
        client.command(f"forceload add {cx * 16} {cz * 16}")
    time.sleep(3)


def disable_datapack_load(world_dir: Path) -> Path | None:
    """Rename load.json so the datapack doesn't auto-run on server start."""
    load_json = world_dir / "datapacks" / "bigreactors_task5b" / "data" / "minecraft" / "tags" / "functions" / "load.json"
    if load_json.exists():
        disabled = load_json.with_suffix(".json.disabled")
        load_json.rename(disabled)
        return disabled
    return None


def enable_datapack_load(disabled: Path | None) -> None:
    if disabled and disabled.exists():
        disabled.rename(disabled.with_suffix("").with_suffix(".json"))


def wait_for_marker_in_log(out_log: Path, marker: str, timeout: int = 60) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        text = read_text(out_log)
        if marker in text:
            return True
        time.sleep(1)
    return False


def check_block(client: RconClient, name: str) -> dict[str, Any]:
    x, y, z, expected_id = SUT_BLOCKS[name]
    check_response = client.command(f"execute if block {x} {y} {z} {expected_id}")
    data_response = client.command(f"data get block {x} {y} {z}")
    return {
        "name": name,
        "position": [x, y, z],
        "expected_id": expected_id,
        "check_response": check_response,
        "data_response": data_response,
        "has_expected_block": "Test passed" in check_response,
        "has_block_entity_data": "has block data" in data_response.lower() or "block data:" in data_response.lower(),
        "data_response_excerpt": data_response[:500],
    }


def stop_server(proc: subprocess.Popen, client: RconClient | None, timeout: int = 60) -> dict[str, Any]:
    if client:
        try:
            client.command("save-all")
            time.sleep(2)
            client.command("stop")
        except Exception:
            pass
    try:
        proc.wait(timeout=timeout)
        return {"stopped": True, "killed": False}
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        return {"stopped": True, "killed": True}


def analyze_log(out_log: Path, err_log: Path) -> dict[str, Any]:
    out_text = read_text(out_log)
    err_text = read_text(err_log)

    errors = []
    for line in out_text.splitlines():
        if "ERROR" in line or "FATAL" in line or "Exception" in line:
            if "biggerreactors" in line.lower() or "phosphophyllite" in line.lower():
                errors.append(line.strip())

    warnings = []
    for line in out_text.splitlines():
        if "WARN" in line:
            if "biggerreactors" in line.lower() or "phosphophyllite" in line.lower():
                warnings.append(line.strip())

    return {
        "errors_found": len(errors),
        "errors": errors[:10],
        "warnings_found": len(warnings),
        "warnings": warnings[:10],
        "has_chunk_errors": "Couldn't load chunk" in out_text or "Couldn't load chunk" in err_text,
        "has_te_errors": "Skipping BlockEntity" in out_text or "Skipping BlockEntity" in err_text,
    }


def main() -> None:
    # Ensure server.properties has RCON enabled for task6
    server_props = SERVER_DIR / "server.properties"
    props_text = server_props.read_text(encoding="utf-8")
    if "enable-rcon=false" in props_text:
        props_text = props_text.replace("enable-rcon=false", "enable-rcon=true")
        props_text = props_text.replace("rcon.password=", "rcon.password=test123")
        props_text = props_text.replace("rcon.port=25575", "rcon.port=25575")
        server_props.write_text(props_text, encoding="utf-8")

    world_dir = SERVER_DIR / "world_bigreactors_task5b"

    # Disable auto-run datapack so we control when it fires (after chunks are loaded)
    disabled_load = disable_datapack_load(world_dir)

    report: dict[str, Any] = {
        "mod": "BigReactors",
        "task": "6",
        "started_at": now_iso(),
        "phases": [],
    }

    # Phase 1: First boot + apply datapack manually + 3 min ticks
    print("[Task 6] Phase 1: First boot + apply + 3 min ticks...")
    proc1, out1, err1 = run_server(SERVER_DIR, "first")
    status1 = wait_for_server(proc1, out1, timeout=180)

    phase1: dict[str, Any] = {
        "phase": "first_boot",
        "server_ready": status1["ready"],
        "elapsed_seconds": status1["elapsed_seconds"],
    }

    client: RconClient | None = None
    if status1["ready"]:
        client = connect_rcon("127.0.0.1", 25575, "test123", timeout=30)
        client.command('say [BIGREACTORS_TASK6] Starting 3-minute tick test')

        # Force-load chunks BEFORE applying the datapack
        forceload_chunks(client)

        # Manually run the datapack function now that chunks are loaded
        client.command('function bigreactors_task5b:apply')
        if not wait_for_marker_in_log(out1, "[BIGREACTORS_TASK5B] apply complete", timeout=60):
            print("WARNING: Datapack apply marker not found in logs")

        # Wait 3 minutes for ticking
        time.sleep(180)

        # Check blocks
        block_checks = {}
        for name in SUT_BLOCKS:
            block_checks[name] = check_block(client, name)
        phase1["block_checks"] = block_checks
        phase1["blocks_passed"] = sum(1 for c in block_checks.values() if c["has_expected_block"])

        client.command('say [BIGREACTORS_TASK6] Tick test complete, saving and stopping')
        stop_server(proc1, client)
    else:
        stop_server(proc1, None)

    phase1["log_analysis"] = analyze_log(out1, err1)
    report["phases"].append(phase1)

    # Phase 2: Restart + verify persistence (datapack still disabled)
    print("[Task 6] Phase 2: Restart + verify persistence...")
    proc2, out2, err2 = run_server(SERVER_DIR, "restart")
    status2 = wait_for_server(proc2, out2, timeout=180)

    phase2: dict[str, Any] = {
        "phase": "restart",
        "server_ready": status2["ready"],
        "elapsed_seconds": status2["elapsed_seconds"],
    }

    if status2["ready"]:
        client = connect_rcon("127.0.0.1", 25575, "test123", timeout=30)
        client.command('say [BIGREACTORS_TASK6] Restart verification')

        # Force-load chunks before checking blocks
        forceload_chunks(client)

        block_checks2 = {}
        for name in SUT_BLOCKS:
            block_checks2[name] = check_block(client, name)
        phase2["block_checks"] = block_checks2
        phase2["blocks_passed"] = sum(1 for c in block_checks2.values() if c["has_expected_block"])

        client.command('say [BIGREACTORS_TASK6] Restart verification complete')
        stop_server(proc2, client)
    else:
        stop_server(proc2, None)

    phase2["log_analysis"] = analyze_log(out2, err2)
    report["phases"].append(phase2)

    # Restore datapack load.json for future runs
    enable_datapack_load(disabled_load)

    report["finished_at"] = now_iso()
    report["overall_pass"] = (
        phase1.get("server_ready", False)
        and phase2.get("server_ready", False)
        and phase1.get("blocks_passed", 0) == len(SUT_BLOCKS)
        and phase2.get("blocks_passed", 0) == len(SUT_BLOCKS)
        and not phase1["log_analysis"]["has_chunk_errors"]
        and not phase2["log_analysis"]["has_chunk_errors"]
    )

    DEFAULT_REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Report -> {DEFAULT_REPORT}")
    print(f"Overall: {'PASS' if report['overall_pass'] else 'FAIL'}")


if __name__ == "__main__":
    main()
