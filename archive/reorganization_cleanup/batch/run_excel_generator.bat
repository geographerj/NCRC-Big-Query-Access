@echo off
REM Fifth Third Bank Combined Report Generator
REM Moves to project root and runs the Python script

cd /d "%~dp0\.."
echo Changed to project directory: %CD%
echo.

echo Generating Excel report for Fifth Third Bank (Combined: Redlining + Demographics)...
echo.
echo Usage: 
echo   run_excel_generator.bat [first_file.csv] [second_file.csv]
echo   If no files provided, will auto-detect two most recent bquxjob CSV files
echo   Looks for CSV files in current directory and 'data' folder
echo.
echo Example: run_excel_generator.bat "redlining_file.csv" "demographics_file.csv"
echo.

if "%~1"=="" (
    echo No filenames provided. Auto-detecting most recent bquxjob CSV files...
    python fifth_third_cba_report.py
) else (
    if "%~2"=="" (
        echo Using provided file: %~1
        python fifth_third_cba_report.py --input "%~1"
    ) else (
        echo Using first file: %~1
        echo Using second file: %~2
        python fifth_third_cba_report.py --input "%~1" --input2 "%~2"
    )
)

echo.
echo Done! Check the 'reports' folder for the Excel file.
pause

