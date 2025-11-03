@echo off
REM Create Symbolic Link to Fix Apostrophe Path Issue
REM Run this as Administrator

echo ========================================
echo Create Symbolic Link for DREAM Analysis
echo ========================================
echo.
echo This will create a junction point:
echo   C:\DREAM -> [Your OneDrive path]
echo.
echo Cursor will use C:\DREAM (no apostrophe!)
echo Files still sync to OneDrive automatically.
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

set "TARGET=C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis"
set "LINK=C:\DREAM"

echo Target path:
echo %TARGET%
echo.
echo Link path:
echo %LINK%
echo.

REM Check if target exists
if not exist "%TARGET%" (
    echo ERROR: Target folder does not exist!
    echo %TARGET%
    pause
    exit /b 1
)

REM Check if link already exists
if exist "%LINK%" (
    echo WARNING: %LINK% already exists!
    echo.
    choice /C YN /M "Delete and recreate"
    if errorlevel 2 exit /b 0
    rmdir "%LINK%"
)

echo Creating junction point...
mklink /J "%LINK%" "%TARGET%"

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS!
    echo ========================================
    echo.
    echo Junction created: %LINK%
    echo.
    echo NEXT STEPS:
    echo 1. Close Cursor if it's open
    echo 2. Open Cursor
    echo 3. File -> Open Folder -> Select: C:\DREAM
    echo 4. Test terminal: python --version
    echo.
) else (
    echo.
    echo ========================================
    echo ERROR!
    echo ========================================
    echo Failed to create junction.
    echo Make sure you ran as Administrator.
    echo.
)

pause

