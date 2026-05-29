#!/usr/bin/env python3
"""
Test: czyści wycinek mapy 1.7.10 (X -1800..-1161, Z -1007..-574).

Pipeline:
1. Kopiuje level.dat + region pliki r.-4.-2.mca, r.-3.-2.mca z mapa_1710
   do test/source_slice/ (minimalne źródłowe środowisko 1.7.10)
2. Uruchamia map-cleaner JAR z --output test/cleaned_slice/ --full
   (bloki modów -> air, usuwa TE i entities)
3. Patchuje level.dat w cleaned_slice: tryb creative, spawn w centrum
"""
from __future__ import annotations

import shutil
import struct
import subprocess
import sys
import zlib
from io import BytesIO
from pathlib import Path

import nbtlib  # type: ignore

ROOT       = Path(__file__).resolve().parent.parent
SCRIPT_DIR = Path(__file__).resolve().parent

SRC_WORLD     = ROOT / "mapa_1710"
TEST_DIR      = SCRIPT_DIR / "test"
SOURCE_SLICE  = TEST_DIR / "source_slice"
CLEANED_SLICE = TEST_DIR / "cleaned_slice"

CLEANER_JAR = SCRIPT_DIR / "jvm" / "build" / "libs" / "map-cleaner-1.0-SNAPSHOT.jar"

REGION_FILES = ["r.-4.-2.mca", "r.-3.-2.mca"]

# Obszar
X_MIN, X_MAX = -1800, -1161
Z_MIN, Z_MAX = -1007, -574
SPAWN_X = (X_MIN + X_MAX) // 2   # -1480
SPAWN_Y = 70
SPAWN_Z = (Z_MIN + Z_MAX) // 2   # -790


def prepare_source_slice():
    print("[1/3] Przygotowanie źródłowego wycinka...")

    if SOURCE_SLICE.exists():
        shutil.rmtree(SOURCE_SLICE)
    (SOURCE_SLICE / "region").mkdir(parents=True)

    shutil.copy2(SRC_WORLD / "level.dat", SOURCE_SLICE / "level.dat")
    level_old = SRC_WORLD / "level.dat_old"
    if level_old.exists():
        shutil.copy2(level_old, SOURCE_SLICE / "level.dat_old")

    copied = []
    for name in REGION_FILES:
        src = SRC_WORLD / "region" / name
        if src.exists():
            shutil.copy2(src, SOURCE_SLICE / "region" / name)
            size_mb = src.stat().st_size / 1_048_576
            copied.append(f"{name} ({size_mb:.1f} MB)")
        else:
            print(f"  BRAK: {src}")

    print(f"  Skopiowano region files: {', '.join(copied)}")
    print(f"  Źródło: {SOURCE_SLICE}")


def run_cleaner():
    print("\n[2/3] Czyszczenie (map-cleaner JAR)...")

    if not CLEANER_JAR.exists():
        print(f"  BLAD: brak JAR: {CLEANER_JAR}")
        print("  Zbuduj: cd map_cleaning\\jvm && .\\gradlew.bat build")
        sys.exit(1)

    if CLEANED_SLICE.exists():
        shutil.rmtree(CLEANED_SLICE)

    cmd = [
        "java", "-jar", str(CLEANER_JAR),
        str(SOURCE_SLICE),
        "--output", str(CLEANED_SLICE),
        "--full",
    ]
    print(f"  Komenda: {' '.join(cmd)}")
    result = subprocess.run(cmd, timeout=1800)
    if result.returncode != 0:
        print(f"  BLAD: JAR zwrocil kod {result.returncode}")
        sys.exit(1)
    print(f"  Wyjscie: {CLEANED_SLICE}")


def patch_level_dat():
    print("\n[3/3] Patchowanie level.dat (creative, spawn)...")

    level_dat = CLEANED_SLICE / "level.dat"
    if not level_dat.exists():
        print(f"  BLAD: brak {level_dat}")
        sys.exit(1)

    level = nbtlib.load(str(level_dat), gzipped=True)
    data = level["Data"]

    data["GameType"]      = nbtlib.Int(1)       # 1 = Creative
    data["allowCommands"] = nbtlib.Byte(1)
    data["Difficulty"]    = nbtlib.Byte(0)       # 0 = Peaceful
    data["SpawnX"]        = nbtlib.Int(SPAWN_X)
    data["SpawnY"]        = nbtlib.Int(SPAWN_Y)
    data["SpawnZ"]        = nbtlib.Int(SPAWN_Z)
    data["LevelName"]     = nbtlib.String("1710 slice cleaned")

    level.save()

    print(f"  GameType  : Creative (1)")
    print(f"  Spawn     : ({SPAWN_X}, {SPAWN_Y}, {SPAWN_Z})")
    print(f"  LevelName : 1710 slice cleaned")


def print_summary():
    print("\n" + "=" * 60)
    print("GOTOWE")
    print("=" * 60)
    print(f"Zrodlo    : {SOURCE_SLICE}")
    print(f"Wyczyszczone : {CLEANED_SLICE}")
    print()
    print("Aby przetestowac: skopiuj cleaned_slice do folderu saves")
    print("Minecrafta 1.7.10 (bez zadnych modow) i otwórz w grze.")
    print("=" * 60)


def main():
    print("=" * 60)
    print("TEST: czyszczenie wycinka mapy 1.7.10")
    print(f"Obszar: X {X_MIN}..{X_MAX}  Z {Z_MIN}..{Z_MAX}")
    print(f"Regiony: {', '.join(REGION_FILES)}")
    print("=" * 60)

    prepare_source_slice()
    run_cleaner()
    patch_level_dat()
    print_summary()


if __name__ == "__main__":
    main()
