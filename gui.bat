@echo off
REM ============================================================
REM  Markitdown CLI - Launch GUI
REM ============================================================
chcp 65001 >nul 2>&1
setlocal
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
cd /d "%~dp0"
python "%~dp0gui.py"
if errorlevel 1 (
    echo.
    echo  [ERROR] GUI failed to start. Is Python installed and in PATH?
    echo  Press any key to close...
    pause >nul
)
endlocal
