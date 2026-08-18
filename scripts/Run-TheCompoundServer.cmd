@echo off
setlocal
set "ROOT=D:\The_Compound"
set "PYTHON=C:\Python313\python.exe"
set "MUD_HOST=0.0.0.0"
set "MUD_PORT=8765"
rem websockets et al live under treyt's user site-packages; the task may run as SYSTEM,
rem so expose that path explicitly regardless of run-as identity.
set "PYTHONPATH=%PYTHONPATH%;C:\Users\treyt\AppData\Roaming\Python\Python313\site-packages"

if not exist "%ROOT%\data\logs" mkdir "%ROOT%\data\logs"

cd /d "%ROOT%"
"%PYTHON%" -u "%ROOT%\engine\server.py" >> "%ROOT%\data\logs\the-compound-server.out.log" 2>> "%ROOT%\data\logs\the-compound-server.err.log"
