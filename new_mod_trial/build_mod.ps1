# build_mod.ps1 - Skrypt budujący mod CuttableBlocks

$ErrorActionPreference = "Stop"

Write-Host "=== Budowanie CuttableBlocks ===" -ForegroundColor Cyan

# Sprawdź czy Java jest dostępna
try {
    $javaVersion = java -version 2>&1 | Select-String "version" | Select-Object -First 1
    Write-Host "Znaleziono Java: $javaVersion" -ForegroundColor Green
} catch {
    Write-Host "BŁĄD: Java nie jest zainstalowana lub nie ma jej w PATH" -ForegroundColor Red
    exit 1
}

# Sprawdź czy Gradle jest dostępny (lokalnie lub globalnie)
$gradleCmd = $null
if (Test-Path "./gradlew.bat") {
    $gradleCmd = ".\gradlew.bat"
    Write-Host "Używam Gradle wrappera" -ForegroundColor Yellow
} elseif (Get-Command "gradle" -ErrorAction SilentlyContinue) {
    $gradleCmd = "gradle"
    Write-Host "Używam systemowego Gradle" -ForegroundColor Yellow
} else {
    Write-Host "BŁĄD: Nie znaleziono Gradle. Zainstaluj Gradle lub pobierz wrapper." -ForegroundColor Red
    exit 1
}

# Wyczyść poprzednie buildy
Write-Host "`nCzyszczenie poprzednich buildów..." -ForegroundColor Cyan
& $gradleCmd clean
if ($LASTEXITCODE -ne 0) {
    Write-Host "BŁĄD podczas czyszczenia" -ForegroundColor Red
    exit 1
}

# Buduj mod
Write-Host "`nBudowanie moda..." -ForegroundColor Cyan
& $gradleCmd build
if ($LASTEXITCODE -ne 0) {
    Write-Host "BŁĄD podczas budowania" -ForegroundColor Red
    exit 1
}

# Sprawdź czy JAR powstał
$jarPath = "./build/libs/CuttableBlocks-1.0.0.jar"
if (Test-Path $jarPath) {
    $jarSize = (Get-Item $jarPath).Length / 1KB
    Write-Host "`nSUKCES! Zbudowano mod:" -ForegroundColor Green
    Write-Host "  $jarPath ($([math]::Round($jarSize, 2)) KB)" -ForegroundColor Green
    
    # Pokaż zawartość JAR
    Write-Host "`nZawartość JAR:" -ForegroundColor Gray
    jar tf $jarPath | Select-String -Pattern "(\.class$|mcmod.info|\.png$|\.lang$)" | ForEach-Object { "  $_" }
} else {
    Write-Host "BŁĄD: Nie znaleziono pliku JAR" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Budowanie zakończone ===" -ForegroundColor Cyan
