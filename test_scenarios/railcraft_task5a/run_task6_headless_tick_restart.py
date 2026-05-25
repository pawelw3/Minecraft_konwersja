#!/usr/bin/env python3
"""Run Railcraft Task 6 headless tick/restart verification.

Starts the server with the 5B datapack enabled, manually triggers the apply
function via RCON, waits for ticks, checks selected block states, disables the
datapack, saves, restarts, and checks persistence.
"""

from __future__ import annotations

import argparse
import hashlib
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
DEFAULT_REPORT = SCENARIO_DIR / "railcraft_task6_headless_tick_restart_report.json"

sys.path.insert(0, str(PROJECT_ROOT))
from src.converters.projectred.test_structures.headless_test.rcon_client import RconClient  # noqa: E402


SUT_BLOCKS = {
    "mechanical_press": (212, 64, 200, "create:mechanical_press"),
    "crushing_wheel": (214, 64, 200, "create:crushing_wheel"),
    "campfire": (216, 64, 200, "minecraft:campfire"),
    "smoker": (218, 64, 200, "minecraft:smoker"),
    "steam_engine": (232, 64, 200, "create:steam_engine"),
    "fluid_tank": (238, 64, 200, "create:fluid_tank"),
    "observer": (294, 64, 200, "minecraft:observer"),
    "comparator": (284, 64, 200, "minecraft:comparator"),
    "framed_slab": (312, 64, 200, "framedblocks:framed_slab"),
    "air": (320, 64, 200, "minecraft:air"),
}

APPLY_MARKER = "[RAILCRAFT_TASK5B] apply complete"
APPLY_FUNCTION_ERROR = "Failed to load function railcraft_task5b:apply"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def run_server(server_dir: Path, label: str) -> tuple[subprocess.Popen, Path, Path]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_log = server_dir / f"server_railcraft_task6_{label}_{stamp}_out.log"
    err_log = server_dir / f"server_railcraft_task6_{label}_{stamp}_err.log"
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


def wait_for_server(proc: subprocess.Popen, out_log: Path, timeout: int, require_apply: bool = False) -> dict[str, Any]:
    deadline = time.time() + timeout
    start = time.time()
    while time.time() < deadline:
        combined = read_text(out_log)
        done = "Done (" in combined
        rcon_ready = "RCON running on" in combined
        apply_complete = APPLY_MARKER in combined
        failed_function = APPLY_FUNCTION_ERROR in combined
        ready = done and rcon_ready and (apply_complete if require_apply else True)
        if failed_function or ready:
            return {
                "ready": ready and not failed_function,
                "done": done,
                "rcon_ready": rcon_ready,
                "apply_complete": apply_complete,
                "failed_function": failed_function,
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
        "apply_complete": APPLY_MARKER in combined,
        "failed_function": APPLY_FUNCTION_ERROR in combined,
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
        "data_sha256": digest(data_response),
        "has_expected_block": "Test passed" in check_response,
        "has_block_entity_data": "block data:" in data_response.lower(),
        "data_response_excerpt": data_response[:500],
    }


def collect_sut(client: RconClient, phase: str) -> dict[str, Any]:
    return {
        "phase": phase,
        "timestamp": now_iso(),
        "blocks": {name: check_block(client, name) for name in SUT_BLOCKS},
    }


def stop_server(proc: subprocess.Popen, client: RconClient | None, timeout: int = 60) -> dict[str, Any]:
    result: dict[str, Any] = {"stop_command_sent": False, "graceful": False}
    if client:
        try:
            client.command("stop")
            result["stop_command_sent"] = True
        except Exception as exc:  # noqa: BLE001
            result["stop_error"] = str(exc)
    try:
        proc.wait(timeout=timeout)
        result["graceful"] = True
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=20)
        result["killed"] = True
    result["returncode"] = proc.returncode
    return result


def run(args: argparse.Namespace) -> dict[str, Any]:
    report: dict[str, Any] = {
        "name": "Railcraft Task 6 headless tick/restart",
        "status": "started",
        "start_time": now_iso(),
        "server_dir": str(args.server_dir),
        "world": "world_railcraft_task5b",
        "tick_wait_seconds": args.tick_seconds,
        "phases": [],
    }

    proc1: subprocess.Popen | None = None
    rcon1: RconClient | None = None
    proc2: subprocess.Popen | None = None
    rcon2: RconClient | None = None

    try:
        # Phase 1: first start
        print("[Task6] Starting server (first run)...")
        proc1, out1, err1 = run_server(args.server_dir, "first")
        wait1 = wait_for_server(proc1, out1, 120, require_apply=False)
        report["phases"].append({"name": "first_start", **wait1, "out_log": str(out1), "err_log": str(err1)})
        if not wait1["ready"]:
            report["status"] = "failed_first_start"
            return report

        rcon1 = connect_rcon("127.0.0.1", 25581, "test123", 30)

        # Apply datapack manually (load tag doesn't auto-trigger for existing worlds)
        print("[Task6] Applying datapack via RCON...")
        apply_resp = rcon1.command("function railcraft_task5b:apply")
        report["phases"][-1]["manual_apply_response"] = apply_resp
        time.sleep(3)

        # Force-load chunks around test area so blocks are accessible
        print("[Task6] Forceloading chunks...")
        rcon1.command("forceload add 192 192 336 208")
        time.sleep(8)  # wait for chunks to actually load

        # Check blocks right after apply
        print("[Task6] Checking blocks post-apply...")
        post_apply = collect_sut(rcon1, "post_apply")
        report["phases"][-1]["sut"] = post_apply

        # Wait for ticks
        print(f"[Task6] Waiting {args.tick_seconds}s for ticks...")
        time.sleep(args.tick_seconds)

        # Check blocks after ticks
        print("[Task6] Checking blocks after ticks...")
        after_ticks = collect_sut(rcon1, "after_ticks")
        report["phases"].append({"name": "after_ticks", **after_ticks})

        # TPS check
        tps_resp = rcon1.command("forge tps")
        report["phases"][-1]["tps_response"] = tps_resp

        # Save
        print("[Task6] Saving world...")
        rcon1.command("save-all flush")
        time.sleep(5)

        # Disable datapack so it won't reapply on restart
        print("[Task6] Disabling datapack...")
        disable_resp = rcon1.command("datapack disable file/railcraft_task5b")
        report["phases"][-1]["disable_datapack_response"] = disable_resp
        time.sleep(2)

        # Stop server
        print("[Task6] Stopping server...")
        stop1 = stop_server(proc1, rcon1)
        report["phases"].append({"name": "stop", **stop1})
        rcon1.disconnect()
        rcon1 = None
        proc1 = None

        # Phase 2: restart
        print("[Task6] Restarting server...")
        proc2, out2, err2 = run_server(args.server_dir, "restart")
        wait2 = wait_for_server(proc2, out2, 120, require_apply=False)
        report["phases"].append({"name": "restart", **wait2, "out_log": str(out2), "err_log": str(err2)})
        if not wait2["ready"]:
            report["status"] = "failed_restart"
            return report

        rcon2 = connect_rcon("127.0.0.1", 25581, "test123", 30)

        # Re-forceload chunks after restart (in case they were dropped)
        print("[Task6] Re-forceloading chunks after restart...")
        rcon2.command("forceload add 192 192 336 208")
        time.sleep(8)  # wait for chunks to actually load

        # Verify datapack did NOT reapply
        restart_log = read_text(out2)
        report["phases"][-1]["apply_marker_count"] = restart_log.count(APPLY_MARKER)
        report["phases"][-1]["failed_function_count"] = restart_log.count(APPLY_FUNCTION_ERROR)

        # Check blocks after restart
        print("[Task6] Checking blocks after restart...")
        after_restart = collect_sut(rcon2, "after_restart")
        report["phases"][-1]["sut"] = after_restart

        # Final TPS
        tps_resp2 = rcon2.command("forge tps")
        report["phases"][-1]["tps_response"] = tps_resp2

        # Determine overall status
        all_checks = (
            post_apply["blocks"]["mechanical_press"]["has_expected_block"]
            and after_ticks["blocks"]["mechanical_press"]["has_expected_block"]
            and after_restart["blocks"]["mechanical_press"]["has_expected_block"]
            and after_restart["blocks"]["observer"]["has_expected_block"]
            and after_restart["blocks"]["framed_slab"]["has_expected_block"]
        )
        report["status"] = "passed" if all_checks else "failed_persistence_check"

        # Stop
        print("[Task6] Stopping server (final)...")
        stop2 = stop_server(proc2, rcon2)
        report["phases"].append({"name": "stop_final", **stop2})
        rcon2.disconnect()
        rcon2 = None
        proc2 = None

    except Exception as exc:  # noqa: BLE001
        report["status"] = "error"
        report["error"] = str(exc)
        if rcon1:
            rcon1.disconnect()
        if rcon2:
            rcon2.disconnect()
        if proc1 and proc1.poll() is None:
            proc1.kill()
            proc1.wait(timeout=20)
        if proc2 and proc2.poll() is None:
            proc2.kill()
            proc2.wait(timeout=20)

    report["end_time"] = now_iso()
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Railcraft Task 6 headless tick/restart")
    parser.add_argument("--server-dir", type=Path, default=SERVER_DIR)
    parser.add_argument("--tick-seconds", type=int, default=180)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    report = run(args)
    report_path: Path = args.report
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nReport: {report_path}")
    print(f"Status: {report['status']}")


if __name__ == "__main__":
    main()
