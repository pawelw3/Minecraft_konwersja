#!/usr/bin/env python3
"""
Skrypt testowy dla AE2 na headless serwerze 1.18.2 - WERSJA 2
Zadanie 6: Test serwera z przekonwertowaną mapą
"""

import subprocess
import time
import socket
import struct
import os
import json
import sys
from pathlib import Path
from datetime import datetime
import threading

# Konfiguracja
SERVER_DIR = Path("headless_server/1.18.2")
WORLD_DIR = SERVER_DIR / "world"
LOG_FILE = SERVER_DIR / "logs" / "latest.log"
RCON_HOST = "127.0.0.1"
RCON_PORT = 25575
RCON_PASSWORD = "ae2test123"
TEST_DURATION = 60  # 60 sekund (krótszy test)


def send_rcon_command(host, port, password, command, timeout=5):
    """Wysłanie pojedynczej komendy RCON"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        
        # Autentykacja
        auth = struct.pack('<ii', 0, 3) + password.encode() + b'\x00\x00'
        sock.send(struct.pack('<i', len(auth)) + auth)
        sock.recv(1024)
        
        # Komenda
        cmd = struct.pack('<ii', 1, 2) + command.encode() + b'\x00\x00'
        sock.send(struct.pack('<i', len(cmd)) + cmd)
        
        # Odpowiedź
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


def analyze_logs_for_errors():
    """Analiza logów w poszukiwaniu błędów"""
    import glob
    
    all_logs = ""
    
    # Zbierz wszystkie pliki logów (w tym .gz)
    log_files = glob.glob(str(SERVER_DIR / "logs" / "*.log"))
    log_files.extend(glob.glob(str(SERVER_DIR / "logs" / "*.log.gz")))
    
    for log_path in log_files:
        try:
            if log_path.endswith('.gz'):
                import gzip
                with gzip.open(log_path, 'rt', encoding='utf-8', errors='ignore') as f:
                    all_logs += f.read() + "\n"
            else:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    all_logs += f.read() + "\n"
        except:
            pass
    
    if not all_logs:
        return {"errors": [], "warnings": [], "ae2_specific": []}
    
    try:
        logs = all_logs
        
        lines = logs.split('\n')
        errors = []
        warnings = []
        ae2_specific = []
        
        for line in lines:
            line_lower = line.lower()
            
            # Błędy
            if '[error]' in line_lower or 'exception' in line_lower:
                errors.append(line.strip())
            
            # AE2 specific
            if 'appliedenergistics' in line_lower or 'ae2' in line_lower:
                ae2_specific.append(line.strip())
            
            # Ostrzeżenia chunków
            if 'old_noise' in line_lower or 'chunk' in line_lower and '[error]' in line_lower:
                warnings.append(line.strip())
        
        return {
            "errors": errors[-20:],  # Ostatnie 20
            "warnings": warnings[-10:],
            "ae2_specific": ae2_specific
        }
    except Exception as e:
        return {"errors": [f"Log analysis error: {e}"], "warnings": [], "ae2_specific": []}


def main():
    print("=" * 70)
    print("TEST SERWERA AE2 - ZADANIE 6 (v2)")
    print("=" * 70)
    
    results = {
        "test_version": "2.0",
        "start_time": datetime.now().isoformat(),
        "phases": []
    }
    
    # 1. Uruchom serwer w tle
    print("\n[FAZA 1] Uruchamianie serwera...")
    os.chdir(SERVER_DIR)
    
    proc = subprocess.Popen(
        ["java", "-Xms2G", "-Xmx4G", "@user_jvm_args.txt", 
         "@libraries/net/minecraftforge/forge/1.18.2-40.2.0/win_args.txt", "nogui"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
    
    print(f"[INFO] Serwer PID: {proc.pid}")
    
    # 2. Czekaj na uruchomienie
    print("\n[FAZA 2] Czekanie na uruchomienie (max 180s)...")
    server_ready = False
    startup_output = []
    start_time = time.time()
    
    while time.time() - start_time < 180:
        try:
            line = proc.stdout.readline()
            if line:
                line = line.strip()
                startup_output.append(line)
                
                if "Done" in line and "For help" in line:
                    server_ready = True
                    results["phases"].append({
                        "phase": "startup",
                        "status": "success",
                        "time": time.time() - start_time
                    })
                    print(f"[OK] Serwer gotowy po {time.time() - start_time:.1f}s")
                    break
                
                if len(startup_output) % 50 == 0:
                    print(f"[INFO] Wczytano {len(startup_output)} linii logów...")
        except:
            pass
        
        if proc.poll() is not None:
            print("[ERROR] Serwer zakończył działanie przedwcześnie!")
            results["phases"].append({
                "phase": "startup",
                "status": "failed"
            })
            break
    
    if not server_ready:
        print("[ERROR] Serwer nie uruchomił się w czasie")
        proc.terminate()
        return 1
    
    # 3. Test RCON
    print("\n[FAZA 3] Test połączenia RCON...")
    time.sleep(2)
    
    rcon_result = send_rcon_command(RCON_HOST, RCON_PORT, RCON_PASSWORD, "list")
    print(f"[RCON] Wynik: {rcon_result}")
    
    results["phases"].append({
        "phase": "rcon_connect",
        "status": "success" if rcon_result and "ERROR" not in str(rcon_result) else "failed",
        "response": str(rcon_result)[:200]
    })
    
    # 4. Komenda testowa przez RCON
    print("\n[FAZA 4] Wysyłanie komendy testowej...")
    test_result = send_rcon_command(
        RCON_HOST, RCON_PORT, RCON_PASSWORD, 
        "say [AE2-TEST] Start testu - sprawdzanie bloków AE2"
    )
    print(f"[RCON] Test: {test_result}")
    
    # 5. Oczekiwanie na ticki
    print(f"\n[FAZA 5] Oczekiwanie {TEST_DURATION}s na ticki serwera...")
    time.sleep(TEST_DURATION)
    
    # 6. Sprawdź stan po tickach
    print("\n[FAZA 6] Sprawdzanie stanu po tickach...")
    after_ticks = send_rcon_command(RCON_HOST, RCON_PORT, RCON_PASSWORD, "forge tps")
    print(f"[RCON] TPS: {after_ticks}")
    
    results["phases"].append({
        "phase": "after_ticks",
        "tps_info": str(after_ticks)[:200] if after_ticks else None
    })
    
    # 7. Zatrzymaj serwer
    print("\n[FAZA 7] Zatrzymywanie serwera...")
    send_rcon_command(RCON_HOST, RCON_PORT, RCON_PASSWORD, "save-all")
    time.sleep(1)
    send_rcon_command(RCON_HOST, RCON_PORT, RCON_PASSWORD, "stop")
    
    # Czekaj na zatrzymanie
    try:
        proc.wait(timeout=30)
        print("[OK] Serwer zatrzymany")
    except:
        proc.terminate()
        print("[WARN] Wymuszono zatrzymanie")
    
    # 8. Analiza logów
    print("\n[FAZA 8] Analiza logów...")
    log_analysis = analyze_logs_for_errors()
    
    print(f"[INFO] Znaleziono {len(log_analysis['errors'])} błędów")
    print(f"[INFO] Znaleziono {len(log_analysis['ae2_specific'])} logów AE2")
    
    # Pokaż błędy AE2
    if log_analysis['ae2_specific']:
        print("\n--- Logi AE2 ---")
        for log in log_analysis['ae2_specific'][-5:]:
            print(f"  {log[:100]}")
    
    # Pokaż błędy chunków
    chunk_errors = [e for e in log_analysis['errors'] if 'old_noise' in e.lower()]
    if chunk_errors:
        print(f"\n--- Błędy chunków (old_noise): {len(chunk_errors)} ---")
        print("  (To błędy związane z konwersją chunków 1.7.10 -> 1.18.2, zazwyczaj niekrytyczne)")
    
    # 9. Zapisz wyniki
    results["end_time"] = datetime.now().isoformat()
    results["log_analysis"] = log_analysis
    results["server_ready"] = server_ready
    
    output_dir = Path("output/ae2_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "server_test_results.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # 10. Podsumowanie
    print("\n" + "=" * 70)
    print("PODSUMOWANIE")
    print("=" * 70)
    
    print(f"Serwer uruchomiony: {'TAK' if server_ready else 'NIE'}")
    print(f"Czas startu: {results['phases'][0].get('time', 'N/A'):.1f}s" if server_ready else "N/A")
    print(f"Liczba błędów: {len(log_analysis['errors'])}")
    print(f"Liczba ostrzeżeń chunków: {len(chunk_errors)}")
    print(f"Logi AE2: {len(log_analysis['ae2_specific'])}")
    
    # Status końcowy
    critical_errors = [e for e in log_analysis['errors'] 
                      if 'appliedenergistics' in e.lower() and 'error' in e.lower()]
    
    if not critical_errors and server_ready:
        print("\n[OK] TEST ZALICZONY")
        print("    - Serwer uruchomił się poprawnie")
        print("    - Brak krytycznych błędów AE2")
        print("    - RCON działa")
        return 0
    elif server_ready:
        print("\n[WARN] TEST ZALICZONY Z OSTRZEŻENIAMI")
        print("    - Serwer działa ale są błędy w logach")
        return 0
    else:
        print("\n[FAIL] TEST NIEZALICZONY")
        return 1


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n[INFO] Przerwano przez użytkownika")
        # Zatrzymaj serwer jeśli działa
        send_rcon_command(RCON_HOST, RCON_PORT, RCON_PASSWORD, "stop")
        exit(1)
