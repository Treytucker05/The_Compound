@echo off
REM COMPOUND_APPROACH Portal Launcher
REM Portable entry point — resolves its own directory.

REM Switch to the folder containing this batch file
pushd "%~dp0"

set PYTHONNOUSERSITE=1

set "PYTHON="

REM The portal launcher is a Tk GUI, so the chosen Python must include tkinter.
REM The engine also needs websockets because it runs under the launcher Python.
if exist "C:\Python313\python.exe" (
    "C:\Python313\python.exe" -c "import tkinter, websockets" >nul 2>&1
    if not errorlevel 1 set "PYTHON=C:\Python313\python.exe"
)

if not defined PYTHON if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import tkinter, websockets" >nul 2>&1
    if not errorlevel 1 set "PYTHON=.venv\Scripts\python.exe"
)

if not defined PYTHON if exist ".python\python.exe" (
    ".python\python.exe" -c "import tkinter, websockets" >nul 2>&1
    if not errorlevel 1 set "PYTHON=.python\python.exe"
)

if not defined PYTHON (
    python -c "import tkinter, websockets" >nul 2>&1
    if not errorlevel 1 set "PYTHON=python"
)

if not defined PYTHON (
    echo [ERROR] No usable Python found.
    echo The launcher needs tkinter and websockets.
    echo Try: C:\Python313\python.exe -m pip install websockets
    pause
    popd
    exit /b 1
)

"%PYTHON%" launcher\main.py

popd
