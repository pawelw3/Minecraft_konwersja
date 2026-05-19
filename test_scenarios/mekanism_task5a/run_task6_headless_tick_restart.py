#!/usr/bin/env python3
"""Run Mekanism Task 6 headless tick/restart verification.

The 5B datapack materializes the converted structure on load. This runner
starts the server once with that datapack enabled, powers the TEST_START bus,
checks block entity NBT after ticks, disables the datapack, saves, restarts,
and checks that selected Mekanism block entities persisted without reapply.
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
DEFAULT_REPORT = Path(__file__).resolve().parent / "mekanism_task6_headless_tick_restart_report.json"

sys.path.insert(0, str(PROJECT_ROOT))
from src.converters.projectred.test_structures.headless_test.rcon_client import RconClient  # noqa: E402


SUT_BLOCKS = {
    "elite_smelting_factory": (118, 64, 108, "mekanism:elite_smelting_factory"),
    "advanced_energy_cube": (112, 64, 110, "mekanism:advanced_energy_cube"),
}


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def run_server(server_dir: Path, label: str) -> tuple[subprocess.Popen, Path, Path]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_log = server_dir / f"server_mekanism_task6_{label}_{stamp}_out.log"
    err_log = server_dir / f"server_mekanism_task6_{label}_{stamp}_err.log"
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


def wait_for_server(proc: subprocess.Popen, out_log: Path, latest_log: Path, timeout: int) -> dict[str, Any]:
    deadline = time.time() + timeout
    start = time.time()
    while time.time() < deadline:
        # Use this process' stdout as the readiness source. latest.log can still
        # contain markers from a previous run while Forge is replacing it.
        combined = read_text(out_log)
        done = "Done (" in combined
        rcon_ready = "RCON running on" in combined
        apply_complete = "[MEKANISM_TASK5B] apply complete" in combined
        failed_function = "Failed to load function mekanism_task5b:apply" in combined
        if failed_function or (done and rcon_ready):
            return {
                "ready": done and rcon_ready and not failed_function,
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
        "apply_complete": "[MEKANISM_TASK5B] apply complete" in combined,
        "failed_function": "Failed to load function mekanism_task5b:apply" in combined,
        "elapsed_seconds": round(time.time() - start, 1),
    }


def connect_rcon(host: str, port: int, password: str, timeout: int) -> RconClient:
    client = RconClient(host, port, password, timeout=30.0)
    deadline = time.time() + timeout
    last_error: str | None = None
    while time.time() < deadline:
        try:
            if client.connect():
                return client
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
        time.sleep(2)
    raise RuntimeError(f"RCON not ready: {last_error}")


def command(client: RconClient, cmd: str) -> dict[str, str]:
    response = client.command(cmd)
    return {"command": cmd, "response": response}


def data_get_block(client: RconClient, name: str) -> dict[str, Any]:
    x, y, z, expected_id = SUT_BLOCKS[name]
    response = client.command(f"data get block {x} {y} {z}")
    return {
        "name": name,
        "position": [x, y, z],
        "expected_id": expected_id,
        "response": response,
        "sha256": digest(response),
        "has_expected_id": expected_id in response,
        "has_block_data": "block data:" in response.lower(),
    }


def collect_sut(client: RconClient, phase: str) -> dict[str, Any]:
    return {
        "phase": phase,
        "timestamp": now_iso(),
        "blocks": {name: data_get_block(client, name) for name in SUT_BLOCKS},
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
    latest_log = args.server_dir / "logs/latest.log"
    report: dict[str, Any] = {
        "name": "Mekanism Task 6 headless tick/restart",
        "status": "started",
        "start_time": now_iso(),
        "server_dir": str(args.server_dir),
        "world": "world_mekanism_task5b",
        "tick_wait_seconds": args.tick_seconds,
        "phases": [],
    }

    proc1: subprocess.Popen | None = None
    rcon1: RconClient | None = None
    proc2: subprocess.Popen | None = None
    rcon2: RconClient | None = None
    try:
        proc1, out1, err1 = run_server(args.server_dir, "first")
        startup1 = wait_for_server(proc1, out1, latest_log, args.startup_timeout)
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
                    command(rcon1, "forceload add 100 96 134 124"),
                    command(rcon1, "tp @a 118 66 108"),
                ],
            }
        )
        report["phases"].append({"phase": "initial_nbt", "data": collect_sut(rcon1, "initial")})
        report["phases"].append(
            {
                "phase": "test_start",
                "commands": [
                    command(rcon1, "setblock 100 65 96 minecraft:lever[face=floor,facing=east,powered=true] replace"),
                    command(rcon1, "say [MEKANISM_TASK6] TEST_START powered"),
                ],
            }
        )
        time.sleep(8)
        log_after_start = read_text(latest_log)
        report["phases"].append(
            {
                "phase": "redstone_assert",
                "pass_marker_found": "[TEST_MEKANISM_5A] redstone harness reached assertion bus PASS" in log_after_start,
            }
        )

        time.sleep(args.tick_seconds)
        report["phases"].append({"phase": "after_ticks_nbt", "data": collect_sut(rcon1, "after_ticks")})
        report["phases"].append({"phase": "tps", "response": rcon1.command("forge tps")})
        report["phases"].append({"phase": "disable_datapack", "response": rcon1.command('datapack disable "file/mekanism_task5b"')})
        report["phases"].append({"phase": "save_all", "response": rcon1.command("save-all flush")})
        stop1 = stop_server(proc1, rcon1)
        rcon1.disconnect()
        rcon1 = None
        report["first_stop"] = stop1
        proc1 = None

        time.sleep(5)
        proc2, out2, err2 = run_server(args.server_dir, "restart")
        startup2 = wait_for_server(proc2, out2, latest_log, args.startup_timeout)
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
        report["phases"].append({"phase": "restart_nbt", "data": collect_sut(rcon2, "restart")})
        report["phases"].append({"phase": "restart_enabled_datapacks", "response": rcon2.command("datapack list enabled")})
        report["phases"].append({"phase": "restart_tps", "response": rcon2.command("forge tps")})
        stop2 = stop_server(proc2, rcon2)
        rcon2.disconnect()
        rcon2 = None
        report["restart_stop"] = stop2
        proc2 = None

        first_logs = read_text(out1)
        restart_logs = read_text(out2)
        restart_apply = "[MEKANISM_TASK5B] apply complete" in restart_logs
        redstone_pass = next(
            phase["pass_marker_found"] for phase in report["phases"] if phase.get("phase") == "redstone_assert"
        )
        restart_nbt = next(phase["data"] for phase in report["phases"] if phase.get("phase") == "restart_nbt")
        nbt_ok = all(block["has_expected_id"] and block["has_block_data"] for block in restart_nbt["blocks"].values())
        report["acceptance"] = {
            "server_started_first": report["first_start"]["ready"],
            "materialization_function_loaded": "[MEKANISM_TASK5B] apply complete" in first_logs,
            "redstone_pass_marker_found": redstone_pass,
            "server_restarted": report["restart"]["ready"],
            "datapack_not_reapplied_on_restart": not restart_apply,
            "selected_block_entities_retained_after_restart": nbt_ok,
            "failed_function_absent": "Failed to load function mekanism_task5b:apply" not in first_logs,
        }
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
    if "error" in report:
        print(f"Error: {report['error']}")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
