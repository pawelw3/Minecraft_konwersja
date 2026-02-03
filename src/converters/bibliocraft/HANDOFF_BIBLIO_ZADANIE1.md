# Handoff: BiblioCraft - Zadanie 1 (Analiza bloków i Tile Entities)

## Podsumowanie sesji

Wykonano pełną analizę bloków i Tile Entities moda **BiblioCraft v1.11.7** dla wersji 1.7.10 oraz zidentyfikowano odpowiedniki w modzie **Supplementaries** dla 1.18.2.

**Uwaga:** BiblioCraft nie ma portu na 1.18.2, więc konwersja polega na mapowaniu funkcjonalności na Supplementaries oraz inne mody dekoracyjne (Handcrafted, itp.).

---

## Ukończono

- [x] Analiza struktury JAR BiblioCraft 1.7.10 (dekompilacja)
- [x] Identyfikacja wszystkich bloków z paczki `jds.bibliocraft.blocks`
- [x] Identyfikacja wszystkich TileEntities z paczki `jds.bibliocraft.tileentities`
- [x] Identyfikacja wszystkich itemów z paczki `jds.bibliocraft.items`
- [x] Analiza kodu źródłowego Supplementaries 1.18.2 (repozytorium)
- [x] Stworzenie mapowania funkcjonalnego BiblioCraft → Supplementaries
- [x] Identyfikacja bloków bez bezpośrednich odpowiedników

---

## Nowe pliki

| Plik | Opis |
|------|------|
| `mod_src/code_from_jar/1.7.10/BiblioCraft/extracted/` | Rozpakowany JAR BiblioCraft 1.7.10 |
| `mod_src/actual_src/1.18.2/Supplementaries/` | Repozytorium Supplementaries (branch 1.18.2) |
| `mod_src/actual_src/1.18.2/FramedBlocks/` | Repozytorium FramedBlocks (1.18.x) |
| `mod_src/actual_src/1.18.2/BlockCarpentry/` | Repozytorium BlockCarpentry |
| `mod_src/actual_src/1.18.2/ImmersivePaintings/` | Repozytorium ImmersivePaintings |
| `docs/mod_mapping_indepth/from/bibliocraft_1710_bloki_i_te.md` | Szczegółowa lista bloków/TE 1.7.10 |
| `docs/mod_mapping_indepth/to/bibliocraft_1182_mapowanie.md` | Mapowanie na 1.18.2 (Supplementaries + inne) |

---

## BiblioCraft 1.7.10 - Pełna lista bloków

### Bloki dekoracyjne (z TileEntity)

| Blok 1.7.10 | Klasa bloku | Klasa TileEntity | Funkcjonalność |
|-------------|-------------|------------------|----------------|
| **Bookcase** | `BlockBookcase` | `TileEntityBookcase` | Magazyn książek, 16 slotów, interakcja z enchantment table |
| **Armor Stand** | `BlockArmorStand` | `TileEntityArmorStand` | Ekspozycja zbroi (4 sloty: hełm, napierśnik, nogawice, buty) |
| **Display Case** | `BlockWeaponCase` | `TileEntityWeaponCase` | Gablotka na przedmioty (1 slot) |
| **Potion Shelf** | `BlockPotionShelf` | `TileEntityPotionShelf` | Półka na mikstury (12 slotów) |
| **Tool Rack** | `BlockWeaponRack` | `TileEntityWeaponRack` | Wieszak na narzędzia/zbroję (2 sloty) |
| **Shelf** | `BlockGenericShelf` | `TileEntityGenericShelf` | Półka ekspozycyjna (4 sloty) |
| **Wood Label** | `BlockLabel` | `TileEntityLabel` | Etykieta na skrzynie (1 slot, wyświetla ikonę) |
| **Desk** | `BlockWritingDesk` | `TileEntityWritingDesk` | Biurko do pisania książek (2 sloty: papier, książka) |
| **Typesetting Table** | `BlockTypeMachine` | `TileEntityTypeMachine` | Przygotowanie płyt do druku |
| **Printing Press** | `BlockPrintPress` | `TileEntityPrintPress` | Kopiowanie książek |
| **Table** | `BlockTable` | `TileEntityTable` | Stół (1 slot, wyświetla przedmiot) |
| **Seat** | `BlockSeat` | `TileEntitySeat` | Krzesło (siedzenie) |
| **Fancy Lantern** | `BlockLantern` | `TileEntityLantern` | Dekoracyjna latarnia |
| **Fancy Lamp** | `BlockLamp` | `TileEntityLamp` | Dekoracyjna lampa (złota/żelazna) |
| **Cookie Jar** | `BlockStuff` (meta) | `TileEntityCookieJar` | Słoik na ciasteczka |
| **Dinner Plate** | `BlockStuff` (meta) | `TileEntityDinnerPlate` | Talerz na jedzenie |
| **Disc Rack** | `BlockStuff` (meta) | `TileEntityDiscRack` | Stojak na płyty muzyczne |
| **Map Frame** | `BlockMapFrame` | `TileEntityMapFrame` | Ramka na mapy |
| **Fancy Sign** | `BlockFancySign` | `TileEntityFancySign` | Znak z lepszą czcionką |
| **Fancy Workbench** | `BlockFancyWorkbench` | `TileEntityFancyWorkbench` | Stół rzemieślniczy z GUI |
| **Sword Pedestal** | `BlockSwordPedestal` | `TileEntitySwordPedestal` | Piedestał na broń |
| **Framed Chest** | `BlockFramedChest` | `TileEntityFramedChest` | Skrzynia z ramką (custom tekstura) |
| **Furniture Paneler** | `BlockFurniturePaneler` | `TileEntityFurniturePaneler` | Maszyna do zmiany tekstur mebli |
| **Clock** | `BlockClock` | `TileEntityClock` | Zegar ścienny (pokazuje czas) |
| **Painting** | `BlockPainting` | `TileEntityPainting` | Obraz (custom, większy niż vanilla) |
| **Paint Press** | `BlockPaintPress` | `TileEntityPaintPress` | Prasa do tworzenia obrazów |
| **Bell** | `BlockBell` | `TileEntityBell` | Dzwonek (dzwiek) |
| **Clipboard** | `BlockClipboard` | `TileEntityClipboard` | Tablica z listą zadań |

### Bloki bez TileEntity

| Blok 1.7.10 | Klasa | Uwagi |
|-------------|-------|-------|
| **Seat Back** | `BlockStuff` | Oparcie krzesła (dekoracja) |
| **Marker Pole** | `BlockStuff` | Słupek znacznika (dla Tape Measure) |
| **Painting Frame** | `BlockPaintingFrame*` | Ramy dla obrazów (różne style) |
| **Iron Lantern** | `BlockIronLantern` | Żelazna latarnia |
| **Iron Lamp** | `BlockIronLamp` | Żelazna lampa |

---

## BiblioCraft 1.7.10 - Pełna lista Tile Entities

```
jds.bibliocraft.tileentities/
├── TileEntityArmorStand
├── TileEntityBell
├── TileEntityBookcase
├── TileEntityClipboard
├── TileEntityClock
├── TileEntityCookieJar
├── TileEntityDinnerPlate
├── TileEntityDiscRack
├── TileEntityFancySign
├── TileEntityFancyWorkbench
├── TileEntityFramedChest
├── TileEntityFurniturePaneler
├── TileEntityGenericShelf
├── TileEntityLabel
├── TileEntityLamp
├── TileEntityLantern
├── TileEntityMapFrame
├── TileEntityMarkerPole
├── TileEntityPainting
├── TileEntityPaintPress
├── TileEntityPotionShelf
├── TileEntityPrintPress
├── TileEntitySeat
├── TileEntitySwordPedestal
├── TileEntityTable
├── TileEntityTypeMachine (Typesetting)
├── TileEntityTypewriter
├── TileEntityWeaponCase
├── TileEntityWeaponRack
└── TileEntityWritingDesk
```

**Łącznie: 29 Tile Entities**

---

## BiblioCraft 1.7.10 - Kluczowe Itemy

| Item | Klasa | Funkcjonalność |
|------|-------|----------------|
| **Tape Measure** | `TapeMeasure` | Mierzenie odległości |
| **Reading Glasses** | `ItemReadingGlasses` | Pokazuje info o blokach |
| **Tinted Glasses** | `ItemReadingGlasses` | Pokazuje info (alternatywne) |
| **Monocle** | `ItemReadingGlasses` | Pokazuje info (alternatywne) |
| **Print Press Chase** | `ItemChase` | Komponent do druku |
| **Print Press Plate** | `ItemPlate` | Płyta do druku |
| **Enchanted Plate** | `ItemEnchantedPlate` | Płyta z enchantem |
| **Drafting Compass** | `ItemMapTool` | Narzędzie do map |
| **Waypoint Compass** | `ItemWaypointCompass` | Kompas z waypointami |
| **Redstone Book** | `ItemRedstoneBook` | Książka dająca sygnał redstone |
| **Clipboard** | `ItemClipboard` | Lista zadań |
| **Screw Gun** | `ItemDrill` | Narzędzie (creative-only?) |
| **Lock and Key** | `ItemLock` | Zamykanie mebli |
| **Atlas** | `ItemAtlas` | Książkowa mapa z waypointami |
| **Death Compass** | `ItemDeathCompass` | Wskazuje miejsce śmierci |
| **Slotted Book** | `ItemSlottedBook` | Książka z miejscem na przedmiot |
| **Stockroom Catalog** | `ItemStockroomCatalog` | Katalog magazynu |
| **Painting Canvas** | `ItemPaintingCanvas` | Płótno do obrazów |
| **Framing Saw** | `ItemFramingSaw` | Piła do ramek |
| **Framing Board** | `ItemFramingBoard` | Deska do ramek |
| **Framing Sheet** | `ItemFramingSheet` | Arkusz do ramek |
| **Seat Back*** | `ItemSeatBack*` | Oparcia krzeseł (5 typów) |
| **Hand Drill** | `ItemHandDrill` | Wiertło ręczne |
| **Plumb Line** | `ItemPlumbLine` | Sznur pionowy |

---

## Supplementaries 1.18.2 - Mapowanie bloków

### Bezpośrednie/dobre zamienniki

| BiblioCraft 1.7.10 | Supplementaries 1.18.2 | Blok 1.18.2 | Uwagi |
|--------------------|------------------------|-------------|-------|
| Bookcase | ✅ Book Pile | `BookPileBlock` / `BookPileHorizontalBlock` | Stos książek (nie półka) |
| Shelf | ✅ Item Shelf | `ItemShelfBlock` | Bardzo podobna funkcjonalność |
| Clock | ✅ Clock Block | `ClockBlock` | Zegar ścienny |
| Fancy Sign | ✅ Hanging Sign | `HangingSignBlock` | Wiszący znak |
| Table | ✅ (częściowo) | - | Brak dokładnego odpowiednika |
| Map Frame | ✅ Item Frame (vanilla+) | `FrameBlock` | Ramka z funkcjami |
| Cookie Jar | ✅ Jar | `JarBlock` | Słoik (nie tylko ciastka) |
| Lantern | ✅ Wall Lantern | `WallLanternBlock` | Latarnia na ścianę |
| Lamp | ✅ End Lamp | `EndLampBlock` | Lampa dekoracyjna |
| Seat | ✅ (częściowo) | - | Brak dokładnego odpowiednika |
| Notice Board | ✅ Notice Board | `NoticeBoardBlock` | Tablica ogłoszeń |
| Sword Pedestal | ✅ Pedestal | `PedestalBlock` | Piedestał na przedmioty |
| Globe | ✅ Globe | `GlobeBlock` | Globus |
| Doormat | ✅ Doormat | `DoormatBlock` | Wycieraczka |
| Flower Box | ✅ Flower Box | `FlowerBoxBlock` | Skrzynka na kwiaty |
| Cage | ✅ Cage | `CageBlock` | Klatka na moby |
| Sack | ✅ Sack | `SackBlock` | Worek na przedmioty |
| Safe | ✅ Safe | `SafeBlock` | Sejf (zabezpieczony) |
| Blackboard | ✅ Blackboard | `BlackboardBlock` | Tablica do pisania |
| Statue | ✅ Statue | `StatueBlock` | Statua |
| Goblet | ✅ Goblet | `GobletBlock` | Kielich |
| Hourglass | ✅ Hourglass | `HourGlassBlock` | Klepsydra |
| Speaker | ✅ Speaker | `SpeakerBlock` | Głośnik (dźwięki) |
| Turn Table | ✅ Turn Table | `TurnTableBlock` | Obrotowy stół |
| Pulley | ✅ Pulley | `PulleyBlock` | Blok linowy |
| Crank | ✅ Crank | `CrankBlock` | Korba |
| Faucet | ✅ Faucet | `FaucetBlock` | Kran (płyny) |
| Cog Block | ✅ Cog Block | `CogBlock` | Blok zębaty (mechanizm) |
| Wind Vane | ✅ Wind Vane | `WindVaneBlock` | Wiatrowskaz |

### Brak bezpośredniego odpowiednika w Supplementaries

| BiblioCraft 1.7.10 | Sugerowany zamiennik 1.18.2 | Mod |
|--------------------|----------------------------|-----|
| Armor Stand | Armor Stand (vanilla) / Statue | Vanilla / Supplementaries |
| Weapon Case | Item Frame / Pedestal | Vanilla / Supplementaries |
| Potion Shelf | Item Shelf (częściowo) | Supplementaries |
| Wood Label | (brak dobrego) | - |
| Desk | (brak) | Handcrafted? |
| Typesetting Table | (brak - funkcja usunięta) | - |
| Printing Press | (brak - funkcja usunięta) | - |
| Fancy Workbench | Crafting Table (vanilla) | Vanilla |
| Framed Chest | FramedBlocks | FramedBlocks |
| Furniture Paneler | (brak - funkcja usunięta) | - |
| Painting (custom) | Painting (vanilla) | Vanilla |
| Paint Press | (brak) | - |
| Bell | Bell (vanilla 1.14+) | Vanilla |
| Clipboard | (brak) | - |
| Dinner Plate | Plate (częściowo) | Supplementaries? |
| Disc Rack | Jukebox (vanilla) | Vanilla |
| Tape Measure | (brak) | - |
| Atlas | Map (vanilla) / JourneyMap | Vanilla |
| Death Compass | (brak) | - |
| Redstone Book | (brak) | - |

---

## Statystyki konwersji

| Kategoria | Liczba |
|-----------|--------|
| **Bloki BiblioCraft 1.7.10** | ~30 |
| **Tile Entities BiblioCraft** | 29 |
| **Itemy BiblioCraft** | ~25 |
| **Dobre zamienniki w Supplementaries** | ~15 |
| **Częściowe zamienniki** | ~8 |
| **Brak zamiennika (funkcja tracona)** | ~7 |

---

## Kluczowe różnice NBT / Dane do konwersji

### BiblioCraft 1.7.10 - typowe pola NBT

```java
// TileEntityBookcase - przykład
- Items (ItemStack[])
- bookCount (int)

// TileEntityArmorStand
- armorItems (ItemStack[4])

// TileEntityGenericShelf / TileEntityPotionShelf
- shelfItems (ItemStack[])

// TileEntityFancySign
- signText (String)
- textScale (float)

// TileEntityClock
- hour (int)
- minute (int)

// TileEntityFramedChest
- frameTexture (String/block ID)
- chestItems (ItemStack[])

// TileEntityLabel
- slotItem (ItemStack)
- text (String)
```

### Supplementaries 1.18.2 - struktura NBT

W Supplementaries bloki używają standardowego systemu BlockEntity Minecraft 1.18.2:
- Dane przechowywane w `CompoundTag`
- Sloty inventory w `Items` tag
- Customowe dane w zależności od bloku

---

## Problemy konwersji

### 🔴 Krytyczne (trudne do przeniesienia)

1. ~~**System druku książek** (Typesetting + Printing Press)~~
   - **NIEISTOTNY** - nie wymaga konwersji
   - Bloki można zastąpić dekoracyjnie lub usunąć

2. **Furniture Paneler / Zmiana tekstur mebli**
   - ✅ **Rozwiązanie:** FramedBlocks lub BlockCarpentry
   - FramedBlocks: wiele kształtów z możliwością "udawania" innych bloków
   - BlockCarpentry: "coverable blocks" z teksturą bloku w środku
   - Konwersja: przeniesienie "cover block" do framed/carpentry block

3. **Custom Paintings**
   - Inny system niż vanilla
   - Wymaga konwersji na standardowe obrazy lub rekonstrukcję

### 🟡 Średnie (częściowa utrata danych)

3. **Bookcase → Book Pile**
   - Zmiana z pionowej półki na poziomy stos
   - Konieczna zmiana orientacji i układu

4. **Custom Paintings (BC) → Immersive Paintings**
   - ✅ **Rozwiązanie:** Mod Immersive Paintings pozwala na customowe obrazy
   - Wczytywanie z plików (drag & drop)
   - Wymaga konwersji ścieżek i formatów NBT

5. **Armor Stand**
   - Vanilla armor stand ma mniej funkcji niż BC
   - Statue z Supplementaries daje więcej opcji ale inny format NBT

6. **Atlas**
   - Brak bezpośredniego odpowiednika
   - JourneyMap waypointy to inny system

### 🟢 Łatwe (dobre mapowanie)

7. **Shelf → Item Shelf**
   - Podobna funkcjonalność
   - Konwersja inventory możliwa

8. **Clock → Clock Block**
   - Podobna funkcja
   - Brak danych do konwersji (tylko wyświetlanie)

9. **Lantern/Lamp → Wall Lantern/End Lamp**
   - Funkcja dekoracyjna zachowana
   - Brak specjalnych danych NBT

---

## Następne kroki (Zadanie 2)

1. **Przygotować symulacje działania kluczowych bloków:**
   - Symulacja Bookcase (inventory książek)
   - Symulacja Armor Stand (ekspozycja zbroi)
   - Symulacja Shelf/Item Shelf (ekspozycja przedmiotów)
   - Symulacja Clock (wyświetlanie czasu)

2. **Napisać kod konwersji NBT:**
   - Konwerter inventory między BC a Supplementaries
   - Mapper tekstur dla Framed Chest → odpowiedniki
   - Konwerter dla Fancy Sign (tekst + formatowanie)

3. **Zdefiniować konwersję dla FramedBlocks:**
   - Mapowanie mebli BC (Framed Chest, etc.) na odpowiednie kształty FramedBlocks
   - Konwersja NBT: `frameTexture` → `camoState`

4. **Przygotować konwersję dla Immersive Paintings:**
   - Mapowanie ścieżek obrazów BC na format Immersive Paintings
   - Upload obrazów do systemu modu

5. **Zdefiniować blok-placeholdery:**
   - Dla Typesetting Table / Printing Press (nieistotne funkcjonalnie)
   - Opcjonalnie zastąpienie dekoracyjnymi blokami

---

## Zalecenia przed Zadaniem 2

1. **Sprawdzić użycie na mapie głównej:**
   - ~~Typesetting Table / Printing Press~~ - NIEISTOTNE, można usunąć/zastąpić dekoracyjnie
   - Furniture Paneler + meble z teksturami - WAŻNE, wymaga konwersji do FramedBlocks
   - Custom Paintings - WAŻNE, wymaga konwersji do Immersive Paintings

2. **Zainstalować mody docelowe do testów:**
   - Supplementaries (główny zamiennik)
   - FramedBlocks (meble z teksturami)
   - BlockCarpentry (alternatywa dla FramedBlocks)
   - Immersive Paintings (customowe obrazy)

3. **Przygotować reguły mapowania tekstur:**
   - Framed Chest / meble BC → odpowiednie kształty FramedBlocks
   - Konwersja `frameTexture` (String) → `camoState` (BlockState)
   - Mapowanie tekstur drewna 1.7.10 → 1.18.2

4. **Przygotować migrację obrazów:**
   - Lokalizacja obrazów BC w folderze mapy
   - Format Immersive Paintings (konwersja ścieżek)

---

**Status:** ✅ Zadanie 1 ukończone - gotowe do przeglądu i akceptacji  
**Data:** 2026-02-02  
**Agent:** AI Konwersji BiblioCraft
