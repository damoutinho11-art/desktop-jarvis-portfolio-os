$ErrorActionPreference = "Stop"

Set-Location -Path $PSScriptRoot

$currentDate = Get-Date -Format "yyyy-MM-dd"

Write-Host ""
Write-Host "============================================================"
Write-Host " J.A.R.V.I.S. Portfolio OS"
Write-Host " Safe daily manual-use launcher"
Write-Host "============================================================"
Write-Host ""
Write-Host "Current date: $currentDate"
Write-Host ""
Write-Host "Running daily operator..."
Write-Host ""

python "$PSScriptRoot\jarvis_operator.py" --daily-operator --current-date $currentDate --max-targets 10

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "============================================================"
    Write-Host " J.A.R.V.I.S. needs review. Dashboard was not opened."
    Write-Host "============================================================"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

$dashboard = Join-Path $PSScriptRoot "outputs\dashboard_latest.html"
$appBaseUrl = "http://127.0.0.1:8765"

Write-Host ""
Write-Host "============================================================"
Write-Host " J.A.R.V.I.S. daily operator completed."
Write-Host " Opening local app dashboard and chat..."
Write-Host "============================================================"
Write-Host ""

Write-Host "Starting local app server at $appBaseUrl ..."
Start-Process -WindowStyle Hidden python -ArgumentList @(
    "$PSScriptRoot\jarvis_operator.py",
    "--local-server",
    "--current-date",
    $currentDate,
    "--host",
    "127.0.0.1",
    "--port",
    "8765"
)

Start-Sleep -Seconds 2

$appReady = $false
try {
    $health = Invoke-WebRequest -UseBasicParsing -Uri "$appBaseUrl/health" -TimeoutSec 5
    $appReady = $health.StatusCode -eq 200
} catch {
    $appReady = $false
}

if ($appReady) {
    Start-Process "$appBaseUrl/dashboard"
    Start-Process "$appBaseUrl/chat"
} else {
    Write-Host "Local app was not ready yet. Opening static dashboard fallback if available..."
    if (Test-Path $dashboard) {
        Start-Process $dashboard
    } else {
        Write-Host "Dashboard fallback file was not found: $dashboard"
    }
}

Write-Host ""
Write-Host "Safety reminder:"
Write-Host "- Manual approval required."
Write-Host "- Diogo makes any real-world purchase outside J.A.R.V.I.S."
Write-Host "- No broker. No credentials. No orders. No trades. No auto-approval."
Write-Host ""
Read-Host "Press Enter to exit"
