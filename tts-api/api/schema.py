# api/schema.py
from pydantic import BaseModel, Field
from typing import Optional


class SpeakRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="Text to convert to speech")
    voice: Optional[str] = Field(None, description="Optional: voice/speaker name if supported")
    speed: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="Speech speed multiplier")


class SpeakResponse(BaseModel):
    correlation_id: str
    audio_base64: str
    model: str
    estimated_duration_sec: Optional[float]
