# BiblioCraft 1.7.10 - Szczegółowa lista bloków i Tile Entities

## Informacje ogólne

- **Wersja moda:** v1.11.7
- **Wersja Minecraft:** 1.7.10
- **Pakiet:** `jds.bibliocraft`
- **Liczba bloków:** ~30
- **Liczba TileEntities:** 29
- **Liczba itemów:** ~25

---

## Struktura kodu

```
jds/bibliocraft/
├── blocks/           # Klasy bloków
├── tileentities/     # Klasy TileEntity
├── items/           # Klasy itemów
├── models/          # Modele
├── rendering/       # Renderery
├── gui/             # Interfejsy
├── network/         # Pakiety sieciowe
└── helpers/         # Pomocnicze
```

---

## Bloki (Block classes)

### Bloki magazynujące / ekspozycyjne

#### 1. BlockBookcase
- **ID:** `BiblioCraft:Bookcase`
- **TileEntity:** `TileEntityBookcase`
- **Inventory:** 16 slotów (tylko książki)
- **Funkcje:**
  - Przechowywanie książek (enchanted books, written books, book and quill)
  - Wizualne wyświetlanie książek na półkach (3 poziomy)
  - Redstone Book daje sygnał redstone gdy jest w środku
  - Interakcja z enchantment table (zwiększa poziom enchantu)
- **NBT:**
  - `Items` - ItemStack[16]
  - `bookCount` - liczba książek (int)
- **Metadata:** 0-5 (drewno), bit 3 = creative mode

#### 2. BlockArmorStand
- **ID:** `BiblioCraft:ArmorStand`
- **TileEntity:** `TileEntityArmorStand`
- **Inventory:** 4 sloty (hełm, napierśnik, nogawice, buty)
- **Funkcje:**
  - Wyświetlanie kompletu zbroi
  - Renderowanie 3D modelu zbroi
  - Możliwość obrotu (8 kierunków)
- **NBT:**
  - `Items` - ItemStack[4] (armor slots)
  - `rotation` - obrót (int 0-7)

#### 3. BlockWeaponCase (Display Case)
- **ID:** `BiblioCraft:WeaponCase`
- **TileEntity:** `TileEntityWeaponCase`
- **Inventory:** 1 slot
- **Funkcje:**
  - Gablotka szklana na jeden przedmiot
  - Renderowanie przedmiotu w środku
  - Możliwość zamknięcia na klucz (Lock and Key)
- **NBT:**
  - `Items` - ItemStack[1]
  - `locked` - czy zamknięta (boolean)

#### 4. BlockPotionShelf
- **ID:** `BiblioCraft:PotionShelf`
- **TileEntity:** `TileEntityPotionShelf`
- **Inventory:** 12 slotów (tylko mikstury)
- **Funkcje:**
  - Wyświetlanie mikstur na półce (4 rzędy × 3)
- **NBT:**
  - `Items` - ItemStack[12]

#### 5. BlockWeaponRack (Tool Rack)
- **ID:** `BiblioCraft:WeaponRack`
- **TileEntity:** `TileEntityWeaponRack`
- **Inventory:** 2 sloty (broń/narzędzia)
- **Funkcje:**
  - Wieszak na ścianę na 2 przedmioty
  - Renderowanie przedmiotów
- **NBT:**
  - `Items` - ItemStack[2]

#### 6. BlockGenericShelf (Shelf)
- **ID:** `BiblioCraft:Shelf`
- **TileEntity:** `TileEntityGenericShelf`
- **Inventory:** 4 sloty (dowolne przedmioty)
- **Funkcje:**
  - Uniwersalna półka ekspozycyjna
  - Wyświetlanie 4 przedmiotów
- **NBT:**
  - `Items` - ItemStack[4]

#### 7. BlockLabel (Wood Label)
- **ID:** `BiblioCraft:Label`
- **TileEntity:** `TileEntityLabel`
- **Inventory:** 1 slot + tekst
- **Funkcje:**
  - Etykieta na skrzynie/bloku
  - Wyświetla ikonę przedmiotu i tekst
  - Pokazuje zawartość skrzyni pod spodem
- **NBT:**
  - `Items` - ItemStack[1]
  - `labelText` - tekst etykiety (String)

### Bloki funkcjonalne (crafting/interakcja)

#### 8. BlockWritingDesk (Desk)
- **ID:** `BiblioCraft:WritingDesk`
- **TileEntity:** `TileEntityWritingDesk`
- **Inventory:** 2 sloty (papier, książka) + slot na atrament
- **Funkcje:**
  - Pisanie książek (book and quill)
  - Przechowywanie zapasów papieru
  - GUI z podglądem tekstu
- **NBT:**
  - `Items` - ItemStack[]
  - `pages` - strony tekstu

#### 9. BlockTypeMachine (Typesetting Table)
- **ID:** `BiblioCraft:TypesettingTable`
- **TileEntity:** `TileEntityTypeMachine`
- **Inventory:** 3 sloty (książka, płyta, wynik)
- **Funkcje:**
  - Tworzenie płyt drukarskich (Print Press Plate)
  - Kopiowanie treści książki na płytę
- **NBT:**
  - `Items` - ItemStack[]
  - `recipe` - zapisany przepis/książka

#### 10. BlockPrintPress (Printing Press)
- **ID:** `BiblioCraft:PrintingPress`
- **TileEntity:** `TileEntityPrintPress`
- **Inventory:** 3 sloty (płyta, atrament, blank book)
- **Funkcje:**
  - Kopiowanie książek z płyty
  - Wymaga atramentu
- **NBT:**
  - `Items` - ItemStack[]
  - `progress` - postęp druku

#### 11. BlockFancyWorkbench
- **ID:** `BiblioCraft:FancyWorkbench`
- **TileEntity:** `TileEntityFancyWorkbench`
- **Inventory:** 9 slotów crafting + 1 wynik + ekstra sloty
- **Funkcje:**
  - Stół rzemieślniczy z GUI
  - Przechowywanie przedmiotów w gridzie
  - Zapamiętywanie recepty
- **NBT:**
  - `Items` - ItemStack[]
  - `recipe` - zapisana recepta

#### 12. BlockFurniturePaneler
- **ID:** `BiblioCraft:FurniturePaneler`
- **TileEntity:** `TileEntityFurniturePaneler`
- **Inventory:** 2 sloty (mebel, materiał)
- **Funkcje:**
  - Zmiana wyglądu mebli (tekstury)
  - Nakładanie custom tekstur na ramkowe meble
- **NBT:**
  - `Items` - ItemStack[]
  - `texture` - ID tekstury

### Bloki dekoracyjne

#### 13. BlockTable
- **ID:** `BiblioCraft:Table`
- **TileEntity:** `TileEntityTable`
- **Inventory:** 1 slot (wyświetlany przedmiot)
- **Funkcje:**
  - Stół z wyświetlanym przedmiotem na blacie
  - Można łączyć w większe stoły (2×2, 2×3, itp.)
- **NBT:**
  - `Items` - ItemStack[1]

#### 14. BlockSeat
- **ID:** `BiblioCraft:Seat`
- **TileEntity:** `TileEntitySeat`
- **Inventory:** 0 slotów (tylko siedzenie)
- **Funkcje:**
  - Krzesło do siedzenia
  - Współpraca z Seat Back (oparciami)
- **NBT:**
  - `color` - kolor siedziska (int)

#### 15. BlockClock
- **ID:** `BiblioCraft:Clock`
- **TileEntity:** `TileEntityClock`
- **Inventory:** 0
- **Funkcje:**
  - Zegar ścienny pokazujący czas gry
  - Wskazówki poruszają się w czasie rzeczywistym
- **NBT:**
  - `hour` - godzina (int)
  - `minute` - minuta (int)

#### 16. BlockLantern (Fancy Lantern)
- **ID:** `BiblioCraft:Lantern`
- **TileEntity:** `TileEntityLantern`
- **Inventory:** 0
- **Funkcje:**
  - Dekoracyjna latarnia
  - Różne style (złota/żelazna)
  - Włączanie/wyłączanie
- **NBT:**
  - `lit` - czy zapalona (boolean)

#### 17. BlockLamp (Fancy Lamp)
- **ID:** `BiblioCraft:Lamp`
- **TileEntity:** `TileEntityLamp`
- **Inventory:** 0
- **Funkcje:**
  - Lampa stojąca
  - Złota lub żelazna wersja
- **NBT:**
  - `lit` - czy zapalona (boolean)

#### 18. BlockFancySign
- **ID:** `BiblioCraft:FancySign`
- **TileEntity:** `TileEntityFancySign`
- **Inventory:** 0 (tylko tekst)
- **Funkcje:**
  - Znak z lepszą czcionką niż vanilla
  - Możliwość skalowania tekstu
  - Formatowanie kolorów
- **NBT:**
  - `Text1-4` - linie tekstu (String)
  - `textScale` - skala tekstu (float)

#### 19. BlockPainting
- **ID:** `BiblioCraft:Painting`
- **TileEntity:** `TileEntityPainting`
- **Inventory:** 0
- **Funkcje:**
  - Customowe obrazy (większe niż vanilla)
  - Wczytywanie obrazów z plików
- **NBT:**
  - `paintingType` - typ obrazu
  - `resourceLocation` - ścieżka do tekstury

#### 20. BlockMapFrame
- **ID:** `BiblioCraft:MapFrame`
- **TileEntity:** `TileEntityMapFrame`
- **Inventory:** 1 slot (tylko mapa)
- **Funkcje:**
  - Ramka na mapy (płaska)
  - Wyświetlanie mapy na ścianie
- **NBT:**
  - `Items` - ItemStack[1] (Filled Map)

#### 21. BlockSwordPedestal
- **ID:** `BiblioCraft:SwordPedestal`
- **TileEntity:** `TileEntitySwordPedestal`
- **Inventory:** 1 slot (broń)
- **Funkcje:**
  - Piedestał na broń
  - Oświetlenie (glowstone w środku)
  - Renderowanie 3D broni
- **NBT:**
  - `Items` - ItemStack[1]
  - `hasGlowstone` - czy ma glowstone (boolean)

### Bloki "Stuff" (wielofunkcyjne)

#### 22. BlockStuff
- **ID:** `BiblioCraft:BlockStuff` (z metadata)
- **TileEntity:** różne w zależności od meta
- **Podtypy (metadata):**
  - 0: Cookie Jar (`TileEntityCookieJar`)
  - 1: Dinner Plate (`TileEntityDinnerPlate`)
  - 2: Disc Rack (`TileEntityDiscRack`)
  - 3: Seat Back (dekoracja, bez TE)
  - 4: Marker Pole (dla Tape Measure)

#### 23. BlockFramedChest
- **ID:** `BiblioCraft:FramedChest`
- **TileEntity:** `TileEntityFramedChest`
- **Inventory:** 27 slotów (jak vanilla chest)
- **Funkcje:**
  - Skrzynia z custom teksturą ramki
  - Tekstura może być zmieniona przez Furniture Paneler
- **NBT:**
  - `Items` - ItemStack[27]
  - `frameTexture` - ID bloku tekstury (String)

#### 24. BlockBell
- **ID:** `BiblioCraft:Bell`
- **TileEntity:** `TileEntityBell`
- **Inventory:** 0
- **Funkcje:**
  - Dzwonek (dzwiek po kliknięciu)
- **NBT:**
  - (brak istotnych danych)

#### 25. BlockClipboard
- **ID:** `BiblioCraft:Clipboard`
- **TileEntity:** `TileEntityClipboard`
- **Inventory:** 0 (tekst/checklist)
- **Funkcje:**
  - Tablica z listą zadań
  - Checkboxy (można zaznaczać)
- **NBT:**
  - `tasks` - lista zadań (String[])
  - `checked` - stan checkboxów (boolean[])

### Bloki ram do obrazów

#### 26-30. BlockPaintingFrame*
- **Klasy:** `BlockPaintingFrameBorderless`, `BlockPaintingFrameFancy`, `BlockPaintingFrameFlat`, `BlockPaintingFrameMiddle`, `BlockPaintingFrameSimple`
- **TileEntity:** `TileEntityPainting` (ten sam)
- **Funkcje:**
  - Ramy dla obrazów w różnych stylach

---

## Tile Entities (szczegóły)

### Wspólna struktura

Wszystkie TileEntities dziedziczą z `TileEntity` Forge i implementują:
- `readFromNBT(NBTTagCompound)` - odczyt danych
- `writeToNBT(NBTTagCompound)` - zapis danych
- `getDescriptionPacket()`/`onDataPacket()` - synchronizacja sieciowa

### Lista wszystkich Tile Entities

| Nazwa klasy | Powiązany blok | Kluczowe pola NBT |
|-------------|----------------|-------------------|
| `TileEntityArmorStand` | Armor Stand | `Items[4]` (armor) |
| `TileEntityBell` | Bell | (brak) |
| `TileEntityBookcase` | Bookcase | `Items[16]`, `bookCount` |
| `TileEntityClipboard` | Clipboard | `tasks[]`, `checked[]` |
| `TileEntityClock` | Clock | `hour`, `minute` |
| `TileEntityCookieJar` | Cookie Jar | `Items[]` (ciastka) |
| `TileEntityDinnerPlate` | Dinner Plate | `Items[]` (jedzenie) |
| `TileEntityDiscRack` | Disc Rack | `Items[]` (płyty) |
| `TileEntityFancySign` | Fancy Sign | `Text1-4`, `textScale` |
| `TileEntityFancyWorkbench` | Fancy Workbench | `Items[]`, `recipe` |
| `TileEntityFramedChest` | Framed Chest | `Items[27]`, `frameTexture` |
| `TileEntityFurniturePaneler` | Furniture Paneler | `Items[]`, `texture` |
| `TileEntityGenericShelf` | Shelf | `Items[4]` |
| `TileEntityLabel` | Label | `Items[1]`, `labelText` |
| `TileEntityLamp` | Lamp | `lit` |
| `TileEntityLantern` | Lantern | `lit` |
| `TileEntityMapFrame` | Map Frame | `Items[1]` (mapa) |
| `TileEntityMarkerPole` | Marker Pole | `owner` (gracz) |
| `TileEntityPainting` | Painting | `paintingType`, `resourceLocation` |
| `TileEntityPaintPress` | Paint Press | `Items[]`, `progress` |
| `TileEntityPotionShelf` | Potion Shelf | `Items[12]` |
| `TileEntityPrintPress` | Printing Press | `Items[]`, `progress` |
| `TileEntitySeat` | Seat | `color` |
| `TileEntitySwordPedestal` | Sword Pedestal | `Items[1]`, `hasGlowstone` |
| `TileEntityTable` | Table | `Items[1]` |
| `TileEntityTypeMachine` | Typesetting Table | `Items[]`, `recipe` |
| `TileEntityTypewriter` | - (item?) | - |
| `TileEntityWeaponCase` | Weapon Case | `Items[1]`, `locked` |
| `TileEntityWeaponRack` | Weapon Rack | `Items[2]` |
| `TileEntityWritingDesk` | Writing Desk | `Items[]`, `pages` |

---

## Itemy

### Narzędzia i utility

| Item | Klasa | Funkcjonalność |
|------|-------|----------------|
| Tape Measure | `TapeMeasure` | Mierzenie odległości, tworzenie waypointów |
| Reading Glasses | `ItemReadingGlasses` | Pokazuje info o blokach BC |
| Tinted Glasses | `ItemReadingGlasses` | Jak wyżej, inny kolor |
| Monocle | `ItemReadingGlasses` | Jak wyżej, styl monocle |
| Screw Gun | `ItemDrill` | Narzędzie (creative-only?) |
| Hand Drill | `ItemHandDrill` | Wiertło ręczne |
| Plumb Line | `ItemPlumbLine` | Sprawdzanie pionowości |

### Nawigacja

| Item | Klasa | Funkcjonalność |
|------|-------|----------------|
| Waypoint Compass | `ItemWaypointCompass` | Kompas z waypointami z Atlasu |
| Death Compass | `ItemDeathCompass` | Wskazuje miejsce śmierci gracza |
| Atlas | `ItemAtlas` | Książkowa mapa z waypointami |

### Druk

| Item | Klasa | Funkcjonalność |
|------|-------|----------------|
| Print Press Chase | `ItemChase` | Komponent do druku |
| Print Press Plate | `ItemPlate` | Płyta z treścią książki |
| Enchanted Plate | `ItemEnchantedPlate` | Płyta z enchantowanym tekstem |

### Inne

| Item | Klasa | Funkcjonalność |
|------|-------|----------------|
| Redstone Book | `ItemRedstoneBook` | Daje sygnał RS gdy w Bookcase |
| Clipboard | `ItemClipboard` | Lista zadań (zaznaczanie) |
| Lock and Key | `ItemLock` | Zamykanie skrzyń i gablot |
| Slotted Book | `ItemSlottedBook` | Książka z miejscem na przedmiot |
| Stockroom Catalog | `ItemStockroomCatalog` | Katalog magazynu |
| Painting Canvas | `ItemPaintingCanvas` | Płótno do obrazów |
| Framing Saw | `ItemFramingSaw` | Crafting component |
| Framing Board | `ItemFramingBoard` | Crafting component |
| Framing Sheet | `ItemFramingSheet` | Crafting component |
| Seat Back* | `ItemSeatBack1-5` | Oparcia krzeseł (5 typów) |
| Big Book | `ItemBigBook` | Duża książka do pisania |
| Recipe Book | `ItemRecipeBook` | Książka receptur |

---

## Metadata i warianty

### Warianty drewna

Wiele bloków BC ma warianty dla różnych typów drewna:
- 0: Oak
- 1: Spruce
- 2: Birch
- 3: Jungle
- 4: Acacia
- 5: Dark Oak

### Framed wersje

Niektóre bloki mają wersje "Framed" (ramkowe):
- Framed Chest
- Framed Bookcase
- Framed Shelf
- itp.

Te wersje pozwalają na zmianę tekstury przez Furniture Paneler.

---

## ID bloków (1.7.10)

```
BiblioCraft:Bookcase
BiblioCraft:BookcaseCreative
BiblioCraft:ArmorStand
BiblioCraft:WeaponCase
BiblioCraft:PotionShelf
BiblioCraft:WeaponRack
BiblioCraft:Shelf
BiblioCraft:Label
BiblioCraft:WritingDesk
BiblioCraft:TypesettingTable
BiblioCraft:PrintingPress
BiblioCraft:Table
BiblioCraft:Seat
BiblioCraft:Clock
BiblioCraft:Lantern
BiblioCraft:Lamp
BiblioCraft:FancySign
BiblioCraft:FancyWorkbench
BiblioCraft:Painting
BiblioCraft:MapFrame
BiblioCraft:SwordPedestal
BiblioCraft:BlockStuff
BiblioCraft:FramedChest
BiblioCraft:Bell
BiblioCraft:Clipboard
BiblioCraft:IronLantern
BiblioCraft:IronLamp
BiblioCraft:PaintingFrameBorderless
BiblioCraft:PaintingFrameFancy
BiblioCraft:PaintingFrameFlat
BiblioCraft:PaintingFrameMiddle
BiblioCraft:PaintingFrameSimple
```

---

## Uwagi dla konwersji

1. **Metadata system** - 1.7.10 używa metadata (0-15) do rozróżniania wariantów
2. **Custom rendering** - wiele bloków ma customowe renderery (ISimpleBlockRenderingHandler)
3. **NBT storage** - wszystkie TE używają standardowego NBT z Forge
4. **Inventory handling** - implementacja IInventory
5. **Locking system** - niektóre bloki (WeaponCase, FramedChest) obsługują Lock and Key
