@echo off
chcp 65001 >nul
setlocal
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
echo.
python "%~dp0converter.py" --check
echo.
echo  Press any key to return...
pause >nul
endlocal
exit /b 0
