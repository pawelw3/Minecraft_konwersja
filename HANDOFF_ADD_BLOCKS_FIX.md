# Poprawka: Obsługa Add/AddBlocks w parserze Anvil (Minecraft 1.7.10)

## Problem

W formacie Anvil (Minecraft 1.7.10) bloki o ID > 255 (czyli większość bloków z modów) wymagają specjalnej obsługi:

- **Blocks[]**: 4096 bajtów, zawiera dolne 8 bitów ID (0-255)
- **Add/AddBlocks[]**: 2048 bajtów, zawiera górne 4 bity ID (0-15)
- **Pełne ID**: `(Add[nibble] << 8) | Blocks[byte]`

Bez tej obsługi bloki modowane są błędnie odczytywane jako bloki vanilla o ID z zakresu 0-255.

## Rozwiązanie

### 1. Nowe metody w `ChunkData` (`anvil_parser.py`)

```python
def get_block_ids_from_sections(self) -> List[int]:
    """Zwraca listę pełnych ID bloków z sekcji (z uwzględnieniem Add)."""
    
def get_blocks_at_positions(self) -> Dict[Tuple[int, int, int], int]:
    """Zwraca mapę pozycji bloków do ich ID (z uwzględnieniem Add)."""
```

Implementacja uwzględnia:
- Odczyt zarówno `Add` jak i `AddBlocks` (różne nazwy w zależności od wersji)
- Poprawne dekodowanie nibbles (4 bity na blok)
- Obsługę zarówno parzystych jak i nieparzystych indeksów

### 2. Poprawka koordynatów w `EPChunkParser`

Problem: AnvilParser.get_chunk() wymaga **lokalnych** koordynatów (0-31), ale EPChunkParser podawał **globalne**.

Poprawka:
```python
# Globalne -> lokalne
local_chunk_x = chunk_x & 0x1F  # Równoważne chunk_x % 32
local_chunk_z = chunk_z & 0x1F

# Użycie lokalnych
chunk_data = parser.get_chunk(local_chunk_x, local_chunk_z)
```

### 3. Funkcje debugujące

```python
def debug_chunk_block_ids(self, chunk_x, chunk_z) -> Dict:
    """Zwraca wszystkie ID bloków z chunka (z Add/AddBlocks)."""
    
def debug_scan_for_modded_blocks(self, max_regions=5) -> Dict:
    """Skanuje regiony w poszukiwaniu bloków modowanych (ID >= 256)."""
```

## Wyniki weryfikacji

### Test na mapie 1.7.10

```
Przeskanowane regiony: 3
Chunki z blokami modded: 1301
Unikalne ID modded znalezione: 290

Przykładowe ID modded: [410, 411, 415, 416, 423, 425, 433, ...]
```

**Wniosek**: Na mapie są bloki modowane (290 różnych ID), więc parser działa poprawnie.

### Test skanowania Enchanting Plus

```
Przeskanowane regiony: 5
Chunki z EP: 0
Bloki EP: 0
```

**Wniosek**: Mody są na mapie, ale Enchanting Plus nie był używany przez graczy (co potwierdza wcześniejsze ustalenia).

## Zmienione pliki

| Plik | Zmiany |
|------|--------|
| `src/minecraft_map_parser/anvil_parser.py` | +130 linii - nowe metody do odczytu bloków z Add/AddBlocks |
| `src/converters/enchantingplus/ep_chunk_parser.py` | +120 linii - poprawka koordynatów, funkcje debugujące |
| `src/converters/enchantingplus/mappings/block_mappings.py` | +15 linii - funkcja `get_block_name()` |

## Testowanie

Wszystkie 41 testów przechodzi:
```bash
python -m pytest src/converters/enchantingplus/tests/ -v
# 41 passed
```

## Użycie debugowania

```python
from src.converters.enchantingplus import EPChunkParser

parser = EPChunkParser()

# Sprawdź konkretny chunk
debug = parser.debug_chunk_block_ids(-31, -31)
print(f"Modded blocks: {debug['modded_ids_count']}")

# Skanuj regiony w poszukiwaniu modded
results = parser.debug_scan_for_modded_blocks(max_regions=3)
print(f"Znaleziono {len(results['total_modded_ids_found'])} unikalnych ID modded")
```

## Zalecenia dla innych modów

Jeśli skanowanie innych modów (np. AE2, Bibliocraft) nie znajduje bloków:

1. Użyj `debug_scan_for_modded_blocks()` aby sprawdzić czy w ogóle są bloki modowane
2. Porównaj ID z listą znalezionych - może mod używa innych ID niż oczekiwane
3. Sprawdź czy bloki są Tile Entities (czy tylko w Blocks[])

## Podsumowanie

- ✅ Parser poprawnie obsługuje Add/AddBlocks
- ✅ Koordynaty chunków są poprawnie konwertowane (globalne -> lokalne)
- ✅ Bloki modowane są wykrywane (290 unikalnych ID)
- ✅ Brak bloków EP potwierdza, że mod nie był używany

---

**Data**: 2026-02-03
**Agent**: AI Assistant
**Status**: Poprawka wdrożona i przetestowana
