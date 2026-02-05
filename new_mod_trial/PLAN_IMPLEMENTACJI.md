# Plan implementacji moda "Cuttable Blocks" dla Minecraft 1.7.10 Forge

## 1. Przegląd koncepcji

Mod dodaje możliwość przycinania dowolnego bloku z gry (vanilla + inne mody) płaszczyzną przechodzącą przez geometryczny środek bloku. Płaszczyzna jest prostopadła do kierunku patrzenia gracza (view direction).

### 1.1 Zasada działania

1. Gracz trzyma specjalne narzędzie (Cutting Tool)
2. Klikając PPM na dowolny blok, zapisujemy oryginalny blok w Tile Entity
3. Oryginalny blok jest zastępowany naszym blokiem z Tile Entity
4. Tile Entity przechowuje:
   - ID oryginalnego bloku (Block + metadata)
   - Normalizowany wektor płaszczyzny cięcia (nx, ny, nz)
   - Stronę zachowaną po cięciu (positive/negative względem płaszczyzny)

### 1.2 Geometria cięcia

- Płaszczyzna zawsze przechodzi przez środek bloku (0.5, 0.5, 0.5)
- Wektor normalny płaszczyzny = wektor kierunku patrzenia gracza (znormalizowany)
- Płaszczyzna dzieli sześcian na dwie części - zachowujemy tę, w której jest gracz

## 2. Architektura

### 2.1 Struktura pakietów

```
com.cuttableblocks
├── CuttableBlocksMod.java          # Główna klasa moda
├── blocks
│   ├── BlockCuttable.java           # Blok reprezentujący przycięty blok
│   └── ModBlocks.java               # Rejestracja bloków
├── tileentities
│   ├── TileEntityCuttable.java      # TE przechowujące dane cięcia
│   └── ModTileEntities.java         # Rejestracja TE
├── items
│   ├── ItemCuttingTool.java         # Narzędzie do cięcia
│   └── ModItems.java                # Rejestracja itemów
├── client
│   ├── CuttableBlockRenderer.java   # Custom renderer (ISimpleBlockRenderingHandler)
│   └── ClientProxy.java             # Proxy po stronie klienta
├── common
│   └── CommonProxy.java             # Proxy wspólne
├── network
│   └── CuttableSyncPacket.java      # Pakiet synchronizacji TE (opcjonalnie)
└── util
    ├── Plane.java                   # Klasa pomocnicza dla płaszczyzny
    └── BlockSnapshot.java           # Snapshot bloku (ID + meta)
```

### 2.2 Kluczowe klasy

#### TileEntityCuttable.java

```java
public class TileEntityCuttable extends TileEntity {
    private Block originalBlock;      // Oryginalny blok
    private int originalMetadata;     // Metadata oryginalnego bloku
    private float normalX, normalY, normalZ;  // Wektor normalny płaszczyzny (znormalizowany)
    private boolean keepPositiveSide; // Którą stronę zachowujemy
    
    // Gettery, settery, NBT read/write
    // Packet synchronization dla klienta
}
```

#### BlockCuttable.java

```java
public class BlockCuttable extends BlockContainer {
    
    // Zachowujemy properties oryginalnego bloku (hardness, light, etc.)
    // Ale dodajemy własną logikę renderowania i kolizji
    
    @Override
    public void setBlockBoundsBasedOnState(IBlockAccess world, int x, int y, int z) {
        // Ustawienie bounding boxa zależnie od płaszczyzny cięcia
        // Dla uproszczenia możemy użyć pełnego boxa lub przybliżenia
    }
    
    @Override
    public int getRenderType() {
        return CUTTABLE_RENDER_ID;  // Custom renderer
    }
    
    @Override
    public boolean isOpaqueCube() {
        return false;  // Zawsze przezroczysty (ma dziury)
    }
    
    @Override
    public boolean renderAsNormalBlock() {
        return false;
    }
    
    // Dodatkowo: raytracing dla nietypowej geometrii
}
```

## 3. Implementacja - szczegóły

### 3.1 Cutting Tool (ItemCuttingTool.java)

```java
public class ItemCuttingTool extends Item {
    
    @Override
    public boolean onItemUse(ItemStack stack, EntityPlayer player, World world, 
                             int x, int y, int z, int side, 
                             float hitX, float hitY, float hitZ) {
        if (world.isRemote) return true;
        
        Block targetBlock = world.getBlock(x, y, z);
        int targetMeta = world.getBlockMetadata(x, y, z);
        
        // Nie tnijmy już przyciętych bloków ani aira/bedrocka
        if (targetBlock == ModBlocks.blockCuttable || targetBlock == Blocks.air 
            || targetBlock == Blocks.bedrock) {
            return false;
        }
        
        // Pobierz kierunek patrzenia gracza
        Vec3 lookVec = player.getLookVec();
        
        // Znormalizuj wektor (już powinien być znormalizowany, ale dla pewności)
        double len = Math.sqrt(lookVec.xCoord * lookVec.xCoord 
                             + lookVec.yCoord * lookVec.yCoord 
                             + lookVec.zCoord * lookVec.zCoord);
        
        float nx = (float)(lookVec.xCoord / len);
        float ny = (float)(lookVec.yCoord / len);
        float nz = (float)(lookVec.zCoord / len);
        
        // Określ którą stronę zachować (gdzie jest gracz względem środka bloku)
        double dx = player.posX - (x + 0.5);
        double dy = player.posY + player.getEyeHeight() - (y + 0.5);
        double dz = player.posZ - (z + 0.5);
        
        // Dot product: jeśli dodatni, gracz jest po stronie dodatniej
        boolean keepPositive = (dx * nx + dy * ny + dz * nz) > 0;
        
        // Zapisz oryginalny blok
        TileEntityCuttable.saveOriginalBlock(world, x, y, z, targetBlock, targetMeta, 
                                             nx, ny, nz, keepPositive);
        
        // Zastąp blokiem Cuttable
        world.setBlock(x, y, z, ModBlocks.blockCuttable, 0, 3);
        
        // Ustaw dane w TE
        TileEntity te = world.getTileEntity(x, y, z);
        if (te instanceof TileEntityCuttable) {
            ((TileEntityCuttable) te).setCutData(targetBlock, targetMeta, nx, ny, nz, keepPositive);
        }
        
        world.markBlockForUpdate(x, y, z);
        return true;
    }
}
```

### 3.2 Renderowanie (RenderCuttableBlock.java)

W 1.7.10 używamy `ISimpleBlockRenderingHandler`:

```java
public class CuttableBlockRenderer implements ISimpleBlockRenderingHandler {
    
    public static final int RENDER_ID = RenderingRegistry.getNextAvailableRenderId();
    
    @Override
    public void renderInventoryBlock(Block block, int metadata, int modelId, 
                                      RenderBlocks renderer) {
        // Render domyślny dla inventory
    }
    
    @Override
    public boolean renderWorldBlock(IBlockAccess world, int x, int y, int z, 
                                    Block block, int modelId, RenderBlocks renderer) {
        TileEntity te = world.getTileEntity(x, y, z);
        if (!(te instanceof TileEntityCuttable)) return false;
        
        TileEntityCuttable cutTE = (TileEntityCuttable) te;
        
        // Pobierz oryginalny renderer
        Block original = cutTE.getOriginalBlock();
        if (original == null) return false;
        
        // Rysujemy oryginalny blok, ale z clippingiem (OpenGL clipping planes)
        // lub custom mesh - to jest najtrudniejsza część
        
        return renderCutBlock(renderer, original, cutTE, x, y, z);
    }
    
    private boolean renderCutBlock(RenderBlocks rb, Block original, 
                                    TileEntityCuttable te, int x, int y, int z) {
        
        // Opcja 1: Użyj Tessellator i rysuj custom mesh
        // Opcja 2: Użyj OpenGL clipping planes
        
        // Dla uproszczenia - rysujemy polygony które tworzą połowę sześcianu
        // wyciętą płaszczyzną
        
        Tessellator tess = Tessellator.instance;
        
        // Oblicz wierzchołki przecięcia płaszczyzny z krawędziami sześcianu
        // Sześcian ma 12 krawędzi, płaszczyzna może przeciąć 3-6 z nich
        
        List<Vec3> intersectionPoints = calculateIntersections(
            te.getNormalX(), te.getNormalY(), te.getNormalZ(), 
            te.keepPositiveSide()
        );
        
        // Rysuj oryginalne tekstury na wyciętej geometrii
        // To wymaga podzielenia każdej ściany oryginalnego bloku
        // na fragmenty po przecięciu z płaszczyzną
        
        return true;
    }
    
    @Override
    public boolean shouldRender3DInInventory(int modelId) {
        return true;
    }
    
    @Override
    public int getRenderId() {
        return RENDER_ID;
    }
}
```

### 3.3 Obliczanie przecięć (Geometria)

```java
public class PlaneIntersection {
    
    /**
     * Oblicza punkty przecięcia płaszczyzny z krawędziami sześcianu [0,1]x[0,1]x[0,1]
     * Płaszczyzna: nx*(x-0.5) + ny*(y-0.5) + nz*(z-0.5) = 0
     * czyli: nx*x + ny*y + nz*z = 0.5*(nx+ny+nz)
     */
    public static List<Vec3> getIntersectionPoints(float nx, float ny, float nz) {
        List<Vec3> points = new ArrayList<>();
        float d = 0.5f * (nx + ny + nz);  // Prawa strona równania
        
        // Sprawdź każdą z 12 krawędzi sześcianu
        // Krawędź: punkt początkowy, kierunek, stałe współrzędne
        
        // Krawędzie równoległe do X (4 sztuki)
        checkEdgeX(points, nx, ny, nz, d, 0, 0);
        checkEdgeX(points, nx, ny, nz, d, 0, 1);
        checkEdgeX(points, nx, ny, nz, d, 1, 0);
        checkEdgeX(points, nx, ny, nz, d, 1, 1);
        
        // Krawędzie równoległe do Y (4 sztuki)
        checkEdgeY(points, nx, ny, nz, d, 0, 0);
        checkEdgeY(points, nx, ny, nz, d, 0, 1);
        checkEdgeY(points, nx, ny, nz, d, 1, 0);
        checkEdgeY(points, nx, ny, nz, d, 1, 1);
        
        // Krawędzie równoległe do Z (4 sztuki)
        checkEdgeZ(points, nx, ny, nz, d, 0, 0);
        checkEdgeZ(points, nx, ny, nz, d, 0, 1);
        checkEdgeZ(points, nx, ny, nz, d, 1, 0);
        checkEdgeZ(points, nx, ny, nz, d, 1, 1);
        
        return points;
    }
    
    private static void checkEdgeX(List<Vec3> points, float nx, float ny, float nz, 
                                    float d, int y, int z) {
        // Krawędź: (t, y, z), t in [0,1]
        // równanie: nx*t + ny*y + nz*z = d
        if (Math.abs(nx) < 0.0001f) return;  // Równoległa do płaszczyzny
        
        float t = (d - ny*y - nz*z) / nx;
        if (t >= 0 && t <= 1) {
            points.add(Vec3.createVectorHelper(t, y, z));
        }
    }
    
    // Analogicznie dla Y i Z...
}
```

### 3.4 Wyznaczanie ścian do narysowania

```java
public class CuttableMeshBuilder {
    
    /**
     * Buduje listę trójkątów do narysowania
     * Zwraca: lista wierzchołków z UV
     */
    public static List<Triangle> buildMesh(TileEntityCuttable te) {
        List<Vec3> intersections = PlaneIntersection.getIntersectionPoints(
            te.getNormalX(), te.getNormalY(), te.getNormalZ()
        );
        
        boolean keepPositive = te.keepPositiveSide();
        float nx = te.getNormalX();
        float ny = te.getNormalY();
        float nz = te.getNormalZ();
        
        List<Triangle> triangles = new ArrayList<>();
        
        // Dla każdej z 6 ścian sześcianu
        for (Face face : Face.values()) {
            // Sprawdź czy ściana jest po stronie którą zachowujemy
            Vec3 faceCenter = face.getCenter();
            float dot = (float)(faceCenter.xCoord - 0.5) * nx
                      + (float)(faceCenter.yCoord - 0.5) * ny  
                      + (float)(faceCenter.zCoord - 0.5) * nz;
            
            boolean faceIsPositive = dot > 0;
            if (faceIsPositive != keepPositive) continue;  // Odrzuć tę ścianę
            
            // Podziel ścianę na trójkąty używając punktów przecięcia
            List<Triangle> faceTriangles = triangulateFace(face, intersections);
            triangles.addAll(faceTriangles);
        }
        
        // Dodaj "pokrywkę" - wielokąt na płaszczyźnie cięcia
        List<Triangle> capTriangles = triangulateCap(intersections, 
            new Vec3(nx, ny, nz), keepPositive);
        triangles.addAll(capTriangles);
        
        return triangles;
    }
}
```

## 4. Dodatkowe funkcje

### 4.1 Kolizje (opcjonalnie - zaawansowane)

```java
@Override
public void addCollisionBoxesToList(World world, int x, int y, int z, 
                                     AxisAlignedBB mask, List list, Entity entity) {
    // Dla uproszczenia możemy użyć pełnego boxa
    // Albo obliczyć dokładne boxy dla wyciętej geometrii
    
    TileEntity te = world.getTileEntity(x, y, z);
    if (te instanceof TileEntityCuttable) {
        // Oblicz boxy na podstawie strony cięcia
        setBlockBoundsBasedOnState(world, x, y, z);
    }
    super.addCollisionBoxesToList(world, x, y, z, mask, list, entity);
}
```

### 4.2 NBT - zapisywanie/wczytywanie

```java
@Override
public void writeToNBT(NBTTagCompound nbt) {
    super.writeToNBT(nbt);
    nbt.setString("originalBlock", Block.blockRegistry.getNameForObject(originalBlock));
    nbt.setInteger("originalMeta", originalMetadata);
    nbt.setFloat("normalX", normalX);
    nbt.setFloat("normalY", normalY);
    nbt.setFloat("normalZ", normalZ);
    nbt.setBoolean("keepPositive", keepPositiveSide);
}

@Override
public void readFromNBT(NBTTagCompound nbt) {
    super.readFromNBT(nbt);
    String blockName = nbt.getString("originalBlock");
    this.originalBlock = (Block) Block.blockRegistry.getObject(blockName);
    this.originalMetadata = nbt.getInteger("originalMeta");
    this.normalX = nbt.getFloat("normalX");
    this.normalY = nbt.getFloat("normalY");
    this.normalZ = nbt.getFloat("normalZ");
    this.keepPositiveSide = nbt.getBoolean("keepPositive");
}

@Override
public Packet getDescriptionPacket() {
    // Synchronizacja z klientem przy ładowaniu chunka
    NBTTagCompound nbt = new NBTTagCompound();
    writeToNBT(nbt);
    return new S35PacketUpdateTileEntity(xCoord, yCoord, zCoord, 0, nbt);
}

@Override
public void onDataPacket(NetworkManager net, S35PacketUpdateTileEntity pkt) {
    readFromNBT(pkt.func_148857_g());
    worldObj.markBlockRangeForRenderUpdate(xCoord, yCoord, zCoord, xCoord, yCoord, zCoord);
}
```

### 4.3 Pick block (Wybieranie bloku)

```java
@Override
public ItemStack getPickBlock(MovingObjectPosition target, World world, int x, int y, int z) {
    // Zwróć oryginalny blok przy middle-click
    TileEntity te = world.getTileEntity(x, y, z);
    if (te instanceof TileEntityCuttable) {
        Block original = ((TileEntityCuttable) te).getOriginalBlock();
        int meta = ((TileEntityCuttable) te).getOriginalMetadata();
        if (original != null) {
            return new ItemStack(original, 1, meta);
        }
    }
    return super.getPickBlock(target, world, x, y, z);
}
```

### 4.4 Drop przy zniszczeniu

```java
@Override
public ArrayList<ItemStack> getDrops(World world, int x, int y, int z, 
                                       int metadata, int fortune) {
    // Dropuj oryginalny blok
    TileEntity te = world.getTileEntity(x, y, z);
    if (te instanceof TileEntityCuttable) {
        Block original = ((TileEntityCuttable) te).getOriginalBlock();
        int meta = ((TileEntityCuttable) te).getOriginalMetadata();
        if (original != null) {
            ArrayList<ItemStack> drops = new ArrayList<>();
            drops.add(new ItemStack(original, 1, meta));
            return drops;
        }
    }
    return super.getDrops(world, x, y, z, metadata, fortune);
}
```

## 5. Testowanie na headless serwerze

Testowanie moda odbywa się w dwóch etapach na dedykowanym serwerze testowym znajdującym się w `headless_server/1.7.10/`.

### 5.1 Etap 1 - Testy integracyjne (automatyczne/podstawowe)

**Cel**: Weryfikacja czy mod poprawnie integruje się z Forge i Minecraft 1.7.10 bez crashy, czy bloki się rejestrują, TE się zapisują/wczytują.

#### Przygotowanie mapy testowej

Przed testami należy przygotować mapę testową z gotowymi przyciętymi blokami:

```
headless_server/1.7.10/world_cuttable_test/
├── level.dat
├── region/
│   └── r.0.0.mca  # Chunki z predefiniowanymi blokami
└── ...
```

**Metoda tworzenia mapy testowej**:
1. Uruchom lokalny client z modem w środowisku deweloperskim
2. Utwórz nowy świat "Test Cuttable Blocks"
3. Wstaw różne bloki (stone, dirt, wood, wool z różnymi metadata)
4. Użyj narzędzia do cięcia z różnymi kierunkami patrzenia:
   - Cięcie poziome (patrzenie w górę/dół) - płaszczyzna Y
   - Cięcie pionowe N-S (patrzenie na +/- Z) - płaszczyzna X
   - Cięcie pionowe E-W (patrzenie na +/- X) - płaszczyzna Z
   - Cięcie ukośne (patrzenie na ukos)
5. Zapisz świat i skopiuj do `headless_server/1.7.10/world_cuttable_test/`

#### Scenariusze testowe (podstawowe)

| Test | Opis | Oczekiwany wynik |
|------|------|------------------|
| **T1** | Serwer startuje z modem | Brak crashy, mod ładuje się |
| **T2** | Wczytanie chunków z Cuttable Blocks | TE się wczytują bez błędów NBT |
| **T3** | Tick serwera (30s) | Brak NullPointerException, stan gry stabilny |
| **T4** | Restart serwera | Dane bloku zachowane po restarcie |
| **T5** | `/save-all` i inspekcja NBT | Region files zawierają poprawne dane TE |

#### Automatyczny skrypt testowy (opcjonalnie)

```powershell
# test_cuttable_integration.ps1
$serverDir = "headless_server/1.7.10"
$worldName = "world_cuttable_test"

# 1. Przygotuj serwer.properties
copy "server.properties.test" "server.properties"

# 2. Skopiuj JAR moda do mods/
copy "build/libs/CuttableBlocks-1.0.0.jar" "mods/"

# 3. Uruchom serwer
Start-Process -FilePath "java" -ArgumentList "-jar forge-1.7.10-10.13.4.1614-1.7.10-universal.jar nogui" -WorkingDirectory $serverDir -RedirectStandardOutput "test_out.log" -RedirectStandardError "test_err.log"

# 4. Czekaj 60s, potem stop
Start-Sleep -Seconds 60
# ... wysłanie komendy stop ...

# 5. Sprawdź logi
if (Select-String -Path "logs/latest.log" -Pattern "FATAL\|ERROR\|Exception" -Quiet) {
    Write-Host "TEST FAILED - Błędy w logach"
    exit 1
}

Write-Host "TEST PASSED"
```

### 5.2 Etap 2 - Testy funkcjonalne (użytkownik)

**Cel**: Weryfikacja czy bloki poprawnie działają w grze - cięcie, renderowanie, kolizje, dropy.

#### Przygotowanie

1. Skopiuj zbudowany JAR do `headless_server/1.7.10/mods/`
2. Uruchom serwer: `run.bat` (lub `run.sh`)
3. Połącz się klientem Minecraft 1.7.10 z zainstalowanym modem

#### Scenariusze testowe (manualne)

| Test | Kroki | Oczekiwany wynik |
|------|-------|------------------|
| **M1** | Weź Cutting Tool, kliknij na Stone | Stone zamienia się na CuttableBlock z zachowaniem tekstury |
| **M2** | Zniszcz przycięty blok kilofem | Dropuje się oryginalny Stone |
| **M3** | Sprawdź middle-click | Daje oryginalny Stone (nie CuttableBlock) |
| **M4** | Cięcie z różnych kierunków | Różne orientacje przyciętej geometrii |
| **M5** | Restart serwer + ponowne wejście | Bloki wyglądają tak samo |
| **M6** | Cięcie bloku z metadanymi (np. Wool:14) | Zachowane metadane (czerwona wełna) |
| **M7** | Cięcie bloku z innego moda (np. AE2) | Poprawne zachowanie jeśli blok prostego typu |

#### Raportowanie

Wyniki testów dokumentuj w:
```
new_mod_trial/TEST_RESULTS.md
```

Szablon:
```markdown
# Testy CuttableBlocks v1.0.0

## Data: 2026-02-05
## Tester: [nazwa]

### Testy integracyjne
- [x] Serwer startuje
- [x] Wczytanie chunków
- [ ] Tick 30s (błąd: ...)

### Testy manualne
- [x] Cięcie Stone
- [x] Drop oryginału
- [ ] Renderowanie (problemy: ...)

## Wnioski
...
```

### 5.3 Struktura testowa w repo

```
new_mod_trial/
├── src/... (kod źródłowy)
├── test_worlds/
│   └── cuttable_test_base/      # Predefiniowana mapa testowa
│       ├── level.dat            # (do utworzenia ręcznie w kliencie)
│       └── region/
│           └── r.0.0.mca        # (chunki z przyciętymi blokami)
├── test_scripts/
│   ├── prepare_test_world.ps1   # Kopiowanie mapy do serwera
│   ├── run_integration_tests.ps1 # Automatyczne testy integracyjne
│   └── verify_nbt.py            # Weryfikacja NBT w region files
└── TEST_RESULTS.md              # Dokumentacja wyników (szablon)
```

### 5.4 Debugowanie na headless serwerze

Jeśli serwer crashuje:
1. Sprawdź `crash-reports/` - tam są stacktraces
2. Sprawdź `logs/latest.log` - logi Forge
3. Włącz debug mode w `forge.cfg`: `B:removeErroringTileEntities=false` (żeby nie usuwał błędnych TE)
4. Użyj NBTExplorer do inspekcji chunków w region files

## 6. Pliki konfiguracyjne

### 6.1 build.gradle

```gradle
version = "1.0.0"
group = "com.cuttableblocks"
archivesBaseName = "CuttableBlocks"

minecraft {
    version = "1.7.10-10.13.4.1614-1.7.10"
    runDir = "eclipse"
}
```

### 6.2 mcmod.info

```json
[
{
  "modid": "cuttableblocks",
  "name": "Cuttable Blocks",
  "description": "Cut any block with a plane through its center",
  "version": "1.0.0",
  "mcversion": "1.7.10",
  "url": "",
  "updateUrl": "",
  "authorList": ["YourName"],
  "credits": "",
  "logoFile": "",
  "screenshots": [],
  "dependencies": []
}
]
```

## 7. Kolejność implementacji

1. **Setup projektu** - struktura folderów, build.gradle, mcmod.info
2. **Podstawowa klasa moda** - CuttableBlocksMod.java z @Mod
3. **TileEntityCuttable** - podstawowa klasa z polami i NBT
4. **BlockCuttable** - podstawowy blok z rejestracją
5. **ItemCuttingTool** - narzędzie do cięcia (bez wizualizacji)
6. **Podstawowy renderer** - rysowanie oryginalnego bloku (bez cięcia)
7. **Test I - Integracja headless** - Testy na serwerze z predefiniowaną mapą
8. **Geometria cięcia** - obliczanie przecięć płaszczyzny z sześcianem
9. **Advanced renderer** - właściwe cięcie z teksturami oryginalnego bloku
10. **Kolizje i bounding boxy**
11. **Test II - Funkcjonalność** - Testy manualne przez użytkownika
12. **Bugfixing i optymalizacja**

## 8. Potencjalne problemy i rozwiązania

### 8.1 Problemy techniczne

| Problem | Rozwiązanie |
|---------|-------------|
| Tekstury animowane | Użyj IIcon z oryginalnego bloku, czas animacji jest globalny |
| Bloki z modelem 3D (np. chest) | Renderuj jako zwykły blok lub użyj domyślnego tekstu |
| TileEntity w oryginalnym bloku | Skopiuj tylko Block + metadata, utracisz funkcjonalność |
| Performance (wiele TE) | Optymalizuj renderer, batchuj podobne bloki |
| Lighting (cienie) | Ustaw proper light opacity, może wymagać custom lighting |

### 8.2 Kompromisy

1. **Skomplikowane bloki** (np. drzwi, łóżka) - można zablokować cięcie lub potraktować jak zwykłe bloki
2. **Tile Entities z funkcjonalnością** (skrzynie, piece) - strata funkcjonalności po przycięciu
3. **Wielokrotne cięcie** - można dodać (chain of cuts) lub ograniczyć do jednego cięcia

## 9. Rozszerzenia (opcjonalne)

### 9.1 Undo system
Zapisuj historię cięć w graczu, umożliwij cofnięcie (przywrócenie oryginalnego bloku).

### 9.2 Multiple cuts
Zamiast zastępować blok, pozwól na kolejne cięcia (przechowuj listę płaszczyzn).

### 9.3 Precyzyjne cięcie
Pozwól graczowi na przesunięcie płaszczyzny (nie tylko przez środek).

### 9.4 Zapis schematów
Możliwość zapisania wzoru cięcia i zastosowania do wielu bloków.

---

**Uwaga**: To ambitny projekt ze względu na custom rendering w 1.7.10. Najtrudniejsza część to poprawne mapowanie tekstur oryginalnego bloku na wyciętą geometrię. Rozważ zaczęcie od prostszej wersji (np. cięcie tylko wzdłuż osi X/Y/Z).