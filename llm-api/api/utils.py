import uuid
import yaml
import json
from pathlib import Path
from fastapi import Request
from loguru import logger
from llama_cpp import Llama

# Logging setup
logger.remove()
logger.add(
    sink="logs/app.log",
    level="INFO",
    format="{time} [{level}] [correlation_id={extra[correlation_id]}] {message}",
)

def get_correlation_id(req: Request) -> str:
    return req.headers.get("X-Correlation-ID", str(uuid.uuid4()))

def log_request(req: Request, correlation_id: str):
    logger.bind(correlation_id=correlation_id).info(
        f"Incoming request: {req.method} {req.url}"
    )

def log_response(correlation_id: str, status_code: int, message: str = ""):
    logger.bind(correlation_id=correlation_id).info(
        f"Response status: {status_code}, message: {message}"
    )

# JSON extraction helper
def extract_first_json(text: str) -> dict:
    json_str = ""
    brace_count = 0
    in_json = False
    i = 0

    while i < len(text):
        char = text[i]
        if char == '{':
            if not in_json:
                in_json = True
                json_str = char
            else:
                json_str += char
            brace_count += 1
        elif char == '}' and in_json:
            json_str += char
            brace_count -= 1
            if brace_count == 0:
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    return {"error": "parse_error", "raw_output": text}
        elif in_json:
            json_str += char
        i += 1

    return {"error": "no_json_found", "raw_output": text}

# Prompts & LLM setup
def load_prompts():
    config_path = Path("/app/config/prompts.yaml")
    if not config_path.exists():
        logger.warning("Prompts config not found at /app/config/prompts.yaml")
        return {"system_prompt": "", "user_prompt_template": "{instruction}"}
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

prompts_config = load_prompts()
SYSTEM_PROMPT = prompts_config.get("system_prompt", "")
USER_PROMPT_TEMPLATE = prompts_config.get("user_prompt_template", "{instruction}")

llm = Llama(
    model_path="/app/models/qwen2-1_5b-instruct-q4_k_m.gguf",
    n_ctx=4096,
    n_threads=8,
)

def generate_command(instruction: str) -> dict:
    """Generate a robot command from the LLM and return parsed JSON."""
    prompt = SYSTEM_PROMPT + "\n" + USER_PROMPT_TEMPLATE.format(instruction=instruction)
    output = llm(
        prompt,
        max_tokens=128,
        temperature=0.7,
        stop=["User:"],
    )
    raw_text = output["choices"][0]["text"].strip()
    return extract_first_json(raw_text)
