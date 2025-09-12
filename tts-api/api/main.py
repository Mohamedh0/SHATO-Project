# api/main.py
import asyncio
import base64
import logging
import os
import tempfile
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .schema import SpeakRequest, SpeakResponse


# Coqui TTS API
from TTS.api import TTS

app = FastAPI(
    title="TTS Service",
    description="Converts text into speech using Coqui TTS.",
    version="1.0.0",
)

logger = logging.getLogger("uvicorn.access")

# Model selection (pretrained)
MODEL_NAME = "tts_models/en/ljspeech/tacotron2-DDC"

# Load model at startup (blocking)
@app.on_event("startup")
def load_model():
    global tts
    logger.info(f"Loading TTS model: {MODEL_NAME} (this may take a while on first run)")
    tts = TTS(MODEL_NAME)
    logger.info("TTS model loaded successfully")





@app.get("/", response_model=dict)
def health():
    return {"message": "TTS Service Running!"}


@app.post("/speak", response_model=SpeakResponse)
async def speak(req: SpeakRequest):
    correlation_id = str(uuid.uuid4())

    # Basic validation
    if not req.text.strip():
        logger.error(f"[{correlation_id}] [TTS-ERROR] Empty text")
        raise HTTPException(status_code=400, detail="Text must not be empty")

    # Use a temp file to ask Coqui to write WAV
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpf:
        audio_path = tmpf.name

    try:
        # The TTS call is synchronous/blocking — run it in a thread
        # NOTE: different TTS models accept different kwargs (speaker, speed). If your chosen model
        # supports 'speaker' or 'speed' parameters, pass them in as needed.
        def run_tts():
            # Basic call: text -> file. Adjust kwargs if your model supports them.
            # Example: tts.tts_to_file(text=req.text, file_path=audio_path, speaker=req.voice, speed=req.speed)
            # Use whichever signature is supported in the installed TTS version.
            # We'll try named args that are commonly supported:
            kwargs = {"text": req.text, "file_path": audio_path}
            if req.speed is not None:
                kwargs["speed"] = req.speed
            # Some models support "speaker" or "speaker_wav" instead of "voice"
            if req.voice:
                kwargs["speaker"] = req.voice
            tts.tts_to_file(**kwargs)

        await asyncio.to_thread(run_tts)

        # read audio bytes
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

        # estimate duration roughly: (bytes not reliable). Provide an approximate by character length
        estimated_duration = round(len(req.text) / 12.0 / (req.speed or 1.0), 2)

        logger.info(f"[{correlation_id}] [TTS-SUCCESS] Generated audio ({len(audio_bytes)} bytes)")

        return {
            "correlation_id": correlation_id,
            "audio_base64": audio_b64,
            "model": MODEL_NAME,
            "estimated_duration_sec": estimated_duration,
        }
    except Exception as e:
        logger.exception(f"[{correlation_id}] [TTS-ERROR] {e}")
        raise HTTPException(status_code=500, detail=f"TTS generation error: {e}")
    finally:
        # cleanup
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception:
            pass
