param(
    [string]$RawBase = "https://raw.githubusercontent.com/kapustazh/zelenskyy-codex-pet/main"
)

$ErrorActionPreference = "Stop"
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
$petRoot = Join-Path $codexHome "pets"
$target = Join-Path $petRoot "zelenskyy"
$stamp = Get-Date -Format "yyyyMMddHHmmss"
$backup = Join-Path $petRoot ".zelenskyy.backup.$stamp"
$temporary = Join-Path ([System.IO.Path]::GetTempPath()) ("zelenskyy-codex-pet-" + [guid]::NewGuid().ToString("N"))
$staged = Join-Path $temporary "zelenskyy"
$hadBackup = $false

try {
    New-Item -ItemType Directory -Force -Path $staged | Out-Null
    Invoke-WebRequest -UseBasicParsing -MaximumRedirection 5 -TimeoutSec 120 "$RawBase/pet.json" -OutFile (Join-Path $staged "pet.json")
    Invoke-WebRequest -UseBasicParsing -MaximumRedirection 5 -TimeoutSec 120 "$RawBase/spritesheet.webp" -OutFile (Join-Path $staged "spritesheet.webp")

    $metadata = Get-Content -Raw (Join-Path $staged "pet.json") | ConvertFrom-Json
    if ($metadata.id -ne "zelenskyy" -or $metadata.spriteVersionNumber -ne 2) {
        throw "Downloaded metadata is not the expected Zelenskyy v2 pet."
    }
    if ((Get-Item (Join-Path $staged "spritesheet.webp")).Length -lt 1000) {
        throw "Downloaded spritesheet is unexpectedly small."
    }

    New-Item -ItemType Directory -Force -Path $petRoot | Out-Null
    if (Test-Path -LiteralPath $target) {
        Move-Item -LiteralPath $target -Destination $backup
        $hadBackup = $true
    }
    Move-Item -LiteralPath $staged -Destination $target
    if ($hadBackup) {
        Remove-Item -LiteralPath $backup -Recurse -Force
        $hadBackup = $false
    }
    Write-Host "Installed Zelenskyy to $target"
    Write-Host "Restart Codex, then select Zelenskyy in Settings > Pets."
}
catch {
    if ($hadBackup -and -not (Test-Path -LiteralPath $target)) {
        Move-Item -LiteralPath $backup -Destination $target
    }
    throw
}
finally {
    if (Test-Path -LiteralPath $temporary) {
        Remove-Item -LiteralPath $temporary -Recurse -Force
    }
}
