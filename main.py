from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import openai
import os

app = FastAPI(
    title="SBIR MatchmakerX API",
    description="API wrapper for SBIR solicitations, winners, and funding gap analysis.",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root
@app.get("/")
def root():
    return {"status": "SBIR MatchmakerX API is live."}

# Ping
@app.get("/ping")
def ping():
    return {"status": "ok", "uptime": "🔥"}

# Awards from SBIR.gov
@app.get("/awards")
def get_awards(agency: str = "DOE", year: int = 2022, start: int = 0, rows: int = 100):
    url = f"https://api.www.sbir.gov/public/api/awards?agency={agency}&year={year}&start={start}&rows={rows}&format=json"
    try:
        res = requests.get(url)
        data = res.json().get("results", [])
        return {"count": len(data), "awards": data}
    except Exception as e:
        return {"error": str(e)}

# GPT tag enrichment
openai.api_key = os.getenv("OPENAI_API_KEY")

class EnrichRequest(BaseModel):
    award_title: str
    abstract: str

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
            messages=[{"role": "user", "content": prompt}]
            max_tokens=60,
            temperature=0.5
        )
        tags_raw = response["choices"][0]["message"]["content"]
        tags = [t.strip().lower() for t in tags_raw.replace("\n", ",").split(",") if t.strip()]
        return {"enriched_tags": tags}
    except Exception as e:
        return {"error": str(e)}
