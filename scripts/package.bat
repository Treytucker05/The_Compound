@echo off
REM Build script: packages COMPOUND_APPROACH into a portable ZIP.
REM Run this after any code changes to create a redistributable archive.

pushd "%~dp0\.."

echo ============================================
echo   COMPOUND_APPROACH Portable Build
echo ============================================
echo.

REM Verify bundled Python exists
if not exist ".python\python.exe" (
    echo [ERROR] Bundled Python not found at .python\python.exe
    echo Run this script after downloading the embeddable Python distribution.
    pause
    popd
    exit /b 1
)

REM Verify websockets is installed locally
set PYTHONNOUSERSITE=1
.python\python.exe -c "import websockets" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] websockets not installed in bundled Python.
    echo Run scripts\setup.bat first.
    pause
    popd
    exit /b 1
)

echo [OK] Bundled Python + websockets verified.

REM Clean build artifacts
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Clean pycache
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"

REM Create dist folder
mkdir dist

REM Build ZIP (exclude .git, .kimi plans, and build dirs)
echo [BUILD] Creating dist\COMPOUND_APPROACH.zip ...
powershell -Command "Compress-Archive -Path '*' -DestinationPath 'dist\COMPOUND_APPROACH.zip' -Force"

echo.
echo ============================================
echo   Build complete.
echo   Output: dist\COMPOUND_APPROACH.zip
echo   Size:
dir "dist\COMPOUND_APPROACH.zip" | findstr "COMPOUND_APPROACH.zip"
echo ============================================
pause
popd
