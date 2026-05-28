param(
    [Parameter(Mandatory = $true)]
    [string]$SourcePath,

    [Parameter(Mandatory = $true)]
    [string]$TargetPath,

    [string]$WorkDir = "C:\tmp\aw_runner_work"
)

$ErrorActionPreference = "Stop"

$gradlew = Join-Path $WorkDir "gradlew.bat"
if (-not (Test-Path -LiteralPath $gradlew)) {
    throw "Armourer's Workshop runner workdir is missing gradlew.bat: $WorkDir"
}

$SourcePath = (Resolve-Path -LiteralPath $SourcePath).Path
$targetParent = Split-Path -Parent $TargetPath
if ($targetParent) {
    New-Item -ItemType Directory -Path $targetParent -Force | Out-Null
}
$TargetPath = [System.IO.Path]::GetFullPath($TargetPath)

& $gradlew -p $WorkDir :forge:runSkinLibraryConvertCli "-PawSource=$SourcePath" "-PawTarget=$TargetPath" --no-daemon --console=plain
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
