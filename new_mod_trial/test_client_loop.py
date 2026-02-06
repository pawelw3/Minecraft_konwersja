#!/usr/bin/env python3
"""
Pełna pętla testowa dla moda CuttableBlocks:
1. Buduje moda (gradle)
2. Kopiuje JAR do mods\
3. Uruchamia launcher (pywinauto)
4. Monitoruje logi klienta
5. Wykrywa crash-e i błędy
6. Generuje raport
"""

import os
import sys
import re
import time
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# Konfiguracja
PROJECT_DIR = Path(r"C:\Users\pawel\Minecraft_konwersja\new_mod_trial")
MINECRAFT_DIR = Path(os.path.expandvars(r"%APPDATA%\.minecraft"))
MODS_DIR = MINECRAFT_DIR / "mods"
LOGS_DIR = MINECRAFT_DIR / "logs"
CRASH_REPORTS_DIR = MINECRAFT_DIR / "crash-reports"
LAUNCHER_PATH = r"F:\Users\pawel\Downloads\ShiginimaSE_v3100\Windows\Shiginima Launcher SE v3.100.exe"

# Pliki do monitorowania
CLIENT_LOG = LOGS_DIR / "fml-client-latest.log"
GAME_OUTPUT_LOG = LOGS_DIR / "latest.log"

class ModTestLoop:
    def __init__(self):
        self.test_start_time = datetime.now()
        self.errors_found = []
        self.critical_errors = []
        self.mod_loaded = False
        
    def log(self, msg, level="INFO"):
        """Logowanie z timestampem"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {msg}")
        
    def build_mod(self):
        """Krok 1: Zbuduj moda przez Gradle"""
        self.log("=" * 60)
        self.log("KROK 1: Budowanie moda")
        self.log("=" * 60)
        
        os.chdir(PROJECT_DIR)
        
        # Uruchom gradlew build
        cmd = [r".\gradlew.bat", "build", "--no-daemon"]
        self.log(f"Wykonuję: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            self.log("BŁĄD BUDOWANIA:", "ERROR")
            self.log(result.stderr[-1000:], "ERROR")  # Ostatnie 1000 znaków
            return False
            
        # Sprawdź czy JAR powstał
        jar_path = PROJECT_DIR / "build" / "libs" / "CuttableBlocks-1.0.0.jar"
        if jar_path.exists():
            self.log(f"✅ Zbudowano: {jar_path}")
            return jar_path
        else:
            self.log("❌ Nie znaleziono pliku JAR!", "ERROR")
            return False
            
    def deploy_mod(self, jar_path):
        """Krok 2: Skopiuj JAR do mods\\"""
        self.log("=" * 60)
        self.log("KROK 2: Deploy moda")
        self.log("=" * 60)
        
        # Upewnij się że folder mods istnieje
        MODS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Kopiuj
        dest_path = MODS_DIR / "CuttableBlocks-1.0.0.jar"
        try:
            shutil.copy2(jar_path, dest_path)
            self.log(f"✅ Skopiowano do: {dest_path}")
            return True
        except Exception as e:
            self.log(f"❌ Błąd kopiowania: {e}", "ERROR")
            return False
            
    def clear_old_logs(self):
        """Wyczyść stare logi przed testem"""
        self.log("Czyszczenie starych logów...")
        
        files_to_clear = [
            CLIENT_LOG,
            GAME_OUTPUT_LOG
        ]
        
        for f in files_to_clear:
            if f.exists():
                try:
                    f.unlink()
                    self.log(f"  Usunięto: {f.name}")
                except:
                    pass
                    
    def launch_client(self):
        """Krok 3: Uruchom klienta przez launcher"""
        self.log("=" * 60)
        self.log("KROK 3: Uruchamianie klienta")
        self.log("=" * 60)
        
        # Importuj pywinauto tylko gdy potrzebne
        try:
            from pywinauto import Desktop, Application
        except ImportError:
            self.log("❌ Pywinauto nie zainstalowane! Uruchom: pip install pywinauto", "ERROR")
            return False
            
        # Uruchom launcher
        self.log(f"Uruchamiam: {LAUNCHER_PATH}")
        try:
            subprocess.Popen([LAUNCHER_PATH], shell=True)
        except Exception as e:
            self.log(f"❌ Błąd uruchamiania: {e}", "ERROR")
            return False
            
        time.sleep(3)
        
        # Obsługa okien
        return self._handle_launcher_windows()
        
    def _handle_launcher_windows(self):
        """Obsługa okien launchera"""
        from pywinauto import Desktop
        
        # Czekaj na okno launchera
        self.log("Czekam na okno launchera...")
        launcher = None
        for i in range(20):  # 20 prób = 20 sekund
            try:
                desktop = Desktop(backend="win32")
                for window in desktop.windows():
                    try:
                        if "Shiginima Launcher" in window.window_text():
                            launcher = window
                            break
                    except:
                        continue
                if launcher:
                    break
            except:
                pass
            time.sleep(1)
            
        if not launcher:
            self.log("❌ Nie znaleziono okna launchera", "ERROR")
            return False
            
        self.log(f"✅ Znaleziono: {launcher.window_text()}")
        
        # Sprawdź czy jest dialog aktualizacji
        try:
            for window in desktop.windows():
                title = window.window_text()
                if "Update" in title or "Aktualizacja" in title:
                    self.log(f"Znaleziono dialog: {title}")
                    # Kliknij Cancel
                    try:
                        window.child_window(title="Cancel").click()
                        self.log("✅ Kliknięto Cancel")
                        time.sleep(1)
                    except:
                        # Fallback: kliknij pierwszy przycisk
                        window.click_input(coords=(300, 200))
                        self.log("Kliknięto współrzędnymi")
                        time.sleep(1)
        except Exception as e:
            self.log(f"Brak dialogu aktualizacji lub błąd: {e}")
            
        # Kliknij Play
        self.log("Szukam przycisku Play...")
        try:
            launcher.set_focus()
            time.sleep(0.5)
            
            # Spróbuj znaleźć przycisk Play
            play_found = False
            for child in launcher.children():
                try:
                    text = child.window_text()
                    if "play" in text.lower():
                        child.click()
                        self.log(f"✅ Kliknięto: {text}")
                        play_found = True
                        break
                except:
                    continue
                    
            if not play_found:
                # Fallback: kliknij w dolnej części okna
                rect = launcher.rectangle()
                x = (rect.left + rect.right) // 2
                y = rect.bottom - 80
                launcher.click_input(coords=(x, y))
                self.log(f"✅ Kliknięto współrzędnymi: ({x}, {y})")
                
        except Exception as e:
            self.log(f"❌ Błąd klikania Play: {e}", "ERROR")
            return False
            
        return True
        
    def monitor_logs(self, duration=60):
        """Krok 4: Monitoruj logi przez N sekund"""
        self.log("=" * 60)
        self.log(f"KROK 4: Monitorowanie logów ({duration}s)")
        self.log("=" * 60)
        
        start_time = time.time()
        last_position = 0
        
        # Czekaj aż log się pojawi
        log_file = None
        for i in range(30):
            if CLIENT_LOG.exists():
                log_file = CLIENT_LOG
                break
            if GAME_OUTPUT_LOG.exists():
                log_file = GAME_OUTPUT_LOG
                break
            time.sleep(1)
            
        if not log_file:
            self.log("❌ Nie znaleziono pliku logów!", "ERROR")
            return False
            
        self.log(f"Monitoring: {log_file.name}")
        
        while time.time() - start_time < duration:
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(last_position)
                    new_lines = f.readlines()
                    last_position = f.tell()
                    
                for line in new_lines:
                    self._analyze_line(line)
                    
            except Exception as e:
                pass
                
            time.sleep(0.5)
            
        return True
        
    def _analyze_line(self, line):
        """Analizuj linię logu pod kątem błędów"""
        line = line.strip()
        if not line:
            return
            
        # Szukaj błędów związanych z modem
        cuttable_patterns = [
            r'cuttable.*error',
            r'cuttable.*exception',
            r'cuttableblocks.*error',
            r'cuttableblocks.*exception',
            r'CuttableTE.*error',
            r'CuttableTE.*exception',
            r'Unable to construct',
            r'NoSuchMethodError.*cuttable',
            r'ClassNotFoundException.*cuttable'
        ]
        
        for pattern in cuttable_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                self.critical_errors.append(line)
                self.log(f"🚨 BŁĄD MODA: {line}", "CRITICAL")
                return
                
        # Ogólne błędy FML/Forge
        if "FML" in line and "ERROR" in line:
            self.errors_found.append(line)
            self.log(f"⚠️  FML ERROR: {line[:100]}", "WARNING")
            
        # Sprawdź czy mod się załadował
        if "cuttableblocks" in line.lower() and "mod" in line.lower():
            if "loaded" in line.lower() or "construction" in line.lower():
                self.mod_loaded = True
                self.log(f"✅ Mod załadowany: {line[:80]}")
                
    def check_for_crashes(self):
        """Krok 5: Sprawdź czy był crash"""
        self.log("=" * 60)
        self.log("KROK 5: Sprawdzanie crashy")
        self.log("=" * 60)
        
        if CRASH_REPORTS_DIR.exists():
            crashes = list(CRASH_REPORTS_DIR.glob("crash-*.txt"))
            
            # Filtruj tylko nowe crash-e (z ostatnich 5 minut)
            recent_crashes = []
            for crash in crashes:
                try:
                    mtime = crash.stat().st_mtime
                    age_minutes = (time.time() - mtime) / 60
                    if age_minutes < 5:
                        recent_crashes.append(crash)
                except:
                    pass
                    
            if recent_crashes:
                self.log(f"🚨 ZNALEZIONO {len(recent_crashes)} NOWYCH CRASHY!", "CRITICAL")
                for crash in recent_crashes:
                    self.log(f"   - {crash.name}")
                    # Przeczytaj pierwsze 20 linii
                    try:
                        with open(crash, 'r') as f:
                            lines = f.readlines()[:20]
                            for line in lines:
                                if 'cuttable' in line.lower():
                                    self.log(f"     >>> {line.strip()}", "CRITICAL")
                    except:
                        pass
                return True
            else:
                self.log("✅ Brak nowych crashy")
                
        return False
        
    def generate_report(self):
        """Generuj raport końcowy"""
        self.log("=" * 60)
        self.log("RAPORT KOŃCOWY")
        self.log("=" * 60)
        
        duration = (datetime.now() - self.test_start_time).total_seconds()
        
        print()
        print("╔" + "═" * 58 + "╗")
        print("║" + " REZULTATY TESTU ".center(58) + "║")
        print("╠" + "═" * 58 + "╣")
        print(f"║ Czas trwania: {duration:.1f}s".ljust(59) + "║")
        print(f"║ Mod załadowany: {'✅ TAK' if self.mod_loaded else '❌ NIE'}".ljust(59) + "║")
        print(f"║ Błędy krytyczne: {len(self.critical_errors)}".ljust(59) + "║")
        print(f"║ Błędy ogólne: {len(self.errors_found)}".ljust(59) + "║")
        print("╠" + "═" * 58 + "╣")
        
        if self.critical_errors:
            print("║ 🚨 BŁĘDY MODA (wymagają poprawki):".ljust(59) + "║")
            for err in self.critical_errors[:3]:  # Max 3 błędy
                short = err[:55] + "..." if len(err) > 55 else err
                print(f"║    {short}".ljust(59) + "║")
                
        print("╚" + "═" * 58 + "╝")
        
        return len(self.critical_errors) == 0 and self.mod_loaded
        
    def run_full_test(self):
        """Uruchom pełną pętlę testową"""
        try:
            # 1. Build
            jar = self.build_mod()
            if not jar:
                return False
                
            # 2. Deploy
            if not self.deploy_mod(jar):
                return False
                
            # 3. Clear logs
            self.clear_old_logs()
            
            # 4. Launch
            if not self.launch_client():
                return False
                
            # 5. Monitor
            self.monitor_logs(duration=60)
            
            # 6. Check crashes
            self.check_for_crashes()
            
            # 7. Report
            success = self.generate_report()
            
            return success
            
        except KeyboardInterrupt:
            self.log("Przerwano przez użytkownika", "WARNING")
            return False
        except Exception as e:
            self.log(f"🚨 Błąd krytyczny: {e}", "CRITICAL")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("PĘTLA TESTOWA MODA CUTTABLEBLOCKS")
    print("=" * 60)
    print()
    print("Co ten skrypt robi:")
    print("  1. Buduje moda (gradle build)")
    print("  2. Kopiuje JAR do .minecraft\\mods\\")
    print("  3. Uruchamia Shiginima Launcher")
    print("  4. Klika Play")
    print("  5. Monitoruje logi (60s)")
    print("  6. Szuka błędów związanych z modem")
    print("  7. Generuje raport")
    print()
    input("Naciśnij ENTER aby rozpocząć...")
    print()
    
    tester = ModTestLoop()
    success = tester.run_full_test()
    
    sys.exit(0 if success else 1)
