#!/usr/bin/env python3
"""Re-convert terrain with updated block-only converters.

This script re-runs only the terrain conversion + event application
for the custom_area_1800_574 world, WITHOUT:
- destroying the existing world directory (preserves backpacks, playerdata, etc.)
- re-converting Armourer's Workshop skins (already done, takes a long time)
- re-converting Backpack mod data (already done)

It keeps the existing events.jsonl and re-applies them after terrain rewrite.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPT_DIR.parents[1] / "src"))

import convert_area_direct as cad  # noqa: E402


def backup_regions():
    region_dir = cad.DST_WORLD / "region"
    backup_dir = cad.DST_WORLD / f"region_backup_{datetime.now():%Y%m%d_%H%M%S}"
    if region_dir.exists():
        print(f"[BACKUP] Copying {region_dir.name} -> {backup_dir.name}")
        shutil.copytree(region_dir, backup_dir)
        print(f"[BACKUP] Done: {backup_dir}")
    return backup_dir


def remove_regions():
    region_dir = cad.DST_WORLD / "region"
    if region_dir.exists():
        print(f"[CLEAN] Removing old region files")
        shutil.rmtree(region_dir)
        region_dir.mkdir(parents=True, exist_ok=True)
        print(f"[CLEAN] Done")


def main():
    print("=" * 70)
    print("Re-conversion with updated block-only converters")
    print(f"World: {cad.DST_WORLD}")
    print(f"Source: {cad.SRC_WORLD}")
    print(f"Events: {cad.EVENTS_FILE}")
    print("=" * 70)

    # 1. Backup existing regions
    backup_dir = backup_regions()

    # 2. Remove old regions (but keep the rest of the world: playerdata, backpacks, etc.)
    remove_regions()

    # 3. Re-write terrain with updated block-only router (this uses the global
    #    BLOCK_ONLY_REGISTRY which is now populated with new AE2/Biblio/etc. mappings)
    print("\n[1/3] Re-writing vanilla terrain + block-only conversions")
    cad.write_vanilla_terrain()

    # 4. Patch level.dat (safe, only changes spawn and game settings)
    print("\n[2/3] Patching level.dat")
    cad.patch_level_dat()

    # 5. Re-apply mod events (JVM worker)
    print("\n[3/3] Re-applying mod conversion events")
    cad.apply_mod_events()

    # 6. Verify
    print("\n[VERIFY] Output files")
    cad.verify_output()

    print(f"\n[DONE] Backup of old regions: {backup_dir}")
    print("[DONE] Skipped: Armourer's Workshop skins, Backpacks (already converted)")


if __name__ == "__main__":
    main()
