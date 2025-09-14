# api/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .model import load_model, generate_command
from .schema import CommandRequest, SuccessResponse, HealthResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to track model loading status
model_loaded = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    global model_loaded
    try:
        logger.info("Starting model loading...")
        load_model()
        model_loaded = True
        logger.info("Model loaded successfully!")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        model_loaded = False
    yield

app = FastAPI(
    title="LLM Robot Command API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(
        message=f"LLM API is running. Model loaded: {model_loaded}"
    )

@app.post("/generate", response_model=SuccessResponse)
async def generate(request: CommandRequest):
    """Generate a robot command from natural language instruction"""
    if not model_loaded:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Service unavailable."
        )
    
    try:
        result = generate_command(request.text)
        
        # Check if the result contains an error
        if "error" in result:
            raise HTTPException(
                status_code=400,
                detail=f"Command generation failed: {result.get('error', 'unknown_error')}"
            )
        
        return SuccessResponse(
            command=result["command"],
            command_params=result["command_params"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating command: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    status = "healthy" if model_loaded else "unhealthy"
    return HealthResponse(
        message=f"Service is {status}. Model loaded: {model_loaded}"
    )