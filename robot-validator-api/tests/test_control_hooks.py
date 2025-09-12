from api.control_hooks import move_to, rotate, start_patrol


def test_move_to_stubbed():
    res = move_to(1.2, -3.4)
    assert res["status"] == "stubbed"
    assert res["action"] == "move_to"
    assert res["params"]["x"] == 1.2
    assert res["params"]["y"] == -3.4


def test_rotate_stubbed():
    res = rotate(45, "counter-clockwise")
    assert res["status"] == "stubbed"
    assert res["action"] == "rotate"
    assert res["params"]["angle"] == 45
    assert res["params"]["direction"] == "counter-clockwise"


def test_start_patrol_stubbed_defaults():
    res = start_patrol("first_floor")
    assert res["status"] == "stubbed"
    assert res["action"] == "start_patrol"
    assert res["params"]["route_id"] == "first_floor"
    assert res["params"]["speed"] == "medium"
    assert res["params"]["repeat_count"] == 1


def test_start_patrol_stubbed_custom():
    res = start_patrol("bedrooms", speed="fast", repeat_count=-1)
    assert res["params"]["speed"] == "fast"
    assert res["params"]["repeat_count"] == -1


