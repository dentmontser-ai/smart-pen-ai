import uvicorn
from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
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
# This directory will store the generated files
OUTPUT_DIR = "generated_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Mount the static directory to serve files ---
# Any file in OUTPUT_DIR will be accessible via the /files URL path
app.mount("/files", StaticFiles(directory=OUTPUT_DIR), name="files")

# We need to add the font file to the project and upload it to GitHub
FONT_FILE_PATH = "DejaVuSans.ttf"

# --- AI Placeholder Function ---
def generate_ai_content(service: str, details: str, lang: str) -> str:
    # This is the "A to Z" comprehensive content generation logic we discussed.
    # For now, it's a placeholder, but we will replace it with a real AI chain.
    
    # 1. The Planner (Create an outline)
    outline = f"خطة محتوى شاملة لموضوع '{details}':\n1. مقدمة\n2. تحليل معمق\n3. تطبيقات عملية\n4. خاتمة"
    
    # 2. The Writer (Expand on the outline)
    written_content = f"بناءً على الخطة، هذا هو المحتوى المفصل الذي يغطي الموضوع من كل الجوانب.\nالخدمة المطلوبة: {service}\nاللغة: {lang}"
    
    # 3. The Editor (Review and format)
    final_text = f"--- مستند احترافي من Smart Pen ---\n\n{outline}\n\n{written_content}\n\n--- تم الإنشاء بواسطة Manus AI ---"
    
    return final_text

# --- File Generation Functions ---
def create_docx_file(content: str, filename: str):
    filepath = os.path.join(OUTPUT_DIR, filename)
    document = Document()
    # Here we would apply the elegant template (headers, footers, etc.)
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
    pdf.add_font('DejaVu', '', FONT_FILE_PATH, uni=True)
    pdf.set_font('DejaVu', '', 12)
    pdf.set_right_to_left(True)
    pdf.multi_cell(0, 10, content)
    pdf.output(filepath)
    return filepath

# --- API Endpoint ---
@app.post("/process-order")
async def process_order(
    details: str = Form(...), service: str = Form(...), lang: str = Form(...),
    format: str = Form(...), email: str = Form(...)
):
    print(f"Received new order for: {email}")

    ai_content = generate_ai_content(service, details, lang)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    file_extension = ""
    if "Word (DOCX)" in format:
        file_extension = "docx"
    elif "PDF" in format:
        file_extension = "pdf"
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format.")

    filename = f"order_{timestamp}.{file_extension}"
    
    try:
        if file_extension == "docx":
            file_path = create_docx_file(ai_content, filename)
        elif file_extension == "pdf":
            file_path = create_pdf_file(ai_content, filename)
    except Exception as e:
        print(f"ERROR creating file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create file: {e}")

    # Construct the public download URL
    # IMPORTANT: Replace with your actual Render URL
    base_url = "https://smart-pen-ai.onrender.com" 
    download_url = f"{base_url}/files/{filename}"

    print(f"SUCCESS: File '{filename}' created. Download URL: {download_url}")
    
    return {
        "message": f"تم إنشاء طلبك بنجاح! يمكنك تحميله الآن.",
        "download_url": download_url
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
