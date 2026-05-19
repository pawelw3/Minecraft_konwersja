#!/usr/bin/env python3
"""Run AE2 Task 6 headless tick/restart verification.

The 5B datapack materializes the converted AE2 structure on load. This runner
starts the server once with the datapack enabled, powers the redstone harness,
collects selected AE2 block/block-entity state after ticks, disables the
datapack, saves, restarts, and checks persistence without reapplying 5B.
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
DEFAULT_REPORT = SCENARIO_DIR / "ae2_task6_headless_tick_restart_report.json"

sys.path.insert(0, str(PROJECT_ROOT))
from src.converters.projectred.test_structures.headless_test.rcon_client import RconClient  # noqa: E402


SUT_BLOCKS = {
    "cable_bus_fallback": (100, 64, 100, "ae2:fluix_block"),
    "drive": (127, 64, 103, "ae2:drive"),
    "interface": (109, 64, 106, "ae2:interface"),
    "pattern_provider": (109, 64, 105, "ae2:pattern_provider"),
    "quantum_link": (118, 64, 106, "ae2:quantum_link"),
    "spatial_io_port": (100, 64, 109, "ae2:spatial_io_port"),
    "quartz_growth_accelerator": (124, 64, 106, "ae2:quartz_growth_accelerator"),
}

REDSTONE_MARKER = "AE2_TASK5A_REDSTONE_PASS"
APPLY_MARKER = "[AE2_TASK5B] apply complete"
APPLY_FUNCTION_ERROR = "Failed to load function ae2_task5b:apply"
GENERIC_KEY_WARNING = "Cannot deserialize generic key"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def run_server(server_dir: Path, label: str) -> tuple[subprocess.Popen, Path, Path]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_log = server_dir / f"server_ae2_task6_{label}_{stamp}_out.log"
    err_log = server_dir / f"server_ae2_task6_{label}_{stamp}_err.log"
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


def wait_for_server(proc: subprocess.Popen, out_log: Path, timeout: int, require_apply: bool) -> dict[str, Any]:
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


def command(client: RconClient, cmd: str) -> dict[str, str]:
    response = client.command(cmd)
    return {"command": cmd, "response": response}


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


def count_marker(text: str, marker: str) -> int:
    return text.count(marker)


def run(args: argparse.Namespace) -> dict[str, Any]:
    report: dict[str, Any] = {
        "name": "AE2 Task 6 headless tick/restart",
        "status": "started",
        "start_time": now_iso(),
        "server_dir": str(args.server_dir),
        "world": "world_ae2_task5b",
        "tick_wait_seconds": args.tick_seconds,
        "phases": [],
    }

    proc1: subprocess.Popen | None = None
    rcon1: RconClient | None = None
    proc2: subprocess.Popen | None = None
    rcon2: RconClient | None = None
    try:
        proc1, out1, err1 = run_server(args.server_dir, "first")
        startup1 = wait_for_server(proc1, out1, args.startup_timeout, require_apply=True)
        report["first_start"] = {
            "pid": proc1.pid,
            "stdout": str(out1),
            "stderr": str(err1),
            **startup1,
        }
        if not startup1["ready"]:
            raise RuntimeError("First server start failed")

        rcon1 = connect_rcon(args.rcon_host, args.rcon_port, args.rcon_password, 45)
        report["phases"].append({"phase": "rcon_first", "status": "ok", "list": rcon1.command("list")})
        report["phases"].append(
            {
                "phase": "force_load",
                "commands": [
                    command(rcon1, "forceload add 96 96 134 110"),
                    command(rcon1, "tp @a 112 66 103"),
                ],
            }
        )
        report["phases"].append({"phase": "initial_state", "data": collect_sut(rcon1, "initial")})
        report["phases"].append(
            {
                "phase": "test_start",
                "commands": [
                    command(rcon1, "setblock 96 65 96 minecraft:lever[face=floor,facing=east,powered=true] replace"),
                    command(rcon1, "say [AE2_TASK6] TEST_START powered"),
                ],
            }
        )
        time.sleep(8)
        first_log_after_start = read_text(out1)
        report["phases"].append(
            {
                "phase": "redstone_assert",
                "pass_marker_found": REDSTONE_MARKER in first_log_after_start,
                "marker_count": count_marker(first_log_after_start, REDSTONE_MARKER),
            }
        )

        time.sleep(args.tick_seconds)
        report["phases"].append({"phase": "after_ticks_state", "data": collect_sut(rcon1, "after_ticks")})
        report["phases"].append({"phase": "tps", "response": rcon1.command("forge tps")})
        report["phases"].append({"phase": "enabled_datapacks_before_disable", "response": rcon1.command("datapack list enabled")})
        report["phases"].append({"phase": "disable_datapack", "response": rcon1.command('datapack disable "file/ae2_task5b"')})
        report["phases"].append({"phase": "enabled_datapacks_after_disable", "response": rcon1.command("datapack list enabled")})
        report["phases"].append({"phase": "save_all", "response": rcon1.command("save-all flush")})
        stop1 = stop_server(proc1, rcon1)
        rcon1.disconnect()
        rcon1 = None
        report["first_stop"] = stop1
        proc1 = None

        time.sleep(5)
        proc2, out2, err2 = run_server(args.server_dir, "restart")
        startup2 = wait_for_server(proc2, out2, args.startup_timeout, require_apply=False)
        report["restart"] = {
            "pid": proc2.pid,
            "stdout": str(out2),
            "stderr": str(err2),
            **startup2,
        }
        if not startup2["ready"]:
            raise RuntimeError("Restart failed")

        rcon2 = connect_rcon(args.rcon_host, args.rcon_port, args.rcon_password, 45)
        report["phases"].append({"phase": "rcon_restart", "status": "ok", "list": rcon2.command("list")})
        report["phases"].append({"phase": "restart_state", "data": collect_sut(rcon2, "restart")})
        report["phases"].append({"phase": "restart_enabled_datapacks", "response": rcon2.command("datapack list enabled")})
        report["phases"].append({"phase": "restart_tps", "response": rcon2.command("forge tps")})
        stop2 = stop_server(proc2, rcon2)
        rcon2.disconnect()
        rcon2 = None
        report["restart_stop"] = stop2
        proc2 = None

        first_logs = read_text(out1)
        restart_logs = read_text(out2)
        redstone_phase = next(phase for phase in report["phases"] if phase.get("phase") == "redstone_assert")
        restart_state = next(phase["data"] for phase in report["phases"] if phase.get("phase") == "restart_state")
        after_ticks_state = next(phase["data"] for phase in report["phases"] if phase.get("phase") == "after_ticks_state")

        restart_blocks_ok = all(block["has_expected_block"] for block in restart_state["blocks"].values())
        after_ticks_blocks_ok = all(block["has_expected_block"] for block in after_ticks_state["blocks"].values())
        block_entity_observed = {
            name: block["has_block_entity_data"]
            for name, block in restart_state["blocks"].items()
        }
        report["log_findings"] = {
            "first_apply_marker_count": count_marker(first_logs, APPLY_MARKER),
            "restart_apply_marker_count": count_marker(restart_logs, APPLY_MARKER),
            "generic_key_warning_first": GENERIC_KEY_WARNING in first_logs,
            "generic_key_warning_restart": GENERIC_KEY_WARNING in restart_logs,
            "chunk_old_noise_first": "No key old_noise" in first_logs,
            "chunk_old_noise_restart": "No key old_noise" in restart_logs,
        }
        report["acceptance"] = {
            "server_started_first": report["first_start"]["ready"],
            "materialization_function_loaded": APPLY_MARKER in first_logs,
            "redstone_pass_marker_found": redstone_phase["pass_marker_found"],
            "selected_blocks_present_after_ticks": after_ticks_blocks_ok,
            "server_restarted": report["restart"]["ready"],
            "datapack_not_reapplied_on_restart": APPLY_MARKER not in restart_logs,
            "selected_blocks_retained_after_restart": restart_blocks_ok,
            "failed_function_absent": APPLY_FUNCTION_ERROR not in first_logs and APPLY_FUNCTION_ERROR not in restart_logs,
        }
        report["block_entity_observed_after_restart"] = block_entity_observed
        report["status"] = "passed" if all(report["acceptance"].values()) else "failed"
    except Exception as exc:  # noqa: BLE001
        report["status"] = "failed"
        report["error"] = str(exc)
        if proc1 is not None:
            report["first_stop_after_error"] = stop_server(proc1, rcon1)
        if proc2 is not None:
            report["restart_stop_after_error"] = stop_server(proc2, rcon2)
    finally:
        if rcon1:
            rcon1.disconnect()
        if rcon2:
            rcon2.disconnect()
        report["end_time"] = now_iso()
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-dir", type=Path, default=SERVER_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--rcon-host", default="127.0.0.1")
    parser.add_argument("--rcon-port", type=int, default=25575)
    parser.add_argument("--rcon-password", default="ae2test123")
    parser.add_argument("--startup-timeout", type=int, default=220)
    parser.add_argument("--tick-seconds", type=int, default=180)
    args = parser.parse_args()
    report = run(args)
    print(f"Status: {report['status']}")
    print(f"Report: {args.report}")
    if "acceptance" in report:
        for key, value in report["acceptance"].items():
            print(f"{key}: {value}")
    if "log_findings" in report:
        for key, value in report["log_findings"].items():
            print(f"{key}: {value}")
    if "error" in report:
        print(f"Error: {report['error']}")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
