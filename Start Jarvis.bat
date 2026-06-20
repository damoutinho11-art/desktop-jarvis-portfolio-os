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
echo Safety reminder:
echo - Manual approval required.
echo - Buy outside J.A.R.V.I.S.
echo - No broker, credential, order, trade, or auto-approval path is enabled.
echo.
pause
endlocal
