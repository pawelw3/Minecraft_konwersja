#!/bin/bash
set -euo pipefail

cd /c/Users/pawel/Minecraft_konwersja

ROOT="$(pwd)"
WORK_DIR="C:/tmp/aw_runner_work"
SOURCE_ROOT="$ROOT/pliki_globalne_serwer_1710/armourersWorkshop"
TARGET_ROOT="$ROOT/tasks/custom_area_1800_574/world/skin-library"
MANIFEST="$ROOT/output/armourers_workshop_step4/skin_library_migration_manifest.json"

mkdir -p "$TARGET_ROOT"

# Get remaining files
python3 -c "
import json, os
with open('$MANIFEST') as f:
    m = json.load(f)
done = set(os.listdir('$TARGET_ROOT'))
for e in m['entries']:
    r = e['relative_path']
    if r not in done:
        print(r)
" > /tmp/aw_remaining.txt

TOTAL=$(wc -l < /tmp/aw_remaining.txt | tr -d ' ')
echo "Remaining: $TOTAL files"
echo "Target: $TARGET_ROOT"
echo

OK=0
FAIL=0
START=$SECONDS

MAX_JOBS=3

cd "$WORK_DIR"

while IFS= read -r rel; do
    src="$SOURCE_ROOT/$rel"
    dst="$TARGET_ROOT/$rel"
    mkdir -p "$(dirname "$dst")"

    ./gradlew.bat :forge:runSkinLibraryConvertCli \
        "-PawSource=$src" \
        "-PawTarget=$dst" \
        --no-daemon --console=plain > /dev/null 2>&1 &

    ((OK++)) || true
    echo "  Started $OK/$TOTAL: $rel"

    # Limit parallel jobs
    while [ "$(jobs -p | wc -l)" -ge "$MAX_JOBS" ]; do
        wait -n 2>/dev/null || true
    done
done < /tmp/aw_remaining.txt

# Wait for all remaining jobs
wait

ELAPSED=$((SECONDS - START))
echo
echo "Done in ${ELAPSED}s"
echo "Output: $TARGET_ROOT"
echo "Files: $(ls "$TARGET_ROOT" | wc -l)"
