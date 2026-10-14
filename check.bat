@echo off
REM ============================================================
REM  Markitdown CLI - Prerequisite Checker
REM ============================================================
chcp 65001 >nul
setlocal EnableDelayedExpansion
cd /d "%~dp0"

set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

echo.
echo  ========================================================
echo                Markitdown CLI  -  Prerequisite Check
echo  ========================================================
echo.

echo  Checking Python...
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo    [MISSING] Python is not installed or not in PATH
) else (
    for /f "tokens=*" %%v in ('python --version 2^>^&1') do (
        echo    [OK]      %%v
    )
)

echo  Checking pip...
python -m pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo    [MISSING] pip is not available
) else (
    for /f "tokens=*" %%v in ('python -m pip --version 2^>^&1') do (
        echo    [OK]      %%v
    )
)

echo  Checking markitdown...
python -c "import markitdown" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo    [MISSING] markitdown is not installed
    echo             Install with option [5] or: pip install "markitdown[docx,pptx,xlsx,pdf]"
) else (
    echo    [OK]      markitdown is installed
)

echo  Checking undoc...
python -c "import undoc" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo    [MISSING] undoc is not installed (image extraction will be skipped)
    echo             Install with option [5] or: pip install undoc
) else (
    echo    [OK]      undoc is installed
)

echo  Checking PyMuPDF (better Persian PDF)...
python -c "import fitz" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo    [MISSING] pymupdf is not installed
    echo             Recommended for Persian/Arabic PDFs: pip install pymupdf
) else (
    echo    [OK]      pymupdf is installed
)

echo  Checking python-bidi (RTL text fix)...
python -c "from bidi.algorithm import get_display" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo    [MISSING] python-bidi is not installed
    echo             Recommended for Persian/Arabic: pip install python-bidi
) else (
    echo    [OK]      python-bidi is installed
)

echo.
echo  --------------------------------------------------------
echo  Check complete.
echo.
echo  Press any key to return to the menu...
pause >nul
endlocal
exit /b 0
