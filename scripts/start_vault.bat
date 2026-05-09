@echo off
REM Open the COMPOUND_APPROACH vault in Obsidian (or Explorer as fallback).

pushd "%~dp0\.."
set VAULTDIR=%CD%\vault

REM Try Obsidian
if exist "%LOCALAPPDATA%\Obsidian\Obsidian.exe" (
    start "" "%LOCALAPPDATA%\Obsidian\Obsidian.exe" --vault "%VAULTDIR%"
    popd
    exit /b 0
)

if exist "C:\Program Files\Obsidian\Obsidian.exe" (
    start "" "C:\Program Files\Obsidian\Obsidian.exe" --vault "%VAULTDIR%"
    popd
    exit /b 0
)

if exist "C:\Program Files (x86)\Obsidian\Obsidian.exe" (
    start "" "C:\Program Files (x86)\Obsidian\Obsidian.exe" --vault "%VAULTDIR%"
    popd
    exit /b 0
)

REM Fallback to Explorer
start "" explorer "%VAULTDIR%"
popd
