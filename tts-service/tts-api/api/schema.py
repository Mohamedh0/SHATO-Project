# api/schema.py
from pydantic import BaseModel, Field, validator
from typing import Optional


class SpeakRequest(BaseModel):
    text: str = Field(
        ..., 
        min_length=1, 
        max_length=1000, 
        description="Text to convert to speech",
        example="Hello, Made In Alexandria! Welcome to our TTS service."
    )
    voice: Optional[str] = Field(
        None, 
        description="Optional: voice/speaker name if supported by the model",
        example="female"
    )
    speed: Optional[float] = Field(
        1.0, 
        ge=0.5, 
        le=2.0, 
        description="Speech speed multiplier (0.5 = slow, 1.0 = normal, 2.0 = fast)",
        example=1.0
    )

    @validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty or contain only whitespace')
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "text": "Hello, Made In Alexandria! Welcome to our TTS service.",
                "voice": "female",
                "speed": 1.0
            }
        }


class SpeakResponse(BaseModel):
    correlation_id: str = Field(
        ..., 
        description="Unique identifier for tracking this request",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    audio_base64: str = Field(
        ..., 
        description="Base64-encoded audio data (WAV format)",
        example="UklGRiQAAABXQVZFZm10IBAAAAABAAEA..."
    )
    model: str = Field(
        ..., 
        description="TTS model used for generation",
        example="tts_models/en/ljspeech/tacotron2-DDC"
    )
    estimated_duration_sec: Optional[float] = Field(
        None, 
        description="Estimated duration of the generated audio in seconds",
        example=2.5
    )

    class Config:
        schema_extra = {
            "example": {
                "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
                "audio_base64": "UklGRiQAAABXQVZFZm10IBAAAAABAAEA...",
                "model": "tts_models/en/ljspeech/tacotron2-DDC",
                "estimated_duration_sec": 2.5
            }
        }


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error type", example="HTTP Error")
    detail: str = Field(..., description="Error details", example="Text must not be empty")
    correlation_id: str = Field(..., description="Request correlation ID", example="123e4567-e89b-12d3-a456-426614174000")

    class Config:
        schema_extra = {
            "example": {
                "error": "HTTP Error",
                "detail": "Text must not be empty",
                "correlation_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
