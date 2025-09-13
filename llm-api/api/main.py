from fastapi import FastAPI, HTTPException
from api.schema import HealthResponse
from api.llm_validator import parse_and_validate_llm_output

app = FastAPI(title="LLM API Service")

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {"message": "ok"}

# Inference endpoint
@app.post("/infer")
async def infer(prompt: dict):
    """
    Receives a natural language prompt (user instruction),
    simulates an LLM output, validates it against the schema,
    and returns either a valid command or an error.
    """

    # --- 1) Dummy LLM output (later will be replaced with real model) ---
    llm_output = '{"command": "move_to", "command_params": {"x": 0.0, "y": 0.0}}'

    # --- 2) Validate using the provided validator ---
    success, result = parse_and_validate_llm_output(llm_output)

    if not success:
        raise HTTPException(status_code=400, detail=result)

    # --- 3) Return validated response ---
    return result
