from fastapi import FastAPI, UploadFile, File
from .schema import HealthResponse, TranscribeResponse
from .utils import transcribe_audio

app = FastAPI(
    title="stt_service",
    description="Audio to Text Transcription Service",
    version="1.0.0",
)


@app.get("/", response_model=HealthResponse)
async def health() -> HealthResponse:
    """
    Health check endpoint to verify the server is running.
    """
    return HealthResponse(message="server is running")


@app.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(audio: UploadFile = File(...)) -> TranscribeResponse:
    """
    Transcribe an uploaded audio file (WAV, MP3, etc.) into text.
    """
    audio_bytes = await audio.read()
    text = transcribe_audio(audio_bytes)
    return TranscribeResponse(text=text)
