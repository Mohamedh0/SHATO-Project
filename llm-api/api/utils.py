import uuid
import yaml
import json
from pathlib import Path
from fastapi import Request
from loguru import logger
from llama_cpp import Llama

# ---------- Logging setup ----------
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

# ---------- JSON extraction helper ----------
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

# ---------- Prompts & LLM setup ----------
def load_prompts():
    config_path = Path("/app/config/prompts.yaml")
    if not config_path.exists():
        logger.warning("Prompts config not found at /app/config/prompts.yaml")
        # Minimal fallback for SHATO if prompts.yaml is missing
        return {
            "system_prompt": "You are SHATO, a robot assistant. Convert instructions to valid JSON commands.",
            "user_prompt_template": "Convert this natural language instruction to a robot command: {instruction}\nRespond with ONLY the JSON."
        }
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

prompts_config = load_prompts()
SYSTEM_PROMPT = prompts_config.get("system_prompt")
USER_PROMPT_TEMPLATE = prompts_config.get("user_prompt_template")

# Load Llama-3.2-3B-Instruct (Q4_K_S) model
llm = Llama(
    model_path="/app/models/llama-3.2-3b-instruct-q4ks.gguf",
    n_ctx=4096,
    n_threads=8,
    n_gpu_layers=0,  # change >0 if you want GPU acceleration
)

# ---------- Generation ----------
def generate_command(instruction: str) -> dict:
    correlation_id = str(uuid.uuid4())
    logger.bind(correlation_id=correlation_id).info(f"Generating command for instruction: {instruction}")
    
    prompt = f"{SYSTEM_PROMPT}\n{USER_PROMPT_TEMPLATE.format(instruction=instruction)}"
    output = llm(
        prompt,
        max_tokens=256,
        temperature=0.5,  # Adjusted for some variety in verbal_response
        stop=["</s>", "User:"]
    )
    raw_text = output["choices"][0]["text"].strip()
    logger.bind(correlation_id=correlation_id).info(f"LLM raw output: {raw_text}")
    
    command_json = extract_first_json(raw_text)
    if "error" in command_json:
        logger.bind(correlation_id=correlation_id).warning(f"JSON extraction failed: {command_json['error']}")
        return {"error": command_json["error"], "raw_output": command_json["raw_output"]}

    return command_json