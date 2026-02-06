#!/usr/bin/env python3
from pywinauto import Desktop
import time

desktop = Desktop(backend='win32')

for window in desktop.windows():
    try:
        if 'Shiginima Launcher' in window.window_text():
            print(f'Okno: {window.window_text()}')
            window.set_focus()
            time.sleep(1)
            
            # Sprawdzam wszystkie dzieci (kontrolki)
            print('\n=== KONTROLKI W OKNIE ===')
            for child in window.children():
                try:
                    text = child.window_text()
                    class_name = child.class_name()
                    if text.strip():
                        print(f'  Tekst: "{text}" | Klasa: {class_name}')
                except:
                    pass
                    
            # Szukam przycisku Play
            print('\n=== SZUKAM PRZYCISKU PLAY ===')
            play_btn = window.child_window(title="Play", control_type="Button")
            if play_btn.exists():
                print(f'Znalazlem przycisk Play!')
                print(f'Rect: {play_btn.rectangle()}')
                play_btn.click()
                print('Kliknieto Play!')
            else:
                print('Nie znalazlem przycisku Play po nazwie')
                
    except Exception as e:
        print(f'Blad: {e}')
