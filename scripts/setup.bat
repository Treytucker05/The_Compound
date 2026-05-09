@echo off
REM One-time setup for COMPOUND_APPROACH.

pushd "%~dp0\.."
set PYTHONNOUSERSITE=1

echo ============================================
echo   COMPOUND_APPROACH Setup
echo ============================================
echo.

REM Prefer bundled Python
if exist ".python\python.exe" (
    set PYTHON=.python\python.exe
) else (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python is not installed or not in PATH.
        echo Please install Python 3.11+ from https://python.org
        pause
        popd
        exit /b 1
    )
    set PYTHON=python
)

echo [OK] Python: %PYTHON%

REM Ensure websockets is installed in bundled Python
%PYTHON% -c "import websockets" >nul 2>&1
if errorlevel 1 (
    echo [SETUP] Installing websockets...
    %PYTHON% -m pip install websockets --no-warn-script-location
) else (
    echo [OK] websockets already installed.
)

echo.
echo ============================================
echo   Setup complete.
echo   Run start_portal.bat to launch.
echo ============================================
pause
popd
