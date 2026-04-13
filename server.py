
import uvicorn
from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import datetime
from typing import Optional

# --- Import file generation libraries ---
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF

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

# --- AI Placeholder Function ---
def generate_ai_content(service: str, details: str, lang: str) -> str:
    header = f"--- طلب خدمة: {service} ({lang}) ---"
    details_section = f"تفاصيل الطلب: {details}"
    
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
    document.settings.element.xpath('.//w:bidi')[0].set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '1')
    
    for line in content.split('\n'):
        p = document.add_paragraph(line)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    document.save(filepath)
    return filepath

def create_pdf_file(content: str, filename: str):
    filepath = os.path.join(OUTPUT_DIR, filename)
    pdf = FPDF()
    pdf.add_page()
    # Add a font that supports Arabic. fpdf2 comes with some.
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)
    
    pdf.set_right_to_left(True)
    pdf.multi_cell(0, 10, content)
    pdf.output(filepath)
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

    print(f"SUCCESS: File '{file_path}' created. Ready to be sent to {email}.")
    
    return {
        "message": f"طلبك قيد المعالجة! سيتم إرسال الملف بصيغة {format.split(' ')[0]} إلى بريدك الإلكتروني ({email}) خلال دقائق."
    }

# --- Main execution ---
if __name__ == "__main__":
    print("Starting Smart Pen AI Server...")
    print("Visit http://127.0.0.1:8000/docs for API documentation.")
    uvicorn.run(app, host="127.0.0.1", port=8000)
