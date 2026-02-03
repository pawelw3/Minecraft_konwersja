# Instrukcja naprawy zadania 5 dla Enchanting Plus

## Problem

Zadanie 5 zostało wykonane **niekompletnie**. Konwersja wygenerowała tylko raporty JSON, ale **NIE zapisała rzeczywistych plików regionów .mca w formacie 1.18.2**.

### Co jest źle:

```
lightweigh_map_templates/1710_modded/ep_test_world_converted/
├── conversion_report.html    ← TYLKO RAPORT
├── conversion_report.md      ← TYLKO RAPORT
├── conversion_result.json    ← TYLKO JSON Z WYNIKAMI
├── conversion_stats.json     ← TYLKO STATYSTYKI
└── converted_blocks.json     ← TYLKO LISTA BLOKÓW
❌ BRAK: region/r.0.0.mca     ← NIE MA PLIKÓW REGIONÓW 1.18.2!
```

### Co powinno być:

```
lightweigh_map_templates/1182_modded/ep_test_world/
├── region/
│   └── r.0.0.mca             ← PLIK REGIONU W FORMACIE 1.18.2
├── level.dat                 ← DANE ŚWIATA 1.18.2
├── conversion_metadata.json  ← METADANE KONWERSJI
└── (opcjonalnie raporty)
```

---

## Wymagania do poprawy

### 1. Stworzenie mapy 1.18.2 z przekonwertowanymi blokami

**Cel:** Folder `lightweigh_map_templates/1182_modded/ep_test_world/` musi zawierać kompletną mapę 1.18.2, którą można skopiować do `headless_server/1.18.2/world/` i uruchomić.

### 2. Wymagane bloki na mapie 1.18.2

Na podstawie wyników konwersji z `converted_blocks.json`:

| Pozycja (X, Y, Z) | Blok 1.18.2 | NBT |
|-------------------|-------------|-----|
| (2, 64, 2) | `enchantinginfuser:enchanting_infuser` | {} |
| (4, 64, 2) | `enchantinginfuser:enchanting_infuser` | lastPlayer: "TestPlayer" |
| (6, 64, 2) | `enchantinginfuser:enchanting_infuser` | {} |
| (2, 64, 5) | `enchantinginfuser:advanced_enchanting_infuser` | {} |
| (4, 64, 5) | `enchantinginfuser:advanced_enchanting_infuser` | repairCost: 15 |
| (6, 64, 5) | `enchantinginfuser:advanced_enchanting_infuser` | {} |
| (10, 64, 2) | `enchantinginfuser:enchanting_infuser` | {} |
| (11, 64, 2) | `enchantinginfuser:advanced_enchanting_infuser` | {} |
| (2, 64, 8) | `minecraft:air` | (usunięty arcane_inscriber) |
| (4, 64, 8) | `minecraft:air` | (usunięty arcane_inscriber) |
| (6, 64, 8) | `minecraft:air` | (usunięty arcane_inscriber) |
| (12, 64, 2) | `minecraft:air` | (usunięty arcane_inscriber) |

Plus platforma ze stone pod blokami (na Y=63).

### 3. Wymagane zależności na serwerze 1.18.2

Przed testem na serwerze, muszą być dodane mody:
- **Enchanting Infuser** (min. 3.3.3 dla 1.18.2 Forge)
- **Puzzles Lib** (wymagana zależność)

Sprawdzić: `headless_server/1.18.2/mods/` - czy zawiera te mody.

---

## Proponowane rozwiązania

### Opcja A: Użycie Kotlin/Hephaistos do zapisu 1.18.2 (ZALECANE)

Rozszerz skill `skills/mca-sections` o obsługę formatu 1.18.2, lub stwórz nowy worker:

```kotlin
// jvm/worker - dodać obsługę formatu 1.18.2
// Format 1.18.2 używa palette + block_states zamiast Blocks/Data/AddBlocks
```

**Kroki:**
1. Odczytaj `converted_blocks.json` z wynikami konwersji
2. Dla każdego bloku stwórz wpis w formacie 1.18.2 (palette-based)
3. Zapisz do pliku `r.0.0.mca` używając Hephaistos

### Opcja B: Użycie RCON do wstawienia bloków na działający serwer

1. Uruchom serwer 1.18.2 z pustym światem
2. Wstaw bloki via RCON `/setblock`
3. Zapisz świat (`/save-all`)
4. Skopiuj wynikowy świat jako mapę testową

**Skrypt Python:**
```python
# Odczytaj converted_blocks.json
# Dla każdego bloku wykonaj: rcon.send(f"setblock {x} {y} {z} {block_id}")
```

### Opcja C: Wykorzystanie oficjalnego konwertera Mojang

1. Skopiuj mapę 1.7.10 do klienta Minecraft 1.18.2
2. Otwórz świat - Minecraft automatycznie przekonwertuje format
3. Wejdź do gry i ręcznie zamień bloki EP na EnchantingInfuser
4. Zapisz i skopiuj jako mapę testową

---

## Co musi dostarczyć poprawione zadanie 5

### Artefakty wynikowe:

1. **Mapa testowa 1.18.2:**
   ```
   lightweigh_map_templates/1182_modded/ep_test_world/
   ├── region/
   │   └── r.0.0.mca
   ├── level.dat
   └── DIM1/, DIM-1/ (opcjonalne)
   ```

2. **Mody do serwera (jeśli nie ma):**
   ```
   headless_server/1.18.2/mods/
   ├── enchantinginfuser-forge-1.18.2-X.X.X.jar
   └── puzzleslib-forge-1.18.2-X.X.X.jar
   ```

3. **Zaktualizowany HANDOFF_ENCHANTINGPLUS_TASK5.md:**
   - Potwierdzenie że mapa 1.18.2 została utworzona
   - Ścieżka do mapy
   - Instrukcja kopiowania na serwer

### Weryfikacja poprawności:

1. Skopiuj mapę do `headless_server/1.18.2/world/`
2. Uruchom serwer
3. Sprawdź logi - brak błędów "missing block"
4. Bloki EnchantingInfuser powinny być widoczne w grze

---

## Dlaczego to ważne dla zadania 6

Zadanie 6 wymaga:
> "Zrobienie testu na headless serwer z **przekonwertowaną mapą**"

Bez rzeczywistej mapy 1.18.2 z blokami EnchantingInfuser, zadanie 6 nie może być wykonane poprawnie.

---

## Kontekst techniczny

### Format chunków 1.7.10 vs 1.18.2:

**1.7.10 (legacy):**
```
Level/Sections/[]/Blocks: ByteArray(4096)  - block IDs
Level/Sections/[]/Data: ByteArray(2048)    - metadata nibbles
Level/TileEntities: List of compounds
```

**1.18.2 (modern):**
```
sections/[]/block_states/palette: List of block state compounds
sections/[]/block_states/data: LongArray (packed indices)
block_entities: List of compounds with different format
```

### Biblioteka do zapisu 1.18.2:
- **Hephaistos** (Kotlin) - obsługuje oba formaty
- Sprawdź: `jvm/hephaistos-src/` czy jest aktualna wersja

---

*Instrukcja przygotowana: 2026-02-03*
*Dla: Agent wykonujący naprawę zadania 5 Enchanting Plus*
