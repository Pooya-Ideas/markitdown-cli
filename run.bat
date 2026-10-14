@echo off
REM ============================================================
REM  Markitdown CLI - Interactive Menu
REM ============================================================
chcp 65001 >nul 2>&1
setlocal EnableExtensions EnableDelayedExpansion
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
cd /d "%~dp0"

:MENU
cls
echo.
echo  ========================================================
echo                   Markitdown CLI
echo  ========================================================
echo.
echo     [1] Convert a single file
echo     [2] Convert a whole folder
echo     [3] Open GUI (graphical interface)
echo     [4] Check prerequisites
echo     [5] Install / Update prerequisites
echo     [6] Exit
echo.
echo  --------------------------------------------------------
set "CHOICE="
set /p "CHOICE=  Enter your choice (1-6): "

if "!CHOICE!"=="1" goto CONVERT_FILE
if "!CHOICE!"=="2" goto CONVERT_FOLDER
if "!CHOICE!"=="3" goto GUI
if "!CHOICE!"=="4" goto CHECK
if "!CHOICE!"=="5" goto INSTALL
if "!CHOICE!"=="6" goto EXIT

echo.
echo  [ERROR] Invalid choice.
timeout /t 2 >nul
goto MENU

:CONVERT_FILE
echo.
echo  --------------------------------------------------------
echo   Convert a single file
echo  --------------------------------------------------------
echo.
set "FILEPATH="
set /p "FILEPATH=  Full path to file: "
set "FILEPATH=!FILEPATH:"=!"
set "FILEPATH=!FILEPATH:'=!"
if "!FILEPATH!"=="" (
    echo  [ERROR] No path entered.
    goto WAIT_AND_MENU
)
echo.
python "%~dp0converter.py" "!FILEPATH!"
echo.
if errorlevel 1 (echo  [ERROR] Conversion failed.) else (echo  [SUCCESS] Done.)
goto WAIT_AND_MENU

:CONVERT_FOLDER
echo.
echo  --------------------------------------------------------
echo   Convert a whole folder
echo  --------------------------------------------------------
echo.
set "FOLDERPATH="
set /p "FOLDERPATH=  Full path to folder: "
set "FOLDERPATH=!FOLDERPATH:"=!"
set "FOLDERPATH=!FOLDERPATH:'=!"
if "!FOLDERPATH!"=="" (
    echo  [ERROR] No path entered.
    goto WAIT_AND_MENU
)
echo.
echo  Which files should be converted?
echo     [A] All supported formats
echo     [D] Only Word (.docx)
echo     [P] Only PowerPoint (.pptx)
echo     [E] Only Excel (.xlsx / .xls)
echo     [F] Only PDF (.pdf)
echo     [M] Mix - type extensions (e.g. docx,pdf)
echo.
set "FMTCHOICE="
set /p "FMTCHOICE=  Choice (A/D/P/E/F/M): "
set "EXTLIST="
if /i "!FMTCHOICE!"=="A" set "EXTLIST=all"
if /i "!FMTCHOICE!"=="D" set "EXTLIST=docx"
if /i "!FMTCHOICE!"=="P" set "EXTLIST=pptx"
if /i "!FMTCHOICE!"=="E" set "EXTLIST=xlsx,xls"
if /i "!FMTCHOICE!"=="F" set "EXTLIST=pdf"
if /i "!FMTCHOICE!"=="M" (
    set /p "EXTLIST=  Extensions: "
)
if "!EXTLIST!"=="" set "EXTLIST=all"
echo.
if /i "!EXTLIST!"=="all" (
    python "%~dp0converter.py" --folder "!FOLDERPATH!"
) else (
    python "%~dp0converter.py" --folder "!FOLDERPATH!" --ext "!EXTLIST!"
)
echo.
if errorlevel 1 (echo  [ERROR] Some files may have failed.) else (echo  [SUCCESS] Done.)
goto WAIT_AND_MENU

:GUI
echo.
echo  Opening GUI...
start "" pythonw "%~dp0gui.py" 2>nul
if errorlevel 1 (
    python "%~dp0gui.py"
)
goto MENU

:CHECK
call "%~dp0check.bat"
goto MENU

:INSTALL
call "%~dp0install.bat"
goto MENU

:WAIT_AND_MENU
echo.
echo  --------------------------------------------------------
echo  Press any key to return to the menu...
pause >nul
goto MENU

:EXIT
echo.
echo  Goodbye!
timeout /t 1 >nul
endlocal
exit /b 0
