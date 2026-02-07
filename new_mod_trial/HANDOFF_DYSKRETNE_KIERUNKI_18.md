# Handoff: Dyskretne kierunki (18 klas) + naprawa połówek

## Podsumowanie sesji
Wprowadzono system 18 dyskretnych kierunków cięcia oraz naprawiono błędy renderowania "dokładnych połówek" (znikające ściany, zielony tint, czarne miganie).

## Wprowadzone zmiany

### 1. NOWA KLASA: CutDirections.java
**Lokalizacja:** `util/CutDirections.java`

Zawiera:
- **BASE_DIRS_18** - 18 kanonicznych wektorów kierunkowych (int[3])
- **System rotacji (24)** - wszystkie rotacje sześcianu (perm + sign)
- **Aproksymacja kierunku** - znajdowanie najbliższego dirId dla lookVec
- **Klasyfikacja render mode** - deterministyczny wybór axis/advanced

### 2. TileEntityCuttable.java
Zmiany:
- **Nowe pola:** `rotId` (byte), `dirId` (byte) zamiast normalX/Y/Z
- **Rekonstrukcja normalnej** - dynamiczna z (rotId, dirId)
- **NBT:** zapis/odczyt rotId/dirId z kompatybilnością wsteczną

### 3. ItemCuttingTool.java
Zmiany:
- **Aproksymacja** - lookVec → najbliższy dirId przez CutDirections.findBestDirection()
- **Snap16** - zachowany dla anchor (UV origin)
- **PlaneD** - zawsze przez środek (0.5,0.5,0.5)

### 4. AdvancedCutRenderer.java
Kluczowe zmiany:

#### Deterministyczny wybór renderera (zamiast progów float):
```java
CutDirections.RenderMode mode = CutDirections.getRenderMode(rotId, dirId);
switch (mode) {
    case AXIS_Y: RenderHelper.renderHorizontalCut(...); break;
    case AXIS_X: RenderHelper.renderVerticalXCut(...); break;
    case AXIS_Z: RenderHelper.renderVerticalZCut(...); break;
    case ADVANCED: renderDiagonalCut(...); break;
}
```

#### Spójny EPS (1e-6):
- Testy strony płaszczyzny
- Clipping
- Deduplikacja

#### Z-fighting offset:
```java
Vec3 offset = Vec3.createVectorHelper(n.x * Z_FIGHT_OFFSET, ...);
// Dodawany do wierzchołków cut-face
```

#### Brightness + Color:
```java
// Ustawiane PRZED każdą ścianą
tess.setBrightness(brightness);
tess.setColorOpaque_F(1.0f, 1.0f, 1.0f); // Biały, brak tintu
```

### 5. RenderHelper.java
- Metody `renderHorizontalCut`, `renderVerticalXCut`, `renderVerticalZCut` → **public static**

## Dyskretne kierunki (18)

| ID | Wektor | Opis |
|----|--------|------|
| 0 | (-1,0,0) | Oś -X |
| 1 | (-1,-1,0) | Diagonal XY |
| 2 | (-1,-1,-1) | Corner |
| 3-5 | (-2,-1,0)... | Płytkie diagonalne |
| 6-10 | (-4,-1,0)... | Bardzo płytkie |
| 11-17 | (-8,-1,0)... | Prawie płaskie |

## Naprawa błędów połówek

### Przyczyna A: Progi float
**Rozwiązanie:** Deterministyczny wybór na podstawie dirId (isAxisAligned())

### Przyczyna B: Z-fighting
**Rozwiązanie:** Offset 1e-4 wzdłuż normalnej dla cut-face

### Przyczyna C: Brak ścian
**Rozwiązanie:** Ujednolicony EPS, poprawne clipping

### Przyczyna D: Zielony/czarny tint
**Rozwiązanie:** Jawne ustawienie brightness i color (1,1,1) przed każdą ścianą

## Pliki wynikowe

| Plik | Rozmiar | Opis |
|------|---------|------|
| `CuttableBlocks-1.0.0_FIXED.jar` | 45.38 KB | Skompilowany mod |
| `new_mod_trial_all_java_files.txt` | 110.78 KB | Wszystkie źródła |

## Testy

1. **Cięcia osiowe** - powinny używać uproszczonych rendererów (half-blocks)
2. **Cięcia diagonalne** - pełny advanced renderer
3. **Brak zielonego tintu** - wszystkie ściany białe
4. **Brak migania** - stabilne cut-face (offset)
5. **Dyskretność** - tylko 18 możliwych kierunków

## Nowe pliki (17 total):
- `util/CutDirections.java` - NOWY
