# SKILL: Zadanie 4 - Integracja konwertera moda z parserem mapy

> **Cel:** Zintegrować konwerter danego moda z systemem parsera mapy Minecraft 1.7.10, zaimplementować batch conversion i zweryfikować pokrycie na rzeczywistej mapie.

---

## KRYTYCZNE ZASADY BEZPIECZEŃSTWA

### 🔴 ABSOLUTNY ZAKAZ MODYFIKACJI MAPY ŹRÓDŁOWEJ

```
NIGDY NIE MODYFIKUJ FOLDERU: mapa_1710/

Ta mapa jest JEDYNYM oryginałem i NIGDY nie może być nadpisana, usunięta ani zmodyfikowana.
Jakiekolwiek operacje zapisu wykonuj TYLKO do:
- output/
- mapa_118/ (docelowa, pusta)
- lightweigh_map_templates/
```

**Dozwolone operacje na `mapa_1710/`:**
- ✅ Odczyt plików `.mca` (regiony)
- ✅ Odczyt `level.dat`
- ✅ Odczyt `playerdata/`

**ZABRONIONE operacje na `mapa_1710/`:**
- ❌ Zapis
- ❌ Usuwanie
- ❌ Modyfikacja
- ❌ Kopiowanie z nadpisaniem

---

## Mapa źródłowa i strefy do analizy

### Mapa źródłowa

```
Ścieżka: mapa_1710/
Wersja: Minecraft 1.7.10
Format: Anvil (.mca)
Rozmiar: ~5GB
```

### Strefy do analizy

Analiza musi objąć **wszystkie zdefiniowane strefy**:

| Strefa | Zakres X | Zakres Z | Opis |
|--------|----------|----------|------|
| `billund` | 280 → 602 | -364 → -81 | Billund |
| `choroszcz` | 763 → 916 | -787 → -636 | Choroszcz |
| `iii_rzesza` | 455 → 966 | 2955 → 3477 | III Rzesza |
| `rzym` | 301 → 1005 | 163 → 929 | Rzym |
| `zsrr` | -2948 → -2086 | -2857 → -1759 | ZSRR |

Definicje stref znajdują się w: `strefy/*/coords.json`

### Dodatkowe regiony do sprawdzenia

Oprócz stref, sprawdź losowe regiony z różnych części mapy:
- `r.0.0.mca` (spawn)
- `r.1.1.mca`, `r.-1.-1.mca` (okolice spawnu)
- `r.10.10.mca`, `r.-10.-10.mca` (dalsze obszary)

---

## KRYTYCZNE: Format identyfikatorów w Minecraft 1.7.10

### Problem halucynacji agentów

Agenci często **mylą formaty ID**, co prowadzi do wyników "0 bloków znaleziono" mimo że bloki istnieją na mapie.

### Trzy różne formaty ID w MC 1.7.10

| Format | Gdzie używany | Przykład | Jak wygląda w NBT |
|--------|---------------|----------|-------------------|
| **Block ID (string)** | Pole `id` w sekcji Blocks (1.7.10+) | `BiblioCraft:Bookcase` | `id: "BiblioCraft:Bookcase"` |
| **Block ID (numeric)** | Stary format bloków | `1245` | `Blocks: [byte array]` |
| **TileEntity ID** | Pole `id` w TileEntity | `TileEntityBookcase` | `id: "TileEntityBookcase"` |

### Szczegółowe wyjaśnienie

#### 1. Block ID (w sekcjach chunka)

W MC 1.7.10 bloki w chunku mogą być zapisane jako:
- **Numeryczne ID** (0-4095) + metadata (0-15) - starszy format
- **String ID** w formacie `ModName:BlockName` - nowszy format

```
Przykłady Block ID:
- "minecraft:stone"
- "BiblioCraft:Bookcase"
- "Thaumcraft:blockCustomPlant"
- "appliedenergistics2:tile.BlockController"
```

#### 2. TileEntity ID (Block Entity)

TileEntity (BlockEntity) to dane dodatkowe dla bloków (inventory, stan maszyny, itp.). Mają **WŁASNY format ID** który NIE jest taki sam jak Block ID!

```
Format TileEntity ID w 1.7.10:

Mod BiblioCraft:
  Block ID:      "BiblioCraft:Bookcase"
  TileEntity ID: "TileEntityBookcase"        ← INNY FORMAT!

Mod Thaumcraft:
  Block ID:      "Thaumcraft:blockTable"
  TileEntity ID: "thaumcraft.BlockTable"     ← INNY FORMAT!

Mod Applied Energistics 2:
  Block ID:      "appliedenergistics2:tile.BlockController"
  TileEntity ID: "AEController"              ← INNY FORMAT!

Mod Thermal Expansion:
  Block ID:      "ThermalExpansion:Machine"
  TileEntity ID: "thermalexpansion:machine.furnace"

Mod IndustrialCraft2:
  Block ID:      "IC2:blockMachine"
  TileEntity ID: "IC2TEMacerator"

Vanilla Minecraft:
  Block ID:      "minecraft:chest"
  TileEntity ID: "Chest"                     ← Bez prefiksu!
```

### Jak znaleźć poprawny format TileEntity ID

**JEDYNY pewny sposób:** Przeczytaj rzeczywiste dane z mapy!

```python
# Skrypt do odkrycia formatów TE ID na mapie
from minecraft_map_parser.anvil_parser import AnvilParser

parser = AnvilParser("mapa_1710/region/r.0.0.mca")
chunk = parser.get_chunk(0, 0)

# Wypisz wszystkie unikalne TileEntity ID
te_ids = set()
for te in chunk.get_tile_entities():
    te_ids.add(te.get("id", "UNKNOWN"))

for te_id in sorted(te_ids):
    print(te_id)
```

**NIE ZGADUJ** formatu TE ID na podstawie Block ID - zawsze sprawdź na mapie!

---

## Implementacja parsera dla moda

### Krok 1: Odkryj format TE ID na mapie

Przed pisaniem kodu, uruchom analizę mapy żeby poznać rzeczywiste formaty:

```python
"""Skrypt do odkrycia TE ID dla moda X"""

from minecraft_map_parser.anvil_parser import AnvilParser
from pathlib import Path
import re

def find_mod_te_ids(world_path: str, mod_patterns: list[str]):
    """
    Znajduje wszystkie TileEntity ID pasujące do wzorców moda.

    Args:
        world_path: Ścieżka do mapa_1710
        mod_patterns: Lista wzorców regex do szukania
                      np. ["BiblioCraft", "bibliocraft", "TileEntityBook"]
    """
    region_path = Path(world_path) / "region"
    found_ids = set()

    # Sprawdź kilka regionów
    for region_file in list(region_path.glob("r.*.*.mca"))[:10]:
        parser = AnvilParser(str(region_file))

        for cz in range(32):
            for cx in range(32):
                chunk = parser.get_chunk(cx, cz)
                if not chunk:
                    continue

                for te in chunk.get_tile_entities():
                    te_id = te.get("id", "")

                    # Sprawdź czy pasuje do wzorców
                    for pattern in mod_patterns:
                        if re.search(pattern, te_id, re.IGNORECASE):
                            found_ids.add(te_id)
                            break

    return found_ids

# Przykład użycia dla BiblioCraft
bc_ids = find_mod_te_ids("mapa_1710", [
    r"biblio",
    r"TileEntityBook",
    r"TileEntityShelf",
    r"TileEntityArmor",
])

print("Znalezione TileEntity ID:")
for te_id in sorted(bc_ids):
    print(f"  - {te_id}")
```

### Krok 2: Zdefiniuj stałą z rzeczywistymi TE ID

Po odkryciu formatów, zdefiniuj stałą:

```python
# KRYTYCZNE: Te ID muszą być DOKŁADNIE takie jak na mapie!
# Nie zgaduj - sprawdź skryptem powyżej.

MOD_TILE_ENTITY_IDS = {
    # Format odkryty z mapy, NIE zgadywany
    "TileEntityBookcase",
    "TileEntityArmorStand",
    # ... itd.
}
```

### Krok 3: Implementacja wykrywania

```python
def is_mod_tile_entity(self, te_data: dict) -> bool:
    """
    Sprawdza czy TileEntity należy do danego moda.

    UWAGA: Sprawdzaj po RZECZYWISTYM formacie TE ID z mapy,
           nie po Block ID ani zgadywanym formacie!
    """
    te_id = te_data.get("id", "")

    # Metoda 1: Dokładne dopasowanie (najlepsza)
    if te_id in MOD_TILE_ENTITY_IDS:
        return True

    # Metoda 2: Wzorzec (jeśli znasz konwencję moda)
    # OSTROŻNIE - może złapać fałszywe pozytywy
    # if te_id.startswith("TileEntityBC"):
    #     return True

    return False
```

---

## Struktura batch converter

### Architektura

```
minecraft_map_parser/
├── AnvilParser          # Odczyt plików .mca
└── ChunkData            # Dane chunka
        │
        v
ModChunkParser           # Wykrywa TE danego moda w chunku
        │
        v
ModBatchConverter        # Konwertuje wiele bloków
        │
        ├── Odczyt z mapa_1710/ (TYLKO ODCZYT!)
        ├── Konwersja NBT
        └── Zapis do output/ lub mapa_118/
```

### Szablon batch converter

```python
class ModBatchConverter:
    """Batch converter dla moda X"""

    def __init__(self, source_world: str, output_path: str):
        # KRYTYCZNE: source_world jest TYLKO DO ODCZYTU
        self.source_world = Path(source_world)  # mapa_1710
        self.output_path = Path(output_path)    # output/mod_x/

        # Utwórz folder wyjściowy (NIE w source_world!)
        self.output_path.mkdir(parents=True, exist_ok=True)

    def run_batch_conversion(self):
        """
        Uruchamia konwersję.

        GWARANCJA: Ta metoda NIE MODYFIKUJE mapa_1710/
        """
        # 1. Analiza (odczyt)
        results = self._scan_source_world()

        # 2. Konwersja (w pamięci)
        converted = self._convert_blocks(results)

        # 3. Zapis (TYLKO do output_path, NIGDY do source_world)
        self._save_results(converted)

    def _save_results(self, converted):
        """Zapisuje wyniki TYLKO do output_path"""
        # ZABEZPIECZENIE
        assert not str(self.output_path).startswith(str(self.source_world)), \
            "BŁĄD: Próba zapisu do mapy źródłowej!"

        output_file = self.output_path / "converted_blocks.json"
        with open(output_file, 'w') as f:
            json.dump(converted, f, indent=2)
```

---

## Generowanie raportów

### Wymagane raporty

Po analizie wygeneruj:

1. **`output/{mod}_analysis.json`** - surowe dane
2. **`output/{mod}_report.md`** - czytelny raport
3. **`output/{mod}_coverage.md`** - pokrycie kodu vs bloki na mapie

### Zawartość raportu

```markdown
# Raport analizy {MOD_NAME}

## Przeskanowane obszary
- Strefy: billund, choroszcz, iii_rzesza, rzym, zsrr
- Dodatkowe regiony: r.0.0, r.1.1, ...
- Łącznie chunków: X

## Znalezione bloki
| TileEntity ID | Liczba | Obsługiwany |
|---------------|--------|-------------|
| TileEntityX   | 150    | ✅          |
| TileEntityY   | 42     | ❌          |

## Pokrycie kodu
- Obsługiwane typy: X / Y (Z%)
- Bloki z pełną konwersją: N
- Bloki bez konwersji: M

## Nieznane TileEntity ID
Lista TE ID które znaleziono ale nie są w kodzie:
- UnknownTE1
- UnknownTE2
```

---

## Checklist przed zakończeniem

### Bezpieczeństwo
- [ ] Kod NIGDY nie zapisuje do `mapa_1710/`
- [ ] Wszystkie zapisy idą do `output/` lub `mapa_118/`
- [ ] Jest asercja/sprawdzenie przed każdym zapisem

### Poprawność wykrywania
- [ ] TE ID zostały ODKRYTE z mapy, nie zgadnięte
- [ ] Parser używa rzeczywistego formatu TE ID
- [ ] Uruchomiono test na mapie i znaleziono >0 bloków (jeśli mod jest używany)

### Pokrycie
- [ ] Przeskanowano wszystkie 5 stref
- [ ] Przeskanowano dodatkowe losowe regiony
- [ ] Raport zawiera listę nieobsługiwanych TE ID

### Dokumentacja
- [ ] HANDOFF.md opisuje co zostało zrobione
- [ ] Raport w `output/` zawiera pełne statystyki

---

## Częste błędy do uniknięcia

### ❌ Błąd 1: Zgadywanie formatu TE ID

```python
# ŹLE - zgadywanie formatu
if te_id.startswith("BiblioCraft:"):  # To jest Block ID, nie TE ID!
    return True

# ŹLE - zgadywanie na podstawie dokumentacji
if te_id == "bibliocraft:bookcase":  # Może być inny format!
    return True

# DOBRZE - użycie formatu odkrytego z mapy
if te_id in DISCOVERED_TE_IDS:  # Te ID zostały odczytane z mapy
    return True
```

### ❌ Błąd 2: Zapis do mapy źródłowej

```python
# ŹLE - zapis do source
output = Path(source_world) / "converted"
output.mkdir()  # NIGDY!

# DOBRZE - zapis do osobnego folderu
output = Path("output") / "mod_conversion"
output.mkdir(parents=True, exist_ok=True)
```

### ❌ Błąd 3: Pominięcie stref

```python
# ŹLE - tylko spawn
regions = ["r.0.0.mca"]

# DOBRZE - wszystkie strefy + losowe regiony
regions = get_regions_for_all_zones() + get_random_regions(10)
```

---

## Przykładowy workflow

```
1. Uruchom skrypt odkrywania TE ID
   → Zapisz wynik do docs/mod_mapping_indepth/from/{mod}_te_ids.md

2. Zaimplementuj parser z RZECZYWISTYMI TE ID

3. Uruchom analizę na wszystkich strefach
   → Zapisz do output/{mod}_analysis.json

4. Sprawdź czy znaleziono bloki
   → Jeśli 0: sprawdź format TE ID!
   → Jeśli >0: kontynuuj

5. Zaimplementuj batch converter

6. Wygeneruj raport pokrycia
   → output/{mod}_coverage.md

7. Napisz HANDOFF.md
```

---

**Autor:** Claude Code
**Wersja:** 2.0 (ogólna, dla dowolnego moda)
**Data:** 2026-02-02
