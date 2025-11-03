"""Inspect Tampa PDF to see table structure"""

import pdfplumber

pdf_path = r"C:\DREAM\Member Reports\supporting_files\Community Profile of Tampa, FL (City, 2020).pdf"

with pdfplumber.open(pdf_path) as pdf:
    # Check page 4 which had a 28-row table
    page = pdf.pages[3]  # Page 4 (0-indexed)
    tables = page.extract_tables()
    
    if tables:
        print(f"Page 4, Table 1 ({len(tables[0])} rows):")
        for i, row in enumerate(tables[0][:10]):  # First 10 rows
            print(f"  Row {i}: {row}")
        
        print(f"\nLast few rows:")
        for i, row in enumerate(tables[0][-5:], len(tables[0])-5):
            print(f"  Row {i}: {row}")

