# Minecraft 1.18.2 Headless Test Server

## Konfiguracja

### Wersje
- **Minecraft**: 1.18.2
- **Forge**: 40.2.0
- **Java**: 17+ (wymagane przez Forge 1.18.2)

### Zainstalowane mody

| Mod | Wersja | Rozmiar | Funkcja |
|-----|--------|---------|---------|
| Applied Energistics 2 | 11.7.6 | 4.9 MB | Sieci ME, storage, autocrafting |
| Mekanism | 10.2.0.459 | 10.94 MB | Maszyny, przetwórstwo, reaktory |
| WorldEdit | 7.2.10 | 5.25 MB | Edycja terenu, schematy |

**Łącznie**: ~21 MB modów

### Świat testowy
- **Źródło**: `lightweigh_map_templates/118_modded/ae2_1/`
- **Opis**: Świat z pre-instalowanymi maszynami AE2 do testowania konwersji
- **Pliki regionu**: 4 chunki (r.0.0, r.0.-1, r.-1.0, r.-1.-1)

### Konfiguracja sieciowa (tylko lokalnie!)
```properties
server-ip=127.0.0.1      # Tylko localhost
server-port=25565        # Standardowy port
online-mode=false        # Brak weryfikacji Mojang
max-players=10
gamemode=creative         # Łatwiejsze testowanie
spawn-protection=0        # Brak ochrony spawna
```

### JVM Arguments
```
-Xms2G
-Xmx4G
-XX:+UseG1GC
```

## Uruchomienie

### Windows
```batch
cd headless_server/1.18.2
run.bat
```

### Pierwsze uruchomienie
1. Serwer wygeneruje konfigurację
2. Zaakceptowano EULA (eula=true)
3. Świat zostanie załadowany z folderu `world/`

## Dostęp dla klienta

### Wymagania klienta
- Minecraft 1.18.2
- Forge 1.18.2-40.2.0
- TE SAME MODY co na serwerze (AE2, Mekanism, WorldEdit)

### Połączenie
1. Dodaj serwer: `localhost` lub `127.0.0.1`
2. Wejdź na serwer (nie wymaga konta premium - offline mode)

## Struktura plików

```
headless_server/1.18.2/
├── libraries/          # Biblioteki Forge/Minecraft
├── mods/               # Zainstalowane mody
│   ├── appliedenergistics2-forge-11.7.6.jar
│   ├── Mekanism-1.18.2-10.2.0.459.jar
│   └── worldedit-mod-7.2.10.jar
├── world/              # Świat testowy (z template)
│   ├── region/
│   ├── level.dat
│   └── ...
├── server.properties   # Konfiguracja serwera
├── user_jvm_args.txt   # Argumenty JVM
├── eula.txt            # EULA (accepted)
└── run.bat             # Skrypt uruchomieniowy
```

## Uwagi dla testów

### Co można testować
1. **AE2**: Sieci ME, kanały, storage cells, autocrafting
2. **Mekanism**: Maszyny, kable, konfiguracja stron
3. **Konwersja**: Porównanie z wersją 1.7.10

### Narzędzia testowe
- **WorldEdit**: Zapis/odczyt schematów, analiza bloków
- **Komendy OP**: Pełen dostęp do komend administracyjnych

### Ograniczenia
- Tylko lokalny dostęp (127.0.0.1)
- Brak autentykacji (online-mode=false)
- Peaceful difficulty (brak mobów)
