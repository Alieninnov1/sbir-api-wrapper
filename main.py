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
