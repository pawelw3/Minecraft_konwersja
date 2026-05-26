#!/usr/bin/env python3
"""Run Logistics Pipes Task 6 headless tick/restart verification."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SERVER_DIR = PROJECT_ROOT / "headless_server" / "1.18.2"
SCENARIO_DIR = Path(__file__).resolve().parent
DEFAULT_REPORT = SCENARIO_DIR / "logistics_pipes_task6_headless_tick_restart_report.json"
WORLD_NAME = "world_logistics_pipes_task5b"
DATAPACK_NAME = "logistics_pipes_task5b"
APPLY_FUNCTION = "logistics_pipes_task5b:apply"
APPLY_MARKER = "[LOGISTICS_PIPES_TASK5B] apply complete"

sys.path.insert(0, str(PROJECT_ROOT))
from src.converters.projectred.test_structures.headless_test.rcon_client import RconClient  # noqa: E402


SUT_BLOCKS = {
    "basic_transport_pipe": (48, 70, 48, "prettypipes:pipe"),
    "basic_logistics_pipe": (49, 70, 48, "prettypipes:pipe"),
    "supplier_pipe": (50, 70, 48, "prettypipes:pipe"),
    "provider_mk2_pipe": (51, 70, 48, "prettypipes:pipe"),
    "chassis_mk4_with_modules": (52, 70, 48, "prettypipes:pipe"),
    "chassis_mk4_unknown_modules": (53, 70, 48, "prettypipes:pipe"),
    "request_pipe": (54, 70, 48, "prettypipes:item_terminal"),
    "request_table_pipe": (55, 70, 48, "prettypipes:item_terminal"),
    "remote_orderer_pipe": (56, 70, 48, "prettypipes:item_terminal"),
    "crafting_table_basic": (48, 70, 50, "ae2:pattern_provider"),
    "crafting_table_fuzzy": (49, 70, 50, "ae2:pattern_provider"),
    "power_junction": (50, 70, 50, "prettypipes:pressurizer"),
    "security_station_placeholder": (51, 70, 50, "conversion_placeholders:block_entity_placeholder"),
}


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_server_properties(server_dir: Path, rcon_port: int, server_port: int) -> Path:
    server_props = server_dir / "server.properties"
    backup = server_dir / "server.properties.before_logistics_pipes_task6"
    if server_props.exists() and not backup.exists():
        shutil.copy2(server_props, backup)

    server_props.write_text(
        f"level-name={WORLD_NAME}\n"
        f"server-port={server_port}\n"
        f"rcon.port={rcon_port}\n"
        "rcon.password=test123\n"
        "enable-rcon=true\n"
        "enable-command-block=true\n"
        "online-mode=false\n"
        "allow-nether=false\n"
        "gamemode=creative\n"
        "difficulty=peaceful\n"
        "spawn-protection=0\n"
        "max-tick-time=-1\n"
        "motd=Logistics Pipes Task 6\n",
        encoding="utf-8",
    )
    return backup


def run_server(server_dir: Path, label: str) -> tuple[subprocess.Popen, Path, Path]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_log = server_dir / f"server_logistics_pipes_task6_{label}_{stamp}_out.log"
    err_log = server_dir / f"server_logistics_pipes_task6_{label}_{stamp}_err.log"
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


def wait_for_server(proc: subprocess.Popen, out_log: Path, timeout: int) -> dict[str, Any]:
    deadline = time.time() + timeout
    start = time.time()
    while time.time() < deadline:
        text = read_text(out_log)
        done = "Done (" in text
        rcon_ready = "RCON running on" in text
        if done and rcon_ready:
            return {"ready": True, "done": done, "rcon_ready": rcon_ready, "elapsed_seconds": round(time.time() - start, 1)}
        if proc.poll() is not None:
            break
        time.sleep(2)
    text = read_text(out_log)
    return {
        "ready": False,
        "done": "Done (" in text,
        "rcon_ready": "RCON running on" in text,
        "elapsed_seconds": round(time.time() - start, 1),
        "process_returncode": proc.poll(),
    }


def wait_for_marker(out_log: Path, marker: str, timeout: int) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        if marker in read_text(out_log):
            return True
        time.sleep(1)
    return False


def connect_rcon(port: int, timeout: int) -> RconClient:
    deadline = time.time() + timeout
    last_error: str | None = None
    while time.time() < deadline:
        client = RconClient("127.0.0.1", port, "test123", timeout=30.0)
        try:
            if client.connect():
                return client
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
            client.disconnect()
        time.sleep(2)
    raise RuntimeError(f"RCON not ready: {last_error}")


def forceload_chunks(client: RconClient) -> None:
    chunks = {(x >> 4, z >> 4) for x, _y, z, _block in SUT_BLOCKS.values()}
    for cx, cz in sorted(chunks):
        client.command(f"forceload add {cx * 16} {cz * 16}")
    time.sleep(3)


def check_block(client: RconClient, name: str) -> dict[str, Any]:
    x, y, z, expected_id = SUT_BLOCKS[name]
    check_response = client.command(f"execute if block {x} {y} {z} {expected_id}")
    data_response = client.command(f"data get block {x} {y} {z}")
    lower_data = data_response.lower()
    return {
        "name": name,
        "position": [x, y, z],
        "expected_id": expected_id,
        "check_response": check_response,
        "data_response_excerpt": data_response[:800],
        "data_sha256": digest(data_response),
        "has_expected_block": "Test passed" in check_response,
        "has_block_entity_data": "block data:" in lower_data or "has the following block data" in lower_data,
    }


def collect_sut(client: RconClient, phase: str) -> dict[str, Any]:
    block_checks = {name: check_block(client, name) for name in SUT_BLOCKS}
    return {
        "phase": phase,
        "timestamp": now_iso(),
        "blocks": block_checks,
        "blocks_passed": sum(1 for check in block_checks.values() if check["has_expected_block"]),
        "block_entities_with_data": sum(1 for check in block_checks.values() if check["has_block_entity_data"]),
    }


def stop_server(proc: subprocess.Popen, client: RconClient | None, timeout: int = 60) -> dict[str, Any]:
    result: dict[str, Any] = {"stop_command_sent": False, "graceful": False}
    if client:
        try:
            client.command("save-all flush")
            time.sleep(2)
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


def disable_datapack_load(world_dir: Path) -> Path | None:
    load_json = world_dir / "datapacks" / DATAPACK_NAME / "data" / "minecraft" / "tags" / "functions" / "load.json"
    if load_json.exists():
        disabled = load_json.with_suffix(".json.disabled")
        if disabled.exists():
            disabled.unlink()
        load_json.rename(disabled)
        return disabled
    return None


def enable_datapack_load(disabled: Path | None) -> None:
    if disabled and disabled.exists():
        target = disabled.with_suffix("").with_suffix(".json")
        if target.exists():
            target.unlink()
        disabled.rename(target)


def analyze_log(out_log: Path, err_log: Path) -> dict[str, Any]:
    out_text = read_text(out_log)
    err_text = read_text(err_log)
    combined = out_text + "\n" + err_text
    relevant_errors = []
    relevant_warnings = []
    for line in combined.splitlines():
        low = line.lower()
        if any(key in low for key in ("prettypipes", "logistics_pipes_task5b", "pattern_provider", "block_entity_placeholder")):
            if "error" in low or "fatal" in low or "exception" in low:
                relevant_errors.append(line.strip())
            elif "warn" in low:
                relevant_warnings.append(line.strip())
    return {
        "apply_marker_count": out_text.count(APPLY_MARKER),
        "relevant_errors_found": len(relevant_errors),
        "relevant_errors": relevant_errors[:20],
        "relevant_warnings_found": len(relevant_warnings),
        "relevant_warnings": relevant_warnings[:20],
        "has_unknown_block": "Unknown block" in combined,
        "has_skipping_block_entity": "Skipping BlockEntity" in combined,
        "has_crash": "Crash report" in combined or "Encountered an unexpected exception" in combined,
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    world_dir = args.server_dir / WORLD_NAME
    disabled_load = disable_datapack_load(world_dir)
    backup = write_server_properties(args.server_dir, args.rcon_port, args.server_port)

    report: dict[str, Any] = {
        "mod": "Logistics Pipes",
        "task": "6",
        "started_at": now_iso(),
        "server_dir": str(args.server_dir),
        "world": WORLD_NAME,
        "tick_wait_seconds": args.tick_seconds,
        "server_properties_backup": str(backup) if backup.exists() else None,
        "phases": [],
    }

    proc1: subprocess.Popen | None = None
    client1: RconClient | None = None
    proc2: subprocess.Popen | None = None
    client2: RconClient | None = None

    try:
        print("[Task 6] Phase 1: first boot + apply + ticks...")
        proc1, out1, err1 = run_server(args.server_dir, "first")
        wait1 = wait_for_server(proc1, out1, args.boot_timeout)
        phase1: dict[str, Any] = {"name": "first_boot", **wait1, "out_log": str(out1), "err_log": str(err1)}
        report["phases"].append(phase1)
        if not wait1["ready"]:
            phase1["log_analysis"] = analyze_log(out1, err1)
            report["status"] = "failed_first_boot"
            return report

        client1 = connect_rcon(args.rcon_port, timeout=30)
        client1.command("say [LOGISTICS_PIPES_TASK6] first boot ready")
        forceload_chunks(client1)

        apply_response = client1.command(f"function {APPLY_FUNCTION}")
        phase1["manual_apply_response"] = apply_response
        phase1["apply_marker_seen"] = wait_for_marker(out1, APPLY_MARKER, timeout=60)
        phase1["post_apply"] = collect_sut(client1, "post_apply")

        print(f"[Task 6] Waiting {args.tick_seconds}s for ticks...")
        time.sleep(args.tick_seconds)
        phase1["after_ticks"] = collect_sut(client1, "after_ticks")
        phase1["tps_response"] = client1.command("forge tps")
        phase1["stop"] = stop_server(proc1, client1)
        client1.disconnect()
        client1 = None
        proc1 = None
        phase1["log_analysis"] = analyze_log(out1, err1)

        print("[Task 6] Phase 2: restart + persistence check...")
        proc2, out2, err2 = run_server(args.server_dir, "restart")
        wait2 = wait_for_server(proc2, out2, args.boot_timeout)
        phase2: dict[str, Any] = {"name": "restart", **wait2, "out_log": str(out2), "err_log": str(err2)}
        report["phases"].append(phase2)
        if not wait2["ready"]:
            phase2["log_analysis"] = analyze_log(out2, err2)
            report["status"] = "failed_restart"
            return report

        client2 = connect_rcon(args.rcon_port, timeout=30)
        client2.command("say [LOGISTICS_PIPES_TASK6] restart ready")
        forceload_chunks(client2)
        phase2["after_restart"] = collect_sut(client2, "after_restart")
        phase2["tps_response"] = client2.command("forge tps")
        phase2["stop"] = stop_server(proc2, client2)
        client2.disconnect()
        client2 = None
        proc2 = None
        phase2["log_analysis"] = analyze_log(out2, err2)

        expected = len(SUT_BLOCKS)
        phase1_pass = (
            phase1.get("ready")
            and phase1.get("apply_marker_seen")
            and phase1["post_apply"]["blocks_passed"] == expected
            and phase1["after_ticks"]["blocks_passed"] == expected
            and phase1["after_ticks"]["block_entities_with_data"] == expected
            and phase1["log_analysis"]["relevant_errors_found"] == 0
            and not phase1["log_analysis"]["has_unknown_block"]
            and not phase1["log_analysis"]["has_skipping_block_entity"]
            and not phase1["log_analysis"]["has_crash"]
        )
        phase2_pass = (
            phase2.get("ready")
            and phase2["after_restart"]["blocks_passed"] == expected
            and phase2["after_restart"]["block_entities_with_data"] == expected
            and phase2["log_analysis"]["relevant_errors_found"] == 0
            and not phase2["log_analysis"]["has_unknown_block"]
            and not phase2["log_analysis"]["has_skipping_block_entity"]
            and not phase2["log_analysis"]["has_crash"]
        )
        report["status"] = "passed" if phase1_pass and phase2_pass else "failed_checks"
        report["overall_pass"] = bool(phase1_pass and phase2_pass)
        return report

    finally:
        if client1:
            client1.disconnect()
        if client2:
            client2.disconnect()
        if proc1 and proc1.poll() is None:
            stop_server(proc1, None)
        if proc2 and proc2.poll() is None:
            stop_server(proc2, None)
        enable_datapack_load(disabled_load)
        report["finished_at"] = now_iso()
        write_json(args.report, report)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-dir", type=Path, default=SERVER_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--tick-seconds", type=int, default=180)
    parser.add_argument("--boot-timeout", type=int, default=180)
    parser.add_argument("--rcon-port", type=int, default=25582)
    parser.add_argument("--server-port", type=int, default=25572)
    args = parser.parse_args()

    report = run(args)
    print(f"Report -> {args.report}")
    print(f"Overall: {'PASS' if report.get('overall_pass') else 'FAIL'}")
    return 0 if report.get("overall_pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
