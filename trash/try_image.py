# import asyncio
# import os
# import requests
# from runware import Runware, IImageInference
# from dotenv import load_dotenv

# # Load your API key from .env
# load_dotenv()
# api_key = os.getenv("RUNWARE_API_KEY")
# if not api_key:
#     raise ValueError("Please set RUNWARE_API_KEY in your .env file")

# async def main():
#     # Initialize and connect the SDK
#     runware = Runware(api_key=api_key)
#     await runware.connect()
#     prompt = "Sung Jinwoo from Solo Leveling, highly detailed, intricate, sharp focus, artstation, concept art, digital painting, fantasy art, trending on artstation, by Magali Villeneuve and Greg Rutkowski and Alphonse Mucha"
#     # Build the image generation request
#     request = IImageInference(
#         positivePrompt=prompt,
#         model="runware:97@2",         # Example model ID
#         numberResults=1,              # Generate 2 images
#         width=512,
#         height=512,
#         steps=30,
#         CFGScale=7.0
#     )

#     # Send the request and await results
#     images = await runware.imageInference(requestImage=request)

#     # Save results locally
#     os.makedirs("outputs", exist_ok=True)
#     for idx, img in enumerate(images, start=1):
#         url = img.imageURL
#         filename = f"outputs/{prompt[:10]}.png"

#         # Download the image
#         response = requests.get(url)
#         if response.status_code == 200:
#             with open(filename, "wb") as f:
#                 f.write(response.content)
#             print(f"✅ Saved {filename}")
#         else:
#             print(f"⚠️ Failed to download {url}")

#     # Disconnect when done
#     await runware.disconnect()

# # Run the async main function
# asyncio.run(main())


# import pollinations

# model = pollinations.Image()  # uses default model "flux"
# image = model("A dog and cat.")        # your prompt goes here
# image.save("my_image.jpeg")           # saves the generated image
# print("Image saved as my_image.jpeg")



import os
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Model
model = genai.GenerativeModel("gemini-1.5-flash")

def make_pollinations_prompt(user_input: str):
    """Generate Pollinations prompt + markdown using Gemini"""
    
    system_instruction = """
    You are a prompt generator for Pollinations.ai.
    The user will describe an image.
    You will:
    1. Create a short 5-word summary.
    2. Expand the description into a Pollinations prompt using this format:
       {sceneDetailed}, {adjective1}, {charactersDetailed}, {adjective2}, 
       {visualStyle1}, {visualStyle2}, {visualStyle3}, {genre}, {artistReference}
    3. Return markdown in this format:
       **Summary:** <summary>
       ![Image](https://image.pollinations.ai/prompt/<encoded_prompt>)
    """

    response = model.generate_content(
        system_instruction + f"\nUser description: {user_input}"
    )

    return response.text

if __name__ == "__main__":
    user_input = "A dog and cat playing chess in a park"
    # user_input = "Sung Jinwoo from Solo Leveling"
    # user_input = "Cindrella"
    result = make_pollinations_prompt(user_input)

    print(result)
