"""Verify Buffer CSV format is correct."""
import pandas as pd
from pathlib import Path

data_dir = Path('Member Reports/data')
platforms = ['bluesky', 'facebook', 'linkedin']

for platform in platforms:
    csv_file = data_dir / f'buffer_{platform}.csv'
    if not csv_file.exists():
        print(f"[WARNING] {csv_file} not found")
        continue
    
    df = pd.read_csv(csv_file)
    
    # Check required columns
    required_cols = ['Text', 'Image URL', 'Tags', 'Posting Time']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        print(f"[ERROR] {platform}: Missing columns: {missing}")
        continue
    
    # Check Posting Time format (should be YYYY-MM-DD HH:MM = 16 chars)
    times = df['Posting Time'].dropna()
    invalid_times = []
    for t in times:
        t_str = str(t).strip()
        if len(t_str) != 16:
            invalid_times.append(t_str)
        elif not (t_str[4] == '-' and t_str[7] == '-' and t_str[10] == ' ' and t_str[13] == ':'):
            invalid_times.append(t_str)
    
    if invalid_times:
        print(f"[ERROR] {platform}: Invalid Posting Time format: {invalid_times[:3]}")
    else:
        print(f"[OK] {platform}: Posting Time format OK")
    
    # Check Tags column is empty (tags must exist in Buffer first)
    tags_filled = df['Tags'].dropna()
    tags_filled = tags_filled[tags_filled != '']
    if len(tags_filled) > 0:
        print(f"[WARNING] {platform}: Tags column has values (Buffer requires tags to exist first): {tags_filled.iloc[0]}")
    else:
        print(f"[OK] {platform}: Tags column is empty (correct)")
    
    print(f"   Total posts: {len(df)}")
    print()

