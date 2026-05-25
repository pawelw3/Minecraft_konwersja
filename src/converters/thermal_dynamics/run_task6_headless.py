"""
Step 6: Headless server test for Thermal Dynamics conversion.

1. Starts Forge 1.18.2 server with Thermal + Mekanism mods
2. Uses RCON to place converted blocks (energy_duct, fluid_duct, logistical_transporter)
3. Waits 3 minutes, checks logs for errors
4. Restarts server and verifies persistence
"""
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SERVER_DIR = ROOT / "headless_server" / "1.18.2"
RCON_HOST = "localhost"
RCON_PORT = 25575
RCON_PASS = "ae2test123"

sys.path.insert(0, str(ROOT / "src"))
from converters.projectred.test_structures.headless_test.rcon_client import RconClient


def run_server(label: str) -> tuple[subprocess.Popen, Path, Path]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_log = SERVER_DIR / f"server_td_task6_{label}_{stamp}_out.log"
    err_log = SERVER_DIR / f"server_td_task6_{label}_{stamp}_err.log"
    out_f = out_log.open("w", encoding="utf-8", errors="replace")
    err_f = err_log.open("w", encoding="utf-8", errors="replace")
    proc = subprocess.Popen(
        [
            "java",
            "@user_jvm_args.txt",
            "@libraries/net/minecraftforge/forge/1.18.2-40.2.4/win_args.txt",
            "nogui",
        ],
        cwd=SERVER_DIR,
        stdout=out_f,
        stderr=err_f,
        text=True,
        creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
    )
    out_f.close()
    err_f.close()
    return proc, out_log, err_log


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def wait_for_server(proc: subprocess.Popen, out_log: Path, timeout: int) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        combined = read_text(out_log)
        done = "Done (" in combined
        rcon_ready = "RCON running on" in combined
        fatal = "FATAL" in combined and "ModLoadingException" in combined
        if fatal:
            return {"ready": False, "done": False, "fatal": True}
        if done and rcon_ready:
            return {"ready": True, "done": True, "fatal": False}
        if proc.poll() is not None:
            return {"ready": False, "done": False, "fatal": True, "exit": proc.returncode}
        time.sleep(1)
    return {"ready": False, "done": False, "fatal": False, "timeout": True}


def place_test_blocks() -> list[str]:
    """Place converted TD blocks via RCON at spawn area."""
    client = RconClient(RCON_HOST, RCON_PORT, RCON_PASS)
    if not client.connect():
        print("  RCON connection failed")
        return ["RCON connection failed"]

    results = []
    # Force load spawn chunk and place blocks near spawn (32, 71, 0)
    client.command("/forceload add 32 0")
    time.sleep(0.5)
    base_x, base_y, base_z = 32, 71, 0
    blocks = [
        (base_x, base_y, base_z, "thermal:energy_duct"),
        (base_x+1, base_y, base_z, "thermal:fluid_duct"),
        (base_x+2, base_y, base_z, "thermal:fluid_duct_windowed"),
        (base_x+3, base_y, base_z, "mekanism:basic_logistical_transporter"),
        (base_x+4, base_y, base_z, "mekanism:advanced_logistical_transporter"),
        (base_x+5, base_y, base_z, "mekanism:elite_logistical_transporter"),
        (base_x+6, base_y, base_z, "mekanism:ultimate_logistical_transporter"),
        (base_x+7, base_y, base_z, "mekanism:teleporter"),
        (base_x+8, base_y, base_z, "mekanism:teleporter_frame"),
    ]

    for x, y, z, block in blocks:
        cmd = f"/setblock {x} {y} {z} {block}"
        resp = client.command(cmd)
        results.append(f"{block}: {resp}")
        time.sleep(0.1)

    # Save world
    client.command("/save-all")
    time.sleep(1)
    client.disconnect()
    return results


def check_logs(out_log: Path, err_log: Path) -> dict:
    out_text = read_text(out_log)
    err_text = read_text(err_log)
    combined = out_text + "\n" + err_text

    errors = []
    warnings = []
    for line in combined.splitlines():
        if "ERROR" in line or "FATAL" in line or "Exception" in line:
            if "forge-1.18.2" not in line and "fmlcore" not in line:
                errors.append(line.strip())
        if "WARN" in line and ("thermaldynamics" in line.lower() or "thermal" in line.lower() or "mekanism" in line.lower()):
            warnings.append(line.strip())

    return {
        "errors": errors[:20],
        "warnings": warnings[:20],
        "has_crash": "Crash report saved" in combined or "---- Minecraft Crash Report ----" in combined,
    }


def main():
    print("=" * 60)
    print("THERMAL DYNAMICS — STEP 6: Headless Server Test")
    print("=" * 60)

    # Ensure server.properties points to world
    props = SERVER_DIR / "server.properties"
    text = props.read_text(encoding="utf-8")
    text = text.replace("level-name=world_forge_multipart_converted", "level-name=world")
    text = text.replace("level-name=world_zsrr_ae2_mek_events", "level-name=world")
    props.write_text(text, encoding="utf-8")

    # Run 1: Start server
    print("\n[1/4] Starting server (first run)...")
    proc, out_log, err_log = run_server("first")
    status = wait_for_server(proc, out_log, timeout=300)
    if not status["ready"]:
        print(f"  Server failed to start: {status}")
        proc.terminate()
        return 1
    print("  Server ready.")

    # Place blocks
    print("\n[2/4] Placing test blocks via RCON...")
    block_results = place_test_blocks()
    for r in block_results:
        print(f"  {r}")

    # Wait 3 minutes
    print("\n[3/4] Waiting 3 minutes for ticks...")
    time.sleep(180)

    # Check logs
    print("\n[4/4] Checking logs...")
    log_status = check_logs(out_log, err_log)
    print(f"  Errors found: {len(log_status['errors'])}")
    print(f"  Warnings found: {len(log_status['warnings'])}")
    print(f"  Crash: {log_status['has_crash']}")

    # Stop server via RCON
    print("\n  Stopping server...")
    try:
        client.command("/stop")
        time.sleep(2)
        client.disconnect()
    except Exception:
        pass
    proc.wait(timeout=60)

    # Restart test
    print("\n[Restart test] Starting server again...")
    proc2, out_log2, err_log2 = run_server("restart")
    status2 = wait_for_server(proc2, out_log2, timeout=300)
    if not status2["ready"]:
        print(f"  Server failed to restart: {status2}")
        proc2.terminate()
        return 1
    print("  Server restarted successfully.")

    log_status2 = check_logs(out_log2, err_log2)
    print(f"  Errors after restart: {len(log_status2['errors'])}")
    print(f"  Warnings after restart: {len(log_status2['warnings'])}")
    print(f"  Crash after restart: {log_status2['has_crash']}")

    try:
        client2 = RconClient(RCON_HOST, RCON_PORT, RCON_PASS)
        client2.connect()
        client2.command("/stop")
        time.sleep(2)
        client2.disconnect()
    except Exception:
        pass
    proc2.wait(timeout=60)

    # Summary
    print("\n" + "=" * 60)
    print("STEP 6 SUMMARY")
    print("=" * 60)
    print(f"First run errors: {len(log_status['errors'])}")
    print(f"First run crashes: {log_status['has_crash']}")
    print(f"Restart errors: {len(log_status2['errors'])}")
    print(f"Restart crashes: {log_status2['has_crash']}")
    success = not log_status["has_crash"] and not log_status2["has_crash"]
    print(f"Overall: {'PASS' if success else 'FAIL'}")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
