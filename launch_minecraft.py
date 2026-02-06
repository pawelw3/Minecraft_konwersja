#!/usr/bin/env python3
"""
Automatyzacja Shiginima Launcher SE v3.100
Przechodzi przez wszystkie 3 okna: Update -> Sponge Edition -> News -> Gra
"""

import subprocess
import time
import sys
from pywinauto import Desktop, Application

# Konfiguracja
LAUNCHER_PATH = r"F:\Users\pawel\Downloads\ShiginimaSE_v3100\Windows\Shiginima Launcher SE v3.100.exe"


def find_window(title_patterns, exclude_patterns=None, timeout=30):
    """Znajduje okno pasujace do wzorca tytulu"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        desktop = Desktop(backend='win32')
        for window in desktop.windows():
            try:
                title = window.window_text()
                matches = any(pattern.lower() in title.lower() for pattern in title_patterns)
                excluded = exclude_patterns and any(exc.lower() in title.lower() for exc in exclude_patterns)
                if matches and not excluded:
                    return window
            except:
                pass
        time.sleep(0.2)
    return None


def click_update_dialog():
    """Klik OK w dialogu aktualizacji"""
    print("[1/4] Czekam na dialog aktualizacji...")
    dialog = find_window(["Launcher Update"], timeout=15)
    if not dialog:
        print("      Dialog nie pojawil sie (kontynuuje)...")
        return True
    
    print("      Znaleziono dialog, klikam OK...")
    rect = dialog.rectangle()
    width = rect.right - rect.left
    height = rect.bottom - rect.top
    
    # OK jest na dole po lewej stronie (~20% szerokosci, ~85% wysokosci)
    ok_x = int(width * 0.20)
    ok_y = int(height * 0.85)
    
    dialog.click_input(coords=(ok_x, ok_y))
    print(f"      OK klikniete @ ({ok_x}, {ok_y})")
    time.sleep(1)
    return True


def click_play_in_sponge_window():
    """Klik Play w zoltym oknie (Sponge Edition)"""
    print("[2/4] Czekam na zolte okno (Sponge Edition)...")
    
    window = find_window(["Shiginima"], exclude_patterns=["Update"], timeout=30)
    if not window:
        print("      Nie znaleziono zoltego okna!")
        return False
    
    rect = window.rectangle()
    width = rect.right - rect.left
    height = rect.bottom - rect.top
    
    # Zolte okno ma mniejsza szerokosc niz czarne (zazwyczaj < 700)
    if width > 800:
        print(f"      To nie jest zolte okno (szerokosc: {width})")
        return False
    
    print(f"      Znaleziono zolte okno: {width}x{height}")
    
    # Play w zoltym oknie jest w srodku (~50% szerokosci, ~55% wysokosci)
    play_x = width // 2
    play_y = int(height * 0.55)
    
    window.click_input(coords=(play_x, play_y))
    print(f"      Play klikniete @ ({play_x}, {play_y})")
    return True


def click_play_in_news_window():
    """Klik Play w czarnym oknie (News)"""
    print("[3/4] Czekam na czarne okno (News)...")
    
    # Poczekaj na pojawienie sie czarnego okna
    time.sleep(2)
    
    window = find_window(["Shiginima"], exclude_patterns=["Update"], timeout=30)
    if not window:
        print("      Nie znaleziono czarnego okna!")
        return False
    
    rect = window.rectangle()
    width = rect.right - rect.left
    height = rect.bottom - rect.top
    
    print(f"      Znaleziono okno: {width}x{height}")
    
    # Play w czarnym oknie jest na dole (~50% szerokosci, ~88% wysokosci)
    play_x = width // 2
    play_y = int(height * 0.88)
    
    window.click_input(coords=(play_x, play_y))
    print(f"      Play klikniete @ ({play_x}, {play_y})")
    return True


def wait_for_minecraft(timeout=120):
    """Czeka na pojawienie sie okna Minecrafta"""
    print("[4/4] Czekam na uruchomienie Minecraft...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        desktop = Desktop(backend='win32')
        for window in desktop.windows():
            try:
                title = window.window_text()
                # Szukaj okna zawierajacego Minecraft/FML/Forge ale nie Shiginima
                if any(x in title for x in ["Minecraft 1.7.10", "FML", "Forge"]):
                    if "Shiginima" not in title and "Visual Studio" not in title:
                        print(f"      Wykryto okno: {title}")
                        return True
            except:
                pass
        
        # Sprawdz tez czy sa procesy Java (gra moze sie uruchamiac bez okna)
        import os
        java_processes = os.popen('tasklist /FI "IMAGENAME eq javaw.exe" 2>nul').read()
        if java_processes.count('javaw.exe') >= 2:
            print(f"      Wykryto procesy Java ({java_processes.count('javaw.exe')} instancji)")
            # Nie zwracaj od razu True - poczekaj na pelne uruchomienie
        
        time.sleep(1)
    
    print("      Timeout - gra moze sie uruchamiac w tle")
    return False


def kill_launcher():
    """Zabija procesy launchera i javaw"""
    import os
    os.system('taskkill /F /IM "Shiginima Launcher SE v3.100.exe" 2>nul')
    os.system('taskkill /F /IM javaw.exe 2>nul')
    time.sleep(1)


def launch_minecraft():
    """Glowna funkcja uruchamiajaca Minecraft"""
    print("="*60)
    print("AUTOMATYZACJA SHIGINIMA LAUNCHER")
    print("="*60)
    print()
    
    # Sprawdz czy launcher juz dziala
    existing = find_window(["Shiginima"], exclude_patterns=["Update"], timeout=2)
    if existing:
        print("Launcher juz uruchomiony, uzywam istniejacego...")
    else:
        print("Uruchamiam launcher...")
        try:
            subprocess.Popen([LAUNCHER_PATH], shell=True)
            time.sleep(2)
        except Exception as e:
            print(f"Blad uruchamiania: {e}")
            return False
    
    # Sekwencja klikniec
    click_update_dialog()
    click_play_in_sponge_window()
    click_play_in_news_window()
    wait_for_minecraft()
    
    print("\n" + "="*60)
    print("AUTOMATYZACJA ZAKONCZONA")
    print("="*60)
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--kill":
        kill_launcher()
        print("Procesy zabite")
    else:
        launch_minecraft()
