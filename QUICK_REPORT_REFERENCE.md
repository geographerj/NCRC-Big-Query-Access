# Quick Report Reference Card

## 🚀 Most Common Reports

### Member Report
**Request:** "Create member report for [location]" or "Member data request"  
**Command:** `python Member Reports/scripts/create_tampa_report.py` (use as template)  
**Location:** `Member Reports/` (root level)

### Merger Report  
**Request:** "Merger report for [Bank A] + [Bank B]" or "Create merger report"  
**Command:** `python scripts/goal_setting_analysis_main.py "ticket.xlsx"`  
**Location:** `reports/Local Markets Analyses/`  
**Features:** Compares two banks, sets mortgage goals, compares small business, analyzes branches

### CBA Banks Analysis
**Request:** "CBA analysis" or "[Bank] CBA report"  
**Command:** `python scripts/cba_banks_analysis_v4_FINAL.py`  
**Location:** `reports/cba_banks/`

### Worst Lenders Analysis
**Request:** "Worst lenders" or "Redlining analysis" (worst context)  
**Command:** `python scripts/ncrc_worst_lenders_analysis_v4.py`  
**Location:** `reports/worst_lenders/`

---

## ⚠️ Common Confusions

| If user says... | They likely mean... | Use this... |
|----------------|---------------------|-------------|
| "Report for member" | Member Report | `Member Reports/` |
| "Merger report" | Always | Merger Report (`reports/Local Markets Analyses/`) |
| "[Bank]+[Bank]" merger | If comparing two banks | Merger Report |
| "Redlining analysis" | Check: worst lenders context? | Worst Lenders OR Member Report |
| "[Location] report" | Most likely | Member Report |

---

## 📁 Folder Structure Quick View

```
Member Reports/              ← Use this (root level)
reports/
  ├── Local Markets Analyses/  ← Goal Setting
  ├── cba_banks/               ← CBA Analysis  
  ├── worst_lenders/           ← Worst Lenders
  └── Member Reports/          ← Don't use (duplicate)
```

---

## ❓ Still Not Sure?

**Ask:**
1. Is this for an NCRC member? → Member Report
2. Is this comparing two banks in a merger? → Merger Report  
3. Is this analyzing worst performers? → Worst Lenders Analysis
4. Is this about CBAs? → CBA Banks Analysis

See `REPORT_TYPE_MAPPING.md` for full details.

