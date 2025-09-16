from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse
from typing import Optional
from api.schema import HealthResponse
from api.utils import (
    get_correlation_id,
    log_request,
    log_response,
    generate_command,
)

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

@app.post("/command")
async def generate_robot_command(
    request: Request,
    body: dict,
    x_correlation_id: Optional[str] = Header(None, alias="X-Correlation-ID"),
):
    correlation_id = x_correlation_id or get_correlation_id(request)
    try:
        command_json = generate_command(body["text"])
        if "error" in command_json:
            raise ValueError("Could not parse JSON from model output")
        # Merge correlation_id into the parsed JSON
        command_json["correlation_id"] = correlation_id
        log_response(correlation_id, 200, f"Generated command: {command_json}")
        return command_json
    except Exception as e:
        log_response(correlation_id, 500, f"Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
            headers={"X-Correlation-ID": correlation_id},
        )
