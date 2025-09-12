from api.validator import validate_command


def test_validate_move_to_success():
    payload = {"command": "move_to", "command_params": {"x": 1.0, "y": -1.0}}
    result = validate_command(payload)
    assert getattr(result, "command", None) == "move_to"


def test_validate_rotate_success():
    payload = {"command": "rotate", "command_params": {"angle": 90, "direction": "clockwise"}}
    result = validate_command(payload)
    assert getattr(result, "command", None) == "rotate"


def test_validate_start_patrol_success():
    payload = {"command": "start_patrol", "command_params": {"route_id": "first_floor", "speed": "slow", "repeat_count": 2}}
    result = validate_command(payload)
    assert getattr(result, "command", None) == "start_patrol"


def test_validate_unknown_command():
    payload = {"command": "dance", "command_params": {}}
    result = validate_command(payload)
    assert isinstance(result, dict) and result.get("error") == "Invalid command"
    assert "Unknown command" in result.get("reason", "")


def test_validate_missing_params():
    payload = {"command": "move_to"}
    result = validate_command(payload)
    assert isinstance(result, dict) and result.get("error") == "Validation failed"
    assert isinstance(result.get("details"), list)


def test_validate_type_errors():
    payload = {"command": "rotate", "command_params": {"angle": "ninety", "direction": "clockwise"}}
    result = validate_command(payload)
    assert isinstance(result, dict) and result.get("error") == "Validation failed"
    assert any("angle" in (err.get("loc") or []) or (err.get("loc") and err["loc"][-1] == "angle") for err in result.get("details", []))


