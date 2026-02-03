# Handoff: BiblioCraft - Zadanie 4 (Integracja z parserem i batch conversion)

## Podsumowanie sesji

Wykonano pełną integrację konwertera BiblioCraft z systemem parsera mapy oraz zaimplementowano batch conversion:

1. **BC Chunk Parser** - integracja z `minecraft_map_parser` do wykrywania bloków BC w chunkach
2. **Batch Converter** - konwersja wsadowa wielu chunków z postępem i statystykami
3. **Report Generator** - generowanie raportów HTML/Markdown/JSON z wynikami
4. **Edge Cases Handler** - obsługa błędów, fallbacki, naprawa uszkodzonych danych

---

## Ukończono

- [x] Integracja z `minecraft_map_parser.AnvilParser`
- [x] `BiblioCraftChunkParser` - wykrywanie bloków BC w chunkach
- [x] `BiblioCraftBatchConverter` - konwersja wsadowa z callbackami postępu
- [x] `BiblioCraftReportGenerator` - raporty HTML/Markdown/JSON
- [x] `BCEdgeCaseManager` - obsługa edge cases i fallbacki
- [x] System weryfikacji manualnej i listy utraconych danych
- [x] Naprawa uszkodzonych NBT (`BCNBTFixup`)
- [x] Rozwiązywanie brakujących tekstur (`TextureFallbackResolver`)
- [x] Aktualizacja `__init__.py` o 25+ nowych eksportów

---

## Nowe pliki

| Plik | Opis | Kluczowe klasy |
|------|------|----------------|
| `bc_chunk_parser.py` | Integracja z parserem NBT | `BiblioCraftChunkParser`, `BCBlockInChunk` |
| `batch_converter.py` | Konwersja wsadowa | `BiblioCraftBatchConverter`, `BatchConversionStats` |
| `report_generator.py` | Raportowanie | `BiblioCraftReportGenerator`, `LostDataInfo`, `VerificationItem` |
| `edge_cases_handler.py` | Obsługa błędów | `BCEdgeCaseManager`, `BCNBTFixup`, `TextureFallbackResolver` |

---

## Architektura integracji

```
minecraft_map_parser/
├── AnvilParser
└── ChunkData
        │
        v
bc_chunk_parser.BiblioCraftChunkParser
        │
        ├──> Analiza chunka
        ├──> Wykrycie BC TE
        └──> Ekstrakcja BCBlockInChunk
                    │
                    v
        batch_converter.BiblioCraftBatchConverter
                    │
                    ├──> Konwersja NBT (nbt_converter)
                    ├──> Edge case handling
                    └──> Statystyki
                                │
                                v
            report_generator.BiblioCraftReportGenerator
                                │
                                ├──> Raport HTML
                                ├──> Lista utraconych danych
                                └──> Checklista weryfikacji
```

---

## Szczegóły implementacji

### 1. BC Chunk Parser (`bc_chunk_parser.py`)

Integruje się z istniejącym `AnvilParser`:

```python
from minecraft_map_parser.anvil_parser import AnvilParser

class BiblioCraftChunkParser:
    def __init__(self, world_path: str):
        self.parser = AnvilParser(str(self.region_path))
    
    def analyze_chunk(self, chunk_x: int, chunk_z: int) -> ChunkAnalysisResult:
        chunk_data = self.parser.get_chunk(chunk_x, chunk_z)
        tile_entities = chunk_data.get_tile_entities()
        # Filtruj tylko BC TE...
```

#### Kluczowe metody

| Metoda | Opis |
|--------|------|
| `analyze_chunk(cx, cz)` | Analizuje pojedynczy chunk |
| `analyze_region(rx, rz)` | Analizuje cały region (32x32 chunków) |
| `scan_all_regions()` | Skanuje wszystkie regiony w świecie |

#### BCBlockInChunk

```python
@dataclass
class BCBlockInChunk:
    x: int; y: int; z: int
    block_id: str          # np. "BiblioCraft:Bookcase"
    block_name: str        # np. "Bookcase"
    metadata: int
    chunk_x: int; chunk_z: int
    tile_entity: Dict      # Surowe dane NBT
    
    @property
    def absolute_pos -> (int, int, int)
    @property
    def region_pos -> (int, int)
```

---

### 2. Batch Converter (`batch_converter.py`)

#### Główna klasa

```python
converter = BiblioCraftBatchConverter(
    world_path_1710="mapa_1710",
    output_path="output/bc_conversion"
)

# Opcjonalny callback postępu
def progress_callback(percent, message):
    print(f"{percent:.1f}%: {message}")

converter.set_progress_callback(progress_callback)

# Uruchom konwersję
stats = converter.run_batch_conversion()
```

#### Fazy konwersji

1. **Analiza (30%)** - skanowanie wszystkich chunków
2. **Konwersja (60%)** - konwersja bloków BC
3. **Raportowanie (10%)** - generowanie plików wyjściowych

#### Wyniki

```python
stats: BatchConversionStats
stats.total_bc_blocks      # Całkowita liczba bloków BC
stats.converted_blocks     # Przekonwertowane
stats.failed_blocks        # Nieudane
stats.success_rate         # Skuteczność %
stats.duration_seconds     # Czas wykonania
```

Pliki wyjściowe:
- `converted_blocks.json` - Lista przekonwertowanych bloków z NBT
- `conversion_stats.json` - Statystyki
- `conversion_errors.json` - Błędy

---

### 3. Report Generator (`report_generator.py`)

#### Generowanie raportu

```python
generator = BiblioCraftReportGenerator("output/path")
report_path = generator.generate_full_report(
    results=conversion_results,
    stats=conversion_stats,
    format="html"  # lub "markdown", "json"
)
```

#### Raport HTML zawiera

- Statystyki w formie kart (liczby, skuteczność, czas)
- Sekcję utraconych danych (np. książki które się nie zmieściły)
- Tabelę do weryfikacji manualnej z priorytetami
- Statystyki per typ bloku

#### Dodatkowe listy

```python
# Eksport utraconych danych
generator.export_lost_data_list()  # -> lost_data.json

# Checklista weryfikacji
generator.export_verification_checklist()  # -> verification_checklist.txt
```

#### LostDataInfo

```python
@dataclass
class LostDataInfo:
    position: (int, int, int)
    block_type: str
    data_type: str          # "inventory", "texture", etc.
    description: str
    severity: str           # "warning", "info", "critical"
```

#### VerificationItem

```python
@dataclass
class VerificationItem:
    position: (int, int, int)
    block_type: str
    reason: str
    recommendation: str
    priority: str           # "low", "medium", "high"
```

---

### 4. Edge Cases Handler (`edge_cases_handler.py`)

#### BCEdgeCaseManager

Główna klasa zarządzająca edge cases:

```python
manager = BCEdgeCaseManager()
result = manager.process_block(
    te_data={...},
    block_id="BiblioCraft:FramedChest",
    pos=(100, 64, 200)
)

# result:
{
    "te_data": {...},           # Naprawione dane
    "warnings": [...],          # Ostrzeżenia
    "used_fallbacks": [...]     # Użyte fallbacki
}
```

#### BCNBTFixup

Naprawia uszkodzone dane NBT:

```python
# Uzupełnia brakujące pola
BCNBTFixup.fixup_te_data(te_data, "TileEntityBookcase")

# Czyści inventory
BCNBTFixup.sanitize_inventory(items_list)

# Naprawia ID tekstury
BCNBTFixup.fix_texture_id("invalid_texture")
```

#### TextureFallbackResolver

Rozwiązuje brakujące tekstury:

```python
resolved, used_fallback = TextureFallbackResolver.resolve_texture(
    "UnknownMod:custom_block"
)
# resolved = "minecraft:oak_planks"
# used_fallback = True
```

Fallback chain:
- `BiomesOPlenty:*` → `minecraft:oak_planks`
- `Forestry:*` → `minecraft:oak_planks`
- `Natura:*` → `minecraft:oak_planks`
- Nieznany mod → `minecraft:oak_planks`

#### UnknownBlockHandler

Obsługuje nieznane bloki:

```python
# Sprawdź czy blok jest znany
UnknownBlockHandler.is_known_block("BiblioCraft:UnknownBlock")

# Spróbuj sklasyfikować
unknown_type = UnknownBlockHandler.classify_unknown_block(
    block_id="BiblioCraft:Unknown",
    te_data={"Items": [...]}
)
# Zwraca: "probably_bookcase", "probably_shelf", etc.
```

---

## API - Przykłady użycia

### Pełna konwersja świata

```python
from converters.bibliocraft import convert_world_bibliocraft

stats = convert_world_bibliocraft(
    world_path_1710="mapa_1710",
    output_path="output/bc_conversion",
    progress_callback=lambda p, m: print(f"{p:.0f}%: {m}")
)

print(f"Przekonwertowano: {stats['converted_blocks']}")
print(f"Skuteczność: {stats['success_rate_percent']}%")
```

### Konwersja pojedynczego chunka

```python
from converters.bibliocraft import convert_chunk_bibliocraft

results = convert_chunk_bibliocraft(
    world_path_1710="mapa_1710",
    chunk_x=6,
    chunk_z=12,
    output_path="output/test_chunk"
)

for result in results:
    print(f"{result.position}: {result.success}")
```

### Generowanie raportu

```python
from converters.bibliocraft import generate_conversion_report

report_path = generate_conversion_report(
    output_path="output/reports",
    results=conversion_results,
    stats=conversion_stats,
    format="html"
)
```

### Ręczna obsługa edge case

```python
from converters.bibliocraft import BCEdgeCaseManager

manager = BCEdgeCaseManager()
result = manager.process_block(
    te_data={"id": "TileEntityFramedChest", ...},
    block_id="TileEntityFramedChest",
    pos=(100, 64, 200)
)

if result["warnings"]:
    print("Ostrzeżenia:", result["warnings"])

if result["used_fallbacks"]:
    print("Użyte fallbacki:", result["used_fallbacks"])

summary = manager.get_summary()
print(f"Edge cases: {summary['total_cases']}")
```

---

## Obsługiwane edge cases

| Typ | Opis | Rozwiązanie |
|-----|------|-------------|
| `missing_texture` | Nieznana tekstura | Fallback do oak_planks |
| `corrupted_nbt` | Uszkodzone dane | Próba naprawy lub pominięcie |
| `unknown_block` | Nieznany typ bloku | Logowanie, pominięcie |
| `missing_te_data` | Brak danych TE | Konwersja jako dekoracyjny |
| `invalid_inventory` | Nieprawidłowe itemy | Czyszczenie listy |
| `unknown_mod_texture` | Tekstura z modu | Fallback do vanilla |

---

## Struktura wyjściowa

```
output/bc_conversion/
├── converted_blocks.json       # Przekonwertowane bloki z NBT
├── conversion_stats.json       # Statystyki
├── conversion_errors.json      # Błędy
└── reports/
    ├── conversion_report.html      # Raport HTML
    ├── conversion_report.md        # Raport Markdown
    ├── conversion_report.json      # Raport JSON
    ├── lost_data.json              # Utracone dane
    └── verification_checklist.txt  # Checklista weryfikacji
```

---

## Problemy znane i ograniczenia

### 🔴 Do rozwiązania w Zadaniu 5

1. **Integracja z rzeczywistymi plikami MCA**
   - Obecnie testowane tylko na mockach
   - Wymaga przetestowania na realnych danych z `mapa_1710`

2. **Wydajność dla dużych map**
   - Skanowanie 5GB mapy może być wolne
   - Rozważyć równoległe przetwarzanie chunków

3. **Zapis do formatu 1.18.2**
   - Obecnie tylko generowanie JSON z NBT
   - Brak faktycznego zapisu do plików MCA 1.18.2

### 🟡 Ulepszenia opcjonalne

4. **Baza danych znanych bloków**
   - Rozszerzyć `KNOWN_BC_IDS` o wszystkie możliwe warianty

5. **Cache'owanie wyników analizy**
   - Unikanie ponownego skanowania tych samych chunków

---

## Testowanie

```bash
# Test modułów
python -m converters.bibliocraft.bc_chunk_parser
python -m converters.bibliocraft.batch_converter
python -m converters.bibliocraft.report_generator
python -m converters.bibliocraft.edge_cases_handler

# Test integracji
python -c "
from converters.bibliocraft import BiblioCraftBatchConverter
converter = BiblioCraftBatchConverter('test_world', 'output')
print('Inicjalizacja OK')
"
```

---

## Statystyki kodu

| Moduł | Klasy | Metody | Linie |
|-------|-------|--------|-------|
| bc_chunk_parser.py | 3 | 15+ | ~420 |
| batch_converter.py | 4 | 20+ | ~550 |
| report_generator.py | 4 | 15+ | ~600 |
| edge_cases_handler.py | 6 | 25+ | ~500 |
| **RAZEM Zadanie 4** | **17** | **75+** | **~2100** |
| **RAZEM Zadania 1-4** | **40+** | **180+** | **~6500** |

---

## Następne kroki (Zadanie 5)

1. **Test na rzeczywistej mapie**
   - Uruchomić konwersję na `mapa_1710`
   - Zweryfikować wyniki

2. **Integracja z zapisem 1.18.2**
   - Połączyć z `nbt_writer` z `minecraft_map_parser`
   - Zapisywać przekonwertowane bloki do plików MCA

3. **Weryfikacja w grze**
   - Wczytać przekonwertowaną mapę w MC 1.18.2
   - Sprawdzić czy bloki wyświetlają się poprawnie

4. **Optymalizacja**
   - Równoległe przetwarzanie
   - Cache'owanie

---

**Status:** ✅ Zadanie 4 ukończone - gotowe do przeglądu i akceptacji  
**Data:** 2026-02-02  
**Agent:** AI Konwersji BiblioCraft
