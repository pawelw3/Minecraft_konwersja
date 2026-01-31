#!/usr/bin/env powershell
# Skrypt uruchamiający test spiralny i zbierający logi

$serverDir = Join-Path $PSScriptRoot "..\1.7.10"
$logFile = Join-Path $PSScriptRoot "spiral_test_output.log"
$duration = 120  # sekundy

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TEST SPIRALNY - Variant B" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Czas trwania: $duration sekund"
Write-Host "Logi będą zapisywane do: $logFile"
Write-Host ""

# Sprawdź czy serwer istnieje
$serverJar = Join-Path $serverDir "minecraft_server.1.7.10.jar"
if (-not (Test-Path $serverJar)) {
    Write-Error "Nie znaleziono serwera: $serverJar"
    exit 1
}

# Usuń stare logi
$logsDir = Join-Path $serverDir "logs"
if (Test-Path $logsDir) {
    Remove-Item "$logsDir\*" -Recurse -Force -ErrorAction SilentlyContinue
}

# Przejdź do katalogu serwera
Push-Location $serverDir

# Przygotuj proces serwera
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = "java"
$psi.Arguments = "-Xmx1G -Xms512M -jar minecraft_server.1.7.10.jar nogui"
$psi.WorkingDirectory = $serverDir
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true

Write-Host "Uruchamianie serwera..." -ForegroundColor Yellow
$process = [System.Diagnostics.Process]::Start($psi)

# Czekaj na pełne uruchomienie (max 60s)
$startTime = Get-Date
$serverReady = $false
$timeout = 60

while (-not $serverReady -and ((Get-Date) - $startTime).TotalSeconds -lt $timeout) {
    Start-Sleep -Milliseconds 500
    $latestLog = Join-Path $logsDir "latest.log"
    if (Test-Path $latestLog) {
        $content = Get-Content $latestLog -Raw -ErrorAction SilentlyContinue
        if ($content -match "Done \(.*\)!") {
            $serverReady = $true
        }
    }
}

if (-not $serverReady) {
    Write-Warning "Serwer nie potwierdził gotowości w czasie $timeout sekund, ale kontynuujemy..."
}

$actualStartTime = Get-Date
Write-Host "Serwer uruchomiony! Rozpoczynam zbieranie logów na $duration sekund..." -ForegroundColor Green
Write-Host "Czas startu: $actualStartTime"
Write-Host ""

# Zbieraj logi przez określony czas
$endTime = $actualStartTime.AddSeconds($duration)
$allLogs = @()

while ((Get-Date) -lt $endTime) {
    $remaining = [math]::Ceiling(($endTime - (Get-Date)).TotalSeconds)
    Write-Host -NoNewline "`rPozostało: $remaining sekund...    "
    
    $latestLog = Join-Path $logsDir "latest.log"
    if (Test-Path $latestLog) {
        $lines = Get-Content $latestLog -ErrorAction SilentlyContinue
        $probeLines = $lines | Select-String "\[PROBE\]" | ForEach-Object { $_.Line }
        if ($probeLines) {
            $allLogs += $probeLines
        }
    }
    
    Start-Sleep -Milliseconds 1000
}

Write-Host ""
Write-Host ""
Write-Host "Zatrzymywanie serwera..." -ForegroundColor Yellow

# Wyślij komendę stop
$psi_stdin = $process.StandardInput
$psi_stdin.WriteLine("stop")

# Czekaj na zatrzymanie (max 30s)
if (-not $process.WaitForExit(30000)) {
    Write-Warning "Serwer nie zatrzymał się w czasie, zabijam proces..."
    $process.Kill()
}

Pop-Location

# Zapisz zebrane logi
$allLogs | Out-File $logFile

# Analiza wyników
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ANALIZA WYNIKÓW" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$uniqueSteps = @{}
$pattern = '\[PROBE\] REACHED cx=(-?\d+) cz=(-?\d+) step=(\d+)'

foreach ($line in $allLogs) {
    if ($line -match $pattern) {
        $step = [int]$matches[3]
        $cx = [int]$matches[1]
        $cz = [int]$matches[2]
        if (-not $uniqueSteps.ContainsKey($step)) {
            $uniqueSteps[$step] = @($cx, $cz)
        }
    }
}

$sortedSteps = $uniqueSteps.Keys | Sort-Object
$totalSteps = 121  # Dla R=5

Write-Host ""
Write-Host "Statystyki:" -ForegroundColor Green
Write-Host "  Odebranych unikalnych kroków: $($uniqueSteps.Count) / $totalSteps"
Write-Host "  Ostatni odebrany krok: $($sortedSteps[-1])"
Write-Host ""

if ($sortedSteps.Count -gt 0) {
    # Sprawdź czy są dziury
    $expectedSteps = 0..$($sortedSteps[-1])
    $missing = $expectedSteps | Where-Object { $_ -notin $sortedSteps }
    
    if ($missing) {
        Write-Host "BRAKUJĄCE KROKI (dziury):" -ForegroundColor Red
        $missing | ForEach-Object { $m = $_; Write-Host "  - step ${m}" }
    } else {
        Write-Host "Wszystkie kroki od 0 do $($sortedSteps[-1]) są obecne!" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "Pierwsze 10 odebranych kroków:" -ForegroundColor Yellow
    $sortedSteps | Select-Object -First 10 | ForEach-Object {
        $stepNum = $_
        $coords = $uniqueSteps[$stepNum]
        Write-Host "  step ${stepNum}: chunk ($($coords[0]), $($coords[1]))"
    }
    
    if ($sortedSteps.Count -gt 10) {
        Write-Host ""
        Write-Host "Ostatnie 5 odebranych kroków:" -ForegroundColor Yellow
        $sortedSteps | Select-Object -Last 5 | ForEach-Object {
            $stepNum = $_
            $coords = $uniqueSteps[$stepNum]
            Write-Host "  step ${stepNum}: chunk ($($coords[0]), $($coords[1]))"
        }
    }
}

# Oznacz PASS/FAIL
Write-Host ""
Write-Host "WERYFIKACJA TESTU:" -ForegroundColor Cyan
if ($sortedSteps.Count -ge 2 -and 0 -in $sortedSteps -and 1 -in $sortedSteps) {
    Write-Host "  Status: PASS (sygnał przeszedł przez co najmniej 2 chunki)" -ForegroundColor Green
} else {
    Write-Host "  Status: FAIL (brak sygnału lub tylko start)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Pełne logi zapisane w: $logFile"
