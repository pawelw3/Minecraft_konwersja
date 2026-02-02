# Handoff: BiblioCraft - Zadanie 2 (Symulacje działania)

## Podsumowanie sesji

Wykonano symulacje działania kluczowych funkcjonalności docelowych modów dla konwersji BiblioCraft 1.7.10 → 1.18.2:

1. **FramedBlocks** - system "camo" (tekstury na blokach)
2. **Immersive Paintings** - system customowych obrazów
3. **Supplementaries** - inventory w block entities (Item Shelf, Book Pile, Jar)

---

## Ukończono

- [x] Analiza kodu FramedBlocks (FramedBlockEntity, camo system)
- [x] Analiza kodu Immersive Paintings (PaintingEntity, PaintingManager)
- [x] Analiza kodu Supplementaries (BookPile, ItemShelf, Jar)
- [x] Symulacja FramedBlocks - system przechowywania tekstur
- [x] Symulacja konwersji BC Furniture → FramedBlocks
- [x] Symulacja Immersive Paintings - system obrazów
- [x] Symulacja konwersji BC Paintings → Immersive Paintings
- [x] Symulacja Supplementaries - inventory management
- [x] Symulacja konwersji BC Bookcase/Shelf/Jar → Supplementaries
- [x] Testy round-trip (zapis → odczyt NBT)

---

## Nowe pliki

| Plik | Opis |
|------|------|
| `src/converters/bibliocraft/__init__.py` | Pakiet Python z eksportami |
| `src/converters/bibliocraft/simulation_framedblocks.py` | Symulacja FramedBlocks (1100+ linii kodu) |
| `src/converters/bibliocraft/simulation_immersive_paintings.py` | Symulacja Immersive Paintings |
| `src/converters/bibliocraft/simulation_supplementaries.py` | Symulacja Supplementaries |

---

## Symulacja 1: FramedBlocks - System "camo"

### Kluczowe klasy (z kodu źródłowego)

```java
// FramedBlockEntity.java (xfacthd.framedblocks.api.block)
public class FramedBlockEntity extends BlockEntity {
    private ItemStack camoStack = ItemStack.EMPTY;
    private BlockState camoState = Blocks.AIR.defaultBlockState();
    private boolean glowing = false;
    private boolean intangible = false;
    private boolean reinforced = false;
    
    // NBT serialization
    @Override
    public void saveAdditional(CompoundTag nbt) {
        nbt.put("camo_stack", camoStack.save(new CompoundTag()));
        nbt.put("camo_state", NbtUtils.writeBlockState(camoState));
        nbt.putBoolean("glowing", glowing);
        nbt.putBoolean("intangible", intangible);
        nbt.putBoolean("reinforced", reinforced);
    }
}
```

### Symulacja Python (nasza implementacja)

```python
@dataclass
class FramedBlockEntity:
    pos: Tuple[int, int, int]
    shape: FramedShape  # Enum: BLOCK, SLAB, STAIRS, etc.
    camo_stack: Optional[ItemStack] = None  # ItemStack użyty jako tekstura
    camo_state: Optional[BlockState] = None  # BlockState jako tekstura
    glowing: bool = False
    intangible: bool = False
    reinforced: bool = False
```

### Mapowanie NBT

| BiblioCraft 1.7.10 | FramedBlocks 1.18.2 | Opis |
|-------------------|---------------------|------|
| `frameTexture: String` | `camo_state: CompoundTag` | BC: ID tekstury jako String<br>FB: BlockState jako CompoundTag |
| - | `camo_stack: CompoundTag` | FB: ItemStack (dla dropów) |
| - | `glowing: boolean` | FB: czy blok świeci |
| - | `intangible: boolean` | FB: czy niematerialny |
| - | `reinforced: boolean` | FB: czy wzmocniony |

### Test symulacji (wynik)

```
[Konwersja BC -> FramedBlocks]
  BC block: FramedChest
  BC texture: minecraft:planks:0
  -> FramedBlocks shape: framed_chest
  -> Camo state: minecraft:oak_planks
  [FramedBlock] Ustawiono camo: minecraft:oak_planks
  
NBT: {
  "shape": "framed_chest",
  "glowing": false,
  "intangible": false,
  "reinforced": false,
  "camo_stack": {"id": "minecraft:oak_planks", "Count": 1},
  "camo_state": {"Name": "minecraft:oak_planks", "Properties": {}}
}
```

### Mapowanie mebli BC na kształty FramedBlocks

| Mebel BC | FramedBlocks Shape | Uwagi |
|----------|-------------------|-------|
| FramedChest | `framed_chest` | Skrzynia |
| FramedBookcase | `framed_block` | Brak dedykowanego |
| FramedShelf | `framed_slab` | Półka |
| FramedTable | `framed_block` | Stół |
| FramedDoor | `framed_door` | Drzwi |
| FramedTrapDoor | `framed_trapdoor` | Klapa |
| FramedFence | `framed_fence` | Płot |
| FramedSign | `framed_sign` | Znak |
| ... | ... | ... (100+ wariantów) |

---

## Symulacja 2: Immersive Paintings

### Kluczowe klasy (z kodu źródłowego)

```java
// ImmersivePaintingEntity.java
public class ImmersivePaintingEntity extends AbstractImmersiveDecorationEntity {
    private Identifier motive = Main.locate("none");
    private Identifier frame = Main.locate("none");
    private Identifier material = Main.locate("none");
    private int width = 1;
    private int height = 1;
    
    @Override
    public void writeCustomDataToNbt(NbtCompound nbt) {
        nbt.putString("Motive", motive.toString());
        nbt.putString("Frame", frame.toString());
        nbt.putString("Material", material.toString());
    }
}

// PaintingManager - zarządzanie obrazami
public class ServerPaintingManager {
    private Map<String, PaintingData> paintings;
    // Obrazy są identyfikowane przez nazwę (Identifier)
    // Przechowywane na serwerze, wysyłane do klientów
}
```

### Symulacja Python

```python
@dataclass
class ImmersivePaintingEntity:
    pos: Tuple[int, int, int]
    facing: str = "north"
    rotation: int = 0
    motive: str = "immersive_paintings:none"  # ID obrazu
    frame: str = "immersive_paintings:classic"
    material: str = "immersive_paintings:wood"
    
@dataclass
class PaintingData:
    name: str  # ID obrazu
    width: int  # w blokach
    height: int  # w blokach
    author: str = "unknown"
    image_hash: str = ""  # hash MD5
```

### Mapowanie NBT

| BiblioCraft 1.7.10 | Immersive Paintings 1.18.2 | Opis |
|-------------------|---------------------------|------|
| `resourceLocation: String` | `Motive: String` | BC: ścieżka do pliku<br>IP: ID obrazu (np. "immersive_paintings:bc_sunset") |
| `paintingType: String` | - | BC: typ obrazu (custom/predef) |
| - | `Frame: String` | IP: styl ramki |
| - | `Material: String` | IP: materiał ramki |
| - | `width/height: int` | IP: rozmiar (auto z PaintingData) |

### Test symulacji (wynik)

```
[Konwersja BC Painting -> Immersive Paintings]
  BC resource: bibliocraft:paintings/custom/sunset_32x32.png
  -> IP name: bc_converted_sunset_32x32
  -> Rozmiar: 2x2 bloków
  [PaintingManager] Zarejestrowano obraz: bc_converted_sunset_32x32
    Rozmiar: 2x2, Hash: 99a15508
  [ImmersivePainting] Ustawiono obraz: bc_converted_sunset_32x32

NBT: {
  "Pos": [100, 65, 200],
  "Facing": "north",
  "Rotation": 0,
  "Motive": "immersive_paintings:bc_converted_sunset_32x32",
  "Frame": "immersive_paintings:classic",
  "Material": "immersive_paintings:wood"
}
```

### Strategia konwersji obrazów

1. **Ekstrakcja nazwy** z `resourceLocation` BC:
   - BC: `"bibliocraft:paintings/custom/sunset.png"`
   - IP: `"bc_converted_sunset"`

2. **Określenie rozmiaru** z nazwy pliku lub metadanych:
   - `"sunset_32x32.png"` → 2×2 bloki (32/16 = 2)

3. **Rejestracja w PaintingManager**:
   - Przechowuje `PaintingData` (metadata)
   - Przechowuje `image_bytes` (dane binarne)
   - Oblicza hash dla weryfikacji

4. **Upload do modu**:
   - Wymaga implementacji protokołu sieciowego
   - Lub manualnego dodania do folderu modu

---

## Symulacja 3: Supplementaries - Inventory

### Kluczowe klasy (z kodu źródłowego)

```java
// BookPileBlockTile (Supplementaries)
public class BookPileBlockTile extends BlockEntity {
    private NonNullList<ItemStack> items = NonNullList.withSize(4, ItemStack.EMPTY);
    private boolean horizontal = false;
    
    @Override
    protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        ContainerHelper.saveAllItems(tag, this.items);
        tag.putBoolean("horizontal", horizontal);
    }
}
```

### Symulacja Python

```python
@dataclass
class BookPileBlockEntity:
    pos: Tuple[int, int, int]
    items: List[ItemStack] = field(default_factory=list)  # 4 sloty
    horizontal: bool = False
    MAX_SLOTS = 4

class ContainerHelper:
    @staticmethod
    def save_all_items(nbt: Dict, items: List[ItemStack]) -> Dict:
        items_list = []
        for slot, item in enumerate(items):
            if not item.is_empty():
                item_nbt = item.to_nbt()
                item_nbt["Slot"] = slot
                items_list.append(item_nbt)
        nbt["Items"] = items_list
        return nbt
```

### Konwersja Bookcase → Book Pile

```
[Konwersja BC Bookcase -> Supplementaries Book Pile]
  BC Bookcase: 10 książek (max 16)
    Przeniesiono: minecraft:book_0 x1 (z slotu BC 0)
    Przeniesiono: minecraft:book_1 x1 (z slotu BC 1)
    Przeniesiono: minecraft:book_2 x1 (z slotu BC 2)
    Przeniesiono: minecraft:book_3 x1 (z slotu BC 3)
  UWAGA: 6 książek nie zmieściło się! Wymaga dodatkowego storage.
  -> Book Pile: 4/4 książek
```

**Problem:** Bookcase ma 16 slotów, Book Pile tylko 4.
**Rozwiązanie:** 
- Pierwsze 4 książki → Book Pile
- Pozostałe → vanilla chest lub dodatkowe Book Pile

### Konwersja Shelf → Item Shelf

```
[Konwersja BC Shelf -> Supplementaries Item Shelf]
  BC Shelf: 4 sloty
    Przeniesiono slot 0: minecraft:diamond_sword x1
    Przeniesiono slot 1: minecraft:apple x16
    Przeniesiono slot 3: minecraft:book x3
  -> Item Shelf: ItemShelfBlockEntity(3/4 slotów zajętych)
```

**Uwaga:** Prawie 1:1 konwersja - obie mają 4 sloty.

### Konwersja Cookie Jar → Jar

```
[Konwersja BC Cookie Jar -> Supplementaries Jar]
    Przeniesiono: minecraft:cookie x8
    Przeniesiono: minecraft:cookie x8
    Przeniesiono: minecraft:cookie x8
  -> Jar: 3/4 slotów
```

**Różnica:** BC Cookie Jar tylko ciastka, Supplementaries Jar dowolne przedmioty.

---

## Kluczowe wnioski dla implementacji

### 1. FramedBlocks

**Camo State Conversion:**
```python
def convert_bc_texture_to_camo_state(bc_texture: str) -> BlockState:
    # BC: "minecraft:planks:0" (metadata)
    # FB: BlockState z Name i Properties
    texture_map = {
        "minecraft:planks:0": "minecraft:oak_planks",
        "minecraft:planks:1": "minecraft:spruce_planks",
        # ...
    }
    block_id = texture_map.get(bc_texture, bc_texture)
    return BlockState(block_id)
```

**NBT Format:**
- `camo_state.Name` - String (ID bloku)
- `camo_state.Properties` - Dict (właściwości BlockState)
- `camo_stack` - ItemStack (dla dropów)

### 2. Immersive Paintings

**Image Registration:**
```python
def register_bc_image(bc_path: str, image_bytes: bytes) -> str:
    # Wydobyć nazwę
    image_name = bc_path.split("/")[-1].replace(".png", "")
    ip_name = f"bc_converted_{image_name}"
    
    # Określić rozmiar
    width, height = extract_size(bc_path)  # z nazwy lub metadanych
    
    # Zarejestrować
    painting_manager.register(ip_name, width, height, image_bytes)
    return ip_name
```

**NBT Format:**
- `Motive` - String (ID obrazu)
- `Frame` - String (styl ramki)
- `Material` - String (materiał ramki)

### 3. Supplementaries

**Inventory Conversion:**
```python
def convert_bookcase_to_piles(bc_bookcase: BCBookcaseTE) -> List[BookPileBlockEntity]:
    """
    Bookcase (16 slotów) -> 4× Book Pile (4 sloty każdy)
    """
    piles = []
    current_pile = BookPileBlockEntity()
    
    for book in bc_bookcase.items:
        if not current_pile.add_book(book):
            piles.append(current_pile)
            current_pile = BookPileBlockEntity()
            current_pile.add_book(book)
    
    return piles
```

**NBT Format:**
- `Items` - List[CompoundTag] (z polem Slot)
- `horizontal` - bool (dla Book Pile)

---

## Następne kroki (Zadanie 3)

1. **Implementacja konwerterów NBT:**
   - Napisać kod konwersji NBT z formatu BC 1.7.10 na 1.18.2
   - Obsługa edge cases (brakujące tekstury, nieprawidłowe ID)

2. **Mapowanie tekstur:**
   - Rozszerzyć `WOOD_TEXTURE_MAP` o wszystkie bloki z BC
   - Obsłużyć niestandardowe tekstury (np. z innych modów)

3. **System obrazów:**
   - Zaimplementować upload obrazów do Immersive Paintings
   - Obsłużyć synchronizację (multiplayer)

4. **Testy na mapie:**
   - Sprawdzić które bloki BC są faktycznie używane na mapie
   - Zweryfikować konwersję dla rzeczywistych danych

---

## Testy round-trip

Wszystkie symulacje przeszły testy round-trip:

| Moduł | Test | Wynik |
|-------|------|-------|
| FramedBlocks | Zapis → Odczyt NBT | ✅ Zgodność 100% |
| Immersive Paintings | Zapis → Odczyt NBT | ✅ Zgodność 100% |
| Supplementaries | Zapis → Odczyt NBT | ✅ Zgodność 100% |

---

**Status:** ✅ Zadanie 2 ukończone - gotowe do przeglądu  
**Data:** 2026-02-02  
**Agent:** AI Konwersji BiblioCraft
