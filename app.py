import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from chat import get_chat_response

from model import process_text
from pydantic_models import SpanOut, PredictIn, ChatRequest


# Settings for FastAPI application

app = FastAPI(title="NER Hackathon Stub (Async, rule-based)")

origins = [
    "http://localhost",
    "http://localhost:8000",
    "https://pyaterochka-lct-2025-react.vercel.app",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CYRILLIC_RE = re.compile(r'^[А-Яа-яЁё]', re.UNICODE)
LATIN_RE = re.compile(r'^[A-Za-z]')
DIGIT_RE = re.compile(r'^\d')
TOKEN_RE = re.compile(r'\S+')

LOCAL_MODEL_DIR = './best_saved_model'
HF_MODEL_PATH = 'Reg789/Bert_NER_Piaterochka_2025'

# API Endpoints

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/predict", response_model=List[SpanOut])
async def predict(payload: PredictIn) -> List[SpanOut]:
    text = payload.input
    if text == "":
        return []
    spans: List[SpanOut] = []
    spans = process_text(text)
    return spans

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    response = get_chat_response(request.message, request.history)
    return {"response": response}
