# Podsumowanie migracji Forge 1.14.4

## Data wykonania
2026-02-01

## Konfiguracja
- **Serwer:** Minecraft Forge 1.14.4 (28.2.23)
- **Java:** Java 8 (1.8.0_431)
- **Mapa źródłowa:** headless_server\1.14\server\world (kopia z 1.7.10)
- **RAM:** 4GB (-Xmx4G -Xms2G)

## Przebieg operacji

### 1. Instalacja Forge
- ✅ Pobrano forge-1.14.4-28.2.23-installer.jar (6.5MB)
- ✅ Zainstalowano serwer Forge (pobrano wszystkie biblioteki)
- ✅ Utworzono forge-1.14.4-28.2.23.jar (183KB)

### 2. Przygotowanie
- ✅ Usunięto folder `players` (problem z 1.7.10)
- ✅ Skonfigurowano eula.txt
- ✅ Wyczyszczono logi

### 3. Uruchomienie
- ✅ Forge się uruchomił
- ✅ Załadowano silnik (ModLauncher 4.1.0)
- ✅ Rozpoczęto przygotowywanie spawn area (53%, 89%)
- ❌ Błędy FATAL podczas ładowania chunków
- ❌ Serwer nie osiągnął "Done"

## Problemy

### Błędy FATAL (te same co w vanilla)
```
FATAL: Error executing task on Chunk source main thread executor
Caused by: net.minecraft.util.ResourceLocationException: 
Non [a-z0-9/._-] character in path of location: minecraft:savedMultipart
```

### Nieobsługiwane Tile Entities
Forge bez modów NIE potrafi obsłużyć tile entities z modów z 1.7.10:
- `savedMultipart` (Forge Multipart)
- `TileEntityCarpentersBlock` (Carpenter's Blocks)
- `te.skinnableChild` (Decocraft/SecretRooms)
- `seatTile` (bibliocraft)
- `Sign`, `Chest`, `Hopper` (vanilla w starym formacie)

## Wnioski

### ❌ Migracja NIE POWIODŁA SIĘ

Forge 1.14.4 **BEZ MODÓW** zachowuje się identycznie jak vanilla:
- Nie ma DataFixerów dla tile entities z modów
- Nie obsługuje starych nazw z wielkimi literami
- Nie potrafi przekonwertować chunków zawierających dane z modów

### Różnica między Forge a Vanilla
W tym przypadku **BRAK RÓŻNICY** - oba serwery zawiodły z tymi samymi błędami.

## Co by pomogło?

### Opcja 1: Forge + Mody 1.14.4
Zainstalować wszystkie odpowiedniki modów z 1.7.10 dla wersji 1.14.4:
- Ale większości modów z 1.7.10 nie ma na 1.14.4
- Wiele modów zmieniło swoje nazwy i strukturę danych

### Opcja 2: Użycie nowszej wersji Forge
Forge 1.16.5 lub 1.18.2 mogą mieć lepsze DataFixery, ale problem pozostaje ten sam.

### Opcja 3: Własny DataFixer
Napisać własny mod dla Forge 1.14.4 który:
1. Rejestruje stare nazwy tile entities
2. Konwertuje je na nowy format lub usuwa

### Opcja 4: Czyszczenie mapy (NAPOLEONICZNE)
Przed migracją usunąć WSZYSTKIE tile entities z modów:
- Użyć MCEdit Unified
- Lub Amulet Editor
- Lub skryptu NBT

## Rekomendacja

Najlepszym rozwiązaniem jest **Opcja 4** - wyczyszczenie mapy z danych modów PRZED migracją. Forge 1.14.4 (lub wyższy) bez modów poradzi sobie z czystą mapą vanilla.

## Logi
- Log serwera: ~1.5 miliona linii
- Głównie błędy związane z nieobsługiwanymi tile entities
- Serwer zużywał ~400MB RAM

## Następne kroki

Jeśli chcesz kontynuować migrację przez Forge:
1. Potrzebujesz **wyczyścić mapę** z tile entities z modów
2. Lub zainstalować **odpowiedniki modów** na 1.14.4 (ale większości nie ma)
3. Lub przejść **bezpośrednio na 1.18.2** z czyszczeniem
