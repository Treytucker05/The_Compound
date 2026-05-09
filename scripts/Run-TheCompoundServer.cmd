@echo off
setlocal
set "ROOT=D:\The_Compound"
set "PYTHON=C:\Python313\python.exe"
set "MUD_HOST=0.0.0.0"
set "MUD_PORT=8765"

if not exist "%ROOT%\data\logs" mkdir "%ROOT%\data\logs"

cd /d "%ROOT%"
"%PYTHON%" -u "%ROOT%\engine\server.py" >> "%ROOT%\data\logs\the-compound-server.out.log" 2>> "%ROOT%\data\logs\the-compound-server.err.log"
