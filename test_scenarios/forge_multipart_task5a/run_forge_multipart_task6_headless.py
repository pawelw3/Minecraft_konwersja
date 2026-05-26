#!/usr/bin/env python3
"""Run ForgeMultipart Task 6 headless tick/restart verification."""

from __future__ import annotations

import argparse
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
DEFAULT_REPORT = SCENARIO_DIR / "forge_multipart_task6_headless_report.json"

sys.path.insert(0, str(PROJECT_ROOT))
from src.converters.projectred.test_structures.headless_test.rcon_client import RconClient  # noqa: E402


EVENTS_PATH = PROJECT_ROOT / "output/forge_multipart/task5a_events_1182.json"
APPLY_MARKER = "[FORGE_MULTIPART_TASK5B] apply complete"


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_samples() -> list[tuple[int, int, int]]:
    events = json.loads(EVENTS_PATH.read_text(encoding="utf-8"))
    samples = []
    for event in events.get("events", []):
        if event.get("op") != "set_block_entity":
            continue
        x, y, z = event["pos"]
        samples.append((int(x), int(y), int(z)))
    return samples


def run_server(server_dir: Path, label: str) -> tuple[subprocess.Popen, Path, Path]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_log = server_dir / f"server_forge_multipart_task6_{label}_{stamp}_out.log"
    err_log = server_dir / f"server_forge_multipart_task6_{label}_{stamp}_err.log"
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


def wait_for_server(proc: subprocess.Popen, out_log: Path, timeout: int, require_apply: bool) -> dict[str, Any]:
    start = time.time()
    deadline = start + timeout
    while time.time() < deadline:
        text = read_text(out_log)
        done = "Done (" in text
        rcon_ready = "RCON running on" in text
        apply_complete = APPLY_MARKER in text
        ready = done and rcon_ready and (apply_complete if require_apply else True)
        if ready:
            return {
                "ready": True,
                "done": done,
                "rcon_ready": rcon_ready,
                "apply_complete": apply_complete,
                "elapsed_seconds": round(time.time() - start, 1),
            }
        if proc.poll() is not None:
            break
        time.sleep(2)
    text = read_text(out_log)
    return {
        "ready": False,
        "done": "Done (" in text,
        "rcon_ready": "RCON running on" in text,
        "apply_complete": APPLY_MARKER in text,
        "elapsed_seconds": round(time.time() - start, 1),
    }


def connect_rcon(port: int, password: str, timeout: int) -> RconClient:
    deadline = time.time() + timeout
    last_error = ""
    while time.time() < deadline:
        client = RconClient("127.0.0.1", port, password, timeout=30.0)
        try:
            if client.connect():
                return client
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
            client.disconnect()
        time.sleep(2)
    raise RuntimeError(f"RCON unavailable: {last_error}")


def command(client: RconClient, cmd: str) -> dict[str, str]:
    return {"command": cmd, "response": client.command(cmd)}


def collect_blocks(client: RconClient, phase: str, samples: list[tuple[int, int, int]]) -> dict[str, Any]:
    blocks = []
    for x, y, z in samples:
        check = client.command(f"execute if block {x} {y} {z} cb_multipart:multipart")
        data = client.command(f"data get block {x} {y} {z}")
        blocks.append(
            {
                "pos": [x, y, z],
                "has_block": "Test passed" in check,
                "has_block_entity": "block data:" in data.lower(),
                "data_excerpt": data[:700],
            }
        )
    return {
        "phase": phase,
        "total": len(blocks),
        "block_ok": sum(1 for block in blocks if block["has_block"]),
        "block_entity_ok": sum(1 for block in blocks if block["has_block_entity"]),
        "blocks": blocks,
    }


def stop_server(proc: subprocess.Popen, client: RconClient | None) -> dict[str, Any]:
    result = {"stop_command_sent": False, "graceful": False}
    if client is not None:
        try:
            client.command("stop")
            result["stop_command_sent"] = True
        except Exception as exc:  # noqa: BLE001
            result["error"] = str(exc)
    try:
        proc.wait(timeout=80)
        result["graceful"] = True
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=20)
        result["killed"] = True
    result["returncode"] = proc.returncode
    return result


def run(args: argparse.Namespace) -> dict[str, Any]:
    report: dict[str, Any] = {
        "name": "ForgeMultipart Task 6 headless tick/restart",
        "status": "started",
        "start_time": now(),
        "world": "world_forge_multipart_task5b",
        "tick_seconds": args.tick_seconds,
    }
    samples = load_samples()
    report["samples"] = [list(sample) for sample in samples]

    proc1 = proc2 = None
    rcon1 = rcon2 = None
    try:
        proc1, out1, err1 = run_server(args.server_dir, "first")
        first = wait_for_server(proc1, out1, args.startup_timeout, require_apply=True)
        report["first_start"] = {"pid": proc1.pid, "stdout": str(out1), "stderr": str(err1), **first}
        if not first["ready"]:
            raise RuntimeError("first server start failed")

        rcon1 = connect_rcon(args.rcon_port, args.rcon_password, 45)
        report["force_load"] = [
            command(rcon1, "forceload add 0 0 14 2"),
            command(rcon1, "tp @a 7 66 1"),
        ]
        report["initial"] = collect_blocks(rcon1, "initial", samples)
        time.sleep(args.tick_seconds)
        report["after_ticks"] = collect_blocks(rcon1, "after_ticks", samples)
        report["tps"] = command(rcon1, "forge tps")
        report["save_all"] = command(rcon1, "save-all flush")
        report["first_stop"] = stop_server(proc1, rcon1)
        rcon1.disconnect()
        rcon1 = None
        proc1 = None

        time.sleep(5)
        proc2, out2, err2 = run_server(args.server_dir, "restart")
        second = wait_for_server(proc2, out2, args.startup_timeout, require_apply=True)
        report["restart"] = {"pid": proc2.pid, "stdout": str(out2), "stderr": str(err2), **second}
        if not second["ready"]:
            raise RuntimeError("restart server start failed")

        rcon2 = connect_rcon(args.rcon_port, args.rcon_password, 45)
        report["restart_force_load"] = [command(rcon2, "forceload add 0 0 14 2")]
        time.sleep(5)
        report["after_restart"] = collect_blocks(rcon2, "after_restart", samples)
        report["restart_stop"] = stop_server(proc2, rcon2)
        rcon2.disconnect()
        rcon2 = None
        proc2 = None

        phases = [report["initial"], report["after_ticks"], report["after_restart"]]
        ok = all(p["block_ok"] == len(samples) and p["block_entity_ok"] == len(samples) for p in phases)
        report["status"] = "passed" if ok else "failed"
    except Exception as exc:  # noqa: BLE001
        report["status"] = "failed"
        report["error"] = str(exc)
    finally:
        if proc1 is not None:
            report["first_cleanup_stop"] = stop_server(proc1, rcon1)
        if rcon1 is not None:
            rcon1.disconnect()
        if proc2 is not None:
            report["restart_cleanup_stop"] = stop_server(proc2, rcon2)
        if rcon2 is not None:
            rcon2.disconnect()
        report["end_time"] = now()
        write_json(args.report, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="ForgeMultipart Task 6 headless verification")
    parser.add_argument("--server-dir", type=Path, default=SERVER_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--rcon-port", type=int, default=25691)
    parser.add_argument("--rcon-password", default="test123")
    parser.add_argument("--startup-timeout", type=int, default=180)
    parser.add_argument("--tick-seconds", type=int, default=180)
    args = parser.parse_args()
    report = run(args)
    print(f"Status: {report['status']}")
    print(f"Report: {args.report}")
    sys.exit(0 if report["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
