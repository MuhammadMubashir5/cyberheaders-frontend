from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.units import inch, cm, mm
from reportlab.platypus import HRFlowable
from reportlab.graphics.shapes import Drawing, Rect, String
from datetime import datetime
import logging
import textwrap
import re
import math

# Optional imports with fallbacks
try:
    from reportlab.graphics.charts.barcharts import VerticalBarChart

    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False
    print("ReportLab charts not available. Using fallback visualizations.")

try:
    from reportlab.graphics.charts.piecharts import Pie

    PIE_CHARTS_AVAILABLE = True
except ImportError:
    PIE_CHARTS_AVAILABLE = False

try:
    from reportlab.graphics import renderPDF

    RENDER_PDF_AVAILABLE = True
except ImportError:
    RENDER_PDF_AVAILABLE = False

logger = logging.getLogger(__name__)


class EnhancedTableOfContents(TableOfContents):
    """Enhanced Table of Contents with better formatting and numbering"""

    def __init__(self):
        super().__init__()
        self.levelStyles = [
            ParagraphStyle(
                name='TOCLevel0',
                fontName='Helvetica-Bold',
                fontSize=12,
                leftIndent=0,
                rightIndent=0,
                spaceBefore=6,
                spaceAfter=3,
                textColor=colors.Color(0.12, 0.23, 0.54)
            ),
            ParagraphStyle(
                name='TOCLevel1',
                fontName='Helvetica',
                fontSize=11,
                leftIndent=20,
                rightIndent=0,
                spaceBefore=3,
                spaceAfter=2,
                textColor=colors.Color(0.02, 0.45, 0.41)
            ),
            ParagraphStyle(
                name='TOCLevel2',
                fontName='Helvetica',
                fontSize=10,
                leftIndent=40,
                rightIndent=0,
                spaceBefore=2,
                spaceAfter=1,
                textColor=colors.Color(0.12, 0.22, 0.31)
            ),
        ]


class ProfessionalPDFGenerator:
    def __init__(self, company_name="CyberHeaders Security", company_logo=None):
        self.company_name = company_name
        self.company_logo = company_logo

        # Enhanced professional color scheme
        self.colors = {
            'primary': colors.Color(0.12, 0.23, 0.54),  # Professional dark blue
            'secondary': colors.Color(0.02, 0.45, 0.41),  # Professional teal
            'accent': colors.Color(0.78, 0.16, 0.16),  # Professional red
            'warning': colors.Color(0.85, 0.47, 0.02),  # Professional orange
            'success': colors.Color(0.13, 0.45, 0.20),  # Green for good scores
            'danger': colors.Color(0.78, 0.16, 0.16),  # Red for poor scores
            'dark': colors.Color(0.12, 0.22, 0.31),  # Dark text
            'light_gray': colors.Color(0.98, 0.98, 0.99),  # Light background
            'medium_gray': colors.Color(0.61, 0.64, 0.69),  # Medium gray
            'border': colors.Color(0.90, 0.91, 0.92),  # Border color
            'watermark': colors.Color(0.95, 0.95, 0.95),  # Very light for watermark
        }

        # Custom styles
        self.custom_styles = self._create_custom_styles()
        self.section_counter = 0
        self.toc = EnhancedTableOfContents()

        # Section tracking for TOC
        self.toc_entries = []

    def _get_score_color(self, score):
        """Return appropriate color based on score"""
        if score >= 80:
            return self.colors['success']
        elif score >= 50:
            return self.colors['warning']
        else:
            return self.colors['danger']

    def _create_custom_styles(self):
        """Create comprehensive custom paragraph styles with improved formatting"""
        styles = getSampleStyleSheet()
        custom_styles = {}

        # Cover page styles
        custom_styles['CoverTitle'] = ParagraphStyle(
            'CoverTitle',
            parent=styles['Title'],
            fontSize=38,
            spaceAfter=25,
            spaceBefore=50,
            textColor=self.colors['primary'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=45
        )

        custom_styles['CoverSubtitle'] = ParagraphStyle(
            'CoverSubtitle',
            parent=styles['Normal'],
            fontSize=22,
            spaceAfter=35,
            textColor=self.colors['secondary'],
            alignment=TA_CENTER,
            fontName='Helvetica',
            leading=26
        )

        custom_styles['CoverInfo'] = ParagraphStyle(
            'CoverInfo',
            parent=styles['Normal'],
            fontSize=13,
            spaceAfter=10,
            textColor=self.colors['dark'],
            alignment=TA_CENTER,
            fontName='Helvetica',
            leading=16
        )

        # Enhanced Table of Contents styles
        custom_styles['TOCTitle'] = ParagraphStyle(
            'TOCTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30,
            spaceBefore=20,
            textColor=self.colors['primary'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=28
        )

        # Section headers with proper hierarchy
        custom_styles['SectionHeader'] = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            spaceBefore=30,
            textColor=colors.white,
            backColor=self.colors['primary'],
            borderWidth=0,
            borderPadding=15,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            leading=22
        )

        custom_styles['SubsectionHeader'] = ParagraphStyle(
            'SubsectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=18,
            textColor=self.colors['secondary'],
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=self.colors['secondary'],
            borderPadding=8,
            leftIndent=0,
            leading=17
        )

        custom_styles['SubSubsectionHeader'] = ParagraphStyle(
            'SubSubsectionHeader',
            parent=styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=15,
            textColor=self.colors['dark'],
            fontName='Helvetica-Bold',
            leftIndent=15,
            leading=15
        )

        # Enhanced content styles
        custom_styles['ExecutiveSummary'] = ParagraphStyle(
            'ExecutiveSummary',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.colors['dark'],
            spaceAfter=25,
            spaceBefore=15,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            backColor=self.colors['light_gray'],
            borderWidth=1,
            borderColor=self.colors['border'],
            borderPadding=20,
            leading=15
        )

        # Risk level styles with proper colors
        custom_styles['HighRisk'] = ParagraphStyle(
            'HighRisk',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.colors['danger'],
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )

        custom_styles['MediumRisk'] = ParagraphStyle(
            'MediumRisk',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.colors['warning'],
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )

        custom_styles['LowRisk'] = ParagraphStyle(
            'LowRisk',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.colors['success'],
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )

        # Enhanced list and content styles
        custom_styles['BulletPoint'] = ParagraphStyle(
            'BulletPoint',
            parent=styles['Normal'],
            fontSize=10,
            leftIndent=25,
            spaceAfter=6,
            textColor=self.colors['dark'],
            fontName='Helvetica',
            leading=13
        )

        custom_styles['NumberedList'] = ParagraphStyle(
            'NumberedList',
            parent=styles['Normal'],
            fontSize=10,
            leftIndent=25,
            spaceAfter=8,
            textColor=self.colors['dark'],
            fontName='Helvetica',
            leading=13
        )

        custom_styles['InfoText'] = ParagraphStyle(
            'InfoText',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.colors['dark'],
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            leading=13
        )

        # Enhanced impact and recommendation styles
        custom_styles['Impact'] = ParagraphStyle(
            'Impact',
            parent=styles['Normal'],
            fontSize=9,
            textColor=self.colors['accent'],
            fontName='Helvetica-Oblique',
            leftIndent=35,
            spaceAfter=4,
            leading=12,
            borderWidth=0.5,
            borderColor=self.colors['accent'],
            borderPadding=5,
            backColor=colors.Color(1, 0.98, 0.98)  # Very light red background
        )

        custom_styles['Recommendation'] = ParagraphStyle(
            'Recommendation',
            parent=styles['Normal'],
            fontSize=9,
            textColor=self.colors['dark'],
            fontName='Helvetica-Bold',
            leftIndent=35,
            spaceAfter=10,
            leading=12,
            borderWidth=0.5,
            borderColor=self.colors['success'],
            borderPadding=5,
            backColor=colors.Color(0.98, 1, 0.98)  # Very light green background
        )

        # Footer styles
        custom_styles['Footer'] = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=self.colors['medium_gray'],
            alignment=TA_CENTER,
            fontName='Helvetica',
            spaceBefore=30
        )

        custom_styles['Confidential'] = ParagraphStyle(
            'Confidential',
            parent=styles['Normal'],
            fontSize=8,
            textColor=self.colors['medium_gray'],
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        )

        return custom_styles

    def _create_header_footer(self, canvas, doc, is_cover=False):
        """Enhanced header and footer with improved formatting"""
        if is_cover:
            return

        canvas.saveState()

        # Add subtle watermark
        if self.company_name:
            canvas.setFont('Helvetica-Bold', 50)
            canvas.setFillColor(self.colors['watermark'])
            canvas.rotate(45)
            text_width = canvas.stringWidth(self.company_name, 'Helvetica-Bold', 50)
            canvas.drawString(250 - text_width / 2, -80, self.company_name)
            canvas.rotate(-45)

        # Enhanced header
        canvas.setStrokeColor(self.colors['primary'])
        canvas.setLineWidth(3)
        canvas.line(doc.leftMargin, doc.height + doc.topMargin - 15,
                    doc.width + doc.rightMargin, doc.height + doc.topMargin - 15)

        canvas.setFont('Helvetica-Bold', 13)
        canvas.setFillColor(self.colors['primary'])
        canvas.drawString(doc.leftMargin, doc.height + doc.topMargin - 35,
                          "Security Analysis Report")

        canvas.drawRightString(doc.width + doc.rightMargin, doc.height + doc.topMargin - 35,
                               self.company_name)

        # Enhanced footer
        canvas.setStrokeColor(self.colors['border'])
        canvas.setLineWidth(1)
        canvas.line(doc.leftMargin, 65, doc.width + doc.rightMargin, 65)

        # Confidentiality notice
        canvas.setFont('Helvetica-Oblique', 8)
        canvas.setFillColor(self.colors['medium_gray'])
        confidential_text = "CONFIDENTIAL - This report contains sensitive security information"
        text_width = canvas.stringWidth(confidential_text, 'Helvetica-Oblique', 8)
        canvas.drawString((doc.width + doc.leftMargin + doc.rightMargin - text_width) / 2, 50, confidential_text)

        # Date and page number
        canvas.setFont('Helvetica', 9)
        canvas.drawString(doc.leftMargin, 35,
                          f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        canvas.drawRightString(doc.width + doc.rightMargin, 35,
                               f"Page {canvas.getPageNumber()}")

        # Version info
        version_text = "Report Version 2.0"
        version_width = canvas.stringWidth(version_text, 'Helvetica', 9)
        canvas.drawString((doc.width + doc.leftMargin + doc.rightMargin - version_width) / 2, 20, version_text)

        canvas.restoreState()

    def _create_cover_page(self, data):
        """Create enhanced professional cover page"""
        story = []

        # Add space from top
        story.append(Spacer(1, 100))

        # Main title
        story.append(Paragraph("SECURITY ANALYSIS<br/>REPORT", self.custom_styles['CoverTitle']))
        story.append(Spacer(1, 40))

        # Subtitle
        story.append(Paragraph("HTTP Security Headers Assessment", self.custom_styles['CoverSubtitle']))
        story.append(Spacer(1, 50))

        # Enhanced target information box
        target_info = f"""
        <b>Target URL:</b><br/>
        <font size="14">{data['url']}</font><br/><br/>
        <b>Scan Date:</b><br/>
        {self._format_timestamp(data['timestamp'])}<br/><br/>
        <b>Overall Security Score:</b><br/>
        <font color="rgb({int(self._get_score_color(data['security_score']).red * 255)},{int(self._get_score_color(data['security_score']).green * 255)},{int(self._get_score_color(data['security_score']).blue * 255)})" size="16">
        <b>{data['security_score']}/100</b>
        </font><br/><br/>
        <b>Risk Level:</b><br/>
        <font color="rgb({int(self._get_risk_badge_color(data['risk_level']).red * 255)},{int(self._get_risk_badge_color(data['risk_level']).green * 255)},{int(self._get_risk_badge_color(data['risk_level']).blue * 255)})" size="16">
        <b>{self._get_risk_icon(data['risk_level'])} {data['risk_level']}</b>
        </font>
        """

        # Create enhanced info box
        story.append(KeepTogether([
            HRFlowable(width="70%", thickness=2, color=self.colors['primary']),
            Spacer(1, 25),
            Paragraph(target_info, self.custom_styles['CoverInfo']),
            Spacer(1, 25),
            HRFlowable(width="70%", thickness=2, color=self.colors['primary'])
        ]))

        story.append(Spacer(1, 120))

        # Prepared by section
        story.append(Paragraph(f"<b>Prepared by:</b><br/>{self.company_name}", self.custom_styles['CoverInfo']))
        story.append(Spacer(1, 30))

        # Enhanced confidentiality notice
        conf_notice = """
        <b>CONFIDENTIAL</b><br/><br/>
        This report contains sensitive security information and should be treated as confidential.<br/>
        Distribution should be limited to authorized personnel only.
        """
        story.append(Paragraph(conf_notice, self.custom_styles['Confidential']))

        story.append(PageBreak())
        return story

    def _create_table_of_contents(self):
        """Create enhanced table of contents with proper formatting"""
        story = []
        story.append(Paragraph("Table of Contents", self.custom_styles['TOCTitle']))
        story.append(Spacer(1, 30))

        # Add a placeholder paragraph that will be replaced by the TOC
        story.append(Paragraph("0Placeholder for table of contents", self.custom_styles['InfoText']))
        story.append(self.toc)

        story.append(PageBreak())
        return story

    def _get_next_section_number(self):
        """Get the next section number with proper formatting"""
        self.section_counter += 1
        return self.section_counter

    def _format_timestamp(self, timestamp):
        """Format timestamp to readable format"""
        try:
            from datetime import datetime
            if timestamp.endswith('Z'):
                scan_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                scan_date = datetime.fromisoformat(timestamp)
            return scan_date.strftime('%B %d, %Y at %I:%M %p UTC')
        except:
            return timestamp

    def _get_risk_badge_color(self, risk_level):
        """Return color for risk level badge"""
        risk_colors = {
            'Low': self.colors['success'],
            'Medium': self.colors['warning'],
            'High': self.colors['danger'],
            'Critical': self.colors['accent']
        }
        return risk_colors.get(risk_level, self.colors['medium_gray'])

    def _get_risk_icon(self, risk_level):
        """Return appropriate icon for risk level"""
        icons = {
            'Low': '🟢',
            'Medium': '🟠',
            'High': '🔴',
            'Critical': '⚫'
        }
        return icons.get(risk_level, '⚪')

    def _create_enhanced_summary_table(self, data):
        """Create enhanced summary table with better styling"""
        formatted_date = self._format_timestamp(data['timestamp'])

        table_data = [
            ['Property', 'Value'],
            ['Target URL', data['url']],
            ['Scan Date', formatted_date],
            ['Security Score', f"{data['security_score']}/100"],
            ['Risk Level', f"{self._get_risk_icon(data['risk_level'])} {data['risk_level']}"],
            ['Total Findings', str(len(data.get('recommendations', [])))],
        ]

        table = Table(table_data, colWidths=[2.8 * inch, 3.7 * inch])
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),

            # Alternating colors
            ('BACKGROUND', (0, 2), (-1, 2), self.colors['light_gray']),
            ('BACKGROUND', (0, 4), (-1, 4), self.colors['light_gray']),

            # Special styling for score and risk
            ('TEXTCOLOR', (1, 3), (1, 3), self._get_score_color(data['security_score'])),
            ('FONTNAME', (1, 3), (1, 3), 'Helvetica-Bold'),
            ('TEXTCOLOR', (1, 4), (1, 4), self._get_risk_badge_color(data['risk_level'])),
            ('FONTNAME', (1, 4), (1, 4), 'Helvetica-Bold'),

            # Borders and padding
            ('GRID', (0, 0), (-1, -1), 1.5, self.colors['border']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 18),
            ('RIGHTPADDING', (0, 0), (-1, -1), 18),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))

        return table

    def _create_enhanced_score_breakdown_table(self, score_breakdown):
        """Enhanced score breakdown table with improved formatting"""
        table_data = [
            ['Security Category', 'Score', 'Rating', 'Status']
        ]

        for category, score in score_breakdown.items():
            if score >= 70:
                status = 'Good'
                status_symbol = '✓'
            elif score >= 40:
                status = 'Fair'
                status_symbol = '⚠'
            else:
                status = 'Poor'
                status_symbol = '✗'

            formatted_category = category.replace('_', ' ').title()
            score_display = f'{score}/100'

            table_data.append([formatted_category, score_display, status, status_symbol])

        table = Table(table_data, colWidths=[2.8 * inch, 1.3 * inch, 1.1 * inch, 0.8 * inch])

        # Base styling
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['secondary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Data styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),

            # Borders and spacing
            ('GRID', (0, 0), (-1, -1), 1.5, self.colors['border']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),

            # Alternating row colors
            ('BACKGROUND', (0, 2), (-1, 2), self.colors['light_gray']),
            ('BACKGROUND', (0, 4), (-1, 4), self.colors['light_gray']),
        ]))

        # Apply individual row coloring
        for i, (category, score) in enumerate(score_breakdown.items(), 1):
            score_color = self._get_score_color(score)
            table.setStyle(TableStyle([
                ('TEXTCOLOR', (1, i), (1, i), score_color),
                ('TEXTCOLOR', (2, i), (2, i), score_color),
                ('TEXTCOLOR', (3, i), (3, i), score_color),
                ('FONTNAME', (1, i), (3, i), 'Helvetica-Bold'),
            ]))

        return table

    def _create_priority_findings_table(self, recommendations):
        """Create enhanced priority findings table"""
        high_priority = recommendations[:5]

        table_data = [
            ['Priority', 'Finding', 'Severity', 'Action Required']
        ]

        for i, rec in enumerate(high_priority, 1):
            severity = "HIGH" if i <= 3 else "MEDIUM"
            finding = rec[:70] + "..." if len(rec) > 70 else rec
            action = "Immediate" if severity == "HIGH" else "Soon"

            table_data.append([f"#{i}", finding, severity, action])

        table = Table(table_data, colWidths=[0.6 * inch, 3.8 * inch, 1.1 * inch, 1 * inch])

        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['accent']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),

            # Styling
            ('GRID', (0, 0), (-1, -1), 1.5, self.colors['border']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        # Color-code severity
        for i in range(1, len(high_priority) + 1):
            severity_color = self.colors['danger'] if i <= 3 else self.colors['warning']
            table.setStyle(TableStyle([
                ('TEXTCOLOR', (2, i), (2, i), severity_color),
                ('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'),
            ]))

        return table

    def _create_security_gauge(self, score):
        """Create enhanced security gauge visualization"""
        try:
            drawing = Drawing(350, 180)

            # Create gauge background
            gauge_center_x, gauge_center_y = 175, 90
            gauge_radius = 70

            # Background arc
            from reportlab.graphics.shapes import Circle, String
            background = Circle(gauge_center_x, gauge_center_y, gauge_radius,
                                fillColor=self.colors['light_gray'],
                                strokeColor=self.colors['border'],
                                strokeWidth=2)
            drawing.add(background)

            # Score indicator
            score_color = self._get_score_color(score)
            score_radius = int(gauge_radius * 0.8 * (score / 100))

            if score_radius > 0:
                score_circle = Circle(gauge_center_x, gauge_center_y, score_radius,
                                      fillColor=score_color,
                                      strokeColor=score_color,
                                      strokeWidth=2)
                drawing.add(score_circle)

            # Score text in center
            score_text = String(gauge_center_x, gauge_center_y - 10, f"{score}/100",
                                fontSize=18, fontName="Helvetica-Bold", textAnchor="middle",
                                fillColor=self.colors['dark'])
            drawing.add(score_text)

            # Add scale labels
            labels = [
                ("0", gauge_center_x - 80, gauge_center_y),
                ("50", gauge_center_x, gauge_center_y + 85),
                ("100", gauge_center_x + 80, gauge_center_y)
            ]

            for label, x, y in labels:
                label_text = String(x, y, label, fontSize=11, fontName="Helvetica",
                                    textAnchor="middle", fillColor=self.colors['medium_gray'])
                drawing.add(label_text)

            return drawing

        except Exception as e:
            logger.warning(f"Gauge creation failed: {e}. Using text representation.")
            return self._create_text_gauge(score)

    def _create_text_gauge(self, score):
        """Create enhanced text-based gauge representation"""
        gauge_length = 40
        filled_length = int((score / 100) * gauge_length)
        empty_length = gauge_length - filled_length

        color = self._get_score_color(score)
        color_rgb = f"rgb({int(color.red * 255)},{int(color.green * 255)},{int(color.blue * 255)})"

        gauge_text = f"""
        <b>Security Score: {score}/100</b><br/><br/>
        <font color='{color_rgb}'>{'█' * filled_length}</font>{'░' * empty_length}<br/>
        <font size="8">0%{' ' * 35}100%</font>
        """

        return Paragraph(gauge_text, self.custom_styles['InfoText'])

    def _create_score_comparison_chart(self, score_breakdown):
        """Create enhanced score comparison visualization"""
        if not CHARTS_AVAILABLE:
            return self._create_fallback_chart(score_breakdown)

        try:
            drawing = Drawing(450, 250)
            chart = VerticalBarChart()

            # Chart positioning and sizing
            chart.x = 60
            chart.y = 60
            chart.height = 150
            chart.width = 330

            # Data preparation
            categories = list(score_breakdown.keys())
            scores = list(score_breakdown.values())

            chart.data = [scores]
            chart.categoryAxis.categoryNames = [cat.replace('_', ' ').title() for cat in categories]

            # Enhanced styling
            chart.bars[0].fillColor = self.colors['secondary']
            chart.bars[0].strokeColor = self.colors['primary']
            chart.bars[0].strokeWidth = 1

            chart.valueAxis.valueMin = 0
            chart.valueAxis.valueMax = 100
            chart.valueAxis.valueStep = 20

            chart.categoryAxis.labels.fontSize = 9
            chart.categoryAxis.labels.angle = 0
            chart.categoryAxis.labels.dx = 0
            chart.categoryAxis.labels.dy = -5

            chart.valueAxis.labels.fontSize = 9
            chart.valueAxis.labels.rightPadding = 10

            # Add title
            from reportlab.graphics.shapes import String
            title = String(225, 220, 'Security Category Scores', fontSize=12,
                           fontName='Helvetica-Bold', textAnchor='middle',
                           fillColor=self.colors['primary'])
            drawing.add(title)

            drawing.add(chart)
            return drawing

        except Exception as e:
            logger.warning(f"Chart creation failed: {e}. Using fallback visualization.")
            return self._create_fallback_chart(score_breakdown)

    def _create_fallback_chart(self, score_breakdown):
        """Create enhanced fallback chart visualization"""
        chart_text = "<b>Security Category Performance:</b><br/><br/>"

        for category, score in score_breakdown.items():
            category_name = category.replace('_', ' ').title()
            bar_length = int(score / 5)
            bar = "█" * bar_length + "░" * (20 - bar_length)

            color = self._get_score_color(score)
            color_rgb = f"rgb({int(color.red * 255)},{int(color.green * 255)},{int(color.blue * 255)})"

            chart_text += f"<b>{category_name}:</b><br/>"
            chart_text += f"<font color='{color_rgb}'>{bar}</font> <b>{score}/100</b><br/><br/>"

        return Paragraph(chart_text, self.custom_styles['InfoText'])

    def _format_ai_analysis(self, text):
        """Enhanced AI analysis formatting with better structure"""
        if not text:
            return ""

        # Split into sections and format
        sections = text.split('\n\n')
        formatted_sections = []

        for section in sections:
            lines = section.split('\n')
            formatted_lines = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Format different types of content
                if line.startswith('##'):
                    # Major section header
                    header = line.replace('##', '').strip()
                    formatted_lines.append(
                        f"<b><font size='12' color='rgb({int(self.colors['secondary'].red * 255)},{int(self.colors['secondary'].green * 255)},{int(self.colors['secondary'].blue * 255)})'>{header}</font></b>")
                elif line.endswith(':') and not line.startswith('•') and not line.startswith('*'):
                    # Subheader
                    formatted_lines.append(f"<b>{line}</b>")
                elif line.startswith('•') or line.startswith('*'):
                    # Bullet point
                    bullet_text = line[1:].strip()
                    formatted_lines.append(f"    • {bullet_text}")
                elif re.match(r'^\d+\.\s', line):
                    # Numbered list
                    formatted_lines.append(f"<b>{line}</b>")
                elif '**' in line:
                    # Bold text
                    line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
                    formatted_lines.append(line)
                else:
                    formatted_lines.append(line)

            if formatted_lines:
                formatted_sections.append('<br/>'.join(formatted_lines))

        return '<br/><br/>'.join(formatted_sections)

    def _create_contact_page(self):
        """Create enhanced thank you and contact information page"""
        story = []

        story.append(Spacer(1, 120))

        # Thank you section
        story.append(Paragraph("Thank You", self.custom_styles['SectionHeader']))
        story.append(Spacer(1, 25))

        thank_you_text = f"""
        Thank you for choosing <b>{self.company_name}</b> for your security assessment needs. 
        We are committed to helping organizations strengthen their security posture through 
        comprehensive analysis and actionable recommendations.<br/><br/>

        This automated assessment provides valuable insights into your HTTP security headers 
        configuration. For a more comprehensive security evaluation, we recommend conducting 
        additional penetration testing and manual security reviews.
        """

        story.append(Paragraph(thank_you_text, self.custom_styles['InfoText']))
        story.append(Spacer(1, 40))

        # Contact Information
        story.append(Paragraph("Contact Information", self.custom_styles['SubsectionHeader']))
        story.append(Spacer(1, 20))

        # Create contact info table for better formatting
        contact_data = [
            ['Contact Type', 'Details'],
            ['Technical Support', 'Email: security@cyberheaders.com\nPhone: +1 (555) 123-4567'],
            ['Business Inquiries', 'Email: sales@cyberheaders.com\nPhone: +1 (555) 765-4321'],
            ['Website', 'https://www.cyberheaders.com'],
            ['Address', f'{self.company_name}\n123 Security Boulevard\nCyber City, CC 12345\nUnited States']
        ]

        contact_table = Table(contact_data, colWidths=[2.2 * inch, 3.8 * inch])
        contact_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),

            ('GRID', (0, 0), (-1, -1), 1, self.colors['border']),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),

            ('BACKGROUND', (0, 2), (-1, 2), self.colors['light_gray']),
            ('BACKGROUND', (0, 4), (-1, 4), self.colors['light_gray']),
        ]))

        story.append(contact_table)
        story.append(Spacer(1, 40))

        # Follow-up services
        story.append(Paragraph("Follow-up Services Available", self.custom_styles['SubsectionHeader']))
        story.append(Spacer(1, 15))

        services_text = """
        • <b>Detailed penetration testing</b> - Comprehensive security assessment<br/>
        • <b>Security architecture review</b> - Infrastructure and design analysis<br/>
        • <b>Compliance assessments</b> - Regulatory compliance verification<br/>
        • <b>Security training and awareness</b> - Staff education programs<br/>
        • <b>Incident response planning</b> - Emergency response preparation<br/><br/>

        <i>Contact us to discuss how we can further enhance your security posture.</i>
        """

        story.append(Paragraph(services_text, self.custom_styles['InfoText']))

        return story

    def generate_pdf_report(self, data, output_path):
        """Generate comprehensive professional PDF report with enhanced formatting"""
        try:
            # Reset counters
            self.section_counter = 0
            self.toc_entries = []

            # Create document with enhanced margins
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=65,
                leftMargin=65,
                topMargin=90,
                bottomMargin=75,
                title="Security Analysis Report",
                author=self.company_name
            )

            story = []

            # 1. COVER PAGE
            story.extend(self._create_cover_page(data))

            # 2. TABLE OF CONTENTS
            story.extend(self._create_table_of_contents())

            # 3. EXECUTIVE SUMMARY
            section_num = self._get_next_section_number()
            section_title = f"{section_num}. Executive Summary"
            story.append(Paragraph(section_title, self.custom_styles['SectionHeader']))
            self.toc.addEntry(0, section_title, 1)
            story.append(Spacer(1, 20))

            # Enhanced executive summary content
            story.append(Paragraph("Assessment Overview", self.custom_styles['SubsectionHeader']))
            self.toc.addEntry(1, "Assessment Overview", 1)
            story.append(Spacer(1, 10))

            exec_summary = f"""
            Our comprehensive security analysis has evaluated the HTTP security headers implementation 
            for <b>{data['url']}</b>. This automated assessment identified critical security gaps 
            that require immediate attention to protect against common web vulnerabilities.
            """
            story.append(Paragraph(exec_summary, self.custom_styles['InfoText']))
            story.append(Spacer(1, 15))

            # Key findings box
            key_findings = f"""
            <b>Key Findings:</b><br/>
            • Overall Security Score: <b><font color="rgb({int(self._get_score_color(data['security_score']).red * 255)},{int(self._get_score_color(data['security_score']).green * 255)},{int(self._get_score_color(data['security_score']).blue * 255)})">{data['security_score']}/100</font></b><br/>
            • Risk Classification: <b><font color="rgb({int(self._get_risk_badge_color(data['risk_level']).red * 255)},{int(self._get_risk_badge_color(data['risk_level']).green * 255)},{int(self._get_risk_badge_color(data['risk_level']).blue * 255)})">{self._get_risk_icon(data['risk_level'])} {data['risk_level']}</font></b><br/>
            • Total Security Recommendations: <b>{len(data['recommendations'])}</b><br/>
            • High-Priority Actions: <b>{min(5, len(data['recommendations']))}</b>
            """
            story.append(Paragraph(key_findings, self.custom_styles['ExecutiveSummary']))
            story.append(Spacer(1, 15))

            # Business Impact
            story.append(Paragraph("Business Impact", self.custom_styles['SubsectionHeader']))
            self.toc.addEntry(1, "Business Impact", 1)
            story.append(Spacer(1, 10))

            impact_text = """
            The identified vulnerabilities expose your organization to potential security breaches, 
            including cross-site scripting (XSS), clickjacking, and man-in-the-middle attacks. 
            Immediate implementation of our recommendations will significantly strengthen your 
            security posture and protect sensitive user data.
            """
            story.append(Paragraph(impact_text, self.custom_styles['InfoText']))
            story.append(Spacer(1, 15))

            # Next Steps
            story.append(Paragraph("Next Steps", self.custom_styles['SubsectionHeader']))
            self.toc.addEntry(1, "Next Steps", 1)
            story.append(Spacer(1, 10))

            next_steps = """
            We recommend prioritizing the high-risk findings detailed in Section 3 and implementing 
            the security recommendations in order of priority. Our team is available to assist 
            with remediation efforts and ongoing security monitoring.
            """
            story.append(Paragraph(next_steps, self.custom_styles['InfoText']))
            story.append(PageBreak())

            # 4. PRIORITY FINDINGS QUICK REFERENCE
            if data.get('recommendations'):
                section_num = self._get_next_section_number()
                section_title = f"{section_num}. Priority Findings Quick Reference"
                story.append(Paragraph(section_title, self.custom_styles['SectionHeader']))
                self.toc.addEntry(0, section_title, 1)
                story.append(Spacer(1, 15))

                intro_text = "The following table summarizes the highest priority security findings that require immediate attention:"
                story.append(Paragraph(intro_text, self.custom_styles['InfoText']))
                story.append(Spacer(1, 20))
                story.append(self._create_priority_findings_table(data['recommendations']))
                story.append(Spacer(1, 30))

            # 5. SCAN OVERVIEW & METRICS
            section_num = self._get_next_section_number()
            section_title = f"{section_num}. Scan Overview & Metrics"
            story.append(Paragraph(section_title, self.custom_styles['SectionHeader']))
            self.toc.addEntry(0, section_title, 1)
            story.append(Spacer(1, 20))

            # 5.1 Scan Details
            subsection_title = "5.1 Scan Details"
            story.append(Paragraph(subsection_title, self.custom_styles['SubsectionHeader']))
            self.toc.addEntry(1, subsection_title, 1)
            story.append(Spacer(1, 15))
            story.append(self._create_enhanced_summary_table(data))
            story.append(Spacer(1, 25))

            # 5.2 Security Score Visualization
            subsection_title = "5.2 Security Score Visualization"
            story.append(Paragraph(subsection_title, self.custom_styles['SubsectionHeader']))
            self.toc.addEntry(1, subsection_title, 1)
            story.append(Spacer(1, 15))
            story.append(self._create_security_gauge(data['security_score']))
            story.append(Spacer(1, 25))

            # 5.3 Security Category Analysis
            subsection_title = "5.3 Security Category Analysis"
            story.append(Paragraph(subsection_title, self.custom_styles['SubsectionHeader']))
            self.toc.addEntry(1, subsection_title, 1)
            story.append(Spacer(1, 10))

            analysis_intro = "The following analysis shows performance across different security categories:"
            story.append(Paragraph(analysis_intro, self.custom_styles['InfoText']))
            story.append(Spacer(1, 15))
            story.append(self._create_enhanced_score_breakdown_table(data['score_breakdown']))
            story.append(Spacer(1, 20))
            story.append(self._create_score_comparison_chart(data['score_breakdown']))
            story.append(Spacer(1, 30))

            # 6. DETAILED SECURITY FINDINGS
            section_num = self._get_next_section_number()
            section_title = f"{section_num}. Detailed Security Findings"
            story.append(Paragraph(section_title, self.custom_styles['SectionHeader']))
            self.toc.addEntry(0, section_title, 1)
            story.append(Spacer(1, 20))

            # 6.1 Critical Missing Security Headers
            if data['analysis']['missing_essential']:
                subsection_title = "6.1 Critical Missing Security Headers"
                story.append(Paragraph(subsection_title, self.custom_styles['SubsectionHeader']))
                self.toc.addEntry(1, subsection_title, 1)
                story.append(Spacer(1, 10))

                intro_text = "The following essential security headers are missing and must be implemented immediately:"
                story.append(Paragraph(intro_text, self.custom_styles['InfoText']))
                story.append(Spacer(1, 15))

                for header in data['analysis']['missing_essential']:
                    story.append(Paragraph(f"• <b>{header}</b> - Critical security header not implemented",
                                           self.custom_styles['BulletPoint']))
                    story.append(Paragraph(f"Impact: Missing {header} exposes users to security vulnerabilities",
                                           self.custom_styles['Impact']))
                    story.append(Paragraph(f"Recommendation: Implement {header} with appropriate security policies",
                                           self.custom_styles['Recommendation']))
                    story.append(Spacer(1, 8))

                story.append(Spacer(1, 20))

            # 6.2 Deprecated Security Headers
            if data['analysis']['deprecated']:
                subsection_title = "6.2 Deprecated Security Headers"
                story.append(Paragraph(subsection_title, self.custom_styles['SubsectionHeader']))
                self.toc.addEntry(1, subsection_title, 1)
                story.append(Spacer(1, 10))

                intro_text = "The following deprecated headers should be removed to prevent information disclosure:"
                story.append(Paragraph(intro_text, self.custom_styles['InfoText']))
                story.append(Spacer(1, 15))

                for header in data['analysis']['deprecated']:
                    story.append(Paragraph(f"• <b>{header}</b> - Deprecated header revealing server information",
                                           self.custom_styles['BulletPoint']))
                    story.append(Paragraph(f"Impact: Information disclosure may aid attackers in reconnaissance",
                                           self.custom_styles['Impact']))
                    story.append(Paragraph(f"Recommendation: Remove or replace {header} with modern alternatives",
                                           self.custom_styles['Recommendation']))
                    story.append(Spacer(1, 8))

                story.append(Spacer(1, 20))

            # 6.3 Content Security Policy Vulnerabilities
            if data['analysis']['csp_issues']:
                subsection_title = "6.3 Content Security Policy Vulnerabilities"
                story.append(Paragraph(subsection_title, self.custom_styles['SubsectionHeader']))
                self.toc.addEntry(1, subsection_title, 1)
                story.append(Spacer(1, 10))

                intro_text = "Critical Content Security Policy configuration issues:"
                story.append(Paragraph(intro_text, self.custom_styles['InfoText']))
                story.append(Spacer(1, 15))

                for issue in data['analysis']['csp_issues']:
                    story.append(Paragraph(f"• {issue}", self.custom_styles['BulletPoint']))
                    story.append(Paragraph("Impact: CSP misconfigurations can lead to XSS vulnerabilities",
                                           self.custom_styles['Impact']))
                    story.append(Spacer(1, 8))

                story.append(Spacer(1, 30))

            # 7. SECURITY RECOMMENDATIONS
            section_num = self._get_next_section_number()
            section_title = f"{section_num}. Security Recommendations"
            story.append(Paragraph(section_title, self.custom_styles['SectionHeader']))
            self.toc.addEntry(0, section_title, 1)
            story.append(Spacer(1, 15))

            intro_text = "The following recommendations are prioritized by security impact. Address high-priority items first:"
            story.append(Paragraph(intro_text, self.custom_styles['InfoText']))
            story.append(Spacer(1, 20))

            for i, rec in enumerate(data['recommendations'], 1):
                if i <= 5:
                    priority = "🔴 HIGH"
                    priority_color = self.colors['danger']
                elif i <= 10:
                    priority = "🟠 MEDIUM"
                    priority_color = self.colors['warning']
                else:
                    priority = "🟢 LOW"
                    priority_color = self.colors['success']

                priority_rgb = f"rgb({int(priority_color.red * 255)},{int(priority_color.green * 255)},{int(priority_color.blue * 255)})"

                rec_text = f"<b>{i}.</b> <font color='{priority_rgb}'>{priority}</font> {rec}"
                story.append(Paragraph(rec_text, self.custom_styles['NumberedList']))

            story.append(Spacer(1, 30))

            # 8. EXPERT AI SECURITY ANALYSIS
            if data.get('gemini_analysis'):
                section_num = self._get_next_section_number()
                section_title = f"{section_num}. Expert AI Security Analysis"
                story.append(Paragraph(section_title, self.custom_styles['SectionHeader']))
                self.toc.addEntry(0, section_title, 1)
                story.append(Spacer(1, 15))

                formatted_analysis = self._format_ai_analysis(data['gemini_analysis'])
                story.append(Paragraph(formatted_analysis, self.custom_styles['InfoText']))
                story.append(Spacer(1, 30))

            # 9. METHODOLOGY & DISCLAIMER
            section_num = self._get_next_section_number()
            section_title = f"{section_num}. Methodology & Disclaimer"
            story.append(Paragraph(section_title, self.custom_styles['SectionHeader']))
            self.toc.addEntry(0, section_title, 1)
            story.append(Spacer(1, 20))

            # Assessment Methodology
            story.append(Paragraph("Assessment Methodology", self.custom_styles['SubsectionHeader']))
            self.toc.addEntry(1, "Assessment Methodology", 1)
            story.append(Spacer(1, 10))

            methodology_text = """
            This security assessment was conducted using automated scanning techniques that analyze 
            HTTP response headers for security configurations. Our analysis includes:<br/><br/>

            • Evaluation of essential security headers (HSTS, CSP, X-Frame-Options, etc.)<br/>
            • Detection of deprecated or information-leaking headers<br/>
            • Content Security Policy validation and vulnerability assessment<br/>
            • SSL/TLS configuration analysis<br/>
            • Cookie security evaluation<br/>
            • CORS policy review
            """
            story.append(Paragraph(methodology_text, self.custom_styles['InfoText']))
            story.append(Spacer(1, 20))

            # Limitations & Disclaimer
            story.append(Paragraph("Limitations & Disclaimer", self.custom_styles['SubsectionHeader']))
            self.toc.addEntry(1, "Limitations & Disclaimer", 1)
            story.append(Spacer(1, 10))

            disclaimer_text = """
            This automated assessment provides a comprehensive overview of HTTP security header 
            implementation but does not constitute a complete security audit. For thorough security 
            assurance, we recommend:<br/><br/>

            • Manual penetration testing<br/>
            • Code review and vulnerability assessment<br/>
            • Infrastructure security evaluation<br/>
            • Social engineering assessments<br/><br/>

            <b>Important Notice:</b> This report is confidential and intended solely for the 
            organization that requested the assessment. The findings and recommendations should 
            be implemented by qualified security professionals.
            """
            story.append(Paragraph(disclaimer_text, self.custom_styles['InfoText']))
            story.append(PageBreak())

            # 10. THANK YOU & CONTACT PAGE
            story.extend(self._create_contact_page())

            # Build PDF with enhanced header/footer
            def first_page(canvas, doc):
                self._create_header_footer(canvas, doc, is_cover=True)

            def later_pages(canvas, doc):
                self._create_header_footer(canvas, doc, is_cover=False)

            # Build the document
            doc.build(story, onFirstPage=first_page, onLaterPages=later_pages)

            logger.info(f"Enhanced professional PDF report generated successfully: {output_path}")

        except Exception as e:
            logger.error(f"PDF generation error: {e}")
            raise


# Convenience function for backward compatibility
def generate_pdf_report(data, output_path, company_name="CyberHeaders Security", company_logo=None):
    """Generate enhanced professional PDF report with improved formatting"""
    generator = ProfessionalPDFGenerator(company_name=company_name, company_logo=company_logo)
    generator.generate_pdf_report(data, output_path)

