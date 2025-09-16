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


class SuccessResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command: str = Field(..., description="The command name")
    command_params: Dict[str, Any] = Field(..., description="Command parameters")
    correlation_id: str = Field(..., description="Unique correlation ID for tracing requests")