[CmdletBinding()]
param(
    [string]$Root = "D:\The_Compound",
    [int]$Port = 8765,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[The Compound] $Message"
}

function Resolve-CompoundPython {
    param([string]$ProjectRoot)

    $candidates = @(
        "C:\Python313\python.exe",
        (Join-Path $ProjectRoot ".python\python.exe"),
        "python"
    )

    foreach ($candidate in $candidates) {
        if ($candidate -ne "python" -and -not (Test-Path $candidate)) {
            continue
        }

        try {
            & $candidate -c "import websockets" *> $null
            if ($LASTEXITCODE -eq 0) {
                return $candidate
            }
        } catch {
            continue
        }
    }

    throw "No Python runtime found that can import websockets."
}

if (-not (Test-Path $Root)) {
    throw "Project root not found: $Root"
}

$serverPath = Join-Path $Root "engine\server.py"
if (-not (Test-Path $serverPath)) {
    throw "Server file not found: $serverPath"
}

$logDir = Join-Path $Root "data\logs"
New-Item -ItemType Directory -Force $logDir | Out-Null

$localUrl = "http://127.0.0.1:$Port/"
$remoteUrl = "http://100.87.143.16:$Port/"
$pidFile = Join-Path $Root "data\the_compound.pid"
$taskName = "TheCompoundServer"
$runner = Join-Path $Root "scripts\Run-TheCompoundServer.cmd"

$listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($listener) {
    Write-Step "Already running on port $Port as PID $($listener.OwningProcess)."
    Write-Step "Local HUD:  $localUrl"
    Write-Step "Remote HUD: $remoteUrl"
    if (-not $NoBrowser) {
        Start-Process $localUrl
    }
    exit 0
}

if (-not (Test-Path $runner)) {
    throw "Scheduled-task runner not found: $runner"
}

$python = Resolve-CompoundPython -ProjectRoot $Root

Write-Step "Starting server from $Root"
Write-Step "Python: $python"

$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$runner`""
# AtStartup so the server survives reboots; SYSTEM so it starts before any login.
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
# RestartCount/RestartInterval make a crashed server self-heal within ~1 minute.
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount 999 `
    -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings `
    -Description "Runs The Compound shared workspace server from D:\The_Compound." `
    -Force | Out-Null

Start-ScheduledTask -TaskName $taskName

$started = $false
$owningPid = $null
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Milliseconds 500
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $localUrl -TimeoutSec 2
        if ([int]$response.StatusCode -eq 200 -and $response.Content -match "The Compound - Portal HUD") {
            $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($listener) {
                $owningPid = $listener.OwningProcess
                Set-Content -Path $pidFile -Value $owningPid -Encoding ASCII
            }
            $started = $true
            break
        }
    } catch {
        # Keep waiting while the Python server finishes booting.
    }
}

if (-not $started) {
    Write-Step "Server did not pass the local HUD check."
    $errLog = Join-Path $logDir "the-compound-server.err.log"
    if (Test-Path $errLog) {
        Get-Content $errLog -Tail 80
    }
    Stop-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    exit 1
}

if ($owningPid) {
    Write-Step "Running as PID $owningPid."
} else {
    Write-Step "Running."
}
Write-Step "Local HUD:  $localUrl"
Write-Step "Remote HUD: $remoteUrl"
Write-Step "Logs: $logDir"

if (-not $NoBrowser) {
    Start-Process $localUrl
}
