from fastapi import FastAPI, HTTPException
from api.schema import HealthResponse
from api.llm_validator import parse_and_validate_llm_output
from model import generate_command  

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
    generates a robot command using the LLM,
    validates it against the schema,
    and returns either a valid command or an error.
    """

    # 1) Generate LLM output from user instruction ---
    user_instruction = prompt.get("prompt")
    if not user_instruction:
        raise HTTPException(status_code=400, detail={"error": "missing_prompt"})

    llm_output_dict = generate_command(user_instruction)

    # 2) Convert dict back to string for validator ---
    import json
    llm_output_str = json.dumps(llm_output_dict)

    # 3) Validate using the provided validator ---
    success, result = parse_and_validate_llm_output(llm_output_str)

    if not success:
        raise HTTPException(status_code=400, detail=result)

    # 4) Return validated response ---
    return result
