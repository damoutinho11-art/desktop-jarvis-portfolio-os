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
echo  Opening dashboard...
echo ============================================================
echo.

if exist "%~dp0outputs\dashboard_latest.html" (
    start "" "%~dp0outputs\dashboard_latest.html"
) else (
    echo Dashboard file was not found:
    echo "%~dp0outputs\dashboard_latest.html"
)

echo.
if /I "%JARVIS_OPEN_CHAT%"=="1" (
    echo Opening local chat at http://127.0.0.1:8765/chat ...
    start "J.A.R.V.I.S. Chat Server" cmd /k python "%~dp0jarvis_operator.py" --local-server --current-date %JARVIS_CURRENT_DATE% --host 127.0.0.1 --port 8765
    timeout /t 2 /nobreak >nul
    start "" "http://127.0.0.1:8765/chat"
) else (
    echo Optional chat is off. To open it, run:
    echo set JARVIS_OPEN_CHAT=1
    echo Start Jarvis.bat
)

echo.
echo Safety reminder:
echo - Manual approval required.
echo - Diogo makes any real-world purchase outside J.A.R.V.I.S.
echo - No broker. No credentials. No orders. No trades. No auto-approval.
echo.
pause
endlocal
