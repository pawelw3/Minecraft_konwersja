"""
Weryfikacja wyników konwersji testowej mapy ForgeMultipart (Zadanie 5A).

Sprawdza czy przekonwertowane NBT jest kompatybilne z symulacją 1.18.2.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from converters.forge_multipart.simulations.cbm_1182 import (
    TileMultipart as TileMultipart1182,
    MicroMaterialRegistry as MatReg1182,
    PartRegistry as Reg1182,
    register_defaults as register_defaults_1182,
)


def verify_event(event: dict) -> dict:
    """Weryfikuje pojedynczy event konwersji."""
    result = {
        "pos": event["pos"],
        "parts_original": event["parts_original"],
        "parts_converted": event["parts_converted"],
        "success": False,
        "errors": [],
    }

    nbt_1182 = event.get("nbt_1182")
    if not nbt_1182:
        result["errors"].append("Brak NBT 1.18.2")
        return result

    # Przygotuj registry 1.18.2
    MatReg1182.reset()
    Reg1182.reset()
    register_defaults_1182()

    # Zarejestruj materiały z oryginalnego NBT (jeśli są)
    for part_id in event["parts_original"]:
        # Dla mikrobloków rejestrujmy domyślny materiał
        if part_id.startswith("mcr_"):
            MatReg1182.register("minecraft:stone")

    pos = tuple(event["pos"])

    try:
        tile = TileMultipart1182.load(nbt_1182, pos)
        result["deserialized_parts_count"] = len(tile.parts)
        expected = len(event["parts_original"])
        result["success"] = len(tile.parts) == expected
        if not result["success"]:
            result["errors"].append(
                f"Rozbieżność liczby partow: oczekiwano={expected}, "
                f"deserializowano={len(tile.parts)}"
            )
    except Exception as e:
        result["errors"].append(f"Deserializacja nie powiodla sie: {e}")

    return result


def run_verification():
    result_path = Path("output/forge_multipart/task5a_conversion_result.json")
    if not result_path.exists():
        print(f"Brak pliku wynikowego: {result_path}")
        print("Uruchom najpierw convert_test_map.py")
        return

    with open(result_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    events = data.get("events", [])
    print(f"Weryfikacja {len(events)} eventow konwersji...")

    results = []
    for event in events:
        res = verify_event(event)
        results.append(res)

    ok = sum(1 for r in results if r["success"])
    fail = len(results) - ok

    print(f"\nWyniki: OK={ok}, FAIL={fail} / {len(results)}")

    if fail > 0:
        print("\nBledy:")
        for r in results:
            if not r["success"]:
                print(f"  Pos={r['pos']}, errors={r['errors']}")

    # Zapisz raport
    report_path = Path("output/forge_multipart/task5a_verification.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "total": len(results),
            "ok": ok,
            "fail": fail,
            "results": results,
        }, f, indent=2, ensure_ascii=False)
    print(f"Raport zapisano w: {report_path}")

    return ok == len(results)


if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)
