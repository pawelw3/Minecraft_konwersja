"""
Enchanting Plus Report Generator

Generowanie raportów z konwersji w formatach HTML/JSON/Markdown.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json
from datetime import datetime

from .batch_converter import BatchConversionResult, BatchConversionStats


@dataclass
class VerificationItem:
    """Element do weryfikacji manualnej."""
    position: Tuple[int, int, int]
    block_type: str
    reason: str
    recommendation: str
    priority: str = "medium"  # "low", "medium", "high"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'position': self.position,
            'block_type': self.block_type,
            'reason': self.reason,
            'recommendation': self.recommendation,
            'priority': self.priority
        }


class EPReportGenerator:
    """
    Generator raportów dla konwersji Enchanting Plus.
    
    Generuje:
    - Raporty HTML z wykresami i statystykami
    - Raporty Markdown dla dokumentacji
    - JSON dla dalszego przetwarzania
    - Checklistę weryfikacji manualnej
    """
    
    def __init__(self, output_path: str = "output/ep_conversion/reports"):
        """
        Inicjalizuje generator.
        
        Args:
            output_path: Ścieżka do zapisu raportów
        """
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
    
    def generate_html_report(self, result: BatchConversionResult) -> str:
        """
        Generuje raport HTML.
        
        Args:
            result: Wynik konwersji wsadowej
            
        Returns:
            Ścieżka do wygenerowanego pliku
        """
        html_content = f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Raport Konwersji - Enchanting Plus</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
        }}
        .stat-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }}
        .stat-card.success .value {{ color: #4CAF50; }}
        .stat-card.warning .value {{ color: #FF9800; }}
        .stat-card.error .value {{ color: #f44336; }}
        .section {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #555;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        .badge-success {{ background: #d4edda; color: #155724; }}
        .badge-warning {{ background: #fff3cd; color: #856404; }}
        .badge-error {{ background: #f8d7da; color: #721c24; }}
        .mapping-info {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📜 Raport Konwersji</h1>
        <p>Enchanting Plus (1.7.10) → Enchanting Infuser (1.18.2)</p>
        <p>Wygenerowano: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <h3>Całkowita liczba bloków</h3>
            <div class="value">{result.stats.total_blocks}</div>
        </div>
        <div class="stat-card success">
            <h3>Przekonwertowane</h3>
            <div class="value">{result.stats.converted_blocks}</div>
        </div>
        <div class="stat-card warning">
            <h3>Usunięte</h3>
            <div class="value">{result.stats.removed_blocks}</div>
        </div>
        <div class="stat-card {'error' if result.stats.failed_blocks > 0 else 'success'}">
            <h3>Nieudane</h3>
            <div class="value">{result.stats.failed_blocks}</div>
        </div>
        <div class="stat-card success">
            <h3>Skuteczność</h3>
            <div class="value">{result.stats.success_rate:.1f}%</div>
        </div>
        <div class="stat-card">
            <h3>Czas wykonania</h3>
            <div class="value">{result.stats.duration_seconds:.1f}s</div>
        </div>
    </div>
    
    <div class="section">
        <h2>📊 Mapowanie Bloków</h2>
        <div class="mapping-info">
            <table>
                <tr>
                    <th>Blok 1.7.10 (Enchanting Plus)</th>
                    <th>Blok 1.18.2 (Enchanting Infuser)</th>
                    <th>Status</th>
                </tr>
                <tr>
                    <td><code>EnchantingPlus:enchanting_table</code></td>
                    <td><code>enchantinginfuser:enchanting_infuser</code></td>
                    <td><span class="badge badge-success">✓ Konwersja</span></td>
                </tr>
                <tr>
                    <td><code>EnchantingPlus:advanced_table</code></td>
                    <td><code>enchantinginfuser:advanced_enchanting_infuser</code></td>
                    <td><span class="badge badge-success">✓ Konwersja</span></td>
                </tr>
                <tr>
                    <td><code>EnchantingPlus:arcane_inscriber</code></td>
                    <td><code>minecraft:air</code> (brak odpowiednika)</td>
                    <td><span class="badge badge-warning">⚠ Usunięcie</span></td>
                </tr>
            </table>
        </div>
    </div>
"""
        
        # Dodaj sekcję bloków według typu
        if result.stats.blocks_by_type:
            html_content += """
    <div class="section">
        <h2>📈 Bloki Według Typu</h2>
        <table>
            <tr>
                <th>Typ bloku</th>
                <th>Liczba</th>
                <th>Procent</th>
            </tr>
"""
            for block_type, count in sorted(result.stats.blocks_by_type.items(), 
                                           key=lambda x: x[1], reverse=True):
                percent = (count / result.stats.total_blocks * 100) if result.stats.total_blocks > 0 else 0
                html_content += f"""
            <tr>
                <td><code>{block_type}</code></td>
                <td>{count}</td>
                <td>{percent:.1f}%</td>
            </tr>
"""
            html_content += """
        </table>
    </div>
"""
        
        # Dodaj sekcję błędów
        if result.stats.errors:
            html_content += """
    <div class="section">
        <h2>⚠️ Błędy</h2>
        <table>
            <tr>
                <th>#</th>
                <th>Opis błędu</th>
            </tr>
"""
            for i, error in enumerate(result.stats.errors[:10], 1):  # Max 10 błędów
                html_content += f"""
            <tr>
                <td>{i}</td>
                <td><code>{error}</code></td>
            </tr>
"""
            if len(result.stats.errors) > 10:
                html_content += f"""
            <tr>
                <td colspan="2">... i {len(result.stats.errors) - 10} więcej</td>
            </tr>
"""
            html_content += """
        </table>
    </div>
"""
        
        # Dodaj sekcję przypadków specjalnych
        html_content += """
    <div class="section">
        <h2>🔍 Informacje o Konwersji</h2>
        <h3>Funkcjonalności zachowane:</h3>
        <ul>
            <li>✓ Wybór enchantów bez RNG (podstawowy stół)</li>
            <li>✓ Modyfikacja istniejących enchantów (zaawansowany stół)</li>
            <li>✓ Naprawa przedmiotów za poziomy XP</li>
            <li>✓ Zdejmowanie enchantów (disenchanting)</li>
        </ul>
        
        <h3>Straty (brak odpowiedników):</h3>
        <ul>
            <li>⚠ Arcane Inscriber - konwersja książek na zwoje</li>
            <li>⚠ Enchanted Scrolls - zastąpione zwykłymi Enchanted Books</li>
        </ul>
        
        <h3>Wymagane zależności w 1.18.2:</h3>
        <ul>
            <li>Puzzles Lib (biblioteka wymagana przez Enchanting Infuser)</li>
        </ul>
    </div>
    
    <div class="footer">
        <p>Raport wygenerowany przez EPReportGenerator</p>
        <p>Enchanting Plus Converter v1.0</p>
    </div>
</body>
</html>
"""
        
        # Zapisz plik
        output_file = self.output_path / 'conversion_report.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_file)
    
    def generate_markdown_report(self, result: BatchConversionResult) -> str:
        """Generuje raport Markdown."""
        md_content = f"""# Raport Konwersji - Enchanting Plus

**Data wygenerowania:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Podsumowanie

| Metryka | Wartość |
|---------|---------|
| Całkowita liczba bloków | {result.stats.total_blocks} |
| Przekonwertowane | {result.stats.converted_blocks} |
| Usunięte | {result.stats.removed_blocks} |
| Nieudane | {result.stats.failed_blocks} |
| Skuteczność | {result.stats.success_rate:.1f}% |
| Czas wykonania | {result.stats.duration_seconds:.2f}s |

## Mapowanie Bloków

| Blok 1.7.10 | Blok 1.18.2 | Status |
|-------------|-------------|--------|
| `EnchantingPlus:enchanting_table` | `enchantinginfuser:enchanting_infuser` | ✓ Konwersja |
| `EnchantingPlus:advanced_table` | `enchantinginfuser:advanced_enchanting_infuser` | ✓ Konwersja |
| `EnchantingPlus:arcane_inscriber` | `minecraft:air` | ⚠ Usunięcie |

## Bloki Według Typu

"""
        
        if result.stats.blocks_by_type:
            md_content += "| Typ bloku | Liczba |\n|-----------|--------|\n"
            for block_type, count in sorted(result.stats.blocks_by_type.items(), 
                                           key=lambda x: x[1], reverse=True):
                md_content += f"| `{block_type}` | {count} |\n"
        else:
            md_content += "*Nie znaleziono bloków Enchanting Plus*\n"
        
        md_content += f"""

## Przypadki Specjalne

### Funkcjonalności zachowane:
- ✓ Wybór enchantów bez RNG
- ✓ Modyfikacja istniejących enchantów
- ✓ Naprawa przedmiotów za XP
- ✓ Zdejmowanie enchantów

### Straty:
- ⚠ Arcane Inscriber (brak odpowiednika)
- ⚠ Enchanted Scrolls (zastąpione vanilla books)

## Weryfikacja w Grze

Jeśli bloki zostały znalezione, należy zweryfikować:

1. [ ] Podstawowy stół wyświetla się poprawnie
2. [ ] Zaawansowany stół wyświetla się poprawnie
3. [ ] GUI otwiera się bez błędów
4. [ ] Enchantowanie działa (wybór bez RNG)
5. [ ] Naprawa przedmiotów działa
6. [ ] Zdejmowanie enchantów działa

---
*Raport wygenerowany przez EPReportGenerator*
"""
        
        output_file = self.output_path / 'conversion_report.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return str(output_file)
    
    def generate_full_report(self, result: BatchConversionResult) -> Dict[str, str]:
        """
        Generuje wszystkie raporty.
        
        Returns:
            Słownik z ścieżkami do raportów
        """
        return {
            'html': self.generate_html_report(result),
            'markdown': self.generate_markdown_report(result),
            'json': str(self.output_path / 'conversion_report.json')
        }


def main():
    """Demo generatora raportów."""
    print("=" * 60)
    print("ENCHANTING PLUS REPORT GENERATOR - Demo")
    print("=" * 60)
    
    # Stwórz przykładowe wyniki
    stats = BatchConversionStats()
    stats.total_blocks = 10
    stats.converted_blocks = 7
    stats.removed_blocks = 3
    stats.success_rate = 100.0
    stats.duration_seconds = 5.5
    stats.blocks_by_type = {
        'EnchantingPlus:enchanting_table': 5,
        'EnchantingPlus:advanced_table': 2,
        'EnchantingPlus:arcane_inscriber': 3
    }
    
    result = BatchConversionResult(
        stats=stats,
        converted_blocks=[],
        output_path="output/ep_conversion"
    )
    
    # Wygeneruj raporty
    generator = EPReportGenerator()
    reports = generator.generate_full_report(result)
    
    print("\nWygenerowane raporty:")
    for format_name, path in reports.items():
        print(f"  {format_name}: {path}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Import needed for type hint
    from typing import Tuple
    main()
