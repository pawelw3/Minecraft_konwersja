# Handoff: Przygotowanie Testu CuttableBlocks

## Podsumowanie

Przygotowano świat testowy z 27 blokami ukośnymi (CuttableBlocks) w różnych konfiguracjach.

## Wykonane Kroki

### 1. Kopia mapy testowej ✓
- Skopiowano `lightweigh_map_templates/1710_modded/test_spiral_spawn`
- Do: `headless_server/1.7.10/world_cuttable_test`
- Mapa ma level.dat i jest gotowa do użycia

### 2. Generacja bloków ukośnych ✓
Skrypt `generate_cuttable_blocks_patch.py` wygenerował 27 bloków:

**Warstwa 1 (Z=0) - Różne typy cięć:**
- 45° XY - przekątna pozioma
- 45° XZ - przekątna w płaszczyźnie XZ  
- 45° YZ - przekątna w płaszczyźnie YZ
- 60° XYZ - równomiernie ukośna

**Warstwa 2 (Z=5) - Różne tekstury:**
- Stone, Dirt, Oak/Spruce Planks
- Cobblestone, Bricks, Stone Bricks

**Warstwa 3 (Z=10) - Różne kierunki:**
- keep_positive = true/false

**Warstwa 4 (Y=65) - Pionowe cięcia:**
- Vertical X, Vertical Z, Diagonal XZ

**Warstwa 5 (Z=-5) - Zaawansowane kąty:**
- 30° X, 30° Y, Mixed XYZ, Shallow X

**Warstwy Y=62 i Y=66:**
- Różne poziomy wysokości (niebieska/czerwona wełna)

### 3. Wstawienie bloków do mapy ✓
Skrypt `apply_patch_to_world.py` wstawił bloki do 4 chunków:
- Chunk (-1, 0): 10 bloków
- Chunk (0, 0): 13 bloków  
- Chunk (-1, -1): 2 bloki
- Chunk (0, -1): 2 bloki

**Format wstawionych bloków:**
- Block ID: 200 (tymczasowy, mod przypisze właściwy)
- TileEntity "CuttableTE" z polami:
  - OriginalBlockID (int)
  - OriginalMeta (int)
  - NormalX/Y/Z (float)
  - KeepPositive (byte)

### 4. Konfiguracja serwera ✓
- Zmieniono `server.properties`: level-name=world_cuttable_test
- Utworzono skrypty testowe:
  - `test_cuttable.bat` - uruchomienie z modem
  - `test_server.ps1` - test PowerShell
  - `run_test.sh` - test Bash

## Struktura Plików

```
headless_server/1.7.10/
├── world_cuttable_test/          # Świat testowy
│   ├── region/
│   │   └── r.0.0.mca            # Zawiera wstawione bloki
│   ├── level.dat
│   └── ...
├── server.properties             # Ustawiony level-name
└── test_cuttable.bat            # Skrypt uruchomienia

new_mod_trial/
├── generate_cuttable_blocks_patch.py    # Generator patcha
├── apply_patch_to_world.py              # Wstawianie bloków
├── cuttable_test_patch.json            # Patch (lista bloków)
├── cuttable_test_patch_jvm.json        # Patch (grupowany po chunkach)
└── HANDOFF_CUTTABLE_TEST.md            # Ten plik
```

## Uruchomienie Testu

### Wymagania:
1. **Java 8** - ForgeGradle 1.2 wymaga Java 8 (mamy Java 17)
2. **Zbudowany mod** - CuttableBlocks musi być skompilowany

### Kroki:

```powershell
# 1. Zbuduj mod (wymaga Java 8)
cd new_mod_trial
$env:JAVA_HOME = "C:\Program Files\Java\jdk1.8.0_XXX"
.\gradlew.bat build

# 2. Skopiuj mod do serwera
copy build\libs\CuttableBlocks-1.0.0.jar ..\headless_server\1.7.10\mods\

# 3. Uruchom serwer
cd ..\headless_server\1.7.10
.\test_cuttable.bat
```

### Bez zbudowanego moda:
Można przetestować bez moda - bloki będą widoczne jako ID 200 (prawdopodobnie jako "Missing Texture" lub inny blok z ID 200).

## Weryfikacja w Grze

Po uruchomieniu serwera i połączeniu się (localhost):
1. Spawn jest w okolicy (0, 64, 0)
2. Bloki ukośne są w promieniu ~20 bloków od spawnu
3. Współrzędne bloków: X=-7 do 7, Y=62 do 66, Z=-5 do 10
4. Użyj F3 aby zobaczyć informacje o blokach

## Problemy i Ograniczenia

1. **Java 8** - Główny blocker do zbudowania moda
2. **Block ID 200** - Tymczasowy ID, może kolidować z innymi modami
3. **Brak tekstur** - Bez moda bloki nie będą mieć poprawnych tekstur

## Następne Kroki

1. [ ] Zainstalować Java 8 lub użyć istniejącej
2. [ ] Zbudować mod: `cd new_mod_trial && gradlew build`
3. [ ] Skopiować JAR do `headless_server/1.7.10/mods/`
4. [ ] Uruchomić serwer i przetestować
5. [ ] Zweryfikować rendering ukośnych bloków
