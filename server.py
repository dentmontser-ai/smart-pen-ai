

import uvicorn
from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import datetime
from typing import Optional

# --- Import file generation libraries ---
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import arabic_reshaper
from bidi.algorithm import get_display

# --- App Initialization ---
app = FastAPI()

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# --- File Storage Setup ---
OUTPUT_DIR = "generated_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- PDF Font Setup for Arabic ---
# Make sure you have an Arabic font file (e.g., a .ttf file) in the same directory.
# I'll try to find a common one, but you might need to provide one.
try:
    # This font is common on many systems. Replace with your font if needed.
    ARABIC_FONT_NAME = 'Arial'
    pdfmetrics.registerFont(TTFont(ARABIC_FONT_NAME, 'arial.ttf'))
except Exception:
    print("WARNING: Arial font not found. PDF Arabic text might not render correctly. Please add an Arabic .ttf font file.")
    ARABIC_FONT_NAME = 'Helvetica' # Fallback

# --- AI Placeholder Function ---
def generate_ai_content(service: str, details: str, lang: str) -> str:
    header = f"--- طلب خدمة: {service} ({lang}) ---"
    details_section = f"تفاصيل الطلب: {details}"
    
    # Simple logic based on service type
    if "ترجمة" in service:
        content = "هذا هو النص المترجم المطلوب الذي تم إنشاؤه بواسطة الذكاء الاصطناعي بناءً على طلبك."
    elif "تلخيص" in service:
        content = "هذا هو ملخص المحتوى المطلوب. تم تحليل النص الأصلي وتقديم النقاط الرئيسية بشكل موجز وواضح."
    elif "كتابة محتوى" in service:
        content = "هذا هو المحتوى الحصري الذي تم إنشاؤه خصيصًا لك بواسطة نظام Smart Pen الآلي. نأمل أن ينال إعجابك."
    else:
        content = "تم إنشاء هذا المحتوى بواسطة نظام Smart Pen الآلي بناءً على الخدمة المحددة."

    footer = "--- تم الإنشاء بواسطة Manus AI ---"
    return f"{header}\n\n{details_section}\n\n{content}\n\n{footer}"

# --- File Generation Functions ---
def create_txt_file(content: str, filename: str):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath

def create_docx_file(content: str, filename: str):
    filepath = os.path.join(OUTPUT_DIR, filename)
    document = Document()
    # Set document to right-to-left
    document.settings.element.xpath('.//w:bidi')[0].set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '1')
    
    for line in content.split('\n'):
        p = document.add_paragraph(line)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    document.save(filepath)
    return filepath

def create_pdf_file(content: str, filename: str):
    filepath = os.path.join(OUTPUT_DIR, filename)
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    c.setFont(ARABIC_FONT_NAME, 12)
    
    y = height - 70
    lines = content.split('\n')
    for line in lines:
        reshaped_text = arabic_reshaper.reshape(line)
        bidi_text = get_display(reshaped_text)
        
        # This is a simple text wrapper. For production, a more robust library might be better.
        # It splits text into lines to fit the page width.
        max_width = width - 100
        while c.stringWidth(bidi_text) > max_width:
            # Find a good split point (e.g., at a space)
            split_at = -1
            for i in range(len(bidi_text) - 1, 0, -1):
                if bidi_text[i] == ' ':
                    if c.stringWidth(bidi_text[:i]) <= max_width:
                        split_at = i
                        break
            if split_at == -1: # Word is too long, force split
                split_at = int(max_width / (c.stringWidth(bidi_text) / len(bidi_text)))

            line_to_draw = bidi_text[:split_at]
            bidi_text = bidi_text[split_at:].lstrip()
            
            c.drawRightString(width - 50, y, line_to_draw)
            y -= 20
            if y < 50: # New page
                c.showPage()
                c.setFont(ARABIC_FONT_NAME, 12)
                y = height - 70
        
        c.drawRightString(width - 50, y, bidi_text) # Draw the remaining part
        y -= 20
        if y < 50: # New page
            c.showPage()
            c.setFont(ARABIC_FONT_NAME, 12)
            y = height - 70
            
    c.save()
    return filepath

# --- API Endpoint ---
@app.post("/process-order")
async def process_order(
    details: str = Form(...), service: str = Form(...), lang: str = Form(...),
    format: str = Form(...), email: str = Form(...), attachment: Optional[UploadFile] = File(None)
):
    print(f"Received new order for: {email} | Service: {service}, Format: {format}")

    ai_content = generate_ai_content(service, details, lang)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"order_{timestamp}_{email.split('@')[0]}"
    
    try:
        if "Word (DOCX)" in format:
            file_path = create_docx_file(ai_content, f"{base_filename}.docx")
        elif "PDF" in format:
            file_path = create_pdf_file(ai_content, f"{base_filename}.pdf")
        elif "Plain Text (TXT)" in format:
            file_path = create_txt_file(ai_content, f"{base_filename}.txt")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format.")
    except Exception as e:
        print(f"ERROR creating file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create file: {e}")

    if attachment:
        attachment_path = os.path.join(OUTPUT_DIR, f"att_{timestamp}_{attachment.filename}")
        with open(attachment_path, "wb") as buffer:
            buffer.write(await attachment.read())
        print(f"Attachment saved: {attachment_path}")

    # In a real app, you would now trigger an email to be sent to `email` with `file_path` as an attachment.
    print(f"SUCCESS: File '{file_path}' created. Ready to be sent to {email}.")
    
    return {
        "message": f"طلبك قيد المعالجة! سيتم إرسال الملف بصيغة {format.split(' ')[0]} إلى بريدك الإلكتروني ({email}) خلال دقائق."
    }

# --- Main execution ---
if __name__ == "__main__":
    print("Starting Smart Pen AI Server...")
    print("Visit http://127.0.0.1:8000/docs for API documentation.")
    uvicorn.run(app, host="127.0.0.1", port=8000)
