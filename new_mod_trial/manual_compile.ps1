# Ręczna kompilacja moda CuttableBlocks
# Używa bezpośrednio javac z classpath z forge

$ErrorActionPreference = "Stop"

$JAVA_HOME = "C:\Program Files\Java\jre1.8.0_431"
$JAVAC = "$JAVA_HOME\bin\javac"
$JAR = "$JAVA_HOME\bin\jar"

$SRC_DIR = "src\main\java"
$RES_DIR = "src\main\resources"
$BUILD_DIR = "build\manual"
$LIBS_DIR = "..\headless_server\1.7.10\libraries"

Write-Host "=== Ręczna kompilacja CuttableBlocks ===" -ForegroundColor Cyan
Write-Host ""

# Utwórz katalog build
New-Item -ItemType Directory -Force -Path "$BUILD_DIR\classes" | Out-Null
New-Item -ItemType Directory -Force -Path "$BUILD_DIR\libs" | Out-Null

# Przygotuj classpath
$CLASSPATH = @(
    "..\headless_server\1.7.10\forge-1.7.10-10.13.4.1614-1.7.10-universal.jar"
    "..\headless_server\1.7.10\minecraft_server.1.7.10.jar"
    "..\headless_server\1.7.10\libraries\net\minecraft\launchwrapper\1.12\launchwrapper-1.12.jar"
) -join ";"

Write-Host "Classpath: $CLASSPATH" -ForegroundColor Gray
Write-Host ""

# Znajdź wszystkie pliki .java
$JAVA_FILES = Get-ChildItem -Path $SRC_DIR -Recurse -Filter "*.java" | Select-Object -ExpandProperty FullName

Write-Host "Znaleziono $($JAVA_FILES.Count) plików Java" -ForegroundColor Yellow
Write-Host ""

# Kompiluj
Write-Host "Kompilowanie..." -ForegroundColor Green
& $JAVAC -cp $CLASSPATH -d "$BUILD_DIR\classes" -source 1.8 -target 1.8 $JAVA_FILES 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Błąd kompilacji!" -ForegroundColor Red
    exit 1
}

Write-Host "Kompilacja zakończona sukcesem!" -ForegroundColor Green
Write-Host ""

# Skopiuj zasoby
Write-Host "Kopiowanie zasobów..." -ForegroundColor Yellow
Copy-Item -Recurse -Force "$RES_DIR\*" "$BUILD_DIR\classes\" 2>$null

# Utwórz JAR
Write-Host "Tworzenie JAR..." -ForegroundColor Yellow
Set-Location "$BUILD_DIR\classes"
& $JAR cvf "..\libs\CuttableBlocks-1.0.0.jar" . 2>&1 | Select-Object -Last 5
Set-Location "..\.."

Write-Host ""
Write-Host "=== SUKCES ===" -ForegroundColor Green
Write-Host "JAR utworzony: $BUILD_DIR\libs\CuttableBlocks-1.0.0.jar" -ForegroundColor Green
Write-Host ""
Write-Host "Aby przetestować:" -ForegroundColor Cyan
Write-Host "  copy $BUILD_DIR\libs\CuttableBlocks-1.0.0.jar ..\headless_server\1.7.10\mods\" -ForegroundColor White
