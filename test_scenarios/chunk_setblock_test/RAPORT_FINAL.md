# Raport z Testu Setblock - Weryfikacja Spawn Chunks

## Hipoteza

**Setblock działa tylko w załadowanych chunkach, czyli dla pustego świata bez graczy tylko w spawn chunkach i ich okolicach.**

## Wyniki testu

| Parametr | Wartość |
|----------|---------|
| Przetworzone chunki | 2116 |
| Czas testu | 152 sekundy |
| Komend RCON | 2116 (100% sukces połączenia) |
| Wynik pozytywny | 256 (12%) |
| Wynik negatywny | 1860 (88%) |

## Analiza odległości od spawnu

Spawn: chunk (43, -11), pozycja (689, 4, -164)

| Odległość | Chunki | Block Placed | Outside World | % Sukcesu |
|-----------|--------|--------------|---------------|-----------|
| **0-5 chunków** | 81 | **81** | 0 | **100%** |
| **5-10 chunków** | 236 | **170** | 66 | **72%** |
| **10-20 chunków** | 494 | **5** | 489 | **1%** |
| **20-50 chunków** | 924 | **0** | 924 | **0%** |
| **50+ chunków** | 381 | **0** | 381 | **0%** |

## Potwierdzenie hipotezy

### ✅ Hipoteza ZWERYFIKOWANA POZYTYWNIE

1. **Sukcesy koncentracja**: Wszystkie 256 sukcesów w promieniu **11.3 chunków** od spawnu
2. **Zero sukcesów dalej**: Od 20 chunków od spawnu - **0% sukcesów**
3. **Spawn chunks**: Promień ~10-12 chunków wokół spawn point jest zawsze załadowany

### Wyjaśnienie "Outside of the world"

Komenda `/setblock` na niezaładowanych chunkach zwraca:
```
Cannot place block outside of the world
```

To jest **błędna nazwa błędu** - chunki fizycznie istnieją (są w plikach MCA), ale nie są załadowane do pamięci gry. Serwer nie może modyfikować niezaładowanych chunków.

## Mechanizm spawn chunks

W Minecraft 1.7.10:

```
Spawn Point (689, 4, -164)
         │
         ▼
    ┌─────────────┐
    │  SPAWN      │ ← Zawsze załadowane (~10-12 chunk radius)
    │   CHUNKS    │   Nawet bez graczy!
    │   ◉         │
    └─────────────┘
           │
     ┌─────┴─────┐
     │           │
   Dalekie    Dalekie
   chunki     chunki
   (0%)       (0%)
```

## Konsekwencje dla testowania

### Do testowania headless (bez gracza):
- ✅ Testy w spawn chunks (radius ~10-12 chunków)
- ✅ Testy na wcześniej załadowanych chunkach
- ❌ Testy na dowolnych chunkach mapy (nie działają)

### Rozwiązania dla testów na dalekich chunkach:

1. **Forceload** (jeśli dostępne w wersji):
   ```
   /forceload add <x> <z>
   ```

2. **Teleportacja gracza** (symulacja wejścia gracza):
   ```
   /tp @p <x> <y> <z>
   ```
   Po czym wykonanie testu

3. **Pre-generation** (wygenerowanie chunków przed testem):
   Niektóre mody pozwalają na wymuszenie generacji

4. **Ograniczenie testów** do spawn chunks:
   Wstawianie struktur testowych tylko w okolicy spawnu

## Pliki testowe

- `chunk_test_report.json` - Pełne dane (2116 rekordów)
- `test_all_chunks.py` - Skrypt wykonujący test
- `analyze_spawn_distance.py` - Analiza odległości od spawnu

---

*Test wykonano: 2026-01-31*
*Weryfikacja hipotezy: POTWIERDZONA*
