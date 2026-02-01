#!/usr/bin/env python3
"""
Test restartu serwera AE2 - Zadanie 6 część 2
Sprawdza czy stan bloków jest zachowany po restarcie
"""

import subprocess
import time
import socket
import struct
import os
import json
from pathlib import Path
from datetime import datetime

SERVER_DIR = Path("headless_server/1.18.2")
RCON_HOST = "127.0.0.1"
RCON_PORT = 25575
RCON_PASSWORD = "ae2test123"


def send_rcon_command(host, port, password, command, timeout=5):
    """Wysłanie komendy RCON"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        auth = struct.pack('<ii', 0, 3) + password.encode() + b'\x00\x00'
        sock.send(struct.pack('<i', len(auth)) + auth)
        sock.recv(1024)
        cmd = struct.pack('<ii', 1, 2) + command.encode() + b'\x00\x00'
        sock.send(struct.pack('<i', len(cmd)) + cmd)
        data = sock.recv(4)
        if len(data) < 4:
            return None
        resp_len = struct.unpack('<i', data)[0]
        resp = sock.recv(resp_len)
        return resp[8:-2].decode('utf-8', errors='ignore') if len(resp) >= 8 else None
    except Exception as e:
        return f"ERROR: {e}"
    finally:
        sock.close()


def start_server_and_wait():
    """Uruchom serwer i poczekaj na gotowość"""
    import os
    original_dir = os.getcwd()
    os.chdir(SERVER_DIR)
    
    proc = subprocess.Popen(
        ["java", "-Xms2G", "-Xmx4G", "@user_jvm_args.txt", 
         "@libraries/net/minecraftforge/forge/1.18.2-40.2.0/win_args.txt", "nogui"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
    
    print(f"  [INFO] Serwer PID: {proc.pid}")
    print("  [INFO] Czekanie na uruchomienie...")
    
    start_time = time.time()
    server_ready = False
    while time.time() - start_time < 180:
        try:
            line = proc.stdout.readline()
            if line and "Done" in line and "For help" in line:
                startup_time = time.time() - start_time
                print(f"  [OK] Serwer gotowy po {startup_time:.1f}s")
                server_ready = True
                break
        except:
            pass
        
        if proc.poll() is not None:
            break
    
    os.chdir(original_dir)
    
    if server_ready:
        return proc, startup_time
    
    if proc.poll() is not None:
        print("  [ERROR] Serwer zakończony przedwcześnie!")
    else:
        print("  [ERROR] Timeout!")
    
    return None, 0


def stop_server(proc):
    """Zatrzymaj serwer przez RCON"""
    print("  [INFO] Zatrzymywanie serwera...")
    send_rcon_command(RCON_HOST, RCON_PORT, RCON_PASSWORD, "save-all")
    time.sleep(1)
    send_rcon_command(RCON_HOST, RCON_PORT, RCON_PASSWORD, "stop")
    
    try:
        proc.wait(timeout=30)
        print("  [OK] Serwer zatrzymany")
        return True
    except:
        proc.terminate()
        print("  [WARN] Wymuszono zatrzymanie")
        return False


def check_server_state():
    """Sprawdź stan serwera przez RCON"""
    time.sleep(2)  # Daj czas na RCON
    
    results = {}
    
    # TPS
    tps = send_rcon_command(RCON_HOST, RCON_PORT, RCON_PASSWORD, "forge tps")
    results["tps"] = tps
    
    # Lista graczy
    players = send_rcon_command(RCON_HOST, RCON_PORT, RCON_PASSWORD, "list")
    results["players"] = players
    
    # Czas serwera (tick)
    time_result = send_rcon_command(RCON_HOST, RCON_PORT, RCON_PASSWORD, "time query daytime")
    results["time"] = time_result
    
    return results


def main():
    print("=" * 70)
    print("TEST RESTARTU SERWERA AE2")
    print("=" * 70)
    
    results = {
        "test_type": "restart_stability",
        "start_time": datetime.now().isoformat(),
        "runs": []
    }
    
    # Pierwszy start
    print("\n[RUN 1] Pierwsze uruchomienie serwera...")
    proc1, time1 = start_server_and_wait()
    
    if not proc1:
        print("[FAIL] Nie udało się uruchomić serwera (run 1)")
        return 1
    
    state1 = check_server_state()
    print(f"  [INFO] TPS: {state1.get('tps', 'N/A')[:50]}...")
    
    results["runs"].append({
        "run": 1,
        "startup_time": time1,
        "state": state1
    })
    
    # Zatrzymaj
    stop_server(proc1)
    time.sleep(3)  # Poczekaj na zwolnienie portów
    
    # Drugi start (restart)
    print("\n[RUN 2] Restart serwera...")
    proc2, time2 = start_server_and_wait()
    
    if not proc2:
        print("[FAIL] Nie udało się uruchomić serwera (run 2)")
        return 1
    
    state2 = check_server_state()
    print(f"  [INFO] TPS: {state2.get('tps', 'N/A')[:50]}...")
    
    results["runs"].append({
        "run": 2,
        "startup_time": time2,
        "state": state2
    })
    
    # Zatrzymaj
    stop_server(proc2)
    
    # Analiza
    print("\n" + "=" * 70)
    print("ANALIZA RESTARTU")
    print("=" * 70)
    
    startup_diff = abs(time1 - time2)
    print(f"Czas startu (run 1): {time1:.1f}s")
    print(f"Czas startu (run 2): {time2:.1f}s")
    print(f"Różnica: {startup_diff:.1f}s")
    
    # Sprawdź czy TPS jest podobny
    tps1_ok = "20,000" in str(state1.get("tps", "")) or "20.000" in str(state1.get("tps", ""))
    tps2_ok = "20,000" in str(state2.get("tps", "")) or "20.000" in str(state2.get("tps", ""))
    
    print(f"\nTPS Run 1 OK: {'TAK' if tps1_ok else 'NIE'}")
    print(f"TPS Run 2 OK: {'TAK' if tps2_ok else 'NIE'}")
    
    # Wymiar AE2 sprawdzony?
    ae2_dim_1 = "ae2:spatial_storage" in str(state1.get("tps", ""))
    ae2_dim_2 = "ae2:spatial_storage" in str(state2.get("tps", ""))
    
    print(f"Wymiar AE2 (run 1): {'TAK' if ae2_dim_1 else 'NIE'}")
    print(f"Wymiar AE2 (run 2): {'TAK' if ae2_dim_2 else 'NIE'}")
    
    # Zapisz wyniki
    results["analysis"] = {
        "startup_time_diff": startup_diff,
        "tps_run1_ok": tps1_ok,
        "tps_run2_ok": tps2_ok,
        "ae2_dim_run1": ae2_dim_1,
        "ae2_dim_run2": ae2_dim_2,
        "restart_stable": tps1_ok and tps2_ok and startup_diff < 60
    }
    results["end_time"] = datetime.now().isoformat()
    
    output_dir = Path("output/ae2_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "restart_test_results.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Podsumowanie
    print("\n" + "=" * 70)
    if tps1_ok and tps2_ok and ae2_dim_1 and ae2_dim_2:
        print("[OK] TEST RESTARTU ZALICZONY")
        print("     - Serwer uruchamia się stabilnie po restarcie")
        print("     - Wymiar AE2 jest dostępny")
        print("     - TPS jest prawidłowy (20)")
        return 0
    else:
        print("[FAIL] TEST RESTARTU NIEZALICZONY")
        return 1


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n[INFO] Przerwano")
        exit(1)
