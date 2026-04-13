import uvicorn
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"],
)

@app.post("/process-order")
async def process_order(
    details: str = Form(...), 
    service: str = Form(...), 
    lang: str = Form(...),
    format: str = Form(...), 
    email: str = Form(...)
):
    print(f"SUCCESS: Received order for {email}. Service: {service}")
    # نحن لا ننشئ ملفًا الآن، فقط نؤكد استلام الطلب.
    return {
        "message": f"تم استلام طلبك بنجاح! (الخادم يعمل الآن)"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
