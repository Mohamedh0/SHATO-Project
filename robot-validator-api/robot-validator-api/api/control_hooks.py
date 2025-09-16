from typing import Any, Dict


def move_to(x: float, y: float) -> Dict[str, Any]:
    """
    Stub hook that would instruct the robot to move to coordinates.
    Returns a structured response for logging/testing.
    """
    return {"status": "stubbed", "action": "move_to", "params": {"x": x, "y": y}}


def rotate(angle: float, direction: str) -> Dict[str, Any]:
    """
    Stub hook that would instruct the robot to rotate.
    """
    return {
        "status": "stubbed",
        "action": "rotate",
        "params": {"angle": angle, "direction": direction},
    }


def start_patrol(route_id: str, speed: str = "medium", repeat_count: int = 1) -> Dict[str, Any]:
    """
    Stub hook that would instruct the robot to start a patrol.
    """
    return {
        "status": "stubbed",
        "action": "start_patrol",
        "params": {"route_id": route_id, "speed": speed, "repeat_count": repeat_count},
    }


