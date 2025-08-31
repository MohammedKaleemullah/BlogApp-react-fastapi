import os
import time
import urllib.parse
import requests
import json
import re
from uuid import uuid4
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow all origins (for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Setup
# -----------------------------
UPLOAD_DIR = Path("../backend/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "svg"}

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Gemini model
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# Pollinations models priority
# MODELS = ["flux", "turbo"]
MODELS = ["turbo", "flux", "kontext"]


# -----------------------------
# Schemas
# -----------------------------
class PromptRequest(BaseModel):
    user_input: str
    width: int = 1024
    height: int = 1024
    seed: int = 42


class PromptResponse(BaseModel):
    summary: str
    image_file: str
    image_url: str


# -----------------------------
# Helpers
# -----------------------------
def make_pollinations_prompt(user_input: str) -> tuple[str, str]:
    """Use Gemini to generate Pollinations prompt + summary, with fallback."""
    system_instruction = """
    You are a prompt generator for Pollinations.ai.
    The user will describe an image.
    You will:
    1. Create a short 5-word summary.
    2. Expand the description into a Pollinations prompt using this format:
       {sceneDetailed}, {adjective1}, {charactersDetailed}, {adjective2}, 
       {visualStyle1}, {visualStyle2}, {visualStyle3}, {genre}, {artistReference}
    Return in JSON:
    {"summary": "...", "prompt": "..."}
    """

    try:
        response = gemini_model.generate_content(
            system_instruction + f"\nUser description: {user_input}"
        )
        raw_text = response.text.strip()
        print("🔎 Gemini raw output:", raw_text)

        # Try strict JSON parse
        try:
            result = json.loads(raw_text)
            if "summary" in result and "prompt" in result:
                return result["summary"], result["prompt"]
        except json.JSONDecodeError:
            # Try regex to extract JSON block
            match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if match:
                result = json.loads(match.group())
                if "summary" in result and "prompt" in result:
                    return result["summary"], result["prompt"]

        # As fallback, just return raw input
        print("⚠️ Gemini failed to produce JSON, falling back to raw input.")
        return user_input[:50], user_input

    except Exception as e:
        print(f"❌ Gemini error: {e}, falling back to raw input.")
        return user_input[:50], user_input


def generate_image(prompt: str, width: int, height: int, seed: int, retries: int = 5) -> str:
    """Try Pollinations models in order, retrying each if needed."""
    encoded_prompt = urllib.parse.quote(prompt)

    for model in MODELS:
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model={model}&width={width}&height={height}&seed={seed}"
        print(f"🔄 Trying model: {model} -> {url}")

        for attempt in range(retries):
            try:
                resp = requests.get(url, timeout=30)
                if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image"):
                    filename = f"{uuid4().hex}_{model}.webp"
                    filepath = UPLOAD_DIR / filename
                    with open(filepath, "wb") as f:
                        f.write(resp.content)
                    print(f"✅ Success with {model}, saved {filepath}")
                    # Return relative URL
                    return f"/uploads/{filename}"
                else:
                    print(f"⚠️ {model} returned non-image, retrying ({attempt+1}/{retries})...")
            except Exception as e:
                print(f"❌ {model} error: {e}, retrying ({attempt+1}/{retries})...")
            time.sleep(2)

    raise HTTPException(status_code=500, detail="All Pollinations models failed.")


# -----------------------------
# Routes
# -----------------------------
@app.post("/generate", response_model=PromptResponse)
def generate(req: PromptRequest):
    summary, pollinations_prompt = make_pollinations_prompt(req.user_input)

    # Generate image and get relative URL
    image_file = generate_image(
        prompt=pollinations_prompt,
        width=req.width,
        height=req.height,
        seed=req.seed
    )

    return PromptResponse(
        summary=summary,
        image_file=image_file,  # now /uploads/xxxx.webp
        image_url=image_file    # optional: use same relative URL
    )


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload an image and store it in /uploads."""
    if not file.filename or "." not in file.filename:
        raise HTTPException(status_code=400, detail="Invalid file")

    file_extension = file.filename.rsplit(".", 1)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type")

    unique_filename = f"{uuid4()}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return JSONResponse(content={"url": f"/uploads/{unique_filename}"})


# -----------------------------
# Run (only if script run directly)
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)
