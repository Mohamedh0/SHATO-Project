import re
import json
import yaml
from pathlib import Path
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig
)

def load_yaml_config(file_name: str) -> dict:
    """Load a YAML configuration file from the config directory."""
    path = Path(__file__).resolve().parent.parent / "config" / file_name
    with open(path, "r") as f:
        return yaml.safe_load(f)

model_config = load_yaml_config("model_config.yaml")
prompts_config = load_yaml_config("prompts.yaml")

MODEL_ID = model_config["model"]["name"]
MAX_LENGTH = model_config["model"]["max_length"]
TEMPERATURE = model_config["model"]["temperature"]

# Global variables for model and tokenizer
model = None
tokenizer = None

def load_model():
    """Load the model and tokenizer (called once at startup)"""
    global model, tokenizer
    
    # Configure quantization if enabled
    quant_config = None
    if model_config.get("quantization", {}).get("enabled", False):
        quant_config = BitsAndBytesConfig(
            load_in_4bit=(model_config["quantization"]["method"] == "4bit"),
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )

    # Load tokenizer
    print(f"Loading tokenizer: {MODEL_ID}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)

    # Load model 
    print(f"Loading model: {MODEL_ID}")
    if quant_config:
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            device_map="auto",
            quantization_config=quant_config,
            trust_remote_code=True
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            device_map="auto",
            trust_remote_code=True
        )
    
    print("Model and tokenizer loaded successfully!")

# Command generation

SYSTEM_PROMPT = prompts_config["system_prompt"]
USER_PROMPT_TEMPLATE = prompts_config["user_prompt_template"]
ERROR_PROMPTS = prompts_config["error_prompts"]
PROMPT_SETTINGS = prompts_config["prompt_settings"]

def extract_first_json(text: str) -> dict:
    """
    Extracts and parses the first valid JSON object from text.
    Returns the parsed dict or an error with the raw output.
    """
    # Initialize variables to track the JSON object
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
                # Found a complete JSON object
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    return {"error": "parse_error", "raw_output": text}
        elif in_json:
            json_str += char
        i += 1

    return {"error": "no_json_found", "raw_output": text}

def generate_command(user_instruction: str) -> dict:
    """
    Generate a robot command from natural language.
    Returns a dict with either {"command": ..., "command_params": ...}
    or {"error": ..., "raw_output": ...}.
    """
    # Ensure model is loaded
    if model is None or tokenizer is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")
    
    # Build the prompt
    prompt = SYSTEM_PROMPT + "\n" + USER_PROMPT_TEMPLATE.format(instruction=user_instruction)

    # Tokenize input
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    # Generate output
    outputs = model.generate(
        **inputs,
        max_new_tokens=PROMPT_SETTINGS["max_tokens"],
        temperature=model_config["model"]["temperature"],
        do_sample=True,
        top_p=PROMPT_SETTINGS["top_p"],
        use_cache=False
    )

    # Only decode the generated part, not the prompt
    generated_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
    text = tokenizer.decode(generated_tokens, skip_special_tokens=True)

    # Extract only the first JSON block
    return extract_first_json(text)