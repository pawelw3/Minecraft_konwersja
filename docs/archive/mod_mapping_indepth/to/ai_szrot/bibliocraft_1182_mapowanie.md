# BiblioCraft 1.7.10 → Supplementaries 1.18.2 - Mapowanie

## Informacje ogólne

- **Cel konwersji:** BiblioCraft nie ma portu na 1.18.2
- **Główny zamiennik:** Supplementaries (Forge 1.18.2)
- **Dodatkowe zamienniki:** Handcrafted, FramedBlocks, Vanilla
- **Strategia:** Funkcjonalne odtworzenie, nie 1:1 blok→blok

---

## Supplementaries - informacje

- **Autor:** MehVahdJukaar
- **Wersja:** 1.5.x (dla MC 1.18.2)
- **Repozytorium:** https://github.com/MehVahdJukaar/Supplementaries
- **Loader:** Forge (i Fabric)
- **Zależności:** Moonlight Library

### Struktura kodu Supplementaries

```
net/mehvahdjukaar/supplementaries/
├── common/
│   ├── block/blocks/      # Klasy bloków
│   ├── block/tiles/       # BlockEntity (TileEntity)
│   ├── items/             # Itemy
│   └── entities/          # Encje
├── client/                # Kod kliencki (rendering)
└── integration/           # Integracje z innymi modami
```

---

## Mapowanie bloków

### ✅ Dobre zamienniki (funkcjonalność zachowana)

#### 1. Bookcase (BC) → Book Pile (Supplementaries)

| Aspekt | BiblioCraft | Supplementaries |
|--------|-------------|-----------------|
| **Blok** | `BlockBookcase` | `BookPileBlock` / `BookPileHorizontalBlock` |
| **TileEntity** | `TileEntityBookcase` | `BookPileBlockTile` |
| **Pojemność** | 16 slotów | 4-8 książek (zależnie od wysokości) |
| **Wyświetlanie** | 3 poziomy półek | Stos książek (pionowy/poziomy) |
| **NBT** | `Items[16]` | `Items[]` (zależnie od implementacji) |

**Uwagi:**
- BC: pionowe półki, Supplementaries: stos książek
- Konieczna zmiana orientacji przy konwersji
- Mniejsza pojemność w Supplementaries

#### 2. Shelf (BC) → Item Shelf (Supplementaries)

| Aspekt | BiblioCraft | Supplementaries |
|--------|-------------|-----------------|
| **Blok** | `BlockGenericShelf` | `ItemShelfBlock` |
| **TileEntity** | `TileEntityGenericShelf` | `ItemShelfBlockTile` |
| **Pojemność** | 4 sloty | 3-4 sloty (zależnie od typu) |
| **Wyświetlanie** | Przedmioty na półce | Przedmioty na półce |
| **NBT** | `Items[4]` | `Items[]` |

**Uwagi:**
- Bardzo podobna funkcjonalność
- Konwersja inventory bezpośrednia
- Supplementaries ma różne typy półek

#### 3. Clock (BC) → Clock Block (Supplementaries)

| Aspekt | BiblioCraft | Supplementaries |
|--------|-------------|-----------------|
| **Blok** | `BlockClock` | `ClockBlock` |
| **TileEntity** | `TileEntityClock` | `ClockBlockTile` |
| **Funkcja** | Wyświetlanie czasu | Wyświetlanie czasu |
| **NBT** | `hour`, `minute` | `time` (automatyczne) |

**Uwagi:**
- Obie wersje pokazują czas gry
- BC: wskazówki, Supplementaries: wyświetlacz
- Brak danych do konwersji (tylko dekoracja)

#### 4. Fancy Sign (BC) → Hanging Sign (Supplementaries)

| Aspekt | BiblioCraft | Supplementaries |
|--------|-------------|-----------------|
| **Blok** | `BlockFancySign` | `HangingSignBlock` |
| **TileEntity** | `TileEntityFancySign` | `HangingSignBlockTile` |
| **Tekst** | 4 linie, skalowalny | 2 linie (wiszący) lub więcej |
| **NBT** | `Text1-4`, `textScale` | `Text[lines]`, `color` |

**Uwagi:**
- BC: znak na ścianie, Supplementaries: wiszący znak
- Konieczna zmiana formatowania tekstu
- Mniejsza pojemność tekstu w Hanging Sign

#### 5. Lantern/Lamp (BC) → Wall Lantern / End Lamp (Supplementaries)

| Aspekt | BiblioCraft | Supplementaries |
|--------|-------------|-----------------|
| **Blok** | `BlockLantern` / `BlockLamp` | `WallLanternBlock` / `EndLampBlock` |
| **TileEntity** | `TileEntityLantern` / `TileEntityLamp` | (brak / prosty) |
| **Funkcja** | Oświetlenie dekoracyjne | Oświetlenie dekoracyjne |
| **NBT** | `lit` | `lit` |

**Uwagi:**
- Wall Lantern: latarnia na ścianę (odpowiednik BC Lantern)
- End Lamp: lampa styl End (odpowiednik BC Lamp)
- Podobna funkcjonalność

#### 6. Notice Board (BC) → Notice Board (Supplementaries)

| Aspekt | BiblioCraft | Supplementaries |
|--------|-------------|-----------------|
| **Blok** | (brak w BC) | `NoticeBoardBlock` |
| **TileEntity** | - | `NoticeBoardBlockTile` |
| **Funkcja** | - | Tablica ogłoszeń |

**Uwagi:**
- BC nie ma tego bloku
- Dobra alternatywa dla wyświetlania informacji

#### 7. Pedestal (Supplementaries) ← Sword Pedestal (BC)

| Aspekt | BiblioCraft | Supplementaries |
|--------|-------------|-----------------|
| **Blok** | `BlockSwordPedestal` | `PedestalBlock` |
| **TileEntity** | `TileEntitySwordPedestal` | `PedestalBlockTile` |
| **Funkcja** | Ekspozycja broni | Ekspycja przedmiotu |
| **NBT** | `Items[1]`, `hasGlowstone` | `Items[1]` |

**Uwagi:**
- Bardzo podobna funkcjonalność
- BC: specyficznie dla broni, Supplementaries: dowolny przedmiot
- Konwersja inventory bezpośrednia

#### 8. Globe (Supplementaries)

| Aspekt | BiblioCraft | Supplementaries |
|--------|-------------|-----------------|
| **Blok** | (brak w BC) | `GlobeBlock` |
| **TileEntity** | - | `GlobeBlockTile` |

**Uwagi:**
- BC nie ma globusa
- Dodatkowa dekoracja dostępna w Supplementaries

#### 9. Doormat (Supplementaries)

| Aspekt | BiblioCraft | Supplementaries |
|--------|-------------|-----------------|
| **Blok** | (brak w BC) | `DoormatBlock` |
| **TileEntity** | - | `DoormatBlockTile` |

**Uwagi:**
- Wycieraczka z tekstem
- Funkcjonalność nieobecna w BC

#### 10. Flower Box (Supplementaries)

| Aspekt | BiblioCraft | Supplementaries |
|--------|-------------|-----------------|
| **Blok** | (brak w BC) | `FlowerBoxBlock` |
| **TileEntity** | - | `FlowerBoxBlockTile` |

**Uwagi:**
- Skrzynka na kwiaty pod okno
- Podobna idea co niektóre bloki BC (dekoracyjne)

#### 11. Cage (Supplementaries)

| Aspekt | BiblioCraft | Supplementaries |
|--------|-------------|-----------------|
| **Blok** | (brak w BC) | `CageBlock` |
| **TileEntity** | - | `CageBlockTile` |

**Uwagi:**
- Klatka na moby (małe)
- Funkcjonalność nieobecna w BC

#### 12. Sack (Supplementaries)

| Aspekt | BiblioCraft | Supplementaries |
|--------|-------------|-----------------|
| **Blok** | (brak w BC) | `SackBlock` |
| **TileEntity** | - | `SackBlockTile` |

**Uwagi:**
- Worek na przedmioty (alternatywa dla skrzyni)
- Podobna funkcja co Framed Chest z BC

#### 13. Safe (Supplementaries)

| Aspekt | BiblioCraft | Supplementaries |
|--------|-------------|-----------------|
| **Blok** | `BlockWeaponCase` (częściowo) | `SafeBlock` |
| **TileEntity** | `TileEntityWeaponCase` | `SafeBlockTile` |
| **Funkcja** | Zamykana gablotka | Zabezpieczona skrzynia |
| **NBT** | `locked` | (zabezpieczenie gracza) |

**Uwagi:**
- BC: Lock and Key, Supplementaries: przypisanie do gracza
- Inny system zabezpieczeń

#### 14. Blackboard (Supplementaries)

| Aspekt | BiblioCraft | Supplementaries |
|--------|-------------|-----------------|
| **Blok** | (brak w BC) | `BlackboardBlock` |
| **TileEntity** | - | `BlackboardBlockTile` |

**Uwagi:**
- Tablica do rysowania (piksele)
- Unikalna funkcja Supplementaries

#### 15. Statue (Supplementaries)

| Aspekt | BiblioCraft | Supplementaries |
|--------|-------------|-----------------|
| **Blok** | `BlockArmorStand` (częściowo) | `StatueBlock` |
| **TileEntity** | `TileEntityArmorStand` | `StatueBlockTile` |

**Uwagi:**
- BC Armor Stand: tylko zbroja
- Supplementaries Statue: pełny model gracza/moba
- Inna funkcjonalność

#### 16. Jar (Supplementaries) ← Cookie Jar (BC)

| Aspekt | BiblioCraft | Supplementaries |
|--------|-------------|-----------------|
| **Blok** | `BlockStuff` (Cookie Jar) | `JarBlock` |
| **TileEntity** | `TileEntityCookieJar` | `JarBlockTile` |
| **Funkcja** | Przechowywanie ciastek | Przechowywanie dowolnych przedmiotów |
| **NBT** | `Items[]` | `Items[]` |

**Uwagi:**
- BC: tylko ciastka, Supplementaries: dowolne przedmioty
- Konwersja możliwa (dla ciastek)
- Supplementaries ma większą funkcjonalność

#### 17. Frame (Supplementaries) ← Map Frame (BC)

| Aspekt | BiblioCraft | Supplementaries |
|--------|-------------|-----------------|
| **Blok** | `BlockMapFrame` | `FrameBlock` |
| **TileEntity** | `TileEntityMapFrame` | `FrameBlockTile` |
| **Funkcja** | Ramka na mapę | Ramka z funkcjami (również mapa) |
| **NBT** | `Items[1]` (mapa) | `Items[1]` |

**Uwagi:**
- BC: tylko mapy, Supplementaries: dowolne przedmioty + mapy
- Konwersja bezpośrednia

---

### ⚠️ Częściowe zamienniki

#### 18. Table (BC) → (brak dokładnego)

**Alternatywy:**
- Vanilla: różne bloki jako stół
- Supplementaries: częściowo `PedestalBlock` (ale bez łączenia)

**Uwagi:**
- BC Table można łączyć w większe stoły (2×2, 2×3)
- Brak bezpośrendniego odpowiednika w 1.18.2

#### 19. Armor Stand (BC) → Vanilla / Statue (Supplementaries)

**Opcje:**
- Vanilla `ArmorStand` - podstawowa funkcja
- Supplementaries `StatueBlock` - bardziej dekoracyjna

**Uwagi:**
- BC: 4 sloty (tylko zbroja), renderowanie 3D
- Vanilla: pełny armor + przedmioty w rękach
- Statue: inna funkcja (wygląd moba/gracza)

#### 20. Weapon Case (BC) → Item Frame / Pedestal

**Alternatywy:**
- Vanilla `ItemFrame` - podstawowa ekspozycja
- Supplementaries `PedestalBlock` - piedestał

**Uwagi:**
- BC: zamykana gablotka szklana
- Brak dokładnego odpowiednika z funkcją zamykania

#### 21. Potion Shelf (BC) → Item Shelf (Supplementaries)

**Uwagi:**
- BC ma dedykowaną półkę na 12 mikstur
- Supplementaries Item Shelf: uniwersalna (ale mniej slotów)

#### 22. Writing Desk (BC) → (brak)

**Uwagi:**
- Unikalna funkcja BC (pisanie książek + storage)
- Brak odpowiednika w Supplementaries
- Można zastąpić vanilla `Lectern` (częściowo)

#### 23. Fancy Workbench (BC) → Vanilla Crafting Table

**Uwagi:**
- BC: crafting + storage
- Vanilla 1.18.2: tylko crafting
- Brak funkcji storage w vanilla

---

### ✅ NIE WYMAGA KONWERSJI (funkcja nieistotna)

#### 24. Typesetting Table / Printing Press

**Decyzja:** Funkcjonalność nieistotna - nie wymaga konwersji

**Opcje:**
- Usunięcie bloków (zastąpienie powietrzem)
- Zastąpienie dekoracyjnymi blokami (FramedBlocks jako meble)
- Zachowanie jako zwykłe bloki bez funkcji

**Uwagi:**
- System druku książek unikalny dla BC
- Nie ma wpływu na kluczowe elementy mapy

#### 25. Furniture Paneler → FramedBlocks / BlockCarpentry ✅

**Rozwiązanie:** Konwersja do systemu "framed/coverable blocks"

**Opcja A: FramedBlocks**
- Blok: `FramedBlock` (wiele wariantów kształtów)
- TileEntity: `FramedBlockEntity`
- Funkcja: Blok przyjmuje teksturę "camo" bloku
- NBT: `camoState` - BlockState używany jako tekstura

**Opcja B: BlockCarpentry**
- Blok: `FrameBlock` / `IllusionBlock`
- TileEntity: `BlockEntityFrame`
- Funkcja: Blok zawiera inny blok i przyjmuje jego teksturę
- NBT: `contained_block` - blok w środku

**Strategia konwersji:**
```java
// BiblioCraft 1.7.10
TileEntityFurniturePaneler:
- frameTexture: String (ID bloku tekstury)
- inventory: mebel do "opanelowania"

// FramedBlocks 1.18.2
FramedBlockEntity:
- camoState: BlockState (stan bloku jako tekstura)
```

**Mapowanie mebli BC na FramedBlocks:**
| Mebel BC | FramedBlocks odpowiednik |
|----------|--------------------------|
| Framed Chest | Framed Chest (jeśli dostępny) lub inny container |
| Framed Bookcase | Framed Bookshelf |
| Framed Shelf | Framed Slab / Framed Panel |
| Inne meble | Odpowiedni kształt z FramedBlocks |

#### 26. Custom Painting System → Immersive Paintings ✅

**Rozwiązanie:** Konwersja do modu Immersive Paintings

**Mod:** Immersive Paintings (Luke100000)
- Repozytorium: https://github.com/Luke100000/ImmersivePaintings
- Licencja: GPL-3.0
- Wersja: 1.18.2 dostępna

**Funkcje:**
- Customowe obrazy (jak BC)
- Wczytywanie z plików (drag & drop)
- Działa w multiplayer
- Różne rozmiary i formaty

**Struktura NBT:**
```java
// BiblioCraft 1.7.10
TileEntityPainting:
- paintingType: String (typ obrazu)
- resourceLocation: String (ścieżka do tekstury)

// Immersive Paintings 1.18.2
PaintingEntity:
- image: String (nazwa/ID obrazu)
- width: int (szerokość)
- height: int (wysokość)
- rotation: int (obrót)
```

**Konwersja:**
- Przeniesienie ścieżek do formatu Immersive Paintings
- Konwersja rozmiarów
- Upload obrazów do systemu modu

#### 27. Label (Wood Label)

**Problem:**
- Unikalna funkcja (etykieta pokazująca zawartość skrzyni)
- Brak odpowiednika

**Alternatywa:**
- Vanilla `Sign` (częściowo)

#### 28. Seat (z oparciami)

**Problem:**
- System krzeseł z oparciami (Seat + Seat Back)
- Supplementaries nie ma tego

**Alternatywa:**
- Handcrafted mod (jeśli dostępny)
- Lub vanilla `Stairs` (jako siedzenie)

#### 29. Tape Measure / Atlas / Waypoint Compass

**Problem:**
- Unikalne narzędzia BC
- Brak bezpośrednich odpowiedników

**Alternatywy:**
- Tape Measure → brak
- Atlas → JourneyMap (mod)
- Waypoint Compass → JourneyMap waypointy

#### 30. Redstone Book

**Problem:**
- Książka dająca sygnał redstone w Bookcase
- Brak odpowiednika

#### 31. Clipboard

**Problem:**
- Tablica z checklistą
- Brak odpowiednika w Supplementaries

---

## Dodatkowe mody do konwersji Bibliocraft

### FramedBlocks (XFactHD)

**Repozytorium:** https://github.com/XFactHD/FramedBlocks  
**Licencja:** LGPL  
**Wersja:** 1.18.x

**Kluczowe klasy:**
```
xfacthd/framedblocks/
├── common/block/          # Bloki (FramedBlock, FramedSlopeBlock, etc.)
├── common/data/           # Dane (BlockState, modeli)
├── common/blockentity/    # BlockEntities
└── client/render/         # Renderery
```

**Główne bloki:**
| Blok | Opis |
|------|------|
| `FramedBlock` | Podstawowy blok z teksturą |
| `FramedSlopeBlock` | Skos |
| `FramedStairsBlock` | Schody |
| `FramedSlabBlock` | Płyta |
| `FramedPanelBlock` | Panel |
| `FramedCornerSlopeBlock` | Narożny skos |
| `FramedPrismBlock` | Pryzma |
| `FramedDoorBlock` | Drzwi |
| `FramedTrapDoorBlock` | Klapa |
| `FramedFenceBlock` | Płot |
| `FramedButtonBlock` | Przycisk |
| `FramedPressurePlateBlock` | Płytka naciskowa |
| `FramedSignBlock` | Znak |
| ... (ponad 100 wariantów) |

**BlockEntity:**
- `FramedBlockEntity` - przechowuje `camoState` (BlockState jako tekstura)

**NBT:**
```java
FramedBlockEntity:
- camoState: CompoundTag (BlockState używany jako tekstura)
- glowing: boolean (czy świeci)
- intangible: boolean (czy niematerialny)
```

---

### BlockCarpentry (PianoManu)

**Repozytorium:** https://github.com/PianoManu/BlockCarpentry  
**Wersja:** 1.18.2

**Główne bloki:**
| Blok | Opis |
|------|------|
| `FrameBlock` | Ramka (pokazuje teksturę bloku w środku) |
| `IllusionBlock` | Blok iluzji (przezroczysty, pokazuje teksturę) |
| `ChestFrameBlock` | Skrzynia-ramka |
| `DoorFrameBlock` | Drzwi-ramka |
| `StairsFrameBlock` | Schody-ramka |
| `SlabFrameBlock` | Płyta-ramka |
| ... |

**BlockEntity:**
- `BlockEntityFrame` - przechowuje `contained_block`

**NBT:**
```java
BlockEntityFrame:
- contained_block: CompoundTag (Block w środku)
- block_state: int (stan bloku)
```

**Różnica od FramedBlocks:**
- BlockCarpentry: blok "zawiera" inny blok (jakby w środku)
- FramedBlocks: blok "udaje" teksturę innego bloku (camo)

---

### Immersive Paintings (Luke100000)

**Repozytorium:** https://github.com/Luke100000/ImmersivePaintings  
**Licencja:** GPL-3.0  
**Wersja:** 1.18.2

**Główne klasy:**
```
immersive_paintings/
├── entity/PaintingEntity.java     # Encja obrazu
├── network/                       # Synchronizacja obrazów
├── client/                        # GUI, renderery
└── server/                        # Serwerowe przechowywanie obrazów
```

**Funkcje:**
- Customowe obrazy z plików
- Drag & drop do gry
- Multiplayer (synchronizacja)
- Różne rozmiary (1×1 do 8×8 bloków)
- Filtry (sepia, grayscale, etc.)

**NBT (PaintingEntity):**
```java
- image: String (nazwa obrazu)
- width: int (szerokość w blokach)
- height: int (wysokość w blokach)
- rotation: int (obrót: 0, 90, 180, 270)
- filter: String (filtr: "none", "sepia", etc.)
- visibility: String (widoczność: "public", "private")
```

**Konwersja z BC Painting:**
```java
// BiblioCraft 1.7.10
TileEntityPainting:
- resourceLocation: "bibliocraft:paintings/custom/moj_obraz.png"
- paintingType: "custom"

// Immersive Paintings 1.18.2
PaintingEntity:
- image: "moj_obraz" (nazwa zarejestrowanego obrazu)
- width/height: do obliczenia z rozmiaru obrazu
```

---

## Supplementaries - dodatkowe bloki (nieobecne w BC)

Bloki dostępne w Supplementaries, których nie było w BC:

| Blok | Funkcjonalność |
|------|----------------|
| `BambooSpikesBlock` | Kolce z bambusa |
| `BellowsBlock` | Miechy (dmuchanie) |
| `CageBlock` | Klatka na moby |
| `CandelabraBlock` | Kandelabr |
| `CandleHolderBlock` | Świecznik |
| `CogBlock` | Zębatka (mechanizm) |
| `CrystalDisplayBlock` | Wyświetlacz kryształowy |
| `FaucetBlock` | Kran (płyny) |
| `FlagBlock` | Flaga |
| `GlobeBlock` | Globus |
| `GoldDoorBlock` / `GoldTrapdoorBlock` | Złote drzwi/klapa |
| `HourGlassBlock` | Klepsydra |
| `IronGateBlock` | Żelazna furtka |
| `LeadDoorBlock` / `LeadTrapdoorBlock` | Ołowiane drzwi/klapa |
| `LockBlock` | Blokada |
| `NetheriteDoorBlock` / `NetheriteTrapdoorBlock` | Netherytowe drzwi/klapa |
| `PancakeBlock` | Naleśnik |
| `PlanterBlock` | Doniczka |
| `PulleyBlock` | Blok linowy |
| `RelayerBlock` | Przekaźnik redstone |
| `RopeBlock` / `RopeKnotBlock` | Lina |
| `SignPostBlock` | Słup z znakiem |
| `SilverDoorBlock` / `SilverTrapdoorBlock` | Srebrne drzwi/klapa |
| `SpeakerBlock` | Głośnik (dźwięki) |
| `SpringLauncherBlock` | Wyrzutnia |
| `TurnTableBlock` | Stół obrotowy |
| `WindVaneBlock` | Wiatrowskaz |
| `CrankBlock` | Korba |
| `AshCauldronBlock` / `AshLayerBlock` | Popiół |
| `FlaxBlock` | Len (uprawa) |
| `GunpowderBlock` | Proch (na ziemi) |
| `SugarBlock` | Cukier (na ziemi) |
| `SoapBlock` | Mydło |
| `BubleBlock` | Bańka mydlana |
| `FeatherBlock` | Pióra (blok) |
| `FlintBlock` | Krzemień (blok) |
| `MagmaCreamBlock` | Krem magmowy (blok) |

---

## Mapowanie TileEntity / BlockEntity

### Struktura NBT

**BiblioCraft 1.7.10:**
```java
// Standard Forge TileEntity
void writeToNBT(NBTTagCompound tag) {
    super.writeToNBT(tag);
    // Custom data
    NBTTagList items = new NBTTagList();
    for (ItemStack stack : inventory) {
        items.appendTag(stack.writeToNBT(new NBTTagCompound()));
    }
    tag.setTag("Items", items);
}
```

**Supplementaries 1.18.2:**
```java
// Standard Minecraft BlockEntity
@Override
protected void saveAdditional(CompoundTag tag) {
    super.saveAdditional(tag);
    ContainerHelper.saveAllItems(tag, this.items);
}

@Override
public void load(CompoundTag tag) {
    super.load(tag);
    this.items = NonNullList.withSize(this.getContainerSize(), ItemStack.EMPTY);
    ContainerHelper.loadAllItems(tag, this.items);
}
```

### Kluczowe różnice

| Aspekt | 1.7.10 (Forge) | 1.18.2 (Forge) |
|--------|----------------|----------------|
| Nazwa | TileEntity | BlockEntity |
| Pakiet | `net.minecraft.tileentity` | `net.minecraft.world.level.block.entity` |
| NBT | `NBTTagCompound` | `CompoundTag` |
| ItemStack | `writeToNBT` / `readFromNBT` | `save` / `load` |
| Inventory | `IInventory` | `Container` / `WorldlyContainer` |
| Sync | `getDescriptionPacket` | `getUpdatePacket` / `getUpdateTag` |

---

## ID bloków (1.18.2 - Supplementaries)

```
supplementaries:book_pile
supplementaries:book_pile_horizontal
supplementaries:item_shelf
supplementaries:clock_block
supplementaries:hanging_sign
supplementaries:wall_lantern
supplementaries:end_lamp
supplementaries:notice_board
supplementaries:pedestal
supplementaries:globe
supplementaries:doormat
supplementaries:flower_box
supplementaries:cage
supplementaries:jar
supplementaries:sack
supplementaries:safe
supplementaries:blackboard
supplementaries:statue
supplementaries:frame
... (i wiele więcej)
```

---

## Strategia konwersji

### Priorytety

1. **Wysoki priorytet** (łatwa konwersja):
   - Shelf → Item Shelf
   - Clock → Clock Block
   - Sword Pedestal → Pedestal
   - Cookie Jar → Jar
   - Map Frame → Frame

2. **Średni priorytet** (częściowa konwersja):
   - Bookcase → Book Pile (zmiana orientacji)
   - Armor Stand → Vanilla Armor Stand / Statue
   - Weapon Case → Pedestal / Item Frame
   - Fancy Sign → Hanging Sign (adaptacja tekstu)

3. **Niski priorytet** (funkcja tracona lub placeholder):
   - Typesetting Table / Printing Press
   - Furniture Paneler
   - Custom Paintings
   - Writing Desk
   - Tape Measure / Atlas / Waypoint Compass

### Placeholdery

Dla bloków bez zamiennika można użyć:
- `supplementaries:pedestal` + opis (funkcja dekoracyjna)
- `minecraft:barrier` (niewidzialny blok)
- Usunięcie bloków (air)

---

## Podsumowanie - Z AKTUALIZACJAMI

| Kategoria | Liczba bloków BC | Dobry zamiennik | Częściowy | Brak/Nieistotne |
|-----------|------------------|-----------------|-----------|-----------------|
| **Storage/Ekspozycja** | 8 | 5 | 2 | 1 |
| **Dekoracyjne** | 12 | 6 | 3 | 3 |
| **Funkcjonalne** | 8 | 2 | 2 | 4 (w tym 2 nieistotne) |
| **Narzędzia (itemy)** | 6 | 0 | 2 | 4 |
| **RAZEM** | ~34 | ~13 (38%) | ~9 (26%) | ~12 (35%) |

### Aktualizacja po analizie

| Problem | Status | Rozwiązanie |
|---------|--------|-------------|
| System druku książek | ✅ NIEISTOTNY | Nie wymaga konwersji |
| Furniture Paneler | ✅ ROZWIĄZANY | FramedBlocks / BlockCarpentry |
| Custom Paintings | ✅ ROZWIĄZANY | Immersive Paintings |

**Mody docelowe do instalacji:**
1. **Supplementaries** - główny zamiennik (półki, globusy, latarnie)
2. **FramedBlocks** - meble z teksturami (zamiennik Furniture Paneler)
3. **BlockCarpentry** - alternatywa dla FramedBlocks (ramki/iluzje)
4. **Immersive Paintings** - customowe obrazy (zamiennik BC Painting)

**Wnioski:**
- ~38% bloków ma dobre zamienniki w Supplementaries
- ~26% wymaga częściowej adaptacji
- Funkcjonalność Furniture Paneler i Custom Paintings **ZACHOWANA** dzięki dodatkowym modom
- Tylko ~15% funkcjonalności rzeczywiście tracona (nieistotne lub niemożliwe do przeniesienia)
