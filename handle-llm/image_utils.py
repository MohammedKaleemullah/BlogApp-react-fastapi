import time
import urllib.parse
import requests
import json
import re
from uuid import uuid4
from fastapi import HTTPException
from config import gemini_model, UPLOAD_DIR, MODELS

def make_pollinations_prompt(user_input: str) -> tuple[str, str]:
    if not gemini_model:
        return user_input[:50], user_input
        
    system_instruction = """
    You are a prompt generator for Pollinations.ai.
    The user will describe an image.
    You will:
    1. Create a short 5-word summary.
    2. Expand the description into a Pollinations prompt using this format:
       {sceneDetailed}, {adjective1}, {charactersDetailed}, {adjective2}, 
       {visualStyle1}, {visualStyle2}, {visualStyle3}, {genre}, {artistReference}
    Strictly Return in JSON:
    {"summary": "...", "prompt": "..."}
    """

    try:
        response = gemini_model.generate_content(
            system_instruction + f"\nUser description: {user_input}"
        )
        raw_text = response.text.strip()
        print("🔎 Gemini raw output:", raw_text)

        try:
            result = json.loads(raw_text)
            if "summary" in result and "prompt" in result:
                return result["summary"], result["prompt"]
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if match:
                result = json.loads(match.group())
                if "summary" in result and "prompt" in result:
                    return result["summary"], result["prompt"]

        print("Gemini failed to produce JSON, falling back to raw input.")
        return user_input[:50], user_input

    except Exception as e:
        print(f"Gemini error: {e}, falling back to raw input.")
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
                    return f"/uploads/{filename}"
                else:
                    print(f"⚠️ {model} returned non-image, retrying ({attempt+1}/{retries})...")
            except Exception as e:
                print(f"❌ {model} error: {e}, retrying ({attempt+1}/{retries})...")
            time.sleep(2)

    raise HTTPException(status_code=500, detail="All Pollinations models failed.")
