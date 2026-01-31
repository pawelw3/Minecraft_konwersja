# Hephaistos Worker - Wyniki Testów

Data: 2026-01-31

## Podsumowanie

Worker JVM używający biblioteki Hephaistos do bezpiecznej edycji plików regionów `.mca` Minecraft 1.7.10.

## Status Testów

| Test | Opis | Status |
|------|------|--------|
| Test 0 | Hello Jar - worker się buduje | ✅ PASS |
| Test 1 | Open world + list regions | ✅ PASS |
| Test 2 | Read → Write unchanged → Read again | ✅ PASS |
| Test 3 | Set 1 block - modyfikacja bloków 1.7.10 | ✅ PASS |
| Test 4 | Set command block + TE | ✅ PASS |
| Test 5 | Boot server smoke | ⏸️ PENDING (wymaga serwera 1.7.10) |
| Test 6 | Multi-chunk patch | ⏸️ PENDING |
| Test 7 | Mini-spiral R=1 | ⏸️ PENDING |
| Test 8 | Spirala R=3 | ⏸️ PENDING |

## Szczegóły Testów

### Test 0: Hello Jar
- **Cel**: Upewnić się, że worker JVM w ogóle startuje
- **Wynik**: ✅ Worker buduje się poprawnie, wyświetla help i exit code 0
- **Polecenie**: `java -jar worker.jar --help`

### Test 1: Open world + list regions
- **Cel**: Potwierdzić, że potrafimy znaleźć regiony `.mca` i je otworzyć
- **Wynik**: ✅ Wszystkie 9 regionów odczytanych poprawnie
- **Szczegóły**:
  - r.-1.-1.mca: 1024 chunków, pierwszy chunk OK
  - r.-1.-2.mca: 230 chunków, pierwszy chunk OK
  - r.-1.0.mca: 948 chunków, pierwszy chunk OK
  - r.-2.-1.mca: 215 chunków, pierwszy chunk OK
  - r.-2.-2.mca: 47 chunków, pierwszy chunk OK
  - r.-2.0.mca: 207 chunków, pierwszy chunk OK
  - r.0.-1.mca: 960 chunków, pierwszy chunk OK
  - r.0.-2.mca: 194 chunków, pierwszy chunk OK
  - r.0.0.mca: 889 chunków, pierwszy chunk OK
- **Polecenie**: `java -jar worker.jar --world <path> --list-regions`

### Test 2: Read → Write unchanged → Read again
- **Cel**: Udowodnić, że można bezpiecznie zapisać `.mca` nawet bez zmian
- **Wynik**: ✅ Round-trip działa poprawnie
- **Szczegóły**: Odczytano chunk (0,0), zapisano bez zmian, odczytano ponownie - koordynaty zachowane
- **Polecenie**: `java -jar worker.jar --world <path> --test-roundtrip`

### Test 3: Set 1 block
- **Cel**: Ustawić 1 blok w formacie 1.7.10 (Blocks/Data/AddBlocks)
- **Wynik**: ✅ Blok stone (ID=1) ustawiony poprawnie na pozycji (0, 64, 0)
- **Szczegóły**:
  - Pozycja: (0, 64, 0)
  - Chunk: (0, 0), Region: (0, 0)
  - Sekcja Y: 4
  - Odczytano: ID=1, Meta=0
- **Polecenie**: `java -jar worker.jar --world <path> --patch test_block_patch.json`

### Test 4: Set command block + TE
- **Cel**: Dopisać TE i zobaczyć, że round-trip zachowuje pola
- **Wynik**: ✅ Command Block z Tile Entity ustawiony poprawnie
- **Szczegóły**:
  - Blok: Command Block (ID=137) na pozycji (0, 64, 1)
  - TE: id='Control', Command='/say [ROUNDTRIP] ok'
  - Tile Entity znaleziony i zachowany po zapisie
- **Polecenie**: `java -jar worker.jar --world <path> --patch test_command_block_patch.json`

## Architektura

### Użyte biblioteki
- **Hephaistos 2.2.0**: NBT + MCA (Anvil) library
  - Maven: `io.github.jglrxavpok.hephaistos:common:2.2.0`
  - RegionFile do obsługi plików MCA
  - NBT API do manipulacji danymi

### Ograniczenia Hephaistos dla 1.7.10
- `ChunkColumn` wymaga `DataVersion` który nie istnieje w 1.7.10
- Dla formatu 1.7.10 używamy niskopoziomowego API NBT (bez ChunkColumn)
- Własna implementacja zapisu chunków bezpośrednio do plików MCA

### Struktura projektu
```
jvm/worker/
├── build.gradle.kts              # Konfiguracja Gradle z Hephaistos
├── src/main/kotlin/mc/editkit/worker/
│   ├── Main.kt                   # Główna klasa z CLI
│   ├── WorldEditor.kt            # Edytor świata (setBlock, setTileEntity, commit)
│   ├── TestCommands.kt           # Testy 1-2 (list regions, roundtrip)
│   ├── TestBlockSet.kt           # Test 3 (weryfikacja bloku)
│   ├── TestCommandBlock.kt       # Test 4 (weryfikacja command blocka)
│   └── Utils.kt                  # Funkcje pomocnicze
└── TEST_RESULTS.md               # Ten plik
```

## Przykłady użycia

### Ustawienie bloku
```bash
java -jar worker.jar --world ./mapa_1710 --patch patch.json
```

Plik `patch.json`:
```json
{
  "edits": [
    {"op": "set_block", "x": 0, "y": 64, "z": 0, "id": 1, "meta": 0}
  ]
}
```

### Ustawienie command blocka z Tile Entity
```json
{
  "edits": [
    {"op": "set_block", "x": 0, "y": 64, "z": 1, "id": 137, "meta": 0},
    {"op": "set_te", "x": 0, "y": 64, "z": 1, "nbt": {"id": "Control", "Command": "/say Hello"}}
  ]
}
```

## Wnioski

1. **Hephaistos działa z 1.7.10** - ale tylko część NBT i RegionFile (obsługa plików MCA)
2. **ChunkColumn nie jest kompatybilny z 1.7.10** - wymaga DataVersion
3. **Własna implementacja zapisu** - wymagana do bezpośredniego zapisu NBT do plików MCA
4. **Testy 0-4 PASS** - podstawowa funkcjonalność działa poprawnie

## Następne kroki

1. Test 5: Boot server smoke (uruchomienie serwera 1.7.10 na zmodyfikowanym świecie)
2. Test 6-8: Multi-chunk i spirale (testy wydajnościowe i skalowalności)
3. Integracja z głównym projektem konwersji
