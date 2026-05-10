param(
    [ValidateSet("Trey", "Joe")]
    [string]$ProfileName = "Trey"
)

$ErrorActionPreference = "Stop"

if ($ProfileName -eq "Joe") {
    $WorktreePath = "D:\The_Compound_Worktrees\Joe"
    $Port = "8767"
} else {
    $WorktreePath = "D:\The_Compound_Worktrees\Trey"
    $Port = "8766"
}

if (-not (Test-Path -LiteralPath $WorktreePath)) {
    throw "Worktree not found: $WorktreePath"
}

Set-Location $WorktreePath

$env:MUD_HOST = "0.0.0.0"
$env:MUD_PORT = $Port
$env:LOG_DIR = Join-Path $WorktreePath "data\logs"

Write-Host "Starting The Compound dev HUD for $ProfileName"
Write-Host "Worktree: $WorktreePath"
Write-Host "URL: http://127.0.0.1:$Port"
Write-Host "Live Compound remains on http://127.0.0.1:8765"

python (Join-Path $WorktreePath "engine\server.py")
