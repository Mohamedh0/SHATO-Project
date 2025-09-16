import pytest
from pydantic import ValidationError

from api.schema import (
    MoveToParams,
    MoveToCommand,
    RotateParams,
    RotateCommand,
    StartPatrolParams,
    StartPatrolCommand,
)


def test_move_to_params_valid():
    p = MoveToParams(x=1.5, y=-2.0)
    assert p.x == 1.5 and p.y == -2.0


def test_move_to_command_valid():
    cmd = MoveToCommand(command="move_to", command_params={"x": 0, "y": 0})
    assert cmd.command == "move_to"
    assert isinstance(cmd.command_params, MoveToParams)


def test_rotate_params_valid():
    p = RotateParams(angle=90, direction="clockwise")
    assert p.angle == 90 and p.direction == "clockwise"


def test_rotate_command_valid():
    cmd = RotateCommand(command="rotate", command_params={"angle": 45.5, "direction": "counter-clockwise"})
    assert cmd.command == "rotate"
    assert isinstance(cmd.command_params, RotateParams)


@pytest.mark.parametrize("route_id", ["first_floor", "bedrooms", "second_floor"])  # allowed values
def test_start_patrol_params_valid(route_id):
    p = StartPatrolParams(route_id=route_id)
    assert p.speed == "medium"
    assert p.repeat_count == 1


def test_start_patrol_params_with_options():
    p = StartPatrolParams(route_id="first_floor", speed="fast", repeat_count=-1)
    assert p.speed == "fast"
    assert p.repeat_count == -1


def test_start_patrol_command_valid():
    cmd = StartPatrolCommand(command="start_patrol", command_params={"route_id": "bedrooms", "speed": "slow", "repeat_count": 2})
    assert cmd.command == "start_patrol"
    assert isinstance(cmd.command_params, StartPatrolParams)


# Edge cases / invalid values

def test_rotate_invalid_direction():
    with pytest.raises(ValidationError):
        RotateCommand(command="rotate", command_params={"angle": 45, "direction": "left"})


def test_start_patrol_invalid_route():
    with pytest.raises(ValidationError):
        StartPatrolParams(route_id="garage")


def test_start_patrol_invalid_speed():
    with pytest.raises(ValidationError):
        StartPatrolParams(route_id="first_floor", speed="turbo")


def test_start_patrol_invalid_repeat_count_type():
    with pytest.raises(ValidationError):
        StartPatrolParams(route_id="first_floor", repeat_count="three")


