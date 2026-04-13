# --- CORS Middleware ---
# Define the list of allowed origins (your website URLs)
origins = [
    "https://smart-pen-ai.netlify.app",  # Your FINAL and current URL
    "https://almier-aa6666.netlify.app",
    "https://coruscating-palmier-aa6666.netlify.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Use the specific list of origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
