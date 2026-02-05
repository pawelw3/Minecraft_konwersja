# prepare_test_world.ps1
# Skrypt przygotowujący mapę testową dla moda CuttableBlocks

param(
    [string]$ServerDir = "../../headless_server/1.7.10",
    [string]$WorldName = "world_cuttable_test"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Przygotowywanie mapy testowej CuttableBlocks ===" -ForegroundColor Cyan

# 1. Sprawdź czy istnieje mapa testowa w test_worlds/
$SourceWorld = "../test_worlds/cuttable_test_base"
if (-not (Test-Path "$SourceWorld/level.dat")) {
    Write-Host "WARNING: Nie znaleziono mapy testowej w $SourceWorld" -ForegroundColor Yellow
    Write-Host "Mapa musi być stworzona ręcznie w kliencie deweloperskim." -ForegroundColor Yellow
    Write-Host "Naciśnij dowolny klawisz gdy mapa będzie gotowa..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# 2. Utwórz backup aktualnego świata (jeśli istnieje)
$TargetWorld = "$ServerDir/$WorldName"
if (Test-Path $TargetWorld) {
    $BackupName = "$WorldName-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Write-Host "Tworzenie backupu istniejącego świata..." -ForegroundColor Yellow
    Rename-Item $TargetWorld "$ServerDir/$BackupName"
    Write-Host "Backup zapisany jako: $BackupName" -ForegroundColor Green
}

# 3. Skopiuj mapę testową
Write-Host "Kopiowanie mapy testowej..." -ForegroundColor Cyan
Copy-Item -Recurse $SourceWorld $TargetWorld
Write-Host "Mapa skopiowana do: $TargetWorld" -ForegroundColor Green

# 4. Skopiuj JAR moda do mods/
$ModJar = "../build/libs/CuttableBlocks-1.0.0.jar"
if (Test-Path $ModJar) {
    Write-Host "Kopiowanie JAR moda..." -ForegroundColor Cyan
    Copy-Item $ModJar "$ServerDir/mods/"
    Write-Host "Mod skopiowany do mods/" -ForegroundColor Green
} else {
    Write-Host "WARNING: Nie znaleziono $ModJar - zbuduj mod najpierw!" -ForegroundColor Red
}

# 5. Przygotuj server.properties
$PropsFile = "$ServerDir/server.properties"
if (Test-Path $PropsFile) {
    Write-Host "Aktualizowanie server.properties..." -ForegroundColor Cyan
    $Content = Get-Content $PropsFile -Raw
    $Content = $Content -replace "level-name=.*", "level-name=$WorldName"
    $Content = $Content -replace "online-mode=.*", "online-mode=false"
    $Content | Set-Content $PropsFile
    Write-Host "server.properties zaktualizowany" -ForegroundColor Green
}

Write-Host "=== Gotowe! ===" -ForegroundColor Green
Write-Host "Uruchom serwer: cd $ServerDir; .\run.bat" -ForegroundColor Cyan
