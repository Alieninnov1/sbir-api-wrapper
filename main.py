from fastapi import FastAPI
import requests
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS so Softr or frontend can call it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "SBIR API Ready"}

@app.get("/awards")
def get_awards(agency: str = "DOE", year: int = 2022, start: int = 0, rows: int = 100):
    url = f"https://api.www.sbir.gov/public/api/awards?agency={agency}&year={year}&start={start}&rows={rows}&format=json"
    try:
        res = requests.get(url)
        data = res.json().get("results", [])
        return {"count": len(data), "awards": data}
    except Exception as e:
        return {"error": str(e)}
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import openai
import os

app = FastAPI()

# Allow all origins for now (secure later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Request model
class EnrichRequest(BaseModel):
    award_title: str
    abstract: str

# Enrich endpoint
@app.post("/enrich")
async def enrich_award(data: EnrichRequest):
    prompt = (
        f"Title: {data.award_title}\n\n"
        f"Abstract: {data.abstract}\n\n"
        "Extract 3–5 concise innovation-related tags for this project (e.g. 'AI', 'healthtech', 'robotics'):"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60,
            temperature=0.5
        )

        tags_raw = response["choices"][0]["message"]["content"]
        tags = [t.strip().lower() for t in tags_raw.replace("\n", ",").split(",") if t.strip()]

        return { "enriched_tags": tags }

    except Exception as e:
        return { "error": str(e) }
