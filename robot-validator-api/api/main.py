from fastapi import FastAPI, status
from .schema import HealthResponse


# App instance 
app = FastAPI(
    title="Robot Validator API",
    description="Validates and logs robot commands.",
    version="1.0.0"
)


# Health endpoint 
@app.get(
    "/", 
    response_model=HealthResponse, 
    status_code=status.HTTP_200_OK 
)
def health():
    """Health check endpoint to verify server is running"""
    return HealthResponse(message="Server Is Running!")
