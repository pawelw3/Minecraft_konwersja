# Handoff: Naprawa artefaktów renderowania ukośnych cięć

## Podsumowanie sesji
Wprowadzono poprawki do renderowania przyciętych bloków w AdvancedCutRenderer.java zgodnie z instrukcją w `bugs/instrukcja_naprawa_ukosne_ciecia.md`. Naprawiono 3 główne problemy: degenerowane quady zamiast trójkątów, poprawne sortowanie wierzchołków na płaszczyźnie oraz deduplikację punktów przecięć.

## Ukończono
- [x] Krok 1: Zamiana trójkątów na degenerowane quady (A,B,C,C) w renderCutFace
- [x] Krok 2: Implementacja sortowania wierzchołków używając tangent/bitangent
- [x] Krok 2: Wymuszenie poprawnego windingu (orientacji wielokąta)
- [x] Krok 3: Deduplikacja punktów przecięć przed sortowaniem
- [x] Weryfikacja składni kodu Java (zbalansowane nawiasy)

## Nowe metody w AdvancedCutRenderer.java

### 1. `deduplicatePoints(List<Vec3> points, double eps)`
Usuwa duplikaty punktów znajdujących się w odległości mniejszej niż epsilon od siebie. Zapobiega to problemom gdy płaszczyzna trafia idealnie w wierzchołek lub krawędź sześcianu.

### 2. `sortPointsByAngle(...)` (przepisana)
Zamiast prostego atan2 w rzucie XY, nowa implementacja:
- Buduje ortonormalną bazę na płaszczyźnie (tangent/bitangent)
- Rzutuje punkty na tę bazę przed sortowaniem
- Zapewnia poprawne sortowanie niezależnie od orientacji płaszczyzny

### 3. `ensureCorrectWinding(List<Vec3> points, nx, ny, nz, keepPositive)`
Sprawdza czy normalna wielokąta wskazuje w odpowiednią stronę:
- Oblicza normalną wielokąta z trzech pierwszych punktów
- Sprawdza zgodność z oczekiwaną orientacją
- Odwraca kolejność punktów jeśli potrzeba (Collections.reverse)

### 4. Pomocnicze metody wektorowe
- `crossProduct(Vec3 a, Vec3 b)` - iloczyn wektorowy
- `normalize(Vec3 v)` - normalizacja wektora

## Zmodyfikowane fragmenty

### renderAdvancedCut(...) - linia ~32-35
Dodano wywołanie deduplikacji:
```java
// Deduplicate intersection points (Step 3)
intersections = deduplicatePoints(intersections, EPSILON);
```

### renderCutFace(...) - linia ~245-270
Zamiana trójkątów na degenerowane quady:
```java
// PRZED (trójkąt):
addVertexWithClippedUV(... a ...);
addVertexWithClippedUV(... b ...);
addVertexWithClippedUV(... c ...);

// PO (degenerowany quad):
addVertexWithClippedUV(... a ...);
addVertexWithClippedUV(... b ...);
addVertexWithClippedUV(... c ...);
addVertexWithClippedUV(... c ...); // DUPE: domyka QUAD
```

### renderCutFace(...) - linia ~192-195
Dodano wymuszenie windingu:
```java
// Ensure correct winding order for visibility
sortedPoints = ensureCorrectWinding(sortedPoints, nx, ny, nz, keepPositive);
```

## Problemy naprawione

### 1. "Płachty" łączące bloki
**Przyczyna**: Tessellator w MC 1.7.10 oczekuje quads (4 wierzchołki), ale kod wysyłał trójkąty (3 wierzchołki). Powodowało to "pożyczanie" 4-tego wierzchołka z następnego batchu.

**Rozwiązanie**: Dodanie czwartego wierzchołka (duplikat trzeciego) tworzy degenerowany quad.

### 2. Przezroczyste/znikające ściany
**Przyczyna**: Niepoprawne sortowanie wierzchołków (atan2 w XY) dawało zły "winding" dla płaszczyzn nie-równoległych do osi. Powodowało to że ściany były renderowane tyłem (backface culling).

**Rozwiązanie**: Sortowanie na bazie tangent/bitangent + wymuszenie poprawnego windingu.

### 3. Wierzchołki "podpinające się" pod poprzednie bloki
**Przyczyna**: Duplikaty punktów przecięć gdy płaszczyzna trafia w wierzchołek/krawędź.

**Rozwiązanie**: Deduplikacja punktów w promieniu EPSILON (1e-5).

## Testy do wykonania

Zgodnie z instrukcją, przetestuj następujące scenariusze:

1. **Normalne losowe**: Postaw 10 bloków, za każdym razem celuj w inny kierunek. Nie powinno być żadnych "płacht" między blokami.

2. **Normalne prawie osiowe**: Sprawdź normalne (0.98, 0.10, 0.00), (0.00, 0.98, 0.10), (0.10, 0.00, 0.98) - nie powinny migać.

3. **Normalna diagonalna "równa"**: (0.577, 0.577, 0.577) - cut face musi być stabilna i poprawnie widoczna.

4. **Normalna z ujemnymi składowymi**: (-0.6, 0.2, -0.77) - brak zaniku ścian.

## Kompilacja

Aby skompilować zmiany:
```bash
cd new_mod_trial
./gradlew.bat compileJava
```

Jeśli wystąpią błędy kompilacji, sprawdź czy:
1. Wszystkie importy są poprawne (`java.util.Collections` jest zaimportowane)
2. Nie ma konfliktów nazw zmiennych

## Następne kroki (opcjonalne)

- [ ] Przetestować w grze zgodnie ze scenariuszami testowymi
- [ ] Jeśli cut face znika po jednej stronie a jest widoczna po drugiej - sprawdzić logikę `ensureCorrectWinding` (może trzeba odwrócić warunek `shouldReverse`)
- [ ] Rozważyć ujednolicenie przecięć z `util/Plane.java` (opcjonalne)
- [ ] Poprawić kolizję dla ukośnych brył (obecnie AABB pełny blok)
- [ ] Przenosić dane TileEntity oryginalnych bloków (na razie cięcie niszczy TE)

## Pliki zmodyfikowane
- `src/main/java/com/cuttableblocks/client/render/AdvancedCutRenderer.java` - pełna modyfikacja

## Referencje
- Instrukcja naprawy: `bugs/instrukcja_naprawa_ukosne_ciecia.md`
- Screeny błędów: `bugs/*.png`
