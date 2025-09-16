# api/schema.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional, Union

class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: str

# --- Command: move_to ---
class MoveToParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    x: float = Field(
        ...,
        description="X coordinate",
        json_schema_extra={"example": 10.0}
    )
    y: float = Field(
        ...,
        description="Y coordinate",
        json_schema_extra={"example": -5.0}
    )

class MoveToCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command: Literal["move_to"]
    command_params: MoveToParams

# --- Command: rotate ---
class RotateParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    angle: float = Field(
        ...,
        description="Rotation angle in degrees",
        json_schema_extra={"example": 90.0}
    )
    direction: Literal["clockwise", "counter-clockwise"] = Field(
        ...,
        description="Rotation direction"
    )

class RotateCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command: Literal["rotate"]
    command_params: RotateParams

# --- Command: start_patrol ---
class StartPatrolParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route_id: Literal["first_floor", "bedrooms", "second_floor"] = Field(
        ...,
        description="Predefined patrol route"
    )
    speed: Optional[Literal["slow", "medium", "fast"]] = Field(
        "medium",
        description="Patrol speed (default=medium)"
    )
    repeat_count: Optional[int] = Field(
        1,
        ge=-1,
        description="Number of loops, -1 for infinite"
    )

class StartPatrolCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command: Literal["start_patrol"]
    command_params: StartPatrolParams

# --- Union of All Valid Commands ---
RobotCommand = Union[MoveToCommand, RotateCommand, StartPatrolCommand]