@echo off
setlocal
cd /d "%~dp0"
rem Starts Trey worktree dev HUD on port 8766.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\Start-WorktreeDev.ps1" -ProfileName Trey
