@echo off
REM Quick test to see if path with apostrophe is the issue

echo ========================================
echo Testing Path Issue
echo ========================================
echo.
echo Current working directory:
cd
echo.

echo Testing Python from Command Prompt...
python --version
if %errorLevel% equ 0 (
    echo.
    echo SUCCESS: Python works in Command Prompt!
    echo.
    echo The issue is likely Cursor's PowerShell wrapper,
    echo not your Python installation.
    echo.
    echo Next: Try changing Cursor's terminal to Command Prompt,
    echo or create a symbolic link to avoid the apostrophe.
) else (
    echo.
    echo ERROR: Python not found or not working.
    echo Check your Python installation.
)

echo.
pause

