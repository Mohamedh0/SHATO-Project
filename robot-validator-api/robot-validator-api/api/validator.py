# api/validator.py
import json
import logging
from typing import Any, Dict, Tuple, Union

from pydantic import ValidationError
from .schema import MoveToCommand, RotateCommand, StartPatrolCommand, RobotCommand

logger = logging.getLogger("uvicorn.error")

# Map top-level command names to their Pydantic models
COMMAND_MODEL_MAP = {
    "move_to": MoveToCommand,
    "rotate": RotateCommand,
    "start_patrol": StartPatrolCommand,
}


class RobotValidationError(Exception):
    """Custom exception to represent parsing/validation errors in robot commands."""

    def __init__(self, code: str, message: str, details: Any = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


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


def _extract_first_json(text: str) -> str:
    """
    Extract the first balanced JSON object or array from a string.

    Raises:
        ValueError: if no balanced object/array is found.
    """
    text = text.strip()

    # Find first '{' or '['
    start_idx = None
    for i, ch in enumerate(text):
        if ch in ("{", "["):
            start_idx = i
            break
    if start_idx is None:
        raise ValueError("No JSON object/array start found in text output.")

    open_char = text[start_idx]
    close_char = "}" if open_char == "{" else "]"
    depth = 0

    for j in range(start_idx, len(text)):
        if text[j] == open_char:
            depth += 1
        elif text[j] == close_char:
            depth -= 1
            if depth == 0:
                return text[start_idx : j + 1]

    raise ValueError("Failed to extract balanced JSON; braces not matched.")


def parse_and_validate_text_output(raw_text: str) -> Tuple[bool, Union[Dict, Any]]:
    """
    Parse text output and validate it against allowed robot command schemas.
    (Adapted from LLM validator but made generic for robot validation)

    Returns:
        (True, validated_model_dict) on success
        (False, error_dict) on failure

    Error dict format:
        {
            "error_code": "parse_error" | "invalid_json" | "unknown_command" | "validation_error",
            "message": "Human-readable message",
            "details": {...}
        }
    """
    try:
        # 1) Extract first JSON object/array
        try:
            json_sub = _extract_first_json(raw_text)
        except ValueError as e:
            raise RobotValidationError("parse_error", "No JSON found in text output", str(e))

        # 2) Parse JSON
        try:
            payload = json.loads(json_sub)
        except json.JSONDecodeError as e:
            raise RobotValidationError(
                "invalid_json",
                "Extracted text is not valid JSON",
                {"json_error": str(e), "json_text": json_sub},
            )

        # 3) Ensure payload is a dict and has a known command
        if not isinstance(payload, dict):
            raise RobotValidationError(
                "invalid_schema",
                "Top-level JSON must be an object (dict).",
                {"payload_type": type(payload).__name__},
            )

        command_name = payload.get("command")
        if command_name not in COMMAND_MODEL_MAP:
            raise RobotValidationError(
                "unknown_command",
                f"Unknown or missing command: '{command_name}'",
                {"command": command_name},
            )

        Model = COMMAND_MODEL_MAP[command_name]

        # 4) Validate using Pydantic model
        try:
            validated = Model(**payload)
        except ValidationError as e:
            raise RobotValidationError(
                "validation_error", "Payload failed schema validation", e.errors()
            )

        validated_dict = validated.model_dump()
        logger.info(f"[ROBOT-VALIDATOR-SUCCESS] Validated command '{command_name}'")
        return True, validated_dict

    except RobotValidationError as re:
        error_obj = {
            "error_code": re.code,
            "message": re.message,
            "details": re.details,
        }
        logger.error(f"[ROBOT-VALIDATOR-ERROR] {error_obj}")
        return False, error_obj

    except Exception as e:
        # Catch unexpected issues
        err = {
            "error_code": "internal_error",
            "message": "Unexpected validator error",
            "details": str(e),
        }
        logger.exception(f"[ROBOT-VALIDATOR-ERROR] {err}")
        return False, err