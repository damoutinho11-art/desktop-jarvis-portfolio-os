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
Write-Host "Safety reminder:"
Write-Host "- Manual approval required."
Write-Host "- Buy outside J.A.R.V.I.S."
Write-Host "- No broker, credential, order, trade, or auto-approval path is enabled."
Write-Host ""
Read-Host "Press Enter to exit"
