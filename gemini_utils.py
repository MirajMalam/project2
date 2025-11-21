import os
import asyncio
from google.genai import Client
from dotenv import load_dotenv 

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_AVAILABLE = True
client = None

try:
    if not API_KEY:
        print("GEMINI_API_KEY missing in .env")
        GEMINI_AVAILABLE = False
    else:
        client = Client(api_key=API_KEY)
        print("Gemini Client initialized (new API).")
except Exception as e:
    print("Gemini init failed:", e)
    GEMINI_AVAILABLE = False


MODEL_NAME = "models/gemini-2.5-flash"   # confirmed working


async def call_gemini(prompt: str) -> str:
    """Safe wrapper with timeout + retry."""
    if not GEMINI_AVAILABLE:
        print("Gemini unavailable.")
        return ""

    async def _call():
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        if hasattr(response, "text") and response.text:
            return response.text.strip()
        return ""

    try:
        return await asyncio.wait_for(_call(), timeout=12)

    except asyncio.TimeoutError:
        print("Gemini timed out, retrying...")

        try:
            return await asyncio.wait_for(_call(), timeout=12)
        except Exception as e:
            print("Gemini retry failed:", e)
            return ""

    except Exception as e:
        print("Gemini call error:", e)
        return ""
