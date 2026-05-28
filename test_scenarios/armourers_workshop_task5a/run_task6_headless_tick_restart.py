#!/usr/bin/env python3
"""Run Armourer's Workshop Task 6 headless tick/restart verification.

Sequence:
  1. Install server.properties with world_armourers_workshop_task5b
  2. Start Forge 1.18.2 headless server
  3. Apply armourers_workshop_task5b datapack via RCON
  4. Check converted AW blocks via RCON
  5. Wait ticks -> re-check
  6. save-all -> stop -> restart -> re-check
  7. Analyze logs for errors / crash reports
  8. Write JSON + Markdown report + Handoff
"""

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

DEFAULT_REPORT = SCENARIO_DIR / "armourers_workshop_task6_headless_tick_restart_report.json"
SERVER_PROPERTIES_TEMPLATE = SCENARIO_DIR / "server_armourers_workshop_task5b.properties"
REPORT_MD = SCENARIO_DIR / "ARMOURERS_WORKSHOP_TASK6_REPORT.md"
HANDOFF = SCENARIO_DIR / "HANDOFF_ARMOURERS_WORKSHOP_TASK6.md"

sys.path.insert(0, str(PROJECT_ROOT))
from src.converters.projectred.test_structures.headless_test.rcon_client import RconClient  # noqa: E402


WORLD_NAME = "world_armourers_workshop_task5b"
DATAPACK_NAME = "armourers_workshop_task5b"
APPLY_FUNCTION = "armourers_workshop_task5b:apply"
APPLY_MARKER = "[AW_TASK5B] apply complete"

# Positions from armourers_workshop_task5a_converted_patch_1182.json
# (x, y, z, expected_block_id)
SUT_BLOCKS: dict[str, tuple[int, int, int, str]] = {
    # AW equipment blocks (row z=160)
    "skin_library":             (160, 70, 160, "armourers_workshop:skin-library"),
    "skin_library_global":      (163, 70, 160, "armourers_workshop:skin-library-global"),
    "skinning_table":           (166, 70, 160, "armourers_workshop:skinning-table"),
    "dye_table":                (169, 70, 160, "armourers_workshop:dye-table"),
    "colour_mixer":             (172, 70, 160, "armourers_workshop:colour-mixer"),
    "armourer":                 (175, 70, 160, "armourers_workshop:armourer"),
    "bounding_box":             (178, 70, 160, "armourers_workshop:bounding-box"),
    "skin_cube":                (181, 70, 160, "armourers_workshop:skin-cube"),
    # AW simple blocks (row z=163)
    "skin_cube_glass":          (160, 70, 163, "armourers_workshop:skin-cube-glass"),
    "skin_cube_glowing":        (163, 70, 163, "armourers_workshop:skin-cube-glowing"),
    "skin_cube_glass_glowing":  (166, 70, 163, "armourers_workshop:skin-cube-glass-glowing"),
    "hologram_projector":       (169, 70, 163, "armourers_workshop:hologram-projector"),
    "outfit_maker":             (181, 70, 163, "armourers_workshop:outfit-maker"),
    # Placeholders (mannequin, doll, miniArmourer)
    "mannequin_inv_placeholder":     (172, 70, 163, "conversion_placeholders:inventory_placeholder"),
    "doll_be_placeholder":           (175, 70, 163, "conversion_placeholders:block_entity_placeholder"),
    "mini_armourer_be_placeholder":  (178, 70, 163, "conversion_placeholders:block_entity_placeholder"),
    # Skinnables (row z=166)
    "skinnable_barrel_south":   (160, 70, 166, "armourers_workshop:skinnable"),
    "skinnable_noskin_north":   (160, 70, 169, "armourers_workshop:skinnable"),
}

CRITICAL_LOG_PATTERNS = [
    f"Failed to load function {DATAPACK_NAME}:apply",
    "Unknown or incomplete command",
    "Unknown block type",
    "Couldn't load chunk",
    "Skipping BlockEntity",
    "Exception caught during firing event",
]


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

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


def write_text_file(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


# ──────────────────────────────────────────────────────────────────────────────
# Server lifecycle
# ──────────────────────────────────────────────────────────────────────────────

def install_server_properties(server_dir: Path) -> Path | None:
    target = server_dir / "server.properties"
    backup = server_dir / "server.properties.before_armourers_workshop_task6"
    if target.exists():
        shutil.copy2(target, backup)
    shutil.copy2(SERVER_PROPERTIES_TEMPLATE, target)
    return backup if backup.exists() else None


def run_server(server_dir: Path, label: str) -> tuple[subprocess.Popen, Path, Path]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_log = server_dir / f"server_armourers_workshop_task6_{label}_{stamp}_out.log"
    err_log = server_dir / f"server_armourers_workshop_task6_{label}_{stamp}_err.log"
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
        combined = read_text(out_log)
        done = "Done (" in combined
        rcon_ready = "RCON running on" in combined
        if done and rcon_ready:
            return {"ready": True, "done": done, "rcon_ready": rcon_ready, "elapsed_seconds": round(time.time() - start, 1)}
        if proc.poll() is not None:
            break
        time.sleep(2)
    combined = read_text(out_log)
    return {"ready": False, "done": "Done (" in combined, "rcon_ready": "RCON running on" in combined, "elapsed_seconds": round(time.time() - start, 1)}


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


def rcon_cmd(client: RconClient, cmd: str) -> dict[str, str]:
    return {"command": cmd, "response": client.command(cmd)}


def forceload_sut_chunks(client: RconClient) -> list[dict[str, str]]:
    chunks = sorted({(x >> 4, z >> 4) for x, _y, z, _e in SUT_BLOCKS.values()})
    responses = []
    for cx, cz in chunks:
        responses.append(rcon_cmd(client, f"forceload add {cx * 16} {cz * 16}"))
    time.sleep(5)
    return responses


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


# ──────────────────────────────────────────────────────────────────────────────
# Block checks
# ──────────────────────────────────────────────────────────────────────────────

def check_block(client: RconClient, name: str) -> dict[str, Any]:
    x, y, z, expected_id = SUT_BLOCKS[name]
    check_response = client.command(f"execute if block {x} {y} {z} {expected_id}")
    data_response = client.command(f"data get block {x} {y} {z}")
    return {
        "name": name,
        "position": [x, y, z],
        "expected_id": expected_id,
        "check_response": check_response,
        "data_response_excerpt": data_response[:800],
        "data_sha256": digest(data_response),
        "has_expected_block": "Test passed" in check_response,
        "has_block_entity_data": (
            "block data:" in data_response.lower()
            or "has block data" in data_response.lower()
        ),
    }


def collect_sut(client: RconClient, phase: str) -> dict[str, Any]:
    return {
        "phase": phase,
        "timestamp": now_iso(),
        "blocks": {name: check_block(client, name) for name in SUT_BLOCKS},
    }


def phase_checks_pass(sut: dict[str, Any]) -> bool:
    return all(item["has_expected_block"] for item in sut["blocks"].values())


# ──────────────────────────────────────────────────────────────────────────────
# Log analysis
# ──────────────────────────────────────────────────────────────────────────────

def analyze_logs(*logs: Path) -> dict[str, Any]:
    full_text = ""
    critical_lines: list[str] = []
    for log in logs:
        text = read_text(log)
        full_text += text + "\n"
        for line in text.splitlines():
            if any(pattern in line for pattern in CRITICAL_LOG_PATTERNS):
                critical_lines.append(line.strip())
    return {
        "critical_count": len(critical_lines),
        "critical_lines": critical_lines[:80],
        "apply_marker_count": full_text.count(APPLY_MARKER),
        "failed_function_count": full_text.count(f"Failed to load function {DATAPACK_NAME}:apply"),
        "unknown_block": "Unknown block type" in full_text,
        "skipping_block_entity": "Skipping BlockEntity" in full_text,
        "crash": "---- Minecraft Crash Report ----" in full_text,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Markdown / Handoff
# ──────────────────────────────────────────────────────────────────────────────

def write_markdown_report(report: dict[str, Any]) -> None:
    la = report.get("log_analysis", {})
    checks = report.get("checks", {})
    lines = [
        "# Armourer's Workshop Task 6 - Raport headless tick/restart",
        "",
        "## Podsumowanie",
        "",
        f"- Status: `{report['status']}`",
        f"- Overall pass: `{str(report.get('overall_pass')).lower()}`",
        f"- Tick wait: {report.get('tick_wait_seconds')} s",
        f"- World: `{report.get('world')}`",
        "",
        "## Wyniki faz",
        "",
        f"- post-apply checks: `{str(checks.get('post_apply')).lower()}`",
        f"- after-ticks checks: `{str(checks.get('after_ticks')).lower()}`",
        f"- after-restart checks: `{str(checks.get('after_restart')).lower()}`",
        f"- apply marker found: `{str(checks.get('apply_marker_found')).lower()}`",
        f"- critical log lines: {la.get('critical_count', '?')}",
        "",
        "## Bloki SUT",
        "",
        "| Nazwa | Pozycja | Oczekiwany blok | Post-apply | Po restarcie |",
        "|-------|---------|-----------------|-----------|--------------|",
    ]
    post = report.get("sut_post_apply", {}).get("blocks", {})
    restart = report.get("sut_after_restart", {}).get("blocks", {})
    for name, (x, y, z, bid) in SUT_BLOCKS.items():
        pa = "TAK" if post.get(name, {}).get("has_expected_block") else "NIE"
        ar = "TAK" if restart.get(name, {}).get("has_expected_block") else "NIE"
        lines.append(f"| `{name}` | {x},{y},{z} | `{bid}` | {pa} | {ar} |")
    lines += [
        "",
        "## Logi",
        "",
        f"- Apply marker `{APPLY_MARKER}`: {la.get('apply_marker_count', '?')}x",
        f"- Critical log lines: {la.get('critical_count', '?')}",
        f"- Unknown block: {la.get('unknown_block', '?')}",
        f"- Skipping BlockEntity: {la.get('skipping_block_entity', '?')}",
        f"- Crash: {la.get('crash', '?')}",
        "",
        "## Pliki",
        "",
        "- `run_task6_headless_tick_restart.py`",
        "- `armourers_workshop_task6_headless_tick_restart_report.json`",
        "- `headless_server/1.18.2/server_armourers_workshop_task6_*_out.log`",
    ]
    write_text_file(REPORT_MD, "\n".join(lines) + "\n")


def write_handoff(report: dict[str, Any]) -> None:
    la = report.get("log_analysis", {})
    overall = report.get("overall_pass", False)
    text = f"""# Handoff: Armourer's Workshop - Zadanie 6

## Podsumowanie sesji

Wykonano headless tick/restart verification dla `{WORLD_NAME}`. Runner uruchomil Forge 1.18.2
z modem `armourersworkshop-forge-1.18.2-2.0.11.jar`, wykonal funkcje datapacka
`{APPLY_FUNCTION}`, sprawdzil {len(SUT_BLOCKS)} skonwertowanych blokow, odczekal ticki,
zapisal swiat, zrestartował serwer i powtorzyl sprawdzenie.

## Wynik

- Status: `{report['status']}`
- Overall pass: `{overall}`
- Tick wait: {report.get('tick_wait_seconds')} s
- Apply marker found: {la.get('apply_marker_count', '?')}x
- Critical log lines: {la.get('critical_count', '?')}

## Pliki

- `test_scenarios/armourers_workshop_task5a/run_task6_headless_tick_restart.py`
- `test_scenarios/armourers_workshop_task5a/armourers_workshop_task6_headless_tick_restart_report.json`
- `test_scenarios/armourers_workshop_task5a/ARMOURERS_WORKSHOP_TASK6_REPORT.md`
- `test_scenarios/armourers_workshop_task5a/HANDOFF_ARMOURERS_WORKSHOP_TASK6.md`
- `headless_server/1.18.2/mods/armourersworkshop-forge-1.18.2-2.0.11.jar`

## Nastepne kroki

1. [ ] Sprawdzic w grze NBT skinnabli: `Skin.Identifier` wskazuje na pliki `.armour` z `skin-library`.
2. [ ] Sprawdzic poprawnosc danych `armourers_workshop:skin-library` po restarcie.
3. [ ] Zweryfikowac rendering skinow przez klienta 1.18.2 z modem AW.

---

**Status:** {"Zadanie 6 ukonczone" if overall else "Zadanie 6 z ostrzezeniami"}
**Data:** {now_iso()[:10]}
"""
    write_text_file(HANDOFF, text)


# ──────────────────────────────────────────────────────────────────────────────
# Main runner
# ──────────────────────────────────────────────────────────────────────────────

def run(args: argparse.Namespace) -> dict[str, Any]:
    report: dict[str, Any] = {
        "name": "Armourer's Workshop Task 6 headless tick/restart",
        "status": "started",
        "start_time": now_iso(),
        "server_dir": str(args.server_dir),
        "world": WORLD_NAME,
        "tick_wait_seconds": args.tick_seconds,
        "phases": [],
        "checks": {},
    }

    proc1: subprocess.Popen | None = None
    proc2: subprocess.Popen | None = None
    rcon1: RconClient | None = None
    rcon2: RconClient | None = None
    logs: list[Path] = []

    try:
        backup = install_server_properties(args.server_dir)
        report["server_properties_backup"] = str(backup) if backup else None

        print("[AW Task6] Starting server first run...")
        proc1, out1, err1 = run_server(args.server_dir, "first")
        logs.extend([out1, err1])
        startup1 = wait_for_server(proc1, out1, args.startup_timeout)
        report["phases"].append({"name": "first_start", **startup1, "out_log": str(out1), "err_log": str(err1)})
        if not startup1["ready"]:
            report["status"] = "failed_first_start"
            return report

        rcon1 = connect_rcon(args.rcon_host, args.rcon_port, args.rcon_password, 45)
        report["phases"].append({"name": "rcon_first", "list": rcon1.command("list")})
        report["phases"].append({"name": "forceload", "commands": forceload_sut_chunks(rcon1)})

        print("[AW Task6] Applying datapack...")
        prep = [
            rcon_cmd(rcon1, "reload"),
            rcon_cmd(rcon1, f'datapack enable "file/{DATAPACK_NAME}"'),
        ]
        time.sleep(5)
        apply_response = rcon1.command(f"function {APPLY_FUNCTION}")
        time.sleep(5)
        post_apply = collect_sut(rcon1, "post_apply")
        report["phases"].append({"name": "post_apply", "prep_commands": prep, "apply_response": apply_response, "sut": post_apply})
        report["checks"]["post_apply"] = phase_checks_pass(post_apply)
        report["sut_post_apply"] = post_apply

        print(f"[AW Task6] Waiting {args.tick_seconds}s for ticks...")
        time.sleep(args.tick_seconds)
        after_ticks = collect_sut(rcon1, "after_ticks")
        report["phases"].append({"name": "after_ticks", "sut": after_ticks, "tps": rcon1.command("forge tps")})
        report["checks"]["after_ticks"] = phase_checks_pass(after_ticks)

        report["phases"].append({"name": "save_all", "response": rcon1.command("save-all flush")})
        time.sleep(5)
        report["phases"].append({"name": "disable_datapack", "response": rcon1.command(f'datapack disable "file/{DATAPACK_NAME}"')})
        time.sleep(2)

        print("[AW Task6] Stopping first run...")
        report["phases"].append({"name": "stop_first", **stop_server(proc1, rcon1)})
        rcon1.disconnect()
        rcon1 = None
        proc1 = None

        time.sleep(5)
        print("[AW Task6] Restarting server...")
        proc2, out2, err2 = run_server(args.server_dir, "restart")
        logs.extend([out2, err2])
        startup2 = wait_for_server(proc2, out2, args.startup_timeout)
        report["phases"].append({"name": "restart", **startup2, "out_log": str(out2), "err_log": str(err2)})
        if not startup2["ready"]:
            report["status"] = "failed_restart"
            return report

        rcon2 = connect_rcon(args.rcon_host, args.rcon_port, args.rcon_password, 45)
        report["phases"].append({"name": "rcon_restart", "list": rcon2.command("list")})
        report["phases"].append({"name": "forceload_restart", "commands": forceload_sut_chunks(rcon2)})
        after_restart = collect_sut(rcon2, "after_restart")
        report["phases"].append({"name": "after_restart", "sut": after_restart, "tps": rcon2.command("forge tps")})
        report["checks"]["after_restart"] = phase_checks_pass(after_restart)
        report["sut_after_restart"] = after_restart

        print("[AW Task6] Stopping restart run...")
        report["phases"].append({"name": "stop_restart", **stop_server(proc2, rcon2)})
        rcon2.disconnect()
        rcon2 = None
        proc2 = None

        log_analysis = analyze_logs(*logs)
        report["log_analysis"] = log_analysis
        report["checks"]["apply_marker_found"] = log_analysis["apply_marker_count"] >= 1
        report["checks"]["no_critical_logs"] = log_analysis["critical_count"] == 0
        report["overall_pass"] = all(report["checks"].values())
        report["status"] = "passed" if report["overall_pass"] else "failed_checks"

    except Exception as exc:  # noqa: BLE001
        report["status"] = "error"
        report["error"] = str(exc)
        report["log_analysis"] = analyze_logs(*logs) if logs else {"critical_count": 0, "critical_lines": []}
        for client in (rcon1, rcon2):
            if client:
                try:
                    client.disconnect()
                except Exception:  # noqa: BLE001
                    pass
        for proc in (proc1, proc2):
            if proc and proc.poll() is None:
                proc.kill()
                proc.wait(timeout=20)
    finally:
        report.setdefault("log_analysis", analyze_logs(*logs) if logs else {"critical_count": 0, "critical_lines": []})
        report["end_time"] = now_iso()

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Armourer's Workshop Task 6 headless tick/restart")
    parser.add_argument("--server-dir", type=Path, default=SERVER_DIR)
    parser.add_argument("--tick-seconds", type=int, default=180)
    parser.add_argument("--startup-timeout", type=int, default=300)
    parser.add_argument("--rcon-host", default="127.0.0.1")
    parser.add_argument("--rcon-port", type=int, default=25581)
    parser.add_argument("--rcon-password", default="cc_task6_test")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    report = run(args)
    write_json(args.report, report)
    write_markdown_report(report)
    write_handoff(report)
    print(f"\nReport: {args.report}")
    print(f"Status: {report['status']}")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
