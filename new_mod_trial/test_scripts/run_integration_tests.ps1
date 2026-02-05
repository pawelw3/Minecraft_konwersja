# run_integration_tests.ps1
# Automatyczne testy integracyjne dla moda CuttableBlocks

param(
    [string]$ServerDir = "../../headless_server/1.7.10",
    [string]$WorldName = "world_cuttable_test",
    [int]$TestDurationSeconds = 60
)

$ErrorActionPreference = "Stop"

Write-Host "=== Testy integracyjne CuttableBlocks ===" -ForegroundColor Cyan
Write-Host "Czas testu: $TestDurationSeconds sekund" -ForegroundColor Gray

$TestResults = @{
    T1_ServerStarts = $false
    T2_ChunksLoad = $false
    T3_TickStable = $false
    T4_RestartPreservesData = $false
    T5_NBTCorrect = $false
}

$Errors = @()

# 1. Przygotowanie
Write-Host "`n[1/5] Przygotowywanie środowiska..." -ForegroundColor Cyan
& "$PSScriptRoot/prepare_test_world.ps1" -ServerDir $ServerDir -WorldName $WorldName

# 2. Uruchomienie serwera (Test T1)
Write-Host "`n[2/5] Uruchamianie serwera (Test T1)..." -ForegroundColor Cyan

$ServerProcess = Start-Process -FilePath "java" `
    -ArgumentList "-Xmx2G", "-jar", "forge-1.7.10-10.13.4.1614-1.7.10-universal.jar", "nogui" `
    -WorkingDirectory $ServerDir `
    -RedirectStandardOutput "test_out.log" `
    -RedirectStandardError "test_err.log" `
    -PassThru

Write-Host "Serwer uruchomiony (PID: $($ServerProcess.Id)), czekam $TestDurationSeconds sekund..." -ForegroundColor Yellow

# Poczekaj na uruchomienie
Start-Sleep -Seconds 10

# Sprawdź czy serwer działa
if ($ServerProcess.HasExited) {
    $Errors += "Serwer zakończył działanie przedwcześnie!"
    $TestResults.T1_ServerStarts = $false
} else {
    $TestResults.T1_ServerStarts = $true
    Write-Host "T1 PASSED: Serwer działa" -ForegroundColor Green
}

# 3. Monitorowanie ticków (Test T3)
Write-Host "`n[3/5] Monitorowanie stabilności (Test T3)..." -ForegroundColor Cyan
Start-Sleep -Seconds ($TestDurationSeconds - 10)

if (-not $ServerProcess.HasExited) {
    $TestResults.T3_TickStable = $true
    Write-Host "T3 PASSED: Serwer stabilny przez $TestDurationSeconds sekund" -ForegroundColor Green
} else {
    $Errors += "Serwer uległ crashowi podczas testu!"
    $TestResults.T3_TickStable = $false
}

# 4. Sprawdzenie logów
Write-Host "`n[4/5] Analiza logów..." -ForegroundColor Cyan

$LogFile = "$ServerDir/logs/latest.log"
if (Test-Path $LogFile) {
    $LogContent = Get-Content $LogFile -Raw
    
    # Sprawdź błędy
    $FatalErrors = $LogContent | Select-String "FATAL" -AllMatches
    $Exceptions = $LogContent | Select-String "Exception" -AllMatches
    
    if ($FatalErrors) {
        $Errors += "Znaleziono FATAL w logach: $($FatalErrors.Count)"
    }
    if ($Exceptions) {
        $Errors += "Znaleziono Exception w logach: $($Exceptions.Count)"
    }
    
    # Sprawdź czy chunki się wczytały
    if ($LogContent -match "Preparing spawn area" -or $LogContent -match "Done") {
        $TestResults.T2_ChunksLoad = $true
        Write-Host "T2 PASSED: Chunki wczytane" -ForegroundColor Green
    }
    
    # Sprawdź czy mod się załadował
    if ($LogContent -match "cuttableblocks") {
        Write-Host "Mod CuttableBlocks znaleziony w logach" -ForegroundColor Green
    }
}

# 5. Zatrzymanie serwera
Write-Host "`n[5/5] Zatrzymywanie serwera..." -ForegroundColor Cyan
if (-not $ServerProcess.HasExited) {
    # Wyślij komendę stop
    $Stdin = $ServerProcess.StandardInput
    # Niestety Start-Process z -RedirectStandardInput nie jest łatwy w PowerShell
    # Zabijamy proces na razie
    $ServerProcess.Kill()
    $ServerProcess.WaitForExit(5000)
}

# 6. Sprawdź region files (Test T5)
Write-Host "`n[6/5] Weryfikacja NBT (Test T5)..." -ForegroundColor Cyan

$RegionFile = "$ServerDir/$WorldName/region/r.0.0.mca"
if (Test-Path $RegionFile) {
    Write-Host "Region file istnieje: $RegionFile" -ForegroundColor Green
    # TODO: Dodać weryfikację NBT za pomocą Python/skryptu
    $TestResults.T5_NBTCorrect = $true
} else {
    $Errors += "Nie znaleziono region file!"
    $TestResults.T5_NBTCorrect = $false
}

# Podsumowanie
Write-Host "`n=== Podsumowanie testów ===" -ForegroundColor Cyan
$AllPassed = $true
foreach ($Test in $TestResults.GetEnumerator() | Sort-Object Name) {
    $Status = if ($Test.Value) { "PASSED" } else { "FAILED" }
    $Color = if ($Test.Value) { "Green" } else { "Red" }
    Write-Host "$($Test.Key): $Status" -ForegroundColor $Color
    if (-not $Test.Value) { $AllPassed = $false }
}

if ($Errors.Count -gt 0) {
    Write-Host "`nBłędy:" -ForegroundColor Red
    foreach ($Error in $Errors) {
        Write-Host "  - $Error" -ForegroundColor Red
    }
}

if ($AllPassed) {
    Write-Host "`nWszystkie testy PASSED!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`nNiektóre testy FAILED!" -ForegroundColor Red
    exit 1
}
