from fastapi import FastAPI, UploadFile, File
from .schema import HealthResponse, TranscribeResponse
from .utils import transcribe_audio
from pydantic import BaseModel
BaseModel.model_config = {"arbitrary_types_allowed": True}

app = FastAPI(
    title="stt_service",
    description="Audio to Text Transcription Service",
    version="1.0.0",
)

@app.get("/", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(message="server is running")

@app.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(audio: UploadFile = File(...)) -> TranscribeResponse:
    audio_bytes = await audio.read()
    id_correlation, text = transcribe_audio(audio_bytes)
    return TranscribeResponse(id_correlation=id_correlation, text=text)
