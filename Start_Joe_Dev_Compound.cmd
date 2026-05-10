@echo off
setlocal
cd /d "%~dp0"
rem Starts Joe worktree dev HUD on port 8767.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\Start-WorktreeDev.ps1" -ProfileName Joe
