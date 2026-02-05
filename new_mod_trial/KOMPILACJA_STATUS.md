# Status Kompilacji Moda CuttableBlocks

## Problem

Kompilacja moda dla Minecraft 1.7.10 napotkała na szereg problemów związanych z przestarzałymi narzędziami:

### Główne Problemy:

1. **ForgeGradle 1.2** ma na sztywno wpisany stary URL S3 Amazon do pobierania Minecraft:
   - `http://s3.amazonaws.com/Minecraft.Download/versions/1.7.10/1.7.10.jar` (nie działa)
   - Powinien używać: `https://launcher.mojang.com/...` lub `https://piston-data.mojang.com/...`

2. **RetroFuturaGradle** (nowsza alternatywa) wymaga Gradle 4.x+, ale mamy 2.14.1

3. **JDK 21** (który mamy) może nie być w pełni kompatybilny z kodem z 2014 roku

## Co Zostało Zrobione:

✅ Pobrano pliki Minecraft ręcznie:
- `minecraft-1.7.10.jar` (serwer) - 9.6 MB
- `minecraft-1.7.10-client.jar` (klient) - 5.3 MB

✅ Pliki są w cachu Gradle:
- `C:\Users\pawel\.gradle\caches\minecraft\net\minecraft\minecraft\1.7.10\`

❌ ForgeGradle nadal próbuje użyć starego URL

## Rozwiązania:

### Opcja 1: Ręczna Kompilacja z MCP (Mod Coder Pack)

MCP to narzędzie używane przed ForgeGradle do modowania Minecraft.

Kroki:
1. Pobrać MCP 1.7.10 z https://minecraftforge.net/forums
2. Rozpakować MCP
3. Skopiować nasz kod źródłowy do `src/minecraft/com/cuttableblocks/`
4. Uruchomić `decompile.bat` (pobierze i zdeobfuskuje Minecraft)
5. Uruchomić `recompile.bat` (skompiluje kod)
6. Uruchomić `reobfuscate.bat` (przygotuje do dystrybucji)
7. Gotowy JAR będzie w `reobf/minecraft/`

### Opcja 2: Użycie GT New Horizons ForgeGradle

GT New Horizons to community, które utrzymuje nowoczesne narzędzia dla starego Minecraft.

Kroki:
1. Zaktualizować Gradle do 4.10.3 lub wyżej
2. Użyć `com.github.GTNewHorizons:ForgeGradle:1.2.11`
3. Zbudować projekt

### Opcja 3: Test Bez Moda (Rekomendowane Teraz)

Uruchomić serwer bez moda - bloki będą widoczne jako ID 200 (brak tekstury), ale dane są poprawne.

Po dodaniu moda później, bloki automatycznie się poprawią.

## Rekomendacja:

Najlepiej teraz uruchomić serwer bez moda i zweryfikować, że bloki są wstawione. Kompilację moda można zrobić później używając Opcji 1 (MCP) lub Opcji 2 (GTNH ForgeGradle).

## Uruchomienie Testu (Bez Moda):

```powershell
cd headless_server/1.7.10
java -Xmx1G -jar forge-1.7.10-10.13.4.1614-1.7.10-universal.jar nogui
```

Bloki będą widoczne jako ID 200 - można sprawdzić współrzędne w logach lub użyć komend `/blockdata`.
