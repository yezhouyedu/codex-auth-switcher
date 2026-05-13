@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  call setup-venv.bat
)
.venv\Scripts\python.exe -m pip show pyinstaller >nul 2>nul
if errorlevel 1 (
  .venv\Scripts\python.exe -m pip install pyinstaller
  if errorlevel 1 pause & exit /b 1
)
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --windowed --onefile --name CodexAuthSwitcher --hidden-import codex_auth_switcher_qt codex_auth_switcher.py
if errorlevel 1 pause & exit /b 1
echo Built dist\CodexAuthSwitcher.exe
pause
