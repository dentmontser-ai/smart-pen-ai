import uvicorn
from fastapi import FastAPI, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import datetime

# --- Import file generation library for Word ---
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

app = FastAPI()

# --- CORS Middleware ---
# السماح بجميع النطاقات مؤقتاً لضمان عمل الاتصال من أي رابط Netlify
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- File Storage Setup ---
OUTPUT_DIR = "public"
os.makedirs(OUTPUT_DIR, exist_ok=True)
# إتاحة المجلد للتحميل المباشر عبر المسار /files/
app.mount("/files", StaticFiles(directory=OUTPUT_DIR), name="files")

@app.post("/process-order")
async def process_order(
    details: str = Form(...), 
    service: str = Form("غير محدد"), 
    lang: str = Form("عربي"), 
    format: str = Form("Word (DOCX)"), 
    email: str = Form(...)
):
    print(f"Received new order for: {email}")

    # محتوى افتراضي شامل كما طلب المستخدم
    ai_content = f"""
تقرير شامل: {service}
الموضوع: {details}
اللغة: {lang}
--------------------------------------------------
هذا المستند تم إنشاؤه تلقائياً بواسطة Smart Pen AI ليغطي الموضوع من الألف إلى الياء.

1. المقدمة:
يعتبر موضوع {details} من المواضيع الحيوية والهامة في الوقت الراهن...

2. التحليل العميق:
عند النظر في جوانب {details}، نجد أن هناك أبعاداً متعددة تشمل...

3. التطبيقات العملية:
يمكن تطبيق المفاهيم المتعلقة بـ {details} في مجالات عدة منها...

4. الخاتمة والتوصيات:
في الختام، يوصى بضرورة الاهتمام بـ {details} لضمان أفضل النتائج...

--------------------------------------------------
تم الإنشاء بواسطة Smart Pen - شريكك الموثوق.
"""
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"order_{timestamp}.docx"
    filepath = os.path.join(OUTPUT_DIR, filename)

    try:
        document = Document()
        # دعم الكتابة من اليمين لليسار
        document.settings.element.xpath('.//w:bidi')[0].set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '1')
        
        for line in ai_content.split('\n'):
            p = document.add_paragraph(line)
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            
        document.save(filepath)
    except Exception as e:
        print(f"ERROR creating file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    # ملاحظة: يجب تغيير هذا الرابط ليتناسب مع رابط Render الفعلي الخاص بك
    # سيتم إرشاد المستخدم لتغييره بعد النشر
    base_url = "https://smart-pen-ai.onrender.com" 
    download_url = f"{base_url}/files/{filename}"

    print(f"SUCCESS: File '{filename}' created. URL: {download_url}")
    
    return {
        "message": "تم إنشاء مستند Word الخاص بك بنجاح! يمكنك تحميله الآن.",
        "download_url": download_url
    }

@app.get("/")
def read_root():
    return {"status": "Server is running!", "message": "Smart Pen AI Backend is Live"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
