@echo off
setlocal
title J.A.R.V.I.S. Portfolio OS

cd /d "%~dp0"

echo.
echo ============================================================
echo  J.A.R.V.I.S. Portfolio OS
echo  Safe daily manual-use launcher
echo ============================================================
echo.

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd"') do set JARVIS_CURRENT_DATE=%%i

echo Current date: %JARVIS_CURRENT_DATE%
echo.
echo Running daily operator...
echo.

python "%~dp0jarvis_operator.py" --daily-operator --current-date %JARVIS_CURRENT_DATE% --max-targets 10

if errorlevel 1 (
    echo.
    echo ============================================================
    echo  J.A.R.V.I.S. needs review. Dashboard was not opened.
    echo ============================================================
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  J.A.R.V.I.S. daily operator completed.
echo  Opening local app dashboard and chat...
echo ============================================================
echo.

echo Starting local app server at http://127.0.0.1:8765 ...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$argsList = @('%~dp0jarvis_operator.py','--local-server','--current-date','%JARVIS_CURRENT_DATE%','--host','127.0.0.1','--port','8765'); Start-Process -WindowStyle Hidden python -ArgumentList $argsList"
timeout /t 2 /nobreak >nul

powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8765/health' -TimeoutSec 5; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"
if errorlevel 1 (
    echo Local app was not ready yet. Opening static dashboard fallback if available...
    if exist "%~dp0outputs\dashboard_latest.html" (
        start "" "%~dp0outputs\dashboard_latest.html"
    ) else (
        echo Dashboard fallback file was not found:
        echo "%~dp0outputs\dashboard_latest.html"
    )
) else (
    start "" "http://127.0.0.1:8765/dashboard"
    start "" "http://127.0.0.1:8765/chat"
)

echo.
echo Safety reminder:
echo - Manual approval required.
echo - Diogo makes any real-world purchase outside J.A.R.V.I.S.
echo - No broker. No credentials. No orders. No trades. No auto-approval.
echo.
pause
endlocal
