# Documentation Organization Guide

## Current MD Files Status

### **KEEP - Essential Reference Guides**

1. **README.md** ✅ KEEP
   - Main project overview
   - Project structure
   - Essential information

2. **GETTING_STARTED.md** ✅ KEEP  
   - Comprehensive getting started guide
   - Setup instructions
   - Workflows

3. **QUICK_REFERENCE.md** ✅ KEEP
   - Quick command reference
   - Common tasks
   - Troubleshooting quick fixes

### **CONSOLIDATE - Can Merge or Archive**

4. **WHAT_THIS_PROJECT_DOES.md** 
   - **ACTION**: Merge into GETTING_STARTED.md or keep as standalone overview
   - Useful for explaining project to new users

5. **APOSTROPHE_FIX_STATUS.md**
   - **ACTION**: ✅ KEEP (but move to docs/archive after verification)
   - Status tracking for the path fix
   - Once verified working, can archive

6. **BRANCH_INTEGRATION_GUIDE.md** ✅ KEEP
   - Comprehensive branch analysis guide
   - Important reference

7. **BRANCH_MATCHING_WORKFLOW.md**
   - **ACTION**: Merge into BRANCH_INTEGRATION_GUIDE.md
   - Overlaps with integration guide

8. **BRANCH_GEOID_GUIDE.md**
   - **ACTION**: Merge into BRANCH_INTEGRATION_GUIDE.md  
   - Part of branch integration

9. **HHI_ANALYSIS_GUIDE.md** ✅ KEEP
   - Important for merger analysis
   - Standalone reference

10. **MERGER_ANALYSIS_GUIDE.md** ✅ KEEP
    - Comprehensive merger analysis guide
    - Important reference

11. **QUICK_START_MERGER_ANALYSIS.md**
    - **ACTION**: Merge into MERGER_ANALYSIS_GUIDE.md as "Quick Start" section
    - Quick start belongs in main guide

12. **SOD_NAME_MATCHES_TO_VERIFY.md**
    - **ACTION**: DELETE after verification
    - Temporary file

### **Archived/Obsolete**

13. **FIX_CURSOR_TERMINAL.md**
    - **ACTION**: Move to docs/archive or delete
    - Fixed issue, no longer needed

## Recommended Organization

### Structure:
```
docs/
├── guides/
│   ├── GETTING_STARTED.md (comprehensive)
│   ├── QUICK_REFERENCE.md
│   ├── BRANCH_ANALYSIS.md (merged from 3 files)
│   ├── HHI_ANALYSIS.md
│   └── MERGER_ANALYSIS.md (merged quick start)
├── technical/
│   └── (keep existing technical docs)
└── archive/
    └── (move obsolete docs here)
```

## Action Items

1. ✅ Keep: README.md, GETTING_STARTED.md, QUICK_REFERENCE.md
2. ✅ Keep: HHI_ANALYSIS_GUIDE.md, MERGER_ANALYSIS_GUIDE.md
3. 🔄 Merge: BRANCH files → single BRANCH_ANALYSIS.md
4. 🔄 Merge: QUICK_START_MERGER → into MERGER_ANALYSIS_GUIDE.md
5. 🗑️ Delete: SOD_NAME_MATCHES_TO_VERIFY.md (after verification)
6. 📦 Archive: APOSTROPHE_FIX_STATUS.md, FIX_CURSOR_TERMINAL.md

