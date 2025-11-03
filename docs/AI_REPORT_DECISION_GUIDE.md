# AI Assistant Report Decision Guide

This file helps AI assistants correctly identify which report system to use when processing user requests.

## Critical Distinctions

### 1. Member Reports vs Everything Else

**Member Reports are DISTINCT from all other report types.**

**Triggers for Member Report:**
- User mentions "member report", "member data request", "report for member"
- User mentions specific location (city/county) + "report" without merger/bank context
- User asks for "mortgage lending report" without specifying merger/goal setting
- Request includes community profile, demographics, top lenders analysis
- Output location: `Member Reports/outputs/`

**NOT Member Reports when:**
- User mentions "merger report" OR "[Bank]+[Bank] merger" → Merger Report (Goal Setting Analysis)
- User mentions "worst lenders" or "problem lenders" → Worst Lenders Analysis
- User mentions "CBA" or "Community Benefits Agreement" → CBA Analysis
- User mentions specific banks merging without member context → Merger/Goal Setting

### 2. Merger Report vs Other Merger Analyses

**Merger Report (also called Goal Setting Analysis / Local Market Analysis):**
- ✅ Always uses Excel ticket file as input
- ✅ Creates dated folder: `YYMMDD_BankA_BankB_Merger/`
- ✅ Focuses on assessment areas
- ✅ Sets performance goals for post-merger
- ✅ Location: `reports/Local Markets Analyses/`
- ✅ Script: `scripts/goal_setting_analysis_main.py`
- ✅ Key phrase: **"merger report"** OR "goal setting" OR "local market analysis"
- ✅ Compares two banks, sets mortgage goals, compares small business, analyzes branches

**Other Merger Analyses (HHI/Concentration Focus):**
- ✅ May or may not use ticket format
- ✅ Focuses on HHI, market concentration, branch footprint
- ✅ More flexible structure
- ✅ Scripts: `scripts/merger_analysis_framework.py`, `scripts/03_generate_merger_analysis.py`
- ✅ Key phrase: "merger analysis" WITHOUT "goal setting"

### 3. Worst Lenders Analysis

**Triggers:**
- "worst lenders", "problem lenders", "worst performing"
- "redlining analysis" in context of identifying bad actors
- Ranking/rating focus

**NOT when:**
- "redlining analysis" is part of member report (then it's Member Report)
- User asking about redlining metrics in general (might be query, not report)

## Decision Algorithm

```
IF user mentions "member" OR "[location] report" (without merger):
    → Member Report
    → Location: Member Reports/ (root level)
    
ELIF user mentions "merger report" OR "[Bank]+[Bank]" merger OR "goal setting" OR "local market analysis":
    → Merger Report (Goal Setting Analysis)
    → Location: reports/Local Markets Analyses/
    → Requires: Excel ticket file
    → Compares: Two banks, mortgage goals, small business, branch networks
    
ELIF user mentions "worst lenders" OR "problem lenders":
    → Worst Lenders Analysis
    → Location: reports/worst_lenders/
    
ELIF user mentions "CBA" OR "Community Benefits Agreement":
    → CBA Banks Analysis
    → Location: reports/cba_banks/
    
ELIF user mentions "merger" but NOT "merger report" and NOT goal setting:
    → Other Merger Analysis (HHI/Concentration)
    → Check if HHI/concentration mentioned → use merger_analysis_framework
    → If comparing two banks with goals → actually Merger Report
    
ELIF user mentions "branch changes" OR "branch report":
    → Branch Changes Report
    → Location: reports/branch_changes/
    
ELSE:
    → Ask clarifying questions:
        - Is this for an NCRC member?
        - Is this for a bank merger?
        - What is the primary purpose?
```

## Folder Location Priority

1. **Member Reports:** Use `Member Reports/` (root level) - NOT `reports/Member Reports/`
2. **Goal Setting:** `reports/Local Markets Analyses/`
3. **All others:** `reports/[type]/`

## Common Mistakes to Avoid

❌ **Mistake:** User says "report" → Assume Member Report  
✅ **Fix:** Check context - "merger report" ≠ Member Report

❌ **Mistake:** User says "merger analysis" → Assume it's HHI analysis  
✅ **Fix:** "Merger report" = standardized Goal Setting format. "Merger analysis" = may be HHI/concentration.

❌ **Mistake:** User says "redlining" → Always Worst Lenders  
✅ **Fix:** Check context - redlining METRICS in Member Report vs redlining ANALYSIS of worst performers

❌ **Mistake:** User mentions location + bank → Member Report  
✅ **Fix:** If bank merger context, check for goal setting first

## Validation Checklist

Before starting work on a report, verify:

- [ ] Correct report type identified
- [ ] Correct folder location confirmed
- [ ] Correct script identified
- [ ] Input requirements understood (config file, ticket file, etc.)
- [ ] Output location known
- [ ] Not confusing Member Reports (root) with reports/Member Reports (duplicate)

## Reference Files

- `REPORT_TYPE_MAPPING.md` - Complete mapping document
- `QUICK_REPORT_REFERENCE.md` - Quick lookup
- This file - AI decision guide

---

**When in doubt:** Ask the user clarifying questions rather than guessing.

