#!/usr/bin/env python3
"""
Batch-convert all Armourer's Workshop .armour files from 1.7.10 to 1.18.2 format.
Uses the pre-built SkinLibraryConvertCli runner in C:\tmp\aw_runner_work.
"""

import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK_DIR = Path("C:/tmp/aw_runner_work")
GRADLEW = WORK_DIR / "gradlew.bat"
MANIFEST = ROOT / "output" / "armourers_workshop_step4" / "skin_library_migration_manifest.json"
SOURCE_ROOT = ROOT / "pliki_globalne_serwer_1710" / "armourersWorkshop"
TARGET_ROOT = ROOT / "tasks" / "custom_area_1800_574" / "world" / "skin-library"
MAX_WORKERS = 1


def convert_one(entry: dict) -> dict:
    rel = entry["relative_path"]
    src = SOURCE_ROOT / rel
    dst = TARGET_ROOT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)

    cmd = (
        f'"{GRADLEW}" -p "{WORK_DIR}" :forge:runSkinLibraryConvertCli '
        f'"-PawSource={src}" "-PawTarget={dst}" --no-daemon --console=plain'
    )

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        ok = result.returncode == 0 and dst.exists()
        return {
            "file": rel,
            "ok": ok,
            "returncode": result.returncode,
            "stderr": result.stderr[-300:] if result.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {"file": rel, "ok": False, "returncode": -1, "stderr": "timeout"}
    except Exception as exc:
        return {"file": rel, "ok": False, "returncode": -1, "stderr": str(exc)}


def main():
    if not GRADLEW.exists():
        print(f"ERROR: gradlew not found at {GRADLEW}")
        sys.exit(1)

    if not MANIFEST.exists():
        print(f"ERROR: manifest not found at {MANIFEST}")
        sys.exit(1)

    with open(MANIFEST, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    entries = manifest.get("entries", [])
    total = len(entries)
    print(f"Converting {total} .armour files -> {TARGET_ROOT}")
    print(f"Parallel workers: {MAX_WORKERS}")
    print()

    TARGET_ROOT.mkdir(parents=True, exist_ok=True)

    ok_count = fail_count = 0
    start = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(convert_one, e): e for e in entries}
        for future in as_completed(futures):
            res = future.result()
            if res["ok"]:
                ok_count += 1
                print(f"  [{ok_count+fail_count}/{total}] OK   {res['file']}")
            else:
                fail_count += 1
                print(f"  [{ok_count+fail_count}/{total}] FAIL {res['file']} (rc={res['returncode']})")
                if res["stderr"]:
                    print(f"       {res['stderr'][:200]}")

    elapsed = time.time() - start
    print()
    print(f"Done in {elapsed:.1f}s")
    print(f"  OK:    {ok_count}/{total}")
    print(f"  Fail:  {fail_count}/{total}")
    print(f"  Output: {TARGET_ROOT}")


if __name__ == "__main__":
    main()
