# Aktualizacja Zadania 1 - BiblioCraft

## Data aktualizacji: 2026-02-02

---

## Wprowadzone zmiany

### 1. System druku książek (Typesetting + Printing Press)
**Decyzja:** Funkcjonalność **NIEISTOTNA** - nie wymaga konwersji.

**Konsekwencje:**
- Bloki Typesetting Table i Printing Press mogą być usunięte lub zastąpione dekoracyjnie
- Brak konieczności szukania zamiennika funkcjonalnego

---

### 2. Furniture Paneler / Zmiana tekstury mebli
**Rozwiązanie:** Dwa mody do wyboru:

#### Opcja A: FramedBlocks (XFactHD)
- **Repozytorium:** https://github.com/XFactHD/FramedBlocks
- **Klon:** `mod_src/actual_src/1.18.2/FramedBlocks/`
- **Licencja:** LGPL
- **Funkcja:** Bloki wielu kształtów przyjmujące teksturę innego bloku ("camo")
- **Ilość kształtów:** 100+ (schody, płyty, drzwi, skosy, itp.)

**Konwersja:**
```java
BiblioCraft 1.7.10:
- TileEntityFramedChest: frameTexture (String ID bloku)

FramedBlocks 1.18.2:
- FramedBlockEntity: camoState (BlockState jako tekstura)
```

#### Opcja B: BlockCarpentry (PianoManu)
- **Repozytorium:** https://github.com/PianoManu/BlockCarpentry
- **Klon:** `mod_src/actual_src/1.18.2/BlockCarpentry/`
- **Funkcja:** "Coverable blocks" - bloki zawierające inny blok w środku

**Różnica:**
- FramedBlocks: blok "udaje" teksturę (camo)
- BlockCarpentry: blok "zawiera" inny blok (jakby w środku)

**Rekomendacja:** Użyć FramedBlocks jako głównego rozwiązania (więcej kształtów, lepsza dokumentacja).

---

### 3. Custom Paintings
**Rozwiązanie:** Immersive Paintings (Luke100000)

- **Repozytorium:** https://github.com/Luke100000/ImmersivePaintings
- **Klon:** `mod_src/actual_src/1.18.2/ImmersivePaintings/`
- **Licencja:** GPL-3.0
- **Funkcja:** Customowe obrazy wczytywane z plików (drag & drop)

**Funkcje:**
- Wczytywanie obrazów z plików
- Drag & drop do gry
- Działa w multiplayer
- Różne rozmiary (1×1 do 8×8 bloków)
- Filtry (sepia, grayscale)

**Konwersja:**
```java
BiblioCraft 1.7.10:
- TileEntityPainting: resourceLocation (String "bibliocraft:paintings/custom/xxx.png")

ImmersivePaintings 1.18.2:
- PaintingEntity: image (String - nazwa zarejestrowanego obrazu)
- width/height: int (rozmiar w blokach)
```

---

## Zaktualizowane pliki

| Plik | Zmiany |
|------|--------|
| `HANDOFF_BIBLIO_ZADANIE1.md` | Aktualizacja statusu problemów, nowe repozytoria |
| `docs/mod_mapping_indepth/to/bibliocraft_1182_mapowanie.md` | Szczegółowe mapowanie na FramedBlocks/BlockCarpentry/ImmersivePaintings |
| `docs/LISTA_KONWERSJI_MODOW.md` | Aktualizacja listy modów docelowych |

## Nowe repozytoria kodów źródłowych

```
mod_src/actual_src/1.18.2/
├── Supplementaries/       # (było) Półki, latarnie, globusy
├── FramedBlocks/          # (nowe) Meble z teksturami
├── BlockCarpentry/        # (nowe) Alternatywa dla FramedBlocks
└── ImmersivePaintings/    # (nowe) Customowe obrazy
```

---

## Podsumowanie statusu konwersji Bibliocraft

| Element | Status | Rozwiązanie |
|---------|--------|-------------|
| Półki meblowe | ✅ | Supplementaries (Item Shelf) |
| Regały na książki | ✅ | Supplementaries (Book Pile) |
| Latarnie/Lampy | ✅ | Supplementaries (Wall Lantern/End Lamp) |
| Zegar | ✅ | Supplementaries (Clock Block) |
| Znaki | ✅ | Supplementaries (Hanging Sign) |
| Meble z teksturami | ✅ | FramedBlocks / BlockCarpentry |
| Customowe obrazy | ✅ | Immersive Paintings |
| Typesetting/Printing | ✅ | NIEISTOTNE (nie trzeba konwertować) |
| Atlas/Tape Measure | ⚠️ | Częściowa utrata (alternatywy: JourneyMap) |
| Armor Stand | ⚠️ | Vanilla / Supplementaries Statue |
| Writing Desk | ❌ | Brak odpowiednika (funkcja tracona) |

**Podsumowanie:** 
- Funkcjonalność Furniture Paneler **ZACHOWANA** (FramedBlocks)
- Funkcjonalność Custom Paintings **ZACHOWANA** (Immersive Paintings)
- System druku książek **NIE WYMAGA** konwersji
- Tylko ~15% funkcjonalności rzeczywiście tracona

---

## Następne kroki (Zadanie 2)

1. **Symulacje działania:**
   - FramedBlocks (camo system)
   - Immersive Paintings (ładowanie obrazów)

2. **Konwertery NBT:**
   - `frameTexture` → `camoState`
   - Ścieżki obrazów BC → format Immersive Paintings

3. **Mapowanie kształtów:**
   - Meble BC → odpowiednie kształty FramedBlocks
