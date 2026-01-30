# Headless Minecraft Test Servers

Serwery Minecraft do testowania konwersji modów 1.7.10 → 1.18.2

## Status

### ✅ Serwer 1.18.2 (GOTOWY)

| Element | Status |
|---------|--------|
| Forge 1.18.2-40.2.0 | ✅ Zainstalowany |
| Applied Energistics 2 11.7.6 | ✅ Zainstalowany |
| Mekanism 10.2.0.459 | ✅ Zainstalowany |
| WorldEdit 7.2.10 | ✅ Zainstalowany |
| Świat testowy (ae2_1) | ✅ Skopiowany |
| Konfiguracja lokalna | ✅ Skonfigurowana |
| EULA | ✅ Zaakceptowana |

**Gotowy do uruchomienia!**

```bash
cd headless_server/1.18.2
run.bat
```

### ⏳ Serwer 1.7.10 (W PRZYSZŁOŚCI)
Planowany dla testów porównawczych.

## Struktura folderów

```
headless_server/
├── 1.18.2/              # Aktywny serwer testowy
│   ├── mods/            # AE2, Mekanism, WorldEdit
│   ├── world/           # Świat z AE2
│   ├── server.properties
│   └── run.bat
└── 1.7.10/              # TODO
```

## Uwagi

- Serwer działa tylko na localhost (127.0.0.1)
- Klient musi być na tym samym komputerze
- Nie wymaga konta premium (online-mode=false)
- Gamemode: creative
- Difficulty: peaceful

## Dostęp

Klient Minecraft 1.18.2 z Forge → dodaj serwer `localhost:25565`
