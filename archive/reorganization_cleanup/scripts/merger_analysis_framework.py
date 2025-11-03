"""
Bank Merger Analysis Framework

Comprehensive analysis for bank mergers including:
1. Individual lending reports for each bank (like Fifth Third report)
2. Branch network analysis and overlap detection
3. HHI calculations pre- and post-merger in overlapping markets
4. Combined analysis report

Example: Fifth Third Bank + Comerica Bank merger
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Handle module imports with spaces in path
import importlib.util

# Import utilities
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)

def load_module(module_name, file_path):
    """Load a module from a file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

bigquery_client = load_module(
    "bigquery_client",
    os.path.join(base_dir, "Lending and Branch Analysis", "utils", "bigquery_client.py")
)
branch_queries = load_module(
    "branch_queries",
    os.path.join(base_dir, "Lending and Branch Analysis", "queries", "branch_queries.py")
)
hhi_analysis = load_module(
    "hhi_analysis",
    os.path.join(base_dir, "Lending and Branch Analysis", "utils", "hhi_analysis.py")
)
branch_matching = load_module(
    "branch_matching",
    os.path.join(base_dir, "Lending and Branch Analysis", "utils", "branch_matching.py")
)
branch_hmda_join = load_module(
    "branch_hmda_join",
    os.path.join(base_dir, "Lending and Branch Analysis", "utils", "branch_hmda_join.py")
)

create_client = bigquery_client.create_client


class BankMergerAnalysis:
    """
    Comprehensive merger analysis for two banks.
    """
    
    def __init__(
        self,
        bank1_name: str,
        bank1_lei: str,
        bank1_rssd: str = None,  # RSSD number (RECOMMENDED - more reliable than name)
        bank1_sod_name: str = None,  # SOD name (only if no RSSD)
        bank2_name: str,
        bank2_lei: str,
        bank2_rssd: str = None,  # RSSD number (RECOMMENDED)
        bank2_sod_name: str = None,  # SOD name (only if no RSSD)
        years: List[int] = [2018, 2019, 2020, 2021, 2022, 2023, 2024],
        sod_table: str = 'sod25'  # Table with 2017-2025 data
    ):
        """
        Initialize merger analysis.
        
        Args:
            bank1_name: Name of first bank (for display)
            bank1_lei: LEI of first bank (for HMDA queries)
            bank1_sod_name: Verified SOD institution name (verify manually!)
            bank2_name: Name of second bank (for display)
            bank2_lei: LEI of second bank (for HMDA queries)
            bank2_sod_name: Verified SOD institution name (verify manually!)
            years: Years to analyze
            sod_table: Which SOD table to use
        """
        self.bank1_name = bank1_name
        self.bank1_lei = bank1_lei
        self.bank1_rssd = bank1_rssd
        self.bank1_sod_name = bank1_sod_name
        self.bank2_name = bank2_name
        self.bank2_lei = bank2_lei
        self.bank2_rssd = bank2_rssd
        self.bank2_sod_name = bank2_sod_name
        self.years = years
        self.sod_table = sod_table
        
        # Validate that we have RSSD or SOD name for each bank
        if not bank1_rssd and not bank1_sod_name:
            raise ValueError(f"Must provide either bank1_rssd or bank1_sod_name for {bank1_name}")
        if not bank2_rssd and not bank2_sod_name:
            raise ValueError(f"Must provide either bank2_rssd or bank2_sod_name for {bank2_name}")
        
        self.client = create_client()
        
        print(f"\n{'='*80}")
        print(f"MERGER ANALYSIS: {bank1_name} + {bank2_name}")
        print(f"{'='*80}")
        print(f"Bank 1 - HMDA Name: {bank1_name}, LEI: {bank1_lei}")
        if bank1_rssd:
            print(f"Bank 1 - RSSD: {bank1_rssd} (USING RSSD - MOST RELIABLE!)")
        else:
            print(f"Bank 1 - SOD Name: {bank1_sod_name} (name matching)")
        print(f"Bank 2 - HMDA Name: {bank2_name}, LEI: {bank2_lei}")
        if bank2_rssd:
            print(f"Bank 2 - RSSD: {bank2_rssd} (USING RSSD - MOST RELIABLE!)")
        else:
            print(f"Bank 2 - SOD Name: {bank2_sod_name} (name matching)")
        print(f"Years: {years}")
        print(f"SOD Table: {sod_table}")
        print(f"{'='*80}\n")
    
    
    def get_top_cbsas(self, lei: str, year: int = 2024, limit: int = 20) -> pd.DataFrame:
        """
        Get top CBSAs by lending volume for a bank.
        """
        query = f"""
        SELECT 
            cbsa_code,
            COUNTIF(action_taken = '1') as originations,
            SUM(CASE WHEN action_taken = '1' THEN loan_amount END) as loan_volume
        FROM `hdma1-242116.hmda.hmda`
        WHERE activity_year = {year}
          AND lei = '{lei}'
          AND action_taken = '1'
          AND cbsa_code IS NOT NULL
          AND cbsa_code != ''
        GROUP BY cbsa_code
        ORDER BY originations DESC
        LIMIT {limit}
        """
        
        return self.client.execute_query(query)
    
    
    def get_lending_by_cbsa(self, lei: str, cbsa_codes: List[str], years: List[int]) -> pd.DataFrame:
        """
        Get lending data by CBSA for multiple years.
        """
        cbsa_str = "', '".join(cbsa_codes)
        years_str = ', '.join(map(str, years))
        
        query = f"""
        SELECT 
            activity_year as year,
            cbsa_code,
            COUNTIF(action_taken = '1') as originations,
            SUM(CASE WHEN action_taken = '1' THEN loan_amount END) as loan_volume
        FROM `hdma1-242116.hmda.hmda`
        WHERE activity_year IN ({years_str})
          AND lei = '{lei}'
          AND cbsa_code IN ('{cbsa_str}')
          AND action_taken = '1'
        GROUP BY activity_year, cbsa_code
        ORDER BY year, cbsa_code
        """
        
        return self.client.execute_query(query)
    
    
    def get_branch_data(self, rssd: str = None, sod_name: str = None, year: int = None) -> pd.DataFrame:
        """
        Get branch data for a bank using RSSD (preferred) or name.
        """
        if rssd:
            # Use RSSD - most reliable!
            query = branch_queries.get_branches_by_rssd(
                rssd=rssd,
                year=year or 2024,
                sod_table=self.sod_table
            )
        elif sod_name:
            # Fallback to name matching
            query = branch_queries.get_lender_branches(
                lender_name=sod_name,
                year=year or 2024,
                sod_table=self.sod_table
            )
        else:
            raise ValueError("Must provide either rssd or sod_name")
        
        df = self.client.execute_query(query)
        
        # Deduplicate using uninumbr
        if 'uninumbr' in df.columns and 'year' in df.columns:
            df = branch_matching.deduplicate_branches(df, year_col='year', unique_col='uninumbr')
        
        return df
    
    
    def find_overlapping_markets(self, year: int = 2024) -> pd.DataFrame:
        """
        Find CBSAs where both banks have branches or significant lending.
        """
        # Get lending CBSAs for both banks
        bank1_cbsas = self.get_top_cbsas(self.bank1_lei, year=year)
        bank2_cbsas = self.get_top_cbsas(self.bank2_lei, year=year)
        
        # Get branch CBSAs for both banks (use RSSD if available)
        bank1_branches = self.get_branch_data(rssd=self.bank1_rssd, sod_name=self.bank1_sod_name, year=year)
        bank2_branches = self.get_branch_data(rssd=self.bank2_rssd, sod_name=self.bank2_sod_name, year=year)
        
        # Combine CBSAs (lending + branches)
        bank1_markets = set(bank1_cbsas['cbsa_code'].unique()) | set(bank1_branches['cbsa_code'].unique()) if 'cbsa_code' in bank1_branches.columns else set(bank1_cbsas['cbsa_code'].unique())
        bank2_markets = set(bank2_cbsas['cbsa_code'].unique()) | set(bank2_branches['cbsa_code'].unique()) if 'cbsa_code' in bank2_branches.columns else set(bank2_cbsas['cbsa_code'].unique())
        
        # Find overlap
        overlapping = bank1_markets & bank2_markets
        
        # Create summary
        overlap_data = []
        for cbsa in overlapping:
            bank1_lending = bank1_cbsas[bank1_cbsas['cbsa_code'] == cbsa]['originations'].sum() if len(bank1_cbsas[bank1_cbsas['cbsa_code'] == cbsa]) > 0 else 0
            bank2_lending = bank2_cbsas[bank2_cbsas['cbsa_code'] == cbsa]['originations'].sum() if len(bank2_cbsas[bank2_cbsas['cbsa_code'] == cbsa]) > 0 else 0
            
            bank1_branch_count = len(bank1_branches[bank1_branches['cbsa_code'] == cbsa]) if 'cbsa_code' in bank1_branches.columns else 0
            bank2_branch_count = len(bank2_branches[bank2_branches['cbsa_code'] == cbsa]) if 'cbsa_code' in bank2_branches.columns else 0
            
            overlap_data.append({
                'cbsa_code': cbsa,
                f'{self.bank1_name}_originations': bank1_lending,
                f'{self.bank2_name}_originations': bank2_lending,
                f'{self.bank1_name}_branches': bank1_branch_count,
                f'{self.bank2_name}_branches': bank2_branch_count,
                'total_combined_originations': bank1_lending + bank2_lending,
                'total_combined_branches': bank1_branch_count + bank2_branch_count
            })
        
        return pd.DataFrame(overlap_data).sort_values('total_combined_originations', ascending=False)
    
    
    def calculate_hhi_pre_merger(self, cbsa_code: str, year: int) -> Dict:
        """
        Calculate HHI for a market pre-merger (banks separate).
        """
        # Get all lending in this CBSA for this year
        query = f"""
        SELECT 
            lei,
            COUNTIF(action_taken = '1') as originations,
            SUM(CASE WHEN action_taken = '1' THEN loan_amount END) as loan_amount
        FROM `hdma1-242116.hmda.hmda`
        WHERE activity_year = {year}
          AND cbsa_code = '{cbsa_code}'
          AND action_taken = '1'
          AND cbsa_code IS NOT NULL
        GROUP BY lei
        """
        
        df = self.client.execute_query(query)
        
        if len(df) == 0:
            return None
        
        # Calculate market shares
        total_originations = df['originations'].sum()
        df['market_share_pct'] = (df['originations'] / total_originations) * 100
        
        # Calculate HHI
        hhi = hhi_analysis.calculate_hhi(df['market_share_pct'], as_percentages=True)
        
        # Get shares for merging banks
        bank1_share = df[df['lei'] == self.bank1_lei]['market_share_pct'].values[0] if len(df[df['lei'] == self.bank1_lei]) > 0 else 0
        bank2_share = df[df['lei'] == self.bank2_lei]['market_share_pct'].values[0] if len(df[df['lei'] == self.bank2_lei]) > 0 else 0
        
        return {
            'cbsa_code': cbsa_code,
            'year': year,
            'hhi_pre_merger': hhi,
            'concentration_category': hhi_analysis.categorize_market_concentration(hhi),
            'total_originations': total_originations,
            'number_of_lenders': len(df),
            f'{self.bank1_name}_share': bank1_share,
            f'{self.bank2_name}_share': bank2_share,
            'combined_share': bank1_share + bank2_share
        }
    
    
    def calculate_hhi_post_merger(self, cbsa_code: str, year: int) -> Dict:
        """
        Calculate HHI for a market post-merger (banks combined).
        """
        # Get all lending data
        query = f"""
        SELECT 
            lei,
            COUNTIF(action_taken = '1') as originations,
            SUM(CASE WHEN action_taken = '1' THEN loan_amount END) as loan_amount
        FROM `hdma1-242116.hmda.hmda`
        WHERE activity_year = {year}
          AND cbsa_code = '{cbsa_code}'
          AND action_taken = '1'
        GROUP BY lei
        """
        
        df = self.client.execute_query(query)
        
        if len(df) == 0:
            return None
        
        # Combine the merging banks
        merging_leis = [self.bank1_lei, self.bank2_lei]
        combined_originations = df[df['lei'].isin(merging_leis)]['originations'].sum()
        combined_loan_amount = df[df['lei'].isin(merging_leis)]['loan_amount'].sum()
        
        # Remove individual banks, add combined
        df_post = df[~df['lei'].isin(merging_leis)].copy()
        combined_row = pd.DataFrame([{
            'lei': f'{self.bank1_lei}+{self.bank2_lei}',
            'originations': combined_originations,
            'loan_amount': combined_loan_amount
        }])
        df_post = pd.concat([df_post, combined_row], ignore_index=True)
        
        # Calculate market shares
        total_originations = df_post['originations'].sum()
        df_post['market_share_pct'] = (df_post['originations'] / total_originations) * 100
        
        # Calculate HHI
        hhi = hhi_analysis.calculate_hhi(df_post['market_share_pct'], as_percentages=True)
        
        # Combined bank share
        combined_share = df_post[df_post['lei'].str.contains('+')]['market_share_pct'].values[0]
        
        return {
            'cbsa_code': cbsa_code,
            'year': year,
            'hhi_post_merger': hhi,
            'concentration_category': hhi_analysis.categorize_market_concentration(hhi),
            'combined_bank_share': combined_share
        }
    
    
    def analyze_hhi_in_overlapping_markets(self, year: int = 2024) -> pd.DataFrame:
        """
        Calculate HHI pre- and post-merger for all overlapping markets.
        """
        print(f"\nAnalyzing HHI in overlapping markets for {year}...")
        
        # Get overlapping markets
        overlap = self.find_overlapping_markets(year=year)
        
        if len(overlap) == 0:
            print("No overlapping markets found!")
            return pd.DataFrame()
        
        results = []
        
        for _, row in overlap.iterrows():
            cbsa = row['cbsa_code']
            
            print(f"  Analyzing CBSA {cbsa}...")
            
            # Pre-merger HHI
            pre_hhi = self.calculate_hhi_pre_merger(cbsa, year)
            if pre_hhi is None:
                continue
            
            # Post-merger HHI
            post_hhi = self.calculate_hhi_post_merger(cbsa, year)
            if post_hhi is None:
                continue
            
            # Combine results
            result = {
                **pre_hhi,
                **post_hhi,
                'hhi_change': post_hhi['hhi_post_merger'] - pre_hhi['hhi_pre_merger'],
                'antitrust_concern': (
                    pre_hhi['hhi_pre_merger'] > 1800 and 
                    (post_hhi['hhi_post_merger'] - pre_hhi['hhi_pre_merger']) > 100
                )
            }
            
            results.append(result)
        
        df_results = pd.DataFrame(results)
        
        print(f"\n✓ Analyzed {len(df_results)} overlapping markets")
        if len(df_results) > 0:
            concerns = df_results['antitrust_concern'].sum()
            print(f"  Markets with antitrust concerns: {concerns}")
        
        return df_results.sort_values('hhi_change', ascending=False)
    
    
    def generate_full_report(self, output_dir: str = "reports/merger_analysis") -> str:
        """
        Generate comprehensive merger analysis report.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_path / f"{self.bank1_name}_{self.bank2_name}_Merger_Analysis_{timestamp}.xlsx"
        
        print(f"\n{'='*80}")
        print("GENERATING COMPREHENSIVE MERGER ANALYSIS REPORT")
        print(f"{'='*80}\n")
        
        with pd.ExcelWriter(str(report_file), engine='openpyxl') as writer:
            # 1. Executive Summary
            print("1. Creating Executive Summary...")
            self._create_executive_summary(writer)
            
            # 2. Overlapping Markets
            print("2. Analyzing Overlapping Markets...")
            overlap = self.find_overlapping_markets(year=2024)
            overlap.to_excel(writer, sheet_name='Overlapping Markets', index=False)
            
            # 3. HHI Analysis
            print("3. Calculating HHI Pre/Post Merger...")
            hhi_results = self.analyze_hhi_in_overlapping_markets(year=2024)
            hhi_results.to_excel(writer, sheet_name='HHI Analysis', index=False)
            
            # 4. Branch Networks
            print("4. Analyzing Branch Networks...")
            self._create_branch_analysis(writer, year=2024)
            
            # 5. Lending Comparison
            print("5. Comparing Lending Patterns...")
            self._create_lending_comparison(writer)
        
        print(f"\n✓ Report saved to: {report_file}")
        return str(report_file)
    
    
    def _create_executive_summary(self, writer):
        """Create executive summary sheet"""
        summary_data = {
            'Metric': [
                'Bank 1 Name',
                'Bank 1 LEI',
                'Bank 1 SOD Name',
                'Bank 2 Name',
                'Bank 2 LEI',
                'Bank 2 SOD Name',
                'Analysis Years',
                'SOD Table Used',
                'Report Generated'
            ],
            'Value': [
                self.bank1_name,
                self.bank1_lei,
                self.bank1_sod_name,
                self.bank2_name,
                self.bank2_lei,
                self.bank2_sod_name,
                ', '.join(map(str, self.years)),
                self.sod_table,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
        }
        
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Executive Summary', index=False)
    
    
    def _create_branch_analysis(self, writer, year: int):
        """Create branch network analysis"""
        bank1_branches = self.get_branch_data(rssd=self.bank1_rssd, sod_name=self.bank1_sod_name, year=year)
        bank2_branches = self.get_branch_data(rssd=self.bank2_rssd, sod_name=self.bank2_sod_name, year=year)
        
        # Bank 1 branches
        bank1_branches['bank'] = self.bank1_name
        bank1_branches.to_excel(writer, sheet_name=f'{self.bank1_name} Branches', index=False)
        
        # Bank 2 branches
        bank2_branches['bank'] = self.bank2_name
        bank2_branches.to_excel(writer, sheet_name=f'{self.bank2_name} Branches', index=False)
        
        # Combined summary by CBSA
        if 'cbsa_code' in bank1_branches.columns and 'cbsa_code' in bank2_branches.columns:
            combined = pd.concat([bank1_branches, bank2_branches], ignore_index=True)
            summary = combined.groupby(['cbsa_code', 'bank']).agg({
                'uninumbr': 'count',
                'deposits': 'sum'
            }).reset_index()
            summary.columns = ['cbsa_code', 'bank', 'branch_count', 'total_deposits']
            summary.to_excel(writer, sheet_name='Branch Summary by CBSA', index=False)
    
    
    def _create_lending_comparison(self, writer):
        """Create lending comparison"""
        # Get top CBSAs for both banks
        bank1_top = self.get_top_cbsas(self.bank1_lei, year=2024, limit=20)
        bank2_top = self.get_top_cbsas(self.bank2_lei, year=2024, limit=20)
        
        bank1_top['bank'] = self.bank1_name
        bank2_top['bank'] = self.bank2_name
        
        comparison = pd.concat([bank1_top, bank2_top], ignore_index=True)
        comparison.to_excel(writer, sheet_name='Lending by CBSA', index=False)


def main():
    """
    Example: Fifth Third + Comerica merger analysis
    """
    # IMPORTANT: Verify SOD names manually before running!
    # LEIs found from data/reference/Lenders_and_LEI_Numbers.csv:
    # - Fifth Third Bank: QFROUN1UWUYU0DVIWD51
    # - Comerica Bank: 70WY0ID1N53Q4254VH70
    
    analysis = BankMergerAnalysis(
        bank1_name="Fifth Third Bank",
        bank1_lei="QFROUN1UWUYU0DVIWD51",
        bank1_rssd="723112",  # RSSD from SharePoint file - MOST RELIABLE!
        bank2_name="Comerica Bank",
        bank2_lei="70WY0ID1N53Q4254VH70",
        bank2_rssd="60143",  # RSSD from SharePoint file - MOST RELIABLE!
        years=[2018, 2019, 2020, 2021, 2022, 2023, 2024],
        sod_table='sod25'  # VERIFY THIS HAS 2017-2025 DATA!
    )
    
    # Generate full report
    report_path = analysis.generate_full_report()
    print(f"\n✓ Complete! Report: {report_path}")


if __name__ == "__main__":
    main()

