@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

echo.
echo  ========================================================
echo           Markitdown-CLI  -  Install Prerequisites
echo  ========================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python 3.10+ required and must be on PATH.
    echo          https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo  [INFO] Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo  [ERROR] pip upgrade failed.
    pause
    exit /b 1
)

echo  [INFO] Installing markitdown...
python -m pip install --upgrade "markitdown[docx,pptx,xlsx,pdf]>=0.0.1a3,<1.0"
if errorlevel 1 (
    echo  [ERROR] markitdown install failed. Try: python -m pip install --user "markitdown[docx,pptx,xlsx,pdf]"
    pause
    exit /b 1
)

echo  [INFO] Installing undoc...
python -m pip install --upgrade "undoc>=0.1.0,<1.0"
if errorlevel 1 echo  [WARNING] undoc install failed - images may be skipped.

echo  [INFO] Installing pymupdf...
python -m pip install --upgrade "pymupdf>=1.24.0,<2.0"
if errorlevel 1 echo  [WARNING] pymupdf install failed - PDF quality may be lower.

echo  [INFO] Installing python-bidi...
python -m pip install --upgrade "python-bidi>=0.4.0,<1.0"
if errorlevel 1 echo  [WARNING] python-bidi install failed.

echo  [INFO] Installing tqdm...
python -m pip install --upgrade "tqdm>=4.66.0,<5.0"

echo  [INFO] Installing package editable...
python -m pip install -e .
if errorlevel 1 echo  [WARNING] editable install skipped - converter.py still works.

echo.
echo  ========================================================
echo  [SUCCESS] Installation finished.
echo  Use run.bat or gui.bat to convert files.
echo  ========================================================
echo.
pause
endlocal
exit /b 0
