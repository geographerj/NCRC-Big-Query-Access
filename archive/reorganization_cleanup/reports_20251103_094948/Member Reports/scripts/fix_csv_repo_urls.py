"""Fix GitHub repo URLs in CSV files."""
import pandas as pd
from pathlib import Path

data_dir = Path('Member Reports/data')
old_repo = 'ncrc/dream'
new_repo = 'geographerj/NCRC-Big-Query-Access'

for csv_file in data_dir.glob('buffer_*.csv'):
    print(f"Updating {csv_file.name}...")
    df = pd.read_csv(csv_file)
    
    if 'Image URL' in df.columns:
        df['Image URL'] = df['Image URL'].str.replace(old_repo, new_repo, regex=False)
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        count = df['Image URL'].str.contains(new_repo, na=False).sum()
        print(f"  Updated {count} image URLs")
    else:
        print(f"  No Image URL column found")

print("\nDone!")

