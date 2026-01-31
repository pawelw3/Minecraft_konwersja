#!/usr/bin/env python3
"""
Uruchamia test spiralny i zbiera logi.
"""

import os
import sys
import subprocess
import time
import re
from pathlib import Path

def main():
    script_dir = Path(__file__).parent
    server_dir = script_dir.parent / "1.7.10"
    log_file = script_dir / "spiral_test_output.log"
    duration = 120  # sekundy
    
    print("=" * 60)
    print("TEST SPIRALNY - Variant B")
    print("=" * 60)
    print(f"Czas trwania: {duration} sekund")
    print(f"Logi będą zapisywane do: {log_file}")
    print()
    
    # Sprawdź czy serwer istnieje
    server_jar = server_dir / "minecraft_server.1.7.10.jar"
    if not server_jar.exists():
        print(f"BŁĄD: Nie znaleziono serwera: {server_jar}")
        sys.exit(1)
    
    # Usuń stare logi
    logs_dir = server_dir / "logs"
    if logs_dir.exists():
        for f in logs_dir.iterdir():
            try:
                f.unlink()
            except:
                pass
    
    # Uruchom serwer
    print("Uruchamianie serwera...")
    process = subprocess.Popen(
        ["java", "-Xmx1G", "-Xms512M", "-jar", "minecraft_server.1.7.10.jar", "nogui"],
        cwd=server_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Czekaj na pełne uruchomienie
    start_time = time.time()
    server_ready = False
    timeout = 60
    
    while not server_ready and time.time() - start_time < timeout:
        time.sleep(0.5)
        latest_log = logs_dir / "latest.log"
        if latest_log.exists():
            try:
                content = latest_log.read_text()
                if "Done (" in content:
                    server_ready = True
            except:
                pass
    
    if not server_ready:
        print("OSTRZEŻENIE: Serwer nie potwierdził gotowości w czasie 60s")
    
    actual_start = time.time()
    print(f"Serwer uruchomiony! Rozpoczynam zbieranie logów na {duration} sekund...")
    print(f"Czas startu: {time.strftime('%H:%M:%S')}")
    print()
    
    # Zbieraj logi
    end_time = actual_start + duration
    all_logs = []
    
    while time.time() < end_time:
        remaining = int(end_time - time.time())
        print(f"\rPozostało: {remaining} sekund...    ", end="", flush=True)
        
        latest_log = logs_dir / "latest.log"
        if latest_log.exists():
            try:
                with open(latest_log, "r") as f:
                    for line in f:
                        if "[PROBE]" in line:
                            all_logs.append(line.strip())
            except:
                pass
        
        time.sleep(1)
    
    print()
    print()
    print("Zatrzymywanie serwera...")
    
    # Wyślij komendę stop
    try:
        process.stdin.write("stop\n")
        process.stdin.flush()
    except:
        pass
    
    # Czekaj na zatrzymanie
    try:
        process.wait(timeout=30)
    except:
        process.kill()
    
    # Zapisz logi
    with open(log_file, "w") as f:
        for line in all_logs:
            f.write(line + "\n")
    
    # Analiza wyników
    print()
    print("=" * 60)
    print("ANALIZA WYNIKÓW")
    print("=" * 60)
    
    unique_steps = {}
    pattern = r'\[PROBE\] REACHED cx=(-?\d+) cz=(-?\d+) step=(\d+)'
    
    for line in all_logs:
        match = re.search(pattern, line)
        if match:
            cx = int(match.group(1))
            cz = int(match.group(2))
            step = int(match.group(3))
            if step not in unique_steps:
                unique_steps[step] = (cx, cz)
    
    sorted_steps = sorted(unique_steps.keys())
    total_steps = 121  # Dla R=5
    
    print()
    print("Statystyki:")
    print(f"  Odebranych unikalnych kroków: {len(unique_steps)} / {total_steps}")
    if sorted_steps:
        print(f"  Ostatni odebrany krok: {sorted_steps[-1]}")
    
    if sorted_steps:
        # Sprawdź dziury
        expected = list(range(sorted_steps[-1] + 1))
        missing = [s for s in expected if s not in unique_steps]
        
        print()
        if missing:
            print("BRAKUJĄCE KROKI (dziury):")
            for m in missing:
                print(f"  - step {m}")
        else:
            print(f"Wszystkie kroki od 0 do {sorted_steps[-1]} są obecne!")
        
        print()
        print("Pierwsze 10 odebranych kroków:")
        for step in sorted_steps[:10]:
            cx, cz = unique_steps[step]
            print(f"  step {step}: chunk ({cx}, {cz})")
        
        if len(sorted_steps) > 10:
            print()
            print("Ostatnie 5 odebranych kroków:")
            for step in sorted_steps[-5:]:
                cx, cz = unique_steps[step]
                print(f"  step {step}: chunk ({cx}, {cz})")
    
    # WERYFIKACJA
    print()
    print("=" * 60)
    print("WERYFIKACJA TESTU:")
    if len(sorted_steps) >= 2 and 0 in sorted_steps and 1 in sorted_steps:
        print("  Status: PASS (sygnał przeszedł przez co najmniej 2 chunki)")
    else:
        print("  Status: FAIL (brak sygnału lub tylko start)")
    
    print()
    print(f"Pełne logi zapisane w: {log_file}")

if __name__ == "__main__":
    main()
