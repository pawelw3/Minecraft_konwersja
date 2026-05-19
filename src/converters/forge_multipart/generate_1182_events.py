"""
Generuje eventy w formacie applyEvents1182 (Kotlin worker) z wyników konwersji.
"""
import json
from pathlib import Path


def generate_events(conversion_result_path: str, output_path: str):
    with open(conversion_result_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    events = []
    for ev in data.get("events", []):
        if not ev.get("converted"):
            continue

        pos = ev["pos"]
        block_id = ev.get("block_id_1182")
        nbt = ev.get("nbt_1182")

        if not block_id or not nbt:
            continue

        # Upewnij się że NBT ma poprawne typy (int dla x,y,z)
        nbt_out = dict(nbt)
        nbt_out["x"] = int(pos[0])
        nbt_out["y"] = int(pos[1])
        nbt_out["z"] = int(pos[2])

        events.append({
            "op": "set_block_entity",
            "pos": pos,
            "block": block_id,
            "nbt": nbt_out,
        })

    output = {"events": events}
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Wygenerowano {len(events)} eventow")
    print(f"Zapisano: {output_path}")


if __name__ == "__main__":
    generate_events(
        "output/forge_multipart/task5a_conversion_result.json",
        "output/forge_multipart/task5a_events_1182.json",
    )
