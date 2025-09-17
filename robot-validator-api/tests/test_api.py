import pytest


@pytest.mark.asyncio
async def test_health(async_client):
    resp = await async_client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["message"] == "Server Is Running!"


@pytest.mark.asyncio
async def test_execute_command_valid_move_to(async_client):
    payload = {"command": "move_to", "command_params": {"x": 0, "y": 0}}
    resp = await async_client.post("/execute_command", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["message"] == "Command validated"
    assert body["data"]["command"] == "move_to"


@pytest.mark.asyncio
async def test_execute_command_invalid(async_client):
    payload = {"command": "dance", "command_params": {}}
    resp = await async_client.post("/execute_command", json=payload)
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"] == "Invalid command"
    assert "correlation_id" in body


@pytest.mark.asyncio
async def test_execute_command_validation_error(async_client):
    payload = {"command": "rotate", "command_params": {"angle": "ninety", "direction": "clockwise"}}
    resp = await async_client.post("/execute_command", json=payload)
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"] == "Validation failed"
    assert any(isinstance(err, dict) for err in body.get("details", []))


