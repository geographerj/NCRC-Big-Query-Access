"""Understand Mortgage Goals sheet structure - what goes in columns A and B"""

import openpyxl
from pathlib import Path

template_file = r"C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis\data\raw\PNC+FirstBank merger research ticket.xlsx"

print("="*80)
print("UNDERSTANDING MORTGAGE GOALS STRUCTURE")
print("="*80)
print("\nBased on earlier inspection:")
print("  - Column A: State names (and possibly county/CBSA)")
print("  - Column B: Metric names (and possibly CBSA/county info)")
print("\nPlease confirm the exact structure:")
print("\n1. Is the structure:")
print("   a) State-level only (each state has 11 metric rows)?")
print("   b) State -> CBSA -> Metrics?")
print("   c) State -> County -> Metrics?")
print("   d) State -> CBSA -> County -> Metrics?")
print("\n2. For columns A & B:")
print("   - What goes in Column A for each row?")
print("   - What goes in Column B for each row?")
print("\n3. Should data be:")
print("   a) Aggregated to state level only (combining all counties/CBSAs)?")
print("   b) Kept at CBSA level within each state?")
print("   c) Kept at county level within each state?")

print("\n" + "="*80)
print("CURRENT UNDERSTANDING FROM TEMPLATE INSPECTION:")
print("="*80)
print("Row 2: Grand Total row")
print("Row 3-12: Metrics for Grand Total (no state in A)")
print("Row 13: Alabama | Loans | [data]")
print("Row 14: [empty A] | ~LMICT | [data]")
print("...")
print("\nThis suggests:")
print("  - Column A: State name on first row of state group")
print("  - Column B: Metric name for all rows")
print("  - But you mentioned county/CBSA info...")

print("\nPlease provide clarification on the structure needed!")

