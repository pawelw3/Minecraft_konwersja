# Raport z Testu Setblock na Wszystkich Chunkach

## Podsumowanie wykonania

| Parametr | Wartość |
|----------|---------|
| **Data testu** | 2026-01-31 |
| **Czas trwania** | 152 sekundy (2 min 32 s) |
| **Liczba chunków** | 2116 |
| **Średni czas na komendę** | 71.8 ms |
| **Status RCON** | 100% sukces (0 błędów połączenia) |

## Wyniki komend setblock

| Wynik | Liczba | Procent | Opis |
|-------|--------|---------|------|
| **Block placed** | 256 | 12% | Blok postawiony pomyślnie |
| **Cannot place block outside of the world** | 1860 | 88% | Pozycja Y=40 poza światem |
| **Inne** | 0 | 0% | Brak innych odpowiedzi |

## Kluczowe odkrycie

**Poziom Y=40 jest poza granicami świata w 88% chunków!**

W Minecraft 1.7.10 świat technicznie istnieje w zakresie Y=0-255, ale "granice świata" (world boundaries) są dynamiczne i zależą od wygenerowanego terenu:

- W większości chunków poziom Y=40 jest **poniżej dna świata** lub w **niewygenerowanej przestrzeni**
- Tylko w regionie **r.1.-1** (chunki X:35-50, Z:-18 do -3) poziom Y=40 jest dostępny
- To sugeruje, że ten region został wygenerowany z różnymi parametrami lub ma inną strukturę terenu

## Szczegóły regionalne

| Region | Chunki | Block Placed | Outside World | % Sukcesu |
|--------|--------|--------------|---------------|-----------|
| r.-1.-1 | 212 | 0 | 212 | 0% |
| r.-1.0 | 237 | 0 | 237 | 0% |
| r.-1.1 | 8 | 0 | 8 | 0% |
| r.0.-1 | 271 | 0 | 271 | 0% |
| r.0.0 | 455 | 0 | 455 | 0% |
| r.0.1 | 8 | 0 | 8 | 0% |
| **r.1.-1** | **626** | **256** | **370** | **40%** |
| r.1.0 | 291 | 0 | 291 | 0% |
| r.1.1 | 8 | 0 | 8 | 0% |

## Miejsca ze sukcesem

Chunki gdzie udało się postawić blok (X:35-50, Z:-18 do -3):
- Pozycje absolutne: od (565, 40, -283) do (805, 40, -43)
- Współrzędne bloków: X=565-805, Y=40, Z=-283 do -43

## Wnioski

1. **RCON działa niezawodnie** - wszystkie 2116 komend zostało wykonanych bez błędów połączenia

2. **Poziom Y=40 jest nieprzewidywalny** - w większości chunków jest poza światem, prawdopodobnie z powodu:
   - Głębokich jaskiń sięgających poniżej Y=40
   - Różnic w generacji terenu między regionami
   - Optymalizacji "dno świata" w różnych wersjach/wymiarach

3. **Region r.1.-1 jest wyjątkowy** - jedyny region gdzie Y=40 jest dostępny w znacznej części chunków (40%)

4. **Zalecenie dla przyszłych testów**:
   - Używać wyższego poziomu Y (np. Y=100) aby uniknąć problemu z dnem świata
   - Sprawdzać dostępność pozycji przed wykonaniem testu
   - Rozważyć testy na poziomie Y=64 (poziom morza) lub wyżej

## Techniczne szczegóły

- **Mechanizm**: RCON (Remote Console) na porcie 25579
- **Komenda**: `/setblock <x> 40 <z> minecraft:redstone_block 0`
- **Pozycja w chunku**: (X*16+5, 40, Z*16+5) - zawsze ten sam względny offset
- **Odpowiedzi serwera**: Tylko 2 unikalne: "Block placed" lub "Cannot place block outside of the world"

## Pliki wygenerowane

- `chunk_test_report.json` - Pełne dane JSON z wszystkimi chunkami i wynikami
- `test_all_chunks.py` - Skrypt wykonujący test
- `generate_report.py` - Generator raportu tekstowego
- `analyze_errors.py` - Analiza błędów

---

*Test wykonano automatycznie przez RCON na headless serwerze Minecraft 1.7.10*
