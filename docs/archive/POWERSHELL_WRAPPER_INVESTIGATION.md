# PowerShell Wrapper Issue Investigation

## Problem Summary
Cursor IDE's integrated terminal (PowerShell on Windows) is failing to execute Python commands, even simple ones like `python --version` or `print("test")`. The errors suggest Cursor is wrapping commands in a base64-encoded PowerShell command that fails to parse properly.

## Error Pattern
- **Error**: `The string is missing the terminator: '`
- **Error**: `Missing ')' in method call`
- **Occurs**: Even for simple commands like `python --version`
- **Root Cause**: Appears to be Cursor's internal PowerShell wrapper attempting to base64-decode commands before execution

## Online Search Results
**Status**: No specific examples found of identical issues with Cursor IDE's PowerShell wrapper

**Searches Performed**:
- Cursor IDE GitHub issues
- VS Code PowerShell wrapper errors
- Cursor terminal execution problems
- PowerShell base64 decode command wrapper errors

**Conclusion**: This appears to be either:
1. A relatively new or uncommon issue with Cursor
2. An environment-specific problem
3. Not widely reported yet in public forums

## Working Solutions (Tested)

### Solution 1: Change Default Terminal Profile (Recommended)
1. Cursor Settings → Search "Default Profile"
2. Set **Terminal: Integrated › Default Profile (Windows)** to **Command Prompt**
3. Close and reopen terminal
4. Test with: `python --version`

### Solution 2: Use External Terminal
- Open Windows Terminal or Command Prompt outside Cursor
- Navigate to project directory
- Run Python scripts directly: `python script.py`

### Solution 3: Use Batch Files
- Create `.bat` files to run Python scripts
- Example: `run_excel_generator.bat`
- Execute batch files from external terminal

## Workaround for This Project
1. **BigQuery**: Run SQL queries directly in BigQuery Console
2. **Python**: Execute `fifth_third_cba_report.py` from external Command Prompt
3. **Batch File**: Use `run_excel_generator.bat` for convenience

## Technical Details
The wrapper likely executes something like:
```powershell
powershell -Command [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('<payload>'))
```

If this base64 payload contains quotes or special characters, PowerShell's parser fails before the actual command runs.

## Next Steps if Issue Persists
1. **Report to Cursor**: Submit a bug report to Cursor's support/issue tracker
2. **Check for Updates**: Ensure Cursor IDE is up to date
3. **Try Git Bash**: Set default terminal to Git Bash as an alternative
4. **PowerShell Profile Check**: Temporarily disable all PowerShell profiles to rule out profile interference

## Files Created to Work Around Issue
- `run_excel_generator.bat` - Batch file to run Excel generator
- `run_cmd.bat` - Generic batch file wrapper
- `README_FOR_CURSOR_TERMINAL_ISSUE.md` - User instructions
- `CURSOR_SETTINGS_FIX.md` - Settings change instructions

