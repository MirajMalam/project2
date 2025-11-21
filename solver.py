import time
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from playwright.async_api import async_playwright
from gemini_utils import call_gemini

MAX_TIME = 180  # 3 minutes limit


def extract_visible_text(html: str) -> str:
    """Extract visible text from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ")
    text = " ".join(text.split())
    return text[:20000]


async def process_quiz(payload: dict):
    email = payload["email"]
    secret = payload["secret"]
    url = payload["url"]

    print(f"Starting solver for: {url}")
    start_time = time.time()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        while url and (time.time() - start_time) < MAX_TIME:

            page = await context.new_page()
            print(f"Loading page: {url}")

            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_timeout(2500)

            html = await page.content()
            visible_text = extract_visible_text(html)

            print("Page text preview:")
            print(visible_text[:350], "...\n")

            # LLM prompt
            prompt = f"""
You are solving a quiz.

Here is the visible text from the webpage:
------------------------------------------------------------
{visible_text}
------------------------------------------------------------

Your tasks:
1. Identify the exact URL where the answer must be POSTed.
2. Determine the correct answer.
3. Return ONLY a valid JSON object in this exact format:

{{
  "submit_url": "THE_URL_TO_POST_TO",
  "answer": VALUE_OR_JSON
}}

Output only JSON. No explanations. No markdown.
"""

            print("Calling Gemini...")
            llm_output = await call_gemini(prompt)

            if not llm_output.strip():
                print("LLM returned no output. Stopping.")
                break

            print("LLM Output:", llm_output)

            try:
                result = json.loads(llm_output)
            except Exception as e:
                print("Failed to parse LLM JSON:", e)
                break

            submit_url = result.get("submit_url")
            answer = result.get("answer")

            if not submit_url:
                print("LLM did not return submit_url.")
                break

            # Convert relative URL to absolute
            submit_url = urljoin(url, submit_url)

            print(f"Using submit_url: {submit_url}")
            print(f"Answer: {answer}")

            # Submit to server
            print("Submitting answer...")

            try:
                response = requests.post(submit_url, json={
                    "email": email,
                    "secret": secret,
                    "url": url,
                    "answer": answer
                })
            except Exception as e:
                print("Submission failed:", e)
                break

            try:
                server_response = response.json()
            except:
                print("Server did not return JSON.")
                break

            print("Server Response:", server_response)

            # Move to next quiz URL
            url = server_response.get("url")
            if not url:
                print("Quiz complete.")
                break

        await browser.close()

    print("Solver finished.")
