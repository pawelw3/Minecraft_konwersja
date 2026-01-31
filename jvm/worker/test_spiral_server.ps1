# Test serwera ze spiralą redstone
param(
    [Parameter(Mandatory=$true)]
    [string]$WorldPath,
    
    [int]$TimeoutSeconds = 45
)

$ErrorActionPreference = "Stop"
$serverDir = "..\..\headless_server\1.7.10"
$worldName = "test_spiral_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$targetWorld = Join-Path $serverDir $worldName

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Test serwera ze spiralą redstone" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Świat źródłowy: $WorldPath"
Write-Host "Świat docelowy: $targetWorld"
Write-Host "Timeout: $TimeoutSeconds sekund"

# Sprawdź czy istnieje Java 8
$java8Paths = @(
    "C:\Program Files (x86)\Common Files\Oracle\Java\java8path\java.exe",
    "C:\Program Files\Java\jdk1.8.0_*.\bin\java.exe",
    "C:\Program Files (x86)\Java\jdk1.8.0_*.\bin\java.exe"
)

$javaExe = $null
foreach ($path in $java8Paths) {
    $found = Get-Item $path -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $javaExe = $found.FullName
        break
    }
}

if (-not $javaExe) {
    Write-Host "FAIL: Nie znaleziono Java 8" -ForegroundColor Red
    exit 1
}

Write-Host "Znaleziono Java: $javaExe"

# Skopiuj świat
Write-Host "`nKopiowanie świata..."
if (Test-Path $targetWorld) {
    Remove-Item -Recurse -Force $targetWorld
}
Copy-Item -Recurse -Force $WorldPath $targetWorld

# Przygotuj server.properties
$serverProperties = @"
server-port=25566
online-mode=false
level-name=$worldName
enable-command-block=true
gamemode=1
max-players=1
allow-flight=true
spawn-protection=0
"@

$propsPath = Join-Path $serverDir "server.properties"
$serverProperties | Out-File -FilePath $propsPath -Encoding ASCII

Write-Host "Server properties zapisane"

# Uruchom serwer
Write-Host "`nUruchamianie serwera (timeout: $TimeoutSeconds sekund)..." -ForegroundColor Yellow
$javaOpts = "-Xms2G -Xmx4G -XX:+UseG1GC -XX:MaxGCPauseMillis=200"
$serverJar = "forge-1.7.10-10.13.4.1614-1.7.10-universal.jar"

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $javaExe
$psi.Arguments = "$javaOpts -jar $serverJar nogui"
$psi.WorkingDirectory = $serverDir
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true

$process = [System.Diagnostics.Process]::Start($psi)

# Czekaj na zakończenie lub timeout
$timer = [System.Diagnostics.Stopwatch]::StartNew()
$probeCount = 0
$foundDone = $false

try {
    while (-not $process.HasExited -and $timer.Elapsed.TotalSeconds -lt $TimeoutSeconds) {
        # Odczytaj stdout
        while ($process.StandardOutput.Peek() -gt -1) {
            $line = $process.StandardOutput.ReadLine()
            
            if ($line -match "\[ROUNDTRIP\]") {
                Write-Host "ROUNDTRIP: $line" -ForegroundColor Green
            }
            elseif ($line -match "\[PROBE\]") {
                Write-Host "PROBE: $line" -ForegroundColor Cyan
                $probeCount++
            }
            elseif ($line -match "Done \(") {
                Write-Host "Serwer gotowy: $line" -ForegroundColor Green
                $foundDone = $true
            }
            elseif ($line -match "FATAL|ERROR|Exception" -and $line -notmatch "Expected") {
                Write-Host "ERROR: $line" -ForegroundColor Red
            }
        }
        
        Start-Sleep -Milliseconds 100
    }
} finally {
    $timer.Stop()
    
    if (-not $process.HasExited) {
        Write-Host "`nZatrzymywanie serwera..." -ForegroundColor Yellow
        $process.Kill()
        Start-Sleep -Seconds 2
    }
}

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "PODSUMOWANIE" -ForegroundColor Cyan
Write-Host "=========================================="
Write-Host "Czas działania: $($timer.Elapsed.TotalSeconds.ToString('F1')) sekund"
Write-Host "Znaleziono [PROBE]: $probeCount"
Write-Host "Serwer gotowy: $foundDone"

# Sprawdź logi
$logFile = Join-Path $serverDir "logs\latest.log"
if (Test-Path $logFile) {
    $logContent = Get-Content $logFile -Raw
    $probeMatches = [regex]::Matches($logContent, "\[PROBE\].*")
    Write-Host "Wszystkich [PROBE] w logach: $($probeMatches.Count)"
    
    if ($probeMatches.Count -gt 0) {
        Write-Host "`nPrzykladowe logi [PROBE]:" -ForegroundColor Green
        $probeMatches | Select-Object -First 5 | ForEach-Object {
            Write-Host "  $($_.Value)"
        }
    }
}

# Sprzątanie
Write-Host "`nSprzątanie..."
if (Test-Path $targetWorld) {
    Remove-Item -Recurse -Force $targetWorld
}

# Wynik
if ($probeCount -gt 0 -or ($probeMatches -and $probeMatches.Count -gt 0)) {
    Write-Host "`nTEST PASS: Command blocki wykonały się!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`nTEST FAIL: Nie znaleziono logów [PROBE]" -ForegroundColor Red
    exit 1
}
