# Analiza ForgeMultipart / CB Multipart — Zadanie 1

> **Mod źródłowy 1.7.10:** ForgeMultipart 1.2.0.345 (zawiera ForgeMultipart + McMultipart + ForgeMicroblock)
> **Mod docelowy 1.18.2:** CB Multipart (continuation, modid `cb_multipart` + `microblockcbe`)
> **Data analizy:** 2026-05-19
> **Skill:** analyze_and_summarize_sc

---

## 1.7.10 — Bloki

### BlockMultipart (multipart:block)
- **Typ:** Block
- **Wersja:** 1.7.10
- **Registry names:**
  - Block registry: `"ForgeMultipart:block"`
  - **Ma prefiks moda:** TAK
- **Klasa Java:** `codechicken.multipart.BlockMultipart`
- **Opis działania:** Jeden uniwersalny blok kontenera, który zastępuje zwykłe bloki w świecie gdy w danym block-space znajdują się "part-y" (części). BlockMultipart nie ma własnej tekstury — całe renderowanie, kolizje, redstone i zachowanie są delegowane do zawartych w nim `TMultiPart`. Blok ten jest niewidoczny w creative tab (rejestracja z `null` ItemBlock). Każdy block-space z partami ma przypisany TileMultipart.
- **Dowody z internetu:**
  - Modrinth/CB Multipart — opisuje się jako "An opensource library for having multiple things in one block space" (dawniej ForgeMultipart).
  - Chicken-Bones/ForgeMultipart na GitHub — "An API for dynamically handling different functional parts in the one block space."
- **Dowód z kodu (rejestracja):**
  - Plik: `MultipartProxy_serverImpl` (wewnątrz zdekompilowanego JAR ForgeMultipart-1.7.10-1.2.0.345-universal.jar)
  - Snippet:
    ```java
    GameRegistry.registerBlock(new BlockMultipart().func_149663_c("multipart"), null, "block");
    this.block_$eq((BlockMultipart)Block.field_149771_c.func_82594_a("ForgeMultipart:block"));
    ```
- **Dowód z kodu (logika):**
  - Plik: `codechicken/multipart/BlockMultipart.class` (dekompilacja Vineflower)
  - Snippet delegacji kolizji:
    ```java
    public boolean func_149747_d(IBlockAccess world, int x, int y, int z, int side) {
        TileMultipart var6 = BlockMultipart$.MODULE$.getTile(world, x, y, z);
        boolean var7;
        if (var6 == null) {
            var7 = false;
        } else {
            var7 = var6.isSolid(side);
        }
        return var7;
    }
    ```

### McBlockPart (bloki vanilla jako part-y)
- **Typ:** Block / Part (wewnętrzny)
- **Wersja:** 1.7.10
- **Registry names:**
  - Nie są rejestrowane jako osobne bloki — działają jako `TMultiPart` wewnątrz `BlockMultipart`.
  - Factory rejestracji partów odbywa się przez `MultiPartRegistry.registerParts` i `registerConverter`.
- **Klasy Java:**
  - `codechicken.multipart.minecraft.TorchPart`
  - `codechicken.multipart.minecraft.RedstoneTorchPart`
  - `codechicken.multipart.minecraft.ButtonPart`
  - `codechicken.multipart.minecraft.LeverPart`
  - `codechicken.multipart.minecraft.McBlockPart`
  - `codechicken.multipart.minecraft.McMetaPart`
  - `codechicken.multipart.minecraft.McSidedMetaPart`
- **Opis działania:** Moduł `McMultipart` (modid `McMultipart`) dostarcza multipartowe odpowiedniki niektórych bloków vanilla: pochodni, pochodni redstone, przycisku, dźwigni. Dzięki temu można umieścić np. pochodnię na ścianie razem z kablem ProjectRed w tym samym block-space. Te elementy nie są osobnymi blokami w rejestrze bloków — są tworzone jako `TMultiPart` i zapisywane w NBT `TileMultipart`.
- **Dowody z internetu:**
  - mcmod.info w JAR ForgeMultipart: `"McMultipart"`, `"Minecraft Multipart Plugin"`, `"Provides multipart versions of some vanilla blocks like torches and buttons."`
- **Dowód z kodu (lista klas):**
  - Plik: struktura JAR ForgeMultipart-1.7.10-1.2.0.345-universal.jar
  - Klasy w pakiecie `codechicken.multipart.minecraft.*`:
    ```
    TorchPart, RedstoneTorchPart, ButtonPart, LeverPart,
    McBlockPart, McMetaPart, McSidedMetaPart
    ```

### Mikrobloki (ForgeMicroblock)
- **Typ:** Item / Part (nie Block)
- **Wersja:** 1.7.10
- **Registry names (items):**
  - Item microblock: `"microblock"` (rejestracja w ForgeMicroblock; w grze prefiks moda to `ForgeMicroblock:microblock` lub `microblock:microblock` w zależności od kontekstu)
  - Item sawStone: `"sawStone"`
  - Item sawIron: `"sawIron"`
  - Item sawDiamond: `"sawDiamond"`
  - Item stoneRod: `"stoneRod"`
- **Klasy Java:**
  - `codechicken.microblock.ItemMicroPart`
  - `codechicken.microblock.ItemSaw`
  - `codechicken.microblock.CommonMicroblock`, `CornerMicroblock`, `EdgeMicroblock`, `FaceMicroblock`, `HollowMicroblock`, `PostMicroblock`
- **Opis działania:** Mikrobloki to części (parts) zajmujące ułamek block-space (np. płytka, róg, krawędź, słup, rura). Są tworzone przez piły (`ItemSaw`) z normalnych bloków. Każdy mikroblok przechowuje w NBT informację o materiale (`mat`) i klasie kształtu (` MicroblockClass` ID). Nie są to osobne bloki — renderują się jako part wewnątrz `TileMultipart`.
- **Dowód z kodu (rejestracja):**
  - Plik: `codechicken.microblock.handler.MicroblockMod` (dekompilacja)
  - Snippet:
    ```java
    this.itemMicro_$eq(new ItemMicroPart());
    GameRegistry.registerItem(this.itemMicro(), "microblock");
    this.sawStone_$eq(this.createSaw(MultipartProxy$.MODULE$.config(), "sawStone", 1));
    this.sawIron_$eq(this.createSaw(MultipartProxy$.MODULE$.config(), "sawIron", 2));
    this.sawDiamond_$eq(this.createSaw(MultipartProxy$.MODULE$.config(), "sawDiamond", 3));
    this.stoneRod_$eq(new Item().func_77655_b("microblock:stoneRod").func_111206_d("microblock:stoneRod"));
    GameRegistry.registerItem(this.stoneRod(), "stoneRod");
    ```

---

## 1.7.10 — Tile Entities

### TileMultipart
- **Typ:** TileEntity
- **Wersja:** 1.7.10
- **Registry name (do weryfikacji na mapie):**
  - Prawdopodobnie `"ForgeMultipart:TileMultipart"` lub `"TileMultipart"`
  - **Ma prefiks moda:** do weryfikacji (FML w 1.7.10 często rejestruje automatycznie jeśli nie podano jawnego stringa)
- **Klasa Java:** `codechicken.multipart.TileMultipart`
- **Opis działania:** Główne TileEntity przechowujące listę partów (`Seq<TMultiPart>`) w danym block-space. Zarządza dodawaniem, usuwaniem, kolizjami, redstone, zapisem/odczytem NBT oraz tickiem poszczególnych partów. W NBT zapisuje pod kluczem `"parts"` tablicę NBT z danymi każdego parta (w tym jego factory ID i stan). Jest to kluczowe TE dla całego ekosystemu multipartów — kable ProjectRed, rurki, mikrobloki itp. wszystkie żyją wewnątrz TileMultipart.
- **Dowód z kodu (logika):**
  - Plik: `codechicken/multipart/TileMultipart.class` (dekompilacja Vineflower)
  - Snippet pola i NBT:
    ```java
    public class TileMultipart extends TileEntity implements IChunkLoadTile {
       private Seq<TMultiPart> partList = (Seq<TMultiPart>).MODULE$.apply(scala.collection.immutable.Nil..MODULE$);
       private boolean doesTick = false;
       // ...
       public static TileMultipart createFromNBT(NBTTagCompound var0) {
          return TileMultipart$.MODULE$.createFromNBT(var0);
       }
    }
    ```
- **Uwaga:** W zdekompilowanym kodzie nie znaleziono jawnego `GameRegistry.registerTileEntity(TileMultipart.class, "...")` — rejestracja może odbywać się dynamicznie lub przez nazwę klasy. **Wymaga weryfikacji exact stringa na mapie .mca** (patrz Zadanie 4).

---

## 1.18.2 — Bloki

### BlockMultipart (cb_multipart:block)
- **Typ:** Block
- **Wersja:** 1.18.2
- **Registry names:**
  - Block registry: najprawdopodobniej `"cb_multipart:block"` (dokładna nazwa do potwierdzenia w kodzie źródłowym CB Multipart; w źródłach ProjectRed 1.18.2 import: `codechicken.multipart.block.BlockMultipart`)
  - **Ma prefiks moda:** TAK (`cb_multipart`)
- **Klasa Java:** `codechicken.multipart.block.BlockMultipart`
- **Opis działania:** Kontynuacja BlockMultipart z 1.7.10. Blok kontenera przechowujący wielokrotne `MultiPart` w jednym block-space. W 1.18.2 używa nowego systemu rejestracji Forge (`DeferredRegister` lub bezpośrednio `RegistryObject`). Renderowanie, kolizje, redstone i inne interakcje są delegowane do partów. W źródłach ProjectRed 1.18.2 widoczne importy i użycia `BlockMultipart` w logice propagacji sygnałów.
- **Dowody z internetu:**
  - TheCBProject/CBMultipart na GitHub: "Formely known as ForgeMultipart. An API for dynamically handling different functional parts in the one block space."
  - Modrinth (CB Multipart 1.18.2): mod działa jako biblioteka dla ProjectRed i innych modów.
- **Dowód z kodu (użycie w ProjectRed 1.18.2):**
  - Plik: `mod_src/118/actual_src/1.18.2/ProjectRed/repo/core/src/main/java/mrtjp/projectred/core/part/IConnectableCenterPart.java`
  - Snippet:
    ```java
    import codechicken.multipart.block.BlockMultipart;
    ```

### Microblock (microblockcbe:microblock)
- **Typ:** Item / Part
- **Wersja:** 1.18.2
- **Registry names:**
  - Item registry: `"microblockcbe:microblock"` (potwierdzone w issue trackerze CB Multipart dla wersji 1.12+/1.16+; w 1.18.2 zachowano konwencję)
  - **Ma prefiks moda:** TAK (`microblockcbe`)
- **Klasy Java (na podstawie kodu źródłowego 1.16+ i struktury):**
  - `codechicken.microblock.ItemMicroPart`
  - `codechicken.microblock.Microblock` (part class)
- **Opis działania:** Mikrobloki w 1.18.2 działają analogicznie jak w 1.7.10 — są partami wewnątrz BlockMultipart. Item `microblockcbe:microblock` przechowuje w NBT materiał (`mat`) i typ kształtu. Wspierane kształty to m.in.: Face (płytka), Hollow (rura), Corner (kant), Edge (krawędź), Post (słup). W 1.18.2 moduł mikrobloków jest wydzielony jako osobny mod (`microblockcbe`).
- **Dowody z internetu:**
  - Issue TheCBProject/CBMultipart #144: `Item Class: class codechicken.microblock.ItemMicroPart`, `Registry Name: microblockcbe:microblock`

---

## 1.18.2 — Block Entities

### TileMultipart (cb_multipart:tile_multipart lub podobna)
- **Typ:** BlockEntity
- **Wersja:** 1.18.2
- **Registry name (do potwierdzenia w kodzie źródłowym CB Multipart):**
  - Prawdopodobnie `"cb_multipart:tile_multipart"` lub `"cb_multipart:multipart"`
  - **Ma prefiks moda:** TAK
- **Klasa Java:** `codechicken.multipart.block.TileMultipart`
- **Opis działania:** Odpowiednik `TileMultipart` z 1.7.10 w nowym API BlockEntity. Przechowuje kolekcję `MultiPart` (obiektów partów), zarządza ich zapisem NBT, synchronizacją sieciową, kolizjami i redstone. W 1.18.2 wykorzystuje `BlockEntityType` do rejestracji. W kodzie ProjectRed 1.18.2 importowana jako `codechicken.multipart.block.TileMultipart` i używana do lookup partów w świecie.
- **Dowód z kodu (użycie w ProjectRed 1.18.2):**
  - Plik: `mod_src/118/actual_src/1.18.2/ProjectRed/repo/core/src/main/java/mrtjp/projectred/core/BundledSignalsLib.java`
  - Snippet:
    ```java
    import codechicken.multipart.block.TileMultipart;
    ```
  - Plik: `mod_src/118/actual_src/1.18.2/ProjectRed/repo/core/src/main/java/mrtjp/projectred/core/CenterLookup.java`
  - Użycie:
    ```java
    import codechicken.multipart.block.TileMultipart;
    ```

---

## Porównanie 1.7.10 vs 1.18.2

| Aspekt | 1.7.10 (ForgeMultipart) | 1.18.2 (CB Multipart) |
|--------|------------------------|----------------------|
| **Główny blok kontenera** | `ForgeMultipart:block` (`BlockMultipart`) | `cb_multipart:block` (`BlockMultipart`) |
| **Główne TE/BE kontenera** | `TileMultipart` | `TileMultipart` (teraz `BlockEntity`) |
| **API partów** | `TMultiPart` (Scala traits) | `MultiPart` (Java/Scala API) |
| **Mikrobloki** | Moduł `ForgeMicroblock` (w tym samym JAR) | Osobny mod `microblockcbe` |
| **Vanilla parts** | `McMultipart` (torch, lever, button) | Zachowane jako część API |
| **Rejestracja bloków** | `GameRegistry.registerBlock(...)` | `DeferredRegister` / `RegistryObject` |
| **Rejestracja TE/BE** | `GameRegistry.registerTileEntity(...)` (brak jawnej dla TileMultipart — dynamiczna?) | `BlockEntityType.Builder.of(...)` |
| **NBT partów** | Zapis wewnątrz `TileMultipart` pod `"parts"` | Zapis wewnątrz `TileMultipart` — format zmieniony |

### Kluczowe różnice konwersyjne
1. **Zmiana namespace:** `ForgeMultipart:` → `cb_multipart:` (oraz `microblock:` → `microblockcbe:` dla mikrobloków).
2. **TileEntity → BlockEntity:** W 1.18.2 `TileMultipart` stało się `BlockEntity`, co zmienia format zapisu w chunk NBT (sekcja `block_entities` zamiast `TileEntities`).
3. **Mikrobloki jako osobny mod:** W 1.7.10 mikrobloki były w tym samym JAR (ForgeMicroblock), w 1.18.2 to osobny mod `microblockcbe`.
4. **ID partów:** W 1.7.10 part-y używały fabryk z ID mapą zapisywaną w `MultiPartRegistry`. W 1.18.2 system rejestracji partów zmienił się na zasoby (resource locations) — konwersja NBT partów będzie wymagała mapowania starych ID na nowe `ResourceLocation`.

---

## Tabela podsumowująca nazwy rejestracji

| Element | Klasa Java | Registry String (1.7.10) | Registry String (1.18.2) | Ma prefiks? |
|---------|-----------|-------------------------|--------------------------|-------------|
| BlockMultipart | `codechicken.multipart.BlockMultipart` | `ForgeMultipart:block` | `cb_multipart:block` | TAK |
| TileMultipart | `codechicken.multipart.TileMultipart` | `"TileMultipart"` (do weryfikacji) | `cb_multipart:tile_multipart` (do potwierdzenia) | TAK |
| ItemMicroPart | `codechicken.microblock.ItemMicroPart` | `microblock` / `ForgeMicroblock:microblock` | `microblockcbe:microblock` | TAK |
| Saw Stone | `codechicken.microblock.ItemSaw` | `sawStone` | — | TAK |
| Saw Iron | `codechicken.microblock.ItemSaw` | `sawIron` | — | TAK |
| Saw Diamond | `codechicken.microblock.ItemSaw` | `sawDiamond` | — | TAK |
| Stone Rod | `codechicken.microblock.Item` (anonymous) | `stoneRod` | — | TAK |
| TorchPart | `codechicken.multipart.minecraft.TorchPart` | part factory ID (dynamiczne) | part RL (dynamiczne) | N/A (part) |
| RedstoneTorchPart | `codechicken.multipart.minecraft.RedstoneTorchPart` | part factory ID (dynamiczne) | part RL (dynamiczne) | N/A (part) |
| ButtonPart | `codechicken.multipart.minecraft.ButtonPart` | part factory ID (dynamiczne) | part RL (dynamiczne) | N/A (part) |
| LeverPart | `codechicken.multipart.minecraft.LeverPart` | part factory ID (dynamiczne) | part RL (dynamiczne) | N/A (part) |
| CommonMicroblock | `codechicken.microblock.CommonMicroblock` | part factory ID + `mat` NBT | part RL + `mat` NBT | N/A (part) |
| CornerMicroblock | `codechicken.microblock.CornerMicroblock` | part factory ID + `mat` NBT | part RL + `mat` NBT | N/A (part) |
| EdgeMicroblock | `codechicken.microblock.EdgeMicroblock` | part factory ID + `mat` NBT | part RL + `mat` NBT | N/A (part) |
| FaceMicroblock | `codechicken.microblock.FaceMicroblock` | part factory ID + `mat` NBT | part RL + `mat` NBT | N/A (part) |
| HollowMicroblock | `codechicken.microblock.HollowMicroblock` | part factory ID + `mat` NBT | part RL + `mat` NBT | N/A (part) |
| PostMicroblock | `codechicken.microblock.PostMicroblock` | part factory ID + `mat` NBT | part RL + `mat` NBT | N/A (part) |

---

## Uwagi i otwarte kwestie

1. **Exact string rejestracji TileMultipart 1.7.10** — Nie znaleziono jawnego `registerTileEntity` w zdekompilowanym kodzie. Prawdopodobnie FML używa nazwy klasy lub jest ona rejestrowana dynamicznie przez ASM. **Wymaga weryfikacji na surowych danych mapy .mca** (Zadanie 4).
2. **Exact string rejestracji TileMultipart 1.18.2** — Brak dostępnego kodu źródłowego CB Multipart 1.18.2 w `mod_src/118` (tylko binaria ProjectRed). **Wymaga pobrania źródeł CB Multipart lub dekompilacji JAR 1.18.2**.
3. **Part factory ID mapping** — W 1.7.10 part-y używają numerycznych/string ID z `MultiPartRegistry`. W 1.18.2 part-y używają `ResourceLocation`. Konwersja NBT partów wymaga znajomości mapowania starych ID → nowe RL.
4. **Mikrobloki — materiały** — W 1.7.10 materiał mikrobloku zapisywany jest jako string `"mat"` w NBT (np. `"minecraft:stone"`). W 1.18.2 prawdopodobnie zachowano ten sam klucz, ale format może się różnić.

---

## Następne kroki (Zadanie 2)

- Przygotowanie symulacji działania multipartów w Pythonie (np. symulacja dodawania/usuwania partów z TileMultipart, kolizje, redstone).
- Symulacja mikrobloków: tworzenie z materiału, placement grid, NBT.
- Symulacja porównawcza 1.7.10 vs 1.18.2 dla kluczowych scenariuszy (kabel + mikroblok w tym samym block-space).
