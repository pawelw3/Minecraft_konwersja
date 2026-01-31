"""
Generator wizualizacji krok po kroku działania cyfrowego licznika.
Tworzy SVG pokazujące stany układu dla cyfr 0-9.
"""

import os

# Definicja stanów dla cyfr 0-9 (Q3 Q2 Q1 Q0 - od MSB do LSB)
DIGIT_STATES = {
    0: {"bits": [0, 0, 0, 0], "active_line": 0},
    1: {"bits": [0, 0, 0, 1], "active_line": 1},
    2: {"bits": [0, 0, 1, 0], "active_line": 2},
    3: {"bits": [0, 0, 1, 1], "active_line": 3},
    4: {"bits": [0, 1, 0, 0], "active_line": 4},
    5: {"bits": [0, 1, 0, 1], "active_line": 5},
    6: {"bits": [0, 1, 1, 0], "active_line": 6},
    7: {"bits": [0, 1, 1, 1], "active_line": 7},
    8: {"bits": [1, 0, 0, 0], "active_line": 8},
    9: {"bits": [1, 0, 0, 1], "active_line": 9},
}

# Kolory
COLOR_OFF = "#3a3a3a"      # Ciemny szary - wyłączony
COLOR_ON = "#ff3333"       # Czerwony - włączony (redstone)
COLOR_ACTIVE = "#00ff00"   # Zielony - aktywny wyjście
COLOR_TEXT = "#ffffff"     # Biały tekst
COLOR_BG = "#1a1a2e"       # Ciemne tło
COLOR_GRID = "#2d2d44"     # Kolor siatki
COLOR_COMPONENT = "#4a4a6a" # Kolor komponentów
COLOR_HIGHLIGHT = "#ffff00" # Żółty - podświetlenie


def generate_svg(digit, show_clock_pulse=False, output_dir="digital_counter_frames"):
    """Generuje SVG dla danego stanu cyfry."""
    
    state = DIGIT_STATES[digit]
    bits = state["bits"]
    active_line = state["active_line"]
    
    width = 1000
    height = 700
    
    svg_parts = []
    
    # Nagłówek SVG
    svg_parts.append(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
<defs>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
        <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
        </feMerge>
    </filter>
</defs>

<!-- Tło -->
<rect width="{width}" height="{height}" fill="{COLOR_BG}"/>

<!-- Tytuł -->
<text x="{width//2}" y="40" text-anchor="middle" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="28" font-weight="bold">
    CYFROWY LICZNIK 4-BITOWY - STAN: {digit}
</text>
''')

    # === SEKCJA 1: ZEGAR ===
    clock_x, clock_y = 80, 100
    svg_parts.append(f'''
<!-- Sekcja Zegar -->
<rect x="{clock_x-20}" y="{clock_y-20}" width="140" height="100" fill="{COLOR_GRID}" rx="10"/>
<text x="{clock_x+50}" y="{clock_y}" text-anchor="middle" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="14" font-weight="bold">ZEGAR 1Hz</text>
''')
    
    # LED zegara
    clock_color = COLOR_ON if show_clock_pulse else COLOR_OFF
    clock_glow = 'filter="url(#glow)"' if show_clock_pulse else ''
    svg_parts.append(f'''
<circle cx="{clock_x+50}" cy="{clock_y+40}" r="25" fill="{clock_color}" {clock_glow}/>
<text x="{clock_x+50}" y="{clock_y+85}" text-anchor="middle" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="12">{"PULS!" if show_clock_pulse else "oczekuje"}</text>
''')

    # === SEKCJA 2: LICZNIK 4-BIT ===
    counter_x, counter_y = 280, 100
    svg_parts.append(f'''
<!-- Sekcja Licznik -->
<rect x="{counter_x-20}" y="{counter_y-20}" width="320" height="140" fill="{COLOR_GRID}" rx="10"/>
<text x="{counter_x+140}" y="{counter_y}" text-anchor="middle" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="14" font-weight="bold">LICZNIK 4-BIT (T FLIP-FLOPs)</text>
''')
    
    # Rysuj 4 bity
    bit_names = ["Q0 (LSB)", "Q1", "Q2", "Q3 (MSB)"]
    bit_x = counter_x + 30
    
    for i, (bit_val, bit_name) in enumerate(zip(reversed(bits), bit_names)):
        bx = bit_x + i * 70
        by = counter_y + 50
        bit_color = COLOR_ON if bit_val else COLOR_OFF
        bit_glow = 'filter="url(#glow)"' if bit_val else ''
        
        svg_parts.append(f'''
<rect x="{bx-25}" y="{by-30}" width="50" height="80" fill="{COLOR_COMPONENT}" rx="5"/>
<text x="{bx}" y="{by-35}" text-anchor="middle" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="11">{bit_name}</text>
<circle cx="{bx}" cy="{by}" r="20" fill="{bit_color}" {bit_glow}/>
<text x="{bx}" y="{by+5}" text-anchor="middle" fill="{COLOR_TEXT if bit_val else '#888'}" font-family="Consolas, monospace" font-size="20" font-weight="bold">{bit_val}</text>
<text x="{bx}" y="{by+45}" text-anchor="middle" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="10">{"AKTYWNY" if bit_val else "OFF"}</text>
''')

    # Połączenie zegar -> licznik
    svg_parts.append(f'''
<!-- Linia zegar -> licznik -->
<line x1="{clock_x+100}" y1="{clock_y+40}" x2="{counter_x-20}" y2="{counter_y+50}" stroke="{COLOR_ON if show_clock_pulse else COLOR_OFF}" stroke-width="3" {'filter="url(#glow)"' if show_clock_pulse else ''}/>
''')

    # === SEKCJA 3: WARTOŚĆ BINARNA ===
    bin_value = ''.join(map(str, bits))
    svg_parts.append(f'''
<!-- Wartość binarna -->
<rect x="{counter_x+80}" y="{counter_y+100}" width="120" height="30" fill="{COLOR_HIGHLIGHT if digit > 0 else COLOR_COMPONENT}" rx="5"/>
<text x="{counter_x+140}" y="{counter_y+120}" text-anchor="middle" fill="#000" font-family="Consolas, monospace" font-size="16" font-weight="bold">BIN: {bin_value}</text>
''')

    # === SEKCJA 4: DEKODER BCD ===
    decoder_x, decoder_y = 80, 280
    svg_parts.append(f'''
<!-- Sekcja Dekoder BCD -->
<rect x="{decoder_x-20}" y="{decoder_y-20}" width="520" height="380" fill="{COLOR_GRID}" rx="10"/>
<text x="{decoder_x+240}" y="{decoder_y}" text-anchor="middle" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="14" font-weight="bold">DEKODER BCD (4→10)</text>
<text x="{decoder_x+240}" y="{decoder_y+18}" text-anchor="middle" fill="#aaa" font-family="Consolas, monospace" font-size="10">Sprawdza stany bitów i aktywuje odpowiednią linię</text>
''')
    
    # Linie wejściowe do dekodera (z licznika)
    for i in range(4):
        line_y = decoder_y + 50 + i * 40
        bit_val = bits[3-i]  # Odwrócona kolejność
        line_color = COLOR_ON if bit_val else COLOR_OFF
        
        svg_parts.append(f'''
<line x1="{counter_x+300}" y1="{counter_y+50+i*70}" x2="{decoder_x+50}" y2="{line_y}" stroke="{line_color}" stroke-width="2"/>
<circle cx="{decoder_x+50}" cy="{line_y}" r="8" fill="{line_color}"/>
<text x="{decoder_x+35}" y="{line_y+4}" text-anchor="end" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="10">Q{3-i}={bit_val}</text>
''')

    # Bramki AND dla cyfr 0-9
    gate_x = decoder_x + 150
    gate_y_start = decoder_y + 40
    
    svg_parts.append(f'''
<text x="{gate_x}" y="{decoder_y+30}" text-anchor="middle" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="11">BRAMKI AND</text>
''')

    for d in range(10):
        gy = gate_y_start + d * 34
        is_active = (d == active_line)
        gate_color = COLOR_ACTIVE if is_active else COLOR_COMPONENT
        gate_border = COLOR_HIGHLIGHT if is_active else COLOR_OFF
        gate_width = 80 if is_active else 60
        
        # Warunek dla cyfry d (jakie bity muszą być 1)
        d_bits = [int(b) for b in format(d, '04b')]
        required = []
        for i, b in enumerate(d_bits):
            if b == 1:
                required.append(f"Q{3-i}")
        condition = " AND ".join(required) if required else "¬Q3∧¬Q2∧¬Q1∧¬Q0"
        
        svg_parts.append(f'''
<rect x="{gate_x-gate_width//2}" y="{gy-12}" width="{gate_width}" height="24" fill="{gate_color}" stroke="{gate_border}" stroke-width="{3 if is_active else 1}" rx="4"/>
<text x="{gate_x}" y="{gy+4}" text-anchor="middle" fill="{'#000' if is_active else COLOR_TEXT}" font-family="Consolas, monospace" font-size="{13 if is_active else 11}" font-weight="{'bold' if is_active else 'normal'}">[{d}] {condition}</text>
''')

    # === SEKCJA 5: LINIE WYJŚCIOWE ===
    output_x = decoder_x + 350
    svg_parts.append(f'''
<text x="{output_x+50}" y="{decoder_y+30}" text-anchor="middle" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="11">LINIE WYJŚCIOWE</text>
''')
    
    for d in range(10):
        ly = gate_y_start + d * 34
        is_active = (d == active_line)
        line_color = COLOR_ACTIVE if is_active else COLOR_OFF
        line_width = 5 if is_active else 2
        
        # Połączenie z bramki
        svg_parts.append(f'''
<line x1="{gate_x+40}" y1="{ly}" x2="{output_x}" y2="{ly}" stroke="{line_color}" stroke-width="{line_width}" {'filter="url(#glow)"' if is_active else ''}/>
<circle cx="{output_x+10}" cy="{ly}" r="{10 if is_active else 6}" fill="{line_color}" {'filter="url(#glow)"' if is_active else ''}/>
<text x="{output_x+30}" y="{ly+4}" fill="{COLOR_ACTIVE if is_active else '#666'}" font-family="Consolas, monospace" font-size="{14 if is_active else 11}" font-weight="{'bold' if is_active else 'normal'}">DIGIT {d}</text>
''')

    # === SEKCJA 6: COMMAND BLOCKI ===
    cmd_x, cmd_y = 750, 280
    svg_parts.append(f'''
<!-- Sekcja Command Blocks -->
<rect x="{cmd_x-20}" y="{cmd_y-20}" width="220" height="380" fill="{COLOR_GRID}" rx="10"/>
<text x="{cmd_x+90}" y="{cmd_y}" text-anchor="middle" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="14" font-weight="bold">COMMAND BLOCKS</text>
<text x="{cmd_x+90}" y="{cmd_y+18}" text-anchor="middle" fill="#aaa" font-family="Consolas, monospace" font-size="10">/say X → log na czacie</text>
''')
    
    for d in range(10):
        cy = cmd_y + 40 + d * 34
        is_active = (d == active_line)
        cmd_color = COLOR_ACTIVE if is_active else COLOR_COMPONENT
        cmd_border = COLOR_HIGHLIGHT if is_active else COLOR_OFF
        
        svg_parts.append(f'''
<rect x="{cmd_x}" y="{cy-12}" width="180" height="26" fill="{cmd_color}" stroke="{cmd_border}" stroke-width="{3 if is_active else 1}" rx="3"/>
<text x="{cmd_x+90}" y="{cy+5}" text-anchor="middle" fill="{'#000' if is_active else COLOR_TEXT}" font-family="Consolas, monospace" font-size="{12 if is_active else 10}" font-weight="{'bold' if is_active else 'normal'}">/say {d}</text>
<text x="{cmd_x+165}" y="{cy+5}" fill="{'#000' if is_active else '#888'}" font-family="Consolas, monospace" font-size="10">{"<< AKCJA!" if is_active else ""}</text>
''')
        
        # Połączenie z dekodera
        line_y = gate_y_start + d * 34
        svg_parts.append(f'''
<line x1="{output_x+70}" y1="{line_y}" x2="{cmd_x}" y2="{cy}" stroke="{COLOR_ACTIVE if is_active else COLOR_OFF}" stroke-width="{3 if is_active else 1}" {'filter="url(#glow)"' if is_active else ''}/>
''')

    # === PODSUMOWANIE ===
    summary_y = 620
    svg_parts.append(f'''
<!-- Podsumowanie -->
<rect x="50" y="{summary_y-30}" width="900" height="60" fill="{COLOR_GRID}" rx="10"/>
<text x="500" y="{summary_y}" text-anchor="middle" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="16" font-weight="bold">
    WYŚWIETLANA CYFRA: {digit}
</text>
<text x="500" y="{summary_y+22}" text-anchor="middle" fill="{COLOR_HIGHLIGHT}" font-family="Consolas, monospace" font-size="14">
    Stan licznika: {bin_value} (bin) = {digit} (dec)
</text>
''')

    # Stopka
    svg_parts.append(f'''
<text x="500" y="690" text-anchor="middle" fill="#666" font-family="Consolas, monospace" font-size="10">
    Scenariusz Testowy: digital_counter_vanilla | Klatka: digit_{digit}_{'pulse' if show_clock_pulse else 'hold'}
</text>

</svg>''')
    
    return '\n'.join(svg_parts)


def generate_transition_frame(from_digit, to_digit, output_dir="digital_counter_frames"):
    """Generuje klatkę przejścia między cyframi."""
    
    from_state = DIGIT_STATES[from_digit]
    to_state = DIGIT_STATES[to_digit]
    
    width = 1000
    height = 700
    
    svg_parts = [f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
<rect width="{width}" height="{height}" fill="{COLOR_BG}"/>
<text x="{width//2}" y="40" text-anchor="middle" fill="{COLOR_HIGHLIGHT}" font-family="Consolas, monospace" font-size="28" font-weight="bold">
    PRZEJŚCIE: {from_digit} → {to_digit}
</text>
''']

    # Tabela zmian
    table_x, table_y = 200, 150
    svg_parts.append(f'''
<rect x="{table_x-20}" y="{table_y-40}" width="600" height="400" fill="{COLOR_GRID}" rx="10"/>
<text x="{table_x+280}" y="{table_y-10}" text-anchor="middle" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="16" font-weight="bold">ZMiana STANÓW</text>
''')

    # Nagłówki
    headers = ["Bit", f"Przed ({from_digit})", f"Po ({to_digit})", "Zmiana?"]
    for i, h in enumerate(headers):
        svg_parts.append(f'<text x="{table_x+i*150}" y="{table_y+30}" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="12" font-weight="bold">{h}</text>')

    # Wiersze dla bitów
    bit_names = ["Q3 (MSB)", "Q2", "Q1", "Q0 (LSB)"]
    for i, bit_name in enumerate(bit_names):
        fy = table_y + 60 + i * 50
        from_val = from_state["bits"][i]
        to_val = to_state["bits"][i]
        changed = from_val != to_val
        
        change_text = "ZMIANA! →" if changed else "-"
        change_color = COLOR_HIGHLIGHT if changed else "#666"
        
        svg_parts.append(f'''
<text x="{table_x}" y="{fy}" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="14">{bit_name}</text>
<text x="{table_x+150}" y="{fy}" fill="{COLOR_ON if from_val else '#666'}" font-family="Consolas, monospace" font-size="20" font-weight="bold">{from_val}</text>
<text x="{table_x+300}" y="{fy}" fill="{COLOR_ON if to_val else '#666'}" font-family="Consolas, monospace" font-size="20" font-weight="bold">{to_val}</text>
<text x="{table_x+450}" y="{fy}" fill="{change_color}" font-family="Consolas, monospace" font-size="14" font-weight="bold">{change_text}</text>
''')

    # Wyjaśnienie
    explain_y = table_y + 300
    toggled = [i for i in range(4) if from_state["bits"][i] != to_state["bits"][i]]
    toggled_names = [f"Q{3-i}" for i in toggled]
    
    svg_parts.append(f'''
<text x="{table_x+280}" y="{explain_y}" text-anchor="middle" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="14">
    Przełączone bity: {', '.join(toggled_names) if toggled_names else 'brak'}
</text>
<text x="{table_x+280}" y="{explain_y+30}" text-anchor="middle" fill="{COLOR_HIGHLIGHT}" font-family="Consolas, monospace" font-size="16" font-weight="bold">
    Następny impuls zegara spowoduje przejście do cyfry {to_digit}
</text>
</svg>''')
    
    return '\n'.join(svg_parts)


def main():
    """Generuje wszystkie pliki SVG."""
    
    output_dir = "digital_counter_frames"
    os.makedirs(output_dir, exist_ok=True)
    
    print("Generowanie wizualizacji cyfrowego licznika...")
    print("=" * 50)
    
    # Generuj stany dla cyfr 0-9 (z pulsem zegara)
    for digit in range(10):
        # Stan trzymania (bez pulsu)
        svg_content = generate_svg(digit, show_clock_pulse=False)
        filename = f"{output_dir}/digit_{digit}_hold.svg"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        print(f"[OK] Wygenerowano: {filename}")
        
        # Stan z impulsem (aktywacja)
        svg_content = generate_svg(digit, show_clock_pulse=True)
        filename = f"{output_dir}/digit_{digit}_pulse.svg"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        print(f"[OK] Wygenerowano: {filename}")
    
    # Generuj klatki przejść
    for i in range(10):
        next_i = (i + 1) % 10
        svg_content = generate_transition_frame(i, next_i)
        filename = f"{output_dir}/transition_{i}_to_{next_i}.svg"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        print(f"[OK] Wygenerowano: {filename}")
    
    # Generuj podsumowanie cyklu
    generate_cycle_summary(output_dir)
    
    print("=" * 50)
    print(f"Gotowe! Wygenerowano {10*2 + 10 + 1} plików SVG w folderze '{output_dir}/'")


def generate_cycle_summary(output_dir):
    """Generuje podsumowanie pełnego cyklu."""
    
    width = 1200
    height = 800
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
<rect width="{width}" height="{height}" fill="{COLOR_BG}"/>

<text x="{width//2}" y="50" text-anchor="middle" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="28" font-weight="bold">
    PEŁNY CYKL LICZNIKA 0-9 (10 sekund)
</text>

<!-- Oś czasu -->
<line x1="100" y1="150" x2="1100" y2="150" stroke="{COLOR_TEXT}" stroke-width="3"/>
<text x="100" y="130" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="14">t=0s</text>
<text x="1100" y="130" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="14">t=10s</text>

<!-- Cyfry na osi czasu -->
'''
    
    for i in range(10):
        x = 150 + i * 100
        
        # Stan binarny
        bits = format(i, '04b')
        
        svg_content += f'''
<line x1="{x}" y1="140" x2="{x}" y2="160" stroke="{COLOR_ON}" stroke-width="2"/>
<circle cx="{x}" cy="{200}" r="30" fill="{COLOR_COMPONENT}" stroke="{COLOR_ON}" stroke-width="2"/>
<text x="{x}" y="{208}" text-anchor="middle" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="28" font-weight="bold">{i}</text>
<text x="{x}" y="{250}" text-anchor="middle" fill="#aaa" font-family="Consolas, monospace" font-size="11">{bits}</text>
<text x="{x}" y="{270}" text-anchor="middle" fill="{COLOR_ON}" font-family="Consolas, monospace" font-size="10">/say {i}</text>
'''
    
    # Diagram przepływu
    svg_content += f'''
<rect x="100" y="320" width="1000" height="400" fill="{COLOR_GRID}" rx="10"/>
<text x="600" y="350" text-anchor="middle" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="16" font-weight="bold">SCHEMAT BLOKOWY UKŁADU</text>

<!-- Bloki -->
<rect x="150" y="400" width="120" height="80" fill="{COLOR_COMPONENT}" rx="10"/>
<text x="210" y="445" text-anchor="middle" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="14" font-weight="bold">ZEGAR</text>
<text x="210" y="465" text-anchor="middle" fill="#aaa" font-family="Consolas, monospace" font-size="10">1Hz (20 ticków)</text>

<rect x="350" y="400" width="140" height="80" fill="{COLOR_COMPONENT}" rx="10"/>
<text x="420" y="445" text-anchor="middle" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="14" font-weight="bold">LICZNIK</text>
<text x="420" y="465" text-anchor="middle" fill="#aaa" font-family="Consolas, monospace" font-size="10">4-bit (0-15)</text>

<rect x="570" y="400" width="140" height="80" fill="{COLOR_COMPONENT}" rx="10"/>
<text x="640" y="445" text-anchor="middle" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="14" font-weight="bold">DEKODER</text>
<text x="640" y="465" text-anchor="middle" fill="#aaa" font-family="Consolas, monospace" font-size="10">BCD → 10 linii</text>

<rect x="790" y="380" width="280" height="200" fill="{COLOR_COMPONENT}" rx="10"/>
<text x="930" y="410" text-anchor="middle" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="14" font-weight="bold">COMMAND BLOCKS</text>
'''
    
    # Command blocks inside
    for i in range(10):
        cx = 830 + (i % 5) * 50
        cy = 440 + (i // 5) * 60
        svg_content += f'''
<rect x="{cx-15}" y="{cy-15}" width="30" height="30" fill="{COLOR_GRID}" rx="3"/>
<text x="{cx}" y="{cy+5}" text-anchor="middle" fill="{COLOR_TEXT}" font-family="Consolas, monospace" font-size="10">{i}</text>
'''
    
    # Strzałki połączeń
    svg_content += f'''
<line x1="270" y1="440" x2="350" y2="440" stroke="{COLOR_ON}" stroke-width="3" marker-end="url(#arrow)"/>
<line x1="490" y1="440" x2="570" y2="440" stroke="{COLOR_ON}" stroke-width="3" marker-end="url(#arrow)"/>
<line x1="710" y1="440" x2="790" y2="440" stroke="{COLOR_ON}" stroke-width="3" marker-end="url(#arrow)"/>

<defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
        <path d="M0,0 L0,6 L9,3 z" fill="{COLOR_ON}"/>
    </marker>
</defs>

<text x="600" y="650" text-anchor="middle" fill="{COLOR_HIGHLIGHT}" font-family="Consolas, monospace" font-size="16" font-weight="bold">
    Cykl powtarza się co 10 sekund → 0,1,2,3,4,5,6,7,8,9,0,1,2...
</text>

<text x="600" y="750" text-anchor="middle" fill="#666" font-family="Consolas, monospace" font-size="12">
    Scenariusz testowy: digital_counter_vanilla | Wizualizacja pełnego cyklu
</text>

</svg>'''
    
    filename = f"{output_dir}/00_CYCLE_SUMMARY.svg"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"[OK] Wygenerowano: {filename}")


if __name__ == "__main__":
    main()
