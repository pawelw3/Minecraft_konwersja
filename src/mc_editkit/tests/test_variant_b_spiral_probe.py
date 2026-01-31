"""
Test Variant B: Spiralny kabel + command block w każdym chunku (PROBE REACHED)

Ten test wstawia spiralę chunków z redstone kablami i command blockami,
uruchamia serwer headless i sprawdza czy sygnał dotarł do kolejnych chunków.
"""
import sys
import os
import subprocess
import time
import re
import logging
from pathlib import Path
from typing import List, Tuple, Dict

# Dodaj src do path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mc_editkit.world.editor import WorldEditor, WorldCopier, edit_world
from mc_editkit.world.types import Pos
from mc_editkit.blocks.registry import get_registry

logger = logging.getLogger(__name__)


def generate_spiral_chunks(radius: int) -> List[Tuple[int, int, int]]:
    """
    Generuje spiralę chunków od (0,0) do promienia R.
    Zwraca listę (cx, cz, step).
    """
    chunks = []
    x, z = 0, 0
    dx, dz = 1, 0
    steps = 1
    step_count = 0
    direction_changes = 0
    
    for step in range((2 * radius + 1) ** 2):
        if abs(x) > radius or abs(z) > radius:
            break
        chunks.append((x, z, step))
        
        x += dx
        z += dz
        step_count += 1
        
        if step_count == steps:
            step_count = 0
            direction_changes += 1
            if dx == 1 and dz == 0:
                dx, dz = 0, 1
            elif dx == 0 and dz == 1:
                dx, dz = -1, 0
            elif dx == -1 and dz == 0:
                dx, dz = 0, -1
            elif dx == 0 and dz == -1:
                dx, dz = 1, 0
            
            if direction_changes % 2 == 0:
                steps += 1
    
    return chunks


def build_spiral_structure(world_path: str, radius: int = 3, y_level: int = 200):
    """
    Buduje spiralę w świecie.
    
    Args:
        world_path: Ścieżka do świata
        radius: Promień spirali (R=3 = 49 chunków)
        y_level: Wysokość Y dla struktury
    """
    logger.info(f"Budowanie spirali R={radius} w {world_path} na Y={y_level}")
    
    chunks = generate_spiral_chunks(radius)
    logger.info(f"Wygenerowano {len(chunks)} punktów spirali")
    
    registry = get_registry()
    stone_id = registry.get_id("minecraft:stone")
    redstone_block_id = registry.get_id("minecraft:redstone_block")
    command_block_id = registry.get_id("minecraft:command_block")
    
    with edit_world(world_path, backup=True) as editor:
        for cx, cz, step in chunks:
            center_x = cx * 16 + 8
            center_z = cz * 16 + 8
            
            # Platforma stone 5x5
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    editor.set_block(
                        Pos(center_x + dx, y_level - 1, center_z + dz),
                        stone_id, 0
                    )
            
            if step == 0:
                # Start - redstone block
                editor.set_block(
                    Pos(center_x, y_level, center_z),
                    redstone_block_id, 0
                )
                logger.debug(f"Step {step}: Redstone block at ({center_x}, {y_level}, {center_z})")
            else:
                # Command block
                cb_x = center_x + 1
                cb_z = center_z
                command = f"/say [PROBE] REACHED cx={cx} cz={cz} step={step}"
                editor.set_command_block(
                    Pos(cb_x, y_level, cb_z),
                    command
                )
                logger.debug(f"Step {step}: Command block at ({cb_x}, {y_level}, {cb_z})")
    
    logger.info(f"Spirala zbudowana: {len(chunks)} chunków")
    return len(chunks)


def run_headless_test(world_path: str, duration: int = 120) -> Dict:
    """
    Uruchamia serwer headless i zbiera logi.
    
    Args:
        world_path: Ścieżka do świata
        duration: Czas trwania testu w sekundach
        
    Returns:
        Słownik z wynikami testu
    """
    server_dir = Path(world_path).parent
    logs_dir = server_dir / "logs"
    
    logger.info(f"Uruchamianie testu headless przez {duration}s...")
    
    # Wyczyść stare logi
    if logs_dir.exists():
        for f in logs_dir.glob("*.log"):
            f.unlink()
    
    # Uruchom serwer
    proc = subprocess.Popen(
        ["java", "-Xmx1G", "-Xms512M", "-jar", "minecraft_server.1.7.10.jar", "nogui"],
        cwd=server_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Czekaj na uruchomienie
    start_time = time.time()
    server_ready = False
    while time.time() - start_time < 60:
        time.sleep(0.5)
        latest_log = logs_dir / "latest.log"
        if latest_log.exists():
            content = latest_log.read_text()
            if "Done (" in content:
                server_ready = True
                break
    
    if not server_ready:
        logger.warning("Serwer nie potwierdził gotowości w czasie 60s")
    else:
        logger.info("Serwer gotowy, zbieranie logów...")
    
    # Zbieraj logi przez duration
    actual_start = time.time()
    end_time = actual_start + duration
    all_probe_logs = []
    
    while time.time() < end_time:
        remaining = int(end_time - time.time())
        if remaining % 10 == 0:
            logger.info(f"Pozostało: {remaining}s")
        
        latest_log = logs_dir / "latest.log"
        if latest_log.exists():
            try:
                with open(latest_log, 'r') as f:
                    for line in f:
                        if '[PROBE]' in line and line not in all_probe_logs:
                            all_probe_logs.append(line.strip())
                            logger.info(f"Znaleziono: {line.strip()[:100]}")
            except:
                pass
        
        time.sleep(1)
    
    # Zatrzymaj serwer
    logger.info("Zatrzymywanie serwera...")
    try:
        proc.stdin.write("stop\n")
        proc.stdin.flush()
    except:
        pass
    
    try:
        proc.wait(timeout=30)
    except:
        proc.kill()
    
    # Analiza wyników
    return analyze_results(all_probe_logs)


def analyze_results(logs: List[str]) -> Dict:
    """
    Analizuje logi i zwraca wyniki testu.
    """
    pattern = r'\[PROBE\] REACHED cx=(-?\d+) cz=(-?\d+) step=(\d+)'
    
    unique_steps: Dict[int, Tuple[int, int]] = {}
    
    for line in logs:
        match = re.search(pattern, line)
        if match:
            cx = int(match.group(1))
            cz = int(match.group(2))
            step = int(match.group(3))
            if step not in unique_steps:
                unique_steps[step] = (cx, cz)
    
    sorted_steps = sorted(unique_steps.keys())
    
    result = {
        "total_logs": len(logs),
        "unique_steps": len(unique_steps),
        "max_step": sorted_steps[-1] if sorted_steps else -1,
        "steps": sorted_steps,
        "details": {step: unique_steps[step] for step in sorted_steps}
    }
    
    # Sprawdź czy są dziury
    if sorted_steps:
        expected = list(range(sorted_steps[-1] + 1))
        missing = [s for s in expected if s not in unique_steps]
        result["missing_steps"] = missing
        result["has_gaps"] = len(missing) > 0
        
        # WERYFIKACJA PASS/FAIL
        if len(sorted_steps) >= 2 and 0 in sorted_steps and 1 in sorted_steps:
            result["status"] = "PASS"
        else:
            result["status"] = "FAIL"
    else:
        result["missing_steps"] = []
        result["has_gaps"] = False
        result["status"] = "FAIL"
    
    return result


def main():
    """Główna funkcja testu"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Variant B: Spiralny kabel")
    parser.add_argument("--world", required=True, help="Ścieżka do świata")
    parser.add_argument("--radius", type=int, default=3, help="Promień spirali")
    parser.add_argument("--y-level", type=int, default=200, help="Wysokość Y")
    parser.add_argument("--duration", type=int, default=120, help="Czas testu")
    parser.add_argument("--skip-build", action="store_true", help="Pomiń budowanie")
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Kopia świata
    logger.info("Tworzenie kopii świata...")
    world_copy = WorldCopier.create_copy(args.world)
    
    try:
        # Budowanie spirali
        if not args.skip_build:
            build_spiral_structure(world_copy, args.radius, args.y_level)
        
        # Uruchomienie testu
        results = run_headless_test(world_copy, args.duration)
        
        # Podsumowanie
        print("\n" + "=" * 60)
        print("WYNIKI TESTU")
        print("=" * 60)
        print(f"Status: {results['status']}")
        print(f"Unikalne kroki: {results['unique_steps']}")
        print(f"Ostatni krok: {results['max_step']}")
        print(f"Dziury: {results['missing_steps']}")
        
        if results['steps']:
            print(f"\nPierwsze 10 kroków:")
            for step in results['steps'][:10]:
                cx, cz = results['details'][step]
                print(f"  step {step}: chunk ({cx}, {cz})")
        
        return 0 if results['status'] == 'PASS' else 1
        
    finally:
        # Sprzątanie
        import shutil
        shutil.rmtree(world_copy, ignore_errors=True)
        logger.info(f"Usunięto kopię świata: {world_copy}")


if __name__ == "__main__":
    sys.exit(main())
