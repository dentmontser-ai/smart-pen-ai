import uvicorn
from fastapi import FastAPI, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import datetime

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
# Create a directory named 'public' to store files.
# We will serve this directory as a static folder.
OUTPUT_DIR = "public"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Mount the static directory ---
# Any file in 'public' will be accessible from the root URL.
# e.g., https://smart-pen-ai.onrender.com/order_123.pdf
app.mount("/", StaticFiles(directory=OUTPUT_DIR), name="public")

# --- AI Placeholder Function ---
def generate_ai_content(service: str, details: str) -> str:
    return f"--- مستند احترافي من Smart Pen ---\n\nالخدمة المطلوبة: {service}\n\nالتفاصيل: {details}\n\n--- تم الإنشاء بواسطة Manus AI ---"

# --- File Generation Functions ---
def create_file(content: str, filename: str, format_type: str):
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    if format_type == "docx":
        document = Document()
        document.settings.element.xpath('.//w:bidi')[0].set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '1')
        p = document.add_paragraph(content)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        document.save(filepath)
    elif format_type == "pdf":
        # Check if the font file exists before proceeding
        font_path = "DejaVuSans.ttf"
        if not os.path.exists(font_path):
            raise FileNotFoundError("Font file 'DejaVuSans.ttf' not found. Please upload it to the repository.")
            
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('DejaVu', '', font_path, uni=True)
        pdf.set_font('DejaVu', '', 12)
        pdf.set_right_to_left(True)
        pdf.multi_cell(0, 10, content)
        pdf.output(filepath)
    
    return filepath

# --- API Endpoint ---
@app.post("/process-order")
async def process_order(
    details: str = Form(...), service: str = Form(...), format: str = Form(...)
):
    print(f"Received new order. Service: {service}, Format: {format}")

    ai_content = generate_ai_content(service, details)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    file_extension = "docx" if "Word" in format else "pdf"
    filename = f"order_{timestamp}.{file_extension}"
    
    try:
        create_file(ai_content, filename, file_extension)
    except Exception as e:
        print(f"ERROR creating file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    # Construct the public download URL
    base_url = "https://smart-pen-ai.onrender.com" 
    download_url = f"{base_url}/{filename}"

    print(f"SUCCESS: File '{filename}' created. URL: {download_url}")
    
    return {
        "message": "تم إنشاء طلبك بنجاح! يمكنك تحميله الآن.",
        "download_url": download_url
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
