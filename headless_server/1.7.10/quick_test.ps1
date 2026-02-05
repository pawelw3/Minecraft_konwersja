# Szybki test serwera - uruchamia na 30 sekund

$serverDir = $PSScriptRoot
$jar = "forge-1.7.10-10.13.4.1614-1.7.10-universal.jar"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "SZYBKI TEST SERWERA CUTTABLE BLOCKS" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Sprawdz czy JAR istnieje
if (-not (Test-Path "$serverDir\$jar")) {
    Write-Host "BLAD: Nie znaleziono $jar" -ForegroundColor Red
    exit 1
}

# Upewnij sie ze mods istnieje
if (-not (Test-Path "$serverDir\mods")) {
    New-Item -ItemType Directory -Path "$serverDir\mods" -Force | Out-Null
}

Write-Host "Swiat: world_cuttable_test" -ForegroundColor Yellow
Write-Host "27 blokow ukosnych wstawionych" -ForegroundColor Yellow
Write-Host ""

# Uruchom serwer w tle
$proc = Start-Process -FilePath "java" -ArgumentList "-Xmx1G", "-jar", $jar, "nogui" -WorkingDirectory $serverDir -PassThru -WindowStyle Hidden

Write-Host "Serwer uruchomiony (PID: $($proc.Id))" -ForegroundColor Green
Write-Host "Czekam 30 sekund na inicjalizacje..." -ForegroundColor Gray

# Czekaj 30 sekund
for ($i = 30; $i -gt 0; $i--) {
    Write-Host -NoNewline "`rPozostalo: $i sekund...    "
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host ""

# Sprawdz logi
$logFile = "$serverDir\logs\latest.log"
if (Test-Path $logFile) {
    $logContent = Get-Content $logFile -Tail 50
    
    if ($logContent -match "Done") {
        Write-Host "OK: Serwer uruchomil sie poprawnie!" -ForegroundColor Green
    } else {
        Write-Host "WARN: Serwer moze miec problemy" -ForegroundColor Yellow
    }
    
    $errors = $logContent | Select-String "Error|Exception" | Select-Object -First 5
    if ($errors) {
        Write-Host "ERR: Znaleziono bledy w logach:" -ForegroundColor Red
        $errors | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    }
}

# Zatrzymaj serwer
Write-Host ""
Write-Host "Zatrzymywanie serwera..." -ForegroundColor Gray
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "TEST ZAKONCZONY" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
