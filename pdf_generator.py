from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

def generate_medical_report_pdf(conversation_text, medical_report, patient_name=None, doctor_name=None):
    """
    Generate a professional medical report PDF from conversation and analysis
    """
    try:
        # Create reports directory if it doesn't exist
        reports_dir = "reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"medical_report_{timestamp}.pdf"
        filepath = os.path.join(reports_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=A4, 
                              rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY
        )
        
        # Title
        title = Paragraph("MEDICAL CONSULTATION REPORT", title_style)
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Header information table
        current_date = datetime.now().strftime("%B %d, %Y")
        current_time = datetime.now().strftime("%I:%M %p")
        
        header_data = [
            ['Report Date:', current_date, 'Report Time:', current_time],
            ['Patient Name:', patient_name or 'Not Specified', 'Doctor Name:', doctor_name or 'Not Specified'],
            ['Report ID:', f'RPT-{timestamp}', 'Status:', 'Computer Generated']
        ]
        
        header_table = Table(header_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 20))
        
        # Conversation Transcript Section
        elements.append(Paragraph("CONVERSATION TRANSCRIPT", header_style))
        elements.append(Paragraph(conversation_text, normal_style))
        elements.append(Spacer(1, 20))
        
        # Medical Analysis Section
        elements.append(Paragraph("MEDICAL ANALYSIS & PRESCRIPTION", header_style))
        
        # Parse and format the medical report
        formatted_report = format_medical_report(medical_report, normal_style, header_style)
        elements.extend(formatted_report)
        
        # Add disclaimer
        elements.append(Spacer(1, 30))
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.red,
            alignment=TA_CENTER,
            borderWidth=1,
            borderColor=colors.red,
            borderPadding=10
        )
        
        disclaimer_text = """
        <b>IMPORTANT DISCLAIMER:</b><br/>
        This report is computer-generated based on conversation analysis using AI technology. 
        It should NOT be considered as a substitute for professional medical advice, diagnosis, or treatment. 
        Please consult with a qualified healthcare provider for proper medical evaluation and treatment decisions.
        All prescriptions and recommendations must be verified by a licensed medical professional.
        """
        
        elements.append(Paragraph(disclaimer_text, disclaimer_style))
        
        # Build PDF
        doc.build(elements)
        logger.info(f"PDF report generated successfully: {filepath}")
        
        return filepath
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        raise Exception(f"Failed to generate PDF report: {str(e)}")

def format_medical_report(report_text, normal_style, header_style):
    """
    Format the medical report text into structured PDF elements
    """
    elements = []
    
    # Split the report into sections
    lines = report_text.split('\n')
    current_section = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line is a header (starts with ## or **header:**)
        if line.startswith('##') or (line.startswith('**') and line.endswith(':**')):
            # Add previous section content
            if current_section:
                section_text = '\n'.join(current_section)
                if section_text.strip():
                    elements.append(Paragraph(section_text, normal_style))
                current_section = []
            
            # Add header
            header_text = line.replace('##', '').replace('**', '').replace(':', '').strip()
            elements.append(Paragraph(header_text, header_style))
            
        else:
            current_section.append(line)
    
    # Add remaining content
    if current_section:
        section_text = '\n'.join(current_section)
        if section_text.strip():
            elements.append(Paragraph(section_text, normal_style))
    
    return elements

def cleanup_old_reports(max_age_hours=24):
    """
    Clean up old report files to prevent disk space issues
    """
    try:
        reports_dir = "reports"
        if not os.path.exists(reports_dir):
            return
        
        current_time = datetime.now().timestamp()
        max_age_seconds = max_age_hours * 3600
        
        for filename in os.listdir(reports_dir):
            filepath = os.path.join(reports_dir, filename)
            if os.path.isfile(filepath) and filename.endswith('.pdf'):
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > max_age_seconds:
                    os.remove(filepath)
                    logger.info(f"Cleaned up old report: {filename}")
                    
    except Exception as e:
        logger.warning(f"Error cleaning up old reports: {e}")
