#!/usr/bin/env python3
from pywinauto import Desktop
import time

# Używam backendu uia (lepszy dla WPF/JavaFX)
desktop = Desktop(backend='uia')

for window in desktop.windows():
    try:
        title = window.window_text()
        if 'Shiginima' in title or 'Sponge' in title:
            print(f'Okno: {title}')
            window.set_focus()
            time.sleep(1)
            
            # Sprawdzam wszystkie dzieci
            print('\n=== KONTROLKI ===')
            for child in window.children():
                try:
                    text = child.window_text()
                    ctrl_type = child.element_info.control_type
                    if text.strip():
                        print(f'  "{text}" | Typ: {ctrl_type}')
                except:
                    pass
                    
            # Szukam Play
            print('\n=== SZUKAM PLAY ===')
            for child in window.children():
                try:
                    text = child.window_text()
                    if 'play' in text.lower():
                        print(f'Znalazlem: "{text}"')
                        child.click()
                        print('Kliknieto!')
                        break
                except:
                    pass
                    
    except Exception as e:
        print(f'Blad: {e}')
