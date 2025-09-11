from pydantic import BaseModel, Field
from typing import Literal, Optional, Union


class HealthResponse(BaseModel):
    message: str

# Base structure
class BaseCommand(BaseModel):
    command: str
    command_params: dict


# Command: move_to 
class MoveToParams(BaseModel):
    x: float = Field(..., description="X coordinate", example=10.0)
    y: float = Field(..., description="Y coordinate", example=-5.0)

class MoveToCommand(BaseModel):
    command: Literal["move_to"]
    command_params: MoveToParams


# Command: rotate 
class RotateParams(BaseModel):
    angle: float = Field(..., description="Rotation angle in degrees", example=90.0)
    direction: Literal["clockwise", "counter-clockwise"] = Field(
        ..., description="Rotation direction"
    )

class RotateCommand(BaseModel):
    command: Literal["rotate"]
    command_params: RotateParams


# Command: start_patrol 
class StartPatrolParams(BaseModel):
    route_id: Literal["first_floor", "bedrooms", "second_floor"] = Field(..., description="Predefined patrol route")
    speed: Optional[Literal["slow", "medium", "fast"]] = Field("medium", description="Patrol speed (default=medium)")
    repeat_count: Optional[int] = Field(1, ge=-1, description="Number of loops, -1 for infinite")

class StartPatrolCommand(BaseModel):
    command: Literal["start_patrol"]
    command_params: StartPatrolParams


# Union of all valid commands 
RobotCommand = Union[MoveToCommand, RotateCommand, StartPatrolCommand]
