from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional

class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: str
    correlation_id: str

class CommandRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(
        ...,
        description="Natural language instruction for the robot",
        min_length=1,
        max_length=1000,
        json_schema_extra={"example": "Shato move to coordinates 10 and -5"},
    )
    correlation_id: Optional[str] = Field(
        None,
        description="Unique correlation ID for tracing requests",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"},
    )

class SuccessResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command: str = Field(..., description="The command name (e.g., 'move_to', 'rotate', 'start_patrol')")
    command_params: Dict[str, Any] = Field(
        ...,
        description="Command parameters conforming to the strict robot command schema",
        json_schema_extra={
            "example": {
                "x": 10.0,
                "y": -5.0
            }
        }
    )
    verbal_response: str = Field(
        ...,
        description="Natural spoken confirmation for TTS",
        json_schema_extra={"example": "Heading over there now—adventure awaits!"}
    )
    correlation_id: str = Field(..., description="Unique correlation ID for tracing requests")