@echo off
REM Test script to verify the apostrophe path issue is resolved
REM Run this from C:\DREAM to test if the fix works

echo ========================================
echo Testing Apostrophe Path Fix
echo ========================================
echo.

REM Check current directory
echo Current working directory:
cd
echo.

REM Test 1: Check if we're in C:\DREAM
if /I "%CD%"=="C:\DREAM" (
    echo [PASS] Working from C:\DREAM (symbolic link)
    echo        No apostrophe in path!
    echo.
) else (
    echo [FAIL] Not in C:\DREAM
    echo        Current: %CD%
    echo        Expected: C:\DREAM
    echo.
    echo NOTE: If you see the OneDrive path with "Nat'l", the symbolic link
    echo       might not be set up. Run CREATE_SYMBOLIC_LINK.bat as Administrator.
    echo.
)

REM Test 2: Check if symbolic link exists
if exist "C:\DREAM" (
    echo [PASS] C:\DREAM directory exists
    echo.
) else (
    echo [FAIL] C:\DREAM does not exist
    echo        Run CREATE_SYMBOLIC_LINK.bat as Administrator to create it.
    echo.
)

REM Test 3: Test Python command
echo Testing Python command...
python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [PASS] Python command works!
    echo.
    python --version
    echo.
) else (
    echo [FAIL] Python command failed
    echo        Error code: %errorLevel%
    echo.
)

REM Test 4: Test running a Python script
echo Testing Python script execution...
if exist "scripts\fifth_third_cba_report.py" (
    python scripts\fifth_third_cba_report.py --help >nul 2>&1
    if %errorLevel% equ 0 (
        echo [PASS] Python script can be executed
        echo.
    ) else (
        echo [WARN] Python script execution returned non-zero (might be expected)
        echo        Error code: %errorLevel%
        echo.
    )
) else (
    echo [SKIP] Test script not found (not a problem)
    echo.
)

REM Test 5: Check path for apostrophe
echo | findstr /C:"'" "%CD%" >nul 2>&1
if %errorLevel% equ 0 (
    echo [FAIL] Current path contains an apostrophe!
    echo        Path: %CD%
    echo        This will likely cause Cursor terminal issues.
    echo        Solution: Open C:\DREAM in Cursor instead.
    echo.
) else (
    echo [PASS] Current path does NOT contain an apostrophe
    echo.
)

echo ========================================
echo Test Summary
echo ========================================
echo.
echo If all tests PASS, the fix is working correctly!
echo.
echo IMPORTANT: In Cursor, make sure you:
echo   1. File -> Open Folder
echo   2. Select: C:\DREAM
echo   3. NOT the OneDrive path with apostrophe
echo.
pause

