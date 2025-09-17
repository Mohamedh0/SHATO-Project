# tests/test_validator.py
import pytest
from api.validator import validate_command, parse_and_validate_text_output


def test_validate_command_move_to():
    """Test the original validate_command function with move_to."""
    payload = {"command": "move_to", "command_params": {"x": 1.0, "y": 2.0}}
    result = validate_command(payload)
    
    # Should return a valid command object, not an error dict
    assert not isinstance(result, dict) or "error" not in result
    assert result.command == "move_to"
    assert result.command_params.x == 1.0
    assert result.command_params.y == 2.0


def test_validate_command_rotate():
    """Test the original validate_command function with rotate."""
    payload = {"command": "rotate", "command_params": {"angle": 90, "direction": "clockwise"}}
    result = validate_command(payload)
    
    assert not isinstance(result, dict) or "error" not in result
    assert result.command == "rotate"
    assert result.command_params.angle == 90


def test_validate_command_unknown():
    """Test the original validate_command function with unknown command."""
    payload = {"command": "fly", "command_params": {"x": 1, "y": 2}}
    result = validate_command(payload)
    
    assert isinstance(result, dict)
    assert result["error"] == "Invalid command"


def test_parse_valid_move_to_command():
    """Should validate a correct move_to command from text."""
    raw = '{"command":"move_to","command_params":{"x":1.0,"y":2.0}}'
    ok, result = parse_and_validate_text_output(raw)
    assert ok is True
    assert result["command"] == "move_to"
    assert result["command_params"]["x"] == 1.0
    assert result["command_params"]["y"] == 2.0


def test_parse_valid_rotate_command():
    """Should validate a correct rotate command from text."""
    raw = '{"command":"rotate","command_params":{"angle":90,"direction":"clockwise"}}'
    ok, result = parse_and_validate_text_output(raw)
    assert ok is True
    assert result["command"] == "rotate"
    assert result["command_params"]["angle"] == 90


def test_parse_valid_start_patrol_command_defaults():
    """Should use default speed and repeat_count if not provided."""
    raw = '{"command":"start_patrol","command_params":{"route_id":"first_floor"}}'
    ok, result = parse_and_validate_text_output(raw)
    assert ok is True
    assert result["command_params"]["route_id"] == "first_floor"
    assert result["command_params"]["speed"] == "medium"  # default
    assert result["command_params"]["repeat_count"] == 1  # default


def test_parse_missing_field():
    """Should fail if required fields are missing (y is missing)."""
    raw = '{"command":"move_to","command_params":{"x":1.0}}'
    ok, result = parse_and_validate_text_output(raw)
    assert ok is False
    assert result["error_code"] == "validation_error"
    assert any("y" in str(e) for e in result["details"])


def test_parse_invalid_type():
    """Should fail if type is wrong (angle should be float)."""
    raw = '{"command":"rotate","command_params":{"angle":"ninety","direction":"clockwise"}}'
    ok, result = parse_and_validate_text_output(raw)
    assert ok is False
    assert result["error_code"] == "validation_error"


def test_parse_unknown_command():
    """Should fail if command is not one of allowed."""
    raw = '{"command":"fly","command_params":{"x":1,"y":2}}'
    ok, result = parse_and_validate_text_output(raw)
    assert ok is False
    assert result["error_code"] == "unknown_command"


def test_parse_extra_field_rejection():
    """Should fail if an unexpected field is present."""
    raw = '{"command":"move_to","command_params":{"x":1.0,"y":2.0},"unexpected":"value"}'
    ok, result = parse_and_validate_text_output(raw)
    assert ok is False
    assert result["error_code"] == "validation_error"


def test_parse_invalid_json():
    """Should fail if JSON is malformed."""
    raw = '{command:"move_to", "command_params":{x:1.0,y:2.0}}'  # invalid JSON
    ok, result = parse_and_validate_text_output(raw)
    assert ok is False
    assert result["error_code"] in ("parse_error", "invalid_json")


def test_parse_json_with_prose():
    """Should still extract and validate JSON if there is extra text around it."""
    raw = 'Sure! {"command":"rotate","command_params":{"angle":90,"direction":"clockwise"}} Thanks.'
    ok, result = parse_and_validate_text_output(raw)
    assert ok is True
    assert result["command"] == "rotate"