#!/usr/bin/env python3
"""Convert remaining Armourer's Workshop skins using a managed pool of subprocesses."""

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK_DIR = Path("C:/tmp/aw_runner_work")
GRADLEW = WORK_DIR / "gradlew.bat"
MANIFEST = ROOT / "output" / "armourers_workshop_step4" / "skin_library_migration_manifest.json"
SOURCE_ROOT = ROOT / "pliki_globalne_serwer_1710" / "armourersWorkshop"
TARGET_ROOT = ROOT / "tasks" / "custom_area_1800_574" / "world" / "skin-library"
MAX_PARALLEL = 3

def main():
    with open(MANIFEST, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    done = set(p.name for p in TARGET_ROOT.iterdir() if p.is_file()) if TARGET_ROOT.exists() else set()
    entries = [e for e in manifest.get("entries", []) if e["relative_path"] not in done]
    total = len(entries)
    print(f"Remaining: {total} files")

    TARGET_ROOT.mkdir(parents=True, exist_ok=True)

    ok_count = len(done)
    fail_count = 0
    start = time.time()
    processes: list[tuple[subprocess.Popen, dict]] = []
    idx = 0

    while idx < len(entries) or processes:
        # Start new processes up to MAX_PARALLEL
        while len(processes) < MAX_PARALLEL and idx < len(entries):
            e = entries[idx]
            idx += 1
            rel = e["relative_path"]
            src = SOURCE_ROOT / rel
            dst = TARGET_ROOT / rel
            dst.parent.mkdir(parents=True, exist_ok=True)

            cmd = [
                str(GRADLEW),
                "-p", str(WORK_DIR),
                ":forge:runSkinLibraryConvertCli",
                f"-PawSource={src}",
                f"-PawTarget={dst}",
                "--no-daemon",
                "--console=plain",
            ]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
            processes.append((proc, e))

        # Check for completed processes
        still_running = []
        for proc, e in processes:
            ret = proc.poll()
            if ret is None:
                still_running.append((proc, e))
                continue

            rel = e["relative_path"]
            dst = TARGET_ROOT / rel
            ok = (ret == 0) and dst.exists()
            if ok:
                ok_count += 1
                print(f"  OK   {rel} ({ok_count} total)")
            else:
                fail_count += 1
                err = proc.stderr.read()[-200:] if proc.stderr else ""
                print(f"  FAIL {rel} rc={ret} ({fail_count} fails)")
                if err:
                    print(f"       {err[:150]}")

        processes = still_running
        if processes:
            time.sleep(0.5)

    elapsed = time.time() - start
    print()
    print(f"Done in {elapsed:.1f}s")
    print(f"  OK:   {ok_count}")
    print(f"  Fail: {fail_count}")
    print(f"  Output: {TARGET_ROOT}")


if __name__ == "__main__":
    main()
