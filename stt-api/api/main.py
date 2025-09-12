from fastapi import FastAPI ,UploadFile,File
from .schema import HealthResponse ,TranscribeResponse
from .utils import transcribe_audio

app= FastAPI(title="stt_service" , description="audio_to_text" , version="1.0.0")

@app.get("/", response_model=HealthResponse)
async def health():
    return HealthResponse(message= "server is running")

@app.post("/transcribe", response_model=transcribe_audio)
async def transcribe(audio: UploadFile=File(...)):
    audio_bytes= await audio.read
    text= transcribe_audio(audio_bytes) 
    return TranscribeResponse(text=text)



