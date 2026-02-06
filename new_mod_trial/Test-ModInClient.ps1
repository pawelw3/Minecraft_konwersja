#!/usr/bin/env powershell
<#
.SYNOPSIS
    Pętla testowa dla moda CuttableBlocks - wersja PowerShell
.DESCRIPTION
    Buduje moda, kopiuje do mods\, uruchamia launcher (ręcznie), monitoruje logi
.NOTES
    Autor: AI Agent
    Wymagania: Java 8, Gradle, Minecraft 1.7.10
#>

[CmdletBinding()]
param(
    [switch]$SkipBuild,
    [switch]$SkipDeploy,
    [int]$MonitorDuration = 60
)

# Konfiguracja
$ProjectDir = "C:\Users\pawel\Minecraft_konwersja\new_mod_trial"
$MinecraftDir = "$env:APPDATA\.minecraft"
$ModsDir = "$MinecraftDir\mods"
$LogsDir = "$MinecraftDir\logs"
$CrashReportsDir = "$MinecraftDir\crash-reports"
$JarFile = "$ProjectDir\build\libs\CuttableBlocks-1.0.0.jar"

$ErrorActionPreference = "Continue"

function Write-Log($Message, $Level = "INFO") {
    $timestamp = Get-Date -Format "HH:mm:ss"
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

function Build-Mod {
    Write-Log "=" 60
    Write-Log "KROK 1: Budowanie moda (Gradle)"
    Write-Log "=" 60
    
    Push-Location $ProjectDir
    
    $env:JAVA_HOME = "C:\Program Files (x86)\Java\jdk1.8.0_202"
    
    Write-Log "Wykonuję: gradlew.bat build --no-daemon"
    & .\gradlew.bat build --no-daemon 2>&1 | Tee-Object -FilePath "build.log"
    
    $exitCode = $LASTEXITCODE
    Pop-Location
    
    if ($exitCode -ne 0) {
        Write-Log "BŁĄD BUDOWANIA! Sprawdź build.log" "ERROR"
        return $false
    }
    
    if (Test-Path $JarFile) {
        Write-Log "✅ Zbudowano: $JarFile" "SUCCESS"
        return $true
    } else {
        Write-Log "❌ Nie znaleziono pliku JAR!" "ERROR"
        return $false
    }
}

function Deploy-Mod {
    Write-Log "=" 60
    Write-Log "KROK 2: Deploy moda do mods\"
    Write-Log "=" 60
    
    if (!(Test-Path $ModsDir)) {
        New-Item -ItemType Directory -Path $ModsDir -Force | Out-Null
    }
    
    try {
        Copy-Item $JarFile "$ModsDir\CuttableBlocks-1.0.0.jar" -Force
        Write-Log "✅ Skopiowano do: $ModsDir" "SUCCESS"
        return $true
    } catch {
        Write-Log "❌ Błąd kopiowania: $_" "ERROR"
        return $false
    }
}

function Clear-OldLogs {
    Write-Log "Czyszczenie starych logów..."
    
    $files = @(
        "$LogsDir\fml-client-latest.log",
        "$LogsDir\latest.log"
    )
    
    foreach ($file in $files) {
        if (Test-Path $file) {
            Remove-Item $file -Force -ErrorAction SilentlyContinue
            Write-Log "  Usunięto: $(Split-Path $file -Leaf)"
        }
    }
}

function Start-LauncherAndWait {
    Write-Log "=" 60
    Write-Log "KROK 3: Uruchamianie launchera"
    Write-Log "=" 60
    
    $launcherPath = "F:\Users\pawel\Downloads\ShiginimaSE_v3100\Windows\Shiginima Launcher SE v3.100.exe"
    
    if (!(Test-Path $launcherPath)) {
        Write-Log "Nie znaleziono launchera: $launcherPath" "ERROR"
        return $false
    }
    
    Write-Log "Uruchamiam: Shiginima Launcher"
    Start-Process $launcherPath
    
    Write-Log "Czekam 5 sekund na uruchomienie..."
    Start-Sleep -Seconds 5
    
    Write-Log "⚠️  TERAZ MUSISZ RĘCZNIE:"
    Write-Log "   1. Kliknij 'Cancel' w dialogu aktualizacji (jeśli jest)"
    Write-Log "   2. Kliknij przycisk 'Play'"
    Write-Log ""
    
    $response = Read-Host "Naciśnij ENTER gdy Minecraft zacznie się ładować (czarne okno)"
    
    return $true
}

function Watch-ClientLogs($Duration = 60) {
    Write-Log "=" 60
    Write-Log "KROK 4: Monitorowanie logów ($Duration s)"
    Write-Log "=" 60
    
    $logFile = "$LogsDir\fml-client-latest.log"
    $startTime = Get-Date
    $lastPosition = 0
    
    $errors = @()
    $criticalErrors = @()
    $modLoaded = $false
    
    # Czekaj na pojawienie się logu
    $timeout = 30
    while (!(Test-Path $logFile) -and $timeout -gt 0) {
        Start-Sleep -Seconds 1
        $timeout--
    }
    
    if (!(Test-Path $logFile)) {
        Write-Log "Nie znaleziono pliku logów!" "ERROR"
        return @{ Errors = $errors; Critical = $criticalErrors; Loaded = $modLoaded }
    }
    
    Write-Log "Monitoring: $logFile"
    
    while ((Get-Date) - $startTime).TotalSeconds -lt $Duration {
        try {
            $content = Get-Content $logFile -Raw -ErrorAction SilentlyContinue
            if ($content) {
                $lines = $content -split "`n"
                $newLines = $lines[$lastPosition..($lines.Count-1)]
                $lastPosition = $lines.Count
                
                foreach ($line in $newLines) {
                    # Szukaj błędów moda
                    if ($line -match "cuttable.*error|cuttable.*exception|CuttableTE.*error|ClassNotFoundException.*cuttable|NoSuchMethodError.*cuttable" -and 
                        $line -notmatch "Forge Version Check") {
                        $criticalErrors += $line
                        Write-Log "🚨 BŁĄD MODA: $line" "ERROR"
                    }
                    # FML błędy
                    elseif ($line -match "FML.*ERROR|Forge.*ERROR") {
                        $errors += $line
                        Write-Log "⚠️  FML ERROR: $($line.Substring(0, [Math]::Min(80, $line.Length)))" "WARNING"
                    }
                    # Mod załadowany
                    elseif ($line -match "cuttableblocks.*loaded|cuttableblocks.*Construction|Sent event FML.*to mod cuttableblocks") {
                        $modLoaded = $true
                        Write-Log "✅ Mod event: $($line.Substring(0, [Math]::Min(80, $line.Length)))" "SUCCESS"
                    }
                }
            }
        } catch {}
        
        Start-Sleep -Milliseconds 500
    }
    
    return @{ Errors = $errors; Critical = $criticalErrors; Loaded = $modLoaded }
}

function Test-CrashReports {
    Write-Log "=" 60
    Write-Log "KROK 5: Sprawdzanie crashy"
    Write-Log "=" 60
    
    if (!(Test-Path $CrashReportsDir)) {
        Write-Log "Brak folderu crash-reports"
        return $false
    }
    
    $crashes = Get-ChildItem $CrashReportsDir -Filter "crash-*.txt" | 
               Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-5) }
    
    if ($crashes) {
        Write-Log "🚨 ZNALEZIONO NOWE CRASHY: $($crashes.Count)" "ERROR"
        foreach ($crash in $crashes) {
            Write-Log "   - $($crash.Name)"
            # Pokaż fragmenty o cuttable
            $content = Get-Content $crash.FullName -Raw
            if ($content -match "cuttable|CuttableTE") {
                Write-Log "   >>> Zawiera odniesienia do moda!" "ERROR"
            }
        }
        return $true
    } else {
        Write-Log "✅ Brak nowych crashy" "SUCCESS"
        return $false
    }
}

function Show-Report($Results) {
    Write-Log "=" 60
    Write-Log "RAPORT KOŃCOWY"
    Write-Log "=" 60
    
    Write-Host ""
    Write-Host "╔" -NoNewline; Write-Host ("═" * 58) -NoNewline; Write-Host "╗"
    Write-Host "║" -NoNewline; Write-Host " REZULTATY TESTU ".PadLeft(29).PadRight(58) -NoNewline; Write-Host "║"
    Write-Host "╠" -NoNewline; Write-Host ("═" * 58) -NoNewline; Write-Host "╣"
    
    $loadedStr = if ($Results.Loaded) { "✅ TAK" } else { "❌ NIE" }
    Write-Host "║ Mod załadowany: $loadedStr".PadRight(59) -NoNewline; Write-Host "║"
    
    $criticalCount = $Results.Critical.Count
    $criticalColor = if ($criticalCount -eq 0) { "Green" } else { "Red" }
    Write-Host "║ Błędy krytyczne: $criticalCount".PadRight(59) -NoNewline; Write-Host "║" -ForegroundColor $criticalColor
    
    $errorCount = $Results.Errors.Count
    Write-Host "║ Błędy ogólne: $errorCount".PadRight(59) -NoNewline; Write-Host "║"
    
    Write-Host "╠" -NoNewline; Write-Host ("═" * 58) -NoNewline; Write-Host "╣"
    
    if ($Results.Critical) {
        Write-Host "║ 🚨 BŁĘDY MODA (wymagają poprawki):".PadRight(59) -NoNewline; Write-Host "║"
        foreach ($err in $Results.Critical | Select-Object -First 3) {
            $short = if ($err.Length -gt 55) { $err.Substring(0, 55) + "..." } else { $err }
            Write-Host "║    $short".PadRight(59) -NoNewline; Write-Host "║"
        }
    }
    
    Write-Host "╚" -NoNewline; Write-Host ("═" * 58) -NoNewline; Write-Host "╝"
    
    return ($criticalCount -eq 0 -and $Results.Loaded)
}

# ============ GŁÓWNY PROGRAM ============

Write-Host ""
Write-Host "=" * 60
Write-Host " PĘTLA TESTOWA CUTTABLEBLOCKS (PowerShell)"
Write-Host "=" * 60
Write-Host ""

# 1. Build
if (!$SkipBuild) {
    if (!(Build-Mod)) { exit 1 }
} else {
    Write-Log "Pominięto budowanie (--SkipBuild)"
}

# 2. Deploy
if (!$SkipDeploy) {
    if (!(Deploy-Mod)) { exit 1 }
} else {
    Write-Log "Pominięto deploy (--SkipDeploy)"
}

# 3. Clear logs
Clear-OldLogs

# 4. Launch (ręczny)
if (!(Start-LauncherAndWait)) { exit 1 }

# 5. Monitor logs
$results = Watch-ClientLogs -Duration $MonitorDuration

# 6. Check crashes
$c hasCrashes = Test-CrashReports

# 7. Report
$success = Show-Report $results

if ($success) {
    Write-Log "✅ TEST ZALICZONY - Mod działa poprawnie!" "SUCCESS"
    exit 0
} else {
    Write-Log "❌ TEST NIEZALICZONY - Są błędy do naprawy" "ERROR"
    exit 1
}
