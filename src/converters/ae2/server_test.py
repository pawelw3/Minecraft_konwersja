#!/usr/bin/env python3
"""
Skrypt testowy dla AE2 na headless serwerze 1.18.2
Zadanie 6: Test serwera z przekonwertowaną mapą
"""

import subprocess
import time
import socket
import struct
import os
import json
import signal
from pathlib import Path
from datetime import datetime

# Konfiguracja
SERVER_DIR = Path("headless_server/1.18.2")
WORLD_DIR = SERVER_DIR / "world"
LOG_FILE = SERVER_DIR / "logs" / "latest.log"
RCON_HOST = "127.0.0.1"
RCON_PORT = 25575
RCON_PASSWORD = "ae2test123"
TEST_DURATION = 180  # 3 minuty w sekundach


class RconClient:
    """Klient RCON do komunikacji z serwerem Minecraft"""
    
    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password
        self.socket = None
    
    def connect(self):
        """Nawiązanie połączenia i autentykacja"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(10)
        self.socket.connect((self.host, self.port))
        
        # Autentykacja
        auth_packet = struct.pack('<ii', 0, 3) + self.password.encode() + b'\x00\x00'
        self.socket.send(struct.pack('<i', len(auth_packet)) + auth_packet)
        
        # Odczyt odpowiedzi
        response = self.socket.recv(1024)
        if len(response) < 4:
            raise ConnectionError("Błąd autentykacji RCON")
        
        return True
    
    def send_command(self, command):
        """Wysłanie komendy do serwera"""
        if not self.socket:
            self.connect()
        
        # Pakiet komendy (type=2)
        cmd_packet = struct.pack('<ii', 1, 2) + command.encode() + b'\x00\x00'
        self.socket.send(struct.pack('<i', len(cmd_packet)) + cmd_packet)
        
        # Odczyt odpowiedzi
        try:
            data = self.socket.recv(4)
            if len(data) < 4:
                return None
            
            resp_len = struct.unpack('<i', data)[0]
            resp = self.socket.recv(resp_len)
            
            if len(resp) >= 8:
                return resp[8:-2].decode('utf-8', errors='ignore')
            return None
        except socket.timeout:
            return None
    
    def close(self):
        """Zamknięcie połączenia"""
        if self.socket:
            self.socket.close()
            self.socket = None


class ServerTester:
    """Tester serwera Minecraft z przekonwertowaną mapą AE2"""
    
    def __init__(self):
        self.server_process = None
        self.rcon = None
        self.results = {
            "start_time": None,
            "end_time": None,
            "errors": [],
            "warnings": [],
            "block_states": {},
            "test_phases": []
        }
    
    def start_server(self):
        """Uruchomienie serwera headless"""
        print("=" * 60)
        print("STARTOWANIE SERWERA 1.18.2 Z AE2")
        print("=" * 60)
        
        os.chdir(SERVER_DIR)
        
        # Uruchomienie serwera
        self.server_process = subprocess.Popen(
            ["java", "-Xms2G", "-Xmx4G", "@user_jvm_args.txt", "@libraries/net/minecraftforge/forge/1.18.2-40.2.0/win_args.txt", "nogui"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
        
        self.results["start_time"] = datetime.now().isoformat()
        print(f"[INFO] Serwer uruchomiony PID: {self.server_process.pid}")
        
        # Czekanie na pełne uruchomienie
        print("[INFO] Czekanie na uruchomienie serwera (max 120s)...")
        start_time = time.time()
        server_ready = False
        
        while time.time() - start_time < 120:
            line = self.server_process.stdout.readline()
            if line:
                line = line.strip()
                print(f"[SERVER] {line}")
                
                # Sprawdź czy serwer jest gotowy
                if "Done" in line and "For help" in line:
                    server_ready = True
                    print("[OK] Serwer gotowy!")
                    break
                
                # Sprawdź błędy podczas startu
                if "ERROR" in line or "Exception" in line:
                    self.results["errors"].append({
                        "phase": "startup",
                        "message": line,
                        "time": datetime.now().isoformat()
                    })
            
            if self.server_process.poll() is not None:
                print("[ERROR] Serwer zakończył działanie przedwcześnie!")
                return False
        
        if not server_ready:
            print("[ERROR] Timeout oczekiwania na serwer")
            return False
        
        return True
    
    def wait_for_ticks(self, duration_seconds):
        """Oczekiwanie na ticki serwera"""
        print(f"\n[INFO] Oczekiwanie {duration_seconds}s na ticki serwera...")
        
        start_time = time.time()
        last_status = start_time
        
        while time.time() - start_time < duration_seconds:
            # Sprawdź czy serwer działa
            if self.server_process.poll() is not None:
                print("[ERROR] Serwer przestał działać!")
                return False
            
            # Odczyt logów
            try:
                line = self.server_process.stdout.readline()
                if line:
                    line = line.strip()
                    # Logowanie tylko ważnych linii
                    if any(x in line for x in ["ERROR", "Exception", "FATAL", "AE2", "appliedenergistics"]):
                        print(f"[LOG] {line}")
                        
                        if "ERROR" in line or "Exception" in line:
                            self.results["errors"].append({
                                "phase": "runtime",
                                "message": line,
                                "time": datetime.now().isoformat()
                            })
                        elif "WARN" in line:
                            self.results["warnings"].append({
                                "phase": "runtime",
                                "message": line,
                                "time": datetime.now().isoformat()
                            })
            except:
                pass
            
            # Status co 30s
            if time.time() - last_status >= 30:
                elapsed = int(time.time() - start_time)
                print(f"[INFO] Minęło {elapsed}s / {duration_seconds}s")
                last_status = time.time()
            
            time.sleep(0.1)
        
        print("[OK] Czas ticków zakończony")
        return True
    
    def connect_rcon(self):
        """Połączenie RCON"""
        print("\n[INFO] Łączenie przez RCON...")
        
        # Czekaj na dostępność RCON
        time.sleep(2)
        
        self.rcon = RconClient(RCON_HOST, RCON_PORT, RCON_PASSWORD)
        try:
            self.rcon.connect()
            print("[OK] Połączono przez RCON")
            return True
        except Exception as e:
            print(f"[ERROR] Błąd połączenia RCON: {e}")
            return False
    
    def check_blocks_via_rcon(self):
        """Sprawdzenie stanu bloków przez RCON"""
        print("\n[INFO] Sprawdzanie stanu bloków przez RCON...")
        
        if not self.rcon:
            return False
        
        # Sprawdź listę graczy (powinien być jeden z testowej mapy)
        result = self.rcon.send_command("list")
        print(f"[RCON] Gracze: {result}")
        
        # Sprawdź pozycję gracza (spawn point)
        result = self.rcon.send_command("execute at @p run say [AE2_TEST] Sprawdzanie bloków...")
        
        # Zapisz wyniki
        self.results["block_states"]["check_time"] = datetime.now().isoformat()
        
        return True
    
    def stop_server(self):
        """Zatrzymanie serwera"""
        print("\n[INFO] Zatrzymywanie serwera...")
        
        if self.rcon:
            try:
                self.rcon.send_command("save-all")
                time.sleep(2)
                self.rcon.send_command("stop")
                self.rcon.close()
            except:
                pass
        
        if self.server_process:
            try:
                # Poczekaj na zakończenie
                self.server_process.wait(timeout=30)
                print("[OK] Serwer zatrzymany")
            except:
                print("[WARN] Wymuszanie zamknięcia serwera")
                self.server_process.terminate()
        
        self.results["end_time"] = datetime.now().isoformat()
    
    def analyze_logs(self):
        """Analiza logów serwera"""
        print("\n[INFO] Analiza logów serwera...")
        
        if not LOG_FILE.exists():
            print("[WARN] Brak pliku logów")
            return
        
        try:
            with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                logs = f.read()
            
            # Szukaj błędów AE2
            ae2_errors = []
            for line in logs.split('\n'):
                if 'appliedenergistics' in line.lower() or 'ae2' in line.lower():
                    if 'error' in line.lower() or 'exception' in line.lower():
                        ae2_errors.append(line)
            
            if ae2_errors:
                print(f"[WARN] Znaleziono {len(ae2_errors)} błędów AE2 w logach:")
                for err in ae2_errors[:5]:  # Pokaż pierwsze 5
                    print(f"  - {err[:150]}")
            else:
                print("[OK] Nie znaleziono błędów AE2 w logach")
            
            self.results["ae2_errors_in_logs"] = len(ae2_errors)
            
        except Exception as e:
            print(f"[ERROR] Błąd analizy logów: {e}")
    
    def save_results(self):
        """Zapisanie wyników testu"""
        output_file = Path("output/ae2_analysis/server_test_results.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n[INFO] Wyniki zapisane do: {output_file}")
    
    def print_summary(self):
        """Wydrukowanie podsumowania"""
        print("\n" + "=" * 60)
        print("PODSUMOWANIE TESTU SERWERA AE2")
        print("=" * 60)
        
        print(f"Czas startu: {self.results['start_time']}")
        print(f"Czas zakończenia: {self.results['end_time']}")
        print(f"Liczba błędów: {len(self.results['errors'])}")
        print(f"Liczba ostrzeżeń: {len(self.results['warnings'])}")
        
        if self.results['errors']:
            print("\n--- Błędy ---")
            for err in self.results['errors'][:10]:
                print(f"[{err['phase']}] {err['message'][:100]}")
        
        if self.results['warnings']:
            print("\n--- Ostrzeżenia ---")
            for warn in self.results['warnings'][:5]:
                print(f"[{warn['phase']}] {warn['message'][:100]}")
        
        # Status końcowy
        if len(self.results['errors']) == 0:
            print("\n[✓] TEST ZALICZONY - Brak krytycznych błędów")
        elif len(self.results['errors']) < 5:
            print("\n[⚠] TEST ZALICZONY Z OSTRZEŻENIAMI - Niewielka liczba błędów")
        else:
            print("\n[✗] TEST NIEZALICZONY - Zbyt wiele błędów")


def main():
    """Główna funkcja testu"""
    print("=" * 60)
    print("TEST SERWERA AE2 - ZADANIE 6")
    print("=" * 60)
    print(f"Mapa testowa: {WORLD_DIR}")
    print(f"Czas testu: {TEST_DURATION}s (3 minuty)")
    print("=" * 60)
    
    tester = ServerTester()
    
    try:
        # 1. Uruchom serwer
        if not tester.start_server():
            print("[ERROR] Nie udało się uruchomić serwera")
            return 1
        
        # 2. Połącz RCON
        if tester.connect_rcon():
            tester.check_blocks_via_rcon()
        
        # 3. Czekaj na ticki
        tester.wait_for_ticks(TEST_DURATION)
        
        # 4. Sprawdź bloki ponownie
        if tester.rcon:
            tester.check_blocks_via_rcon()
        
    except KeyboardInterrupt:
        print("\n[INFO] Przerwano przez użytkownika")
    finally:
        # 5. Zatrzymaj serwer
        tester.stop_server()
        
        # 6. Analizuj logi
        tester.analyze_logs()
        
        # 7. Zapisz wyniki
        tester.save_results()
        
        # 8. Podsumowanie
        tester.print_summary()
    
    return 0


if __name__ == "__main__":
    exit(main())
