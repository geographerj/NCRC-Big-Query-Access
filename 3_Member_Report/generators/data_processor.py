"""
Data Processor for Member Reports

Processes HMDA data and generates:
- Metrics calculations
- Peer comparisons
- Narrative text
- Table data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from scipy import stats


class MemberReportDataProcessor:
    """Process data for member reports"""
    
    def __init__(self):
        """Initialize data processor"""
        pass
    
    def process_report_data(self, 
                          hmda_data: pd.DataFrame,
                          config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process HMDA data and generate report data structure
        
        Args:
            hmda_data: Raw HMDA data DataFrame
            config: Report configuration
        
        Returns:
            Dictionary with processed data for report generation
        """
        # Calculate metrics
        metrics = self._calculate_metrics(hmda_data, config)
        
        # Generate peer comparisons
        peer_data = self._calculate_peer_comparisons(hmda_data, config)
        
        # Generate narratives
        narratives = self._generate_narratives(metrics, peer_data, config)
        
        # Prepare tables
        tables = self._prepare_tables(metrics, peer_data, config)
        
        return {
            'metrics': metrics,
            'peer_data': peer_data,
            'narratives': narratives,
            'tables': tables,
            'methods': self._prepare_methods(config)
        }
    
    def _calculate_metrics(self, df: pd.DataFrame, config: Dict) -> Dict:
        """Calculate lending metrics"""
        metrics = {}
        
        # Basic metrics
        metrics['total_originations'] = len(df[df['action_taken'] == '1'])
        metrics['total_amount'] = df[df['action_taken'] == '1']['loan_amount'].sum()
        
        # Demographic metrics (if columns exist)
        if 'is_hispanic' in df.columns:
            metrics['hispanic_count'] = df['is_hispanic'].sum()
            metrics['hispanic_percentage'] = (metrics['hispanic_count'] / metrics['total_originations'] * 100) if metrics['total_originations'] > 0 else 0
        
        if 'is_black' in df.columns:
            metrics['black_count'] = df['is_black'].sum()
            metrics['black_percentage'] = (metrics['black_count'] / metrics['total_originations'] * 100) if metrics['total_originations'] > 0 else 0
        
        # Income metrics
        if 'is_lmib' in df.columns:
            metrics['lmib_count'] = df['is_lmib'].sum()
            metrics['lmib_percentage'] = (metrics['lmib_count'] / metrics['total_originations'] * 100) if metrics['total_originations'] > 0 else 0
        
        if 'is_lmict' in df.columns:
            metrics['lmict_count'] = df['is_lmict'].sum()
            metrics['lmict_percentage'] = (metrics['lmict_count'] / metrics['total_originations'] * 100) if metrics['total_originations'] > 0 else 0
        
        return metrics
    
    def _calculate_peer_comparisons(self, df: pd.DataFrame, config: Dict) -> Dict:
        """Calculate peer lender comparisons"""
        # Placeholder - would implement peer identification and comparison
        return {}
    
    def _generate_narratives(self, metrics: Dict, peer_data: Dict, 
                            config: Dict) -> Dict[str, str]:
        """Generate narrative text for report sections"""
        narratives = {}
        
        # Introduction
        narratives['introduction'] = self._generate_introduction(config)
        
        # Key points
        narratives['key_points'] = self._generate_key_points(metrics, peer_data)
        
        # Overview
        narratives['overview'] = self._generate_overview(metrics, config)
        
        # Top lenders
        narratives['top_lenders'] = self._generate_top_lenders_analysis(metrics, config)
        
        return narratives
    
    def _generate_introduction(self, config: Dict) -> str:
        """Generate introduction section"""
        metadata = config.get('report_metadata', {})
        geography = config.get('geography', {})
        years = metadata.get('years', [])
        
        year_range = f"{min(years)}-{max(years)}" if years else "specified years"
        
        intro = f"""
This report analyzes mortgage lending patterns in {geography.get('type', 'the specified area')} 
from {year_range}. The analysis examines lending to borrowers by race and ethnicity, 
low-to-moderate income borrowers, and geographic patterns that may indicate redlining.
        """
        return intro.strip()
    
    def _generate_key_points(self, metrics: Dict, peer_data: Dict) -> List[str]:
        """Generate key findings"""
        points = []
        
        if 'total_originations' in metrics:
            points.append(f"Total originations analyzed: {metrics['total_originations']:,}")
        
        if 'black_percentage' in metrics:
            points.append(f"Lending to Black borrowers: {metrics['black_percentage']:.1f}% of originations")
        
        if 'hispanic_percentage' in metrics:
            points.append(f"Lending to Hispanic borrowers: {metrics['hispanic_percentage']:.1f}% of originations")
        
        if 'lmib_percentage' in metrics:
            points.append(f"Lending to Low-to-Moderate Income Borrowers: {metrics['lmib_percentage']:.1f}% of originations")
        
        return points
    
    def _generate_overview(self, metrics: Dict, config: Dict) -> str:
        """Generate overview narrative"""
        return "This section provides an overview of lending patterns in the analysis area."
    
    def _generate_top_lenders_analysis(self, metrics: Dict, config: Dict) -> str:
        """Generate top lenders analysis"""
        return "This section analyzes lending patterns among top lenders in the market."
    
    def _prepare_tables(self, metrics: Dict, peer_data: Dict, 
                       config: Dict) -> Dict[str, pd.DataFrame]:
        """Prepare DataFrame tables for Excel export"""
        tables = {}
        
        # Example: Summary table
        summary_data = {
            'Metric': ['Total Originations', 'Black Borrowers %', 'Hispanic Borrowers %', 'LMIB %'],
            'Value': [
                metrics.get('total_originations', 0),
                metrics.get('black_percentage', 0),
                metrics.get('hispanic_percentage', 0),
                metrics.get('lmib_percentage', 0)
            ]
        }
        tables['Summary'] = pd.DataFrame(summary_data)
        
        return tables
    
    def _prepare_methods(self, config: Dict) -> Dict:
        """Prepare methods data"""
        metadata = config.get('report_metadata', {})
        years = metadata.get('years', [])
        
        methods_text = f"""
PURPOSE:
This report analyzes mortgage lending patterns using Home Mortgage Disclosure Act (HMDA) data.

DATA SOURCES:
- HMDA Data: Federal Financial Institutions Examination Council (FFIEC)
- Years: {', '.join(map(str, years))}
- Geographic scope: As specified in configuration

LOAN FILTERS:
Standard HMDA filters applied as specified in report configuration.

For questions about this report, contact: research@ncrc.org
        """
        
        return {'text': methods_text.strip()}

