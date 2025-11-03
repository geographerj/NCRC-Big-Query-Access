# Fix Cursor Terminal Issue

## Quick Fix: Change Default Terminal

1. Open Cursor Settings (Ctrl+,)
2. Search for "default profile"
3. Find: **Terminal: Integrated › Default Profile (Windows)**
4. Change from "PowerShell" to "**Command Prompt**"
5. Close and reopen the terminal panel
6. Test with: `python --version`

## Or Edit settings.json Directly

1. Ctrl+Shift+P → "Preferences: Open User Settings (JSON)"
2. Add these lines:

```json
{
  "terminal.integrated.profiles.windows": {
    "PowerShell": {
      "source": "PowerShell",
      "args": ["-NoProfile", "-ExecutionPolicy", "Bypass"]
    }
  },
  "terminal.integrated.defaultProfile.windows": "Command Prompt"
}
```

3. Save and restart terminal

## Test

After changing, run:
```
python --version
python find_top_cbsas.py
```

If these work, the terminal issue is fixed!


