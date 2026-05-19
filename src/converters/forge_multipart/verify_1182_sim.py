"""
Weryfikacja symulacji 1.18.2 na przekonwertowanych danych z mapy 1.7.10.
Zadanie 4 — sprawdzenie czy konwertowane NBT działa w symulacji 1.18.2.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from converters.forge_multipart.nbt_converter import TileMultipartNBTConverter
from converters.forge_multipart.simulations.cbm_1182 import (
    TileMultipart as TileMultipart1182,
    MicroMaterialRegistry as MatReg1182,
    PartRegistry as Reg1182,
    register_defaults as register_defaults_1182,
)


PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

def load_samples() -> List[Dict]:
    """Wczytuje próbki z analizy mapy."""
    analysis_path = PROJECT_ROOT / "output/forge_multipart/forge_multipart_analysis.json"
    if not analysis_path.exists():
        return []
    with open(analysis_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    samples = []
    for te_samples in data.get("samples", {}).values():
        samples.extend(te_samples)
    return samples


def verify_sample(sample: Dict) -> Dict:
    """Weryfikuje pojedynczą próbkę: konwersja + deserializacja 1.18.2."""
    result = {
        "original_te_id": sample.get("id"),
        "pos": (sample.get("x"), sample.get("y"), sample.get("z")),
        "parts_count_original": len(sample.get("parts", [])),
        "success": False,
        "errors": [],
    }

    # Konwersja NBT
    nbt_1182 = TileMultipartNBTConverter.convert(sample)
    if nbt_1182 is None:
        result["errors"].append("NBT conversion returned None")
        return result

    result["converted_te_id"] = nbt_1182.get("id")
    result["parts_count_converted"] = len(nbt_1182.get("parts", []))

    # Przygotuj registry 1.18.2
    MatReg1182.reset()
    Reg1182.reset()
    register_defaults_1182()

    # Zarejestruj materiały z próbki
    for part in sample.get("parts", []):
        if isinstance(part, dict) and "material" in part:
            MatReg1182.register(part["material"])

    # Deserializacja w symulacji 1.18.2
    try:
        tile = TileMultipart1182.load(nbt_1182, result["pos"])
        result["deserialized_parts_count"] = len(tile.parts)
        result["success"] = len(tile.parts) == result["parts_count_original"]
        if not result["success"]:
            result["errors"].append(
                f"Part count mismatch: original={result['parts_count_original']}, "
                f"deserialized={len(tile.parts)}"
            )
    except Exception as e:
        result["errors"].append(f"Deserialization failed: {e}")

    return result


def run_verification(max_samples: int = 50):
    samples = load_samples()
    if not samples:
        print("Brak próbek do weryfikacji. Uruchom najpierw analyze_map.py")
        return

    print(f"Weryfikacja {min(max_samples, len(samples))} próbek...")

    results = []
    for sample in samples[:max_samples]:
        res = verify_sample(sample)
        results.append(res)

    ok = sum(1 for r in results if r["success"])
    fail = len(results) - ok

    print(f"\nWyniki: OK={ok}, FAIL={fail} / {len(results)}")

    if fail > 0:
        print("\nPierwsze błędy:")
        for r in results:
            if not r["success"]:
                print(f"  Pos={r['pos']}, errors={r['errors']}")
                break

    # Zapisz raport
    report_path = PROJECT_ROOT / "output/forge_multipart/verification_1182.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "total": len(results),
            "ok": ok,
            "fail": fail,
            "results": results,
        }, f, indent=2, ensure_ascii=False)
    print(f"Raport zapisano w: {report_path}")


if __name__ == "__main__":
    run_verification(max_samples=100)
