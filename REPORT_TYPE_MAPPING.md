# Report Type Mapping Guide

This document maps the terminology you use when requesting reports to the actual report types and their locations in the codebase. Use this to understand what report system should be used for each request.

## Report Type Categories

### 1. Member Reports 📊
**What it is:** Comprehensive mortgage lending analysis reports for NCRC members  
**Location:** `Member Reports/` (root level) - **USE THIS ONE**
- ⚠️ There is also `reports/Member Reports/` which appears to be a duplicate/archive
- Always use the root-level `Member Reports/` folder for new work  
**Output:** PDF + Excel reports with NCRC branding, community profiles, lender background info

**Common Request Terminology:**
- "Member report"
- "Member data request"
- "Report for [member organization]"
- "Analysis for [location] member"
- "[City/County] member report"
- "Mortgage lending report for member"
- "Community lending analysis"

**Key Scripts:**
- Primary: `Member Reports/scripts/create_tampa_report.py` (use as template)
- General: `Member Reports/scripts/generate_member_report.py`
- Interactive: `Member Reports/scripts/generate_member_report_interactive.py`

**Example Requests:**
- "Create a member report for Tampa, FL"
- "Generate report for Montgomery County member"
- "Member data request for Queens, NY"

**Distinguishing Features:**
- ✅ Includes PDF with NCRC branding
- ✅ Includes community profile data integration
- ✅ Includes lender background research (GLEIF, web search)
- ✅ Top 10 lender analysis
- ✅ Race/ethnicity demographics
- ✅ Outputs to `Member Reports/outputs/[Location]_[Member]/`

---

### 2. Merger Report 🎯
**What it is:** Analysis comparing two banks planning to merge, setting mortgage lending goals, comparing small business lending, and analyzing bank branch networks  
**Location:** `reports/Local Markets Analyses/`  
**Output:** Excel workbook with goal setting metrics for HMDA and Small Business lending, plus branch network analysis

**Common Request Terminology:**
- **"Merger report"** ← PRIMARY TERM
- "Merger analysis" (when comparing two banks)
- "Goal setting analysis" or "goal setting" (alternative name)
- "Local market analysis" (alternative name)
- "[Bank A] + [Bank B] merger" or "[Bank A] and [Bank B] merger"
- "Bank merger report"
- "Assessment area analysis" (for mergers)

**Key Features:**
- ✅ Compares two banks (acquirer + target)
- ✅ Sets mortgage lending goals
- ✅ Compares small business lending
- ✅ Analyzes bank branch networks
- ✅ Focuses on assessment areas

**Key Scripts:**
- Main: `scripts/goal_setting_analysis_main.py`
- Input: Requires Excel ticket file (format: `BankA+BankB merger research ticket.xlsx`)

**Example Requests:**
- "Goal setting analysis for PNC and FirstBank merger"
- "Run local market analysis for Huntington and Cadence"
- "Create goal setting for [bank merger]"

**Distinguishing Features:**
- ✅ Uses Excel ticket file as input
- ✅ Creates dated folder: `YYMMDD_BankA_BankB_Merger/`
- ✅ Focuses on assessment areas
- ✅ Calculates LMICT, MMCT percentages
- ✅ Compares subject bank to ALL other lenders (not just peers)
- ✅ Outputs Excel workbook with multiple sheets
- ✅ Uses `reports/Local Markets Analyses/_shared/` for shared utilities

---

### 3. CBA Banks Analysis 💼
**What it is:** Analysis of banks with Community Benefits Agreements  
**Location:** `reports/cba_banks/`  
**Output:** Excel analysis of CBA banks

**Common Request Terminology:**
- "CBA banks analysis"
- "CBA report"
- "Community Benefits Agreement analysis"
- "Banks with CBA analysis"
- "[Bank name] CBA report" (e.g., "Fifth Third CBA report", "Comerica CBA report")

**Key Scripts:**
- General: `scripts/cba_banks_analysis_v4_FINAL.py`
- Fifth Third: `scripts/02_fifth_third_cba_report.py`
- Comerica: `scripts/comerica_cba_report.py`

**Example Requests:**
- "Generate CBA banks analysis"
- "Create Fifth Third CBA report"
- "CBA analysis for Comerica"

**Distinguishing Features:**
- ✅ Focuses on banks with CBAs
- ✅ Outputs to `reports/cba_banks/`
- ✅ Excel format only
- ✅ Usually includes Small Business data

---

### 4. Worst Lenders Analysis ⚠️
**What it is:** Analysis identifying worst-performing lenders based on various metrics  
**Location:** `reports/worst_lenders/`  
**Output:** Excel analysis with worst lender rankings

**Common Request Terminology:**
- "Worst lenders analysis"
- "Worst lenders report"
- "Redlining analysis" (when asking about worst lenders)
- "Problem lenders analysis"
- "Lender performance analysis" (when negative focus)

**Key Scripts:**
- Main: `scripts/ncrc_worst_lenders_analysis_v4.py`
- Alternative: `scripts/01_worst_lenders_analysis_v2.py`
- Simple: `scripts/worst_lenders_analysis.py`

**Example Requests:**
- "Create worst lenders analysis"
- "Generate worst lenders report"
- "Redlining analysis of worst lenders"

**Distinguishing Features:**
- ✅ Rankings/ratings of lenders
- ✅ Focus on negative performance metrics
- ✅ Redlining-related metrics
- ✅ Outputs to `reports/worst_lenders/`

---

### 5. Merger Analysis (General) 🔀
**What it is:** General merger analysis (may overlap with Goal Setting, but more flexible)  
**Location:** `reports/fifth_third_merger/` or `reports/Local Markets Analyses/`  
**Output:** Excel analysis of merger impacts

**Common Request Terminology:**
- "Merger analysis" (when goal setting NOT mentioned)
- "[Bank A] merger with [Bank B]"
- "Branch analysis for merger"
- "HHI analysis" (Herfindahl-Hirschman Index)
- "Market concentration analysis"

**Key Scripts:**
- Framework: `scripts/merger_analysis_framework.py`
- Main: `scripts/03_generate_merger_analysis.py`
- Branch HHI: `scripts/merger_branch_hhi_analysis.py`
- Fifth Third: `scripts/generate_fifth_third_report.py`

**Example Requests:**
- "Create merger analysis for Fifth Third and Comerica"
- "HHI analysis for bank merger"
- "Branch concentration analysis"

**Distinguishing Features:**
- ⚠️ Can overlap with Goal Setting Analysis
- ✅ May focus on market concentration (HHI)
- ✅ Branch footprint analysis
- ✅ May not use ticket Excel format
- ✅ More flexible structure than Goal Setting

**When to use Goal Setting vs Merger Analysis:**
- **Use Goal Setting** if: Assessment areas, performance goals, state-level goals, standard format
- **Use Merger Analysis** if: HHI, market concentration, custom analysis, branch footprint focus

---

### 6. Branch Changes Reports 📍
**What it is:** Weekly/monthly reports of bank branch openings and closures  
**Location:** `reports/branch_changes/weekly/`  
**Output:** Excel reports of branch changes

**Common Request Terminology:**
- "Branch changes report"
- "Weekly branch report"
- "Branch openings and closures"
- "FDIC branch changes"

**Key Scripts:**
- Weekly: `scripts/04_generate_weekly_branch_report.py`
- Auto: `scripts/auto_generate_weekly_report.py`
- FDIC: `scripts/fdic_branch_changes_report.py`

**Example Requests:**
- "Generate weekly branch changes report"
- "Create branch changes analysis"

**Distinguishing Features:**
- ✅ Weekly/monthly snapshots
- ✅ FDIC BankFind data
- ✅ Focus on branch locations
- ✅ Time-series analysis

---

## Decision Tree: Which Report Type?

**Ask yourself:**
1. **Is it for an NCRC member?** → **Member Report**
2. **Is it for a bank merger with goal setting?** → **Goal Setting Analysis**
3. **Is it for banks with CBAs?** → **CBA Banks Analysis**
4. **Is it ranking worst performers?** → **Worst Lenders Analysis**
5. **Is it a general merger analysis?** → **Merger Analysis**
6. **Is it about branch openings/closures?** → **Branch Changes Report**

---

## Confusion Points & Clarifications

### "Member Report" vs Generic "Report"
- ✅ **"Member report"** → Always refers to `Member Reports/` system
- ❌ Generic **"report"** → Ask clarifying questions or check context

### "Merger Report" vs Other Merger Analyses
- ✅ **"Merger report"** → Standardized report comparing two banks, setting goals → `reports/Local Markets Analyses/`
- ✅ **"Merger analysis"** (generic, no goals/mortgage focus) → May be HHI/concentration focus → `scripts/merger_analysis_framework.py`
- **When unclear:** 
  - Comparing two banks + mortgage goals + small business + branches → **Merger Report**
  - HHI, market concentration, branch footprint only → Other Merger Analysis

### Location-Specific Reports (Tampa, Montgomery, etc.)
- These are **Member Reports** with specific location configurations
- Use `create_tampa_report.py` as template for new locations
- All follow same structure, just different geographic scope

### "Redlining Analysis"
- **Worst Lenders context** → `Worst Lenders Analysis`
- **Member Report context** → Part of `Member Reports` (redlining metrics included)
- **General redlining query** → Check if it's a query request vs full report

---

## File Organization Summary

```
DREAM/
├── Member Reports/              # Member Reports (root level - PRIMARY - USE THIS)
│   ├── scripts/
│   │   ├── create_tampa_report.py          # Main generator (use as template)
│   │   ├── generate_member_report.py       # General generator
│   │   └── generate_member_report_interactive.py
│   ├── outputs/                            # PDF + Excel outputs
│   └── configs/                             # JSON configs
│
├── reports/
│   ├── Member Reports/          # ⚠️ DUPLICATE - Do not use (archive/old copy)
│   ├── Local Markets Analyses/  # Goal Setting Analysis
│   │   ├── _shared/            # Shared utilities
│   │   └── YYMMDD_BankA_BankB_Merger/  # Individual analyses
│   ├── cba_banks/               # CBA Banks Analysis
│   ├── worst_lenders/           # Worst Lenders Analysis
│   ├── fifth_third_merger/      # Specific merger analysis
│   └── branch_changes/          # Branch Changes Reports
│
└── scripts/                     # Root-level scripts
    ├── goal_setting_analysis_main.py     # Goal Setting Analysis main script
    ├── cba_banks_analysis_v4_FINAL.py   # CBA Analysis
    ├── ncrc_worst_lenders_analysis_v4.py # Worst Lenders
    └── merger_analysis_framework.py      # Merger Analysis
```

---

## Quick Reference: Request → Report Type

| Your Request Contains... | Use This Report Type | Location |
|-------------------------|---------------------|----------|
| "member report", "[location] member", "member data request" | Member Report | `Member Reports/` |
| "merger report", "[Bank]+[Bank] merger", "goal setting", "local market analysis" | Merger Report | `reports/Local Markets Analyses/` |
| "CBA", "Community Benefits Agreement", "[Bank] CBA" | CBA Banks Analysis | `reports/cba_banks/` |
| "worst lenders", "problem lenders", "redlining" (worst context) | Worst Lenders Analysis | `reports/worst_lenders/` |
| "merger analysis" (no goal setting), "HHI", "market concentration" | Merger Analysis | `scripts/merger_analysis_framework.py` |
| "branch changes", "branch report", "FDIC branches" | Branch Changes Report | `reports/branch_changes/` |

---

## For AI Assistants

When user requests a report:
1. **Check this mapping document first**
2. **Look for key terminology** in the request
3. **If ambiguous, ask clarifying questions:**
   - "Is this for an NCRC member?" → Member Report
   - "Is this for goal setting in a merger?" → Goal Setting Analysis
   - "What is the primary purpose?" → Match to table above
4. **Confirm location** before starting work
5. **Verify you're using the correct folder** (Member Reports root vs reports/Member Reports)

---

**Last Updated:** 2025-01-XX  
**Maintained By:** NCRC Research Department

