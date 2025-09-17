from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx
import uuid

from config import settings

app = FastAPI(title="Orchestrator Service", version="1.0.0")


# ---------- Request / Response Schemas ----------

class InferRequest(BaseModel):
    text: str
    correlation_id: Optional[str] = None


class ExecuteRequest(BaseModel):
    command: str
    command_params: dict
    correlation_id: Optional[str] = None


class SpeakRequest(BaseModel):
    text: str
    voice: Optional[str] = None
    speed: Optional[float] = None
    correlation_id: Optional[str] = None


# ---------- Utility ----------

async def call_service(method: str, url: str, **kwargs):
    """
    Generic helper to call downstream services using httpx.AsyncClient.
    Raises HTTPException if service call fails.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.request(method, url, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Service unreachable: {url} ({e})")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=resp.status_code, detail=f"Service returned error: {resp.text}")


# ---------- Endpoints ----------

@app.get("/")
async def root():
    """Basic health check."""
    return {"message": "Orchestrator service is running"}


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """Send audio to STT service and return transcription."""
    files = {"audio": (audio.filename, await audio.read(), audio.content_type)}
    result = await call_service("POST", settings.stt_url, files=files)
    return result


@app.post("/infer")
async def infer(request: InferRequest):
    """Send text to LLM service to get command + params."""
    payload = request.dict(exclude_none=True)
    result = await call_service("POST", settings.llm_url, json=payload)
    return result


@app.post("/execute")
async def execute(request: ExecuteRequest):
    """Send command to validator service to check if it's valid."""
    payload = request.dict(exclude_none=True)
    result = await call_service("POST", settings.validator_url, json=payload)
    return result


@app.post("/speak")
async def speak(request: SpeakRequest):
    """Send text to TTS service and get back audio."""
    payload = request.dict(exclude_none=True)
    result = await call_service("POST", settings.tts_url, json=payload)
    return result


@app.post("/voice_flow")
async def voice_flow(audio: UploadFile = File(...)):
    """
    Full pipeline:
    1. Transcribe audio -> text
    2. Send text to LLM -> command
    3. Validate command
    4. Synthesize response to speech
    """
    # Step 1: Transcribe
    files = {"audio": (audio.filename, await audio.read(), audio.content_type)}
    stt_result = await call_service("POST", settings.stt_url, files=files)

    text = stt_result.get("text")
    if not text:
        raise HTTPException(status_code=500, detail="STT service did not return text")

    # Step 2: LLM inference
    llm_payload = {"text": text, "correlation_id": str(uuid.uuid4())}
    llm_result = await call_service("POST", settings.llm_url, json=llm_payload)

    # Step 3: Validation
    validator_result = await call_service("POST", settings.validator_url, json=llm_result)

    # Step 4: TTS
    tts_payload = {"text": text}
    tts_result = await call_service("POST", settings.tts_url, json=tts_payload)

    return {
        "stt": stt_result,
        "llm": llm_result,
        "validator": validator_result,
        "tts": tts_result,
    }
