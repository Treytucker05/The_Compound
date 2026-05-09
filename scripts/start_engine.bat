@echo off
REM Start the COMPOUND_APPROACH MUD engine directly.

pushd "%~dp0\.."
set PYTHONNOUSERSITE=1

if exist ".python\python.exe" (
    set PYTHON=.python\python.exe
) else (
    set PYTHON=python
)

set PYTHONPATH=%CD%
%PYTHON% engine\server.py
pause
popd
