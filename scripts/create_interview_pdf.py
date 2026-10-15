import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, HRFlowable
)

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "NaturalSQL — 100 Comprehensive Technical Interview Questions & Answers")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Footer
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 45, letter[0] - 54, 45)
        self.drawString(54, 32, "Confidential — Prepared for Technical & System Design Interviews")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 32, page_str)
        self.restoreState()


def build_pdf(filename="NaturalSQL_Interview_Handbook.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0f172a"),
        alignment=1, # Center
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#475569"),
        alignment=1,
        spaceAfter=25
    )

    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#ffffff"),
        spaceAfter=0
    )

    q_style = ParagraphStyle(
        'QuestionStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1e3a8a"), # Dark Blue
        spaceBefore=8,
        spaceAfter=3
    )

    ans_style = ParagraphStyle(
        'AnswerStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )

    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#64748b"),
        alignment=1
    )

    story = []

    # Title Banner
    story.append(Paragraph("NaturalSQL Technical Interview Handbook", title_style))
    story.append(Paragraph("100 Comprehensive Questions & Detailed Answers (Foundations, Architecture, LLM, Database, Security & Scaling)", subtitle_style))
    
    # Meta Info Card
    meta_data = [
        [Paragraph("<b>Project:</b> NaturalSQL (Natural Language to SQL Engine)", meta_style),
         Paragraph("<b>Tech Stack:</b> FastAPI, Streamlit, SQLite, Gemini 1.5, Pandas", meta_style)],
        [Paragraph("<b>Target Roles:</b> Full-Stack AI Engineer, Backend Dev, Data Engineer", meta_style),
         Paragraph("<b>Live App:</b> https://naturalsql.streamlit.app", meta_style)]
    ]
    t = Table(meta_data, colWidths=[250, 250])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#e2e8f0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # Helper function to add a category header
    def add_category(title, color="#1e40af"):
        p = Paragraph(f"<b>{title}</b>", section_header_style)
        tbl = Table([[p]], colWidths=[letter[0] - 108])
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(color)),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(Spacer(1, 10))
        story.append(tbl)
        story.append(Spacer(1, 8))

    def add_qa(q_num, question, answer):
        q_p = Paragraph(f"<b>Q{q_num}: {question}</b>", q_style)
        a_p = Paragraph(answer, ans_style)
        story.append(KeepTogether([q_p, a_p]))

    # Import questions dataset
    from interview_data import CATEGORIES
    
    q_counter = 1
    for cat in CATEGORIES:
        add_category(cat['title'], cat.get('color', '#1e40af'))
        for q, a in cat['questions']:
            add_qa(q_counter, q, a)
            q_counter += 1

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF built successfully: {filename} with {q_counter - 1} questions!")

if __name__ == '__main__':
    build_pdf()
