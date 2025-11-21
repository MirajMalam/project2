# project2

# IITM LLM Quiz Solver  
FastAPI + Playwright + Gemini (Google GenAI Client)

This project is built for the **Tools in Data Science – LLM Analysis Quiz**.  
It exposes an API endpoint that receives a quiz URL, visits the quiz webpage, 
extracts the visible content, uses a Large Language Model to interpret the question, 
find the submit URL, compute the answer, and submit the response automatically.

The quiz may involve:
- Web scraping  
- Data extraction  
- Data analysis  
- File processing (CSV, JSON, PDF, etc.)  
- Audio/media tasks  
- Multi-step navigation across quiz URLs  

This project is designed to automate the process using a combination of:
- FastAPI (backend API)
- Playwright (render JavaScript pages)
- Google Gemini (reasoning + interpretation)
- Requests (submitting answers)
- A strict prompt strategy to avoid hallucination

---

## Features

### ✔ API endpoint with required behavior  
- **200** for valid requests  
- **400** for invalid JSON  
- **403** for invalid secret  
- Secrets validated using `.env`  

### ✔ LLM-driven quiz solving  
- Extract visible text from the webpage  
- Ask Gemini to produce:
  ```json
  {
    "submit_url": "...",
    "answer": ...
  }
