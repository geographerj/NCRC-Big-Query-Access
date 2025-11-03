"""Quick script to check Tampa data"""
import pandas as pd

df = pd.read_csv('Member Reports/data/raw/tampa_market_data.csv')
m = df[df['analysis_type'] == 'Market'].iloc[0]

print('2018 Market Data:')
print(f'Total originations: {m["total_originations"]}')
print(f'Loans with demographics: {m["loans_with_demographics"]}')
print(f'\nRace counts:')
print(f'  Hispanic: {m["hispanic_loans"]}')
print(f'  Black: {m["black_loans"]}')
print(f'  Asian: {m["asian_loans"]}')
print(f'  White: {m["white_loans"]}')
print(f'  Native American: {m["native_american_loans"]}')
print(f'  HoPI: {m["hopi_loans"]}')

total_classified = (m['hispanic_loans'] + m['black_loans'] + m['asian_loans'] + 
                   m['white_loans'] + m['native_american_loans'] + m['hopi_loans'])
print(f'\nTotal classified: {total_classified}')
print(f'Unclassified (no data): {m["loans_with_demographics"] - total_classified}')


