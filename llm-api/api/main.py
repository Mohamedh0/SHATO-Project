from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from api.schema import HealthResponse, CommandRequest, SuccessResponse
from api.utils import (
    get_correlation_id,
    log_request,
    log_response,
    generate_command,
)
from pydantic import BaseModel
BaseModel.model_config = {"arbitrary_types_allowed": True}

app = FastAPI(title="Robot Command API")

@app.middleware("http")
async def add_correlation_id_header(request: Request, call_next):
    correlation_id = get_correlation_id(request)
    log_request(request, correlation_id)
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response

@app.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    correlation_id = get_correlation_id(request)
    log_response(correlation_id, 200, "Service is healthy")
    return HealthResponse(message="Service is healthy", correlation_id=correlation_id)

@app.post("/command", response_model=SuccessResponse)
async def generate_robot_command(
    request: Request,
    body: CommandRequest,
    x_correlation_id: Optional[str] = Header(None, alias="X-Correlation-ID"),
):
    # Prioritize correlation_id from body, then header, then generate a new one
    correlation_id = body.correlation_id or x_correlation_id or get_correlation_id(request)
    
    # Log warning if body and header correlation IDs differ
    if body.correlation_id and x_correlation_id and body.correlation_id != x_correlation_id:
        log_response(correlation_id, 400, f"Correlation ID mismatch: body={body.correlation_id}, header={x_correlation_id}, using body")
    
    try:
        command_json = generate_command(body.text)
        if "error" in command_json:
            log_response(correlation_id, 500, f"Failed to parse JSON from model: {command_json['raw_output']}")
            raise HTTPException(
                status_code=500,
                detail={"error": command_json["error"], "raw_output": command_json["raw_output"]},
                headers={"X-Correlation-ID": correlation_id},
            )
        # Validate command_json structure
        if "command" not in command_json or "command_params" not in command_json:
            log_response(correlation_id, 500, f"Invalid command structure: {command_json}")
            raise HTTPException(
                status_code=500,
                detail={"error": "Invalid command structure", "raw_output": str(command_json)},
                headers={"X-Correlation-ID": correlation_id},
            )
        # Merge correlation_id into the response
        command_json["correlation_id"] = correlation_id
        log_response(correlation_id, 200, f"Generated command: {command_json}")
        return command_json
    except Exception as e:
        log_response(correlation_id, 500, f"Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)},
            headers={"X-Correlation-ID": correlation_id},
        )