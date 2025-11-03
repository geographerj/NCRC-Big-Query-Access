# PowerShell Issue - Quick Search Guide

## Copy-Paste These Search Queries

### Google/General Web
```
Cursor IDE PowerShell terminal "Missing terminator" Base64 wrapper error
```
```
VS Code PowerShell integrated terminal Base64 decode quote escaping apostrophe path
```
```
Cursor IDE terminal command fails "string missing terminator" PowerShell wrapper
```

### GitHub Issues
```
site:github.com cursor-ai PowerShell terminal Base64 wrapper error
```
```
site:github.com getcursor PowerShell integrated terminal special characters path
```

### Stack Overflow
```
site:stackoverflow.com PowerShell Base64 decode nested quotes FromBase64String error
```
```
site:stackoverflow.com IDE terminal wrapper Base64 encoding special characters apostrophe
```

## The Problem (One Sentence)

**Cursor IDE's PowerShell terminal wrapper fails to execute commands when the project path contains an apostrophe, generating malformed Base64 decoding PowerShell scripts with quote escaping errors.**

## Error Signature

```
Missing ')' in method call.
The string is missing the terminator: '.
At ...\ps-script-*.ps1:34 char:134
... coding]::UTF8.GetString([System.Convert]::FromBase64String(''{1}''))) ...
```

**Location**: `[System.Convert]::FromBase64String(''{1}'')`
**Issue**: Malformed quote escaping in Base64 decode wrapper
**Trigger**: Project path with apostrophe: `...\Nat'l Community...`

## Quick Test

If you have a path with an apostrophe, try moving project to `C:\Test\Project` temporarily - if it works there, confirms the path is the issue.

## Best Search Strategy

1. Start with: **"Cursor IDE PowerShell terminal error"** (broad)
2. Then try: **"Base64 wrapper quote escaping"** (specific)
3. Check: **Cursor GitHub issues** for similar reports
4. Fallback: **VS Code PowerShell terminal** (related platform)

