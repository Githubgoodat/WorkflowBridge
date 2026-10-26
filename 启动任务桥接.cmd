@echo off
setlocal
cd /d "%~dp0"
if exist "%~dp0WorkflowBridge.exe" (
  start "" "%~dp0WorkflowBridge.exe"
  exit /b
)
if exist "%~dp0.venv\Scripts\pythonw.exe" (
  start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0main.py"
  exit /b
)
py -3 "%~dp0main.py"
if errorlevel 1 pause
