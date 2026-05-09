[CmdletBinding()]
param(
    [string]$Root = "D:\The_Compound",
    [int]$Port = 8765
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[The Compound] $Message"
}

$pidFile = Join-Path $Root "data\the_compound.pid"
$taskName = "TheCompoundServer"
$pids = @()

if (Test-Path $pidFile) {
    try {
        $pidText = (Get-Content $pidFile -ErrorAction Stop | Select-Object -First 1).Trim()
        if ($pidText -match "^\d+$") {
            $pids += [int]$pidText
        }
    } catch {
        Write-Step "Could not read PID file: $pidFile"
    }
}

$listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
foreach ($listener in $listeners) {
    if ($listener.OwningProcess -and $listener.OwningProcess -ne 0) {
        $pids += [int]$listener.OwningProcess
    }
}

$pids = $pids | Sort-Object -Unique

if (-not $pids -or $pids.Count -eq 0) {
    Write-Step "No running server found on port $Port."
    Stop-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    exit 0
}

foreach ($processId in $pids) {
    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
    if (-not $process) {
        continue
    }

    Write-Step "Stopping PID $processId ($($process.ProcessName))."
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
}

Stop-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Milliseconds 300
    $stillListening = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $stillListening) {
        break
    }
}

Remove-Item $pidFile -Force -ErrorAction SilentlyContinue

$remaining = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($remaining) {
    Write-Step "Port $Port is still listening. Check Task Manager or run this script as Administrator."
    exit 1
}

Write-Step "Stopped. Port $Port is clear."
