# File Reorganization Instructions

## Status

The folder structure has been created. **You need to run the reorganization script to move files.**

## Quick Start

**Option 1: Double-click the batch file**
```
RUN_REORGANIZATION.bat
```

**Option 2: Run Python script directly**
```cmd
python MOVE_FILES_NOW.py
```

## What Will Happen

The script will:
1. ✅ Move Python scripts → `scripts/`
2. ✅ Move SQL queries → `queries/fifth_third/`
3. ✅ Move Excel reports → `reports/{project_type}/`
4. ✅ Move CSV data → `data/raw/` and `data/reference/`
5. ✅ Move batch files → `batch/`
6. ✅ Move test files → `tests/`
7. ✅ Move documentation → `docs/{guides|technical|archive}/`
8. ✅ Move credentials → `config/credentials/`
9. ✅ Archive duplicate folder → `archive/NCRC-Big-Query-Access/`

## After Running

1. **Review moved files** - Check that everything is in the right place
2. **Update scripts if needed** - Some scripts may have hardcoded paths
3. **Test scripts** - Make sure reports still generate correctly
4. **Update git** - Commit the reorganization

## Files That Need Manual Review

After running, check these scripts for hardcoded paths:
- `scripts/fifth_third_cba_report.py` - May reference `data/` folder
- `scripts/generate_fifth_third_report.py` - May reference credentials path
- `scripts/find_top_cbsas.py` - May reference credentials path

Most scripts already look in `data/` and current directory, so they should work.

## Troubleshooting

If the script fails:
1. Check for file locks (close Excel/CSV files if open)
2. Check permissions (you need write access)
3. Review error messages in the output
4. Some files may already be moved - that's OK, the script skips missing files

