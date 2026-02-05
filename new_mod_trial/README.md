# Cuttable Blocks Mod for Minecraft 1.7.10

Mod pozwalający przycinać dowolne bloki płaszczyzną przechodzącą przez ich środek geometryczny.

## Funkcje

- **Cutting Tool** - narzędzie do cięcia bloków
- Płaszczyzna cięcia zależy od kierunku patrzenia gracza
- Oryginalny blok jest zachowany w Tile Entity
- Drop przyciętego bloku zwraca oryginalny blok

## Budowanie

### Wymagania
- Java JDK 8
- Gradle 2.14+ (lub użyj wrappera)

### Kompilacja

```bash
# Używając Gradle wrappera (Windows)
gradlew.bat build

# Używając Gradle wrappera (Linux/Mac)
./gradlew build

# Lub jeśli masz zainstalowany Gradle
gradle build
```

Plik JAR znajdzie się w `build/libs/`.

## Instalacja

1. Zainstaluj Minecraft Forge 1.7.10-10.13.4.1614 (lub nowszy) na serwerze/klientcie
2. Skopiuj `CuttableBlocks-1.0.0.jar` do folderu `mods/`
3. Uruchom grę/serwer

## Użycie

1. Weź **Cutting Tool** z zakładki "Cuttable Blocks" w creative menu
2. Kliknij PPM na dowolny blok (np. Stone, Dirt, Wood)
3. Blok zostanie zamieniony na Cut Block z zachowaniem oryginalnej tekstury
4. Płaszczyzna cięcia jest prostopadła do kierunku w którym patrzysz

## Testowanie

Zobacz `PLAN_IMPLEMENTACJI.md` szczegółowy plan i dokumentację.

### Testy integracyjne
```powershell
.\test_scripts\run_integration_tests.ps1
```

### Testy manualne
1. Skopiuj JAR do `headless_server/1.7.10/mods/`
2. Uruchom serwer: `cd headless_server/1.7.10 && run.bat`
3. Połącz się klientem z zainstalowanym modem

## Struktura projektu

```
new_mod_trial/
├── src/main/java/com/cuttableblocks/
│   ├── CuttableBlocksMod.java      # Główna klasa moda
│   ├── CreativeTabCuttableBlocks.java
│   ├── blocks/
│   │   ├── BlockCuttable.java      # Blok z TileEntity
│   │   └── ModBlocks.java
│   ├── client/
│   │   ├── ClientProxy.java
│   │   └── CuttableBlockRenderer.java
│   ├── common/
│   │   └── CommonProxy.java
│   ├── items/
│   │   ├── ItemCuttingTool.java    # Narzędzie do cięcia
│   │   └── ModItems.java
│   ├── tileentities/
│   │   ├── TileEntityCuttable.java # Dane o cięciu
│   │   └── ModTileEntities.java
│   └── util/
│       └── Plane.java              # Obliczenia geometryczne
├── src/main/resources/
│   ├── mcmod.info
│   └── assets/cuttableblocks/
│       ├── lang/                   # Tłumaczenia
│       └── textures/
├── test_scripts/                   # Skrypty testowe
├── test_worlds/                    # Mapy testowe
└── build.gradle
```

## Licencja

Własna implementacja do użytku w projekcie konwersji mapy.
