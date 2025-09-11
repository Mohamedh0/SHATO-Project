# api/validator.py
from typing import Union
from pydantic import ValidationError
from .schema import MoveToCommand, RotateCommand, StartPatrolCommand, RobotCommand

def validate_command(payload: dict) -> Union[RobotCommand, dict]:
    """
    Validate incoming payload against strict robot command schema.
    Returns:
        - RobotCommand instance if valid
        - dict with "error" and "details" if invalid
    """
    try:
        command_type = payload.get("command")
        if command_type == "move_to":
            return MoveToCommand(**payload)
        elif command_type == "rotate":
            return RotateCommand(**payload)
        elif command_type == "start_patrol":
            return StartPatrolCommand(**payload)
        else:
            return {"error": "Invalid command", "reason": f"Unknown command '{command_type}'"}
    except ValidationError as e:
        return {"error": "Validation failed", "details": e.errors()}
