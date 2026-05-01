from fastapi import FastAPI
from app.models import Envelope
from app.services.validation_service import validate_envelope
from app.services.matching_service import match_envelope

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai-pipeline", "version": "1.0"}

@app.post("/validate")
async def validate_api(envelope: Envelope):
    return validate_envelope(envelope)

@app.post("/match")
async def match_api(envelope: Envelope):
    return await match_envelope(envelope)

@app.post("/process")
async def process_api(envelope: Envelope):
    envelope = validate_envelope(envelope)
    envelope = await match_envelope(envelope)
    return envelope