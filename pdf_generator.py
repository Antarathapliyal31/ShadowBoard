from fpdf import FPDF
from datetime import datetime

def generate_strategy_brief_pdf(question, moderator_text, session_id):
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 20, "Shadow Board", ln=True, align="C")
    
    # Subtitle
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, "Strategy Brief", ln=True, align="C")
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%B %d, %Y')}", ln=True, align="C")
    
    pdf.ln(10)
    
    # Question
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Strategic Question:", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, question)
    
    pdf.ln(5)
    
    # Moderator Brief
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Board Recommendation:", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, moderator_text)
    
    # Footer
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 10, "Shadow Board by Agent Quorum | Powered by AIRIA", ln=True, align="C")
    
    # Save
    filepath = f"reports/strategy_brief_{session_id}.pdf"
    import os
    os.makedirs("reports", exist_ok=True)
    pdf.output(filepath)
    
    return filepath