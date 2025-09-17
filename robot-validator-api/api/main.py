from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from .schema import HealthResponse
from .validator import validate_command
import logging
import uuid
from pydantic import BaseModel
BaseModel.model_config = {"arbitrary_types_allowed": True}

app = FastAPI(
    title="Robot Validator API",
    description="Validates and logs robot commands.",
    version="1.0.0"
)

logger = logging.getLogger("uvicorn")

@app.get("/", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def health():
    """Health check endpoint to verify server is running"""
    return HealthResponse(message="Server Is Running!")

@app.post("/execute_command")
async def execute_command(request: Request):
    payload = await request.json()
    correlation_id = str(uuid.uuid4())
    result = validate_command(payload)

    if isinstance(result, dict) and "error" in result:
        logger.error(f"[{correlation_id}] [ROBOT-VALIDATOR-ERROR] {result}")
        return JSONResponse(status_code=400, content={"correlation_id": correlation_id, **result})

    logger.info(f"[{correlation_id}] [ROBOT-VALIDATOR-SUCCESS] Valid command: {result.command}")
    return {"correlation_id": correlation_id, "message": "Command validated", "data": result.model_dump()}
