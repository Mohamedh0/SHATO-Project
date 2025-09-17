# api/main.py
import asyncio
import base64
import logging
import os
import tempfile
import uuid
import time
from typing import Optional
from contextvars import ContextVar
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError
BaseModel.model_config = {"arbitrary_types_allowed": True}
from .schema import SpeakRequest, SpeakResponse
from TTS.api import TTS

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('tts_service.log')
    ]
)

# Context variable for correlation ID
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default='')

class CorrelationIDFilter(logging.Filter):
    def filter(self, record):
        record.correlation_id = correlation_id_var.get('')
        return True

# Add filter to all loggers
for handler in logging.root.handlers:
    handler.addFilter(CorrelationIDFilter())

logger = logging.getLogger(__name__)

app = FastAPI(
    title="TTS Service",
    description="Converts text into speech using Coqui TTS with comprehensive logging and error handling.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model selection (pretrained)
MODEL_NAME = "tts_models/en/ljspeech/tacotron2-DDC"

# Global TTS model instance
tts = None

# Correlation ID middleware
@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    # Generate or extract correlation ID
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    correlation_id_var.set(correlation_id)
    
    # Log request
    start_time = time.time()
    logger.info(f"Request started: {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Request completed: {response.status_code} in {process_time:.3f}s")
    
    # Add correlation ID to response headers
    response.headers["X-Correlation-ID"] = correlation_id
    
    return response

# Load model at startup (blocking)
@app.on_event("startup")
async def load_model():
    global tts
    logger.info(f"Starting TTS service - Loading model: {MODEL_NAME}")
    try:
        tts = TTS(MODEL_NAME)
        logger.info("TTS model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load TTS model: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("TTS service shutting down")





@app.get("/", response_model=dict, tags=["Health"])
def health():
    """Health check endpoint"""
    return {
        "message": "TTS Service Running!",
        "status": "healthy",
        "model": MODEL_NAME,
        "version": "1.0.0"
    }

@app.get("/health", response_model=dict, tags=["Health"])
def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": "TTS Service",
        "model": MODEL_NAME,
        "model_loaded": tts is not None,
        "version": "1.0.0",
        "timestamp": time.time()
    }

# Custom exception handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    correlation_id = correlation_id_var.get('')
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "correlation_id": correlation_id
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    correlation_id = correlation_id_var.get('')
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "detail": exc.detail,
            "correlation_id": correlation_id
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    correlation_id = correlation_id_var.get('')
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred",
            "correlation_id": correlation_id
        }
    )

@app.post("/speak", 
          response_model=SpeakResponse, 
          tags=["TTS"],
          summary="Convert text to speech",
          description="Converts the provided text into speech audio using Coqui TTS model",
          responses={
              200: {
                  "description": "Audio generated successfully",
                  "content": {
                      "application/json": {
                          "example": {
                              "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
                              "audio_base64": "UklGRiQAAABXQVZFZm10IBAAAAABAAEA...",
                              "model": "tts_models/en/ljspeech/tacotron2-DDC",
                              "estimated_duration_sec": 2.5
                          }
                      }
                  }
              },
              400: {
                  "description": "Bad request - invalid input",
                  "content": {
                      "application/json": {
                          "example": {
                              "error": "HTTP Error",
                              "detail": "Text must not be empty",
                              "correlation_id": "123e4567-e89b-12d3-a456-426614174000"
                          }
                      }
                  }
              },
              422: {
                  "description": "Validation error",
                  "content": {
                      "application/json": {
                          "example": {
                              "error": "Validation Error",
                              "detail": [{"loc": ["text"], "msg": "field required", "type": "value_error.missing"}],
                              "correlation_id": "123e4567-e89b-12d3-a456-426614174000"
                          }
                      }
                  }
              },
              500: {
                  "description": "Internal server error",
                  "content": {
                      "application/json": {
                          "example": {
                              "error": "Internal Server Error",
                              "detail": "TTS generation failed",
                              "correlation_id": "123e4567-e89b-12d3-a456-426614174000"
                          }
                      }
                  }
              }
          })
async def speak(req: SpeakRequest):
    """
    Convert text to speech using Coqui TTS model.
    
    - **text**: Text to convert to speech (1-1000 characters)
    - **voice**: Optional voice/speaker name if supported by the model
    - **speed**: Speech speed multiplier (0.5-2.0, default: 1.0)
    
    Returns base64-encoded audio data along with metadata.
    """
    correlation_id = correlation_id_var.get('')
    logger.info(f"TTS request received: text_length={len(req.text)}, voice={req.voice}, speed={req.speed}")

    # Enhanced validation
    if not req.text or not req.text.strip():
        logger.warning(f"Empty text provided")
        raise HTTPException(
            status_code=400, 
            detail="Text must not be empty or contain only whitespace"
        )
    
    # Check for invalid characters or suspicious content
    if len(req.text.strip()) < 1:
        logger.warning(f"Text too short: '{req.text}'")
        raise HTTPException(
            status_code=400,
            detail="Text must contain at least 1 character"
        )
    
    # Check if model is loaded
    if tts is None:
        logger.error("TTS model not loaded")
        raise HTTPException(
            status_code=503,
            detail="TTS service not ready - model not loaded"
        )

    # Use a temp file to ask Coqui to write WAV
    audio_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpf:
            audio_path = tmpf.name

        logger.info(f"Generating audio for text: '{req.text[:50]}{'...' if len(req.text) > 50 else ''}'")

        # The TTS call is synchronous/blocking — run it in a thread
        def run_tts():
            try:
                kwargs = {"text": req.text, "file_path": audio_path}
                if req.speed is not None:
                    kwargs["speed"] = req.speed
                if req.voice:
                    kwargs["speaker"] = req.voice
                
                logger.debug(f"TTS parameters: {kwargs}")
                tts.tts_to_file(**kwargs)
            except Exception as e:
                logger.error(f"TTS generation failed: {e}")
                raise

        await asyncio.to_thread(run_tts)

        # Verify audio file was created and has content
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
            logger.error("Audio file was not created or is empty")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate audio - empty output"
            )

        # Read audio bytes
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        if len(audio_bytes) == 0:
            logger.error("Generated audio file is empty")
            raise HTTPException(
                status_code=500,
                detail="Generated audio is empty"
            )

        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

        # Estimate duration more accurately
        estimated_duration = round(len(req.text) / 12.0 / (req.speed or 1.0), 2)

        logger.info(f"TTS generation successful: {len(audio_bytes)} bytes, estimated duration: {estimated_duration}s")

        return SpeakResponse(
            correlation_id=correlation_id,
            audio_base64=audio_b64,
            model=MODEL_NAME,
            estimated_duration_sec=estimated_duration
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error during TTS generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"TTS generation failed: {str(e)}"
        )
    finally:
        # Cleanup temp file
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
                logger.debug(f"Cleaned up temp file: {audio_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {audio_path}: {e}")
