#!/usr/bin/env python3
"""
Skrypt automatyzujący uruchomienie Minecraft przez Shiginima Launcher
Kolejność okien: Dialog aktualizacji -> Żółte okno -> Czarne okno (launcher) -> Gra
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# Pywinauto imports
from pywinauto import Desktop, Application
from pywinauto.timings import TimeoutError

# Konfiguracja
LAUNCHER_PATH = r"F:\Users\pawel\Downloads\ShiginimaSE_v3100\Windows\Shiginima Launcher SE v3.100.exe"
MINECRAFT_PROFILE = "JanuszGasikot"
TIMEOUT = 30  # sekundy

def find_window_by_title(title_keywords, timeout=10):
    """Znajdź okno po słowach kluczowych w tytule"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            desktop = Desktop(backend="win32")
            for window in desktop.windows():
                try:
                    window_title = window.window_text()
                    if any(keyword.lower() in window_title.lower() for keyword in title_keywords):
                        print(f"[OK] Znaleziono okno: '{window_title}'")
                        return window
                except:
                    continue
        except Exception as e:
            print(f"[DEBUG] Błąd podczas szukania okna: {e}")
        time.sleep(0.5)
    return None

def handle_update_dialog():
    """Obsługa dialogu aktualizacji - kliknij Cancel lub Ok"""
    print("[INFO] Szukam dialogu aktualizacji...")
    dialog = find_window_by_title(["Launcher Update", "Update is Available"], timeout=10)
    
    if dialog:
        print("[INFO] Znaleziono dialog aktualizacji")
        try:
            # Spróbuj znaleźć przycisk Cancel
            cancel_btn = dialog.child_window(title="Cancel", control_type="Button")
            if cancel_btn.exists():
                cancel_btn.click()
                print("[OK] Kliknięto 'Cancel' w dialogu aktualizacji")
                time.sleep(1)
                return True
            
            # Albo Ok
            ok_btn = dialog.child_window(title="Ok", control_type="Button")
            if ok_btn.exists():
                ok_btn.click()
                print("[OK] Kliknięto 'Ok' w dialogu aktualizacji")
                time.sleep(1)
                return True
                
        except Exception as e:
            print(f"[WARN] Nie udało się znaleźć przycisku: {e}")
            # Fallback: kliknij współrzędnymi
            try:
                dialog.click_input(coords=(500, 350))  # Przybliżona pozycja Cancel
                print("[OK] Kliknięto współrzędnymi w dialogu")
                time.sleep(1)
                return True
            except Exception as e2:
                print(f"[ERROR] Nie udało się kliknąć dialogu: {e2}")
    else:
        print("[INFO] Nie znaleziono dialogu aktualizacji (może się nie pojawił)")
    
    return False

def click_play_in_launcher():
    """Znajdź launcher i kliknij Play"""
    print("[INFO] Szukam okna launchera...")
    
    launcher = find_window_by_title(["Shiginima Launcher"], timeout=15)
    
    if not launcher:
        print("[ERROR] Nie znaleziono okna launchera!")
        return False
    
    print(f"[INFO] Znaleziono launcher: {launcher.window_text()}")
    launcher.set_focus()
    time.sleep(1)
    
    try:
        # Metoda 1: Szukaj przycisku Play po tekście
        play_btn = launcher.child_window(title="Play", control_type="Button")
        if play_btn.exists():
            play_btn.click()
            print("[OK] Kliknięto przycisk 'Play'")
            return True
        
        # Metoda 2: Szukaj po klasie lub nazwie
        for child in launcher.children():
            try:
                if "play" in child.window_text().lower():
                    child.click()
                    print(f"[OK] Kliknięto element: {child.window_text()}")
                    return True
            except:
                continue
        
        # Metoda 3: Kliknij współrzędnymi (środek okna, dolna część gdzie jest Play)
        rect = launcher.rectangle()
        center_x = (rect.left + rect.right) // 2
        bottom_y = rect.bottom - 100  # 100px od dołu
        launcher.click_input(coords=(center_x, bottom_y))
        print(f"[OK] Kliknięto współrzędnymi: ({center_x}, {bottom_y})")
        return True
        
    except Exception as e:
        print(f"[ERROR] Błąd podczas klikania Play: {e}")
        return False

def wait_for_minecraft():
    """Czekaj na uruchomienie Minecraft"""
    print("[INFO] Czekam na uruchomienie Minecraft...")
    
    start_time = time.time()
    while time.time() - start_time < TIMEOUT:
        try:
            # Szukaj okna Minecraft lub Game Output
            desktop = Desktop(backend="win32")
            for window in desktop.windows():
                try:
                    title = window.window_text()
                    if any(x in title.lower() for x in ["minecraft", "game output", "mojang"]):
                        print(f"[OK] Minecraft uruchomiony: '{title}'")
                        return True
                except:
                    continue
        except:
            pass
        time.sleep(1)
    
    print("[WARN] Timeout - Minecraft może się uruchamiać w tle")
    return False

def main():
    print("=" * 60)
    print("Automatyzacja Shiginima Launcher")
    print("=" * 60)
    
    # Sprawdź czy launcher istnieje
    if not os.path.exists(LAUNCHER_PATH):
        print(f"[ERROR] Nie znaleziono launchera: {LAUNCHER_PATH}")
        sys.exit(1)
    
    # Uruchom launcher
    print(f"[INFO] Uruchamiam launcher: {LAUNCHER_PATH}")
    try:
        subprocess.Popen([LAUNCHER_PATH], shell=True)
        time.sleep(3)  # Poczekaj na uruchomienie
    except Exception as e:
        print(f"[ERROR] Nie udało się uruchomić launchera: {e}")
        sys.exit(1)
    
    # Krok 1: Obsługa dialogu aktualizacji (jeśli się pojawi)
    handle_update_dialog()
    
    # Krok 2: Kliknij Play w launcherze (żółte lub czarne okno)
    if not click_play_in_launcher():
        print("[ERROR] Nie udało się kliknąć Play!")
        sys.exit(1)
    
    # Krok 3: Czekaj na Minecraft
    wait_for_minecraft()
    
    print("=" * 60)
    print("[SUCCESS] Launcher powinien uruchomić Minecraft")
    print("[INFO] Sprawdź okno gry lub logi w launcherze")
    print("=" * 60)

if __name__ == "__main__":
    main()
