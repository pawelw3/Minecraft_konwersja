# Minecraft 1.7.10 Headless Test Server

Serwer testowy Minecraft 1.7.10 z modpackiem konwersji. Zawiera wstawiony schematic `digital_counter` do testowania.

## Konfiguracja

### Wersje
- **Minecraft**: 1.7.10
- **Forge**: 10.13.4.1614
- **Java**: 8 (wymagane przez Forge 1.7.10)

### Zainstalowane mody (37 modów)

| Kategoria | Mody |
|-----------|------|
| **Core/Biblioteki** | CodeChickenCore, CoFHCore, fastcraft |
| **Storage** | Applied Energistics 2, Backpack, EnderStorage |
| **Tech** | BuildCraft (+compat), IndustrialCraft 2, Mekanism (+Generators, Tools), Thermal Expansion/Dynamics/Foundation, Big Reactors, Extra Utilities, Forestry, Logistics Pipes |
| **Transport** | Railcraft, ProjectRed (Base, Integration, Mechanical, World, Lighting, Fabrication, Compat) |
| **Magic** | Thaumcraft 4, Thaumic Tinkerer, Thaumic Energistics, Thaumic Exploration, Thaumic Horizons, Witchery, Blood Magic |
| **Utility** | ComputerCraft, WorldEdit |
| **NEI** | NotEnoughItems, Thaumcraft NEI Plugin |

### Świat testowy
- **Źródło**: `lightweigh_map_templates/1710_modded/konwersja1_with_schematic/`
- **Opis**: Świat z wstawionym schematiciem digital_counter (10-state dropper ring counter)
- **Lokalizacja schematica**: Okolice (0, 60, 0)
- **Bloki**: 112 bloków redstone (droppers, comparators, command blocks, redstone wire, repeaters)

### Konfiguracja sieciowa (tylko lokalnie!)
```properties
server-ip=127.0.0.1      # Tylko localhost
server-port=25565        # Standardowy port
online-mode=false        # Brak weryfikacji Mojang
max-players=10
gamemode=creative        # Creative mode (ID 1)
spawn-protection=0       # Brak ochrony spawna
enable-command-block=true # Włączone command blocki
```

### JVM Arguments
```
-Xms2G
-Xmx4G
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
```

## Uruchomienie

### Windows
```batch
cd headless_server/1.7.10
run.bat
```

### Linux/Mac
```bash
cd headless_server/1.7.10
chmod +x run.sh
./run.sh
```

### Pierwsze uruchomienie
1. Serwer wygeneruje konfigurację
2. EULA jest już zaakceptowana (eula=true)
3. Świat zostanie załadowany z folderu `world/`
4. Mody zostaną załadowane z folderu `mods/`

## Dostęp dla klienta

### Wymagania klienta
- Minecraft 1.7.10
- Forge 1.7.10-10.13.4.1614
- TE SAME MODY co na serwerze (lista powyżej)

### Połączenie
1. Dodaj serwer: `localhost` lub `127.0.0.1`
2. Wejdź na serwer (nie wymaga konta premium - offline mode)

## Struktura plików

```
headless_server/1.7.10/
├── libraries/          # Biblioteki Forge/Minecraft (pobrane przez installer)
├── mods/               # Zainstalowane mody (37 plików .jar)
├── world/              # Świat testowy z wstawionym schematiciem
│   ├── region/
│   ├── level.dat
│   └── ...
├── server.properties   # Konfiguracja serwera
├── eula.txt            # EULA (accepted)
├── run.bat             # Skrypt uruchomieniowy Windows
├── run.sh              # Skrypt uruchomieniowy Linux/Mac
└── README.md           # Ten plik
```

## Testowanie digital_counter

### Opis układu
Schematic `digital_counter` to 10-stanowy licznik pierścieniowy (ring counter) zbudowany z:
- 10x Dropper + 10x Comparator (do odczytu stanu)
- 10x Command Block (wyjście cyfrowe /say 0-9)
- Generator zegara (torch + 3x repeater)
- Redstone wire (magistrala zasilająca)

### Lokalizacja w świecie
- **Centrum**: (0, 60, 0)
- **Zakres**: x: 0-11, y: 60-63, z: 2-10
- **Chunk**: (0, 0) w regionie r.0.0.mca

### Jak przetestować
1. Wejdź na serwer
2. Teleportuj się do układu: `/tp 0 65 0`
3. Znajdź lever w pozycji (0, 63, 2)
4. Włącz lever - układ zacznie liczyć 0-9
5. Obserwuj chat (command blocki wypisują cyfry)

### Oczekiwane zachowanie
- Cykliczne przełączanie się outputu 0→1→2→...→9→0
- Okres: ~10 sekund na cykl
- Komunikaty w chat: `[Server] 0`, `[Server] 1`, itd.

## Uwagi dla testów

### Co można testować
1. **AE2**: Sieci ME, kanały, storage cells
2. **Mekanism**: Maszyny, kable, konfiguracja stron
3. **BuildCraft**: Rury, silniki, pompy
4. **IC2**: Maszyny, kable energetyczne
5. **Thaumcraft**: Aspekty, research, crafting
6. **Thermal Series**: Maszyny, przetwarzanie
7. **Railcraft**: Tory, lokomotywy
8. **ProjectRed**: Logika redstone, kable, bramki

### Narzędzia testowe
- **WorldEdit**: Zapis/odczyt schematów, analiza bloków
- **Command blocks**: Włączone, można używać do testów
- **Komendy OP**: Pełen dostęp do komend administracyjnych

### Ograniczenia
- Tylko lokalny dostęp (127.0.0.1)
- Brak autentykacji (online-mode=false)
- Difficulty: Easy (ID 1)
- PvP wyłączone

## Rozwiązywanie problemów

### "Java version mismatch"
Upewnij się że masz Java 8 (nie 11, 17, ani 21). Sprawdź: `java -version`

### "Missing mods"
Upewnij się że wszystkie 37 modów jest w folderze `mods/`. Niektóre wymagają konkretnej kolejności ładowania.

### "World not loading"
Sprawdź czy folder `world/` zawiera pliki regionów (*.mca) i level.dat.

### "Out of memory"
Zwiększ `-Xmx` w skrypcie startowym (np. `-Xmx6G` dla 6GB RAM).
