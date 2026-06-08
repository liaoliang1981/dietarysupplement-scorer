"""Minimal scoring API — wraps the deterministic engine as POST /score.

Used by:
  - a Custom GPT Action (point openapi.yaml's server URL here), or
  - your own product backend via the OpenAI Responses API (function calling).

Run locally:
    pip install fastapi uvicorn
    uvicorn server:app --host 0.0.0.0 --port 8000

Deploy anywhere that runs Python (Render, Railway, Fly, a VM). For serverless
(Vercel/Cloudflare) adapt the handler — the scoring logic in score.py is the
part that matters and stays identical.

NOTE: this endpoint runs ONLY the deterministic scoring engine. It needs no
LLM API key — the model (ChatGPT / your app) lives elsewhere. Do not put any
API key in client-side code.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List

from score import score

app = FastAPI(title="dietarysupplement.ai scoring API")


class Ingredient(BaseModel):
    name: Optional[str] = None
    nutrient: str
    form: Optional[str] = ""
    amount: float
    unit: Optional[str] = ""


class Product(BaseModel):
    name: Optional[str] = ""
    brand: Optional[str] = ""
    pregnant: Optional[bool] = False
    certifications: Optional[List[str]] = []
    ingredients: List[Ingredient]


@app.post("/score")
def score_endpoint(product: Product):
    p = product.model_dump()
    return score(p, pregnant=bool(p.get("pregnant")))


@app.get("/health")
def health():
    return {"ok": True}
