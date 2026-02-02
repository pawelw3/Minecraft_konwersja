"""
Report Generator dla BiblioCraft - generowanie szczegółowych raportów

Tworzy:
1. Raport podsumowujący konwersję (HTML/Markdown)
2. Listę utraconych danych
3. Listę bloków do weryfikacji manualnej
4. Statystyki per typ bloku
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import json

from .batch_converter import ConversionResult, BatchConversionStats


@dataclass
class LostDataInfo:
    """Informacja o utraconych danych"""
    position: Tuple[int, int, int]
    block_type: str
    data_type: str
    description: str
    severity: str = "warning"  # warning, info, critical


@dataclass
class VerificationItem:
    """Element do weryfikacji manualnej"""
    position: Tuple[int, int, int]
    block_type: str
    reason: str
    recommendation: str
    priority: str = "medium"  # low, medium, high


class BiblioCraftReportGenerator:
    """
    Generator raportów dla konwersji BiblioCraft
    
    Tworzy czytelne raporty podsumowujące proces konwersji.
    """
    
    def __init__(self, output_path: str):
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        self.lost_data: List[LostDataInfo] = []
        self.verification_items: List[VerificationItem] = []
    
    def generate_full_report(self, 
                            results: List[ConversionResult],
                            stats: BatchConversionStats,
                            format: str = "html") -> str:
        """
        Generuje pełny raport konwersji
        
        Args:
            results: Lista wyników konwersji
            stats: Statystyki
            format: Format raportu (html, markdown, json)
            
        Returns:
            Ścieżka do wygenerowanego raportu
        """
        # Analizuj wyniki
        self._analyze_results(results)
        
        if format == "html":
            return self._generate_html_report(results, stats)
        elif format == "markdown":
            return self._generate_markdown_report(results, stats)
        elif format == "json":
            return self._generate_json_report(results, stats)
        else:
            raise ValueError(f"Nieznany format: {format}")
    
    def _analyze_results(self, results: List[ConversionResult]):
        """Analizuje wyniki w poszukiwaniu problemów"""
        self.lost_data = []
        self.verification_items = []
        
        for result in results:
            if not result.success:
                # Blok nie został przekonwertowany
                self.verification_items.append(VerificationItem(
                    position=result.position,
                    block_type=result.original_block.block_id,
                    reason=result.error_message or "Nieznany błąd",
                    recommendation="Sprawdź ręcznie i zastąp odpowiednim blokiem",
                    priority="high"
                ))
                continue
            
            # Sprawdź ostrzeżenia
            for warning in result.warnings:
                self._process_warning(result, warning)
            
            # Sprawdź specyficzne typy bloków
            self._check_block_specific_issues(result)
    
    def _process_warning(self, result: ConversionResult, warning: str):
        """Przetwarza ostrzeżenie i dodaje do odpowiedniej kategorii"""
        warning_lower = warning.lower()
        
        # Strata danych inventory
        if "książek" in warning_lower and "nie zmieściło" in warning_lower:
            # Ekstrahuj liczbę
            import re
            match = re.search(r'(\d+) książek', warning)
            if match:
                lost_count = int(match.group(1))
                self.lost_data.append(LostDataInfo(
                    position=result.position,
                    block_type=result.original_block.block_id,
                    data_type="inventory",
                    description=f"Utracono {lost_count} książek z Bookcase (przekonwertowano tylko 4 pierwsze)",
                    severity="warning"
                ))
        
        # Nieznana tekstura
        if "nieznana tekstura" in warning_lower:
            self.verification_items.append(VerificationItem(
                position=result.position,
                block_type=result.original_block.block_id,
                reason="Nieznana tekstura - użyto domyślnej (oak_planks)",
                recommendation="Sprawdź wygląd i ewentualnie zmień teksturę",
                priority="medium"
            ))
    
    def _check_block_specific_issues(self, result: ConversionResult):
        """Sprawdza problemy specyficzne dla typów bloków"""
        block_id = result.original_block.block_id
        te_data = result.original_block.tile_entity or {}
        
        # Painting - brak obrazu
        if "Painting" in block_id:
            resource_loc = te_data.get("resourceLocation", "")
            if not resource_loc:
                self.verification_items.append(VerificationItem(
                    position=result.position,
                    block_type=block_id,
                    reason="Brak ścieżki do obrazu",
                    recommendation="Sprawdź czy obraz jest widoczny, jeśli nie - usuń lub zastąp",
                    priority="medium"
                ))
        
        # Framed blocks - customowa tekstura
        if "Framed" in block_id:
            frame_texture = te_data.get("frameTexture", "")
            if frame_texture and "minecraft:" not in frame_texture:
                # Tekstura z modu
                self.verification_items.append(VerificationItem(
                    position=result.position,
                    block_type=block_id,
                    reason=f"Tekstura z modu: {frame_texture}",
                    recommendation="Sprawdź czy tekstura jest poprawnie wyświetlana",
                    priority="low"
                ))
        
        # Armor Stand - sprawdź zbroję
        if "ArmorStand" in block_id:
            armor_items = te_data.get("armorItems", [])
            if armor_items and any(armor_items):
                self.verification_items.append(VerificationItem(
                    position=result.position,
                    block_type=block_id,
                    reason="Armor Stand z zawartością - konwertowano na vanilla",
                    recommendation="Sprawdź czy zbroja jest poprawnie wyświetlana",
                    priority="medium"
                ))
    
    def _generate_html_report(self, results: List[ConversionResult], 
                              stats: BatchConversionStats) -> str:
        """Generuje raport HTML"""
        output_file = self.output_path / "conversion_report.html"
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Raport Konwersji BiblioCraft</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat-card {{ background: #f9f9f9; padding: 15px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 2em; font-weight: bold; color: #4CAF50; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .success {{ color: #4CAF50; }}
        .warning {{ color: #FF9800; }}
        .error {{ color: #F44336; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #4CAF50; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        .priority-high {{ background: #ffebee; }}
        .priority-medium {{ background: #fff3e0; }}
        .priority-low {{ background: #f1f8e9; }}
        .timestamp {{ color: #999; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Raport Konwersji BiblioCraft</h1>
        <p class="timestamp">Wygenerowano: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Statystyki</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{stats.total_bc_blocks}</div>
                <div class="stat-label">Znalezionych bloków</div>
            </div>
            <div class="stat-card">
                <div class="stat-value success">{stats.converted_blocks}</div>
                <div class="stat-label">Przekonwertowanych</div>
            </div>
            <div class="stat-card">
                <div class="stat-value error">{stats.failed_blocks}</div>
                <div class="stat-label">Nieudanych</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats.success_rate:.1f}%</div>
                <div class="stat-label">Skuteczność</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats.duration_seconds:.1f}s</div>
                <div class="stat-label">Czas konwersji</div>
            </div>
        </div>
"""
        
        # Dodaj sekcję utraconych danych
        if self.lost_data:
            html += self._generate_lost_data_section_html()
        
        # Dodaj sekcję weryfikacji
        if self.verification_items:
            html += self._generate_verification_section_html()
        
        # Dodaj podsumowanie typów bloków
        html += self._generate_block_types_section_html(results)
        
        html += """
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(output_file)
    
    def _generate_lost_data_section_html(self) -> str:
        """Generuje sekcję utraconych danych w HTML"""
        html = "\n        <h2>Utracone Dane</h2>\n"
        html += f"        <p>Liczba problemów: {len(self.lost_data)}</p>\n"
        html += "        <table>\n"
        html += "            <tr><th>Pozycja</th><th>Typ bloku</th><th>Typ danych</th><th>Opis</th><th>Poziom</th></tr>\n"
        
        for item in self.lost_data:
            pos_str = f"({item.position[0]}, {item.position[1]}, {item.position[2]})"
            severity_class = f"severity-{item.severity}"
            html += f"            <tr class='{severity_class}'>\n"
            html += f"                <td>{pos_str}</td>\n"
            html += f"                <td>{item.block_type}</td>\n"
            html += f"                <td>{item.data_type}</td>\n"
            html += f"                <td>{item.description}</td>\n"
            html += f"                <td>{item.severity}</td>\n"
            html += "            </tr>\n"
        
        html += "        </table>\n"
        return html
    
    def _generate_verification_section_html(self) -> str:
        """Generuje sekcję weryfikacji w HTML"""
        html = "\n        <h2>Do Weryfikacji Manualnej</h2>\n"
        html += f"        <p>Liczba elementów: {len(self.verification_items)}</p>\n"
        html += "        <table>\n"
        html += "            <tr><th>Pozycja</th><th>Typ</th><th>Powód</th><th>Rekomendacja</th><th>Priorytet</th></tr>\n"
        
        for item in self.verification_items:
            pos_str = f"({item.position[0]}, {item.position[1]}, {item.position[2]})"
            priority_class = f"priority-{item.priority}"
            html += f"            <tr class='{priority_class}'>\n"
            html += f"                <td>{pos_str}</td>\n"
            html += f"                <td>{item.block_type}</td>\n"
            html += f"                <td>{item.reason}</td>\n"
            html += f"                <td>{item.recommendation}</td>\n"
            html += f"                <td>{item.priority}</td>\n"
            html += "            </tr>\n"
        
        html += "        </table>\n"
        return html
    
    def _generate_block_types_section_html(self, results: List[ConversionResult]) -> str:
        """Generuje sekcję statystyk per typ bloku"""
        # Grupuj wyniki
        by_type = {}
        for result in results:
            block_type = result.original_block.block_id
            if block_type not in by_type:
                by_type[block_type] = {"total": 0, "success": 0, "failed": 0}
            by_type[block_type]["total"] += 1
            if result.success:
                by_type[block_type]["success"] += 1
            else:
                by_type[block_type]["failed"] += 1
        
        html = "\n        <h2>Statystyki per Typ Bloku</h2>\n"
        html += "        <table>\n"
        html += "            <tr><th>Typ bloku</th><th>Ilość</th><th>Sukces</th><th>Nieudane</th><th>Skuteczność</th></tr>\n"
        
        for block_type, data in sorted(by_type.items(), key=lambda x: x[1]["total"], reverse=True):
            rate = (data["success"] / data["total"] * 100) if data["total"] > 0 else 0
            html += "            <tr>\n"
            html += f"                <td>{block_type}</td>\n"
            html += f"                <td>{data['total']}</td>\n"
            html += f"                <td class='success'>{data['success']}</td>\n"
            html += f"                <td class='error'>{data['failed']}</td>\n"
            html += f"                <td>{rate:.1f}%</td>\n"
            html += "            </tr>\n"
        
        html += "        </table>\n"
        return html
    
    def _generate_markdown_report(self, results: List[ConversionResult],
                                   stats: BatchConversionStats) -> str:
        """Generuje raport Markdown"""
        output_file = self.output_path / "conversion_report.md"
        
        md = f"""# Raport Konwersji BiblioCraft

**Wygenerowano:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Statystyki

| Metryka | Wartość |
|---------|---------|
| Znalezionych bloków | {stats.total_bc_blocks} |
| Przekonwertowanych | {stats.converted_blocks} |
| Nieudanych | {stats.failed_blocks} |
| Pominiętych | {stats.skipped_blocks} |
| Skuteczność | {stats.success_rate:.1f}% |
| Czas wykonania | {stats.duration_seconds:.2f}s |

"""
        
        # Dodaj sekcję utraconych danych
        if self.lost_data:
            md += "## Utracone Dane\n\n"
            md += "| Pozycja | Typ | Opis | Poziom |\n"
            md += "|---------|-----|------|--------|\n"
            for item in self.lost_data:
                pos_str = f"({item.position[0]}, {item.position[1]}, {item.position[2]})"
                md += f"| {pos_str} | {item.block_type} | {item.description} | {item.severity} |\n"
            md += "\n"
        
        # Dodaj sekcję weryfikacji
        if self.verification_items:
            md += "## Do Weryfikacji Manualnej\n\n"
            md += "| Pozycja | Typ | Powód | Rekomendacja | Priorytet |\n"
            md += "|---------|-----|-------|--------------|-----------|\n"
            for item in self.verification_items:
                pos_str = f"({item.position[0]}, {item.position[1]}, {item.position[2]})"
                md += f"| {pos_str} | {item.block_type} | {item.reason} | {item.recommendation} | {item.priority} |\n"
            md += "\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md)
        
        return str(output_file)
    
    def _generate_json_report(self, results: List[ConversionResult],
                              stats: BatchConversionStats) -> str:
        """Generuje raport JSON"""
        output_file = self.output_path / "conversion_report.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "statistics": stats.to_dict(),
            "lost_data": [
                {
                    "position": item.position,
                    "block_type": item.block_type,
                    "data_type": item.data_type,
                    "description": item.description,
                    "severity": item.severity
                }
                for item in self.lost_data
            ],
            "verification_items": [
                {
                    "position": item.position,
                    "block_type": item.block_type,
                    "reason": item.reason,
                    "recommendation": item.recommendation,
                    "priority": item.priority
                }
                for item in self.verification_items
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return str(output_file)
    
    def export_lost_data_list(self) -> str:
        """Eksportuje listę utraconych danych do osobnego pliku"""
        output_file = self.output_path / "lost_data.json"
        
        data = [
            {
                "position": item.position,
                "block_type": item.block_type,
                "data_type": item.data_type,
                "description": item.description,
                "severity": item.severity
            }
            for item in self.lost_data
        ]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return str(output_file)
    
    def export_verification_checklist(self) -> str:
        """Eksportuje listę weryfikacji do formatu checklisty"""
        output_file = self.output_path / "verification_checklist.txt"
        
        lines = [
            "CHECKLISTA WERYFIKACJI BIBLIOCRAFT",
            "=" * 50,
            f"Liczba elementów: {len(self.verification_items)}",
            "",
        ]
        
        # Grupuj po priorytecie
        by_priority = {"high": [], "medium": [], "low": []}
        for item in self.verification_items:
            by_priority[item.priority].append(item)
        
        for priority in ["high", "medium", "low"]:
            if by_priority[priority]:
                lines.append(f"\n[{priority.upper()}] Priorytet:")
                lines.append("-" * 30)
                for item in by_priority[priority]:
                    pos = f"({item.position[0]}, {item.position[1]}, {item.position[2]})"
                    lines.append(f"[ ] {pos} - {item.block_type}")
                    lines.append(f"    Powód: {item.reason}")
                    lines.append(f"    Rekomendacja: {item.recommendation}")
                    lines.append("")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        
        return str(output_file)


# Funkcje pomocnicze

def generate_conversion_report(output_path: str,
                                results: List[ConversionResult],
                                stats: BatchConversionStats,
                                format: str = "html") -> str:
    """
    Funkcja pomocnicza do generowania raportu
    
    Returns:
        Ścieżka do wygenerowanego raportu
    """
    generator = BiblioCraftReportGenerator(output_path)
    return generator.generate_full_report(results, stats, format)


# Testowanie
if __name__ == "__main__":
    print("=" * 60)
    print("TEST: BiblioCraft Report Generator")
    print("=" * 60)
    
    # Test utraconych danych
    print("\n--- Test lost data ---")
    lost = LostDataInfo(
        position=(100, 64, 200),
        block_type="BiblioCraft:Bookcase",
        data_type="inventory",
        description="Utracono 6 książek",
        severity="warning"
    )
    print(f"  Pozycja: {lost.position}")
    print(f"  Opis: {lost.description}")
    
    # Test weryfikacji
    print("\n--- Test verification item ---")
    verify = VerificationItem(
        position=(101, 64, 200),
        block_type="BiblioCraft:Painting",
        reason="Brak obrazu",
        recommendation="Sprawdź ręcznie",
        priority="high"
    )
    print(f"  Pozycja: {verify.position}")
    print(f"  Priorytet: {verify.priority}")
    
    print("\n" + "=" * 60)
    print("Test zakończony!")
    print("=" * 60)
