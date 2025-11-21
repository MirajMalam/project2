from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import asyncio
import os
from dotenv import load_dotenv
from solver import process_quiz

load_dotenv()

EXPECTED_SECRET = os.getenv("EXPECTED_SECRET")

app = FastAPI()

@app.post("/solve")
async def solve(req: Request):
    try:
        body = await req.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    for field in ["email", "secret", "url"]:
        if field not in body:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")

    if body["secret"] != EXPECTED_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    asyncio.create_task(process_quiz(body))

    return JSONResponse({"status": "accepted"}, 200)
