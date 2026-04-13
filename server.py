import uvicorn
from fastapi import FastAPI, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import datetime

# --- Import file generation library for Word ---
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- App Initialization ---
app = FastAPI()

# --- CORS Middleware ---
origins = ["https://smart-pen-ai.netlify.app"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- File Storage Setup ---
OUTPUT_DIR = "public"
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount("/files", StaticFiles(directory=OUTPUT_DIR), name="files")

# --- API Endpoint ---
@app.post("/process-order")
async def process_order(details: str = Form(...), format: str = Form(...)):
    print(f"Received new order. Format: {format}")

    if "Word (DOCX)" not in format:
        raise HTTPException(status_code=400, detail="Sorry, only Word (DOCX) files are supported for now.")

    content = f"--- Document from Smart Pen ---\n\nDetails: {details}"
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"order_{timestamp}.docx"
    filepath = os.path.join(OUTPUT_DIR, filename)

    try:
        document = Document()
        document.settings.element.xpath('.//w:bidi')[0].set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '1')
        p = document.add_paragraph(content)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        document.save(filepath)
    except Exception as e:
        print(f"ERROR creating file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    base_url = "https://smart-pen-ai.onrender.com"
    download_url = f"{base_url}/files/{filename}"

    print(f"SUCCESS: File '{filename}' created. URL: {download_url}")
    
    return {
        "message": "Your Word document is ready!",
        "download_url": download_url
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
