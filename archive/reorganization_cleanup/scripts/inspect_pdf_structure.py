"""
Inspect PDF structure to understand how assessment area data is organized.
This helps create a more targeted parser.
"""

import pdfplumber
from pathlib import Path
import sys
import json

def inspect_pdf_structure(pdf_path, output_limit=5):
    """
    Inspect the first few pages of a PDF to understand its structure.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    print(f"\n{'='*80}")
    print(f"INSPECTING PDF STRUCTURE: {pdf_path.name}")
    print(f"{'='*80}\n")
    
    results = {
        'total_pages': 0,
        'pages_summary': [],
        'sample_text': [],
        'sample_tables': []
    }
    
    with pdfplumber.open(pdf_path) as pdf:
        results['total_pages'] = len(pdf.pages)
        print(f"Total pages: {len(pdf.pages)}")
        
        # Inspect first few pages in detail
        inspect_pages = min(output_limit, len(pdf.pages))
        
        for page_num in range(1, inspect_pages + 1):
            page = pdf.pages[page_num - 1]
            
            print(f"\n--- Page {page_num} ---")
            
            # Get text
            text = page.extract_text()
            if text:
                # Show first 500 chars
                preview = text[:500].replace('\n', ' ')
                print(f"Text preview: {preview}...")
                results['sample_text'].append({
                    'page': page_num,
                    'preview': preview,
                    'full_length': len(text)
                })
            
            # Get tables
            tables = page.extract_tables()
            if tables:
                print(f"Tables found: {len(tables)}")
                for table_idx, table in enumerate(tables):
                    if table and len(table) > 0:
                        print(f"  Table {table_idx + 1}: {len(table)} rows, {len(table[0])} columns")
                        # Show first few rows
                        print(f"    Header: {table[0][:5]}")
                        if len(table) > 1:
                            print(f"    Row 2: {table[1][:5]}")
                        results['sample_tables'].append({
                            'page': page_num,
                            'table': table_idx,
                            'rows': len(table),
                            'cols': len(table[0]) if table else 0,
                            'header': table[0] if table else None
                        })
            else:
                print("No tables found")
            
            results['pages_summary'].append({
                'page': page_num,
                'has_text': bool(text),
                'text_length': len(text) if text else 0,
                'table_count': len(tables) if tables else 0
            })
        
        # Also sample some middle and end pages
        if len(pdf.pages) > output_limit * 2:
            sample_pages = [
                len(pdf.pages) // 3,
                len(pdf.pages) // 2,
                len(pdf.pages) - 1
            ]
            
            print(f"\n--- Sampling middle/end pages ---")
            for page_num in sample_pages:
                if page_num >= inspect_pages:
                    page = pdf.pages[page_num]
                    text = page.extract_text()
                    tables = page.extract_tables()
                    print(f"Page {page_num + 1}: {len(text) if text else 0} chars, {len(tables) if tables else 0} tables")
    
    # Save results
    output_file = pdf_path.parent / f"{pdf_path.stem}_structure_inspection.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\nInspection results saved to: {output_file}")
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python inspect_pdf_structure.py <pdf_file>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    
    try:
        inspect_pdf_structure(pdf_file)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()


