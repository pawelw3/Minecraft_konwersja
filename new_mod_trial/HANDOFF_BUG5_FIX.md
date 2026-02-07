# Handoff: Naprawa błędu #5 - Kamera, dyskretne kierunki, połówki i UV

## Podsumowanie sesji

Wprowadzono kompleksową naprawę modu CuttableBlocks zgodnie z instrukcją w `bugs/5/instrukcja_fix_kamera_dyskretne_kierunki_polowki_uv.md`. Głównym celem było usunięcie zależności geometrii/UV od punktu kliknięcia (hitX/hitY/hitZ) i zastąpienie jej deterministyczną logiką opartą wyłącznie na kierunku patrzenia gracza.

---

## Ukończono

### A. ItemCuttingTool.java
- [x] Usunięto metodę `snap16()` i całą logikę związaną z `anchorX/Y/Z`
- [x] `dirId` obliczane wyłącznie na podstawie `player.getLookVec()` (po dyskretyzacji)
- [x] Płaszczyzna cięcia **zawsze** przechodzi przez środek bloku `(0.5, 0.5, 0.5)`
- [x] `keepPositive` obliczane deterministycznie: zachowaj stronę bliżej kamery gracza
- [x] Usunięto przekazywanie anchor do TileEntity

### B. TileEntityCuttable.java  
- [x] Uproszczony kontrakt `setCutData()` - bez anchor/hitpoint
- [x] Dodano metodę `getCenter()` zwracającą środek bloku w koordynatach świata
- [x] Anchor pozostawiony w NBT tylko dla backward compatibility
- [x] Dodano komentarze wyjaśniające, że anchor nie wpływa na geometrię

### C. AdvancedCutRenderer.java
- [x] Wprowadzono stałą `EPSILON = 1e-6` dla stabilnych porównań
- [x] Zmieniono logikę `keepSide()` - używa EPS zamiast ostrych `>0/<0`
- [x] Poprawiono UV dla cut-face:
  - Origin UV = zawsze środek bloku `(0.5, 0.5, 0.5)`
  - World-space tangent/bitangent basis
  - Tiling z wrap16 dla większych ścian
  - Atlas bleeding fix (inset 0.5 texela)
- [x] Zmieniono renderowanie na proper `GL_TRIANGLES` (fan trójkątów)
- [x] Usunięto "triangle as quad (A,B,C,C)" - teraz są to prawidłowe trójkąty
- [x] Poprawiono UV dla ścian bocznych - używają world-space coordinates

### D. RenderHelper.java
- [x] Dodano stałą `EPSILON = 1e-6`
- [x] Zaktualizowano porównania osiowe do używania EPS
- [x] Tekstury na ścianach bocznych są "clipped" nie rozciągnięte
- [x] Spójność z AdvancedCutRenderer

### E. Usunięto stare renderery
- [x] Usunięto `TextureMapper.java` (nieużywany)
- [x] Usunięto `CutFaceRenderer.java` (nieużywany)

---

## Zmodyfikowane pliki

| Plik | Zmiany |
|------|--------|
| `src/main/java/com/cuttableblocks/items/ItemCuttingTool.java` | Usunięto anchor/hitpoint, deterministyczny `keepPositive` |
| `src/main/java/com/cuttableblocks/tileentities/TileEntityCuttable.java` | Uproszczony kontrakt, anchor tylko dla backward compat |
| `src/main/java/com/cuttableblocks/client/render/AdvancedCutRenderer.java` | EPS, poprawne UV z origin=center, GL_TRIANGLES, atlas bleeding fix |
| `src/main/java/com/cuttableblocks/client/render/RenderHelper.java` | EPS, poprawne UV ścian bocznych |

## Usunięte pliki

| Plik | Powód |
|------|-------|
| `src/main/java/com/cuttableblocks/client/render/TextureMapper.java` | Nie używany, kolidował z nowym systemem UV |
| `src/main/java/com/cuttableblocks/client/render/CutFaceRenderer.java` | Nie używany, kolidował z nowym systemem UV |

---

## Kontrakt po zmianach (sekcja J z instrukcji)

✅ `dirId` zależy **tylko** od `playerLookVec`  
✅ Płaszczyzna zawsze przechodzi przez `center`  
✅ `keepPositive` zależy **tylko** od położenia kamery względem `center` i `n`  
✅ UV cut-face liczone z projekcji na (tangent, bitangent) i *wrap 16*  
✅ Żadna część geometrii/UV nie zależy od `hitX/hitY/hitZ`  
✅ Żadnych ostrych `>0/<0` bez EPS  
✅ Żadnych "triangle as quad (A,B,C,C)"  

---

## Następne kroki / Testowanie

1. **Test determinizmu**: Kliknij w ten sam blok kilka razy z różnych stron/rogów przy stałym kącie patrzenia → wynik powinien być identyczny

2. **Test połówek**: Sprawdź cięcia dokładnie osiowe (lookDir ≈ (0,1,0), (1,0,0), (0,0,1)):
   - Bryła powinna być zamknięta (brak dziur)
   - Brak migotania/czernienia

3. **Test tekstur**: Sprawdź cegły na ścianie cięcia:
   - Skala powinna być stała (jak na ścianie bocznej)
   - Wzór powinien się powtarzać na dłuższych przekątnych
   - Brak zielonych/losowych przebarwień (atlas bleeding)

4. **Test spójności**: Sąsiednie bloki przycięte tym samym kierunkiem powinny mieć spójne tekstury

---

## Budowa i instalacja

```bash
cd new_mod_trial
./gradlew build
```

Wynikowy JAR: `build/libs/CuttableBlocks-1.0.0.jar`

---

*Zmiany wdrożone zgodnie z instrukcją: `bugs/5/instrukcja_fix_kamera_dyskretne_kierunki_polowki_uv.md`*
