@echo off
setlocal
cd /d "%~dp0"
set "PYTHON_EXE=python"
if exist ".venv\Scripts\python.exe" set "PYTHON_EXE=.venv\Scripts\python.exe"
%PYTHON_EXE% -c "import PySide6" >nul 2>nul
if errorlevel 1 (
  echo PySide6 is not installed. Run:
  echo py -3.12 -m venv .venv
  echo .venv\Scripts\python.exe -m pip install -r requirements.txt
  pause
  exit /b 1
)
%PYTHON_EXE% codex_auth_switcher.py gui
if errorlevel 1 pause
