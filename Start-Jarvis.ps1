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

Write-Host ""
Write-Host "============================================================"
Write-Host " J.A.R.V.I.S. daily operator completed."
Write-Host " Opening dashboard..."
Write-Host "============================================================"
Write-Host ""

if (Test-Path $dashboard) {
    Start-Process $dashboard
} else {
    Write-Host "Dashboard file was not found: $dashboard"
}

Write-Host ""
if ($env:JARVIS_OPEN_CHAT -eq "1") {
    Write-Host "Opening local chat at http://127.0.0.1:8765/chat ..."
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
    Start-Process "http://127.0.0.1:8765/chat"
} else {
    Write-Host "Optional chat is off. To open it:"
    Write-Host '$env:JARVIS_OPEN_CHAT = "1"'
    Write-Host ".\Start-Jarvis.ps1"
}

Write-Host ""
Write-Host "Safety reminder:"
Write-Host "- Manual approval required."
Write-Host "- Diogo makes any real-world purchase outside J.A.R.V.I.S."
Write-Host "- No broker. No credentials. No orders. No trades. No auto-approval."
Write-Host ""
Read-Host "Press Enter to exit"
