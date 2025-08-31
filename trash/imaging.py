import requests
import time

MODELS = ["flux", "turbo", "kontext"]

def generate_image(prompt, width=1024, height=1024, seed=42, retries=2):
    """
    Try Pollinations models in order, retrying each if needed.
    """
    for model in MODELS:
        url = f"https://image.pollinations.ai/prompt/{prompt}?model={model}&width={width}&height={height}&seed={seed}"
        print(f"🔄 Trying model: {model} -> {url}")
        
        for attempt in range(retries):
            try:
                resp = requests.get(url, timeout=30)
                if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image"):
                    filename = f"output_{model}.jpg"
                    with open(filename, "wb") as f:
                        f.write(resp.content)
                    print(f"✅ Success with {model}, saved {filename}")
                    return filename
                else:
                    print(f"⚠️ {model} returned non-image, retrying ({attempt+1}/{retries})...")
            except Exception as e:
                print(f"❌ {model} error: {e}, retrying ({attempt+1}/{retries})...")
            time.sleep(2)
    
    raise RuntimeError("🚨 All Pollinations models failed.")

if __name__ == "__main__":
    generate_image("Charizard flying over a city at sunset, digital art")
