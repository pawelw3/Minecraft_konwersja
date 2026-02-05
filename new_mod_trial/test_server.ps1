# Test serwera - uruchamia i sprawdza czy dziala

$ErrorActionPreference = "Stop"

$serverDir = "C:\Users\pawel\Minecraft_konwersja\headless_server\1.7.10"
$jar = "forge-1.7.10-10.13.4.1614-1.7.10-universal.jar"

Set-Location $serverDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TEST SERWERA CUTTABLE BLOCKS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Sprawdz czy JAR istnieje
if (-not (Test-Path $jar)) {
    Write-Host "BLAD: Nie znaleziono $jar" -ForegroundColor Red
    exit 1
}

# Upewnij sie ze mods istnieje
if (-not (Test-Path "mods")) {
    New-Item -ItemType Directory -Path "mods" -Force | Out-Null
}

# Utworz katalog dla swiata jesli nie istnieje
if (-not (Test-Path "world_cuttable_test")) {
    Write-Host "BLAD: Nie znaleziono swiata world_cuttable_test" -ForegroundColor Red
    exit 1
}

Write-Host "Swiat: world_cuttable_test" -ForegroundColor Yellow
Write-Host "Nacisnij Ctrl+C aby zatrzymac" -ForegroundColor Gray
Write-Host ""

# Usun stare logi
if (Test-Path "logs\latest.log") {
    Remove-Item "logs\latest.log" -Force
}

# Uruchom serwer
Write-Host "Uruchamianie serwera..." -ForegroundColor Green
& java -Xmx1G -jar $jar nogui

Write-Host ""
Write-Host "Serwer zatrzymany" -ForegroundColor Cyan
