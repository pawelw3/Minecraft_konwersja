#!/usr/bin/env python3
"""
Skrypt analizujący okna Shiginima Launchera
"""

from pywinauto import Desktop, Application
import time

def analyze_all_windows():
    """Analizuje wszystkie okna Shiginima Launchera"""
    
    desktop = Desktop(backend='win32')
    
    print("="*60)
    print("ANALIZA OKIEN SHIGINIMA LAUNCHERA")
    print("="*60)
    print("\nOczekiwanie na okno... Uruchom launcher i obserwuj output.\n")
    print("(Naciśnij Ctrl+C aby zakończyć)\n")
    
    seen_windows = {}
    
    try:
        while True:
            for window in desktop.windows():
                try:
                    title = window.window_text()
                    if 'Shiginima' in title:
                        rect = window.rectangle()
                        width = rect.right - rect.left
                        height = rect.bottom - rect.top
                        
                        # Unikalny identyfikator okna
                        window_id = f"{title}_{width}x{height}"
                        
                        if window_id not in seen_windows:
                            seen_windows[window_id] = True
                            
                            print("\n" + "="*60)
                            print(f"NOWE OKNO: {title}")
                            print(f"Rozmiar: {width}x{height}")
                            print(f"Pozycja: ({rect.left}, {rect.top})")
                            print("="*60)
                            
                            # Próba wylistowania kontrolek
                            print("\nKontrolki (children):")
                            try:
                                for child in window.children():
                                    try:
                                        child_title = child.window_text()
                                        child_class = child.class_name()
                                        child_rect = child.rectangle()
                                        print(f"  - '{child_title}' (class: {child_class})")
                                        print(f"    Pozycja: ({child_rect.left}, {child_rect.top})")
                                    except:
                                        pass
                            except Exception as e:
                                print(f"  Błąd: {e}")
                            
                            # Próba zrzutu ekranu dla analizy koloru
                            print("\nAby zidentyfikować okno:")
                            if height > 500:
                                print("  [PRAWDOPODOBNIE ŻÓŁTE OKNO - Sponge Edition]")
                                print(f"  Sugerowane coords dla Play: (~{width//2}, ~{int(height*0.4)})")
                            else:
                                print("  [PRAWDOPODOBNIE CZARNE OKNO - News]")
                                print(f"  Sugerowane coords dla Play: (~{width//2}, ~{int(height*0.8)})")
                
                except Exception as e:
                    pass
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\nZakończono.")


def click_play_smart():
    """
    Inteligentne klikanie Play - rozróżnia okna po rozmiarze
    """
    desktop = Desktop(backend='win32')
    
    for window in desktop.windows():
        try:
            title = window.window_text()
            if 'Shiginima' in title and 'Update' not in title:
                rect = window.rectangle()
                width = rect.right - rect.left
                height = rect.bottom - rect.top
                
                print(f"Znaleziono okno: {title} ({width}x{height})")
                
                # Kliknij w środek okna, ale w odpowiedniej wysokości
                center_x = rect.left + width // 2
                
                if height > 500:
                    # Żółte okno - Play jest wyżej (około 40% wysokości)
                    click_y = rect.top + int(height * 0.45)
                    print(f"  -> ŻÓŁTE OKNO, klikam w ({center_x}, {click_y})")
                else:
                    # Czarne okno - Play jest niżej (około 80% wysokości)
                    click_y = rect.top + int(height * 0.80)
                    print(f"  -> CZARNE OKNO, klikam w ({center_x}, {click_y})")
                
                window.click_input(coords=(center_x - rect.left, click_y - rect.top))
                return True
                
        except Exception as e:
            pass
    
    return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--click":
        print("Klikam Play w wykrytym oknie...")
        click_play_smart()
    else:
        analyze_all_windows()
