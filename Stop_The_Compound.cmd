@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\Stop-TheCompound.ps1"
echo.
pause
