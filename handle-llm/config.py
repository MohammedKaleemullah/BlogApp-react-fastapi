import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

UPLOAD_DIR = Path("../backend/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "svg"}

try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
    print("✅ Gemini configured for image generation")
except Exception as e:
    print(f"⚠️ Gemini image generation setup failed: {e}")
    gemini_model = None

MODELS = ["turbo", "flux", "kontext"]

def get_database_url():
    return f"postgresql+psycopg2://{os.getenv('db_user')}:{os.getenv('db_password')}@{os.getenv('db_host')}:{os.getenv('db_port')}/{os.getenv('db_database')}"
