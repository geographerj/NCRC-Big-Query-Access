"""
PDF Report Generator for NCRC Member Reports

Generates branded PDF reports with:
- NCRC logo and branding
- Pagination
- Report sections (Introduction, Key Points, Overview, Analysis, Methods)
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import Dict, List, Optional, Any
import os
from pathlib import Path


# NCRC Brand Colors (RGB)
NCRC_BLUE = colors.HexColor('#003366')
NCRC_ORANGE = colors.HexColor('#FF6B35')


class PDFReportGenerator:
    """Generate PDF reports with NCRC branding"""
    
    def __init__(self, logo_path: Optional[str] = None):
        """
        Initialize PDF generator
        
        Args:
            logo_path: Path to NCRC logo image file
        """
        self.logo_path = logo_path or self._find_logo()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _find_logo(self) -> Optional[str]:
        """Find NCRC logo file"""
        possible_paths = [
            "Member Reports/supporting_files/NCRC_Logo.png",
            "Member Reports/supporting_files/NCRC_Logo.jpg",
            "supporting_files/NCRC_Logo.png",
            "supporting_files/NCRC_Logo.jpg"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.title_style = ParagraphStyle(
            'NCRCTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=NCRC_BLUE,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'NCRCSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=NCRC_BLUE,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        # Section heading
        self.section_style = ParagraphStyle(
            'NCRCSection',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=NCRC_BLUE,
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        )
        
        # Body text
        self.body_style = ParagraphStyle(
            'NCRCBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        )
        
        # Key points style
        self.key_point_style = ParagraphStyle(
            'NCRCKeyPoint',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            leftIndent=20,
            bulletIndent=10,
            fontName='Helvetica'
        )
    
    def _header_footer(self, canvas, doc):
        """Add logo on first content page and page number on all pages"""
        # Save state
        canvas.saveState()
        
        # Add logo to title page (page 1) only - positioned precisely 10 points from left and top
        if doc.page == 1 and self.logo_path:
            try:
                from reportlab.lib.utils import ImageReader
                from PIL import Image as PILImage
                
                # Get image dimensions using PIL for accurate aspect ratio
                pil_img = PILImage.open(self.logo_path)
                img_width, img_height = pil_img.size
                aspect_ratio = img_width / img_height
                
                # Calculate logo size - maintain aspect ratio, reasonable max height
                # Max height: 1 inch, but maintain exact aspect ratio
                max_height = 1.0 * inch
                logo_height = min(max_height, img_height)
                logo_width = logo_height * aspect_ratio
                
                # Position: exactly 10 points from left and top
                offset_points = 10  # 10 points from edges
                
                # ReportLab coordinates: y=0 is bottom, so from top = page_height - logo_height - offset
                x_position = offset_points  # 10 points from left edge
                y_position = doc.pagesize[1] - logo_height - offset_points  # 10 points from top
                
                # Draw image preserving aspect ratio exactly
                canvas.drawImage(self.logo_path, x_position, y_position, 
                                width=logo_width, height=logo_height, 
                                preserveAspectRatio=True,
                                anchor='nw')  # Anchor at northwest (top-left)
            except Exception as e:
                # If logo fails to load, just continue without it
                pass
        
        # Page number - bottom right on all pages
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.black)
        page_text = f"{doc.page}"
        canvas.drawRightString(doc.width + doc.leftMargin - 0.5*inch, 
                              0.5*inch, 
                              page_text)
        
        # Restore state
        canvas.restoreState()
    
    def _get_header_info(self) -> Dict[str, str]:
        """Get NCRC header information"""
        return {
            "organization": "National Community Reinvestment Coalition",
            "organization_short": "NCRC",
            "contact_email": "research@ncrc.org",
            "website": "www.ncrc.org"
        }
    
    def generate_report(self, 
                       output_path: str,
                       report_title: str,
                       report_data: Dict[str, Any],
                       member_org: Optional[str] = None,
                       report_date: Optional[str] = None) -> str:
        """
        Generate complete PDF report
        
        Args:
            output_path: Path to save PDF
            report_title: Report title
            report_data: Dictionary with report sections and data
            member_org: Member organization name
            report_date: Report date (ISO format)
        
        Returns:
            Path to generated PDF
        """
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1.0*inch,  # Increased to avoid header overlap
            bottomMargin=0.75*inch
        )
        
        # Build story (content)
        story = []
        
        # Title page
        story.extend(self._create_title_page(report_title, member_org, report_date))
        story.append(PageBreak())
        
        # Introduction
        if 'introduction' in report_data:
            story.extend(self._create_section('Introduction', report_data['introduction']))
        
        # Key Points
        if 'key_points' in report_data:
            story.extend(self._create_key_points_section(report_data['key_points']))
        
        # Overview of Lending
        if 'overview' in report_data:
            story.extend(self._create_overview_section(report_data['overview']))
        
        # Analysis of Top Lenders
        if 'top_lenders' in report_data:
            story.extend(self._create_top_lenders_section(report_data['top_lenders']))
        
        # Methods and Sources
        story.extend(self._create_methods_section(report_data.get('methods', {})))
        
        # Build PDF
        doc.build(story, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
        
        return output_path
    
    def _create_title_page(self, title: str, member_org: Optional[str], 
                          report_date: Optional[str]) -> List:
        """Create title page"""
        elements = []
        
        # Note: Logo is added via _header_footer function for precise positioning
        # Add spacer to leave room for logo (logo will be drawn at absolute position)
        elements.append(Spacer(1, 1.0*inch))
        
        # Title
        elements.append(Paragraph(title, self.title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Member organization
        if member_org:
            elements.append(Paragraph(f"Prepared for: {member_org}", self.subtitle_style))
            elements.append(Spacer(1, 0.2*inch))
        
        # Report date
        if report_date:
            elements.append(Paragraph(f"Report Date: {report_date}", self.body_style))
        
        elements.append(Spacer(1, 1*inch))
        
        # Organization info
        header_info = self._get_header_info()
        elements.append(Paragraph(header_info['organization'], self.subtitle_style))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(header_info['contact_email'], self.body_style))
        elements.append(Paragraph(header_info['website'], self.body_style))
        
        return elements
    
    def _create_section(self, section_title: str, content: Any) -> List:
        """Create a section with title and content"""
        elements = []
        elements.append(Paragraph(section_title, self.section_style))
        
        if isinstance(content, str):
            elements.append(Paragraph(content, self.body_style))
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, str):
                    elements.append(Paragraph(item, self.body_style))
                elif isinstance(item, dict):
                    # Handle formatted paragraphs
                    text = item.get('text', '')
                    elements.append(Paragraph(text, self.body_style))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _create_key_points_section(self, key_points: List[str]) -> List:
        """Create key points section"""
        elements = []
        elements.append(Paragraph("Key Findings", self.section_style))
        
        for point in key_points:
            elements.append(Paragraph(f"• {point}", self.key_point_style))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _create_overview_section(self, overview_data: Dict) -> List:
        """Create overview of lending section with lead-in, two tables, and analysis"""
        elements = []
        elements.append(Paragraph("Overview of Lending", self.section_style))
        
        # Lead-in (2 sentences before tables)
        if 'lead_in' in overview_data:
            elements.append(Paragraph(overview_data['lead_in'], self.body_style))
            elements.append(Spacer(1, 0.15*inch))
        
        # Table 1: Race/Ethnicity with caption
        if 'race_table' in overview_data and overview_data['race_table'] is not None:
            table_data = overview_data['race_table']
            if table_data and len(table_data) > 0:
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                # Caption for first table
                caption_style = ParagraphStyle(
                    'NCRCCaption',
                    parent=self.body_style,
                    fontSize=9,
                    textColor=colors.grey,
                    alignment=TA_LEFT,
                    spaceAfter=12
                )
                caption_text = (
                    "Note: Originations refer to home purchase loans that were originated (approved and closed). "
                    "Percentages for race/ethnicity categories are calculated as a share of loans with demographic "
                    "data available (loans without demographic data are excluded from the denominator). "
                    "Abbreviations: LMIB = Low-to-Moderate Income Borrower, LMICT = Low-to-Moderate "
                    "Income Census Tract, MMCT = Majority-Minority Census Tract."
                )
                caption = Paragraph(caption_text, caption_style)
                
                # Keep table and caption together on one page
                elements.append(KeepTogether([table, Spacer(1, 0.14*inch), caption]))
        
        elements.append(Spacer(1, 0.15*inch))
        
        # Table 2: Geographic metrics
        if 'geographic_table' in overview_data and overview_data['geographic_table'] is not None:
            table_data = overview_data['geographic_table']
            if table_data and len(table_data) > 0:
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                # Keep table together on one page
                elements.append(KeepTogether([table]))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Analysis after tables (multiple paragraphs)
        if 'analysis' in overview_data:
            # Split analysis into paragraphs by double newlines
            analysis_paragraphs = overview_data['analysis'].split('\n\n')
            for para in analysis_paragraphs:
                para = para.strip()
                if para:
                    elements.append(Paragraph(para, self.body_style))
                    elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _create_top_lenders_section(self, lenders_data: Dict) -> List:
        """Create analysis of top lenders section with separate table for each lender"""
        elements = []
        elements.append(Paragraph("Analysis of Top Lenders", self.section_style))
        
        # Narrative
        if 'narrative' in lenders_data:
            elements.append(Paragraph(lenders_data['narrative'], self.body_style))
        
        # Multiple tables - one per lender
        if 'tables' in lenders_data and lenders_data['tables'] is not None:
            lender_narratives = lenders_data.get('lender_narratives', {})
            
            for lender_name, table_data in lenders_data['tables'].items():
                if table_data and len(table_data) > 0:
                    # Add lender name as subheading with optional hyperlink
                    lender_style = ParagraphStyle(
                        'NCRCLenderName',
                        parent=self.section_style,
                        fontSize=12,
                        spaceAfter=8,
                        spaceBefore=16
                    )
                    
                    # Check if lender has a website URL
                    lender_url = None
                    if lender_name in lender_narratives:
                        background_info = lender_narratives[lender_name].get('background_info', {})
                        lender_url = background_info.get('website') or background_info.get('url')
                    
                    # Create lender name with hyperlink if URL available
                    if lender_url:
                        # ReportLab uses <link> tags for hyperlinks
                        lender_name_with_link = f'<link href="{lender_url}" color="blue"><u>{lender_name}</u></link>'
                    else:
                        lender_name_with_link = lender_name
                    
                    elements.append(Paragraph(lender_name_with_link, lender_style))
                    
                    # Add lead-in (2 sentences) if available
                    if lender_name in lender_narratives and 'lead_in' in lender_narratives[lender_name]:
                        lead_in_text = lender_narratives[lender_name]['lead_in']
                        # Convert URLs to hyperlinks
                        import re
                        url_pattern = r'(https?://[^\s\)]+)'
                        urls_in_text = re.findall(url_pattern, lead_in_text)
                        if urls_in_text:
                            for url in urls_in_text:
                                link_text = f'<link href="{url}" color="blue"><u>{url}</u></link>'
                                lead_in_text = lead_in_text.replace(url, link_text)
                        elements.append(Paragraph(lead_in_text, self.body_style))
                        elements.append(Spacer(1, 0.1*inch))
                    
                    # Create table
                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), NCRC_BLUE),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                    ]))
                    # Keep table together on one page
                    elements.append(KeepTogether([table]))
                    
                    # Add analysis after table if available - split into paragraphs
                    if lender_name in lender_narratives and 'analysis' in lender_narratives[lender_name]:
                        elements.append(Spacer(1, 0.15*inch))
                        # Split analysis into paragraphs by double newlines
                        analysis_paragraphs = lender_narratives[lender_name]['analysis'].split('\n\n')
                        for para in analysis_paragraphs:
                            para = para.strip()
                            if para:
                                elements.append(Paragraph(para, self.body_style))
                                elements.append(Spacer(1, 0.1*inch))
                    
                    elements.append(Spacer(1, 0.2*inch))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _create_methods_section(self, methods_data: Dict) -> List:
        """Create methods and sources section with bullet points"""
        elements = []
        elements.append(Paragraph("Methods and Sources", self.section_style))
        
        # Use methodology template if available
        methods_text = methods_data.get('text', self._get_default_methodology())
        
        # Split into paragraphs and handle bullet points
        import re
        
        # Process lines to handle multi-line bullet points properly
        # Join indented continuation lines with their bullet points
        lines = methods_text.split('\n')
        processed_lines = []
        current_bullet = None
        
        for i, line in enumerate(lines):
            line_stripped = line.rstrip()
            line_leading = line[:len(line) - len(line.lstrip())] if line.strip() else ''
            
            # Check if this is a bullet point
            is_bullet = (line_stripped.startswith('- ') or 
                        line_stripped.startswith('• ') or 
                        (len(line_stripped) > 2 and line_stripped[0].isdigit() and line_stripped[1] == '.'))
            
            # Check if this is an indented continuation (starts with 2+ spaces, not a bullet)
            is_indented_continuation = (len(line_leading) >= 2 and 
                                       not is_bullet and 
                                       line_stripped and
                                       current_bullet is not None)
            
            if not line_stripped:
                # Empty line - reset and add paragraph break
                if current_bullet:
                    processed_lines.append(current_bullet)
                    current_bullet = None
                processed_lines.append('')
            elif is_bullet:
                # New bullet point - save previous one if exists
                if current_bullet:
                    processed_lines.append(current_bullet)
                current_bullet = line_stripped
            elif is_indented_continuation:
                # Continuation line - append to current bullet with line break
                current_bullet = current_bullet + '<br/>' + line_stripped
            else:
                # Regular paragraph line
                if current_bullet:
                    processed_lines.append(current_bullet)
                    current_bullet = None
                processed_lines.append(line_stripped)
        
        # Save any remaining bullet point
        if current_bullet:
            processed_lines.append(current_bullet)
        
        # Now process paragraphs (split by empty lines)
        for paragraph in '\n'.join(processed_lines).split('\n\n'):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Check if paragraph contains URLs and convert to hyperlinks
            url_pattern = r'(https?://[^\s\)]+)'
            urls_in_text = re.findall(url_pattern, paragraph)
            
            if urls_in_text:
                # Replace URLs with hyperlink tags for ReportLab
                for url in urls_in_text:
                    # Create clickable link
                    link_text = f'<link href="{url}" color="blue"><u>{url}</u></link>'
                    paragraph = paragraph.replace(url, link_text)
            
            # Check if paragraph starts with bullet marker or numbered list item
            if paragraph.startswith('•') or paragraph.startswith('-') or (len(paragraph) > 2 and paragraph[0].isdigit() and paragraph[1] == '.'):
                # It's a bullet point or numbered list item
                elements.append(Paragraph(paragraph, self.body_style))
            else:
                # Regular paragraph (no bold formatting)
                elements.append(Paragraph(paragraph, self.body_style))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _get_default_methodology(self) -> str:
        """Get default methodology text"""
        return """
This report analyzes mortgage lending patterns using Home Mortgage Disclosure Act (HMDA) data 
from the Federal Financial Institutions Examination Council (FFIEC).

Data Sources:
• HMDA data: Federal Financial Institutions Examination Council (FFIEC)
• Geographic data: U.S. Census Bureau
• Years analyzed: As specified in report configuration

Loan Filters:
Standard HMDA filters were applied including owner-occupied properties, site-built construction, 
and originations only. Reverse mortgages were excluded.

Race/Ethnicity Classification:
NCRC methodology uses hierarchical classification with Hispanic ethnicity checked first, 
followed by race classification for non-Hispanic borrowers.

Peer Comparison:
Peers are defined as lenders with 50%-200% of the subject lender's origination volume 
in each market-year combination.

Report Production and Disclaimer:
This report was produced using Cursor, an AI-powered code editor, and other AI language models 
to assist with data analysis, narrative generation, and report formatting. While NCRC staff have 
reviewed this report for accuracy and quality, there may be errors or omissions. If readers have 
questions about the data, methodology, or findings presented in this report, or if they identify 
any potential errors, please contact the NCRC Research Department for review and clarification.

For questions about this report, contact: research@ncrc.org
        """

