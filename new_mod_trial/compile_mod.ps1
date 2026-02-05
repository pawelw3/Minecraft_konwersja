# Kompilacja moda uzywajac javac bezposrednio
# Uzywa lokalnych bibliotek z serwera

$ErrorActionPreference = "Stop"

# Ustawienia
$JDK_HOME = "C:\Program Files\Java\jdk-21"
$JAVAC = "$JDK_HOME\bin\javac"
$JAR = "$JDK_HOME\bin\jar"

$MOD_SRC = "src\main\java"
$MOD_RES = "src\main\resources"
$BUILD_DIR = "build\manual"
$SERVER_DIR = "..\headless_server\1.7.10"
$LIBS_DIR = "$SERVER_DIR\libraries"

Write-Host "=== Kompilacja CuttableBlocks ===" -ForegroundColor Cyan
Write-Host "JDK: $JDK_HOME" -ForegroundColor Gray
Write-Host ""

# Przygotuj katalogi
New-Item -ItemType Directory -Force -Path "$BUILD_DIR\classes" | Out-Null
New-Item -ItemType Directory -Force -Path "$BUILD_DIR\classes\META-INF" | Out-Null
New-Item -ItemType Directory -Force -Path "$BUILD_DIR\libs" | Out-Null

# Przygotuj classpath
$CLASSPATH = @(
    "$SERVER_DIR\forge-1.7.10-10.13.4.1614-1.7.10-universal.jar"
    "$SERVER_DIR\minecraft_server.1.7.10.jar"
    "$LIBS_DIR\net\minecraft\launchwrapper\1.12\launchwrapper-1.12.jar"
    "$LIBS_DIR\org\ow2\asm\asm-all\5.0.3\asm-all-5.0.3.jar"
    "$LIBS_DIR\com\google\guava\guava\17.0\guava-17.0.jar"
    "$LIBS_DIR\com\google\code\gson\gson\2.2.4\gson-2.2.4.jar"
    "$LIBS_DIR\org\apache\logging\log4j\log4j-api\2.0-beta9\log4j-api-2.0-beta9.jar"
    "$LIBS_DIR\org\apache\logging\log4j\log4j-core\2.0-beta9\log4j-core-2.0-beta9.jar"
) -join ";"

Write-Host "Classpath ready" -ForegroundColor Gray
Write-Host ""

# Znajdz wszystkie pliki Java
Write-Host "Szukanie plikow Java..." -ForegroundColor Yellow
$JAVA_FILES = Get-ChildItem -Path $MOD_SRC -Recurse -Filter "*.java" | Select-Object -ExpandProperty FullName

Write-Host "Znaleziono $($JAVA_FILES.Count) plikow Java" -ForegroundColor Green
Write-Host ""

# Kompiluj
Write-Host "Kompilowanie (Java 8 target)..." -ForegroundColor Yellow

# Zapisz liste plikow do pliku tymczasowego
$TEMP_FILE = "$BUILD_DIR\sources.txt"
$JAVA_FILES | Out-File -FilePath $TEMP_FILE -Encoding UTF8

# Kompiluj
& $JAVAC -cp $CLASSPATH `
    -d "$BUILD_DIR\classes" `
    -source 8 `
    -target 8 `
    -encoding UTF8 `
    -proc:none `
    "@$TEMP_FILE" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Blad kompilacji!" -ForegroundColor Red
    exit 1
}

Write-Host "Kompilacja zakonczona sukcesem!" -ForegroundColor Green
Write-Host ""

# Skopiuj zasoby
Write-Host "Kopiowanie zasobow..." -ForegroundColor Yellow
if (Test-Path $MOD_RES) {
    Copy-Item -Recurse -Force "$MOD_RES\*" "$BUILD_DIR\classes\" 2>$null
}

# Utworz plik mcmod.info
if (-not (Test-Path "$BUILD_DIR\classes\mcmod.info")) {
    Write-Host "Tworzenie mcmod.info..." -ForegroundColor Yellow
    @'
[{
  "modid": "cuttableblocks",
  "name": "Cuttable Blocks",
  "description": "Cut blocks at any angle",
  "version": "1.0.0",
  "mcversion": "1.7.10",
  "url": "",
  "updateUrl": "",
  "authorList": ["CuttableBlocks"],
  "credits": "",
  "logoFile": "",
  "screenshots": [],
  "dependencies": []
}]
'@ | Out-File -FilePath "$BUILD_DIR\classes\mcmod.info" -Encoding UTF8
}

# Utworz JAR
Write-Host "Tworzenie JAR..." -ForegroundColor Yellow
Set-Location "$BUILD_DIR\classes"

# Utworz manifest
@"
Manifest-Version: 1.0
FMLCorePlugin: com.cuttableblocks.asm.CuttableBlocksLoadingPlugin
FMLCorePluginContainsFMLMod: true
Implementation-Title: CuttableBlocks
Implementation-Version: 1.0.0
Implementation-Vendor: com.cuttableblocks
"@ | Out-File -FilePath "META-INF\MANIFEST.MF" -Encoding ASCII

# Spakuj JAR
& $JAR cvfm "..\libs\CuttableBlocks-1.0.0.jar" "META-INF\MANIFEST.MF" . 2>&1 | Select-Object -Last 10

Set-Location "..\.."

# Sprawdz czy JAR powstal
if (Test-Path "$BUILD_DIR\libs\CuttableBlocks-1.0.0.jar") {
    $SIZE = (Get-Item "$BUILD_DIR\libs\CuttableBlocks-1.0.0.jar").Length
    Write-Host ""
    Write-Host "=== SUKCES ===" -ForegroundColor Green
    Write-Host "JAR utworzony: $BUILD_DIR\libs\CuttableBlocks-1.0.0.jar" -ForegroundColor Green
    Write-Host "Rozmiar: $([math]::Round($SIZE/1024, 2)) KB" -ForegroundColor Green
    Write-Host ""
    
    # Kopiuj automatycznie
    New-Item -ItemType Directory -Force -Path "$SERVER_DIR\mods" | Out-Null
    Copy-Item -Force "$BUILD_DIR\libs\CuttableBlocks-1.0.0.jar" "$SERVER_DIR\mods\"
    Write-Host "Skopiowano do $SERVER_DIR\mods\" -ForegroundColor Green
} else {
    Write-Host "Blad: JAR nie powstal!" -ForegroundColor Red
    exit 1
}

# Cleanup
Remove-Item $TEMP_FILE -ErrorAction SilentlyContinue
